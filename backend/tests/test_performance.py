"""
Model Performance Testing

Test recommendation quality and performance.
"""

import sys
import os
import time
import numpy as np
from pymongo import MongoClient
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.models.user_based import UserBasedCF
from ml.models.item_based import ItemBasedCF
from ml.models.content_based import ContentBasedCF
from ml.training.evaluate import rmse, mae

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DB = os.getenv('MONGODB_DB', 'anime_recommendation')


def load_test_data(limit=1000):
    """Load test data from MongoDB"""
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    
    # Get random sample of ratings for testing
    ratings = list(db.ratings.aggregate([
        {'$sample': {'size': limit}}
    ]))
    
    client.close()
    return ratings


def test_model_performance(model, model_name, test_data):
    """Test model prediction performance"""
    print(f"\n{'=' * 60}")
    print(f"Testing: {model_name}")
    print('=' * 60)
    
    # Test prediction accuracy
    print("Testing prediction accuracy...")
    actual_ratings = []
    predicted_ratings = []
    
    start_time = time.time()
    
    for i, rating in enumerate(test_data):
        if i % 100 == 0:
            print(f"  Progress: {i}/{len(test_data)}", end='\r')
        
        actual = rating['rating']
        predicted = model.predict(rating['user_id'], rating['anime_id'])
        
        if predicted > 0:
            actual_ratings.append(actual)
            predicted_ratings.append(predicted)
    
    prediction_time = time.time() - start_time
    
    print(f"\n  Predictions made: {len(predicted_ratings)}/{len(test_data)}")
    print(f"  Coverage: {len(predicted_ratings)/len(test_data)*100:.2f}%")
    print(f"  Time: {prediction_time:.2f}s")
    print(f"  Avg time per prediction: {prediction_time/len(test_data)*1000:.2f}ms")
    
    if len(predicted_ratings) > 0:
        actual_ratings = np.array(actual_ratings)
        predicted_ratings = np.array(predicted_ratings)
        
        rmse_value = rmse(actual_ratings, predicted_ratings)
        mae_value = mae(actual_ratings, predicted_ratings)
        
        print(f"\n  RMSE: {rmse_value:.4f}")
        print(f"  MAE: {mae_value:.4f}")
        
        return {
            'model': model_name,
            'coverage': len(predicted_ratings)/len(test_data),
            'rmse': rmse_value,
            'mae': mae_value,
            'avg_time_ms': prediction_time/len(test_data)*1000
        }
    
    return None


def test_recommendation_speed(model, model_name, test_users):
    """Test recommendation generation speed"""
    print(f"\nTesting recommendation speed for {model_name}...")
    
    if not hasattr(model, 'recommend'):
        print("  Model does not support recommendations")
        return None
    
    times = []
    
    for user_id in test_users[:10]:  # Test with 10 users
        start = time.time()
        try:
            recs = model.recommend(user_id, n=10)
            times.append(time.time() - start)
        except:
            pass
    
    if times:
        avg_time = np.mean(times) * 1000
        print(f"  Avg recommendation time: {avg_time:.2f}ms")
        return avg_time
    
    return None


def main():
    """Main testing function"""
    print("=" * 60)
    print("MODEL PERFORMANCE TESTING")
    print("=" * 60)
    
    # Load test data
    print("\nLoading test data...")
    test_data = load_test_data(limit=1000)
    test_users = list(set([r['user_id'] for r in test_data]))[:20]
    print(f"Loaded {len(test_data)} test ratings")
    print(f"Test users: {len(test_users)}")
    
    # Load models
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'ml', 'saved_models')
    
    results = []
    
    # Test User-Based CF
    try:
        print("\nLoading User-Based CF...")
        user_model = UserBasedCF.load(os.path.join(models_dir, 'user_based_cf.pkl'))
        result = test_model_performance(user_model, "User-Based CF", test_data)
        if result:
            rec_time = test_recommendation_speed(user_model, "User-Based CF", test_users)
            if rec_time:
                result['rec_time_ms'] = rec_time
            results.append(result)
    except Exception as e:
        print(f"Error testing User-Based CF: {e}")
    
    # Test Item-Based CF
    try:
        print("\nLoading Item-Based CF...")
        item_model = ItemBasedCF.load(os.path.join(models_dir, 'item_based_cf.pkl'))
        result = test_model_performance(item_model, "Item-Based CF", test_data)
        if result:
            rec_time = test_recommendation_speed(item_model, "Item-Based CF", test_users)
            if rec_time:
                result['rec_time_ms'] = rec_time
            results.append(result)
    except Exception as e:
        print(f"Error testing Item-Based CF: {e}")
    
    # Print comparison
    print("\n" + "=" * 60)
    print("PERFORMANCE COMPARISON")
    print("=" * 60)
    
    if results:
        print(f"\n{'Model':<20} {'RMSE':<8} {'MAE':<8} {'Coverage':<10} {'Pred(ms)':<10} {'Rec(ms)':<10}")
        print("-" * 80)
        
        for r in results:
            print(f"{r['model']:<20} "
                  f"{r['rmse']:<8.4f} "
                  f"{r['mae']:<8.4f} "
                  f"{r['coverage']*100:<10.2f} "
                  f"{r['avg_time_ms']:<10.2f} "
                  f"{r.get('rec_time_ms', 0):<10.2f}")
        
        # Best model
        best_rmse = min(results, key=lambda x: x['rmse'])
        best_speed = min(results, key=lambda x: x['avg_time_ms'])
        
        print(f"\nBest Accuracy (RMSE): {best_rmse['model']} ({best_rmse['rmse']:.4f})")
        print(f"Fastest Prediction: {best_speed['model']} ({best_speed['avg_time_ms']:.2f}ms)")
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
