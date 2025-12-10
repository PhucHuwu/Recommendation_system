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
    """Get comprehensive data for 14+ visualization charts"""
    db = get_db()
    
    data = {}
    
    # 1. Rating distribution (Histogram)
    pipeline = [
        {'$group': {'_id': '$rating', 'count': {'$sum': 1}}},
        {'$sort': {'_id': 1}}
    ]
    data['rating_distribution'] = list(db.ratings.aggregate(pipeline))
    
    # 2. Top 10 most rated animes (Bar Chart)
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
    
    # 3. Genre frequency (Horizontal Bar)
    pipeline = [
        {'$project': {'genres': {'$split': ['$genres', ', ']}}},
        {'$unwind': '$genres'},
        {'$group': {'_id': '$genres', 'count': {'$sum': 1}}},
        {'$match': {'_id': {'$ne': ''}}},
        {'$sort': {'count': -1}},
        {'$limit': 15}
    ]
    data['genre_frequency'] = list(db.animes.aggregate(pipeline))
    
    # 4. Anime type distribution (Pie Chart) - DISABLED: no 'type' field in DB
    # Use genre distribution as alternative
    pipeline = [
        {'$project': {'first_genre': {'$arrayElemAt': [{'$split': ['$genres', ', ']}, 0]}}},
        {'$group': {'_id': '$first_genre', 'count': {'$sum': 1}}},
        {'$match': {'_id': {'$ne': '', '$ne': None}}},
        {'$sort': {'count': -1}},
        {'$limit': 8}
    ]
    data['anime_type_distribution'] = list(db.animes.aggregate(pipeline))
    
    # 5. Rating categories (Donut Chart)
    pipeline = [
        {'$bucket': {
            'groupBy': '$rating',
            'boundaries': [1, 5, 8, 11],
            'default': 'Other',
            'output': {'count': {'$sum': 1}}
        }}
    ]
    rating_buckets = list(db.ratings.aggregate(pipeline))
    data['rating_categories'] = [
        {'category': 'Poor (1-4)', 'count': rating_buckets[0]['count'] if len(rating_buckets) > 0 else 0},
        {'category': 'Average (5-7)', 'count': rating_buckets[1]['count'] if len(rating_buckets) > 1 else 0},
        {'category': 'Good (8-10)', 'count': rating_buckets[2]['count'] if len(rating_buckets) > 2 else 0}
    ]
    
    # 6. Score distribution (Area Chart)
    pipeline = [
        {'$bucket': {
            'groupBy': '$score',
            'boundaries': [0, 5, 6, 7, 8, 9, 10],
            'default': 'Unknown',
            'output': {'count': {'$sum': 1}}
        }}
    ]
    data['score_distribution'] = list(db.animes.aggregate(pipeline))
    
    # 7. Score vs Rating Count scatter (episodes field doesn't exist in DB)
    pipeline = [
        {'$match': {'score': {'$exists': True, '$ne': None}}},
        {'$lookup': {
            'from': 'ratings',
            'localField': 'mal_id',
            'foreignField': 'anime_id',
            'as': 'ratings'
        }},
        {'$project': {
            '_id': 0,  # Exclude ObjectId
            'score': {'$toDouble': '$score'},
            'rating_count': {'$size': '$ratings'},
            'avg_user_rating': {'$avg': '$ratings.rating'}
        }},
        {'$match': {'rating_count': {'$gt': 10}}},  # At least 10 ratings
        {'$sample': {'size': 200}}
    ]
    data['episode_rating_scatter'] = list(db.animes.aggregate(pipeline))
    
    # 8. Genre co-occurrence (for heatmap)
    # Get top 10 genres first
    top_genres_data = data['genre_frequency'][:10]
    top_genres = [g['_id'] for g in top_genres_data]
    
    cooccurrence = {}
    for genre1 in top_genres:
        cooccurrence[genre1] = {}
        for genre2 in top_genres:
            if genre1 == genre2:
                cooccurrence[genre1][genre2] = 0
            else:
                # Count animes with both genres
                count = db.animes.count_documents({
                    'genres': {'$regex': f'.*{genre1}.*{genre2}.*|.*{genre2}.*{genre1}.*'}
                })
                cooccurrence[genre1][genre2] = count
    
    data['genre_cooccurrence'] = cooccurrence
    
    # 9. User engagement funnel
    total_users = db.users.count_documents({})
    users_with_ratings = db.ratings.distinct('user_id')
    active_users = db.watch_history.distinct('user_id')
    
    data['user_engagement_funnel'] = [
        {'stage': 'Registered Users', 'count': total_users},
        {'stage': 'Users with Ratings', 'count': len(users_with_ratings)},
        {'stage': 'Active Users', 'count': len(active_users)}
    ]
    
    # 10. Top animes for radar chart
    pipeline = [
        {'$sort': {'score': -1}},
        {'$limit': 5},
        {'$lookup': {
            'from': 'ratings',
            'localField': 'mal_id',
            'foreignField': 'anime_id',
            'as': 'ratings'
        }},
        {'$project': {
            '_id': 0,  # Exclude ObjectId
            'name': 1,
            'score': {'$multiply': ['$score', 10]},  # Normalize to 100
            'popularity': {'$min': [100, {'$multiply': [{'$divide': ['$members', 100000]}, 10]}]},
            'favorites': {'$min': [100, {'$multiply': [{'$divide': ['$favorites', 10000]}, 10]}]},
            'rating_count': {'$min': [100, {'$multiply': [{'$divide': [{'$size': '$ratings'}, 1000]}, 10]}]}
        }}
    ]
    data['top_anime_radar'] = list(db.animes.aggregate(pipeline))
    
    return jsonify({'data': data}), 200


@admin_bp.route('/models', methods=['GET'])
def get_models():
    """Get list of available ML models"""
    db = get_db()
    
    # Define available models with display names
    model_definitions = {
        'user_based_cf': 'User-Based CF',
        'item_based_cf': 'Item-Based CF',
        'hybrid': 'Hybrid',
        'neural_cf': 'Neural CF'
    }
    
    models = []
    
    # Query from model_registry collection (not 'models')
    for model_name, display_name in model_definitions.items():
        # Get model from registry
        model_doc = db.model_registry.find_one({'model_name': model_name})
        
        if model_doc:
            # Model exists in registry (trained)
            models.append({
                'name': model_name,
                'display_name': display_name,
                'is_active': model_doc.get('is_active', False),
                'trained_at': model_doc.get('trained_at'),
                'metrics': model_doc.get('metrics', {}),
                'status': 'trained'
            })
        else:
            # Model not yet trained
            models.append({
                'name': model_name,
                'display_name': display_name,
                'is_active': False,
                'trained_at': None,
                'metrics': {},
                'status': 'not_trained'
            })
    
    return jsonify({'models': models}), 200


@admin_bp.route('/models/select', methods=['POST'])
def select_model():
    """Select which model to use for recommendations"""
    data = request.get_json()
    
    if not data or 'model_name' not in data:
        return jsonify({'error': 'model_name is required'}), 400
    
    model_name = data['model_name']
    valid_models = ['user_based_cf', 'item_based_cf', 'hybrid', 'neural_cf']
    
    if model_name not in valid_models:
        return jsonify({'error': f'Invalid model. Choose from: {valid_models}'}), 400
    
    # Update recommendation service
    from app.services.recommendation_service import get_recommendation_service
    rec_service = get_recommendation_service()
    
    if not rec_service.set_active_model(model_name):
        return jsonify({'error': f'Could not load model {model_name}'}), 500
    
    db = get_db()
    
    # Deactivate all models in registry
    db.model_registry.update_many({}, {'$set': {'is_active': False}})
    
    # Activate selected model in registry
    db.model_registry.update_one(
        {'model_name': model_name},
        {
            '$set': {'is_active': True, 'activated_at': datetime.utcnow()},
            '$setOnInsert': {'model_name': model_name, 'created_at': datetime.utcnow()}
        },
        upsert=True
    )
    
    return jsonify({'message': f'Model {model_name} is now active'}), 200


@admin_bp.route('/models/train', methods=['POST'])
def train_model():
    """Trigger model training in background"""
    data = request.get_json()
    
    if not data or 'model_name' not in data:
        return jsonify({'error': 'model_name is required'}), 400
    
    model_name = data['model_name']
    valid_models = ['user_based_cf', 'item_based_cf', 'hybrid', 'neural_cf']
    
    if model_name not in valid_models:
        return jsonify({'error': f'Invalid model. Choose from: {valid_models}'}), 400
    
    # Get training service
    from app.services.training_service import get_training_service
    training_service = get_training_service()
    
    try:
        # Create training job
        job_id = training_service.create_job(model_name)
        
        # Start training in background
        def run_training(job_id, service):
            """Background training function"""
            try:
                # Mark as running
                service.mark_running(job_id)
                
                # Import training function
                from ml.training.individual_trainers import get_trainer
                trainer = get_trainer(model_name)
                
                # Define progress callback
                def progress_callback(progress: int, step: str):
                    service.update_progress(job_id, progress, step)
                
                # Run training
                model, metrics = trainer(progress_callback=progress_callback)
                
                # Mark as completed
                service.mark_completed(job_id, metrics)
                
            except Exception as e:
                import traceback
                error_msg = f"{str(e)}\n{traceback.format_exc()}"
                service.mark_failed(job_id, error_msg)
        
        # Start background thread
        training_service.start_training_background(job_id, run_training)
        
        return jsonify({
            'message': f'Training job started for {model_name}',
            'job_id': job_id,
            'status': 'pending'
        }), 202
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 409  # Conflict - another job running


@admin_bp.route('/models/train/status/<job_id>', methods=['GET'])
def get_training_status(job_id: str):
    """Get status of a training job"""
    from app.services.training_service import get_training_service
    training_service = get_training_service()
    
    job = training_service.get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job.to_dict()), 200


@admin_bp.route('/models/train/jobs', methods=['GET'])
def list_training_jobs():
    """List recent training jobs"""
    from app.services.training_service import get_training_service
    training_service = get_training_service()
    
    limit = request.args.get('limit', 10, type=int)
    jobs = training_service.list_jobs(limit=limit)
    
    return jsonify({'jobs': jobs}), 200


@admin_bp.route('/models/compare', methods=['GET'])
def compare_models():
    """Compare metrics of all models"""
    db = get_db()
    
    # Get all models from model_registry
    models = list(db.model_registry.find({}, {'_id': 0}))
    
    # Return comparison data
    comparison = []
    for model in models:
        comparison.append({
            'name': model.get('model_name'),  # Use model_name not name
            'metrics': model.get('metrics', {}),
            'trained_at': model.get('trained_at'),
            'is_active': model.get('is_active', False)
        })
    
    return jsonify({'comparison': comparison}), 200
