// src/app/dashboard/page.tsx
"use client";

import { useSession } from "next-auth/react";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Role } from "@/constants/Role";

export default function Dashboard() {
  const { data: session, status } = useSession();
  const router = useRouter();
  
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/auth/login");
      return;
    }
    
    if (status === "authenticated" && session?.user) {
      const role = session.user.role;
      
      // Chuyển hướng dựa trên role
      switch (role) {
        case Role.ADMIN:
          router.push("/admin");
          break;
        case Role.TEACHER:
          router.push("/teacher");
          break;
        case Role.STUDENT:
          router.push("/student");
          break;
        default:
          // Nếu không có role cụ thể, ở lại dashboard
          break;
      }
    }
  }, [session, status, router]);
  
  if (status === "loading") {
    return (
      <div className="h-screen flex justify-center items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-sky-500"></div>
        <p className="ml-2">Đang tải...</p>
      </div>
    );
  }
  
  return (
    <div className="h-screen flex justify-center items-center">
      <p>Chuyển hướng...</p>
    </div>
  );
}