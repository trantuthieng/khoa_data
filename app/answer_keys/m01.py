"""Đáp án giảng viên – buổi 1."""
from .kit import L, N, P, TABLE, UL, board, case_key, key  # noqa: F401


def cia(c, i, a, ai_dung, ai):
    return {"c": c, "i": i, "a": a, "ai_dung": ai_dung, "ai": ai}


# ---------- Thực hành 1: phân loại dữ liệu ----------
KEY_TH1 = key(
    "Bốn nhóm có dữ liệu khách hàng hoặc nhân sự xếp Mật; tài liệu vận hành, sơ đồ lưới xếp Hạn chế cao vì giúp kẻ tấn công. "
    "Chỉ số công tơ có toàn vẹn Cao. Một nhóm có thể có nhiều nhãn: bản tổng hợp theo vùng là Nội bộ, bản đã duyệt công bố là Công khai.",
    {"phan_loai_bang": board([
        N("d_kh", "data", 893, 340, "Lộ ra thì kẻ gian gọi lừa, khách mất niềm tin. Chỉ người có nhiệm vụ được xem.",
          p=cia("Trung bình", "Trung bình", "Thấp", "CSKH, kinh doanh của đơn vị quản lý; qua hệ thống nghiệp vụ",
                "Không đưa dữ liệu thật vào công cụ chưa duyệt; thử bằng dữ liệu giả lập")),
        N("d_cto", "data", 1141, 340, "Chi tiết theo từng khách hàng → Mật. Bị sửa sai là sai hóa đơn: toàn vẹn Cao.",
          p=cia("Trung bình", "Cao", "Trung bình", "Bộ phận ghi chỉ số, tính hóa đơn, kế hoạch",
                "Chỉ bản tổng hợp, không có mã khách hàng, trên công cụ được duyệt")),
        N("d_ns", "data", 893, 600, "Thông tin cá nhân của nhân viên; lương, sức khỏe còn nhạy cảm hơn.",
          p=cia("Trung bình", "Trung bình", "Thấp", "Phòng tổ chức – nhân sự, quản lý trực tiếp theo phạm vi",
                "Không tải danh sách nhân sự lên AI “để thử công cụ”")),
        N("d_file", "data", 1141, 600, "Họ tên, điện thoại, địa chỉ, tình trạng nợ của cả Điện lực X.",
          p=cia("Trung bình", "Trung bình", "Thấp", "Người được giao thu nợ của Điện lực X; không gửi email kèm nguyên file",
                "Không dán vào chatbot cá nhân; lọc bằng Excel hoặc chỉ mô tả cấu trúc cột")),
        N("d_vh", "data", 1430, 340, "Không có dữ liệu cá nhân nhưng chỉ cho kẻ tấn công biết đánh vào đâu. Chủ tài liệu xác nhận nhãn.",
          p=cia("Cao", "Cao", "Cao", "Nhóm kỹ thuật được giao; kho tài liệu kỹ thuật có phân quyền",
                "Mặc định không đưa vào AI khi chưa có phê duyệt rõ ràng")),
        N("x_tang", "ext", 1430, 640, "Từng dòng chỉ là Nội bộ; gộp lại lộ phụ tải và điểm yếu của lưới → Hạn chế cao.",
          title="Sản lượng 12 tháng theo từng trạm biến áp", tag="Gộp làm tăng mức"),
        N("x_ha", "ext", 110, 340, "Lãnh đạo đã duyệt đăng website → hạ từ Nội bộ xuống Công khai, đúng phạm vi đã duyệt.",
          title="Báo cáo sản lượng quý đã duyệt công bố", tag="Hạ mức sau công bố"),
        N("n_vung", "note", 545, 340, "Bản tổng hợp, chưa duyệt công bố, mỗi vùng đủ lớn → Nội bộ. Cùng nhóm dữ liệu công tơ nhưng khác nhãn.",
          title="Sản lượng tổng hợp theo vùng"),
    ])},
    modules=[
        ("📂 <b>Khách hàng và hợp đồng</b> → Mật", "C / I / A: Trung bình / Trung bình / Thấp. Ai dùng: CSKH, kinh doanh đơn vị quản lý.",
         "Lý do phải gắn với “nếu lộ ra thì sao”: lừa đảo, mất niềm tin. Ghi “mọi người cần” ở cột ai được dùng là chưa đạt."),
        ("📂 <b>Chỉ số công tơ và báo cáo sản lượng</b> → Mật", "C / I / A: Trung bình / <b>Cao</b> / Trung bình.",
         "Điểm chữa bài chính: bí mật có thể thấp nhưng <b>toàn vẹn Cao</b> (sửa sai là sai hóa đơn). Học viên xếp Nội bộ cũng đạt nếu "
         "ghi rõ là bản tổng hợp, còn bản chi tiết theo khách hàng là Mật."),
        ("📂 <b>Vận hành và tài liệu kỹ thuật</b> → Hạn chế cao", "Cao / Cao / Cao. Chủ tài liệu xác nhận.",
         "Không có dữ liệu cá nhân không có nghĩa là công khai. Xếp Mật cũng chấp nhận; xếp Công khai là sai (có cảnh báo ⚠)."),
        ("📂 <b>Thông tin nhân sự</b> → Mật", "Trung bình / Trung bình / Thấp. Phòng nhân sự, quản lý trực tiếp.",
         "Lương, sức khỏe có thể cao hơn; học viên xếp Hạn chế cao với lý do đó vẫn đạt."),
        ("📂 <b>File DS_KhachHang_DLX.xlsx</b> → Mật", "Trung bình / Trung bình / Thấp. Chỉ người thu nợ của Điện lực X.",
         "Nối với chương 1: file đang bị gửi kèm email, dán vào chatbot. Xếp Nội bộ là chưa đạt (có cảnh báo ⚠)."),
        ("➕ <b>Mở rộng</b> (làm xong sớm)", "Gộp làm tăng mức: sản lượng 12 tháng theo trạm. Hạ mức: báo cáo quý đã duyệt đăng website.",
         "Cộng điểm trình bày. Không bắt buộc."),
        ("📝 <b>Ghi chú</b> ở cột Nội bộ", "Bản tổng hợp theo vùng chưa công bố.",
         "Minh họa ý “một nhóm dữ liệu có thể có nhiều nhãn tùy mức chi tiết”."),
    ],
    more=[("Bảng C1 mong đợi", [
        TABLE(["Nhóm dữ liệu", "Nhãn", "C / I / A", "Ai được dùng, kênh", "Điều kiện dùng AI"],
              ["Khách hàng và hợp đồng", "Mật", "TB / TB / Thấp", "CSKH, kinh doanh đơn vị quản lý; qua hệ thống", "Không đưa dữ liệu thật vào công cụ chưa duyệt"],
              ["Chỉ số công tơ, sản lượng", "Mật (chi tiết); Nội bộ / Công khai (tổng hợp đã duyệt)", "TB / Cao / TB", "Ghi chỉ số, hóa đơn, kế hoạch", "Chỉ bản tổng hợp, không mã KH, công cụ được duyệt"],
              ["Vận hành, tài liệu kỹ thuật", "Hạn chế cao (hoặc Mật)", "Cao / Cao / Cao", "Nhóm kỹ thuật được giao", "Mặc định không đưa vào AI"],
              ["Nhân sự", "Mật", "TB / TB / Thấp", "Nhân sự, quản lý trực tiếp", "Không tải lên AI để thử"],
              ["File DS_KhachHang_DLX", "Mật", "TB / TB / Thấp", "Người thu nợ Điện lực X", "Không dán vào chatbot cá nhân"]),
        P("Đây không phải quyết định phân loại chính thức. Nhãn khác vẫn đạt nếu lý do và giả định rõ ràng."),
    ])],
    rubric=[
        ("Nhãn", "3", "Cả 5 thẻ nằm trong cột; lý do gắn với “nếu lộ ra thì sao”; không xếp tài liệu kỹ thuật hay file anh Cường vào Công khai."),
        ("C / I / A", "3", "Đủ ba mức cho 5 thẻ; chỉ số công tơ có I = Cao."),
        ("Ai được dùng", "2", "Bộ phận hoặc vai trò cụ thể, có kênh; không ghi “mọi người”."),
        ("Điều kiện AI", "2", "Nêu công cụ nào, dữ liệu nào, phần nào được đưa vào."),
    ],
    mistakes=[
        ("Sản lượng tổng hợp xếp Công khai", "Thẻ công tơ ở cột Công khai, có ⚠", "“Báo cáo đã được duyệt công bố chưa? Vùng nhỏ có nhận ra khách hàng lớn không?”"),
        ("Tài liệu kỹ thuật xếp Công khai", "Thẻ vận hành ở cột Công khai, có ⚠", "“Không có tên người, nhưng sơ đồ lưới lọt ra ngoài thì ai được lợi?”"),
        ("Chỉ đánh giá bí mật", "C có, I và A để trống hoặc đều Thấp", "“Chỉ số công tơ bị sửa thì sao? Hệ thống ngừng một ngày thì sao?”"),
        ("Cột ai được dùng ghi chung chung", "“Mọi người”, “nhân viên”", "“Bộ phận nào, qua kênh nào?”"),
        ("Điều kiện AI là “được” hoặc “không”", "Không nêu công cụ, phần dữ liệu", "“Công cụ nào được duyệt? Bản nào được đưa vào?”"),
    ],
    flow=["Chiếu hai bài xếp khác nhau cho thẻ chỉ số công tơ; hỏi lớp vì sao.",
          "Mở bảng mẫu, dừng ở thẻ công tơ: bí mật Trung bình nhưng toàn vẹn Cao.",
          "Dừng ở thẻ vận hành: “không có dữ liệu cá nhân” không có nghĩa là công khai.",
          "Nhắc học viên giữ bảng này để dùng ở Thực hành 2 và 3.",
          "Công bố để học viên xem đáp án gợi ý."],
)

# ---------- Bài tập thêm: một báo cáo, ba phiên bản ----------
KEY_CASE1 = case_key(
    "A (tên, điện thoại, số nợ từng hộ) là Mật, không đưa vào chatbot cá nhân. B (tổng hợp chưa duyệt) là Nội bộ. "
    "C (đã duyệt đăng website) là Công khai trong phạm vi đã duyệt, nhưng việc dùng công cụ vẫn theo quy định đơn vị.",
    ["Bản A có tên, điện thoại và số nợ của từng hộ: lộ ra là lộ dữ liệu cá nhân, kẻ gian dùng để gọi lừa → Mật.\n"
     "Bản B chỉ có tổng sản lượng theo 4 vùng nhưng chưa được duyệt công bố → Nội bộ, chưa được đưa ra ngoài.\n"
     "Bản C là số liệu đã được duyệt đăng website → Công khai, nhưng chỉ đúng phạm vi đã duyệt.",
     "Anh/chị đừng đưa bản A vào chatbot cá nhân: trong đó có tên, điện thoại, số nợ của khách hàng. "
     "Mình có thể viết nhận xét từ bản C, hoặc dựng khung nhận xét bằng dữ liệu giả lập rồi điền số thật trong Excel. "
     "Nếu cần dùng AI với bản B, mình hỏi CNTT công cụ nào đã được duyệt trước. Em giúp anh/chị làm khung nhé.",
     "1) Có vùng nào quá nhỏ hoặc một khách hàng lớn chiếm phần lớn tổng không (nhận ra được khách hàng từ số tổng)?\n"
     "2) Công cụ AI định dùng đã được đơn vị duyệt chưa, mục đích và phạm vi dữ liệu đưa vào đã được người có thẩm quyền đồng ý chưa?"],
    [("1. Nhãn", "A Mật; B Nội bộ; C Công khai trong phạm vi đã duyệt. Lý do lấy từ dữ kiện đề (cột của A, “chưa duyệt” của B).",
      "A xếp Hạn chế cao vì có số nợ."),
     ("2. Trả lời đồng nghiệp", "Không đưa A vào chatbot cá nhân; đưa ra cách khác để vẫn xong việc.", "Gợi ý dữ liệu giả lập, dùng bản C, hỏi công cụ đã duyệt."),
     ("3. Hai điều kiểm tra với B", "Rủi ro nhận diện (nhóm nhỏ / áp đảo) và công cụ, mục đích đã được duyệt.", "Kiểm tra mức chi tiết, người nhận kết quả.")],
    ["Đọc đúng ba bản, không nhầm B là công khai chỉ vì đã bỏ tên.",
     "Từ chối có lý do và vẫn đưa cách hoàn thành công việc; lời trả lời lịch sự, ngắn.",
     "Hai điều kiểm tra với B là kiểm tra được (nhóm nhỏ, áp đảo, công cụ đã duyệt), không chỉ “cẩn thận”."],
    [("B xếp Công khai", "“Đã bỏ tên nên công khai được”", "“Bản B đã được ai duyệt công bố chưa?”"),
     ("Chỉ nói “không được”", "Câu 2 không có cách làm thay thế", "“Đồng nghiệp vẫn cần viết nhận xét. Bạn giúp họ bằng cách nào?”"),
     ("Cho rằng C dùng thoải mái", "Không nhắc quy định dùng công cụ", "“Dữ liệu công khai rồi, nhưng chatbot cá nhân có được dùng cho việc cơ quan không?”")],
)

KEYS = {"m01-th1": KEY_TH1, "m01-case-v2": KEY_CASE1}
