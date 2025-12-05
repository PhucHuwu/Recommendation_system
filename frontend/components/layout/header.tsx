"use client"

import type React from "react"

import Link from "next/link"
import { useAuth } from "@/context/auth-context"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Search, User, LogOut, History, Settings, Film } from "lucide-react"
import { useState } from "react"
import { useRouter } from "next/navigation"

export function Header() {
  const { user, isAuthenticated, logout } = useAuth()
  const [searchQuery, setSearchQuery] = useState("")
  const router = useRouter()

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`)
    }
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <Film className="h-8 w-8 text-primary" />
          <span className="text-xl font-bold text-foreground">Wibiflix</span>
        </Link>

        {/* Navigation */}
        <nav className="hidden md:flex items-center gap-6">
          <Link
            href="/anime"
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            Anime
          </Link>
          {isAuthenticated && (
            <>
              <Link
                href="/history"
                className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                Lịch sử
              </Link>
              <Link
                href="/profile"
                className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                Profile
              </Link>
            </>
          )}
        </nav>

        {/* Search & User */}
        <div className="flex items-center gap-4">
          {/* Search */}
          <form onSubmit={handleSearch} className="hidden sm:flex items-center">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                type="search"
                placeholder="Tìm kiếm anime..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-64 pl-9 bg-secondary border-border"
              />
            </div>
          </form>

          {/* Mobile Search Button */}
          <Button variant="ghost" size="icon" className="sm:hidden" onClick={() => router.push("/search")}>
            <Search className="h-5 w-5" />
            <span className="sr-only">Tìm kiếm</span>
          </Button>

          {/* User Menu */}
          {isAuthenticated ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="rounded-full">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    <span className="text-sm font-medium">{user?.user_id?.toString().charAt(0) || "U"}</span>
                  </div>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <div className="flex items-center gap-2 p-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    <User className="h-4 w-4" />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-sm font-medium">User #{user?.user_id}</span>
                    <span className="text-xs text-muted-foreground">{user?.username}</span>
                  </div>
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link href="/profile" className="flex items-center gap-2 cursor-pointer">
                    <User className="h-4 w-4" />
                    Profile
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/history" className="flex items-center gap-2 cursor-pointer">
                    <History className="h-4 w-4" />
                    Lịch sử xem
                  </Link>
                </DropdownMenuItem>
                {user?.user_id === 1 && (
                  <>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem asChild>
                      <Link href="/admin" className="flex items-center gap-2 cursor-pointer">
                        <Settings className="h-4 w-4" />
                        Admin Dashboard
                      </Link>
                    </DropdownMenuItem>
                  </>
                )}
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={logout}
                  className="flex items-center gap-2 cursor-pointer text-destructive focus:text-destructive"
                >
                  <LogOut className="h-4 w-4" />
                  Đăng xuất
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Button asChild>
              <Link href="/login">Đăng nhập</Link>
            </Button>
          )}
        </div>
      </div>
    </header>
  )
}
