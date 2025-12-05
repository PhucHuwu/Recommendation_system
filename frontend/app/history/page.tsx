"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import Image from "next/image"
import { useAuth } from "@/context/auth-context"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { PageLoading } from "@/components/ui/loading"
import { RatingStars } from "@/components/anime/rating-stars"
import { History, Search, User, Calendar, Film, Trash2, ExternalLink } from "lucide-react"
import type { UserHistory } from "@/types/user"

// Mock data
const mockHistory: UserHistory[] = [
  {
    user_id: 1,
    anime_id: 1,
    watched_at: "2025-01-05T10:30:00Z",
    anime: { name: "Attack on Titan", genre: ["Action", "Drama", "Fantasy"], rating: 9.1 },
  },
  {
    user_id: 1,
    anime_id: 2,
    watched_at: "2025-01-04T15:20:00Z",
    anime: { name: "Death Note", genre: ["Mystery", "Psychological"], rating: 9.0 },
  },
  {
    user_id: 1,
    anime_id: 3,
    watched_at: "2025-01-03T20:00:00Z",
    anime: { name: "Demon Slayer", genre: ["Action", "Fantasy"], rating: 8.9 },
  },
  {
    user_id: 1,
    anime_id: 4,
    watched_at: "2025-01-02T18:45:00Z",
    anime: { name: "Jujutsu Kaisen", genre: ["Action", "Supernatural"], rating: 8.8 },
  },
  {
    user_id: 1,
    anime_id: 5,
    watched_at: "2025-01-01T14:00:00Z",
    anime: { name: "My Hero Academia", genre: ["Action", "School"], rating: 8.5 },
  },
]

function formatDate(dateString: string) {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date)
}

function HistoryItem({ item, onRemove }: { item: UserHistory; onRemove?: () => void }) {
  return (
    <Card className="bg-card hover:bg-card/80 transition-colors">
      <CardContent className="p-4">
        <div className="flex gap-4">
          {/* Thumbnail */}
          <Link href={`/anime/${item.anime_id}`} className="flex-shrink-0">
            <div className="relative w-20 h-28 rounded-lg overflow-hidden">
              <Image
                src={
                  item.anime?.image_url ||
                  `/placeholder.svg?height=112&width=80&query=${encodeURIComponent(item.anime?.name || "anime")}`
                }
                alt={item.anime?.name || "Anime"}
                fill
                className="object-cover"
              />
            </div>
          </Link>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <Link href={`/anime/${item.anime_id}`}>
              <h3 className="font-semibold text-foreground hover:text-primary transition-colors line-clamp-1">
                {item.anime?.name}
              </h3>
            </Link>

            <div className="flex items-center gap-2 mt-1">
              <RatingStars value={item.anime?.rating || 0} readonly size="sm" showValue={false} />
              <span className="text-sm text-muted-foreground">{item.anime?.rating?.toFixed(1)}</span>
            </div>

            <div className="flex flex-wrap gap-1 mt-2">
              {item.anime?.genre?.slice(0, 3).map((genre) => (
                <Badge key={genre} variant="secondary" className="text-xs">
                  {genre}
                </Badge>
              ))}
            </div>

            <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
              <Calendar className="h-3 w-3" />
              <span>{formatDate(item.watched_at)}</span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-col gap-2">
            <Button variant="ghost" size="icon" asChild>
              <Link href={`/anime/${item.anime_id}`}>
                <ExternalLink className="h-4 w-4" />
                <span className="sr-only">Xem chi tiết</span>
              </Link>
            </Button>
            {onRemove && (
              <Button
                variant="ghost"
                size="icon"
                onClick={onRemove}
                className="text-destructive hover:text-destructive"
              >
                <Trash2 className="h-4 w-4" />
                <span className="sr-only">Xóa khỏi lịch sử</span>
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function HistoryList({
  history,
  loading,
  onRemove,
}: {
  history: UserHistory[]
  loading: boolean
  onRemove?: (animeId: number) => void
}) {
  if (loading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 5 }, (_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-4">
              <div className="flex gap-4">
                <div className="w-20 h-28 bg-muted rounded-lg" />
                <div className="flex-1 space-y-2">
                  <div className="h-5 bg-muted rounded w-3/4" />
                  <div className="h-4 bg-muted rounded w-1/4" />
                  <div className="flex gap-1">
                    <div className="h-5 bg-muted rounded-full w-16" />
                    <div className="h-5 bg-muted rounded-full w-12" />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (history.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <Film className="h-16 w-16 text-muted-foreground/50 mb-4" />
        <h3 className="text-lg font-semibold mb-2">Chưa có lịch sử xem</h3>
        <p className="text-muted-foreground mb-4">Bắt đầu xem anime để lưu lịch sử</p>
        <Button asChild>
          <Link href="/anime">Khám phá anime</Link>
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {history.map((item) => (
        <HistoryItem
          key={`${item.anime_id}-${item.watched_at}`}
          item={item}
          onRemove={onRemove ? () => onRemove(item.anime_id) : undefined}
        />
      ))}
    </div>
  )
}

export default function HistoryPage() {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth()
  const router = useRouter()
  const [myHistory, setMyHistory] = useState<UserHistory[]>([])
  const [otherUserHistory, setOtherUserHistory] = useState<UserHistory[]>([])
  const [otherUserId, setOtherUserId] = useState("")
  const [loading, setLoading] = useState(true)
  const [searchLoading, setSearchLoading] = useState(false)
  const [searchError, setSearchError] = useState("")

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login")
      return
    }

    if (isAuthenticated) {
      // Fetch user's history
      const fetchHistory = async () => {
        setLoading(true)
        await new Promise((resolve) => setTimeout(resolve, 500))
        setMyHistory(mockHistory)
        setLoading(false)
      }
      fetchHistory()
    }
  }, [isAuthenticated, authLoading, router])

  const handleSearchUser = async () => {
    if (!otherUserId.trim()) return

    setSearchError("")
    setSearchLoading(true)

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 500))

    const userId = Number.parseInt(otherUserId, 10)
    if (isNaN(userId) || userId <= 0) {
      setSearchError("User ID không hợp lệ")
      setSearchLoading(false)
      return
    }

    // Mock other user's history
    setOtherUserHistory(mockHistory.map((h) => ({ ...h, user_id: userId })))
    setSearchLoading(false)
  }

  const handleRemoveFromHistory = (animeId: number) => {
    setMyHistory((prev) => prev.filter((h) => h.anime_id !== animeId))
  }

  if (authLoading || (!isAuthenticated && !authLoading)) {
    return <PageLoading />
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <History className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold">Lịch sử xem</h1>
          <p className="text-muted-foreground">Xem lại những anime bạn đã xem</p>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="my-history" className="space-y-6">
        <TabsList className="grid w-full max-w-md grid-cols-2">
          <TabsTrigger value="my-history" className="gap-2">
            <User className="h-4 w-4" />
            Của tôi
          </TabsTrigger>
          <TabsTrigger value="other-user" className="gap-2">
            <Search className="h-4 w-4" />
            Xem user khác
          </TabsTrigger>
        </TabsList>

        {/* My History Tab */}
        <TabsContent value="my-history">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Lịch sử xem của bạn</span>
                {myHistory.length > 0 && <Badge variant="secondary">{myHistory.length} anime</Badge>}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <HistoryList history={myHistory} loading={loading} onRemove={handleRemoveFromHistory} />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Other User Tab */}
        <TabsContent value="other-user">
          <Card>
            <CardHeader>
              <CardTitle>Xem lịch sử của user khác</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Search Form */}
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="number"
                    placeholder="Nhập User ID..."
                    value={otherUserId}
                    onChange={(e) => {
                      setOtherUserId(e.target.value)
                      setSearchError("")
                    }}
                    className="pl-10"
                    min="1"
                  />
                </div>
                <Button onClick={handleSearchUser} disabled={searchLoading}>
                  {searchLoading ? "Đang tìm..." : "Tìm kiếm"}
                </Button>
              </div>

              {searchError && <p className="text-sm text-destructive">{searchError}</p>}

              {/* Results */}
              {otherUserId && otherUserHistory.length > 0 && (
                <div className="pt-4 border-t border-border">
                  <h3 className="font-semibold mb-4">Lịch sử xem của User #{otherUserId}</h3>
                  <HistoryList history={otherUserHistory} loading={searchLoading} />
                </div>
              )}

              {otherUserId && !searchLoading && otherUserHistory.length === 0 && !searchError && (
                <div className="text-center py-8 text-muted-foreground">User này chưa có lịch sử xem nào</div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
