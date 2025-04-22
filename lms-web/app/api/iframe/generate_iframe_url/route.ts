// src/app/api/iframe/generate_iframe_url/route.ts
import { NextRequest, NextResponse } from "next/server";
import { useSession } from "next-auth/react";
import { API_BASE_URL } from "@/constants/URL";
import axiosInstance from "@/lib/Api-Instance";


export async function GET(request: NextRequest) {
  try {
    const { data: session } =  useSession();
    
    if (!session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }
    
    // Gọi API backend để lấy URL iframe
    const response = await axiosInstance.get(`${API_BASE_URL}/iframe/generate_iframe_url`);
    
    return NextResponse.json({ data: response.data.data });
  } catch (error: any) {
    console.error("Error fetching iframe URL:", error);
    return NextResponse.json(
      { error: "Failed to generate iframe URL" },
      { status: error.response?.status || 500 }
    );
  }
}