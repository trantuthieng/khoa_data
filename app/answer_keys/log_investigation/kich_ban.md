# Buổi 9 – Kịch bản tổ chức bài điều tra toàn bộ log

**Chỉ dành cho giảng viên. Có tiết lộ đáp án.**

Tài liệu này đi cùng `BUOI_9_DE_THUC_HANH_HOC_VIEN.md` và bài `m09-loglab-v1` trên webapp. Đề đã được rút gọn cho lớp có kiến thức trung bình: làm cá nhân, 4 bước, 5 phát hiện, 1 lần kiểm tra lại, 1 timeline, bàn giao tối đa 150 từ.

## Mục tiêu của bản đơn giản

Học viên không cần đọc hết 10.000 dòng hay rà đủ 29 nguồn. Mục tiêu là ba thói quen: **dẫn đúng event_id và giá trị trong log**, **tìm thêm dòng liên quan trước khi kết luận**, và **nói được điều gì còn chưa chắc**. File thực tế có 9.637 INFO, 337 WARN, 25 ERROR và 1 DEBUG, nên nhắc học viên rằng nhiều dấu vết quan trọng nằm ở các thao tác thành công.

Đề có sẵn gợi ý từ khóa (`anyone`, `public_read`, `disabled`, `"approved_ticket":null`, `unmanaged`, nguồn `backup`). Mỗi từ khóa đưa học viên tới một nhóm dòng nhỏ, đọc được trong vài phút. Học viên khá có thể làm thêm 8 phát hiện hoặc rà theo nguồn ở mục tùy chọn.

Bộ log có 60 tình huống thiết kế, gồm cả đối chứng và trường hợp cần xác minh; không phải 60 sự cố đã xác nhận. Không dùng con số này làm chỉ tiêu.

## Nhịp buổi học đề xuất: 08:00–11:30

| Giờ | Hoạt động | Cách tạo tương tác |
|---|---|---|
| 08:00–08:10 | Mở ca, giao vai người trực ca | Hỏi: “Một dòng log chứng minh được điều gì, và không chứng minh được điều gì?” |
| 08:10–08:35 | Ôn sự kiện–cảnh báo–sự cố, các trường log, giữ bằng chứng | Chiếu một dòng nền, cả lớp trả lời 5 câu: khi nào, ai, từ đâu, làm gì, kết quả |
| 08:35–08:55 | Làm mẫu trên bàn điều tra: tìm kiếm, mở chi tiết, bấm actor_id để tìm tiếp, ghim event | Làm mẫu trên dòng nền; không mở trước các dòng có đáp án |
| 08:55–09:05 | Bước 1: làm quen dữ liệu | Hỏi ngẫu nhiên vài người: tổng số dòng, số nguồn, một dòng đã đọc |
| 09:05–09:35 | Bước 2 (phần đầu): tìm phát hiện | Đi quanh lớp, hỏi “Giá trị nào trong details làm bạn lo?” |
| 09:35–09:50 | Nghỉ | |
| 09:50–10:05 | Bước 2 (phần cuối): đủ 5 phát hiện | Mở thẻ 1 và thẻ 4 nếu lớp bị bí |
| 10:05–10:20 | Bước 3: kiểm tra lại một nghi vấn | Mở thẻ 3 |
| 10:20–10:40 | Bước 4: timeline và bàn giao | Kiểm tra mỗi người có ít nhất 3 event, 2 nguồn |
| 10:40–11:30 | Chữa bài, chuyển đầu vào sang buổi 10 | Chọn 3 bài có cách làm khác nhau, yêu cầu dẫn event |

Với lớp còn chậm: giảm xuống 3 phát hiện trong giờ, làm nốt 2 phát hiện ở nhà; vẫn giữ bước kiểm tra lại. Thời lượng 90 phút là đề xuất, cần chỉnh sau một lần dạy thử.

## Các thẻ gợi ý mở dần

Các câu trong ngoặc kép có thể đọc cho học viên; phần đáp án bên dưới không phát trước. Thẻ 1, 3 và 4 dùng trong giờ; thẻ 2 và 5 dùng khi chữa bài hoặc cho học viên khá.

**Thẻ 1 – Thành công có an toàn?** “Hãy tìm một thao tác thành công (INFO) nhưng vẫn khiến bạn lo.”

Chữa bằng S38: EVT000315 cho thấy miễn MFA không hạn (`expiry: null`), EVT002280 ghi đăng nhập từ `unmanaged-admin-64`, `mfa: bypassed_by_policy`. Hai dòng cách nhau 2 ngày. Cũng chấp nhận S16 (link anyone) hoặc S50 (tắt luật) nếu chỉ ra đúng giá trị.

**Thẻ 2 – Mỗi lần đều ít (mở rộng).** “Nếu mỗi lần xuất không lớn, làm sao phát hiện một mẫu kéo dài nhiều ngày?”

Chữa bằng S34: 16 dòng từ EVT002347/EVT002351 đến EVT009389/EVT009395. Mỗi ngày dùng session khác nhau, nên phải nối các ngày bằng `actor_id` (nv_bh_hn_01) và tên file `CN_HN_cust_batch_01`…`08`. Có 8 ngày, tổng 1.796 dòng xuất, tải lên personal-drive.example. Không lấy tổng số dòng làm số khách hàng duy nhất nếu chưa kiểm tra trùng lặp.

**Thẻ 3 – Đừng kết luận vội.** “Chọn một thao tác có vẻ đáng ngờ. Tìm bằng chứng có thể khiến bạn đổi ý.”

Chữa bằng S44: EVT005812, EVT005816, EVT005817. Đăng nhập 22:10, xuất 10.420 dòng, nhưng có VPN công ty, passkey, ticket FIN-9812, không có PII và cửa sổ phê duyệt 22:00–23:00. Đối chứng khác dễ tìm: S46 (gõ sai mật khẩu 3 lần rồi MFA thành công), S45 (tên O'Brien, truy vấn tham số hóa).

**Thẻ 4 – Vì sao không ai nhận cảnh báo?** “Không có cảnh báo có thể vì mọi thứ bình thường, hoặc vì cảnh báo bị tắt. Hãy tìm bằng chứng.”

Chữa bằng S50: EVT009369 tắt luật (`change_ticket: null`), EVT009371 xuất 8.700 dòng với `alert_fired=false`, EVT009372 ghi `suppressed_alert_count=1`. Đây cũng là timeline mẫu: 3 event, 2 nguồn. Không đồng nhất mất cảnh báo với mất log.

**Thẻ 5 – Phản ánh của khách hàng (mở rộng).** “Đọc EVT009393 và EVT009396. Bạn sẽ kiểm tra những đường dữ liệu nào trước khi nói nguồn rò rỉ ở đâu?”

Chữa bằng S58. `last_known_export: DN_full_customers` trùng `resource_id` của EVT009371 (S50). Đó là hướng kiểm tra, chưa chứng minh nguyên nhân hoặc nguồn duy nhất.

## Cách hỗ trợ học viên trong giờ

1. Khi học viên chỉ ghi “lộ dữ liệu” hoặc “bị tấn công”, hỏi: “Dòng nào? Trường nào? Giá trị bao nhiêu?”.
2. Khi học viên thấy một dòng lạ, nhắc bấm `actor_id` hoặc `resource_id` để xem dòng liên quan trước khi kết luận.
3. Khen việc hạ mức nghi ngờ có bằng chứng ngang với tìm được phát hiện mới.
4. Không công bố mã S01–S60 hoặc số dòng gài trước khi đóng bài.

## Mốc kiểm tra dữ liệu dành riêng giảng viên

Các số sau đã đối chiếu trực tiếp file log với `thong_ke_ky_thuat.json`:

- 10.000 JSON hợp lệ; 5 vùng; 29 nguồn; 20–29/10/2026, toàn bộ 10.000 giá trị `ts` và `ingested_at` đều có `+07:00`.
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

## Chấm và chữa bài

Thang 10 điểm như trong đề: làm quen dữ liệu 1,5; năm phát hiện 4 (0,8 mỗi phát hiện: có event và giá trị thật 0,4; lý do và việc làm tiếp hợp lý 0,4); kiểm tra lại 1,5; timeline 1,5; bàn giao 1,5. Nhiều dòng của cùng một sự việc vẫn tính một phát hiện. Phát hiện ngoài các tình huống gợi ý vẫn được tính nếu có bằng chứng đúng.

Không trừ điểm vì dùng từ chưa chuẩn (ví dụ gọi “link anyone” là “link công khai”). Trừ điểm khi bịa giá trị không có trong log, hoặc khẳng định tên người thật đã thao tác.

Khi chữa, chọn ba kiểu bài: có bằng chứng rõ; đã tự hạ mức sau khi xem thêm; còn thiếu bằng chứng. Cho người viết trình bày 60 giây rồi hỏi: “Dòng nào chứng minh? Điều gì chưa biết? Hỏi ai để kiểm tra?”.

Kết thúc, mỗi học viên giữ lại ba việc ưu tiên và danh sách bằng chứng để chuyển sang buổi 10. Chỉ mô phỏng đề xuất ứng phó; không thao tác lên hệ thống thật.
