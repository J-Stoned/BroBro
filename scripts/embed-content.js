/**
 * Content Embedding Script
 *
 * Generates embeddings for chunked documents and uploads to Chroma collections.
 * Uses Xenova/all-MiniLM-L6-v2 for embedding generation.
 *
 * Usage:
 *   node scripts/embed-content.js --collection ghl-docs
 *   node scripts/embed-content.js --input kb/ghl-docs/processed --batch-size 100
 *   node scripts/embed-content.js --collection youtube-tutorials --input kb/youtube-transcripts/processed
 *
 * Options:
 *   --input <path>          Input directory with chunked documents
 *   --collection <name>     Chroma collection name (default: ghl-knowledge-base)
 *   --batch-size <number>   Batch size for embedding generation (default: 100)
 *   --source <type>         Source type: ghl-docs, best-practices, snapshots, or all (default: all)
 *
 * NOTE: This script requires Chroma MCP server for vector storage integration.
 *       Currently uses placeholder implementation. See .mcp.json for MCP setup.
 */

import fs from 'fs/promises';
import path from 'path';
import { config as dotenvConfig } from 'dotenv';
import { createLogger } from './utils/logger.js';
import { createEmbedder } from './utils/embedder.js';
import { ChromaClient } from 'chromadb';

// Load environment variables
dotenvConfig();

// Parse command-line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const config = {
    input: null,
    collection: null,
    batchSize: 100,
    source: 'all' // all, ghl-docs, youtube-transcripts
  };

  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace(/^--/, '');
    const value = args[i + 1];

    switch (key) {
      case 'input':
        config.input = value;
        break;
      case 'collection':
        config.collection = value;
        break;
      case 'batch-size':
      case 'batchSize':
        config.batchSize = parseInt(value, 10);
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

  // If specific input/collection provided, use that
  if (config.input && config.collection) {
    return [{
      name: path.basename(config.input),
      input: config.input,
      collection: config.collection
    }];
  }

  // Process all sources
  if (config.source === 'all') {
    sources.push({
      name: 'ghl-docs',
      input: 'kb/ghl-docs/processed',
      collection: 'ghl-knowledge-base'
    });
    sources.push({
      name: 'best-practices',
      input: 'kb/best-practices/processed',
      collection: 'ghl-knowledge-base'
    });
    sources.push({
      name: 'snapshots-reference',
      input: 'kb/snapshots-reference/processed',
      collection: 'ghl-knowledge-base'
    });
  } else if (config.source === 'ghl-docs') {
    sources.push({
      name: 'ghl-docs',
      input: 'kb/ghl-docs/processed',
      collection: config.collection || 'ghl-knowledge-base'
    });
  } else if (config.source === 'best-practices') {
    sources.push({
      name: 'best-practices',
      input: 'kb/best-practices/processed',
      collection: config.collection || 'ghl-knowledge-base'
    });
  } else if (config.source === 'snapshots') {
    sources.push({
      name: 'snapshots-reference',
      input: 'kb/snapshots-reference/processed',
      collection: config.collection || 'ghl-knowledge-base'
    });
  }

  return sources;
}

/**
 * Find all chunk files in a directory
 */
async function findChunkFiles(dir) {
  const files = [];

  try {
    const entries = await fs.readdir(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);

      if (entry.isDirectory()) {
        // Recurse into subdirectories
        const subFiles = await findChunkFiles(fullPath);
        files.push(...subFiles);
      } else if (entry.isFile() && entry.name.endsWith('_chunks.json')) {
        files.push(fullPath);
      }
    }
  } catch (error) {
    return [];
  }

  return files;
}

/**
 * Load chunks from a file
 */
async function loadChunks(filePath) {
  const content = await fs.readFile(filePath, 'utf-8');
  const data = JSON.parse(content);
  return data.chunks;
}

/**
 * Create or get Chroma collection
 */
async function getOrCreateCollection(chromaClient, collectionName, embeddingDimension, logger) {
  try {
    // Try to get existing collection
    const collection = await chromaClient.getOrCreateCollection({
      name: collectionName,
      metadata: {
        description: 'GoHighLevel knowledge base',
        embedding_dimension: embeddingDimension.toString()
      }
    });

    logger.success(`Collection ready: ${collectionName}`);
    return collection;
  } catch (error) {
    throw new Error(`Failed to get/create collection: ${error.message}`);
  }
}

/**
 * Add documents to Chroma collection
 */
async function addDocumentsToCollection(collection, documents, embeddings, logger) {
  try {
    // Generate unique IDs for each document
    const ids = documents.map((d, i) => {
      const baseId = `${d.metadata.documentTitle}_${d.metadata.chunkIndex}`;
      return `${baseId}_${Date.now()}_${i}`;
    });

    // Add documents to collection
    await collection.add({
      ids: ids,
      embeddings: embeddings,
      documents: documents.map(d => d.content),
      metadatas: documents.map(d => ({
        ...d.metadata,
        // Ensure all metadata values are strings, numbers, or booleans
        documentUrl: String(d.metadata.documentUrl || ''),
        category: String(d.metadata.category || ''),
        section: String(d.metadata.section || ''),
        chunkIndex: Number(d.metadata.chunkIndex || 0),
        hasCode: Boolean(d.metadata.hasCode || false)
      }))
    });

    logger.debug(`Added ${documents.length} documents to collection`);

    return {
      success: true,
      addedCount: documents.length
    };
  } catch (error) {
    throw new Error(`Failed to add documents: ${error.message}`);
  }
}

/**
 * Process and embed chunks from a file
 */
async function processChunkFile(filePath, collection, embedder, logger) {
  // Load chunks
  const chunks = await loadChunks(filePath);

  if (chunks.length === 0) {
    logger.warn(`No chunks found in ${path.basename(filePath)}`);
    return { chunksProcessed: 0, documentsAdded: 0 };
  }

  // Generate embeddings
  const texts = chunks.map(chunk => chunk.content);
  const embeddings = await embedder.generateEmbeddings(texts);

  // Add to Chroma collection
  const result = await addDocumentsToCollection(collection, chunks, embeddings, logger);

  return {
    chunksProcessed: chunks.length,
    documentsAdded: result.addedCount
  };
}

/**
 * Query collection to verify embeddings
 */
async function queryCollection(collection, queryText, embedder, topK = 5, logger) {
  try {
    // Generate embedding for query
    const queryEmbedding = await embedder.generateEmbedding(queryText);

    // Query the collection
    const results = await collection.query({
      queryEmbeddings: [queryEmbedding],
      nResults: topK
    });

    logger.debug(`Query returned ${results.documents[0]?.length || 0} results`);

    return {
      documents: results.documents[0] || [],
      distances: results.distances[0] || [],
      metadatas: results.metadatas[0] || []
    };
  } catch (error) {
    throw new Error(`Failed to query collection: ${error.message}`);
  }
}

/**
 * Main embedding function
 */
async function main() {
  const config = parseArgs();
  const logPath = path.join('kb', 'embed.log');
  const logger = createLogger(logPath);

  logger.step('Content Embedding Script');
  logger.info(`Batch size: ${config.batchSize}`);
  logger.info(`Source: ${config.source}`);

  try {
    // Initialize ChromaDB client
    logger.step('Step 1: Initialize ChromaDB client');
    const chromaUrl = process.env.CHROMA_URL || 'http://localhost:8000';
    const chromaClient = new ChromaClient({ path: chromaUrl });

    // Test connection
    const heartbeat = await chromaClient.heartbeat();
    logger.success(`Connected to ChromaDB at ${chromaUrl} (heartbeat: ${heartbeat}ns)`);

    // Initialize embedder
    logger.step('Step 2: Initialize embedder');
    const embedder = await createEmbedder();
    logger.success(`Embedder initialized (dimension: ${embedder.getDimension()})`);

    const sources = getSourceDirectories(config);
    logger.info(`Processing ${sources.length} source(s)`);

    let totalChunks = 0;
    let totalDocuments = 0;
    const collectionStats = [];

    for (const source of sources) {
      logger.step(`Processing: ${source.name}`);
      logger.info(`Input: ${source.input}`);
      logger.info(`Collection: ${source.collection}`);

      // Get or create collection
      const collection = await getOrCreateCollection(
        chromaClient,
        source.collection,
        embedder.getDimension(),
        logger
      );

      // Find chunk files
      const chunkFiles = await findChunkFiles(source.input);

      if (chunkFiles.length === 0) {
        logger.warn(`No chunk files found in ${source.input}`);
        continue;
      }

      logger.success(`Found ${chunkFiles.length} chunk file(s)`);

      // Process each chunk file
      let sourceChunks = 0;
      let sourceDocuments = 0;

      for (let i = 0; i < chunkFiles.length; i++) {
        const file = chunkFiles[i];
        const fileNum = i + 1;

        try {
          logger.progressBar(fileNum, chunkFiles.length, 'Embedding');

          const result = await processChunkFile(file, collection, embedder, logger);

          sourceChunks += result.chunksProcessed;
          sourceDocuments += result.documentsAdded;

          logger.debug(`Embedded: ${path.basename(file)} -> ${result.chunksProcessed} chunks`);
        } catch (error) {
          logger.error(`Failed to process ${file}`, error);
        }
      }

      totalChunks += sourceChunks;
      totalDocuments += sourceDocuments;

      collectionStats.push({
        collection: source.collection,
        chunks: sourceChunks,
        documents: sourceDocuments
      });

      // Test query (optional verification)
      logger.info('Testing collection with sample query...');
      const testQuery = 'How do I create a workflow?';
      const testResults = await queryCollection(collection, testQuery, embedder, 3, logger);
      logger.detail(`Sample query returned ${testResults.documents.length} results`);
    }

    // Save embedding summary
    const summaryPath = path.join('kb', 'embed-summary.json');
    const summary = {
      embeddedAt: new Date().toISOString(),
      config: {
        batchSize: config.batchSize,
        source: config.source,
        model: 'Xenova/all-MiniLM-L6-v2',
        dimension: embedder.getDimension()
      },
      totals: {
        chunks: totalChunks,
        documents: totalDocuments
      },
      collections: collectionStats
    };

    await fs.mkdir('kb', { recursive: true });
    await fs.writeFile(summaryPath, JSON.stringify(summary, null, 2), 'utf-8');

    // Final statistics
    logger.step('Summary');
    logger.stats({
      total_chunks: totalChunks,
      total_documents: totalDocuments,
      collections: collectionStats.length,
      embedding_dimension: embedder.getDimension(),
      elapsed_time: logger.getElapsed()
    });

    logger.success(`Summary saved to ${summaryPath}`);
    logger.success('Embedding completed successfully!');

    process.exit(0);
  } catch (error) {
    logger.error('Embedding failed', error);
    process.exit(1);
  }
}

// Run if called directly
import { fileURLToPath } from 'url';
const __filename = fileURLToPath(import.meta.url);
if (process.argv[1] === __filename || process.argv[1].replace(/\\/g, '/') === __filename.replace(/\\/g, '/')) {
  main();
}

export { processChunkFile, getOrCreateCollection, queryCollection };
