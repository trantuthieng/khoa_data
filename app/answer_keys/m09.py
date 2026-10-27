"""Đáp án giảng viên – buổi 9."""
from .kit import L, N, P, TABLE, board, case_key, key

NVC = "nv_c / 203.0.113.45"
EVENTS = [  # (tiêu đề, giờ +07:00, tài khoản / IP, nhận định, mô tả)
    ("Xuất 320 dòng nợ quá hạn", "20/10 16:40", "nv_d / 10.1.2.15", "Bình thường", "Trong giờ, máy công ty, đúng vai trò, có phiếu."),
    ("7 lần sai mật khẩu", "21/10 02:10–02:14", NVC, "Bất thường", "IP lạ, nửa đêm, thử nhiều biến thể."),
    ("Đăng nhập, MFA đẩy được chấp thuận", "21/10 02:15", NVC, "Bất thường", "Ai chấp thuận, vì sao – chưa rõ."),
    ("Thêm phương thức MFA mới", "21/10 02:17", NVC, "Bất thường", "Cửa sau để quay lại không cần điện thoại chủ."),
    ("412 lượt xem, xuất 8.500 dòng", "21/10 02:20–02:42", NVC, "Bất thường", "Toàn bộ khách hàng Điện lực X, đủ cột."),
    ("Link Anyone, ẩn danh tải file", "21/10 02:45–03:06", "nv_c; ẩn danh / 198.51.100.7", "Bất thường", "Dữ liệu ra khỏi tổ chức lúc 03:06."),
]


def ev(i, e):
    return N(f"e{i}", "event", 40 + (i - 1) * 290, 70, e[4], title=e[0], tag=e[3], p={"gio": e[1], "tk": e[2]})


# ---------- Thực hành 10: truy vết truy cập bất thường (vòng 2) ----------
KEY_TH10 = key(
    "Đổi UTC sang +07:00: chuỗi bất thường xảy ra 02:10–03:06 sáng 21/10, không phải buổi tối. Dòng nv_d là bình thường theo ngữ cảnh. "
    "Tách quan sát với giả thuyết; “tài khoản nv_c bị chiếm” là giả thuyết mạnh nhất, “nv_c tự làm” chưa có căn cứ. "
    "Giữ bằng chứng trước khi ngăn chặn; nối dòng log với các việc đã hẹn sửa sau.",
    {"truy_vet": board([ev(i, e) for i, e in enumerate(EVENTS, 1)] + [
        N("f1", "fact", 42, 390, "nv_c đăng nhập từ IP lạ sau 7 lần sai; MFA được chấp thuận; thêm MFA mới.", title="Đăng nhập lạ"),
        N("f2", "fact", 42, 570, "Xuất 8.500 dòng; lên OneDrive; link Anyone; tải từ 198.51.100.7 lúc 03:06.", title="Dữ liệu ra ngoài"),
        N("f3", "fact", 42, 750, "Cả đêm không có cảnh báo; 07:45 nv_c đăng nhập bình thường từ máy công ty.", title="Không ai biết"),
        N("u1", "unknown", 362, 390, "Thiết bị nào, ai chấp thuận MFA lúc 02:15, vì sao.", title="Ai bấm Chấp nhận"),
        N("u2", "unknown", 362, 570, "Ai điều khiển phiên; mật khẩu lộ từ đâu.", title="Ai đứng sau phiên"),
        N("u3", "unknown", 362, 750, "File đã được chuyển tiếp cho ai.", title="File đi đâu tiếp"),
        N("h1", "hypo", 682, 390, "Tài khoản nv_c bị chiếm quyền (mạnh).", title="Bị chiếm tài khoản"),
        N("h2", "hypo", 682, 540, "Mật khẩu lộ do dùng lại ở trang khác (có khả năng).", title="Mật khẩu dùng lại"),
        N("h3", "hypo", 682, 690, "Dữ liệu được dùng để gọi lừa khách hàng (có khả năng).", title="Dùng để lừa đảo"),
        N("h4", "hypo", 682, 840, "nv_c tự làm (chưa có căn cứ).", title="Người dùng tự làm"),
        N("b1", "need", 1002, 375, "Nhật ký MFA chi tiết: thiết bị chấp thuận, phương thức mới.", title="Nhật ký MFA", p={"ai": "CNTT"}),
        N("b2", "need", 1002, 583, "Đăng nhập từ hai IP lạ 30 ngày; lịch sử chia sẻ file.", title="Log 30 ngày, OneDrive",
          p={"ai": "CNTT"}),
        N("b3", "need", 1002, 791, "Phiếu phản ánh, số kẻ gian đã gọi; trao đổi với anh Cường.", title="Tổng đài, người dùng",
          p={"ai": "Tổng đài; quản lý trực tiếp"}),
        N("x1", "action", 1310, 386, "Giữ log gốc + mã băm SHA-256; lưu thông tin file, link.", title="Giữ bằng chứng trước"),
        N("x2", "action", 1500, 515, "Đề xuất: tắt link, khóa nv_c, thu hồi phiên, gỡ MFA lạ.", title="Đề xuất ngăn chặn"),
        N("v1", "fix", 1310, 716, "Mật khẩu cũ lộ chưa đổi; MFA đẩy không khớp số.", title="Chương 4 – mật khẩu, MFA"),
        N("v2", "fix", 1500, 846, "Xuất toàn đơn vị, đủ cột; OneDrive cho link Anyone.", title="Chương 3, 5, 6 – quyền, chia sẻ"),
    ], [L(f"e{i}", f"e{i + 1}") for i in range(1, 6)] + [
        L("h1", "b1"), L("h1", "b2"), L("h2", "b3"), L("h3", "b3"), L("h4", "b1"),
        L("e2", "v1", vi_sao="Mật khẩu cũ chưa đổi"), L("e3", "v1", vi_sao="MFA không khớp số"),
        L("e5", "v2", vi_sao="GDV được xuất toàn đơn vị"), L("e6", "v2", vi_sao="Cho tạo link Anyone"),
    ])},
    modules=[
        ("🕒 <b>Sáu sự kiện</b>", "Giờ +07:00, tài khoản / IP, nhận định. Dòng nv_d: Bình thường.",
         "Đọc 19:10 là 7 giờ tối là lỗi nặng (có ⚠ nếu còn ghi UTC). Gộp các dòng cùng loại (7 lần sai) là được."),
        ("✔️ <b>Đã biết</b>", "Chỉ điều log ghi: đăng nhập lạ, xuất, link, tải từ IP ngoài, không cảnh báo.", "Không có suy đoán trong cột này."),
        ("❓ <b>Chưa biết</b>", "Ai chấp thuận MFA; ai điều khiển phiên; mật khẩu lộ từ đâu; file đi đâu.", ""),
        ("💡 <b>Giả thuyết</b> (4)", "Bị chiếm (mạnh); mật khẩu dùng lại; dùng để lừa; tự làm (chưa có căn cứ).",
         "Phải có giả thuyết “tài khoản bị chiếm”. Ghi kèm mức chắc chắn."),
        ("📎 <b>Bằng chứng cần thêm</b>", "Nhật ký MFA; log 30 ngày và lịch sử chia sẻ; tổng đài và người dùng.", "Ghi ai cung cấp."),
        ("▶️ <b>Hành động</b>", "Giữ bằng chứng trước; đề xuất ngăn chặn cho người có thẩm quyền.",
         "Trong thẩm quyền của người phân tích: đề xuất, không tự khóa. Giữ bằng chứng trước khi xóa, khóa."),
        ("🧾 <b>Việc hẹn sửa sau</b>", "Chương 4; chương 3, 5, 6. “Không có cảnh báo” là lỗ hổng mới (chương 9), ghi ở thẻ Đã biết.",
         "Chỉ đủ chỗ cho 2 thẻ trên bảng; học viên làm 3–4 thẻ cũng được."),
    ],
    links=[
        ("Sự kiện → sự kiện", "—", "Theo đúng thứ tự thời gian."),
        ("Giả thuyết → bằng chứng", "—", "Mỗi giả thuyết có ít nhất một bằng chứng kiểm tra được nó."),
        ("7 lần sai → Chương 4", "Mật khẩu cũ chưa đổi", "Dòng log 2–8."),
        ("MFA chấp thuận → Chương 4", "MFA không khớp số", "Dòng log 9."),
        ("Xuất 8.500 dòng → Chương 3, 6", "GDV được xuất toàn đơn vị", "Dòng log 12."),
        ("Link Anyone → Chương 5", "Cho tạo link Anyone", "Dòng log 14."),
    ],
    more=[("Bằng chứng cần giữ ngay (trao cho buổi 10)", [
        P("File log gốc từ ba nguồn kèm mã băm SHA-256 và biên bản trích xuất (ai trích, lúc nào, từ đâu); nhật ký MFA chi tiết của nv_c; "
          "thông tin file và link trên OneDrive (không xóa file trước khi lưu thông tin); phiếu phản ánh của tổng đài; số điện thoại kẻ gian đã gọi."),
        TABLE(["Dòng log", "Vì sao thành công", "Dòng trên tờ"],
              ["2–9 (02:10–02:15)", "Mật khẩu cũ lộ chưa đổi; MFA đẩy không khớp số", "Chương 4"],
              ["12 (02:42)", "GDV có quyền xuất toàn đơn vị; xuất luôn đủ cột", "Chương 3 và 6"],
              ["14 (02:47)", "OneDrive công ty cho tạo link Anyone", "Chương 5"],
              ["Cả đêm", "Không có cảnh báo nào, hoặc không ai nhận", "Mới – chương 9"]),
        P("Vòng 1 (log mẫu 5 dòng): đã biết nv_a đăng nhập, xuất 12.000 dòng; admin_b cấp quyền Export lúc 22:03. Cần xác minh quyền hiệu lực lúc 22:01, "
          "đồng hồ, thiết bị. Hành động: giữ log, báo đầu mối, cân nhắc tạm giới hạn quyền xuất, hỏi admin_b lý do cấp quyền."),
    ])],
    rubric=[
        ("Dòng thời gian", "2,5", "Đúng thứ tự, đã đổi sang +07:00, có tài khoản / IP. Trừ nặng nếu đọc 19:10 là 7 giờ tối."),
        ("Loại trừ dòng nv_d", "1", "Nhận định Bình thường kèm ngữ cảnh."),
        ("Quan sát và suy đoán", "2,5", "Đủ 4 cột; ít nhất 3 giả thuyết có “tài khoản bị chiếm”; mỗi giả thuyết nối bằng chứng."),
        ("Hành động", "2", "Trong thẩm quyền; giữ bằng chứng trước khi xóa, khóa; không kết luận người cụ thể."),
        ("Vòng 2: việc hẹn sửa", "2", "Ít nhất 3 dòng log nối việc hẹn sửa có lý do; nhận ra lỗ hổng không có cảnh báo."),
    ],
    mistakes=[
        ("Không đổi múi giờ", "Giờ ghi 19:10, có ⚠", "“Chữ Z cuối giờ nghĩa là gì? Nhân viên đang làm gì lúc 02:10?”"),
        ("Kết luận anh Cường làm lộ", "Giả thuyết “nv_c tự làm” ở cột Đã biết", "Quy tắc: không kết luận người cụ thể chỉ từ tên tài khoản."),
        ("Nghi dòng nv_d", "Dòng 16:40 nhận định Bất thường", "“Trong giờ, máy công ty, có phiếu: khác gì công việc thường ngày?”"),
        ("Xóa link trước khi lưu", "Hành động đầu tiên là xóa", "“Xóa rồi lấy gì làm bằng chứng ai đã tải?”"),
        ("Bỏ sót cảnh báo", "Không nhắc việc cả đêm không ai biết", "“Vì sao 5 tiếng sau mới có người phát hiện?”"),
    ],
    flow=["Hỏi lớp: 19:10Z là mấy giờ ở Việt Nam?",
          "Mở bảng mẫu: đọc dòng thời gian từ trái sang phải; dừng ở dòng nv_d.",
          "Đọc 4 cột: hỏi giả thuyết nào chưa có căn cứ.",
          "Nối với tờ “Việc hẹn sửa sau”; chuyển dòng thời gian sang buổi 10."],
)

# ---------- Bài tập thêm: log cho biết gì, còn thiếu gì? ----------
KEY_CASE9 = case_key(
    "Năm mốc đều sang ngày 21/10 (+07:00): 02:10, 02:15, 02:18, 02:40, 02:45. Log cho thấy thao tác dưới tài khoản nv_a, "
    "chưa chứng minh chính chủ làm hay đã có người tải. Cần nhật ký phiên, MFA, liên kết, lịch làm việc; báo đầu mối, bảo toàn log.",
    ["Diễn biến (giờ +07:00):\n21/10 02:10 – nv_a đăng nhập thất bại từ 203.0.113.8\n21/10 02:15 – đăng nhập thành công sau MFA\n"
     "21/10 02:18 – thêm phương thức MFA\n21/10 02:40 – xuất 5.000 dòng\n21/10 02:45 – tạo liên kết công khai",
     "Đã thấy trong log: (1) đăng nhập thất bại rồi thành công từ 203.0.113.8 sau MFA; (2) thêm phương thức MFA lúc 02:18; "
     "(3) xuất 5.000 dòng và tạo liên kết công khai dưới tài khoản nv_a.\n"
     "Giả thuyết cần xác minh: (a) tài khoản nv_a bị người khác chiếm và điều khiển; (b) file đã bị người ngoài mở hoặc tải qua liên kết.",
     "Bằng chứng cần bổ sung: nhật ký phiên (thiết bị, IP các phiên khác), chi tiết MFA (thiết bị chấp thuận, phương thức mới), "
     "thông tin liên kết và nhật ký truy cập liên kết, lịch làm việc của nv_a.\n"
     "Hành động trong thẩm quyền: (1) báo ngay đầu mối ATTT kèm bảng diễn biến; (2) bảo toàn nhật ký gốc (bản sao, mã băm). "
     "Đề xuất người có thẩm quyền hạn chế liên kết và xử lý phiên nghi ngờ; không tự xóa file, không kết luận cá nhân."],
    [("1. Đổi giờ", "Đủ 5 mốc, cộng 7 giờ, sang ngày 21/10.", "Ghi rõ múi giờ trên bảng."),
     ("2. Tách quan sát / giả thuyết", "3 điều log ghi; 2 giả thuyết (bị chiếm; đã bị tải).", "Ghi mức chắc chắn."),
     ("3. Bằng chứng, hành động", "Nhật ký phiên, MFA, liên kết, lịch làm việc; báo đầu mối, bảo toàn log.",
      "Đề xuất hạn chế liên kết cho người có thẩm quyền.")],
    ["Đổi đúng giờ và ngày; không đọc 19:10 là buổi tối.",
     "Tách rõ quan sát với giả thuyết; không kết luận chính chủ làm.",
     "Bằng chứng bổ sung kiểm tra được từng giả thuyết; hành động đúng thẩm quyền, giữ log trước."],
    [("Quên đổi ngày", "Ghi 20/10 02:10", "“Cộng 7 giờ vào 19:10 ngày 20 thì sang ngày nào?”"),
     ("Kết luận nv_a cố ý", "“nv_a làm lộ dữ liệu”", "“Log cho biết tài khoản hay người?”"),
     ("Tự khóa, xóa file", "Hành động vượt thẩm quyền", "“Bạn được giao quyền gì? Xóa file rồi lấy gì làm bằng chứng?”")],
)

KEYS = {"m09-th10": KEY_TH10, "m09-case-v2": KEY_CASE9}
