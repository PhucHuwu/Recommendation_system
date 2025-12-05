"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
    BarChart,
    Bar,
    PieChart,
    Pie,
    AreaChart,
    Area,
    ScatterChart,
    Scatter,
    RadarChart,
    Radar,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    Cell,
} from "recharts";
import { api } from "@/lib/api";

const COLORS = ["#6366f1", "#8b5cf6", "#ec4899", "#f59e0b", "#10b981", "#06b6d4", "#ef4444", "#84cc16"];

const customTooltipStyle = {
    backgroundColor: "rgba(17, 24, 39, 0.95)", // dark bg với transparency
    border: "1px solid rgba(99, 102, 241, 0.3)",
    borderRadius: "8px",
    padding: "12px",
    boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)",
    backdropFilter: "blur(8px)",
};

const customTooltipContent = {
    color: "#e5e7eb",
    fontSize: "13px",
    fontWeight: 500,
};

export default function VisualizationPage() {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch("http://localhost:5000/api/admin/visualization");
                const json = await response.json();
                setData(json.data);
            } catch (error) {
                console.error("Failed to fetch visualization data:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    // Format large numbers: 1000 -> 1K, 1000000 -> 1M
    const formatNumber = (value: number) => {
        if (value >= 1000000) {
            return `${(value / 1000000).toFixed(1)}M`;
        } else if (value >= 1000) {
            return `${(value / 1000).toFixed(1)}K`;
        }
        return value.toString();
    };

    if (loading) {
        return (
            <div className="space-y-6">
                <h1 className="text-3xl font-bold">Trực quan hóa dữ liệu</h1>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {[1, 2, 3, 4].map((i) => (
                        <Card key={i}>
                            <CardContent className="p-6">
                                <div className="h-80 animate-pulse bg-muted rounded" />
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
                <h1 className="text-3xl font-bold">Trực quan hóa dữ liệu</h1>
                <p className="text-muted-foreground">Phân tích toàn diện về hệ thống gợi ý anime</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* 1. Rating Distribution - Histogram */}
                <Card>
                    <CardHeader>
                        <CardTitle>Phân bố Rating (1-10)</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-80">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={data?.rating_distribution || []}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                                    <XAxis
                                        dataKey="_id"
                                        stroke="#9ca3af"
                                        tick={{ fill: "#e5e7eb" }}
                                        label={{ value: "Rating", position: "insideBottom", offset: -5, fill: "#e5e7eb" }}
                                    />
                                    <YAxis
                                        stroke="#9ca3af"
                                        tick={{ fill: "#e5e7eb", fontSize: 11 }}
                                        tickFormatter={formatNumber}
                                        label={{
                                            value: "Số lượng",
                                            angle: -90,
                                            position: "insideLeft",
                                            style: { textAnchor: "middle", fill: "#e5e7eb" },
                                        }}
                                        width={60}
                                    />
                                    <Tooltip contentStyle={customTooltipStyle} itemStyle={customTooltipContent} />
                                    <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>

                {/* 2. Top Rated Animes - Bar Chart */}
                <Card>
                    <CardHeader>
                        <CardTitle>Top 10 Anime được đánh giá nhiều nhất</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-80">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart layout="vertical" data={data?.top_rated_animes || []}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                                    <XAxis type="number" stroke="#9ca3af" tick={{ fill: "#e5e7eb" }} tickFormatter={formatNumber} />
                                    <YAxis type="category" dataKey="anime_name" width={150} stroke="#9ca3af" tick={{ fill: "#e5e7eb", fontSize: 11 }} />
                                    <Tooltip contentStyle={customTooltipStyle} itemStyle={customTooltipContent} />
                                    <Bar dataKey="rating_count" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>

                {/* 3. Genre Frequency - Horizontal Bar */}
                <Card>
                    <CardHeader>
                        <CardTitle>Tần suất thể loại (Top 15)</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-80">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart layout="vertical" data={data?.genre_frequency || []}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                                    <XAxis type="number" stroke="#9ca3af" tick={{ fill: "#e5e7eb" }} tickFormatter={formatNumber} />
                                    <YAxis type="category" dataKey="_id" width={100} stroke="#9ca3af" tick={{ fill: "#e5e7eb", fontSize: 12 }} />
                                    <Tooltip contentStyle={customTooltipStyle} itemStyle={customTooltipContent} />
                                    <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                                        {(data?.genre_frequency || []).map((entry: any, index: number) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>

                {/* 4. Primary Genre Distribution - Pie Chart */}
                <Card>
                    <CardHeader>
                        <CardTitle>Phân bố thể loại chính</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-80">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={data?.anime_type_distribution || []}
                                        cx="50%"
                                        cy="50%"
                                        labelLine={{ stroke: "#fff", strokeWidth: 1 }}
                                        label={(props: any) => {
                                            const RADIAN = Math.PI / 180;
                                            const { cx, cy, midAngle, outerRadius, fill, payload, percent } = props;
                                            const sin = Math.sin(-RADIAN * midAngle);
                                            const cos = Math.cos(-RADIAN * midAngle);
                                            const sx = cx + (outerRadius + 10) * cos;
                                            const sy = cy + (outerRadius + 10) * sin;
                                            const mx = cx + (outerRadius + 25) * cos;
                                            const my = cy + (outerRadius + 25) * sin;
                                            const ex = mx + (cos >= 0 ? 1 : -1) * 22;
                                            const ey = my;
                                            const textAnchor = cos >= 0 ? "start" : "end";

                                            return (
                                                <text x={ex} y={ey} textAnchor={textAnchor} fill="#fff" fontSize={13} fontWeight={600}>
                                                    {`${payload._id}: ${(percent * 100).toFixed(0)}%`}
                                                </text>
                                            );
                                        }}
                                        outerRadius={100}
                                        fill="#8884d8"
                                        dataKey="count"
                                        nameKey="_id"
                                    >
                                        {(data?.anime_type_distribution || []).map((entry: any, index: number) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip contentStyle={customTooltipStyle} itemStyle={customTooltipContent} />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>

                {/* 5. Rating Categories - Donut Chart */}
                <Card>
                    <CardHeader>
                        <CardTitle>Phân loại Rating</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-80">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={data?.rating_categories || []}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={100}
                                        fill="#8884d8"
                                        paddingAngle={5}
                                        dataKey="count"
                                        nameKey="category"
                                        labelLine={{ stroke: "#fff", strokeWidth: 1 }}
                                        label={(props: any) => {
                                            const RADIAN = Math.PI / 180;
                                            const { cx, cy, midAngle, outerRadius, payload, percent } = props;
                                            const sin = Math.sin(-RADIAN * midAngle);
                                            const cos = Math.cos(-RADIAN * midAngle);
                                            const sx = cx + (outerRadius + 10) * cos;
                                            const sy = cy + (outerRadius + 10) * sin;
                                            const mx = cx + (outerRadius + 25) * cos;
                                            const my = cy + (outerRadius + 25) * sin;
                                            const ex = mx + (cos >= 0 ? 1 : -1) * 22;
                                            const ey = my;
                                            const textAnchor = cos >= 0 ? "start" : "end";

                                            return (
                                                <text x={ex} y={ey} textAnchor={textAnchor} fill="#fff" fontSize={13} fontWeight={600}>
                                                    {`${payload.category}: ${(percent * 100).toFixed(0)}%`}
                                                </text>
                                            );
                                        }}
                                    >
                                        <Cell fill="#ef4444" />
                                        <Cell fill="#f59e0b" />
                                        <Cell fill="#10b981" />
                                    </Pie>
                                    <Tooltip contentStyle={customTooltipStyle} itemStyle={customTooltipContent} />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>

                {/* 6. Score Distribution - Area Chart */}
                <Card>
                    <CardHeader>
                        <CardTitle>Phân bố điểm số Anime</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-80">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={data?.score_distribution || []}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                                    <XAxis dataKey="_id" stroke="#9ca3af" tick={{ fill: "#e5e7eb" }} />
                                    <YAxis stroke="#9ca3af" tick={{ fill: "#e5e7eb" }} />
                                    <Tooltip contentStyle={customTooltipStyle} itemStyle={customTooltipContent} />
                                    <Area type="monotone" dataKey="count" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.6} />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>

                {/* 7. Score vs Rating Count Scatter */}
                <Card>
                    <CardHeader>
                        <CardTitle>Điểm số vs Số lượng đánh giá</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-80">
                            <ResponsiveContainer width="100%" height="100%">
                                <ScatterChart>
                                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                                    <XAxis
                                        type="number"
                                        dataKey="rating_count"
                                        name="Rating Count"
                                        stroke="#9ca3af"
                                        tick={{ fill: "#e5e7eb" }}
                                        label={{ value: "Số đánh giá", position: "insideBottom", offset: -5, fill: "#e5e7eb" }}
                                    />
                                    <YAxis
                                        type="number"
                                        dataKey="score"
                                        name="Score"
                                        stroke="#9ca3af"
                                        tick={{ fill: "#e5e7eb" }}
                                        label={{ value: "Điểm", angle: -90, position: "insideLeft", fill: "#e5e7eb" }}
                                    />
                                    <Tooltip cursor={{ strokeDasharray: "3 3" }} contentStyle={customTooltipStyle} itemStyle={customTooltipContent} />
                                    <Scatter data={data?.episode_rating_scatter || []} fill="#ec4899" />
                                </ScatterChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>

                {/* 8. Top Anime Radar Chart */}
                <Card>
                    <CardHeader>
                        <CardTitle>Top 5 Anime - So sánh đa chiều</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-80">
                            <ResponsiveContainer width="100%" height="100%">
                                <RadarChart data={data?.top_anime_radar || []}>
                                    <PolarGrid stroke="hsl(var(--border))" />
                                    <PolarAngleAxis dataKey="name" tick={{ fill: "#e5e7eb", fontSize: 10 }} />
                                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: "#e5e7eb" }} />
                                    <Radar name="Score" dataKey="score" stroke="#6366f1" fill="#6366f1" fillOpacity={0.5} />
                                    <Radar name="Popularity" dataKey="popularity" stroke="#10b981" fill="#10b981" fillOpacity={0.5} />
                                    <Legend />
                                    <Tooltip contentStyle={customTooltipStyle} itemStyle={customTooltipContent} />
                                </RadarChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>

                {/* 9. User Engagement Funnel  */}
                <Card>
                    <CardHeader>
                        <CardTitle>Phễu tương tác người dùng</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-80">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={data?.user_engagement_funnel || []}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                                    <XAxis dataKey="stage" stroke="#9ca3af" tick={{ fill: "#e5e7eb", fontSize: 11 }} />
                                    <YAxis stroke="#9ca3af" tick={{ fill: "#e5e7eb" }} />
                                    <Tooltip contentStyle={customTooltipStyle} itemStyle={customTooltipContent} />
                                    <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                                        <Cell fill="#6366f1" />
                                        <Cell fill="#8b5cf6" />
                                        <Cell fill="#ec4899" />
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>

                {/* 10. Genre Co-occurrence Heatmap (Custom) */}
                <Card className="lg:col-span-2">
                    <CardHeader>
                        <CardTitle>Ma trận đồng xuất hiện thể loại</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="overflow-x-auto">
                            <table className="w-full border-collapse">
                                <thead>
                                    <tr>
                                        <th className="border p-2 bg-muted"></th>
                                        {data?.genre_frequency?.slice(0, 10).map((g: any) => (
                                            <th key={g._id} className="border p-2 bg-muted text-xs">
                                                {g._id}
                                            </th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {data?.genre_frequency?.slice(0, 10).map((g1: any) => (
                                        <tr key={g1._id}>
                                            <td className="border p-2 bg-muted font-semibold text-xs">{g1._id}</td>
                                            {data.genre_frequency.slice(0, 10).map((g2: any) => {
                                                const value = data.genre_cooccurrence?.[g1._id]?.[g2._id] || 0;
                                                const maxValue = 1000; // Adjust based on data
                                                const intensity = Math.min(value / maxValue, 1);
                                                return (
                                                    <td
                                                        key={g2._id}
                                                        className="border p-2 text-center text-xs"
                                                        style={{
                                                            backgroundColor: `rgba(99, 102, 241, ${intensity})`,
                                                            color: intensity > 0.5 ? "white" : "inherit",
                                                        }}
                                                    >
                                                        {value}
                                                    </td>
                                                );
                                            })}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
