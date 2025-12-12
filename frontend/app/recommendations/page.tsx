"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/context/auth-context";
import { RecommendationList } from "@/components/recommendation/recommendation-list";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Sparkles, Zap, Users, Grid, Info } from "lucide-react";
import { api } from "@/lib/api";
import type { RecommendationResponse } from "@/types/api";

export default function RecommendationsPage() {
    const { user, token, isAuthenticated } = useAuth();

    // State for each model's recommendations
    const [neuralRecommendations, setNeuralRecommendations] = useState<RecommendationResponse[]>([]);
    const [hybridRecommendations, setHybridRecommendations] = useState<RecommendationResponse[]>([]);
    const [userBasedRecommendations, setUserBasedRecommendations] = useState<RecommendationResponse[]>([]);
    const [itemBasedRecommendations, setItemBasedRecommendations] = useState<RecommendationResponse[]>([]);

    // Loading states
    const [neuralLoading, setNeuralLoading] = useState(true);
    const [hybridLoading, setHybridLoading] = useState(true);
    const [userBasedLoading, setUserBasedLoading] = useState(true);
    const [itemBasedLoading, setItemBasedLoading] = useState(true);

    // Fetch recommendations for each model
    useEffect(() => {
        if (!isAuthenticated || !token) return;

        const fetchRecommendations = async () => {
            // Fetch Neural CF recommendations
            try {
                setNeuralLoading(true);
                const response = await api.getRecommendations(token, 12, "neural_cf");
                setNeuralRecommendations(response.recommendations || []);
            } catch (error) {
                console.error("Failed to fetch Neural CF recommendations:", error);
            } finally {
                setNeuralLoading(false);
            }

            // Fetch Hybrid recommendations
            try {
                setHybridLoading(true);
                const response = await api.getRecommendations(token, 12, "hybrid");
                setHybridRecommendations(response.recommendations || []);
            } catch (error) {
                console.error("Failed to fetch Hybrid recommendations:", error);
            } finally {
                setHybridLoading(false);
            }

            // Fetch User-Based CF recommendations
            try {
                setUserBasedLoading(true);
                const response = await api.getRecommendations(token, 12, "user_based_cf");
                setUserBasedRecommendations(response.recommendations || []);
            } catch (error) {
                console.error("Failed to fetch User-Based CF recommendations:", error);
            } finally {
                setUserBasedLoading(false);
            }

            // Fetch Item-Based CF recommendations
            try {
                setItemBasedLoading(true);
                const response = await api.getRecommendations(token, 12, "item_based_cf");
                setItemBasedRecommendations(response.recommendations || []);
            } catch (error) {
                console.error("Failed to fetch Item-Based CF recommendations:", error);
            } finally {
                setItemBasedLoading(false);
            }
        };

        fetchRecommendations();
    }, [isAuthenticated, token]);

    if (!isAuthenticated) {
        return (
            <div className="container mx-auto px-4 py-16 text-center">
                <Sparkles className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <h1 className="text-3xl font-bold mb-4">Gợi ý cá nhân hóa</h1>
                <p className="text-muted-foreground mb-6">Vui lòng đăng nhập để xem gợi ý từ các mô hình AI</p>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">Gợi ý cá nhân hóa</h1>
                <p className="text-muted-foreground">Khám phá anime được đề xuất bởi các mô hình AI khác nhau</p>
            </div>

            {/* Info Alert */}
            <Alert className="mb-8">
                <Info className="h-4 w-4" />
                <AlertDescription>
                    Mỗi mô hình AI sử dụng thuật toán khác nhau để đề xuất anime phù hợp với sở thích của bạn. Hãy khám phá và tìm anime yêu thích!
                </AlertDescription>
            </Alert>

            <div className="space-y-12">
                {/* Neural CF Recommendations */}
                <section>
                    <div className="flex items-center gap-3 mb-4">
                        <Sparkles className="h-6 w-6 text-purple-500" />
                        <h2 className="text-2xl font-bold">Neural CF</h2>
                        <Badge variant="secondary" className="bg-purple-500/10 text-purple-500 border-purple-500/20">
                            Deep Learning
                        </Badge>
                    </div>
                    <p className="text-muted-foreground mb-4">
                        Sử dụng mạng neural network (deep learning) để học các patterns phức tạp từ lịch sử đánh giá của bạn. Mô hình này có khả năng phát hiện
                        những mối liên hệ tinh vi giữa người dùng và anime, mang lại gợi ý chính xác và đa dạng nhất.
                    </p>
                    <RecommendationList title="" items={neuralRecommendations} loading={neuralLoading} showScrollButtons={true} />
                </section>

                {/* Hybrid Recommendations */}
                <section>
                    <div className="flex items-center gap-3 mb-4">
                        <Zap className="h-6 w-6 text-amber-500" />
                        <h2 className="text-2xl font-bold">Hybrid</h2>
                        <Badge variant="secondary" className="bg-amber-500/10 text-amber-500 border-amber-500/20">
                            Kết hợp
                        </Badge>
                    </div>
                    <p className="text-muted-foreground mb-4">
                        Kết hợp thông minh giữa User-Based CF và Item-Based CF để tận dụng ưu điểm của cả hai phương pháp. Mô hình này cân bằng giữa việc tìm
                        anime mà người dùng tương tự thích và anime có nội dung tương đồng với những gì bạn đã xem.
                    </p>
                    <RecommendationList title="" items={hybridRecommendations} loading={hybridLoading} showScrollButtons={true} />
                </section>

                {/* User-Based CF Recommendations */}
                <section>
                    <div className="flex items-center gap-3 mb-4">
                        <Users className="h-6 w-6 text-blue-500" />
                        <h2 className="text-2xl font-bold">User-Based CF</h2>
                        <Badge variant="secondary" className="bg-blue-500/10 text-blue-500 border-blue-500/20">
                            Dựa trên người dùng
                        </Badge>
                    </div>
                    <p className="text-muted-foreground mb-4">
                        Tìm những người dùng có sở thích tương tự với bạn (dựa trên lịch sử đánh giá), sau đó gợi ý anime mà họ thích nhưng bạn chưa xem. Phương
                        pháp này đặc biệt hiệu quả khi khám phá anime mới ngoài thể loại quen thuộc.
                    </p>
                    <RecommendationList title="" items={userBasedRecommendations} loading={userBasedLoading} showScrollButtons={true} />
                </section>

                {/* Item-Based CF Recommendations */}
                <section>
                    <div className="flex items-center gap-3 mb-4">
                        <Grid className="h-6 w-6 text-green-500" />
                        <h2 className="text-2xl font-bold">Item-Based CF</h2>
                        <Badge variant="secondary" className="bg-green-500/10 text-green-500 border-green-500/20">
                            Dựa trên nội dung
                        </Badge>
                    </div>
                    <p className="text-muted-foreground mb-4">
                        Phân tích mối tương quan giữa các anime dựa trên patterns đánh giá của tất cả người dùng. Nếu bạn thích một anime, mô hình sẽ tìm những
                        anime khác được đánh giá tương tự bởi cộng đồng - giúp bạn tìm thấy những tác phẩm "an toàn" và phù hợp với khẩu vị.
                    </p>
                    <RecommendationList title="" items={itemBasedRecommendations} loading={itemBasedLoading} showScrollButtons={true} />
                </section>
            </div>
        </div>
    );
}
