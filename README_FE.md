# Anime Recommendation System - Frontend

## Overview

WibiFlix is a modern web application built with Next.js 16, providing an intuitive interface for discovering and receiving personalized anime recommendations. The application features a responsive design with dark mode support, real-time search, and comprehensive admin dashboard for system management.

## Table of Contents

-   [Technology Stack](#technology-stack)
-   [Features](#features)
-   [Project Structure](#project-structure)
-   [Pages and Routes](#pages-and-routes)
-   [Components](#components)
-   [State Management](#state-management)
-   [API Integration](#api-integration)
-   [Installation](#installation)
-   [Configuration](#configuration)
-   [Running the Application](#running-the-application)
-   [Building for Production](#building-for-production)
-   [Styling](#styling)

## Technology Stack

| Category        | Technology       | Version |
| --------------- | ---------------- | ------- |
| Framework       | Next.js          | 16.0.7  |
| Language        | TypeScript       | 5.x     |
| UI Library      | React            | 19.2.0  |
| Styling         | Tailwind CSS     | 4.1.9   |
| UI Components   | Radix UI         | Various |
| Charts          | Recharts         | Latest  |
| Form Handling   | React Hook Form  | 7.60.0  |
| Validation      | Zod              | 3.25.76 |
| Icons           | Lucide React     | 0.454.0 |
| Theme           | next-themes      | 0.4.6   |
| Analytics       | Vercel Analytics | Latest  |
| Package Manager | pnpm             | -       |

## Features

### User Features

-   **Personalized Recommendations**: AI-powered anime suggestions based on user preferences
-   **Anime Discovery**: Browse, search, and filter anime catalog
-   **Rating System**: Rate animes on a 1-10 scale
-   **Watch History**: Track viewed animes
-   **User Profile**: View personal statistics and rating history
-   **Real-time Search**: Debounced search with instant results
-   **Responsive Design**: Optimized for desktop, tablet, and mobile

### Admin Features

-   **Dashboard**: System overview with key metrics
-   **Model Management**: View, compare, and activate ML models
-   **Data Visualization**: Charts and graphs for analytics
-   **Statistics**: User engagement, rating distribution, genre analysis

## Project Structure

```
frontend/
├── app/                        # Next.js App Router
│   ├── layout.tsx             # Root layout with providers
│   ├── page.tsx               # Homepage
│   ├── globals.css            # Global styles
│   ├── admin/                 # Admin section
│   │   ├── layout.tsx         # Admin layout with navigation
│   │   ├── page.tsx           # Admin dashboard
│   │   ├── models/            # Model management
│   │   └── visualization/     # Data visualization
│   ├── anime/                 # Anime pages
│   │   ├── page.tsx           # Anime list
│   │   ├── loading.tsx        # Loading state
│   │   └── [id]/              # Anime detail (dynamic route)
│   ├── history/               # Watch history
│   ├── login/                 # Authentication
│   ├── profile/               # User profile
│   └── search/                # Search page
├── components/                 # Reusable components
│   ├── admin/                 # Admin-specific components
│   ├── anime/                 # Anime-related components
│   ├── layout/                # Layout components (header, footer)
│   ├── recommendation/        # Recommendation components
│   └── ui/                    # Base UI components (Radix-based)
├── context/                   # React Context providers
│   └── auth-context.tsx       # Authentication context
├── hooks/                     # Custom React hooks
│   ├── use-debounce.ts        # Debounce hook for search
│   ├── use-mobile.ts          # Mobile detection hook
│   └── use-toast.ts           # Toast notification hook
├── lib/                       # Utility functions
│   ├── api.ts                 # API client
│   └── utils.ts               # Helper functions
├── types/                     # TypeScript type definitions
│   ├── anime.ts               # Anime-related types
│   ├── api.ts                 # API response types
│   └── user.ts                # User types
├── public/                    # Static assets
├── styles/                    # Additional styles
├── next.config.mjs            # Next.js configuration
├── tailwind.config.js         # Tailwind configuration
├── tsconfig.json              # TypeScript configuration
└── package.json               # Dependencies
```

## Pages and Routes

| Route                  | Page             | Description                              | Auth Required |
| ---------------------- | ---------------- | ---------------------------------------- | ------------- |
| `/`                    | Homepage         | Hero section, recommendations, top anime | No            |
| `/login`               | Login            | User authentication                      | No            |
| `/anime`               | Anime List       | Browse, search, filter animes            | No            |
| `/anime/[id]`          | Anime Detail     | Detailed anime info, similar animes      | No            |
| `/search`              | Search           | Full-page search experience              | No            |
| `/history`             | Watch History    | User's watched animes                    | Yes           |
| `/profile`             | User Profile     | User stats, ratings, preferences         | Yes           |
| `/admin`               | Admin Dashboard  | System statistics overview               | Admin         |
| `/admin/models`        | Model Management | ML model control panel                   | Admin         |
| `/admin/visualization` | Visualization    | Data charts and analytics                | Admin         |

## Components

### Layout Components

-   **Header**: Navigation bar, search, user menu
-   **Footer**: Copyright, links

### UI Components (Radix-based)

| Component     | Description                          |
| ------------- | ------------------------------------ |
| Button        | Primary action buttons with variants |
| Card          | Content container with header/footer |
| Input         | Form input fields                    |
| Select        | Dropdown selection                   |
| Dialog        | Modal dialogs                        |
| Dropdown Menu | Context menus                        |
| Badge         | Status indicators                    |
| Table         | Data tables                          |
| Tabs          | Tab navigation                       |
| Toast         | Notifications                        |
| Tooltip       | Hover information                    |
| Avatar        | User avatars                         |
| Progress      | Progress indicators                  |
| Skeleton      | Loading placeholders                 |

### Feature Components

**Anime Components**

-   `AnimeCard`: Individual anime display card
-   `AnimeList`: Grid/list of anime cards
-   `RatingStars`: Interactive star rating component

**Recommendation Components**

-   `RecommendationList`: Horizontal scrollable recommendation carousel

**Admin Components**

-   `StatsCard`: Metric display card
-   `ChartContainer`: Chart wrapper component

## State Management

### Authentication Context

The application uses React Context for authentication state management.

```typescript
interface AuthContextType {
    user: User | null;
    token: string | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    login: (userId: number) => Promise<void>;
    logout: () => Promise<void>;
}
```

**Storage**: LocalStorage with keys `WibiFlix_user` and `WibiFlix_token`

### Data Fetching

-   Server-side and client-side data fetching with `fetch` API
-   Custom API client (`lib/api.ts`) for all backend communications
-   React hooks for component-level state

## API Integration

### API Client Configuration

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api";
```

### API Methods

**Authentication**

```typescript
api.login(userId: number)
api.logout(token: string)
api.getCurrentUser(token: string)
```

**Anime**

```typescript
api.getAnimes(params)
api.getAnime(id: number)
api.searchAnime(query: string, limit?: number)
api.getTopAnimes(limit?: number)
api.getGenres()
```

**Recommendations**

```typescript
api.getRecommendations(token: string, limit?: number, model?: string)
api.getSimilarAnimes(animeId: number, limit?: number)
```

**Ratings**

```typescript
api.getMyRatingForAnime(token: string, animeId: number)
api.addRating(token: string, animeId: number, rating: number)
api.updateRating(token: string, animeId: number, rating: number)
api.deleteRating(token: string, animeId: number)
api.getUserRatings(userId: number, page?: number, limit?: number)
```

**History**

```typescript
api.getMyHistory(token: string, page?: number, limit?: number)
api.addToHistory(token: string, animeId: number)
api.removeFromHistory(token: string, animeId: number)
```

**Admin**

```typescript
api.getSystemStats()
api.getVisualizationData()
api.getModels()
api.selectModel(modelName: string)
api.compareModels()
```

## Installation

### Prerequisites

-   Node.js 18.17+
-   pnpm (recommended) or npm

### Steps

1. Clone the repository:

```bash
git clone https://github.com/PhucHuwu/Recommendation_system.git
cd Recommendation_system/frontend
```

2. Install dependencies:

```bash
pnpm install
# or
npm install
```

## Configuration

### Environment Variables

Create a `.env.local` file in the frontend directory:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:5000/api

# Optional: Analytics
VERCEL_ANALYTICS_ID=your-analytics-id
```

### Next.js Configuration

The `next.config.mjs` file contains Next.js configuration including:

-   Image optimization settings
-   API rewrites (if needed)
-   Build optimizations

## Running the Application

### Development Mode

```bash
pnpm dev
# or
npm run dev
```

The application will be available at `http://localhost:3000`

### Available Scripts

| Script | Command      | Description              |
| ------ | ------------ | ------------------------ |
| dev    | `pnpm dev`   | Start development server |
| build  | `pnpm build` | Build for production     |
| start  | `pnpm start` | Start production server  |
| lint   | `pnpm lint`  | Run ESLint               |

## Building for Production

### Build

```bash
pnpm build
```

### Start Production Server

```bash
pnpm start
```

### Static Export

For static hosting, modify `next.config.mjs`:

```javascript
const nextConfig = {
    output: "export",
};
```

## Styling

### Tailwind CSS

The project uses Tailwind CSS 4.x with:

-   Custom color scheme (primary, secondary, muted, etc.)
-   Dark mode support via CSS variables
-   Responsive breakpoints (sm, md, lg, xl, 2xl)
-   Custom animations (`tailwindcss-animate`)

### Color Scheme

The application uses CSS variables for theming:

```css
:root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 262.1 83.3% 57.8%;
    --secondary: 210 40% 96.1%;
    --muted: 210 40% 96.1%;
    --accent: 210 40% 96.1%;
    --destructive: 0 84.2% 60.2%;
    /* ... */
}
```

### Component Styling

Components use the `cn()` utility for conditional class merging:

```typescript
import { cn } from "@/lib/utils";

<div className={cn("base-classes", condition && "conditional-classes", className)} />;
```

## Type Definitions

### Anime Type

```typescript
interface Anime {
    anime_id: number;
    name: string;
    genres?: string;
    score?: number;
    mal_id?: number;
    episodes?: number;
    type?: string;
    members?: number;
}
```

### User Type

```typescript
interface User {
    user_id: number;
    username: string;
}
```

### Recommendation Response

```typescript
interface RecommendationResponse {
    anime_id: number;
    name: string;
    genres: string;
    score: number;
    predicted_rating: number;
}
```

## Browser Support

-   Chrome (latest)
-   Firefox (latest)
-   Safari (latest)
-   Edge (latest)

## Performance Optimizations

-   Image optimization with Next.js Image component
-   Code splitting per route
-   Debounced search input
-   Loading states with skeletons
-   Lazy loading for non-critical components

## Accessibility

-   Semantic HTML elements
-   ARIA labels on interactive elements
-   Keyboard navigation support
-   Focus management
-   Color contrast compliance

## License

This project is part of an academic recommendation system implementation.
