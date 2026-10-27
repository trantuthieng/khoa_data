"""Đáp án dành cho giảng viên, theo mã hoạt động.

Chỉ gửi qua API giảng viên (/api/t/answers), không gắn vào ACTIVITIES nên không bao giờ tới trình duyệt học viên.

Mỗi đáp án:
  "fields": bài làm mẫu, cùng định dạng bài nộp của học viên (trường "board" là
            {nodes: [{id, kind, x, y, title?, text, tag?, p?}], links: [{id, from, to, <trường trên dây>}]}).
            Giao diện giảng viên hiển thị bằng chính bảng của học viên ở chế độ chỉ đọc.
  "sections": phần giải thích, dạng khối nội dung như giáo trình (h3, p, list, table).
            Mục có "private": True (thang điểm, lỗi hay gặp) tự ẩn khi trình chiếu.
"""


def P(html):
    return {"t": "p", "html": html}


def UL(*items):
    return {"t": "list", "ordered": False, "items": [{"html": x, "level": 0} for x in items]}


def OL(*items):
    return {"t": "list", "ordered": True, "items": [{"html": x, "level": 0} for x in items]}


def TABLE(head, *rows):
    return {"t": "table", "rows": [[{"html": c} for c in r] for r in (head, *rows)]}


def H(text):
    return {"t": "h3", "text": text}


def N(id, kind, x, y, text, title=None, tag=None, p=None):
    n = {"id": id, "kind": kind, "x": x, "y": y, "text": text}
    if title:
        n["title"] = title
    if tag:
        n["tag"] = tag
    if p:
        n["p"] = p
    return n


def L(a, b, **fields):
    return {"id": "k_" + a + "_" + b, "from": a, "to": b, **fields}


# ---------- Buổi 4 – Thực hành 5: thay tài khoản dùng chung ----------
KEY_TH5 = {
    "summary": "Bỏ truc_ca, mỗi người một tài khoản cá nhân có MFA. Quyền gán theo nhóm: nhóm Trực ca xem, tạo, cập nhật; "
               "nhóm Trưởng ca có thêm quyền hủy phiếu, phải ghi lý do và có nhật ký. Phiếu giao cho hàng đợi của nhóm "
               "nên một người vắng thì người khác vẫn làm tiếp. Thu hồi phải gồm cả thu hồi phiên và gỡ MFA.",
    "fields": {
        "so_do_tai_khoan": {
            "nodes": [
                N("p1", "person", 42, 80, "Mỗi người một tài khoản riêng (VD: an.nv). MFA trên điện thoại của chính mình."),
                N("p2", "person", 42, 260, "Tài khoản cá nhân, MFA riêng. Nhận ca thì đăng nhập, giao ca thì đăng xuất."),
                N("p3", "person", 42, 440, "Tài khoản cá nhân, MFA riêng. Không biết và không cần mật khẩu của ai khác."),
                N("p_tc", "person", 42, 620, "3 người, mỗi ca 1. Thuộc cả 2 nhóm. Có quyền hủy phiếu nên dùng khóa bảo mật / passkey."),
                N("g1", "group", 442, 80, "Cả 12 người (gồm trưởng ca). Xem, tạo, cập nhật phiếu. Phiếu giao cho hàng đợi của ca, không giao riêng ai.",
                  title="Trực ca"),
                N("g2", "group", 442, 300, "3 trưởng ca. Thêm quyền hủy phiếu: bắt buộc ghi lý do, hệ thống ghi ai hủy, lúc nào. "
                  "Hủy = chuyển trạng thái, không xóa hẳn.", title="Trưởng ca"),
                N("s_ca", "shift", 442, 530, "Phiếu nằm trong hàng đợi chung của nhóm Trực ca → người vắng thì người khác cùng ca mở phiếu "
                  "và xử lý tiếp bằng tài khoản của mình.\nTrưởng ca chuyển phiếu dở sang người khác; hệ thống ghi lại.\n"
                  "Không đưa mật khẩu, không đăng nhập hộ."),
                N("a_phieu", "app", 842, 300, "Đăng nhập qua SSO của Điện lực. Nhật ký ghi tài khoản cá nhân cho mọi lần tạo, sửa, hủy phiếu."),
                N("a_may", "app", 842, 80, "Bỏ đăng nhập chung. Mỗi người đăng nhập tài khoản mình khi nhận ca, đăng xuất khi giao ca; "
                  "tự khóa màn hình sau 5 phút."),
                N("n_bu", "note", 842, 530, "Kiểm soát bù tạm thời: sổ giao ca ghi ai dùng từ mấy giờ đến mấy giờ; đổi mật khẩu khi có "
                  "người rời tổ; kế hoạch nâng cấp có hạn.", title="Nếu phần mềm cũ chưa có nhiều tài khoản"),
                N("x_truc", "shared", 1242, 70, "Rút quyền xóa ngay hôm nay. Khóa truc_ca khi 12 tài khoản cá nhân chạy được; không xóa hẳn "
                  "để giữ nhật ký điều tra 20 phiếu.\nGỡ và hủy tờ giấy mật khẩu, đổi mật khẩu trong thời gian chuyển tiếp.",
                  tag="Vô hiệu hóa"),
                N("x_mfa", "mfa", 1500, 70, "Khớp số chặn bấm nhầm. Không dùng SMS. Ai không có điện thoại thông minh: khóa bảo mật.",
                  tag="Đẩy có khớp số", p={"sso": "Dùng SSO", "ap_dung": "Toàn Điện lực X; quản trị → passkey"}),
                N("l1", "life", 1242, 500, "☐ Có quyết định / phiếu duyệt\n☐ Tạo TK cá nhân, bật MFA\n☐ Gán nhóm theo ma trận\n☐ Trưởng tổ ký xác nhận"),
                N("l2", "life", 1500, 500, "☐ Xuất báo cáo quyền trước\n☐ Gỡ nhóm cũ (VD Trưởng ca)\n☐ Gán nhóm mới theo ma trận\n"
                  "☐ Đăng xuất phiên đang mở\n☐ Xuất báo cáo quyền sau, lưu"),
                N("l3", "life", 1242, 670, "☐ Khóa TK đúng ngày nghỉ\n☐ Thu hồi phiên mọi ứng dụng\n☐ Gỡ MFA, thu khóa bảo mật\n"
                  "☐ Gỡ khỏi nhóm, ghi biên bản\n☐ Kiểm tra lại sau 1 ngày"),
            ],
            "links": [
                L("p1", "g1"), L("p2", "g1"), L("p3", "g1"), L("p_tc", "g1"), L("p_tc", "g2"),
                L("g1", "a_phieu", quyen="Xem, tạo, sửa phiếu"),
                L("g1", "a_may", quyen="Đăng nhập cá nhân"),
                L("g2", "a_phieu", quyen="Hủy phiếu, ghi lý do"),
                L("s_ca", "g1"),
                L("l1", "l2"), L("l2", "l3"),
            ],
        },
        "de_xuat_mfa": (
            "Kính gửi Ban Giám đốc Điện lực X,\n\n"
            "Đề nghị: (1) Trong tháng này, bật MFA dạng thông báo đẩy có khớp số cho toàn bộ tài khoản của Điện lực X, "
            "đăng nhập tập trung qua SSO; bỏ kiểu bấm Chấp nhận / Từ chối và mã OTP qua SMS. "
            "(2) Trong quý tới, chuyển tài khoản quản trị và tài khoản có quyền xuất dữ liệu khách hàng sang passkey / khóa bảo mật; "
            "người không dùng điện thoại thông minh được cấp khóa bảo mật. "
            "(3) Không còn tài khoản dùng chung: mỗi người đăng ký MFA trên thiết bị của chính mình.\n\n"
            "Lý do: MFA kiểu Chấp nhận / Từ chối có thể bị vượt chỉ bằng một cú bấm nhầm; mã SMS có thể bị lừa đọc lại qua điện thoại. "
            "Tháng trước, 20 phiếu ở tổ tổng đài bị xóa mà không truy ra người làm vì cả tổ dùng chung truc_ca đã tắt MFA.\n\n"
            "Đề nghị giao Phòng CNTT thống kê số khóa bảo mật cần mua và báo cáo tiến độ sau 2 tuần."
        ),
    },
    "sections": [
        {"title": "Cách đọc bảng mẫu", "blocks": [
            P("Bảng trên là một bài làm đạt điểm tối đa, dựng bằng đúng các module học viên có. Kéo nền để xem từng vùng; "
              "bấm <b>Xem toàn bộ</b> để thấy cả bảng. Ma trận nhóm quyền × ứng dụng và bản đọc nhanh ở dưới bảng tự lập từ các dây nối."),
            P("Khi chấm, đặt bảng của học viên cạnh bảng này và đối chiếu theo thứ tự: <b>thẻ đỏ truc_ca → dây người–nhóm → "
              "quyền trên dây nhóm–ứng dụng → bài toán ca trực → MFA → vòng đời</b>. Học viên không cần đặt module đúng vị trí "
              "hay viết đúng từng chữ; cần đúng quyết định và đúng cách nối."),
        ]},
        {"title": "Từng module: ghi gì và vì sao", "blocks": [
            TABLE(["Module (vùng)", "Nội dung cần có", "Vì sao – điều cần thấy trong bài học viên"],
                  ["🔓 <b>truc_ca</b> (Tài khoản chung và MFA)",
                   "Chọn <b>Vô hiệu hóa</b>. Rút quyền xóa ngay; khóa tài khoản khi tài khoản cá nhân đã chạy; gỡ và hủy tờ giấy; "
                   "đổi mật khẩu trong thời gian chuyển tiếp.",
                   "Dùng chung thì không truy vết được ai xóa 20 phiếu. Nên <b>vô hiệu hóa, không xóa hẳn</b>: nhật ký cũ gắn với "
                   "truc_ca vẫn cần cho điều tra. Chỉ đổi mật khẩu mà vẫn dùng chung là chưa đạt."],
                  ["👤 <b>Nhân viên ca 1, 2, 3</b> (Người dùng)",
                   "Mỗi người một tài khoản cá nhân, MFA trên thiết bị của mình, đăng nhập khi nhận ca, đăng xuất khi giao ca.",
                   "Ba thẻ “Nhân viên ca” đại diện cho các nhân viên của từng ca, không phải ba tài khoản. Học viên tạo thẻ riêng cho từng người cũng được."],
                  ["👤 <b>Trưởng ca</b>",
                   "Tài khoản cá nhân, thuộc <b>cả hai nhóm</b>. Có quyền cao nên ưu tiên passkey / khóa bảo mật.",
                   "Lý do cũ để tắt MFA là “mã chỉ về điện thoại trưởng ca”. Khi mỗi người có MFA riêng, lý do này không còn."],
                  ["👥 <b>Trực ca</b> (Nhóm quyền 1)",
                   "Cả 12 người. Xem, tạo, cập nhật phiếu; <b>không</b> hủy, xóa. Phiếu giao cho hàng đợi của ca.",
                   "Quyền gán cho nhóm, không gán từng người: thêm, bớt người chỉ cần đổi thành viên nhóm."],
                  ["👥 <b>Trưởng ca</b> (Nhóm quyền 2)",
                   "3 trưởng ca. Thêm quyền hủy phiếu, bắt buộc ghi lý do, có nhật ký; hủy là chuyển trạng thái, không xóa hẳn.",
                   "Tiêu chí “quyền cao tách riêng”. Ghi lý do và xóa mềm giúp lần sau truy được ai hủy, vì sao và khôi phục được."],
                  ["🕒 <b>Bài toán ca trực</b>",
                   "Phiếu ở hàng đợi chung của nhóm; người khác cùng ca mở và xử lý tiếp bằng tài khoản mình; trưởng ca chuyển phiếu; "
                   "không đưa mật khẩu, không đăng nhập hộ.",
                   "Tiêu chí “không gián đoạn khi một người vắng”. Mấu chốt: <b>giao việc cho nhóm</b> chứ không cho chung tài khoản."],
                  ["🖥️ <b>Hệ thống tiếp nhận yêu cầu</b>",
                   "Đăng nhập qua SSO; nhật ký ghi tài khoản cá nhân cho mọi lần tạo, sửa, hủy.",
                   "Đây là nơi phải có nhật ký: truy vết được từng người."],
                  ["🖥️ <b>Máy trực dùng chung</b>",
                   "Giữ máy, bỏ đăng nhập chung. Đăng nhập khi nhận ca, đăng xuất khi giao ca; tự khóa màn hình sau vài phút.",
                   "Dùng chung <b>máy</b> được, dùng chung <b>tài khoản</b> thì không. Khóa màn hình chặn người sau dùng phiên của người trước."],
                  ["🔐 <b>MFA cho toàn Điện lực X</b>",
                   "Loại: <b>Đẩy có khớp số</b> (hoặc Passkey). SSO: <b>Dùng SSO</b>. Áp dụng: toàn Điện lực X; quản trị và quyền xuất "
                   "dữ liệu chuyển sang passkey.",
                   "Đẩy Chấp nhận / Từ chối bị vượt bằng một cú bấm nhầm; SMS bị lừa đọc mã. Phạm vi phải là <b>toàn đơn vị</b>, không chỉ tổ trực."],
                  ["🔁 <b>Cấp mới → Thay vị trí → Thu hồi</b>",
                   "Ba checklist (xem bản đầy đủ ở mục dưới).",
                   "Bước thu hồi phải có <b>thu hồi phiên</b> và <b>gỡ MFA</b>, không chỉ khóa tài khoản."],
                  ["📝 <b>Ghi chú</b> (không bắt buộc)",
                   "Kiểm soát bù nếu phần mềm cũ chưa hỗ trợ nhiều tài khoản.",
                   "Bài có ý này được cộng điểm trình bày: học viên nghĩ tới trường hợp chưa làm được ngay."]),
        ]},
        {"title": "Các dây nối: nối thế nào", "blocks": [
            TABLE(["Dây nối", "Ghi trên dây", "Ý nghĩa"],
                  ["Nhân viên ca 1, 2, 3 → <b>Trực ca</b>", "—", "Mọi nhân viên chỉ thuộc nhóm Trực ca."],
                  ["Trưởng ca → <b>Trực ca</b> và Trưởng ca → <b>Trưởng ca</b>", "—",
                   "Trưởng ca có <b>hai dây</b>: vẫn làm việc trực bình thường và có thêm quyền hủy. Thiếu dây tới Trực ca thì trưởng ca không tạo, cập nhật phiếu được."],
                  ["Trực ca → Hệ thống tiếp nhận yêu cầu", "Xem, tạo, sửa phiếu",
                   "Quyền thường ngày. <b>Không</b> có hủy, xóa."],
                  ["Trực ca → Máy trực dùng chung", "Đăng nhập cá nhân", "Ai trong tổ cũng dùng máy được, mỗi người bằng tài khoản mình."],
                  ["Trưởng ca → Hệ thống tiếp nhận yêu cầu", "Hủy phiếu, ghi lý do",
                   "Quyền cao, chỉ ở nhóm này. Hệ thống bắt nhập lý do và ghi nhật ký ai hủy, lúc nào."],
                  ["Bài toán ca trực → Trực ca", "—", "Cách xử lý người vắng dựa trên hàng đợi của nhóm."],
                  ["Cấp mới → Thay vị trí → Thu hồi", "—", "Dây dựng sẵn, giữ nguyên."]),
            P("<b>Dây không nên có:</b>"),
            UL("Nhân viên ca → nhóm <b>Trưởng ca</b>: cấp quyền hủy cho cả tổ, lặp lại lỗi cũ.",
               "Người dùng nối thẳng tới ứng dụng, bỏ qua nhóm: quay về gán quyền cho từng người, khó thu hồi.",
               "truc_ca nối tới ứng dụng kèm quyền: tài khoản chung vẫn còn được dùng.",
               "Trưởng ca → Máy trực: không sai nhưng thừa, vì trưởng ca đã dùng máy qua nhóm Trực ca."),
            P("<b>Ma trận mong đợi</b> (ở dưới bảng của học viên):"),
            TABLE(["", "Hệ thống tiếp nhận yêu cầu", "Máy trực dùng chung"],
                  ["<b>Trực ca</b>", "Xem, tạo, sửa phiếu", "Đăng nhập cá nhân"],
                  ["<b>Trưởng ca</b>", "Hủy phiếu, ghi lý do", "— (đã có qua nhóm Trực ca)"]),
            P("Ma trận có chữ “xóa” hoặc “hủy” ở dòng Trực ca là bài chưa tách quyền cao."),
        ]},
        {"title": "Checklist vòng đời đầy đủ", "blocks": [
            P("Trên bảng chỉ đủ chỗ cho bản rút gọn. Bản đầy đủ để chữa bài:"),
            TABLE(["Bước", "Việc cần làm", "Ai làm / ai duyệt"],
                  ["<b>Cấp mới</b>",
                   "☐ Có quyết định phân công hoặc phiếu yêu cầu<br>☐ Tạo tài khoản cá nhân, không tạo tài khoản chung<br>"
                   "☐ Bắt buộc đăng ký MFA trước lần dùng đầu tiên<br>☐ Gán nhóm theo ma trận (Trực ca; thêm Trưởng ca nếu được bổ nhiệm)<br>"
                   "☐ Người dùng ký cam kết không chia sẻ tài khoản",
                   "Tổ trưởng đề nghị, trưởng phòng duyệt, CNTT thực hiện"],
                  ["<b>Thay vị trí</b> (VD: nhân viên lên trưởng ca, trưởng ca chuyển phòng)",
                   "☐ Xuất báo cáo quyền hiện có<br>☐ Gỡ nhóm không còn cần<br>☐ Gán nhóm mới theo ma trận<br>"
                   "☐ Đăng xuất các phiên đang mở để quyền mới có hiệu lực<br>☐ Xuất báo cáo quyền sau khi đổi, lưu hồ sơ",
                   "Quản lý cũ xác nhận gỡ, quản lý mới duyệt cấp"],
                  ["<b>Thu hồi</b> (nghỉ việc, điều chuyển hẳn)",
                   "☐ Khóa tài khoản đúng ngày, không chờ cuối tháng<br>☐ <b>Thu hồi phiên</b> trên SSO và từng ứng dụng<br>"
                   "☐ <b>Gỡ phương thức MFA</b>, thu khóa bảo mật hoặc thiết bị<br>☐ Gỡ khỏi mọi nhóm<br>"
                   "☐ Chuyển phiếu đang dở cho người khác<br>☐ Kiểm tra lại sau 1 ngày và ghi biên bản",
                   "Nhân sự báo, CNTT thực hiện, trưởng phòng xác nhận"]),
            P("Lý do phải thu hồi phiên: khóa tài khoản chỉ chặn lần đăng nhập sau. Phiên đang mở (trên máy trực, trên điện thoại) "
              "vẫn dùng được đến khi hết hạn."),
        ]},
        {"title": "Đoạn đề xuất MFA gửi lãnh đạo", "blocks": [
            P("Đoạn mẫu nằm ở ô cuối bài làm mẫu phía trên. Một đoạn đạt cần đủ 4 ý:"),
            OL("<b>Loại MFA</b> cụ thể: khớp số, hoặc passkey cho tài khoản quyền cao. Không chọn SMS hay bấm Chấp nhận.",
               "<b>Phạm vi</b>: toàn bộ tài khoản của Điện lực X, không chỉ tổ tổng đài.",
               "<b>SSO</b>: có hay không, kèm lý do (đăng nhập một nơi, MFA một lần, thu hồi một chỗ).",
               "<b>Lý do và thời hạn</b> viết cho lãnh đạo đọc: rủi ro bấm nhầm, vụ 20 phiếu, làm trong bao lâu, ai thực hiện."),
            P("Chấp nhận nếu học viên ghi “chưa dùng SSO” vì đơn vị chưa triển khai, với điều kiện có MFA trực tiếp trên ứng dụng và "
              "có ghi thu hồi quyền, phiên ở từng ứng dụng."),
        ]},
        {"title": "Phương án khác vẫn đạt", "blocks": [
            UL("Thêm nhóm thứ ba, VD “Giám sát – chỉ xem báo cáo” cho tổ trưởng tổng đài, hoặc “Quản trị (CNTT)” không có quyền nghiệp vụ.",
               "Không cho trưởng ca hủy trực tiếp; nhân viên gửi đề nghị hủy, trưởng ca duyệt (hai người). Chặt hơn đáp án mẫu, cho điểm tối đa.",
               "Chọn <b>Passkey / khóa bảo mật</b> cho toàn đơn vị: đạt, nhưng hỏi thêm lộ trình và chi phí.",
               "Phần mềm cũ không tạo được nhiều tài khoản: chấp nhận giữ truc_ca <b>tạm thời</b> nếu có kiểm soát bù "
               "(sổ giao ca, đổi mật khẩu khi có người rời tổ, bỏ quyền xóa, hạn nâng cấp). Không có hạn nâng cấp thì chưa đạt."),
        ]},
        {"title": "Thang điểm 10", "private": True, "blocks": [
            TABLE(["Tiêu chí", "Điểm", "Đạt đủ khi"],
                  ["truc_ca", "1,5", "Vô hiệu hóa (hoặc giữ tạm có kiểm soát bù và hạn); xử lý tờ giấy; nêu được việc giữ nhật ký."],
                  ["Tài khoản cá nhân và nhóm", "1,5", "Mỗi người nối tới nhóm; trưởng ca thuộc cả hai nhóm; không nối người thẳng tới ứng dụng."],
                  ["Tách quyền cao", "1,5", "Hủy, xóa chỉ ở nhóm Trưởng ca; có ghi lý do hoặc nhật ký. Ma trận không có “xóa” ở dòng Trực ca."],
                  ["Bài toán ca trực", "1,5", "Giao việc cho nhóm hoặc hàng đợi; người khác làm tiếp bằng tài khoản mình. Không đưa mật khẩu, không đăng nhập hộ."],
                  ["MFA và SSO", "1,5", "Khớp số hoặc passkey; quyết định SSO có lý do; phạm vi toàn Điện lực X."],
                  ["Vòng đời", "1,5", "Đủ 3 bước; bước thu hồi có thu hồi phiên và gỡ MFA. Thiếu thu hồi phiên: tối đa 0,75."],
                  ["Đoạn đề xuất", "1,0", "Đủ 4 ý ở mục trên, viết được cho lãnh đạo đọc."]),
            P("Cảnh báo ⚠ trên bảng của học viên là dấu hiệu nhanh: còn cảnh báo nào thì tiêu chí tương ứng chưa đạt."),
        ]},
        {"title": "Lỗi hay gặp và nhận xét gợi ý", "private": True, "blocks": [
            TABLE(["Lỗi", "Dấu hiệu trên bảng", "Câu hỏi hoặc nhận xét gợi ý"],
                  ["Giữ truc_ca, chỉ đổi mật khẩu", "Thẻ đỏ chọn “Giữ nguyên”, có cảnh báo ⚠",
                   "“Lần sau lại có phiếu bị xóa, bạn chỉ ra người xóa bằng cách nào?”"],
                  ["Xóa hẳn truc_ca", "Ghi “xóa tài khoản”", "“Nhật ký 20 phiếu đang gắn với truc_ca. Xóa tài khoản thì còn điều tra được không?”"],
                  ["Quyền hủy cho cả tổ", "Ma trận có “xóa” hoặc “hủy” ở dòng Trực ca, hoặc nhân viên nối tới nhóm Trưởng ca",
                   "“Quyền nào gây ra sự cố tháng trước? Cả 12 người có cần quyền đó không?”"],
                  ["Trưởng ca chỉ thuộc nhóm Trưởng ca", "Trưởng ca có một dây", "“Trưởng ca có tạo, cập nhật phiếu được không?”"],
                  ["Gán quyền từng người", "Người dùng nối thẳng tới ứng dụng", "“Có người mới vào tổ, bạn phải sửa bao nhiêu chỗ?”"],
                  ["Ca trực giải bằng đưa mật khẩu", "Ghi “người trực thay dùng tài khoản của người vắng” hoặc “trưởng ca đăng nhập hộ”",
                   "“Vậy là quay lại dùng chung. Phiếu giao cho ai thì người khác làm tiếp được?”"],
                  ["MFA yếu", "Chọn “Đẩy Chấp nhận / Từ chối” hoặc “Mã OTP qua SMS”, có cảnh báo ⚠",
                   "“Nhớ lại phần mở đầu chương 4: chỉ một cú bấm nhầm là đủ.”"],
                  ["MFA chỉ cho tổ trực", "Ô “Áp dụng cho” ghi tổ tổng đài", "“Đề bài yêu cầu cho toàn Điện lực X.”"],
                  ["Thu hồi chỉ khóa tài khoản", "Thẻ “Thu hồi quyền và phiên” không nhắc phiên, MFA",
                   "“Người đó vẫn đang đăng nhập trên máy trực. Khóa tài khoản có đẩy họ ra không?”"],
                  ["Đề xuất viết như ghi chú kỹ thuật", "Không có lý do, thời hạn, người thực hiện",
                   "“Lãnh đạo đọc xong có biết duyệt gì, đến khi nào, vì sao không?”"]),
        ]},
        {"title": "Gợi ý chữa bài trên lớp (10–15 phút)", "blocks": [
            OL("<b>Đóng</b> bài, mở <b>Xem kết quả</b>, chọn 2 bài khác nhau để chiếu: một bài giữ truc_ca hoặc cho cả tổ quyền hủy, một bài gần đáp án.",
               "Hỏi lớp với bài thứ nhất: “Tháng sau lại mất 20 phiếu. Chúng ta tìm ra ai bằng cách nào?”",
               "Chiếu bảng mẫu này, đi theo thứ tự: truc_ca → dây người–nhóm (nhấn mạnh trưởng ca có 2 dây) → ma trận → ca trực.",
               "Dừng ở thẻ Thu hồi: hỏi “khóa tài khoản xong, phiên trên máy trực còn không?”.",
               "<b>Công bố</b> để học viên xem đáp án gợi ý trong giáo trình, điểm và nhận xét."),
        ]},
    ],
}

ANSWER_KEYS = {
    "m04-th5": KEY_TH5,
}
