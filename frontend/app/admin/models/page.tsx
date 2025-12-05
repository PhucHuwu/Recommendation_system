"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { ChartContainer } from "@/components/admin/chart-container"
import { Brain, CheckCircle2, Play, RefreshCw, Zap, AlertCircle } from "lucide-react"
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts"
import type { ModelInfo } from "@/types/api"

// Mock data
const mockModels: ModelInfo[] = [
  {
    model_id: "svd-v1",
    model_name: "SVD",
    model_type: "Matrix Factorization",
    is_active: true,
    metrics: {
      rmse: 0.8234,
      mae: 0.6123,
      precision_at_k: 0.7845,
      recall_at_k: 0.6234,
    },
    created_at: "2025-01-01T00:00:00Z",
    trained_at: "2025-01-05T10:30:00Z",
  },
  {
    model_id: "knn-v1",
    model_name: "KNN",
    model_type: "Collaborative Filtering",
    is_active: false,
    metrics: {
      rmse: 0.8756,
      mae: 0.6534,
      precision_at_k: 0.7234,
      recall_at_k: 0.589,
    },
    created_at: "2025-01-01T00:00:00Z",
    trained_at: "2025-01-04T15:00:00Z",
  },
  {
    model_id: "nmf-v1",
    model_name: "NMF",
    model_type: "Matrix Factorization",
    is_active: false,
    metrics: {
      rmse: 0.8912,
      mae: 0.6789,
      precision_at_k: 0.7012,
      recall_at_k: 0.5678,
    },
    created_at: "2025-01-01T00:00:00Z",
    trained_at: "2025-01-03T09:00:00Z",
  },
  {
    model_id: "baseline-v1",
    model_name: "Baseline",
    model_type: "Statistical",
    is_active: false,
    metrics: {
      rmse: 0.9345,
      mae: 0.7234,
      precision_at_k: 0.6534,
      recall_at_k: 0.5123,
    },
    created_at: "2025-01-01T00:00:00Z",
    trained_at: "2025-01-02T12:00:00Z",
  },
]

const comparisonData = mockModels.map((model) => ({
  name: model.model_name,
  rmse: model.metrics.rmse,
  mae: model.metrics.mae,
  precision: model.metrics.precision_at_k || 0,
  recall: model.metrics.recall_at_k || 0,
}))

const radarData = [
  { metric: "RMSE (↓)", SVD: 0.85, KNN: 0.78, NMF: 0.75, Baseline: 0.65 },
  { metric: "MAE (↓)", SVD: 0.88, KNN: 0.82, NMF: 0.78, Baseline: 0.68 },
  { metric: "Precision@K", SVD: 0.78, KNN: 0.72, NMF: 0.7, Baseline: 0.65 },
  { metric: "Recall@K", SVD: 0.62, KNN: 0.59, NMF: 0.57, Baseline: 0.51 },
  { metric: "Coverage", SVD: 0.75, KNN: 0.68, NMF: 0.65, Baseline: 0.9 },
]

export default function ModelsPage() {
  const [models, setModels] = useState<ModelInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedModel, setSelectedModel] = useState<string>("")
  const [training, setTraining] = useState(false)
  const [activating, setActivating] = useState(false)

  useEffect(() => {
    const fetchModels = async () => {
      setLoading(true)
      await new Promise((resolve) => setTimeout(resolve, 500))
      setModels(mockModels)
      setLoading(false)
    }
    fetchModels()
  }, [])

  const activeModel = models.find((m) => m.is_active)

  const handleActivateModel = async (modelId: string) => {
    setActivating(true)
    await new Promise((resolve) => setTimeout(resolve, 1000))
    setModels((prev) =>
      prev.map((m) => ({
        ...m,
        is_active: m.model_id === modelId,
      })),
    )
    setActivating(false)
  }

  const handleTrainModel = async () => {
    if (!selectedModel) return
    setTraining(true)
    await new Promise((resolve) => setTimeout(resolve, 2000))
    setTraining(false)
    // Show success message
  }

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
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold">Quản lý Models</h1>
        <p className="text-muted-foreground">Quản lý và so sánh các model recommendation</p>
      </div>

      {/* Active Model Info */}
      {activeModel && (
        <Alert className="bg-primary/10 border-primary/20">
          <CheckCircle2 className="h-4 w-4 text-primary" />
          <AlertDescription className="flex items-center justify-between">
            <span>
              Model đang active: <strong>{activeModel.model_name}</strong> ({activeModel.model_type})
            </span>
            <Badge variant="default" className="bg-primary">
              RMSE: {activeModel.metrics.rmse.toFixed(4)}
            </Badge>
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
                <TableHead>Loại</TableHead>
                <TableHead className="text-right">RMSE</TableHead>
                <TableHead className="text-right">MAE</TableHead>
                <TableHead className="text-right">Precision@K</TableHead>
                <TableHead className="text-right">Recall@K</TableHead>
                <TableHead>Trạng thái</TableHead>
                <TableHead className="text-right">Hành động</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {models.map((model) => (
                <TableRow key={model.model_id}>
                  <TableCell className="font-medium">{model.model_name}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{model.model_type}</Badge>
                  </TableCell>
                  <TableCell className="text-right font-mono">{model.metrics.rmse.toFixed(4)}</TableCell>
                  <TableCell className="text-right font-mono">{model.metrics.mae.toFixed(4)}</TableCell>
                  <TableCell className="text-right font-mono">
                    {(model.metrics.precision_at_k || 0).toFixed(4)}
                  </TableCell>
                  <TableCell className="text-right font-mono">{(model.metrics.recall_at_k || 0).toFixed(4)}</TableCell>
                  <TableCell>
                    {model.is_active ? (
                      <Badge className="bg-success">Active</Badge>
                    ) : (
                      <Badge variant="secondary">Inactive</Badge>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    {!model.is_active && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleActivateModel(model.model_id)}
                        disabled={activating}
                      >
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

      {/* Train New Model */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <RefreshCw className="h-5 w-5" />
            Train Model Mới
          </CardTitle>
          <CardDescription>Chọn loại model và bắt đầu quá trình training</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4">
            <Select value={selectedModel} onValueChange={setSelectedModel}>
              <SelectTrigger className="w-full sm:w-64">
                <SelectValue placeholder="Chọn loại model" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="svd">SVD (Matrix Factorization)</SelectItem>
                <SelectItem value="knn">KNN (Collaborative Filtering)</SelectItem>
                <SelectItem value="nmf">NMF (Non-negative MF)</SelectItem>
                <SelectItem value="baseline">Baseline (Statistical)</SelectItem>
              </SelectContent>
            </Select>
            <Button onClick={handleTrainModel} disabled={!selectedModel || training}>
              {training ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Đang train...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  Bắt đầu Train
                </>
              )}
            </Button>
          </div>
          {training && (
            <Alert className="mt-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Quá trình training có thể mất vài phút. Vui lòng không đóng trang này.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Model Comparison Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Metrics Comparison Bar Chart */}
        <ChartContainer title="So sánh Metrics" description="So sánh RMSE và MAE giữa các models">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis
                  dataKey="name"
                  stroke="hsl(var(--muted-foreground))"
                  tick={{ fill: "hsl(var(--muted-foreground))" }}
                />
                <YAxis stroke="hsl(var(--muted-foreground))" tick={{ fill: "hsl(var(--muted-foreground))" }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                    color: "hsl(var(--foreground))",
                  }}
                />
                <Legend />
                <Bar dataKey="rmse" fill="hsl(var(--primary))" name="RMSE" />
                <Bar dataKey="mae" fill="hsl(var(--success))" name="MAE" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartContainer>

        {/* Radar Chart */}
        <ChartContainer title="Model Performance Radar" description="So sánh đa chiều giữa các models">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid stroke="hsl(var(--border))" />
                <PolarAngleAxis dataKey="metric" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 1]} tick={{ fill: "hsl(var(--muted-foreground))" }} />
                <Radar name="SVD" dataKey="SVD" stroke="#6366f1" fill="#6366f1" fillOpacity={0.3} />
                <Radar name="KNN" dataKey="KNN" stroke="#22c55e" fill="#22c55e" fillOpacity={0.3} />
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </ChartContainer>
      </div>
    </div>
  )
}
