"""
Recommendation Service

Service layer để load và sử dụng trained models.
"""

import os
from typing import List, Tuple, Optional
from ml.models.user_based import UserBasedCF
from ml.models.item_based import ItemBasedCF
from ml.models.hybrid import HybridWeightedCF
from ml.models.neural_cf import NeuralCF


class RecommendationService:
    """Service for managing and using recommendation models"""
    
    def __init__(self, models_dir: str = None):
        """
        Initialize Recommendation Service
        
        Args:
            models_dir: Directory containing trained models
        """
        if models_dir is None:
            # Default to backend/ml/saved_models
            current_dir = os.path.dirname(os.path.abspath(__file__))
            models_dir = os.path.join(current_dir, '..', '..', 'ml', 'saved_models')
        
        self.models_dir = models_dir
        self.models = {}
        self.active_model = None
        
    def load_model(self, model_name: str) -> bool:
        """
        Load a specific model
        
        Args:
            model_name: Name of model (user_based_cf, item_based_cf, hybrid, neural_cf)
            
        Returns:
            True if loaded successfully
        """
        # Neural CF uses .pt extension, others use .pkl
        if model_name == 'neural_cf':
            model_path = os.path.join(self.models_dir, f'{model_name}.pt')
        else:
            model_path = os.path.join(self.models_dir, f'{model_name}.pkl')
        
        if not os.path.exists(model_path):
            print(f"Model file not found: {model_path}")
            return False
        
        try:
            if model_name == 'user_based_cf':
                self.models[model_name] = UserBasedCF.load(model_path)
            elif model_name == 'item_based_cf':
                self.models[model_name] = ItemBasedCF.load(model_path)
            elif model_name == 'hybrid':
                # Hybrid needs both base models loaded first
                if 'user_based_cf' not in self.models:
                    self.load_model('user_based_cf')
                if 'item_based_cf' not in self.models:
                    self.load_model('item_based_cf')
                
                if 'user_based_cf' in self.models and 'item_based_cf' in self.models:
                    self.models[model_name] = HybridWeightedCF.load(
                        model_path,
                        self.models['user_based_cf'],
                        self.models['item_based_cf']
                    )
                else:
                    print("Cannot load hybrid: base models not available")
                    return False
            elif model_name == 'neural_cf':
                # Neural CF already has correct path (.pt)
                self.models[model_name] = NeuralCF.load(model_path)
            else:
                print(f"Unknown model name: {model_name}")
                return False
            
            return True
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            return False
    
    def load_all_models(self) -> dict:
        """
        Load all available models
        
        Returns:
            Dictionary of loaded models status
        """
        models_to_load = ['user_based_cf', 'item_based_cf', 'hybrid', 'neural_cf']
        results = {}
        
        for model_name in models_to_load:
            results[model_name] = self.load_model(model_name)
        
        return results
    
    def set_active_model(self, model_name: str) -> bool:
        """
        Set which model to use for recommendations
        
        Args:
            model_name: Name of model to activate
            
        Returns:
            True if successful
        """
        # ALWAYS reload model from disk to get latest trained version
        # This ensures that newly trained models are used immediately
        print(f"[RecommendationService] Activating model: {model_name}")
        print(f"[RecommendationService] Reloading from disk to get latest version...")
        
        # Remove old model from cache if exists
        if model_name in self.models:
            del self.models[model_name]
        
        # Load fresh model from disk
        if not self.load_model(model_name):
            print(f"[RecommendationService] Failed to load model: {model_name}")
            return False
        
        self.active_model = model_name
        print(f"[RecommendationService] Successfully activated: {model_name}")
        return True
    
    def get_recommendations(
        self, 
        user_id: int, 
        n: int = 10, 
        model_name: Optional[str] = None
    ) -> List[Tuple[int, float]]:
        """
        Get personalized recommendations for a user
        
        Args:
            user_id: User ID
            n: Number of recommendations
            model_name: Specific model to use (optional)
            
        Returns:
            List of (anime_id, predicted_rating) tuples
        """
        # Determine which model to use
        target_model = model_name if model_name else self.active_model
        
        if not target_model:
            target_model = 'user_based_cf'  # Default
        
        # Load model if not loaded
        if target_model not in self.models:
            if not self.load_model(target_model):
                return []
        
        model = self.models[target_model]
        
        # Get recommendations (CF, Hybrid, and Neural CF models support recommend())
        if target_model in ['user_based_cf', 'item_based_cf', 'hybrid', 'neural_cf']:
            return model.recommend(user_id, n=n, exclude_rated=True)
        
        return []
    
    def get_similar_animes(
        self, 
        anime_id: int, 
        n: int = 10
    ) -> List[Tuple[int, float]]:
        """
        Get similar animes using Item-Based CF
        
        Args:
            anime_id: Target anime ID
            n: Number of similar animes
            
        Returns:
            List of (anime_id, similarity_score) tuples
        """
        model_name = 'item_based_cf'
        
        # Load model if not loaded
        if model_name not in self.models:
            if not self.load_model(model_name):
                return []
        
        model = self.models[model_name]
        return model.get_similar_animes(anime_id, n=n)
    
    def predict_rating(
        self, 
        user_id: int, 
        anime_id: int,
        model_name: Optional[str] = None
    ) -> float:
        """
        Predict rating for a user-anime pair
        
        Args:
            user_id: User ID
            anime_id: Anime ID
            model_name: Specific model to use (optional)
            
        Returns:
            Predicted rating (1-10)
        """
        target_model = model_name if model_name else self.active_model
        
        if not target_model:
            target_model = 'user_based_cf'
        
        # Load model if not loaded
        if target_model not in self.models:
            if not self.load_model(target_model):
                return 0.0
        
        model = self.models[target_model]
        
        # CF, Hybrid, and Neural CF models support prediction
        if target_model in ['user_based_cf', 'item_based_cf', 'hybrid', 'neural_cf']:
            return model.predict(user_id, anime_id)
        
        return 0.0
    
    def get_loaded_models(self) -> List[str]:
        """Get list of currently loaded models"""
        return list(self.models.keys())
    
    def clear_models(self):
        """Clear all loaded models from memory"""
        self.models.clear()
        self.active_model = None


# Global service instance
_recommendation_service = None


def get_recommendation_service() -> RecommendationService:
    """Get or create global recommendation service instance"""
    global _recommendation_service
    
    if _recommendation_service is None:
        _recommendation_service = RecommendationService()
        # Try to load all models on startup
        _recommendation_service.load_all_models()
        # Set default active model to neural_cf (best performing model)
        _recommendation_service.set_active_model('neural_cf')
    
    return _recommendation_service
