import { useState } from "react";
import { signIn } from "next-auth/react";
import { toast } from "sonner";
import axios from "axios";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function LoginForm({
    className,
    ...props
}: React.ComponentPropsWithoutRef<"form">) {
    const [isLoading, setIsLoading] = useState(false);
    const [isGoogleLoading, setIsGoogleLoading] = useState(false);
    const [formData, setFormData] = useState({
        email: "",
        password: ""
    });

    const handleGoogleLogin = async () => {
        setIsGoogleLoading(true);
        await signIn("google", { callbackUrl: "/" });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (!formData.email || !formData.password) {
            toast.error("Vui lòng nhập đầy đủ email và mật khẩu!");
            return;
        }

        setIsLoading(true);

        try {
            // Bước 1: Gọi API route để login và set cookie
            const loginResponse = await axios.post("/api/auth/login", {
                email: formData.email,
                password: formData.password,
            }, {
                withCredentials: true
            });

            if (loginResponse.status === 200 && loginResponse.data.status === 'success') {
        
                const userResponse = await axios.get(`${process.env.NEXT_PUBLIC_API_BASE_URL}/users/me`, {
                    withCredentials: true, // Sử dụng cookie access_token
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });

                const userData = userResponse.data;
                // lưu user vào localStorage để sử dụng sau này
                localStorage.setItem("user", JSON.stringify(userData));

                // Bước 3: Tạo NextAuth session với user data
                const result = await signIn("credentials", {
                    email: formData.email,
                    password: formData.password,
                    // Truyền user data dưới dạng JSON string
                    userData: JSON.stringify({
                        id: userData.id,
                        name: userData.name,
                        email: userData.email,
                        role: userData.role,
                        loginType: userData.login_type
                    }),
                    redirect: false,
                });

                if (result?.ok) {
                    toast.success("Đăng nhập thành công!");
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

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    return (
        <form className={cn("flex flex-col gap-6", className)} onSubmit={handleSubmit} {...props}>
            <div className="flex flex-col items-center gap-2 text-center">
                <h1 className="text-2xl font-bold">Welcome back</h1>
                <p className="text-balance text-sm text-muted-foreground">
                    Enter your email below to login to your account
                </p>
            </div>
            <div className="grid gap-6">
                <div className="grid gap-2">
                    <Input 
                        id="email" 
                        name="email"
                        type="email" 
                        placeholder="example@email.com" 
                        value={formData.email}
                        onChange={handleInputChange}
                        required 
                    />
                </div>
                <div className="grid gap-2">
                    <Input 
                        id="password" 
                        name="password"
                        type="password" 
                        placeholder="Mật khẩu"
                        value={formData.password}
                        onChange={handleInputChange}
                        required 
                    />
                </div>
                <Button
                    type="submit"
                    disabled={isLoading}
                    className="w-full">
                    {isLoading ? "Đang đăng nhập..." : "Đăng nhập"}
                </Button>
                <div className="relative text-center text-sm after:absolute after:inset-0 after:top-1/2 after:z-0 after:flex after:items-center after:border-t after:border-border">
                    <span className="relative z-10 bg-background px-2 text-muted-foreground">
                        Hoặc tiếp tục với
                    </span>
                </div>
                <Button
                    variant="outline"
                    type="button"
                    disabled={isGoogleLoading}
                    className="w-full"
                    onClick={handleGoogleLogin}>
                    {isGoogleLoading ? "Đang đăng nhập..." : "Google"}
                </Button>
            </div>
            <div className="text-center text-sm">
                Bạn chưa có tài khoản?{" "}
                <a href="/auth/register" className="underline underline-offset-4">
                    Đăng ký
                </a>
            </div>
        </form>
    )
}
