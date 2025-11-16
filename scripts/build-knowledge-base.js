/**
 * Knowledge Base Build Orchestrator
 *
 * Orchestrates the full knowledge base pipeline:
 * 1. Scrape GHL documentation
 * 2. Extract YouTube transcripts
 * 3. Chunk documents
 * 4. Generate embeddings and upload to Chroma
 *
 * Usage:
 *   node scripts/build-knowledge-base.js
 *   node scripts/build-knowledge-base.js --steps scrape,chunk
 *   node scripts/build-knowledge-base.js --steps embed --clean false
 *   node scripts/build-knowledge-base.js --steps all
 *
 * Options:
 *   --steps <steps>     Steps to run: all, scrape, extract, chunk, embed (default: all)
 *                       Multiple steps: --steps scrape,chunk,embed
 *   --clean <bool>      Clean output directories before running (default: false)
 *
 * Individual step options can be passed through:
 *   --max-pages <n>     For scrape step (default: 500)
 *   --limit <n>         For extract step (default: 100)
 *   --chunk-size <n>    For chunk step (default: 512)
 *   --batch-size <n>    For embed step (default: 100)
 */

import fs from 'fs/promises';
import path from 'path';
import { spawn } from 'child_process';
import { createLogger } from './utils/logger.js';

// Parse command-line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const config = {
    steps: 'all', // all, scrape, extract, chunk, embed
    clean: false,
    // Pass-through options for individual scripts
    maxPages: 500,
    limit: 100,
    chunkSize: 512,
    overlap: 0.10,
    batchSize: 100
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg.startsWith('--')) {
      const key = arg.replace(/^--/, '');
      const value = args[i + 1];

      switch (key) {
        case 'steps':
          config.steps = value;
          i++;
          break;
        case 'clean':
          config.clean = value === 'true' || value === '1';
          i++;
          break;
        case 'max-pages':
        case 'maxPages':
          config.maxPages = parseInt(value, 10);
          i++;
          break;
        case 'limit':
          config.limit = parseInt(value, 10);
          i++;
          break;
        case 'chunk-size':
        case 'chunkSize':
          config.chunkSize = parseInt(value, 10);
          i++;
          break;
        case 'overlap':
          config.overlap = parseFloat(value);
          i++;
          break;
        case 'batch-size':
        case 'batchSize':
          config.batchSize = parseInt(value, 10);
          i++;
          break;
      }
    }
  }

  return config;
}

/**
 * Determine which steps to run
 */
function getStepsToRun(stepsArg) {
  const allSteps = ['scrape', 'extract', 'chunk', 'embed'];

  if (stepsArg === 'all') {
    return allSteps;
  }

  // Parse comma-separated list
  const requestedSteps = stepsArg.split(',').map(s => s.trim().toLowerCase());

  // Validate steps
  const validSteps = requestedSteps.filter(s => allSteps.includes(s));

  if (validSteps.length === 0) {
    throw new Error(`No valid steps specified. Valid steps: ${allSteps.join(', ')}`);
  }

  return validSteps;
}

/**
 * Clean output directories
 */
async function cleanDirectories(logger) {
  const directories = [
    'kb/ghl-docs/raw',
    'kb/ghl-docs/processed',
    'kb/youtube-transcripts',
    'kb/youtube-transcripts/processed'
  ];

  for (const dir of directories) {
    try {
      await fs.rm(dir, { recursive: true, force: true });
      logger.detail(`Cleaned: ${dir}`);
    } catch (error) {
      // Directory might not exist - that's fine
      logger.debug(`Could not clean ${dir}: ${error.message}`);
    }
  }
}

/**
 * Run a Node.js script as child process
 */
function runScript(scriptPath, args = [], logger) {
  return new Promise((resolve, reject) => {
    logger.info(`Running: node ${scriptPath} ${args.join(' ')}`);

    const child = spawn('node', [scriptPath, ...args], {
      stdio: ['inherit', 'pipe', 'pipe'],
      shell: true
    });

    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (data) => {
      const text = data.toString();
      stdout += text;
      process.stdout.write(text); // Pass through to console
    });

    child.stderr.on('data', (data) => {
      const text = data.toString();
      stderr += text;
      process.stderr.write(text); // Pass through to console
    });

    child.on('close', (code) => {
      if (code === 0) {
        resolve({ stdout, stderr, code });
      } else {
        reject(new Error(`Script exited with code ${code}\n${stderr}`));
      }
    });

    child.on('error', (error) => {
      reject(error);
    });
  });
}

/**
 * Step 1: Scrape GHL documentation
 */
async function runScrapeStep(config, logger) {
  const args = [
    '--source', 'help.gohighlevel.com',
    '--output', 'kb/ghl-docs/raw',
    '--max-pages', config.maxPages.toString()
  ];

  await runScript('scripts/scrape-ghl-docs.js', args, logger);
}

/**
 * Step 2: Extract YouTube transcripts
 */
async function runExtractStep(config, logger) {
  const args = [
    '--source-config', 'kb/youtube-sources.json',
    '--output', 'kb/youtube-transcripts',
    '--limit', config.limit.toString()
  ];

  await runScript('scripts/extract-yt-transcripts.js', args, logger);
}

/**
 * Step 3: Chunk documents
 */
async function runChunkStep(config, logger) {
  const args = [
    '--source', 'all',
    '--chunk-size', config.chunkSize.toString(),
    '--overlap', config.overlap.toString()
  ];

  await runScript('scripts/chunk-documents.js', args, logger);
}

/**
 * Step 4: Generate embeddings and upload
 */
async function runEmbedStep(config, logger) {
  const args = [
    '--source', 'all',
    '--batch-size', config.batchSize.toString()
  ];

  await runScript('scripts/embed-content.js', args, logger);
}

/**
 * Main orchestration function
 */
async function main() {
  const config = parseArgs();
  const logPath = path.join('kb', 'build.log');
  const logger = createLogger(logPath);

  logger.step('Knowledge Base Build Pipeline');

  try {
    // Determine steps to run
    const stepsToRun = getStepsToRun(config.steps);
    logger.info(`Steps to run: ${stepsToRun.join(', ')}`);

    // Clean directories if requested
    if (config.clean) {
      logger.step('Cleaning output directories');
      await cleanDirectories(logger);
      logger.success('Directories cleaned');
    }

    const startTime = Date.now();
    const stepResults = {};

    // Run each step
    for (const step of stepsToRun) {
      const stepStartTime = Date.now();

      try {
        switch (step) {
          case 'scrape':
            logger.step('Step 1: Scrape GHL Documentation');
            await runScrapeStep(config, logger);
            break;

          case 'extract':
            logger.step('Step 2: Extract YouTube Transcripts');
            await runExtractStep(config, logger);
            break;

          case 'chunk':
            logger.step('Step 3: Chunk Documents');
            await runChunkStep(config, logger);
            break;

          case 'embed':
            logger.step('Step 4: Generate Embeddings');
            await runEmbedStep(config, logger);
            break;
        }

        const stepDuration = ((Date.now() - stepStartTime) / 1000).toFixed(2);
        stepResults[step] = {
          success: true,
          duration: stepDuration
        };

        logger.success(`${step} completed in ${stepDuration}s`);
      } catch (error) {
        const stepDuration = ((Date.now() - stepStartTime) / 1000).toFixed(2);
        stepResults[step] = {
          success: false,
          duration: stepDuration,
          error: error.message
        };

        logger.error(`${step} failed after ${stepDuration}s`, error);

        // Ask whether to continue or abort
        logger.warn('Step failed - stopping pipeline');
        throw error;
      }
    }

    const totalDuration = ((Date.now() - startTime) / 1000).toFixed(2);

    // Load summaries from individual steps
    const summaries = await loadStepSummaries(stepsToRun, logger);

    // Create comprehensive build summary
    const buildSummary = {
      buildAt: new Date().toISOString(),
      config: {
        steps: stepsToRun,
        clean: config.clean,
        maxPages: config.maxPages,
        limit: config.limit,
        chunkSize: config.chunkSize,
        overlap: config.overlap,
        batchSize: config.batchSize
      },
      stepResults,
      summaries,
      totalDuration,
      success: Object.values(stepResults).every(r => r.success)
    };

    // Save build summary
    const buildSummaryPath = path.join('kb', 'build-summary.json');
    await fs.mkdir('kb', { recursive: true });
    await fs.writeFile(buildSummaryPath, JSON.stringify(buildSummary, null, 2), 'utf-8');

    // Final statistics
    logger.step('Build Summary');

    // Aggregate stats
    const stats = {
      total_duration: `${totalDuration}s`,
      steps_completed: stepsToRun.filter(s => stepResults[s].success).length,
      steps_failed: stepsToRun.filter(s => !stepResults[s].success).length
    };

    // Add step-specific stats
    if (summaries.chunk) {
      stats.total_documents = summaries.chunk.totals?.documents || 0;
      stats.total_chunks = summaries.chunk.totals?.chunks || 0;
    }

    if (summaries.embed) {
      stats.embeddings_generated = summaries.embed.totals?.documents || 0;
      stats.collections = summaries.embed.collections?.length || 0;
    }

    logger.stats(stats);

    logger.success(`Build summary saved to ${buildSummaryPath}`);

    if (buildSummary.success) {
      logger.success('Knowledge base build completed successfully!');
      process.exit(0);
    } else {
      logger.error('Build completed with errors - see build.log for details');
      process.exit(1);
    }
  } catch (error) {
    logger.error('Build pipeline failed', error);
    process.exit(1);
  }
}

/**
 * Load summaries from individual step outputs
 */
async function loadStepSummaries(steps, logger) {
  const summaries = {};

  const summaryFiles = {
    scrape: 'kb/ghl-docs/scrape.log',
    extract: 'kb/youtube-transcripts/extract.log',
    chunk: 'kb/chunk-summary.json',
    embed: 'kb/embed-summary.json'
  };

  for (const step of steps) {
    const summaryPath = summaryFiles[step];
    if (!summaryPath) continue;

    try {
      if (summaryPath.endsWith('.json')) {
        const content = await fs.readFile(summaryPath, 'utf-8');
        summaries[step] = JSON.parse(content);
      } else {
        // For log files, just note they exist
        summaries[step] = { logFile: summaryPath };
      }
    } catch (error) {
      logger.debug(`Could not load summary for ${step}: ${error.message}`);
    }
  }

  return summaries;
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1].replace(/\\/g, '/')}`) {
  main();
}

export { runScrapeStep, runExtractStep, runChunkStep, runEmbedStep };
