# Giao diện lớp học An toàn ứng dụng & Dữ liệu dành cho cán bộ vận hành

Bản thiết kế triển khai cục bộ ngày 25/10/2026. Các ảnh trong `previews/` được chụp từ webapp đang chạy với lớp minh họa và dữ liệu giả lập.

## Hướng thiết kế

Giao diện phục vụ một lớp học có giảng viên điều khiển nội dung và học viên làm bài cá nhân. Ưu tiên đọc bài, làm bài và theo dõi kết quả. Không dùng số liệu trang trí trong giao diện thật: các chỉ số đều lấy từ lớp và bài đang chọn.

- Navy `#142D45`: chữ và phần giới thiệu khóa học.
- Teal `#087E8B`: hành động chính và phần đang chọn.
- Vàng nhẹ `#F2BC57`: điểm nhấn trên nền navy. Trạng thái cần chú ý dùng nền vàng nhạt và chữ sẫm.
- Nền `#F5F7F8`, thẻ trắng, viền mảnh, góc bo 10–14 px.
- Chữ Segoe UI/system có tiếng Việt. Nội dung chính 16 px, nút có trạng thái bàn phím rõ.

## Các màn hình

1. **Vào lớp**: giới thiệu ngắn ở bên trái, form mã lớp và tên ở bên phải; giữ cách vào lại bằng mã cá nhân.
2. **Học viên**: phân biệt Bài học và Bài tập của tôi, cho biết đang theo nhịp giảng viên hay tự xem. Đề bài, mã mẫu và phần nộp nằm trong cùng luồng.
3. **Giảng viên**: bên trái là mục lục và cách dẫn lớp, giữa là phần đang dạy, bên phải là hoạt động và học viên. Có tổng số học viên, trực tuyến và bài đang mở của buổi đang chọn.
4. **Chấm bài**: số đã nộp/chưa nộp/đã chấm ở đầu. Mỗi học viên có một mục mở rộng chứa cả bài đã nộp, điểm và nhận xét, tránh cuộn qua toàn bộ bảng điểm rồi mới tìm thấy bài làm. Chỉ bài đầu mở sẵn, các bài khác có thể mở riêng.
5. **Điện thoại**: form vào lớp một cột, mục lục và hoạt động mở thành ngăn riêng có nút đóng; nút nộp nằm sau phần bài làm. Giữ chế độ sáng/tối và chế độ trình chiếu.

## Tệp triển khai

`app/static/studio.css` chứa bảng màu và bố cục mới, được nạp sau CSS nền. Ba trang HTML được cập nhật phần giới thiệu, điều hướng và số liệu thực. `common.js` theo dõi chiều cao thanh đầu trang để mục lục không bị che khi xuống dòng.

Đã thử trên Edge ở chiều rộng 1440/1600 px và 390 px, kiểm tra mở/đóng ngăn di động, nộp và chấm bài, công bố điểm, tải bộ thực hành và chế độ tối. Các bộ kiểm thử API và ba luồng trình duyệt đều chạy qua. Chưa triển khai lên máy chủ.

## Trạng thái Canva

Đã gửi brief tạo bộ 4 màn hình UI cho Canva. Canva trả về lỗi yêu cầu xác thực lại (`oauth_token_invalid_grant`), vì vậy chưa tạo được thiết kế hoặc liên kết Canva. Bản web cục bộ và ảnh xem thử là công việc chuẩn bị độc lập, không phải thiết kế đã lưu trên Canva.

Sau khi kết nối lại, brief để dựng trên Canva là: bộ UI website chỉnh sửa được gồm Vào lớp, Học viên làm SQL 01, Giảng viên điều khiển lớp, Theo dõi/chấm bài. Dùng hệ màu ở trên, chữ Việt rõ, dữ liệu minh họa; giữ đúng các chức năng cá nhân, bốn trạng thái Ẩn/Mở/Đóng/Công bố và điểm chỉ hiển thị cho học viên khi đã công bố. Các ảnh `previews/` là tham chiếu bố cục thực tế.
