from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import get_db
from datetime import datetime

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get overall system statistics"""
    db = get_db()
    
    stats = {
        'total_users': db.users.count_documents({}),
        'total_animes': db.animes.count_documents({}),
        'total_ratings': db.ratings.count_documents({}),
        'total_history': db.watch_history.count_documents({})
    }
    
    # Get rating distribution
    pipeline = [
        {'$group': {
            '_id': '$rating',
            'count': {'$sum': 1}
        }},
        {'$sort': {'_id': 1}}
    ]
    rating_dist = list(db.ratings.aggregate(pipeline))
    stats['rating_distribution'] = {str(r['_id']): r['count'] for r in rating_dist}
    
    # Get top genres
    pipeline = [
        {'$project': {'genres': {'$split': ['$genres', ', ']}}},
        {'$unwind': '$genres'},
        {'$group': {'_id': '$genres', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 10}
    ]
    top_genres = list(db.animes.aggregate(pipeline))
    stats['top_genres'] = [{'genre': g['_id'], 'count': g['count']} for g in top_genres if g['_id']]
    
    return jsonify({'stats': stats}), 200


@admin_bp.route('/visualization', methods=['GET'])
def get_visualization_data():
    """Get data for visualization charts"""
    db = get_db()
    
    data = {}
    
    # Rating distribution (1-10)
    pipeline = [
        {'$group': {'_id': '$rating', 'count': {'$sum': 1}}},
        {'$sort': {'_id': 1}}
    ]
    data['rating_distribution'] = list(db.ratings.aggregate(pipeline))
    
    # Top 10 most rated animes
    pipeline = [
        {'$group': {'_id': '$anime_id', 'rating_count': {'$sum': 1}, 'avg_rating': {'$avg': '$rating'}}},
        {'$sort': {'rating_count': -1}},
        {'$limit': 10},
        {'$lookup': {
            'from': 'animes',
            'localField': '_id',
            'foreignField': 'mal_id',
            'as': 'anime'
        }},
        {'$unwind': '$anime'},
        {'$project': {
            'anime_id': '$_id',
            'anime_name': '$anime.name',
            'rating_count': 1,
            'avg_rating': {'$round': ['$avg_rating', 2]}
        }}
    ]
    data['top_rated_animes'] = list(db.ratings.aggregate(pipeline))
    
    # Genre frequency
    pipeline = [
        {'$project': {'genres': {'$split': ['$genres', ', ']}}},
        {'$unwind': '$genres'},
        {'$group': {'_id': '$genres', 'count': {'$sum': 1}}},
        {'$match': {'_id': {'$ne': ''}}},
        {'$sort': {'count': -1}},
        {'$limit': 15}
    ]
    data['genre_frequency'] = list(db.animes.aggregate(pipeline))
    
    # Score distribution (anime scores)
    pipeline = [
        {'$bucket': {
            'groupBy': '$score',
            'boundaries': [0, 5, 6, 7, 8, 9, 10],
            'default': 'Unknown',
            'output': {'count': {'$sum': 1}}
        }}
    ]
    data['score_distribution'] = list(db.animes.aggregate(pipeline))
    
    return jsonify({'data': data}), 200


@admin_bp.route('/models', methods=['GET'])
def get_models():
    """Get list of available ML models"""
    db = get_db()
    
    models = list(db.models.find({}, {'_id': 0}))
    
    # If no models in DB, return default list
    if not models:
        models = [
            {'name': 'user_based', 'display_name': 'User-Based CF', 'is_active': True, 'status': 'not_trained'},
            {'name': 'item_based', 'display_name': 'Item-Based CF', 'is_active': False, 'status': 'not_trained'},
            {'name': 'content_based', 'display_name': 'Content-Based', 'is_active': False, 'status': 'not_trained'}
        ]
    
    return jsonify({'models': models}), 200


@admin_bp.route('/models/select', methods=['POST'])
def select_model():
    """Select which model to use for recommendations"""
    data = request.get_json()
    
    if not data or 'model_name' not in data:
        return jsonify({'error': 'model_name is required'}), 400
    
    model_name = data['model_name']
    valid_models = ['user_based_cf', 'item_based_cf', 'content_based']
    
    if model_name not in valid_models:
        return jsonify({'error': f'Invalid model. Choose from: {valid_models}'}), 400
    
    # Update recommendation service
    from app.services.recommendation_service import get_recommendation_service
    rec_service = get_recommendation_service()
    
    if not rec_service.set_active_model(model_name):
        return jsonify({'error': f'Could not load model {model_name}'}), 500
    
    db = get_db()
    
    # Deactivate all models in DB
    db.models.update_many({}, {'$set': {'is_active': False}})
    
    # Activate selected model in DB
    db.models.update_one(
        {'name': model_name},
        {
            '$set': {'is_active': True, 'activated_at': datetime.utcnow()},
            '$setOnInsert': {'name': model_name, 'created_at': datetime.utcnow()}
        },
        upsert=True
    )
    
    return jsonify({'message': f'Model {model_name} is now active'}), 200


@admin_bp.route('/models/train', methods=['POST'])
def train_model():
    """Trigger model training (placeholder)"""
    data = request.get_json()
    
    if not data or 'model_name' not in data:
        return jsonify({'error': 'model_name is required'}), 400
    
    model_name = data['model_name']
    
    # TODO: Implement actual training logic
    # For now, just return a job ID
    job_id = f"train_{model_name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    return jsonify({
        'message': f'Training job started for {model_name}',
        'job_id': job_id,
        'status': 'pending'
    }), 202


@admin_bp.route('/models/compare', methods=['GET'])
def compare_models():
    """Compare metrics of all models"""
    db = get_db()
    
    models = list(db.models.find({}, {'_id': 0}))
    
    # Return comparison data (metrics will be populated after training)
    comparison = []
    for model in models:
        comparison.append({
            'name': model.get('name'),
            'metrics': model.get('metrics', {}),
            'trained_at': model.get('trained_at'),
            'is_active': model.get('is_active', False)
        })
    
    return jsonify({'comparison': comparison}), 200
