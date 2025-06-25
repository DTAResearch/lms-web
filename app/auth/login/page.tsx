"use client";

import { signIn } from "next-auth/react";
import { useState } from "react";
import { LoginForm } from "@/components/auth/login-form";
import { GalleryVerticalEnd } from "lucide-react";
import Image, { StaticImageData } from "next/image"
import LogoLMS from "@/public/images/logo.png"
import Background from "@/public/images/background.jpg"
import LanguageSwitch from "@/components/language-switch";

export default function LoginPage() {
    return (
        <div className="relative min-h-svh">
            {/* Background full screen */}
            <div className="absolute inset-0">
                <Image
                    src={Background}
                    alt="Background"
                    className="h-full w-full object-cover dark:brightness-[0.2] dark:grayscale"
                />
                <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-blue-800/50 to-indigo-900/50"></div>
            </div>

            {/* Logo positioned at top */}
            <div className="absolute top-6 left-6 z-20 md:top-10 md:left-10">
                <a href="#" className="flex items-center gap-2 font-medium text-white">
                    <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary text-primary-foreground">
                        <div className="bg-white text-sidebar-primary-foreground flex aspect-square size-8 items-center justify-center rounded-full border">
                            <Image src={LogoLMS as StaticImageData} alt="Logo-LMS" className="size-8" />
                        </div>
                    </div>
                    Trợ giảng AI
                </a>
            </div>

            {/* Login form centered */}
            <div className="absolute p-4 lg:p-0 inset-0 z-10 flex items-center justify-center">
                <div className="w-full max-w-sm bg-white backdrop-blur-sm rounded-lg p-6 shadow-lg">
                    <LoginForm />
                </div>
            </div>

            {/* Language switch at bottom */}
            <div className="absolute bottom-4 left-4 z-20 flex items-center gap-2">
                <LanguageSwitch />
            </div>
        </div>
    );
}