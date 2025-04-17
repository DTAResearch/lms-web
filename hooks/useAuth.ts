// src/hooks/useAuth.ts
"use client";

import { useSession } from "next-auth/react";
import { useRouter, usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { Role } from "@/constants/Role";

export function useAuth(requiredRoles?: string[]) {
  const { data: session, status } = useSession();
  const router = useRouter();
  const pathname = usePathname();
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    // Nếu đang loading, chờ
    if (status === "loading") return;
    
    // Nếu không đăng nhập, chuyển hướng đến login
    if (status === "unauthenticated") {
      router.push(`/login?returnUrl=${encodeURIComponent(pathname)}`);
      return;
    }
    
    // Nếu không cần kiểm tra role, đã đăng nhập là đủ
    if (!requiredRoles || requiredRoles.length === 0) {
      setIsAuthorized(true);
      setIsLoading(false);
      return;
    }
    
    // Kiểm tra role
    const userRole = session?.user?.role;
    if (userRole && requiredRoles.includes(userRole)) {
      setIsAuthorized(true);
    } else {
      // Chuyển hướng dựa trên role của người dùng nếu không có quyền
      if (userRole === Role.ADMIN) {
        router.push("/admin");
      } else if (userRole === Role.TEACHER) {
        router.push("/teacher");
      } else if (userRole === Role.STUDENT) {
        router.push("/student");
      } else {
        router.push("/auth/login?returnUrl=/login"); // Nếu không có role cụ thể, chuyển hướng về login
      }
    }
    
    setIsLoading(false);
  }, [status, session, router, pathname, requiredRoles]);
  
  return { isAuthorized, isLoading };
}