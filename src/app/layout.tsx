"use client";

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Toaster } from "sonner";
import "@/app/globals.css"; // Đảm bảo đường dẫn đúng
import { ThemeProvider } from "@/components/theme-provider"; // Sẽ tạo component này sau

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" }); // Thêm variable cho font

export const metadata: Metadata = {
  title: "EduScan - Hệ thống quản lý giáo dục",
  description: "EduScan - Nền tảng quản lý giáo dục và chấm điểm tự động.",
  // Thêm các metadata khác nếu cần, ví dụ icons
  icons: {
    icon: "/favicon.ico", // Đảm bảo có file này trong public
    // apple: "/apple-touch-icon.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased min-h-screen bg-background text-foreground`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
          <Toaster position="top-center" richColors closeButton />
        </ThemeProvider>
      </body>
    </html>
  );
} 