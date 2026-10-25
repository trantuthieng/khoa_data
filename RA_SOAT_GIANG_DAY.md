# Rà soát nội dung và tổ chức lớp học

Ngày rà soát: 25/10/2026. Phạm vi chỉnh sửa: dự án `webapp`. Đối chiếu với tài liệu Tổng quan và 10 tài liệu Word theo buổi trong thư mục cha. Các file Word nguồn được giữ nguyên; bản biên tập trên web được áp dụng mỗi lần dựng nội dung.

## Kết quả đối chiếu

Dự án có đủ 10 chủ đề của giáo trình, 11 bài thực hành gốc, câu hỏi ôn tập theo buổi và bài kiểm tra cuối khóa 20 câu. Trình tự đi từ phân loại dữ liệu, luồng dữ liệu, quyền và xác thực đến chia sẻ, phân tích, báo cáo, phát hiện và ứng phó sự cố. Chưa thấy thiếu buổi hoặc đổi sai chủ đề khi đối chiếu cấu trúc và hoạt động.

Những điểm đã sửa:

- Hướng dẫn làm nhóm, chia vai và trình bày nhóm được chuyển sang bài cá nhân trong các hoạt động trên web. Những cụm “nhóm dữ liệu”, “nhóm quyền”, “nhóm ứng phó” vẫn giữ đúng nghĩa chuyên môn.
- Sửa chỗ bài ma trận quyền nhắc “bốn nhóm dữ liệu” thành năm nhóm, khớp bài phân loại ở buổi 1.
- Đổi một số câu mang tính khuôn mẫu, như “Mạch nối”, “đầu vào”, “đầu ra”, “timeline”, thành cách diễn đạt gần với hướng dẫn của giảng viên. Giữ thuật ngữ chuyên môn và mã thực hành khi cần.
- Có bộ kiểm tra nhanh mới, tách khỏi câu hỏi cuối khóa. Bộ cũ được đổi tên thành ôn cuối khóa tùy chọn để không làm sai các bài nộp đã có.
- Bảng đáp án trò chơi CIA và kết quả phân tích nhật ký rút gọn được giữ lại đến khi giảng viên công bố.
- Làm rõ T0 = 08:50 trong tình huống gốc là giả định tính giờ; không dạy cách lấy thời điểm đầu mối nhận tin để mặc định kéo dài hạn thông báo. Vẫn phải giữ mốc tổng đài nhận tin sớm hơn và xác định nghĩa vụ từ sự việc thực tế.

## Bài cá nhân bổ sung

Mỗi buổi thêm một bài có dữ kiện ngay trong đề, ba mục trả lời, gợi ý chữa bài và tiêu chí 10 điểm. Các bài thêm khoảng 15–20 phút, dùng để luyện thêm hoặc giao về nhà; giảng viên chủ động chọn để tránh kéo dài thời lượng buổi gốc.

| Buổi | Nội dung giáo trình | Bài bổ sung và sản phẩm học viên nộp |
|---|---|---|
| 1 | CIA, vòng đời, phân loại, AI | Phân loại ba phiên bản báo cáo; viết lời trả lời đồng nghiệp và điều kiện dùng AI |
| 2 | Tuân thủ, lỗi thao tác, luồng dữ liệu | Tìm bản sao còn sót; đề xuất ba điểm sửa và người chịu trách nhiệm |
| 3 | Quyền tối thiểu, RBAC/ABAC | Phương án quyền bàn giao; phê duyệt, hạn và ba phép thử |
| 4 | MFA, SSO, tài khoản và phiên | Xử lý MFA lạ khi nhận ca; kiểm tra phiên và cách tiếp tục công việc |
| 5 | Mã hóa, chia sẻ an toàn | Rà gói báo cáo có sheet ẩn; quy trình tạo bản gửi và hai phép thử |
| 6 | Giảm dữ liệu, an toàn CSDL | Tính tỷ trọng 61,8%; phân tích nguy cơ nhận diện và điều kiện giao dữ liệu |
| 7 | Power BI, RLS, chia sẻ | Nhận xét bốn lượt kiểm thử; sửa quyền và viết kế hoạch thử lại |
| 8 | Lừa đảo, xác minh độc lập | Nhận diện áp lực; viết câu từ chối và tin báo đầu mối |
| 9 | Nhật ký, truy vết | Đổi năm mốc UTC sang +07:00; tách dữ kiện với giả thuyết |
| 10 | Ứng phó, báo cáo, phục hồi | Báo cáo ban đầu; thứ tự xử lý, thẩm quyền và tính hạn theo T0 giả định |

Buổi 1–9 có thêm tổng cộng 18 câu trắc nghiệm tình huống, mỗi buổi hai câu, có giải thích. Buổi 10 giữ bài kiểm tra cuối khóa 20 câu. Các bài bổ sung không cần file tải ngoài; chúng luyện quyết định và cách giải thích, không thay thế thao tác thực tế của bài Excel/Power BI gốc.

## Theo dõi và chấm bài

Mỗi bài nộp gắn với mã học viên, không dùng nhóm làm đơn vị sở hữu. Giảng viên vào **Xem kết quả** để xem số đã nộp, chưa nộp, đã chấm; mở danh sách chưa nộp để nhắc bài. Bài trắc nghiệm chấm tự động. Bài tự luận và thực hành chấm toàn bài, có điểm tối đa và nhận xét. Thang gợi ý cho bài bổ sung: đúng tình huống 3 điểm, giải pháp và lý do 4 điểm, kiểm chứng 3 điểm.

Nên đóng bài rồi chấm. Nếu mở lại cho học viên sửa, bản mới phải chấm lại; hệ thống không áp điểm bản cũ sang bản mới. Học viên chỉ nhận điểm và nhận xét của mình khi giảng viên công bố. CSV có điểm tự động, điểm chấm tay và nhận xét.

Hệ thống tính một bài đã nộp khi học viên bấm Nộp bài và lưu thành công nội dung không rỗng. Đây không phải xác nhận học viên đã hoàn thành mọi yêu cầu; giảng viên đánh giá mức độ hoàn thành khi đọc bài. Bài chưa chấm để trống điểm, không tính là 0.

## Chuẩn bị trước khi dạy các bài gốc

Trong thư mục dự án hiện chưa có sẵn file Excel/Power BI thực hành như `BaoCao_Thang.xlsx`, `DLX_SanLuong_Q3.csv` và bộ dữ liệu Power BI. Giáo trình có hướng dẫn/mã tạo dữ liệu cho một số bài; giảng viên cần chuẩn bị và kiểm tra các file trước giờ học. Bài Power BI trên service còn cần môi trường và tài khoản thử phù hợp. Không dùng kết quả phân tích tình huống để ghi nhận rằng học viên đã thực hiện kiểm thử trên service.

Ứng dụng hiện nhận nội dung, bảng, checklist; chưa có tải tệp bài làm lên máy chủ. Đề trên web đã chỉ rõ cách lưu file, ảnh tại máy học viên, ghi tên file và kết quả vào bài; giảng viên xem file trực tiếp khi chữa. Muốn thu file tập trung cần bổ sung cơ chế nộp tệp riêng.

## Kiểm chứng

- Kiểm thử API với SQLite tạm: hai học viên có bài riêng, danh sách chưa nộp, từ chối bài rỗng và bài nộp khi đóng; chấm điểm hợp lệ, chặn điểm vượt tối đa; ẩn điểm/nhận xét trước công bố; công bố và xuất CSV; chặn chấm nhầm lớp và người chưa đăng nhập; bản sửa không giữ điểm cũ.
- Kiểm tra nội dung: 10 bài bổ sung có mẫu trả lời; 18 câu mới không trùng nguyên câu cuối khóa, chấm đúng; đáp án và phần chữa bài được lọc trên server.
- Kiểm thử trình duyệt Edge: nhập và lưu điểm, giữ đúng điểm sau lần làm mới tự động, học viên thấy điểm/nhận xét đã công bố; không có lỗi JavaScript. Đã xem ảnh giao diện giảng viên và học viên.
- Kiểm tra cú pháp Python và JavaScript. Các kiểm thử này dùng môi trường cục bộ; chưa chạy trên Postgres/Supabase hoặc kiểm chứng cấu hình Power BI thật của đơn vị.

## Nguồn kỹ thuật và pháp lý đối chiếu thêm

RLS áp dụng cho Viewer; quyền Admin, Member và Contributor ở workspace có quyền sửa và không bị giới hạn như Viewer theo [Microsoft Learn – Row-level security](https://learn.microsoft.com/power-bi/service-admin-rls).

Việc thông báo trong 72 giờ phải xét điều kiện áp dụng và tính từ khi phát hiện, không mặc định mọi sự kiện đều cùng nghĩa vụ hoặc tự lấy mốc báo đến đầu mối. Tham khảo hướng dẫn dẫn Điều 23 Luật Bảo vệ dữ liệu cá nhân và Điều 28 Nghị định 356/2025/NĐ-CP của [Bộ Công an](https://mps.gov.vn/chinh-sach-phap-luat/bai-viet/canh-bao-nguy-co-vi-pham-phap-luat-ve-an-ninh-mang-doi-voi-doanh-nghiep-ho-kinh-doanh-trong-qua-trinh-chuyen-doi-so-1785806444). Phần này đối chiếu hai điểm dễ gây hiểu nhầm trong bài dạy, không phải rà soát pháp lý toàn bộ quy trình nội bộ của đơn vị.
