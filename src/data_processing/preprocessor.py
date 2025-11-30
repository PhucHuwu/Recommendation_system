"""
Data Preprocessor Module for Movie Recommendation System

Feature engineering và text vectorization.
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
import re


class MovieDataPreprocessor:
    """
    Class để preprocessing dữ liệu phim.
    
    Thực hiện:
    - Feature engineering (extract year, parse genres)
    - Text vectorization (TF-IDF, BoW)
    - Encoding categorical features
    """
    
    def __init__(self, verbose=True):
        """
        Initialize preprocessor
        
        Args:
            verbose: In thông tin chi tiết
        """
        self.verbose = verbose
        self.tfidf_vectorizer = None
        self.count_vectorizer = None
        self.mlb = None
    
    def _log(self, message):
        """Print message nếu verbose=True"""
        if self.verbose:
            print(message)
    
    def extract_year_from_title(self, df, title_column='title', year_column='year'):
        """
        Extract năm phát hành từ title
        
        Args:
            df: DataFrame
            title_column: Tên column chứa title
            year_column: Tên column mới cho year
        
        Returns:
            DataFrame với year column
        """
        df_processed = df.copy()
        
        # Extract year từ title (format: "Movie Name (YYYY)")
        df_processed[year_column] = df_processed[title_column].str.extract(r'\((\d{4})\)', expand=False)
        df_processed[year_column] = pd.to_numeric(df_processed[year_column], errors='coerce')
        
        # Xử lý missing years
        missing_years = df_processed[year_column].isnull().sum()
        if missing_years > 0:
            self._log(f"Found {missing_years} movies without year information")
        
        self._log(f"Extracted year from '{title_column}' to '{year_column}'")
        
        return df_processed
    
    def clean_title(self, df, title_column='title', clean_column='title_clean'):
        """
        Clean title bằng cách remove year
        
        Args:
            df: DataFrame
            title_column: Tên column chứa title
            clean_column: Tên column mới cho cleaned title
        
        Returns:
            DataFrame với cleaned title
        """
        df_processed = df.copy()
        
        # Remove year khỏi title
        df_processed[clean_column] = df_processed[title_column].str.replace(
            r'\s*\(\d{4}\)', '', regex=True
        ).str.strip()
        
        self._log(f"Cleaned title from '{title_column}' to '{clean_column}'")
        
        return df_processed
    
    def parse_genres(self, df, genre_column='genres', separator='|'):
        """
        Parse genres từ string thành list
        
        Args:
            df: DataFrame
            genre_column: Tên column chứa genres
            separator: Ký tự phân cách genres
        
        Returns:
            DataFrame với parsed genres
        """
        df_processed = df.copy()
        
        # Parse genres thành list
        df_processed[f'{genre_column}_list'] = df_processed[genre_column].str.split(separator)
        
        # Count số genres cho mỗi phim
        df_processed[f'{genre_column}_count'] = df_processed[f'{genre_column}_list'].apply(len)
        
        self._log(f"Parsed genres from '{genre_column}'")
        
        return df_processed
    
    def encode_genres_onehot(self, df, genre_column='genres', separator='|'):
        """
        One-hot encode genres
        
        Args:
            df: DataFrame
            genre_column: Tên column chứa genres
            separator: Ký tự phân cách genres
        
        Returns:
            DataFrame với one-hot encoded genres, fitted MultiLabelBinarizer
        """
        df_processed = df.copy()
        
        # Parse genres thành list
        genres_list = df_processed[genre_column].str.split(separator).tolist()
        
        # One-hot encode
        self.mlb = MultiLabelBinarizer()
        genres_encoded = self.mlb.fit_transform(genres_list)
        
        # Tạo DataFrame với encoded genres
        genres_df = pd.DataFrame(
            genres_encoded,
            columns=[f'genre_{genre}' for genre in self.mlb.classes_],
            index=df_processed.index
        )
        
        # Merge với df gốc
        df_processed = pd.concat([df_processed, genres_df], axis=1)
        
        self._log(f"One-hot encoded {len(self.mlb.classes_)} genres")
        
        return df_processed, self.mlb
    
    def create_genre_features(self, df, genre_column='genres'):
        """
        Tạo genre-based features
        
        Args:
            df: DataFrame
            genre_column: Tên column chứa genres
        
        Returns:
            DataFrame với genre features
        """
        df_processed = df.copy()
        
        # Các genre phổ biến
        popular_genres = ['Action', 'Comedy', 'Drama', 'Thriller', 'Romance', 
                         'Horror', 'Sci-Fi', 'Adventure', 'Crime', 'Fantasy']
        
        # Tạo binary features cho popular genres
        for genre in popular_genres:
            df_processed[f'is_{genre.lower()}'] = df_processed[genre_column].str.contains(
                genre, case=False, na=False
            ).astype(int)
        
        self._log(f"Created {len(popular_genres)} genre binary features")
        
        return df_processed
    
    def vectorize_text_tfidf(self, texts, max_features=100, ngram_range=(1, 2)):
        """
        Vectorize text sử dụng TF-IDF
        
        Args:
            texts: Series hoặc list of texts
            max_features: Số features tối đa
            ngram_range: N-gram range (default unigram + bigram)
        
        Returns:
            TF-IDF matrix, fitted vectorizer
        """
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            stop_words='english',
            lowercase=True,
            strip_accents='unicode'
        )
        
        # Xử lý missing values
        texts = texts.fillna('')
        
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
        
        self._log(f"TF-IDF vectorization: {tfidf_matrix.shape}")
        self._log(f"  Features: {max_features}, N-grams: {ngram_range}")
        
        return tfidf_matrix, self.tfidf_vectorizer
    
    def vectorize_text_bow(self, texts, max_features=100):
        """
        Vectorize text sử dụng Bag of Words
        
        Args:
            texts: Series hoặc list of texts
            max_features: Số features tối đa
        
        Returns:
            BoW matrix, fitted vectorizer
        """
        self.count_vectorizer = CountVectorizer(
            max_features=max_features,
            stop_words='english',
            lowercase=True,
            strip_accents='unicode'
        )
        
        # Xử lý missing values
        texts = texts.fillna('')
        
        bow_matrix = self.count_vectorizer.fit_transform(texts)
        
        self._log(f"Bag of Words vectorization: {bow_matrix.shape}")
        
        return bow_matrix, self.count_vectorizer
    
    def create_rating_features(self, movies_df, ratings_df):
        """
        Tạo rating-based features
        
        Args:
            movies_df: Movies DataFrame
            ratings_df: Ratings DataFrame
        
        Returns:
            Movies DataFrame với rating features
        """
        df_processed = movies_df.copy()
        
        # Calculate rating statistics
        rating_stats = ratings_df.groupby('movieId').agg({
            'rating': ['mean', 'std', 'count', 'min', 'max']
        }).reset_index()
        
        rating_stats.columns = ['movieId', 'avg_rating', 'std_rating', 
                               'num_ratings', 'min_rating', 'max_rating']
        
        # Merge với movies
        df_processed = df_processed.merge(rating_stats, on='movieId', how='left')
        
        # Fill NaN cho movies chưa có ratings
        rating_columns = ['avg_rating', 'std_rating', 'num_ratings', 'min_rating', 'max_rating']
        for col in rating_columns:
            df_processed[col] = df_processed[col].fillna(0)
        
        # Tạo popularity score (log-scaled num_ratings)
        df_processed['popularity'] = np.log1p(df_processed['num_ratings'])
        
        # Tạo rating confidence (dựa trên số ratings)
        df_processed['rating_confidence'] = df_processed['num_ratings'] / (df_processed['num_ratings'] + 10)
        
        self._log(f"Created rating features for {len(df_processed)} movies")
        
        return df_processed
    
    def create_temporal_features(self, df, year_column='year'):
        """
        Tạo temporal features từ year
        
        Args:
            df: DataFrame
            year_column: Tên column chứa year
        
        Returns:
            DataFrame với temporal features
        """
        df_processed = df.copy()
        
        current_year = pd.Timestamp.now().year
        
        # Age of movie
        df_processed['movie_age'] = current_year - df_processed[year_column]
        
        # Decade
        df_processed['decade'] = (df_processed[year_column] // 10) * 10
        
        # Era categories
        def categorize_era(year):
            if pd.isna(year):
                return 'Unknown'
            elif year < 1960:
                return 'Classic'
            elif year < 1980:
                return '60s-70s'
            elif year < 2000:
                return '80s-90s'
            elif year < 2010:
                return '2000s'
            else:
                return 'Modern'
        
        df_processed['era'] = df_processed[year_column].apply(categorize_era)
        
        self._log(f"Created temporal features from '{year_column}'")
        
        return df_processed
    
    def create_combined_text_features(self, df, columns=['title_clean', 'genres']):
        """
        Kết hợp nhiều text columns thành một
        
        Args:
            df: DataFrame
            columns: List columns cần combine
        
        Returns:
            DataFrame với combined text column
        """
        df_processed = df.copy()
        
        # Combine columns
        df_processed['combined_features'] = ''
        for col in columns:
            if col in df_processed.columns:
                df_processed['combined_features'] += ' ' + df_processed[col].fillna('').astype(str)
        
        df_processed['combined_features'] = df_processed['combined_features'].str.strip()
        
        self._log(f"Combined text from columns: {columns}")
        
        return df_processed


def main():
    """Test the preprocessor"""
    print("=" * 50)
    print("DATA PREPROCESSOR TEST")
    print("=" * 50)
    
    # Sample data
    movies_data = {
        'movieId': [1, 2, 3, 4],
        'title': ['Toy Story (1995)', 'Jumanji (1995)', 'Heat (1995)', 'Batman (1989)'],
        'genres': ['Animation|Children|Comedy', 'Adventure|Children|Fantasy', 
                  'Action|Crime|Thriller', 'Action|Crime|Drama']
    }
    
    movies_df = pd.DataFrame(movies_data)
    
    print("\nOriginal Data:")
    print(movies_df)
    
    preprocessor = MovieDataPreprocessor(verbose=True)
    
    print("\n1. Extract Year:")
    movies_df = preprocessor.extract_year_from_title(movies_df)
    
    print("\n2. Clean Title:")
    movies_df = preprocessor.clean_title(movies_df)
    
    print("\n3. Parse Genres:")
    movies_df = preprocessor.parse_genres(movies_df)
    
    print("\n4. Create Genre Features:")
    movies_df = preprocessor.create_genre_features(movies_df)
    
    print("\n5. Create Temporal Features:")
    movies_df = preprocessor.create_temporal_features(movies_df)
    
    print("\n6. TF-IDF Vectorization:")
    tfidf_matrix, _ = preprocessor.vectorize_text_tfidf(movies_df['title_clean'], max_features=50)
    
    print("\nProcessed Data (first few columns):")
    print(movies_df[['movieId', 'title_clean', 'year', 'decade', 'era']].head())
    
    print("\n✅ Preprocessor test completed!")


if __name__ == "__main__":
    main()
