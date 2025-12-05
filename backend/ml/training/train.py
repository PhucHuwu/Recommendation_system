"""
Training Pipeline for ML Models

Train all recommendation models and save them.
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)

from ml.models.user_based import UserBasedCF
from ml.models.item_based import ItemBasedCF
from ml.models.content_based import ContentBasedCF

# Load environment
load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DB = os.getenv('MONGODB_DB', 'anime_recommendation')

# Paths
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'saved_models')
os.makedirs(MODELS_DIR, exist_ok=True)


def load_data_from_mongodb():
    """Load training data from MongoDB"""
    print("=" * 60)
    print("Loading data from MongoDB...")
    print("=" * 60)
    
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    
    # Load ratings
    print("Loading ratings...")
    ratings_cursor = db.ratings.find({}, {'_id': 0, 'user_id': 1, 'anime_id': 1, 'rating': 1})
    ratings_data = list(ratings_cursor)
    print(f"  Loaded {len(ratings_data):,} ratings")
    
    # Load animes
    print("Loading animes...")
    animes_cursor = db.animes.find({}, {'_id': 0, 'mal_id': 1, 'name': 1, 'genres': 1, 'synopsis': 1})
    animes_data = list(animes_cursor)
    print(f"  Loaded {len(animes_data):,} animes")
    
    client.close()
    
    return ratings_data, animes_data


def train_user_based_cf(ratings_data):
    """Train User-Based Collaborative Filtering"""
    print("\n" + "=" * 60)
    print("TRAINING: User-Based CF")
    print("=" * 60)
    
    model = UserBasedCF(k_neighbors=50)
    model.fit(ratings_data)
    
    # Save model
    model_path = os.path.join(MODELS_DIR, 'user_based_cf.pkl')
    model.save(model_path)
    
    return model


def train_item_based_cf(ratings_data):
    """Train Item-Based Collaborative Filtering"""
    print("\n" + "=" * 60)
    print("TRAINING: Item-Based CF")
    print("=" * 60)
    
    model = ItemBasedCF(k_similar=30)
    model.fit(ratings_data)
    
    # Save model
    model_path = os.path.join(MODELS_DIR, 'item_based_cf.pkl')
    model.save(model_path)
    
    return model


def train_content_based(animes_data):
    """Train Content-Based Filtering"""
    print("\n" + "=" * 60)
    print("TRAINING: Content-Based")
    print("=" * 60)
    
    model = ContentBasedCF(use_synopsis=True, use_genres=True)
    model.fit(animes_data)
    
    # Save model
    model_path = os.path.join(MODELS_DIR, 'content_based.pkl')
    model.save(model_path)
    
    return model


def update_model_registry(model_name, metrics=None):
    """Update model registry in MongoDB"""
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    
    model_path = os.path.join(MODELS_DIR, f'{model_name}.pkl')
    
    db.models.update_one(
        {'name': model_name},
        {
            '$set': {
                'name': model_name,
                'trained_at': datetime.utcnow(),
                'file_path': model_path,
                'status': 'trained',
                'metrics': metrics or {}
            },
            '$setOnInsert': {
                'created_at': datetime.utcnow(),
                'is_active': False
            }
        },
        upsert=True
    )
    
    client.close()
    print(f"  Updated model registry for {model_name}")


def main():
    """Main training pipeline"""
    print("\n" + "=" * 60)
    print("RECOMMENDATION SYSTEM - TRAINING PIPELINE")
    print("=" * 60)
    
    try:
        # Load data
        ratings_data, animes_data = load_data_from_mongodb()
        
        # Train User-Based CF
        user_based_model = train_user_based_cf(ratings_data)
        update_model_registry('user_based_cf')
        
        # Train Item-Based CF
        item_based_model = train_item_based_cf(ratings_data)
        update_model_registry('item_based_cf')
        
        # Train Content-Based
        content_based_model = train_content_based(animes_data)
        update_model_registry('content_based')
        
        print("\n" + "=" * 60)
        print("TRAINING COMPLETE!")
        print("=" * 60)
        print(f"\nModels saved to: {MODELS_DIR}")
        print("\nTrained models:")
        print("  - user_based_cf.pkl")
        print("  - item_based_cf.pkl")
        print("  - content_based.pkl")
        
    except Exception as e:
        print(f"\nError during training: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
