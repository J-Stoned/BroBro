"""
Simple FastAPI backend for GHL WHIZ Desktop App
Provides ChromaDB query endpoints
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
from typing import List, Optional

app = FastAPI(title="GHL WHIZ Desktop Backend")

# Enable CORS for desktop app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ChromaDB client - Use HTTP client to connect to running ChromaDB server
try:
    chroma_client = chromadb.HttpClient(host="localhost", port=8001)
    print("[OK] Connected to ChromaDB at localhost:8001")
except Exception as e:
    print(f"[ERROR] ChromaDB connection failed: {e}")
    chroma_client = None

class QueryRequest(BaseModel):
    query: str
    n_results: int = 15  # Return 15 results by default (was 5)

class QueryResult(BaseModel):
    document: str
    metadata: dict
    distance: float

class QueryResponse(BaseModel):
    success: bool
    results: List[QueryResult]
    message: Optional[str] = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "chromadb": "connected" if chroma_client else "disconnected"
    }

@app.post("/query")
async def query_knowledge_base(request: QueryRequest):
    """Query the ChromaDB knowledge base"""
    if not chroma_client:
        raise HTTPException(status_code=503, detail="ChromaDB not available")
    
    try:
        # Search ALL 7 collections comprehensively
        collections_to_search = [
            "ghl-youtube",
            "ghl-best-practices",
            "ghl-tutorials",
            "ghl-docs",
            "ghl-snapshots",
            "ghl-business",
            "ghl-knowledge-base"
        ]
        
        all_results = []
        
        # Get MORE results from each collection (20 per collection = 140 total potential)
        results_per_collection = max(20, request.n_results * 4)
        
        for collection_name in collections_to_search:
            try:
                collection = chroma_client.get_collection(name=collection_name)
                results = collection.query(
                    query_texts=[request.query],
                    n_results=results_per_collection,
                    include=["documents", "metadatas", "distances"]
                )
                
                # Format results with source info
                if results and results['documents'] and results['documents'][0]:
                    for i in range(len(results['documents'][0])):
                        metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                        metadata['collection'] = collection_name  # Track which collection
                        all_results.append({
                            "document": results['documents'][0][i],
                            "metadata": metadata,
                            "distance": results['distances'][0][i] if results['distances'] else 0.0
                        })
            except Exception as e:
                print(f"Could not query {collection_name}: {e}")
                continue
        
        if not all_results:
            return QueryResponse(
                success=True,
                results=[],
                message="No results found in any collection"
            )
        
        # Sort ALL results by relevance (lower distance = better match)
        # BUT boost books and strategic content higher!
        print(f"\n[DEBUG] Processing {len(all_results)} total results...")
        
        for result in all_results:
            meta = result.get('metadata', {})
            source = meta.get('source', '').lower()
            doc_type = meta.get('type', '').lower()
            collection = meta.get('collection', '')
            title = str(meta.get('title', '')).lower()
            
            original_distance = result['distance']
            boost = 0
            
            # Boost priority content (NEGATIVE = moves UP in ranking)
            if doc_type in ['book', 'pdf_book', 'training']:
                boost = -0.5  # STRONG boost for books
            if 'book' in source or 'business' in source:
                boost = -0.5
            if 'hormozi' in title or 'brunson' in title or 'offers' in title:
                boost = -0.6  # Extra boost for known experts
            if collection == 'ghl-knowledge-base' and 'book' in doc_type:
                boost = -0.5
                
            result['distance'] += boost
            
            # Debug: show top boosts
            if boost < 0:
                print(f"  BOOSTED: {meta.get('title', 'unknown')[:50]} | {doc_type} | {original_distance:.3f} -> {result['distance']:.3f}")
        
        all_results.sort(key=lambda x: x['distance'])
        
        # Show what's at the top after sorting
        print(f"\n[DEBUG] Top 5 after boosting:")
        for i, r in enumerate(all_results[:5]):
            print(f"  {i+1}. {r['metadata'].get('title', 'unknown')[:40]} | dist: {r['distance']:.3f}")
        
        # Return requested number of top results (default increased to 15)
        top_results = all_results[:request.n_results]
        
        return QueryResponse(
            success=True,
            results=top_results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("GHL WHIZ Desktop Backend")
    print("=" * 50)
    print("Starting server on http://localhost:8000")
    print("Press CTRL+C to stop")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
