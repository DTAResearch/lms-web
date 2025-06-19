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
      loginType?: "google" | "local" | "outlook";
      role?: Role;
      password_changed?: boolean;
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


export default axiosInstance;