# Kế Hoạch Thực Hiện Dự Án Hệ Thống Gợi Ý (Recommendation System)

## Mục Tiêu Dự Án

Xây dựng một hệ thống gợi ý hoàn chỉnh với khả năng thu thập, xử lý dữ liệu, xây dựng mô hình recommendation, và hiển thị gợi ý cho người dùng thông qua giao diện web.

## Lựa Chọn Lĩnh Vực

> [!IMPORTANT] > **Cần xác định lĩnh vực hệ thống gợi ý:**
>
> -   Gợi ý phim (Movies)
> -   Gợi ý sản phẩm thương mại điện tử (E-commerce)
> -   Gợi ý nhạc (Music)
> -   Gợi ý sách (Books)
>
> **Khuyến nghị:** Chọn **Gợi ý phim** do có nhiều dataset công khai sẵn có (MovieLens, TMDB, IMDb) và dễ triển khai các tính năng nâng cao.

## Các Thay Đổi Đề Xuất

### Cấu Trúc Dự Án

```
Recommendation_system/
├── data/
│   ├── raw/                    # Dữ liệu gốc
│   ├── processed/              # Dữ liệu đã xử lý
│   └── models/                 # Mô hình đã train
├── notebooks/
│   ├── 01_data_collection.ipynb      # Thu thập dữ liệu
│   ├── 02_data_cleaning.ipynb        # Làm sạch dữ liệu
│   ├── 03_eda_visualization.ipynb    # Phân tích & trực quan hóa
│   ├── 04_model_building.ipynb       # Xây dựng mô hình
│   └── 05_model_evaluation.ipynb     # Đánh giá mô hình
├── src/
│   ├── data_processing/
│   │   ├── collector.py        # Thu thập dữ liệu
│   │   ├── cleaner.py          # Làm sạch dữ liệu
│   │   └── preprocessor.py     # Tiền xử lý
│   ├── models/
│   │   ├── collaborative_filtering.py
│   │   ├── content_based.py
│   │   └── hybrid.py
│   ├── evaluation/
│   │   └── metrics.py          # Các metrics đánh giá
│   └── utils/
│       └── helpers.py
├── web_app/
│   ├── app.py                  # Flask/Streamlit app
│   ├── templates/              # HTML templates
│   ├── static/                 # CSS, JS, images
│   └── requirements.txt
├── tests/                      # Unit tests
├── reports/                    # Báo cáo
├── videos/                     # Video demo
├── requirements.txt
└── README.md
```

---

## Chi Tiết Các Giai Đoạn Thực Hiện

### Giai Đoạn 1: Thu Thập Dữ Liệu

**Mục tiêu:** Thu thập dataset ≥ 2,000 items với ≥ 5 features

#### [NEW] [collector.py](file:///d:/Project/Git/Recommendation_system/src/data_processing/collector.py)

-   Triển khai thu thập dữ liệu từ nguồn công khai (Kaggle, API, web scraping)
-   Lưu trữ dữ liệu gốc vào `data/raw/`
-   Hỗ trợ các nguồn:
    -   **MovieLens Dataset** (khuyến nghị - đơn giản)
    -   **TMDB API** (nếu cần dữ liệu thời gian thực)
    -   **IMDb datasets** (dữ liệu phong phú)

#### [NEW] [01_data_collection.ipynb](file:///d:/Project/Git/Recommendation_system/notebooks/01_data_collection.ipynb)

-   Notebook hướng dẫn thu thập dữ liệu
-   Khám phát cấu trúc dữ liệu ban đầu
-   Xác minh đủ yêu cầu (≥2000 items, ≥5 features)

**Features cần có (ví dụ cho phim):**

1. Title (tên phim)
2. Genres (thể loại)
3. Rating (đánh giá)
4. Year (năm phát hành)
5. Director/Cast (đạo diễn/diễn viên)
6. Description/Plot (mô tả)
7. Duration (thời lượng)

---

### Giai Đoạn 2: Làm Sạch và Chuẩn Bị Dữ Liệu

**Mục tiêu:** Thực hiện ≥ 3 tác vụ làm sạch dữ liệu

#### [NEW] [cleaner.py](file:///d:/Project/Git/Recommendation_system/src/data_processing/cleaner.py)

-   **Xử lý Missing Values:** Imputation, drop rows/columns
-   **Loại bỏ Duplicates:** Dựa trên ID hoặc features chính
-   **Xử lý Outliers:** IQR method, Z-score
-   **Chuẩn hóa dữ liệu:** StandardScaler, MinMaxScaler

#### [NEW] [preprocessor.py](file:///d:/Project/Git/Recommendation_system/src/data_processing/preprocessor.py)

-   **Vector hóa text:**
    -   TF-IDF cho descriptions/genres
    -   Word embeddings (Word2Vec, GloVe) cho nâng cao
-   **Feature engineering:**
    -   Tạo features mới từ existing data
    -   Encoding categorical features
-   Lưu processed data vào `data/processed/`

#### [NEW] [02_data_cleaning.ipynb](file:///d:/Project/Git/Recommendation_system/notebooks/02_data_cleaning.ipynb)

-   Notebook chi tiết quá trình làm sạch
-   Báo cáo trước/sau cleaning
-   Visualize missing data patterns

---

### Giai Đoạn 3: Phân Tích & Trực Quan Hóa Dữ Liệu

**Mục tiêu:** Thực hiện ≥ 3 tác vụ trực quan hóa

#### [NEW] [03_eda_visualization.ipynb](file:///d:/Project/Git/Recommendation_system/notebooks/03_eda_visualization.ipynb)

-   **Phân bố Rating:** Histogram, density plot
-   **Tần suất thể loại:** Bar chart top genres
-   **Top Items:** Top rated, most popular
-   **Heatmap:** Correlation matrix giữa features
-   **Time series:** Xu hướng theo năm (nếu có)
-   **Word cloud:** Từ phổ biến trong descriptions

**Thư viện sử dụng:**

-   Matplotlib, Seaborn cho static plots
-   Plotly cho interactive visualization
-   WordCloud cho text visualization

---

### Giai Đoạn 4: Xây Dựng Hệ Thống Gợi Ý

**Mục tiêu:** Triển khai ≥ 2 phương pháp recommendation

#### [NEW] [content_based.py](file:///d:/Project/Git/Recommendation_system/src/models/content_based.py)

**Content-Based Filtering:**

-   Sử dụng TF-IDF vectors cho genres/descriptions
-   Cosine similarity để tìm items tương tự
-   Feature-based similarity

#### [NEW] [collaborative_filtering.py](file:///d:/Project/Git/Recommendation_system/src/models/collaborative_filtering.py)

**Collaborative Filtering:**

-   User-based CF: tìm users tương tự
-   Item-based CF: tìm items tương tự
-   Matrix Factorization (SVD, NMF)
-   Surprise library cho implementation

#### [NEW] [hybrid.py](file:///d:/Project/Git/Recommendation_system/src/models/hybrid.py)

**Hybrid Approach (Nâng cao):**

-   Kết hợp content-based + collaborative filtering
-   Weighted hybrid hoặc switching hybrid
-   Deep Learning (Neural Collaborative Filtering) - optional

#### [NEW] [04_model_building.ipynb](file:///d:/Project/Git/Recommendation_system/notebooks/04_model_building.ipynb)

-   Notebook xây dựng và so sánh các models
-   Train-test split
-   Parameter tuning
-   Lưu models vào `data/models/`

---

### Giai Đoạn 5: Đánh Giá Mô Hình

**Mục tiêu:** Đánh giá với các metrics chuẩn

#### [NEW] [metrics.py](file:///d:/Project/Git/Recommendation_system/src/evaluation/metrics.py)

-   **RMSE (Root Mean Squared Error)**
-   **MAE (Mean Absolute Error)**
-   **Precision@K:** độ chính xác top-K recommendations
-   **Recall@K:** độ phủ top-K recommendations
-   **F1-Score@K**
-   **NDCG (Normalized Discounted Cumulative Gain)** - optional

#### [NEW] [05_model_evaluation.ipynb](file:///d:/Project/Git/Recommendation_system/notebooks/05_model_evaluation.ipynb)

-   So sánh các models
-   Visualization kết quả đánh giá
-   Phân tích lỗi
-   Chọn model tốt nhất

---

### Giai Đoạn 6: Giao Diện Hiển Thị

**Khuyến nghị:** Sử dụng **Streamlit** (dễ và nhanh) hoặc **Flask** (linh hoạt hơn)

#### [NEW] [app.py](file:///d:/Project/Git/Recommendation_system/web_app/app.py)

**Features giao diện:**

-   **Trang chủ:** Giới thiệu hệ thống
-   **Search/Browse:** Tìm kiếm items
-   **Item Details:** Chi tiết item với recommendations
-   **User Preferences:** Người dùng chọn sở thích
-   **Recommendation Results:** Hiển thị top-N gợi ý với:
    -   Item poster/image
    -   Title, rating, genre
    -   Similarity score
    -   Mô tả ngắn

#### [NEW] [templates/](file:///d:/Project/Git/Recommendation_system/web_app/templates/)

**HTML Templates (nếu dùng Flask):**

-   `base.html`: Layout chung
-   `index.html`: Trang chủ
-   `item_detail.html`: Chi tiết item
-   `recommendations.html`: Kết quả gợi ý

#### [NEW] [static/](file:///d:/Project/Git/Recommendation_system/web_app/static/)

**CSS và JavaScript:**

-   Thiết kế responsive, modern UI
-   Interactive elements
-   Data visualization trên web

---

## Tính Năng Nâng Cao (Điểm Cộng)

### [OPTIONAL] Context-Aware Recommendation

-   Gợi ý dựa trên thời gian, thiết bị, location
-   Session-based recommendations

### [OPTIONAL] Real-time Recommendations

-   Update recommendations khi user tương tác
-   Online learning

### [OPTIONAL] User History & Personalization

-   Lưu lịch sử xem/đánh giá
-   Persistent user profiles
-   SQLite hoặc MongoDB cho database

### [OPTIONAL] Advanced Embeddings

-   BERT embeddings cho text
-   Graph embeddings
-   Multi-modal embeddings

### [OPTIONAL] Cloud Deployment

-   Deploy lên Heroku, Railway, hoặc Render
-   Containerize với Docker
-   CI/CD pipeline

---

## Deliverables (Nộp Bài)

### [NEW] Mã Nguồn

-   Code đầy đủ theo cấu trúc trên
-   Comments rõ ràng
-   Requirements.txt đầy đủ

### [NEW] [report.pdf](file:///d:/Project/Git/Recommendation_system/reports/report.pdf)

**Báo cáo 8-12 trang:**

1. **Giới thiệu** (1 trang)
    - Bài toán, mục tiêu
    - Lĩnh vực đã chọn
2. **Thu thập dữ liệu** (1 trang)
    - Nguồn dữ liệu
    - Mô tả dataset
3. **Xử lý dữ liệu** (2 trang)
    - Các bước làm sạch
    - Feature engineering
4. **Phân tích & Trực quan hóa** (2 trang)
    - Các insights từ EDA
    - Charts/graphs quan trọng
5. **Mô hình Recommendation** (3 trang)
    - Các approaches đã thử
    - Architecture/algorithms
    - Kết quả đánh giá
6. **Giao diện & Demo** (1 trang)
    - Screenshots giao diện
    - Hướng dẫn sử dụng
7. **Kết luận** (1 trang)
    - Thành tựu
    - Hạn chế
    - Hướng phát triển

### [OPTIONAL] [demo_video.mp4](file:///d:/Project/Git/Recommendation_system/videos/demo_video.mp4)

**Video demo 3-5 phút:**

-   Giới thiệu hệ thống
-   Demo các features chính
-   Chạy thử recommendations
-   Screen recording với narration

### [NEW] [README.md](file:///d:/Project/Git/Recommendation_system/README.md)

-   Project overview
-   Setup instructions
-   Usage guide
-   Team members
-   References

---

## Kế Hoạch Thực Hiện (Timeline)

### Phase 1: Setup & Data Collection (Tuần 1)

-   [ ] Setup môi trường, cấu trúc project
-   [ ] Thu thập dataset
-   [ ] Preliminary data exploration

### Phase 2: Data Processing (Tuần 2)

-   [ ] Làm sạch dữ liệu
-   [ ] Feature engineering
-   [ ] Vectorization

### Phase 3: EDA & Visualization (Tuần 3)

-   [ ] Phân tích dữ liệu
-   [ ] Tạo visualizations
-   [ ] Document insights

### Phase 4: Model Development (Tuần 4-5)

-   [ ] Implement content-based
-   [ ] Implement collaborative filtering
-   [ ] Implement hybrid (optional)
-   [ ] Model evaluation

### Phase 5: Web Interface (Tuần 6)

-   [ ] Design UI/UX
-   [ ] Implement web app
-   [ ] Integration với models
-   [ ] Testing

### Phase 6: Documentation & Finalization (Tuần 7)

-   [ ] Viết báo cáo
-   [ ] Tạo video demo (optional)
-   [ ] Code cleanup
-   [ ] Testing tổng thể
-   [ ] Package submission

---

## Tech Stack Đề Xuất

### Core Libraries

```python
# Data Processing
pandas
numpy
scikit-learn

# Visualization
matplotlib
seaborn
plotly
wordcloud

# Recommendation
surprise  # Collaborative Filtering
scikit-learn  # Content-Based

# Web Framework
streamlit  # Hoặc flask
```

### Optional Advanced

```python
# Deep Learning
tensorflow/pytorch
keras

# NLP
transformers
sentence-transformers

# Database
sqlalchemy
pymongo
```

---

## Verification Plan

### Automated Tests

```bash
# Run unit tests
pytest tests/

# Check code quality
pylint src/
flake8 src/

# Run notebooks
jupyter nbconvert --execute notebooks/*.ipynb
```

### Manual Verification

1. **Kiểm tra dataset:** Xác minh ≥2000 items, ≥5 features
2. **Test recommendations:** Chạy thử với các items khác nhau
3. **Evaluate metrics:** Kiểm tra RMSE, MAE, Precision@K, Recall@K
4. **UI testing:** Test tất cả features trên web interface
5. **Cross-browser testing:** Chrome, Firefox, Safari
6. **End-to-end flow:** Từ search → view details → get recommendations

### User Acceptance Testing

-   Test với người dùng thật
-   Thu thập feedback về chất lượng recommendations
-   Cải thiện dựa trên feedback

---

## Rủi Ro & Giải Pháp

> [!WARNING] > **Rủi ro 1:** Dataset không đủ lớn hoặc thiếu features
>
> -   **Giải pháp:** Kết hợp nhiều nguồn, feature engineering

> [!WARNING] > **Rủi ro 2:** Cold start problem (user/item mới)
>
> -   **Giải pháp:** Hybrid approach, popularity-based fallback

> [!WARNING] > **Rủi ro 3:** Performance issues với dataset lớn
>
> -   **Giải pháp:** Sampling, caching, pre-compute similarities

> [!CAUTION] > **Lưu ý:** Đảm bảo tuân thủ license của dataset và không vi phạm bản quyền khi thu thập dữ liệu.
