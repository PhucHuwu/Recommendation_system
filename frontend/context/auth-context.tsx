"use client"

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react"
import type { User } from "@/types/user"

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (userId: number) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const USER_STORAGE_KEY = "wibiflix_user"

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check for stored user on mount
    const storedUser = localStorage.getItem(USER_STORAGE_KEY)
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser))
      } catch {
        localStorage.removeItem(USER_STORAGE_KEY)
      }
    }
    setIsLoading(false)
  }, [])

  const login = useCallback(async (userId: number) => {
    setIsLoading(true)
    try {
      // In a real app, this would call the API
      // For now, we'll create a mock user
      const newUser: User = {
        user_id: userId,
        username: `User ${userId}`,
      }
      setUser(newUser)
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(newUser))
    } finally {
      setIsLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    setUser(null)
    localStorage.removeItem(USER_STORAGE_KEY)
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
