"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useAuth } from "@/context/auth-context"
import { Button } from "@/components/ui/button"
import { RecommendationList } from "@/components/recommendation/recommendation-list"
import { Play, Sparkles, TrendingUp } from "lucide-react"
import type { Anime } from "@/types/anime"
import type { RecommendationResponse } from "@/types/api"

// Mock data for demonstration
const mockTopAnimes: Anime[] = [
  {
    anime_id: 1,
    name: "Attack on Titan",
    genre: ["Action", "Drama", "Fantasy"],
    type: "TV",
    episodes: 75,
    rating: 9.1,
    members: 3500000,
  },
  {
    anime_id: 2,
    name: "Death Note",
    genre: ["Mystery", "Psychological", "Thriller"],
    type: "TV",
    episodes: 37,
    rating: 9.0,
    members: 3200000,
  },
  {
    anime_id: 3,
    name: "Fullmetal Alchemist: Brotherhood",
    genre: ["Action", "Adventure", "Drama"],
    type: "TV",
    episodes: 64,
    rating: 9.2,
    members: 2800000,
  },
  {
    anime_id: 4,
    name: "Steins;Gate",
    genre: ["Sci-Fi", "Thriller", "Drama"],
    type: "TV",
    episodes: 24,
    rating: 9.1,
    members: 2100000,
  },
  {
    anime_id: 5,
    name: "One Punch Man",
    genre: ["Action", "Comedy", "Parody"],
    type: "TV",
    episodes: 24,
    rating: 8.7,
    members: 2500000,
  },
  {
    anime_id: 6,
    name: "Demon Slayer",
    genre: ["Action", "Fantasy", "Supernatural"],
    type: "TV",
    episodes: 26,
    rating: 8.9,
    members: 2300000,
  },
]

const mockRecommendations: RecommendationResponse[] = [
  { anime_id: 7, name: "Jujutsu Kaisen", predicted_rating: 9.0, genre: ["Action", "Supernatural", "School"] },
  { anime_id: 8, name: "Spy x Family", predicted_rating: 8.8, genre: ["Action", "Comedy", "Slice of Life"] },
  { anime_id: 9, name: "Chainsaw Man", predicted_rating: 8.7, genre: ["Action", "Horror", "Supernatural"] },
  { anime_id: 10, name: "My Hero Academia", predicted_rating: 8.5, genre: ["Action", "School", "Superhero"] },
  { anime_id: 11, name: "Tokyo Revengers", predicted_rating: 8.3, genre: ["Action", "Drama", "Delinquent"] },
  { anime_id: 12, name: "Mob Psycho 100", predicted_rating: 8.9, genre: ["Action", "Comedy", "Supernatural"] },
]

export default function HomePage() {
  const { user, isAuthenticated } = useAuth()
  const [topAnimes, setTopAnimes] = useState<Anime[]>([])
  const [recommendations, setRecommendations] = useState<RecommendationResponse[]>([])
  const [recentlyWatched, setRecentlyWatched] = useState<Anime[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate API call
    const fetchData = async () => {
      setLoading(true)
      // In real app, this would be API calls
      await new Promise((resolve) => setTimeout(resolve, 500))
      setTopAnimes(mockTopAnimes)
      if (isAuthenticated) {
        setRecommendations(mockRecommendations)
        setRecentlyWatched(mockTopAnimes.slice(0, 4))
      }
      setLoading(false)
    }

    fetchData()
  }, [isAuthenticated])

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary/20 via-background to-background">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary/10 via-transparent to-transparent" />
        <div className="container mx-auto px-4 py-16 md:py-24 relative">
          <div className="max-w-3xl">
            <h1 className="text-4xl md:text-6xl font-bold mb-6 text-balance">
              Khám phá <span className="text-primary">Anime</span> phù hợp với bạn
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground mb-8 text-pretty">
              Hệ thống gợi ý thông minh của Wibiflix sẽ giúp bạn tìm ra những bộ anime hay nhất dựa trên sở thích và
              lịch sử xem của bạn.
            </p>
            <div className="flex flex-wrap gap-4">
              {isAuthenticated ? (
                <Button size="lg" asChild>
                  <Link href="/anime">
                    <Play className="mr-2 h-5 w-5" />
                    Khám phá ngay
                  </Link>
                </Button>
              ) : (
                <>
                  <Button size="lg" asChild>
                    <Link href="/login">
                      <Sparkles className="mr-2 h-5 w-5" />
                      Đăng nhập để nhận gợi ý
                    </Link>
                  </Button>
                  <Button size="lg" variant="outline" asChild>
                    <Link href="/anime">Xem danh sách Anime</Link>
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Content Sections */}
      <div className="container mx-auto px-4 py-12 space-y-12">
        {/* Recommendations (only for logged in users) */}
        {isAuthenticated && (
          <RecommendationList
            title={`Gợi ý cho ${user?.username || "bạn"}`}
            items={recommendations}
            loading={loading}
          />
        )}

        {/* Recently Watched (only for logged in users) */}
        {isAuthenticated && recentlyWatched.length > 0 && (
          <RecommendationList title="Xem gần đây" items={recentlyWatched} loading={loading} />
        )}

        {/* Top Anime */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-6 w-6 text-primary" />
              <h2 className="text-xl font-semibold">Top Anime</h2>
            </div>
            <Button variant="ghost" asChild>
              <Link href="/anime?sort=rating">Xem tất cả</Link>
            </Button>
          </div>
          <RecommendationList title="" items={topAnimes} loading={loading} showScrollButtons={false} />
        </section>

        {/* CTA for non-logged in users */}
        {!isAuthenticated && (
          <section className="bg-card rounded-2xl p-8 md:p-12 text-center">
            <Sparkles className="h-12 w-12 text-primary mx-auto mb-4" />
            <h2 className="text-2xl md:text-3xl font-bold mb-4">Nhận gợi ý anime cá nhân hóa</h2>
            <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
              Đăng nhập để hệ thống AI của chúng tôi có thể phân tích sở thích và gợi ý những bộ anime phù hợp nhất với
              bạn.
            </p>
            <Button size="lg" asChild>
              <Link href="/login">Đăng nhập ngay</Link>
            </Button>
          </section>
        )}
      </div>
    </div>
  )
}
