"""Đáp án giảng viên – buổi 7 (bài lớn và bài tình huống; bài ngắn Power BI ở labs.py)."""
from .kit import L, N, P, TABLE, board, case_key, key


def acc(id, x, y, text, ws, ky_vong, thuc_te, dat, title=None):
    return N(id, "acc", x, y, text, title=title, p={"ws": ws, "ky_vong": ky_vong, "thuc_te": thuc_te, "dat": dat})


# ---------- Thực hành 8: kiểm thử RLS ----------
KEY_TH8 = key(
    "Kiểm thử cả được phép lẫn bị từ chối, đọc số trên thẻ để biết tài khoản thấy bao nhiêu (DV_A 826.436; DV_B 742.030; cả hai 1.568.466 kWh). "
    "Hai lỗi chỉ lộ ra khi kiểm thử: Member của workspace không chịu RLS; bảng PhanQuyen còn dòng cũ của chị Hà.",
    {"kiem_thu_rls": board([
        acc("a_A", 42, 70, "Anh Tuấn, cấu hình đúng; thử trên service.", "Viewer", "Chỉ DV_A: 826.436 kWh",
            "826.436 kWh; slicer chỉ còn Điện lực X", "Đạt"),
        acc("a_B", 42, 270, "Trưởng phòng Điện lực Y.", "Viewer", "Chỉ DV_B: 742.030 kWh", "742.030 kWh", "Đạt"),
        acc("a_none", 42, 470, "Không gán role nào: mặc định từ chối.", "Viewer", "Không thấy dữ liệu", "Báo cáo trống", "Đạt"),
        acc("a_mem", 42, 670, "Tái hiện lỗi chương 7: thêm làm Member.", "Member", "Theo nghiệp vụ: chỉ DV_A",
            "1.568.466 kWh – thấy cả hai → gỡ khỏi workspace, phân phối qua App", "Không đạt", title="tuan_member"),
        N("r_A", "role", 442, 66, "Bảng DimDonVi, lọc DV_A."),
        N("r_B", "role", 442, 196, "Bảng DimDonVi, lọc DV_B."),
        N("r_dyn", "role", 442, 326, "Lọc theo email đăng nhập qua PhanQuyen; bảng PhanQuyen ẩn. moi.vao (không có trong bảng): trống – Đạt."),
        acc("a_minh", 442, 500, "Phòng Kế hoạch Công ty.", "Viewer", "DV_A và DV_B", "1.568.466 kWh", "Đạt", title="minh.kehoach (RLS động)"),
        acc("a_ha", 442, 683, "Đã chuyển sang Điện lực Y.", "Viewer", "Chỉ DV_B", "1.568.466 kWh – thấy cả DV_A → xóa dòng ha – DV_A",
            "Không đạt", title="ha.kehoach (RLS động)"),
        N("d_X", "data", 856, 80, "826.436 kWh quý III."),
        N("d_Y", "data", 856, 300, "742.030 kWh quý III."),
        N("c1", "step", 1210, 80, "Người thấy báo cáo công khai (đồng nghiệp, khách hàng) báo quản lý và chị Lan."),
        N("c2", "step", 1480, 80, "Chị Lan báo người có thẩm quyền trên workspace và lãnh đạo phụ trách."),
        N("c3", "step", 1210, 360, "Xóa mã nhúng hoặc thu hồi liên kết ngay; giữ ảnh chụp, xin nhật ký hoạt động: ai đã xem, xuất."),
        N("c4", "step", 1480, 360, "Xác định dữ liệu đã lộ (số tổng hợp theo phường); rà quyền workspace; đề nghị giới hạn Publish to web; ghi nhận sự cố."),
    ], [
        L("a_A", "r_A"), L("a_B", "r_B"), L("a_mem", "r_A"), L("a_minh", "r_dyn"), L("a_ha", "r_dyn"),
        L("r_A", "d_X", quy_tac='[MaDonVi] = "DV_A"'), L("r_B", "d_Y", quy_tac='[MaDonVi] = "DV_B"'),
        L("r_dyn", "d_X", quy_tac="theo email (PhanQuyen)"), L("r_dyn", "d_Y", quy_tac="theo email (PhanQuyen)"),
        L("c1", "c2"), L("c2", "c3"), L("c3", "c4"),
    ]),
     "slicer": "Không. Khi View as DonVi_A, slicer TenDonVi chỉ còn “Điện lực X”, vì dòng Điện lực Y đã bị RLS loại khỏi mô hình trước khi tới slicer. "
               "Ẩn hay hiện slicer không phải là cách bảo vệ; RLS mới là."},
    modules=[
        ("🧪 <b>Bốn tài khoản RLS tĩnh</b>", "nguoixem_A, nguoixem_B, khong_gan, tuan_member; vai trò workspace và kết quả C8.",
         "Phải có ít nhất một trường hợp <b>bị từ chối</b> (khong_gan). Cảnh báo ⚠ về Member hiện đúng thiết kế: bài mẫu cố ý thử Member."),
        ("🧪 <b>Hai tài khoản RLS động</b>", "minh.kehoach (Đạt), ha.kehoach (Không đạt).",
         "Đặt ở cột Role cho gọn vì cột Tài khoản thử hết chỗ. Tìm ra dòng cũ của chị Hà là mức Tốt."),
        ("🛡️ <b>Ba role</b>", "DonVi_A, DonVi_B trên DimDonVi; NguoiXem lọc theo email qua PhanQuyen.", "Bảng PhanQuyen phải ẩn khỏi báo cáo."),
        ("🏢 <b>Hai đơn vị dữ liệu</b>", "Ghi tổng kWh để đối chiếu nhanh.", "Nhìn số trên thẻ là biết tài khoản thấy bao nhiêu."),
        ("🚨 <b>Bốn bước chia sẻ nhầm</b>", "Ai phát hiện → báo ai → thu hồi và giữ bằng chứng → xác định phạm vi, rà quyền, ghi nhận.",
         "Thu hồi trước, không chờ họp; nhưng giữ ảnh và nhật ký."),
    ],
    links=[
        ("Tài khoản → role", "—", "Có dây nghĩa là được gán role. khong_gan không có dây (nối là sai, có ⚠)."),
        ("DonVi_A → Điện lực X", '[MaDonVi] = "DV_A"', "Quy tắc trên DimDonVi; quan hệ 1 → nhiều tới FactDien phải đang bật."),
        ("DonVi_B → Điện lực Y", '[MaDonVi] = "DV_B"', ""),
        ("NguoiXem → hai đơn vị", "theo email (PhanQuyen)",
         "Quy tắc trên PhanQuyen: [Email] = USERPRINCIPALNAME(). Đơn vị thấy được tùy dòng của người đó trong PhanQuyen."),
        ("Bước 1 → 4", "—", "Dây dựng sẵn."),
    ],
    more=[("Ma trận C8 mong đợi", [
        TABLE(["Tài khoản", "Workspace", "Role", "Kỳ vọng", "Thực tế", "Đạt"],
              ["nguoixem_A", "Viewer / qua App", "DonVi_A", "Chỉ DV_A: 826.436", "826.436", "Đạt"],
              ["nguoixem_B", "Viewer", "DonVi_B", "Chỉ DV_B: 742.030", "742.030", "Đạt"],
              ["khong_gan", "Viewer", "(không)", "Không thấy gì", "Trống", "Đạt"],
              ["tuan_member", "Member", "DonVi_A", "Chỉ DV_A", "1.568.466", "Không đạt"],
              ["bientap_A (tùy chọn)", "Contributor", "DonVi_A", "Thấy tất cả (đúng thiết kế)", "1.568.466", "Đạt"],
              ["minh.kehoach", "Viewer", "NguoiXem", "DV_A và DV_B", "1.568.466", "Đạt"],
              ["ha.kehoach", "Viewer", "NguoiXem", "Chỉ DV_B", "1.568.466", "Không đạt"],
              ["moi.vao", "Viewer", "NguoiXem", "Không thấy gì", "Trống", "Đạt"]),
        P("Lớp chưa có Power BI service: chấp nhận ghi “chưa kiểm thử trên service” cho dòng Member, vì View as trên Desktop không phát hiện được lỗi này."),
    ])],
    rubric=[
        ("RLS tĩnh", "2", "Nối đúng tài khoản → role → đơn vị, quy tắc lọc đúng cột MaDonVi."),
        ("Được phép và bị từ chối", "2", "Ma trận có khong_gan (hoặc người mới) bị từ chối."),
        ("Số liệu kiểm tra", "2", "Thực tế ghi bằng số kWh, không ghi “thấy đúng”."),
        ("RLS động và lỗi cấu hình", "2", "Tìm ra dòng cũ của chị Hà; có dòng Member (hoặc ghi rõ chưa thử trên service)."),
        ("Chia sẻ nhầm và slicer", "2", "Đủ 4 bước, thu hồi kèm giữ bằng chứng; trả lời slicer đúng lý do."),
    ],
    mistakes=[
        ("Quan hệ bị tắt, View as vẫn ra 1.568.466", "Ghi “RLS không chạy”", "“Mở tab Model: quan hệ DimDonVi – FactDien có đường liền không?”"),
        ("Thẻ số khách hàng 2.208", "Thực tế ghi 2.208", "Dùng thước đo bình quân tháng, không cộng dồn 3 tháng (đúng là 736)."),
        ("Chỉ thử trường hợp được phép", "Không có khong_gan, moi.vao", "“Người không có quyền thấy gì?”"),
        ("Kiểm thử bằng tài khoản Admin", "“Tôi vẫn thấy tất cả”", "Admin luôn thấy tất cả; dùng Test as role hoặc tài khoản Viewer."),
        ("Không ẩn PhanQuyen", "Bảng phân quyền hiện trong báo cáo", "“Người xem có đọc được danh sách phân quyền không?”"),
    ],
    flow=["Trên Desktop, View as DonVi_A: lớp đọc số trên thẻ.",
          "View as Other user ha.kehoach: thấy 1.568.466 – hỏi vì sao.",
          "Mở bảng mẫu, đọc ma trận C8; dừng ở hai dòng Không đạt.",
          "Hỏi: cả hai lỗi có lộ ra khi người làm báo cáo tự xem không? (Không – họ luôn thấy tất cả.)"],
)

# ---------- Bài tập thêm: đọc bảng kiểm thử phân quyền báo cáo ----------
KEY_CASE7 = case_key(
    "Lan đúng kỳ vọng; Bình là Member nên RLS không giới hạn – sai quyền nghiệp vụ; Mai bị từ chối là đúng nguyên tắc mặc định; "
    "Hà là lỗi bảng ánh xạ còn quyền cũ. Sửa Bình về Viewer, xóa dòng cũ của Hà, thử lại trên service gồm cả xem, xuất và người chưa được cấp quyền.",
    ["(1) Lan, Viewer, RLS X → thấy X: đúng kỳ vọng.\n"
     "(2) Bình, Member, RLS Y → thấy X và Y: sai quyền nghiệp vụ. Member có quyền sửa workspace nên RLS không giới hạn như Viewer.\n"
     "(3) Mai, chưa có trong bảng ánh xạ → không thấy dữ liệu: đúng nguyên tắc mặc định từ chối; cần xác minh lại trên mô hình thật.\n"
     "(4) Hà đã chuyển sang Y, bảng ánh xạ còn ghi X → vẫn thấy X: sai, lỗi bảng ánh xạ không cập nhật khi điều chuyển.",
     "Bình: nếu chỉ cần xem thì gỡ khỏi Member, cấp Viewer hoặc phân phối qua App. Chủ báo cáo / quản lý duyệt; quản trị workspace thực hiện.\n"
     "Hà: xóa dòng Hà – X, thêm dòng Hà – Y trong bảng phân quyền. Quản lý Điện lực Y xác nhận, người quản lý mô hình thực hiện; "
     "gắn việc cập nhật bảng vào quy trình điều chuyển nhân sự.",
     "Thử trên Power BI service bằng tài khoản thử, không dùng View as trên Desktop:\n"
     "☐ Bình (sau khi đổi Viewer): chỉ thấy Y.\n☐ Hà (sau khi sửa bảng): chỉ thấy Y, không thấy X.\n"
     "☐ Mai và một người mới: không thấy dữ liệu.\n"
     "☐ Thử xuất dữ liệu (Export data) bằng tài khoản Viewer: chỉ xuất được phần được thấy.\n"
     "☐ Thử mở link chia sẻ bằng tài khoản không được cấp quyền: bị từ chối.\nGhi kỳ vọng, thực tế, đạt cho từng dòng."],
    [("1. Nhận xét 4 lượt", "Lan đúng; Bình sai vì Member; Mai đúng (mặc định từ chối); Hà sai vì bảng ánh xạ cũ.", "Mai cần xác minh trên mô hình thật."),
     ("2. Sửa Bình và Hà", "Bình về Viewer / App; Hà xóa dòng X. Có người duyệt và người thực hiện.", "Gắn vào quy trình điều chuyển."),
     ("3. Phép thử lại", "Trên service; có xem, xuất và người chưa được cấp quyền.", "Thử link chia sẻ.")],
    ["Hiểu RLS không áp với Member và bảng ánh xạ là nguồn quyền của RLS động.",
     "Cách sửa đúng gốc, có người duyệt và người thực hiện.",
     "Phép thử lại trên service, có cả xuất và người không có quyền, có kỳ vọng rõ."],
    [("Sửa quy tắc DAX cho Bình", "“Viết lại quy tắc lọc”", "“Quy tắc có sai không? Vai trò workspace của Bình là gì?”"),
     ("Coi Mai là lỗi", "“Mai phải thấy dữ liệu”", "“Người chưa được cấp quyền thì nên thấy gì?”"),
     ("Thử lại bằng View as", "Không nhắc service", "“View as có tái hiện được lỗi Member không?”")],
)

KEYS = {"m07-th8": KEY_TH8, "m07-case-v2": KEY_CASE7}
