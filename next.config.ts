import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  eslint: {
    ignoreDuringBuilds: true, // Bỏ qua ESLint khi chạy "next build"
  },
  // output: "standalone",

};

export default nextConfig;
