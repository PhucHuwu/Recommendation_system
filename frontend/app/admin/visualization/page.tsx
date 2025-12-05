"use client";

import { useState, useEffect } from "react";
import { ChartContainer } from "@/components/admin/chart-container";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BarChart3, TrendingUp, Film, Users } from "lucide-react";
import { api } from "@/lib/api";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from "recharts";

const COLORS = ["#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#ec4899", "#84cc16"];

export default function VisualizationPage() {
    const [loading, setLoading] = useState(true);
    const [visualData, setVisualData] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await api.getVisualizationData();
                setVisualData(response.data);
            } catch (err) {
                console.error("Failed to fetch visualization data:", err);
                setError("Không thể tải dữ liệu visualization. Vui lòng kiểm tra kết nối Backend.");
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="space-y-6 animate-pulse">
                <div className="h-8 bg-muted rounded w-48" />
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {Array.from({ length: 4 }, (_, i) => (
                        <Card key={i}>
                            <CardContent className="p-6">
                                <div className="h-80 bg-muted rounded" />
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="space-y-6">
                <div>
                    <h1 className="text-3xl font-bold">Trực quan hóa dữ liệu</h1>
                    <p className="text-muted-foreground">Phân tích và trực quan hóa dữ liệu hệ thống</p>
                </div>
                <div className="bg-destructive/10 text-destructive px-4 py-3 rounded">{error}</div>
            </div>
        );
    }

    // Transform API data
    const ratingDistribution = (visualData?.rating_distribution || [])
        .map((item: any) => ({
            rating: item._id?.toString() || "0",
            count: item.count || 0,
        }))
        .sort((a: any, b: any) => parseInt(a.rating) - parseInt(b.rating));

    const genreFrequency = (visualData?.genre_frequency || []).slice(0, 10).map((item: any) => ({
        name: item._id || "Unknown",
        count: item.count || 0,
    }));

    const topAnimes = (visualData?.top_rated_animes || []).slice(0, 10).map((item: any) => ({
        name: item.anime_name || `Anime ${item.anime_id}`,
        ratings: item.rating_count || 0,
        score: item.avg_rating || 0,
    }));

    const scoreDistribution = (visualData?.score_distribution || []).map((item: any) => ({
        name: item._id?.toString() || "0",
        value: item.count || 0,
    }));

    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div>
                <h1 className="text-3xl font-bold">Trực quan hóa dữ liệu</h1>
                <p className="text-muted-foreground">Phân tích và trực quan hóa dữ liệu hệ thống</p>
            </div>

            {/* Tabs for different visualizations */}
            <Tabs defaultValue="overview" className="space-y-6">
                <TabsList className="grid w-full max-w-xl grid-cols-3">
                    <TabsTrigger value="overview" className="gap-2">
                        <BarChart3 className="h-4 w-4" />
                        Tổng quan
                    </TabsTrigger>
                    <TabsTrigger value="ratings" className="gap-2">
                        <TrendingUp className="h-4 w-4" />
                        Ratings
                    </TabsTrigger>
                    <TabsTrigger value="animes" className="gap-2">
                        <Film className="h-4 w-4" />
                        Anime
                    </TabsTrigger>
                </TabsList>

                {/* Overview Tab */}
                <TabsContent value="overview" className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Rating Distribution */}
                        <ChartContainer title="Phân bố Rating" description="Số lượng ratings theo điểm (1-10)">
                            <div className="h-80">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={ratingDistribution}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                                        <XAxis dataKey="rating" stroke="hsl(var(--muted-foreground))" tick={{ fill: "hsl(var(--muted-foreground))" }} />
                                        <YAxis
                                            stroke="hsl(var(--muted-foreground))"
                                            tick={{ fill: "hsl(var(--muted-foreground))" }}
                                            tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`}
                                        />
                                        <Tooltip
                                            contentStyle={{
                                                backgroundColor: "hsl(var(--card))",
                                                border: "1px solid hsl(var(--border))",
                                                borderRadius: "8px",
                                                color: "hsl(var(--foreground))",
                                            }}
                                            formatter={(value: number) => [value.toLocaleString(), "Ratings"]}
                                        />
                                        <Bar dataKey="count" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </ChartContainer>

                        {/* Anime Type Distribution */}
                        <ChartContainer title="Phân bố điểm Anime" description="Số lượng anime theo điểm MAL">
                            <div className="h-80">
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie data={scoreDistribution} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value">
                                            {scoreDistribution.map((_: any, index: number) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Tooltip
                                            contentStyle={{
                                                backgroundColor: "hsl(var(--card))",
                                                border: "1px solid hsl(var(--border))",
                                                borderRadius: "8px",
                                                color: "hsl(var(--foreground))",
                                            }}
                                            formatter={(value: number) => [value.toLocaleString() + " anime", "Số lượng"]}
                                        />
                                        <Legend />
                                    </PieChart>
                                </ResponsiveContainer>
                            </div>
                        </ChartContainer>
                    </div>
                </TabsContent>

                {/* Ratings Tab */}
                <TabsContent value="ratings" className="space-y-6">
                    <div className="grid grid-cols-1 gap-6">
                        {/* Rating Distribution Large */}
                        <ChartContainer title="Chi tiết phân bố Rating" description="Số lượng ratings theo điểm từ 1-10">
                            <div className="h-96">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={ratingDistribution}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                                        <XAxis dataKey="rating" stroke="hsl(var(--muted-foreground))" tick={{ fill: "hsl(var(--muted-foreground))" }} />
                                        <YAxis
                                            stroke="hsl(var(--muted-foreground))"
                                            tick={{ fill: "hsl(var(--muted-foreground))" }}
                                            tickFormatter={(value) =>
                                                value >= 1000000 ? `${(value / 1000000).toFixed(1)}M` : value >= 1000 ? `${(value / 1000).toFixed(0)}K` : value
                                            }
                                        />
                                        <Tooltip
                                            contentStyle={{
                                                backgroundColor: "hsl(var(--card))",
                                                border: "1px solid hsl(var(--border))",
                                                borderRadius: "8px",
                                                color: "hsl(var(--foreground))",
                                            }}
                                            formatter={(value: number) => [value.toLocaleString(), "Ratings"]}
                                        />
                                        <Bar dataKey="count" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </ChartContainer>
                    </div>
                </TabsContent>

                {/* Anime Tab */}
                <TabsContent value="animes" className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Genre Frequency */}
                        <ChartContainer title="Tần suất Genres" description="Top 10 thể loại phổ biến nhất">
                            <div className="h-96">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={genreFrequency} layout="vertical">
                                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                                        <XAxis type="number" stroke="hsl(var(--muted-foreground))" tick={{ fill: "hsl(var(--muted-foreground))" }} />
                                        <YAxis
                                            type="category"
                                            dataKey="name"
                                            width={100}
                                            stroke="hsl(var(--muted-foreground))"
                                            tick={{ fill: "hsl(var(--muted-foreground))" }}
                                        />
                                        <Tooltip
                                            contentStyle={{
                                                backgroundColor: "hsl(var(--card))",
                                                border: "1px solid hsl(var(--border))",
                                                borderRadius: "8px",
                                                color: "hsl(var(--foreground))",
                                            }}
                                            formatter={(value: number) => [value.toLocaleString() + " anime", "Số lượng"]}
                                        />
                                        <Bar dataKey="count" fill="hsl(var(--primary))" radius={[0, 4, 4, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </ChartContainer>

                        {/* Top Animes */}
                        <ChartContainer title="Top 10 Anime" description="Anime được đánh giá nhiều nhất">
                            <div className="h-96 overflow-y-auto">
                                <div className="space-y-3">
                                    {topAnimes.map((anime: any, index: number) => (
                                        <div key={anime.name} className="flex items-center gap-3 p-3 rounded-lg bg-secondary/50">
                                            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                                                <span className="text-sm font-bold text-primary">{index + 1}</span>
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <p className="font-medium text-sm truncate">{anime.name}</p>
                                                <p className="text-xs text-muted-foreground">
                                                    {anime.ratings >= 1000000
                                                        ? `${(anime.ratings / 1000000).toFixed(1)}M`
                                                        : anime.ratings >= 1000
                                                        ? `${(anime.ratings / 1000).toFixed(1)}K`
                                                        : anime.ratings}{" "}
                                                    ratings
                                                </p>
                                            </div>
                                            <Badge variant="secondary" className="flex-shrink-0">
                                                {anime.score.toFixed(1)}
                                            </Badge>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </ChartContainer>
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
}
