"use client"

import { useState } from "react"
import { Star } from "lucide-react"
import { cn } from "@/lib/utils"

interface RatingStarsProps {
  value: number
  onChange?: (val: number) => void
  readonly?: boolean
  size?: "sm" | "md" | "lg"
  showValue?: boolean
}

const sizeClasses = {
  sm: "h-3 w-3",
  md: "h-5 w-5",
  lg: "h-6 w-6",
}

const gapClasses = {
  sm: "gap-0.5",
  md: "gap-1",
  lg: "gap-1.5",
}

export function RatingStars({ value, onChange, readonly = false, size = "md", showValue = true }: RatingStarsProps) {
  const [hoverValue, setHoverValue] = useState<number | null>(null)

  const displayValue = hoverValue ?? value
  const maxStars = 10

  const handleClick = (starIndex: number) => {
    if (!readonly && onChange) {
      onChange(starIndex + 1)
    }
  }

  const handleMouseEnter = (starIndex: number) => {
    if (!readonly) {
      setHoverValue(starIndex + 1)
    }
  }

  const handleMouseLeave = () => {
    if (!readonly) {
      setHoverValue(null)
    }
  }

  return (
    <div className="flex items-center gap-2">
      <div className={cn("flex", gapClasses[size])} onMouseLeave={handleMouseLeave}>
        {Array.from({ length: maxStars }, (_, i) => {
          const isFilled = i < displayValue
          const isHalfFilled = readonly && !Number.isInteger(value) && i === Math.floor(value)

          return (
            <button
              key={i}
              type="button"
              disabled={readonly}
              onClick={() => handleClick(i)}
              onMouseEnter={() => handleMouseEnter(i)}
              className={cn(
                "relative transition-transform",
                !readonly && "hover:scale-110 cursor-pointer",
                readonly && "cursor-default",
              )}
            >
              <Star
                className={cn(
                  sizeClasses[size],
                  "transition-colors",
                  isFilled || isHalfFilled ? "fill-warning text-warning" : "fill-transparent text-muted-foreground",
                )}
              />
              {isHalfFilled && (
                <div className="absolute inset-0 overflow-hidden" style={{ width: "50%" }}>
                  <Star className={cn(sizeClasses[size], "fill-warning text-warning")} />
                </div>
              )}
            </button>
          )
        })}
      </div>
      {showValue && (
        <span
          className={cn(
            "font-medium text-foreground",
            size === "sm" && "text-xs",
            size === "md" && "text-sm",
            size === "lg" && "text-base",
          )}
        >
          {value > 0 ? `${value}/10` : "—"}
        </span>
      )}
    </div>
  )
}
