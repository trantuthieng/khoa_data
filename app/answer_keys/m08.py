"""Đáp án giảng viên – buổi 8."""
from .kit import L, N, P, TABLE, board, case_key, key

# (đòn tâm lý, dấu hiệu, tạm dừng, xác minh, báo, thực hiện + câu từ chối)
ROWS = [
    ("Uy quyền, Khẩn cấp, Chặn xác minh",
     "Tài khoản Zalo lạ dùng ảnh lấy từ website; vượt quy trình; gấp; xin danh sách kèm số điện thoại qua Zalo.",
     "Không gửi, không trả lời chi tiết. Chụp tin nhắn.",
     "Gọi số của giám đốc trong danh bạ cơ quan hoặc qua thư ký.",
     "Báo đầu mối ATTT; giữ ảnh tin nhắn, tên tài khoản, giờ nhận.",
     "Thật thì gửi qua kênh công vụ. “Dạ danh sách khách hàng em chỉ gửi qua kênh công vụ sau khi xác nhận qua số nội bộ ạ.”"),
    ("Quen thuộc, Khẩn cấp",
     "Không chờ báo giá; file .xlsm đòi Enable Content; tên miền thêm “-vn” khác nhà cung cấp thật.",
     "Không mở file, không bật nội dung.",
     "Gọi nhân viên kinh doanh của nhà cung cấp theo số trong hợp đồng.",
     "Report phishing / chuyển email cho ATTT; không tự xóa trước khi được hướng dẫn.",
     "Nhận báo giá qua kênh đã biết. “Em sẽ gọi lại bạn phụ trách bên anh theo số trong hợp đồng để nhận báo giá ạ.”"),
    ("Uy quyền, Khẩn cấp, Quen thuộc",
     "Đe dọa khóa tài khoản; đăng nhập qua QR trên điện thoại cá nhân; không có phòng ban, số liên hệ; CNTT không thông báo bằng poster.",
     "Không quét, không đăng nhập qua QR. Chụp poster, ghi vị trí.",
     "Tự mở ứng dụng email như mọi ngày; hỏi helpdesk qua số nội bộ.",
     "Báo helpdesk / ATTT kèm ảnh, vị trí; đề nghị gỡ poster. Ai đã nhập mật khẩu → báo ngay.",
     "Không cần trả lời ai. Nếu lỡ nhập mật khẩu: đổi mật khẩu, thu hồi phiên."),
    ("Uy quyền, Khẩn cấp, Chặn xác minh, Quen thuộc",
     "Zalo cá nhân lúc 21:30; dặn chấp nhận đăng nhập mình không tạo; dọa cả phòng không vào được; nài nỉ.",
     "Không trả lời, không bấm. Có thông báo MFA → Từ chối.",
     "Gọi hotline CNTT theo số trong danh bạ nội bộ.",
     "Báo ATTT ngay trong đêm; giữ ảnh tin nhắn, tài khoản Zalo, giờ các thông báo MFA.",
     "Đổi mật khẩu vì ai đó đã có nó. “Em không chấp nhận đăng nhập mà em không tự thực hiện. Em gọi hotline CNTT để hỏi lại.”"),
]

# dấu hiệu rút gọn cho vừa thẻ trên bảng; bản đầy đủ ở bảng đáp án
SHORT = ["Zalo lạ, ảnh lấy từ website; gấp; xin DS kèm SĐT.",
         "Không chờ báo giá; .xlsm đòi Enable Content; miền “-vn”.",
         "Dọa khóa tài khoản; đăng nhập qua QR; không có đầu mối.",
         "Zalo cá nhân 21:30; dặn chấp nhận MFA; dọa, nài nỉ."]

_nodes, _links = [], []
for i, (don, _, stop, verify, report, act) in enumerate(ROWS, 1):
    y = 70 + (i - 1) * 260
    _nodes += [N(f"h{i}", "case", 40, y - 20, SHORT[i - 1], p={"don": don}),
               N(f"h{i}_stop", "stop", 380, y, stop), N(f"h{i}_verify", "verify", 720, y, verify),
               N(f"h{i}_report", "report", 1060, y, report), N(f"h{i}_act", "act", 1400, y, act)]
    _links += [L(f"h{i}", f"h{i}_stop"), L(f"h{i}_stop", f"h{i}_verify"),
               L(f"h{i}_verify", f"h{i}_report"), L(f"h{i}_report", f"h{i}_act")]

# ---------- Thực hành 9: bốn yêu cầu cần xác minh ----------
KEY_TH9 = key(
    "Không cần đoán thật hay giả: cả bốn tình huống giải quyết bằng cùng một quy trình – tạm dừng, xác minh qua kênh độc lập "
    "(không phải kênh của người yêu cầu), báo đầu mối kèm bằng chứng, chỉ thực hiện khi đã rõ. Câu từ chối dựa vào quy định, lịch sự.",
    {"xu_ly_yeu_cau": board(_nodes, _links)},
    modules=[
        ("📨 <b>Tình huống</b>", "Chọn đòn tâm lý và ghi dấu hiệu nghi ngờ.",
         "Chọn thêm hoặc bớt một đòn vẫn đạt nếu dấu hiệu đúng. Quan trọng là chỉ ra được dấu hiệu cụ thể."),
        ("✋ <b>1. Tạm dừng</b>", "Không làm theo; giữ lại bằng chứng.", "Không xóa tin, không trả lời chi tiết."),
        ("☎️ <b>2. Xác minh độc lập</b>", "Kênh cụ thể: danh bạ cơ quan, số trong hợp đồng, hotline nội bộ.",
         "Gọi lại số trong tin nhắn hay hỏi “có phải anh không?” trên chính kênh đó là <b>không</b> độc lập."),
        ("📣 <b>3. Báo đầu mối</b>", "ATTT hoặc helpdesk; giữ ảnh, tên tài khoản, giờ, địa chỉ email.", "Không tự xóa email trước khi được hướng dẫn."),
        ("✅ <b>4. Thực hiện khi rõ</b>", "Việc làm khi đã rõ và câu từ chối lịch sự.", "Câu từ chối dựa vào quy định, không dựa vào “em thấy nghi”."),
    ],
    more=[("Bảng đáp án theo tình huống", [
        TABLE(["Tình huống", "Dấu hiệu chính", "Kênh xác minh", "Báo ai, giữ gì"],
              *[[f"{i}", r[1], r[3], r[4]] for i, r in enumerate(ROWS, 1)]),
        P("Nếu “lãnh đạo” ở tình huống 1 là thật, cuộc gọi xác minh tốn một phút và lãnh đạo sẽ yên tâm hơn về nhân viên của mình."),
    ])],
    rubric=[
        ("Dấu hiệu và đòn tâm lý", "2", "Mỗi tình huống có ít nhất 2 dấu hiệu cụ thể và đòn tâm lý phù hợp."),
        ("Tạm dừng", "1", "Không làm theo, giữ bằng chứng."),
        ("Xác minh độc lập", "3", "Kênh cụ thể, độc lập với người yêu cầu, cho cả 4 tình huống."),
        ("Báo và bằng chứng", "2", "Báo đúng đầu mối, liệt kê bằng chứng cần giữ."),
        ("Câu từ chối", "2", "Lịch sự, dựa vào quy định; tình huống 4 có Từ chối MFA và đổi mật khẩu."),
    ],
    mistakes=[
        ("Đoán thật/giả rồi dừng", "“Tình huống 2 là thật vì đúng tên công ty”", "“Bạn kiểm chứng bằng cách nào? Quy trình có cần đoán không?”"),
        ("Xác minh trên kênh của kẻ gian", "“Nhắn lại hỏi có phải anh không”", "“Nếu là kẻ gian, họ sẽ trả lời gì?”"),
        ("Tự xóa email", "“Xóa luôn cho an toàn”", "“ATTT cần email đó để chặn cho cả đơn vị.”"),
        ("Bấm Chấp nhận rồi báo", "Tình huống 4 chọn bấm cho xong", "“Bạn có đang đăng nhập không? Vậy ai đang đăng nhập?”"),
        ("Câu từ chối cảm tính", "“Em thấy nghi nên không gửi”", "Dựa vào quy định: “dữ liệu khách hàng chỉ gửi qua kênh công vụ”."),
    ],
    flow=["Đóng vai tình huống 4: giảng viên làm kẻ giả mạo, ép hai lần.",
          "Mở bảng mẫu: đọc theo hàng; chỉ ra cột ② luôn là một kênh khác.",
          "Hỏi: tình huống nào cần biết chắc thật hay giả? (Không tình huống nào.)",
          "Phát checklist xác minh thông điệp để học viên mang về."],
)

# ---------- Bài tập thêm: viết lời từ chối và báo tin đáng ngờ ----------
KEY_CASE8 = case_key(
    "Dấu hiệu: ngoài giờ, thúc giục, đe trách nhiệm, cấm gọi lại, gửi danh sách qua kênh lạ, liên kết đăng nhập lạ. "
    "Từ chối lịch sự, xác minh qua số nội bộ đã biết; báo đầu mối với đủ giờ, kênh, nội dung, việc đã làm, bằng chứng.",
    ["Dấu hiệu: (1) 21:30, ngoài giờ; (2) “gửi ngay”, “chậm là em chịu trách nhiệm” – thúc giục, đe dọa; (3) “đừng gọi” – chặn xác minh; "
     "(4) xin 320 hộ nợ qua kênh nhắn tin, vượt quy trình; (5) liên kết minhan-support.example không phải tên miền Công ty.\n"
     "Đòn tâm lý: mượn uy quyền, tạo khẩn cấp, chặn kênh xác minh.",
     "“Dạ em cần xác minh yêu cầu qua kênh công việc trước khi chuyển dữ liệu khách hàng. Em sẽ liên hệ anh theo số nội bộ đã có ạ.”\n"
     "Xác minh: gọi số của lãnh đạo trong danh bạ cơ quan hoặc qua thư ký; không gọi số, không mở liên kết trong tin nhắn.",
     "Gửi đầu mối ATTT: “21:30 ngày …, em nhận tin nhắn từ tài khoản [tên hiển thị, định danh] mang ảnh lãnh đạo, qua [ứng dụng]. "
     "Nội dung: đòi gửi danh sách 320 hộ nợ, yêu cầu không gọi lại, kèm liên kết https://minhan-support.example/login. "
     "Em chưa gửi dữ liệu, chưa mở liên kết, chưa nhập thông tin (nếu đã bấm: ghi rõ giờ và đã nhập gì). "
     "Em đã giữ ảnh chụp tin nhắn, định danh người gửi, giờ nhận và URL dạng văn bản.”"],
    [("1. Dấu hiệu, đòn tâm lý", "Ít nhất 3 dấu hiệu từ đề; gọi tên đòn tâm lý.", "Nhận ra tên miền lạ."),
     ("2. Trả lời và xác minh", "2–3 câu lịch sự, dựa vào quy định; kênh xác minh độc lập.", "Không dùng số / liên kết trong tin nhắn."),
     ("3. Tin báo đầu mối", "Đủ thời điểm, kênh, nội dung, việc đã làm, bằng chứng.", "Nói rõ nếu đã bấm hoặc nhập thông tin.")],
    ["Nhận ra yêu cầu bất thường và các đòn tâm lý từ dữ kiện đề.",
     "Từ chối lịch sự, có kênh xác minh độc lập; không gửi dữ liệu.",
     "Tin báo đủ 5 ý để đầu mối xử lý ngay; bằng chứng giữ đúng cách."],
    [("Hỏi lại trên chính kênh đó", "“Anh có phải là giám đốc không?”", "“Kẻ gian sẽ trả lời gì?”"),
     ("Mở liên kết để kiểm tra", "“Em vào thử xem trang có thật không”", "Không mở; chép URL dạng văn bản để báo."),
     ("Chuyển tiếp file để minh họa", "Đính kèm danh sách khi báo", "Không chuyển dữ liệu khách hàng khi báo sự việc.")],
)

KEYS = {"m08-th9": KEY_TH9, "m08-case-v2": KEY_CASE8}
