# Backend - Anime Recommendation System

Flask-based REST API backend that powers the anime recommendation system with multiple machine learning models, including collaborative filtering, neural networks, and FAISS-powered semantic search.

## Table of Contents

-   [Overview](#overview)
-   [Technology Stack](#technology-stack)
-   [Project Structure](#project-structure)
-   [Getting Started](#getting-started)
-   [API Documentation](#api-documentation)
-   [Machine Learning Models](#machine-learning-models)
-   [Database Schema](#database-schema)
-   [Services](#services)
-   [Training Pipeline](#training-pipeline)
-   [Development](#development)
-   [Testing](#testing)
-   [Deployment](#deployment)

## Overview

The backend provides a comprehensive REST API for anime recommendations, user management, and model training. It implements five different recommendation strategies and combines them using a hybrid approach for optimal performance.

### Core Capabilities

-   RESTful API with JWT authentication
-   Multiple collaborative filtering algorithms
-   Neural network-based predictions
-   FAISS vector search for semantic similarity
-   Real-time model training and evaluation
-   User rating management and history
-   Admin dashboard with analytics

## Technology Stack

### Web Framework

-   **Flask**: 3.0.0 - Lightweight WSGI web application framework
-   **Flask-CORS**: 4.0.0 - Cross-Origin Resource Sharing support
-   **Flask-JWT-Extended**: 4.6.0 - JWT authentication

### Database

-   **PyMongo**: 4.6.0 - MongoDB driver
-   **MongoDB**: NoSQL database for user data and ratings

### Machine Learning

-   **scikit-learn**: 1.7.2 - Traditional ML algorithms
-   **scikit-surprise**: 1.1.4 - Collaborative filtering library
-   **PyTorch**: 2.0.1 - Deep learning framework
-   **FAISS**: 1.7.4 - Vector similarity search
-   **Sentence Transformers**: 2.2.2 - Embedding generation

### Data Processing

-   **Pandas**: 2.3.3 - Data manipulation and analysis
-   **NumPy**: 1.26.2 - Numerical computing
-   **SciPy**: 1.11.4 - Scientific computing

### Utilities

-   **python-dotenv**: 1.0.0 - Environment variable management
-   **NLTK**: 3.8.1 - Natural language processing
-   **tqdm**: 4.66.1 - Progress bars
-   **kagglehub**: 0.2.5 - Dataset management

## Project Structure

```
backend/
├── app/                               # Flask application package
│   ├── __init__.py                    # App factory and initialization
│   ├── config.py                      # Configuration settings
│   ├── routes/                        # API endpoints
│   │   ├── __init__.py                # Blueprint registration
│   │   ├── auth.py                    # Authentication endpoints
│   │   ├── anime.py                   # Anime CRUD operations
│   │   ├── rating.py                  # Rating management
│   │   ├── recommendation.py          # Recommendation endpoints
│   │   ├── search.py                  # Search functionality
│   │   ├── history.py                 # User history
│   │   └── admin.py                   # Admin operations
│   ├── services/                      # Business logic layer
│   │   ├── recommendation_service.py  # Recommendation logic
│   │   └── training_service.py        # Model training logic
│   └── models/                        # Data models (if using ORM)
├── ml/                                # Machine Learning modules
│   ├── models/                        # ML model implementations
│   │   ├── user_based.py              # User-based collaborative filtering
│   │   ├── item_based.py              # Item-based collaborative filtering
│   │   ├── neural_cf.py               # Neural collaborative filtering
│   │   └── hybrid.py                  # Hybrid model
│   ├── services/                      # ML services
│   │   ├── embedding_service.py       # Text embedding generation
│   │   └── faiss_service.py           # FAISS index management
│   ├── training/                      # Training scripts
│   │   ├── train.py                   # Main training script
│   │   ├── evaluate.py                # Model evaluation
│   │   ├── individual_trainers.py     # Individual model trainers
│   │   └── re_evaluate_ncf.py         # NCF re-evaluation
│   └── saved_models/                  # Trained model storage
│       ├── neural_cf.pt               # PyTorch model weights
│       ├── faiss_index.bin            # FAISS index
│       └── *.pkl                      # Pickled models
├── scripts/                           # Utility scripts
│   ├── import_data.py                 # Data import from Kaggle
│   └── build_faiss_index.py           # FAISS index builder
├── run.py                             # Application entry point
└── requirements.txt                   # Python dependencies
```

## Getting Started

### Prerequisites

-   Python 3.8 or higher
-   MongoDB 4.4 or higher
-   pip (Python package manager)
-   Virtual environment (recommended)

### Installation

1. **Create Virtual Environment**

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. **Install Dependencies**

```bash
pip install -r ../requirements.txt
```

3. **Environment Configuration**

Create a `.env` file in the backend directory:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DEBUG=True

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ACCESS_TOKEN_EXPIRES=86400

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=anime_recommendation

# API Configuration
API_PREFIX=/api

# FAISS Configuration
FAISS_INDEX_PATH=ml/saved_models/faiss_index.bin
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_DIM=384
```

4. **Initialize Database**

Start MongoDB:

```bash
# Windows
net start MongoDB

# Linux
sudo systemctl start mongod

# Mac
brew services start mongodb-community
```

Import initial data:

```bash
python scripts/import_data.py
```

5. **Build FAISS Index**

```bash
python scripts/build_faiss_index.py
```

6. **Run Application**

```bash
python run.py
```

The API will be available at http://localhost:5000

### Quick Start

```bash
# Health check
curl http://localhost:5000/health

# Register user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "password123", "email": "test@example.com"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "password123"}'
```

## API Documentation

### Base URL

```
http://localhost:5000/api
```

### Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

### Endpoints

#### Authentication (`/api/auth`)

**Register User**

```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "string",
  "password": "string",
  "email": "string"
}

Response: 201 Created
{
  "user": {
    "id": "string",
    "username": "string",
    "email": "string"
  },
  "token": "string"
}
```

**Login**

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}

Response: 200 OK
{
  "user": {...},
  "token": "string"
}
```

**Get Profile** (Protected)

```http
GET /api/auth/profile
Authorization: Bearer <token>

Response: 200 OK
{
  "id": "string",
  "username": "string",
  "email": "string",
  "created_at": "datetime"
}
```

#### Anime (`/api/anime`)

**Get Anime List**

```http
GET /api/anime?page=1&limit=20&genre=Action&sort=rating

Response: 200 OK
{
  "anime": [...],
  "total": number,
  "page": number,
  "pages": number
}
```

**Get Anime Details**

```http
GET /api/anime/:id

Response: 200 OK
{
  "anime_id": number,
  "name": "string",
  "genre": "string",
  "type": "string",
  "episodes": number,
  "rating": number,
  "members": number,
  "description": "string"
}
```

#### Recommendations (`/api/recommendations`)

**Get Personalized Recommendations**

```http
GET /api/recommendations/:user_id?model=hybrid&n=10

Parameters:
- model: user_based | item_based | ncf | hybrid (default: hybrid)
- n: number of recommendations (default: 10)

Response: 200 OK
{
  "recommendations": [
    {
      "anime_id": number,
      "predicted_rating": number,
      "anime": {...}
    }
  ],
  "model_used": "string"
}
```

**Get Similar Anime**

```http
GET /api/recommendations/:user_id/similar/:anime_id?n=10

Response: 200 OK
{
  "similar_anime": [
    {
      "anime_id": number,
      "similarity_score": number,
      "anime": {...}
    }
  ]
}
```

#### Ratings (`/api/ratings`)

**Submit Rating** (Protected)

```http
POST /api/ratings
Authorization: Bearer <token>
Content-Type: application/json

{
  "anime_id": number,
  "rating": number (1-10)
}

Response: 201 Created
{
  "rating_id": "string",
  "user_id": "string",
  "anime_id": number,
  "rating": number,
  "created_at": "datetime"
}
```

**Get User Ratings**

```http
GET /api/ratings/user/:user_id

Response: 200 OK
{
  "ratings": [...]
}
```

**Delete Rating** (Protected)

```http
DELETE /api/ratings/:rating_id
Authorization: Bearer <token>

Response: 204 No Content
```

#### Search (`/api/search`)

**Search Anime**

```http
GET /api/search?q=naruto&type=semantic&limit=20

Parameters:
- q: search query
- type: keyword | semantic (default: keyword)
- limit: max results (default: 20)

Response: 200 OK
{
  "results": [...],
  "search_type": "string"
}
```

#### Admin (`/api/admin`)

**Train Models** (Protected, Admin Only)

```http
POST /api/admin/train
Authorization: Bearer <token>
Content-Type: application/json

{
  "models": ["user_based", "item_based", "ncf", "hybrid"],
  "test_size": 0.2
}

Response: 200 OK
{
  "status": "success",
  "results": {
    "user_based": {
      "rmse": number,
      "mae": number,
      "training_time": number
    },
    ...
  }
}
```

**Get Model Metrics** (Protected, Admin Only)

```http
GET /api/admin/metrics

Response: 200 OK
{
  "metrics": {
    "user_based": {...},
    "item_based": {...},
    "ncf": {...},
    "hybrid": {...}
  },
  "last_trained": "datetime"
}
```

## Machine Learning Models

### 1. User-Based Collaborative Filtering

**File**: `ml/models/user_based.py`

Finds users with similar rating patterns and recommends anime they enjoyed.

**Algorithm**:

-   Compute user-user similarity using Pearson correlation
-   Find K nearest neighbors for target user
-   Predict ratings based on weighted average of neighbor ratings

**Key Features**:

-   Handles sparse data
-   Cold-start support for new items
-   Configurable K neighbors

**Usage**:

```python
from ml.models.user_based import UserBasedCF

model = UserBasedCF(k=20, min_support=5)
model.fit(ratings_df)
prediction = model.predict(user_id, anime_id)
recommendations = model.recommend(user_id, n=10)
```

### 2. Item-Based Collaborative Filtering

**File**: `ml/models/item_based.py`

Recommends anime similar to those the user has rated highly.

**Algorithm**:

-   Compute item-item similarity using adjusted cosine similarity
-   For each item user hasn't rated, find similar rated items
-   Predict rating based on weighted average

**Key Features**:

-   More stable than user-based (items don't change frequently)
-   Better for large user bases
-   Pre-computed similarities for efficiency

**Usage**:

```python
from ml.models.item_based import ItemBasedCF

model = ItemBasedCF(k=20)
model.fit(ratings_df)
prediction = model.predict(user_id, anime_id)
recommendations = model.recommend(user_id, n=10)
```

### 3. Neural Collaborative Filtering (NCF)

**File**: `ml/models/neural_cf.py`

Deep learning model that learns latent representations of users and items.

**Architecture**:

-   Embedding layers for users and items
-   Multi-layer perceptron (MLP)
-   Output layer for rating prediction

**Training**:

-   Optimizer: Adam
-   Loss: Mean Squared Error (MSE)
-   Batch size: 256
-   Epochs: 10-20

**Key Features**:

-   Captures non-linear relationships
-   Learns from complex patterns
-   Handles cold-start with metadata

**Usage**:

```python
from ml.models.neural_cf import NeuralCF

model = NeuralCF(
    n_users=num_users,
    n_items=num_items,
    embedding_dim=64,
    hidden_layers=[128, 64, 32]
)
model.train(train_loader, epochs=10)
prediction = model.predict(user_id, anime_id)
```

### 4. Hybrid Weighted Model

**File**: `ml/models/hybrid.py`

Combines multiple models using weighted averaging.

**Strategy**:

```
prediction = α × user_based + β × item_based + γ × ncf
where α + β + γ = 1
```

**Key Features**:

-   Leverages strengths of all models
-   Configurable weights
-   Fallback when models can't predict
-   Optimizable weights based on validation data

**Usage**:

```python
from ml.models.hybrid import HybridWeightedCF

hybrid = HybridWeightedCF(
    user_based_model=user_model,
    item_based_model=item_model,
    user_weight=0.4,
    item_weight=0.6
)
prediction = hybrid.predict(user_id, anime_id)
recommendations = hybrid.recommend(user_id, n=10)
```

### 5. FAISS Semantic Search

**Files**: `ml/services/faiss_service.py`, `ml/services/embedding_service.py`

Vector-based similarity search for content discovery.

**Components**:

-   **Embedding Service**: Generates text embeddings using Sentence Transformers
-   **FAISS Service**: Manages vector index and similarity search

**Process**:

1. Generate embeddings for anime descriptions
2. Build FAISS index for efficient search
3. Query with text to find similar anime

**Key Features**:

-   Multilingual support
-   Sub-second search times
-   Semantic understanding

**Usage**:

```python
from ml.services.faiss_service import FAISSService

faiss_service = FAISSService()
faiss_service.build_index(anime_df)
similar_anime = faiss_service.search("action anime with magic", k=10)
```

## Database Schema

### Collections

#### users

```javascript
{
  _id: ObjectId,
  username: String (unique),
  email: String (unique),
  password_hash: String,
  is_admin: Boolean,
  created_at: DateTime,
  updated_at: DateTime
}
```

#### anime

```javascript
{
  _id: ObjectId,
  anime_id: Number (unique),
  name: String,
  genre: String,
  type: String,
  episodes: Number,
  rating: Number,
  members: Number,
  description: String,
  image_url: String,
  created_at: DateTime
}
```

#### ratings

```javascript
{
  _id: ObjectId,
  user_id: ObjectId (ref: users),
  anime_id: Number (ref: anime),
  rating: Number (1-10),
  created_at: DateTime,
  updated_at: DateTime
}
```

#### model_metrics

```javascript
{
  _id: ObjectId,
  model_name: String,
  rmse: Number,
  mae: Number,
  precision_at_k: Number,
  recall_at_k: Number,
  coverage: Number,
  training_time: Number,
  trained_at: DateTime
}
```

### Indexes

```javascript
// users
db.users.createIndex({ username: 1 }, { unique: true });
db.users.createIndex({ email: 1 }, { unique: true });

// anime
db.anime.createIndex({ anime_id: 1 }, { unique: true });
db.anime.createIndex({ name: "text" });
db.anime.createIndex({ genre: 1 });

// ratings
db.ratings.createIndex({ user_id: 1, anime_id: 1 }, { unique: true });
db.ratings.createIndex({ user_id: 1 });
db.ratings.createIndex({ anime_id: 1 });

// model_metrics
db.model_metrics.createIndex({ model_name: 1, trained_at: -1 });
```

## Services

### Recommendation Service

**File**: `app/services/recommendation_service.py`

Provides high-level recommendation functionality.

**Methods**:

-   `get_recommendations(user_id, model, n)`: Get personalized recommendations
-   `get_similar_anime(user_id, anime_id, n)`: Find similar anime
-   `predict_rating(user_id, anime_id, model)`: Predict single rating
-   `batch_predict(user_id, anime_ids, model)`: Predict multiple ratings

### Training Service

**File**: `app/services/training_service.py`

Manages model training and evaluation.

**Methods**:

-   `train_all_models()`: Train all models
-   `train_model(model_name)`: Train specific model
-   `evaluate_model(model_name)`: Evaluate model performance
-   `save_model(model, path)`: Persist model to disk
-   `load_model(path)`: Load model from disk

## Training Pipeline

### Training Process

1. **Data Preparation**

    ```python
    # Load ratings from database
    ratings = load_ratings_from_db()

    # Split train/test
    train, test = train_test_split(ratings, test_size=0.2)
    ```

2. **Model Training**

    ```python
    # Train individual models
    user_model = train_user_based(train)
    item_model = train_item_based(train)
    ncf_model = train_neural_cf(train)

    # Train hybrid
    hybrid_model = train_hybrid(user_model, item_model, ncf_model)
    ```

3. **Evaluation**

    ```python
    # Evaluate on test set
    metrics = evaluate_model(model, test)
    # RMSE, MAE, Precision@K, Recall@K, Coverage
    ```

4. **Model Persistence**
    ```python
    # Save models
    save_model(user_model, 'ml/saved_models/user_based.pkl')
    save_model(ncf_model, 'ml/saved_models/neural_cf.pt')
    ```

### Training Script

**File**: `ml/training/train.py`

```bash
# Train all models
python -m ml.training.train --all

# Train specific model
python -m ml.training.train --model user_based

# Train with custom parameters
python -m ml.training.train --model ncf --epochs 20 --batch-size 512
```

### Evaluation Metrics

-   **RMSE** (Root Mean Squared Error): Lower is better
-   **MAE** (Mean Absolute Error): Lower is better
-   **Precision@K**: Percentage of relevant items in top K
-   **Recall@K**: Percentage of relevant items retrieved in top K
-   **Coverage**: Percentage of items that can be recommended
-   **Training Time**: Time to train model

## Development

### Project Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install pytest pytest-cov black flake8 mypy
```

### Code Style

Follow PEP 8 guidelines:

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### Adding New Endpoints

1. Create route in `app/routes/`:

```python
# app/routes/my_route.py
from flask import Blueprint, request, jsonify

bp = Blueprint('my_route', __name__)

@bp.route('/my-endpoint', methods=['GET'])
def my_endpoint():
    return jsonify({'message': 'Hello World'})
```

2. Register blueprint in `app/routes/__init__.py`:

```python
from .my_route import bp as my_route_bp

def register_blueprints(app):
    app.register_blueprint(my_route_bp, url_prefix='/api/my-route')
```

### Adding New Models

1. Create model class in `ml/models/`:

```python
# ml/models/my_model.py
class MyModel:
    def __init__(self, **kwargs):
        pass

    def fit(self, train_data):
        pass

    def predict(self, user_id, anime_id):
        pass

    def recommend(self, user_id, n=10):
        pass
```

2. Add trainer in `ml/training/individual_trainers.py`

3. Update hybrid model to include new model

## Testing

### Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov=ml

# Run specific test file
pytest tests/test_models.py

# Run specific test
pytest tests/test_models.py::test_user_based_cf
```

### Test Structure

```
tests/
├── conftest.py              # Pytest fixtures
├── test_models.py           # Model tests
├── test_routes.py           # API endpoint tests
├── test_services.py         # Service tests
└── test_integration.py      # Integration tests
```

### Example Test

```python
import pytest
from ml.models.user_based import UserBasedCF

def test_user_based_cf_predict():
    model = UserBasedCF(k=10)
    model.fit(train_data)

    prediction = model.predict(user_id=1, anime_id=100)

    assert 1 <= prediction <= 10
    assert isinstance(prediction, float)
```

## Deployment

### Production Configuration

**File**: `app/config.py`

```python
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

    # Use environment variables
    SECRET_KEY = os.getenv('SECRET_KEY')
    MONGODB_URI = os.getenv('MONGODB_URI')

    # Security headers
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
```

### Running in Production

**Using Gunicorn**:

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

**Using Docker**:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

```bash
# Build image
docker build -t anime-backend .

# Run container
docker run -p 5000:5000 -e MONGODB_URI=mongodb://host:27017 anime-backend
```

### Environment Variables

Production `.env`:

```env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=<strong-secret-key>
JWT_SECRET_KEY=<strong-jwt-secret>
MONGODB_URI=mongodb://username:password@host:27017/
MONGODB_DB=anime_recommendation
```

### Performance Optimization

-   Use Redis for caching recommendations
-   Implement connection pooling for MongoDB
-   Pre-compute item similarities
-   Use CDN for static assets
-   Enable gzip compression
-   Implement rate limiting

### Monitoring

-   Log all API requests
-   Track model performance metrics
-   Monitor database queries
-   Set up error tracking (e.g., Sentry)
-   Implement health check endpoints

## Troubleshooting

### Common Issues

**MongoDB Connection Errors**:

-   Verify MongoDB is running: `systemctl status mongod`
-   Check connection string in `.env`
-   Ensure network connectivity

**Model Loading Errors**:

-   Verify model files exist in `ml/saved_models/`
-   Check file permissions
-   Ensure models are trained before loading

**Import Errors**:

-   Activate virtual environment
-   Install all dependencies: `pip install -r requirements.txt`
-   Check Python version compatibility

**Performance Issues**:

-   Enable model caching
-   Pre-compute recommendations
-   Optimize database queries with indexes
-   Use batch predictions

## Best Practices

1. **API Design**

    - Use RESTful conventions
    - Version your API
    - Return appropriate status codes
    - Include error messages

2. **Security**

    - Use HTTPS in production
    - Validate all inputs
    - Implement rate limiting
    - Use strong JWT secrets

3. **Model Management**

    - Version your models
    - Track model performance
    - Retrain periodically
    - A/B test new models

4. **Code Quality**
    - Write docstrings
    - Add type hints
    - Write unit tests
    - Use linting tools

## Resources

-   [Flask Documentation](https://flask.palletsprojects.com/)
-   [PyTorch Documentation](https://pytorch.org/docs/)
-   [scikit-learn Documentation](https://scikit-learn.org/)
-   [MongoDB Python Driver](https://pymongo.readthedocs.io/)
-   [FAISS Documentation](https://faiss.ai/)

---

For frontend documentation, see [../frontend/README_FE.md](../frontend/README_FE.md)
