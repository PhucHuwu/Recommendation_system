"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Users, Film, Star, History } from "lucide-react";
import { api } from "@/lib/api";

export default function AdminDashboardPage() {
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            setLoading(true);
            try {
                const response = await api.getSystemStats();
                setStats(response.stats);
            } catch (error) {
                console.error("Failed to fetch stats:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchStats();
    }, []);

    if (loading) {
        return (
            <div className="space-y-6">
                <h1 className="text-3xl font-bold">Tổng quan hệ thống</h1>
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                    {[1, 2, 3, 4].map((i) => (
                        <Card key={i}>
                            <CardContent className="p-6">
                                <div className="h-20 animate-pulse bg-muted rounded" />
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold">Tổng quan hệ thống</h1>
                <p className="text-muted-foreground">Thống kê tổng quan về hệ thống gợi ý anime</p>
            </div>

            {/* Overview Stats */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Tổng người dùng</CardTitle>
                        <Users className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats?.total_users?.toLocaleString() || 0}</div>
                        <p className="text-xs text-muted-foreground mt-1">Users trong hệ thống</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Tổng Anime</CardTitle>
                        <Film className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats?.total_animes?.toLocaleString() || 0}</div>
                        <p className="text-xs text-muted-foreground mt-1">Anime trong database</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Tổng Ratings</CardTitle>
                        <Star className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats?.total_ratings?.toLocaleString() || 0}</div>
                        <p className="text-xs text-muted-foreground mt-1">Đánh giá từ users</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Lịch sử xem</CardTitle>
                        <History className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats?.total_history?.toLocaleString() || 0}</div>
                        <p className="text-xs text-muted-foreground mt-1">Lượt xem anime</p>
                    </CardContent>
                </Card>
            </div>

            {/* Top Genres */}
            {stats?.top_genres && stats.top_genres.length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle>Top Genres</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-2">
                            {stats.top_genres.slice(0, 10).map((item: any, index: number) => (
                                <div key={item.genre} className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <span className="text-sm font-medium text-muted-foreground">#{index + 1}</span>
                                        <span>{item.genre}</span>
                                    </div>
                                    <span className="text-sm text-muted-foreground">{item.count.toLocaleString()} animes</span>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Rating Distribution */}
            {stats?.rating_distribution &&
                (() => {
                    // Calculate max count for percentage calculation
                    const ratingCounts = Object.values(stats.rating_distribution) as number[];
                    const maxCount = Math.max(...ratingCounts, 1);

                    return (
                        <Card>
                            <CardHeader>
                                <CardTitle>Phân bố Rating (1-10)</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-2">
                                    {Object.entries(stats.rating_distribution)
                                        .sort(([a], [b]) => Number(a) - Number(b))
                                        .map(([rating, count]: [string, any]) => (
                                            <div key={rating} className="flex items-center gap-3">
                                                <span className="w-8 text-sm font-medium text-right">{rating}★</span>
                                                <Progress value={maxCount > 0 ? (count / maxCount) * 100 : 0} className="flex-1 h-6" />
                                                <span className="w-12 text-sm text-muted-foreground text-right">{count.toLocaleString()}</span>
                                            </div>
                                        ))}
                                </div>
                            </CardContent>
                        </Card>
                    );
                })()}
        </div>
    );
}
