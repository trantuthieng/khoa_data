# Đối chiếu với Slide ATUD 5 ngày

Ngày kiểm tra: 25/10/2026.

Nguồn: `C:\Users\trant\Downloads\Slide ATUD 5 ngày.pptx`, 111 slide. Đã đọc nội dung chữ và bảng trong các slide, xem riêng hai ảnh hướng dẫn RLS ở slide 76–77. File thuyết trình được giữ nguyên. Phạm vi chỉnh sửa là bài học và bài tập trong `webapp`.

## Kết luận

Không thấy thiếu chủ đề lớn so với slide. Bản web diễn giải rộng hơn nhiều nội dung trong slide, nhưng trước lần bổ sung này còn thiếu một lộ trình thực hành ngắn cho người mới dùng SQL/Python, bộ dữ liệu nhỏ có thể chạy ngay và phần giải thích sự khác nhau giữa mô hình BI ngày/tháng. Hai ảnh hướng dẫn RLS trong slide cũng chưa có trên web.

Đã bổ sung 26 bài cá nhân: 8 SQL, 8 Python, 10 Power BI. Mỗi bài tập trung một thao tác, có mẫu để làm tiếp, nơi ghi kết quả và giải thích. Giảng viên mở, đóng, xem ai nộp, chấm điểm và công bố theo luồng hiện có. Không phát lời giải trong gói tải cho học viên.

## Đối chiếu theo từng buổi

| Slide | Buổi trên web | Nội dung cần có | Kết quả |
|---|---|---|---|
| 1–2 | Tổng quan | Lộ trình 5 ngày, 10 buổi, lý thuyết và thực hành | Đã có cấu trúc 10 buổi. Bài mới là ngân hàng lựa chọn, không cộng tất cả vào thời lượng chính |
| 3–15 | 1 | CIA, vòng đời, nhận diện, phân loại, nhãn/quyền, AI và bài phân loại | Đã có. Slide yêu cầu 4 nhóm dữ liệu; web thêm file khách hàng làm trường hợp thứ 5 để nối câu chuyện |
| 16–25 | 2 | GDPR/PDPA ở mức nhận thức, bốn câu hỏi tuân thủ, lỗi nhập/xuất/gửi, data flow và bản sao | Đã có. Web mở rộng thêm bối cảnh pháp luật Việt Nam; không tự coi PDPA là luật của một quốc gia khi slide chưa chỉ rõ |
| 26–37 | 3 | Định danh/xác thực/quyền, quyền tối thiểu, RBAC/ABAC, ma trận, vòng đời và điều chuyển | Đã có hai bài cá nhân về ma trận và điều chuyển, gồm kiểm thử được phép/từ chối |
| 38–47 | 4 | Yếu tố xác thực, MFA, passkey, SSO, tài khoản chung, phiên và bàn giao ca | Đã có. Các yêu cầu phân vai trong tài liệu tham khảo được tổ chức thành phương án cá nhân trên web |
| 48–57 | 5 | Mã hóa, khóa, TLS, bản sao lưu, quy trình chia sẻ, thử mở sai quyền/mật khẩu | Đã có. Bài gốc vẫn cần giảng viên chuẩn bị file Excel mẫu và môi trường thao tác |
| 58–69 | 6 | Masking/giả danh/ẩn danh, chọn cột, SQL tổng hợp, Python che dữ liệu, masking động, tham số hóa, bản xuất và AI | Đã có lý thuyết và bài lớn. Đã thêm 16 bài ngắn cùng dữ liệu 6 dòng, khung chạy SQLite/Python và lời giải có kiểm soát |
| 70–81 | 7 | Mô hình, RLS, View as, Security/Test as role, workspace, nhiều role, cột, xuất/chia sẻ và Publish to web | Đã có. Đã thêm cầu nối mô hình ngày/tháng, hai ảnh RLS và 10 bài ngắn từ nhập dữ liệu tới kiểm thử service |
| 82–90 | 8 | Phishing, áp lực tâm lý, email/file/QR, HTTPS, xác minh độc lập và báo đầu mối | Đã có. Web có 4 tình huống, thêm MFA giả danh CNTT so với 3 tình huống trong slide |
| 91–101 | 9 | Log vận hành/kiểm toán, trường log, giám sát, bảo vệ log, giả thuyết, timeline và bằng chứng | Đã có cả bài log 5 dòng tương ứng slide 97 và bài mở rộng 17 dòng; không kết luận danh tính từ tài khoản |
| 102–110 | 10 | Báo cáo ban đầu, vai trò, cô lập và duy trì vận hành, bằng chứng, truyền thông, phục hồi, diễn tập | Đã có bài diễn tập 5 đợt. Học viên tự lập phương án theo các vai, nộp cá nhân; không thao tác hệ thống sản xuất |
| 111 | Kết thúc | Trang cảm ơn | Không phát sinh yêu cầu kiến thức hoặc bài tập |

## Các chỗ đã bổ sung hoặc làm rõ

### SQL và Python: từ ví dụ đọc hiểu sang bài tự làm

Slide 62 có truy vấn tổng hợp và slide 63 có hàm che điện thoại. Slide 68 yêu cầu học viên tạo cả bản SQL và Python. Trên web trước đó có các ví dụ dài và bài lớn, nhưng chưa có dãy bài đi từ chọn hai cột tới lọc, cộng, gộp và kiểm tra. Bộ mới dùng cùng 6 khách hàng giả lập, tránh bắt người mới xử lý hàng nghìn dòng ngay từ đầu.

| Nhóm | Bài | Kỹ năng |
|---|---|---|
| SQL | 01–03 | SELECT hai cột, WHERE đơn vị, điều kiện sản lượng |
| SQL | 04–07 | COUNT/SUM, GROUP BY, HAVING và AND |
| SQL | 08 | Tham số `?` của sqlite3, truyền giá trị tách khỏi lệnh |
| Python | 01–03 | Đọc danh sách, cắt chuỗi che điện thoại, tạo bản chỉ có trường cần |
| Python | 04–05 | Lọc bằng if, cộng theo đơn vị bằng từ điển |
| Python | 06–08 | Xử lý ô trống, đổi chuỗi số, lưu JSON và đọc lại để kiểm tra |

SQL/Python chỉ cần Python 3 và thư viện chuẩn, không yêu cầu pandas hoặc máy chủ SQL. File khung tạo cơ sở dữ liệu trong bộ nhớ. Gói tải có `customers.json`, hai file `.py` và hướng dẫn. Nếu máy chưa có Python, học viên có thể ghi dự đoán nhưng phải đánh dấu **Chưa chạy**, không được coi là đã thực hành.

Ngưỡng 2 khách ở bài HAVING chỉ giúp nhìn rõ cú pháp trên bộ nhỏ, không phải tiêu chuẩn ẩn danh. Bỏ tên, che điện thoại hoặc tổng hợp không tự chứng minh an toàn để dùng AI. Các bài vẫn yêu cầu xét khả năng nhận diện và phê duyệt công cụ/dữ liệu.

### Power BI: thống nhất mức chi tiết và cách đếm

Slide 72 có `DimNgay(Ngay, Thang)` và `FactDien(MaDonVi, Ngay, kWh)`. Bài lớn trên web dùng `DimThang` cùng `SoKH` đã tổng hợp theo tháng. Đây là khác mức chi tiết, không thể đổi tên bảng rồi dùng chung mọi công thức.

Slide 81 yêu cầu số khách hàng, nhưng sơ đồ slide 72 chưa nêu mã khách hoặc số khách. Bộ nhỏ bổ sung `MaKH` giả lập để dùng `DISTINCTCOUNT`. Có 8 dòng theo ngày nhưng chỉ 6 khách, giúp học viên thấy ngay việc đếm dòng khác đếm khách. Với nguồn tổng hợp không có mã khách, phải chọn chỉ tiêu phù hợp; không thêm định danh thật chỉ để khớp bài luyện.

| Bài BI | Thao tác |
|---|---|
| 01 | Nhập ba bảng nhỏ bằng Enter data, đặt kiểu dữ liệu |
| 02 | Tạo hai quan hệ một–nhiều đang hoạt động |
| 03 | SUM và một Card tổng sản lượng |
| 04 | DISTINCTCOUNT so với COUNTROWS |
| 05 | Slicer và giới hạn của bộ lọc giao diện |
| 06 | RLS tĩnh, View as A và B |
| 07 | Phát hiện và sửa quan hệ bị tắt trong bản sao thực hành |
| 08 | Thử đồng thời hai role để thấy hợp quyền |
| 09 | Lọc theo ngày và kiểm tra số khách bị lặp giữa các ngày |
| 10 | Tùy chọn: publish, gán role và thử tài khoản Viewer thật trên service |

Đã đưa ảnh từ slide 76–77 vào phần chuẩn bị BI, ghi rõ là ảnh tài liệu có thể khác giao diện hiện tại. Bài service vẫn cần giấy phép, workspace và tài khoản thử. Không dùng Member/Admin/Contributor làm bằng chứng RLS của Viewer đã đúng. Không bật Publish to web để minh họa.

## Cách dùng trong lớp

Mọi bài đều nộp cá nhân. Các bài ngắn thường 5–10 phút; nhập dữ liệu BI và kiểm thử service có thể cần thêm thời gian. Đây là ngân hàng bài tập, không yêu cầu làm toàn bộ trong một buổi.

Gợi ý chọn trước giờ học: SQL 01, 02, 05, 08; Python 02, 03, 05; BI 01, 02, 03, 06. Những bài còn lại giao luyện thêm hoặc dùng để chữa lỗi. Bài lớn của giáo trình vẫn dùng để ghép các kỹ năng sau khi học viên đã quen.

Tiêu chí gợi ý mỗi bài 10 điểm: mã/thao tác 4, kết quả/đối chiếu 3, giải thích 3. Giảng viên có thể điều chỉnh theo đối tượng. Học viên ghi mã/thao tác, kết quả, giải thích và trạng thái đã chạy/chưa chạy/còn lỗi. File và ảnh lưu trên máy để giảng viên xem trực tiếp; ứng dụng chưa thu tệp đính kèm.

## Kiểm chứng và giới hạn

Đã chạy cả 8 lời giải SQL và 8 lời giải Python trên dữ liệu mẫu, kiểm tra đầu ra. File khung và gói ZIP chạy/đọc được. Đã kiểm tra số liệu BI bằng phép tính độc lập: tổng 1.770 kWh, 8 dòng, 6 khách; DV_A 560, DV_B 810, DV_C 400; A hợp B là 1.370. Đây là đối chiếu dữ liệu, không phải tuyên bố đã chạy DAX hoặc Power BI service. Cần làm thử trên Power BI của lớp trước buổi dạy để xác nhận giao diện, quan hệ và quyền thực tế.

Kiểm thử ứng dụng bao gồm việc ẩn lời giải trước công bố và giữ mẫu nộp cá nhân cho đủ 26 bài mới, cùng các kiểm thử nộp/chấm điểm đã có.

Đã thử thêm trên trình duyệt Edge: học viên mở trực tiếp đề SQL có mẫu điền tiếp, tải ZIP, nộp bài cá nhân; giảng viên nhận đúng bài và lưu điểm; phần chuẩn bị BI hiển thị cả hai ảnh RLS. Không gặp lỗi JavaScript trong luồng này. Kiểm tra trình duyệt áp dụng cho web lớp học, không phải cho ứng dụng Power BI Desktop.

Nguồn kỹ thuật đối chiếu: [Python sqlite3 về tham số hóa](https://docs.python.org/3/library/sqlite3.html), [Microsoft về RLS và vai trò workspace](https://learn.microsoft.com/power-bi/service-admin-rls), [Microsoft về measure](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-measures), [Microsoft về tổng hợp và đếm khác biệt](https://learn.microsoft.com/en-us/power-bi/create-reports/service-aggregates).
