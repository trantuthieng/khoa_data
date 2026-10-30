# ĐÁP ÁN RIÊNG GIẢNG VIÊN – Bộ log website 10.000 dòng

**Không phát tài liệu này cùng file log cho học viên trước khi làm bài.** Dữ liệu hoàn toàn giả lập. Các dòng được sắp theo `ingested_at`; `ts` có thể không đồng thứ tự. Các tình huống "CẦN XÁC MINH" không được coi là sự cố chắc chắn.

- Số dòng log: **10,000**; số tình huống được thiết kế: **60**; số dòng được cố ý gài vào tình huống: **458**. Các dòng còn lại mô phỏng hoạt động bình thường.
- Phân bố zone: ANALYTICS=521, INFRA=207, INTERNAL=2910, PUBLIC=4325, SALES_ADMIN=2037
- Cột `event_id` có số 6 chữ số trùng chính xác số thứ tự dòng trong file `.log`.

## Chỉ mục tình huống

| Mã GV | Cấp độ | Loại kết luận | Chủ đề | Dòng log | Bài học |
|---|---|---|---|---|---|
| S01 | DE | CAN_DIEU_TRA | File giao dịch riêng tư mở công khai | 354, 355, 356, 357, 358 (5 bản ghi) | 1, 2, 5, 9 |
| S02 | DE | CAN_DIEU_TRA | Trang quản trị nhận truy cập chưa xác thực | 442, 443, 444 (3 bản ghi) | 2, 3, 9 |
| S03 | DE | CAN_DIEU_TRA | Tên cửa hàng có dấu nháy gây lỗi truy vấn | 485, 486 (2 bản ghi) | 6, 9 |
| S04 | DE | CAN_DIEU_TRA | WAF chặn thăm dò dấu hiệu injection | 1084, 1085, 1086, 1087, 1088, 1089, 1090, 1091, 1092 (9 bản ghi) | 6, 9 |
| S05 | TRUNG_BINH | CAN_DIEU_TRA | Password spray vào nhiều tài khoản | 1136, 1137, 1138, 1139, 1140, 1141, 1142, 1143, 1144, 1145… (50 bản ghi) | 4, 8, 9 |
| S06 | KHO | CAN_DIEU_TRA | Giả IT thúc ép MFA và truy cập bất thường | 880, 882, 884, 885, 887, 888, 890, 891, 893, 894… (12 bản ghi) | 4, 8, 9, 10 |
| S07 | TRUNG_BINH | CAN_DIEU_TRA | Tài khoản dùng chung xóa đơn hàng, mất khả năng quy trách nhiệm | 1286, 1287, 1288, 1289, 1290, 1292, 1293, 1294, 1295, 1296… (13 bản ghi) | 3, 4, 9 |
| S08 | TRUNG_BINH | CAN_DIEU_TRA | Nhân sự điều chuyển vẫn xuất dữ liệu chi nhánh cũ | 1629, 1630, 1631 (3 bản ghi) | 2, 3, 7, 9 |
| S09 | TRUNG_BINH | CAN_DIEU_TRA | Tài khoản nghỉ việc còn truy cập và xuất báo cáo | 2880, 2881, 2882, 2883 (4 bản ghi) | 3, 4, 9, 10 |
| S10 | TRUNG_BINH | CAN_DIEU_TRA | Tự cấp vai trò quản trị để sửa chính sách | 3036, 3039, 3042 (3 bản ghi) | 3, 4, 9 |
| S11 | TRUNG_BINH | CAN_DIEU_TRA | Một người vừa tạo vừa duyệt hoàn tiền | 3344, 3347, 3350 (3 bản ghi) | 3, 9 |
| S12 | KHO | CAN_DIEU_TRA | Truy cập đơn hàng chi nhánh khác qua API | 3381, 3382, 3383, 3384, 3385, 3386 (6 bản ghi) | 3, 6, 9 |
| S13 | TRUNG_BINH | CAN_DIEU_TRA | Masking giao diện không áp dụng cho export | 3553, 3554 (2 bản ghi) | 1, 6, 7, 9 |
| S14 | DE | CAN_DIEU_TRA | Thu thập vượt mục đích đăng ký nhận tin | 4345, 4346 (2 bản ghi) | 1, 2, 6 |
| S15 | DE | CAN_DIEU_TRA | Secret và thông tin xác thực ghi vào log | 4394, 4395 (2 bản ghi) | 4, 5, 9 |
| S16 | TRUNG_BINH | CAN_DIEU_TRA | Chia sẻ file nhạy cảm bằng link Anyone không hạn | 4405, 4413, 4414, 4420 (4 bản ghi) | 2, 5, 9 |
| S17 | TRUNG_BINH | CAN_DIEU_TRA | Mật khẩu file gửi cùng email chứa file | 4462, 4464 (2 bản ghi) | 5, 8 |
| S18 | DE | CAN_DIEU_TRA | Khóa sửa Sheet nhầm với mã hóa file | 4577, 4578 (2 bản ghi) | 5, 6 |
| S19 | DE | CAN_DIEU_TRA | Đăng nhập quản trị qua HTTP không mã hóa | 5258, 5260 (2 bản ghi) | 5, 9 |
| S20 | TRUNG_BINH | CAN_DIEU_TRA | Bỏ qua lỗi chứng chỉ TLS của kết nối đối tác | 5296, 5299, 5300 (3 bản ghi) | 5, 9 |
| S21 | KHO | CAN_DIEU_TRA | Sao lưu lỗi nhiều ngày, thử phục hồi thất bại | 36, 1036, 2022, 2997, 3955, 4947, 5943, 7093 (8 bản ghi) | 1, 5, 9, 10 |
| S22 | TRUNG_BINH | CAN_DIEU_TRA | Bản sao lưu riêng tư nằm trên bucket công khai | 5981, 5983, 5985 (3 bản ghi) | 1, 5, 9 |
| S23 | DE | CAN_DIEU_TRA | Tăng đột biến request kèm lỗi 503 | 6667, 6668, 6669, 6670, 6671, 6672, 6673, 6674, 6675, 6676… (160 bản ghi) | 1, 9, 10 |
| S24 | KHO | CAN_DIEU_TRA | Credential stuffing từ nhiều IP vào một tài khoản | 7179, 7180, 7181, 7182, 7183, 7184, 7185, 7186, 7187, 7188… (42 bản ghi) | 4, 8, 9 |
| S25 | TRUNG_BINH | CAN_DIEU_TRA | Dữ liệu nội bộ tải lên công cụ AI bên ngoài | 7554, 7556, 7557 (3 bản ghi) | 1, 2, 5, 6, 8 |
| S26 | TRUNG_BINH | CAN_DIEU_TRA | CSV nhập từ đối tác có ô giống công thức | 7669, 7671, 7674 (3 bản ghi) | 6, 8, 9 |
| S27 | KHO | CAN_DIEU_TRA | RLS không còn hiệu lực với workspace Member | 7716, 7717, 7718 (3 bản ghi) | 3, 7, 9 |
| S28 | DE | CAN_DIEU_TRA | Publish-to-web báo cáo doanh số bí mật | 8464, 8465, 8466, 8468, 8469 (5 bản ghi) | 5, 7, 9 |
| S29 | KHO | CAN_DIEU_TRA | Tổng hợp nhóm quá nhỏ có thể tái nhận diện | 8516, 8517 (2 bản ghi) | 1, 6, 7 |
| S30 | KHO | CAN_DIEU_TRA | Đối tác API được quyền rộng hơn hợp đồng | 8550, 8551, 8553, 8554, 8556, 8557, 8558 (7 bản ghi) | 2, 3, 6, 9 |
| S31 | TRUNG_BINH | CAN_DIEU_TRA | Webhook thanh toán chữ ký không hợp lệ vẫn xử lý | 8599, 8600 (2 bản ghi) | 1, 5, 9 |
| S32 | KHO | CAN_DIEU_TRA | Tắt audit trước khi sửa kho và bật lại | 8993, 8996, 9005 (3 bản ghi) | 3, 9, 10 |
| S33 | KHO | CAN_DIEU_TRA | Cố xóa nhật ký và sai hash kiểm toán | 9067, 9068 (2 bản ghi) | 5, 9, 10 |
| S34 | KHO | CAN_DIEU_TRA | Xuất dữ liệu nhỏ giọt nhiều ngày | 2347, 2351, 3288, 3293, 4304, 4308, 5253, 5263, 6274, 6282… (16 bản ghi) | 3, 6, 9, 10 |
| S35 | KHO | CAN_DIEU_TRA | Xuất dữ liệu ngoài giờ trước khi chuyển công tác | 9903, 9904, 9905, 9906, 9908, 9909, 9911, 9914, 9917 (9 bản ghi) | 1, 3, 5, 9, 10 |
| S36 | TRUNG_BINH | CAN_DIEU_TRA | Email giả đăng nhập SSO và click QR | 2396, 2397, 2398, 2400 (4 bản ghi) | 4, 5, 8, 9 |
| S37 | DE | CAN_DIEU_TRA | File đính kèm nguy hiểm bị cách ly | 2407, 2408 (2 bản ghi) | 5, 8, 9 |
| S38 | TRUNG_BINH | CAN_DIEU_TRA | MFA của quản trị viên bị miễn trừ | 315, 2280 (2 bản ghi) | 3, 4, 9 |
| S39 | KHO | CAN_DIEU_TRA | HTTP cache chia sẻ nhầm dữ liệu người dùng | 1543, 1544 (2 bản ghi) | 1, 2, 3, 9 |
| S40 | TRUNG_BINH | CAN_DIEU_TRA | CORS tùy ý với cookies đăng nhập | 2659, 2660 (2 bản ghi) | 3, 5, 9 |
| S41 | TRUNG_BINH | CAN_DIEU_TRA | Giữ dữ liệu đã hết thời hạn lưu trữ | 3299, 3301 (2 bản ghi) | 1, 2, 6, 9 |
| S42 | TRUNG_BINH | CAN_DIEU_TRA | Khóa mã hóa và file nằm cùng chỗ | 4059, 4060 (2 bản ghi) | 5, 9 |
| S43 | KHO | CAN_XAC_MINH | Thứ tự nhận log khác thời điểm sự kiện | 4300, 4303, 4305 (3 bản ghi) | 3, 9 |
| S44 | KHO | DOI_CHUNG_HOP_LE | Xuất báo cáo ngoài giờ nhưng có phê duyệt hợp lệ | 5812, 5816, 5817 (3 bản ghi) | 3, 4, 9 |
| S45 | TRUNG_BINH | DOI_CHUNG_HOP_LE | Cảnh báo WAF với tên có dấu nháy nhưng truy vấn an toàn | 5369, 5370 (2 bản ghi) | 6, 9 |
| S46 | DE | DOI_CHUNG_HOP_LE | Gõ sai mật khẩu vài lần rồi MFA thành công | 6233, 6234, 6235, 6236 (4 bản ghi) | 4, 9 |
| S47 | TRUNG_BINH | CAN_DIEU_TRA | Giả danh nhà cung cấp yêu cầu gửi bảng khách hàng | 6502, 6506 (2 bản ghi) | 5, 8, 9 |
| S48 | KHO | CAN_DIEU_TRA | Sửa giá bán sâu và hóa đơn không có duyệt | 7750, 7753, 7756 (3 bản ghi) | 1, 3, 9 |
| S49 | KHO | CAN_DIEU_TRA | Đổi mật khẩu IdP nhưng phiên ứng dụng vẫn dùng được | 8838, 8843 (2 bản ghi) | 4, 9, 10 |
| S50 | KHO | CAN_DIEU_TRA | Quy tắc cảnh báo bị vô hiệu trước hoạt động nhạy cảm | 9369, 9371, 9372 (3 bản ghi) | 3, 9, 10 |
| S51 | DE | CAN_DIEU_TRA | Dữ liệu định danh đặt trong URL rồi bị ghi log | 605, 608 (2 bản ghi) | 1, 5, 9 |
| S52 | KHO | CAN_DIEU_TRA | QR thanh toán bị đổi điểm đến | 9502, 9503, 9507 (3 bản ghi) | 1, 8, 9, 10 |
| S53 | TRUNG_BINH | DOI_CHUNG_HOP_LE | Khuyến mại giảm giá lớn nhưng có duyệt | 1454, 1456 (2 bản ghi) | 3, 9 |
| S54 | TRUNG_BINH | CAN_DIEU_TRA | Source map công khai tiết lộ thông tin nội bộ | 1735 (1 bản ghi) | 1, 5, 9 |
| S55 | KHO | CAN_DIEU_TRA | Dấu hiệu injection dẫn tới truy vấn trả quá nhiều dòng | 2038, 2039, 2040 (3 bản ghi) | 6, 9 |
| S56 | TRUNG_BINH | CAN_DIEU_TRA | Redirect SSO sang miền ngoài do tham số next | 3450 (1 bản ghi) | 4, 5, 8 |
| S57 | KHO | CAN_DIEU_TRA | Sai lệch chữ ký/hash bảng giá trước nhập liệu | 9766, 9767 (2 bản ghi) | 1, 5, 9, 10 |
| S58 | KHO | CAN_DIEU_TRA | Khách báo cuộc gọi lừa đảo biết đúng dữ liệu nội bộ | 9393, 9396 (2 bản ghi) | 1, 2, 5, 8, 9, 10 |
| S59 | TRUNG_BINH | CAN_DIEU_TRA | Kết nối DB sản xuất từ thiết bị ngoài quản lý | 2574, 2576 (2 bản ghi) | 3, 5, 6, 9 |
| S60 | KHO | CAN_DIEU_TRA | Ghép hai bảng tổng hợp có thể suy ra một người | 8697, 8699 (2 bản ghi) | 1, 6, 7, 9 |

## Phân tích bằng chứng theo tình huống

### S01 – File giao dịch riêng tư mở công khai

- **Độ khó:** DE; **định tính:** CAN_DIEU_TRA; **chủ đề:** `PUBLIC_EXPOSURE`; **bài:** 1, 2, 5, 9.
- **Dòng liên quan (5):** 354, 355, 356, 357, 358
- **Event ID tiêu biểu:** EVT000354, EVT000355, EVT000356, EVT000357, EVT000358
- **Nhận định:** ACL public-read của file doanh thu nội bộ; khách không đăng nhập vẫn tải được.
- **Cần kiểm chứng/ứng phó:** Xác minh độ nhạy, lịch sử download, thu hồi ACL và lưu bằng chứng.

### S02 – Trang quản trị nhận truy cập chưa xác thực

- **Độ khó:** DE; **định tính:** CAN_DIEU_TRA; **chủ đề:** `ACCESS_CONTROL`; **bài:** 2, 3, 9.
- **Dòng liên quan (3):** 442, 443, 444
- **Event ID tiêu biểu:** EVT000442, EVT000443, EVT000444
- **Nhận định:** Endpoint /quan-tri/thiet-lap trả 200 với khách nặc danh.
- **Cần kiểm chứng/ứng phó:** Kiểm tra quyền thực thi thực tế; trả 200 chưa đủ chứng minh có thể sửa dữ liệu.

### S03 – Tên cửa hàng có dấu nháy gây lỗi truy vấn

- **Độ khó:** DE; **định tính:** CAN_DIEU_TRA; **chủ đề:** `SQL_ERROR`; **bài:** 6, 9.
- **Dòng liên quan (2):** 485, 486
- **Event ID tiêu biểu:** EVT000485, EVT000486
- **Nhận định:** Tra cứu tên hợp lệ có dấu nháy khiến DB lỗi cú pháp và lộ tên bảng.
- **Cần kiểm chứng/ứng phó:** Báo lỗi cho nhóm phát triển; không tự thử chuỗi khai thác, chưa kết luận có khai thác thành công.

### S04 – WAF chặn thăm dò dấu hiệu injection

- **Độ khó:** DE; **định tính:** CAN_DIEU_TRA; **chủ đề:** `BLOCKED_PROBE`; **bài:** 6, 9.
- **Dòng liên quan (9):** 1084, 1085, 1086, 1087, 1088, 1089, 1090, 1091, 1092
- **Event ID tiêu biểu:** EVT001084, EVT001085, EVT001086, EVT001087, EVT001088, EVT001089, EVT001090, EVT001091
- **Nhận định:** Chuỗi truy cập bất thường bị chặn; không có bằng chứng đã xâm nhập.
- **Cần kiểm chứng/ứng phó:** Phân biệt dấu hiệu thăm dò với dữ liệu bị lấy thành công.

### S05 – Password spray vào nhiều tài khoản

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `PASSWORD_SPRAY`; **bài:** 4, 8, 9.
- **Dòng liên quan (50):** 1136, 1137, 1138, 1139, 1140, 1141, 1142, 1143, 1144, 1145, 1146, 1147, 1148, 1149, 1150, 1151, 1152, 1153, 1154, 1155, 1156, 1157, 1158, 1159, 1160, 1161, 1162, 1163, 1164, 1165, 1166, 1167, 1168, 1169, 1170, 1171, 1172, 1173, 1174, 1175, 1176, 1177, 1178, 1179, 1181, 1182, 1183, 1184, 1185, 1186
- **Event ID tiêu biểu:** EVT001136, EVT001137, EVT001138, EVT001139, EVT001140, EVT001141, EVT001142, EVT001143
- **Nhận định:** Một địa chỉ IP thử đăng nhập nhiều nhân viên trong thời gian ngắn, sau đó truy cập thành công một tài khoản.
- **Cần kiểm chứng/ứng phó:** Đối chiếu VPN, thiết bị, MFA và khóa phiên; failed login riêng lẻ chưa đủ kết luận.

### S06 – Giả IT thúc ép MFA và truy cập bất thường

- **Độ khó:** KHO; **định tính:** CAN_DIEU_TRA; **chủ đề:** `MFA_FATIGUE`; **bài:** 4, 8, 9, 10.
- **Dòng liên quan (12):** 880, 882, 884, 885, 887, 888, 890, 891, 893, 894, 897, 901
- **Event ID tiêu biểu:** EVT000880, EVT000882, EVT000884, EVT000885, EVT000887, EVT000888, EVT000890, EVT000891
- **Nhận định:** Tin nhắn mạo danh hỗ trợ xuất hiện đúng lúc nhiều MFA push không do người dùng khởi tạo, một lần sau đó được chấp nhận.
- **Cần kiểm chứng/ứng phó:** Cần xác minh người thao tác, thiết bị, revoke session, lịch sử xuất; không quy kết nhân viên theo mỗi tên tài khoản.

### S07 – Tài khoản dùng chung xóa đơn hàng, mất khả năng quy trách nhiệm

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `SHARED_ACCOUNT`; **bài:** 3, 4, 9.
- **Dòng liên quan (13):** 1286, 1287, 1288, 1289, 1290, 1292, 1293, 1294, 1295, 1296, 1297, 1298, 1299
- **Event ID tiêu biểu:** EVT001286, EVT001287, EVT001288, EVT001289, EVT001290, EVT001292, EVT001293, EVT001294
- **Nhận định:** Tài khoản ca_quay_01 dùng chung, xóa nhiều phiếu/đơn; nhật ký không ghi người trực thực tế.
- **Cần kiểm chứng/ứng phó:** Đối chiếu ca trực camera phiếu công việc; không thể xác định chính xác người xóa chỉ từ account.

### S08 – Nhân sự điều chuyển vẫn xuất dữ liệu chi nhánh cũ

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `PRIVILEGE_DRIFT`; **bài:** 2, 3, 7, 9.
- **Dòng liên quan (3):** 1629, 1630, 1631
- **Event ID tiêu biểu:** EVT001629, EVT001630, EVT001631
- **Nhận định:** Org_unit là CN_DN nhưng Access Matrix còn CN_HCM, vẫn xuất khách hàng CN_HCM.
- **Cần kiểm chứng/ứng phó:** Đối chiếu phiếu điều chuyển, thời hạn ngoại lệ, quyền được duyệt.

### S09 – Tài khoản nghỉ việc còn truy cập và xuất báo cáo

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `OFFBOARDING`; **bài:** 3, 4, 9, 10.
- **Dòng liên quan (4):** 2880, 2881, 2882, 2883
- **Event ID tiêu biểu:** EVT002880, EVT002881, EVT002882, EVT002883
- **Nhận định:** Nhân sự đã nghỉ còn phiên và quyền, xuất báo cáo sau ngày chấm dứt.
- **Cần kiểm chứng/ứng phó:** Kiểm tra thiết bị bàn giao, vô hiệu hóa tài khoản và session, đánh giá dữ liệu bị tác động.

### S10 – Tự cấp vai trò quản trị để sửa chính sách

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `PRIVILEGE_ESCALATION`; **bài:** 3, 4, 9.
- **Dòng liên quan (3):** 3036, 3039, 3042
- **Event ID tiêu biểu:** EVT003036, EVT003039, EVT003042
- **Nhận định:** Tài khoản bán hàng có khả năng tự cấp sales_admin rồi sửa chiết khấu.
- **Cần kiểm chứng/ứng phó:** Đối chiếu hệ thống phê duyệt, quyền GRANT, báo cáo thay đổi giá và hóa đơn.

### S11 – Một người vừa tạo vừa duyệt hoàn tiền

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `SEGREGATION_OF_DUTIES`; **bài:** 3, 9.
- **Dòng liên quan (3):** 3344, 3347, 3350
- **Event ID tiêu biểu:** EVT003344, EVT003347, EVT003350
- **Nhận định:** Refund creator và approver trùng nhau dù quy trình yêu cầu 2 người.
- **Cần kiểm chứng/ứng phó:** Xác minh tài khoản đặc quyền, phân công duty, chứng từ hoàn tiền.

### S12 – Truy cập đơn hàng chi nhánh khác qua API

- **Độ khó:** KHO; **định tính:** CAN_DIEU_TRA; **chủ đề:** `BOLA_IDOR`; **bài:** 3, 6, 9.
- **Dòng liên quan (6):** 3381, 3382, 3383, 3384, 3385, 3386
- **Event ID tiêu biểu:** EVT003381, EVT003382, EVT003383, EVT003384, EVT003385, EVT003386
- **Nhận định:** Nhân viên HCM đọc được đơn DN qua API trả 200 dù scope không cho phép.
- **Cần kiểm chứng/ứng phó:** Đối chiếu org_unit, owner của order, policy tại API; 200 có thể là dữ liệu bị lọt.

### S13 – Masking giao diện không áp dụng cho export

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `MASKING_BYPASS`; **bài:** 1, 6, 7, 9.
- **Dòng liên quan (2):** 3553, 3554
- **Event ID tiêu biểu:** EVT003553, EVT003554
- **Nhận định:** Trên màn hình chỉ thấy số đã che nhưng export có nguyên dữ liệu định danh.
- **Cần kiểm chứng/ứng phó:** Kiểm tra quyền xuất ở lớp API/DB, không coi masking giao diện là phân quyền.

### S14 – Thu thập vượt mục đích đăng ký nhận tin

- **Độ khó:** DE; **định tính:** CAN_DIEU_TRA; **chủ đề:** `DATA_MINIMIZATION`; **bài:** 1, 2, 6.
- **Dòng liên quan (2):** 4345, 4346
- **Event ID tiêu biểu:** EVT004345, EVT004346
- **Nhận định:** Biểu mẫu newsletter thu cả CCCD, tài khoản ngân hàng, ngày sinh không cần thiết.
- **Cần kiểm chứng/ứng phó:** Xem chính sách dữ liệu, mục đích và cột trường cần xóa; log không chứa giá trị định danh thật.

### S15 – Secret và thông tin xác thực ghi vào log

- **Độ khó:** DE; **định tính:** CAN_DIEU_TRA; **chủ đề:** `SECRET_IN_LOG`; **bài:** 4, 5, 9.
- **Dòng liên quan (2):** 4394, 4395
- **Event ID tiêu biểu:** EVT004394, EVT004395
- **Nhận định:** Log DEBUG ghi giá trị giống access token, cần xem là sự cố lộ bí mật.
- **Cần kiểm chứng/ứng phó:** Không sử dụng giá trị demo, lập tức che trong pipeline log, thay thế token bị lộ nếu là thật.

### S16 – Chia sẻ file nhạy cảm bằng link Anyone không hạn

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `ANYONE_LINK`; **bài:** 2, 5, 9.
- **Dòng liên quan (4):** 4405, 4413, 4414, 4420
- **Event ID tiêu biểu:** EVT004405, EVT004413, EVT004414, EVT004420
- **Nhận định:** File khách hàng được chia sẻ ai có link đều xem, không expiry và đã được truy cập từ mạng ngoài.
- **Cần kiểm chứng/ứng phó:** Thu hồi link, kiểm tra lượt tải, owner và các bản sao đã lưu.

### S17 – Mật khẩu file gửi cùng email chứa file

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `WEAK_FILE_SHARING`; **bài:** 5, 8.
- **Dòng liên quan (2):** 4462, 4464
- **Event ID tiêu biểu:** EVT004462, EVT004464
- **Nhận định:** Có mã hóa file nhưng mật khẩu đính ngay cùng email và email gửi ngoài công ty.
- **Cần kiểm chứng/ứng phó:** Yêu cầu kênh xác thực độc lập và duyệt người nhận đúng mục đích.

### S18 – Khóa sửa Sheet nhầm với mã hóa file

- **Độ khó:** DE; **định tính:** CAN_DIEU_TRA; **chủ đề:** `FAKE_ENCRYPTION`; **bài:** 5, 6.
- **Dòng liên quan (2):** 4577, 4578
- **Event ID tiêu biểu:** EVT004577, EVT004578
- **Nhận định:** File chứa báo cáo khách hàng chỉ protect worksheet và mở không cần mật khẩu.
- **Cần kiểm chứng/ứng phó:** Phân biệt bảo vệ chỉnh sửa và bảo vệ khi bị lấy cắp file.

### S19 – Đăng nhập quản trị qua HTTP không mã hóa

- **Độ khó:** DE; **định tính:** CAN_DIEU_TRA; **chủ đề:** `INSECURE_TRANSPORT`; **bài:** 5, 9.
- **Dòng liên quan (2):** 5258, 5260
- **Event ID tiêu biểu:** EVT005258, EVT005260
- **Nhận định:** Ứng dụng cho phép POST đăng nhập admin HTTP và cấu hình redirect tắt.
- **Cần kiểm chứng/ứng phó:** Cần tắt HTTP, ép HTTPS, HSTS và kiểm tra chứng thư; log không ghi mật khẩu.

### S20 – Bỏ qua lỗi chứng chỉ TLS của kết nối đối tác

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `TLS_VALIDATION`; **bài:** 5, 9.
- **Dòng liên quan (3):** 5296, 5299, 5300
- **Event ID tiêu biểu:** EVT005296, EVT005299, EVT005300
- **Nhận định:** Client gọi API nhà cung cấp với verify_tls=False sau cảnh báo chứng chỉ hết hạn.
- **Cần kiểm chứng/ứng phó:** Kiểm tra kênh chính thức, xoay chứng chỉ; không coi kết nối HTTPS là an toàn nếu không kiểm định.

### S21 – Sao lưu lỗi nhiều ngày, thử phục hồi thất bại

- **Độ khó:** KHO; **định tính:** CAN_DIEU_TRA; **chủ đề:** `BACKUP_FAILURE`; **bài:** 1, 5, 9, 10.
- **Dòng liên quan (8):** 36, 1036, 2022, 2997, 3955, 4947, 5943, 7093
- **Event ID tiêu biểu:** EVT000036, EVT001036, EVT002022, EVT002997, EVT003955, EVT004947, EVT005943, EVT007093
- **Nhận định:** Backup giao dịch thất bại liên tiếp, restore test không thành công, mất khả năng phục hồi.
- **Cần kiểm chứng/ứng phó:** Phải xác định RPO/RTO, bản offline/immutable và thử khôi phục được, không chỉ xem job backup tồn tại.

### S22 – Bản sao lưu riêng tư nằm trên bucket công khai

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `BACKUP_EXPOSURE`; **bài:** 1, 5, 9.
- **Dòng liên quan (3):** 5981, 5983, 5985
- **Event ID tiêu biểu:** EVT005981, EVT005983, EVT005985
- **Nhận định:** Bản backup mã hóa nhưng bucket mở public và khóa giải mã bị để cùng nơi.
- **Cần kiểm chứng/ứng phó:** Đánh giá đồng thời ACL, quản lý key, người tải và thời gian tồn tại.

### S23 – Tăng đột biến request kèm lỗi 503

- **Độ khó:** DE; **định tính:** CAN_DIEU_TRA; **chủ đề:** `AVAILABILITY_DOS`; **bài:** 1, 9, 10.
- **Dòng liên quan (160):** 6667, 6668, 6669, 6670, 6671, 6672, 6673, 6674, 6675, 6676, 6677, 6678, 6679, 6680, 6681, 6682, 6683, 6684, 6685, 6686, 6687, 6688, 6689, 6690, 6691, 6692, 6693, 6694, 6695, 6696, 6697, 6698, 6699, 6700, 6701, 6702, 6703, 6704, 6705, 6706, 6707, 6708, 6709, 6710, 6711, 6712, 6713, 6714, 6715, 6716, 6717, 6718, 6719, 6720, 6721, 6722, 6723, 6724, 6725, 6726, 6727, 6728, 6729, 6730, 6731, 6732, 6733, 6734, 6735, 6736, 6737, 6738, 6739, 6740, 6741, 6742, 6743, 6744, 6745, 6746, 6747, 6748, 6749, 6750, 6751, 6752, 6753, 6754, 6755, 6756, 6757, 6758, 6759, 6760, 6761, 6762, 6763, 6764, 6765, 6766, 6767, 6768, 6769, 6770, 6771, 6772, 6773, 6774, 6775, 6776, 6777, 6778, 6779, 6780, 6781, 6782, 6783, 6784, 6785, 6786, 6787, 6788, 6789, 6790, 6791, 6792, 6793, 6794, 6795, 6796, 6797, 6798, 6799, 6800, 6801, 6802, 6803, 6804, 6805, 6806, 6807, 6808, 6809, 6810, 6811, 6812, 6813, 6814, 6815, 6816, 6817, 6818, 6819, 6820, 6821, 6822, 6823, 6824, 6825, 6827
- **Event ID tiêu biểu:** EVT006667, EVT006668, EVT006669, EVT006670, EVT006671, EVT006672, EVT006673, EVT006674
- **Nhận định:** Truy cập bùng nổ từ cùng IP, nhiều 429, dịch vụ lỗi 503 và latency tăng.
- **Cần kiểm chứng/ứng phó:** Đối chiếu campaign thật, bot, resource server, nguyên nhân hạ tầng trước khi kết luận DDoS.

### S24 – Credential stuffing từ nhiều IP vào một tài khoản

- **Độ khó:** KHO; **định tính:** CAN_DIEU_TRA; **chủ đề:** `CREDENTIAL_STUFFING`; **bài:** 4, 8, 9.
- **Dòng liên quan (42):** 7179, 7180, 7181, 7182, 7183, 7184, 7185, 7186, 7187, 7188, 7189, 7190, 7191, 7192, 7193, 7194, 7196, 7197, 7198, 7199, 7200, 7201, 7202, 7203, 7204, 7205, 7206, 7207, 7208, 7209, 7210, 7211, 7212, 7213, 7214, 7215, 7216, 7217, 7218, 7219, 7220, 7221
- **Event ID tiêu biểu:** EVT007179, EVT007180, EVT007181, EVT007182, EVT007183, EVT007184, EVT007185, EVT007186
- **Nhận định:** Nhiều lần thử tài khoản đích từ IP khác nhau, một đăng nhập thành công và có session không quen thuộc.
- **Cần kiểm chứng/ứng phó:** Cần đối chiếu IP/thiết bị/MFA và thời điểm thay đổi mật khẩu.

### S25 – Dữ liệu nội bộ tải lên công cụ AI bên ngoài

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `EXTERNAL_AI_UPLOAD`; **bài:** 1, 2, 5, 6, 8.
- **Dòng liên quan (3):** 7554, 7556, 7557
- **Event ID tiêu biểu:** EVT007554, EVT007556, EVT007557
- **Nhận định:** Báo cáo có dữ liệu định danh được upload sang miền AI bên ngoài khi chưa có quyết định xử lý dữ liệu.
- **Cần kiểm chứng/ứng phó:** Kiểm tra hợp đồng, phân loại, quy trình giảm dữ liệu, bằng chứng tải lên và hướng dẫn ứng phó.

### S26 – CSV nhập từ đối tác có ô giống công thức

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `CSV_FORMULA`; **bài:** 6, 8, 9.
- **Dòng liên quan (3):** 7669, 7671, 7674
- **Event ID tiêu biểu:** EVT007669, EVT007671, EVT007674
- **Nhận định:** CSV không tin cậy chứa ô bắt đầu bằng ký hiệu công thức, được đưa vào file báo cáo mở bằng Excel.
- **Cần kiểm chứng/ứng phó:** Kiểm tra cách escape công thức trước khi mở; log không đủ chứng minh có thực thi.

### S27 – RLS không còn hiệu lực với workspace Member

- **Độ khó:** KHO; **định tính:** CAN_DIEU_TRA; **chủ đề:** `BI_RLS_BYPASS`; **bài:** 3, 7, 9.
- **Dòng liên quan (3):** 7716, 7717, 7718
- **Event ID tiêu biểu:** EVT007716, EVT007717, EVT007718
- **Nhận định:** Người xem được gán Member thay Viewer, sau đó nhận cả CN_HCM và CN_DN dù role RLS chỉ CN_HCM.
- **Cần kiểm chứng/ứng phó:** So quyền workspace, RLS, Access Matrix và dữ liệu thực được trả.

### S28 – Publish-to-web báo cáo doanh số bí mật

- **Độ khó:** DE; **định tính:** CAN_DIEU_TRA; **chủ đề:** `BI_PUBLIC_LINK`; **bài:** 5, 7, 9.
- **Dòng liên quan (5):** 8464, 8465, 8466, 8468, 8469
- **Event ID tiêu biểu:** EVT008464, EVT008465, EVT008466, EVT008468, EVT008469
- **Nhận định:** Báo cáo phân tích doanh thu không được phép công khai nhưng được publish-to-web.
- **Cần kiểm chứng/ứng phó:** Thu hồi mã nhúng, kiểm tra truy cập nặc danh và bản sao; RLS không dùng để bảo vệ link công khai.

### S29 – Tổng hợp nhóm quá nhỏ có thể tái nhận diện

- **Độ khó:** KHO; **định tính:** CAN_DIEU_TRA; **chủ đề:** `REIDENTIFICATION`; **bài:** 1, 6, 7.
- **Dòng liên quan (2):** 8516, 8517
- **Event ID tiêu biểu:** EVT008516, EVT008517
- **Nhận định:** Bảng đã bỏ tên nhưng group có duy nhất một khách hàng, kết hợp nhóm và hóa đơn sẽ suy đoán người.
- **Cần kiểm chứng/ứng phó:** Kiểm tra k-anonymity, nhóm nhỏ, ngoại lai và dữ liệu công khai kết hợp.

### S30 – Đối tác API được quyền rộng hơn hợp đồng

- **Độ khó:** KHO; **định tính:** CAN_DIEU_TRA; **chủ đề:** `THIRD_PARTY_SCOPE`; **bài:** 2, 3, 6, 9.
- **Dòng liên quan (7):** 8550, 8551, 8553, 8554, 8556, 8557, 8558
- **Event ID tiêu biểu:** EVT008550, EVT008551, EVT008553, EVT008554, EVT008556, EVT008557, EVT008558
- **Nhận định:** Vendor chỉ chăm sóc đơn CN_HCM nhưng token scope read_all_customers, đã truy xuất CN_DN.
- **Cần kiểm chứng/ứng phó:** Kiểm tra hợp đồng, app registration, ACL theo dữ liệu và key rotation.

### S31 – Webhook thanh toán chữ ký không hợp lệ vẫn xử lý

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `WEBHOOK_INTEGRITY`; **bài:** 1, 5, 9.
- **Dòng liên quan (2):** 8599, 8600
- **Event ID tiêu biểu:** EVT008599, EVT008600
- **Nhận định:** Gateway phát hiện chữ ký webhook fail nhưng đơn được cập nhật đã thanh toán.
- **Cần kiểm chứng/ứng phó:** Xác minh idempotency, verify signature, đối soát giao dịch ngân hàng/gateway.

### S32 – Tắt audit trước khi sửa kho và bật lại

- **Độ khó:** KHO; **định tính:** CAN_DIEU_TRA; **chủ đề:** `AUDIT_LOG_GAP`; **bài:** 3, 9, 10.
- **Dòng liên quan (3):** 8993, 8996, 9005
- **Event ID tiêu biểu:** EVT008993, EVT008996, EVT009005
- **Nhận định:** Tắt nhật ký bán hàng rồi có thay đổi hàng tồn trước khi bật lại; bản thân khoảng trống là bằng chứng.
- **Cần kiểm chứng/ứng phó:** Tìm nhật ký ở lớp khác, lưu bản gốc, xem quyền tắt log và thay đổi tồn kho.

### S33 – Cố xóa nhật ký và sai hash kiểm toán

- **Độ khó:** KHO; **định tính:** CAN_DIEU_TRA; **chủ đề:** `LOG_TAMPERING`; **bài:** 5, 9, 10.
- **Dòng liên quan (2):** 9067, 9068
- **Event ID tiêu biểu:** EVT009067, EVT009068
- **Nhận định:** Tài khoản quản trị thực hiện DELETE với audit archive và integrity hash mismatch.
- **Cần kiểm chứng/ứng phó:** Bảo toàn bản WORM hoặc remote collector, ghi chuỗi bàn giao bằng chứng.

### S34 – Xuất dữ liệu nhỏ giọt nhiều ngày

- **Độ khó:** KHO; **định tính:** CAN_DIEU_TRA; **chủ đề:** `LOW_AND_SLOW_EXFIL`; **bài:** 3, 6, 9, 10.
- **Dòng liên quan (16):** 2347, 2351, 3288, 3293, 4304, 4308, 5253, 5263, 6274, 6282, 7461, 7467, 8428, 8432, 9389, 9395
- **Event ID tiêu biểu:** EVT002347, EVT002351, EVT003288, EVT003293, EVT004304, EVT004308, EVT005253, EVT005263
- **Nhận định:** Một nhân viên export 150-250 khách mỗi ngày, các phần không lặp; tổng vượt ngưỡng và upload ngoài.
- **Cần kiểm chứng/ứng phó:** Cần tổng hợp theo user/cột/scope nhiều ngày, không chỉ tìm export > 1000 một lần.

### S35 – Xuất dữ liệu ngoài giờ trước khi chuyển công tác

- **Độ khó:** KHO; **định tính:** CAN_DIEU_TRA; **chủ đề:** `INSIDER_RISK`; **bài:** 1, 3, 5, 9, 10.
- **Dòng liên quan (9):** 9903, 9904, 9905, 9906, 9908, 9909, 9911, 9914, 9917
- **Event ID tiêu biểu:** EVT009903, EVT009904, EVT009905, EVT009906, EVT009908, EVT009909, EVT009911, EVT009914
- **Nhận định:** Tài khoản đang chờ điều chuyển xuất nhiều file và sao chép ra cloud cá nhân, cần điều tra không vội quy kết.
- **Cần kiểm chứng/ứng phó:** Đối chiếu phê duyệt, thiết bị, phiên, hồ sơ nhân sự; giữ chứng cứ và bảo đảm nguyên tắc suy đoán.

### S36 – Email giả đăng nhập SSO và click QR

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `PHISHING`; **bài:** 4, 5, 8, 9.
- **Dòng liên quan (4):** 2396, 2397, 2398, 2400
- **Event ID tiêu biểu:** EVT002396, EVT002397, EVT002398, EVT002400
- **Nhận định:** Email giả danh IT dẫn tới host ngoài công ty, có click và đăng nhập thử; log chưa đủ biết mật khẩu đã lộ.
- **Cần kiểm chứng/ứng phó:** Kiểm tra email headers, DMARC, domain, IdP và khóa phiên nếu có dấu hiệu chiếm đoạt.

### S37 – File đính kèm nguy hiểm bị cách ly

- **Độ khó:** DE; **định tính:** CAN_DIEU_TRA; **chủ đề:** `SUSPICIOUS_ATTACHMENT`; **bài:** 5, 8, 9.
- **Dòng liên quan (2):** 2407, 2408
- **Event ID tiêu biểu:** EVT002407, EVT002408
- **Nhận định:** Attachment có phần mở rộng kép / file macro được mail gateway chặn; không có bằng chứng đã thực thi.
- **Cần kiểm chứng/ứng phó:** Xác nhận cách ly, người nhận, không mở file trên máy thật.

### S38 – MFA của quản trị viên bị miễn trừ

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `MFA_EXEMPTION`; **bài:** 3, 4, 9.
- **Dòng liên quan (2):** 315, 2280
- **Event ID tiêu biểu:** EVT000315, EVT002280
- **Nhận định:** Tài khoản admin thuộc nhóm bypass MFA lâu dài, về sau đăng nhập bằng mật khẩu trên thiết bị mới.
- **Cần kiểm chứng/ứng phó:** Rà soát chính sách ngoại lệ và cơ chế truy cập khẩn cấp riêng.

### S39 – HTTP cache chia sẻ nhầm dữ liệu người dùng

- **Độ khó:** KHO; **định tính:** CAN_DIEU_TRA; **chủ đề:** `CACHE_LEAK`; **bài:** 1, 2, 3, 9.
- **Dòng liên quan (2):** 1543, 1544
- **Event ID tiêu biểu:** EVT001543, EVT001544
- **Nhận định:** Endpoint khách hàng có Cache-Control public; người dùng khác nhận response cache có cùng object.
- **Cần kiểm chứng/ứng phó:** Kiểm tra cache key, Vary Authorization, CDN và bản ghi truy cập.

### S40 – CORS tùy ý với cookies đăng nhập

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `CORS_MISCONFIG`; **bài:** 3, 5, 9.
- **Dòng liên quan (2):** 2659, 2660
- **Event ID tiêu biểu:** EVT002659, EVT002660
- **Nhận định:** Phản hồi API cho Origin ngoài tin cậy và allow_credentials=true.
- **Cần kiểm chứng/ứng phó:** Kiểm tra allowlist origin, access token, CSRF và dữ liệu được trả, tránh suy đoán đã mất dữ liệu.

### S41 – Giữ dữ liệu đã hết thời hạn lưu trữ

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `RETENTION`; **bài:** 1, 2, 6, 9.
- **Dòng liên quan (2):** 3299, 3301
- **Event ID tiêu biểu:** EVT003299, EVT003301
- **Nhận định:** Đã hết retention 90 ngày nhưng có dữ liệu 2 năm và job purge bị tắt.
- **Cần kiểm chứng/ứng phó:** Đối chiếu cơ sở pháp lý, lịch xóa, trường hợp legal hold.

### S42 – Khóa mã hóa và file nằm cùng chỗ

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `KEY_MANAGEMENT`; **bài:** 5, 9.
- **Dòng liên quan (2):** 4059, 4060
- **Event ID tiêu biểu:** EVT004059, EVT004060
- **Nhận định:** Backup được mã hóa nhưng keyfile nằm cùng thư mục và cùng quyền ACL.
- **Cần kiểm chứng/ứng phó:** Đánh giá KMS và tách quyền lưu khóa, không chỉ kiểm tra cờ encrypted=true.

### S43 – Thứ tự nhận log khác thời điểm sự kiện

- **Độ khó:** KHO; **định tính:** CAN_XAC_MINH; **chủ đề:** `CLOCK_SKEW`; **bài:** 3, 9.
- **Dòng liên quan (3):** 4300, 4303, 4305
- **Event ID tiêu biểu:** EVT004300, EVT004303, EVT004305
- **Nhận định:** Trong file, role_change EVT004303 đứng trước export EVT004305; ts của export sớm hơn ts của role_change, nhưng details có effective_at/cache từ 08:58 và clock skew. Chưa đủ kết luận vượt quyền.
- **Cần kiểm chứng/ứng phó:** Đối chiếu ts, ingested_at, version policy, NTP và ticket trước khi kết luận.

### S44 – Xuất báo cáo ngoài giờ nhưng có phê duyệt hợp lệ

- **Độ khó:** KHO; **định tính:** DOI_CHUNG_HOP_LE; **chủ đề:** `FALSE_POSITIVE`; **bài:** 3, 4, 9.
- **Dòng liên quan (3):** 5812, 5816, 5817
- **Event ID tiêu biểu:** EVT005812, EVT005816, EVT005817
- **Nhận định:** Hoạt động xuất lớn, ngoài giờ nhưng có ticket, VPN, MFA mạnh và scope phù hợp; không đủ để kết luận xâm nhập.
- **Cần kiểm chứng/ứng phó:** Không nhầm lượng bản ghi lớn với sự cố; kiểm tra hồ sơ duyệt và thiết bị.

### S45 – Cảnh báo WAF với tên có dấu nháy nhưng truy vấn an toàn

- **Độ khó:** TRUNG_BINH; **định tính:** DOI_CHUNG_HOP_LE; **chủ đề:** `FALSE_POSITIVE`; **bài:** 6, 9.
- **Dòng liên quan (2):** 5369, 5370
- **Event ID tiêu biểu:** EVT005369, EVT005370
- **Nhận định:** Tên O'Brien có dấu nháy hợp lệ, SQL dùng parameter và 200; cảnh báo pattern không đủ nói SQLi.
- **Cần kiểm chứng/ứng phó:** Kiểm tra DB query parameterized, WAF false-positive và ảnh hưởng người dùng.

### S46 – Gõ sai mật khẩu vài lần rồi MFA thành công

- **Độ khó:** DE; **định tính:** DOI_CHUNG_HOP_LE; **chủ đề:** `FALSE_POSITIVE`; **bài:** 4, 9.
- **Dòng liên quan (4):** 6233, 6234, 6235, 6236
- **Event ID tiêu biểu:** EVT006233, EVT006234, EVT006235, EVT006236
- **Nhận định:** Ba lần sai mật khẩu từ cùng máy nội bộ, sau đó đăng nhập MFA bình thường.
- **Cần kiểm chứng/ứng phó:** Đối chứng giúp tránh nâng mọi login failure thành credential stuffing.

### S47 – Giả danh nhà cung cấp yêu cầu gửi bảng khách hàng

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `SOCIAL_ENGINEERING`; **bài:** 5, 8, 9.
- **Dòng liên quan (2):** 6502, 6506
- **Event ID tiêu biểu:** EVT006502, EVT006506
- **Nhận định:** Email mạo danh nhà cung cấp yêu cầu danh sách khách hàng không đúng hợp đồng, nhân viên gửi file mà thiếu callback.
- **Cần kiểm chứng/ứng phó:** Kiểm tra danh tính người gửi, nguồn email, quy trình duyệt và xác minh độc lập.

### S48 – Sửa giá bán sâu và hóa đơn không có duyệt

- **Độ khó:** KHO; **định tính:** CAN_DIEU_TRA; **chủ đề:** `SALES_INTEGRITY`; **bài:** 1, 3, 9.
- **Dòng liên quan (3):** 7750, 7753, 7756
- **Event ID tiêu biểu:** EVT007750, EVT007753, EVT007756
- **Nhận định:** Giá SKU bị hạ mạnh trước bán, không có duyệt hoặc đợt khuyến mại; cần đối chiếu lịch sử giá.
- **Cần kiểm chứng/ứng phó:** Kiểm tra chiến dịch, duyệt giá, vai trò người chỉnh và hóa đơn phát sinh.

### S49 – Đổi mật khẩu IdP nhưng phiên ứng dụng vẫn dùng được

- **Độ khó:** KHO; **định tính:** CAN_DIEU_TRA; **chủ đề:** `SESSION_REVOCATION`; **bài:** 4, 9, 10.
- **Dòng liên quan (2):** 8838, 8843
- **Event ID tiêu biểu:** EVT008838, EVT008843
- **Nhận định:** Reset password rồi chỉ IdP logout, phiên sales app trước đó còn sống và được sử dụng.
- **Cần kiểm chứng/ứng phó:** Kiểm tra revoke token/session ứng dụng và sự kiện từ thiết bị cũ.

### S50 – Quy tắc cảnh báo bị vô hiệu trước hoạt động nhạy cảm

- **Độ khó:** KHO; **định tính:** CAN_DIEU_TRA; **chủ đề:** `DETECTION_BLIND_SPOT`; **bài:** 3, 9, 10.
- **Dòng liên quan (3):** 9369, 9371, 9372
- **Event ID tiêu biểu:** EVT009369, EVT009371, EVT009372
- **Nhận định:** Quy tắc cảnh báo bulk export tắt trước một export lớn; không phải log bị biến mất.
- **Cần kiểm chứng/ứng phó:** Đối chiếu chủ thể thay đổi rule, ticket, nhật ký thay đổi và trạng thái SIEM.

### S51 – Dữ liệu định danh đặt trong URL rồi bị ghi log

- **Độ khó:** DE; **định tính:** CAN_DIEU_TRA; **chủ đề:** `PII_IN_URL`; **bài:** 1, 5, 9.
- **Dòng liên quan (2):** 605, 608
- **Event ID tiêu biểu:** EVT000605, EVT000608
- **Nhận định:** GET gửi email/số điện thoại mẫu qua query string khiến access log và proxy lưu lại.
- **Cần kiểm chứng/ứng phó:** Sửa phương thức và xử lý log, không đưa giá trị cá nhân vào query URL.

### S52 – QR thanh toán bị đổi điểm đến

- **Độ khó:** KHO; **định tính:** CAN_DIEU_TRA; **chủ đề:** `PAYMENT_REDIRECTION`; **bài:** 1, 8, 9, 10.
- **Dòng liên quan (3):** 9502, 9503, 9507
- **Event ID tiêu biểu:** EVT009502, EVT009503, EVT009507
- **Nhận định:** QR checkout trỏ miền/merchant ID không khớp cấu hình, phản ánh người mua; chưa chứng minh tiền đã mất.
- **Cần kiểm chứng/ứng phó:** Kiểm tra nguồn QR, nhật ký cấu hình, hóa đơn và chứng từ ngân hàng.

### S53 – Khuyến mại giảm giá lớn nhưng có duyệt

- **Độ khó:** TRUNG_BINH; **định tính:** DOI_CHUNG_HOP_LE; **chủ đề:** `FALSE_POSITIVE`; **bài:** 3, 9.
- **Dòng liên quan (2):** 1454, 1456
- **Event ID tiêu biểu:** EVT001454, EVT001456
- **Nhận định:** Giảm giá sâu trong chiến dịch đã có approval id và ngày hiệu lực.
- **Cần kiểm chứng/ứng phó:** Dùng đối chứng kiểm tra quy tắc phân quyền giá.

### S54 – Source map công khai tiết lộ thông tin nội bộ

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `CLIENT_ARTIFACT_LEAK`; **bài:** 1, 5, 9.
- **Dòng liên quan (1):** 1735
- **Event ID tiêu biểu:** EVT001735
- **Nhận định:** Public sourcemap chứa đường dẫn API nội bộ và nhãn debug; chưa đủ khẳng định có secret thật.
- **Cần kiểm chứng/ứng phó:** Gỡ artifacts không nên công khai, quét thông tin nhạy cảm, không coi tên endpoint là lộ toàn DB.

### S55 – Dấu hiệu injection dẫn tới truy vấn trả quá nhiều dòng

- **Độ khó:** KHO; **định tính:** CAN_DIEU_TRA; **chủ đề:** `SQL_INJECTION_SUSPECTED`; **bài:** 6, 9.
- **Dòng liên quan (3):** 2038, 2039, 2040
- **Event ID tiêu biểu:** EVT002038, EVT002039, EVT002040
- **Nhận định:** API tìm kiếm đáp 200 cho mẫu truy vấn bất thường, DB trả toàn bộ bản ghi vượt dự kiến.
- **Cần kiểm chứng/ứng phó:** Phải xác nhận log DB, code có parameterized không; không khẳng định quy mô rò rỉ nếu thiếu bản ghi bytes/download.

### S56 – Redirect SSO sang miền ngoài do tham số next

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `UNTRUSTED_REDIRECT`; **bài:** 4, 5, 8.
- **Dòng liên quan (1):** 3450
- **Event ID tiêu biểu:** EVT003450
- **Nhận định:** URL login cho phép redirect đến host ngoài sau đăng nhập, có thể bị lạm dụng phishing.
- **Cần kiểm chứng/ứng phó:** Cần allowlist return URL và xác minh callback OAuth.

### S57 – Sai lệch chữ ký/hash bảng giá trước nhập liệu

- **Độ khó:** KHO; **định tính:** CAN_DIEU_TRA; **chủ đề:** `DATA_INTEGRITY`; **bài:** 1, 5, 9, 10.
- **Dòng liên quan (2):** 9766, 9767
- **Event ID tiêu biểu:** EVT009766, EVT009767
- **Nhận định:** File bảng giá mới có hash khác bản đã duyệt, nhưng import vẫn chạy.
- **Cần kiểm chứng/ứng phó:** Đối chiếu chữ ký tài liệu nguồn và người phê duyệt, dừng cập nhật khi integrity check fail.

### S58 – Khách báo cuộc gọi lừa đảo biết đúng dữ liệu nội bộ

- **Độ khó:** KHO; **định tính:** CAN_DIEU_TRA; **chủ đề:** `CUSTOMER_SCAM_LEAK`; **bài:** 1, 2, 5, 8, 9, 10.
- **Dòng liên quan (2):** 9393, 9396
- **Event ID tiêu biểu:** EVT009393, EVT009396
- **Nhận định:** Kẻ gọi giả CSKH biết order id, giá trị đơn và số liên hệ; cần ghép với export/file-share gần đó.
- **Cần kiểm chứng/ứng phó:** Không khẳng định nguồn rò rỉ khi chưa kiểm tra tất cả đường dữ liệu; giữ nội dung phản ánh.

### S59 – Kết nối DB sản xuất từ thiết bị ngoài quản lý

- **Độ khó:** TRUNG_BINH; **định tính:** CAN_DIEU_TRA; **chủ đề:** `DB_EXCESSIVE_ACCESS`; **bài:** 3, 5, 6, 9.
- **Dòng liên quan (2):** 2574, 2576
- **Event ID tiêu biểu:** EVT002574, EVT002576
- **Nhận định:** Analyst dùng account DB chung trên thiết bị ngoài quản lý, SELECT bảng đầy đủ khách thay vì view.
- **Cần kiểm chứng/ứng phó:** Thực thi quyền chỉ đọc trên view, account cá nhân, VPN và logging.

### S60 – Ghép hai bảng tổng hợp có thể suy ra một người

- **Độ khó:** KHO; **định tính:** CAN_DIEU_TRA; **chủ đề:** `DIFFERENCING_REIDENTIFICATION`; **bài:** 1, 6, 7, 9.
- **Dòng liên quan (2):** 8697, 8699
- **Event ID tiêu biểu:** EVT008697, EVT008699
- **Nhận định:** Hai báo cáo nhóm gần giống nhau chênh một bản ghi; phép trừ có thể suy ra dữ liệu của 1 khách.
- **Cần kiểm chứng/ứng phó:** Đánh giá phép trừ giữa các bảng xuất, mức chi tiết, số nhóm nhỏ và quyền công bố.

## Quy tắc chấm bài

1. Điểm cao khi đưa ra chuỗi sự kiện `event_id` và nguồn `source`, không chỉ kể tên lỗ hổng.
2. Phân biệt hành vi chắc chắn có trên log và khả năng ảnh hưởng còn cần kiểm chứng.
3. Trình bày đối tượng bị ảnh hưởng, thời điểm có timezone, mức độ CIA và ưu tiên xử lý.
4. Đề xuất nguồn kiểm chứng tiếp theo (ticket phê duyệt, lịch trực, EDR, IdP, object store, BI workspace, DB audit, email).
5. Không gán trách nhiệm cho người có tên trên log khi tài khoản có thể bị chiếm hoặc dùng chung.
