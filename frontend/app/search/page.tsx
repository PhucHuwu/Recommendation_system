"use client"

import { useState, useEffect, Suspense } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { AnimeList } from "@/components/anime/anime-list"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Search, X, Film } from "lucide-react"
import { useDebounce } from "@/hooks/use-debounce"
import type { Anime } from "@/types/anime"

// Mock data
const mockAnimes: Anime[] = Array.from({ length: 30 }, (_, i) => ({
  anime_id: i + 1,
  name:
    [
      "Attack on Titan",
      "Death Note",
      "Fullmetal Alchemist",
      "One Piece",
      "Naruto",
      "Dragon Ball Z",
      "Demon Slayer",
      "Jujutsu Kaisen",
      "My Hero Academia",
      "One Punch Man",
    ][i % 10] + (i >= 10 ? ` Season ${Math.floor(i / 10) + 1}` : ""),
  genre: ["Action", "Adventure", "Drama"].slice(0, (i % 3) + 1),
  type: ["TV", "Movie", "OVA"][i % 3],
  episodes: [24, 12, 37][i % 3],
  rating: 7 + Math.random() * 3,
  members: Math.floor(500000 + Math.random() * 2500000),
}))

function SearchContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const initialQuery = searchParams.get("q") || ""

  const [query, setQuery] = useState(initialQuery)
  const [results, setResults] = useState<Anime[]>([])
  const [loading, setLoading] = useState(false)
  const [hasSearched, setHasSearched] = useState(!!initialQuery)

  const debouncedQuery = useDebounce(query, 300)

  useEffect(() => {
    const search = async () => {
      if (!debouncedQuery.trim()) {
        setResults([])
        setHasSearched(false)
        return
      }

      setLoading(true)
      setHasSearched(true)

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 300))

      const filtered = mockAnimes.filter((anime) => anime.name.toLowerCase().includes(debouncedQuery.toLowerCase()))

      setResults(filtered)
      setLoading(false)

      // Update URL
      router.replace(`/search?q=${encodeURIComponent(debouncedQuery)}`, { scroll: false })
    }

    search()
  }, [debouncedQuery, router])

  const clearSearch = () => {
    setQuery("")
    setResults([])
    setHasSearched(false)
    router.replace("/search", { scroll: false })
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Tìm kiếm Anime</h1>
        <p className="text-muted-foreground">Nhập tên anime bạn muốn tìm</p>
      </div>

      {/* Search Input */}
      <div className="relative max-w-2xl mb-8">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
        <Input
          type="search"
          placeholder="Tìm kiếm anime..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="pl-12 pr-12 h-14 text-lg"
          autoFocus
        />
        {query && (
          <Button
            variant="ghost"
            size="icon"
            className="absolute right-2 top-1/2 -translate-y-1/2"
            onClick={clearSearch}
          >
            <X className="h-5 w-5" />
            <span className="sr-only">Xóa tìm kiếm</span>
          </Button>
        )}
      </div>

      {/* Results */}
      {hasSearched ? (
        <>
          {!loading && results.length > 0 && (
            <p className="text-muted-foreground mb-6">
              Tìm thấy <span className="font-medium text-foreground">{results.length}</span> kết quả cho "
              {debouncedQuery}"
            </p>
          )}
          <AnimeList
            animes={results}
            loading={loading}
            emptyMessage={`Không tìm thấy kết quả cho "${debouncedQuery}"`}
          />
        </>
      ) : (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <Film className="h-16 w-16 text-muted-foreground/50 mb-4" />
          <h2 className="text-xl font-semibold mb-2">Bắt đầu tìm kiếm</h2>
          <p className="text-muted-foreground max-w-md">
            Nhập tên anime vào ô tìm kiếm để tìm những bộ anime bạn yêu thích
          </p>
        </div>
      )}
    </div>
  )
}

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="container mx-auto px-4 py-8">Đang tải...</div>}>
      <SearchContent />
    </Suspense>
  )
}
