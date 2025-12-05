"use client"

import { useState, useEffect } from "react"
import { StatsCard } from "@/components/admin/stats-card"
import { ChartContainer } from "@/components/admin/chart-container"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Users, Film, Star, Brain, TrendingUp, Activity } from "lucide-react"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  LineChart,
  Line,
} from "recharts"

// Mock data
const mockStats = {
  total_users: 73516,
  total_animes: 12294,
  total_ratings: 7813737,
  active_model: "SVD",
}

const ratingDistribution = [
  { rating: "1", count: 15234 },
  { rating: "2", count: 28456 },
  { rating: "3", count: 89234 },
  { rating: "4", count: 234567 },
  { rating: "5", count: 456789 },
  { rating: "6", count: 789012 },
  { rating: "7", count: 1234567 },
  { rating: "8", count: 2345678 },
  { rating: "9", count: 1567890 },
  { rating: "10", count: 852200 },
]

const topGenres = [
  { name: "Action", value: 4523 },
  { name: "Comedy", value: 3892 },
  { name: "Drama", value: 3456 },
  { name: "Fantasy", value: 2987 },
  { name: "Romance", value: 2654 },
  { name: "Adventure", value: 2345 },
  { name: "Sci-Fi", value: 1876 },
  { name: "Slice of Life", value: 1654 },
]

const userActivity = [
  { month: "T1", users: 45000, ratings: 520000 },
  { month: "T2", users: 48000, ratings: 580000 },
  { month: "T3", users: 52000, ratings: 650000 },
  { month: "T4", users: 55000, ratings: 720000 },
  { month: "T5", users: 58000, ratings: 780000 },
  { month: "T6", users: 62000, ratings: 850000 },
  { month: "T7", users: 65000, ratings: 920000 },
  { month: "T8", users: 68000, ratings: 980000 },
  { month: "T9", users: 70000, ratings: 1050000 },
  { month: "T10", users: 71500, ratings: 1120000 },
  { month: "T11", users: 72800, ratings: 1180000 },
  { month: "T12", users: 73516, ratings: 1250000 },
]

const COLORS = ["#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#ec4899", "#84cc16"]

export default function AdminDashboard() {
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 500)
    return () => clearTimeout(timer)
  }, [])

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }, (_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="h-20 bg-muted rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {Array.from({ length: 2 }, (_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="h-80 bg-muted rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Tổng quan về hệ thống gợi ý anime</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Tổng Users"
          value={mockStats.total_users.toLocaleString()}
          icon={Users}
          trend={{ value: 2.5, isPositive: true }}
        />
        <StatsCard title="Tổng Animes" value={mockStats.total_animes.toLocaleString()} icon={Film} />
        <StatsCard
          title="Tổng Ratings"
          value={(mockStats.total_ratings / 1000000).toFixed(1) + "M"}
          icon={Star}
          trend={{ value: 5.2, isPositive: true }}
        />
        <StatsCard
          title="Active Model"
          value={mockStats.active_model}
          description="Singular Value Decomposition"
          icon={Brain}
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Rating Distribution */}
        <ChartContainer title="Phân bố Rating" description="Số lượng ratings theo điểm (1-10)">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ratingDistribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis
                  dataKey="rating"
                  stroke="hsl(var(--muted-foreground))"
                  tick={{ fill: "hsl(var(--muted-foreground))" }}
                />
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

        {/* Top Genres */}
        <ChartContainer title="Top Genres" description="Các thể loại anime phổ biến nhất">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={topGenres}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {topGenres.map((_, index) => (
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
              </PieChart>
            </ResponsiveContainer>
          </div>
        </ChartContainer>
      </div>

      {/* User Activity Chart */}
      <ChartContainer title="Hoạt động theo thời gian" description="Tăng trưởng users và ratings theo tháng">
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={userActivity}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis
                dataKey="month"
                stroke="hsl(var(--muted-foreground))"
                tick={{ fill: "hsl(var(--muted-foreground))" }}
              />
              <YAxis
                yAxisId="left"
                stroke="hsl(var(--muted-foreground))"
                tick={{ fill: "hsl(var(--muted-foreground))" }}
                tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
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
                formatter={(value: number, name: string) => [
                  value.toLocaleString(),
                  name === "users" ? "Users" : "Ratings",
                ]}
              />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="users"
                stroke="hsl(var(--primary))"
                strokeWidth={2}
                dot={false}
                name="Users"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="ratings"
                stroke="hsl(var(--success))"
                strokeWidth={2}
                dot={false}
                name="Ratings"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </ChartContainer>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Rating trung bình</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <span className="text-3xl font-bold">7.6</span>
              <Badge variant="secondary">/10</Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Ratings / User (TB)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <span className="text-3xl font-bold">106</span>
              <Activity className="h-5 w-5 text-success" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Độ phủ dữ liệu</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <span className="text-3xl font-bold">0.86%</span>
              <TrendingUp className="h-5 w-5 text-primary" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
