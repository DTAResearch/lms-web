import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";
import { GoogleOAuthProvider } from '@react-oauth/google';
import { ThemeProvider } from "@/components/provider/theme-provider"
import AuthCookieManager from "@/components/AuthCookieManager";
import { ModalProvider } from "@/components/provider/modal-provider";
import { Toaster } from "@/components/ui/sonner"
import { I18nProvider } from "@/components/provider/i18nProvider";


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
        <GoogleOAuthProvider clientId={process.env.GOOGLE_CLIENT_ID || ""}>
          <I18nProvider>
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
              richColors={false}
              position="top-center"
            />
          </I18nProvider>
        </GoogleOAuthProvider>
      </body>
    </html>
  );
}
