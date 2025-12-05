import { cn } from "@/lib/utils"
import { Loader2 } from "lucide-react"

interface LoadingProps {
  size?: "sm" | "md" | "lg"
  text?: string
  className?: string
}

const sizeClasses = {
  sm: "h-4 w-4",
  md: "h-6 w-6",
  lg: "h-10 w-10",
}

export function Loading({ size = "md", text, className }: LoadingProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center gap-2", className)}>
      <Loader2 className={cn("animate-spin text-primary", sizeClasses[size])} />
      {text && <p className="text-sm text-muted-foreground">{text}</p>}
    </div>
  )
}

export function PageLoading() {
  return (
    <div className="flex h-[50vh] items-center justify-center">
      <Loading size="lg" text="Đang tải..." />
    </div>
  )
}

export function CardSkeleton() {
  return (
    <div className="animate-pulse rounded-lg bg-card overflow-hidden border border-border">
      <div className="h-32 bg-muted" />
      <div className="p-4 space-y-2">
        <div className="h-4 bg-muted rounded w-3/4" />
        <div className="h-4 bg-muted rounded w-1/2" />
        <div className="h-3 bg-muted rounded w-1/4" />
        <div className="flex gap-1">
          <div className="h-5 bg-muted rounded-full w-12" />
          <div className="h-5 bg-muted rounded-full w-16" />
        </div>
      </div>
    </div>
  )
}
