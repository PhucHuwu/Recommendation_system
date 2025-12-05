"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/auth-context";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { PageLoading } from "@/components/ui/loading";
import { Star, Film, Heart, TrendingUp, BarChart3, LogOut } from "lucide-react";
import { api } from "@/lib/api";
import type { UserRating, UserStats } from "@/types/user";

export default function ProfilePage() {
    const { user, token, isAuthenticated, isLoading: authLoading, logout } = useAuth();
    const router = useRouter();
    const [stats, setStats] = useState<UserStats | null>(null);
    const [ratings, setRatings] = useState<UserRating[]>([]);
    const [ratingDistribution, setRatingDistribution] = useState<{ rating: number; count: number }[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!authLoading && !isAuthenticated) {
            router.push("/login");
            return;
        }

        if (isAuthenticated && user) {
            const fetchData = async () => {
                setLoading(true);
                try {
                    // Fetch user ratings
                    const ratingsResponse = await api.getUserRatings(user.user_id, 1, 50);

                    // Transform to UserRating format
                    const userRatings: UserRating[] = (ratingsResponse.ratings || []).map((item: any) => ({
                        user_id: user.user_id,
                        anime_id: item.anime_id,
                        rating: item.rating,
                        anime: {
                            name: item.anime_name || `Anime ${item.anime_id}`,
                            genre: item.anime_genres ? item.anime_genres.split(", ") : [],
                        },
                    }));
                    setRatings(userRatings);

                    // Calculate stats from ratings
                    const totalRatings = ratingsResponse.total || userRatings.length;
                    const avgRating = userRatings.length > 0 ? userRatings.reduce((sum, r) => sum + r.rating, 0) / userRatings.length : 0;

                    // Get unique genres from ratings
                    const genreSet = new Set<string>();
                    userRatings.forEach((r) => {
                        r.anime?.genre?.forEach((g: string) => genreSet.add(g));
                    });
                    const favoriteGenres = Array.from(genreSet).slice(0, 5);

                    // Fetch history count (optional)
                    let totalWatched = 0;
                    if (token) {
                        try {
                            const historyResponse = await api.getMyHistory(token, 1, 1);
                            totalWatched = historyResponse.total || 0;
                        } catch (e) {
                            console.error("Failed to fetch history count:", e);
                        }
                    }

                    setStats({
                        total_ratings: totalRatings,
                        total_watched: totalWatched,
                        favorite_genres: favoriteGenres,
                        average_rating: avgRating,
                    });

                    // Calculate rating distribution
                    const distribution: Record<number, number> = {};
                    for (let i = 1; i <= 10; i++) distribution[i] = 0;
                    userRatings.forEach((r) => {
                        if (r.rating >= 1 && r.rating <= 10) {
                            distribution[r.rating]++;
                        }
                    });
                    setRatingDistribution(
                        Object.entries(distribution).map(([rating, count]) => ({
                            rating: parseInt(rating),
                            count,
                        }))
                    );
                } catch (error) {
                    console.error("Failed to fetch profile data:", error);
                } finally {
                    setLoading(false);
                }
            };
            fetchData();
        }
    }, [isAuthenticated, authLoading, user, token, router]);

    const handleLogout = () => {
        logout();
        router.push("/");
    };

    if (authLoading || (!isAuthenticated && !authLoading)) {
        return <PageLoading />;
    }

    const maxRatingCount = Math.max(...ratingDistribution.map((r) => r.count), 1);

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Profile Header */}
            <div className="flex flex-col md:flex-row items-start md:items-center gap-6 mb-8">
                {/* Avatar */}
                <div className="flex items-center justify-center h-24 w-24 rounded-full bg-primary text-primary-foreground">
                    <span className="text-4xl font-bold">{user?.user_id?.toString().charAt(0) || "U"}</span>
                </div>

                {/* Info */}
                <div className="flex-1">
                    <h1 className="text-3xl font-bold mb-1">User #{user?.user_id}</h1>
                    <p className="text-muted-foreground mb-4">{user?.username || `User ${user?.user_id}`}</p>
                    <div className="flex flex-wrap gap-4">
                        <Button variant="outline" asChild>
                            <Link href="/history">
                                <Film className="h-4 w-4 mr-2" />
                                Lịch sử xem
                            </Link>
                        </Button>
                        <Button variant="destructive" onClick={handleLogout}>
                            <LogOut className="h-4 w-4 mr-2" />
                            Đăng xuất
                        </Button>
                    </div>
                </div>
            </div>

            {/* Stats Grid */}
            {loading ? (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    {Array.from({ length: 4 }, (_, i) => (
                        <Card key={i} className="animate-pulse">
                            <CardContent className="p-6">
                                <div className="h-10 bg-muted rounded mb-2" />
                                <div className="h-4 bg-muted rounded w-1/2" />
                            </CardContent>
                        </Card>
                    ))}
                </div>
            ) : (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    <Card>
                        <CardContent className="p-6">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-primary/10">
                                    <Star className="h-6 w-6 text-primary" />
                                </div>
                                <div>
                                    <p className="text-3xl font-bold">{stats?.total_ratings}</p>
                                    <p className="text-sm text-muted-foreground">Đánh giá</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardContent className="p-6">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-success/10">
                                    <Film className="h-6 w-6 text-success" />
                                </div>
                                <div>
                                    <p className="text-3xl font-bold">{stats?.total_watched}</p>
                                    <p className="text-sm text-muted-foreground">Đã xem</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardContent className="p-6">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-warning/10">
                                    <TrendingUp className="h-6 w-6 text-warning" />
                                </div>
                                <div>
                                    <p className="text-3xl font-bold">{stats?.average_rating.toFixed(1)}</p>
                                    <p className="text-sm text-muted-foreground">Điểm TB</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardContent className="p-6">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-destructive/10">
                                    <Heart className="h-6 w-6 text-destructive" />
                                </div>
                                <div>
                                    <p className="text-3xl font-bold">{stats?.favorite_genres.length}</p>
                                    <p className="text-sm text-muted-foreground">Thể loại yêu thích</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}

            {/* Main Content */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Favorite Genres */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Heart className="h-5 w-5 text-destructive" />
                            Thể loại yêu thích
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        {loading ? (
                            <div className="space-y-2">
                                {Array.from({ length: 5 }, (_, i) => (
                                    <div key={i} className="h-8 bg-muted rounded animate-pulse" />
                                ))}
                            </div>
                        ) : (
                            <div className="flex flex-wrap gap-2">
                                {stats?.favorite_genres.map((genre, index) => (
                                    <Badge key={genre} variant={index === 0 ? "default" : "secondary"} className="text-sm">
                                        {genre}
                                        {index === 0 && <span className="ml-1 text-xs">★</span>}
                                    </Badge>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Rating Distribution */}
                <Card className="lg:col-span-2">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <BarChart3 className="h-5 w-5 text-primary" />
                            Phân bố đánh giá
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        {loading ? (
                            <div className="space-y-3">
                                {Array.from({ length: 10 }, (_, i) => (
                                    <div key={i} className="flex items-center gap-3">
                                        <div className="w-8 h-4 bg-muted rounded animate-pulse" />
                                        <div className="flex-1 h-4 bg-muted rounded animate-pulse" />
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="space-y-2">
                                {ratingDistribution.map(({ rating, count }) => (
                                    <div key={rating} className="flex items-center gap-3">
                                        <span className="w-8 text-sm font-medium text-right">{rating}★</span>
                                        <Progress value={maxRatingCount > 0 ? (count / maxRatingCount) * 100 : 0} className="flex-1 h-6" />
                                        <span className="w-8 text-sm text-muted-foreground">{count}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* My Ratings */}
                <Card className="lg:col-span-3">
                    <CardHeader>
                        <CardTitle className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <Star className="h-5 w-5 text-warning" />
                                Anime đã đánh giá
                            </div>
                            {ratings.length > 0 && <Badge variant="secondary">{ratings.length} anime</Badge>}
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        {loading ? (
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                                {Array.from({ length: 8 }, (_, i) => (
                                    <div key={i} className="animate-pulse">
                                        <div className="aspect-[3/4] bg-muted rounded-lg mb-2" />
                                        <div className="h-4 bg-muted rounded w-3/4 mb-1" />
                                        <div className="h-3 bg-muted rounded w-1/2" />
                                    </div>
                                ))}
                            </div>
                        ) : ratings.length === 0 ? (
                            <div className="flex flex-col items-center justify-center py-12 text-center">
                                <Star className="h-12 w-12 text-muted-foreground/50 mb-4" />
                                <h3 className="text-lg font-semibold mb-2">Chưa có đánh giá nào</h3>
                                <p className="text-muted-foreground mb-4">Bắt đầu đánh giá anime để theo dõi sở thích của bạn</p>
                                <Button asChild>
                                    <Link href="/anime">Khám phá anime</Link>
                                </Button>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                                {ratings.map((rating) => (
                                    <Link key={rating.anime_id} href={`/anime/${rating.anime_id}`} className="group">
                                        <Card className="bg-secondary/50 hover:bg-secondary transition-colors">
                                            <CardContent className="p-4">
                                                <div className="flex items-start justify-between gap-2">
                                                    <h4 className="font-medium text-sm line-clamp-2 group-hover:text-primary transition-colors flex-1">
                                                        {rating.anime?.name}
                                                    </h4>
                                                    <Badge className="bg-warning text-warning-foreground font-bold flex-shrink-0">{rating.rating}/10</Badge>
                                                </div>
                                                <div className="flex flex-wrap gap-1 mt-2">
                                                    {rating.anime?.genre?.slice(0, 3).map((genre) => (
                                                        <Badge key={genre} variant="outline" className="text-xs">
                                                            {genre}
                                                        </Badge>
                                                    ))}
                                                </div>
                                            </CardContent>
                                        </Card>
                                    </Link>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
