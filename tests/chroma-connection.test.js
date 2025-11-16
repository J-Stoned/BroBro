#!/usr/bin/env node

/**
 * Chroma Connection and Functionality Tests
 *
 * Tests:
 * - Connection to Chroma server
 * - Collection operations (create, list, retrieve)
 * - Document operations (add, query, delete)
 * - Semantic search with cosine similarity
 * - Metadata filtering
 * - Performance benchmarks
 *
 * Usage: npm run test:chroma
 */

import { ChromaClient } from 'chromadb';

const CHROMA_URL = process.env.CHROMA_URL || 'http://localhost:8001';
const TEST_COLLECTION_NAME = 'ghl-wiz-test-collection';

// Test utilities
let testsPassed = 0;
let testsFailed = 0;

function assert(condition, message) {
  if (condition) {
    console.log(`   ✅ ${message}`);
    testsPassed++;
  } else {
    console.error(`   ❌ ${message}`);
    testsFailed++;
    throw new Error(`Assertion failed: ${message}`);
  }
}

function assertLessThan(actual, expected, message) {
  if (actual < expected) {
    console.log(`   ✅ ${message} (${actual}ms < ${expected}ms)`);
    testsPassed++;
  } else {
    console.error(`   ❌ ${message} (${actual}ms >= ${expected}ms)`);
    testsFailed++;
  }
}

async function runTests() {
  console.log('🧪 Chroma Connection and Functionality Tests\n');
  console.log(`📍 Testing against: ${CHROMA_URL}\n`);

  let client;
  let testCollection;

  try {
    // Test 1: Connection
    console.log('📝 Test 1: Connection Establishment');
    const startTime = Date.now();
    client = new ChromaClient({ path: CHROMA_URL });
    const heartbeat = await client.heartbeat();
    const connectionTime = Date.now() - startTime;

    assert(heartbeat !== undefined, 'Heartbeat response received');
    assert(typeof heartbeat === 'number', 'Heartbeat is a number');
    assertLessThan(connectionTime, 1000, 'Connection established quickly');
    console.log('');

    // Test 2: Collection Creation
    console.log('📝 Test 2: Collection Creation');
    try {
      // Clean up if test collection exists
      await client.deleteCollection({ name: TEST_COLLECTION_NAME });
    } catch (e) {
      // Collection doesn't exist, that's fine
    }

    const createStart = Date.now();
    testCollection = await client.createCollection({
      name: TEST_COLLECTION_NAME,
      metadata: {
        'hnsw:space': 'cosine',
        'hnsw:M': 16
      }
    });
    const createTime = Date.now() - createStart;

    assert(testCollection !== undefined, 'Collection created');
    assert(testCollection.name === TEST_COLLECTION_NAME, 'Collection has correct name');
    assertLessThan(createTime, 1000, 'Collection created quickly');
    console.log('');

    // Test 3: Collection Listing
    console.log('📝 Test 3: Collection Listing');
    const collections = await client.listCollections();
    const testCollectionExists = collections.some(c => c.name === TEST_COLLECTION_NAME);

    assert(Array.isArray(collections), 'Collections list is an array');
    assert(testCollectionExists, 'Test collection appears in list');
    console.log('');

    // Test 4: Document Addition
    console.log('📝 Test 4: Document Addition with Embeddings');

    // Generate sample 384-dimensional embeddings (normally from all-MiniLM-L6-v2)
    const sampleEmbedding1 = Array(384).fill(0).map(() => Math.random());
    const sampleEmbedding2 = Array(384).fill(0).map(() => Math.random());

    const addStart = Date.now();
    await testCollection.add({
      ids: ['test-doc-1', 'test-doc-2'],
      embeddings: [sampleEmbedding1, sampleEmbedding2],
      documents: [
        'This is a test document about GoHighLevel workflows',
        'This document describes funnel automation in GHL'
      ],
      metadatas: [
        { category: 'workflows', source: 'test' },
        { category: 'funnels', source: 'test' }
      ]
    });
    const addTime = Date.now() - addStart;

    const count = await testCollection.count();
    assert(count === 2, `Collection contains 2 documents (got ${count})`);
    assertLessThan(addTime, 2000, 'Documents added within 2 seconds');
    console.log('');

    // Test 5: Semantic Search Query
    console.log('📝 Test 5: Semantic Search Query');

    const queryEmbedding = Array(384).fill(0).map(() => Math.random());
    const queryStart = Date.now();
    const results = await testCollection.query({
      queryEmbeddings: [queryEmbedding],
      nResults: 2
    });
    const queryTime = Date.now() - queryStart;

    assert(results.ids !== undefined, 'Query returned results');
    assert(results.ids.length > 0, 'Query returned at least one result');
    assertLessThan(queryTime, 100, 'Query completed in <100ms');
    console.log('');

    // Test 6: Metadata Filtering
    console.log('📝 Test 6: Metadata Filtering');

    const filterStart = Date.now();
    const filteredResults = await testCollection.query({
      queryEmbeddings: [queryEmbedding],
      nResults: 5,
      where: { category: 'workflows' }
    });
    const filterTime = Date.now() - filterStart;

    assert(filteredResults.ids !== undefined, 'Filtered query returned results');
    assert(filteredResults.metadatas[0].every(m => m.category === 'workflows'),
      'All results match metadata filter');
    assertLessThan(filterTime, 500, 'Filtered query completed in <500ms');
    console.log('');

    // Test 7: Collection Retrieval
    console.log('📝 Test 7: Collection Retrieval');
    const retrievedCollection = await client.getCollection({
      name: TEST_COLLECTION_NAME
    });

    assert(retrievedCollection.name === TEST_COLLECTION_NAME, 'Retrieved correct collection');
    const retrievedCount = await retrievedCollection.count();
    assert(retrievedCount === 2, 'Retrieved collection has correct document count');
    console.log('');

    // Test 8: Document Deletion
    console.log('📝 Test 8: Document Deletion');
    await testCollection.delete({
      ids: ['test-doc-1']
    });

    const finalCount = await testCollection.count();
    assert(finalCount === 1, `One document deleted (count: ${finalCount})`);
    console.log('');

    // Cleanup
    console.log('🧹 Cleaning up test collection...');
    await client.deleteCollection({ name: TEST_COLLECTION_NAME });
    console.log('   ✅ Test collection deleted\n');

    // Summary
    console.log('═'.repeat(50));
    console.log('📊 Test Summary');
    console.log('═'.repeat(50));
    console.log(`✅ Tests passed: ${testsPassed}`);
    console.log(`❌ Tests failed: ${testsFailed}`);
    console.log(`📈 Success rate: ${((testsPassed / (testsPassed + testsFailed)) * 100).toFixed(1)}%`);
    console.log('');

    if (testsFailed === 0) {
      console.log('🎉 All tests passed! Chroma is working correctly.\n');
      process.exit(0);
    } else {
      console.log('⚠️  Some tests failed. Please check configuration.\n');
      process.exit(1);
    }

  } catch (error) {
    console.error('\n❌ Test execution failed:');
    console.error(`   Error: ${error.message}`);

    if (error.message.includes('ECONNREFUSED') || error.message.includes('fetch failed')) {
      console.error('\n💡 Troubleshooting:');
      console.error('   - Is Chroma running? Start with: npm run start-chroma');
      console.error('   - Check Docker Desktop is running');
      console.error('   - Verify Chroma is accessible at: http://localhost:8000');
      console.error('   - Check logs with: npm run chroma-logs');
    }

    // Try to cleanup even if tests failed
    if (client && testCollection) {
      try {
        await client.deleteCollection({ name: TEST_COLLECTION_NAME });
      } catch (e) {
        // Ignore cleanup errors
      }
    }

    console.log('');
    console.log(`✅ Tests passed: ${testsPassed}`);
    console.log(`❌ Tests failed: ${testsFailed + 1}\n`);

    process.exit(1);
  }
}

// Run tests
runTests();
