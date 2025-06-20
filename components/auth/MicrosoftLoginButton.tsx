import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export default function MicrosoftLoginButton() {
    const handleMicrosoftLogin = async () => {
        try {
            // TODO: Implement Outlook login logic
            toast.info("Tính năng đăng nhập bằng Microsoft đang được bảo trì!");
        } catch (error) {
            console.error("Outlook login error:", error);
            toast.error("Có lỗi xảy ra khi đăng nhập bằng Microsoft!");
        }
    };

    return (
        <Button
            type="button"
            variant="outline"
            className="w-full font-normal rounded-[5px] hover:border-blue-500 hover:bg-blue-50/40 focus:ring-blue-500 focus:ring-offset-blue-100"
            onClick={handleMicrosoftLogin}
        >
            <svg xmlns="http://www.w3.org/2000/svg" x="0px" y="0px" width="100" height="100" viewBox="0 0 48 48">
                <path fill="#ff5722" d="M6 6H22V22H6z" transform="rotate(-180 14 14)"></path><path fill="#4caf50" d="M26 6H42V22H26z" transform="rotate(-180 34 14)"></path><path fill="#ffc107" d="M26 26H42V42H26z" transform="rotate(-180 34 34)"></path><path fill="#03a9f4" d="M6 26H22V42H6z" transform="rotate(-180 14 34)"></path>
            </svg>
            Đăng nhập bằng Microsoft
        </Button>
    );
}