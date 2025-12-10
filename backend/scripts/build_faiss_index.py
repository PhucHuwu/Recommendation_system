"""
Build FAISS Index Script

This script:
1. Loads all anime from MongoDB
2. Generates embeddings using sentence-transformers
3. Builds FAISS index for similarity search
4. Saves embeddings and index to disk
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from pymongo import MongoClient
from dotenv import load_dotenv
from ml.services.embedding_service import EmbeddingService
from ml.services.faiss_service import FAISSService

# Load environment variables
load_dotenv()

# Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DB = os.getenv('MONGODB_DB', 'anime_recommendation')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
EMBEDDINGS_PATH = os.getenv('EMBEDDINGS_PATH', 'ml/saved_models/anime_embeddings.pkl')
FAISS_INDEX_PATH = os.getenv('FAISS_INDEX_PATH', 'ml/saved_models/faiss_index.bin')
EMBEDDING_DIM = 384


def main():
    """Main function to build FAISS index"""
    print("=" * 70)
    print("Building FAISS Index for Vector Search")
    print("=" * 70)
    print()
    
    # Step 1: Connect to MongoDB
    print("[1/5] Connecting to MongoDB...")
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.server_info()
        db = client[MONGODB_DB]
        print(f"Connected to {MONGODB_DB}")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)
    
    # Step 2: Load anime data
    print("\n[2/5] Loading anime data...")
    animes = list(db.animes.find({}, {
        'mal_id': 1,
        'name': 1,
        'synopsis': 1,
        'genres': 1,
        '_id': 0
    }))
    
    if not animes:
        print("No anime found in database")
        sys.exit(1)
    
    print(f"Loaded {len(animes)} anime")
    
    # Step 3: Generate embeddings
    print(f"\n[3/5] Generating embeddings using {EMBEDDING_MODEL}...")
    embedding_service = EmbeddingService(model_name=EMBEDDING_MODEL)
    
    embeddings, anime_ids = embedding_service.generate_anime_embeddings(
        animes,
        batch_size=32,
        show_progress=True
    )
    
    print(f"Generated embeddings: shape {embeddings.shape}")
    
    # Save embeddings to file
    print(f"\nSaving embeddings to {EMBEDDINGS_PATH}...")
    embedding_service.save_embeddings(embeddings, anime_ids, EMBEDDINGS_PATH)
    print("Embeddings saved")
    
    # Step 4: Build FAISS index
    print(f"\n[4/5] Building FAISS index...")
    faiss_service = FAISSService(embedding_dim=EMBEDDING_DIM)
    faiss_service.build_index(embeddings, anime_ids, index_type='flat')
    print("FAISS index built")
    
    # Step 5: Save FAISS index
    print(f"\n[5/5] Saving FAISS index to {FAISS_INDEX_PATH}...")
    faiss_service.save(FAISS_INDEX_PATH)
    print("FAISS index saved")
    
    # Summary
    print("\n" + "=" * 70)
    print("[OK] Build Complete!")
    print("=" * 70)
    print(f"\nIndex Statistics:")
    stats = faiss_service.get_stats()
    print(f"  - Total vectors: {stats['total_vectors']}")
    print(f"  - Embedding dimension: {stats['embedding_dim']}")
    print(f"  - Index type: {stats['index_type']}")
    print(f"\nFiles created:")
    print(f"  - {EMBEDDINGS_PATH}")
    print(f"  - {FAISS_INDEX_PATH}")
    print(f"  - {FAISS_INDEX_PATH}.meta")
    print("\nYou can now use the vector search API!")
    print()
    
    client.close()


if __name__ == '__main__':
    main()
