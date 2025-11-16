/**
 * Document Chunking Script
 *
 * Chunks raw markdown documents from kb directories into semantic chunks.
 * Saves processed chunks to kb processed directories.
 *
 * Usage:
 *   node scripts/chunk-documents.js
 *   node scripts/chunk-documents.js --input kb/ghl-docs/raw --output kb/ghl-docs/processed
 *   node scripts/chunk-documents.js --chunk-size 512 --overlap 0.10
 *   node scripts/chunk-documents.js --source best-practices
 *
 * Options:
 *   --input <path>         Input directory with raw markdown (default: kb source dirs)
 *   --output <path>        Output directory for chunks (default: kb processed dirs)
 *   --chunk-size <number>  Target chunk size in tokens (default: 512)
 *   --overlap <number>     Overlap percentage 0-1 (default: 0.10)
 *   --source <type>        Source type: ghl-docs, youtube-transcripts, best-practices, snapshots, or all (default: all)
 *
 * Source types:
 *   all                    All sources (ghl-docs, youtube-transcripts, best-practices, snapshots)
 *   ghl-docs               GoHighLevel documentation (kb/ghl-docs/raw)
 *   youtube-transcripts    YouTube tutorial transcripts
 *   best-practices         Best practices guides (69 curated files)
 *   snapshots              Snapshot references (31 marketplace profiles)
 */

import fs from 'fs/promises';
import path from 'path';
import { createLogger } from './utils/logger.js';
import { chunkDocument, getChunkingStats } from './utils/chunker.js';

// Parse command-line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const config = {
    input: null,
    output: null,
    chunkSize: 512,
    overlap: 0.10,
    source: 'all' // all, ghl-docs, youtube-transcripts
  };

  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace(/^--/, '');
    const value = args[i + 1];

    switch (key) {
      case 'input':
        config.input = value;
        break;
      case 'output':
        config.output = value;
        break;
      case 'chunk-size':
      case 'chunkSize':
        config.chunkSize = parseInt(value, 10);
        break;
      case 'overlap':
        config.overlap = parseFloat(value);
        break;
      case 'source':
        config.source = value;
        break;
    }
  }

  return config;
}

/**
 * Get source directories to process
 */
function getSourceDirectories(config) {
  const sources = [];

  if (config.source === 'all' || config.source === 'ghl-docs') {
    sources.push({
      name: 'ghl-docs',
      input: config.input || 'kb/ghl-docs/raw',
      output: config.output || 'kb/ghl-docs/processed'
    });
  }

  if (config.source === 'all' || config.source === 'youtube-transcripts') {
    sources.push({
      name: 'youtube-transcripts',
      input: config.input || 'kb/youtube-transcripts',
      output: config.output || 'kb/youtube-transcripts/processed'
    });
  }

  if (config.source === 'all' || config.source === 'best-practices') {
    sources.push({
      name: 'best-practices',
      input: config.input || 'kb/best-practices',
      output: config.output || 'kb/best-practices/processed'
    });
  }

  if (config.source === 'all' || config.source === 'snapshots') {
    sources.push({
      name: 'snapshots-reference',
      input: config.input || 'kb/snapshots-reference',
      output: config.output || 'kb/snapshots-reference/processed'
    });
  }

  // If specific input/output provided, override
  if (config.input && config.output) {
    return [{
      name: path.basename(config.input),
      input: config.input,
      output: config.output
    }];
  }

  return sources;
}

/**
 * Find all markdown files in a directory
 */
async function findMarkdownFiles(dir) {
  const files = [];

  try {
    const entries = await fs.readdir(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);

      if (entry.isDirectory()) {
        // Recurse into subdirectories
        const subFiles = await findMarkdownFiles(fullPath);
        files.push(...subFiles);
      } else if (entry.isFile() && entry.name.endsWith('.md')) {
        files.push(fullPath);
      }
    }
  } catch (error) {
    // Directory doesn't exist or not accessible
    return [];
  }

  return files;
}

/**
 * Find all JSON transcript files (for YouTube transcripts)
 */
async function findTranscriptFiles(dir) {
  const files = [];

  try {
    const entries = await fs.readdir(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);

      if (entry.isDirectory()) {
        // Recurse into subdirectories
        const subFiles = await findTranscriptFiles(fullPath);
        files.push(...subFiles);
      } else if (entry.isFile() && entry.name.endsWith('.json') && entry.name !== 'index.json') {
        files.push(fullPath);
      }
    }
  } catch (error) {
    return [];
  }

  return files;
}

/**
 * Load markdown document and metadata
 */
async function loadMarkdownDocument(filePath, logger) {
  // Read markdown content
  const markdown = await fs.readFile(filePath, 'utf-8');

  // Try to load metadata from .meta.json file
  const metaPath = filePath.replace(/\.md$/, '.meta.json');
  let metadata = {};

  try {
    const metaContent = await fs.readFile(metaPath, 'utf-8');
    metadata = JSON.parse(metaContent);
  } catch (error) {
    // No metadata file - extract basic info from filename
    logger.debug(`No metadata file for ${path.basename(filePath)}`);
    metadata = {
      title: path.basename(filePath, '.md').replace(/_/g, ' '),
      url: filePath
    };
  }

  return { markdown, metadata };
}

/**
 * Load YouTube transcript and convert to markdown
 */
async function loadTranscriptDocument(filePath, logger) {
  const content = await fs.readFile(filePath, 'utf-8');
  const data = JSON.parse(content);

  // Convert transcript JSON to markdown format
  const markdown = `# ${data.metadata.title}

**Creator:** ${data.metadata.creator}
**Video ID:** ${data.videoId}
**Duration:** ${data.metadata.duration}s
**Published:** ${data.metadata.publishDate}

## Transcript

${data.transcript}
`;

  const metadata = {
    title: data.metadata.title,
    url: `https://youtube.com/watch?v=${data.videoId}`,
    category: 'youtube-tutorial',
    creator: data.metadata.creator,
    videoId: data.videoId,
    duration: data.metadata.duration
  };

  return { markdown, metadata };
}

/**
 * Save chunks to output directory
 */
async function saveChunks(outputDir, sourceFileName, chunks, logger) {
  // Ensure output directory exists
  await fs.mkdir(outputDir, { recursive: true });

  // Create filename for chunks
  const baseName = path.basename(sourceFileName, path.extname(sourceFileName));
  const chunksFileName = `${baseName}_chunks.json`;
  const chunksPath = path.join(outputDir, chunksFileName);

  // Save chunks with metadata
  const output = {
    sourceFile: sourceFileName,
    chunkCount: chunks.length,
    chunks,
    stats: getChunkingStats(chunks),
    chunkedAt: new Date().toISOString()
  };

  await fs.writeFile(chunksPath, JSON.stringify(output, null, 2), 'utf-8');

  return chunksPath;
}

/**
 * Process a single document
 */
async function processDocument(filePath, outputDir, config, logger) {
  const isTranscript = filePath.endsWith('.json');

  // Load document
  const { markdown, metadata } = isTranscript
    ? await loadTranscriptDocument(filePath, logger)
    : await loadMarkdownDocument(filePath, logger);

  // Chunk document
  const chunks = chunkDocument(markdown, metadata, {
    chunkSize: config.chunkSize,
    overlap: config.overlap
  });

  // Save chunks
  const outputPath = await saveChunks(outputDir, filePath, chunks, logger);

  return {
    sourceFile: filePath,
    outputFile: outputPath,
    chunkCount: chunks.length,
    stats: getChunkingStats(chunks)
  };
}

/**
 * Main chunking function
 */
async function main() {
  const config = parseArgs();
  const logPath = path.join('kb', 'chunk.log');
  const logger = createLogger(logPath);

  logger.step('Document Chunking Script');
  logger.info(`Chunk size: ${config.chunkSize} tokens`);
  logger.info(`Overlap: ${(config.overlap * 100).toFixed(0)}%`);
  logger.info(`Source: ${config.source}`);

  try {
    const sources = getSourceDirectories(config);
    logger.info(`Processing ${sources.length} source(s)`);

    let totalDocuments = 0;
    let totalChunks = 0;
    let totalTokens = 0;
    const results = [];

    for (const source of sources) {
      logger.step(`Processing: ${source.name}`);
      logger.info(`Input: ${source.input}`);
      logger.info(`Output: ${source.output}`);

      // Find files to process
      const isTranscriptSource = source.name === 'youtube-transcripts';
      const files = isTranscriptSource
        ? await findTranscriptFiles(source.input)
        : await findMarkdownFiles(source.input);

      if (files.length === 0) {
        logger.warn(`No files found in ${source.input}`);
        continue;
      }

      logger.success(`Found ${files.length} file(s) to process`);

      // Process each file
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const fileNum = i + 1;

        try {
          logger.progressBar(fileNum, files.length, 'Chunking');

          const result = await processDocument(file, source.output, config, logger);

          results.push(result);
          totalDocuments++;
          totalChunks += result.chunkCount;
          totalTokens += result.stats.totalTokens;

          logger.debug(`Chunked: ${path.basename(file)} -> ${result.chunkCount} chunks`);
        } catch (error) {
          logger.error(`Failed to process ${file}`, error);
        }
      }
    }

    // Save processing summary
    const summaryPath = path.join('kb', 'chunk-summary.json');
    const summary = {
      processedAt: new Date().toISOString(),
      config: {
        chunkSize: config.chunkSize,
        overlap: config.overlap,
        source: config.source
      },
      totals: {
        documents: totalDocuments,
        chunks: totalChunks,
        tokens: totalTokens,
        avgChunksPerDoc: Math.round(totalChunks / totalDocuments),
        avgTokensPerChunk: Math.round(totalTokens / totalChunks)
      },
      results
    };

    await fs.mkdir('kb', { recursive: true });
    await fs.writeFile(summaryPath, JSON.stringify(summary, null, 2), 'utf-8');

    // Final statistics
    logger.step('Summary');
    logger.stats({
      total_documents: totalDocuments,
      total_chunks: totalChunks,
      total_tokens: totalTokens,
      avg_chunks_per_doc: Math.round(totalChunks / totalDocuments),
      avg_tokens_per_chunk: Math.round(totalTokens / totalChunks),
      elapsed_time: logger.getElapsed()
    });

    logger.success(`Summary saved to ${summaryPath}`);
    logger.success('Chunking completed successfully!');

    process.exit(0);
  } catch (error) {
    logger.error('Chunking failed', error);
    process.exit(1);
  }
}

// Run if called directly
const isMain = process.argv[1] && import.meta.url.endsWith(path.basename(process.argv[1]));
if (isMain) {
  main();
}

export { processDocument, findMarkdownFiles, findTranscriptFiles };
