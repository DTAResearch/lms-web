"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { Button } from "../ui/button"
import { LoaderCircle } from "lucide-react";
import { API_BASE_URL } from "@/constants/URL";
import axiosInstance from "@/lib/Api-Instance";


export const AnalysisPage = () => {

    const [iframeUrl, setIframeUrl] = useState<string | null>(null);

    useEffect(() => {
        const fetchDashboard = async () => {
            try {

                const response = await axiosInstance.get(`${API_BASE_URL}/iframe/dashboard`)
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
