"""
Data Cleaner Module for Movie Recommendation System

Xử lý missing values, duplicates, outliers trong dữ liệu phim.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler


class MovieDataCleaner:
    """
    Class để làm sạch dữ liệu phim.
    
    Thực hiện:
    - Xử lý missing values
    - Loại bỏ duplicates
    - Xử lý outliers
    - Chuẩn hóa dữ liệu
    """
    
    def __init__(self, verbose=True):
        """
        Initialize cleaner
        
        Args:
            verbose: In thông tin chi tiết
        """
        self.verbose = verbose
        self.scaler = None
    
    def _log(self, message):
        """Print message nếu verbose=True"""
        if self.verbose:
            print(message)
    
    def check_missing_values(self, df, column_name=None):
        """
        Kiểm tra missing values
        
        Args:
            df: DataFrame
            column_name: Tên column (None = check all)
        
        Returns:
            Series hoặc int với số missing values
        """
        if column_name:
            return df[column_name].isnull().sum()
        else:
            missing = df.isnull().sum()
            missing_pct = 100 * missing / len(df)
            result = pd.DataFrame({
                'Missing Count': missing,
                'Percentage': missing_pct
            })
            return result[result['Missing Count'] > 0]
    
    def handle_missing_values(self, df, strategy='drop', columns=None, fill_value=None):
        """
        Xử lý missing values
        
        Args:
            df: DataFrame
            strategy: 'drop', 'mean', 'median', 'mode', 'constant'
            columns: List columns cần xử lý (None = all columns with missing)
            fill_value: Giá trị để fill (cho strategy='constant')
        
        Returns:
            DataFrame đã xử lý
        """
        df_clean = df.copy()
        
        if columns is None:
            columns = df_clean.columns[df_clean.isnull().any()].tolist()
        
        self._log(f"Handling missing values in columns: {columns}")
        self._log(f"Strategy: {strategy}")
        
        before_count = len(df_clean)
        
        if strategy == 'drop':
            df_clean = df_clean.dropna(subset=columns)
            self._log(f"Dropped {before_count - len(df_clean)} rows")
        
        elif strategy == 'mean':
            for col in columns:
                if df_clean[col].dtype in ['float64', 'int64']:
                    df_clean[col].fillna(df_clean[col].mean(), inplace=True)
        
        elif strategy == 'median':
            for col in columns:
                if df_clean[col].dtype in ['float64', 'int64']:
                    df_clean[col].fillna(df_clean[col].median(), inplace=True)
        
        elif strategy == 'mode':
            for col in columns:
                df_clean[col].fillna(df_clean[col].mode()[0], inplace=True)
        
        elif strategy == 'constant':
            if fill_value is None:
                raise ValueError("fill_value must be provided for 'constant' strategy")
            for col in columns:
                df_clean[col].fillna(fill_value, inplace=True)
        
        return df_clean
    
    def remove_duplicates(self, df, subset=None, keep='first'):
        """
        Loại bỏ duplicate rows
        
        Args:
            df: DataFrame
            subset: Columns để check duplicates (None = all columns)
            keep: 'first', 'last', False
        
        Returns:
            DataFrame không có duplicates
        """
        before_count = len(df)
        df_clean = df.drop_duplicates(subset=subset, keep=keep)
        removed = before_count - len(df_clean)
        
        self._log(f"Removed {removed} duplicate rows")
        
        return df_clean
    
    def detect_outliers_iqr(self, df, column, multiplier=1.5):
        """
        Phát hiện outliers sử dụng IQR method
        
        Args:
            df: DataFrame
            column: Tên column
            multiplier: IQR multiplier (default 1.5)
        
        Returns:
            Boolean Series indicating outliers
        """
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        outliers = (df[column] < lower_bound) | (df[column] > upper_bound)
        
        self._log(f"Column '{column}': Found {outliers.sum()} outliers")
        self._log(f"  Range: [{lower_bound:.2f}, {upper_bound:.2f}]")
        
        return outliers
    
    def detect_outliers_zscore(self, df, column, threshold=3):
        """
        Phát hiện outliers sử dụng Z-score method
        
        Args:
            df: DataFrame
            column: Tên column
            threshold: Z-score threshold (default 3)
        
        Returns:
            Boolean Series indicating outliers
        """
        z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
        outliers = z_scores > threshold
        
        self._log(f"Column '{column}': Found {outliers.sum()} outliers (z-score > {threshold})")
        
        return outliers
    
    def handle_outliers(self, df, column, method='remove', strategy='iqr'):
        """
        Xử lý outliers
        
        Args:
            df: DataFrame
            column: Tên column
            method: 'remove', 'cap', 'log_transform'
            strategy: 'iqr' or 'zscore' for detection
        
        Returns:
            DataFrame đã xử lý outliers
        """
        df_clean = df.copy()
        
        # Detect outliers
        if strategy == 'iqr':
            outliers = self.detect_outliers_iqr(df_clean, column)
        else:
            outliers = self.detect_outliers_zscore(df_clean, column)
        
        if method == 'remove':
            before_count = len(df_clean)
            df_clean = df_clean[~outliers]
            self._log(f"Removed {before_count - len(df_clean)} outlier rows")
        
        elif method == 'cap':
            # Cap at percentiles
            lower = df_clean[column].quantile(0.01)
            upper = df_clean[column].quantile(0.99)
            df_clean[column] = df_clean[column].clip(lower, upper)
            self._log(f"Capped values to [{lower:.2f}, {upper:.2f}]")
        
        elif method == 'log_transform':
            # Log transformation (only for positive values)
            if (df_clean[column] > 0).all():
                df_clean[column] = np.log1p(df_clean[column])
                self._log(f"Applied log transformation")
            else:
                self._log(f"Warning: Cannot apply log transform to non-positive values")
        
        return df_clean
    
    def normalize_data(self, df, columns, method='standard'):
        """
        Chuẩn hóa dữ liệu
        
        Args:
            df: DataFrame
            columns: List columns cần normalize
            method: 'standard' (StandardScaler) or 'minmax' (MinMaxScaler)
        
        Returns:
            DataFrame với normalized columns
        """
        df_clean = df.copy()
        
        if method == 'standard':
            self.scaler = StandardScaler()
        elif method == 'minmax':
            self.scaler = MinMaxScaler()
        else:
            raise ValueError("method must be 'standard' or 'minmax'")
        
        df_clean[columns] = self.scaler.fit_transform(df_clean[columns])
        
        self._log(f"Normalized columns {columns} using {method} scaler")
        
        return df_clean
    
    def clean_text(self, df, column, lowercase=True, remove_special=False):
        """
        Clean text columns
        
        Args:
            df: DataFrame
            column: Text column name
            lowercase: Convert to lowercase
            remove_special: Remove special characters
        
        Returns:
            DataFrame with cleaned text
        """
        df_clean = df.copy()
        
        if lowercase:
            df_clean[column] = df_clean[column].str.lower()
        
        if remove_special:
            df_clean[column] = df_clean[column].str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
        
        # Remove extra whitespace
        df_clean[column] = df_clean[column].str.strip().str.replace(r'\s+', ' ', regex=True)
        
        self._log(f"Cleaned text in column '{column}'")
        
        return df_clean
    
    def get_cleaning_report(self, df_before, df_after):
        """
        Tạo report so sánh trước/sau cleaning
        
        Args:
            df_before: DataFrame trước cleaning
            df_after: DataFrame sau cleaning
        
        Returns:
            Dictionary với thông tin cleaning
        """
        report = {
            'rows_before': len(df_before),
            'rows_after': len(df_after),
            'rows_removed': len(df_before) - len(df_after),
            'missing_before': df_before.isnull().sum().sum(),
            'missing_after': df_after.isnull().sum().sum(),
            'duplicates_removed': len(df_before) - len(df_before.drop_duplicates())
        }
        
        return report


def main():
    """Test the cleaner"""
    print("=" * 50)
    print("DATA CLEANER TEST")
    print("=" * 50)
    
    # Create sample data with issues
    data = {
        'id': [1, 2, 2, 3, 4, 5, 6],
        'value': [10, 20, 20, np.nan, 100, 25, 30],
        'rating': [4.5, 3.0, 3.0, 2.5, 5.0, 4.0, 3.5],
        'text': ['Hello World', '  Test  ', 'SAMPLE', None, 'Data!', 'example', 'test']
    }
    df = pd.DataFrame(data)
    
    print("\nOriginal Data:")
    print(df)
    
    cleaner = MovieDataCleaner(verbose=True)
    
    print("\n1. Check Missing Values:")
    print(cleaner.check_missing_values(df))
    
    print("\n2. Handle Missing Values:")
    df = cleaner.handle_missing_values(df, strategy='mean', columns=['value'])
    df = cleaner.handle_missing_values(df, strategy='constant', columns=['text'], fill_value='unknown')
    
    print("\n3. Remove Duplicates:")
    df = cleaner.remove_duplicates(df, subset=['id', 'value'])
    
    print("\n4. Detect Outliers:")
    cleaner.detect_outliers_iqr(df, 'value')
    
    print("\n5. Clean Text:")
    df = cleaner.clean_text(df, 'text', lowercase=True, remove_special=True)
    
    print("\nCleaned Data:")
    print(df)
    
    print("\nCleaner test completed!")


if __name__ == "__main__":
    main()
