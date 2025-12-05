import type React from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface ChartContainerProps {
  title: string
  description?: string
  children: React.ReactNode
  className?: string
}

export function ChartContainer({ title, description, children, className }: ChartContainerProps) {
  return (
    <Card className={cn("bg-card", className)}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  )
}
