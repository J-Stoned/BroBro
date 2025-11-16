#!/usr/bin/env node

/**
 * Initialize Chroma collections for GHL Wiz knowledge base
 *
 * Creates four collections with proper HNSW index configuration:
 * - ghl-docs: GoHighLevel documentation
 * - ghl-tutorials: YouTube tutorial transcripts
 * - ghl-best-practices: Curated best practices
 * - ghl-snapshots: Snapshot marketplace information
 *
 * Usage: npm run init-chroma
 */

import { ChromaClient } from 'chromadb';

const CHROMA_URL = process.env.CHROMA_URL || 'http://localhost:8001';
const EMBEDDING_DIMENSION = 384; // all-MiniLM-L6-v2

// HNSW index configuration for optimal performance
const HNSW_CONFIG = {
  'hnsw:space': 'cosine',          // Cosine similarity for semantic search
  'hnsw:construction_ef': 200,     // Higher = better recall, slower indexing
  'hnsw:search_ef': 100,           // Higher = better recall, slower queries
  'hnsw:M': 16                     // Connections per layer
};

// Collection definitions with metadata schemas
const COLLECTIONS = [
  {
    name: 'ghl-docs',
    description: 'GoHighLevel official documentation',
    estimatedVectors: 5000,
    metadataSchema: {
      doc_title: 'string',
      doc_url: 'string',
      section: 'string',
      category: 'string (workflows|funnels|api|etc)',
      last_updated: 'date'
    }
  },
  {
    name: 'ghl-tutorials',
    description: 'YouTube tutorial transcripts from GHL experts',
    estimatedVectors: 2000,
    metadataSchema: {
      video_title: 'string',
      creator: 'string',
      video_url: 'string',
      timestamp: 'string',
      duration: 'integer',
      publish_date: 'date',
      topics: 'array<string>'
    }
  },
  {
    name: 'ghl-best-practices',
    description: 'Curated best practices and guides',
    estimatedVectors: 500,
    metadataSchema: {
      practice_title: 'string',
      category: 'string',
      source: 'string',
      effectiveness: 'string (proven|experimental)'
    }
  },
  {
    name: 'ghl-snapshots',
    description: 'Snapshot marketplace information',
    estimatedVectors: 200,
    metadataSchema: {
      snapshot_name: 'string',
      marketplace: 'string (extendly|ghl-central|etc)',
      features: 'array<string>',
      pricing: 'string',
      use_cases: 'array<string>'
    }
  }
];

async function initializeCollections() {
  console.log('🚀 Initializing Chroma collections for GHL Wiz...\n');
  console.log(`📍 Chroma URL: ${CHROMA_URL}`);
  console.log(`📐 Embedding Dimension: ${EMBEDDING_DIMENSION}\n`);

  try {
    // Connect to Chroma
    const client = new ChromaClient({ path: CHROMA_URL });

    // Test connection
    console.log('🔌 Testing connection to Chroma...');
    const heartbeat = await client.heartbeat();
    console.log(`✅ Connected! Heartbeat: ${heartbeat}ms\n`);

    // Get existing collections
    const existingCollections = await client.listCollections();
    const existingNames = existingCollections.map(c => c.name);

    console.log(`📋 Found ${existingCollections.length} existing collection(s)\n`);

    // Create or verify each collection
    for (const collectionDef of COLLECTIONS) {
      console.log(`\n📦 Processing collection: ${collectionDef.name}`);
      console.log(`   Description: ${collectionDef.description}`);
      console.log(`   Estimated vectors: ~${collectionDef.estimatedVectors.toLocaleString()}`);

      try {
        let collection;

        if (existingNames.includes(collectionDef.name)) {
          console.log(`   ℹ️  Collection already exists, retrieving...`);
          collection = await client.getCollection({
            name: collectionDef.name
          });

          // Get collection count
          const count = await collection.count();
          console.log(`   📊 Current document count: ${count.toLocaleString()}`);
        } else {
          console.log(`   ✨ Creating new collection...`);
          collection = await client.createCollection({
            name: collectionDef.name,
            metadata: {
              ...HNSW_CONFIG,
              description: collectionDef.description,
              embedding_dimension: EMBEDDING_DIMENSION
            }
          });
          console.log(`   ✅ Created successfully!`);
        }

        // Display metadata schema for reference
        console.log(`   📋 Metadata schema:`);
        for (const [field, type] of Object.entries(collectionDef.metadataSchema)) {
          console.log(`      - ${field}: ${type}`);
        }

      } catch (error) {
        console.error(`   ❌ Error processing collection ${collectionDef.name}:`, error.message);
        throw error;
      }
    }

    // Final summary
    console.log('\n\n✅ Collection initialization complete!');
    console.log('\n📊 Summary:');
    const finalCollections = await client.listCollections();
    for (const collection of finalCollections) {
      const col = await client.getCollection({ name: collection.name });
      const count = await col.count();
      console.log(`   - ${collection.name}: ${count.toLocaleString()} documents`);
    }

    console.log(`\n📈 Total estimated capacity: ~${COLLECTIONS.reduce((sum, c) => sum + c.estimatedVectors, 0).toLocaleString()} vectors`);
    console.log(`💾 Estimated storage: ~11 MB (when fully populated)`);

    console.log('\n🎉 Chroma is ready for knowledge base population!');
    console.log('Next steps:');
    console.log('  1. Run: npm run scrape-docs');
    console.log('  2. Run: npm run extract-yt');
    console.log('  3. Run: npm run chunk-docs');
    console.log('  4. Run: npm run embed-content');
    console.log('  Or run all at once: npm run build-kb\n');

  } catch (error) {
    console.error('\n❌ Failed to initialize Chroma collections:');
    console.error(`   Error: ${error.message}`);

    if (error.message.includes('ECONNREFUSED') || error.message.includes('fetch failed')) {
      console.error('\n💡 Troubleshooting:');
      console.error('   - Is Chroma running? Start with: npm run start-chroma');
      console.error('   - Check Docker Desktop is running');
      console.error('   - Verify Chroma is accessible at: http://localhost:8000');
      console.error('   - Check logs with: npm run chroma-logs');
    }

    process.exit(1);
  }
}

// Run initialization
initializeCollections();
