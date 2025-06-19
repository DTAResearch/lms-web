import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { id_token } = body;

        // Gọi API backend để verify Google token
        const response = await axios.post(`${API_BASE_URL}/auth/google/verify-id-token`, {
            id_token: id_token,
        }, {
            headers: { 
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/json"
            }
        });

        const tokenData = response.data;
        console.log("Google API Route: Backend response:", tokenData);

        if (tokenData && tokenData.token) {
            // Tạo response và forward cookie từ backend
            const nextResponse = NextResponse.json({
                status: 'success',
                message: 'Google login successful',
                token: tokenData.token
            });

            // Forward cookie từ backend response
            const setCookieHeader = response.headers['set-cookie'];
            if (setCookieHeader) {
                setCookieHeader.forEach(cookie => {
                    nextResponse.headers.append('Set-Cookie', cookie);
                });
            } else {
                // Nếu backend không set cookie, tự set
                nextResponse.cookies.set({
                    name: 'access_token',
                    value: tokenData.token,
                    httpOnly: true,
                    maxAge: 86400 * 30, // 30 days
                    sameSite: 'lax',
                    secure: process.env.NODE_ENV === 'production',
                    path: '/'
                });
            }

            return nextResponse;
        }

        return NextResponse.json(
            { error: 'Google authentication failed' },
            { status: 401 }
        );
    } catch (error: any) {
        console.error('Google login error:', error);
        
        if (error.response?.status === 401) {
            return NextResponse.json(
                { error: 'Google token không hợp lệ' },
                { status: 401 }
            );
        }
        
        return NextResponse.json(
            { error: 'Có lỗi xảy ra khi đăng nhập Google' },
            { status: 500 }
        );
    }
}