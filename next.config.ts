import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  eslint: {
    ignoreDuringBuilds: true, // Bỏ qua ESLint khi chạy "next build"
  },
  // output: "standalone",

  // Cấu hình đa ngôn ngữ
  i18n: {
    locales: ['vi', 'en'],
    defaultLocale: 'vi',
    localeDetection: false, // Không tự đổi URL theo trình duyệt
  },

};

export default nextConfig;
