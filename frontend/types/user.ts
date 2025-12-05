export interface User {
  user_id: number
  username?: string
  email?: string
  created_at?: string
}

export interface UserRating {
  user_id: number
  anime_id: number
  rating: number
  timestamp?: string
  anime?: {
    name: string
    image_url?: string
    genre: string[]
  }
}

export interface UserHistory {
  user_id: number
  anime_id: number
  watched_at: string
  anime?: {
    name: string
    image_url?: string
    genre: string[]
    rating: number
  }
}

export interface UserStats {
  total_ratings: number
  total_watched: number
  favorite_genres: string[]
  average_rating: number
}
