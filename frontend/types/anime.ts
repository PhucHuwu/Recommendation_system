export interface Anime {
  anime_id: number
  name: string
  genre: string[]
  type: string
  episodes: number
  rating: number
  members: number
}

export interface AnimeDetail extends Anime {
  synopsis?: string
  aired?: string
  score?: number
  scored_by?: number
  rank?: number
  popularity?: number
  favorites?: number
}

export interface AnimeCardProps {
  id: number
  name: string
  score: number
  genres: string[]
  episodes?: number
  type?: string
}

export interface AnimeListParams {
  page?: number
  limit?: number
  genre?: string
  sort_by?: "name" | "rating" | "members"
  sort_order?: "asc" | "desc"
  search?: string
}

export interface AnimeResponse {
  data: Anime[]
  total: number
  page: number
  limit: number
  total_pages: number
}
