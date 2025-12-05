"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { AnimeList } from "@/components/anime/anime-list";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Search, Filter, X, ChevronLeft, ChevronRight } from "lucide-react";
import { useDebounce } from "@/hooks/use-debounce";
import { api } from "@/lib/api";
import type { Anime } from "@/types/anime";

const ITEMS_PER_PAGE = 20;

export default function AnimePage() {
    const router = useRouter();
    const searchParams = useSearchParams();

    const [animes, setAnimes] = useState<Anime[]>([]);
    const [genres, setGenres] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState(searchParams.get("search") || "");
    const [selectedGenre, setSelectedGenre] = useState(searchParams.get("genre") || "");
    const [sortBy, setSortBy] = useState(searchParams.get("sort") || "score");
    const [currentPage, setCurrentPage] = useState(Number(searchParams.get("page")) || 1);
    const [totalPages, setTotalPages] = useState(1);
    const [total, setTotal] = useState(0);

    const debouncedSearch = useDebounce(searchQuery, 300);

    // Fetch genres on mount
    useEffect(() => {
        const fetchGenres = async () => {
            try {
                const response = await api.getGenres();
                setGenres(response.genres || []);
            } catch (error) {
                console.error("Failed to fetch genres:", error);
            }
        };
        fetchGenres();
    }, []);

    // Fetch animes
    useEffect(() => {
        const fetchAnimes = async () => {
            setLoading(true);
            try {
                if (debouncedSearch) {
                    // Use search API
                    const response = await api.searchAnime(debouncedSearch, ITEMS_PER_PAGE);
                    setAnimes(response.animes || []);
                    setTotal(response.count || 0);
                    setTotalPages(1); // Search doesn't use pagination
                } else {
                    // Use regular anime list API
                    const response = await api.getAnimes({
                        page: currentPage,
                        limit: ITEMS_PER_PAGE,
                        genre: selectedGenre,
                        sort: sortBy,
                        order: "desc",
                    });
                    setAnimes(response.animes || []);
                    setTotal(response.total || 0);
                    setTotalPages(response.pages || 1);
                }
            } catch (error) {
                console.error("Failed to fetch animes:", error);
                setAnimes([]);
            } finally {
                setLoading(false);
            }
        };

        fetchAnimes();
    }, [debouncedSearch, selectedGenre, sortBy, currentPage]);

    // Update URL params
    useEffect(() => {
        const params = new URLSearchParams();
        if (searchQuery) params.set("search", searchQuery);
        if (selectedGenre) params.set("genre", selectedGenre);
        if (sortBy !== "score") params.set("sort", sortBy);
        if (currentPage > 1) params.set("page", currentPage.toString());

        const newUrl = params.toString() ? `?${params.toString()}` : "/anime";
        router.replace(newUrl, { scroll: false });
    }, [searchQuery, selectedGenre, sortBy, currentPage, router]);

    const clearFilters = () => {
        setSearchQuery("");
        setSelectedGenre("");
        setSortBy("score");
        setCurrentPage(1);
    };

    const hasFilters = searchQuery || selectedGenre || sortBy !== "score";

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">Danh sách Anime</h1>
                <p className="text-muted-foreground">Khám phá {total.toLocaleString()} anime từ database</p>
            </div>

            {/* Filters */}
            <div className="flex flex-col gap-4 mb-8">
                <div className="flex flex-col sm:flex-row gap-4">
                    {/* Search */}
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input
                            type="search"
                            placeholder="Tìm kiếm anime..."
                            value={searchQuery}
                            onChange={(e) => {
                                setSearchQuery(e.target.value);
                                setCurrentPage(1);
                            }}
                            className="pl-10"
                        />
                    </div>

                    {/* Genre Filter */}
                    <Select
                        value={selectedGenre}
                        onValueChange={(value) => {
                            setSelectedGenre(value === "all" ? "" : value);
                            setCurrentPage(1);
                        }}
                    >
                        <SelectTrigger className="w-full sm:w-48">
                            <Filter className="h-4 w-4 mr-2" />
                            <SelectValue placeholder="Thể loại" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">Tất cả thể loại</SelectItem>
                            {genres.map((genre) => (
                                <SelectItem key={genre} value={genre}>
                                    {genre}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>

                    {/* Sort */}
                    <Select
                        value={sortBy}
                        onValueChange={(value) => {
                            setSortBy(value);
                            setCurrentPage(1);
                        }}
                    >
                        <SelectTrigger className="w-full sm:w-48">
                            <SelectValue placeholder="Sắp xếp theo" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="score">Điểm đánh giá</SelectItem>
                            <SelectItem value="name">Tên A-Z</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                {/* Active filters */}
                {hasFilters && (
                    <div className="flex flex-wrap items-center gap-2">
                        <span className="text-sm text-muted-foreground">Đang lọc:</span>
                        {searchQuery && (
                            <Badge variant="secondary" className="gap-1">
                                Tìm: {searchQuery}
                                <button onClick={() => setSearchQuery("")}>
                                    <X className="h-3 w-3" />
                                </button>
                            </Badge>
                        )}
                        {selectedGenre && (
                            <Badge variant="secondary" className="gap-1">
                                {selectedGenre}
                                <button onClick={() => setSelectedGenre("")}>
                                    <X className="h-3 w-3" />
                                </button>
                            </Badge>
                        )}
                        <Button variant="ghost" size="sm" onClick={clearFilters}>
                            Xóa bộ lọc
                        </Button>
                    </div>
                )}
            </div>

            {/* Anime Grid */}
            <AnimeList animes={animes} loading={loading} emptyMessage="Không tìm thấy anime nào phù hợp với bộ lọc" />

            {/* Pagination */}
            {!loading && totalPages > 1 && !searchQuery && (
                <div className="flex items-center justify-center gap-2 mt-8">
                    <Button variant="outline" size="icon" disabled={currentPage === 1} onClick={() => setCurrentPage((p) => p - 1)}>
                        <ChevronLeft className="h-4 w-4" />
                        <span className="sr-only">Trang trước</span>
                    </Button>

                    <div className="flex items-center gap-1">
                        {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                            let page: number;
                            if (totalPages <= 5) {
                                page = i + 1;
                            } else if (currentPage <= 3) {
                                page = i + 1;
                            } else if (currentPage >= totalPages - 2) {
                                page = totalPages - 4 + i;
                            } else {
                                page = currentPage - 2 + i;
                            }

                            return (
                                <Button key={page} variant={currentPage === page ? "default" : "outline"} size="icon" onClick={() => setCurrentPage(page)}>
                                    {page}
                                </Button>
                            );
                        })}
                    </div>

                    <Button variant="outline" size="icon" disabled={currentPage === totalPages} onClick={() => setCurrentPage((p) => p + 1)}>
                        <ChevronRight className="h-4 w-4" />
                        <span className="sr-only">Trang sau</span>
                    </Button>

                    <span className="text-sm text-muted-foreground ml-4">
                        Trang {currentPage} / {totalPages}
                    </span>
                </div>
            )}
        </div>
    );
}
