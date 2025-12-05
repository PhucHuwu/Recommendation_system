# 🔧 IMPLEMENTATION PLAN: BACKEND

## Python + Flask + MongoDB

---

## 📋 Tổng quan

Backend xử lý toàn bộ logic nghiệp vụ, kết nối database, huấn luyện và phục vụ các mô hình recommendation.

---

## 🏗️ I. CẤU TRÚC THƯ MỤC

```
backend/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Cấu hình (MongoDB URI, secrets...)
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   ├── user.py              # User model
│   │   ├── anime.py             # Anime model
│   │   └── rating.py            # Rating model
│   ├── routes/                  # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py              # Đăng nhập/đăng xuất
│   │   ├── anime.py             # CRUD anime
│   │   ├── rating.py            # Rating endpoints
│   │   ├── recommendation.py    # Gợi ý phim
│   │   ├── history.py           # Lịch sử xem
│   │   └── admin.py             # Admin endpoints
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── recommendation_service.py
│   │   ├── training_service.py
│   │   └── visualization_service.py
│   └── utils/                   # Utilities
│       ├── __init__.py
│       ├── data_processor.py    # Xử lý dữ liệu
│       └── sparse_matrix.py     # Ma trận thưa
├── ml/                          # Machine Learning
│   ├── __init__.py
│   ├── models/
│   │   ├── user_based.py        # User-based CF
│   │   ├── item_based.py        # Item-based CF
│   │   └── content_based.py     # Content-based
│   ├── training/
│   │   ├── train.py             # Script huấn luyện
│   │   └── evaluate.py          # Đánh giá mô hình
│   └── saved_models/            # Lưu model đã train
├── data/
│   ├── raw/                     # Dữ liệu gốc từ Kaggle
│   └── processed/               # Dữ liệu đã xử lý
├── notebooks/                   # Jupyter notebooks (EDA, experiments)
├── tests/                       # Unit tests
├── requirements.txt
├── run.py                       # Entry point
└── .env                         # Environment variables
```

---

## 🔌 II. API ENDPOINTS

### 🔐 Authentication (`/api/auth`)

| Method | Endpoint  | Mô tả              | Request       | Response          |
| ------ | --------- | ------------------ | ------------- | ----------------- |
| `POST` | `/login`  | Đăng nhập          | `{ user_id }` | `{ token, user }` |
| `POST` | `/logout` | Đăng xuất          | -             | `{ message }`     |
| `GET`  | `/me`     | Lấy thông tin user | -             | `{ user }`        |

### 🎬 Anime (`/api/anime`)

| Method | Endpoint  | Mô tả           | Request        | Response              |
| ------ | --------- | --------------- | -------------- | --------------------- |
| `GET`  | `/`       | Danh sách anime | `?page, limit` | `{ animes[], total }` |
| `GET`  | `/:id`    | Chi tiết anime  | -              | `{ anime }`           |
| `GET`  | `/search` | Tìm kiếm        | `?q=name`      | `{ animes[] }`        |
| `GET`  | `/top`    | Top anime       | `?limit`       | `{ animes[] }`        |

### ⭐ Rating (`/api/rating`) - Thang điểm 1-10

| Method   | Endpoint         | Mô tả           | Request                      | Response        |
| -------- | ---------------- | --------------- | ---------------------------- | --------------- |
| `POST`   | `/`              | Thêm rating     | `{ anime_id, rating: 1-10 }` | `{ rating }`    |
| `PUT`    | `/:id`           | Cập nhật rating | `{ rating: 1-10 }`           | `{ rating }`    |
| `DELETE` | `/:id`           | Xóa rating      | -                            | `{ message }`   |
| `GET`    | `/user/:user_id` | Rating của user | -                            | `{ ratings[] }` |

> ⚠️ **Validation**: `rating` phải là số nguyên từ **1 đến 10** (theo dataset gốc)

### 🎯 Recommendation (`/api/recommendation`)

| Method | Endpoint             | Mô tả          | Request     | Response                |
| ------ | -------------------- | -------------- | ----------- | ----------------------- |
| `GET`  | `/`                  | Lấy gợi ý      | `?limit=10` | `{ recommendations[] }` |
| `GET`  | `/similar/:anime_id` | Anime tương tự | -           | `{ animes[] }`          |

### 📜 History (`/api/history`)

| Method | Endpoint         | Mô tả             | Request        | Response        |
| ------ | ---------------- | ----------------- | -------------- | --------------- |
| `GET`  | `/`              | Lịch sử bản thân  | -              | `{ history[] }` |
| `GET`  | `/user/:user_id` | Lịch sử user khác | -              | `{ history[] }` |
| `POST` | `/`              | Thêm vào lịch sử  | `{ anime_id }` | `{ history }`   |

### 👑 Admin (`/api/admin`)

| Method | Endpoint          | Mô tả                 | Request          | Response          |
| ------ | ----------------- | --------------------- | ---------------- | ----------------- |
| `GET`  | `/stats`          | Thống kê tổng quan    | -                | `{ stats }`       |
| `GET`  | `/visualization`  | Dữ liệu visualization | -                | `{ charts_data }` |
| `GET`  | `/models`         | Danh sách models      | -                | `{ models[] }`    |
| `POST` | `/models/select`  | Chọn model active     | `{ model_name }` | `{ message }`     |
| `POST` | `/models/train`   | Huấn luyện lại        | `{ model_name }` | `{ job_id }`      |
| `GET`  | `/models/compare` | So sánh models        | -                | `{ comparison }`  |

---

## 🤖 III. MACHINE LEARNING MODELS

### 1. User-Based Collaborative Filtering

```python
class UserBasedCF:
    """
    Gợi ý dựa trên sự tương đồng giữa các users.
    - Input: user_id, rating_matrix (sparse)
    - Output: top-K anime recommendations
    - Similarity: Cosine, Pearson
    """
```

### 2. Item-Based Collaborative Filtering

```python
class ItemBasedCF:
    """
    Gợi ý dựa trên sự tương đồng giữa các anime.
    - Input: anime_id, rating_matrix (sparse)
    - Output: similar animes
    - Similarity: Cosine
    """
```

### 3. Content-Based Filtering

```python
class ContentBasedCF:
    """
    Gợi ý dựa trên nội dung anime.
    - Features: Genres, Synopsis (TF-IDF/Embeddings)
    - Output: similar animes based on content
    """
```

### Đánh giá Models

| Metric          | Công thức                         | Mục đích         |
| --------------- | --------------------------------- | ---------------- |
| **RMSE**        | √(Σ(actual - predicted)²/n)       | Đo lỗi dự đoán   |
| **MAE**         | Σ\|actual - predicted\|/n         | Đo lỗi tuyệt đối |
| **Precision@K** | relevant ∩ recommended / K        | Độ chính xác     |
| **Recall@K**    | relevant ∩ recommended / relevant | Độ phủ           |

---

## 💾 IV. DATABASE SCHEMA (MongoDB)

### Collection: `users`

```json
{
    "_id": ObjectId,
    "user_id": 12345,
    "created_at": ISODate,
    "last_login": ISODate
}
```

### Collection: `animes`

```json
{
    "_id": ObjectId,
    "mal_id": 1,
    "name": "Cowboy Bebop",
    "score": 8.78,
    "genres": ["Action", "Adventure", "Sci-Fi"],
    "synopsis": "...",
    "image_url": "..."
}
```

### Collection: `ratings` (Thang điểm 1-10)

```json
{
    "_id": ObjectId,
    "user_id": 12345,
    "anime_id": 1,
    "rating": 9,              // Thang điểm 1-10 (integer)
    "created_at": ISODate,
    "updated_at": ISODate
}
```

> ⚠️ **Validation**: Rating phải là số nguyên từ **1 đến 10** (theo dataset gốc)

### Collection: `watch_history`

```json
{
    "_id": ObjectId,
    "user_id": 12345,
    "anime_id": 1,
    "watched_at": ISODate
}
```

### Collection: `models`

```json
{
    "_id": ObjectId,
    "name": "user_based_cf",
    "version": "1.0",
    "metrics": { "rmse": 0.85, "mae": 0.65 },
    "is_active": true,
    "trained_at": ISODate,
    "file_path": "saved_models/user_based_v1.pkl"
}
```

---

## 📦 V. DEPENDENCIES

```txt
# requirements.txt
flask==3.0.0
flask-cors==4.0.0
flask-jwt-extended==4.6.0
pymongo==4.6.0
python-dotenv==1.0.0

# Data Processing
pandas==2.1.0
numpy==1.26.0
scipy==1.11.0

# Machine Learning
scikit-learn==1.3.0
surprise==1.1.3

# NLP
nltk==3.8.0
gensim==4.3.0

# Visualization
matplotlib==3.8.0
seaborn==0.13.0

# Utils
kagglehub==0.2.0
tqdm==4.66.0
```

---

## ✅ VI. CHECKLIST TRIỂN KHAI

### Phase 1: Setup & Data

-   [ ] Khởi tạo Flask project
-   [ ] Cấu hình MongoDB connection
-   [ ] Download dataset từ Kaggle
-   [ ] Import data vào MongoDB
-   [ ] Xử lý và làm sạch dữ liệu

### Phase 2: Core APIs

-   [ ] Authentication endpoints
-   [ ] Anime CRUD endpoints
-   [ ] Rating endpoints
-   [ ] History endpoints
-   [ ] Search functionality

### Phase 3: ML Models

-   [ ] Implement User-based CF
-   [ ] Implement Item-based CF
-   [ ] Implement Content-based
-   [ ] Training pipeline
-   [ ] Evaluation metrics

### Phase 4: Admin Features

-   [ ] Stats & visualization API
-   [ ] Model selection
-   [ ] Retrain functionality
-   [ ] Model comparison

### Phase 5: Testing & Optimization

-   [ ] Unit tests
-   [ ] API tests
-   [ ] Performance optimization
-   [ ] Documentation

---

## 🚀 VII. CHẠY ỨNG DỤNG

```bash
# 1. Cài đặt dependencies
pip install -r requirements.txt

# 2. Cấu hình environment
cp .env.example .env
# Chỉnh sửa MONGODB_URI trong .env

# 3. Import data
python scripts/import_data.py

# 4. Train models
python ml/training/train.py

# 5. Chạy server
python run.py
# Server chạy tại http://localhost:5000
```
