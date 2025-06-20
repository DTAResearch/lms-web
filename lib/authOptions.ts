import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import { NextAuthOptions } from "next-auth";

export const authOptions: NextAuthOptions = {
    providers: [
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
        async jwt({ token, user }) {
            if (user) {
                return {
                    ...token,
                    role: user.role,
                    userId: user.id,
                    loginType: user.loginType,
                    email: user.email,
                    name: user.name,
                    password_changed: user.password_changed,
                };
            }
            return token;
        },

        async session({ session, token }) {
            return {
                ...session,
                user: {
                    id: token.userId,
                    name: token.name,
                    email: token.email,
                    role: token.role,
                    password_changed: token.password_changed,
                    loginType: token.loginType,
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
};

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
