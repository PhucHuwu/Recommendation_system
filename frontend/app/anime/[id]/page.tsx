"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/auth-context";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { RatingStars } from "@/components/anime/rating-stars";
import { PageLoading } from "@/components/ui/loading";
import { Play, Plus, Star, Users, Clock, ArrowLeft, Tv, Video, Film } from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { Anime } from "@/types/anime";

function getTypeIcon(type?: string) {
    switch (type?.toLowerCase()) {
        case "tv":
            return Tv;
        case "movie":
            return Film;
        default:
            return Video;
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
    ];
    const index = name.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0) % gradients.length;
    return gradients[index];
}

export default function AnimeDetailPage() {
    const params = useParams();
    const { user, token, isAuthenticated } = useAuth();
    const [anime, setAnime] = useState<(Anime & { synopsis?: string; user_avg_rating?: number }) | null>(null);
    const [similarAnimes, setSimilarAnimes] = useState<any[]>([]);
    const [userRating, setUserRating] = useState<number>(0);
    const [loading, setLoading] = useState(true);
    const [ratingLoading, setRatingLoading] = useState(false);

    useEffect(() => {
        const fetchAnime = async () => {
            setLoading(true);
            try {
                const animeId = Number(params.id);

                // Fetch anime details
                const response = await api.getAnime(animeId);
                setAnime(response.anime);

                // Fetch similar animes (using content-based)
                try {
                    const similarResponse = await api.getSimilarAnimes(animeId, 12, true);
                    setSimilarAnimes(similarResponse.similar_animes || []);
                } catch (err) {
                    console.error("Failed to fetch similar animes:", err);
                }

                // Fetch user's rating if authenticated
                if (isAuthenticated && token) {
                    try {
                        const ratingResponse = await api.getMyRatingForAnime(token, animeId);
                        if (ratingResponse.rating) {
                            setUserRating(ratingResponse.rating.rating);
                        }
                    } catch (err) {
                        console.error("Failed to fetch user rating:", err);
                    }
                }
            } catch (error) {
                console.error("Failed to fetch anime:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchAnime();
    }, [params.id, isAuthenticated, token]);

    const handleRating = async (rating: number) => {
        if (!isAuthenticated || !token) return;

        setRatingLoading(true);
        try {
            const animeId = Number(params.id);

            if (userRating > 0) {
                // Update existing rating
                await api.updateRating(token, animeId, rating);
            } else {
                // Add new rating
                await api.addRating(token, animeId, rating);
            }

            setUserRating(rating);
        } catch (error) {
            console.error("Failed to save rating:", error);
        } finally {
            setRatingLoading(false);
        }
    };

    const handleAddToHistory = async () => {
        if (!isAuthenticated || !token) return;

        try {
            const animeId = Number(params.id);
            await api.addToHistory(token, animeId);
        } catch (error) {
            console.error("Failed to add to history:", error);
        }
    };

    if (loading) {
        return <PageLoading />;
    }

    if (!anime) {
        return (
            <div className="container mx-auto px-4 py-16 text-center">
                <h1 className="text-2xl font-bold mb-4">Không tìm thấy anime</h1>
                <Button asChild>
                    <Link href="/anime">Quay lại danh sách</Link>
                </Button>
            </div>
        );
    }

    const TypeIcon = getTypeIcon(anime.type);
    const gradientClass = getGradientClass(anime.name);

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
                <div className="absolute inset-0 h-96 bg-gradient-to-b from-primary/20 to-background" />

                <div className="container mx-auto px-4 pt-8 pb-12 relative">
                    <div className="flex flex-col md:flex-row gap-8">
                        <div className="flex-shrink-0 w-full md:w-72">
                            <div
                                className={cn(
                                    "relative aspect-[3/4] rounded-xl overflow-hidden shadow-2xl bg-gradient-to-br",
                                    gradientClass,
                                    "flex items-center justify-center border border-border"
                                )}
                            >
                                <TypeIcon className="h-24 w-24 text-foreground/20" />
                                {/* Score overlay */}
                                {anime.score && (
                                    <div className="absolute bottom-4 left-4 right-4">
                                        <div className="bg-background/90 backdrop-blur-sm rounded-lg p-3 flex items-center justify-between">
                                            <div className="flex items-center gap-2">
                                                <Star className="h-5 w-5 text-warning fill-warning" />
                                                <span className="text-xl font-bold">{anime.score.toFixed(1)}</span>
                                            </div>
                                            {anime.type && <Badge variant="secondary">{anime.type}</Badge>}
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Action Buttons */}
                            <div className="flex flex-col gap-2 mt-4">
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
                            {anime.genres && (
                                <div className="flex flex-wrap gap-2 mb-6">
                                    {anime.genres.split(", ").map((genre) => (
                                        <Badge key={genre} variant="secondary">
                                            {genre}
                                        </Badge>
                                    ))}
                                </div>
                            )}

                            {/* Stats Grid */}
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
                                {anime.score && (
                                    <Card className="bg-card/50">
                                        <CardContent className="p-4 flex items-center gap-3">
                                            <Star className="h-5 w-5 text-warning" />
                                            <div>
                                                <p className="text-2xl font-bold">{anime.score.toFixed(1)}</p>
                                                <p className="text-xs text-muted-foreground">Điểm</p>
                                            </div>
                                        </CardContent>
                                    </Card>
                                )}

                                {anime.user_avg_rating && (
                                    <Card className="bg-card/50">
                                        <CardContent className="p-4 flex items-center gap-3">
                                            <Users className="h-5 w-5 text-primary" />
                                            <div>
                                                <p className="text-2xl font-bold">{anime.user_avg_rating.toFixed(1)}</p>
                                                <p className="text-xs text-muted-foreground">User rating</p>
                                            </div>
                                        </CardContent>
                                    </Card>
                                )}

                                {anime.episodes && (
                                    <Card className="bg-card/50">
                                        <CardContent className="p-4 flex items-center gap-3">
                                            <Clock className="h-5 w-5 text-primary" />
                                            <div>
                                                <p className="text-2xl font-bold">{anime.episodes}</p>
                                                <p className="text-xs text-muted-foreground">Tập</p>
                                            </div>
                                        </CardContent>
                                    </Card>
                                )}
                            </div>

                            {/* Synopsis */}
                            {anime.synopsis && (
                                <Card className="bg-card/50">
                                    <CardHeader>
                                        <CardTitle className="text-lg">Nội dung</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <p className="text-muted-foreground leading-relaxed">{anime.synopsis}</p>
                                    </CardContent>
                                </Card>
                            )}
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
                                {userRating > 0 && !ratingLoading && <span className="text-sm text-success">Bạn đã đánh giá {userRating}/10 ⭐</span>}
                            </div>
                            {userRating > 0 ? (
                                <p className="text-sm text-muted-foreground mt-2">Click vào các ngôi sao để cập nhật đánh giá</p>
                            ) : (
                                <p className="text-sm text-muted-foreground mt-2">Click vào các ngôi sao để đánh giá anime này (1-10)</p>
                            )}
                        </CardContent>
                    </Card>
                </section>
            )}

            {/* Similar Anime Section */}
            {similarAnimes.length > 0 && (
                <section className="container mx-auto px-4 py-8">
                    <h2 className="text-2xl font-bold mb-6">Anime tương tự</h2>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                        {similarAnimes.map((similar) => (
                            <Link key={similar.anime_id} href={`/anime/${similar.anime_id}`} className="group">
                                <div className="bg-card rounded-lg p-4 hover:bg-accent transition-colors h-full">
                                    <h3 className="font-medium group-hover:text-primary transition-colors line-clamp-2 mb-2">{similar.name}</h3>
                                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                        <Star className="h-3 w-3" />
                                        <span>{similar.score?.toFixed(1) || "N/A"}</span>
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
                </section>
            )}
        </div>
    );
}
