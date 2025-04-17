// src/app/error/page.tsx
"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";

export default function ErrorPage() {
  const searchParams = useSearchParams();
  const error = searchParams.get("error");
  
  let errorMessage = "Có lỗi xảy ra";
  let errorDescription = "Vui lòng thử lại sau";
  
  if (error === "AccessDenied") {
    errorMessage = "Không có quyền truy cập";
    errorDescription = "Tài khoản của bạn không có quyền truy cập vào ứng dụng này";
  } else if (error === "OAuthSignin" || error === "OAuthCallback") {
    errorMessage = "Lỗi đăng nhập với Google";
    errorDescription = "Không thể kết nối với dịch vụ Google, vui lòng thử lại sau";
  } else if (error === "Verification") {
    errorMessage = "Không thể xác thực tài khoản";
    errorDescription = "Liên kết xác thực không hợp lệ hoặc đã hết hạn";
  }
  
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 px-4">
      <div className="bg-white p-8 rounded-lg shadow-md max-w-lg w-full text-center">
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        
        <h1 className="text-2xl font-bold mb-4 text-gray-800">{errorMessage}</h1>
        <p className="text-gray-600 mb-8">{errorDescription}</p>
        
        <div className="flex flex-col gap-4">
          <Link 
            href="/auth/login" 
            className="w-full bg-sky-500 text-white py-2 px-4 rounded transition hover:bg-sky-600"
          >
            Quay lại đăng nhập
          </Link>
          <Link
            href="/"
            className="w-full border border-gray-300 text-gray-700 py-2 px-4 rounded transition hover:bg-gray-50"
          >
            Về trang chủ
          </Link>
        </div>
      </div>
    </div>
  )
}