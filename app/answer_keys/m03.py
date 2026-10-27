"""Đáp án giảng viên – buổi 3."""
from .kit import L, N, P, TABLE, board, key


def q(pham_vi, duyet):
    return {"pham_vi": pham_vi, "duyet": duyet}


# ---------- Thực hành 3: ma trận quyền ----------
KEY_TH3 = key(
    "Xét nhóm “Khách hàng & hợp đồng”. Quyền xuất và cấp quyền tách khỏi quyền xem; mỗi dây quyền có phạm vi và người duyệt. "
    "Quản trị hệ thống không xem dữ liệu khách hàng mặc định, chỉ thực thi cấp quyền theo phiếu. Có ít nhất 3 trường hợp phải bị từ chối "
    "và 2 trường hợp xin thêm quyền.",
    {"ma_tran_bang": board([
        N("r_nv", "role", 742, 80, "Giao dịch viên: tiếp nhận, cập nhật hồ sơ khách hàng được giao."),
        N("r_tp", "role", 742, 260, "Trưởng phòng Kinh doanh: theo dõi, duyệt nghiệp vụ của đơn vị mình."),
        N("r_tn", "role", 742, 440, "Thu nợ: cần danh sách hộ nợ của đơn vị mình."),
        N("r_cntt", "role", 742, 620, "Hỗ trợ người dùng khi có phiếu, không làm nghiệp vụ."),
        N("r_qt", "role", 742, 800, "Cấu hình hệ thống và thực thi cấp quyền theo phiếu."),
        N("d_nhom", "data", 1302, 80, "Mật (Thực hành 1): tên, điện thoại, hợp đồng, số nợ.", p={"nhom": "Khách hàng & hợp đồng"}),
        N("p_xem", "perm", 1302, 410, "Mặc định chỉ đơn vị mình."),
        N("p_sua", "perm", 1302, 560, "Có lưu vết người sửa."),
        N("p_xuat", "perm", 1302, 710, "Ghi lý do, mẫu cột cố định, có log."),
        N("p_cap", "perm", 1302, 860, "Người duyệt khác người cấu hình."),
        N("t_1", "deny", 42, 100, "NV Điện lực X mở hồ sơ khách hàng Điện lực Y: ngoài phạm vi đơn vị."),
        N("t_2", "deny", 42, 300, "Giao dịch viên xuất danh sách toàn đơn vị (lỗi chương 3): không có quyền xuất."),
        N("t_3", "deny", 42, 510, "CNTT xuất danh sách khách hàng khi không có phiếu: không có quyền xuất."),
        N("t_4", "deny", 42, 720, "Nhân viên tự cấp thêm quyền xuất cho mình: người xin không được tự cấp.", title="Từ chối 4"),
        N("x_1", "req", 362, 100, "TP cần xuất sản lượng chi tiết cho đoàn kiểm tra → quyền tạm, có ngày hết hạn, chủ dữ liệu duyệt."),
        N("x_2", "req", 362, 330, "GDV được giao gọi nhắc nợ một đợt → không cấp xuất; cho xem danh sách được giao trong hệ thống, TP KD duyệt."),
    ], [
        L("r_nv", "p_xem", **q("KH đơn vị mình", "TP KD")),
        L("r_nv", "p_sua", **q("Hồ sơ được giao", "TP KD")),
        L("r_tp", "p_xem", **q("KH đơn vị mình", "GĐ")),
        L("r_tp", "p_sua", **q("Theo chức trách", "GĐ")),
        L("r_tp", "p_xuat", **q("Đơn vị mình, có lý do", "GĐ")),
        L("r_tp", "p_cap", **q("Duyệt, không tự làm", "chủ dữ liệu")),
        L("r_tn", "p_xem", **q("KH đơn vị mình", "TP KD")),
        L("r_tn", "p_xuat", **q("DS nợ, cột cố định", "TP KD")),
        L("r_cntt", "p_xem", **q("Khi có phiếu", "TP CNTT")),
        L("r_cntt", "p_sua", **q("Phiếu đã duyệt", "TP CNTT")),
        L("r_qt", "p_cap", **q("Theo phiếu, có log", "người duyệt")),
        L("t_1", "r_nv"), L("t_2", "r_nv"), L("t_3", "r_cntt"), L("t_4", "r_nv"),
        L("x_1", "r_tp"), L("x_2", "r_nv"),
    ]),
     "ghi_chu": "Nhóm Chỉ số công tơ cần thêm quyền Sửa có đối soát: quản trị hệ thống không được sửa chỉ số khi không có yêu cầu nghiệp vụ "
                "được duyệt (thêm một trường hợp phải bị từ chối). Còn phân vân: trưởng phòng có cần quyền Sửa không hay chỉ duyệt."},
    modules=[
        ("📂 <b>Nhóm dữ liệu</b>", "Chọn “Khách hàng & hợp đồng” (nhãn Mật ở Thực hành 1).",
         "Chọn nhóm khác cũng được, nhưng ma trận phải khớp nhóm đã chọn."),
        ("👤 <b>Năm vai trò</b>", "Một câu: công việc chính cần dữ liệu gì.", "Viết đúng công việc thì mới thấy vai trò nào không cần xuất."),
        ("🔑 <b>Bốn thao tác</b>", "Điều kiện chung: xem theo đơn vị; sửa có lưu vết; xuất có lý do và mẫu cột; cấp quyền tách người duyệt và người làm.",
         "Tiêu chí “quyền xuất và cấp quyền tách khỏi quyền xem”."),
        ("🚫 <b>Phải bị từ chối</b> (4)", "Khác đơn vị; GDV xuất toàn đơn vị; CNTT xuất không phiếu; tự cấp quyền.",
         "Cộng thêm: quản trị hệ thống sửa chỉ số công tơ khi không có yêu cầu được duyệt."),
        ("✋ <b>Phải xin thêm quyền</b> (2)", "Quyền tạm có hạn cho đoàn kiểm tra; nhắc nợ một đợt không cấp xuất.",
         "Mỗi ô ghi đủ: ai – cần gì – ai duyệt – đến khi nào."),
    ],
    more=[("Ma trận C3 mong đợi", [
        TABLE(["Vai trò", "Xem", "Sửa", "Xuất", "Cấp quyền"],
              ["Nhân viên nghiệp vụ", "KH đơn vị mình – duyệt: TP KD", "Hồ sơ được giao – duyệt: TP KD", "Không", "Không"],
              ["Trưởng phòng KD", "KH đơn vị mình", "Theo chức trách", "Đơn vị mình, ghi lý do – duyệt: GĐ", "Duyệt đề nghị, không tự cấu hình"],
              ["Chuyên viên thu nợ", "KH đơn vị mình – duyệt: TP KD", "Không", "DS nợ, mẫu cột cố định – duyệt: TP KD", "Không"],
              ["Cán bộ CNTT hỗ trợ", "Khi có phiếu – duyệt: TP CNTT", "Khi có phiếu đã duyệt", "Không", "Không"],
              ["Quản trị hệ thống", "Không mặc định", "Không mặc định", "Không", "Thực thi theo phiếu; có log riêng"]),
        P("Trên bảng: có dây là có quyền. Ô “Không” trong ma trận nghĩa là <b>không có dây</b>. Người duyệt của trưởng phòng ghi “Giám đốc” "
          "hoặc “theo bổ nhiệm” đều được."),
    ])],
    rubric=[
        ("Không có toàn quyền thiếu lý do", "2", "Không vai trò nào nối cả 4 thao tác mà không có lý do."),
        ("Tách xuất và cấp quyền", "3", "Xuất chỉ ở trưởng phòng và thu nợ; cấp quyền tách người duyệt (TP) và người thực thi (QT)."),
        ("Phạm vi và người duyệt", "2", "Mọi dây quyền ghi phạm vi và người duyệt."),
        ("Kiểm thử quyền", "3", "Ít nhất 3 trường hợp từ chối và 2 xin thêm, nối đúng vai trò."),
    ],
    mistakes=[
        ("Nhiều vai trò được Xuất", "Có cảnh báo ⚠ ở thẻ Xuất", "“Vai trò nào thật sự cần mang dữ liệu ra khỏi hệ thống?”"),
        ("CNTT được xuất", "Dây CNTT → Xuất, có ⚠", "“Hỗ trợ kỹ thuật cần file khách hàng làm gì? Theo phiếu nào?”"),
        ("Quản trị xem dữ liệu khách hàng", "Dây Quản trị → Xem, có ⚠", "“Cấu hình hệ thống có cần đọc hồ sơ khách hàng không?”"),
        ("Dây không ghi phạm vi", "Ô vàng trong ma trận", "“Xem khách hàng nào? Ai duyệt?”"),
        ("Xin thêm quyền không có hạn", "Ô ✋ không có ngày hết hạn", "“Quyền tạm này kết thúc khi nào, ai gỡ?”"),
    ],
    flow=["Chiếu ma trận của một bài cho nhiều vai trò được Xuất; hỏi lớp ai thật sự cần.",
          "Mở bảng mẫu, đọc ma trận C3 ở dưới; nhấn mạnh ô “Không” là không có dây.",
          "Đọc 4 trường hợp từ chối: mỗi trường hợp là một phép thử bằng tài khoản thật sau khi cấu hình.",
          "Nối sang Thực hành 4: chị Hà chuyển đơn vị là trường hợp “xin thêm quyền” có hạn."],
)


def actor_step(a, b, viec):
    return L(a, b, viec=viec)


# ---------- Thực hành 4: chuyển đơn vị còn quyền cũ ----------
KEY_TH4 = key(
    "Chị Hà chỉ cần xem 37 hồ sơ khiếu nại để bàn giao. Gỡ ngay quyền xuất và quyền xem toàn Điện lực X; nếu chưa giao được hồ sơ thì "
    "ngoại lệ chỉ xem 37 hồ sơ, có người duyệt và hạn 2 tuần. Cấp vai trò mới ở Điện lực Y theo ma trận. Kiểm tra bằng tài khoản chị Hà, "
    "lưu báo cáo quyền trước – sau, phiếu ngoại lệ, log gỡ quyền.",
    {"so_do_xu_ly": board([
        N("a_ha", "actor", 42, 66, "Muốn: bàn giao xong 37 hồ sơ, bắt đầu việc mới. Lo: mất quyền khi người kế nhiệm chưa nắm hồ sơ."),
        N("a_tuan", "actor", 42, 240, "Muốn: 37 khiếu nại xử lý đúng hạn. Lo: người kế nhiệm chưa nắm lịch sử hồ sơ."),
        N("a_y", "actor", 42, 394, "Muốn: chị Hà đúng quyền, tập trung việc mới. Lo: tài khoản của phòng giữ dữ liệu đơn vị khác."),
        N("a_cntt", "actor", 42, 588, "Muốn: phiếu duyệt rõ gỡ gì, cấp gì, hạn nào. Lo: ngoại lệ không có hạn, không ai nhớ gỡ."),
        N("q_xem", "right", 402, 70, "Chỉ xem đúng 37 hồ sơ, không sửa, hết hạn sau 2 tuần.", tag="Thu hẹp"),
        N("q_moi", "newright", 752, 70, "Theo ma trận phòng Kế hoạch Điện lực Y; không sao chép quyền cũ.", tag="Cấp mới"),
        N("q_xuat", "right", 1102, 70, "Gỡ ngay. Bàn giao không cần mang dữ liệu ra ngoài.", tag="Thu hồi"),
        N("b_nhu_cau", "step", 392, 345, "Lập danh sách mã 37 hồ sơ và việc còn lại. Chỉ cần xem. Xong trong ngày đầu."),
        N("b_cap_moi", "step", 392, 560, "Gán vai trò Kế hoạch – Điện lực Y theo ma trận quyền."),
        N("b_duyet", "step", 1050, 345, "Phiếu ngoại lệ: 37 hồ sơ, chỉ xem, hạn 2 tuần."),
        N("b_thu_hoi", "step", 1050, 478, "Gỡ xuất và xem toàn X; ngoại lệ tự hết hạn."),
        N("b_kiem_tra", "step", 1050, 611, "Thử: ngoài 37 hồ sơ, xuất → bị từ chối."),
        N("e_1", "evidence", 1462, 70, "Báo cáo quyền tài khoản chị Hà trước và sau.", title="Báo cáo quyền trước – sau"),
        N("e_2", "evidence", 1462, 240, "Phạm vi, người duyệt, ngày giờ hết hạn.", title="Phiếu ngoại lệ đã ký"),
        N("e_3", "evidence", 1462, 410, "Ngày giờ, người thực hiện; log đóng ngoại lệ khi hết hạn.", title="Log gỡ quyền"),
        N("e_4", "evidence", 1462, 580, "Ảnh màn hình bị từ chối khi mở hồ sơ ngoài phạm vi, khi xuất.", title="Kết quả phép thử"),
    ], [
        L("b_nhu_cau", "b_duyet"), L("b_duyet", "b_thu_hoi"), L("b_thu_hoi", "b_cap_moi"), L("b_cap_moi", "b_kiem_tra"),
        actor_step("a_tuan", "b_nhu_cau", "thực hiện"), actor_step("a_ha", "b_nhu_cau", "xác nhận"),
        actor_step("a_tuan", "b_duyet", "duyệt"), actor_step("a_y", "b_duyet", "đồng ý"),
        actor_step("a_cntt", "b_thu_hoi", "thực hiện"), actor_step("a_y", "b_cap_moi", "duyệt"),
        actor_step("a_cntt", "b_kiem_tra", "thực hiện"), actor_step("a_ha", "b_kiem_tra", "xác nhận"),
        L("e_1", "q_xuat", ghi_chu="quyền xuất đã gỡ"), L("e_2", "b_duyet", ghi_chu="ngoại lệ hẹp, có hạn"),
        L("e_3", "b_thu_hoi", ghi_chu="đã gỡ thật"), L("e_4", "b_kiem_tra", ghi_chu="quyền cũ hết dùng được"),
    ]),
     "tom_tat": "Chị Hà chỉ cần xem 37 hồ sơ khiếu nại đang dở để bàn giao, không cần sửa hay xuất. Cán bộ CNTT gỡ ngay quyền xuất và "
                "quyền xem toàn bộ khách hàng Điện lực X; nếu chưa giao được hồ sơ cho người kế nhiệm, anh Tuấn và chủ sở hữu dữ liệu duyệt "
                "ngoại lệ chỉ xem đúng 37 hồ sơ, hết hạn sau 2 tuần. Chị Hà được cấp vai trò Kế hoạch – Điện lực Y theo ma trận quyền. "
                "Kiểm tra bằng tài khoản chị Hà: hồ sơ ngoài 37 hồ sơ và thao tác xuất đều phải bị từ chối. Lưu báo cáo quyền trước – sau, "
                "phiếu ngoại lệ và log gỡ quyền làm bằng chứng."},
    modules=[
        ("👤 <b>Bốn người liên quan</b>", "Mỗi người: muốn gì, lo ngại gì.",
         "Xem xét đủ góc nhìn mới thấy phương án “giao hồ sơ cho người kế nhiệm” tốt hơn ngoại lệ."),
        ("🔑 <b>Xem toàn bộ KH Điện lực X</b>", "<b>Thu hẹp</b>: chỉ 37 hồ sơ, chỉ xem, hạn 2 tuần.",
         "Chọn <b>Thu hồi</b> cũng đạt nếu bài ghi giao 37 hồ sơ cho người kế nhiệm. Giữ nguyên là sai (có ⚠)."),
        ("🔑 <b>Xuất dữ liệu KH Điện lực X</b>", "<b>Thu hồi</b> ngay.", "Không có lý do nào để giữ quyền xuất khi bàn giao."),
        ("➕ <b>Vai trò Kế hoạch – Điện lực Y</b>", "<b>Cấp mới</b> theo ma trận.", "Không “cấp giống người cũ”."),
        ("🧭 <b>Năm bước</b>", "Nhu cầu → duyệt ngoại lệ (có thể không cần nếu giao được người kế nhiệm) → thu hồi, đăng xuất phiên → "
         "cấp mới → kiểm tra bằng tài khoản chị Hà: ngoài 37 hồ sơ và xuất bị từ chối, chức năng Điện lực Y được phép; ngày hết hạn thử lại.",
         "Bước kiểm tra phải có phép thử <b>bị từ chối</b>, không chỉ “kiểm tra lại”. Trên bảng mẫu chữ được rút gọn cho vừa thẻ."),
        ("📋 <b>Bằng chứng</b> (4)", "Báo cáo quyền trước – sau; phiếu ngoại lệ; log gỡ quyền; kết quả phép thử.",
         "Email đề nghị gỡ quyền <b>không</b> phải bằng chứng hoàn tất: chỉ cho thấy có người yêu cầu."),
    ],
    links=[
        ("Bước → bước (4 dây)", "—", "Chuỗi theo thứ tự 1 → 5."),
        ("Anh Tuấn → Nhu cầu, Duyệt", "thực hiện; duyệt", "Quản lý cũ chịu trách nhiệm phạm vi bàn giao."),
        ("Chị Hà → Nhu cầu, Kiểm tra", "xác nhận", "Người dùng xác nhận danh sách và kết quả thử."),
        ("Quản lý Điện lực Y → Duyệt, Cấp mới", "đồng ý; duyệt", "Đồng ý cho chị Hà dành thời gian bàn giao; duyệt vai trò mới."),
        ("CNTT → Thu hồi, Kiểm tra", "thực hiện", "Làm theo phiếu đã duyệt, không tự quyết."),
        ("Bằng chứng → quyền hoặc bước", "chứng minh điều gì", "Mỗi bằng chứng nối với đúng việc nó chứng minh."),
    ],
    rubric=[
        ("Góc nhìn", "1", "Đủ 4 người, mỗi người có mong muốn và lo ngại."),
        ("Quyết định quyền", "2", "Xem thu hẹp (hoặc thu hồi có lý do), xuất thu hồi, vai trò mới cấp theo ma trận."),
        ("Ngoại lệ", "2", "Có phạm vi đúng 37 hồ sơ, chỉ xem, người duyệt, ngày hết hạn."),
        ("Chuỗi bước và người phụ trách", "2", "5 bước nối đúng thứ tự, mỗi bước có người và vai trò trên dây."),
        ("Kiểm tra", "1,5", "Có phép thử phải bị từ chối và thử lại khi ngoại lệ hết hạn."),
        ("Bằng chứng", "1,5", "Ít nhất 2 bằng chứng cụ thể, nối đúng; không dùng email đề nghị."),
    ],
    mistakes=[
        ("Giữ nguyên quyền “cho tiện”", "Thẻ quyền chọn Giữ nguyên, có ⚠",
         "“Vấn đề không phải chị Hà có đáng tin không, mà là nếu tài khoản bị chiếm thì kẻ gian có thêm dữ liệu cả một đơn vị.”"),
        ("Ngoại lệ không có hạn", "Bước duyệt không ghi ngày", "“Ai nhớ gỡ, vào ngày nào?”"),
        ("Kiểm tra chung chung", "“Kiểm tra lại quyền”", "“Thử thao tác nào, kết quả mong đợi là gì?”"),
        ("Bằng chứng là email", "“Email đề nghị CNTT gỡ quyền”", "“Email cho biết đã làm xong chưa?”"),
        ("CNTT tự quyết", "CNTT duyệt ngoại lệ", "“CNTT thực hiện theo phiếu; ai có thẩm quyền duyệt?”"),
    ],
    flow=["Cho một học viên đóng vai anh Tuấn nói “cứ để nguyên cho tiện”; lớp phản biện.",
          "Mở bảng mẫu: đi từ ba thẻ quyền sang chuỗi 5 bước.",
          "Dừng ở bước kiểm tra: phép thử nào phải bị từ chối.",
          "Đọc 4 bằng chứng; hỏi vì sao email đề nghị không đủ."],
)


# ---------- Bài tập thêm: cấp quyền đủ để bàn giao (bảng) ----------
KEY_CASE3 = key(
    "Ưu tiên giao 12 hồ sơ cho người kế nhiệm. Nếu cần ngoại lệ: chỉ xem đúng 12 hồ sơ đến hết 30/10; gỡ quyền xuất và xem toàn X. "
    "Chủ dữ liệu và quản lý duyệt, CNTT cấu hình; lưu phiếu, báo cáo quyền trước – sau, kết quả thử. "
    "Thử một hồ sơ trong danh sách (được), ngoài danh sách và xuất (bị từ chối), và thử lại sau khi hết hạn.",
    {"phuong_an": board([
        N("q_xem", "right", 42, 70, "Gỡ xem toàn X; chỉ còn 12 hồ sơ qua ngoại lệ ②.", tag="Thu hẹp"),
        N("q_xuat", "right", 42, 256, "Gỡ ngay; bàn giao không cần xuất.", tag="Thu hồi"),
        N("g_ngoai_le", "grant", 42, 500, "Chỉ dùng khi chưa giao được hồ sơ cho người kế nhiệm.",
          p={"pham_vi": "Đúng 12 hồ sơ trong danh sách bàn giao", "thao_tac": "Chỉ xem, ghi chú bàn giao", "het_han": "23:59 ngày 30/10"}),
        N("a_chu", "actor", 482, 70, "Duyệt phạm vi và hạn ngoại lệ."),
        N("a_ql", "actor", 482, 240, "Lập danh sách 12 hồ sơ; ưu tiên giao người kế nhiệm."),
        N("a_cntt", "actor", 482, 410, "Gỡ quyền, cấu hình ngoại lệ tự hết hạn, lưu log."),
        N("a_ha", "actor", 482, 580, "Chỉ bàn giao; xác nhận kết quả thử."),
        N("e_1", "evidence", 922, 70, "Tài khoản chị Hà trước và sau khi gỡ.", title="Báo cáo quyền trước – sau"),
        N("e_2", "evidence", 922, 240, "Phạm vi 12 hồ sơ, thao tác, hạn, người duyệt.", title="Phiếu ngoại lệ đã ký"),
        N("e_3", "evidence", 922, 410, "Log cấu hình, ảnh bị từ chối khi thử.", title="Log và kết quả phép thử"),
        N("t_1", "test", 1372, 60, "Mở một hồ sơ trong danh sách 12 hồ sơ.", tag="Được phép"),
        N("t_2", "test", 1372, 250, "Mở một hồ sơ Điện lực X ngoài danh sách.", tag="Phải bị từ chối"),
        N("t_3", "test", 1372, 440, "Xuất danh sách khách hàng Điện lực X.", tag="Phải bị từ chối"),
    ], [
        L("a_chu", "g_ngoai_le", viec="duyệt"), L("a_ql", "g_ngoai_le", viec="đề xuất, cùng duyệt"),
        L("a_cntt", "g_ngoai_le", viec="cấu hình"), L("a_cntt", "q_xuat", viec="gỡ ngay"), L("a_cntt", "q_xem", viec="gỡ xem toàn X"),
        L("a_cntt", "e_3", viec="lưu"), L("a_ql", "e_2", viec="lưu"),
        L("t_1", "g_ngoai_le"), L("t_2", "q_xem"), L("t_3", "q_xuat"),
    ]),
     "giai_thich": "Nếu giao được 12 hồ sơ cho người kế nhiệm thì không cần ngoại lệ: chọn Thu hồi cả hai quyền. "
                   "Không chấp nhận đề nghị giữ nguyên quyền thêm một tháng vì vượt cả phạm vi (toàn X) lẫn thời gian (sau 30/10). "
                   "Sáng 31/10 làm lại phép thử 1: lần này phải bị từ chối, chứng tỏ ngoại lệ đã tự hết hạn."},
    modules=[
        ("🔑 <b>Quyền hiện tại</b>", "Xem: Thu hẹp (hoặc Thu hồi). Xuất: Thu hồi.", "Giữ nguyên bất kỳ quyền nào là sai (có ⚠)."),
        ("⏳ <b>Ngoại lệ</b>", "Phạm vi 12 hồ sơ; chỉ xem; hết hạn 23:59 ngày 30/10.", "Hạn phải là ngày giờ cụ thể, không “khi xong việc”."),
        ("👤 <b>Bốn người</b>", "Chủ dữ liệu duyệt, quản lý đề xuất, CNTT cấu hình, chị Hà xác nhận.", "Người duyệt khác người cấu hình."),
        ("📋 <b>Bằng chứng</b>", "Báo cáo quyền trước – sau; phiếu; log và kết quả thử.", "Email đề nghị không phải bằng chứng hoàn tất."),
        ("🧪 <b>Phép thử</b>", "Trong danh sách: được. Ngoài danh sách, xuất: bị từ chối.",
         "Thử lại phép thử 1 sau 30/10 (ghi ở ô giải thích) là điểm cộng."),
    ],
    rubric=[
        ("Hiểu đúng tình huống", "3", "Thấy được 12 hồ sơ, hạn 30/10, đề nghị “giữ một tháng” là quá rộng."),
        ("Đề xuất phù hợp, có lý do", "4", "Gỡ xuất, thu hẹp xem; ngoại lệ đủ phạm vi, thao tác, hạn; người duyệt và người cấu hình nối vào."),
        ("Kiểm chứng được kết quả", "3", "Đủ 3 phép thử có kết quả mong đợi, nối đúng quyền; ít nhất 2 bằng chứng."),
    ],
    mistakes=[
        ("Đồng ý giữ quyền một tháng", "Ngoại lệ hết hạn cuối tháng 11", "“Hồ sơ chỉ cần đến 30/10. Một tháng thêm để làm gì?”"),
        ("Phép thử không có kết quả mong đợi", "Thẻ phép thử chưa chọn kết quả", "“Thử xong, thế nào là đạt?”"),
        ("Phép thử không nối", "Thẻ 🧪 không có dây", "“Phép thử này kiểm tra quyền nào?”"),
    ],
)

KEYS = {"m03-th3": KEY_TH3, "m03-th4": KEY_TH4, "m03-case-v2": KEY_CASE3}
