from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import get_db
from app.services.recommendation_service import get_recommendation_service

recommendation_bp = Blueprint('recommendation', __name__)


# ========================= K VALUE RECOMMENDATIONS =========================
# Homepage recommendations: K = 5-10 (high precision, focused list)
# Similar anime section: K = 6-12 (balanced precision/recall)
# Search results: K = 20-30 (higher recall for exploration)
# Evaluation/Training: K = 10-20 (standard for metrics)
# ===========================================================================

DEFAULT_K_HOMEPAGE = 10      # Recommendations on homepage
DEFAULT_K_SIMILAR = 12       # Similar anime suggestions
DEFAULT_K_SEARCH = 20        # Search results
MAX_K_LIMIT = 50             # Maximum allowed K


@recommendation_bp.route('/', methods=['GET'])
@jwt_required()
def get_recommendations():
    """Get personalized recommendations for the current user
    
    K Value Strategy:
    - Default K=10 optimized for homepage (high precision)
    - Lower K (5-10): Better precision, user sees only best matches
    - Higher K (15-30): Better recall, more exploration options
    """
    user_id = int(get_jwt_identity())
    limit = request.args.get('limit', DEFAULT_K_HOMEPAGE, type=int)
    model = request.args.get('model', None)  # Allow specifying model
    
    limit = min(limit, MAX_K_LIMIT)
    
    db = get_db()
    
    # Use neural_cf as default if not specified (best performing model)
    if not model:
        model = 'neural_cf'
    
    # Get recommendation service
    rec_service = get_recommendation_service()
    
    # Get recommendations from ML model
    recommendations = rec_service.get_recommendations(user_id, n=limit, model_name=model)
    
    if not recommendations:
        # Fallback: return top animes if no recommendations
        user_ratings = list(db.ratings.find({'user_id': user_id}, {'anime_id': 1}))
        rated_anime_ids = [r['anime_id'] for r in user_ratings]
        
        animes = list(db.animes.find(
            {'mal_id': {'$nin': rated_anime_ids}},
            {'_id': 0}
        ).sort('score', -1).limit(limit))
        
        recommendations = [(a['mal_id'], a.get('score', 0)) for a in animes]
    
    # Get anime details for recommendations
    result = []
    for anime_id, predicted_rating in recommendations:
        anime = db.animes.find_one({'mal_id': anime_id}, {'_id': 0})
        if anime:
            result.append({
                'anime_id': anime_id,
                'name': anime.get('name'),
                'genres': anime.get('genres'),
                'score': anime.get('score'),
                'predicted_rating': round(float(predicted_rating), 2)  # Convert numpy float32 to Python float
            })
    
    return jsonify({
        'recommendations': result,
        'model_used': model,
        'count': len(result)
    }), 200


@recommendation_bp.route('/similar/<int:anime_id>', methods=['GET'])
def get_similar_animes(anime_id):
    """Get similar animes using Item-Based CF
    
    K Value Strategy:
    - Default K=12 for similar anime section (balanced)
    - Capped at 20 to maintain precision quality
    """
    limit = request.args.get('limit', DEFAULT_K_SIMILAR, type=int)
    
    limit = min(limit, 20)  # Cap for similar section (quality > quantity)
    
    db = get_db()
    
    # Get the target anime
    target_anime = db.animes.find_one({'mal_id': anime_id})
    
    if not target_anime:
        return jsonify({'error': 'Anime not found'}), 404
    
    # Get recommendation service
    rec_service = get_recommendation_service()
    
    # Get similar animes from Item-Based CF
    similar = rec_service.get_similar_animes(anime_id, n=limit)
    
    # Get anime details
    result = []
    for sim_anime_id, similarity in similar:
        anime = db.animes.find_one({'mal_id': sim_anime_id}, {'_id': 0})
        if anime:
            result.append({
                'anime_id': sim_anime_id,
                'name': anime.get('name'),
                'genres': anime.get('genres'),
                'score': anime.get('score'),
                'similarity': round(float(similarity), 4)  # Convert to Python float
            })
    
    return jsonify({
        'anime_id': anime_id,
        'anime_name': target_anime.get('name'),
        'similar_animes': result,
        'count': len(result),
        'method': 'item-based'
    }), 200
