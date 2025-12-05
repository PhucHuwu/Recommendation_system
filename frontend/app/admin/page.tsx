"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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

            {/* Rating Distribution - Enhanced */}
            {stats?.rating_distribution && (
                <Card>
                    <CardHeader>
                        <CardTitle>Phân bố Rating (1-10)</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-3">
                            {Object.entries(stats.rating_distribution)
                                .sort(([a], [b]) => Number(a) - Number(b))
                                .map(([rating, count]: [string, any]) => {
                                    // Color mapping based on rating
                                    const ratingColors: Record<string, { from: string; to: string; text: string }> = {
                                        "1": { from: "from-red-500", to: "to-red-600", text: "text-red-50" },
                                        "2": { from: "from-orange-500", to: "to-orange-600", text: "text-orange-50" },
                                        "3": { from: "from-amber-500", to: "to-amber-600", text: "text-amber-50" },
                                        "4": { from: "from-amber-500", to: "to-amber-600", text: "text-amber-50" },
                                        "5": { from: "from-yellow-500", to: "to-yellow-600", text: "text-yellow-50" },
                                        "6": { from: "from-lime-500", to: "to-lime-600", text: "text-lime-50" },
                                        "7": { from: "from-green-500", to: "to-green-600", text: "text-green-50" },
                                        "8": { from: "from-emerald-500", to: "to-emerald-600", text: "text-emerald-50" },
                                        "9": { from: "from-cyan-500", to: "to-cyan-600", text: "text-cyan-50" },
                                        "10": { from: "from-indigo-500", to: "to-indigo-600", text: "text-indigo-50" },
                                    };
                                    const colors = ratingColors[rating] || { from: "from-blue-500", to: "to-blue-600", text: "text-blue-50" };
                                    const percentage = (count / stats.total_ratings) * 100;

                                    return (
                                        <div key={rating} className="flex items-center gap-4">
                                            <span className="text-sm font-semibold w-10 flex items-center gap-1">
                                                {rating}
                                                <span className="text-xs">⭐</span>
                                            </span>
                                            <div className="flex-1 bg-muted/50 rounded-lg h-8 overflow-hidden shadow-sm relative">
                                                <div
                                                    className={`bg-gradient-to-r ${colors.from} ${colors.to} h-full flex items-center justify-end px-3 transition-all duration-700 ease-out`}
                                                    style={{
                                                        width: `${percentage}%`,
                                                        minWidth: count > 0 ? "60px" : "0px",
                                                    }}
                                                >
                                                    <span className={`text-xs font-bold ${colors.text} drop-shadow-sm`}>{count.toLocaleString()}</span>
                                                </div>
                                                {/* Percentage indicator */}
                                                {percentage > 5 && (
                                                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-xs font-medium text-muted-foreground/70">
                                                        {percentage.toFixed(1)}%
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    );
                                })}
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
