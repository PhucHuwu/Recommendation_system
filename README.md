# Backend README

# 🔧 Anime Recommendation System - Backend

Flask API Backend cho hệ thống gợi ý Anime.

## 📦 Cài đặt

### 1. Tạo virtual environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình environment

```bash
# Copy và chỉnh sửa file .env
cp .env.example .env
```

### 4. Khởi động MongoDB

Đảm bảo MongoDB đang chạy tại `localhost:27017`

### 5. Import dữ liệu

```bash
python scripts/import_data.py
```

### 6. Chạy server

```bash
python run.py
```

Server sẽ chạy tại `http://localhost:5000`

## 🔌 API Endpoints

| Endpoint              | Method     | Mô tả           |
| --------------------- | ---------- | --------------- |
| `/health`             | GET        | Health check    |
| `/api/auth/login`     | POST       | Đăng nhập       |
| `/api/auth/logout`    | POST       | Đăng xuất       |
| `/api/auth/me`        | GET        | Thông tin user  |
| `/api/anime`          | GET        | Danh sách anime |
| `/api/anime/:id`      | GET        | Chi tiết anime  |
| `/api/anime/search`   | GET        | Tìm kiếm anime  |
| `/api/anime/top`      | GET        | Top anime       |
| `/api/rating`         | POST       | Thêm rating     |
| `/api/rating/:id`     | PUT/DELETE | Sửa/xóa rating  |
| `/api/recommendation` | GET        | Lấy gợi ý       |
| `/api/history`        | GET/POST   | Lịch sử xem     |
| `/api/admin/stats`    | GET        | Thống kê        |
| `/api/admin/models`   | GET/POST   | Quản lý models  |

## 📁 Cấu trúc thư mục

```
backend/
├── app/
│   ├── __init__.py      # Flask app factory
│   ├── config.py        # Configuration
│   ├── routes/          # API endpoints
│   ├── models/          # DB models
│   ├── services/        # Business logic
│   └── utils/           # Utilities
├── ml/
│   ├── models/          # ML implementations
│   ├── training/        # Training scripts
│   └── saved_models/    # Trained models
├── scripts/
│   └── import_data.py   # Data import script
├── data/
│   ├── raw/             # Raw dataset
│   └── processed/       # Processed data
├── requirements.txt
├── run.py
└── .env
```
