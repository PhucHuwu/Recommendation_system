"use client";

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";
import { api } from "@/lib/api";
import type { User } from "@/types/user";

interface AuthContextType {
    user: User | null;
    token: string | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    login: (userId: number) => Promise<void>;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const USER_STORAGE_KEY = "wibiflix_user";
const TOKEN_STORAGE_KEY = "wibiflix_token";

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Check for stored user and token on mount
        const storedUser = localStorage.getItem(USER_STORAGE_KEY);
        const storedToken = localStorage.getItem(TOKEN_STORAGE_KEY);

        if (storedUser && storedToken) {
            try {
                setUser(JSON.parse(storedUser));
                setToken(storedToken);

                // Verify token is still valid by fetching current user
                api.getCurrentUser(storedToken)
                    .then((response) => {
                        // Update user with fresh data
                        const userData: User = {
                            user_id: response.user.user_id,
                            username: `User ${response.user.user_id}`,
                        };
                        setUser(userData);
                    })
                    .catch(() => {
                        // Token invalid, clear storage
                        localStorage.removeItem(USER_STORAGE_KEY);
                        localStorage.removeItem(TOKEN_STORAGE_KEY);
                        setUser(null);
                        setToken(null);
                    })
                    .finally(() => {
                        setIsLoading(false);
                    });
            } catch {
                localStorage.removeItem(USER_STORAGE_KEY);
                localStorage.removeItem(TOKEN_STORAGE_KEY);
                setIsLoading(false);
            }
        } else {
            setIsLoading(false);
        }
    }, []);

    const login = useCallback(async (userId: number) => {
        setIsLoading(true);
        try {
            // Call Backend API
            const response = await api.login(userId);

            const userData: User = {
                user_id: response.user.user_id,
                username: `User ${response.user.user_id}`,
            };

            setUser(userData);
            setToken(response.token);

            // Store in localStorage
            localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(userData));
            localStorage.setItem(TOKEN_STORAGE_KEY, response.token);
        } catch (error) {
            console.error("Login failed:", error);
            throw error;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const logout = useCallback(async () => {
        if (token) {
            try {
                await api.logout(token);
            } catch (error) {
                console.error("Logout API call failed:", error);
            }
        }

        setUser(null);
        setToken(null);
        localStorage.removeItem(USER_STORAGE_KEY);
        localStorage.removeItem(TOKEN_STORAGE_KEY);
    }, [token]);

    return (
        <AuthContext.Provider
            value={{
                user,
                token,
                isLoading,
                isAuthenticated: !!user && !!token,
                login,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
