import { GoogleLogin } from '@react-oauth/google';
import { API_BASE_URL } from '@/constants/URL';
import { getMe } from '@/utils/getMe';
import { signIn } from "next-auth/react";
import { toast } from "sonner";
import axios from 'axios';

export default function GoogleLoginButton() {
    const handleLogin = async (credentialResponse: any) => {
        try {
            // Bước 1: Verify Google token và set cookie
            const res = await axios.post(`${API_BASE_URL}/auth/google/verify-id-token`, {
                id_token: credentialResponse.credential,
            }, {
                withCredentials: true,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (res.status === 200 && res.data.status === 'success') {
                // Bước 2: Lấy thông tin user từ backend
                const userData = await getMe();
                
                // Bước 3: Lưu user data vào localStorage
                localStorage.setItem("user", JSON.stringify(userData));

                // Bước 4: Tạo NextAuth session với user data
                const result = await signIn("credentials", {
                    email: userData.email,
                    password: "google_auth", // dummy password cho Google auth
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
                    toast.success("Đăng nhập Google thành công!");
                    window.location.href = "/";
                } else {
                    toast.error("Có lỗi khi tạo session!");
                }
            }
        } catch (error: any) {
            console.error("Google login error:", error);
            if (error.response?.data?.detail) {
                toast.error(error.response.data.detail);
            } else {
                toast.error("Đăng nhập Google thất bại!");
            }
        }
    };

    return (
        <GoogleLogin
            onSuccess={handleLogin}
            onError={() => {
                console.log('Login Failed');
                toast.error("Đăng nhập Google thất bại!");
            }}
            size="large"
            theme="outline"
            text="signin_with"
            shape="rectangular"
            width="100%"
            logo_alignment="center"
        />
    );
}
