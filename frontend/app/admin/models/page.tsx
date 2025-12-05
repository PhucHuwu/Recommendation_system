"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Brain, CheckCircle2, Zap, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";

export default function ModelsPage() {
    const [models, setModels] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [activating, setActivating] = useState(false);
    const [message, setMessage] = useState("");

    useEffect(() => {
        fetchModels();
    }, []);

    const fetchModels = async () => {
        setLoading(true);
        try {
            const response = await api.getModels();
            setModels(response.models || []);
        } catch (error) {
            console.error("Failed to fetch models:", error);
        } finally {
            setLoading(false);
        }
    };

    const activeModel = models.find((m) => m.is_active);

    const handleActivateModel = async (modelName: string) => {
        setActivating(true);
        setMessage("");
        try {
            await api.selectModel(modelName);
            setMessage(`Model ${modelName} đã được kích hoạt thành công!`);
            await fetchModels();
        } catch (error) {
            console.error("Failed to activate model:", error);
            setMessage("Lỗi khi kích hoạt model");
        } finally {
            setActivating(false);
        }
    };

    if (loading) {
        return (
            <div className="space-y-6 animate-pulse">
                <div className="h-8 bg-muted rounded w-48" />
                <Card>
                    <CardContent className="p-6">
                        <div className="h-64 bg-muted rounded" />
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Quản lý Models</h1>
                    <p className="text-muted-foreground">Quản lý và so sánh các model recommendation</p>
                </div>
                <Button asChild>
                    <Link href="/admin/models/compare">So sánh Models</Link>
                </Button>
            </div>

            {/* Success Message */}
            {message && (
                <Alert>
                    <CheckCircle2 className="h-4 w-4" />
                    <AlertDescription>{message}</AlertDescription>
                </Alert>
            )}

            {/* Active Model Info */}
            {activeModel && (
                <Alert className="bg-primary/10 border-primary/20">
                    <CheckCircle2 className="h-4 w-4 text-primary" />
                    <AlertDescription className="flex items-center justify-between">
                        <span>
                            Model đang active: <strong>{activeModel.display_name || activeModel.name}</strong>
                        </span>
                        {activeModel.metrics?.rmse && (
                            <Badge variant="default" className="bg-primary">
                                RMSE: {activeModel.metrics.rmse.toFixed(4)}
                            </Badge>
                        )}
                    </AlertDescription>
                </Alert>
            )}

            {/* Models Table */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Brain className="h-5 w-5" />
                        Danh sách Models
                    </CardTitle>
                    <CardDescription>Tất cả các model đã được train trong hệ thống</CardDescription>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Model</TableHead>
                                <TableHead>Tên hiển thị</TableHead>
                                <TableHead className="text-right">RMSE</TableHead>
                                <TableHead className="text-right">MAE</TableHead>
                                <TableHead className="text-right">Precision@K</TableHead>
                                <TableHead className="text-right">Recall@K</TableHead>
                                <TableHead>Training Status</TableHead>
                                <TableHead>Trạng thái</TableHead>
                                <TableHead className="text-right">Hành động</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {models.map((model) => (
                                <TableRow key={model.name}>
                                    <TableCell className="font-medium font-mono">{model.name}</TableCell>
                                    <TableCell>{model.display_name || model.name}</TableCell>
                                    <TableCell className="text-right font-mono">{model.metrics?.rmse ? model.metrics.rmse.toFixed(4) : "-"}</TableCell>
                                    <TableCell className="text-right font-mono">{model.metrics?.mae ? model.metrics.mae.toFixed(4) : "-"}</TableCell>
                                    <TableCell className="text-right font-mono">
                                        {model.metrics?.precision_at_k ? model.metrics.precision_at_k.toFixed(4) : "-"}
                                    </TableCell>
                                    <TableCell className="text-right font-mono">
                                        {model.metrics?.recall_at_k ? model.metrics.recall_at_k.toFixed(4) : "-"}
                                    </TableCell>
                                    <TableCell>
                                        <Badge variant={model.status === "trained" ? "default" : "secondary"}>{model.status || "not_trained"}</Badge>
                                    </TableCell>
                                    <TableCell>
                                        {model.is_active ? <Badge className="bg-success">Active</Badge> : <Badge variant="secondary">Inactive</Badge>}
                                    </TableCell>
                                    <TableCell className="text-right">
                                        {!model.is_active && model.status === "trained" && (
                                            <Button size="sm" variant="outline" onClick={() => handleActivateModel(model.name)} disabled={activating}>
                                                <Zap className="h-4 w-4 mr-1" />
                                                Kích hoạt
                                            </Button>
                                        )}
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            {/* Info */}
            <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>Models được train từ Backend. RMSE và MAE càng thấp càng tốt. Precision@K và Recall@K càng cao càng tốt.</AlertDescription>
            </Alert>
        </div>
    );
}
