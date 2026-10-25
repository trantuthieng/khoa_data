# Biên tập nội dung cho bản phát hành

Ngày thực hiện: 25/10/2026. Phạm vi: câu chữ trong webapp, nội dung 10 buổi và hướng dẫn bài tập. Các file Word, PowerPoint nguồn giữ nguyên.

## Những điểm đã chỉnh

- Giới thiệu đúng đối tượng: cán bộ quản lý, CNTT, quản trị cơ sở dữ liệu, phát triển phần mềm và vận hành điện lực. Mô tả bài thực hành theo mức kinh nghiệm, tránh khẳng định khóa dành cho người không có nền tảng CNTT.
- Làm rõ mục tiêu nền tảng về bảo vệ dữ liệu, kiểm soát truy cập và phối hợp xử lý sự cố, phù hợp với nội dung đang có.
- Thống nhất thuật ngữ giao diện: học viên **Nộp bài**, giảng viên **Lưu điểm và nhận xét**, sau đó **Công bố**. “Đã nộp” chỉ xuất hiện sau khi hệ thống nhận bài thành công; nội dung đang sửa được ghi “chưa nộp”.
- Giải thích bốn trạng thái của bài tập. Làm rõ số “Bài được giao” và “Đang mở, chưa nộp”, tránh gọi cả bài đã đóng là bài đang mở.
- Dùng “trực tuyến” thay “online”. Làm rõ cách dùng mã vào lại cá nhân, thông báo phiên truy cập, thao tác xóa lớp/học viên/bài nộp và phần dữ liệu bị xóa kèm theo.
- Thông báo lỗi nêu việc cần làm tiếp theo, không hiển thị tên biến cấu hình máy chủ cho người sử dụng. Lỗi kết nối có thông báo tiếng Việt.
- Sửa lỗi chính tả, các cách nói quá khẩu ngữ và câu tuyệt đối dễ gây hiểu nhầm. Ví dụ SSO được mô tả là quản lý danh tính tập trung, vẫn phải kiểm tra quyền và phiên tại ứng dụng liên quan.
- Bỏ số slide khỏi tên mục điều hướng; giữ tham chiếu tài liệu ở phần thông tin buổi học. Phần chuẩn bị SQL/Python/BI được đặt tên và dẫn chiếu nhất quán.
- Nhãn nhập bài phù hợp với từng công cụ: câu lệnh SQL, đoạn mã Python hoặc các bước Power BI. Hướng dẫn đánh giá service chỉ xuất hiện ở BI 10, không lặp trong mọi bài SQL/Python.
- Chỉnh phần tổng quan để không đồng nhất chữ viết tắt PDPA với luật Việt Nam. Phần giới thiệu không khái quát một mức phạt hoặc thời hạn cho mọi trường hợp.
- Đồng bộ giờ buổi chiều theo tài liệu trình chiếu là 13:30–16:30; ghi rõ giảng viên thông báo lịch chi tiết. Sửa nhật ký đêm thành 17 dòng và tham chiếu buổi 10 thành slide 102–110.

Lời thoại của nhân vật trong tình huống vẫn được giữ khi cần mô tả hành vi hoặc tâm lý. Bài tập tiếp tục dùng dữ liệu giả lập, làm và nộp cá nhân.

## Lưu trữ và kiểm chứng

Phần biên tập nội dung nằm ở `tools/production_copy.py`, áp dụng sau khi dựng giáo trình và thêm bài tập. Chạy lại `python tools/build_content.py` sẽ giữ các chỉnh sửa này. Mã bài tập, tên trường bài làm, đáp án trắc nghiệm, mã thực hành và số liệu không được đổi trong bước biên tập.

Kiểm chứng gồm: dựng lại nội dung; chạy lời giải SQL/Python, kiểm tra bộ dữ liệu BI, lọc lời giải trước công bố; thử luồng nộp, chấm và công bố trên API và trình duyệt; xem lại giao diện máy tính, điện thoại và chế độ tối. Những kiểm tra này thực hiện trên dữ liệu thử cục bộ.

Nguồn đối chiếu cho phần pháp luật: [Luật 91/2025/QH15 trên Cổng thông tin Bộ Công an](https://vanban.bocongan.gov.vn/co-so-du-lieu-van-ban/luat-bao-ve-du-lieu-ca-nhan-1753688803) và [PDPA của Singapore trên Singapore Statutes Online](https://sso.agc.gov.sg/Act/PDPA2012/). Đây là nguồn cho việc chỉnh cách diễn đạt ở phần giới thiệu, không phải kết luận rà soát pháp lý toàn bộ khóa học.
