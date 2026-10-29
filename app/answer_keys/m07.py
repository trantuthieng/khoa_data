"""Đáp án giảng viên – buổi 7 (bài lớn và bài tình huống; bài ngắn Power BI ở labs.py)."""
from .kit import LAB_SOLUTION, L, N, P, TABLE, board, case_key, key


LAB_TH8 = '<a href="/static/labs/rls/index.html?bai=th8" target="_blank" rel="noopener">phòng thí nghiệm RLS – Thực hành 8</a>'


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
    ]), ("Làm trên phòng thí nghiệm RLS (bài mẫu từng bước)", [
        LAB_SOLUTION("th8"),
        P(f'Học viên mở {LAB_TH8}. Bốn bảng đã nạp sẵn. Khung 📋 Đề bài có 10 mục tự kiểm tra: đủ ✓ là đạt phần thao tác. '
          "Tài khoản trên mô phỏng khác tên trong đề: Tuấn (tuan.truongphong) là người xem A, truongphong@dly là người xem B, khong.gan là người chưa gán role, bientap.a dùng để thử Member."),
        {"t": "list", "ordered": True, "items": [{"html": x, "level": 0} for x in [
            "Model view: quan hệ DimDonVi → PhanQuyen có nhãn “tự phát hiện” → Xóa. Giữ DimDonVi → FactDien và DimThang → FactDien.",
            "Home → New measure: <code>Tong kWh = SUM ( FactDien[kWh] )</code> và "
            "<code>So KH binh quan thang = AVERAGEX ( VALUES ( DimThang[Thang] ), CALCULATE ( SUM ( FactDien[SoKH] ) ) )</code>.",
            "Visualizations: Clustered bar (TenDonVi, Tong kWh); Card (So KH binh quan thang); Table (Phuong, Thang, Tong kWh); Slicer (DimDonVi[TenDonVi]).",
            'Modeling → Manage roles: DonVi_A trên DimDonVi <code>[MaDonVi] = "DV_A"</code>; DonVi_B tương tự; '
            "NguoiXem có hai quy tắc – DimDonVi: <code>[MaDonVi] IN CALCULATETABLE ( VALUES ( PhanQuyen[MaDonVi] ), PhanQuyen[Email] = USERPRINCIPALNAME () )</code>; "
            "PhanQuyen: <code>[Email] = USERPRINCIPALNAME ()</code>. Kiểm tra (✓) rồi Save.",
            "Data pane: bấm 👁 cạnh PhanQuyen (Hide in report view).",
            "Modeling → View as: DonVi_A, rồi DonVi_B. Sau đó Other user + NguoiXem lần lượt minh.kehoach, ha.kehoach, moi.vao.",
            "Home → Publish. Service → Security (RLS): thêm tuan.truongphong, truongphong@dly, minh.kehoach, ha.kehoach vào NguoiXem; không thêm khong.gan.",
            "Workspace → Manage access: các tài khoản trên và khong.gan làm Viewer. Thêm bientap.a làm Member để tái hiện lỗi; thử xong thì gỡ ra.",
            "Ô “Đang đăng nhập”: đổi lần lượt từng người, mở báo cáo. Ma trận kiểm thử tự ghi; bấm Chép (TSV) để dán vào bảng C8.",
            "Sửa lỗi chị Hà: Desktop → Table view → PhanQuyen → ✎ Sửa dữ liệu nguồn → xóa dòng ha.kehoach – DV_A → Publish lại → đăng nhập chị Hà lần nữa."]]},
        TABLE(["Bước kiểm thử trên mô phỏng", "Phải thấy (Tong kWh)", "Số KH bình quân tháng"],
              ["View as DonVi_A", "826.436, chỉ Điện lực X", "736"],
              ["View as DonVi_B", "742.030, chỉ Điện lực Y", "701"],
              ["Không View as (người làm báo cáo)", "1.568.466", "1.437"],
              ["View as Other user minh.kehoach + NguoiXem", "1.568.466", "1.437"],
              ["View as Other user ha.kehoach + NguoiXem (chưa sửa)", "1.568.466 – lỗi dòng cũ", "1.437"],
              ["View as Other user moi.vao + NguoiXem", "Trống", "—"],
              ["Service – đăng nhập tuan.truongphong (Viewer, NguoiXem)", "826.436", "736"],
              ["Service – đăng nhập truongphong@dly", "742.030", "701"],
              ["Service – đăng nhập khong.gan (Viewer, không role)", "“Không thể tải dữ liệu cho hình ảnh này”", "—"],
              ["Service – đăng nhập bientap.a (Member)", "1.568.466 – không chịu RLS", "1.437"],
              ["Service – đăng nhập ha.kehoach sau khi xóa dòng DV_A", "742.030", "701"]),
        P("Hai chỗ học viên hay vấp trên mô phỏng, giống hệt Power BI thật: "
          "(1) Test as role ra số đúng nhưng đăng nhập bằng chính người đó thì bị chặn – vì Test as role không thêm thành viên vào role; phải thêm ở Security. "
          "(2) Quên quy tắc trên PhanQuyen: một Table có Email, MaDonVi sẽ hiện quyền của cả công ty với mọi người xem. "
          "Thẻ số khách ra 2.208 khi View as DonVi_A (4.311 khi xem tất cả) là cộng dồn ba tháng: dùng SUM thay cho bình quân, hoặc thiếu CALCULATE trong AVERAGEX."),
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

# ---------- Phòng thí nghiệm RLS: rà soát báo cáo cài sẵn lỗi (kịch bản “rasoat” trong app/static/labs/rls/data.js) ----------
LAB = '<a href="/static/labs/rls/index.html?bai=rasoat" target="_blank" rel="noopener">kịch bản Rà soát</a>'

# (lỗi, cách tái hiện trên mô phỏng, thấy gì, sửa đúng gốc, buổi liên quan)
RASOAT = [
    ("Role <b>TatCa_TamThoi</b> (quy tắc <code>TRUE ()</code>) gán cho nhóm động Toan_Cong_Ty “để demo cho lãnh đạo” ngày 12/8, không gỡ",
     "Đăng nhập bất kỳ ai, ví dụ trưởng phòng Điện lực Y. Security: xem thành viên role. Nhật ký: CreateRole 12/8.",
     "Mọi tài khoản nội bộ đều thấy 1.568.466. Role này che lấp các lỗi RLS khác: vì hợp quyền, ai cũng thấy hết.",
     "Xóa role trên Desktop (Manage roles) rồi Publish, hoặc ít nhất gỡ nhóm khỏi role. Quyền tạm phải có ngày hết hạn và người gỡ.",
     "Buổi 3 (quyền đúng lúc, tích tụ quyền)"),
    ("Liên kết chia sẻ “Mọi người trong tổ chức” do anh Tuấn tạo, cho chia sẻ lại và Build",
     "Đăng nhập nv.kythuat (không làm kinh doanh) → Trang chủ thấy báo cáo, đường vào là liên kết.",
     "Nhân viên kỹ thuật mở được báo cáo, có Build nên dùng được Analyze in Excel.",
     "Xóa liên kết (Workspace → Liên kết chia sẻ). Phân phối qua App cho nhóm NguoiXem_BaoCao, không bật Build, không cho chia sẻ lại.",
     "Buổi 5 (chọn kênh chia sẻ), buổi 7"),
    ("Anh Tuấn là <b>Member</b> workspace (lỗi chương 7)",
     "Đăng nhập tuan.truongphong. Khung thông tin: “RLS KHÔNG áp dụng (Member)”.",
     "1.568.466 kWh, thấy cả Điện lực Y. Test as role NguoiXem với tên anh Tuấn lại cho kết quả đúng, nên dễ kết luận sai.",
     "Gỡ anh Tuấn khỏi Manage access; anh vẫn xem được qua nhóm NguoiXem_BaoCao (Viewer) và App.",
     "Buổi 7"),
    ("nhanvien.baocao chỉ cần xem số Điện lực X nhưng là <b>Contributor</b> “để sửa giúp tiêu đề”",
     "Đăng nhập nhanvien.baocao.",
     "Thấy cả hai đơn vị (Contributor không chịu RLS), sửa được báo cáo. Nhật ký: chính tài khoản này đã Publish to web bản nháp.",
     "Đổi về Viewer, thêm vào NguoiXem_BaoCao và thêm dòng PhanQuyen (nhanvien.baocao, DV_A). Chỉ đổi Viewer mà quên hai việc sau thì người này thấy báo cáo trống.",
     "Buổi 3 (quyền tối thiểu), buổi 7"),
    ("PhanQuyen còn dòng <b>ha.kehoach – DV_A</b> sau khi chị Hà chuyển sang Điện lực Y",
     "Sau khi sửa lỗi 1: đăng nhập ha.kehoach, hoặc View as Other user ha.kehoach + NguoiXem trên Desktop.",
     "1.568.466 thay vì 742.030.",
     "Desktop → Table view → PhanQuyen → Sửa dữ liệu nguồn: xóa dòng DV_A, Publish. Gắn việc cập nhật PhanQuyen vào quy trình Chuyển.",
     "Buổi 3 (Vào – Chuyển – Ra)"),
    ("Anh An <b>đã nghỉ việc</b> (tài khoản đã khóa) vẫn là Viewer, còn trong NguoiXem_BaoCao và PhanQuyen",
     "Entra ID: trạng thái Đã khóa. Manage access, nhóm, PhanQuyen vẫn còn tên. Đăng nhập: không được.",
     "Hiện không xem được vì tài khoản bị khóa. Nếu mở khóa nhầm hoặc dùng lại tên thì quyền cũ còn nguyên.",
     "Gỡ khỏi workspace, nhóm, PhanQuyen. Khóa tài khoản chưa đủ: thu hồi cả quyền (quy trình Ra, rà soát định kỳ).",
     "Buổi 3 (Ra, rà soát quyền)"),
    ("Tài khoản dùng chung <b>baocao.chung</b>: 5 người biết mật khẩu, không MFA, có cả DV_A và DV_B trong PhanQuyen",
     "Đăng nhập baocao.chung. Nhật ký: ExportReport lúc 21:15 ngày 18/9 bởi baocao.chung.",
     "Thấy cả hai đơn vị. Nhật ký không cho biết người thật nào đã xuất dữ liệu.",
     "Khóa tài khoản chung, xóa khỏi nhóm và PhanQuyen; mỗi người dùng tài khoản riêng có MFA.",
     "Buổi 4 (tài khoản dùng chung), buổi 9 (truy vết)"),
    ("Nhóm <b>KT_TongHop</b> là thành viên của cả DonVi_A và DonVi_B (role tĩnh cũ còn sót)",
     "Đăng nhập lan.ketoan (sau khi sửa lỗi 1).",
     "Chị Lan chỉ cần Điện lực X nhưng thấy 1.568.466: hai role cộng thành hợp quyền.",
     "Xóa hai role tĩnh cũ; đưa chị Lan vào NguoiXem_BaoCao (PhanQuyen đã có dòng DV_A). Một mô hình chỉ nên có một cách phân quyền.",
     "Buổi 3 (tích tụ quyền), buổi 7 (BI 08)"),
    ("Bảng <b>DSKhachHang</b> không có quan hệ tới DimDonVi",
     "Service → Security → Test as role NguoiXem, người cụ thể tuan.truongphong → trang “Tra cứu khách hàng”.",
     "Trang Sản lượng đúng (826.436) nhưng trang khách hàng hiện đủ 12 khách của cả hai đơn vị. RLS chỉ lọc qua quan hệ.",
     "Tốt nhất: bỏ bảng khỏi mô hình (báo cáo quản trị không cần danh sách khách). Nếu thật sự cần: tạo quan hệ DimDonVi[MaDonVi] → DSKhachHang[MaDonVi] rồi kiểm thử lại.",
     "Buổi 7 (BI 07), buổi 6 (giảm dữ liệu)"),
    ("Số điện thoại chỉ được <b>che trên hình ảnh</b> (cột tính toán SDT_hien_thi), cột gốc SoDienThoai vẫn nạp; CCCD chỉ “Hide in report view”",
     "Trên trang khách hàng: ⋯ → Export data → Underlying data. Hoặc Export → Analyze in Excel → bảng DSKhachHang.",
     "Tệp xuất có 0900000101…; Analyze in Excel thấy cả CCCD. Che hiển thị và ẩn cột không phải bảo vệ.",
     "Power Query: Remove column CCCD; che SoDienThoai trước khi nạp (masking tĩnh) hoặc bỏ hẳn. Chỉ nạp cột cần dùng.",
     "Buổi 6 (che tĩnh và che khi hiển thị, giảm dữ liệu)"),
    ("Bảng <b>PhanQuyen</b> không ẩn, role NguoiXem không có quy tắc trên PhanQuyen",
     "Đăng nhập bất kỳ ai có Build (ví dụ qua liên kết lỗi 2) → Analyze in Excel → PhanQuyen.",
     "Đọc được toàn bộ danh sách email và quyền của mọi người.",
     "Thêm quy tắc <code>[Email] = USERPRINCIPALNAME()</code> trên PhanQuyen trong role NguoiXem; ẩn bảng; không cấp Build cho người xem.",
     "Buổi 7 (mục 2.4)"),
    ("Bản sao <b>SanLuong_BanNhap</b> (mô hình không có role, có cả bảng khách hàng) đã <b>Publish to web</b>",
     "Đổi “Đang đăng nhập” sang Người ngoài internet → mở liên kết. Admin portal → Embed codes. Nhật ký 3/9.",
     "Người ngoài không đăng nhập vẫn thấy 1.568.466 và danh sách khách hàng. Publish to web chặn được báo cáo có RLS nhưng không chặn bản sao bỏ RLS.",
     "Xóa mã nhúng ngay, giữ ảnh chụp và nhật ký; xóa bản sao; tắt Publish to web ở tenant hoặc chỉ cho nhóm được duyệt. Xử lý như sự cố lộ dữ liệu (buổi 10).",
     "Buổi 5, buổi 7 (Bài 4)"),
    ("Nhãn độ nhạy <b>Công khai</b> cho báo cáo có dữ liệu khách hàng; tenant cho xuất dữ liệu gốc",
     "Tiêu đề báo cáo; tên tệp khi Export: “SanLuong_Q3 [Công khai].csv”. Admin portal.",
     "Tệp xuất ra mang nhãn sai, người nhận tưởng được phép chia sẻ tự do.",
     "Gắn nhãn Mật (có dữ liệu khách hàng) theo mô hình 4 mức; tắt xuất dữ liệu gốc hoặc chỉ cho nhóm cần.",
     "Buổi 1 (phân loại, nhãn), buổi 5"),
]

# Bài làm mẫu ngắn để vừa ô bảng: (lỗi, bằng chứng, nguyên nhân, cách sửa, buổi)
RASOAT_MAU = [
    ("Role tạm TatCa_TamThoi", "TP Điện lực Y thấy 1.568.466", "Role TRUE() gán nhóm toàn công ty, quên gỡ", "Xóa role, Publish lại", "Buổi 3 – quyền tối thiểu, Vào–Chuyển–Ra"),
    ("Liên kết toàn tổ chức", "nv.kythuat mở được báo cáo", "Share “Mọi người trong tổ chức”, cho Build", "Xóa liên kết, phân phối qua App", "Buổi 5 – chia sẻ an toàn"),
    ("Anh Tuấn là Member", "tuan: 1.568.466, không áp RLS", "Thêm Member “cho tiện”", "Gỡ khỏi workspace, xem qua App", "Buổi 7 – RLS, workspace, chia sẻ"),
    ("nhanvien.baocao là Contributor", "Thấy cả X, Y; đã Publish to web", "Cấp quyền sửa cho người chỉ cần xem", "Viewer + nhóm + dòng PhanQuyen DV_A", "Buổi 3 – quyền tối thiểu, Vào–Chuyển–Ra"),
    ("Dòng cũ của chị Hà", "ha: 1.568.466 thay vì 742.030", "Không cập nhật PhanQuyen khi chuyển", "Xóa dòng ha – DV_A", "Buổi 3 – quyền tối thiểu, Vào–Chuyển–Ra"),
    ("Anh An đã nghỉ còn quyền", "Entra: Đã khóa; vẫn Viewer, PhanQuyen", "Quy trình Ra chỉ khóa tài khoản", "Gỡ workspace, nhóm, PhanQuyen", "Buổi 3 – quyền tối thiểu, Vào–Chuyển–Ra"),
    ("Tài khoản dùng chung", "baocao.chung thấy X, Y; xuất 18/9", "5 người dùng chung, không MFA", "Khóa, gỡ quyền; mỗi người một tài khoản", "Buổi 4 – tài khoản dùng chung"),
    ("KT_TongHop trong hai role", "lan: 1.568.466, chỉ cần X", "Hai role cộng thành hợp quyền", "Xóa role tĩnh cũ, đưa Lan vào nhóm", "Buổi 3 – quyền tối thiểu, Vào–Chuyển–Ra"),
    ("DSKhachHang không có quan hệ", "Test NguoiXem + tuan: 12 khách", "RLS chỉ lọc qua quan hệ", "Bỏ bảng khỏi mô hình", "Buổi 7 – RLS, workspace, chia sẻ"),
    ("Che SĐT chỉ trên hình ảnh", "Export dữ liệu gốc: 0900000101", "Cột gốc vẫn nạp; CCCD chỉ ẩn", "Power Query: bỏ hoặc che trước khi nạp", "Buổi 6 – giảm dữ liệu, che"),
    ("PhanQuyen lộ", "Analyze in Excel đọc 10 dòng email", "Không ẩn, không có quy tắc riêng", "[Email] = USERPRINCIPALNAME(), ẩn bảng", "Buổi 7 – RLS, workspace, chia sẻ"),
    ("Bản sao Publish to web", "Người ngoài thấy 1.568.466 + khách", "Bản sao bỏ RLS rồi publish công khai", "Xóa mã nhúng, bản sao; tắt tenant", "Buổi 5 – chia sẻ an toàn"),
    ("Nhãn Công khai, cho xuất gốc", "Tệp “SanLuong_Q3 [Công khai].csv”", "Không phân loại theo nội dung", "Nhãn Mật; tắt xuất dữ liệu gốc", "Buổi 1 – phân loại, nhãn"),
]

KEY_RLSLAB = key(
    "13 lỗi trong 6 lớp: role tạm, liên kết toàn tổ chức, Member/Contributor, PhanQuyen cũ (Hà, An, tài khoản chung), nhóm trong hai role, "
    "bảng khách hàng không có quan hệ, che chỉ trên hình ảnh, PhanQuyen lộ, bản sao Publish to web, nhãn sai. "
    "Sửa xong: X 826.436 (Tuấn, Lan), Y 742.030 (TP Điện lực Y, Hà), cả hai 1.568.466 (Minh), còn lại không thấy dữ liệu.",
    {"phat_hien": [dict(zip(("loi", "bang_chung", "nguyen_nhan", "cach_sua", "buoi"), r)) for r in RASOAT_MAU],
     "kiem_thu_lai": "Service – đăng nhập (sau khi sửa và Publish lại):\n"
                     "tuan.truongphong – Viewer qua nhóm/App – NguoiXem – Điện lực X – 826.436 – Đạt\n"
                     "truongphong@dly – NguoiXem – Điện lực Y – 742.030 – Đạt\n"
                     "minh.kehoach – NguoiXem – X, Y – 1.568.466 – Đạt\n"
                     "ha.kehoach – NguoiXem – Điện lực Y – 742.030 – Đạt\n"
                     "lan.ketoan – NguoiXem – Điện lực X – 826.436 – Đạt\n"
                     "nhanvien.baocao – Viewer – NguoiXem – Điện lực X – 826.436 – Đạt\n"
                     "moi.vao – NguoiXem, không có trong PhanQuyen – không thấy dữ liệu – Đạt (mặc định từ chối)\n"
                     "nv.kythuat, doitac – không mở được báo cáo – Đạt\n"
                     "an.nghiviec, baocao.chung – không đăng nhập được – Đạt\n"
                     "Người ngoài internet – không còn mã nhúng – Đạt",
     "quy_trinh": "1. Mọi quyền tạm (role, nhóm, liên kết) có ngày hết hạn và người gỡ; rà soát quyền báo cáo hằng quý.\n"
                  "2. Quy trình Vào – Chuyển – Ra cập nhật cả PhanQuyen, nhóm bảo mật, workspace; không dùng tài khoản chung.\n"
                  "3. Trước khi publish: chỉ nạp cột cần dùng, gắn nhãn đúng, kiểm thử bằng tài khoản Viewer thật cả trường hợp bị từ chối; "
                  "Publish to web và xuất dữ liệu gốc chỉ bật cho nhóm được duyệt."},
    read=[LAB_SOLUTION("rasoat"), P("Ba ô phía trên là bài làm mẫu đạt 10 điểm: đủ 13 lỗi, ma trận sau khi sửa và ba việc cho quy trình. "
            f"Học viên tìm được 8–9 lỗi có bằng chứng bằng con số đã là bài tốt. Mở {LAB} để trình diễn.")],
    more=[
        ("Bảng lỗi cài sẵn: tái hiện và sửa", [
            TABLE(["#", "Lỗi", "Tái hiện trên mô phỏng", "Thấy gì", "Sửa đúng gốc", "Buổi"],
                  *[[str(i), l, t, g, s, b] for i, (l, t, g, s, b) in enumerate(RASOAT, 1)]),
            P("Lỗi 1 che lấp lỗi 5, 8 và một phần lỗi 3: khi mọi người cùng thuộc TatCa_TamThoi thì ai cũng thấy hết. "
              "Học viên phải sửa lỗi 1 rồi kiểm thử lại mới thấy các lỗi sau. Đây là điểm muốn dạy: một lần kiểm thử “thấy hết” chưa chỉ ra được hết nguyên nhân.")]),
        ("Ma trận trước và sau khi sửa (số liệu mô phỏng)", [
            TABLE(["Tài khoản", "Ai cần thấy gì", "Trước khi sửa", "Sau khi sửa"],
                  ["tuan.truongphong", "Chỉ X", "1.568.466 (Member, không áp RLS)", "826.436"],
                  ["truongphong@dly", "Chỉ Y", "1.568.466 (NguoiXem + TatCa)", "742.030"],
                  ["minh.kehoach", "X và Y", "1.568.466", "1.568.466"],
                  ["ha.kehoach", "Chỉ Y (đã chuyển)", "1.568.466", "742.030"],
                  ["moi.vao", "Không", "1.568.466 (TatCa)", "Không thấy dữ liệu"],
                  ["nhanvien.baocao", "Chỉ X, chỉ xem", "1.568.466 (Contributor)", "826.436 (Viewer)"],
                  ["lan.ketoan", "Chỉ X", "1.568.466 (DonVi_A + DonVi_B + TatCa)", "826.436"],
                  ["baocao.chung", "Không được tồn tại", "1.568.466", "Không đăng nhập được"],
                  ["an.nghiviec", "Không (đã nghỉ)", "Không đăng nhập được, quyền còn nguyên", "Không đăng nhập được, quyền đã gỡ"],
                  ["nv.kythuat", "Không", "1.568.466 (liên kết toàn tổ chức)", "Không mở được báo cáo"],
                  ["doitac (khách ngoài)", "Không", "Không mở được", "Không mở được"],
                  ["Người ngoài internet", "Không", "1.568.466 + danh sách khách (Publish to web)", "Không còn liên kết"])]),
        ("Trình tự trình diễn trên lớp (15–20 phút)", [
            {"t": "list", "ordered": True, "items": [{"html": x, "level": 0} for x in [
                f"Mở {LAB}, chế độ service. Hỏi lớp: “Báo cáo đã có RLS. Có cần rà soát không?”",
                "Đổi “Đang đăng nhập” lần lượt: trưởng phòng Điện lực Y, nv.kythuat, Người ngoài internet. Cả ba đều thấy 1.568.466. Mở ma trận kiểm thử cho lớp xem.",
                "Hỏi “vì sao người ngoài thấy được?” → Admin portal → Embed codes → Nhật ký (3/9, nhanvien.baocao). Xóa mã nhúng, xóa bản sao, tắt Publish to web. Nói về giữ bằng chứng trước khi xóa.",
                "Hỏi “vì sao trưởng phòng Y thấy cả X?” → khung thông tin mô phỏng: NguoiXem + TatCa_TamThoi. Desktop → Manage roles: xóa TatCa_TamThoi, DonVi_A, DonVi_B → Publish. Xóa liên kết toàn tổ chức.",
                "Kiểm thử lại: Tuấn vẫn 1.568.466 (Member). Hà 1.568.466 (dòng cũ). Lan không còn mở được báo cáo: trước đây chị vào nhờ liên kết toàn tổ chức, nay chưa có trong nhóm người xem. Sửa từng lỗi, mỗi lần kiểm thử lại một tài khoản.",
                "Test as role NguoiXem + tuan → trang Tra cứu khách hàng: 12 khách. Export Underlying data: số điện thoại thật. Hỏi: báo cáo quản trị có cần bảng này không? (Buổi 6.)",
                "Kết: đọc lại ma trận sau khi sửa. Mỗi lỗi nằm ở một lớp khác nhau. Không lớp nào tự đủ: RLS, workspace, chia sẻ, dữ liệu nạp vào, tài khoản, cài đặt tenant."]]}]),
        ("Nối với các buổi trước", [
            TABLE(["Buổi", "Khái niệm", "Trong kịch bản"],
                  ["1", "Phân loại 4 mức, nhãn đi theo dữ liệu", "Nhãn Công khai cho báo cáo có dữ liệu khách hàng; tên tệp xuất mang nhãn"],
                  ["2", "Mỗi bản sao là một vòng đời mới", "SanLuong_BanNhap, tệp xuất CSV, Analyze in Excel đều là bản sao ngoài tầm RLS"],
                  ["3", "Quyền tối thiểu, quyền tạm, Vào – Chuyển – Ra, tích tụ quyền", "Contributor thay vì Viewer; role tạm không gỡ; Hà, An; Lan trong hai role"],
                  ["4", "Tài khoản dùng chung", "baocao.chung: không truy vết được người đã xuất dữ liệu"],
                  ["5", "Chọn kênh chia sẻ", "Liên kết toàn tổ chức, Publish to web, cho chia sẻ lại và Build"],
                  ["6", "Che tĩnh và che khi hiển thị; chỉ lấy cột cần", "SDT_hien_thi chỉ che trên hình ảnh; CCCD chỉ ẩn; bảng khách hàng không cần cho báo cáo quản trị"],
                  ["7", "RLS cần quan hệ đúng; Member không chịu RLS; ẩn và lọc PhanQuyen", "Lỗi 3, 4, 9, 11"],
                  ["9 (xem trước)", "Nhật ký hoạt động", "Nhật ký cho biết ai tạo role tạm, ai Publish to web, tài khoản nào xuất dữ liệu"])]),
        ("Mô phỏng khác Power BI thật ở đâu", [
            {"t": "list", "ordered": False, "items": [{"html": x, "level": 0} for x in [
                "Chỉ hỗ trợ một phần DAX (SUM, DISTINCTCOUNT, COUNTROWS, AVERAGEX, CALCULATE, CALCULATETABLE, VALUES, FILTER, LOOKUPVALUE, RELATED, USERPRINCIPALNAME…). Thông báo lỗi được viết lại bằng tiếng Việt theo ý của thông báo thật.",
                "Khung “Thông tin mô phỏng” (đường truy cập, có áp RLS không) Power BI thật không hiện. Ngoài đời phải suy ra từ Manage access, Security và kiểm thử.",
                "Dữ liệu gốc khi Export gồm các cột không ẩn của bảng chi tiết nhất trong hình ảnh. Power BI thật có quy tắc chi tiết hơn và tùy cài đặt.",
                "OLS trên Power BI thật thường cấu hình bằng Tabular Editor. Nhóm Toan_Cong_Ty mô phỏng nhóm động của Entra ID.",
                "Kết quả trên mô phỏng không thay cho kiểm thử trên service thật của đơn vị. Học viên ghi rõ “kiểm thử trên mô phỏng”."]]}]),
    ],
    rubric=[("Tìm lỗi có bằng chứng", "4", "Từ 8 lỗi trở lên, mỗi lỗi có tài khoản và con số hoặc mục nhật ký; có ít nhất một lỗi ngoài RLS (chia sẻ, Publish to web, dữ liệu nạp vào)."),
            ("Sửa đúng gốc", "3", "Không nâng quyền để “cho chạy”; sửa ở PhanQuyen, nhóm, workspace, mô hình; có người làm."),
            ("Kiểm thử lại và nối bài học", "3", "Ma trận sau khi sửa có cả trường hợp bị từ chối; mỗi lỗi nối đúng buổi.")],
    mistakes=[("Dừng ở lỗi đầu tiên", "Chỉ ghi “ai cũng thấy hết”", "“Sửa xong lỗi đó, đăng nhập lại chị Hà và chị Lan: thấy gì?”"),
              ("Sửa bằng cách thêm quyền", "Thêm Lan làm Member để “thấy được”", "“Member có chịu RLS không? Lan cần thấy gì?”"),
              ("Chỉ kiểm thử bằng Test as role", "Ma trận không có dòng Service – đăng nhập", "“Test as role có biết anh Tuấn là Member không?”"),
              ("Coi che hiển thị là đã bảo vệ", "Không nhắc Export / Analyze in Excel", "“Thử xuất dữ liệu gốc trang khách hàng xem.”"),
              ("Xóa mã nhúng mà không giữ bằng chứng", "Không nhắc nhật ký, ảnh chụp", "“Làm sao biết ai đã xem trong 3 tuần đó?”")],
    flow=["Lớp nêu các lỗi tìm được; giảng viên đánh dấu vào bảng 13 lỗi.",
          "Chiếu lỗi 1 và cách nó che lấp lỗi 5, 8.",
          "Trình diễn lỗi 10 (Export dữ liệu gốc) và lỗi 12 (Publish to web) vì lớp hay bỏ sót.",
          "Đọc ma trận sau khi sửa; hỏi lớp ba việc đưa vào quy trình."],
)

KEYS = {"m07-th8": KEY_TH8, "m07-case-v2": KEY_CASE7, "m07-rlslab-v1": KEY_RLSLAB}
