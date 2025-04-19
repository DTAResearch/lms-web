"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { Button } from "../ui/button";

import { useAuth } from "@/hooks/useAuth";
import { Role } from "@/constants/Role";
import LogoutButton from "@/components/auth/logout-button";
import { useSession } from "next-auth/react";


export const AdminPage = () => {

    const { isAuthorized, isLoading } = useAuth([Role.ADMIN]);
    const { data: session } = useSession();

    if (isLoading) {
        return (
            <div className="h-screen flex justify-center items-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-sky-500"></div>
                <p className="ml-2">Đang tải...</p>
            </div>
        );
    }

    if (!isAuthorized) {
        return null; // useAuth sẽ tự chuyển hướng nên không cần render gì
    }


    return (
        <div>
            <main className="flex-col w-full p-4 overflow-y-auto h-fit">
                <h1 className="text-2xl font-bold mb-4">Admin Dashboard</h1>
                <p>Welcome, {session?.user?.name}!</p>
            </main>
        </div >
    )
}