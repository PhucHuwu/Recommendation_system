"use client"

import { useState, useEffect } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { useAuth } from "@/context/auth-context"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { RatingStars } from "@/components/anime/rating-stars"
import { RecommendationList } from "@/components/recommendation/recommendation-list"
import { PageLoading } from "@/components/ui/loading"
import { Play, Plus, Star, Users, Calendar, Film, Clock, Trophy, Heart, ArrowLeft, Tv, Video } from "lucide-react"
import { cn } from "@/lib/utils"
import type { AnimeDetail } from "@/types/anime"
import type { RecommendationResponse } from "@/types/api"

// Mock data
const mockAnimeDetail: AnimeDetail = {
  anime_id: 1,
  name: "Attack on Titan",
  genre: ["Action", "Drama", "Fantasy", "Military", "Mystery"],
  type: "TV",
  episodes: 75,
  rating: 9.1,
  members: 3500000,
  synopsis:
    "Centuries ago, mankind was slaughtered to near extinction by monstrous humanoid creatures called Titans, forcing humans to hide in fear behind enormous concentric walls. What makes these giants truly terrifying is that their taste for human flesh is not born out of hunger but what appears to be out of pleasure. To ensure their survival, the remnants of humanity began living within defensive barriers, resulting in one hundred years without a single titan encounter. However, that fragile calm is soon shattered when a colossal Titan manages to breach the supposedly impregnable outer wall, reigniting the fight for survival against the man-eating abominations.",
  aired: "Apr 7, 2013 to Sep 29, 2013",
  score: 9.1,
  scored_by: 2500000,
  rank: 1,
  popularity: 1,
  favorites: 150000,
}

const mockSimilarAnimes: RecommendationResponse[] = [
  { anime_id: 2, name: "Demon Slayer", predicted_rating: 8.9, genre: ["Action", "Fantasy", "Supernatural"] },
  { anime_id: 3, name: "Jujutsu Kaisen", predicted_rating: 8.8, genre: ["Action", "Supernatural", "School"] },
  { anime_id: 4, name: "Vinland Saga", predicted_rating: 8.7, genre: ["Action", "Adventure", "Drama"] },
  { anime_id: 5, name: "Tokyo Ghoul", predicted_rating: 8.5, genre: ["Action", "Horror", "Mystery"] },
  { anime_id: 6, name: "Kabaneri of the Iron Fortress", predicted_rating: 7.8, genre: ["Action", "Fantasy", "Horror"] },
]

function getTypeIcon(type?: string) {
  switch (type?.toLowerCase()) {
    case "tv":
      return Tv
    case "movie":
      return Film
    default:
      return Video
  }
}

function getGradientClass(name: string) {
  const gradients = [
    "from-indigo-500/30 to-purple-600/30",
    "from-blue-500/30 to-cyan-500/30",
    "from-emerald-500/30 to-teal-500/30",
    "from-orange-500/30 to-red-500/30",
    "from-pink-500/30 to-rose-500/30",
    "from-violet-500/30 to-indigo-500/30",
  ]
  const index = name.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0) % gradients.length
  return gradients[index]
}

export default function AnimeDetailPage() {
  const params = useParams()
  const { user, isAuthenticated } = useAuth()
  const [anime, setAnime] = useState<AnimeDetail | null>(null)
  const [similarAnimes, setSimilarAnimes] = useState<RecommendationResponse[]>([])
  const [userRating, setUserRating] = useState<number>(0)
  const [loading, setLoading] = useState(true)
  const [ratingLoading, setRatingLoading] = useState(false)

  useEffect(() => {
    const fetchAnime = async () => {
      setLoading(true)
      await new Promise((resolve) => setTimeout(resolve, 500))
      setAnime({ ...mockAnimeDetail, anime_id: Number(params.id) })
      setSimilarAnimes(mockSimilarAnimes)
      setLoading(false)
    }

    fetchAnime()
  }, [params.id])

  const handleRating = async (rating: number) => {
    if (!isAuthenticated) return

    setRatingLoading(true)
    await new Promise((resolve) => setTimeout(resolve, 300))
    setUserRating(rating)
    setRatingLoading(false)
  }

  const handleAddToHistory = async () => {
    if (!isAuthenticated) return
    await new Promise((resolve) => setTimeout(resolve, 300))
  }

  if (loading) {
    return <PageLoading />
  }

  if (!anime) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <h1 className="text-2xl font-bold mb-4">Không tìm thấy anime</h1>
        <Button asChild>
          <Link href="/anime">Quay lại danh sách</Link>
        </Button>
      </div>
    )
  }

  const TypeIcon = getTypeIcon(anime.type)
  const gradientClass = getGradientClass(anime.name)

  return (
    <div className="min-h-screen">
      {/* Back Button */}
      <div className="container mx-auto px-4 py-4">
        <Button variant="ghost" size="sm" asChild>
          <Link href="/anime">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Quay lại
          </Link>
        </Button>
      </div>

      {/* Hero Section */}
      <section className="relative">
        {/* Background */}
        <div className="absolute inset-0 h-96 bg-gradient-to-b from-primary/20 to-background" />

        <div className="container mx-auto px-4 pt-8 pb-12 relative">
          <div className="flex flex-col md:flex-row gap-8">
            <div className="flex-shrink-0 w-full md:w-72">
              <div
                className={cn(
                  "relative aspect-[3/4] rounded-xl overflow-hidden shadow-2xl bg-gradient-to-br",
                  gradientClass,
                  "flex items-center justify-center border border-border",
                )}
              >
                <TypeIcon className="h-24 w-24 text-foreground/20" />
                {/* Score overlay */}
                <div className="absolute bottom-4 left-4 right-4">
                  <div className="bg-background/90 backdrop-blur-sm rounded-lg p-3 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Star className="h-5 w-5 text-warning fill-warning" />
                      <span className="text-xl font-bold">{anime.rating.toFixed(1)}</span>
                    </div>
                    <Badge variant="secondary">{anime.type}</Badge>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col gap-2 mt-4">
                <Button className="w-full" size="lg">
                  <Play className="h-5 w-5 mr-2" />
                  Xem ngay
                </Button>
                {isAuthenticated && (
                  <Button variant="outline" className="w-full bg-transparent" onClick={handleAddToHistory}>
                    <Plus className="h-5 w-5 mr-2" />
                    Thêm vào lịch sử
                  </Button>
                )}
              </div>
            </div>

            {/* Info */}
            <div className="flex-1">
              <h1 className="text-3xl md:text-4xl font-bold mb-4">{anime.name}</h1>

              {/* Genres */}
              <div className="flex flex-wrap gap-2 mb-6">
                {anime.genre.map((genre) => (
                  <Badge key={genre} variant="secondary">
                    {genre}
                  </Badge>
                ))}
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <Card className="bg-card/50">
                  <CardContent className="p-4 flex items-center gap-3">
                    <Star className="h-5 w-5 text-warning" />
                    <div>
                      <p className="text-2xl font-bold">{anime.rating.toFixed(1)}</p>
                      <p className="text-xs text-muted-foreground">Điểm</p>
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-card/50">
                  <CardContent className="p-4 flex items-center gap-3">
                    <Trophy className="h-5 w-5 text-primary" />
                    <div>
                      <p className="text-2xl font-bold">#{anime.rank}</p>
                      <p className="text-xs text-muted-foreground">Xếp hạng</p>
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-card/50">
                  <CardContent className="p-4 flex items-center gap-3">
                    <Users className="h-5 w-5 text-primary" />
                    <div>
                      <p className="text-2xl font-bold">{(anime.members / 1000000).toFixed(1)}M</p>
                      <p className="text-xs text-muted-foreground">Thành viên</p>
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-card/50">
                  <CardContent className="p-4 flex items-center gap-3">
                    <Heart className="h-5 w-5 text-destructive" />
                    <div>
                      <p className="text-2xl font-bold">{(anime.favorites! / 1000).toFixed(0)}K</p>
                      <p className="text-xs text-muted-foreground">Yêu thích</p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Meta Info */}
              <div className="flex flex-wrap gap-6 text-sm text-muted-foreground mb-6">
                <div className="flex items-center gap-2">
                  <Film className="h-4 w-4" />
                  <span>{anime.type}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  <span>{anime.episodes} tập</span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  <span>{anime.aired}</span>
                </div>
              </div>

              {/* Synopsis */}
              <Card className="bg-card/50">
                <CardHeader>
                  <CardTitle className="text-lg">Nội dung</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground leading-relaxed">{anime.synopsis}</p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* User Rating Section */}
      {isAuthenticated && (
        <section className="container mx-auto px-4 py-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Star className="h-5 w-5 text-warning" />
                Đánh giá của bạn
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                <RatingStars value={userRating} onChange={handleRating} size="lg" showValue />
                {ratingLoading && <span className="text-sm text-muted-foreground">Đang lưu...</span>}
                {userRating > 0 && !ratingLoading && (
                  <span className="text-sm text-success">Đã lưu đánh giá của bạn</span>
                )}
              </div>
              {!userRating && (
                <p className="text-sm text-muted-foreground mt-2">
                  Click vào các ngôi sao để đánh giá anime này (1-10)
                </p>
              )}
            </CardContent>
          </Card>
        </section>
      )}

      {/* Similar Anime Section */}
      <section className="container mx-auto px-4 py-8">
        <RecommendationList title="Anime tương tự" items={similarAnimes} />
      </section>
    </div>
  )
}
