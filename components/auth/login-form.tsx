import { useState } from "react";
import { signIn } from "next-auth/react";
import axios from "axios";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import axiosInstance from "@/lib/Api-Instance";
import GoogleLoginButton from "./GoogleLoginButton";
import MicrosoftLoginButton from "./MicrosoftLoginButton";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Eye, EyeOff } from "lucide-react";
import { useTranslations } from "next-intl";
import { API_BASE_URL } from "@/constants/URL";
import Logo from "@/public/images/logo.png";
import Image, { StaticImageData } from "next/image";
import { toast } from "sonner";
// Schema validation với Zod
const loginSchema = z.object({
    email: z
        .string()
        .min(1, "emailRequired")
        .email("emailInvalid"),
    password: z
        .string()
        .min(1, "passwordRequired")
});

type LoginFormData = z.infer<typeof loginSchema>;

export function LoginForm({
    className,
    ...props
}: React.ComponentPropsWithoutRef<"form">) {
    const [isLoading, setIsLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const t = useTranslations();

    const {
        register,
        handleSubmit,
        formState: { errors },
        reset
    } = useForm<LoginFormData>({
        resolver: zodResolver(loginSchema),
        defaultValues: {
            email: "",
            password: ""
        }
    });

    const onSubmit = async (data: LoginFormData) => {
        setIsLoading(true);

        try {
            // Bước 1: Gọi API route để login và set cookie
            const loginResponse = await axiosInstance.post(`${API_BASE_URL}/auth/login`, {
                email: data.email,
                password: data.password,
            });

            if (loginResponse.status === 200 && loginResponse.data.status === 'success') {
                const userResponse = await axiosInstance.get(`${process.env.NEXT_PUBLIC_API_BASE_URL}/users/me`);
                const userData = userResponse.data;

                // lưu user vào localStorage để sử dụng sau này
                localStorage.setItem("user", JSON.stringify(userData));

                // Bước 3: Tạo NextAuth session với user data
                const result = await signIn("credentials", {
                    email: data.email,
                    password: data.password,
                    userData: JSON.stringify({
                        id: userData.id,
                        name: userData.name,
                        email: userData.email,
                        role: userData.role,
                        loginType: userData.login_type,
                        password_changed: userData.password_changed,
                    }),
                    redirect: false,
                });

                if (result?.ok) {
                    toast.success("Đăng nhập thành công!");
                    reset();
                    window.location.href = "/";
                } else {
                    toast.error("Có lỗi khi tạo session!");
                }
            }
        } catch (error: any) {
            console.error("Form: Login error:", error);
            if (error.response?.status === 401) {
                toast.error("Email hoặc mật khẩu không đúng!");
            } else {
                toast.error("Có lỗi xảy ra. Vui lòng thử lại!");
            }
        } finally {
            setIsLoading(false);
        }
    };

    const getYear = new Date().getFullYear();

    return (
        <form className={cn("flex flex-col gap-6", className)} onSubmit={handleSubmit(onSubmit)} {...props}>
            <div className="flex flex-col items-center gap-2 text-center">
                <Image src={Logo as StaticImageData} alt="Logo-LMS" className="w-27 h-25" />
                <h1 className="text-3xl font-bold text-primary hidden sm:block">{t("loginTitle")}</h1>
                <p className="text-balance text-sm text-primary/90 hidden sm:block">
                    {t("loginSubtitle")}
                </p>
            </div>
            <div className="grid gap-6">
                <div className="grid gap-2">
                    <Label className="text-primary" htmlFor="email">{t("email")}</Label>
                    <Input
                        id="email"
                        type="email"
                        placeholder={t("emailPlaceholder")}
                        {...register("email")}
                        className={errors.email ? "border-red-500" : ""}
                    />
                    {errors.email && (
                        <p className="text-sm text-red-500">{t(errors.email.message || "")}</p>
                    )}
                </div>
                <div className="grid gap-2">
                    <Label className="text-primary" htmlFor="password">{t("password")}</Label>
                    <div className="relative">
                        <Input
                            id="password"
                            type={showPassword ? "text" : "password"}
                            placeholder={t("passwordPlaceholder")}
                            {...register("password")}
                            className={cn(
                                "pr-10",
                                errors.password ? "border-red-500" : ""
                            )}
                        />
                        <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                            onClick={() => setShowPassword(!showPassword)}
                            aria-label={showPassword ? t("hidePassword") : t("showPassword")}
                        >
                            {showPassword ? (
                                <EyeOff className="h-4 w-4 text-muted-foreground" />
                            ) : (
                                <Eye className="h-4 w-4 text-muted-foreground" />
                            )}
                        </Button>
                    </div>
                    {errors.password && (
                        <p className="text-sm text-red-500">{t(errors.password.message || "")}</p>
                    )}
                </div>
                <Button
                    type="submit"
                    disabled={isLoading}
                    className="w-full bg-gradient-to-r from-primary to-orange-600 hover:from-orange-400 hover:to-orange-500 text-white border-0 shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-[1.01] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none">
                    {isLoading ? t("signingIn") : t("signIn")}
                </Button>
                <div className="relative text-center text-sm after:absolute after:inset-0 after:top-1/2 after:z-0 after:flex after:items-center after:border-t after:border-border">
                    <span className="relative z-10 bg-background px-2 text-muted-foreground">
                        {t("orContinueWith")}
                    </span>
                </div>
                <div className="flex flex-col gap-4">
                    <GoogleLoginButton />
                    <MicrosoftLoginButton />
                </div>

            </div>
            {/* <div className="text-center text-sm">
                Bạn chưa có tài khoản?{" "}
                <a href="/auth/register" className="underline underline-offset-4">
                    Đăng ký
                </a>
            </div> */}
            <div className="text-center text-sm text-muted-foreground mt-1">
                {`© ${getYear} Học Tiếp. All rights reserved.`}
            </div>
        </form>
    )
}
