"""Đáp án giảng viên – buổi 6 (bài lớn và bài tình huống; bài ngắn SQL/Python ở labs.py)."""
from .kit import L, N, P, TABLE, board, case_key, key


def col(id, x, y, can, xu_ly, ly_do):
    return N("c_" + id, "col", x, y, p={"can": can, "xu_ly": xu_ly, "ly_do": ly_do})


def chk(id, x, y, ban_th, ban_che):
    return N(id, "check", x, y, p={"ban_th": ban_th, "ban_che": ban_che})


DE_XUAT = (
    "Đề nghị anh duyệt bản tổng hợp số khách hàng và tổng kWh theo phường – tháng, quý III/2026, nhóm Sinh hoạt và Kinh doanh, "
    "không có cột định danh, mọi nhóm từ 10 khách hàng trở lên, không khách hàng nào chiếm quá 6% tổng nhóm. Khách hàng sản xuất "
    "ở Cảng Mới được tách riêng, dự báo theo hợp đồng. Người nhận: anh Minh, phòng Kế hoạch; mục đích: dự báo nhu cầu trên môi trường "
    "AI thử nghiệm (đang chờ CNTT xác nhận công cụ được phép và không dùng dữ liệu để huấn luyện). File trung gian đủ cột đã xóa."
)

PHIEU = ["Anh Minh, phòng Kế hoạch Công ty",
         "Dự báo nhu cầu điện theo phường trên môi trường AI thử nghiệm",
         "phuong, thang, số khách hàng, tổng kWh – đủ cho dự báo theo phường; không cần cột định danh, số nợ",
         "Tổng hợp phường × tháng, quý III/2026, nhóm Sinh hoạt + Kinh doanh",
         "Bỏ cột định danh; tổng hợp; ngưỡng nhóm ≥ 10; tách khách hàng sản xuất Cảng Mới; kiểm tra áp đảo (lớn nhất 5,2%)",
         "Môi trường AI thử nghiệm – chờ CNTT và chị Lan xác nhận đã được phép, dữ liệu không dùng để huấn luyện",
         "Dùng trong dự án dự báo quý IV; hết dự án thì xóa, báo lại chủ dữ liệu. Bản trung gian xóa ngay sau khi giao",
         "Anh Tuấn – chủ dữ liệu Điện lực X"]

# ---------- Thực hành 7: chuẩn bị dữ liệu cho phân tích và AI ----------
KEY_TH7 = key(
    "Bốn cột định danh và số nợ bị bỏ; giao bản tổng hợp phường × tháng của nhóm Sinh hoạt + Kinh doanh (phương án 2), tách riêng "
    "khách hàng sản xuất Cảng Mới. Bản gộp Cảng Mới vào Đông Hòa vẫn bị áp đảo (46,3%); bản che từng dòng không đưa vào AI. "
    "Anh Tuấn duyệt file thật, CNTT xác nhận công cụ.",
    {"chuan_bi_du_lieu": board([
        col("ma_kh", 30, 420, "Không cần", "Bỏ", "Định danh; dự báo theo phường không cần"),
        col("ho_ten", 30, 510, "Không cần", "Bỏ", "Định danh trực tiếp"),
        col("dien_thoai", 30, 600, "Không cần", "Bỏ", "Định danh trực tiếp"),
        col("dia_chi", 30, 690, "Không cần", "Bỏ", "Định danh; phường đã đủ cho dự báo"),
        col("phuong", 315, 420, "Cần", "Giữ", "Đơn vị dự báo; mọi nhóm ≥ 10 khách hàng"),
        col("loai_kh", 315, 510, "Cần", "Biến đổi", "Chỉ dùng để lọc Sinh hoạt + Kinh doanh, không xuất ra (Bình Minh – KD chỉ 8)"),
        col("so_tien_no", 600, 420, "Không cần", "Bỏ", "Nhạy cảm, ngoài mục đích dự báo"),
        col("thang", 885, 420, "Cần", "Giữ", "Cần cho dự báo theo tháng"),
        col("kwh", 885, 510, "Cần", "Biến đổi", "Tổng hợp thành số khách hàng và tổng kWh theo phường – tháng"),
        chk("k1", 1192, 70, "Đạt: mọi nhóm ≥ 10 (Cảng Mới đã tách)", "Không đạt: Cảng Mới – SX 1; Bình Minh – KD 8"),
        chk("k2", 1470, 70, "Hộ 3.370 kWh chìm trong 174 hộ", "Dòng 3.370 và 42.359 kWh nổi bật"),
        chk("k3", 1192, 160, "Lớn nhất 5,2% – đạt (bản gộp: 46,3% – không đạt)", "– (mỗi dòng là một khách hàng)"),
        chk("k4", 1470, 160, "Không có bảng nào để trừ", "Mã thay thế cố định qua các tháng: theo dõi được từng hộ"),
        N("v_th", "ver", 1180, 330, "Phương án 2: Sinh hoạt + Kinh doanh, tách khách hàng sản xuất Cảng Mới. Nhóm ≥ 10, lớn nhất 5,2%. "
          "Giao sau khi anh Tuấn duyệt.", tag="Đưa vào AI thử nghiệm"),
        N("v_che", "ver", 1180, 640, "Dự báo không cần từng hộ; còn điện thoại che, dòng nổi bật, mã theo dõi được – vẫn là dữ liệu cá nhân.",
          tag="Không đưa"),
        N("a_tuan", "actor", 1504, 330, "Chủ dữ liệu Điện lực X.", title="Anh Tuấn"),
        N("a_cntt", "actor", 1504, 520, "Xác nhận công cụ AI thử nghiệm.", title="CNTT và chị Lan"),
    ], [
        L("a_tuan", "v_th", viec="duyệt file"),
        L("a_cntt", "v_th", viec="duyệt công cụ"),
        L("a_tuan", "v_che", viec="không giao"),
    ]),
     "phieu": [{"noi_dung": x} for x in PHIEU],
     "de_xuat": DE_XUAT},
    modules=[
        ("🧩 <b>Định danh trực tiếp</b>", "ma_kh, ho_ten, dien_thoai, dia_chi → Bỏ.", "ho_ten ở vùng Dữ liệu phân tích là sai (có ⚠)."),
        ("🧩 <b>Định danh gián tiếp</b>", "phuong (Giữ), loai_kh (dùng để lọc, không xuất).",
         "Xuất thêm loai_kh “cho đầy đủ” tạo nhóm nhỏ Bình Minh – Kinh doanh: 8."),
        ("🧩 <b>Thuộc tính nhạy cảm</b>", "so_tien_no → Bỏ.", "Giữ số nợ là ngoài mục đích (có ⚠)."),
        ("🧩 <b>Dữ liệu phân tích</b>", "thang (Giữ), kwh (tổng hợp).", "Xếp ma_kh vào gián tiếp cũng chấp nhận nếu vẫn Bỏ."),
        ("🔍 <b>Bốn phép kiểm tra</b>", "Kết quả cho cả bản tổng hợp và bản che.", "Bản che không đạt nhóm nhỏ, ngoại lai, phép trừ."),
        ("📦 <b>Quyết định giao</b>", "Tổng hợp phương án 2: Đưa vào AI. Bản che: Không đưa.",
         "Chọn “Chưa – cần xử lý thêm” cho bản tổng hợp cũng đạt nếu lý do là chờ duyệt công cụ."),
        ("👤 <b>Người duyệt, xác nhận</b>", "Anh Tuấn duyệt file; CNTT, chị Lan xác nhận công cụ.", "Ít nhất 2 người, ghi rõ duyệt gì."),
    ],
    more=[("Ba bản tổng hợp cần so sánh", [
        TABLE(["Bản", "Nhóm nhỏ", "Áp đảo", "Quyết định"],
              ["A – tổng hợp thô", "Cảng Mới: 1 khách hàng", "100%", "Không"],
              ["D – gộp Cảng Mới vào Đông Hòa", "Đạt", "Xưởng 46,3% – không đạt", "Chưa"],
              ["F – phương án 2 (Sinh hoạt + Kinh doanh)", "Đạt", "Cao nhất 5,2% – đạt", "Có, sau khi duyệt"],
              ["Bản che từng dòng", "Cảng Mới – SX 1; Bình Minh – KD 8", "–", "Không"]),
        P("Chỉ ghi “đã khử nhận dạng” khi có căn cứ đánh giá như trên, không dựa vào việc bỏ cột tên. Phiếu C7 và đoạn đề xuất mẫu ở dưới bảng."),
    ])],
    rubric=[
        ("Phân loại cột", "2", "Đủ 9 cột, 4 cột định danh trực tiếp bị bỏ, số nợ bỏ; có lý do."),
        ("Bản tổng hợp", "2", "Không còn nhóm dưới ngưỡng; xử lý Cảng Mới có báo lại cho anh Minh."),
        ("Kiểm tra nhận diện", "2", "Đủ 4 phép cho 2 bản; phát hiện áp đảo sau khi gộp."),
        ("Quyết định và người duyệt", "2", "Không giao bản che từng dòng; 2 người duyệt, điều kiện công cụ AI."),
        ("Phiếu C7 và đề xuất", "2", "Phiếu đủ 8 dòng; đoạn đề xuất đủ ý để anh Tuấn ký ngay; nhắc xóa bản trung gian."),
    ],
    mistakes=[
        ("Dừng ở HAVING, mất Cảng Mới", "Không nhắc khách hàng sản xuất", "“Dự báo của anh Minh có thiếu phường nào không? Báo anh ấy thế nào?”"),
        ("Gộp rồi dừng", "Không có kết quả áp đảo", "“Trong nhóm gộp, xưởng chiếm bao nhiêu phần trăm?”"),
        ("Xuất thêm loai_kh", "loai_kh xử lý Giữ", "“Mỗi cột thêm chia nhóm nhỏ hơn: Bình Minh – Kinh doanh còn mấy khách?”"),
        ("Gọi bản che là ẩn danh", "Bản che chọn Đưa vào AI, có ⚠", "“Mã thay thế cố định theo dõi được từng hộ qua 3 tháng không?”"),
        ("Khóa HMAC ghi trong script", "Ghi khóa trong bài", "Khóa lưu riêng, đọc từ biến môi trường hoặc kho khóa."),
        ("Quên xóa file đủ cột", "Đề xuất không nhắc", "Bước cuối của quy trình."),
    ],
    flow=["Mở bảng kết quả kiểm tra A–F (phần Chuẩn bị của giảng viên, Thực hành 7) đến bước B: lớp thấy Cảng Mới chỉ 1 khách hàng.",
          "Sang bước E: bản gộp 46,3% – hỏi “gộp xong đã an toàn chưa?”.",
          "Mở bảng mẫu: đọc bảng phân loại cột, rồi bảng 4 phép kiểm tra.",
          "Đọc đoạn đề xuất mẫu; hỏi anh Tuấn còn cần gì để ký."],
)

# ---------- Bài tập thêm: tổng hợp rồi đã an toàn chưa? ----------
KEY_CASE6 = case_key(
    "Cảng Mới chỉ 1 khách hàng: tổng chính là số của khách đó. Gộp với Đông Hòa: 42.000 / 68.000 ≈ 61,8% – vẫn áp đảo. "
    "Tổng hợp rộng hơn hoặc tách khách hàng lớn, kiểm tra lại 4 phép; công cụ AI chưa duyệt thì chưa đưa vào.",
    ["Nhóm có nguy cơ: Cảng Mới – 1 khách hàng, tổng 42.000 kWh chính là sản lượng của khách đó.\n"
     "Gộp Cảng Mới với Đông Hòa: 101 khách hàng, tổng 42.000 + 26.000 = 68.000 kWh; khách lớn nhất 42.000 / 68.000 ≈ 61,8% – "
     "vẫn áp đảo, ai biết mức bình thường của Đông Hòa sẽ ước được số của khách lớn.\n"
     "An Phú: 120 khách hàng, khách lớn nhất 700 / 30.000 ≈ 2,3% – đạt.",
     "Đề xuất giao bản tổng hợp theo vùng của khách hàng sinh hoạt, kinh doanh (An Phú, Đông Hòa…), tách riêng khách hàng lớn Cảng Mới để "
     "dự báo theo hợp đồng, hoặc tổng hợp ở mức rộng hơn. Sau đó kiểm tra lại nhóm nhỏ, ngoại lai, áp đảo và phép trừ giữa các bảng.\n"
     "Chỉ bỏ tên chưa đủ vì nhóm 1 người vẫn lộ số của người đó; chỉ gộp hai vùng chưa đủ vì một khách vẫn chiếm phần lớn tổng, "
     "và ai có bảng Đông Hòa riêng có thể trừ ra.",
     "Trước khi dùng AI: công cụ phải được đơn vị duyệt; chủ dữ liệu duyệt bản giao và mục đích; xác nhận dữ liệu không bị dùng để "
     "huấn luyện; ghi sổ theo dõi bản xuất.\n"
     "Bản trung gian (file đủ cột, bản thử gộp): lưu ở thư mục được phép trong lúc làm, xóa ngay sau khi giao theo quy định, "
     "ghi lại người xóa và thời điểm."],
    [("1. Nhóm nguy cơ, tỷ trọng", "Cảng Mới 1 khách; 42.000 / 68.000 ≈ 61,8%.", "Tính thêm An Phú 2,3%."),
     ("2. Bản đề xuất", "Tách khách lớn hoặc tổng hợp rộng hơn; giải thích vì sao bỏ tên, gộp hai vùng chưa đủ.", "Nhắc phép trừ giữa các bảng."),
     ("3. Điều kiện AI, bản trung gian", "Công cụ được duyệt, chủ dữ liệu duyệt; xóa bản trung gian theo quy định.", "Không dùng dữ liệu để huấn luyện.")],
    ["Nhận ra Cảng Mới là nhóm một người; tính đúng 61,8%.",
     "Đề xuất xử lý khách lớn có lý do, không dừng ở gộp hai vùng.",
     "Có điều kiện kiểm chứng: 4 phép kiểm tra, người duyệt, cách xử lý bản trung gian."],
    [("Tính tỷ trọng sai mẫu số", "42.000 / 26.000", "“Tổng của nhóm mới là bao nhiêu?”"),
     ("Cho rằng gộp là xong", "Không kiểm tra áp đảo", "“Trong nhóm mới, một khách chiếm bao nhiêu?”"),
     ("Đưa vào AI chưa duyệt", "“Dữ liệu tổng hợp rồi nên dùng được”", "“Công cụ đã được đơn vị duyệt chưa?”")],
)

KEYS = {"m06-th7": KEY_TH7, "m06-case-v2": KEY_CASE6}
