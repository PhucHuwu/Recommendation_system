"""
Models package for recommendation systems.
"""

from .content_based import ContentBasedRecommender
from .collaborative_filtering import CollaborativeFilteringRecommender

__all__ = [
    'ContentBasedRecommender',
    'CollaborativeFilteringRecommender'
]
