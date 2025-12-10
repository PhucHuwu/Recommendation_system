"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { AnimeList } from "@/components/anime/anime-list";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, X, Film, Sparkles } from "lucide-react";
import { useDebounce } from "@/hooks/use-debounce";
import { api } from "@/lib/api";
import type { Anime } from "@/types/anime";

type SearchMode = "text" | "vector";

function SearchContent() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const initialQuery = searchParams.get("q") || "";
    const initialMode = (searchParams.get("mode") as SearchMode) || "text";

    const [query, setQuery] = useState(initialQuery);
    const [searchMode, setSearchMode] = useState<SearchMode>(initialMode);
    const [results, setResults] = useState<Anime[]>([]);
    const [loading, setLoading] = useState(false);
    const [hasSearched, setHasSearched] = useState(!!initialQuery);
    const [totalResults, setTotalResults] = useState(0);

    const debouncedQuery = useDebounce(query, 300);

    useEffect(() => {
        const search = async () => {
            if (!debouncedQuery.trim()) {
                setResults([]);
                setHasSearched(false);
                setTotalResults(0);
                return;
            }

            setLoading(true);
            setHasSearched(true);

            try {
                if (searchMode === "vector") {
                    // Vector search
                    const response = await api.vectorSearch(debouncedQuery, 50);
                    setResults(response.animes || []);
                    setTotalResults(response.count || 0);
                } else {
                    // Text search
                    const response = await api.searchAnime(debouncedQuery, 50);
                    setResults(response.animes || []);
                    setTotalResults(response.count || 0);
                }
            } catch (error) {
                console.error("Search failed:", error);
                setResults([]);
                setTotalResults(0);
            } finally {
                setLoading(false);
            }

            // Update URL
            router.replace(`/search?q=${encodeURIComponent(debouncedQuery)}&mode=${searchMode}`, { scroll: false });
        };

        search();
    }, [debouncedQuery, searchMode, router]);

    const clearSearch = () => {
        setQuery("");
        setResults([]);
        setHasSearched(false);
        router.replace("/search", { scroll: false });
    };

    const toggleSearchMode = () => {
        const newMode = searchMode === "text" ? "vector" : "text";
        setSearchMode(newMode);
        // Trigger re-search if there's a query
        if (debouncedQuery.trim()) {
            setHasSearched(false);
        }
    };

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">Tìm kiếm Anime</h1>
                <p className="text-muted-foreground">
                    {searchMode === "vector" ? "Tìm kiếm ngữ nghĩa - mô tả nội dung anime bạn muốn tìm" : "Nhập tên anime bạn muốn tìm"}
                </p>
            </div>

            {/* Search Mode Toggle */}
            <div className="flex gap-2 mb-4 max-w-2xl">
                <Button variant={searchMode === "text" ? "default" : "outline"} onClick={() => setSearchMode("text")} className="flex-1">
                    <Search className="h-4 w-4 mr-2" />
                    Text Search
                </Button>
                <Button variant={searchMode === "vector" ? "default" : "outline"} onClick={() => setSearchMode("vector")} className="flex-1">
                    <Sparkles className="h-4 w-4 mr-2" />
                    Semantic Search
                </Button>
            </div>

            {/* Search Input */}
            <div className="relative max-w-2xl mb-8">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <Input
                    type="search"
                    placeholder={searchMode === "vector" ? "Ví dụ: anime with mecha robot fight, romantic comedy school..." : "Tìm kiếm anime..."}
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="pl-12 pr-12 h-14 text-lg"
                    autoFocus
                />
                {query && (
                    <Button variant="ghost" size="icon" className="absolute right-2 top-1/2 -translate-y-1/2" onClick={clearSearch}>
                        <X className="h-5 w-5" />
                        <span className="sr-only">Xóa tìm kiếm</span>
                    </Button>
                )}
            </div>

            {/* Results */}
            {hasSearched ? (
                <>
                    {!loading && results.length > 0 && (
                        <p className="text-muted-foreground mb-6">
                            Tìm thấy <span className="font-medium text-foreground">{totalResults}</span> kết quả
                            {searchMode === "vector" ? " (semantic search)" : ""} cho "{debouncedQuery}"
                        </p>
                    )}
                    <AnimeList animes={results} loading={loading} emptyMessage={`Không tìm thấy kết quả cho "${debouncedQuery}"`} />
                </>
            ) : (
                <div className="flex flex-col items-center justify-center py-16 text-center">
                    {searchMode === "vector" ? (
                        <Sparkles className="h-16 w-16 text-muted-foreground/50 mb-4" />
                    ) : (
                        <Film className="h-16 w-16 text-muted-foreground/50 mb-4" />
                    )}
                    <h2 className="text-xl font-semibold mb-2">Bắt đầu tìm kiếm</h2>
                    <p className="text-muted-foreground max-w-md">
                        {searchMode === "vector"
                            ? "Mô tả anime bạn muốn tìm bằng ngôn ngữ tự nhiên. Ví dụ: 'action anime with magic and fighting'"
                            : "Nhập tên anime vào ô tìm kiếm để tìm những bộ anime bạn yêu thích"}
                    </p>
                </div>
            )}
        </div>
    );
}

export default function SearchPage() {
    return (
        <Suspense fallback={<div className="container mx-auto px-4 py-8">Đang tải...</div>}>
            <SearchContent />
        </Suspense>
    );
}
