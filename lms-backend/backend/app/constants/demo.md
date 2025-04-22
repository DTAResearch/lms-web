Note for Google auth
Truyền token qua query params không an toàn:
Hiện tại, access_token và refresh_token được gửi qua query string (http://localhost:3000/logged-in?access_token=...). Điều này dễ bị lộ trong history trình duyệt hoặc log server.
Không có cơ chế thu hồi token:
Nếu token bị lộ, không có cách nào vô hiệu hóa nó ngay lập tức.
Không mã hóa dữ liệu trong dev:
OAUTHLIB_INSECURE_TRANSPORT = "1" cho phép HTTP thay vì HTTPS, dễ bị chặn bắt (man-in-the-middle).
Thiếu kiểm tra state trong OAuth2:
Không kiểm tra state parameter để ngăn tấn công CSRF trong flow OAuth2.
SECRET_KEY không được quản lý tốt:
Mỗi lần chạy lại server, SECRET_KEY thay đổi, làm vô hiệu hóa các token cũ.
Không giới hạn scope hoặc kiểm tra userinfo:
Không xác minh thêm thông tin từ Google (ví dụ: domain email).


Giải pháp tăng cường bảo mật trong dev
1. Truyền token qua cookie thay vì query params
Sử dụng cookie HttpOnly để gửi access_token và refresh_token từ backend về frontend, tránh lộ trong URL.
Trong dev, có thể bỏ qua Secure flag (chỉ áp dụng với HTTPS).
2. Thêm cơ chế thu hồi token
Dùng một tập hợp (set) hoặc Redis để lưu danh sách token bị thu hồi khi logout.
3. Giả lập HTTPS trong dev
Tạo self-signed certificate để chạy localhost với HTTPS, dù không bắt buộc trong dev nhưng là thực hành tốt.
4. Thêm kiểm tra state trong OAuth2
Tạo state ngẫu nhiên, lưu vào session hoặc cookie, rồi kiểm tra khi Google callback.
5. Quản lý SECRET_KEY
Lưu SECRET_KEY vào biến môi trường hoặc file .env, tránh tạo mới mỗi lần chạy.
6. Giới hạn scope và kiểm tra userinfo
Chỉ yêu cầu scope cần thiết và kiểm tra thông tin user (ví dụ: chỉ chấp nhận email từ domain cụ thể).

https://grok.com/chat/3d68114f-689a-4d1e-992e-0f82b385bf99

React yêu cầu các biến môi trường được "nhúng" vào mã nguồn tại build time, chứ không phải tại runtime như các ứng dụng backend thông thường.

React
https://grok.com/chat/99b5301d-a6a2-4ee5-99e3-16ff971df182?referrer=website
