/**
 * Test Embeddings Script
 *
 * Validates the embedding generation and tests sample queries
 */

import { config as dotenvConfig } from 'dotenv';
import { ChromaClient } from 'chromadb';
import { createEmbedder } from './utils/embedder.js';

// Load environment variables
dotenvConfig();

async function main() {
  try {
    console.log('🔍 Testing Embeddings in Chroma Database\n');

    // Initialize ChromaDB client
    const chromaUrl = process.env.CHROMA_URL || 'http://localhost:8001';
    const chromaClient = new ChromaClient({ path: chromaUrl });

    console.log(`✓ Connected to ChromaDB at ${chromaUrl}`);

    // Get collection
    const collection = await chromaClient.getCollection({
      name: 'ghl-knowledge-base'
    });

    console.log(`✓ Retrieved collection: ${collection.name}`);

    // Get collection count
    const count = await collection.count();
    console.log(`✓ Total embeddings in collection: ${count}\n`);

    // Initialize embedder for queries
    console.log('Initializing embedder...');
    const embedder = await createEmbedder();
    console.log('✓ Embedder ready\n');

    // Test queries
    const queries = [
      'How do I create a workflow in GoHighLevel?',
      'What are the best practices for appointment scheduling?',
      'How to set up automated follow-up messages?',
      'What snapshots are available for real estate agents?'
    ];

    console.log('📊 Testing Sample Queries:\n');
    console.log('='.repeat(80) + '\n');

    for (const query of queries) {
      console.log(`Query: "${query}"`);

      // Generate query embedding
      const queryEmbedding = await embedder.generateEmbedding(query);

      // Search collection
      const results = await collection.query({
        queryEmbeddings: [queryEmbedding],
        nResults: 3
      });

      console.log(`\nTop 3 Results:`);

      if (results.documents && results.documents[0]) {
        results.documents[0].forEach((doc, idx) => {
          const metadata = results.metadatas[0][idx];
          const distance = results.distances[0][idx];
          const similarity = (1 - distance).toFixed(4);

          console.log(`\n  ${idx + 1}. Similarity: ${similarity}`);
          console.log(`     Document: ${metadata.documentTitle || 'Unknown'}`);
          console.log(`     Section: ${metadata.section || 'N/A'}`);
          console.log(`     Preview: ${doc.substring(0, 150)}...`);
        });
      }

      console.log('\n' + '-'.repeat(80) + '\n');
    }

    console.log('✅ All tests completed successfully!');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

main();
