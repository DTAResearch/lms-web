import { redirect } from "next/navigation";
export default function Setup() {
  // Check if the user is logged in
  // Phần này kiểm tra quyền truy cập của người dùng dựa vào role tưng ứng rồi trả về đường dẫn
  return (
    redirect("/admin")
  )
  
}
