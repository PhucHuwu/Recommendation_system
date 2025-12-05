"use client"

import Link from "next/link"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { Film, Tv, Video, Star } from "lucide-react"
import type { AnimeCardProps } from "@/types/anime"

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
    "from-indigo-500/20 to-purple-600/20",
    "from-blue-500/20 to-cyan-500/20",
    "from-emerald-500/20 to-teal-500/20",
    "from-orange-500/20 to-red-500/20",
    "from-pink-500/20 to-rose-500/20",
    "from-violet-500/20 to-indigo-500/20",
    "from-amber-500/20 to-yellow-500/20",
    "from-cyan-500/20 to-blue-500/20",
  ]
  const index = name.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0) % gradients.length
  return gradients[index]
}

export function AnimeCard({ id, name, score, genres, episodes, type }: AnimeCardProps) {
  const displayGenres = genres.slice(0, 2)
  const TypeIcon = getTypeIcon(type)
  const gradientClass = getGradientClass(name)

  return (
    <Link href={`/anime/${id}`}>
      <Card className="group overflow-hidden bg-card border-border hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:shadow-primary/10 h-full">
        <div className={cn("relative h-32 bg-gradient-to-br", gradientClass, "flex items-center justify-center")}>
          <TypeIcon className="h-12 w-12 text-foreground/30 group-hover:text-primary/50 transition-colors" />

          {/* Score badge */}
          <div className="absolute top-2 right-2">
            <Badge
              variant="secondary"
              className={cn(
                "font-bold flex items-center gap-1",
                score >= 8 && "bg-success text-success-foreground",
                score >= 6 && score < 8 && "bg-warning text-warning-foreground",
                score < 6 && "bg-destructive text-destructive-foreground",
              )}
            >
              <Star className="h-3 w-3" />
              {score.toFixed(1)}
            </Badge>
          </div>

          {/* Type badge */}
          {type && (
            <div className="absolute top-2 left-2">
              <Badge variant="outline" className="bg-background/80 border-border text-xs">
                {type}
              </Badge>
            </div>
          )}
        </div>

        <CardContent className="p-4">
          <h3 className="font-semibold text-foreground line-clamp-2 mb-2 group-hover:text-primary transition-colors min-h-[2.5rem]">
            {name}
          </h3>

          {episodes && <p className="text-xs text-muted-foreground mb-2">{episodes} tập</p>}

          <div className="flex flex-wrap gap-1">
            {displayGenres.map((genre) => (
              <Badge key={genre} variant="outline" className="text-xs bg-secondary/50">
                {genre}
              </Badge>
            ))}
            {genres.length > 2 && (
              <Badge variant="outline" className="text-xs bg-secondary/50">
                +{genres.length - 2}
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
