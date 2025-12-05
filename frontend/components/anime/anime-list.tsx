"use client";

import { AnimeCard } from "./anime-card";
import { CardSkeleton } from "@/components/ui/loading";
import type { Anime } from "@/types/anime";

interface AnimeListProps {
    animes: Anime[];
    loading?: boolean;
    emptyMessage?: string;
}

export function AnimeList({ animes, loading = false, emptyMessage = "Không tìm thấy anime nào" }: AnimeListProps) {
    if (loading) {
        return (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                {Array.from({ length: 10 }, (_, i) => (
                    <CardSkeleton key={i} />
                ))}
            </div>
        );
    }

    if (animes.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-16 text-center">
                <p className="text-muted-foreground text-lg">{emptyMessage}</p>
            </div>
        );
    }

    return (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {animes.map((anime) => {
                const animeId = (anime as any).mal_id || anime.anime_id;
                const score = (anime as any).score || (anime as any).rating || 0;
                const genres = (anime as any).genres || (anime as any).genre || [];

                return <AnimeCard key={animeId} id={animeId} name={anime.name} score={score} genres={genres} episodes={anime.episodes} type={anime.type} />;
            })}
        </div>
    );
}
