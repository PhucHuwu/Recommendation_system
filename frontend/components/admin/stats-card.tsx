import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import type { LucideIcon } from "lucide-react"

interface StatsCardProps {
  title: string
  value: string | number
  description?: string
  icon: LucideIcon
  trend?: {
    value: number
    isPositive: boolean
  }
  className?: string
}

export function StatsCard({ title, value, description, icon: Icon, trend, className }: StatsCardProps) {
  return (
    <Card className={cn("bg-card", className)}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-3xl font-bold mt-2">{value}</p>
            {description && <p className="text-xs text-muted-foreground mt-1">{description}</p>}
            {trend && (
              <p
                className={cn(
                  "text-xs mt-2 flex items-center gap-1",
                  trend.isPositive ? "text-success" : "text-destructive",
                )}
              >
                {trend.isPositive ? "↑" : "↓"} {Math.abs(trend.value)}%
                <span className="text-muted-foreground">vs tháng trước</span>
              </p>
            )}
          </div>
          <div className="p-3 rounded-lg bg-primary/10">
            <Icon className="h-6 w-6 text-primary" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
