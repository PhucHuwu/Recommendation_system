"""
Script to download dataset from Kaggle and import into MongoDB

Dataset: hernan4444/anime-recommendation-database-2020
Files used:
- anime_with_synopsis.csv
- rating_complete.csv (limited to 3 million samples)
"""

import os
import sys
import kagglehub
import pandas as pd
from pymongo import MongoClient
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DB = os.getenv('MONGODB_DB', 'anime_recommendation')

# Rating limit (3 million as per requirements)
RATING_LIMIT = 3_000_000


def download_dataset():
    """Download dataset from Kaggle using kagglehub"""
    print("Downloading dataset from Kaggle...")
    
    # Download using kagglehub (correct API)
    path = kagglehub.dataset_download("hernan4444/anime-recommendation-database-2020")
    
    print(f"Dataset downloaded to: {path}")
    return path


def find_csv_file(dataset_path, filename):
    """Find CSV file in dataset directory"""
    # Try direct path first
    direct_path = os.path.join(dataset_path, filename)
    if os.path.exists(direct_path):
        return direct_path
    
    # Search recursively
    for root, dirs, files in os.walk(dataset_path):
        if filename in files:
            return os.path.join(root, filename)
    
    raise FileNotFoundError(f"Could not find {filename} in {dataset_path}")


def load_anime_data(dataset_path):
    """Load anime_with_synopsis.csv"""
    print(f"Loading anime data...")
    
    anime_file = find_csv_file(dataset_path, 'anime_with_synopsis.csv')
    print(f"Found: {anime_file}")
    
    df = pd.read_csv(anime_file)
    print(f"Loaded {len(df)} animes")
    return df


def load_rating_data(dataset_path, limit=RATING_LIMIT):
    """Load rating_complete.csv with limit"""
    print(f"Loading rating data...")
    print(f"Limiting to {limit:,} ratings...")
    
    rating_file = find_csv_file(dataset_path, 'rating_complete.csv')
    print(f"Found: {rating_file}")
    
    df = pd.read_csv(rating_file, nrows=limit)
    print(f"Loaded {len(df):,} ratings")
    return df


def clean_anime_data(df):
    """Clean and preprocess anime data"""
    print("Cleaning anime data...")
    
    # Rename columns to match our schema
    df = df.rename(columns={
        'MAL_ID': 'mal_id',
        'Name': 'name',
        'Score': 'score',
        'Genres': 'genres',
        'sypnopsis': 'synopsis'  # Note: typo in original dataset
    })
    
    # Handle missing values
    df['synopsis'] = df['synopsis'].fillna('')
    df['genres'] = df['genres'].fillna('')
    df['score'] = pd.to_numeric(df['score'], errors='coerce').fillna(0)
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['mal_id'])
    
    # Remove rows with missing critical fields
    df = df.dropna(subset=['mal_id', 'name'])
    
    # Convert mal_id to int
    df['mal_id'] = df['mal_id'].astype(int)
    
    print(f"Cleaned anime data: {len(df)} records")
    return df


def clean_rating_data(df):
    """Clean and preprocess rating data"""
    print("Cleaning rating data...")
    
    # Ensure columns exist
    if 'user_id' not in df.columns or 'anime_id' not in df.columns or 'rating' not in df.columns:
        print(f"Columns in dataframe: {df.columns.tolist()}")
        raise ValueError("Missing required columns in rating data")
    
    # Remove ratings of -1 (not rated)
    df = df[df['rating'] != -1]
    
    # Ensure rating is in 1-10 range
    df = df[(df['rating'] >= 1) & (df['rating'] <= 10)]
    
    # Remove duplicates (keep first)
    df = df.drop_duplicates(subset=['user_id', 'anime_id'], keep='first')
    
    # Ensure numeric types
    df['user_id'] = df['user_id'].astype(int)
    df['anime_id'] = df['anime_id'].astype(int)
    df['rating'] = df['rating'].astype(int)
    
    print(f"Cleaned rating data: {len(df):,} records")
    return df


def import_to_mongodb(anime_df, rating_df):
    """Import data into MongoDB"""
    print(f"Connecting to MongoDB: {MONGODB_URI}")
    
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        # Test connection
        client.server_info()
        print("Connected to MongoDB")
    except Exception as e:
        print(f"Could not connect to MongoDB: {e}")
        print("Make sure MongoDB is running at localhost:27017")
        sys.exit(1)
    
    db = client[MONGODB_DB]
    
    # Clear existing data
    print("Clearing existing data...")
    db.animes.delete_many({})
    db.ratings.delete_many({})
    
    # Import animes
    print("Importing animes...")
    anime_records = anime_df.to_dict('records')
    if anime_records:
        db.animes.insert_many(anime_records)
    print(f"Imported {len(anime_records)} animes")
    
    # Create indexes on animes
    print("Creating indexes on animes...")
    db.animes.create_index('mal_id', unique=True)
    db.animes.create_index('name')
    db.animes.create_index('score')
    
    # Import ratings in batches
    print("Importing ratings...")
    rating_records = rating_df.to_dict('records')
    batch_size = 10000
    
    for i in tqdm(range(0, len(rating_records), batch_size), desc="Importing ratings"):
        batch = rating_records[i:i + batch_size]
        db.ratings.insert_many(batch)
    
    print(f"Imported {len(rating_records):,} ratings")
    
    # Create indexes on ratings
    print("Creating indexes on ratings...")
    db.ratings.create_index('user_id')
    db.ratings.create_index('anime_id')
    db.ratings.create_index([('user_id', 1), ('anime_id', 1)], unique=True)
    
    # Print stats
    print("\nDatabase Stats:")
    print(f"   - Animes: {db.animes.count_documents({})}")
    print(f"   - Ratings: {db.ratings.count_documents({})}")
    print(f"   - Unique Users: {len(rating_df['user_id'].unique()):,}")
    
    client.close()
    print("Import complete!")


def main():
    """Main function"""
    print("=" * 60)
    print("Anime Recommendation System - Data Import Script")
    print("=" * 60)
    
    try:
        # Step 1: Download dataset
        dataset_path = download_dataset()
        
        # Step 2: Load data
        anime_df = load_anime_data(dataset_path)
        rating_df = load_rating_data(dataset_path)
        
        # Step 3: Clean data
        anime_df = clean_anime_data(anime_df)
        rating_df = clean_rating_data(rating_df)
        
        # Step 4: Import to MongoDB
        import_to_mongodb(anime_df, rating_df)
        
        print("\n" + "=" * 60)
        print("All done! Data is ready in MongoDB.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
