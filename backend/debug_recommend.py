"""
Quick test script to debug Item-Based and Hybrid recommend() issues
"""

import sys
sys.path.append('d:/Project/Git/Recommendation_system/backend')

from ml.models.item_based import ItemBasedCF
from ml.models.hybrid import HybridWeightedCF
import pickle

print("Loading models...")

# Load Item-Based
try:
    with open('d:/Project/Git/Recommendation_system/backend/ml/saved_models/item_based_cf.pkl', 'rb') as f:
        item_model = pickle.load(f)
    print("✓ Item-Based loaded")
except Exception as e:
    print(f"✗ Item-Based load failed: {e}")
    item_model = None

# Load Hybrid
try:
    with open('d:/Project/Git/Recommendation_system/backend/ml/saved_models/hybrid.pkl', 'rb') as f:
        hybrid_data = pickle.load(f)
    print("✓ Hybrid loaded")
    # Hybrid needs base models
    with open('d:/Project/Git/Recommendation_system/backend/ml/saved_models/user_based_cf.pkl', 'rb') as f:
        user_model = pickle.load(f)
    
    # Recreate hybrid with loaded models
    hybrid_model = HybridWeightedCF(
        user_model, 
        item_model,
        user_weight=hybrid_data.get('user_weight', 0.5),
        item_weight=hybrid_data.get('item_weight', 0.5)
    )
    print("✓ Hybrid reconstructed")
except Exception as e:
    print(f"✗ Hybrid load failed: {e}")
    hybrid_model = None

# Test recommendations
test_user_id = 1  # Pick any user

print("\n" + "="*60)
print("TESTING ITEM-BASED CF")
print("="*60)
if item_model:
    try:
        recs = item_model.recommend(test_user_id, n=10, exclude_rated=True)
        print(f"✓ Got {len(recs)} recommendations")
        for anime_id, score in recs[:5]:
            print(f"  - Anime {anime_id}: {score:.4f}")
    except Exception as e:
        print(f"✗ recommend() failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("TESTING HYBRID")
print("="*60)
if hybrid_model:
    try:
        recs = hybrid_model.recommend(test_user_id, n=10, exclude_rated=True)
        print(f"✓ Got {len(recs)} recommendations")
        for anime_id, score in recs[:5]:
            print(f"  - Anime {anime_id}: {score:.4f}")
    except Exception as e:
        print(f"✗ recommend() failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
