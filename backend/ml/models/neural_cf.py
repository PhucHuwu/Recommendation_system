"""
Neural Collaborative Filtering (NCF) Model

Implementation of Neural Collaborative Filtering combining:
- Generalized Matrix Factorization (GMF)
- Multi-Layer Perceptron (MLP)

Reference: "Neural Collaborative Filtering" (He et al., 2017)
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pickle
from typing import List, Tuple, Optional
from tqdm import tqdm


class RatingDataset(Dataset):
    """Dataset for user-item ratings"""
    
    def __init__(self, ratings_data: List[dict]):
        """
        Args:
            ratings_data: List of dicts with keys: user_id, anime_id, rating
        """
        self.users = torch.LongTensor([r['user_id'] for r in ratings_data])
        self.items = torch.LongTensor([r['anime_id'] for r in ratings_data])
        self.ratings = torch.FloatTensor([r['rating'] for r in ratings_data])
        
    def __len__(self):
        return len(self.ratings)
    
    def __getitem__(self, idx):
        return self.users[idx], self.items[idx], self.ratings[idx]


class NeuralCF(nn.Module):
    """
    Neural Collaborative Filtering Model
    
    Architecture:
    - GMF path: User/Item embeddings → Element-wise product
    - MLP path: User/Item embeddings → Hidden layers
    - Final: Concatenate both paths → Output layer
    """
    
    def __init__(self, 
                 num_users: int,
                 num_items: int,
                 embedding_dim: int = 64,
                 mlp_layers: List[int] = [128, 64, 32],
                 dropout: float = 0.2):
        """
        Initialize NCF model
        
        Args:
            num_users: Number of unique users
            num_items: Number of unique items
            embedding_dim: Dimension for GMF embeddings
            mlp_layers: List of hidden layer sizes for MLP
            dropout: Dropout probability
        """
        super(NeuralCF, self).__init__()
        
        self.num_users = num_users
        self.num_items = num_items
        self.embedding_dim = embedding_dim
        
        # GMF embeddings
        self.gmf_user_embedding = nn.Embedding(num_users, embedding_dim)
        self.gmf_item_embedding = nn.Embedding(num_items, embedding_dim)
        
        # MLP embeddings (separate from GMF)
        self.mlp_user_embedding = nn.Embedding(num_users, mlp_layers[0] // 2)
        self.mlp_item_embedding = nn.Embedding(num_items, mlp_layers[0] // 2)
        
        # MLP layers
        mlp_modules = []
        input_size = mlp_layers[0]
        for layer_size in mlp_layers[1:]:
            mlp_modules.append(nn.Linear(input_size, layer_size))
            mlp_modules.append(nn.ReLU())
            mlp_modules.append(nn.BatchNorm1d(layer_size))
            mlp_modules.append(nn.Dropout(dropout))
            input_size = layer_size
        
        self.mlp_layers = nn.Sequential(*mlp_modules)
        
        # Final prediction layer
        # Input: GMF output (embedding_dim) + MLP output (last mlp layer)
        self.predict_layer = nn.Linear(embedding_dim + mlp_layers[-1], 1)
        
        # Initialize weights
        self._init_weights()
        
    def _init_weights(self):
        """Initialize model weights"""
        nn.init.normal_(self.gmf_user_embedding.weight, std=0.01)
        nn.init.normal_(self.gmf_item_embedding.weight, std=0.01)
        nn.init.normal_(self.mlp_user_embedding.weight, std=0.01)
        nn.init.normal_(self.mlp_item_embedding.weight, std=0.01)
        
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
    
    def forward(self, user_ids, item_ids):
        """
        Forward pass
        
        Args:
            user_ids: Tensor of user IDs
            item_ids: Tensor of item IDs
            
        Returns:
            Predicted ratings
        """
        # GMF path
        gmf_user_embed = self.gmf_user_embedding(user_ids)
        gmf_item_embed = self.gmf_item_embedding(item_ids)
        gmf_output = gmf_user_embed * gmf_item_embed  # Element-wise product
        
        # MLP path
        mlp_user_embed = self.mlp_user_embedding(user_ids)
        mlp_item_embed = self.mlp_item_embedding(item_ids)
        mlp_input = torch.cat([mlp_user_embed, mlp_item_embed], dim=-1)
        mlp_output = self.mlp_layers(mlp_input)
        
        # Concatenate GMF and MLP outputs
        concat = torch.cat([gmf_output, mlp_output], dim=-1)
        
        # Final prediction
        prediction = self.predict_layer(concat)
        
        return prediction.squeeze()
    
    def fit(self, 
            train_data: List[dict],
            val_data: Optional[List[dict]] = None,
            epochs: int = 30,
            batch_size: int = 256,
            lr: float = 0.001,
            early_stopping: int = 5,
            device: str = 'cpu'):
        """
        Train the model
        
        Args:
            train_data: Training ratings data
            val_data: Validation ratings data (optional)
            epochs: Number of training epochs
            batch_size: Batch size
            lr: Learning rate
            early_stopping: Patience for early stopping
            device: Device to train on ('cpu' or 'cuda')
        """
        self.to(device)
        self.train()
        
        # Create data loaders
        train_dataset = RatingDataset(train_data)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, 
                                 shuffle=True, num_workers=0)
        
        val_loader = None
        if val_data:
            val_dataset = RatingDataset(val_data)
            val_loader = DataLoader(val_dataset, batch_size=batch_size, 
                                   shuffle=False, num_workers=0)
        
        # Loss and optimizer
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.parameters(), lr=lr)
        
        # Training loop
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(epochs):
            # Training
            train_loss = 0.0
            self.train()
            
            pbar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{epochs}')
            for user_ids, item_ids, ratings in pbar:
                user_ids = user_ids.to(device)
                item_ids = item_ids.to(device)
                ratings = ratings.to(device)
                
                # Forward pass
                predictions = self(user_ids, item_ids)
                loss = criterion(predictions, ratings)
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
                pbar.set_postfix({'loss': loss.item()})
            
            train_loss /= len(train_loader)
            
            # Validation
            if val_loader:
                val_loss = 0.0
                self.eval()
                
                with torch.no_grad():
                    for user_ids, item_ids, ratings in val_loader:
                        user_ids = user_ids.to(device)
                        item_ids = item_ids.to(device)
                        ratings = ratings.to(device)
                        
                        predictions = self(user_ids, item_ids)
                        loss = criterion(predictions, ratings)
                        val_loss += loss.item()
                
                val_loss /= len(val_loader)
                
                print(f'Epoch {epoch+1}: Train Loss = {train_loss:.4f}, Val Loss = {val_loss:.4f}')
                
                # Early stopping
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    patience_counter = 0
                else:
                    patience_counter += 1
                    if patience_counter >= early_stopping:
                        print(f'Early stopping at epoch {epoch+1}')
                        break
            else:
                print(f'Epoch {epoch+1}: Train Loss = {train_loss:.4f}')
        
        self.eval()
    
    def predict(self, user_id: int, anime_id: int, device: str = 'cpu') -> float:
        """
        Predict rating for a single user-item pair
        
        Args:
            user_id: User ID (original ID)
            anime_id: Anime ID (original ID)
            device: Device for inference
            
        Returns:
            Predicted rating (1-10 scale), or 0 if ID not found
        """
        self.eval()
        self.to(device)
        
        # Map IDs if mappings exist
        if hasattr(self, 'user_id_map') and hasattr(self, 'item_id_map'):
            if user_id not in self.user_id_map or anime_id not in self.item_id_map:
                return 0.0  # Cannot predict for unknown IDs
            
            mapped_user_id = self.user_id_map[user_id]
            mapped_anime_id = self.item_id_map[anime_id]
        else:
            # No mapping, use IDs directly (for backward compatibility)
            mapped_user_id = user_id
            mapped_anime_id = anime_id
        
        with torch.no_grad():
            user_tensor = torch.LongTensor([mapped_user_id]).to(device)
            item_tensor = torch.LongTensor([mapped_anime_id]).to(device)
            
            prediction = self(user_tensor, item_tensor)
            rating = prediction.item()
            
            # Clip to valid range [1, 10]
            rating = max(1.0, min(10.0, rating))
            
        return rating
    
    def recommend(self, 
                  user_id: int,
                  n: int = 10,
                  exclude_rated: bool = True,
                  candidate_items: Optional[List[int]] = None,
                  device: str = 'cpu') -> List[Tuple[int, float]]:
        """
        Generate top-N recommendations for a user
        
        Args:
            user_id: User ID (original ID)
            n: Number of recommendations
            exclude_rated: Whether to exclude already rated items (for compatibility)
            candidate_items: Optional list of candidate anime IDs. If None, use all items
            device: Device for inference
            
        Returns:
            List of (anime_id, predicted_rating) tuples (original IDs)
        """
        self.eval()
        self.to(device)
        
        # Map IDs if mappings exist
        if hasattr(self, 'user_id_map') and hasattr(self, 'item_id_map'):
            if user_id not in self.user_id_map:
                return []  # Cannot recommend for unknown user
            
            mapped_user_id = self.user_id_map[user_id]
            
            # Get candidate items
            if candidate_items is None:
                # Use all known items
                candidate_items = list(self.item_id_map.keys())
            
            # Filter candidates to only include known items
            valid_candidates = []
            original_ids = []
            for item_id in candidate_items:
                if item_id in self.item_id_map:
                    valid_candidates.append(self.item_id_map[item_id])
                    original_ids.append(item_id)
            
            if not valid_candidates:
                return []
        else:
            # No mapping, use IDs directly
            mapped_user_id = user_id
            if candidate_items is None:
                return []  # Cannot recommend without mappings or candidate items
            valid_candidates = candidate_items
            original_ids = candidate_items
        
        # Batch prediction
        with torch.no_grad():
            user_tensor = torch.LongTensor([mapped_user_id] * len(valid_candidates)).to(device)
            item_tensor = torch.LongTensor(valid_candidates).to(device)
            
            predictions = self(user_tensor, item_tensor)
            predictions = predictions.cpu().numpy()
            
            # Clip to valid range
            predictions = np.clip(predictions, 1.0, 10.0)
        
        # Sort by predicted rating (use original IDs in output)
        item_scores = list(zip(original_ids, predictions))
        item_scores.sort(key=lambda x: x[1], reverse=True)
        
        return item_scores[:n]

    
    def save(self, filepath: str):
        """Save model to file"""
        model_state = {
            'state_dict': self.state_dict(),
            'num_users': self.num_users,
            'num_items': self.num_items,
            'embedding_dim': self.embedding_dim,
            'mlp_layers': [128, 64, 32],  # Hardcoded for now
            'model_class': 'NeuralCF'
        }
        
        # Save ID mappings if they exist (CRITICAL for personalization!)
        if hasattr(self, 'user_id_map'):
            model_state['user_id_map'] = self.user_id_map
        if hasattr(self, 'item_id_map'):
            model_state['item_id_map'] = self.item_id_map
        
        torch.save(model_state, filepath)
        print(f"Model saved to {filepath}")
        if hasattr(self, 'user_id_map'):
            print(f"  - Saved {len(self.user_id_map)} user mappings")
        if hasattr(self, 'item_id_map'):
            print(f"  - Saved {len(self.item_id_map)} item mappings")
    
    @classmethod
    def load(cls, filepath: str, device: str = 'cpu'):
        """Load model from file"""
        model_state = torch.load(filepath, map_location=device)
        
        # Create model instance
        model = cls(
            num_users=model_state['num_users'],
            num_items=model_state['num_items'],
            embedding_dim=model_state['embedding_dim'],
            mlp_layers=model_state.get('mlp_layers', [128, 64, 32])
        )
        
        # Load weights
        model.load_state_dict(model_state['state_dict'])
        model.to(device)
        model.eval()
        
        # Restore ID mappings (CRITICAL for personalization!)
        if 'user_id_map' in model_state:
            model.user_id_map = model_state['user_id_map']
            print(f"  - Restored {len(model.user_id_map)} user mappings")
        if 'item_id_map' in model_state:
            model.item_id_map = model_state['item_id_map']
            print(f"  - Restored {len(model.item_id_map)} item mappings")
        
        print(f"Model loaded from {filepath}")
        return model
