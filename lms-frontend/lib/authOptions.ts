// src/app/api/auth/[...nextauth]/route.ts
import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import { NextAuthOptions } from "next-auth";
import axios from "axios";
import axiosInstance from "@/lib/Api-Instance";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export const authOptions: NextAuthOptions = {
    providers: [
        GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID as string,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET as string,
            authorization: {
                params: {
                    prompt: "select_account",
                    scope: "openid email profile",
                    access_type: "offline",
                    response_type: "code",
                },
            },
        }),
    ],
    callbacks: {
        async signIn({ account, profile }) {
            if (!account || !profile) return false;

            try {
                // console.log("account", account);
                // console.log("profile", profile);

                // Gửi id_token lên backend để xác thực
                const response = await axios.post(`${API_BASE_URL}/auth/google/verify-id-token`, {
                    id_token: account.id_token,
                }, {
                    headers: { "X-Requested-With": "XMLHttpRequest" }
                });

                // console.log("response", response.data);

                return true;
            } catch (error) {
                console.error("Đăng nhập thất bại:", error);
                return false;
            }
        },
        // async jwt({ token, user, account }) {
        //     // Nếu đang đăng nhập, cập nhật token với thông tin từ user
        //     if (account && user) {
        //         try {
        //             const response = await axios.get(`${API_BASE_URL}/users/me`, {
        //                 headers: {
        //                     "Authorization": `Bearer ${account.id_token}`,
        //                     "X-Requested-With": "XMLHttpRequest"
        //                 }
        //             });

        //             const userData = response.data;
        //             return {
        //                 ...token,
        //                 accessToken: account.id_token,
        //                 role: userData.role,
        //                 userId: userData.id,
        //                 avatar: userData.avatar,
        //             };
        //         } catch (error) {
        //             console.error("Lỗi khi lấy thông tin user:", error);
        //         }
        //     }

        //     return token;
        // },
        async jwt({ token, user, account }) {
            if (account && user) {
                try {
                    // Step 1: Verify the Google token with backend and get token
                    const verifyResponse = await axios.post(`${API_BASE_URL}/auth/google/verify-id-token`, {
                        id_token: account.id_token,
                    }, {
                        headers: { "X-Requested-With": "XMLHttpRequest" },
                        withCredentials: true
                    });
                    
                    // console.log("Backend token response:", verifyResponse.data);
                    
                    // Extract token from response
                    const backendToken = verifyResponse.data.token;
                    // console.log("Backend token:", backendToken);
                    
                    // Step 2: Use the token for /users/me
                    const me = await axios.get(`${API_BASE_URL}/users/me`, {
                        headers: {
                            "Authorization": `Bearer ${backendToken}`,
                            "X-Requested-With": "XMLHttpRequest",
                            "Cookie": `access_token=${backendToken}` // Include the session token in the request
                        },
                        withCredentials: true
                    });

                    console.log("User data retrieved successfully");
                    const userData = me.data;

                    return {
                        ...token,
                        accessToken: account.id_token,    // Google token
                        backendToken: backendToken,       // Your backend token
                        role: userData.role,
                        userId: userData.id || userData.email,
                        avatar: userData.avatar,
                        loginType: userData.login_type,
                        email: userData.email
                    };
                } catch (err) {
                    console.error("Lỗi khi lấy user từ backend:", err);
                    return token;
                }
            }

            return token;
        },

        async session({ session, token }) {
            return {
                ...session,
                user: {
                    ...session.user,
                    id: token.userId,
                    role: token.role,
                    avatar: token.avatar,
                    loginType: token.loginType,
                    backendToken: token.backendToken,  // Include this for client API calls
                    email: token.email,
                }
            };
        }
    },
    pages: {
        signIn: '/auth/login',
        error: '/error',
    },
    session: {
        strategy: 'jwt',
    },
    cookies: {
        sessionToken: {
            name: "next-auth.session-token", // Use a different name from your backend cookie
            options: {
                httpOnly: true,
                sameSite: "lax",
                path: "/",
                secure: process.env.NODE_ENV === "production",
            },
        },
    },
};

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
