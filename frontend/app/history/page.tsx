"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/auth-context";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PageLoading } from "@/components/ui/loading";
import { RatingStars } from "@/components/anime/rating-stars";
import { History, Search, User, Calendar, Film, Trash2, ExternalLink } from "lucide-react";
import { api } from "@/lib/api";
import type { UserHistory } from "@/types/user";

function formatDate(dateString: string) {
    if (!dateString) return "N/A";

    const date = new Date(dateString);

    // Check if date is valid
    if (isNaN(date.getTime())) return "N/A";

    return new Intl.DateTimeFormat("vi-VN", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    }).format(date);
}

function HistoryItem({ item, onRemove }: { item: UserHistory; onRemove?: () => void }) {
    return (
        <Card className="bg-card hover:bg-card/80 transition-colors">
            <CardContent className="p-4">
                <div className="flex gap-4">
                    {/* Info */}
                    <div className="flex-1 min-w-0">
                        <Link href={`/anime/${item.anime_id}`}>
                            <h3 className="font-semibold text-foreground hover:text-primary transition-colors line-clamp-1">{item.anime?.name}</h3>
                        </Link>

                        <div className="flex items-center gap-2 mt-1">
                            <RatingStars value={item.anime?.rating || 0} readonly size="sm" showValue={false} />
                            <span className="text-sm text-muted-foreground">{item.anime?.rating?.toFixed(1)}</span>
                        </div>

                        <div className="flex flex-wrap gap-1 mt-2">
                            {item.anime?.genre?.slice(0, 3).map((genre) => (
                                <Badge key={genre} variant="secondary" className="text-xs">
                                    {genre}
                                </Badge>
                            ))}
                        </div>

                        <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
                            <Calendar className="h-3 w-3" />
                            <span>{formatDate(item.watched_at)}</span>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex flex-col gap-2">
                        <Button variant="ghost" size="icon" asChild>
                            <Link href={`/anime/${item.anime_id}`}>
                                <ExternalLink className="h-4 w-4" />
                                <span className="sr-only">Xem chi tiết</span>
                            </Link>
                        </Button>
                        {onRemove && (
                            <Button variant="ghost" size="icon" onClick={onRemove} className="text-destructive hover:text-destructive">
                                <Trash2 className="h-4 w-4" />
                                <span className="sr-only">Xóa khỏi lịch sử</span>
                            </Button>
                        )}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}

function HistoryList({ history, loading, onRemove }: { history: UserHistory[]; loading: boolean; onRemove?: (animeId: number) => void }) {
    if (loading) {
        return (
            <div className="space-y-4">
                {Array.from({ length: 5 }, (_, i) => (
                    <Card key={i} className="animate-pulse">
                        <CardContent className="p-4">
                            <div className="space-y-2">
                                <div className="h-5 bg-muted rounded w-3/4" />
                                <div className="h-4 bg-muted rounded w-1/4" />
                                <div className="flex gap-1">
                                    <div className="h-5 bg-muted rounded-full w-16" />
                                    <div className="h-5 bg-muted rounded-full w-12" />
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        );
    }

    if (history.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-16 text-center">
                <Film className="h-16 w-16 text-muted-foreground/50 mb-4" />
                <h3 className="text-lg font-semibold mb-2">Chưa có lịch sử xem</h3>
                <p className="text-muted-foreground mb-4">Bắt đầu xem anime để lưu lịch sử</p>
                <Button asChild>
                    <Link href="/anime">Khám phá anime</Link>
                </Button>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {history.map((item) => (
                <HistoryItem key={`${item.anime_id}-${item.watched_at}`} item={item} onRemove={onRemove ? () => onRemove(item.anime_id) : undefined} />
            ))}
        </div>
    );
}

export default function HistoryPage() {
    const { user, token, isAuthenticated, isLoading: authLoading } = useAuth();
    const router = useRouter();
    const [myHistory, setMyHistory] = useState<UserHistory[]>([]);
    const [otherUserHistory, setOtherUserHistory] = useState<UserHistory[]>([]);
    const [otherUserId, setOtherUserId] = useState("");
    const [loading, setLoading] = useState(true);
    const [searchLoading, setSearchLoading] = useState(false);
    const [searchError, setSearchError] = useState("");

    useEffect(() => {
        if (!authLoading && !isAuthenticated) {
            router.push("/login");
            return;
        }

        if (isAuthenticated && token) {
            // Fetch user's history from API
            const fetchHistory = async () => {
                setLoading(true);
                try {
                    const response = await api.getMyHistory(token, 1, 50);
                    // Transform API response to UserHistory format
                    const historyData: UserHistory[] = (response.history || []).map((item: any) => ({
                        user_id: response.user_id,
                        anime_id: item.anime_id,
                        watched_at: item.watched_at,
                        anime: {
                            name: item.anime_name || `Anime ${item.anime_id}`,
                            genre: item.anime_genres ? item.anime_genres.split(", ") : [],
                            rating: item.anime_score || 0,
                        },
                    }));
                    setMyHistory(historyData);
                } catch (error) {
                    console.error("Failed to fetch history:", error);
                    setMyHistory([]);
                } finally {
                    setLoading(false);
                }
            };
            fetchHistory();
        }
    }, [isAuthenticated, authLoading, token, router]);

    const handleSearchUser = async () => {
        if (!otherUserId.trim()) return;

        setSearchError("");
        setSearchLoading(true);

        const userId = Number.parseInt(otherUserId, 10);
        if (isNaN(userId) || userId < 0) {
            setSearchError("User ID không hợp lệ");
            setSearchLoading(false);
            return;
        }

        try {
            const response = await api.getUserHistory(userId, 1, 50);
            // Transform API response to UserHistory format
            const historyData: UserHistory[] = (response.history || []).map((item: any) => ({
                user_id: userId,
                anime_id: item.anime_id,
                watched_at: item.watched_at,
                anime: {
                    name: item.anime_name || `Anime ${item.anime_id}`,
                    genre: item.anime_genres ? item.anime_genres.split(", ") : [],
                    rating: item.anime_score || 0,
                },
            }));
            setOtherUserHistory(historyData);
        } catch (error) {
            console.error("Failed to fetch user history:", error);
            setSearchError("Không thể tải lịch sử của user này");
            setOtherUserHistory([]);
        } finally {
            setSearchLoading(false);
        }
    };

    const handleRemoveFromHistory = async (animeId: number) => {
        if (!token) return;

        try {
            await api.deleteFromHistory(token, animeId);
            // Only update local state after successful API call
            setMyHistory((prev) => prev.filter((h) => h.anime_id !== animeId));
        } catch (error) {
            console.error("Failed to delete from history:", error);
            // Could show a toast notification here
        }
    };

    if (authLoading || (!isAuthenticated && !authLoading)) {
        return <PageLoading />;
    }

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Header */}
            <div className="flex items-center gap-3 mb-8">
                <History className="h-8 w-8 text-primary" />
                <div>
                    <h1 className="text-3xl font-bold">Lịch sử xem</h1>
                    <p className="text-muted-foreground">Xem lại những anime bạn đã xem</p>
                </div>
            </div>

            {/* Tabs */}
            <Tabs defaultValue="my-history" className="space-y-6">
                <TabsList className="grid w-full max-w-md grid-cols-2">
                    <TabsTrigger value="my-history" className="gap-2">
                        <User className="h-4 w-4" />
                        Của tôi
                    </TabsTrigger>
                    <TabsTrigger value="other-user" className="gap-2">
                        <Search className="h-4 w-4" />
                        Xem user khác
                    </TabsTrigger>
                </TabsList>

                {/* My History Tab */}
                <TabsContent value="my-history">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center justify-between">
                                <span>Lịch sử xem của bạn</span>
                                {myHistory.length > 0 && <Badge variant="secondary">{myHistory.length} anime</Badge>}
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <HistoryList history={myHistory} loading={loading} onRemove={handleRemoveFromHistory} />
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Other User Tab */}
                <TabsContent value="other-user">
                    <Card>
                        <CardHeader>
                            <CardTitle>Xem lịch sử của user khác</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {/* Search Form */}
                            <div className="flex gap-2">
                                <div className="relative flex-1">
                                    <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                    <Input
                                        type="number"
                                        placeholder="Nhập User ID..."
                                        value={otherUserId}
                                        onChange={(e) => {
                                            setOtherUserId(e.target.value);
                                            setSearchError("");
                                        }}
                                        className="pl-10"
                                        min="0"
                                    />
                                </div>
                                <Button onClick={handleSearchUser} disabled={searchLoading}>
                                    {searchLoading ? "Đang tìm..." : "Tìm kiếm"}
                                </Button>
                            </div>

                            {searchError && <p className="text-sm text-destructive">{searchError}</p>}

                            {/* Results */}
                            {otherUserId && otherUserHistory.length > 0 && (
                                <div className="pt-4 border-t border-border">
                                    <h3 className="font-semibold mb-4">Lịch sử xem của User #{otherUserId}</h3>
                                    <HistoryList history={otherUserHistory} loading={searchLoading} />
                                </div>
                            )}

                            {otherUserId && !searchLoading && otherUserHistory.length === 0 && !searchError && (
                                <div className="text-center py-8 text-muted-foreground">User này chưa có lịch sử xem nào</div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
}
