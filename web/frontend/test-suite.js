/**
 * Comprehensive BroBro Platform Test Suite
 * Tests all major features with Puppeteer
 */

import puppeteer from 'puppeteer';
import { writeFileSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const FRONTEND_URL = 'http://localhost:3000';
const BACKEND_URL = 'http://localhost:8000';
const TEST_RESULTS_DIR = join(__dirname, 'test-results');

// Ensure test results directory exists
try {
  mkdirSync(TEST_RESULTS_DIR, { recursive: true });
} catch (err) {
  // Directory might already exist
}

const testResults = {
  timestamp: new Date().toISOString(),
  services: {},
  tests: [],
  screenshots: [],
  consoleErrors: [],
  performance: {},
  summary: { passed: 0, failed: 0, total: 0 }
};

function logTest(name, status, message, data = {}) {
  const result = { name, status, message, timestamp: new Date().toISOString(), ...data };
  testResults.tests.push(result);
  testResults.summary.total++;
  if (status === 'PASSED') testResults.summary.passed++;
  if (status === 'FAILED') testResults.summary.failed++;

  const icon = status === 'PASSED' ? '✅' : status === 'FAILED' ? '❌' : 'ℹ️';
  console.log(`${icon} ${name}: ${message}`);
}

async function takeScreenshot(page, name) {
  const filename = `${name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${Date.now()}.png`;
  const filepath = join(TEST_RESULTS_DIR, filename);
  await page.screenshot({ path: filepath, fullPage: true });
  testResults.screenshots.push({ name, filename, path: filepath });
  console.log(`📸 Screenshot saved: ${filename}`);
  return filepath;
}

async function testHealthCheck() {
  console.log('\n=== Testing Health Check ===');
  try {
    const response = await fetch(`${BACKEND_URL}/api/health`);
    const data = await response.json();

    testResults.services.backend = {
      status: data.status,
      chroma_connected: data.chroma_connected,
      collections: data.collections
    };

    if (data.status === 'healthy' && data.chroma_connected) {
      logTest('Health Check', 'PASSED', 'Backend healthy, ChromaDB connected', data);
    } else {
      logTest('Health Check', 'FAILED', `Status: ${data.status}, ChromaDB: ${data.chroma_connected}`, data);
    }
  } catch (error) {
    logTest('Health Check', 'FAILED', `Error: ${error.message}`);
  }
}

async function testSearchAPI() {
  console.log('\n=== Testing Search API ===');
  try {
    const startTime = Date.now();
    const response = await fetch(`${BACKEND_URL}/api/search/quick?q=send+email&limit=5`);
    const data = await response.json();
    const responseTime = Date.now() - startTime;

    testResults.performance.searchAPI = responseTime;

    if (data.success && data.results && data.results.length > 0) {
      logTest('Search API', 'PASSED', `Found ${data.results.length} results in ${responseTime}ms`, {
        responseTime,
        resultCount: data.results.length
      });
    } else {
      logTest('Search API', 'FAILED', 'No results returned or error occurred', data);
    }
  } catch (error) {
    logTest('Search API', 'FAILED', `Error: ${error.message}`);
  }
}

async function runBrowserTests() {
  console.log('\n=== Starting Browser Tests ===');

  const browser = await puppeteer.launch({
    headless: false, // Set to true for headless mode
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    defaultViewport: { width: 1920, height: 1080 }
  });

  const page = await browser.newPage();

  // Capture console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      testResults.consoleErrors.push({
        text: msg.text(),
        location: msg.location(),
        timestamp: new Date().toISOString()
      });
    }
  });

  page.on('pageerror', error => {
    testResults.consoleErrors.push({
      text: error.toString(),
      type: 'pageerror',
      timestamp: new Date().toISOString()
    });
  });

  try {
    // Test 1: Homepage Load
    console.log('\n--- Test: Homepage Load ---');
    const startLoad = Date.now();
    await page.goto(FRONTEND_URL, { waitUntil: 'networkidle0', timeout: 30000 });
    const loadTime = Date.now() - startLoad;
    testResults.performance.homepageLoad = loadTime;

    await takeScreenshot(page, 'homepage');

    if (loadTime < 5000) {
      logTest('Homepage Load', 'PASSED', `Loaded in ${loadTime}ms`, { loadTime });
    } else {
      logTest('Homepage Load', 'WARNING', `Loaded in ${loadTime}ms (>5s)`, { loadTime });
    }

    // Test 2: Search Functionality
    console.log('\n--- Test: Search Functionality ---');
    const searchSelector = 'input[type="text"], input[placeholder*="search" i], input[placeholder*="Search" i]';
    const searchInput = await page.$(searchSelector);

    if (searchInput) {
      await searchInput.click();
      await searchInput.type('send email', { delay: 50 });
      await new Promise(resolve => setTimeout(resolve, 2000)); // Wait for search results

      await takeScreenshot(page, 'search_results');

      const hasResults = await page.evaluate(() => {
        const resultsText = document.body.innerText.toLowerCase();
        return resultsText.includes('result') || resultsText.includes('command');
      });

      if (hasResults) {
        logTest('Search Functionality', 'PASSED', 'Search executed and results displayed');
      } else {
        logTest('Search Functionality', 'FAILED', 'No search results found');
      }
    } else {
      logTest('Search Functionality', 'FAILED', 'Search input not found');
    }

    // Test 3: Navigation
    console.log('\n--- Test: Navigation ---');
    const navLinks = await page.$$('a, button');
    let foundWorkflows = false;

    for (const link of navLinks) {
      const text = await page.evaluate(el => el.textContent, link);
      if (text && text.toLowerCase().includes('workflow')) {
        foundWorkflows = true;
        await link.click();
        await new Promise(resolve => setTimeout(resolve, 2000));
        await takeScreenshot(page, 'workflows_page');
        break;
      }
    }

    if (foundWorkflows) {
      logTest('Navigation', 'PASSED', 'Navigated to Workflows page');
    } else {
      logTest('Navigation', 'WARNING', 'Workflows navigation link not found');
    }

    // Test 4: Workflow Builder
    console.log('\n--- Test: Workflow Builder ---');
    const canvasExists = await page.$('canvas, svg, .workflow-canvas, .workflow-builder');

    if (canvasExists) {
      await takeScreenshot(page, 'workflow_builder');
      logTest('Workflow Builder', 'PASSED', 'Workflow builder canvas detected');
    } else {
      logTest('Workflow Builder', 'FAILED', 'Workflow builder canvas not found');
    }

    // Test 5: AI Generation Button
    console.log('\n--- Test: AI Generation Feature ---');
    const aiButton = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      return buttons.some(btn => {
        const text = btn.textContent.toLowerCase();
        return text.includes('ai') || text.includes('generate');
      });
    });

    if (aiButton) {
      logTest('AI Generation Button', 'PASSED', 'AI generation button found');
    } else {
      logTest('AI Generation Button', 'WARNING', 'AI generation button not visible');
    }

    // Test 6: Keyboard Shortcuts - Command Palette
    console.log('\n--- Test: Command Palette (Cmd+/) ---');
    await page.keyboard.down('Control');
    await page.keyboard.press('/');
    await page.keyboard.up('Control');
    await new Promise(resolve => setTimeout(resolve, 1000));

    await takeScreenshot(page, 'command_palette');

    const paletteVisible = await page.evaluate(() => {
      const text = document.body.innerText.toLowerCase();
      return text.includes('command') || text.includes('palette') || text.includes('search');
    });

    if (paletteVisible) {
      logTest('Command Palette', 'PASSED', 'Command palette opened with Ctrl+/');

      // Close with Escape
      await page.keyboard.press('Escape');
      await new Promise(resolve => setTimeout(resolve, 500));
    } else {
      logTest('Command Palette', 'FAILED', 'Command palette did not open');
    }

    // Test 7: Shortcuts Help (Shift+?)
    console.log('\n--- Test: Shortcuts Help (Shift+?) ---');
    await page.keyboard.down('Shift');
    await page.keyboard.press('?');
    await page.keyboard.up('Shift');
    await new Promise(resolve => setTimeout(resolve, 1000));

    await takeScreenshot(page, 'shortcuts_help');

    const helpVisible = await page.evaluate(() => {
      const text = document.body.innerText.toLowerCase();
      return text.includes('shortcut') || text.includes('keyboard') || text.includes('help');
    });

    if (helpVisible) {
      logTest('Shortcuts Help', 'PASSED', 'Shortcuts help modal opened with Shift+?');
      await page.keyboard.press('Escape');
    } else {
      logTest('Shortcuts Help', 'WARNING', 'Shortcuts help modal did not open');
    }

    // Test 8: Check Console Errors
    console.log('\n--- Test: Console Errors ---');
    if (testResults.consoleErrors.length === 0) {
      logTest('Console Errors', 'PASSED', 'No console errors detected');
    } else {
      logTest('Console Errors', 'FAILED', `Found ${testResults.consoleErrors.length} console errors`, {
        errorCount: testResults.consoleErrors.length,
        errors: testResults.consoleErrors.slice(0, 5) // First 5 errors
      });
    }

    // Final screenshot
    await takeScreenshot(page, 'final_state');

  } catch (error) {
    logTest('Browser Tests', 'FAILED', `Error during browser tests: ${error.message}`);
    console.error('Browser test error:', error);
  } finally {
    await browser.close();
  }
}

async function generateReport() {
  console.log('\n=== Generating Test Report ===');

  const reportPath = join(TEST_RESULTS_DIR, 'test-report.json');
  writeFileSync(reportPath, JSON.stringify(testResults, null, 2));
  console.log(`\n📄 Full report saved to: ${reportPath}`);

  // Generate summary
  console.log('\n' + '='.repeat(60));
  console.log('TEST SUMMARY');
  console.log('='.repeat(60));
  console.log(`Total Tests: ${testResults.summary.total}`);
  console.log(`✅ Passed: ${testResults.summary.passed}`);
  console.log(`❌ Failed: ${testResults.summary.failed}`);
  console.log(`📸 Screenshots: ${testResults.screenshots.length}`);
  console.log(`🚨 Console Errors: ${testResults.consoleErrors.length}`);
  console.log('='.repeat(60));

  // Performance metrics
  console.log('\nPERFORMANCE METRICS:');
  console.log(`- Homepage Load: ${testResults.performance.homepageLoad || 'N/A'}ms`);
  console.log(`- Search API: ${testResults.performance.searchAPI || 'N/A'}ms`);

  // Service status
  console.log('\nSERVICE STATUS:');
  console.log(`- Backend: ${testResults.services.backend?.status || 'Unknown'}`);
  console.log(`- ChromaDB: ${testResults.services.backend?.chroma_connected ? 'Connected' : 'Not Connected'}`);

  console.log('\n' + '='.repeat(60));

  return testResults;
}

async function runAllTests() {
  console.log('🚀 Starting BroBro Comprehensive Test Suite\n');
  console.log(`Frontend URL: ${FRONTEND_URL}`);
  console.log(`Backend URL: ${BACKEND_URL}`);
  console.log(`Test Results Dir: ${TEST_RESULTS_DIR}\n`);

  try {
    await testHealthCheck();
    await testSearchAPI();
    await runBrowserTests();

    const results = await generateReport();

    // Exit with appropriate code
    if (results.summary.failed > 0) {
      console.log('\n⚠️  Some tests failed. Please review the report.');
      process.exit(1);
    } else {
      console.log('\n✅ All tests passed!');
      process.exit(0);
    }
  } catch (error) {
    console.error('\n❌ Test suite error:', error);
    process.exit(1);
  }
}

// Run tests
runAllTests();
