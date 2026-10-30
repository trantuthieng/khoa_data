# Buổi 9 – Kịch bản tổ chức bài điều tra toàn bộ log

**Chỉ dành cho giảng viên. Có tiết lộ đáp án.**

Tài liệu này đi cùng `BUOI_9_DE_THUC_HANH_HOC_VIEN.md`, dựa trên đáp án riêng, hướng dẫn học viên, thống kê kỹ thuật, file log và giáo trình Word buổi 9. Chưa tích hợp hoặc thay đổi webapp. Đề giữ hình thức làm và nộp cá nhân theo bản tổ chức lớp hiện có.

## Điều cần thay đổi trong cách giao bài

Hướng dẫn gốc yêu cầu ít nhất 15 vấn đề, ba timeline và ba đối chứng nhưng chưa có cơ chế giúp học viên rà đủ nguồn. Học viên dễ tìm một vài từ như ERROR, export, failed rồi dừng lại. File thực tế có 9.637 INFO, 337 WARN, 25 ERROR và một DEBUG; nhiều dấu vết quan trọng nằm trong các thao tác thành công.

Nên hiểu mục tiêu “đọc toàn bộ log” là **công cụ xử lý đủ 10.000 bản ghi, học viên rà có hệ thống mọi nguồn và ngày, rồi đọc sâu các chuỗi liên quan**. Không thể xác nhận học viên hiểu từng dòng chỉ bằng thanh tiến độ hoặc số dòng đã mở. Đọc thủ công tuần tự 10.000 dòng trong một buổi cũng không phải mục tiêu hợp lý.

Bộ log có 60 tình huống thiết kế, gồm cả đối chứng và trường hợp cần xác minh; không phải 60 sự cố đã xác nhận. Có 458 dòng được gài vào tình huống và 9.542 dòng nền. Các con số này dùng để kiểm tra thiết kế và chữa bài, không dùng làm chỉ tiêu bắt học viên tìm đủ.

## Nhịp buổi học đề xuất: 08:00–11:30

Đây là phương án thay phần thực hành bằng bộ 10.000 dòng, giữ tổng 3,5 giờ của giáo trình. Chọn trước phương án này; không cộng thêm toàn bộ hai vòng thực hành cũ vào cùng lịch.

| Giờ | Hoạt động | Cách tạo tương tác |
|---|---|---|
| 08:00–08:10 | Mở ca, giao vai chuyên viên điều tra cá nhân | Mỗi người ghi một điều muốn biết và một kết luận chưa được phép đưa ra |
| 08:10–08:35 | Ôn sự kiện–cảnh báo–sự cố, trường log, bảo toàn bằng chứng | Chiếu một dòng, hỏi “dòng này chứng minh được điều gì?” |
| 08:35–08:55 | Làm mẫu lọc, đọc details, mở rộng phạm vi và ghép nguồn | Dùng bản ghi nền; không chỉ trước các dòng có đáp án |
| 08:55–09:10 | Chặng 1: nhận ca và bản đồ | Học viên tự đếm; giảng viên hỏi ngẫu nhiên một nguồn ít dòng |
| 09:10–09:35 | Chặng 2: rà đủ phạm vi | Kiểm tra phiếu nguồn/ngày; không chỉ hỏi đã tìm bao nhiêu lỗi |
| 09:35–09:50 | Nghỉ | |
| 09:50–10:30 | Chặng 3: hồ sơ điều tra | Mở dần các thẻ thử thách dưới đây |
| 10:30–10:45 | Chặng 4: phản biện | Mỗi người tự sửa một nhận định sau khi tìm thêm bằng chứng |
| 10:45–10:55 | Chặng 5: bàn giao | Chốt hai timeline và ba ưu tiên |
| 10:55–11:30 | Chữa bài và chuyển đầu vào sang buổi 10 | Chọn bài có lập luận khác nhau, yêu cầu dẫn event và nguồn |

Chuẩn bị công cụ và hướng dẫn mở JSONL trước giờ học. Với lớp chưa quen lọc log, giảm số hồ sơ trong lớp xuống năm, hoàn thiện tám hồ sơ ở nhà; giữ yêu cầu rà nguồn và phản biện. Mốc 120 phút là thời lượng đề xuất cần điều chỉnh sau một lần dạy thử, không phải kết quả đã kiểm nghiệm trên lớp.

## Các thẻ thử thách mở dần

Các câu trong ngoặc kép có thể đọc cho học viên; phần đáp án bên dưới không phát trước. Đây là yêu cầu điều tra, không phải bằng chứng mới ngoài file.

**Thẻ 1 – Thành công có an toàn?** Mở đầu chặng 3: “Hãy tìm một thao tác thành công nhưng quyền hoặc chính sách đi kèm khiến bạn muốn điều tra.”

Chữa bằng S38: EVT000315 cho thấy miễn MFA không hạn, EVT002280 ghi đăng nhập thiết bị ngoài quản lý, bypass theo policy. Hai bản ghi cách nhau nhiều ngày. Cần kiểm tra ngoại lệ và phiên; không gọi tên người thao tác thật. Có thể chấp nhận phát hiện khác nếu chứng minh tương đương.

**Thẻ 2 – Mỗi lần đều ít.** Sau khoảng 10 phút: “Nếu mỗi lần xuất không lớn, bạn sẽ kiểm tra kiểu nào để phát hiện một mẫu kéo dài nhiều ngày?”

Chữa bằng S34: 16 bản ghi từ EVT002347/EVT002351 đến EVT009389/EVT009395. Ghép actor, session, tên file/resource và các phần dữ liệu; tổng hợp xuyên ngày. Không lấy tổng số dòng xuất làm số khách hàng duy nhất nếu chưa kiểm tra trùng lặp. Trong tình huống này có chi tiết partitions_non_overlapping để hỗ trợ nhận định, vẫn cần kiểm chứng dữ liệu nguồn.

**Thẻ 3 – Hãy cứu một cảnh báo khỏi kết luận vội.** Sau khoảng 20 phút: “Chọn một thao tác ban đầu có vẻ đáng ngờ. Tìm bằng chứng có thể khiến bạn đổi ý.”

Chữa bằng S44: EVT005812, EVT005816, EVT005817. Đăng nhập 22:10, xuất 10.420 dòng nhưng có VPN công ty, passkey, ticket, phạm vi dữ liệu và cửa sổ phê duyệt. Lượng lớn và ngoài giờ chưa đủ để kết luận xâm nhập. Các đối chứng khác: S45, S46, S53.

**Thẻ 4 – Vì sao không ai nhận cảnh báo?** Sau khoảng 30 phút: “Không có cảnh báo có thể do hoạt động bình thường, do luật không phù hợp hoặc do cơ chế giám sát. Hãy tìm bằng chứng phân biệt.”

Chữa bằng S50: EVT009369 tắt luật, EVT009371 xuất 8.700 dòng và alert_fired=false, EVT009372 ghi suppressed_alert_count=1. Phân biệt với S32 tắt audit và S33 sai hash/cố xóa archive. Không đồng nhất mất cảnh báo với mất log.

**Thẻ 5 – Phản ánh của khách hàng.** Dùng khi chữa hoặc mở rộng: “Đọc EVT009393 và EVT009396. Bạn sẽ kiểm tra những đường dữ liệu nào trước khi nói nguồn rò rỉ ở đâu?”

Chữa bằng S58. Có đầu mối tham chiếu DN_full_customers và có thể quay về S50; đó là hướng kiểm tra, chưa chứng minh quan hệ nhân quả hoặc nguồn duy nhất. Không ép ghép tất cả 60 tình huống thành một cuộc tấn công chung.

## Cách giúp học viên đi hết phạm vi

1. Mỗi người phải có phiếu cho 29 nguồn và 10 ngày. Nguồn ít dòng được đọc toàn bộ; nguồn nhiều dòng phải có thống kê toàn nguồn, mẫu nền và truy vấn ngoại lệ. Kiểm tra phép đếm tổng phải khớp 10.000.
2. Sau mỗi dấu hiệu, yêu cầu ghi “tôi đã mở rộng lại toàn file bằng trường nào?”. Không chỉ ghép `actor_id`: người thay quyền có thể khác người nhận quyền, nên phải tìm cả `resource_id` và các trường đích trong `details`.
3. Mỗi người phải quay lại một ngày khác và đọc ít nhất một nguồn hiếm. Chỉ chia theo từng ngày hoặc nguồn sẽ làm đứt chuỗi; nếu trao đổi chung cả lớp, bài nộp vẫn là phân tích cá nhân.
4. Hỏi bất chợt “mẫu bình thường bạn dùng so sánh ở đâu?”. Khen việc loại trừ có bằng chứng và tự sửa nhận định ngang với tìm phát hiện mới.
5. Không công bố mã S01–S60, số dòng gài hoặc tiêu đề tình huống trước khi đóng bài. Sau công bố có thể cho học viên chọn một hồ sơ bỏ sót để viết lại cách truy tìm.

Phiếu rà soát chứng minh phương pháp và phạm vi khai báo, không chứng minh đã phát hiện mọi bất thường. Không chấm điểm dựa riêng vào số lần nhấp hoặc việc mở đủ trang.

## Mốc kiểm tra dữ liệu dành riêng giảng viên

Các số sau đã đối chiếu trực tiếp file log với `thong_ke_ky_thuat.json`:

- 10.000 JSON hợp lệ; 5 vùng; 29 nguồn; 20–29/10/2026, dấu thời gian có `+07:00` trong các bản ghi đã dùng minh họa.
- PUBLIC 4.325; INTERNAL 2.910; SALES_ADMIN 2.037; ANALYTICS 521; INFRA 207.
- Ba nguồn lớn nhất: nginx_access 5.947, sales_app 1.786, identity 814. Tổng 8.547 dòng; vì vậy không thể coi xem ba nguồn lớn là rà toàn bộ hệ thống.
- Những nguồn chỉ có một dòng: database, dns, endpoint, payment_gateway. Ít dòng không đồng nghĩa ít quan trọng.

Số dòng theo **ngày của `ts`**, không phải ngày nhận log:

| Ngày tháng 10/2026 | Dòng |
|---|---:|
| 20 | 1.001 |
| 21 | 973 |
| 22 | 974 |
| 23 | 968 |
| 24 | 982 |
| 25 | 1.011 |
| 26 | 1.136 |
| 27 | 1.031 |
| 28 | 940 |
| 29 | 984 |

Lưu ý S43 khi chữa: EVT004303 (role_change) đứng trước EVT004305 (export) trong file, nhưng `ts` của export (09:02:20) sớm hơn `ts` của role_change (09:03:55), trong khi details có effective_at=08:58, permission_cached_at=08:58 và source_clock_skew_seconds=-190. Chưa đủ kết luận vượt quyền. Bản đáp án đã sửa câu mô tả thứ tự cũ (“export xuất hiện trước grant trong file”); không dùng lại cách diễn đạt đó.

Bộ 10.000 dòng có bối cảnh bán hàng và khoảng 10 ngày; log 17 dòng trong giáo trình có bối cảnh điện lực và đêm 20–21/10. Không lấy số lượng xuất, nhân vật hoặc giờ của bộ này để điền vào đáp án bộ kia. Nếu cần luyện đổi UTC, dùng riêng ví dụ giáo trình; không cộng 7 giờ lần nữa cho các thời điểm đã có +07:00.

## Chấm và chữa để bài sống động

Áp dụng thang 10 điểm công khai trong đề. Ở mục tám phát hiện, chấm theo chất lượng bằng chứng và độ bao phủ, không theo số thuật ngữ. Một vụ có nhiều dấu vết vẫn tính một hồ sơ; tám dòng bất thường của cùng chuỗi không thành tám phát hiện.

Khi chữa, chọn ba kiểu bài: kết luận có chuỗi bằng chứng; kết luận đã tự sửa sau khi có đối chứng; kết luận còn thiếu nguồn kiểm chứng. Cho người viết trình bày trong 60 giây rồi hỏi: “Dòng nào chứng minh? Điều gì chưa biết? Lấy thêm bằng chứng ở đâu?”. Không dùng tốc độ tìm thấy hoặc cáo buộc mạnh làm tiêu chí thắng.

Nếu muốn trao danh hiệu vui, dùng “Truy vết xuyên ngày”, “Phản biện có bằng chứng”, “Bàn giao rõ nhất”. Không trao điểm thêm ngoài thang chỉ vì học viên tìm đúng tình huống giảng viên gợi ý.

Kết thúc, mỗi học viên chọn ba hồ sơ ưu tiên và danh sách bằng chứng cần giữ để chuyển sang buổi 10. Chỉ mô phỏng đề xuất ứng phó; không yêu cầu thao tác lên hệ thống thật. Với giữ chứng cứ và hạn chế ảnh hưởng đang diễn ra, yêu cầu phối hợp kịp thời theo thẩm quyền, không dạy chờ thu thập hoàn hảo mới ngăn chặn.
