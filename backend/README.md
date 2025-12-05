# 🚀 Backend API - Quick Start Guide

## ✅ Hoàn thành

Backend đã hoàn thành với đầy đủ tính năng:

-   ✅ Flask API với tất cả endpoints
-   ✅ MongoDB integration (16K animes, 3M ratings)
-   ✅ 3 ML models đã được train
-   ✅ Recommendation service tích hợp

---

## 🔧 Chạy Server

### 1. Activate environment

```bash
# Windows
cd backend
..\venv\Scripts\activate

# hoặc nếu dùng conda
conda activate RCMsys
```

### 2. Chạy Flask server

```bash
python run.py
```

Server sẽ chạy tại: `http://localhost:5000`

---

## 🔌 API Endpoints

### Health Check

```
GET /health
```

### Authentication

| Endpoint           | Method | Mô tả                 |
| ------------------ | ------ | --------------------- |
| `/api/auth/login`  | POST   | Đăng nhập với user_id |
| `/api/auth/logout` | POST   | Đăng xuất             |
| `/api/auth/me`     | GET    | Thông tin user        |

### Anime

| Endpoint                  | Method | Mô tả                        |
| ------------------------- | ------ | ---------------------------- |
| `/api/anime`              | GET    | Danh sách anime (pagination) |
| `/api/anime/:id`          | GET    | Chi tiết anime               |
| `/api/anime/search?q=...` | GET    | Tìm kiếm anime               |
| `/api/anime/top`          | GET    | Top anime                    |
| `/api/anime/genres`       | GET    | Danh sách genres             |

### Rating (Thang 1-10)

| Endpoint                    | Method | Mô tả              |
| --------------------------- | ------ | ------------------ |
| `/api/rating`               | POST   | Thêm rating (1-10) |
| `/api/rating/:id`           | PUT    | Cập nhật rating    |
| `/api/rating/:id`           | DELETE | Xóa rating         |
| `/api/rating/user/:user_id` | GET    | Rating của user    |

### Recommendation (ML-powered)

| Endpoint                                | Method | Mô tả             |
| --------------------------------------- | ------ | ----------------- |
| `/api/recommendation?limit=10`          | GET    | Gợi ý cá nhân hóa |
| `/api/recommendation/similar/:anime_id` | GET    | Anime tương tự    |

### History

| Endpoint                     | Method | Mô tả                 |
| ---------------------------- | ------ | --------------------- |
| `/api/history`               | GET    | Lịch sử xem của mình  |
| `/api/history/user/:user_id` | GET    | Lịch sử của user khác |
| `/api/history`               | POST   | Thêm vào lịch sử      |

### Admin

| Endpoint                    | Method | Mô tả             |
| --------------------------- | ------ | ----------------- |
| `/api/admin/stats`          | GET    | Thống kê hệ thống |
| `/api/admin/visualization`  | GET    | Dữ liệu visualize |
| `/api/admin/models`         | GET    | Danh sách models  |
| `/api/admin/models/select`  | POST   | Chọn model active |
| `/api/admin/models/train`   | POST   | Train lại model   |
| `/api/admin/models/compare` | GET    | So sánh models    |

---

## 🤖 ML Models

### Models đã train:

1. **User-Based CF** (`user_based_cf`)

    - Gợi ý dựa trên users tương tự
    - K=50 neighbors

2. **Item-Based CF** (`item_based_cf`)

    - Gợi ý dựa trên anime tương tự
    - K=30 similar items

3. **Content-Based** (`content_based`)
    - Gợi ý dựa trên nội dung (genres, synopsis)
    - TF-IDF + MultiLabelBinarizer

### Chuyển đổi model:

```bash
POST /api/admin/models/select
{
  "model_name": "user_based_cf"  # hoặc item_based_cf, content_based
}
```

---

## 📊 Database

### MongoDB Collections:

-   `animes` - 16,214 animes
-   `ratings` - 3,000,000 ratings
-   `users` - User accounts
-   `watch_history` - Lịch sử xem
-   `models` - Model registry

---

## 🧪 Test API

### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

### Get Recommendations

```bash
curl -X GET http://localhost:5000/api/recommendation?limit=10 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Similar Animes

```bash
curl -X GET http://localhost:5000/api/recommendation/similar/1?limit=10
```

---

## 📁 Cấu trúc Backend

```
backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration
│   ├── routes/              # API endpoints
│   │   ├── auth.py
│   │   ├── anime.py
│   │   ├── rating.py
│   │   ├── recommendation.py  # ML-powered
│   │   ├── history.py
│   │   └── admin.py
│   └── services/
│       └── recommendation_service.py  # ML service
├── ml/
│   ├── models/              # ML implementations
│   ├── training/            # Training scripts
│   └── saved_models/        # Trained models (.pkl)
├── scripts/
│   └── import_data.py
└── run.py                   # Entry point
```
