// src/app/api/iframe/generate_iframe_url/route.ts
import { getServerSession } from "next-auth";
import { authOptions } from "../../auth/[...nextauth]/route";
import { NextRequest, NextResponse } from "next/server";
import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }
    
    // Gọi API backend để lấy URL iframe
    const response = await axios.get(`${API_BASE_URL}/iframe/generate_iframe_url`, {
      headers: {
        Authorization: `Bearer ${session.user.accessToken}`,
        "X-Requested-With": "XMLHttpRequest",
      },
    });
    
    return NextResponse.json({ data: response.data.data });
  } catch (error: any) {
    console.error("Error fetching iframe URL:", error);
    return NextResponse.json(
      { error: "Failed to generate iframe URL" },
      { status: error.response?.status || 500 }
    );
  }
}