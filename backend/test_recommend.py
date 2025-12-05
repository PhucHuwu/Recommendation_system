"""Test recommend() function directly"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ml.models.item_based import ItemBasedCF

model_path = r'd:\Project\Git\Recommendation_system\backend\ml\saved_models\item_based_cf.pkl'
print(f'Loading model from {model_path}')

model = ItemBasedCF.load(model_path)
print(f'Model loaded successfully')
print(f'Model has {len(model.anime_id_map)} animes')

# Test recommend
print('\nTesting recommend() with exclude_rated=False...')
recs = model.recommend(1, n=10, exclude_rated=False)
print(f'Result: {len(recs)} recommendations')

if len(recs) > 0:
    print('\nTop 5 recommendations:')
    for i, (aid, score) in enumerate(recs[:5]):
        print(f'  {i+1}. Anime {aid}: {score:.4f}')
else:
    print('ERROR: No recommendations returned!')
    print('\nDebugging...')
    
    user_id = 1
    if user_id in model.user_id_map:
        user_idx = model.user_id_map[user_id]
        rated_animes = model.user_item_matrix[user_idx].nonzero()[1]
        print(f'User {user_id} has rated {len(rated_animes)} animes')
    else:
        print(f'User {user_id} not in user_id_map')
