import NextAuth from "next-auth";
import { Role } from "@/constants/Role";

declare module "next-auth" {
  interface User {
    role?: Role;
    id?: string | null;
    accessToken?: string | null;
    loginType?: "local" | "google" | "outlook";
    name?: string | null;
    email?: string | null;
    password_changed?: boolean;
  }
  
  interface Session {
    user: {
      id?: string | null;
      name?: string | null;
      email?: string | null;
      role?: Role;
      password_changed?: boolean;
      loginType?: "local" | "google" | "outlook";
      accessToken?: string | null; // Chỉ có khi loginType là google
    }
  }
}