"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { Brain, CheckCircle2, Zap, AlertCircle, Loader2, Play } from "lucide-react";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

export default function ModelsPage() {
    const [models, setModels] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [activating, setActivating] = useState(false);
    const [message, setMessage] = useState("");

    // Training states
    const [trainingDialogOpen, setTrainingDialogOpen] = useState(false);
    const [selectedModel, setSelectedModel] = useState<string | null>(null);
    const [trainingJobId, setTrainingJobId] = useState<string | null>(null);
    const [trainingStatus, setTrainingStatus] = useState<any>(null);

    const { toast } = useToast();

    useEffect(() => {
        fetchModels();
    }, []);

    // Poll training status
    useEffect(() => {
        if (!trainingJobId) return;

        const pollInterval = setInterval(async () => {
            try {
                const status = await api.getTrainingStatus(trainingJobId);
                setTrainingStatus(status);

                // If completed or failed, stop polling
                if (status.status === "completed" || status.status === "failed") {
                    clearInterval(pollInterval);
                    setTrainingJobId(null);

                    if (status.status === "completed") {
                        toast({
                            title: "Training hoàn tất!",
                            description: `Model ${status.model_name} đã được train thành công.`,
                        });
                        await fetchModels(); // Refresh models list
                    } else {
                        toast({
                            title: "Training thất bại",
                            description: status.error || "Có lỗi xảy ra",
                            variant: "destructive",
                        });
                    }
                }
            } catch (error) {
                console.error("Failed to fetch training status:", error);
            }
        }, 3000); // Poll every 3 seconds

        return () => clearInterval(pollInterval);
    }, [trainingJobId, toast]);

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

    const handleTrainClick = (modelName: string) => {
        setSelectedModel(modelName);
        setTrainingDialogOpen(true);
    };

    const handleConfirmTrain = async () => {
        if (!selectedModel) return;

        setTrainingDialogOpen(false);

        try {
            const response = await api.trainModel(selectedModel);
            setTrainingJobId(response.job_id);
            setTrainingStatus({
                job_id: response.job_id,
                model_name: selectedModel,
                status: "pending",
                progress: 0,
                current_step: "Initializing...",
            });

            toast({
                title: "Training đã bắt đầu",
                description: `Model ${selectedModel} đang được train...`,
            });
        } catch (error: any) {
            toast({
                title: "Không thể bắt đầu training",
                description: error.message || "Có lỗi xảy ra",
                variant: "destructive",
            });
        }
    };

    const getModelDisplayName = (name: string) => {
        const names: Record<string, string> = {
            user_based_cf: "User-Based CF",
            item_based_cf: "Item-Based CF",
            hybrid: "Hybrid",
            neural_cf: "Neural CF",
        };
        return names[name] || name;
    };

    const getEstimatedTime = (modelName: string) => {
        const times: Record<string, string> = {
            user_based_cf: "2-3 phút",
            item_based_cf: "2-3 phút",
            hybrid: "3-5 phút",
            neural_cf: "30-60 phút",
        };
        return times[modelName] || "5-10 phút";
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

            {/* Training Progress */}
            {trainingStatus && trainingStatus.status !== "completed" && (
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Loader2 className="h-5 w-5 animate-spin" />
                            Training {getModelDisplayName(trainingStatus.model_name)}
                        </CardTitle>
                        <CardDescription>{trainingStatus.current_step}</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Progress value={trainingStatus.progress} className="h-2" />
                        <p className="text-sm text-muted-foreground mt-2">{trainingStatus.progress}% hoàn thành</p>
                    </CardContent>
                </Card>
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
                                <TableHead className="text-right">RMSE ↓</TableHead>
                                <TableHead className="text-right">MAE ↓</TableHead>
                                <TableHead className="text-right">Precision@K ↑</TableHead>
                                <TableHead className="text-right">Recall@K ↑</TableHead>
                                <TableHead className="text-right">Coverage ↑</TableHead>
                                <TableHead className="text-right">Diversity ↑</TableHead>
                                <TableHead className="text-right">Novelty ↑</TableHead>
                                <TableHead className="text-right">Training Status</TableHead>
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
                                        {model.metrics?.precision_at_k ? (model.metrics.precision_at_k * 100).toFixed(2) + "%" : "-"}
                                    </TableCell>
                                    <TableCell className="text-right font-mono">
                                        {model.metrics?.recall_at_k ? (model.metrics.recall_at_k * 100).toFixed(2) + "%" : "-"}
                                    </TableCell>
                                    <TableCell className="text-right font-mono">
                                        {model.metrics?.coverage ? (model.metrics.coverage * 100).toFixed(2) + "%" : "-"}
                                    </TableCell>
                                    <TableCell className="text-right font-mono">
                                        {model.metrics?.diversity ? model.metrics.diversity.toFixed(4) : "-"}
                                    </TableCell>
                                    <TableCell className="text-right font-mono">{model.metrics?.novelty ? model.metrics.novelty.toFixed(2) : "-"}</TableCell>
                                    <TableCell className="text-right">
                                        <Badge variant={model.status === "trained" ? "default" : "secondary"}>{model.status || "not_trained"}</Badge>
                                    </TableCell>

                                    <TableCell className="text-right">
                                        <div className="flex gap-2 justify-end">
                                            <Button size="sm" variant="outline" onClick={() => handleTrainClick(model.name)} disabled={!!trainingJobId}>
                                                <Play className="h-4 w-4 mr-1" />
                                                Train
                                            </Button>
                                        </div>
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

            {/* Training Confirmation Dialog */}
            <Dialog open={trainingDialogOpen} onOpenChange={setTrainingDialogOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Confirm Training</DialogTitle>
                        <DialogDescription>
                            Bạn có chắc muốn train lại model <strong>{selectedModel ? getModelDisplayName(selectedModel) : ""}</strong>?
                        </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                        <Alert>
                            <AlertCircle className="h-4 w-4" />
                            <AlertDescription>
                                <p className="font-medium mb-2">Lưu ý:</p>
                                <ul className="list-disc list-inside space-y-1 text-sm">
                                    <li>Training sẽ sử dụng data mới nhất từ MongoDB</li>
                                    <li>
                                        Thời gian ước tính: <strong>{selectedModel ? getEstimatedTime(selectedModel) : ""}</strong>
                                    </li>
                                    <li>Chỉ có thể train 1 model tại 1 thời điểm</li>
                                    <li>Bạn có thể đóng trang này, training vẫn tiếp tục</li>
                                </ul>
                            </AlertDescription>
                        </Alert>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setTrainingDialogOpen(false)}>
                            Hủy
                        </Button>
                        <Button onClick={handleConfirmTrain}>
                            <Play className="h-4 w-4 mr-2" />
                            Bắt đầu Training
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
