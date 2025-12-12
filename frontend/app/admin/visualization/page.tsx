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

const COLORS = ["#a7c7e7", "#d8b4fe", "#fbb6ce", "#fed7aa", "#bbf7d0", "#fde68a", "#fecaca", "#ddd6fe"];

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
                {/* 1. Rating Distribution - Enhanced Histogram */}
                <Card>
                    <CardHeader>
                        <CardTitle>Phân bố Rating (1-10)</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-80">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={data?.rating_distribution || []}>
                                    <defs>
                                        {/* Gradient definitions for each rating with pastel colors */}
                                        <linearGradient id="colorRating1" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="#fecaca" stopOpacity={0.9} />
                                            <stop offset="100%" stopColor="#fecaca" stopOpacity={0.6} />
                                        </linearGradient>
                                        <linearGradient id="colorRating2" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="#fed7aa" stopOpacity={0.9} />
                                            <stop offset="100%" stopColor="#fed7aa" stopOpacity={0.6} />
                                        </linearGradient>
                                        <linearGradient id="colorRating3" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="#fde68a" stopOpacity={0.9} />
                                            <stop offset="100%" stopColor="#fde68a" stopOpacity={0.6} />
                                        </linearGradient>
                                        <linearGradient id="colorRating4" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="#fef3c7" stopOpacity={0.9} />
                                            <stop offset="100%" stopColor="#fef3c7" stopOpacity={0.6} />
                                        </linearGradient>
                                        <linearGradient id="colorRating5" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="#d1fae5" stopOpacity={0.9} />
                                            <stop offset="100%" stopColor="#d1fae5" stopOpacity={0.6} />
                                        </linearGradient>
                                        <linearGradient id="colorRating6" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="#bbf7d0" stopOpacity={0.9} />
                                            <stop offset="100%" stopColor="#bbf7d0" stopOpacity={0.6} />
                                        </linearGradient>
                                        <linearGradient id="colorRating7" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="#a7f3d0" stopOpacity={0.9} />
                                            <stop offset="100%" stopColor="#a7f3d0" stopOpacity={0.6} />
                                        </linearGradient>
                                        <linearGradient id="colorRating8" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="#b6d7ff" stopOpacity={0.9} />
                                            <stop offset="100%" stopColor="#b6d7ff" stopOpacity={0.6} />
                                        </linearGradient>
                                        <linearGradient id="colorRating9" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="#a7c7e7" stopOpacity={0.9} />
                                            <stop offset="100%" stopColor="#a7c7e7" stopOpacity={0.6} />
                                        </linearGradient>
                                        <linearGradient id="colorRating10" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="#d8b4fe" stopOpacity={0.9} />
                                            <stop offset="100%" stopColor="#d8b4fe" stopOpacity={0.6} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                                    <XAxis
                                        dataKey="_id"
                                        stroke="#9ca3af"
                                        tick={{ fill: "#e5e7eb", fontSize: 13, fontWeight: 600 }}
                                        label={{ value: "Rating", position: "insideBottom", offset: -5, fill: "#e5e7eb", fontSize: 14 }}
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
                                    <Tooltip
                                        contentStyle={customTooltipStyle}
                                        itemStyle={customTooltipContent}
                                        formatter={(value: any) => [formatNumber(value), "Số đánh giá"]}
                                        labelFormatter={(label) => `Rating ${label}`}
                                    />
                                    <Bar dataKey="count" radius={[8, 8, 0, 0]} animationDuration={1000} animationBegin={0}>
                                        {(data?.rating_distribution || []).map((entry: any, index: number) => (
                                            <Cell key={`cell-${index}`} fill={`url(#colorRating${entry._id})`} stroke="#fff" strokeWidth={0} />
                                        ))}
                                    </Bar>
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
                                    <defs>
                                        <linearGradient id="colorTopRated" x1="0" y1="0" x2="1" y2="0">
                                            <stop offset="0%" stopColor="#d8b4fe" stopOpacity={0.9} />
                                            <stop offset="50%" stopColor="#c4b5fd" stopOpacity={1} />
                                            <stop offset="100%" stopColor="#a78bfa" stopOpacity={0.8} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                                    <XAxis type="number" stroke="#9ca3af" tick={{ fill: "#e5e7eb" }} tickFormatter={formatNumber} />
                                    <YAxis type="category" dataKey="anime_name" width={150} stroke="#9ca3af" tick={{ fill: "#e5e7eb", fontSize: 11 }} />
                                    <Tooltip contentStyle={customTooltipStyle} itemStyle={customTooltipContent} />
                                    <Bar dataKey="rating_count" fill="url(#colorTopRated)" radius={[0, 4, 4, 0]} />
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
                                    <defs>
                                        <linearGradient id="colorGenre0" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stopColor="#a7c7e7" stopOpacity={0.9} /><stop offset="100%" stopColor="#a7c7e7" stopOpacity={0.7} /></linearGradient>
                                        <linearGradient id="colorGenre1" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stopColor="#d8b4fe" stopOpacity={0.9} /><stop offset="100%" stopColor="#d8b4fe" stopOpacity={0.7} /></linearGradient>
                                        <linearGradient id="colorGenre2" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stopColor="#fbb6ce" stopOpacity={0.9} /><stop offset="100%" stopColor="#fbb6ce" stopOpacity={0.7} /></linearGradient>
                                        <linearGradient id="colorGenre3" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stopColor="#fed7aa" stopOpacity={0.9} /><stop offset="100%" stopColor="#fed7aa" stopOpacity={0.7} /></linearGradient>
                                        <linearGradient id="colorGenre4" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stopColor="#bbf7d0" stopOpacity={0.9} /><stop offset="100%" stopColor="#bbf7d0" stopOpacity={0.7} /></linearGradient>
                                        <linearGradient id="colorGenre5" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stopColor="#fde68a" stopOpacity={0.9} /><stop offset="100%" stopColor="#fde68a" stopOpacity={0.7} /></linearGradient>
                                        <linearGradient id="colorGenre6" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stopColor="#fecaca" stopOpacity={0.9} /><stop offset="100%" stopColor="#fecaca" stopOpacity={0.7} /></linearGradient>
                                        <linearGradient id="colorGenre7" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stopColor="#ddd6fe" stopOpacity={0.9} /><stop offset="100%" stopColor="#ddd6fe" stopOpacity={0.7} /></linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                                    <XAxis type="number" stroke="#9ca3af" tick={{ fill: "#e5e7eb" }} tickFormatter={formatNumber} />
                                    <YAxis type="category" dataKey="_id" width={100} stroke="#9ca3af" tick={{ fill: "#e5e7eb", fontSize: 12 }} />
                                    <Tooltip contentStyle={customTooltipStyle} itemStyle={customTooltipContent} />
                                    <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                                        {(data?.genre_frequency || []).map((entry: any, index: number) => (
                                            <Cell key={`cell-${index}`} fill={`url(#colorGenre${index % 8})`} />
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
                                        <Cell fill="#fbb6ce" />
                                        <Cell fill="#fed7aa" />
                                        <Cell fill="#bbf7d0" />
                                    </Pie>
                                    <Tooltip contentStyle={customTooltipStyle} itemStyle={customTooltipContent} />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>

                {/* 6. Score vs Rating Count Scatter */}
                <Card>
                    <CardHeader>
                        <CardTitle>Điểm số vs Số lượng đánh giá</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-80">
                            <ResponsiveContainer width="100%" height="100%">
                                <ScatterChart>
                                    <defs>
                                        <radialGradient id="colorScatter">
                                            <stop offset="0%" stopColor="#fbb6ce" stopOpacity={0.9} />
                                            <stop offset="50%" stopColor="#f9a8d4" stopOpacity={0.8} />
                                            <stop offset="100%" stopColor="#d8b4fe" stopOpacity={1} />
                                        </radialGradient>
                                    </defs>
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
                                    <Scatter data={data?.episode_rating_scatter || []} fill="url(#colorScatter)" />
                                </ScatterChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>

                {/* 7. Genre Co-occurrence Heatmap (Custom) */}
                <Card className="lg:col-span-2">
                    <CardHeader>
                        <CardTitle>Ma trận đồng xuất hiện thể loại</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="overflow-x-auto">
                            <table className="w-full rounded-lg overflow-hidden shadow-sm" style={{borderSpacing: '4px', borderCollapse: 'separate'}}>
                                <thead>
                                    <tr>
                                        <th className="p-3 bg-slate-800 text-slate-300 font-medium rounded-lg"></th>
                                        {data?.genre_frequency?.slice(0, 10).map((g: any) => (
                                            <th key={g._id} className="p-3 bg-slate-800 text-xs font-medium text-slate-300 min-w-16 rounded-lg">
                                                {g._id}
                                            </th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {data?.genre_frequency?.slice(0, 10).map((g1: any) => (
                                        <tr key={g1._id}>
                                            <td className="p-3 bg-slate-800 font-semibold text-xs text-slate-300 min-w-20 rounded-lg">{g1._id}</td>
                                            {data.genre_frequency.slice(0, 10).map((g2: any) => {
                                                const value = data.genre_cooccurrence?.[g1._id]?.[g2._id] || 0;
                                                const maxValue = 1000; // Adjust based on data
                                                const intensity = Math.min(value / maxValue, 1);
                                                
                                                // Use pastel purple gradient suitable for dark theme
                                                const backgroundColor = intensity === 0 
                                                    ? 'rgba(30, 41, 59, 0.3)' // Dark slate for 0 values
                                                    : `rgba(216, 180, 254, ${0.15 + intensity * 0.6})`; // Pastel purple with varying opacity for dark theme
                                                
                                                const textColor = intensity > 0.4 ? '#f1f5f9' : intensity > 0.2 ? '#d8b4fe' : '#94a3b8';
                                                
                                                return (
                                                    <td
                                                        key={g2._id}
                                                        className="p-3 text-center text-xs font-medium transition-all hover:brightness-110 rounded-lg"
                                                        style={{
                                                            backgroundColor,
                                                            color: textColor,
                                                            boxShadow: intensity > 0.5 ? '0 1px 4px rgba(216, 180, 254, 0.3)' : '0 1px 2px rgba(0, 0, 0, 0.1)'
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
