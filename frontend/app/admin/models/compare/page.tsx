"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ArrowLeft, TrendingUp, TrendingDown } from "lucide-react";
import {
    RadarChart,
    Radar,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
} from "recharts";

const COLORS = {
    user_based_cf: "#a7c7e7",
    item_based_cf: "#bbf7d0",
    hybrid: "#fde68a",
    neural_cf: "#fbb6ce",
};

const PASTEL_COLORS = ["#fecaca", "#fed7aa", "#fde68a", "#d1fae5", "#bbf7d0", "#a7f3d0", "#a7c7e7", "#d8b4fe", "#fbb6ce", "#ddd6fe"];

const customTooltipStyle = {
    backgroundColor: "rgba(17, 24, 39, 0.95)",
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

const getModelDisplayName = (modelName: string): string => {
    const displayNames: Record<string, string> = {
        user_based_cf: "User-Based CF",
        item_based_cf: "Item-Based CF",
        hybrid: "Hybrid",
        neural_cf: "Neural CF",
    };
    return displayNames[modelName] || modelName;
};

export default function ModelsComparePage() {
    const [models, setModels] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchModels = async () => {
            try {
                const response = await fetch("http://localhost:5000/api/admin/models/compare");
                const json = await response.json();
                setModels(json.comparison || []);
            } catch (error) {
                console.error("Failed to fetch comparison:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchModels();
    }, []);

    if (loading) {
        return (
            <div className="space-y-6 animate-pulse">
                <div className="h-8 bg-muted rounded w-48" />
                <Card>
                    <CardContent className="p-6">
                        <div className="h-96 bg-muted rounded" />
                    </CardContent>
                </Card>
            </div>
        );
    }

    // Prepare data for charts
    const metricsData = models
        .filter((m) => m.metrics && Object.keys(m.metrics).length > 0)
        .map((m) => ({
            name: getModelDisplayName(m.name),
            RMSE: m.metrics.rmse || 0,
            MAE: m.metrics.mae || 0,
            "Precision@K": (m.metrics.precision_at_k || 0) * 100,
            "Recall@K": (m.metrics.recall_at_k || 0) * 100,
        }));

    // Radar chart data (normalized)
    const radarData = [
        {
            metric: "RMSE (↓)",
            ...Object.fromEntries(models.map((m) => [m.name, m.metrics?.rmse ? Math.max(0, 100 - m.metrics.rmse * 10) : 0])),
        },
        {
            metric: "MAE (↓)",
            ...Object.fromEntries(models.map((m) => [m.name, m.metrics?.mae ? Math.max(0, 100 - m.metrics.mae * 10) : 0])),
        },
        {
            metric: "Precision@K",
            ...Object.fromEntries(models.map((m) => [m.name, (m.metrics?.precision_at_k || 0) * 100])),
        },
        {
            metric: "Recall@K",
            ...Object.fromEntries(models.map((m) => [m.name, (m.metrics?.recall_at_k || 0) * 100])),
        },
    ];

    // Find best model per metric
    const getBestModel = (metric: string, lowerIsBetter = false) => {
        const validModels = models.filter((m) => m.metrics && m.metrics[metric]);
        if (validModels.length === 0) return null;

        return validModels.reduce((best, current) => {
            const currentValue = current.metrics[metric];
            const bestValue = best.metrics[metric];
            if (lowerIsBetter) {
                return currentValue < bestValue ? current : best;
            } else {
                return currentValue > bestValue ? current : best;
            }
        });
    };

    const bestRMSE = getBestModel("rmse", true);
    const bestMAE = getBestModel("mae", true);
    const bestPrecision = getBestModel("precision_at_k");
    const bestRecall = getBestModel("recall_at_k");
    const bestCoverage = getBestModel("coverage");
    const bestDiversity = getBestModel("diversity");
    const bestNovelty = getBestModel("novelty");

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">So sánh Models</h1>
                    <p className="text-muted-foreground">Phân tích hiệu suất các model recommendation</p>
                </div>
                <Button variant="outline" asChild>
                    <Link href="/admin/models">
                        <ArrowLeft className="h-4 w-4 mr-2" />
                        Quay lại
                    </Link>
                </Button>
            </div>

            {/* Metrics Comparison Table */}
            <Card>
                <CardHeader>
                    <CardTitle>Bảng so sánh Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Model</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead className="text-right">RMSE ↓</TableHead>
                                <TableHead className="text-right">MAE ↓</TableHead>
                                <TableHead className="text-right">Precision@K ↑</TableHead>
                                <TableHead className="text-right">Recall@K ↑</TableHead>
                                <TableHead className="text-right">Coverage ↑</TableHead>
                                <TableHead className="text-right">Diversity ↑</TableHead>
                                <TableHead className="text-right">Novelty ↑</TableHead>
                                <TableHead>Trained At</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {models.map((model) => (
                                <TableRow key={model.name}>
                                    <TableCell className="font-medium">{getModelDisplayName(model.name)}</TableCell>
                                    <TableCell>
                                        {model.is_active ? <Badge className="bg-success">Active</Badge> : <Badge variant="secondary">Inactive</Badge>}
                                    </TableCell>
                                    <TableCell className="text-right font-mono">
                                        {model.metrics?.rmse ? (
                                            <div className="flex items-center justify-end gap-2">
                                                <span>{model.metrics.rmse.toFixed(4)}</span>
                                                {bestRMSE?.name === model.name && <TrendingDown className="h-4 w-4 text-success" />}
                                            </div>
                                        ) : (
                                            "-"
                                        )}
                                    </TableCell>
                                    <TableCell className="text-right font-mono">
                                        {model.metrics?.mae ? (
                                            <div className="flex items-center justify-end gap-2">
                                                <span>{model.metrics.mae.toFixed(4)}</span>
                                                {bestMAE?.name === model.name && <TrendingDown className="h-4 w-4 text-success" />}
                                            </div>
                                        ) : (
                                            "-"
                                        )}
                                    </TableCell>
                                    <TableCell className="text-right font-mono">
                                        {model.metrics?.precision_at_k ? (
                                            <div className="flex items-center justify-end gap-2">
                                                <span>{(model.metrics.precision_at_k * 100).toFixed(2)}%</span>
                                                {bestPrecision?.name === model.name && <TrendingUp className="h-4 w-4 text-success" />}
                                            </div>
                                        ) : (
                                            "-"
                                        )}
                                    </TableCell>
                                    <TableCell className="text-right font-mono">
                                        {model.metrics?.recall_at_k ? (
                                            <div className="flex items-center justify-end gap-2">
                                                <span>{(model.metrics.recall_at_k * 100).toFixed(2)}%</span>
                                                {bestRecall?.name === model.name && <TrendingUp className="h-4 w-4 text-success" />}
                                            </div>
                                        ) : (
                                            "-"
                                        )}
                                    </TableCell>
                                    <TableCell className="text-right font-mono">
                                        {model.metrics?.coverage ? (
                                            <div className="flex items-center justify-end gap-2">
                                                <span>{(model.metrics.coverage * 100).toFixed(2)}%</span>
                                                {bestCoverage?.name === model.name && <TrendingUp className="h-4 w-4 text-success" />}
                                            </div>
                                        ) : (
                                            "-"
                                        )}
                                    </TableCell>
                                    <TableCell className="text-right font-mono">
                                        {model.metrics?.diversity ? (
                                            <div className="flex items-center justify-end gap-2">
                                                <span>{model.metrics.diversity.toFixed(4)}</span>
                                                {bestDiversity?.name === model.name && <TrendingUp className="h-4 w-4 text-success" />}
                                            </div>
                                        ) : (
                                            "-"
                                        )}
                                    </TableCell>
                                    <TableCell className="text-right font-mono">
                                        {model.metrics?.novelty ? (
                                            <div className="flex items-center justify-end gap-2">
                                                <span>{model.metrics.novelty.toFixed(2)}</span>
                                                {bestNovelty?.name === model.name && <TrendingUp className="h-4 w-4 text-success" />}
                                            </div>
                                        ) : (
                                            "-"
                                        )}
                                    </TableCell>
                                    <TableCell className="text-sm text-muted-foreground">
                                        {model.trained_at ? new Date(model.trained_at).toLocaleDateString() : "Not trained"}
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Radar Chart */}
                <Card>
                    <CardHeader>
                        <CardTitle>So sánh đa chiều (Radar)</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-96">
                            <ResponsiveContainer width="100%" height="100%">
                                <RadarChart data={radarData}>
                                    <defs>
                                        {models.map((model, index) => (
                                            <linearGradient key={`radarGradient${index}`} id={`radarGradient${index}`} x1="0" y1="0" x2="1" y2="1">
                                                <stop
                                                    offset="0%"
                                                    stopColor={COLORS[model.name as keyof typeof COLORS] || PASTEL_COLORS[index % PASTEL_COLORS.length]}
                                                    stopOpacity={0.8}
                                                />
                                                <stop
                                                    offset="100%"
                                                    stopColor={COLORS[model.name as keyof typeof COLORS] || PASTEL_COLORS[index % PASTEL_COLORS.length]}
                                                    stopOpacity={0.1}
                                                />
                                            </linearGradient>
                                        ))}
                                    </defs>
                                    <PolarGrid stroke="hsl(var(--border))" strokeOpacity={0.3} />
                                    <PolarAngleAxis dataKey="metric" tick={{ fill: "#e5e7eb", fontSize: 12 }} />
                                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: "#e5e7eb", fontSize: 10 }} />
                                    {models.map((model, index) => (
                                        <Radar
                                            key={model.name}
                                            name={getModelDisplayName(model.name)}
                                            dataKey={model.name}
                                            stroke={COLORS[model.name as keyof typeof COLORS] || PASTEL_COLORS[index % PASTEL_COLORS.length]}
                                            fill={`url(#radarGradient${index})`}
                                            fillOpacity={0.4}
                                            strokeWidth={2}
                                        />
                                    ))}
                                    <Legend wrapperStyle={{ paddingTop: "20px" }} />
                                    <Tooltip
                                        contentStyle={{
                                            ...customTooltipStyle,
                                            background: "linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(31, 41, 55, 0.95) 100%)",
                                        }}
                                        itemStyle={customTooltipContent}
                                    />
                                </RadarChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>

                {/* Bar Chart - RMSE & MAE */}
                <Card>
                    <CardHeader>
                        <CardTitle>RMSE & MAE Comparison</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-96">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={metricsData}>
                                    <defs>
                                        <linearGradient id="colorRMSE" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="#a7c7e7" stopOpacity={0.9} />
                                            <stop offset="70%" stopColor="#a7c7e7" stopOpacity={0.7} />
                                            <stop offset="100%" stopColor="#a7c7e7" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="colorMAE" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="#d8b4fe" stopOpacity={0.9} />
                                            <stop offset="70%" stopColor="#d8b4fe" stopOpacity={0.7} />
                                            <stop offset="100%" stopColor="#d8b4fe" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" strokeOpacity={0.3} />
                                    <XAxis dataKey="name" stroke="#9ca3af" tick={{ fill: "#e5e7eb", fontSize: 12 }} />
                                    <YAxis stroke="#9ca3af" tick={{ fill: "#e5e7eb" }} />
                                    <Tooltip
                                        contentStyle={{
                                            ...customTooltipStyle,
                                            background: "linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(31, 41, 55, 0.95) 100%)",
                                        }}
                                        itemStyle={customTooltipContent}
                                    />
                                    <Legend wrapperStyle={{ paddingTop: "20px" }} />
                                    <Bar dataKey="RMSE" fill="url(#colorRMSE)" radius={[4, 4, 0, 0]} />
                                    <Bar dataKey="MAE" fill="url(#colorMAE)" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>

                {/* Bar Chart - Precision & Recall */}
                <Card>
                    <CardHeader>
                        <CardTitle>Precision@K & Recall@K (%)</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-96">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={metricsData}>
                                    <defs>
                                        <linearGradient id="colorPrecision" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="#bbf7d0" stopOpacity={0.9} />
                                            <stop offset="70%" stopColor="#bbf7d0" stopOpacity={0.7} />
                                            <stop offset="100%" stopColor="#bbf7d0" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="colorRecall" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="#fbb6ce" stopOpacity={0.9} />
                                            <stop offset="70%" stopColor="#fbb6ce" stopOpacity={0.7} />
                                            <stop offset="100%" stopColor="#fbb6ce" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" strokeOpacity={0.3} />
                                    <XAxis dataKey="name" stroke="#9ca3af" tick={{ fill: "#e5e7eb", fontSize: 12 }} />
                                    <YAxis stroke="#9ca3af" tick={{ fill: "#e5e7eb" }} />
                                    <Tooltip
                                        contentStyle={{
                                            ...customTooltipStyle,
                                            background: "linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(31, 41, 55, 0.95) 100%)",
                                        }}
                                        itemStyle={customTooltipContent}
                                    />
                                    <Legend wrapperStyle={{ paddingTop: "20px" }} />
                                    <Bar dataKey="Precision@K" fill="url(#colorPrecision)" radius={[4, 4, 0, 0]} />
                                    <Bar dataKey="Recall@K" fill="url(#colorRecall)" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>

                {/* Summary Card */}
                <Card>
                    <CardHeader>
                        <CardTitle>Tổng kết so sánh</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <p className="text-sm text-muted-foreground mb-2">Best RMSE (Lower is better)</p>
                            <div className="flex items-center gap-2">
                                <Badge className="bg-success">{bestRMSE?.name || "N/A"}</Badge>
                                <span className="font-mono">{bestRMSE?.metrics?.rmse?.toFixed(4) || "-"}</span>
                            </div>
                        </div>
                        <div>
                            <p className="text-sm text-muted-foreground mb-2">Best MAE (Lower is better)</p>
                            <div className="flex items-center gap-2">
                                <Badge className="bg-success">{bestMAE?.name || "N/A"}</Badge>
                                <span className="font-mono">{bestMAE?.metrics?.mae?.toFixed(4) || "-"}</span>
                            </div>
                        </div>
                        <div>
                            <p className="text-sm text-muted-foreground mb-2">Best Precision@K</p>
                            <div className="flex items-center gap-2">
                                <Badge className="bg-success">{bestPrecision?.name || "N/A"}</Badge>
                                <span className="font-mono">
                                    {bestPrecision?.metrics?.precision_at_k ? `${(bestPrecision.metrics.precision_at_k * 100).toFixed(2)}%` : "-"}
                                </span>
                            </div>
                        </div>
                        <div>
                            <p className="text-sm text-muted-foreground mb-2">Best Recall@K</p>
                            <div className="flex items-center gap-2">
                                <Badge className="bg-success">{bestRecall?.name || "N/A"}</Badge>
                                <span className="font-mono">
                                    {bestRecall?.metrics?.recall_at_k ? `${(bestRecall.metrics.recall_at_k * 100).toFixed(2)}%` : "-"}
                                </span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
