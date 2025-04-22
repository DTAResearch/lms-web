import NextAuth from "next-auth";
import { Role } from "@/constants/Role";

declare module "next-auth" {
  interface User {
    role?: Role;
  }
  
  interface Session {
    user: {
      name?: string | null;
      email?: string | null;
      image?: string | null;
      role?: Role;
      id?: string | null;
      backendToken?: string | null; // Add this line
      loginType?: string | null;
      avatar?: string | null;
    }
  }
}