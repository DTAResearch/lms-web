import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import CredentialsProvider from "next-auth/providers/credentials";
import { NextAuthOptions } from "next-auth";
import axios from "axios";

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
        CredentialsProvider({
            name: "credentials",
            credentials: {
                email: { label: "Email", type: "email" },
                password: { label: "Password", type: "password" },
                userData: { label: "User Data", type: "text" }
            },
            async authorize(credentials) {
                if (!credentials?.email || !credentials?.password || !credentials?.userData) {
                    return null;
                }

                try {
                    const userData = JSON.parse(credentials.userData);
                    
                    return {
                        id: userData.id,
                        name: userData.name,
                        email: userData.email,
                        role: userData.role,
                        loginType: userData.loginType,
                        password_changed: userData.password_changed,
                    };
                } catch (error) {
                    console.error("AuthOptions: Failed to parse user data:", error);
                    return null;
                }
            }
        })
    ],
    callbacks: {
        async signIn({ account, profile, user }) {
            if (account?.provider === "credentials") {
                return true;
            }

            if (!account || !profile) return false;

            try {
                // Verify Google login
                await axios.post(`${API_BASE_URL}/auth/google/verify-id-token`, {
                    id_token: account.id_token,
                }, {
                    headers: { "X-Requested-With": "XMLHttpRequest" },
                    withCredentials: true
                });
                return true;
            } catch (error) {
                console.error("AuthOptions: Google login failed:", error);
                return false;
            }
        },

        async jwt({ token, user, account }) {
            if (account && user) {
                if (account.provider === "credentials") {
                    // Local login - chỉ lưu thông tin cần thiết vào token
                    return {
                        ...token,
                        role: user.role,
                        userId: user.id,
                        loginType: "local",
                        email: user.email,
                        name: user.name,
                        password_changed: user.password_changed,
                    };
                }

                try {
                    // Google login
                    const verifyResponse = await axios.post(`${API_BASE_URL}/auth/google/verify-id-token`, {
                        id_token: account.id_token,
                    }, {
                        headers: { "X-Requested-With": "XMLHttpRequest" },
                        withCredentials: true
                    });

                    const accessToken = verifyResponse.data.token;

                    const userResponse = await axios.get(`${API_BASE_URL}/users/me`, {
                        headers: {
                            "Authorization": `${accessToken}`,
                            "X-Requested-With": "XMLHttpRequest",
                            "Cookie": `access_token=${accessToken}`
                        },
                        withCredentials: true
                    });

                    const userData = userResponse.data;
                    
                    return {
                        ...token,
                        role: userData.role,
                        name: userData.name,
                        userId: userData.id,
                        loginType: userData.login_type,
                        email: userData.email,
                        accessToken: accessToken,
                        password_changed: userData.password_changed,
                    };
                } catch (err) {
                    console.error("AuthOptions: Error in Google JWT creation:", err);
                    return token;
                }
            }

            return token;
        },

        async session({ session, token }) {
            // Session chỉ chứa thông tin cần thiết
            const sessionUser = {
                id: token.userId,
                name: token.name,
                email: token.email,
                role: token.role,
                password_changed: token.password_changed,
                loginType: token.loginType,
            };

            // Chỉ thêm accessToken khi là Google login
            if (token.loginType === "google" && token.accessToken) {
                (sessionUser as any).accessToken = token.accessToken;
            }

            return {
                ...session,
                user: sessionUser,
                // Thêm userData để client có thể lưu vào localStorage
                userData: token.userData
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
            name: "next-auth.session-token",
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
