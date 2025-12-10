# Frontend - Anime Recommendation System

Modern, responsive frontend application built with Next.js 16 and React 19, providing an intuitive interface for anime discovery and personalized recommendations.

## Table of Contents

-   [Overview](#overview)
-   [Technology Stack](#technology-stack)
-   [Project Structure](#project-structure)
-   [Getting Started](#getting-started)
-   [Features](#features)
-   [Components](#components)
-   [API Integration](#api-integration)
-   [State Management](#state-management)
-   [Styling](#styling)
-   [Development](#development)
-   [Build and Deployment](#build-and-deployment)

## Overview

The frontend application provides a seamless user experience for browsing anime, receiving personalized recommendations, and managing user profiles. Built with modern React patterns and Next.js App Router, it offers server-side rendering, optimized performance, and a fully responsive design.

### Key Features

-   Server-side rendering (SSR) with Next.js App Router
-   Responsive design with Tailwind CSS
-   Type-safe development with TypeScript
-   Component library based on Radix UI and shadcn/ui
-   JWT-based authentication
-   Real-time search and filtering
-   Interactive data visualizations
-   Dark/light theme support

## Technology Stack

### Core Framework

-   **Next.js**: 16.0.7 (App Router)
-   **React**: 19.2.0
-   **TypeScript**: 5.x
-   **Node.js**: 18+

### UI and Styling

-   **Tailwind CSS**: 4.1.9 - Utility-first CSS framework
-   **Radix UI**: Accessible component primitives
-   **shadcn/ui**: Pre-built component library
-   **Lucide React**: Icon library
-   **next-themes**: Theme management

### Form Handling

-   **React Hook Form**: 7.60.0 - Performant form validation
-   **Zod**: 3.25.76 - Schema validation
-   **@hookform/resolvers**: Form validation integration

### Data Visualization

-   **Recharts**: Latest - Chart library for admin dashboard

### Additional Libraries

-   **date-fns**: 4.1.0 - Date manipulation
-   **cmdk**: 1.0.4 - Command menu
-   **Sonner**: 1.7.4 - Toast notifications
-   **Embla Carousel**: 8.5.1 - Carousel component

## Project Structure

```
frontend/
├── app/                             # Next.js App Router
│   ├── layout.tsx                   # Root layout
│   ├── page.tsx                     # Home page
│   ├── globals.css                  # Global styles
│   ├── admin/                       # Admin dashboard
│   │   ├── page.tsx                 # Admin overview
│   │   ├── models/                  # Model training page
│   │   └── visualization/           # Analytics page
│   ├── anime/                       # Anime pages
│   │   ├── page.tsx                 # Anime list
│   │   └── [id]/                    # Anime detail page
│   ├── history/                     # Rating history
│   ├── login/                       # Login page
│   ├── profile/                     # User profile
│   └── search/                      # Search page
├── components/                      # React components
│   ├── ui/                          # Base UI components (shadcn/ui)
│   ├── layout/                      # Layout components
│   │   ├── header.tsx               # Navigation header
│   │   └── footer.tsx               # Footer
│   ├── anime/                       # Anime-related components
│   │   ├── anime-card.tsx           # Anime card display
│   │   ├── anime-list.tsx           # Anime list grid
│   │   └── rating-stars.tsx         # Star rating component
│   ├── recommendation/              # Recommendation components
│   │   └── recommendation-list.tsx
│   ├── admin/                       # Admin components
│   │   ├── stats-card.tsx           # Statistics card
│   │   └── chart-container.tsx
│   └── theme-provider.tsx           # Theme context provider
├── lib/                             # Utilities
│   ├── api.ts                       # API client
│   └── utils.ts                     # Helper functions
├── context/                         # React contexts
│   └── auth-context.tsx             # Authentication context
├── hooks/                           # Custom React hooks
│   ├── use-toast.ts                 # Toast notification hook
│   ├── use-mobile.ts                # Mobile detection hook
│   └── use-debounce.ts              # Debounce hook
├── types/                           # TypeScript definitions
│   ├── anime.ts                     # Anime types
│   ├── user.ts                      # User types
│   └── api.ts                       # API response types
├── public/                          # Static assets
├── package.json                     # Dependencies
├── tsconfig.json                    # TypeScript config
├── next.config.mjs                  # Next.js config
├── tailwind.config.js               # Tailwind config
└── components.json                  # shadcn/ui config
```

## Getting Started

### Prerequisites

-   Node.js 18 or higher
-   pnpm (recommended), npm, or yarn
-   Backend API running on http://localhost:5000

### Installation

1. **Install dependencies**

```bash
cd frontend
pnpm install
```

2. **Environment Configuration**

Create a `.env.local` file in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

3. **Run Development Server**

```bash
pnpm dev
```

The application will be available at http://localhost:3000

### Available Scripts

```bash
# Development server with hot reload
pnpm dev

# Production build
pnpm build

# Start production server
pnpm start

# Lint code
pnpm lint
```

## Features

### 1. User Authentication

-   JWT-based authentication
-   Persistent login with localStorage
-   Protected routes and pages
-   Automatic token refresh

**Implementation**: `context/auth-context.tsx`

### 2. Anime Browsing

-   Paginated anime catalog
-   Grid and list view options
-   Lazy loading with Next.js Image
-   Detailed anime information pages

**Pages**: `app/anime/page.tsx`, `app/anime/[id]/page.tsx`

### 3. Search Functionality

-   Real-time search with debouncing
-   Filter by genre, year, rating
-   Semantic search integration
-   Search history

**Page**: `app/search/page.tsx`

### 4. Personalized Recommendations

-   User-based recommendations
-   Item-based similar anime
-   Hybrid model results
-   Recommendation explanations

**Component**: `components/recommendation/recommendation-list.tsx`

### 5. Rating System

-   Interactive star rating (1-10 scale)
-   Quick rating from anime cards
-   Rating history management
-   Update and delete ratings

**Component**: `components/anime/rating-stars.tsx`

### 6. Admin Dashboard

-   Model training interface
-   Performance metrics visualization
-   System analytics
-   User statistics

**Pages**: `app/admin/`, `app/admin/models/`, `app/admin/visualization/`

### 7. Responsive Design

-   Mobile-first approach
-   Breakpoint-based layouts
-   Touch-friendly interfaces
-   Adaptive navigation

### 8. Theme Support

-   Dark and light modes
-   System preference detection
-   Persistent theme selection
-   Smooth transitions

**Provider**: `components/theme-provider.tsx`

## Components

### UI Components (shadcn/ui)

Located in `components/ui/`, these are pre-built, customizable components:

-   **Button**: Various button styles and sizes
-   **Card**: Content containers
-   **Dialog**: Modal dialogs
-   **Form**: Form components with validation
-   **Input**: Text input fields
-   **Select**: Dropdown selects
-   **Tabs**: Tabbed interfaces
-   **Toast**: Notification system
-   **And more**: accordion, alert, avatar, badge, calendar, etc.

### Custom Components

#### Anime Card (`components/anime/anime-card.tsx`)

Displays anime information with image, title, rating, and genres.

```typescript
interface AnimeCardProps {
    anime: Anime;
    showRating?: boolean;
    onRate?: (rating: number) => void;
}
```

#### Anime List (`components/anime/anime-list.tsx`)

Grid layout for displaying multiple anime cards with loading states.

```typescript
interface AnimeListProps {
    animeList: Anime[];
    loading?: boolean;
    onLoadMore?: () => void;
}
```

#### Rating Stars (`components/anime/rating-stars.tsx`)

Interactive star rating component supporting 1-10 scale.

```typescript
interface RatingStarsProps {
    rating: number;
    maxRating?: number;
    onRate?: (rating: number) => void;
    readonly?: boolean;
}
```

#### Header (`components/layout/header.tsx`)

Navigation bar with authentication state, search, and theme toggle.

#### Stats Card (`components/admin/stats-card.tsx`)

Dashboard statistics card for admin panel.

## API Integration

### API Client (`lib/api.ts`)

Centralized API client using fetch with TypeScript:

```typescript
class ApiClient {
    private baseURL: string;
    private token: string | null;

    // Authentication
    async login(username: string, password: string): Promise<LoginResponse>;
    async register(userData: RegisterData): Promise<User>;
    async getProfile(): Promise<User>;

    // Anime
    async getAnimeList(params?: AnimeListParams): Promise<AnimeListResponse>;
    async getAnimeById(id: string): Promise<Anime>;
    async searchAnime(query: string): Promise<Anime[]>;

    // Recommendations
    async getRecommendations(userId: string): Promise<Recommendation[]>;
    async getSimilarAnime(userId: string, animeId: string): Promise<Anime[]>;

    // Ratings
    async submitRating(animeId: string, rating: number): Promise<Rating>;
    async getUserRatings(userId: string): Promise<Rating[]>;
    async deleteRating(ratingId: string): Promise<void>;

    // Admin
    async trainModels(): Promise<TrainingResult>;
    async getMetrics(): Promise<ModelMetrics>;
}
```

### Request Interceptors

-   Automatic JWT token attachment
-   Request/response logging
-   Error handling
-   Token refresh logic

### Error Handling

```typescript
try {
    const anime = await api.getAnimeById(id);
} catch (error) {
    if (error.status === 401) {
        // Redirect to login
    } else if (error.status === 404) {
        // Show not found
    } else {
        // Show error toast
    }
}
```

## State Management

### Authentication Context

Global authentication state using React Context:

```typescript
interface AuthContextType {
    user: User | null;
    token: string | null;
    login: (username: string, password: string) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
    isLoading: boolean;
}
```

**Usage**:

```typescript
import { useAuth } from "@/context/auth-context";

function MyComponent() {
    const { user, isAuthenticated, logout } = useAuth();

    if (!isAuthenticated) {
        return <LoginPrompt />;
    }

    return <div>Welcome {user.username}</div>;
}
```

### Local State

Component-level state using React hooks:

-   `useState` for simple state
-   `useReducer` for complex state logic
-   `useEffect` for side effects
-   Custom hooks for reusable logic

## Styling

### Tailwind CSS

Utility-first CSS framework with custom configuration:

```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {...},
        secondary: {...},
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
}
```

### CSS Variables

Global CSS variables in `app/globals.css`:

```css
:root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    /* ... */
}

.dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    /* ... */
}
```

### Component Styling

Using `cn()` utility for conditional classes:

```typescript
import { cn } from "@/lib/utils";

<div className={cn("base-class", isActive && "active-class", "hover:bg-primary")} />;
```

## Development

### Code Organization

-   **Pages**: One component per page in `app/`
-   **Components**: Reusable components in `components/`
-   **Utilities**: Helper functions in `lib/`
-   **Types**: Centralized type definitions in `types/`

### TypeScript Best Practices

-   Define interfaces for all props
-   Use strict mode
-   Avoid `any` type
-   Export types with components

```typescript
// Good
export interface AnimeCardProps {
    anime: Anime;
    onRate?: (rating: number) => void;
}

export function AnimeCard({ anime, onRate }: AnimeCardProps) {
    // ...
}
```

### Adding New Components

1. Create component file in appropriate directory
2. Define TypeScript interface for props
3. Implement component logic
4. Add to index file if needed
5. Document usage

### Custom Hooks

Example: Debounce hook

```typescript
// hooks/use-debounce.ts
export function useDebounce<T>(value: T, delay: number): T {
    const [debouncedValue, setDebouncedValue] = useState<T>(value);

    useEffect(() => {
        const handler = setTimeout(() => {
            setDebouncedValue(value);
        }, delay);

        return () => clearTimeout(handler);
    }, [value, delay]);

    return debouncedValue;
}
```

### Performance Optimization

-   Use `React.memo` for expensive components
-   Implement virtualization for long lists
-   Lazy load images with Next.js Image
-   Code splitting with dynamic imports

```typescript
import dynamic from "next/dynamic";

const AdminDashboard = dynamic(() => import("@/components/admin/dashboard"), {
    loading: () => <Loading />,
    ssr: false,
});
```

## Build and Deployment

### Production Build

```bash
pnpm build
```

This creates an optimized production build in `.next/` directory.

### Environment Variables

**Development** (`.env.local`):

```env
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

**Production** (`.env.production`):

```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api
```

### Deployment Options

#### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

#### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

#### Static Export

For static hosting:

```javascript
// next.config.mjs
export default {
    output: "export",
};
```

```bash
pnpm build
# Output in 'out/' directory
```

### Performance Checklist

-   [ ] Enable Next.js image optimization
-   [ ] Implement route prefetching
-   [ ] Minimize bundle size
-   [ ] Enable compression
-   [ ] Configure CDN for static assets
-   [ ] Implement caching strategies
-   [ ] Monitor Core Web Vitals

### Testing

```bash
# Unit tests
pnpm test

# E2E tests
pnpm test:e2e

# Type checking
pnpm type-check
```

## Troubleshooting

### Common Issues

**Build Errors**:

-   Clear `.next/` directory: `rm -rf .next`
-   Delete `node_modules/` and reinstall
-   Check Node.js version compatibility

**API Connection Issues**:

-   Verify `NEXT_PUBLIC_API_URL` is set correctly
-   Check CORS configuration in backend
-   Ensure backend server is running

**Styling Issues**:

-   Rebuild Tailwind: `pnpm build:css`
-   Clear browser cache
-   Check dark mode class on html element

## Contributing

1. Follow the existing code structure
2. Use TypeScript for all new code
3. Write meaningful commit messages
4. Test components before submitting
5. Update documentation as needed

## Resources

-   [Next.js Documentation](https://nextjs.org/docs)
-   [React Documentation](https://react.dev)
-   [Tailwind CSS](https://tailwindcss.com)
-   [shadcn/ui](https://ui.shadcn.com)
-   [Radix UI](https://www.radix-ui.com)

---

For backend documentation, see [../backend/README_BE.md](../backend/README_BE.md)
