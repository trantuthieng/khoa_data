"""Đáp án giảng viên – buổi 10."""
from .kit import L, N, P, TABLE, board, case_key, key

# (đợt, tiêu đề, giờ, căn cứ, nội dung, vai quyết A, vai làm R)
DECISIONS = [
    (1, "Báo cáo ban đầu cho lãnh đạo, chủ dữ liệu", "08:50", "Quy chế: đầu mối ATTT nhận báo cáo",
     "Email kèm gọi điện, 4 nhóm thông tin, không chờ log; đề nghị CNTT trích log 3 nguồn.", 1, 2),
    (1, "Tổng đài trả lời tạm, không gọi lại kẻ gian", "09:05", "Câu trả lời tạm thời (bài 3)",
     "Không xác nhận, không phủ nhận; dặn khách không chuyển tiền; giữ số kẻ gian cho công an.", 1, 3),
    (2, "Giữ bằng chứng trước", "10:25", "Bằng chứng trước, ngăn chặn sau",
     "Thông tin file, link, nhật ký; mã băm; BC-002, BC-003.", 1, 2),
    (2, "Thu hồi link, vô hiệu hóa nv_c", "10:35–10:40", "Quy chế: đầu mối quyết 1 TK, 1 link",
     "Không xóa file, tài khoản; thu hồi phiên, gỡ MFA lạ.", 1, 2),
    (2, "Chặn link Anyone mới toàn Công ty", "10:45", "Vượt thẩm quyền → lãnh đạo duyệt",
     "Báo trước 3 phòng chia sẻ đối tác; rà link cũ 48 giờ.", 4, 2),
    (3, "Phạm vi: 8.500 khách hàng, 6 nhóm cột", "11:30", "Nhật ký link, file OneDrive",
     "Coi như toàn bộ đã ra ngoài từ 03:06; link mở 02:47–10:35.", 1, 2),
    (3, "Anh Cường là nạn nhân, không kỷ luật", "11:45", "Lời kể, nhật ký MFA, tin Zalo",
     "Cảm ơn, hỗ trợ đổi mật khẩu, không nêu tên. Hai tài khoản bị thử: buộc đổi mật khẩu.", 3, 1),
    (4, "Thông báo cơ quan chuyên trách", "14:10", "Nghị định 356; T0 = 08:50 thứ Tư",
     "Hạn 08:50 thứ Bảy (72 giờ đồng hồ). Song song tố giác lừa đảo với công an.", 4, 5),
    (4, "Cảnh báo khách hàng, một người phát ngôn", "14:30", "Thông cáo đã duyệt",
     "Tin cảnh báo không có link; anh Khoa trả lời báo chí; không nêu tên nhân viên.", 4, 6),
    (5, "24 giờ: khớp số MFA, bật cảnh báo", "09:30 23/10", "Nguyên nhân đã xác minh",
     "Lịch trực cảnh báo ngoài giờ; trong 1 tuần bỏ quyền xuất toàn đơn vị của giao dịch viên.", 4, 2),
    (5, "Sổ đăng ký rủi ro cho việc hẹn sửa sau", "09:45 23/10", "Cây “vì sao”: không ai chấp nhận rủi ro",
     "Ông Hưng giao chị Lan theo dõi, rà soát hằng tháng có biên bản.", 4, 1),
]

_nodes = [N(f"vai{i}", "role", 52, 80 + (i - 1) * 108) for i in range(1, 8)]
_links, _row = [], {}
_count = {d[0]: sum(1 for x in DECISIONS if x[0] == d[0]) for d in DECISIONS}
for dot, title, gio, can_cu, text, a, r in DECISIONS:
    k = _row.get(dot, 0)
    _row[dot] = k + 1
    qid = f"q{dot}" if k == 0 else f"q{dot}_{k + 1}"
    step = 294 if _count[dot] < 3 else 270   # cột 3 quyết định: chữ ngắn hơn, xếp sát hơn
    _nodes.append(N(qid, "dec", 373 + (dot - 1) * 278, 66 + k * step, text, title=title, p={"gio": gio, "can_cu": can_cu}))
    _links += [L(f"vai{a}", qid, vai="A"), L(f"vai{r}", qid, vai="R")]

KHUYEN_NGHI = [
    ("Bật khớp số cho MFA toàn Công ty", "Trưởng nhóm hạ tầng CNTT", "24 giờ", "Đăng nhập thử: không nhập số thì không qua"),
    ("Bật cảnh báo đăng nhập lạ, xuất lớn, link Anyone; lịch trực ngoài giờ", "Chị Lan", "24 giờ", "Tạo sự kiện thử, có người nhận trong 15 phút"),
    ("Bỏ quyền xuất toàn đơn vị của giao dịch viên", "Anh Tuấn và CNTT", "1 tuần", "Thử xuất bằng tài khoản giao dịch viên: bị từ chối"),
    ("Chức năng xuất theo mẫu cột, mặc định ít cột nhất", "CNTT theo yêu cầu anh Tuấn", "1 tháng", "Bản xuất mặc định không còn điện thoại, số nợ"),
    ("Sổ đăng ký rủi ro cho mọi việc hẹn sửa sau", "Ông Hưng giao chị Lan", "Thường xuyên", "Rà soát hằng tháng có biên bản"),
]

# ---------- Thực hành 11: diễn tập trên bàn ----------
KEY_TH11 = key(
    "Mỗi quyết định ghi đủ giờ, ai quyết (A), ai làm (R), căn cứ. Giữ bằng chứng trước hoặc song song với ngăn chặn; không xóa file, "
    "không xóa tài khoản; việc vượt thẩm quyền đầu mối trình lãnh đạo. Đồng hồ 72 giờ tính theo giờ đồng hồ từ T0 = 08:50 thứ Tư. "
    "Rút kinh nghiệm không đổ lỗi cho anh Cường.",
    {"dien_tap": board(_nodes, _links),
     "hop_nhanh": "Làm tốt: tổng đài báo ngay, đầu mối báo cáo sau 20 phút, giữ bằng chứng trước khi thu hồi link, anh Cường kể thật.\n"
                  "Chưa rõ: ai được tắt chia sẻ toàn Công ty khi lãnh đạo đang họp; ai trực nhận cảnh báo ban đêm.\n"
                  "Cần sửa ngay ở đơn vị: lập sổ đăng ký rủi ro, mọi việc “hẹn sửa sau” phải có người chấp nhận và hạn.",
     "khuyen_nghi": [{"viec": v, "nguoi": n, "han": h, "kiem_chung": k} for v, n, h, k in KHUYEN_NGHI],
     "cau_hoi_mo": "File đã được chuyển tiếp cho ai (ngoài tầm log Công ty, chờ cơ quan chức năng)? "
                   "Mật khẩu lộ từ trang mua sắm mới ở mức “có khả năng”. Công ty hỗ trợ hai khách đã mất tiền đến mức nào?"},
    modules=[
        ("🎭 <b>Bảy vai</b>", "Có sẵn; không cần ghi.", "Thư ký có thể không nối dây nào."),
        ("⚖️ <b>Đợt 1 – Phát hiện</b>", "Báo cáo ban đầu không chờ log; tổng đài trả lời tạm, không gọi lại kẻ gian.",
         "Ghi mốc 08:35 và 08:50; pháp chế chọn T0. Điểm trừ: chờ thêm cuộc gọi “cho chắc”."),
        ("⚖️ <b>Đợt 2 – Ngăn chặn</b>", "Giữ bằng chứng → thu hồi link (không xóa file) → vô hiệu nv_c; trình lãnh đạo việc chặn link toàn Công ty.",
         "Điểm trừ: xóa file, xóa tài khoản, tắt cả hệ thống, chờ lãnh đạo họp xong mới thu hồi link."),
        ("⚖️ <b>Đợt 3 – Phạm vi</b>", "8.500 khách hàng, 6 nhóm cột; anh Cường là nạn nhân và nhân chứng.",
         "Ghi “mật khẩu lộ từ trang mua sắm” vào cột đã xác minh là sai: mới ở mức có khả năng."),
        ("⚖️ <b>Đợt 4 – Báo cáo</b>", "Thông báo cơ quan chuyên trách hạn 08:50 thứ Bảy; cảnh báo khách không có link; một người phát ngôn.",
         "Tính 72 giờ theo ngày làm việc là sai."),
        ("⚖️ <b>Đợt 5 – Phục hồi</b>", "Cải tiến theo mốc có người phụ trách; sổ đăng ký rủi ro.",
         "Nguyên nhân gốc nằm ở chức năng quản trị, không nằm ở một cú bấm."),
    ],
    links=[
        ("Vai → quyết định", "A", "Người có thẩm quyền quyết. Biện pháp ảnh hưởng toàn Công ty: A là ông Hưng."),
        ("Vai → quyết định", "R", "Người thực hiện. Phần lớn biện pháp kỹ thuật: R là anh Phong."),
    ],
    more=[("Đoạn rút kinh nghiệm mẫu", [
        P("“Đêm 20–21/10, tài khoản của một giao dịch viên Điện lực X bị đăng nhập từ bên ngoài, nhiều khả năng bằng một mật khẩu cũ đã lộ ở "
          "một trang web khác. Một tin nhắn giả danh CNTT khiến yêu cầu MFA lúc 02:15 trông như việc đã được báo trước, và cấu hình MFA chỉ "
          "cần một cú bấm. Với quyền xuất toàn đơn vị và chức năng xuất luôn đủ cột, phiên đó tạo ra file 8.500 khách hàng; link “Anyone” "
          "đưa file ra Internet trong 20 phút, và không có cảnh báo nào trong đêm. Bốn điều kiện đã được phát hiện từ trước và hẹn xử lý sau, "
          "nhưng không ai được giao chấp nhận rủi ro và theo dõi hạn. Các lớp đã hoạt động: khách hàng gọi kênh chính thức, giao dịch viên báo "
          "ngay, đầu mối báo cáo sau 20 phút và giữ bằng chứng trước khi ngăn chặn, người dùng bị chiếm tài khoản đã kể thật.”"),
        P("Đoạn này không có tên người, không có từ “bất cẩn”, và có một câu về những gì đã làm tốt."),
    ])],
    rubric=[
        ("Đủ 5 đợt", "2", "Mỗi đợt có ít nhất một quyết định đã ghi nội dung."),
        ("Bốn ý mỗi quyết định", "2", "Có giờ, căn cứ, A và R trên dây."),
        ("Thẩm quyền và bằng chứng", "2", "Việc vượt thẩm quyền trình lên; giữ bằng chứng trước khi ngăn chặn; không xóa file, tài khoản."),
        ("72 giờ và truyền thông", "2", "T0 có lý do, hạn tính theo giờ đồng hồ; tin cảnh báo không có link, không nêu tên nhân viên."),
        ("Rút kinh nghiệm", "2", "Không đổ lỗi; khuyến nghị có người, hạn, cách kiểm chứng; có câu hỏi còn mở."),
    ],
    mistakes=[
        ("Xóa link và file ngay", "Đợt 2 không có bước giữ bằng chứng", "“Xóa rồi thì biết ai đã tải bằng cách nào?”"),
        ("Đầu mối tự tắt chia sẻ toàn Công ty", "A là chị Lan", "“Quy chế cho đầu mối quyết những biện pháp nào?”"),
        ("Kỷ luật anh Cường", "Quyết định đợt 3 là kiểm điểm", "“Nếu bị kỷ luật, lần sau người bị lừa có kể thật không?”"),
        ("Tính 72 giờ theo ngày làm việc", "Hạn thứ Hai tuần sau", "72 giờ đồng hồ từ T0: 08:50 thứ Bảy."),
        ("Khuyến nghị chỉ “đào tạo lại”", "Không có người, hạn, kiểm chứng", "“Ai làm, đến khi nào, thử thế nào để biết đã xong?”"),
    ],
    flow=["Sau mỗi đợt, cho một học viên đọc quyết định kèm A/R; lớp hỏi “căn cứ là gì?”.",
          "Cuối buổi mở bảng mẫu, đọc biên bản tự lập theo đợt.",
          "Đọc đoạn rút kinh nghiệm mẫu; hỏi lớp tìm câu nói về việc làm tốt.",
          "Họp nhanh 10 phút theo ba câu hỏi."],
)

# ---------- Bài tập thêm: báo cáo sự cố trong 5 phút ----------
KEY_CASE10 = case_key(
    "Phân biệt 600 dòng trong file với số người đã bị ảnh hưởng; chưa có log tải thì không kết luận. Giữ thông tin liên kết, nhật ký, "
    "báo người có thẩm quyền thu hồi liên kết. Theo giả định T0 08:40 ngày 21/10, hạn là 08:40 ngày 24/10/2026, tính giờ liên tục.",
    ["Báo cáo ban đầu: 08:40 ngày 21/10 tổng đài nhận phản ánh kẻ gian biết số nợ khách hàng; 08:55 em nhận tin. "
     "09:10 phát hiện một liên kết công khai tới file 600 dòng. Chưa rõ: có ai đã tải file chưa, file lộ từ đâu, bao nhiêu khách thật sự bị ảnh hưởng. "
     "Nguy cơ: kẻ gian tiếp tục gọi lừa khách hàng; liên kết còn mở thì còn người tải được. "
     "Em đã ghi lại thông tin liên kết, giờ phát hiện và đề nghị trích nhật ký truy cập. "
     "Cần anh/chị duyệt: thu hồi liên kết ngay và rà tài khoản đã tạo liên kết. Em cập nhật tiếp lúc 10:00.",
     "Em làm được: (1) chụp và ghi thông tin liên kết, người tạo, thời điểm; xin trích nhật ký truy cập; ghi nơi lưu bằng chứng; "
     "(2) báo người được giao quyền; (3) ghi phiếu phản ánh của khách đầy đủ.\n"
     "Cần người có thẩm quyền: thu hồi liên kết (không xóa file); rà phiên và tài khoản đã tạo liên kết; bố trí phương án tiếp nhận khách đã duyệt.\n"
     "Thứ tự: giữ thông tin liên kết trong vài phút → thu hồi ngay → rà tài khoản; không để liên kết mở lâu chỉ để thu thập hoàn hảo.",
     "T0 (giả định) = 08:40 ngày 21/10/2026 (+07:00); T0 + 72 giờ = 08:40 ngày 24/10/2026, tính giờ liên tục, không theo ngày làm việc.\n"
     "Cải tiến 1: chủ dữ liệu rà quyền xuất trong 7 ngày; CNTT thử xuất bằng tài khoản thường → phải bị từ chối.\n"
     "Cải tiến 2: đầu mối sự cố tổ chức thử cảnh báo liên kết công khai trong 14 ngày; lưu thời gian từ cảnh báo đến khi có người nhận."],
    [("1. Báo cáo ban đầu", "Đủ: đã biết, chưa rõ, nguy cơ, việc đã làm, việc cần duyệt, người và giờ cập nhật.",
      "Không nói “đã lộ 600 khách” hay “chưa lộ gì”."),
     ("2. Thứ tự và thẩm quyền", "Giữ bằng chứng → ngăn chặn → duy trì công việc; tách việc mình làm và việc cần duyệt.", "Không kéo dài phơi lộ."),
     ("3. 72 giờ và cải tiến", "08:40 ngày 24/10/2026; 2 cải tiến có người, hạn, cách kiểm chứng.", "Nêu: thực tế pháp chế xác định T0.")],
    ["Phân biệt dữ kiện với điều chưa biết; không kết luận khi chưa có log.",
     "Thứ tự hợp lý, đúng thẩm quyền; không tự khóa toàn hệ thống.",
     "Tính đúng hạn theo giờ liên tục; cải tiến kiểm chứng được."],
    [("Kết luận 600 khách đã bị lộ", "“600 khách hàng bị ảnh hưởng”", "“Đã có log tải chưa?”"),
     ("Tự khóa toàn hệ thống", "Câu 2: “khóa hết”", "“Đề bài nói bạn có quyền gì?”"),
     ("Tính hạn theo ngày làm việc", "Hạn ngày 26/10", "72 giờ liên tục từ T0."),
     ("Cải tiến chung chung", "“Nâng cao ý thức”", "“Ai, đến khi nào, kiểm tra bằng cách nào?”")],
)

KEYS = {"m10-th11": KEY_TH11, "m10-case-v2": KEY_CASE10}
