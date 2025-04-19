import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";
import { ThemeProvider } from "@/components/provider/theme-provider"
import AuthCookieManager from "@/components/AuthCookieManager";
import { ModalProvider } from "@/components/provider/modal-provider";
import { Toaster } from "sonner";


const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Học tiếp - LMS",
  description: "DTA LMS - Hệ thống quản lý học tập",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <AuthProvider>
          <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
          >
            <AuthCookieManager />
            <ModalProvider />
            {children}
          </ThemeProvider>
        </AuthProvider>
        <Toaster
          toastOptions={{
            classNames: {
              success: "!bg-emerald-400 !text-white !border !border-green-300",
              error: "!bg-red-500 !text-white !border !border-red-300",
              warning: "!bg-yellow-400 !text-white !border !border-yellow-300",
              info: "!bg-blue-500 !text-white !border !border-blue-300",
              description: "text-sm opacity-80",
              closeButton: "hover:text-white"
            },
          }}
        />
      </body>
    </html>
  );
}
