export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  total_pages: number
}

export interface RecommendationResponse {
  anime_id: number
  name: string
  predicted_rating: number
  genre: string[]
  image_url?: string
  similarity_score?: number
}

export interface ModelInfo {
  model_id: string
  model_name: string
  model_type: string
  is_active: boolean
  metrics: {
    rmse: number
    mae: number
    precision_at_k?: number
    recall_at_k?: number
  }
  created_at: string
  trained_at?: string
}

export interface SystemStats {
  total_users: number
  total_animes: number
  total_ratings: number
  active_model: string
}

export interface ChartData {
  labels: string[]
  values: number[]
}
