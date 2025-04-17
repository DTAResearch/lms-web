"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { Button } from "../ui/button";

import { useAuth } from "@/hooks/useAuth";
import { Role } from "@/constants/Role";
import LogoutButton from "@/components/auth/LogoutButton";
import { getSession, useSession } from "next-auth/react";
import { LoaderCircle } from "lucide-react";
import { API_BASE_URL } from "@/constants/Url";


export const AnalysisPage = () => {

    const [iframeUrl, setIframeUrl] = useState<string | null>(null);

    useEffect(() => {
        const fetchDashboard = async () => {
            try {
                const session = await getSession();
                console.log("session", session);
                // const verifyResponse = await axios.post(`${API_BASE_URL}/auth/google/verify-id-token`, {
                //     id_token: account.id_token,
                // }, {
                //     headers: { "X-Requested-With": "XMLHttpRequest" },
                //     withCredentials: true // Important to accept cookies from response
                // });

                // console.log(account)
                // const cookies = verifyResponse.headers['set-cookie'] || [];
                // const cookieHeader = cookies.join('; ');

                const response = await axios.get(`${API_BASE_URL}/iframe/dashboard`, {
                    headers: {
                        "Authorization": `Bearer ${session?.user?.accessToken}`,
                        "X-Requested-With": "XMLHttpRequest",
                        "Cookie": session?.user.accessToken // Pass cookies from previous response
                    },
                    withCredentials: true
                  
                });
                setIframeUrl(response.data.data);
            } catch (error) {
                console.error("Error loading dashboard:", error);
            }
        };

        fetchDashboard();
    }, []);

    return (
        <div className="h-screen w-full pt-1">
            {iframeUrl ? (
                <iframe
                    src={iframeUrl}
                    title="Admin Dashboard"
                    className="w-full h-full"
                />
            ) : (
                <div className="space-y-2 w-full h-full flex flex-col items-center justify-center">
                    <p>Đang tải dữ liệu...</p>
                    <LoaderCircle className="animate-spin" />
                </div>
            )}
        </div>
    );
};
