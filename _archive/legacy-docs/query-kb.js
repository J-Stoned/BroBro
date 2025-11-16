import { ChromaClient } from 'chromadb';

async function queryKB() {
  try {
    console.log('🔍 Connecting to Chroma...\n');
    
    const client = new ChromaClient({
      host: 'localhost',
      port: 8001
    });
    
    const collection = await client.getCollection({ name: 'ghl-knowledge-base' });
    console.log('✅ Connected to knowledge base\n');
    
    console.log('📚 Searching for: form email notifications, merge fields\n');
    
    const results = await collection.query({
      queryTexts: ['form email notification merge fields dynamic content'],
      nResults: 5,
      include: ['documents', 'distances']
    });
    
    console.log('='.repeat(80));
    console.log('KNOWLEDGE BASE RESULTS');
    console.log('='.repeat(80));
    
    if (results.documents && results.documents[0]) {
      results.documents[0].forEach((doc, idx) => {
        console.log(`\n[RESULT ${idx + 1}]`);
        console.log('-'.repeat(80));
        console.log(doc.substring(0, 500) + (doc.length > 500 ? '...' : ''));
        console.log('-'.repeat(80));
      });
    } else {
      console.log('No results found');
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

queryKB();