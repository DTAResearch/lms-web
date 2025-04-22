// src/context/AuthContext.tsx
"use client";

import { SessionProvider } from "next-auth/react";
import { ReactNode } from "react";
// import { ToastContainer } from "react-toastify";
// import "react-toastify/dist/ReactToastify.css";

export interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  return (
    <SessionProvider>
      {/* <ToastContainer
        position="top-center"
        autoClose={2000}
        hideProgressBar={false}
        newestOnTop={true}
        theme="light"
      /> */}
      {children}
    </SessionProvider>
  );
};