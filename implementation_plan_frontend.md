# 🎨 IMPLEMENTATION PLAN: FRONTEND

## Next.js + TypeScript

---

## 📋 Tổng quan

Frontend cung cấp giao diện người dùng hiện đại, responsive để tương tác với hệ thống recommendation.

---

## 🏗️ I. CẤU TRÚC THƯ MỤC

```
frontend/
├── src/
│   ├── app/                     # Next.js App Router
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx             # Trang chủ
│   │   ├── login/
│   │   │   └── page.tsx         # Trang đăng nhập
│   │   ├── anime/
│   │   │   ├── page.tsx         # Danh sách anime
│   │   │   └── [id]/
│   │   │       └── page.tsx     # Chi tiết anime
│   │   ├── search/
│   │   │   └── page.tsx         # Kết quả tìm kiếm
│   │   ├── history/
│   │   │   └── page.tsx         # Lịch sử xem
│   │   ├── profile/
│   │   │   └── page.tsx         # Trang cá nhân
│   │   └── admin/
│   │       ├── layout.tsx       # Admin layout
│   │       ├── page.tsx         # Dashboard
│   │       ├── models/
│   │       │   └── page.tsx     # Quản lý models
│   │       └── visualization/
│   │           └── page.tsx     # Trực quan hóa
│   ├── components/              # React components
│   │   ├── ui/                  # UI primitives
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── Loading.tsx
│   │   ├── layout/              # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Navbar.tsx
│   │   ├── anime/               # Anime components
│   │   │   ├── AnimeCard.tsx
│   │   │   ├── AnimeList.tsx
│   │   │   ├── AnimeDetail.tsx
│   │   │   └── RatingStars.tsx
│   │   ├── recommendation/      # Recommendation components
│   │   │   ├── RecommendationList.tsx
│   │   │   └── SimilarAnime.tsx
│   │   └── admin/               # Admin components
│   │       ├── StatsCard.tsx
│   │       ├── ChartContainer.tsx
│   │       └── ModelSelector.tsx
│   ├── hooks/                   # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useAnime.ts
│   │   ├── useRecommendation.ts
│   │   └── useDebounce.ts
│   ├── lib/                     # Utilities
│   │   ├── api.ts               # API client
│   │   ├── auth.ts              # Auth helpers
│   │   └── utils.ts             # Utility functions
│   ├── types/                   # TypeScript types
│   │   ├── anime.ts
│   │   ├── user.ts
│   │   └── api.ts
│   ├── context/                 # React Context
│   │   └── AuthContext.tsx
│   └── styles/                  # Global styles
│       └── globals.css
├── public/                      # Static files
│   ├── images/
│   └── icons/
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.ts
└── .env.local
```

---

## 📱 II. CÁC TRANG (PAGES)

### 🏠 Trang chủ (`/`)

| Section       | Mô tả                                         |
| ------------- | --------------------------------------------- |
| Hero Banner   | Welcome message, nút CTA                      |
| Gợi ý cho bạn | Danh sách anime được gợi ý (nếu đã đăng nhập) |
| Top Anime     | Top anime có điểm cao nhất                    |
| Anime mới xem | Lịch sử xem gần đây                           |

### 🔐 Đăng nhập (`/login`)

| Element | Mô tả                          |
| ------- | ------------------------------ |
| Input   | Nhập User ID                   |
| Button  | Đăng nhập                      |
| Info    | Hướng dẫn (không cần mật khẩu) |

### 🎬 Danh sách Anime (`/anime`)

| Feature    | Mô tả                     |
| ---------- | ------------------------- |
| Grid       | Danh sách anime dạng grid |
| Filter     | Lọc theo Genres           |
| Sort       | Sắp xếp theo Score, Name  |
| Pagination | Phân trang                |

### 📖 Chi tiết Anime (`/anime/[id]`)

| Section  | Mô tả                  |
| -------- | ---------------------- |
| Info     | Tên, Score, Genres     |
| Synopsis | Tóm tắt nội dung       |
| Rating   | Cho phép đánh giá (⭐) |
| Similar  | Anime tương tự         |
| Actions  | Thêm vào lịch sử xem   |

### 🔍 Tìm kiếm (`/search?q=...`)

| Feature     | Mô tả                       |
| ----------- | --------------------------- |
| Search bar  | Input tìm kiếm với debounce |
| Results     | Danh sách kết quả           |
| Empty state | Thông báo không tìm thấy    |

### 📜 Lịch sử (`/history`)

| Tab           | Mô tả                    |
| ------------- | ------------------------ |
| Của tôi       | Lịch sử xem của bản thân |
| Xem user khác | Nhập user_id để xem      |

### 👤 Profile (`/profile`)

| Section    | Mô tả                       |
| ---------- | --------------------------- |
| User info  | Thông tin user              |
| My ratings | Danh sách anime đã đánh giá |
| Statistics | Thống kê cá nhân            |

---

## 👑 III. ADMIN PAGES

### 📊 Dashboard (`/admin`)

```
┌─────────────────────────────────────────────────────────┐
│  📊 ADMIN DASHBOARD                                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ Users    │ │ Animes   │ │ Ratings  │ │ Active   │   │
│  │ 50,000   │ │ 17,000   │ │ 3M       │ │ Model    │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│                                                         │
│  ┌─────────────────────┐ ┌─────────────────────────┐   │
│  │ Rating Distribution │ │ Top Genres              │   │
│  │ [Histogram Chart]   │ │ [Bar Chart]             │   │
│  └─────────────────────┘ └─────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 🤖 Quản lý Models (`/admin/models`)

| Feature      | Mô tả                            |
| ------------ | -------------------------------- |
| Model list   | Danh sách các models             |
| Active model | Hiển thị model đang active       |
| Metrics      | RMSE, MAE, Precision@K, Recall@K |
| Actions      | Chọn model, Train lại            |
| Comparison   | So sánh các models               |

### 📈 Visualization (`/admin/visualization`)

| Chart               | Dữ liệu                             |
| ------------------- | ----------------------------------- |
| Rating Distribution | Phân bố rating (1-10)               |
| Genres Frequency    | Tần suất các thể loại               |
| Top Animes          | Top 10 anime được xem nhiều         |
| User Activity       | Hoạt động người dùng theo thời gian |
| Heatmap             | Correlation matrix                  |

---

## 🧩 IV. COMPONENTS CHI TIẾT

### AnimeCard

```tsx
interface AnimeCardProps {
    id: number;
    name: string;
    score: number;
    genres: string[];
    imageUrl?: string;
}

// Features:
// - Ảnh thumbnail
// - Tên anime (truncate nếu dài)
// - Score badge
// - Genres tags
// - Hover effect
// - Click để xem chi tiết
```

### RatingStars (Thang điểm 1-10 ⭐)

```tsx
interface RatingStarsProps {
    value: number; // 1-10 (theo dataset gốc)
    onChange?: (val: number) => void;
    readonly?: boolean;
    size?: "sm" | "md" | "lg";
}

// Features:
// - 10 sao tương ứng với thang điểm 1-10
// - Hover preview (highlight các sao khi hover)
// - Click để chọn điểm
// - Hiển thị số điểm bên cạnh (VD: 8/10)
// - Half-star support cho readonly mode
// - Animation khi hover/click
```

> ⚠️ **Validation**: Rating phải là số nguyên từ **1 đến 10**

### RecommendationList

```tsx
interface RecommendationListProps {
    title: string;
    animes: Anime[];
    loading?: boolean;
}

// Features:
// - Horizontal scroll
// - Loading skeleton
// - Empty state
// - "Xem thêm" button
```

---

## 🎨 V. DESIGN SYSTEM

### Colors

```css
:root {
    /* Primary */
    --primary: #6366f1; /* Indigo */
    --primary-light: #818cf8;
    --primary-dark: #4f46e5;

    /* Background */
    --bg-primary: #0f172a; /* Dark blue */
    --bg-secondary: #1e293b;
    --bg-card: #334155;

    /* Text */
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;

    /* Accent */
    --accent-success: #22c55e;
    --accent-warning: #f59e0b;
    --accent-error: #ef4444;
    --accent-star: #fbbf24; /* Rating stars */
}
```

### Typography

| Element | Font  | Size | Weight |
| ------- | ----- | ---- | ------ |
| H1      | Inter | 36px | 700    |
| H2      | Inter | 28px | 600    |
| H3      | Inter | 22px | 600    |
| Body    | Inter | 16px | 400    |
| Small   | Inter | 14px | 400    |

### Spacing

```css
/* Sử dụng Tailwind spacing scale */
--spacing-xs: 4px; /* 1 */
--spacing-sm: 8px; /* 2 */
--spacing-md: 16px; /* 4 */
--spacing-lg: 24px; /* 6 */
--spacing-xl: 32px; /* 8 */
```

---

## 🔗 VI. API INTEGRATION

### API Client

```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL;

export const api = {
  // Auth
  login: (userId: number) => fetch(`${API_BASE}/auth/login`, {...}),
  logout: () => fetch(`${API_BASE}/auth/logout`, {...}),

  // Anime
  getAnimes: (params) => fetch(`${API_BASE}/anime?${params}`),
  getAnime: (id: number) => fetch(`${API_BASE}/anime/${id}`),
  searchAnime: (q: string) => fetch(`${API_BASE}/anime/search?q=${q}`),

  // Recommendation
  getRecommendations: () => fetch(`${API_BASE}/recommendation`),
  getSimilar: (id: number) => fetch(`${API_BASE}/recommendation/similar/${id}`),

  // Rating
  addRating: (animeId, rating) => fetch(`${API_BASE}/rating`, {...}),

  // History
  getHistory: () => fetch(`${API_BASE}/history`),
  getUserHistory: (userId) => fetch(`${API_BASE}/history/user/${userId}`),
};
```

### Custom Hooks

```typescript
// hooks/useAnime.ts
export function useAnime(id: number) {
    const [anime, setAnime] = useState<Anime | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        api.getAnime(id)
            .then((res) => res.json())
            .then((data) => setAnime(data))
            .catch((err) => setError(err))
            .finally(() => setLoading(false));
    }, [id]);

    return { anime, loading, error };
}
```

---

## 📦 VII. DEPENDENCIES

```json
{
    "dependencies": {
        "next": "14.0.0",
        "react": "18.2.0",
        "react-dom": "18.2.0",
        "typescript": "5.2.0",

        // Styling
        "tailwindcss": "3.4.0",
        "@tailwindcss/typography": "0.5.0",

        // Charts
        "recharts": "2.10.0",
        "chart.js": "4.4.0",
        "react-chartjs-2": "5.2.0",

        // Icons
        "lucide-react": "0.300.0",

        // Utils
        "axios": "1.6.0",
        "clsx": "2.0.0",
        "date-fns": "3.0.0"
    }
}
```

---

## ✅ VIII. CHECKLIST TRIỂN KHAI

### Phase 1: Setup & Foundation

-   [ ] Khởi tạo Next.js project
-   [ ] Cấu hình Tailwind CSS
-   [ ] Setup TypeScript types
-   [ ] Tạo API client
-   [ ] Implement AuthContext

### Phase 2: Core Pages

-   [ ] Trang chủ
-   [ ] Trang đăng nhập
-   [ ] Danh sách anime
-   [ ] Chi tiết anime
-   [ ] Trang tìm kiếm
-   [ ] Trang lịch sử
-   [ ] Trang profile

### Phase 3: Components

-   [ ] UI components (Button, Card, Input, Modal)
-   [ ] Layout components (Header, Footer, Navbar)
-   [ ] AnimeCard, AnimeList
-   [ ] RatingStars
-   [ ] RecommendationList

### Phase 4: Admin Pages

-   [ ] Admin layout
-   [ ] Dashboard với stats
-   [ ] Model management
-   [ ] Visualization charts

### Phase 5: Polish

-   [ ] Loading states
-   [ ] Error handling
-   [ ] Empty states
-   [ ] Responsive design
-   [ ] Animations & transitions

---

## 🚀 IX. CHẠY ỨNG DỤNG

```bash
# 1. Cài đặt dependencies
npm install

# 2. Cấu hình environment
cp .env.example .env.local
# Chỉnh sửa NEXT_PUBLIC_API_URL trong .env.local

# 3. Chạy development server
npm run dev
# App chạy tại http://localhost:3000

# 4. Build production
npm run build
npm start
```
