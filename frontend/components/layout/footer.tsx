import Link from "next/link";
import { Film, Github, Twitter } from "lucide-react";

export function Footer() {
    return (
        <footer className="border-t border-border bg-card">
            <div className="container mx-auto px-4 py-8">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                    {/* Brand */}
                    <div className="col-span-1 md:col-span-2">
                        <Link href="/" className="flex items-center gap-2 mb-4">
                            <Film className="h-6 w-6 text-primary" />
                            <span className="text-lg font-bold">WibiFlix</span>
                        </Link>
                        <p className="text-sm text-muted-foreground max-w-md">
                            Hệ thống gợi ý phim Anime thông minh, giúp bạn khám phá những bộ anime phù hợp với sở thích của mình.
                        </p>
                    </div>

                    {/* Links */}
                    <div>
                        <h3 className="font-semibold mb-4">Khám phá</h3>
                        <ul className="space-y-2 text-sm">
                            <li>
                                <Link href="/anime" className="text-muted-foreground hover:text-foreground transition-colors">
                                    Danh sách Anime
                                </Link>
                            </li>
                            <li>
                                <Link href="/search" className="text-muted-foreground hover:text-foreground transition-colors">
                                    Tìm kiếm
                                </Link>
                            </li>
                            <li>
                                <Link href="/anime?sort=rating" className="text-muted-foreground hover:text-foreground transition-colors">
                                    Top Anime
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* Account */}
                    <div>
                        <h3 className="font-semibold mb-4">Tài khoản</h3>
                        <ul className="space-y-2 text-sm">
                            <li>
                                <Link href="/login" className="text-muted-foreground hover:text-foreground transition-colors">
                                    Đăng nhập
                                </Link>
                            </li>
                            <li>
                                <Link href="/history" className="text-muted-foreground hover:text-foreground transition-colors">
                                    Lịch sử xem
                                </Link>
                            </li>
                            <li>
                                <Link href="/profile" className="text-muted-foreground hover:text-foreground transition-colors">
                                    Profile
                                </Link>
                            </li>
                        </ul>
                    </div>
                </div>

                <div className="flex flex-col md:flex-row items-center justify-between gap-4 mt-8 pt-8 border-t border-border">
                    <p className="text-sm text-muted-foreground">© 2025 WibiFlix. All rights reserved.</p>
                    <div className="flex items-center gap-4">
                        <a
                            href="https://github.com"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-muted-foreground hover:text-foreground transition-colors"
                        >
                            <Github className="h-5 w-5" />
                            <span className="sr-only">GitHub</span>
                        </a>
                        <a
                            href="https://twitter.com"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-muted-foreground hover:text-foreground transition-colors"
                        >
                            <Twitter className="h-5 w-5" />
                            <span className="sr-only">Twitter</span>
                        </a>
                    </div>
                </div>
            </div>
        </footer>
    );
}
