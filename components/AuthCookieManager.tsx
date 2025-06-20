'use client';

import { useSession } from "next-auth/react";
import { useEffect } from "react";
import Cookies from "js-cookie";
import axiosInstance from "@/lib/Api-Instance";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export default function AuthCookieManager() {
  const { data: session } = useSession();

  // useEffect(() => {
  //   if (session?.user?.accessToken) {
  //     // Set the cookie with the backend token (unencoded)
  //     Cookies.set('access_token', session.user.accessToken, {
  //       path: '/',
  //       sameSite: 'lax'
  //     });
  //   }
  // }, [session]);

  // useEffect(() => {
  //   const fetchUserData = async () => {
  //     if (session?.user?.loginType === "google" || session?.user?.loginType === "outlook") {
  //       if (session.user.accessToken) {
  //         document.cookie = `access_token=${session.user.accessToken}; path=/; secure; samesite=strict`;
  //       }

  //       const userData = await axiosInstance.get(`${API_BASE_URL}/users/me`)
  //       // lưu user vào localStorage để sử dụng sau này
  //       localStorage.setItem("user", JSON.stringify(userData.data));
  //     }
  //   };

  //   fetchUserData();
  // }, [session]);

  return null; // This component doesn't render anything
}