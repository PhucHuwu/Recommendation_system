"""
Script to build FAISS index for anime vector search

This script:
1. Loads all anime from MongoDB
2. Generates embeddings using sentence-transformers
3. Builds FAISS index
4. Saves index and embeddings to disk
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from pymongo import MongoClient
from dotenv import load_dotenv
from ml.services.embedding_service import EmbeddingService
from ml.services.faiss_service import FAISSService

# Load environment
load_dotenv()

# Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DB = os.getenv('MONGODB_DB', 'anime_recommendation')
MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'

# Use absolute paths based on backend directory
FAISS_INDEX_PATH = str(BACKEND_DIR / 'ml' / 'saved_models' / 'faiss_index.bin')
EMBEDDINGS_PATH = str(BACKEND_DIR / 'ml' / 'saved_models' / 'anime_embeddings.pkl')


def main():
    """Main function to build FAISS index"""
    print("=" * 70)
    print("Building FAISS Index for Anime Vector Search")
    print("=" * 70)
    
    try:
        # Step 1: Connect to MongoDB
        print("\n[1/5] Connecting to MongoDB...")
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.server_info()  # Test connection
        db = client[MONGODB_DB]
        print(f"[OK] Connected to MongoDB: {MONGODB_DB}")
        
        # Step 2: Load anime data
        print("\n[2/5] Loading anime data from MongoDB...")
        animes = list(db.animes.find({}, {'_id': 0, 'mal_id': 1, 'name': 1, 
                                           'synopsis': 1, 'genres': 1}))
        
        if not animes:
            print("[ERROR] No anime found in database!")
            print("Please run scripts/import_data.py first to import anime data.")
            sys.exit(1)
        
        print(f"[OK] Loaded {len(animes)} anime from database")
        
        # Step 3: Generate embeddings
        print("\n[3/5] Generating embeddings...")
        print(f"Using model: {MODEL_NAME}")
        print("This may take a few minutes...")
        
        embedding_service = EmbeddingService(model_name=MODEL_NAME)
        embeddings = embedding_service.generate_anime_embeddings(animes, batch_size=32)
        
        # Extract anime IDs
        anime_ids = [anime['mal_id'] for anime in animes]
        
        print(f"[OK] Generated embeddings: shape {embeddings.shape}")
        
        # Save embeddings to file
        print(f"\nSaving embeddings to {EMBEDDINGS_PATH}...")
        embedding_service.save_embeddings(embeddings, anime_ids, EMBEDDINGS_PATH)
        print("[OK] Embeddings saved")
        
        # Step 4: Build FAISS index
        print("\n[4/5] Building FAISS index...")
        faiss_service = FAISSService(embedding_dim=embedding_service.embedding_dim)
        faiss_service.build_index(embeddings, anime_ids, index_type='flat')
        print("[OK] FAISS index built")
        
        # Step 5: Save FAISS index
        print(f"\n[5/5] Saving FAISS index to {FAISS_INDEX_PATH}...")
        faiss_service.save(FAISS_INDEX_PATH)
        print("[OK] FAISS index saved")
        
        # Stats
        print("\n" + "=" * 70)
        print("Build Complete!")
        print("=" * 70)
        stats = faiss_service.get_stats()
        print(f"Total anime indexed: {stats['total_anime']}")
        print(f"Embedding dimension: {stats['embedding_dim']}")
        print(f"Index file: {FAISS_INDEX_PATH}")
        print(f"Embeddings file: {EMBEDDINGS_PATH}")
        
        # Test search
        print("\n" + "=" * 70)
        print("Testing search functionality...")
        print("=" * 70)
        
        # Test with a sample query
        test_query = "anime hành động với phép thuật"
        print(f"\nTest query: '{test_query}'")
        
        query_embedding = embedding_service.generate_embedding(test_query)
        result_ids, distances = faiss_service.search(query_embedding, k=5)
        
        print(f"\nTop 5 results:")
        for i, (anime_id, distance) in enumerate(zip(result_ids, distances), 1):
            anime = db.animes.find_one({'mal_id': anime_id}, {'name': 1, 'genres': 1})
            print(f"{i}. {anime['name']}")
            print(f"   Genres: {anime.get('genres', 'N/A')}")
            print(f"   Distance: {distance:.4f}")
        
        print("\n[OK] Search test completed successfully!")
        
        client.close()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
