#!/usr/bin/env node

/**
 * GHL Documentation Scraper using Puppeteer
 *
 * This script uses Puppeteer for headless browser automation to:
 * - Browse and discover GHL documentation pages
 * - Extract clean content with JavaScript rendering
 * - Automatically follow documentation links
 * - Implement custom rate limiting to avoid HTTP 429 errors
 * - Save Markdown and metadata to kb/ghl-docs/raw/
 *
 * Key Features:
 * - 2.5 second delays between requests (learned from Firecrawl 84% failure rate)
 * - Exponential backoff on HTTP 429 errors
 * - Checkpoint/resume capability for long-running scrapes
 * - Browser restart every 100 pages to prevent memory leaks
 *
 * Usage:
 *   node scripts/scrape-ghl-with-puppeteer.js --start-url help.gohighlevel.com --max-pages 500
 *
 * CLI Arguments:
 *   --start-url     Starting URL to crawl (default: help.gohighlevel.com)
 *   --max-pages     Maximum pages to scrape (default: 500)
 *   --output        Output directory (default: kb/ghl-docs/raw/help)
 *   --delay         Base delay between requests in ms (default: 2500)
 *   --api           Also scrape API docs from marketplace (default: false)
 *   --resume        Resume from checkpoint (default: false)
 */

import puppeteer from 'puppeteer';
import TurndownService from 'turndown';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// === CLI ARGUMENT PARSING ===
const args = process.argv.slice(2);
const config = {
  startUrl: args.find(a => a.startsWith('--start-url='))?.split('=')[1] || 'help.gohighlevel.com',
  maxPages: parseInt(args.find(a => a.startsWith('--max-pages='))?.split('=')[1] || '500'),
  output: args.find(a => a.startsWith('--output='))?.split('=')[1] || 'kb/ghl-docs/raw/help',
  delay: parseInt(args.find(a => a.startsWith('--delay='))?.split('=')[1] || '2500'),
  api: args.includes('--api'),
  resume: args.includes('--resume'),
};

// === PATHS ===
const projectRoot = path.resolve(__dirname, '..');
const outputDir = path.join(projectRoot, config.output);
const failedLogPath = path.join(projectRoot, 'kb/ghl-docs/failed.log');
const reportPath = path.join(projectRoot, 'kb/ghl-docs/scraping-report.json');
const checkpointPath = path.join(projectRoot, 'kb/ghl-docs/scraping-checkpoint.json');

// === SCRAPING STATE ===
const state = {
  visitedUrls: new Set(),
  queuedUrls: [],
  successCount: 0,
  failedCount: 0,
  startTime: Date.now(),
  results: [],
  currentDelay: config.delay,
  pagesSinceRestart: 0,
};

// === BROWSER INSTANCE ===
let browser = null;
let page = null;

// === TURNDOWN (HTML TO MARKDOWN) ===
const turndownService = new TurndownService({
  headingStyle: 'atx',
  codeBlockStyle: 'fenced',
});

console.log(`
╔═══════════════════════════════════════════════════════════════════════════╗
║          GHL Documentation Scraper (Puppeteer)                            ║
╚═══════════════════════════════════════════════════════════════════════════╝

Configuration:
  Start URL:     ${config.startUrl}
  Max Pages:     ${config.maxPages}
  Base Delay:    ${config.delay}ms (2.5s)
  Output:        ${outputDir}
  Resume:        ${config.resume}

Rate Limiting Strategy:
  ✓ 2.5 second delays between requests
  ✓ Exponential backoff on HTTP 429 errors
  ✓ Browser restart every 100 pages
  ✓ Checkpoint save every 50 pages

Historical Context:
  - Firecrawl v1.0: 84% failure rate (16/19 URLs with HTTP 429)
  - Context7 v2.0: Wrong tool (library docs only)
  - Puppeteer v3.0: Expected to succeed with custom rate limiting
`);

// === UTILITY FUNCTIONS ===

/**
 * Normalize URL to ensure consistency
 */
function normalizeUrl(url) {
  if (!url.startsWith('http')) {
    url = 'https://' + url;
  }
  // Remove trailing slash and fragments
  return url.replace(/\/$/, '').replace(/#.*$/, '');
}

/**
 * Extract domain from URL
 */
function extractDomain(url) {
  const match = url.match(/^https?:\/\/([^\/]+)/);
  return match ? match[1] : null;
}

/**
 * Generate filename from URL
 */
function urlToFilename(url) {
  return url
    .replace(/https?:\/\//, '')
    .replace(/[^a-z0-9]/gi, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
    .substring(0, 200);
}

/**
 * Delay with random jitter
 */
async function delay(ms) {
  const jitter = Math.random() * 500; // 0-500ms random jitter
  await new Promise(resolve => setTimeout(resolve, ms + jitter));
}

/**
 * Save page content to file
 */
function savePage(url, markdown, metadata) {
  const filename = urlToFilename(url) + '.md';
  const filepath = path.join(outputDir, filename);
  const metapath = filepath.replace('.md', '.meta.json');

  // Save Markdown content
  fs.writeFileSync(filepath, markdown, 'utf8');

  // Save metadata
  fs.writeFileSync(metapath, JSON.stringify(metadata, null, 2), 'utf8');

  console.log(`✓ Saved: ${filename} (${metadata.wordCount} words)`);
  return filepath;
}

/**
 * Log failed page
 */
function logFailedPage(url, error) {
  const logEntry = `${new Date().toISOString()} | ${url} | ${error}\n`;
  fs.appendFileSync(failedLogPath, logEntry, 'utf8');
  console.error(`✗ Failed: ${url} - ${error}`);
}

/**
 * Save checkpoint for resume capability
 */
function saveCheckpoint() {
  const checkpoint = {
    timestamp: new Date().toISOString(),
    visitedUrls: Array.from(state.visitedUrls),
    queuedUrls: state.queuedUrls,
    successCount: state.successCount,
    failedCount: state.failedCount,
    currentDelay: state.currentDelay,
  };
  fs.writeFileSync(checkpointPath, JSON.stringify(checkpoint, null, 2), 'utf8');
  console.log(`💾 Checkpoint saved (${state.visitedUrls.size} pages processed)`);
}

/**
 * Load checkpoint for resume
 */
function loadCheckpoint() {
  if (!fs.existsSync(checkpointPath)) {
    return false;
  }

  const checkpoint = JSON.parse(fs.readFileSync(checkpointPath, 'utf8'));
  state.visitedUrls = new Set(checkpoint.visitedUrls);
  state.queuedUrls = checkpoint.queuedUrls;
  state.successCount = checkpoint.successCount;
  state.failedCount = checkpoint.failedCount;
  state.currentDelay = checkpoint.currentDelay;

  console.log(`✓ Resumed from checkpoint: ${state.visitedUrls.size} pages already processed`);
  return true;
}

/**
 * Generate scraping report
 */
function generateReport() {
  const report = {
    timestamp: new Date().toISOString(),
    config: config,
    totalUrls: state.visitedUrls.size,
    successful: state.successCount,
    failed: state.failedCount,
    duration: Date.now() - state.startTime,
    averageDelay: state.currentDelay,
    results: state.results,
  };

  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2), 'utf8');
  console.log(`\n✓ Scraping report saved to: ${reportPath}`);
  return report;
}

/**
 * Initialize browser
 */
async function initBrowser() {
  if (browser) {
    await browser.close();
  }

  browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  page = await browser.newPage();

  // Set user agent to appear more human-like
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

  // Set viewport
  await page.setViewport({ width: 1920, height: 1080 });

  console.log('🌐 Browser initialized');
  state.pagesSinceRestart = 0;
}

/**
 * Scrape a single URL with rate limiting and error handling
 */
async function scrapeUrl(url) {
  url = normalizeUrl(url);

  // Skip if already visited
  if (state.visitedUrls.has(url)) {
    return null;
  }

  // Mark as visited
  state.visitedUrls.add(url);

  try {
    console.log(`\n📄 Scraping: ${url}`);

    // Navigate to page with timeout
    const response = await page.goto(url, {
      waitUntil: 'networkidle2',
      timeout: 30000,
    });

    // Check for rate limiting
    if (response.status() === 429) {
      throw new Error('HTTP 429: Rate Limited');
    }

    // Wait for content to load
    await page.waitForSelector('body', { timeout: 5000 });

    // Extract page metadata
    const metadata = await page.evaluate(() => {
      return {
        title: document.title || 'Unknown',
        headings: Array.from(document.querySelectorAll('h1, h2, h3')).map(h => h.textContent.trim()),
        lastUpdated: document.querySelector('meta[property="article:modified_time"]')?.content || null,
      };
    });

    // Get HTML content
    const htmlContent = await page.content();

    // Convert HTML to Markdown
    const markdown = turndownService.turndown(htmlContent);

    // Complete metadata
    const fullMetadata = {
      url: url,
      title: metadata.title,
      scrapedAt: new Date().toISOString(),
      wordCount: markdown.split(/\s+/).length,
      headings: metadata.headings,
      lastUpdated: metadata.lastUpdated,
      status: 'success',
    };

    // Save content
    savePage(url, markdown, fullMetadata);

    state.successCount++;
    state.results.push({
      url: url,
      status: 'success',
      wordCount: fullMetadata.wordCount,
    });

    // Discover links on page
    const links = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('a[href]'))
        .map(a => a.href)
        .filter(href => href && href.startsWith('http'));
    });

    // Filter links to same domain
    const domain = extractDomain(url);
    const relevantLinks = links
      .map(normalizeUrl)
      .filter(link => {
        const linkDomain = extractDomain(link);
        return linkDomain === domain && !state.visitedUrls.has(link);
      });

    // Add to queue
    for (const link of relevantLinks) {
      if (!state.queuedUrls.includes(link) && state.visitedUrls.size < config.maxPages) {
        state.queuedUrls.push(link);
      }
    }

    console.log(`  ✓ Discovered ${relevantLinks.length} new links`);

    // Success - use base delay
    await delay(config.delay);
    state.currentDelay = config.delay;

    return { success: true, metadata: fullMetadata };

  } catch (error) {
    // Handle HTTP 429 rate limiting
    if (error.message.includes('429')) {
      state.currentDelay = Math.min(state.currentDelay * 2, 30000); // Max 30s
      console.error(`⚠️  Rate limited! Increasing delay to ${state.currentDelay}ms`);
      await delay(state.currentDelay);

      // Retry
      state.visitedUrls.delete(url); // Remove from visited to allow retry
      return scrapeUrl(url);
    }

    // Other errors
    logFailedPage(url, error.message);
    state.failedCount++;
    state.results.push({
      url: url,
      status: 'failed',
      error: error.message,
    });

    // Still apply delay
    await delay(config.delay);

    return { success: false, error: error.message };
  }
}

/**
 * Main scraping orchestration
 */
async function main() {
  try {
    // Create output directories
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
      console.log(`✓ Created output directory: ${outputDir}`);
    }

    // Resume from checkpoint if requested
    if (config.resume) {
      loadCheckpoint();
    }

    // Initialize queue with start URL if not resuming
    if (state.queuedUrls.length === 0) {
      const startUrl = normalizeUrl(`https://${config.startUrl}`);
      state.queuedUrls.push(startUrl);
    }

    // Initialize browser
    await initBrowser();

    console.log(`\n╔═══════════════════════════════════════════════════════════════════════════╗`);
    console.log(`║              Starting GHL Documentation Scraping                         ║`);
    console.log(`╚═══════════════════════════════════════════════════════════════════════════╝\n`);

    // Process queue
    while (state.queuedUrls.length > 0 && state.visitedUrls.size < config.maxPages) {
      const url = state.queuedUrls.shift();
      await scrapeUrl(url);

      state.pagesSinceRestart++;

      // Checkpoint every 50 pages
      if (state.visitedUrls.size % 50 === 0) {
        saveCheckpoint();
      }

      // Browser restart every 100 pages
      if (state.pagesSinceRestart >= 100) {
        console.log(`\n🔄 Restarting browser (memory management)...`);
        await initBrowser();
      }

      // Progress update
      if (state.visitedUrls.size % 10 === 0) {
        console.log(`\n📊 Progress: ${state.visitedUrls.size}/${config.maxPages} pages`);
        console.log(`   Success: ${state.successCount} | Failed: ${state.failedCount}`);
        console.log(`   Queue: ${state.queuedUrls.length} URLs | Current delay: ${state.currentDelay}ms\n`);
      }
    }

    // Close browser
    if (browser) {
      await browser.close();
    }

    // Generate final report
    const report = generateReport();

    console.log(`\n╔═══════════════════════════════════════════════════════════════════════════╗`);
    console.log(`║                     Scraping Complete!                                   ║`);
    console.log(`╚═══════════════════════════════════════════════════════════════════════════╝\n`);
    console.log(`Total pages scraped: ${report.totalUrls}`);
    console.log(`Successful: ${report.successful}`);
    console.log(`Failed: ${report.failed}`);
    console.log(`Success Rate: ${((report.successful / report.totalUrls) * 100).toFixed(1)}%`);
    console.log(`Duration: ${Math.round(report.duration / 1000)}s (${Math.round(report.duration / 60000)}m)`);
    console.log(`\nOutput: ${outputDir}`);
    console.log(`Report: ${reportPath}\n`);

  } catch (error) {
    console.error('\n✗ Script failed:', error.message);
    console.error(error.stack);

    // Close browser on error
    if (browser) {
      await browser.close();
    }

    process.exit(1);
  }
}

// === RUN SCRIPT ===
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { scrapeUrl, initBrowser, config };
