/**
 * API Client for Backend Connection
 * Backend: http://localhost:5000
 */

import type { Anime } from "@/types/anime";
import type { RecommendationResponse } from "@/types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api";

interface FetchOptions extends RequestInit {
    token?: string;
}

async function fetchApi<T>(endpoint: string, options?: FetchOptions): Promise<T> {
    const url = `${API_BASE}${endpoint}`;

    const headers: Record<string, string> = {
        "Content-Type": "application/json",
        ...(options?.headers as Record<string, string>),
    };

    // Add JWT token if provided
    if (options?.token) {
        headers["Authorization"] = `Bearer ${options.token}`;
    }

    const response = await fetch(url, {
        ...options,
        headers,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ message: "An error occurred" }));
        throw new Error(error.error || error.message || `HTTP error! status: ${response.status}`);
    }

    return response.json();
}

export const api = {
    // ============ Auth ============
    login: async (userId: number) => {
        const response = await fetchApi<{ message: string; token: string; user: { user_id: number } }>("/auth/login", {
            method: "POST",
            body: JSON.stringify({ user_id: userId }),
        });
        return response;
    },

    logout: (token: string) =>
        fetchApi<{ message: string }>("/auth/logout", {
            method: "POST",
            token,
        }),

    getCurrentUser: (token: string) => fetchApi<{ user: { user_id: number; rating_count: number; history_count: number } }>("/auth/me", { token }),

    // ============ Anime ============
    getAnimes: async (params?: { page?: number; limit?: number; genre?: string; sort?: string; order?: string }) => {
        const searchParams = new URLSearchParams();
        if (params?.page) searchParams.set("page", params.page.toString());
        if (params?.limit) searchParams.set("limit", params.limit.toString());
        if (params?.genre) searchParams.set("genre", params.genre);
        if (params?.sort) searchParams.set("sort", params.sort);
        if (params?.order) searchParams.set("order", params.order);

        const response = await fetchApi<{
            animes: Anime[];
            total: number;
            page: number;
            limit: number;
            pages: number;
        }>(`/anime?${searchParams.toString()}`);

        return response;
    },

    getAnime: async (id: number) => {
        const response = await fetchApi<{
            anime: Anime & { user_avg_rating?: number; user_rating_count?: number };
        }>(`/anime/${id}`);
        return response;
    },

    searchAnime: async (query: string, limit = 20) => {
        const response = await fetchApi<{
            animes: Anime[];
            count: number;
            query: string;
        }>(`/anime/search?q=${encodeURIComponent(query)}&limit=${limit}`);
        return response;
    },

    getTopAnimes: async (limit = 10) => {
        const response = await fetchApi<{ animes: Anime[] }>(`/anime/top?limit=${limit}`);
        return response;
    },

    getGenres: async () => {
        const response = await fetchApi<{ genres: string[] }>("/anime/genres");
        return response;
    },

    // ============ Recommendations ============
    getRecommendations: async (token: string, limit = 10, model?: string) => {
        const params = new URLSearchParams({ limit: limit.toString() });
        if (model) params.set("model", model);

        const response = await fetchApi<{
            recommendations: RecommendationResponse[];
            model_used: string;
            count: number;
        }>(`/recommendation?${params.toString()}`, { token });

        return response;
    },

    getSimilarAnimes: async (animeId: number, limit = 10, useContent = false) => {
        const params = new URLSearchParams({
            limit: limit.toString(),
            use_content: useContent.toString(),
        });

        const response = await fetchApi<{
            anime_id: number;
            anime_name: string;
            similar_animes: Array<{
                anime_id: number;
                name: string;
                genres: string;
                score: number;
                similarity: number;
            }>;
            count: number;
            method: string;
        }>(`/recommendation/similar/${animeId}?${params.toString()}`);

        return response;
    },

    // ============ Rating ============
    getMyRatingForAnime: (token: string, animeId: number) =>
        fetchApi<{
            rating: {
                user_id: number;
                anime_id: number;
                rating: number;
                created_at?: string;
                updated_at?: string;
            } | null;
        }>(`/rating/${animeId}`, { token }),

    addRating: (token: string, animeId: number, rating: number) =>
        fetchApi<{ message: string; rating: { user_id: number; anime_id: number; rating: number } }>("/rating", {
            method: "POST",
            token,
            body: JSON.stringify({ anime_id: animeId, rating }),
        }),

    updateRating: (token: string, animeId: number, rating: number) =>
        fetchApi<{ message: string }>(`/rating/${animeId}`, {
            method: "PUT",
            token,
            body: JSON.stringify({ rating }),
        }),

    deleteRating: (token: string, animeId: number) =>
        fetchApi<{ message: string }>(`/rating/${animeId}`, {
            method: "DELETE",
            token,
        }),

    getUserRatings: (userId: number, page = 1, limit = 20) =>
        fetchApi<{
            ratings: Array<{
                anime_id: number;
                rating: number;
                created_at: string;
                updated_at: string;
                anime_name?: string;
                anime_genres?: string;
            }>;
            total: number;
            page: number;
            limit: number;
        }>(`/rating/user/${userId}?page=${page}&limit=${limit}`),

    // ============ History ============
    getMyHistory: (token: string, page = 1, limit = 20) =>
        fetchApi<{
            history: Array<{
                anime_id: number;
                watched_at: string;
                anime_name?: string;
                anime_genres?: string;
                anime_score?: number;
            }>;
            total: number;
            page: number;
            limit: number;
            user_id: number;
        }>(`/history?page=${page}&limit=${limit}`, { token }),

    getUserHistory: (userId: number, page = 1, limit = 20) =>
        fetchApi<{
            history: Array<{
                anime_id: number;
                watched_at: string;
                anime_name?: string;
                anime_genres?: string;
                anime_score?: number;
            }>;
            total: number;
            page: number;
            limit: number;
            user_id: number;
        }>(`/history/user/${userId}?page=${page}&limit=${limit}`),

    addToHistory: (token: string, animeId: number) =>
        fetchApi<{
            message: string;
            history: { user_id: number; anime_id: number; anime_name: string };
        }>("/history", {
            method: "POST",
            token,
            body: JSON.stringify({ anime_id: animeId }),
        }),

    // ============ Admin ============
    getSystemStats: async () => {
        const response = await fetchApi<{
            stats: {
                total_users: number;
                total_animes: number;
                total_ratings: number;
                total_history: number;
                rating_distribution: Record<string, number>;
                top_genres: Array<{ genre: string; count: number }>;
            };
        }>("/admin/stats");
        return response;
    },

    getVisualizationData: async () => {
        const response = await fetchApi<{
            data: {
                rating_distribution: Array<{ _id: number; count: number }>;
                top_rated_animes: Array<{
                    anime_id: number;
                    anime_name: string;
                    rating_count: number;
                    avg_rating: number;
                }>;
                genre_frequency: Array<{ _id: string; count: number }>;
                score_distribution: Array<{ _id: number; count: number }>;
            };
        }>("/admin/visualization");
        return response;
    },

    getModels: async () => {
        const response = await fetchApi<{
            models: Array<{
                name: string;
                display_name?: string;
                is_active: boolean;
                status?: string;
                metrics?: {
                    rmse?: number;
                    mae?: number;
                    precision_at_k?: number;
                    recall_at_k?: number;
                };
                trained_at?: string;
            }>;
        }>("/admin/models");
        return response;
    },

    selectModel: async (modelName: string) => {
        const response = await fetchApi<{ message: string }>("/admin/models/select", {
            method: "POST",
            body: JSON.stringify({ model_name: modelName }),
        });
        return response;
    },

    trainModel: async (modelName: string) => {
        const response = await fetchApi<{ message: string; job_id: string; status: string }>("/admin/models/train", {
            method: "POST",
            body: JSON.stringify({ model_name: modelName }),
        });
        return response;
    },

    compareModels: async () => {
        const response = await fetchApi<{
            comparison: Array<{
                name: string;
                metrics: Record<string, number>;
                trained_at?: string;
                is_active: boolean;
            }>;
        }>("/admin/models/compare");
        return response;
    },
};
