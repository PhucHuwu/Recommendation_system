# ML Models README

## 📚 Recommendation Models

Hệ thống có 3 models recommendation:

### 1. User-Based Collaborative Filtering

-   **File**: `ml/models/user_based.py`
-   **Cách hoạt động**: Tìm users tương tự dựa trên lịch sử rating, gợi ý anime mà các users tương tự đã thích
-   **Similarity**: Cosine Similarity
-   **Parameters**: `k_neighbors=50`

### 2. Item-Based Collaborative Filtering

-   **File**: `ml/models/item_based.py`
-   **Cách hoạt động**: Tìm anime tương tự dựa trên rating patterns, gợi ý anime tương tự với những anime user đã thích
-   **Similarity**: Cosine Similarity
-   **Parameters**: `k_similar=30`

### 3. Content-Based Filtering

-   **File**: `ml/models/content_based.py`
-   **Cách hoạt động**: Phân tích nội dung anime (genres, synopsis), gợi ý anime có nội dung tương tự
-   **Features**: TF-IDF cho synopsis + MultiLabelBinarizer cho genres
-   **Parameters**: `use_synopsis=True, use_genres=True`

---

## 🚀 Training Models

### Chạy training pipeline

```bash
cd backend
python ml/training/train.py
```

Script sẽ:

1. Load dữ liệu từ MongoDB
2. Train 3 models
3. Lưu models vào `ml/saved_models/`
4. Cập nhật model registry trong MongoDB

### Models được lưu

-   `ml/saved_models/user_based_cf.pkl`
-   `ml/saved_models/item_based_cf.pkl`
-   `ml/saved_models/content_based.pkl`

---

## 📊 Evaluation Metrics

File `ml/training/evaluate.py` cung cấp:

-   **RMSE** (Root Mean Square Error): Đo lỗi dự đoán rating
-   **MAE** (Mean Absolute Error): Đo lỗi tuyệt đối
-   **Precision@K**: Độ chính xác của top-K recommendations
-   **Recall@K**: Độ phủ của top-K recommendations

---

## 🔧 Sử dụng Models

### Load model

```python
from ml.models.user_based import UserBasedCF

# Load trained model
model = UserBasedCF.load('ml/saved_models/user_based_cf.pkl')

# Get recommendations
recommendations = model.recommend(user_id=123, n=10)
# Returns: [(anime_id, predicted_rating), ...]

# Predict rating
rating = model.predict(user_id=123, anime_id=456)
```

### Tương tự cho các models khác

```python
from ml.models.item_based import ItemBasedCF
from ml.models.content_based import ContentBasedCF

# Item-Based CF
item_model = ItemBasedCF.load('ml/saved_models/item_based_cf.pkl')
similar_animes = item_model.get_similar_animes(anime_id=1, n=10)

# Content-Based
content_model = ContentBasedCF.load('ml/saved_models/content_based.pkl')
similar_animes = content_model.get_similar_animes(anime_id=1, n=10)
```

---

## 📁 Cấu trúc ML

```
ml/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── user_based.py      # User-Based CF
│   ├── item_based.py      # Item-Based CF
│   └── content_based.py   # Content-Based
├── training/
│   ├── __init__.py
│   ├── train.py           # Training pipeline
│   └── evaluate.py        # Evaluation metrics
└── saved_models/          # Trained models (.pkl)
    ├── user_based_cf.pkl
    ├── item_based_cf.pkl
    └── content_based.pkl
```
