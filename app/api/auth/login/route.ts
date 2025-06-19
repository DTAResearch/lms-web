import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { email, password } = body;

        // Gọi API backend
        const response = await axios.post(`${API_BASE_URL}/auth/login`, {
            email,
            password,
        });

        if (response.status === 401) {
            return new NextResponse(
                'Invalid credentials',
                { status: 401 }
            );

        }

        const userData = response.data;

        if (userData && userData.status === 'success') {
            // Tạo response và forward cookie từ backend
            const nextResponse = NextResponse.json(userData);

            // Forward cookie từ backend response
            const setCookieHeader = response.headers['set-cookie'];
            if (setCookieHeader) {
                setCookieHeader.forEach(cookie => {
                    nextResponse.headers.append('Set-Cookie', cookie);
                });
            }

            return nextResponse;
        }

        return NextResponse.json(
            { error: 'Invalid credentials' },
            { status: 401 }
        );
    } catch (error) {
        console.error('Login error:', error);
        return NextResponse.json(
            { error: 'Login failed' },
            { status: 500 }
        );
    }
}