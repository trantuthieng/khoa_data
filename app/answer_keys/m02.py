"""Đáp án giảng viên – buổi 2."""
from .kit import L, N, board, case_key, key


def risk(tac_dong, kiem_soat, nguoi, minh_chung):
    return {"tac_dong": tac_dong, "kiem_soat": kiem_soat, "nguoi": nguoi, "minh_chung": minh_chung}


def flow(du_lieu, cach, ranh_gioi=None):
    d = {"du_lieu": du_lieu, "cach": cach}
    if ranh_gioi:
        d["ranh_gioi"] = ranh_gioi
    return d


# ---------- Thực hành 2: sơ đồ luồng dữ liệu (quy trình A) ----------
KEY_TH2 = key(
    "Quy trình A có năm bước và bốn ranh giới tin cậy: ảnh phiếu qua Zalo cá nhân, xuất Excel về máy, gửi email, lưu ổ chia sẻ. "
    "Phải có bản sao không chính thức (ảnh Zalo, file trong thư mục Tải về) và bảng rủi ro có người chịu trách nhiệm cụ thể, không phải “phòng CNTT”.",
    {"quy_trinh": "Quy trình A – Tiếp nhận và xử lý yêu cầu khách hàng",
     "so_do_luong": board([
         N("n_kh", "actor", 42, 90, "Gọi tổng đài hoặc đến quầy, đọc tên, điện thoại, mã KH, nội dung."),
         N("n_td", "actor", 382, 90, "Nhập phiếu vào hệ thống ngay khi nhận."),
         N("n_ld", "actor", 382, 420, "Nhận báo cáo tháng qua email. Chỉ cần số lượng và thời gian xử lý."),
         N("r3", "risk", 382, 640, "Gửi email đính kèm cho danh sách dài, có người đã chuyển đơn vị.", title="Email cho danh sách nhận cũ",
           p=risk("Người không còn liên quan vẫn nhận file", "Gửi link tới ổ chia sẻ có phân quyền; rà danh sách nhận hằng quý",
                  "Trưởng phòng", "Danh sách nhận đã rà soát")),
         N("n_ht", "system", 662, 90, "Lưu phiếu, địa chỉ. Ai có quyền xuất là xuất được đủ cột."),
         N("n_nv", "actor", 662, 300, "Nhận phiếu, cần địa chỉ để cử người xuống hiện trường."),
         N("r1", "risk", 662, 530, "Chụp màn hình phiếu gửi qua Zalo cá nhân cho tổ hiện trường.", title="Ảnh phiếu trên Zalo cá nhân",
           p=risk("Ảnh có tên, địa chỉ nằm trong điện thoại cá nhân, tự sao lưu lên cloud",
                  "Dùng chức năng giao việc của hệ thống hoặc ứng dụng nhắn tin được duyệt", "Tổ trưởng hiện trường",
                  "Quy định kênh giao việc đã ban hành")),
         N("c_down", "copy", 1002, 90, "Bản xuất đủ cột, kể cả tên, điện thoại; nằm lại sau khi lập báo cáo.",
           title="File xuất trong thư mục Tải về", tag="Không chính thức"),
         N("n_xl", "copy", 1002, 320, "Lập trên máy cá nhân; báo cáo chỉ cần số yêu cầu và thời gian xử lý.", tag="Chính thức"),
         N("r2", "risk", 1002, 540, "Xuất đủ cột trong khi báo cáo chỉ cần số lượng.", title="Xuất thừa cột",
           p=risk("Bản sao thừa dữ liệu cá nhân trên máy và trong email", "Xuất theo mẫu chỉ có cột tổng hợp",
                  "Chuyên viên tổng hợp", "Mẫu xuất đã duyệt")),
         N("c_zalo", "copy", 1402, 90, "Ảnh chụp phiếu trong Zalo của tổ, thư viện ảnh và bản sao lưu điện thoại.",
           title="Ảnh phiếu gửi Zalo tổ hiện trường", tag="Không chính thức"),
         N("c_email", "copy", 1402, 320, "Hộp thư đã gửi và hộp thư từng người nhận đều giữ một bản.",
           title="Email gửi báo cáo", tag="Chính thức"),
         N("n_os", "copy", 1402, 530, "Báo cáo các tháng để mãi, ai có quyền vào ổ là đọc được.", tag="Chính thức"),
         N("r4", "risk", 1402, 730, "Báo cáo các tháng cũ nằm mãi trên ổ chia sẻ.", title="Không có hạn lưu",
           p=risk("Mở rộng phạm vi nếu ổ bị lộ", "Đặt thời hạn lưu theo quy định, xóa định kỳ", "Chuyên viên tổng hợp", "Nhật ký dọn dẹp")),
     ], [
         L("n_kh", "n_td", **flow("Tên, SĐT, mã KH", "Gọi, quầy")),
         L("n_td", "n_ht", **flow("Phiếu", "Nhập tay")),
         L("n_ht", "n_nv", **flow("Phiếu + địa chỉ", "Hệ thống")),
         L("n_nv", "c_zalo", **flow("Ảnh phiếu", "Zalo cá nhân", "1")),
         L("n_ht", "c_down", **flow("DS đủ cột", "Xuất Excel", "2")),
         L("c_down", "n_xl", **flow("Số phiếu, thời gian", "Trên máy")),
         L("n_xl", "c_email", **flow("Báo cáo", "Email", "3")),
         L("c_email", "n_ld", **flow("Báo cáo", "Hộp thư")),
         L("n_xl", "n_os", **flow("Báo cáo", "Chép lên ổ", "4")),
         L("r1", "c_zalo"), L("r2", "c_down"), L("r3", "n_ld"), L("r4", "n_os"),
     ])},
    modules=[
        ("👤 Khách hàng, tổng đài, nghiệp vụ, lãnh đạo; 🗄️ hệ thống phiếu", "Mỗi thẻ ghi làm gì với dữ liệu.",
         "Đặt đúng vùng: khách hàng ở ① bên ngoài; hệ thống và người xử lý ở ②."),
        ("📄 <b>Ảnh phiếu gửi Zalo</b> (Không chính thức)", "Ảnh trong Zalo, thư viện ảnh, bản sao lưu điện thoại.",
         "Bản sao bị quên nhiều nhất. Bài không có bản sao không chính thức là thiếu tiêu chí “Bản sao”."),
        ("📄 <b>File xuất trong Tải về</b> (Không chính thức)", "Bản đủ cột còn nằm lại sau khi lập báo cáo.", "Khác với báo cáo Excel: đây là file trung gian."),
        ("📄 Báo cáo Excel, email, ổ chia sẻ (Chính thức)", "Nơi lưu, ai giữ, bao giờ xóa.",
         "Email có hai bản: hộp thư đã gửi và hộp thư người nhận."),
        ("⚠️ <b>Bốn điểm yếu</b>", "Zalo cá nhân, xuất thừa cột, danh sách nhận cũ, không có hạn lưu. Bảng C2 điền đủ 4 cột.",
         "Người chịu trách nhiệm là <b>người làm bước đó</b> (tổ trưởng, chuyên viên, trưởng phòng)."),
    ],
    links=[
        ("Khách hàng → Tổng đài", "Tên, điện thoại, mã KH, nội dung · Gọi điện, quầy", "Dữ liệu đi vào, chưa vượt ranh giới."),
        ("Tổng đài → Hệ thống", "Phiếu yêu cầu · Nhập tay", "Trong hệ thống chính thức."),
        ("Hệ thống → Nghiệp vụ", "Phiếu + địa chỉ · Hệ thống", "Đường chính thức."),
        ("Nghiệp vụ → Ảnh Zalo", "Ảnh phiếu · Zalo cá nhân · <b>RG 1</b>", "Cách làm thực tế, ra khỏi kênh được quản lý."),
        ("Hệ thống → File Tải về", "Danh sách đủ cột · Xuất Excel · <b>RG 2</b>", "Ra máy cá nhân."),
        ("File Tải về → Báo cáo Excel", "Số yêu cầu, thời gian · Lập trên máy", "Cùng máy, không vượt thêm ranh giới."),
        ("Báo cáo → Email", "File báo cáo · Email đính kèm · <b>RG 3</b>", "Ra kênh gửi."),
        ("Báo cáo → Ổ chia sẻ", "File báo cáo · Chép lên ổ · <b>RG 4</b>", "Ra nơi lưu ngoài hệ thống."),
        ("⚠️ Điểm yếu → bước liên quan", "—", "Bảng C2 tự lấy tên bước từ dây này."),
    ],
    rubric=[
        ("Nguồn – đích", "2", "Mọi mũi tên có điểm đầu, điểm cuối; đi theo cách mọi người thật sự làm."),
        ("Trường dữ liệu", "2", "Ít nhất 5 mũi tên ghi dữ liệu gì, truyền bằng cách nào."),
        ("Ranh giới", "2", "Đánh số đủ chỗ ra máy cá nhân, email, Zalo, ổ chia sẻ (ít nhất 2, bài mẫu có 4)."),
        ("Bản sao", "2", "Có bản sao không chính thức (Zalo, ảnh, file Tải về, bản in)."),
        ("Bảng rủi ro", "2", "Ít nhất 3 dòng, mỗi dòng có người chịu trách nhiệm cụ thể và minh chứng."),
    ],
    mistakes=[
        ("Chỉ nối tên phòng ban", "Mũi tên không ghi dữ liệu", "“Trên mũi tên này đi những trường nào?”"),
        ("Vẽ quy trình trên giấy", "Không có Zalo, ảnh chụp", "“Tổ hiện trường thật sự nhận địa chỉ bằng cách nào?”"),
        ("Quên bản sao và bước lưu giữ", "Không có file Tải về, không có hạn lưu ổ chia sẻ", "“Sau khi gửi, file còn nằm ở những đâu?”"),
        ("“Phòng CNTT” chịu trách nhiệm mọi dòng", "Có cảnh báo ⚠ ở bảng C2", "“Ai là người làm bước đó hằng ngày?”"),
        ("Chấm điểm rủi ro bằng con số", "Cột tác động ghi 1–5", "Không chấm số khi đơn vị chưa có phương pháp thống nhất; mô tả tác động bằng lời."),
    ],
    flow=["Chiếu một bài chỉ có tên phòng ban nối với nhau; hỏi “trên mũi tên đi dữ liệu gì?”.",
          "Mở bảng mẫu, đi theo mũi tên từ trái sang phải; dừng ở 4 nhãn RG.",
          "Hỏi lớp: còn bản sao nào chưa có trên bảng (bản in, thùng rác, OneDrive đồng bộ)?",
          "Đọc bảng C2: người chịu trách nhiệm phải là người làm bước đó.",
          "Nhắc giữ sơ đồ cho buổi 3 và buổi 5; công bố đáp án."],
)

# ---------- Bài tập thêm: tìm những bản sao bị bỏ quên ----------
KEY_CASE2 = case_key(
    "Xóa file trong Tải về chưa phải hết bản sao: còn hộp thư đã gửi, hộp thư tổ hiện trường, ảnh trong ứng dụng nhắn tin, "
    "thư viện ảnh và bản sao lưu điện thoại, thùng rác, ổ đồng bộ. Báo cáo tháng chỉ cần số phiếu và thời gian xử lý.",
    ["Hệ thống phiếu → xuất 50 phiếu về máy (thư mục Tải về) → email cho tổ hiện trường → chụp 3 phiếu gửi tài khoản nhắn tin cá nhân → "
     "báo cáo tháng.\nNơi còn bản sao: (1) hộp thư đã gửi của nhân viên; (2) hộp thư từng người trong tổ hiện trường và máy họ đã tải về; "
     "(3) ảnh trong ứng dụng nhắn tin, thư viện ảnh và bản sao lưu điện thoại (cả người gửi lẫn người nhận); (4) thùng rác máy tính; "
     "(5) thư mục OneDrive đồng bộ nếu Tải về được đồng bộ.",
     "1) Bản xuất 50 phiếu: lập báo cáo từ bản tổng hợp chỉ có số phiếu và thời gian xử lý; xóa bản xuất và dọn thùng rác sau khi xong. "
     "Người chịu trách nhiệm: người lập báo cáo.\n"
     "2) Ảnh phiếu qua nhắn tin cá nhân: giao việc qua hệ thống hoặc kênh nhắn tin được duyệt; xóa ảnh cũ ở cả hai đầu. "
     "Người chịu trách nhiệm: tổ trưởng hiện trường.\n"
     "3) Email cho tổ hiện trường: gửi đường dẫn tới phiếu trong hệ thống thay vì đính kèm; chủ dữ liệu xác nhận phạm vi và thời hạn lưu. "
     "Người chịu trách nhiệm: chủ dữ liệu.",
     "Trước khi gửi báo cáo tháng: báo cáo chỉ cần số phiếu và thời gian xử lý, không cần tên hay điện thoại khách. "
     "Kiểm tra file không còn sheet hoặc cột chi tiết. Bản xuất trung gian xóa ngay sau khi lập xong, nhớ cả thùng rác. "
     "Hồ sơ phải lưu hoặc liên quan sự cố thì không tự xóa, báo chủ dữ liệu."],
    [("1. Đường đi và bản sao", "Đủ đường đi; ít nhất 4 nơi còn bản sao, có cả hộp thư người nhận và ảnh trên điện thoại.",
      "Bản in, máy người nhận đã tải, nhóm chat."),
     ("2. Ba điểm sửa", "Mỗi điểm có cách sửa và người chịu trách nhiệm cụ thể.", "Thời hạn lưu, người xác nhận đã xóa."),
     ("3. Lời nhắc", "Tối đa 5 câu; nêu dữ liệu cần thiết cho báo cáo và việc xử lý bản trung gian.",
      "Nhắc không tự xóa hồ sơ phải lưu.")],
    ["Nhận ra xóa ở Tải về chưa phải hết bản sao; kể được bản sao ở phía người nhận.",
     "Cách sửa đi vào gốc (xuất ít cột, kênh giao việc được duyệt), có người chịu trách nhiệm.",
     "Có cách kiểm chứng đã hết bản sao: rà hộp thư, ảnh, thùng rác, người nhận xác nhận đã xóa."],
    [("Chỉ kể bản sao trên máy mình", "Không có hộp thư, điện thoại của tổ hiện trường", "“Người nhận email, nhận ảnh còn giữ gì?”"),
     ("Sửa bằng “ẩn cột”", "Ghi ẩn cột điện thoại rồi gửi", "“Ẩn cột có xóa dữ liệu khỏi file không?”"),
     ("Không có người chịu trách nhiệm", "Câu 2 chỉ có cách sửa", "“Ai làm việc này, ai xác nhận đã làm?”"),
     ("Xóa cả hồ sơ phải lưu", "“Xóa hết mọi thứ”", "Nhắc thời hạn lưu và bằng chứng sự cố.")],
)

KEYS = {"m02-th2": KEY_TH2, "m02-case-v2": KEY_CASE2}
