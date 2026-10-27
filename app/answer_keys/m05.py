"""Đáp án giảng viên – buổi 5."""
from .kit import L, N, P, board, case_key, key

PHAN_B = (
    "Lọc sheet ChiTiet các hộ có SoTienNo > 0 (file mẫu: 106 hộ), chép sang file mới chỉ 4 cột MaKH, TenKH, DiaChi, SoTienNo; "
    "xóa hẳn các cột khác, không chỉ ẩn; kiểm tra lại số dòng. Mã hóa file, chia sẻ OneDrive “Specific people” cho đúng một địa chỉ "
    "bên công ty thu hộ, chỉ xem, hạn 7 ngày; báo mật khẩu qua điện thoại theo số trong hợp đồng.\n"
    "Bỏ DienThoai, kWh_T10, SoNgayQuaHan, GhiChuNoiBo vì thu nợ theo hợp đồng không cần; GhiChuNoiBo có ghi chú về hoàn cảnh "
    "(“Hộ khó khăn”) – lộ ra gây hại cho khách hàng.\n"
    "Khi công ty thu hộ đòi số điện thoại: không tự thêm. Đối chiếu hợp đồng và mục đích đã thống nhất; nếu thật sự cần thì xin "
    "phê duyệt của chủ dữ liệu, bổ sung phụ lục hợp đồng rồi mới gửi."
)

# ---------- Thực hành 6: bảo vệ báo cáo trước khi gửi ----------
KEY_TH6 = key(
    "File gửi chỉ có giá trị bảng 4 vùng của TongHop; không còn ChiTiet, sheet ẩn VanHanh, cột ẩn GhiChuNoiBo, công thức liên kết. "
    "Mã hóa bằng Encrypt with Password (Protect Sheet chỉ khóa sửa), thử mật khẩu sai bị từ chối, mật khẩu đi kênh khác với file, "
    "có kế hoạch xóa file trung gian và người nhận xác nhận.",
    {"bao_ve_file": board([
        N("f_goc", "file", 42, 80, "Sheet ChiTiet có 400 hộ; cột I bị ẩn chứa ghi chú kiểu “Hộ khó khăn”, “Hay khiếu nại”.",
          p={"so_sheet": "3", "sheet_an": "VanHanh", "cot_an": "Cột I GhiChuNoiBo (sheet ChiTiet)"}),
        N("k_tonghop", "find", 370, 74, "Số hộ, sản lượng theo 4 vùng. Người nhận cần đúng bảng này.", tag="Sheet"),
        N("k_cthuc", "find", 370, 262, "Giữ số liệu, bỏ công thức trỏ về ChiTiet: Paste Values.",
          title="Công thức trong TongHop", tag="Công thức liên kết"),
        N("k_chitiet", "find", 370, 514, "400 hộ: tên, SĐT, số nợ; cột ẩn I ghi hoàn cảnh hộ.", title="Sheet ChiTiet + cột ẩn I", tag="Cột ẩn"),
        N("k_vanhanh", "find", 370, 684, "Tải trạm, mất điện theo vùng. Không cần.", title="Sheet VanHanh", tag="Sheet ẩn"),
        N("n_new", "step", 722, 80, "Workbook mới, Paste Values bảng 4 vùng (không công thức). Inspect Document: gỡ thông tin tác giả; không còn sheet ẩn. Kiểm tra đúng tháng 10."),
        N("n_enc", "enc", 722, 300, "Cụm từ dài ngẫu nhiên, không chứa tên đơn vị hay ngày tháng.", p={"sai_mk": "Bị từ chối"}),
        N("n_cmp", "cmp", 722, 520, "Protect Sheet chỉ chặn sửa ô; đóng mở lại vẫn đọc toàn bộ.", tag="Vẫn đọc được nội dung"),
        N("s_file", "send", 1072, 80, "BaoCao_T10_TongHop.xlsx đã mã hóa, không kèm file gốc."),
        N("s_pw", "send", 1072, 600, "Báo sau khi người nhận xác nhận đã nhận email."),
        N("r_tp", "person", 1150, 330, "Trưởng phòng Kế hoạch [tên]; địa chỉ email công vụ chọn từ danh bạ."),
        N("t_tg", "keep", 1462, 66, "Xóa bản sao để cắt gọn và dọn thùng rác.", p={"khi": "Ngay sau khi gửi", "ai": "Người gửi"}),
        N("t_goc", "keep", 1462, 320, "File gốc ở thư mục phòng trên máy chủ, không để trên Desktop.",
          p={"khi": "Thường xuyên", "ai": "Người gửi; trưởng phòng KD rà"}),
        N("t_xn", "keep", 1462, 594, "Trả lời email xác nhận; ghi vào sổ theo dõi gửi dữ liệu.",
          p={"khi": "Trong ngày gửi", "ai": "Trưởng phòng Kế hoạch"}),
    ], [
        L("s_file", "r_tp", kenh="Email công vụ"),
        L("s_pw", "r_tp", kenh="Điện thoại nội bộ"),
    ]),
     "checklist": [True, True, True, True, True],
     "phan_b": PHAN_B},
    modules=[
        ("📊 <b>File gốc</b>", "3 sheet; sheet ẩn VanHanh; cột ẩn I GhiChuNoiBo.", "Bỏ qua bước khảo sát là lỗi gốc của mọi lỗi sau."),
        ("🔎 <b>Bốn phát hiện</b>", "TongHop → Giữ; công thức trong TongHop → giữ số liệu dạng giá trị. ChiTiet (gồm cột ẩn I GhiChuNoiBo), "
         "VanHanh (sheet ẩn) → Bỏ.",
         "Học viên tách cột ẩn GhiChuNoiBo thành thẻ riêng ở vùng Bỏ là tốt hơn; bảng mẫu gộp vì vùng chỉ đủ chỗ 2 thẻ. Ghi chú “Hộ khó khăn” "
         "là thông tin về hoàn cảnh, cần thận trọng như dữ liệu nhạy cảm (mức Tốt). Thẻ công thức xếp vào Bỏ cũng đúng."),
        ("🛠️ <b>Tạo file mới</b>", "Paste Values; Inspect Document; kiểm tra đúng tháng.", "Chỉ ẩn sheet thì người nhận Unhide là thấy."),
        ("🔒 <b>Mã hóa</b>", "Encrypt with Password; mật khẩu sai → <b>Bị từ chối</b>.", "Ảnh chụp thông báo từ chối là đầu ra bắt buộc."),
        ("⚖️ <b>So sánh Protect Sheet</b>", "<b>Vẫn đọc được nội dung</b>.", "Chọn “Không đọc được” là chưa đóng mở lại để thử (có ⚠)."),
        ("📤 → 👤 <b>Gửi đi</b>", "File qua email công vụ; mật khẩu qua điện thoại nội bộ.", "Hai kênh khác nhau. Cùng kênh thì có ⚠."),
        ("🗂️ <b>Thu hồi, lưu giữ</b>", "Xóa file trung gian ngay; file gốc trên máy chủ; người nhận xác nhận trong ngày.", "Mỗi việc có thời điểm và người."),
    ],
    links=[
        ("File đã mã hóa → Trưởng phòng Kế hoạch", "Email công vụ", "Địa chỉ chọn từ danh bạ, không gõ tay."),
        ("Mật khẩu → Trưởng phòng Kế hoạch", "Điện thoại nội bộ", "Kênh khác email; ai đọc trộm email vẫn không mở được file."),
    ],
    more=[("Phần B và checklist C6", [
        P("Checklist C6: cả 5 mục đều phải đánh dấu được sau khi làm đúng Phần A."),
        P("<b>Phần B mẫu</b> nằm ở ô cuối bài làm mẫu. Ý bắt buộc: đúng 4 cột, đúng 106 dòng, xóa hẳn cột thừa; "
          "chia sẻ cho người cụ thể có hạn; số điện thoại chỉ thêm khi có phê duyệt và căn cứ hợp đồng."),
    ])],
    rubric=[
        ("Khảo sát", "2", "Ghi đúng 3 sheet, sheet ẩn VanHanh, cột ẩn GhiChuNoiBo; ít nhất 4 phát hiện."),
        ("Nội dung gửi", "2", "Chỉ TongHop ở vùng Giữ; file mới dán giá trị; có kết quả Inspect Document."),
        ("Bảo vệ", "2", "Mã hóa thật, thử mật khẩu sai bị từ chối; Protect Sheet vẫn đọc được."),
        ("Gửi đi", "2", "Người nhận cụ thể; file và mật khẩu khác kênh."),
        ("Sau gửi và Phần B", "2", "Thu hồi có thời điểm, người; Phần B đúng cột, trả lời đúng tình huống số điện thoại."),
    ],
    mistakes=[
        ("Chỉ ẩn sheet ChiTiet", "ChiTiet ở vùng Giữ hoặc ghi “ẩn đi”, có ⚠", "“Người nhận chuột phải → Unhide thì thấy gì?”"),
        ("Không thấy sheet VanHanh", "Thẻ file ghi 2 sheet, không có sheet ẩn", "“Bạn đã chuột phải vào tên sheet chưa?”"),
        ("Protect Sheet = mã hóa", "So sánh chọn “Không đọc được”, có ⚠", "“Đóng file, mở lại: bạn có đọc được không?”"),
        ("Mật khẩu cùng email", "Hai dây cùng kênh, có ⚠", "“Ai đọc được email đó là mở được file.”"),
        ("Mật khẩu là tên đơn vị + năm", "Ghi ví dụ mật khẩu dễ đoán", "“Kẻ gian thử gì đầu tiên?”"),
        ("Phần B giữ cột điện thoại", "“Để bên kia tiện gọi”", "“Hợp đồng thống nhất mục đích gì? Ai duyệt thêm cột?”"),
    ],
    flow=["Mở file BaoCao_Thang.xlsx trên máy chiếu, cùng lớp Unhide sheet VanHanh và cột I.",
          "Đóng mở lại bản có Protect Sheet: lớp thấy vẫn đọc được.",
          "Mở bảng mẫu: đi từ trái sang phải theo 5 vùng.",
          "Hỏi Phần B: công ty thu hộ đòi số điện thoại thì làm gì?"],
)

# ---------- Bài tập thêm: kiểm tra một gói báo cáo trước khi gửi ----------
KEY_CASE5 = case_key(
    "Ba vấn đề: gửi cả file gốc còn ChiTiet và sheet ẩn; Protect Sheet không mã hóa; mật khẩu đi cùng email. "
    "Tạo file mới chỉ có giá trị tổng hợp, mã hóa thật, người nhận cụ thể, mật khẩu kênh khác, thử người ngoài danh sách và mật khẩu sai.",
    ["1) Gửi file gốc: còn sheet ChiTiet có tên, số nợ và sheet VanHanh đang ẩn, trong khi người nhận chỉ cần bảng 4 vùng.\n"
     "2) Protect Sheet chỉ chặn sửa ô, không mã hóa: ai có file vẫn đọc toàn bộ.\n"
     "3) Mật khẩu gửi cùng email với file: ai đọc được email là mở được file.",
     "a) Tạo workbook mới, Paste Values bảng tổng hợp 4 vùng.\n"
     "b) Rà sheet ẩn, cột ẩn, liên kết; chạy Inspect Document.\n"
     "c) File → Info → Protect Workbook → Encrypt with Password, cụm từ dài; đóng và mở lại để kiểm tra.\n"
     "d) Gửi cho người nhận cụ thể (chọn từ danh bạ), có thời hạn nếu chia sẻ link; báo mật khẩu qua điện thoại.\n"
     "e) Xóa bản trung gian; ghi sổ theo dõi gửi.",
     "Phép thử 1 – người không có quyền: đăng nhập bằng một tài khoản ngoài danh sách mở link chia sẻ → phải bị từ chối.\n"
     "Phép thử 2 – nhập sai mật khẩu: mở file đã mã hóa với mật khẩu sai → không mở được, không đọc được nội dung.\n"
     "Lưu ý: thu hồi link không thu hồi được bản người nhận đã tải."],
    [("1. Ba vấn đề", "Gửi file gốc còn dữ liệu thừa/ẩn; Protect Sheet ≠ mã hóa; mật khẩu cùng kênh.", "Liên kết công thức về file gốc."),
     ("2. Quy trình", "File mới dán giá trị → rà ẩn → mã hóa → người nhận cụ thể → mật khẩu kênh khác.", "Xóa bản trung gian, ghi sổ."),
     ("3. Hai phép thử", "Người ngoài danh sách bị từ chối; sai mật khẩu không mở được.", "Nhắc thu hồi link không xóa bản đã tải.")],
    ["Nhận ra cả ba vấn đề, đặc biệt Protect Sheet không phải mã hóa.",
     "Quy trình đúng thứ tự, tạo file mới thay vì sửa file gốc; mật khẩu kênh khác.",
     "Hai phép thử có kết quả mong đợi rõ ràng, làm được ngay."],
    [("Ẩn sheet ChiTiet rồi gửi", "“Ẩn sheet ChiTiet”", "“Unhide mất bao lâu?”"),
     ("Chỉ đổi mật khẩu mạnh hơn", "Vẫn dùng Protect Sheet", "“Protect Sheet có ngăn đọc không?”"),
     ("Phép thử không có kết quả mong đợi", "“Thử mở file”", "“Thế nào là đạt?”")],
)

KEYS = {"m05-th6": KEY_TH6, "m05-case-v2": KEY_CASE5}
