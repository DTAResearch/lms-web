"use client";

import { SessionProvider } from "next-auth/react";
import { ReactNode } from "react";


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