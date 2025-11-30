"""
Data Collector Module for Movie Recommendation System

Thu thập dữ liệu phim từ MovieLens dataset.
"""

import os
import urllib.request
import zipfile
from pathlib import Path
import pandas as pd
from tqdm import tqdm


class DownloadProgressBar(tqdm):
    """Progress bar cho download"""
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


class MovieDataCollector:
    """
    Class để thu thập dữ liệu phim từ MovieLens dataset.
    
    MovieLens cung cấp nhiều kích thước dataset:
    - Small: 100,000 ratings và 3,600 tag applications cho 9,000 phim
    - 25M: 25 million ratings và 1 million tag applications cho 62,000 phim
    """
    
    # URLs cho các dataset khác nhau
    DATASETS = {
        'small': 'https://files.grouplens.org/datasets/movielens/ml-latest-small.zip',
        '25m': 'https://files.grouplens.org/datasets/movielens/ml-25m.zip',
        'latest': 'https://files.grouplens.org/datasets/movielens/ml-latest.zip'
    }
    
    def __init__(self, data_dir='data/raw'):
        """
        Initialize collector
        
        Args:
            data_dir: Thư mục lưu dữ liệu raw
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def download_dataset(self, dataset_type='small'):
        """
        Download MovieLens dataset
        
        Args:
            dataset_type: Loại dataset ('small', '25m', 'latest')
        
        Returns:
            Path to extracted dataset directory
        """
        if dataset_type not in self.DATASETS:
            raise ValueError(f"Dataset type must be one of {list(self.DATASETS.keys())}")
        
        url = self.DATASETS[dataset_type]
        filename = url.split('/')[-1]
        filepath = self.data_dir / filename
        
        # Download nếu chưa có
        if not filepath.exists():
            print(f"Downloading {dataset_type} dataset from {url}...")
            with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=filename) as t:
                urllib.request.urlretrieve(url, filepath, reporthook=t.update_to)
            print(f"Downloaded to {filepath}")
        else:
            print(f"Dataset already exists at {filepath}")
        
        # Extract zip file
        extract_dir = self.data_dir / filename.replace('.zip', '')
        if not extract_dir.exists():
            print(f"Extracting {filename}...")
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(self.data_dir)
            print(f"Extracted to {extract_dir}")
        else:
            print(f"Dataset already extracted at {extract_dir}")
        
        return extract_dir
    
    def load_movies(self, dataset_dir):
        """
        Load movies data
        
        Args:
            dataset_dir: Path to dataset directory
        
        Returns:
            DataFrame with movies data
        """
        movies_file = Path(dataset_dir) / 'movies.csv'
        if not movies_file.exists():
            raise FileNotFoundError(f"Movies file not found at {movies_file}")
        
        df = pd.read_csv(movies_file)
        print(f"Loaded {len(df)} movies")
        return df
    
    def load_ratings(self, dataset_dir):
        """
        Load ratings data
        
        Args:
            dataset_dir: Path to dataset directory
        
        Returns:
            DataFrame with ratings data
        """
        ratings_file = Path(dataset_dir) / 'ratings.csv'
        if not ratings_file.exists():
            raise FileNotFoundError(f"Ratings file not found at {ratings_file}")
        
        df = pd.read_csv(ratings_file)
        print(f"Loaded {len(df)} ratings")
        return df
    
    def load_tags(self, dataset_dir):
        """
        Load tags data (if available)
        
        Args:
            dataset_dir: Path to dataset directory
        
        Returns:
            DataFrame with tags data or None
        """
        tags_file = Path(dataset_dir) / 'tags.csv'
        if not tags_file.exists():
            print("Tags file not found")
            return None
        
        df = pd.read_csv(tags_file)
        print(f"Loaded {len(df)} tags")
        return df
    
    def load_links(self, dataset_dir):
        """
        Load links data (IMDb and TMDB IDs)
        
        Args:
            dataset_dir: Path to dataset directory
        
        Returns:
            DataFrame with links data or None
        """
        links_file = Path(dataset_dir) / 'links.csv'
        if not links_file.exists():
            print("Links file not found")
            return None
        
        df = pd.read_csv(links_file)
        print(f"Loaded {len(df)} links")
        return df
    
    def get_dataset_info(self, dataset_dir):
        """
        Get thông tin tổng quan về dataset
        
        Args:
            dataset_dir: Path to dataset directory
        
        Returns:
            Dictionary with dataset information
        """
        movies = self.load_movies(dataset_dir)
        ratings = self.load_ratings(dataset_dir)
        tags = self.load_tags(dataset_dir)
        links = self.load_links(dataset_dir)
        
        info = {
            'num_movies': len(movies),
            'num_ratings': len(ratings),
            'num_users': ratings['userId'].nunique(),
            'num_tags': len(tags) if tags is not None else 0,
            'movies_columns': list(movies.columns),
            'ratings_columns': list(ratings.columns),
            'avg_rating': ratings['rating'].mean(),
            'rating_range': (ratings['rating'].min(), ratings['rating'].max())
        }
        
        return info


def main():
    """Main function để test collector"""
    collector = MovieDataCollector()
    
    # Download small dataset (tốt cho development)
    print("=" * 50)
    print("DOWNLOADING MOVIELENS DATASET")
    print("=" * 50)
    
    dataset_dir = collector.download_dataset('small')
    
    print("\n" + "=" * 50)
    print("DATASET INFORMATION")
    print("=" * 50)
    
    info = collector.get_dataset_info(dataset_dir)
    
    for key, value in info.items():
        print(f"{key}: {value}")
    
    print("\n✅ Data collection completed successfully!")
    print(f"📁 Data saved to: {dataset_dir}")


if __name__ == "__main__":
    main()
