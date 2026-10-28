"""Mẫu nộp bài cho từng bài thực hành (theo Phụ lục C của giáo trình).

Mỗi trường (field):
  {"type": "text" | "textarea", "key", "label", "hint"?}
  {"type": "checklist", "key", "label", "items": [...]}
  {"type": "table", "key", "label", "columns": [{"key","label","options"?}],
   "rows": [nhãn dòng cố định] | None, "min_rows": n}
Cột có "options" hiển thị dạng danh sách chọn.
  {"type": "board", "key", "label", "hint"?, "size": [rộng, cao], "kinds": [...], "nodes": [...],
   "zones"?, "links"?, "goals"?, "warnings"?, "summary"?}
  Không gian bảng (static/board.js): học viên kéo module, ghi nội dung và nối các module.
  Vùng có "id" (hàm sz) là vùng phân loại: thả thẻ vào vùng nào thì thẻ thuộc vùng đó.
  Thuộc tính của thẻ (pr): "options" là ô chọn, "multi" là chip chọn nhiều, "table": True chỉ sửa
  trong bảng tổng hợp. "presetLinks" là dây nối có sẵn; "summary" là ma trận hoặc bảng theo thẻ.
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


def pr(key, label, placeholder=None, **extra):
    d = {"key": key, "label": label, **extra}
    if placeholder:
        d["placeholder"] = placeholder
    return d


def kind(k, label, color, icon, hint=None, add=False, **extra):
    d = {"kind": k, "label": label, "color": color, "icon": icon, "add": add, **extra}
    if hint:
        d["hint"] = hint
    return d


def node(id, k, x, y, title=None, hint=None, locked=True):
    d = {"id": id, "kind": k, "x": x, "y": y, "locked": locked}
    if title:
        d["title"] = title
    if hint:
        d["hint"] = hint
    return d


def zone(x, y, w, h, label, color, hint=None):
    d = {"x": x, "y": y, "w": w, "h": h, "label": label, "color": color}
    if hint:
        d["hint"] = hint
    return d


def lf(key, label, placeholder, prefix=None):
    d = {"key": key, "label": label, "placeholder": placeholder}
    if prefix:
        d["prefix"] = prefix
    return d


# Năm nhóm dữ liệu của Thực hành 1, dùng lại ở Thực hành 3
NHOM_TH1 = ["Khách hàng và hợp đồng mua bán điện", "Chỉ số công tơ và báo cáo sản lượng",
            "Vận hành và tài liệu kỹ thuật (sơ đồ lưới, cấu hình thiết bị)", "Thông tin nhân sự",
            "File DS_KhachHang_DLX.xlsx của anh Cường"]
NHOM_TH1_NGAN = ["Khách hàng & hợp đồng", "Chỉ số công tơ & sản lượng", "Vận hành & tài liệu kỹ thuật",
                 "Nhân sự", "File DS_KhachHang_DLX.xlsx"]
GHI_CHU = kind("note", "Ghi chú", "slate", "📝", "Ý tưởng, câu hỏi, điều cần kiểm tra thêm…", add=True)
QUYEN_HIEN_TAI = dict(options=["Giữ nguyên", "Thu hẹp", "Thu hồi"], optionLabel="Quyết định…",
                      tones={"Giữ nguyên": "warn", "Thu hẹp": "info", "Thu hồi": "bad"})

BOARD_TH3 = {
    "type": "board", "key": "ma_tran_bang", "size": [1580, 1000],
    "label": "Không gian ma trận quyền – nối vai trò với thao tác được phép, ghi phạm vi và người duyệt trên từng dây",
    "hint": "Có dây nối nghĩa là có quyền; không nối nghĩa là không có quyền. Bảng ma trận bên dưới tự lập từ các dây nối.",
    "steps": [
        "Ở module 📂 (đầu cột Thao tác), bấm chọn một hay nhiều nhóm trong năm nhóm dữ liệu của Thực hành 1 và ghi nhãn bạn đã chọn.",
        "Với từng vai trò ở cột ① (giữa bảng), ghi ngắn công việc chính cần dữ liệu gì.",
        "Nối vai trò sang thao tác ở cột ② (bên phải) mà vai trò đó thật sự cần. Không cần thì không nối.",
        "Bấm nhãn trên mỗi dây, ghi phạm vi (dữ liệu nào) và người duyệt.",
        "Ở cột ③ (bên trái), viết 3 trường hợp phải bị từ chối và 2 trường hợp phải xin thêm quyền, rồi nối mỗi ô với vai trò liên quan.",
        "Đọc ma trận C3 bên dưới: ô tô vàng là còn thiếu thông tin. Xem lại các gợi ý ⚠ rồi nộp bài.",
    ],
    "zones": [zone(20, 20, 600, 960, "③ Kiểm thử quyền", "red", "Trường hợp phải bị từ chối (trái) và phải xin thêm quyền (phải), nối với vai trò"),
              zone(720, 20, 280, 960, "① Vai trò", "blue", "Năm vai trò trong đề"),
              zone(1280, 20, 280, 960, "② Thao tác", "teal", "Trên nhóm dữ liệu bạn chọn")],
    "kinds": [
        kind("role", "Vai trò", "blue", "👤", "Công việc chính cần dữ liệu gì?", add=True),
        kind("data", "Nhóm dữ liệu", "slate", "📂", "Nhãn đã chọn ở Thực hành 1 và lý do",
             props=[pr("nhom", "Bấm chọn một hay nhiều nhóm", multi=NHOM_TH1_NGAN)]),
        kind("perm", "Thao tác", "teal", "🔑", "Điều kiện chung cho thao tác này (nếu có)"),
        kind("deny", "Phải bị từ chối", "red", "🚫", "Ai – làm gì – vì sao phải chặn", add=True),
        kind("req", "Phải xin thêm quyền", "amber", "✋", "Ai – cần gì – ai duyệt – đến khi nào", add=True),
        GHI_CHU,
    ],
    "nodes": [
        node("r_nv", "role", 742, 80, "Nhân viên nghiệp vụ"),
        node("r_tp", "role", 742, 260, "Trưởng phòng"),
        node("r_tn", "role", 742, 440, "Chuyên viên thu nợ"),
        node("r_cntt", "role", 742, 620, "Cán bộ CNTT hỗ trợ"),
        node("r_qt", "role", 742, 800, "Quản trị hệ thống"),
        node("d_nhom", "data", 1302, 80, "Nhóm dữ liệu đang xét"),
        node("p_xem", "perm", 1302, 410, "Xem"),
        node("p_sua", "perm", 1302, 560, "Sửa"),
        node("p_xuat", "perm", 1302, 710, "Xuất"),
        node("p_cap", "perm", 1302, 860, "Cấp quyền"),
        node("t_1", "deny", 42, 100, "Từ chối 1", locked=False),
        node("t_2", "deny", 42, 300, "Từ chối 2", locked=False),
        node("t_3", "deny", 42, 510, "Từ chối 3", locked=False),
        node("x_1", "req", 362, 100, "Xin thêm 1", locked=False),
        node("x_2", "req", 362, 300, "Xin thêm 2", locked=False),
    ],
    "links": [{"a": "role", "b": "perm", "fields": [lf("pham_vi", "Phạm vi", "VD: KH đơn vị mình"),
                                                      lf("duyet", "Người duyệt", "VD: TP Kinh doanh", "duyệt: ")]}],
    "goals": [
        {"type": "props", "ids": ["d_nhom"], "fields": ["nhom"], "text": "Chọn nhóm dữ liệu đang xét (một hay nhiều nhóm)"},
        {"type": "each", "kind": "role", "to": ["perm"], "text": "Nối mỗi vai trò tới thao tác được phép"},
        {"type": "linkfield", "a": "role", "b": "perm", "fields": ["pham_vi", "duyet"], "text": "Mỗi dây quyền có phạm vi và người duyệt"},
        {"type": "filled", "kind": "deny", "min": 3, "text": "Ít nhất 3 trường hợp phải bị từ chối"},
        {"type": "filled", "kind": "req", "min": 2, "text": "Ít nhất 2 trường hợp phải xin thêm quyền"},
        {"type": "each", "kind": ["deny", "req"], "to": ["role"], "text": "Nối mỗi trường hợp kiểm thử với vai trò liên quan"},
    ],
    "warnings": [
        {"type": "maxIn", "node": "p_xuat", "max": 2, "text": "Nhiều vai trò được Xuất. Vai trò nào thật sự cần mang dữ liệu ra khỏi hệ thống?"},
        {"type": "maxIn", "node": "p_cap", "max": 2, "text": "Nhiều vai trò được Cấp quyền. Ai duyệt và ai thực thi? Một người có tự cấp cho mình được không?"},
        {"type": "pair", "node": "r_cntt", "other": "p_xuat", "text": "Cán bộ CNTT hỗ trợ có cần xuất dữ liệu khách hàng không? Nếu có, theo phiếu nào?"},
        {"type": "pair", "node": "r_qt", "other": "p_xem", "text": "Quản trị hệ thống có cần xem dữ liệu khách hàng thường xuyên không?"},
    ],
    "summary": {"type": "matrix", "rows": "role", "cols": "perm", "title": "Ma trận quyền tự lập từ các dây nối (mẫu C3)",
                "cell": [{"key": "pham_vi"}, {"key": "duyet", "prefix": "duyệt: "}]},
}

BOARD_TH4 = {
    "type": "board", "key": "so_do_xu_ly", "size": [1740, 760],
    "label": "Không gian xử lý tình huống chị Hà – quyết định cho từng quyền, nối các bước theo thứ tự, gắn người phụ trách và bằng chứng",
    "hint": "Xem xét góc nhìn của cả bốn người trước khi chốt phương án. Nối bước trước → bước sau.",
    "steps": [
        "Ở cột Người liên quan, ghi mỗi người muốn gì và lo ngại gì.",
        "Với từng quyền của chị Hà, chọn Giữ nguyên, Thu hẹp hoặc Thu hồi và ghi lý do. Chọn có cấp quyền mới ở Điện lực Y hay chưa.",
        "Viết nội dung cho 5 bước xử lý: làm gì, trên dữ liệu nào, đến khi nào.",
        "Nối các bước thành chuỗi: kéo từ bước trước sang bước sau.",
        "Nối người phụ trách vào từng bước, bấm nhãn trên dây để ghi vai trò (duyệt, thực hiện, xác nhận).",
        "Ghi ít nhất 2 bằng chứng cụ thể, nối mỗi bằng chứng với bước hoặc quyền nó chứng minh.",
        "Viết tóm tắt phương án 3–5 câu ở ô bên dưới bảng rồi nộp bài.",
    ],
    "zones": [zone(20, 20, 280, 720, "Người liên quan", "violet", "Mỗi người muốn gì? Lo ngại gì?"),
              zone(380, 20, 980, 255, "Quyền của chị Hà", "amber", "Quyết định cho từng quyền"),
              zone(380, 295, 980, 445, "Các bước xử lý", "teal", "Nối bước trước → bước sau; nối người phụ trách vào từng bước"),
              zone(1440, 20, 280, 720, "Bằng chứng", "green", "Thứ chứng minh quyền cũ đã được xử lý")],
    "kinds": [
        kind("actor", "Người liên quan", "violet", "👤", "Góc nhìn, mong muốn của người này", add=True),
        kind("right", "Quyền hiện tại", "amber", "🔑", "Phạm vi còn lại (nếu thu hẹp) và lý do", **QUYEN_HIEN_TAI),
        kind("newright", "Quyền mới", "green", "➕", "Cấp theo ma trận quyền nào?",
             options=["Cấp mới", "Chưa cấp"], optionLabel="Quyết định…", tones={"Cấp mới": "ok"}),
        kind("step", "Bước xử lý", "teal", "🧭", "Làm gì, trên dữ liệu nào, đến khi nào", add=True),
        kind("evidence", "Bằng chứng", "green", "📋", "Tài liệu, báo cáo hoặc log cụ thể", add=True),
        GHI_CHU,
    ],
    "nodes": [
        node("a_ha", "actor", 42, 80, "Chị Hà"),
        node("a_tuan", "actor", 42, 245, "Anh Tuấn – quản lý Điện lực X"),
        node("a_y", "actor", 42, 410, "Quản lý phòng Kế hoạch – Điện lực Y"),
        node("a_cntt", "actor", 42, 580, "Cán bộ CNTT"),
        node("q_xem", "right", 402, 80, "Xem toàn bộ khách hàng Điện lực X"),
        node("q_xuat", "right", 752, 80, "Xuất dữ liệu khách hàng Điện lực X"),
        node("q_moi", "newright", 1102, 80, "Vai trò Kế hoạch – Điện lực Y"),
        node("b_nhu_cau", "step", 402, 360, "Xác định nhu cầu bàn giao", "Bàn giao việc gì? Cần xem hay sửa? Đúng những hồ sơ nào?"),
        node("b_duyet", "step", 752, 360, "Phê duyệt ngoại lệ và đặt hạn", "Ai duyệt? Hết hạn ngày nào? Có cách nào không cần ngoại lệ?"),
        node("b_thu_hoi", "step", 1102, 360, "Thu hồi quyền không còn cần", "Gỡ quyền nào, khi nào, ai làm?"),
        node("b_cap_moi", "step", 1102, 560, "Cấp quyền mới ở Điện lực Y", "Vai trò nào, theo ma trận quyền nào?"),
        node("b_kiem_tra", "step", 752, 560, "Kiểm tra lại", "Thử bằng tài khoản chị Hà: thao tác nào phải bị từ chối?"),
        node("e_1", "evidence", 1462, 90, "Bằng chứng 1", locked=False),
        node("e_2", "evidence", 1462, 280, "Bằng chứng 2", locked=False),
    ],
    "links": [{"a": "actor", "b": ["step", "right", "newright"],
               "fields": [lf("viec", "Vai trò trong bước", "VD: duyệt / thực hiện / xác nhận")]},
              {"a": "evidence", "b": ["step", "right", "newright"], "fields": [lf("ghi_chu", "Chứng minh điều gì", "VD: quyền xuất đã gỡ")]}],
    "goals": [
        {"type": "filled", "kind": "actor", "min": 4, "text": "Ghi góc nhìn của cả 4 người"},
        {"type": "tagged", "kind": ["right", "newright"], "text": "Quyết định cho từng quyền của chị Hà"},
        {"type": "filled", "ids": ["b_nhu_cau", "b_duyet", "b_thu_hoi", "b_cap_moi", "b_kiem_tra"], "text": "Viết nội dung cho 5 bước xử lý"},
        {"type": "links", "a": "step", "b": "step", "min": 4, "text": "Nối các bước thành chuỗi theo thứ tự"},
        {"type": "each", "kind": "step", "to": ["actor"], "text": "Mỗi bước có người phụ trách"},
        {"type": "filled", "kind": "evidence", "min": 2, "text": "Ít nhất 2 bằng chứng cụ thể"},
        {"type": "each", "kind": "evidence", "to": ["step", "right", "newright"], "text": "Nối bằng chứng với bước hoặc quyền nó chứng minh"},
    ],
    "warnings": [
        {"type": "tag", "node": "q_xuat", "value": "Giữ nguyên", "text": "Giữ quyền xuất toàn bộ khách hàng Điện lực X chỉ để bàn giao hồ sơ: phạm vi này có quá rộng không?"},
        {"type": "tag", "node": "q_xem", "value": "Giữ nguyên", "text": "Bàn giao 37 hồ sơ có cần xem toàn bộ khách hàng Điện lực X không?"},
    ],
}

BOARD_CASE_M03 = {
    "type": "board", "key": "phuong_an", "size": [1740, 840],
    "label": "Không gian phương án – đi từ trái sang phải: quyền hiện tại → ngoại lệ → người duyệt và cấu hình → bằng chứng → phép thử",
    "hint": "Mỗi phép thử nối với quyền hoặc ngoại lệ mà nó kiểm tra.",
    "steps": [
        "① Với từng quyền hiện tại của chị Hà, chọn Giữ nguyên, Thu hẹp hoặc Thu hồi và ghi lý do.",
        "② Trong module Ngoại lệ, ghi phạm vi hồ sơ, thao tác được làm và ngày giờ hết hạn.",
        "③ Ghi việc của từng người liên quan, nối người duyệt và người cấu hình vào quyền hoặc ngoại lệ; bấm nhãn trên dây để ghi việc.",
        "④ Ghi ít nhất 2 bằng chứng cần lưu (tài liệu, báo cáo, log).",
        "⑤ Viết 3 phép thử bằng tài khoản chị Hà, chọn kết quả mong đợi cho từng phép thử, rồi nối mỗi phép thử với quyền hoặc ngoại lệ nó kiểm tra.",
        "Viết phần giải thích ở ô bên dưới bảng rồi nộp bài.",
    ],
    "zones": [zone(20, 20, 280, 420, "① Quyền hiện tại", "amber"),
              zone(20, 460, 280, 360, "② Ngoại lệ đề xuất", "green"),
              zone(460, 20, 280, 800, "③ Ai duyệt, ai cấu hình", "violet"),
              zone(900, 20, 280, 800, "④ Bằng chứng cần lưu", "slate"),
              zone(1340, 20, 300, 800, "⑤ Ba phép thử", "red")],
    "kinds": [
        kind("right", "Quyền hiện tại", "amber", "🔑", "Lý do quyết định", **QUYEN_HIEN_TAI),
        kind("grant", "Ngoại lệ", "green", "⏳", "Vì sao cần ngoại lệ? Có cách nào không cần không?",
             props=[{"key": "pham_vi", "label": "Phạm vi hồ sơ", "placeholder": "VD: đúng các hồ sơ được giao"},
                    {"key": "thao_tac", "label": "Thao tác", "placeholder": "VD: chỉ xem"},
                    {"key": "het_han", "label": "Hết hạn", "placeholder": "Ngày giờ cụ thể"}]),
        kind("actor", "Người liên quan", "violet", "👤", "Làm gì trong phương án?", add=True),
        kind("evidence", "Bằng chứng", "slate", "📋", "Tài liệu, báo cáo hoặc log cụ thể", add=True),
        kind("test", "Phép thử", "red", "🧪", "Thao tác thử cụ thể bằng tài khoản chị Hà",
             options=["Được phép", "Phải bị từ chối"], optionLabel="Kết quả mong đợi…",
             tones={"Được phép": "ok", "Phải bị từ chối": "bad"}),
        GHI_CHU,
    ],
    "nodes": [
        node("q_xem", "right", 42, 70, "Xem toàn bộ khách hàng Điện lực X"),
        node("q_xuat", "right", 42, 250, "Xuất dữ liệu khách hàng Điện lực X"),
        node("g_ngoai_le", "grant", 42, 510, "Ngoại lệ bàn giao 12 hồ sơ"),
        node("a_chu", "actor", 482, 70, "Chủ dữ liệu"),
        node("a_ql", "actor", 482, 240, "Quản lý Điện lực X"),
        node("a_cntt", "actor", 482, 410, "Cán bộ CNTT"),
        node("a_ha", "actor", 482, 580, "Chị Hà"),
        node("e_1", "evidence", 922, 70, "Bằng chứng 1", locked=False),
        node("e_2", "evidence", 922, 240, "Bằng chứng 2", locked=False),
        node("t_1", "test", 1372, 70, "Phép thử 1 – Trường hợp được phép"),
        node("t_2", "test", 1372, 300, "Phép thử 2 – Truy cập ngoài phạm vi"),
        node("t_3", "test", 1372, 530, "Phép thử 3 – Thao tác xuất"),
    ],
    "links": [{"a": "actor", "b": ["right", "grant", "evidence"], "fields": [lf("viec", "Việc", "VD: duyệt / cấu hình / lưu")]}],
    "goals": [
        {"type": "tagged", "kind": "right", "text": "Quyết định giữ, thu hẹp hay thu hồi cho từng quyền"},
        {"type": "props", "ids": ["g_ngoai_le"], "fields": ["pham_vi", "thao_tac", "het_han"], "text": "Ghi phạm vi, thao tác và ngày hết hạn của ngoại lệ"},
        {"type": "linkfield", "a": "actor", "b": ["right", "grant"], "fields": ["viec"], "min": 2, "text": "Nối người duyệt và người cấu hình vào phương án"},
        {"type": "filled", "kind": "evidence", "min": 2, "text": "Ít nhất 2 bằng chứng cần lưu"},
        {"type": "filled", "kind": "test", "text": "Viết đủ 3 phép thử"},
        {"type": "tagged", "kind": "test", "text": "Ghi kết quả mong đợi cho từng phép thử"},
        {"type": "each", "kind": "test", "to": ["right", "grant"], "text": "Nối mỗi phép thử với quyền hoặc ngoại lệ nó kiểm tra"},
    ],
    "warnings": [
        {"type": "tag", "node": "q_xuat", "value": "Giữ nguyên", "text": "Việc bàn giao 12 hồ sơ có cần quyền xuất toàn bộ khách hàng Điện lực X không?"},
        {"type": "tag", "node": "q_xem", "value": "Giữ nguyên", "text": "Chỉ cần 12 hồ sơ nhưng vẫn giữ quyền xem toàn bộ Điện lực X?"},
    ],
}

def sz(id, x, y, w, h, label, color, hint=None):
    """Vùng phân loại: thả thẻ vào vùng nào thì thẻ thuộc vùng đó."""
    return {**zone(x, y, w, h, label, color, hint), "id": id}


# ---------- Buổi 1 – Thực hành 1: phân loại bằng cách kéo thẻ vào cột nhãn ----------
CIA = ["Thấp", "Trung bình", "Cao"]
BOARD_TH1 = {
    "type": "board", "key": "phan_loai_bang", "size": [1760, 900],
    "label": "Không gian phân loại – kéo từng nhóm dữ liệu vào cột nhãn, đánh giá C / I / A và ghi lý do",
    "hint": "Câu hỏi để chọn nhãn: nếu dữ liệu này lộ ra, bị sửa sai hoặc không dùng được thì sao? Bảng C1 bên dưới tự lập từ bảng.",
    "steps": [
        "Đọc 5 thẻ nhóm dữ liệu ở hàng trên cùng.",
        "Kéo từng thẻ xuống cột nhãn phù hợp: Công khai, Nội bộ, Mật hoặc Hạn chế cao. Cột sáng lên khi thẻ đang ở trong cột.",
        "Trên mỗi thẻ, chọn mức tác động C (bí mật), I (toàn vẹn), A (sẵn sàng) và ghi lý do chọn nhãn.",
        "Ở bảng C1 bên dưới, điền ai được dùng, qua kênh nào và điều kiện dùng AI cho từng nhóm.",
        "Làm xong sớm: thêm thẻ “Mở rộng” cho một trường hợp gộp dữ liệu làm tăng mức và một trường hợp hạ mức sau khi công bố.",
    ],
    "zones": [zone(20, 20, 1720, 250, "Năm nhóm dữ liệu – kéo từng thẻ xuống cột nhãn", "slate"),
              sz("z_ck", 20, 290, 415, 590, "Công khai", "green", "Ai cũng được biết"),
              sz("z_nb", 455, 290, 415, 590, "Nội bộ", "blue", "Chỉ người trong đơn vị"),
              sz("z_mat", 890, 290, 415, 590, "Mật", "amber", "Chỉ người có nhiệm vụ"),
              sz("z_hc", 1325, 290, 415, 590, "Hạn chế cao", "red", "Rất ít người, kiểm soát chặt")],
    "kinds": [
        kind("data", "Nhóm dữ liệu", "violet", "📂", "Lý do chọn nhãn: nếu lộ ra thì sao?", shortProps=True,
             props=[pr("c", "C", "C…", options=CIA), pr("i", "I", "I…", options=CIA), pr("a", "A", "A…", options=CIA),
                    pr("ai_dung", "Ai được dùng, kênh chia sẻ", "VD: CSKH, qua hệ thống", table=True),
                    pr("ai", "Điều kiện dùng AI", "VD: chỉ công cụ đã duyệt, đã bỏ định danh", table=True)]),
        kind("ext", "Mở rộng", "teal", "➕", "Mô tả trường hợp và mức thay đổi", add=True,
             options=["Gộp làm tăng mức", "Hạ mức sau công bố"], optionLabel="Loại trường hợp…"),
        GHI_CHU,
    ],
    "nodes": [
        node("d_kh", "data", 40, 70, NHOM_TH1[0]),
        node("d_cto", "data", 380, 70, NHOM_TH1[1]),
        node("d_vh", "data", 720, 70, NHOM_TH1[2]),
        node("d_ns", "data", 1060, 70, NHOM_TH1[3]),
        node("d_file", "data", 1400, 70, NHOM_TH1[4]),
    ],
    "goals": [
        {"type": "inzone", "kind": "data", "text": "Kéo cả 5 nhóm dữ liệu vào cột nhãn"},
        {"type": "props", "kind": "data", "fields": ["c", "i", "a"], "text": "Đánh giá C, I, A cho từng nhóm"},
        {"type": "text", "kind": "data", "text": "Ghi lý do chọn nhãn trên từng thẻ"},
        {"type": "props", "kind": "data", "fields": ["ai_dung", "ai"], "text": "Điền ai được dùng và điều kiện dùng AI (bảng C1)"},
    ],
    "warnings": [
        {"type": "inzone", "node": "d_vh", "zone": "z_ck", "text": "Sơ đồ lưới và cấu hình thiết bị không có thông tin cá nhân – nhưng nếu lọt ra ngoài thì ai được lợi?"},
        {"type": "inzone", "node": "d_cto", "zone": "z_ck", "text": "Báo cáo sản lượng đã được duyệt công bố chưa? Ở mức chi tiết nào thì nhận ra được một khách hàng lớn?"},
        {"type": "prop", "node": "d_cto", "key": "i", "value": "Thấp", "text": "Nếu chỉ số công tơ bị sửa sai thì hóa đơn và đối soát sẽ ra sao?"},
        {"type": "inzone", "node": "d_file", "zone": "z_ck", "text": "File có danh sách khách hàng của cả Điện lực X. Nếu lọt ra ngoài thì sao?"},
        {"type": "inzone", "node": "d_file", "zone": "z_nb", "text": "File có danh sách khách hàng của cả Điện lực X. Mọi người trong đơn vị đều cần đọc file này không?"},
    ],
    "summary": {"type": "cards", "kind": "data", "title": "Bảng phân loại dữ liệu (mẫu C1) – tự lập từ bảng",
                "hint": "Nhãn lấy theo cột bạn thả thẻ vào. Điền hai cột “Ai được dùng” và “Điều kiện dùng AI” ngay trong bảng này.",
                "cols": [{"key": "title", "label": "Nhóm dữ liệu"}, {"key": "zone", "label": "Nhãn"},
                         {"key": "c", "label": "C"}, {"key": "i", "label": "I"}, {"key": "a", "label": "A"},
                         {"key": "ai_dung", "label": "Ai được dùng, kênh chia sẻ"}, {"key": "ai", "label": "Điều kiện dùng AI"},
                         {"key": "text", "label": "Lý do chọn nhãn"}]},
}

# ---------- Buổi 2 – Thực hành 2: vẽ sơ đồ luồng dữ liệu ----------
BOARD_TH2 = {
    "type": "board", "key": "so_do_luong", "size": [1760, 880],
    "label": "Không gian sơ đồ luồng dữ liệu – vẽ mũi tên giữa các bước, ghi dữ liệu và cách truyền, đánh dấu ranh giới và điểm yếu",
    "hint": "Bốn vùng là bốn nơi dữ liệu nằm. Mũi tên đi từ vùng này sang vùng khác thường là một ranh giới tin cậy.",
    "steps": [
        "Ghi quy trình bạn chọn ở ô phía trên. Các thẻ có sẵn theo quy trình A; chọn quy trình B thì xóa và tự tạo thẻ.",
        "Đặt người, hệ thống, bản sao vào đúng vùng nơi dữ liệu nằm. Thêm thẻ bằng nút “Thêm module”.",
        "Kéo mũi tên theo đường đi của dữ liệu. Bấm nhãn trên mũi tên, ghi dữ liệu gì, truyền bằng cách nào.",
        "Mũi tên nào vượt ranh giới tin cậy (xuất Excel, gửi email, đưa lên cloud hoặc AI) thì ghi số ranh giới.",
        "Ghi mọi bản sao, kể cả bản sao không chính thức (ảnh chụp, file trên Desktop, tin Zalo), và chọn loại cho từng bản.",
        "Thêm ít nhất 3 thẻ “Điểm yếu”, nối với bước liên quan, rồi điền bảng rủi ro C2 bên dưới.",
    ],
    "zones": [zone(20, 20, 300, 840, "① Bên ngoài đơn vị", "violet", "Khách hàng, đối tác"),
              zone(360, 20, 560, 840, "② Hệ thống và bộ phận chính thức", "teal", "Phần mềm, cơ sở dữ liệu, người xử lý"),
              zone(960, 20, 360, 840, "③ Máy cá nhân, file trung gian", "amber", "Excel, Desktop, ảnh chụp"),
              zone(1360, 20, 380, 840, "④ Kênh gửi, nơi lưu ngoài hệ thống", "red", "Email, Zalo, ổ chia sẻ, cloud, AI")],
    "kinds": [
        kind("actor", "Người / bộ phận", "blue", "👤", "Làm gì với dữ liệu ở bước này?", add=True),
        kind("system", "Hệ thống", "teal", "🗄️", "Lưu gì, ai truy cập được?", add=True),
        kind("copy", "Bản sao / kênh", "amber", "📄", "Ở đâu, ai giữ, bao giờ xóa?", add=True,
             options=["Chính thức", "Không chính thức"], optionLabel="Loại bản sao…", tones={"Không chính thức": "warn", "Chính thức": "info"}),
        kind("risk", "Điểm yếu (C2)", "red", "⚠️", "Điểm yếu là gì?", add=True,
             props=[pr("tac_dong", "Tác động nếu xảy ra", table=True), pr("kiem_soat", "Kiểm soát đề xuất", table=True),
                    pr("nguoi", "Người chịu trách nhiệm", table=True), pr("minh_chung", "Minh chứng", table=True)]),
        GHI_CHU,
    ],
    "nodes": [
        node("n_kh", "actor", 42, 90, "Khách hàng", locked=False),
        node("n_td", "actor", 382, 90, "Nhân viên tổng đài / quầy", locked=False),
        node("n_ht", "system", 662, 90, "Hệ thống phiếu yêu cầu", locked=False),
        node("n_nv", "actor", 662, 330, "Nghiệp vụ / hiện trường", locked=False),
        node("n_ld", "actor", 382, 570, "Lãnh đạo", locked=False),
        node("n_xl", "copy", 1002, 330, "Báo cáo Excel cuối tháng", locked=False),
        node("n_os", "copy", 1402, 570, "Ổ chia sẻ", locked=False),
    ],
    "links": [{"a": "risk", "b": "*", "fields": []},
              {"a": "*", "b": "*", "fields": [lf("du_lieu", "Dữ liệu gì", "VD: tên, điện thoại, mã KH"),
                                              lf("cach", "Truyền bằng cách nào", "VD: nhập tay, email, Zalo"),
                                              lf("ranh_gioi", "Ranh giới số (nếu vượt)", "VD: 1", "RG ")]}],
    "goals": [
        {"type": "linkfield", "fields": ["du_lieu", "cach"], "min": 5, "atLeast": True, "text": "Ít nhất 5 mũi tên ghi rõ dữ liệu gì, truyền bằng cách nào"},
        {"type": "linkfield", "fields": ["ranh_gioi"], "min": 2, "atLeast": True, "text": "Đánh số các ranh giới tin cậy trên mũi tên (ít nhất 2)"},
        {"type": "tagged", "kind": "copy", "text": "Chọn loại cho mọi bản sao"},
        {"type": "tagged", "kind": "copy", "value": "Không chính thức", "min": 1, "text": "Tìm ít nhất 1 bản sao không chính thức"},
        {"type": "props", "kind": "risk", "min": 3, "fields": ["tac_dong", "kiem_soat", "nguoi", "minh_chung"], "text": "Ít nhất 3 điểm yếu điền đủ bảng C2"},
        {"type": "each", "kind": "risk", "to": ["actor", "system", "copy"], "text": "Nối mỗi điểm yếu với bước trên sơ đồ"},
    ],
    "warnings": [
        {"type": "propAny", "kind": "risk", "key": "nguoi", "value": "Phòng CNTT", "text": "Mọi điểm yếu đều do phòng CNTT chịu trách nhiệm? Ai là người thực sự làm bước đó?"},
    ],
    "summary": {"type": "cards", "kind": "risk", "title": "Bảng rủi ro luồng dữ liệu (mẫu C2) – tự lập từ bảng",
                "hint": "Mỗi thẻ “Điểm yếu” là một dòng. Điền các cột còn lại ngay trong bảng này.",
                "cols": [{"key": "title", "label": "Điểm yếu"}, {"key": "links", "label": "Bước trên sơ đồ"},
                         {"key": "tac_dong", "label": "Tác động"}, {"key": "kiem_soat", "label": "Kiểm soát đề xuất"},
                         {"key": "nguoi", "label": "Người chịu trách nhiệm"}, {"key": "minh_chung", "label": "Minh chứng"}]},
}

# ---------- Buổi 4 – Thực hành 5: thay tài khoản dùng chung ----------
BOARD_TH5 = {
    "type": "board", "key": "so_do_tai_khoan", "size": [1760, 880],
    "label": "Không gian thiết kế tài khoản – người dùng → nhóm quyền → ứng dụng, quyết định cho truc_ca và MFA, vòng đời tài khoản",
    "hint": "Tổ tổng đài 3 ca, mỗi ca 4 người, đang dùng chung truc_ca; tháng trước 20 phiếu bị xóa mà không biết ai xóa.",
    "steps": [
        "Quyết định làm gì với tài khoản truc_ca (thẻ đỏ) và ghi cách xử lý tờ giấy dán mật khẩu.",
        "Đặt tên và mô tả các nhóm quyền ở cột giữa (đổi tên “Nhóm quyền 1, 2”, thêm nhóm nếu cần).",
        "Nối mỗi người dùng tới nhóm quyền của họ; nối nhóm tới ứng dụng và ghi quyền trên dây (xem, tạo, sửa, xóa…).",
        "Viết cách giải bài toán ca trực: một người vắng thì người khác làm thế nào mà không dùng chung tài khoản.",
        "Chọn loại MFA, quyết định có dùng SSO không, ghi phạm vi áp dụng.",
        "Viết checklist cho 3 bước vòng đời: cấp mới, thay vị trí, thu hồi quyền và phiên. Cuối cùng viết đoạn đề xuất MFA ở ô bên dưới.",
    ],
    "zones": [zone(20, 20, 300, 840, "Người dùng", "blue", "Mỗi người một tài khoản cá nhân"),
              zone(420, 20, 300, 840, "Nhóm quyền", "violet", "Gán quyền cho nhóm, không cho từng người"),
              zone(820, 20, 300, 840, "Ứng dụng", "teal"),
              zone(1220, 20, 520, 400, "Tài khoản chung và MFA", "red"),
              zone(1220, 440, 520, 420, "Vòng đời tài khoản", "green", "Cấp mới → thay vị trí → thu hồi")],
    "kinds": [
        kind("person", "Người dùng", "blue", "👤", "Tài khoản cá nhân, MFA", add=True),
        kind("group", "Nhóm quyền", "violet", "👥", "Gồm những ai, dùng khi nào", add=True),
        kind("app", "Ứng dụng", "teal", "🖥️", "Ghi chú về ứng dụng / máy", add=True),
        kind("shared", "Tài khoản dùng chung", "red", "🔓", "Làm gì với tài khoản và tờ giấy dán mật khẩu?",
             options=["Giữ nguyên", "Vô hiệu hóa"], optionLabel="Quyết định…", tones={"Giữ nguyên": "bad", "Vô hiệu hóa": "ok"}),
        kind("mfa", "Cấu hình MFA", "amber", "🔐", "Vì sao chọn loại này?",
             options=["Đẩy Chấp nhận / Từ chối", "Đẩy có khớp số", "Mã OTP qua SMS", "Ứng dụng tạo mã OTP", "Passkey / khóa bảo mật"],
             optionLabel="Loại MFA…", tones={"Đẩy Chấp nhận / Từ chối": "warn", "Mã OTP qua SMS": "warn"},
             props=[pr("sso", "SSO", "Chọn…", options=["Dùng SSO", "Không dùng SSO"]), pr("ap_dung", "Áp dụng cho", "VD: toàn Điện lực X")]),
        kind("shift", "Bài toán ca trực", "slate", "🕒", "Khi một người vắng, người khác làm việc thế nào?"),
        kind("life", "Bước vòng đời", "green", "🔁", "Checklist: làm gì, ai duyệt, thu hồi phiên thế nào"),
        GHI_CHU,
    ],
    "nodes": [
        node("p1", "person", 42, 80, "Nhân viên ca 1"), node("p2", "person", 42, 250, "Nhân viên ca 2"),
        node("p3", "person", 42, 420, "Nhân viên ca 3"), node("p_tc", "person", 42, 590, "Trưởng ca"),
        node("g1", "group", 442, 80, "Nhóm quyền 1", locked=False), node("g2", "group", 442, 300, "Nhóm quyền 2", locked=False),
        node("s_ca", "shift", 442, 560, "Khi một người vắng"),
        node("a_phieu", "app", 842, 80, "Hệ thống tiếp nhận yêu cầu khách hàng"),
        node("a_may", "app", 842, 300, "Máy trực dùng chung"),
        node("x_truc", "shared", 1242, 70, "truc_ca", "Mật khẩu dán trên màn hình, MFA đã tắt, có quyền xóa phiếu. Bạn làm gì?"),
        node("x_mfa", "mfa", 1500, 70, "MFA cho toàn Điện lực X"),
        node("l1", "life", 1242, 490, "Cấp mới"), node("l2", "life", 1500, 490, "Thay vị trí"),
        node("l3", "life", 1242, 690, "Thu hồi quyền và phiên"),
    ],
    "presetLinks": [["l1", "l2"], ["l2", "l3"]],
    "links": [{"a": "group", "b": "app", "fields": [lf("quyen", "Quyền trên ứng dụng", "VD: xem, tạo, cập nhật phiếu")]}],
    "goals": [
        {"type": "tagged", "ids": ["x_truc"], "text": "Quyết định cho tài khoản truc_ca"},
        {"type": "each", "kind": "person", "to": ["group"], "text": "Nối mỗi người dùng tới nhóm quyền"},
        {"type": "linkfield", "a": "group", "b": "app", "fields": ["quyen"], "min": 2, "text": "Ghi quyền của từng nhóm trên ứng dụng"},
        {"type": "text", "ids": ["s_ca"], "text": "Giải bài toán ca trực"},
        {"type": "tagged", "ids": ["x_mfa"], "text": "Chọn loại MFA"},
        {"type": "props", "ids": ["x_mfa"], "fields": ["sso", "ap_dung"], "text": "Quyết định SSO và phạm vi áp dụng MFA"},
        {"type": "text", "ids": ["l1", "l2", "l3"], "text": "Viết checklist cho 3 bước vòng đời"},
    ],
    "warnings": [
        {"type": "tag", "node": "x_truc", "value": "Giữ nguyên", "text": "Vẫn dùng chung truc_ca thì lần sau phiếu bị xóa có truy ra ai xóa không?"},
        {"type": "tag", "node": "x_mfa", "value": "Đẩy Chấp nhận / Từ chối", "text": "Chỉ một cú bấm nhầm “Chấp nhận” có đủ để kẻ gian vào không?"},
        {"type": "tag", "node": "x_mfa", "value": "Mã OTP qua SMS", "text": "Mã OTP qua SMS có bị kẻ gian gọi điện xin đọc lại được không?"},
    ],
    "summary": {"type": "matrix", "rows": "group", "cols": "app", "title": "Ma trận nhóm quyền × ứng dụng – tự lập từ các dây nối",
                "cell": [{"key": "quyen"}], "none": "—", "empty": "Có (chưa ghi quyền)"},
}

# ---------- Buổi 5 – Thực hành 6: bảo vệ báo cáo trước khi gửi ----------
BOARD_TH6 = {
    "type": "board", "key": "bao_ve_file", "size": [1760, 900],
    "label": "Không gian chuẩn bị file gửi – khảo sát, quyết định giữ / bỏ, bảo vệ, gửi đi, thu hồi",
    "hint": "Đi từ trái sang phải. Người nhận: trưởng phòng Kế hoạch, chỉ cần sản lượng tổng hợp theo vùng.",
    "steps": [
        "① Mở file BaoCao_Thang.xlsx, tìm mọi sheet, kể cả sheet ẩn và cột ẩn. Ghi số sheet, sheet ẩn, cột ẩn vào thẻ file.",
        "Mỗi thứ tìm thấy là một thẻ “Phát hiện” (2 thẻ có sẵn, tự thêm thẻ cho thứ bị ẩn). Chọn loại và ghi trong đó có gì.",
        "② Kéo từng thẻ phát hiện vào vùng “Giữ trong file gửi” hoặc “Bỏ khỏi file gửi”.",
        "③ Ghi cách tạo file mới và kết quả Inspect Document; mã hóa rồi thử mở bằng mật khẩu sai; so sánh với Protect Sheet.",
        "④ Nối “File đã mã hóa” và “Mật khẩu” tới người nhận, bấm nhãn trên dây ghi kênh gửi.",
        "⑤ Ghi kế hoạch thu hồi, lưu giữ: khi nào, ai làm. Sau đó đánh dấu checklist C6 và làm Phần B ở bên dưới.",
    ],
    "zones": [zone(20, 20, 300, 860, "① Khảo sát file", "blue", "Mọi sheet, kể cả sheet ẩn và cột ẩn"),
              sz("z_giu", 360, 20, 300, 420, "② Giữ trong file gửi", "green", "Người nhận cần"),
              sz("z_bo", 360, 460, 300, 420, "Bỏ khỏi file gửi", "red", "Xóa hẳn, không chỉ ẩn"),
              zone(700, 20, 320, 860, "③ Bảo vệ file", "amber"),
              zone(1060, 20, 340, 860, "④ Gửi đi", "teal", "Ghi kênh trên dây nối"),
              zone(1440, 20, 300, 860, "⑤ Thu hồi, lưu giữ", "violet")],
    "kinds": [
        kind("file", "File", "slate", "📊", "Ghi chú khác khi khảo sát",
             props=[pr("so_sheet", "Số sheet"), pr("sheet_an", "Sheet ẩn", "Tên sheet ẩn"), pr("cot_an", "Cột ẩn", "Tên cột ẩn")]),
        kind("find", "Phát hiện", "blue", "🔎", "Trong đó có gì? Người nhận có cần không?", add=True,
             options=["Sheet", "Sheet ẩn", "Cột ẩn", "Công thức liên kết", "Khác"], optionLabel="Loại…",
             tones={"Sheet ẩn": "warn", "Cột ẩn": "warn", "Công thức liên kết": "warn"}),
        kind("step", "Bước bảo vệ", "amber", "🛠️", "Làm thế nào, kết quả ra sao"),
        kind("enc", "Mã hóa", "amber", "🔒", "Cách đặt mật khẩu (cụm từ dài)",
             props=[pr("sai_mk", "Mở bằng mật khẩu sai", "Kết quả…", options=["Bị từ chối", "Vẫn mở được", "Chưa thử"])]),
        kind("cmp", "So sánh", "amber", "⚖️", "Bạn thấy gì khi đóng và mở lại?",
             options=["Vẫn đọc được nội dung", "Không đọc được nội dung"], optionLabel="Kết quả…"),
        kind("send", "Thứ gửi đi", "teal", "📤", "Ghi chú"),
        kind("person", "Người nhận", "violet", "👤", "Tên, chức vụ, địa chỉ email công vụ", add=True),
        kind("keep", "Thu hồi / lưu giữ", "violet", "🗂️", "Làm gì",
             props=[pr("khi", "Khi nào", "VD: ngay sau khi gửi"), pr("ai", "Ai làm / xác nhận")]),
        GHI_CHU,
    ],
    "nodes": [
        node("f_goc", "file", 42, 80, "BaoCao_Thang.xlsx (tháng 10)"),
        node("k_tonghop", "find", 42, 420, "Sheet TongHop"),
        node("k_chitiet", "find", 42, 600, "Sheet ChiTiet"),
        node("n_new", "step", 722, 80, "Tạo file mới chỉ có nội dung cần gửi", "Dán giá trị? Kết quả Inspect Document?"),
        node("n_enc", "enc", 722, 280, "Encrypt with Password"),
        node("n_cmp", "cmp", 722, 520, "Thử Protect Sheet trên một bản sao"),
        node("s_file", "send", 1082, 80, "File đã mã hóa"),
        node("s_pw", "send", 1082, 290, "Mật khẩu"),
        node("r_tp", "person", 1150, 560, "Trưởng phòng Kế hoạch"),
        node("t_tg", "keep", 1462, 80, "Xóa file trung gian trên máy"),
        node("t_goc", "keep", 1462, 340, "Nơi để file gốc"),
        node("t_xn", "keep", 1462, 600, "Người nhận xác nhận đã nhận"),
    ],
    "links": [{"a": "send", "b": "person", "fields": [lf("kenh", "Kênh", "VD: email công vụ / điện thoại nội bộ")]}],
    "goals": [
        {"type": "props", "ids": ["f_goc"], "fields": ["so_sheet", "sheet_an", "cot_an"], "text": "Ghi kết quả khảo sát file"},
        {"type": "filled", "kind": "find", "min": 4, "text": "Ít nhất 4 phát hiện, kể cả thứ bị ẩn"},
        {"type": "inzone", "kind": "find", "zones": ["z_giu", "z_bo"], "text": "Xếp mọi phát hiện vào Giữ hoặc Bỏ"},
        {"type": "text", "ids": ["n_new"], "text": "Ghi cách tạo file mới và kết quả Inspect Document"},
        {"type": "props", "ids": ["n_enc"], "fields": ["sai_mk"], "text": "Thử mở file bằng mật khẩu sai"},
        {"type": "tagged", "ids": ["n_cmp"], "text": "So sánh với Protect Sheet"},
        {"type": "linkfield", "a": "send", "b": "person", "fields": ["kenh"], "min": 2, "text": "Ghi kênh gửi file và kênh báo mật khẩu"},
        {"type": "props", "kind": "keep", "fields": ["khi", "ai"], "text": "Kế hoạch thu hồi, lưu giữ có thời điểm và người làm"},
    ],
    "warnings": [
        {"type": "inzone", "node": "k_chitiet", "zone": "z_giu", "text": "Trưởng phòng Kế hoạch cần sản lượng theo vùng – có cần dữ liệu từng hộ không?"},
        {"type": "samefield", "from": ["s_file", "s_pw"], "to": "r_tp", "field": "kenh", "text": "Mật khẩu đi cùng kênh với file: ai đọc được kênh đó là mở được file."},
        {"type": "tag", "node": "n_cmp", "value": "Không đọc được nội dung", "text": "Bạn đã đóng file và mở lại để thử chưa? Protect Sheet khóa việc sửa hay mã hóa nội dung?"},
        {"type": "prop", "node": "n_enc", "key": "sai_mk", "value": "Vẫn mở được", "text": "File vẫn mở được bằng mật khẩu sai – kiểm tra lại: đã dùng Encrypt with Password chưa?"},
    ],
    "summary": {"type": "cards", "kind": "find", "sort": "zone", "title": "Khảo sát và quyết định nội dung file gửi",
                "cols": [{"key": "title", "label": "Phát hiện"}, {"key": "tag", "label": "Loại"},
                         {"key": "zone", "label": "Quyết định"}, {"key": "text", "label": "Trong đó có gì"}]},
}

# ---------- Buổi 6 – Thực hành 7: chuẩn bị dữ liệu cho phân tích và AI ----------
COT_TH7 = ["ma_kh", "ho_ten", "dien_thoai", "dia_chi", "phuong", "loai_kh", "thang", "kwh", "so_tien_no"]
BOARD_TH7 = {
    "type": "board", "key": "chuan_bi_du_lieu", "size": [1760, 1000],
    "label": "Không gian chuẩn bị dữ liệu – xếp 9 cột vào 4 loại, ghi kết quả kiểm tra nhận diện, quyết định bản nào được giao",
    "hint": "File DLX_SanLuong_Q3.csv: 737 khách hàng × 3 tháng. Anh Minh cần dự báo nhu cầu điện theo phường trên môi trường AI thử nghiệm.",
    "steps": [
        "Kéo từng cột trong hàng trên cùng xuống 1 trong 4 loại: định danh trực tiếp, định danh gián tiếp, thuộc tính nhạy cảm, dữ liệu phân tích.",
        "Ở bảng bên dưới, ghi anh Minh cần hay không, cách xử lý (giữ, bỏ, biến đổi) và lý do cho từng cột.",
        "Tạo bản che từng dòng và bản tổng hợp theo phường bằng Excel (công thức, PivotTable – bước 3–7 của bài).",
        "Ghi kết quả bốn phép kiểm tra nhận diện cho cả hai bản ở bảng thứ hai.",
        "Ở vùng “Quyết định giao”, chọn quyết định cho từng bản. Thêm người duyệt / xác nhận (đặt ở cột bên phải vùng), nối tới bản liên quan, ghi họ duyệt gì.",
        "Điền phiếu yêu cầu dữ liệu C7 và viết đoạn đề xuất gửi anh Tuấn ở bên dưới.",
    ],
    "zones": [zone(20, 20, 1125, 330, "9 cột của file – kéo từng cột xuống loại phù hợp", "slate"),
              sz("z_dd", 20, 370, 270, 610, "Định danh trực tiếp", "red", "Chỉ ra ngay một người"),
              sz("z_gt", 305, 370, 270, 610, "Định danh gián tiếp", "amber", "Ghép lại thì nhận ra người"),
              sz("z_nc", 590, 370, 270, 610, "Thuộc tính nhạy cảm", "violet", "Lộ ra thì ảnh hưởng tới người đó"),
              sz("z_pt", 875, 370, 270, 610, "Dữ liệu phân tích", "green", "Phục vụ mục đích dự báo"),
              zone(1170, 20, 570, 250, "Bốn phép kiểm tra nhận diện", "blue", "Ghi kết quả ở bảng bên dưới"),
              zone(1170, 290, 570, 690, "Quyết định giao", "teal", "Bản nào được đưa vào AI thử nghiệm? Ai duyệt, xác nhận gì?")],
    "kinds": [
        kind("col", "Cột", "slate", "🧩", notext=True,
             props=[pr("can", "Anh Minh cần?", options=["Cần", "Không cần"], table=True),
                    pr("xu_ly", "Xử lý", options=["Giữ", "Bỏ", "Biến đổi"], table=True),
                    pr("ly_do", "Vì sao", "Lý do", table=True)]),
        kind("check", "Phép kiểm tra", "blue", "🔍", notext=True,
             props=[pr("ban_th", "Bản tổng hợp", "Kết quả", table=True), pr("ban_che", "Bản che từng dòng", "Kết quả", table=True)]),
        kind("ver", "Bản dữ liệu", "teal", "📦", "Lý do quyết định",
             options=["Đưa vào AI thử nghiệm", "Chưa – cần xử lý thêm", "Không đưa"], optionLabel="Quyết định…",
             tones={"Đưa vào AI thử nghiệm": "ok", "Chưa – cần xử lý thêm": "warn", "Không đưa": "bad"}),
        kind("actor", "Người duyệt / xác nhận", "violet", "👤", "Vai trò của người này", add=True),
        GHI_CHU,
    ],
    "nodes": [node("c_" + c, "col", 40 + (i % 4) * 272, 70 + (i // 4) * 90, c) for i, c in enumerate(COT_TH7)] + [
        node("k1", "check", 1192, 70, "Nhóm nhỏ"), node("k2", "check", 1470, 70, "Ngoại lai"),
        node("k3", "check", 1192, 160, "Áp đảo"), node("k4", "check", 1470, 160, "Phép trừ giữa các bảng"),
        node("v_th", "ver", 1192, 360, "Bản tổng hợp theo phường × tháng"),
        node("v_che", "ver", 1192, 620, "Bản che từng dòng"),
    ],
    "links": [{"a": "actor", "b": "ver", "fields": [lf("viec", "Duyệt / xác nhận gì", "VD: duyệt file thật")]}],
    "goals": [
        {"type": "inzone", "kind": "col", "text": "Xếp cả 9 cột vào 4 loại"},
        {"type": "props", "kind": "col", "fields": ["can", "xu_ly"], "text": "Ghi anh Minh cần hay không và cách xử lý từng cột"},
        {"type": "props", "kind": "col", "fields": ["ly_do"], "text": "Ghi lý do cho từng cột"},
        {"type": "props", "kind": "check", "fields": ["ban_th", "ban_che"], "text": "Ghi kết quả bốn phép kiểm tra cho cả hai bản"},
        {"type": "tagged", "kind": "ver", "text": "Quyết định cho từng bản"},
        {"type": "linkfield", "a": "actor", "b": "ver", "fields": ["viec"], "min": 2, "atLeast": True, "text": "Nối ít nhất 2 người duyệt / xác nhận"},
    ],
    "warnings": [
        {"type": "inzone", "node": "c_ho_ten", "zone": "z_pt", "text": "Họ tên có phục vụ dự báo nhu cầu theo phường không?"},
        {"type": "prop", "node": "c_dien_thoai", "key": "xu_ly", "value": "Giữ", "text": "Dự báo nhu cầu theo phường có cần số điện thoại không?"},
        {"type": "prop", "node": "c_so_tien_no", "key": "xu_ly", "value": "Giữ", "text": "Số tiền nợ có nằm trong mục đích dự báo nhu cầu điện không?"},
        {"type": "tag", "node": "v_che", "value": "Đưa vào AI thử nghiệm", "text": "Bản che từng dòng vẫn là từng khách hàng một – bốn phép kiểm tra nói gì về bản này?"},
    ],
    "summary": [
        {"type": "cards", "kind": "col", "sort": "zone", "title": "Bảng phân loại cột và so sánh đầu vào – đầu ra",
         "cols": [{"key": "title", "label": "Cột"}, {"key": "zone", "label": "Loại trường"}, {"key": "can", "label": "Anh Minh cần?"},
                  {"key": "xu_ly", "label": "Xử lý"}, {"key": "ly_do", "label": "Vì sao"}]},
        {"type": "cards", "kind": "check", "title": "Kết quả bốn phép kiểm tra nhận diện",
         "cols": [{"key": "title", "label": "Phép kiểm tra"}, {"key": "ban_th", "label": "Bản tổng hợp"}, {"key": "ban_che", "label": "Bản che từng dòng"}]},
    ],
}

# ---------- Buổi 7 – Thực hành 8: kiểm thử RLS ----------
BOARD_TH8 = {
    "type": "board", "key": "kiem_thu_rls", "size": [1760, 880],
    "label": "Không gian kiểm thử RLS – nối tài khoản thử → role → dữ liệu thấy được, ghi kỳ vọng và thực tế",
    "hint": "Thử cả trường hợp được phép và bị từ chối. Số kiểm tra nhanh: DV_A 826.436 kWh, DV_B 742.030 kWh, cả hai 1.568.466 kWh.",
    "steps": [
        "Nối mỗi tài khoản thử tới role RLS được gán (tài khoản không gán role thì không nối).",
        "Nối role tới đơn vị dữ liệu mà role cho xem, ghi quy tắc lọc trên dây.",
        "Chọn vai trò workspace cho từng tài khoản. Thêm ít nhất 1 tài khoản thử nữa (VD: tài khoản Member, người trong bảng PhanQuyen).",
        "Ở bảng C8 bên dưới, ghi kỳ vọng thấy, thực tế thấy và kết quả Đạt / Không đạt cho từng tài khoản.",
        "Ở vùng bên phải, viết 4 bước xử lý tình huống chia sẻ nhầm báo cáo ra ngoài. Trả lời câu hỏi về slicer ở ô bên dưới.",
    ],
    "zones": [zone(20, 20, 320, 840, "Tài khoản thử", "blue", "Ghi kỳ vọng, thực tế, đạt ở bảng C8 bên dưới"),
              zone(420, 20, 300, 840, "Role RLS", "violet"),
              zone(800, 20, 300, 840, "Dữ liệu thấy được", "green"),
              zone(1180, 20, 560, 840, "Chia sẻ nhầm báo cáo ra ngoài", "red", "Ai phát hiện → báo ai → làm gì trước → làm gì sau")],
    "kinds": [
        kind("acc", "Tài khoản thử", "blue", "🧪", "Ghi chú: ai, thử ở Desktop hay service", add=True,
             props=[pr("ws", "Vai trò workspace", "Chọn…", options=["Viewer", "Qua App", "Contributor", "Member", "Admin", "Không có"]),
                    pr("ky_vong", "Kỳ vọng thấy", "VD: chỉ DV_A", table=True), pr("thuc_te", "Thực tế thấy", "VD: 826.436 kWh", table=True),
                    pr("dat", "Đạt", options=["Đạt", "Không đạt", "Chưa thử"], table=True)]),
        kind("role", "Role RLS", "violet", "🛡️", "Bảng và điều kiện lọc", add=True),
        kind("data", "Đơn vị dữ liệu", "green", "🏢", "Tổng kWh quý III thấy được"),
        kind("step", "Bước xử lý", "red", "🚨", "Làm gì, ai làm"),
        GHI_CHU,
    ],
    "nodes": [
        node("a_A", "acc", 42, 80, "nguoixem_A"), node("a_B", "acc", 42, 300, "nguoixem_B"),
        node("a_none", "acc", 42, 520, "khong_gan (không gán role)"),
        node("r_A", "role", 442, 80, "DonVi_A"), node("r_B", "role", 442, 260, "DonVi_B"),
        node("r_dyn", "role", 442, 440, "NguoiXem (RLS động)"),
        node("d_X", "data", 822, 80, "Điện lực X (DV_A)"), node("d_Y", "data", 822, 300, "Điện lực Y (DV_B)"),
        node("c1", "step", 1210, 80, "Ai phát hiện"), node("c2", "step", 1480, 80, "Báo ai"),
        node("c3", "step", 1210, 360, "Làm gì trước"), node("c4", "step", 1480, 360, "Làm gì sau"),
    ],
    "presetLinks": [["c1", "c2"], ["c2", "c3"], ["c3", "c4"]],
    "links": [{"a": "role", "b": "data", "fields": [lf("quy_tac", "Quy tắc lọc", "VD: [MaDonVi] = \"DV_A\"")]}],
    "goals": [
        {"type": "links", "a": "acc", "b": "role", "min": 2, "text": "Nối tài khoản thử tới role được gán"},
        {"type": "linkfield", "a": "role", "b": "data", "fields": ["quy_tac"], "min": 2, "atLeast": True, "text": "Nối role tới dữ liệu, ghi quy tắc lọc"},
        {"type": "props", "kind": "acc", "fields": ["ws"], "text": "Chọn vai trò workspace cho từng tài khoản"},
        {"type": "props", "kind": "acc", "fields": ["ky_vong", "thuc_te", "dat"], "min": 4, "text": "Ít nhất 4 tài khoản có kỳ vọng, thực tế, kết quả (bảng C8)"},
        {"type": "text", "ids": ["c1", "c2", "c3", "c4"], "text": "Viết 4 bước xử lý chia sẻ nhầm"},
    ],
    "warnings": [
        {"type": "propAny", "kind": "acc", "key": "ws", "value": "Member", "text": "RLS có áp cho Member, Contributor, Admin của workspace không? Chỉ kiểm thử trên service mới thấy được."},
        {"type": "pair", "node": "a_none", "other": "r_A", "text": "khong_gan là tài khoản chưa được gán role – vì sao lại nối tới DonVi_A?"},
    ],
    "summary": {"type": "cards", "kind": "acc", "title": "Ma trận kiểm thử RLS (mẫu C8) – tự lập từ bảng",
                "hint": "Role lấy theo dây nối; điền kỳ vọng, thực tế và kết quả ngay trong bảng.",
                "cols": [{"key": "title", "label": "Tài khoản thử"}, {"key": "links", "label": "Role RLS"}, {"key": "ws", "label": "Vai trò workspace"},
                         {"key": "ky_vong", "label": "Kỳ vọng thấy"}, {"key": "thuc_te", "label": "Thực tế thấy"}, {"key": "dat", "label": "Đạt"}]},
}

# ---------- Buổi 8 – Thực hành 9: bốn yêu cầu cần xác minh ----------
TINH_HUONG_TH9 = ["1. “Lãnh đạo” nhắn Zalo xin danh sách", "2. “Nhà cung cấp” gửi file đòi Enable Content",
                  "3. Poster QR “đăng nhập lại”", "4. “CNTT” nhắn Zalo dặn bấm Chấp nhận MFA"]
BUOC_TH9 = [("stop", 380), ("verify", 720), ("report", 1060), ("act", 1400)]
BOARD_TH9 = {
    "type": "board", "key": "xu_ly_yeu_cau", "size": [1760, 1060],
    "label": "Không gian xử lý bốn yêu cầu – mỗi hàng một tình huống, đi qua quy trình 4 bước",
    "hint": "Không cần đoán thật hay giả. Cả bốn tình huống giải quyết bằng cùng một quy trình.",
    "steps": [
        "Đọc tình huống ở đầu mỗi hàng (đề bài trong giáo trình).",
        "Trên thẻ tình huống, bấm chọn các đòn tâm lý kẻ gian dùng (mượn uy quyền, tạo khẩn cấp, chặn kênh xác minh, tạo quen thuộc) và ghi các dấu hiệu nghi ngờ.",
        "Đi theo mũi tên, viết hành động cho từng bước: tạm dừng, xác minh độc lập (kênh cụ thể), báo đầu mối (bằng chứng cần giữ), thực hiện khi rõ.",
        "Ở bước 4, viết thêm một câu từ chối lịch sự cho tình huống đó.",
    ],
    "zones": [zone(20, 20 + i * 260, 1720, 250, t, ["red", "amber", "violet", "blue"][i]) for i, t in enumerate(TINH_HUONG_TH9)],
    "kinds": [
        kind("case", "Tình huống", "red", "📨", "Dấu hiệu nghi ngờ: người gửi, yêu cầu, áp lực, liên kết, file…",
             props=[pr("don", "Đòn tâm lý", multi=["Uy quyền", "Khẩn cấp", "Chặn xác minh", "Quen thuộc"])]),
        kind("stop", "1. Tạm dừng", "slate", "✋", "Dừng tay, chụp lại gì; không làm gì"),
        kind("verify", "2. Xác minh độc lập", "blue", "☎️", "Kênh cụ thể: gọi số nào, gặp ai"),
        kind("report", "3. Báo đầu mối", "amber", "📣", "Báo ai, qua kênh nào, giữ bằng chứng gì"),
        kind("act", "4. Thực hiện khi rõ", "green", "✅", "Làm gì khi đã rõ + câu từ chối lịch sự"),
        GHI_CHU,
    ],
    "nodes": [n for i, t in enumerate(TINH_HUONG_TH9) for n in
              [node(f"h{i + 1}", "case", 40, 52 + i * 260, t.split(" ", 1)[1])] +
              [node(f"h{i + 1}_{k}", k, x, 70 + i * 260) for k, x in BUOC_TH9]],
    "presetLinks": [l for i in range(1, 5) for l in
                    [[f"h{i}", f"h{i}_stop"], [f"h{i}_stop", f"h{i}_verify"], [f"h{i}_verify", f"h{i}_report"], [f"h{i}_report", f"h{i}_act"]]],
    "goals": [
        {"type": "props", "kind": "case", "fields": ["don"], "text": "Gọi tên đòn tâm lý cho cả 4 tình huống"},
        {"type": "text", "kind": "case", "text": "Ghi dấu hiệu nghi ngờ của từng tình huống"},
        {"type": "text", "kind": "stop", "text": "Bước 1 – tạm dừng (4 tình huống)"},
        {"type": "text", "kind": "verify", "text": "Bước 2 – kênh xác minh độc lập (4 tình huống)"},
        {"type": "text", "kind": "report", "text": "Bước 3 – báo ai, giữ bằng chứng gì (4 tình huống)"},
        {"type": "text", "kind": "act", "text": "Bước 4 – hành động và câu từ chối (4 tình huống)"},
    ],
}

# ---------- Buổi 9 – Thực hành 10: truy vết truy cập bất thường ----------
BOARD_TH10 = {
    "type": "board", "key": "truy_vet", "size": [1760, 1020],
    "label": "Không gian truy vết – dựng dòng thời gian từ log, tách điều đã biết với giả thuyết, nối với việc hẹn sửa sau",
    "hint": "Quy tắc: không kết luận một người cụ thể làm lộ dữ liệu chỉ từ tên tài khoản hoặc một lần xuất file.",
    "steps": [
        "Đổi giờ UTC trong log sang +07:00. Mỗi sự kiện đáng chú ý là một thẻ ở dòng thời gian (5 thẻ có sẵn, thêm nếu cần).",
        "Ghi giờ, tài khoản / IP, mô tả sự kiện và chọn nhận định: bình thường, bất thường, cần xem thêm. Giữ mũi tên theo đúng thứ tự thời gian.",
        "Ở 4 cột bên dưới, thêm thẻ: Đã biết (từ log), Chưa biết, Giả thuyết (ít nhất 3), Bằng chứng cần thêm.",
        "Nối mỗi giả thuyết với bằng chứng cần thêm để kiểm tra nó; ghi ai cung cấp bằng chứng.",
        "Thêm hành động tiếp theo trong phạm vi thẩm quyền của bạn.",
        "Vòng 2: thêm thẻ “Việc hẹn sửa sau”, nối sự kiện bất thường tới thẻ đó và ghi vì sao sự kiện thành công.",
    ],
    "zones": [zone(20, 20, 1720, 300, "Diễn biến theo thời gian (giờ +07:00)", "blue", "Mỗi thẻ một sự kiện; nối theo thứ tự thời gian"),
              zone(20, 340, 300, 660, "Đã biết (từ log)", "green"),
              zone(340, 340, 300, 660, "Chưa biết", "slate"),
              zone(660, 340, 300, 660, "Giả thuyết", "amber"),
              zone(980, 340, 300, 660, "Bằng chứng cần thêm", "violet"),
              zone(1300, 340, 440, 310, "Hành động tiếp theo", "teal", "Trong phạm vi thẩm quyền của bạn"),
              zone(1300, 670, 440, 330, "Việc hẹn sửa sau (vòng 2)", "red", "Nối dòng log bất thường với mục trên tờ")],
    "kinds": [
        kind("event", "Sự kiện", "blue", "🕒", "Sự kiện gì", add=True, shortProps=True,
             options=["Bình thường", "Bất thường", "Cần xem thêm"], optionLabel="Nhận định…",
             tones={"Bình thường": "ok", "Bất thường": "bad", "Cần xem thêm": "warn"},
             props=[pr("gio", "Giờ (+07:00)", "21/10 02:10"), pr("tk", "Tài khoản / IP", "nv_c / IP")]),
        kind("fact", "Đã biết", "green", "✔️", "Quan sát từ log, không suy đoán", add=True),
        kind("unknown", "Chưa biết", "slate", "❓", "Điều log chưa trả lời được", add=True),
        kind("hypo", "Giả thuyết", "amber", "💡", "Có thể đã xảy ra điều gì?", add=True),
        kind("need", "Bằng chứng cần thêm", "violet", "📎", "Cần gì để kiểm tra", add=True,
             props=[pr("ai", "Ai cung cấp", "VD: CNTT, tổng đài")]),
        kind("action", "Hành động", "teal", "▶️", "Làm gì, ai quyết", add=True),
        kind("fix", "Việc hẹn sửa sau", "red", "🧾", "Mục nào trên tờ, chương nào", add=True),
        GHI_CHU,
    ],
    "nodes": [node(f"e{i + 1}", "event", 40 + i * 340, 80, f"Sự kiện {i + 1}", locked=False) for i in range(5)] + [
        node("f1", "fact", 42, 400, "Đã biết 1", locked=False), node("u1", "unknown", 362, 400, "Chưa biết 1", locked=False),
        node("h1", "hypo", 682, 400, "Giả thuyết 1", locked=False), node("b1", "need", 1002, 400, "Bằng chứng 1", locked=False),
        node("x1", "action", 1322, 400, "Hành động 1", locked=False), node("v1", "fix", 1322, 730, "Việc hẹn sửa 1", locked=False),
    ],
    "presetLinks": [[f"e{i}", f"e{i + 1}"] for i in range(1, 5)],
    "links": [{"a": "event", "b": "fix", "fields": [lf("vi_sao", "Vì sao thành công", "VD: mật khẩu cũ chưa đổi")]}],
    "goals": [
        {"type": "props", "kind": "event", "fields": ["gio", "tk"], "min": 5, "text": "Ít nhất 5 sự kiện có giờ +07:00 và tài khoản / IP"},
        {"type": "tagged", "kind": "event", "text": "Nhận định từng sự kiện"},
        {"type": "links", "a": "event", "b": "event", "min": 4, "text": "Nối các sự kiện theo thứ tự thời gian"},
        {"type": "filled", "kind": "fact", "min": 2, "text": "Ít nhất 2 điều đã biết"},
        {"type": "filled", "kind": "unknown", "min": 2, "text": "Ít nhất 2 điều chưa biết"},
        {"type": "filled", "kind": "hypo", "min": 3, "text": "Ít nhất 3 giả thuyết"},
        {"type": "each", "kind": "hypo", "to": ["need"], "text": "Mỗi giả thuyết có bằng chứng cần thêm"},
        {"type": "filled", "kind": "action", "min": 2, "text": "Ít nhất 2 hành động tiếp theo"},
        {"type": "linkfield", "a": "event", "b": "fix", "fields": ["vi_sao"], "min": 3, "atLeast": True, "text": "(Vòng 2) Nối ít nhất 3 sự kiện với việc hẹn sửa sau"},
    ],
    "warnings": [
        {"type": "propRe", "kind": "event", "key": "gio", "re": "Z$|UTC|T\\d", "text": "Giờ trong log là UTC – bạn đã đổi sang +07:00 chưa?"},
    ],
    "summary": {"type": "cards", "kind": "event", "sort": "x", "title": "Diễn biến theo thời gian – tự lập theo thứ tự trên bảng",
                "cols": [{"key": "gio", "label": "Giờ (+07:00)"}, {"key": "tk", "label": "Tài khoản / IP"},
                         {"key": "title", "label": "Sự kiện"}, {"key": "text", "label": "Mô tả"}, {"key": "tag", "label": "Nhận định"}]},
}

# ---------- Buổi 10 – Thực hành 11: diễn tập trên bàn ----------
DOT_TH11 = [("Đợt 1 · Phát hiện", "09:00 21/10 · đã qua 0,2 giờ"), ("Đợt 2 · Ngăn chặn", "10:20 · đã qua 1,5 giờ"),
            ("Đợt 3 · Phạm vi", "Phạm vi, bằng chứng · 11:15 · đã qua 2,4 giờ"), ("Đợt 4 · Báo cáo", "Báo cáo, truyền thông · 14:00 · đã qua 5,2 giờ"),
            ("Đợt 5 · Phục hồi", "09:00 23/10 · đã qua 48,2 giờ")]
VAI_TH11 = ["Điều phối – chị Lan (ATTT)", "Kỹ thuật – anh Phong (CNTT)", "Nghiệp vụ – anh Tuấn (chủ dữ liệu)",
            "Lãnh đạo – ông Hưng (PGĐ)", "Pháp chế – chị Ngọc", "Truyền thông – anh Khoa", "Thư ký"]
BOARD_TH11 = {
    "type": "board", "key": "dien_tap", "size": [1760, 900],
    "label": "Không gian diễn tập – mỗi đợt một cột quyết định; nối vai quyết (A) và vai làm (R) vào từng quyết định",
    "hint": "Mỗi quyết định ghi đủ bốn ý: giờ (theo câu chuyện), ai quyết, ai làm, căn cứ. Đồng hồ 72 giờ ghi ở đầu mỗi cột.",
    "steps": [
        "Đọc sáu vai ở cột trái và thông tin chỉ vai đó biết (đề bài trong giáo trình).",
        "Mỗi đợt, ghi quyết định vào thẻ trong cột của đợt đó (thêm thẻ “Quyết định” nếu cần, kéo vào đúng cột).",
        "Trên thẻ, ghi giờ theo câu chuyện và căn cứ. Nối vai quyết và vai làm tới thẻ, ghi A hoặc R trên dây.",
        "Bảng biên bản bên dưới tự xếp quyết định theo đợt – thư ký đọc lại cuối buổi.",
        "Cuối bài: viết phần họp nhanh, khuyến nghị và câu hỏi còn mở ở bên dưới.",
    ],
    "zones": [zone(20, 20, 300, 860, "Các vai", "violet", "Ai được quyết, ai thực hiện")] +
             [sz(f"z_dot{i + 1}", 360 + i * 278, 20, 262, 860, t, ["red", "amber", "blue", "teal", "green"][i], h) for i, (t, h) in enumerate(DOT_TH11)],
    "kinds": [
        kind("role", "Vai", "violet", "🎭", notext=True),
        kind("dec", "Quyết định", "teal", "⚖️", "Quyết định gì", add=True,
             props=[pr("gio", "Giờ (câu chuyện)", "VD: 10:25"), pr("can_cu", "Căn cứ", "VD: quy chế, log, yêu cầu pháp chế")]),
        GHI_CHU,
    ],
    "nodes": [node(f"vai{i + 1}", "role", 52, 80 + i * 108, t) for i, t in enumerate(VAI_TH11)] +
             [node(f"q{i + 1}", "dec", 373 + i * 278, 100, f"Quyết định đợt {i + 1}", locked=False) for i in range(5)],
    "links": [{"a": "role", "b": "dec", "fields": [lf("vai", "Quyết (A) / làm (R)", "A hoặc R")]}],
    "goals": [
        {"type": "coverZones", "kind": "dec", "text": "Mỗi đợt có ít nhất một quyết định đã ghi nội dung"},
        {"type": "props", "kind": "dec", "fields": ["gio", "can_cu"], "min": 5, "text": "Ít nhất 5 quyết định có giờ và căn cứ"},
        {"type": "each", "kind": "dec", "to": ["role"], "text": "Mỗi quyết định nối với vai liên quan"},
        {"type": "linkfield", "a": "role", "b": "dec", "fields": ["vai"], "min": 5, "atLeast": True, "text": "Ghi A / R trên các dây nối (ít nhất 5)"},
    ],
    "summary": {"type": "cards", "kind": "dec", "sort": "zone", "title": "Biên bản quyết định theo đợt – tự lập từ bảng",
                "cols": [{"key": "zone", "label": "Đợt"}, {"key": "gio", "label": "Giờ"}, {"key": "title", "label": "Quyết định"},
                         {"key": "text", "label": "Nội dung"}, {"key": "links", "label": "Ai quyết / ai làm"}, {"key": "can_cu", "label": "Căn cứ"}]},
}


# Bài lấy mẫu theo mã hoạt động (thay cho mẫu sinh tự động khi dựng nội dung)
OVERRIDES = {
    "m03-case-v2": [
        BOARD_CASE_M03,
        ta("giai_thich", "Giải thích ngắn (tùy chọn)", "Điều bạn cân nhắc mà chưa thể hiện được trên bảng."),
    ],
}


TEMPLATES = {
    1: [
        BOARD_TH1,
    ],
    2: [
        {"type": "text", "key": "quy_trinh", "label": "Quy trình bạn chọn (A hoặc B – ghi tên quy trình)"},
        BOARD_TH2,
    ],
    3: [
        BOARD_TH3,
        ta("ghi_chu", "Ghi chú thêm (tùy chọn)", "VD: quyền của nhóm dữ liệu khác, điểm bạn còn phân vân."),
    ],
    4: [
        BOARD_TH4,
        ta("tom_tat", "Phương án của bạn trong 3–5 câu", "Viết như khi trình quản lý duyệt: giữ gì, gỡ gì, đến khi nào, kiểm tra bằng cách nào."),
    ],
    5: [
        BOARD_TH5,
        ta("de_xuat_mfa", "Đoạn đề xuất cấu hình MFA cho toàn Điện lực X gửi lãnh đạo (chọn loại MFA, có dùng SSO không)"),
    ],
    6: [
        BOARD_TH6,
        {"type": "checklist", "key": "checklist", "label": "Checklist chia sẻ 5 bước (mẫu C6)",
         "items": ["Ai nhận, có đúng người cần nhận không?",
                   "File chỉ còn các cột, dòng cần thiết (không còn sheet ẩn, cột ẩn)?",
                   "Đã mã hóa bằng tính năng mã hóa thật?",
                   "Chia sẻ cho người cụ thể, có hạn, không dùng link “Anyone”?",
                   "Mật khẩu gửi qua kênh khác và có ghi lại việc gửi?"]},
        ta("phan_b", "Phần B – Cách chia sẻ danh sách hộ nợ cho công ty thu hộ; vì sao bỏ các cột còn lại; xử lý thế nào khi họ đòi số điện thoại?"),
    ],
    7: [
        BOARD_TH7,
        {"type": "table", "key": "phuong_an", "label": "Chọn phương án xử lý dữ liệu (số liệu bước 9)",
         "rows": ["A – Tổng hợp thô theo phường", "B – Bỏ nhóm dưới 10 khách hàng (như HAVING)",
                  "D – Gộp Cảng Mới vào Đông Hòa", "F – Phương án 2: chỉ Sinh hoạt + Kinh doanh"],
         "columns": [col("nhom_nho", "Nhóm nhỏ nhất (KH)"), col("ty_trong", "Tỷ trọng lớn nhất (%)"),
                     col("giu_sl", "Giữ bao nhiêu % sản lượng"), col("chon", "Chọn?", ["Chọn", "Không chọn"]),
                     col("ly_do", "Vì sao")]},
        ta("phan_tach", "Phần sản lượng không có trong phương án bạn chọn là của ai? Báo anh Minh thế nào để dự báo không bị thiếu?"),
        {"type": "table", "key": "phieu", "label": "Phiếu yêu cầu dữ liệu (mẫu C7)",
         "rows": ["Người yêu cầu, đơn vị", "Mục đích sử dụng", "Các trường cần và lý do", "Mức chi tiết",
                  "Kỹ thuật giảm dữ liệu áp dụng", "Công cụ sẽ dùng (có AI không, đã được duyệt chưa)", "Hạn sử dụng và cách hủy", "Chủ dữ liệu duyệt"],
         "columns": [col("noi_dung", "Nội dung")]},
        ta("de_xuat", "Đoạn đề xuất gửi anh Tuấn"),
    ],
    8: [
        BOARD_TH8,
        ta("slicer", "Khi View as DonVi_A, slicer có chọn được Điện lực Y không? Vì sao?"),
    ],
    9: [
        BOARD_TH9,
    ],
    10: [
        BOARD_TH10,
    ],
    11: [
        BOARD_TH11,
        ta("hop_nhanh", "Họp nhanh: điều gì làm tốt, điều gì chưa rõ, điều gì trong quy trình thật cần sửa ngay?"),
        {"type": "table", "key": "khuyen_nghi", "label": "Khuyến nghị (biên bản diễn tập)", "rows": None, "min_rows": 3,
         "columns": [col("viec", "Việc"), col("nguoi", "Người phụ trách"), col("han", "Hạn"), col("kiem_chung", "Cách kiểm chứng")]},
        ta("cau_hoi_mo", "Câu hỏi còn mở"),
    ],
}


def template_for(activity_id: str):
    if activity_id in OVERRIDES:
        return OVERRIDES[activity_id]
    try:
        n = int(activity_id.rsplit("-th", 1)[1])
    except (IndexError, ValueError):
        return []
    return TEMPLATES.get(n, [ta("bai_lam", "Bài làm")])
