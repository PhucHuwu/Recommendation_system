import type React from "react"
import type { Metadata, Viewport } from "next"
import { Inter, Geist_Mono } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import { AuthProvider } from "@/context/auth-context"
import { Header } from "@/components/layout/header"
import { Footer } from "@/components/layout/footer"
import "./globals.css"

const inter = Inter({ subsets: ["latin", "vietnamese"] })
const _geistMono = Geist_Mono({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Wibiflix - Hệ thống gợi ý Anime",
  description: "Khám phá và nhận gợi ý anime phù hợp với sở thích của bạn với hệ thống AI thông minh",
  keywords: ["anime", "recommendation", "wibiflix", "gợi ý anime", "phim anime"],
  authors: [{ name: "Wibiflix Team" }],
    generator: 'v0.app'
}

export const viewport: Viewport = {
  themeColor: "#6366f1",
  width: "device-width",
  initialScale: 1,
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="vi">
      <body className="font-sans antialiased min-h-screen flex flex-col">
        <AuthProvider>
          <Header />
          <main className="flex-1">{children}</main>
          <Footer />
        </AuthProvider>
        <Analytics />
      </body>
    </html>
  )
}
