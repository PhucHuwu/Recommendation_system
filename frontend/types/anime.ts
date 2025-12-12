export interface Anime {
    anime_id: number;
    name: string;
    genre?: string | string[]; // Support both formats
    genres?: string; // Backend format (comma-separated)
    type: string;
    episodes: number;
    rating?: number;
    score?: number; // Backend uses 'score' instead of 'rating'
    members?: number;
    mal_id?: number; // Backend uses mal_id
}

export interface AnimeDetail extends Anime {
    synopsis?: string;
    aired?: string;
    scored_by?: number;
    rank?: number;
    popularity?: number;
    favorites?: number;
    user_avg_rating?: number;
}

export interface AnimeCardProps {
    id: number;
    name: string;
    score: number;
    genres: string | string[]; // Support both formats
    episodes?: number;
    type?: string;
    isRecommendation?: boolean;
}

export interface AnimeListParams {
    page?: number;
    limit?: number;
    genre?: string;
    sort_by?: "name" | "rating" | "members";
    sort_order?: "asc" | "desc";
    search?: string;
}

export interface AnimeResponse {
    data: Anime[];
    total: number;
    page: number;
    limit: number;
    total_pages: number;
}
