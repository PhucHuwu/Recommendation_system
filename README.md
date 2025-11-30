# Movie Recommendation System

Hệ thống gợi ý phim sử dụng Content-Based Filtering và Collaborative Filtering.

## Mô Tả Dự Án

Dự án xây dựng một hệ thống recommendation hoàn chỉnh bao gồm:

-   Thu thập và xử lý dữ liệu phim
-   Phân tích và trực quan hóa dữ liệu
-   Xây dựng mô hình gợi ý (Content-Based, Collaborative Filtering, Hybrid)
-   Giao diện web để hiển thị kết quả

## Dataset

Sử dụng **MovieLens Dataset** với:

-   ≥ 2,000 phim
-   ≥ 5 features: title, genres, rating, year, director/cast, description

## Cấu Trúc Dự Án

```
Recommendation_system/
├── data/
│   ├── raw/                    # Dữ liệu gốc
│   ├── processed/              # Dữ liệu đã xử lý
│   └── models/                 # Mô hình đã train
├── notebooks/                  # Jupyter notebooks
├── src/                        # Source code
│   ├── data_processing/        # Thu thập & xử lý dữ liệu
│   ├── models/                 # Mô hình recommendation
│   ├── evaluation/             # Đánh giá mô hình
│   └── utils/                  # Utilities
├── web_app/                    # Web application
├── tests/                      # Unit tests
├── reports/                    # Báo cáo
└── videos/                     # Video demo
```

## Setup

### Yêu Cầu

-   Python 3.8+
-   Các thư viện trong `requirements.txt`

### Cài Đặt

```bash
# Clone repository
git clone <repo-url>
cd Recommendation_system

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt

# Download dataset
python src/data_processing/collector.py
```

## Sử Dụng

### 1. Data Collection & Processing

```bash
# Chạy notebook để explore dữ liệu
jupyter notebook notebooks/01_data_collection.ipynb
```

### 2. Model Training

```bash
# Chạy notebooks theo thứ tự
jupyter notebook notebooks/02_data_cleaning.ipynb
jupyter notebook notebooks/03_eda_visualization.ipynb
jupyter notebook notebooks/04_model_building.ipynb
jupyter notebook notebooks/05_model_evaluation.ipynb
```

### 3. Web Application

```bash
# Chạy Streamlit app
streamlit run web_app/app.py

# Hoặc Flask app
python web_app/app.py
```

## Tech Stack

### Core

-   **Data Processing:** pandas, numpy, scikit-learn
-   **Visualization:** matplotlib, seaborn, plotly
-   **Recommendation:** surprise (CF), scikit-learn (content-based)
-   **Web:** Streamlit hoặc Flask

### Optional

-   **Deep Learning:** TensorFlow/PyTorch
-   **NLP:** transformers, sentence-transformers
-   **Database:** SQLite, MongoDB

## Tính Năng

### Core Features

✅ Thu thập dữ liệu từ MovieLens  
✅ Làm sạch và preprocessing  
✅ EDA với visualizations  
✅ Content-Based Filtering  
✅ Collaborative Filtering  
✅ Hybrid Recommendation  
✅ Đánh giá mô hình (RMSE, MAE, Precision@K, Recall@K)  
✅ Web interface

### Advanced Features (Optional)

-   Context-aware recommendations
-   Real-time recommendations
-   User history & personalization
-   Advanced embeddings (BERT)
-   Cloud deployment

## Kết Quả Đánh Giá

| Model                   | RMSE | MAE | Precision@10 | Recall@10 |
| ----------------------- | ---- | --- | ------------ | --------- |
| Content-Based           | -    | -   | -            | -         |
| Collaborative Filtering | -    | -   | -            | -         |
| Hybrid                  | -    | -   | -            | -         |

_(Sẽ được cập nhật sau khi training)_

## Đóng Góp

[Thông tin team members]

## Tài Liệu Tham Khảo

-   [MovieLens Dataset](https://grouplens.org/datasets/movielens/)
-   [Surprise Documentation](https://surpriselib.com/)
-   [Scikit-learn](https://scikit-learn.org/)

## License

[License information]
