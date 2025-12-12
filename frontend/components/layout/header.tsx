"use client";

import type React from "react";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuth } from "@/context/auth-context";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Search, User, LogOut, History, Settings, Film } from "lucide-react";
import { useState } from "react";
import { useRouter } from "next/navigation";

export function Header() {
    const { user, isAuthenticated, logout } = useAuth();
    const [searchQuery, setSearchQuery] = useState("");
    const router = useRouter();
    const pathname = usePathname();

    const isActive = (href: string) => {
        if (!pathname) return false;
        if (href === "/") return pathname === "/";
        return pathname.startsWith(href);
    };

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (searchQuery.trim()) {
            router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
        }
    };

    return (
        <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container mx-auto flex h-16 items-center justify-between px-4">
                {/* Logo */}
                <Link href="/" className="flex items-center gap-2">
                    <Film className="h-8 w-8 text-primary" />
                    <span className="text-xl font-bold text-foreground">WibiFlix</span>
                </Link>

                {/* Navigation */}
                <nav className="hidden md:flex items-center gap-6">
                    <Link
                        href="/"
                        className={cn(
                            "text-sm font-medium transition-colors",
                            isActive("/") ? "underline underline-offset-4 decoration-primary text-foreground" : "text-muted-foreground hover:text-foreground"
                        )}
                    >
                        Trang chủ
                    </Link>
                    <Link
                        href="/anime"
                        className={cn(
                            "text-sm font-medium transition-colors",
                            isActive("/anime")
                                ? "underline underline-offset-4 decoration-primary text-foreground"
                                : "text-muted-foreground hover:text-foreground"
                        )}
                    >
                        Anime
                    </Link>
                    {isAuthenticated && (
                        <Link
                            href="/admin"
                            className={cn(
                                "text-sm font-medium transition-colors",
                                isActive("/admin")
                                    ? "underline underline-offset-4 decoration-primary text-foreground"
                                    : "text-muted-foreground hover:text-foreground"
                            )}
                        >
                            Admin
                        </Link>
                    )}
                    {isAuthenticated && (
                        <>
                            <Link
                                href="/history"
                                className={cn(
                                    "text-sm font-medium transition-colors",
                                    isActive("/history")
                                        ? "underline underline-offset-4 decoration-primary text-foreground"
                                        : "text-muted-foreground hover:text-foreground"
                                )}
                            >
                                Lịch sử
                            </Link>
                            <Link
                                href="/profile"
                                className={cn(
                                    "text-sm font-medium transition-colors",
                                    isActive("/profile")
                                        ? "underline underline-offset-4 decoration-primary text-foreground"
                                        : "text-muted-foreground hover:text-foreground"
                                )}
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
                                    <Link
                                        href="/profile"
                                        className={cn(
                                            "flex items-center gap-2 cursor-pointer text-sm transition-colors",
                                            isActive("/profile")
                                                ? "underline underline-offset-2 decoration-primary text-foreground"
                                                : "text-muted-foreground hover:text-foreground"
                                        )}
                                    >
                                        <User className="h-4 w-4" />
                                        Profile
                                    </Link>
                                </DropdownMenuItem>
                                <DropdownMenuItem asChild>
                                    <Link
                                        href="/history"
                                        className={cn(
                                            "flex items-center gap-2 cursor-pointer text-sm transition-colors",
                                            isActive("/history")
                                                ? "underline underline-offset-2 decoration-primary text-foreground"
                                                : "text-muted-foreground hover:text-foreground"
                                        )}
                                    >
                                        <History className="h-4 w-4" />
                                        Lịch sử xem
                                    </Link>
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem asChild>
                                    <Link
                                        href="/admin"
                                        className={cn(
                                            "flex items-center gap-2 cursor-pointer text-sm transition-colors",
                                            isActive("/admin")
                                                ? "underline underline-offset-2 decoration-primary text-foreground"
                                                : "text-muted-foreground hover:text-foreground"
                                        )}
                                    >
                                        <Settings className="h-4 w-4" />
                                        Admin Dashboard
                                    </Link>
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem onClick={logout} className="flex items-center gap-2 cursor-pointer text-destructive focus:text-destructive">
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
    );
}
