// src/lib/axiosInstance.ts
"use client";

import axios from "axios";
import { getSession, signOut } from "next-auth/react";
import "next-auth";
import { Role } from "@/constants/Role";
import { URL_LOGIN } from "@/constants/URL";

// Extend the Session type to include accessToken
declare module "next-auth" {
  interface Session {
    user: {
      name?: string | null;
      email?: string | null;
      image?: string | null;
      accessToken?: string;
      backendToken?: string | null; // Add this line
      loginType?: string | null;
      role?: Role;
    }
  }
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/json',
  },
});

// Thêm interceptor để tự động thêm token vào mỗi request
// axiosInstance.interceptors.request.use(
//   async (config) => {
//     const session = await getSession();
//     if (session?.user?.accessToken) {
//       config.headers.Authorization = `Bearer ${session.user.accessToken}`;
//     }
//     return config;
//   },
//   (error) => {
//     return Promise.reject(error);
//   }
// );

// Xử lý lỗi từ API
// axiosInstance.interceptors.response.use(
//   (response) => {
//     return response;
//   },
//   async (error) => {
//     const originalRequest = error.config;

//     // Nếu token hết hạn (401), đăng xuất người dùng
//     if (error.response?.status === 401 && !originalRequest._retry) {
//       originalRequest._retry = true;
//       await signOut({ redirect: false });
//       window.location.href = URL_LOGIN;
//       return Promise.reject(error);
//     }

//     return Promise.reject(error);
//   }
// );

// axiosInstance.interceptors.request.use(config => {
//   if (typeof window !== "undefined") {
//     const token = localStorage.getItem("access_token");
//     console.log("token", token);
//     if (token) {
//       config.headers.Authorization = `access_token=${token}`;
//     }
//   }
//   return config;
// }, error => {
//   return Promise.reject(error);
// });

export default axiosInstance;