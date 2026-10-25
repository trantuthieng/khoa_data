"""Mẫu nộp bài cho từng bài thực hành (theo Phụ lục C của giáo trình).

Mỗi trường (field):
  {"type": "text" | "textarea", "key", "label", "hint"?}
  {"type": "checklist", "key", "label", "items": [...]}
  {"type": "table", "key", "label", "columns": [{"key","label","options"?}],
   "rows": [nhãn dòng cố định] | None, "min_rows": n}
Cột có "options" hiển thị dạng danh sách chọn.
"""

MUC = ["Thấp", "Trung bình", "Cao", "Không áp dụng"]
NHAN = ["Công khai", "Nội bộ", "Mật", "Hạn chế cao"]


def col(key, label, options=None):
    c = {"key": key, "label": label}
    if options:
        c["options"] = options
    return c


def ta(key, label, hint=None):
    f = {"type": "textarea", "key": key, "label": label}
    if hint:
        f["hint"] = hint
    return f


TEMPLATES = {
    1: [
        {"type": "table", "key": "phan_loai", "label": "Bảng phân loại dữ liệu (mẫu C1)",
         "rows": ["Khách hàng và hợp đồng mua bán điện", "Chỉ số công tơ và báo cáo sản lượng",
                  "Vận hành và tài liệu kỹ thuật", "Thông tin nhân sự", "File DS_KhachHang_DLX.xlsx"],
         "columns": [col("nhan", "Nhãn", NHAN), col("c", "Bí mật", MUC), col("i", "Toàn vẹn", MUC),
                     col("a", "Sẵn sàng", MUC), col("ai_dung", "Ai được dùng, kênh chia sẻ"),
                     col("ai", "Điều kiện dùng AI"), col("ly_do", "Lý do chọn nhãn")]},
        ta("mo_rong", "Mở rộng (nếu làm xong sớm)", "Một trường hợp “gộp dữ liệu làm tăng mức” và một trường hợp “hạ mức sau khi công bố”."),
    ],
    2: [
        {"type": "text", "key": "quy_trinh", "label": "Quy trình bạn chọn (A hoặc B – ghi tên quy trình)"},
        ta("so_do", "Các bước trên sơ đồ", "Mỗi dòng một mũi tên: từ đâu → đến đâu, trường dữ liệu nào, truyền bằng cách nào."),
        ta("ranh_gioi", "Các ranh giới tin cậy (đánh số)"),
        ta("ban_sao", "Danh sách bản sao, kể cả bản sao không chính thức"),
        {"type": "table", "key": "rui_ro", "label": "Bảng rủi ro luồng dữ liệu (mẫu C2) – ít nhất 3 điểm yếu", "rows": None, "min_rows": 3,
         "columns": [col("buoc", "Bước trên sơ đồ"), col("diem_yeu", "Điểm yếu"), col("tac_dong", "Tác động nếu xảy ra"),
                     col("kiem_soat", "Kiểm soát đề xuất"), col("nguoi", "Người chịu trách nhiệm"), col("minh_chung", "Minh chứng")]},
    ],
    3: [
        {"type": "table", "key": "ma_tran", "label": "Ma trận quyền (mẫu C3) – mỗi ô ghi quyền, phạm vi và người duyệt; để trống = không có quyền",
         "rows": ["Nhân viên nghiệp vụ", "Trưởng phòng", "Chuyên viên thu nợ", "Cán bộ CNTT hỗ trợ", "Quản trị hệ thống"],
         "columns": [col("xem", "Xem"), col("sua", "Sửa"), col("xuat", "Xuất"), col("cap_quyen", "Cấp quyền"), col("duyet", "Người duyệt")]},
        ta("tu_choi", "Ít nhất 3 trường hợp phải bị từ chối"),
        ta("xin_them", "Ít nhất 2 trường hợp phải xin thêm quyền"),
    ],
    4: [
        ta("nhu_cau", "Nhu cầu bàn giao cụ thể là gì? Cần quyền gì (xem hay sửa), trên dữ liệu nào?"),
        ta("phe_duyet", "Ai phê duyệt ngoại lệ, và quyền hết hạn khi nào?"),
        ta("thu_hoi", "Thu hồi phần quyền không còn cần, cấp quyền mới ở Điện lực Y, rồi kiểm tra lại bằng cách nào?"),
        ta("bang_chung", "Bằng chứng nào cho thấy quyền cũ đã được xử lý?"),
    ],
    5: [
        {"type": "table", "key": "thay_tk", "label": "Phương án thay tài khoản dùng chung (mẫu C5)", "rows": None, "min_rows": 1,
         "columns": [col("tk", "Tài khoản chung hiện tại"), col("ai", "Ai đang dùng"), col("vi_sao", "Vì sao đang dùng chung"),
                     col("phuong_an", "Phương án thay"), col("mfa", "MFA"), col("phien", "Xử lý phiên"), col("bu", "Kiểm soát bù nếu chưa thay được")]},
        ta("ca_truc", "Bài toán ca trực: khi một người vắng, người khác làm thế nào mà không dùng chung tài khoản?"),
        ta("vong_doi", "Checklist vòng đời tài khoản: cấp mới – thay vị trí – thu hồi quyền và phiên"),
        ta("de_xuat_mfa", "Đoạn đề xuất cấu hình MFA cho toàn Điện lực X gửi lãnh đạo (chọn loại MFA, có dùng SSO không)"),
    ],
    6: [
        ta("khao_sat", "Phần A – 1. Khảo sát file: bao nhiêu sheet, sheet nào ẩn, cột nào ẩn, trong đó có gì?"),
        ta("giu_gi", "Phần A – 2. Quyết định giữ gì trong file gửi đi"),
        ta("ma_hoa", "Phần A – 3–4. Mã hóa thế nào? So sánh với Protect Sheet: có đọc được nội dung không?"),
        ta("kenh", "Phần A – 5. Danh sách người nhận, kênh gửi file, kênh báo mật khẩu"),
        ta("thu_hoi", "Phần A – 7. Kế hoạch thu hồi / lưu giữ"),
        {"type": "checklist", "key": "checklist", "label": "Checklist chia sẻ 5 bước (mẫu C6)",
         "items": ["Ai nhận, có đúng người cần nhận không?",
                   "File chỉ còn các cột, dòng cần thiết (không còn sheet ẩn, cột ẩn)?",
                   "Đã mã hóa bằng tính năng mã hóa thật?",
                   "Chia sẻ cho người cụ thể, có hạn, không dùng link “Anyone”?",
                   "Mật khẩu gửi qua kênh khác và có ghi lại việc gửi?"]},
        ta("phan_b", "Phần B – Cách chia sẻ danh sách hộ nợ cho công ty thu hộ; vì sao bỏ các cột còn lại; xử lý thế nào khi họ đòi số điện thoại?"),
    ],
    7: [
        {"type": "table", "key": "phan_loai_cot", "label": "Bảng phân loại cột và so sánh đầu vào – đầu ra",
         "rows": ["ma_kh", "ho_ten", "dien_thoai", "dia_chi", "phuong", "loai_kh", "thang", "kwh", "so_tien_no"],
         "columns": [col("loai", "Loại trường", ["Định danh trực tiếp", "Định danh gián tiếp", "Thuộc tính nhạy cảm", "Dữ liệu phân tích"]),
                     col("can", "Anh Minh cần?", ["Cần", "Không cần"]),
                     col("xu_ly", "Xử lý", ["Giữ", "Bỏ", "Biến đổi"]), col("ly_do", "Vì sao")]},
        ta("kiem_tra", "Kết quả bốn phép kiểm tra nhận diện: nhóm nhỏ, ngoại lai, áp đảo, phép trừ giữa các bảng"),
        ta("quyet_dinh", "Bản nào được đưa vào môi trường AI thử nghiệm, bản nào không? Cần ai duyệt, xác nhận gì về công cụ AI?"),
        {"type": "table", "key": "phieu", "label": "Phiếu yêu cầu dữ liệu (mẫu C7)",
         "rows": ["Người yêu cầu, đơn vị", "Mục đích sử dụng", "Các trường cần và lý do", "Mức chi tiết",
                  "Kỹ thuật giảm dữ liệu áp dụng", "Công cụ sẽ dùng (có AI không, đã được duyệt chưa)", "Hạn sử dụng và cách hủy", "Chủ dữ liệu duyệt"],
         "columns": [col("noi_dung", "Nội dung")]},
        ta("de_xuat", "Đoạn đề xuất gửi anh Tuấn"),
    ],
    8: [
        {"type": "table", "key": "kiem_thu", "label": "Ma trận kiểm thử RLS (mẫu C8)", "rows": None, "min_rows": 4,
         "columns": [col("tk", "Tài khoản thử"), col("rls", "Vai trò RLS"), col("ws", "Vai trò workspace"),
                     col("ky_vong", "Kỳ vọng thấy"), col("thuc_te", "Thực tế thấy"), col("dat", "Đạt", ["Đạt", "Không đạt", "Chưa thử"])]},
        ta("slicer", "Khi View as DonVi_A, slicer có chọn được Điện lực Y không? Vì sao?"),
        ta("chia_se_nham", "Phân tích tình huống chia sẻ nhầm báo cáo ra ngoài: ai phát hiện, báo ai, làm gì trước, làm gì sau"),
    ],
    9: [
        {"type": "table", "key": "phan_tich", "label": "Bảng phân tích bốn tình huống",
         "rows": ["1. “Lãnh đạo” nhắn Zalo xin danh sách", "2. “Nhà cung cấp” gửi file yêu cầu Enable Content",
                  "3. Poster QR “đăng nhập lại”", "4. “CNTT” nhắn Zalo dặn bấm Chấp nhận MFA"],
         "columns": [col("dau_hieu", "Dấu hiệu nghi ngờ"), col("don", "Đòn tâm lý"), col("dung", "Hành động dừng"),
                     col("kenh", "Kênh xác minh"), col("bao", "Báo ai, giữ bằng chứng gì"), col("tu_choi", "Câu từ chối lịch sự")]},
    ],
    10: [
        {"type": "table", "key": "timeline", "label": "Diễn biến theo thời gian (ghi rõ múi giờ +07:00)", "rows": None, "min_rows": 5,
         "columns": [col("gio", "Giờ"), col("tk", "Tài khoản / IP"), col("su_kien", "Sự kiện"), col("nhan_xet", "Nhận xét")]},
        {"type": "table", "key": "truy_vet", "label": "Bảng truy vết (mẫu C10)", "rows": None, "min_rows": 3,
         "columns": [col("da_biet", "Đã biết (từ log)"), col("chua_biet", "Chưa biết"), col("gia_thuyet", "Giả thuyết"),
                     col("can_them", "Bằng chứng cần thêm, ai cung cấp")]},
        ta("hanh_dong", "Hành động tiếp theo trong phạm vi thẩm quyền của bạn"),
        ta("hen_sua", "(Vòng 2) Nối từng dòng bất thường với tờ “Việc hẹn sửa sau”"),
    ],
    11: [
        ta("dot1", "Đợt 1 – Phát hiện: quyết định của bạn", "Mỗi quyết định ghi: giờ (theo câu chuyện), ai quyết, ai làm, căn cứ."),
        ta("dot2", "Đợt 2 – Xác minh và ngăn chặn"),
        ta("dot3", "Đợt 3 – Phạm vi và bằng chứng"),
        ta("dot4", "Đợt 4 – Báo cáo và truyền thông"),
        ta("dot5", "Đợt 5 – Phục hồi và phòng ngừa"),
        ta("hop_nhanh", "Họp nhanh: điều gì làm tốt, điều gì chưa rõ, điều gì trong quy trình thật cần sửa ngay?"),
        {"type": "table", "key": "khuyen_nghi", "label": "Khuyến nghị (biên bản diễn tập)", "rows": None, "min_rows": 3,
         "columns": [col("viec", "Việc"), col("nguoi", "Người phụ trách"), col("han", "Hạn"), col("kiem_chung", "Cách kiểm chứng")]},
        ta("cau_hoi_mo", "Câu hỏi còn mở"),
    ],
}


def template_for(activity_id: str):
    try:
        n = int(activity_id.rsplit("-th", 1)[1])
    except (IndexError, ValueError):
        return []
    return TEMPLATES.get(n, [ta("bai_lam", "Bài làm")])
