"use client"

import { useState, useEffect } from "react"
import { ChartContainer } from "@/components/admin/chart-container"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { BarChart3, TrendingUp, Film, Users } from "lucide-react"
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
  AreaChart,
  Area,
  ScatterChart,
  Scatter,
  ZAxis,
} from "recharts"

// Mock data
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

const genreFrequency = [
  { name: "Action", count: 4523, percentage: 36.8 },
  { name: "Comedy", count: 3892, percentage: 31.7 },
  { name: "Drama", count: 3456, percentage: 28.1 },
  { name: "Fantasy", count: 2987, percentage: 24.3 },
  { name: "Romance", count: 2654, percentage: 21.6 },
  { name: "Adventure", count: 2345, percentage: 19.1 },
  { name: "Sci-Fi", count: 1876, percentage: 15.3 },
  { name: "Slice of Life", count: 1654, percentage: 13.5 },
  { name: "Supernatural", count: 1432, percentage: 11.7 },
  { name: "School", count: 1234, percentage: 10.0 },
]

const topAnimes = [
  { name: "Fullmetal Alchemist: Brotherhood", ratings: 2800000, score: 9.2 },
  { name: "Steins;Gate", ratings: 2100000, score: 9.1 },
  { name: "Attack on Titan", ratings: 3500000, score: 9.1 },
  { name: "Hunter x Hunter", ratings: 1900000, score: 9.0 },
  { name: "Death Note", ratings: 3200000, score: 9.0 },
  { name: "Code Geass", ratings: 1700000, score: 8.9 },
  { name: "Demon Slayer", ratings: 2300000, score: 8.9 },
  { name: "Mob Psycho 100", ratings: 1200000, score: 8.8 },
  { name: "Spy x Family", ratings: 1500000, score: 8.8 },
  { name: "Jujutsu Kaisen", ratings: 1800000, score: 8.7 },
]

const userActivity = [
  { date: "01/01", newUsers: 1200, activeUsers: 15000, ratings: 45000 },
  { date: "01/02", newUsers: 1350, activeUsers: 16200, ratings: 52000 },
  { date: "01/03", newUsers: 980, activeUsers: 14800, ratings: 41000 },
  { date: "01/04", newUsers: 1100, activeUsers: 15500, ratings: 48000 },
  { date: "01/05", newUsers: 1450, activeUsers: 17000, ratings: 56000 },
  { date: "01/06", newUsers: 1680, activeUsers: 18500, ratings: 62000 },
  { date: "01/07", newUsers: 1520, activeUsers: 17800, ratings: 58000 },
]

const correlationData = Array.from({ length: 100 }, () => ({
  x: Math.random() * 10,
  y: Math.random() * 10,
  z: Math.floor(Math.random() * 1000) + 100,
}))

const typeDistribution = [
  { name: "TV", value: 5234 },
  { name: "Movie", value: 2456 },
  { name: "OVA", value: 1876 },
  { name: "Special", value: 1234 },
  { name: "ONA", value: 987 },
  { name: "Music", value: 507 },
]

const COLORS = ["#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#ec4899", "#84cc16"]

export default function VisualizationPage() {
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 500)
    return () => clearTimeout(timer)
  }, [])

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
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold">Trực quan hóa dữ liệu</h1>
        <p className="text-muted-foreground">Phân tích và trực quan hóa dữ liệu hệ thống</p>
      </div>

      {/* Tabs for different visualizations */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full max-w-2xl grid-cols-4">
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
          <TabsTrigger value="users" className="gap-2">
            <Users className="h-4 w-4" />
            Users
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

            {/* Anime Type Distribution */}
            <ChartContainer title="Phân bố loại Anime" description="Số lượng anime theo loại">
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={typeDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {typeDistribution.map((_, index) => (
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
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Rating Trend */}
            <ChartContainer
              title="Xu hướng Ratings theo ngày"
              description="Số lượng ratings mới mỗi ngày"
              className="lg:col-span-2"
            >
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={userActivity}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis
                      dataKey="date"
                      stroke="hsl(var(--muted-foreground))"
                      tick={{ fill: "hsl(var(--muted-foreground))" }}
                    />
                    <YAxis
                      stroke="hsl(var(--muted-foreground))"
                      tick={{ fill: "hsl(var(--muted-foreground))" }}
                      tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
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
                    <Area
                      type="monotone"
                      dataKey="ratings"
                      stroke="hsl(var(--primary))"
                      fill="hsl(var(--primary))"
                      fillOpacity={0.2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </ChartContainer>

            {/* Rating vs Score Correlation */}
            <ChartContainer
              title="Rating vs Score Correlation"
              description="Mối quan hệ giữa số ratings và điểm trung bình"
              className="lg:col-span-2"
            >
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis
                      type="number"
                      dataKey="x"
                      name="Score"
                      domain={[0, 10]}
                      stroke="hsl(var(--muted-foreground))"
                      tick={{ fill: "hsl(var(--muted-foreground))" }}
                    />
                    <YAxis
                      type="number"
                      dataKey="y"
                      name="Rating Count"
                      stroke="hsl(var(--muted-foreground))"
                      tick={{ fill: "hsl(var(--muted-foreground))" }}
                    />
                    <ZAxis type="number" dataKey="z" range={[50, 500]} />
                    <Tooltip
                      cursor={{ strokeDasharray: "3 3" }}
                      contentStyle={{
                        backgroundColor: "hsl(var(--card))",
                        border: "1px solid hsl(var(--border))",
                        borderRadius: "8px",
                        color: "hsl(var(--foreground))",
                      }}
                    />
                    <Scatter data={correlationData} fill="hsl(var(--primary))" fillOpacity={0.6} />
                  </ScatterChart>
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
                    <XAxis
                      type="number"
                      stroke="hsl(var(--muted-foreground))"
                      tick={{ fill: "hsl(var(--muted-foreground))" }}
                    />
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
            <ChartContainer title="Top 10 Anime" description="Anime được xem nhiều nhất">
              <div className="h-96 overflow-y-auto">
                <div className="space-y-3">
                  {topAnimes.map((anime, index) => (
                    <div key={anime.name} className="flex items-center gap-3 p-3 rounded-lg bg-secondary/50">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                        <span className="text-sm font-bold text-primary">{index + 1}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm truncate">{anime.name}</p>
                        <p className="text-xs text-muted-foreground">{(anime.ratings / 1000000).toFixed(1)}M ratings</p>
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

        {/* Users Tab */}
        <TabsContent value="users" className="space-y-6">
          <div className="grid grid-cols-1 gap-6">
            {/* User Activity */}
            <ChartContainer title="Hoạt động Users" description="Users mới và users active theo ngày">
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={userActivity}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis
                      dataKey="date"
                      stroke="hsl(var(--muted-foreground))"
                      tick={{ fill: "hsl(var(--muted-foreground))" }}
                    />
                    <YAxis
                      stroke="hsl(var(--muted-foreground))"
                      tick={{ fill: "hsl(var(--muted-foreground))" }}
                      tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
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
                        name === "newUsers" ? "Users mới" : "Users active",
                      ]}
                    />
                    <Legend formatter={(value) => (value === "newUsers" ? "Users mới" : "Users active")} />
                    <Line
                      type="monotone"
                      dataKey="newUsers"
                      stroke="hsl(var(--primary))"
                      strokeWidth={2}
                      dot={{ fill: "hsl(var(--primary))" }}
                    />
                    <Line
                      type="monotone"
                      dataKey="activeUsers"
                      stroke="hsl(var(--success))"
                      strokeWidth={2}
                      dot={{ fill: "hsl(var(--success))" }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </ChartContainer>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
