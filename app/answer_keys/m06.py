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

PHUONG_AN = [("1", "100", "100", "Không chọn", "Dòng Cảng Mới là sản lượng của đúng một xưởng"),
             ("121", "5,2", "86,7", "Không chọn", "Số đạt nhưng mất xưởng Cảng Mới mà không ai biết"),
             ("121", "46,3", "100", "Không chọn", "Xưởng chiếm gần nửa tổng nhóm gộp – vẫn ước được"),
             ("121", "5,2", "86,7", "Chọn", "Đạt hai phép; phần tách ra (khách hàng sản xuất) ghi trong đề xuất")]
PHAN_TACH = ("Phần không có trong bản giao là khách hàng sản xuất ở Cảng Mới: 42.359 kWh tháng 9 (13,3%), 128.185 kWh cả quý III. "
             "Ghi rõ trong đề xuất và báo anh Minh: bản tổng hợp chỉ gồm Sinh hoạt + Kinh doanh, phần sản xuất dự báo riêng "
             "theo hợp đồng cung cấp điện, không đưa vào AI thử nghiệm.")

# ---------- Thực hành 7: chuẩn bị dữ liệu cho phân tích và AI ----------
KEY_TH7 = key(
    "Các cột định danh, ngày sinh, giới tính và nhạy cảm bị bỏ; so sánh 4 phương án A, B, D, F rồi giao bản tổng hợp phường × tháng của nhóm Sinh hoạt + Kinh doanh (phương án 2), tách riêng "
    "khách hàng sản xuất Cảng Mới. Bản gộp Cảng Mới vào Đông Hòa vẫn bị áp đảo (46,3%); bản che từng dòng không đưa vào AI. "
    "Anh Tuấn duyệt file thật, CNTT xác nhận công cụ.",
    {"chuan_bi_du_lieu": board([
        col("ma_kh", 30, 510, "Không cần", "Bỏ", "Định danh; dự báo theo phường không cần"),
        col("ho_ten", 30, 600, "Không cần", "Bỏ", "Định danh trực tiếp"),
        col("so_cccd", 30, 690, "Không cần", "Bỏ", "Số định danh cá nhân; 6 số đầu còn lộ giới tính, năm sinh"),
        col("dien_thoai", 30, 780, "Không cần", "Bỏ", "Định danh trực tiếp"),
        col("email", 30, 870, "Không cần", "Bỏ", "Định danh trực tiếp (có cả tên trong địa chỉ email)"),
        col("dia_chi", 30, 960, "Không cần", "Bỏ", "Định danh; phường đã đủ cho dự báo"),
        col("ngay_sinh", 315, 510, "Không cần", "Bỏ", "Ghép với phường, giới tính là nhận ra gần như từng người"),
        col("gioi_tinh", 315, 600, "Không cần", "Bỏ", "Dự báo theo phường không cần; chia nhóm nhỏ hơn"),
        col("phuong", 315, 690, "Cần", "Giữ", "Đơn vị dự báo; mọi nhóm ≥ 10 khách hàng"),
        col("loai_kh", 315, 780, "Cần", "Biến đổi", "Chỉ dùng để lọc Sinh hoạt + Kinh doanh, không xuất ra (Bình Minh – KD chỉ 8)"),
        col("so_tien_no", 600, 510, "Không cần", "Bỏ", "Nhạy cảm, ngoài mục đích dự báo"),
        col("ho_chinh_sach", 600, 600, "Không cần", "Bỏ", "Hoàn cảnh kinh tế của gia đình; ngoài mục đích"),
        col("so_tk_ngan_hang", 600, 690, "Không cần", "Bỏ", "Thông tin tài khoản – lộ ra dễ bị lừa đảo"),
        col("ghi_chu", 600, 780, "Không cần", "Bỏ", "Gõ tự do: có tên, số người thân, tình trạng sức khỏe"),
        col("thang", 885, 510, "Cần", "Giữ", "Cần cho dự báo theo tháng"),
        col("kwh", 885, 600, "Cần", "Biến đổi", "Tổng hợp thành số khách hàng và tổng kWh theo phường – tháng"),
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
     "phuong_an": [dict(zip(("nhom_nho", "ty_trong", "giu_sl", "chon", "ly_do"), r)) for r in PHUONG_AN],
     "phan_tach": PHAN_TACH,
     "phieu": [{"noi_dung": x} for x in PHIEU],
     "de_xuat": DE_XUAT},
    modules=[
        ("🧩 <b>Định danh trực tiếp</b>", "ma_kh, ho_ten, so_cccd, dien_thoai, email, dia_chi → Bỏ.", "ho_ten ở vùng Dữ liệu phân tích là sai (có ⚠)."),
        ("🧩 <b>Định danh gián tiếp</b>", "ngay_sinh, gioi_tinh (Bỏ); phuong (Giữ), loai_kh (dùng để lọc, không xuất).",
         "Phường + giới tính + ngày sinh: 735/737 khách hàng là duy nhất. Xuất thêm loai_kh “cho đầy đủ” tạo nhóm nhỏ Bình Minh – Kinh doanh: 8."),
        ("🧩 <b>Thuộc tính nhạy cảm</b>", "so_tien_no, ho_chinh_sach, so_tk_ngan_hang, ghi_chu → Bỏ.", "Xếp so_tk_ngan_hang hoặc ghi_chu vào định danh trực tiếp cũng chấp nhận nếu vẫn Bỏ."),
        ("🧩 <b>Dữ liệu phân tích</b>", "thang (Giữ), kwh (tổng hợp).", "Xếp ma_kh vào gián tiếp cũng chấp nhận nếu vẫn Bỏ."),
        ("🔍 <b>Bốn phép kiểm tra</b>", "Kết quả cho cả bản tổng hợp và bản che.", "Bản che không đạt nhóm nhỏ, ngoại lai, phép trừ."),
        ("📦 <b>Quyết định giao</b>", "Tổng hợp phương án 2: Đưa vào AI. Bản che: Không đưa.",
         "Chọn “Chưa – cần xử lý thêm” cho bản tổng hợp cũng đạt nếu lý do là chờ duyệt công cụ."),
        ("👤 <b>Người duyệt, xác nhận</b>", "Anh Tuấn duyệt file; CNTT, chị Lan xác nhận công cụ.", "Ít nhất 2 người, ghi rõ duyệt gì."),
    ],
    more=[("Bảng chọn phương án xử lý (bước 9, tháng 2026-09)", [
        TABLE(["Phương án", "Nhóm nhỏ nhất", "Tỷ trọng lớn nhất", "Giữ sản lượng", "Quyết định"],
              ["A – tổng hợp thô", "1 KH (Cảng Mới)", "100%", "100%", "Không"],
              ["B – bỏ nhóm dưới 10 (HAVING)", "121 KH", "5,2%", "86,7%", "Không – mất xưởng mà không báo ai"],
              ["D – gộp Cảng Mới vào Đông Hòa", "121 KH", "46,3%", "100%", "Không – áp đảo"],
              ["F – phương án 2 (Sinh hoạt + Kinh doanh)", "121 KH", "5,2%", "86,7%", "Có, sau khi duyệt"],
              ["Bản che từng dòng", "Cảng Mới – SX 1; Bình Minh – KD 8", "–", "–", "Không"]),
        P("B và F ra cùng số vì Cảng Mới chỉ có khách hàng sản xuất. Khác biệt là cách làm: B lọc theo kết quả nên lặng lẽ bỏ cả phường; "
          "F tách theo loại khách hàng có lý do, báo anh Minh phần sản xuất (42.359 kWh tháng 9, 13,3%; 128.185 kWh cả quý) để dự báo riêng. Học viên chọn B "
          "nhưng ghi rõ phần bị bỏ và báo anh Minh thì chấp nhận được."),
        P("Chỉ ghi “đã khử nhận dạng” khi có căn cứ đánh giá như trên, không dựa vào việc bỏ cột tên. Phiếu C7 và đoạn đề xuất mẫu ở dưới bảng."),
    ])],
    rubric=[
        ("Phân loại cột", "2", "Đủ 16 cột; 6 cột định danh trực tiếp, ngày sinh, giới tính và 4 cột nhạy cảm bị bỏ; có lý do."),
        ("Bản tổng hợp và chọn phương án", "2", "Bảng chọn phương án đủ 4 dòng có số; chọn F (hoặc B có báo phần bị bỏ); xử lý Cảng Mới có báo lại cho anh Minh."),
        ("Kiểm tra nhận diện", "2", "Đủ 4 phép cho 2 bản; phát hiện áp đảo sau khi gộp."),
        ("Quyết định và người duyệt", "2", "Không giao bản che từng dòng; 2 người duyệt, điều kiện công cụ AI."),
        ("Phiếu C7 và đề xuất", "2", "Phiếu đủ 8 dòng; đoạn đề xuất đủ ý để anh Tuấn ký ngay; nhắc xóa bản trung gian."),
    ],
    mistakes=[
        ("Dừng ở HAVING, mất Cảng Mới", "Không nhắc khách hàng sản xuất", "“Dự báo của anh Minh có thiếu phường nào không? Báo anh ấy thế nào?”"),
        ("Gộp rồi dừng", "Không có kết quả áp đảo", "“Trong nhóm gộp, xưởng chiếm bao nhiêu phần trăm?”"),
        ("Chọn phương án theo một con số", "Chọn D vì giữ 100% sản lượng, hoặc B vì số giống F", "“Ba con số của phương án này đều đạt chưa? Phần bị bỏ là của ai?”"),
        ("Xuất thêm loai_kh", "loai_kh xử lý Giữ", "“Mỗi cột thêm chia nhóm nhỏ hơn: Bình Minh – Kinh doanh còn mấy khách?”"),
        ("Giữ ghi_chu hoặc ngày sinh “vì không phải tên”", "ghi_chu, ngay_sinh xử lý Giữ (có ⚠)", "“Đọc thử 5 ô ghi chú. Phường + giới tính + ngày sinh có mấy người trùng?”"),
        ("Gọi bản che là ẩn danh", "Bản che chọn Đưa vào AI, có ⚠", "“Mã thay thế cố định theo dõi được từng hộ qua 3 tháng không?”"),
        ("Để bảng đối chiếu đi cùng bản che", "Sheet DoiChieu còn trong file, hoặc gửi kèm", "Ai có bảng đối chiếu là nối ngược mã P0xxx về khách hàng thật; lưu file riêng có mã hóa."),
        ("Quên xóa file đủ cột", "Đề xuất không nhắc", "Bước cuối của quy trình."),
    ],
    flow=["Mở bảng kết quả kiểm tra A–F (phần Chuẩn bị của giảng viên, Thực hành 7) đến bước B: lớp thấy Cảng Mới chỉ 1 khách hàng.",
          "Sang bước E: bản gộp 46,3% – hỏi “gộp xong đã an toàn chưa?”.",
          "Chiếu bảng chọn phương án (bước 9): hỏi “B và F cùng số, chọn cái nào, vì sao?”.",
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
