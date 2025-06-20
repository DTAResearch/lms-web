// src/app/login/page.tsx
"use client";

import { signIn } from "next-auth/react";
import { useState } from "react";
import { LoginForm } from "@/components/auth/login-form";
import { GalleryVerticalEnd } from "lucide-react";
import Image, { StaticImageData } from "next/image"
import LogoLMS from "@/public/images/logo.png"
import Background from "@/public/images/background.jpg"

export default function LoginPage() {
    return (
        <div className="grid min-h-svh lg:grid-cols-2">
            <div className="flex flex-col gap-4 p-6 md:p-10">
                <div className="flex justify-center gap-2 md:justify-start">
                    <a href="#" className="flex items-center gap-2 font-medium">
                        <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary text-primary-foreground">
                            <div className="bg-sidebar-primary text-sidebar-primary-foreground flex aspect-square size-8 items-center justify-center rounded-full border">
                                {/* <activeTeam.logo className="size-4" /> */}
                                <Image src={LogoLMS as StaticImageData} alt="Logo-LMS" className="size-8" />
                            </div>
                        </div>
                        Trợ giảng AI
                    </a>
                </div>
                <div className="flex flex-1 items-center justify-center">
                    <div className="w-full max-w-xs">
                        <LoginForm />
                    </div>
                </div>
            </div>
            <div className="relative hidden bg-muted lg:block">
                <Image
                    src={Background}
                    alt="Image"
                    className="absolute inset-0 h-full w-full object-cover dark:brightness-[0.2] dark:grayscale"
                />
            </div>
        </div>
    );
}