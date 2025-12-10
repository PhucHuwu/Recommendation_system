"""
Re-evaluate Neural CF model without retraining
"""

import sys
import os

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from ml.models.neural_cf import NeuralCF
from ml.training.train import load_data_from_mongodb, split_by_user, update_model_registry
from ml.training.evaluate import evaluate_model

print("=" * 80)
print("RE-EVALUATING NEURAL CF MODEL")
print("=" * 80)

# Load data
print("\nLoading data...")
ratings_data, animes_data = load_data_from_mongodb()

# Split data (same split as training)
train_data, test_data = split_by_user(ratings_data, test_ratio=0.2, seed=42)

# Load trained model
models_dir = os.path.join(os.path.dirname(__file__), '../saved_models')
model_path = os.path.join(models_dir, 'neural_cf.pt')

print(f"\nLoading model from: {model_path}")

import torch
device = 'cuda' if torch.cuda.is_available() else 'cpu'
ncf_model = NeuralCF.load(model_path, device=device)

print(f"Model loaded successfully!")
print(f"  Users: {ncf_model.num_users:,}")
print(f"  Items: {ncf_model.num_items:,}")

# Load ID mappings from training data
print("\nRestoring ID mappings...")
user_ids = set(r['user_id'] for r in train_data)
item_ids = set(r['anime_id'] for r in train_data)

user_id_map = {uid: idx for idx, uid in enumerate(sorted(user_ids))}
item_id_map = {iid: idx for idx, iid in enumerate(sorted(item_ids))}

ncf_model.user_id_map = user_id_map
ncf_model.item_id_map = item_id_map
ncf_model.reverse_user_map = {v: k for k, v in user_id_map.items()}
ncf_model.reverse_item_map = {v: k for k, v in item_id_map.items()}

print(f"  Mapped {len(user_id_map):,} users")
print(f"  Mapped {len(item_id_map):,} items")

# Evaluate
print("\n" + "=" * 80)
print("EVALUATING NEURAL CF")
print("=" * 80)

ncf_metrics = evaluate_model(ncf_model, train_data, test_data, k=10)

# Update registry with correct metrics
update_model_registry('neural_cf', ncf_metrics, is_active=True)

print("\n" + "=" * 80)
print("RE-EVALUATION COMPLETE")
print("=" * 80)
print("\nUpdated metrics in database!")
print(f"  RMSE: {ncf_metrics['rmse']:.4f}")
print(f"  MAE: {ncf_metrics['mae']:.4f}")
print(f"  Precision@K: {ncf_metrics['precision_at_k']:.4f}")
print(f"  Recall@K: {ncf_metrics['recall_at_k']:.4f}")
print(f"  Coverage: {ncf_metrics['coverage']:.4f}")
