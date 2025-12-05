from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import get_db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login with user_id only (no password required as per requirements)"""
    data = request.get_json()
    
    if not data or 'user_id' not in data:
        return jsonify({'error': 'user_id is required'}), 400
    
    try:
        user_id = int(data['user_id'])
    except ValueError:
        return jsonify({'error': 'user_id must be a number'}), 400
    
    db = get_db()
    
    if user_id != 0:
        user_exists = db.ratings.find_one({'user_id': user_id})
        
        if not user_exists:
            # Check if user_id is in valid range (for demo purposes)
            # In production, you might want different validation
            return jsonify({'error': 'User not found. Please use a valid user_id from the dataset.'}), 404
    
    # Update or create user record
    db.users.update_one(
        {'user_id': user_id},
        {
            '$set': {
                'user_id': user_id,
                'last_login': datetime.utcnow()
            },
            '$setOnInsert': {
                'created_at': datetime.utcnow()
            }
        },
        upsert=True
    )
    
    # Create JWT token
    access_token = create_access_token(identity=str(user_id))
    
    return jsonify({
        'message': 'Login successful',
        'token': access_token,
        'user': {
            'user_id': user_id
        }
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client should discard the token)"""
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current logged in user info"""
    user_id = int(get_jwt_identity())
    db = get_db()
    
    user = db.users.find_one({'user_id': user_id}, {'_id': 0})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user stats
    rating_count = db.ratings.count_documents({'user_id': user_id})
    history_count = db.watch_history.count_documents({'user_id': user_id})
    
    return jsonify({
        'user': {
            **user,
            'rating_count': rating_count,
            'history_count': history_count
        }
    }), 200
