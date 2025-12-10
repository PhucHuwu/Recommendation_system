"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { AnimeList } from "@/components/anime/anime-list";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Search, X, Film, Sparkles } from "lucide-react";
import { useDebounce } from "@/hooks/use-debounce";
import { api } from "@/lib/api";
import type { Anime } from "@/types/anime";

function SearchContent() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const initialQuery = searchParams.get("q") || "";

    const [query, setQuery] = useState(initialQuery);
    const [results, setResults] = useState<Anime[]>([]);
    const [loading, setLoading] = useState(false);
    const [hasSearched, setHasSearched] = useState(!!initialQuery);
    const [totalResults, setTotalResults] = useState(0);
    const [useVectorSearch, setUseVectorSearch] = useState(true); // Default to vector search

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
                if (useVectorSearch) {
                    // Use vector search with FAISS
                    const response = await api.vectorSearch(debouncedQuery, 50);
                    setResults(response.animes || []);
                    setTotalResults(response.count || 0);
                } else {
                    // Use traditional text search
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
            router.replace(`/search?q=${encodeURIComponent(debouncedQuery)}`, { scroll: false });
        };

        search();
    }, [debouncedQuery, useVectorSearch, router]);

    const clearSearch = () => {
        setQuery("");
        setResults([]);
        setHasSearched(false);
        router.replace("/search", { scroll: false });
    };

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">Tìm kiếm Anime</h1>
                <p className="text-muted-foreground">{useVectorSearch ? "Tìm kiếm thông minh với AI - hỗ trợ tiếng Việt" : "Tìm kiếm theo tên anime"}</p>
            </div>

            {/* Search Mode Toggle */}
            <div className="flex items-center gap-3 mb-6 p-4 rounded-lg border bg-card">
                <Sparkles className={`h-5 w-5 ${useVectorSearch ? "text-primary" : "text-muted-foreground"}`} />
                <div className="flex items-center gap-3 flex-1">
                    <Label htmlFor="vector-search-mode" className="cursor-pointer flex-1">
                        <span className="font-medium">Tìm kiếm thông minh (AI)</span>
                        <span className="block text-sm text-muted-foreground">Tìm kiếm theo ý nghĩa, hỗ trợ tiếng Việt</span>
                    </Label>
                    <Switch id="vector-search-mode" checked={useVectorSearch} onCheckedChange={setUseVectorSearch} />
                </div>
            </div>

            {/* Search Input */}
            <div className="relative max-w-2xl mb-8">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <Input
                    type="search"
                    placeholder={useVectorSearch ? "VD: anime hành động với phép thuật, chiến đấu và rồng..." : "Tìm kiếm anime..."}
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
                            Tìm thấy <span className="font-medium text-foreground">{totalResults}</span> kết quả cho "{debouncedQuery}"
                        </p>
                    )}
                    <AnimeList animes={results} loading={loading} emptyMessage={`Không tìm thấy kết quả cho "${debouncedQuery}"`} />
                </>
            ) : (
                <div className="flex flex-col items-center justify-center py-16 text-center">
                    <Film className="h-16 w-16 text-muted-foreground/50 mb-4" />
                    <h2 className="text-xl font-semibold mb-2">Bắt đầu tìm kiếm</h2>
                    <p className="text-muted-foreground max-w-md">Nhập tên anime vào ô tìm kiếm để tìm những bộ anime bạn yêu thích</p>
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
