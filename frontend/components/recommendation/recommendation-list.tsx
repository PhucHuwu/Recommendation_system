"use client"

import { useRef } from "react"
import { AnimeCard } from "@/components/anime/anime-card"
import { CardSkeleton } from "@/components/ui/loading"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight } from "lucide-react"
import type { RecommendationResponse } from "@/types/api"
import type { Anime } from "@/types/anime"

interface RecommendationListProps {
  title: string
  items: (RecommendationResponse | Anime)[]
  loading?: boolean
  showScrollButtons?: boolean
}

export function RecommendationList({
  title,
  items,
  loading = false,
  showScrollButtons = true,
}: RecommendationListProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null)

  const scroll = (direction: "left" | "right") => {
    if (scrollContainerRef.current) {
      const scrollAmount = 300
      scrollContainerRef.current.scrollBy({
        left: direction === "left" ? -scrollAmount : scrollAmount,
        behavior: "smooth",
      })
    }
  }

  if (loading) {
    return (
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">{title}</h2>
        <div className="flex gap-4 overflow-x-auto scrollbar-hide pb-4">
          {Array.from({ length: 6 }, (_, i) => (
            <div key={i} className="w-48 flex-shrink-0">
              <CardSkeleton />
            </div>
          ))}
        </div>
      </section>
    )
  }

  if (items.length === 0) {
    return null
  }

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">{title}</h2>
        {showScrollButtons && items.length > 5 && (
          <div className="hidden md:flex items-center gap-2">
            <Button variant="outline" size="icon" onClick={() => scroll("left")} className="h-8 w-8">
              <ChevronLeft className="h-4 w-4" />
              <span className="sr-only">Cuộn trái</span>
            </Button>
            <Button variant="outline" size="icon" onClick={() => scroll("right")} className="h-8 w-8">
              <ChevronRight className="h-4 w-4" />
              <span className="sr-only">Cuộn phải</span>
            </Button>
          </div>
        )}
      </div>

      <div ref={scrollContainerRef} className="flex gap-4 overflow-x-auto scrollbar-hide pb-4 -mx-4 px-4">
        {items.map((item) => {
          const isRecommendation = "predicted_rating" in item
          const animeId = isRecommendation ? item.anime_id : item.anime_id
          const name = item.name
          const score = isRecommendation ? item.predicted_rating : item.rating
          const genres = isRecommendation ? item.genre || [] : item.genre
          const episodes = !isRecommendation ? item.episodes : undefined
          const type = !isRecommendation ? item.type : undefined

          return (
            <div key={animeId} className="w-48 flex-shrink-0">
              <AnimeCard id={animeId} name={name} score={score} genres={genres} episodes={episodes} type={type} />
            </div>
          )
        })}
      </div>
    </section>
  )
}
