"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/context/auth-context";
import { Button } from "@/components/ui/button";
import { RecommendationList } from "@/components/recommendation/recommendation-list";
import { Play, Sparkles, TrendingUp } from "lucide-react";
import { api } from "@/lib/api";
import type { Anime } from "@/types/anime";
import type { RecommendationResponse } from "@/types/api";

export default function HomePage() {
    const { user, token, isAuthenticated } = useAuth();
    const [topAnimes, setTopAnimes] = useState<Anime[]>([]);
    const [recommendations, setRecommendations] = useState<RecommendationResponse[]>([]);
    const [recentlyWatched, setRecentlyWatched] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setError(null);

            try {
                // Fetch top animes (always visible)
                const topResponse = await api.getTopAnimes(10);
                setTopAnimes(topResponse.animes || []);

                // Fetch user-specific data if authenticated
                if (isAuthenticated && token) {
                    try {
                        // Fetch personalized recommendations
                        const recResponse = await api.getRecommendations(token, 10);
                        setRecommendations(recResponse.recommendations || []);
                    } catch (err) {
                        console.error("Failed to fetch recommendations:", err);
                    }

                    try {
                        // Fetch recently watched
                        const historyResponse = await api.getMyHistory(token, 1, 4);
                        setRecentlyWatched(historyResponse.history || []);
                    } catch (err) {
                        console.error("Failed to fetch history:", err);
                    }
                }
            } catch (err) {
                console.error("Error fetching data:", err);
                setError("Không thể tải dữ liệu. Vui lòng kiểm tra kết nối Backend.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [isAuthenticated, token]);

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
                            Hệ thống gợi ý thông minh của WibiFlix sẽ giúp bạn tìm ra những bộ anime hay nhất dựa trên sở thích và lịch sử xem của bạn.
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

            {/* Error Message */}
            {error && (
                <div className="container mx-auto px-4 py-4">
                    <div className="bg-destructive/10 text-destructive px-4 py-3 rounded">{error}</div>
                </div>
            )}

            {/* Content Sections */}
            <div className="container mx-auto px-4 py-12 space-y-12">
                {/* Recommendations (only for logged in users) */}
                {isAuthenticated && <RecommendationList title={`Gợi ý cho ${user?.username || "bạn"}`} items={recommendations} loading={loading} />}

                {/* Recently Watched (only for logged in users) */}
                {isAuthenticated && recentlyWatched.length > 0 && (
                    <section className="space-y-4">
                        <h2 className="text-xl font-semibold">Xem gần đây</h2>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            {recentlyWatched.map((item) => (
                                <Link key={item.anime_id} href={`/anime/${item.anime_id}`} className="group">
                                    <div className="bg-card rounded-lg p-4 hover:bg-accent transition-colors">
                                        <h3 className="font-medium group-hover:text-primary transition-colors line-clamp-2">
                                            {item.anime_name || `Anime ${item.anime_id}`}
                                        </h3>
                                        {item.anime_genres && <p className="text-sm text-muted-foreground mt-1 line-clamp-1">{item.anime_genres}</p>}
                                    </div>
                                </Link>
                            ))}
                        </div>
                    </section>
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
                            Đăng nhập để hệ thống AI của chúng tôi có thể phân tích sở thích và gợi ý những bộ anime phù hợp nhất với bạn.
                        </p>
                        <Button size="lg" asChild>
                            <Link href="/login">Đăng nhập ngay</Link>
                        </Button>
                    </section>
                )}
            </div>
        </div>
    );
}
