"use client"

import { AnimeCard } from "./anime-card"
import { CardSkeleton } from "@/components/ui/loading"
import type { Anime } from "@/types/anime"

interface AnimeListProps {
  animes: Anime[]
  loading?: boolean
  emptyMessage?: string
}

export function AnimeList({ animes, loading = false, emptyMessage = "Không tìm thấy anime nào" }: AnimeListProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
        {Array.from({ length: 10 }, (_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
    )
  }

  if (animes.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <p className="text-muted-foreground text-lg">{emptyMessage}</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
      {animes.map((anime) => (
        <AnimeCard
          key={anime.anime_id}
          id={anime.anime_id}
          name={anime.name}
          score={anime.rating}
          genres={anime.genre}
          imageUrl={anime.image_url}
          episodes={anime.episodes}
          type={anime.type}
        />
      ))}
    </div>
  )
}
