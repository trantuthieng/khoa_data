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


GHI_CHU = kind("note", "Ghi chú", "slate", "📝", "Ý tưởng, câu hỏi, điều cần kiểm tra thêm…", add=True)
QUYEN_HIEN_TAI = dict(options=["Giữ nguyên", "Thu hẹp", "Thu hồi"], optionLabel="Quyết định…",
                      tones={"Giữ nguyên": "warn", "Thu hẹp": "info", "Thu hồi": "bad"})

BOARD_TH3 = {
    "type": "board", "key": "ma_tran_bang", "size": [1000, 900],
    "label": "Không gian ma trận quyền – nối vai trò với thao tác được phép, ghi phạm vi và người duyệt trên từng dây",
    "hint": "Có dây nối nghĩa là có quyền; không nối nghĩa là không có quyền. Bảng ma trận bên dưới tự lập từ các dây nối.",
    "steps": [
        "Ghi nhóm dữ liệu đang xét vào module 📂 (lấy từ Thực hành 1).",
        "Với từng vai trò ở cột ①, ghi ngắn công việc chính cần dữ liệu gì.",
        "Nối vai trò sang thao tác ở cột ② mà vai trò đó thật sự cần. Không cần thì không nối.",
        "Bấm nhãn trên mỗi dây, ghi phạm vi (dữ liệu nào) và người duyệt.",
        "Ở cột ③, viết 3 trường hợp phải bị từ chối và 2 trường hợp phải xin thêm quyền, rồi nối mỗi ô với vai trò liên quan.",
        "Đọc ma trận C3 bên dưới: ô tô vàng là còn thiếu thông tin. Xem lại các gợi ý ⚠ rồi nộp bài.",
    ],
    "zones": [zone(20, 20, 280, 860, "① Vai trò", "blue", "Năm vai trò trong đề"),
              zone(340, 20, 280, 860, "② Thao tác", "teal", "Trên nhóm dữ liệu bạn chọn"),
              zone(660, 20, 320, 860, "③ Kiểm thử quyền", "red", "Trường hợp phải bị từ chối và trường hợp phải xin thêm quyền")],
    "kinds": [
        kind("role", "Vai trò", "blue", "👤", "Công việc chính cần dữ liệu gì?", add=True),
        kind("data", "Nhóm dữ liệu", "slate", "📂", "VD: Khách hàng và hợp đồng (lấy từ Thực hành 1)"),
        kind("perm", "Thao tác", "teal", "🔑", "Điều kiện chung cho thao tác này (nếu có)"),
        kind("deny", "Phải bị từ chối", "red", "🚫", "Ai – làm gì – vì sao phải chặn", add=True),
        kind("req", "Phải xin thêm quyền", "amber", "✋", "Ai – cần gì – ai duyệt – đến khi nào", add=True),
        GHI_CHU,
    ],
    "nodes": [
        node("r_nv", "role", 42, 80, "Nhân viên nghiệp vụ"),
        node("r_tp", "role", 42, 240, "Trưởng phòng"),
        node("r_tn", "role", 42, 400, "Chuyên viên thu nợ"),
        node("r_cntt", "role", 42, 560, "Cán bộ CNTT hỗ trợ"),
        node("r_qt", "role", 42, 720, "Quản trị hệ thống"),
        node("d_nhom", "data", 362, 80, "Nhóm dữ liệu đang xét"),
        node("p_xem", "perm", 362, 260, "Xem"),
        node("p_sua", "perm", 362, 410, "Sửa"),
        node("p_xuat", "perm", 362, 560, "Xuất"),
        node("p_cap", "perm", 362, 710, "Cấp quyền"),
        node("t_1", "deny", 702, 100, "Từ chối 1", locked=False),
        node("t_2", "deny", 702, 250, "Từ chối 2", locked=False),
        node("t_3", "deny", 702, 400, "Từ chối 3", locked=False),
        node("x_1", "req", 702, 590, "Xin thêm 1", locked=False),
        node("x_2", "req", 702, 740, "Xin thêm 2", locked=False),
    ],
    "links": [{"a": "role", "b": "perm", "fields": [lf("pham_vi", "Phạm vi", "VD: KH đơn vị mình"),
                                                      lf("duyet", "Người duyệt", "VD: TP Kinh doanh", "duyệt: ")]}],
    "goals": [
        {"type": "filled", "ids": ["d_nhom"], "text": "Ghi nhóm dữ liệu đang xét"},
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
    "type": "board", "key": "so_do_xu_ly", "size": [1460, 800],
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
    "zones": [zone(20, 20, 280, 760, "Người liên quan", "violet", "Mỗi người muốn gì? Lo ngại gì?"),
              zone(340, 20, 800, 260, "Quyền của chị Hà", "amber", "Quyết định cho từng quyền"),
              zone(340, 300, 800, 480, "Các bước xử lý", "teal", "Nối bước trước → bước sau; nối người phụ trách vào từng bước"),
              zone(1160, 20, 280, 760, "Bằng chứng", "green", "Thứ chứng minh quyền cũ đã được xử lý")],
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
        node("a_tuan", "actor", 42, 240, "Anh Tuấn – quản lý Điện lực X"),
        node("a_y", "actor", 42, 400, "Quản lý phòng Kế hoạch – Điện lực Y"),
        node("a_cntt", "actor", 42, 560, "Cán bộ CNTT"),
        node("q_xem", "right", 362, 80, "Xem toàn bộ khách hàng Điện lực X"),
        node("q_xuat", "right", 622, 80, "Xuất dữ liệu khách hàng Điện lực X"),
        node("q_moi", "newright", 882, 80, "Vai trò Kế hoạch – Điện lực Y"),
        node("b_nhu_cau", "step", 362, 370, "Xác định nhu cầu bàn giao", "Bàn giao việc gì? Cần xem hay sửa? Đúng những hồ sơ nào?"),
        node("b_duyet", "step", 622, 370, "Phê duyệt ngoại lệ và đặt hạn", "Ai duyệt? Hết hạn ngày nào? Có cách nào không cần ngoại lệ?"),
        node("b_thu_hoi", "step", 882, 370, "Thu hồi quyền không còn cần", "Gỡ quyền nào, khi nào, ai làm?"),
        node("b_cap_moi", "step", 882, 590, "Cấp quyền mới ở Điện lực Y", "Vai trò nào, theo ma trận quyền nào?"),
        node("b_kiem_tra", "step", 622, 590, "Kiểm tra lại", "Thử bằng tài khoản chị Hà: thao tác nào phải bị từ chối?"),
        node("e_1", "evidence", 1182, 100, "Bằng chứng 1", locked=False),
        node("e_2", "evidence", 1182, 280, "Bằng chứng 2", locked=False),
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
    "type": "board", "key": "phuong_an", "size": [1300, 820],
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
    "zones": [zone(20, 20, 280, 400, "① Quyền hiện tại", "amber"),
              zone(20, 440, 280, 360, "② Ngoại lệ đề xuất", "green"),
              zone(340, 20, 280, 780, "③ Ai duyệt, ai cấu hình", "violet"),
              zone(660, 20, 280, 780, "④ Bằng chứng cần lưu", "slate"),
              zone(980, 20, 300, 780, "⑤ Ba phép thử", "red")],
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
        node("q_xuat", "right", 42, 240, "Xuất dữ liệu khách hàng Điện lực X"),
        node("g_ngoai_le", "grant", 42, 490, "Ngoại lệ bàn giao 12 hồ sơ"),
        node("a_chu", "actor", 362, 70, "Chủ dữ liệu"),
        node("a_ql", "actor", 362, 230, "Quản lý Điện lực X"),
        node("a_cntt", "actor", 362, 390, "Cán bộ CNTT"),
        node("a_ha", "actor", 362, 550, "Chị Hà"),
        node("e_1", "evidence", 682, 70, "Bằng chứng 1", locked=False),
        node("e_2", "evidence", 682, 230, "Bằng chứng 2", locked=False),
        node("t_1", "test", 1012, 70, "Phép thử 1 – Trường hợp được phép"),
        node("t_2", "test", 1012, 300, "Phép thử 2 – Truy cập ngoài phạm vi"),
        node("t_3", "test", 1012, 530, "Phép thử 3 – Thao tác xuất"),
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

# Bài lấy mẫu theo mã hoạt động (thay cho mẫu sinh tự động khi dựng nội dung)
OVERRIDES = {
    "m03-case-v2": [
        BOARD_CASE_M03,
        ta("giai_thich", "Giải thích ngắn (tùy chọn)", "Điều bạn cân nhắc mà chưa thể hiện được trên bảng."),
    ],
}


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
        BOARD_TH3,
        ta("ghi_chu", "Ghi chú thêm (tùy chọn)", "VD: quyền của nhóm dữ liệu khác, điểm bạn còn phân vân."),
    ],
    4: [
        BOARD_TH4,
        ta("tom_tat", "Phương án của bạn trong 3–5 câu", "Viết như khi trình quản lý duyệt: giữ gì, gỡ gì, đến khi nào, kiểm tra bằng cách nào."),
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
    if activity_id in OVERRIDES:
        return OVERRIDES[activity_id]
    try:
        n = int(activity_id.rsplit("-th", 1)[1])
    except (IndexError, ValueError):
        return []
    return TEMPLATES.get(n, [ta("bai_lam", "Bài làm")])
