// src/components/LogoutButton.tsx
"use client";

import { signOut } from "next-auth/react";
import { useRouter } from "next/navigation";
import { Button } from "../ui/button";
import axiosInstance from "@/lib/Api-Instance";
import { API_BASE_URL } from "@/constants/URL";

interface LogoutButtonProps {
  className?: string;
  children?: React.ReactNode;
}

export default function LogoutButton({ className, children }: LogoutButtonProps) {
  const router = useRouter();
  
  const handleLogout = async () => {
  
    // await axiosInstance.post(`${API_BASE_URL}/logout`)
    await signOut({ redirect: true, callbackUrl: "/" });
    // Chuyển hướng đến trang đăng nhập sau khi đăng xuất
    router.push("/");
  };
  
  return (
    <button 
      className={className || ""}
      onClick={handleLogout}
    >
      {children || "Đăng xuất"}
    </button>
  );
}