"use client";

import type React from "react";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { PageLoading } from "@/components/ui/loading";
import { cn } from "@/lib/utils";
import { LayoutDashboard, Brain, BarChart3, ArrowLeft, Settings } from "lucide-react";

const adminNavItems = [
    { href: "/admin", label: "Dashboard", icon: LayoutDashboard },
    { href: "/admin/models", label: "Quản lý Models", icon: Brain },
    { href: "/admin/visualization", label: "Trực quan hóa", icon: BarChart3 },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
    const { user, isAuthenticated, isLoading } = useAuth();
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        if (!isLoading && !isAuthenticated) {
            router.push("/login");
            return;
        }
    }, [isAuthenticated, isLoading, user, router]);

    if (isLoading || !isAuthenticated) {
        return <PageLoading />;
    }

    return (
        <div className="min-h-screen">
            {/* Admin Header */}
            <div className="border-b border-border bg-card">
                <div className="container mx-auto px-4">
                    <div className="flex items-center justify-between h-14">
                        <div className="flex items-center gap-4">
                            <Link href="/" className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors">
                                <ArrowLeft className="h-4 w-4" />
                                <span className="text-sm">Quay lại</span>
                            </Link>
                            <div className="h-6 w-px bg-border" />
                            <div className="flex items-center gap-2">
                                <Settings className="h-5 w-5 text-primary" />
                                <span className="font-semibold">Admin Panel</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Admin Navigation */}
            <div className="border-b border-border bg-background">
                <div className="container mx-auto px-4">
                    <nav className="flex items-center gap-1 overflow-x-auto">
                        {adminNavItems.map((item) => {
                            const isActive = pathname === item.href;
                            const Icon = item.icon;

                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={cn(
                                        "flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap",
                                        isActive
                                            ? "border-primary text-primary"
                                            : "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
                                    )}
                                >
                                    <Icon className="h-4 w-4" />
                                    {item.label}
                                </Link>
                            );
                        })}
                    </nav>
                </div>
            </div>

            {/* Content */}
            <div className="container mx-auto px-4 py-8">{children}</div>
        </div>
    );
}
