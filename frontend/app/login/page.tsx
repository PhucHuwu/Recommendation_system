"use client";

import type React from "react";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/auth-context";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Film, User, ArrowRight, Info } from "lucide-react";

export default function LoginPage() {
    const [userId, setUserId] = useState("");
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const { login } = useAuth();
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        const id = Number.parseInt(userId, 10);
        if (isNaN(id) || id < 0) {
            setError("Vui lòng nhập User ID hợp lệ (số nguyên không âm)");
            return;
        }

        setIsLoading(true);
        try {
            await login(id);
            router.push("/");
        } catch {
            setError("Đã có lỗi xảy ra. Vui lòng thử lại.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-[80vh] flex items-center justify-center px-4">
            <div className="w-full max-w-md">
                {/* Logo */}
                <Link href="/" className="flex items-center justify-center gap-2 mb-8">
                    <Film className="h-10 w-10 text-primary" />
                    <span className="text-2xl font-bold">WibiFlix</span>
                </Link>

                <Card className="bg-card border-border">
                    <CardHeader className="text-center">
                        <CardTitle className="text-2xl">Đăng nhập</CardTitle>
                        <CardDescription>Nhập User ID của bạn để tiếp tục</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="userId">User ID</Label>
                                <div className="relative">
                                    <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                    <Input
                                        id="userId"
                                        type="number"
                                        placeholder="Nhập User ID (ví dụ: 0, 12345)"
                                        value={userId}
                                        onChange={(e) => setUserId(e.target.value)}
                                        className="pl-10"
                                        min="0"
                                        required
                                    />
                                </div>
                            </div>

                            {error && (
                                <Alert variant="destructive">
                                    <AlertDescription>{error}</AlertDescription>
                                </Alert>
                            )}

                            <Button type="submit" className="w-full" disabled={isLoading}>
                                {isLoading ? (
                                    "Đang đăng nhập..."
                                ) : (
                                    <>
                                        Đăng nhập
                                        <ArrowRight className="ml-2 h-4 w-4" />
                                    </>
                                )}
                            </Button>
                        </form>

                        {/* Info box */}
                        <div className="mt-6 p-4 rounded-lg bg-secondary/50 border border-border">
                            <div className="flex gap-3">
                                <Info className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                                <div className="text-sm text-muted-foreground">
                                    <p className="font-medium text-foreground mb-1">Hướng dẫn</p>
                                    <p>
                                        Hệ thống sử dụng User ID từ dataset để đăng nhập. Không cần mật khẩu. Nhập bất kỳ số nào để trải nghiệm hệ thống gợi ý.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
