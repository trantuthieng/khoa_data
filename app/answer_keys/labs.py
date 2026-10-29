"""Đáp án giảng viên – 26 bài ngắn SQL, Python (buổi 6) và Power BI (buổi 7).

Lời giải, kết quả mong đợi và giải thích lấy từ tools/beginner_labs.py (nguồn dựng bài), để sửa một chỗ là đủ.
"""
import importlib.util
import json
from pathlib import Path

from .kit import CODE, LAB_SOLUTION, P, TABLE, key

_spec = importlib.util.spec_from_file_location(
    "beginner_labs", Path(__file__).resolve().parents[2] / "tools" / "beginner_labs.py")
_labs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_labs)

MISTAKES = {
    "sql": [("Chạy được nhưng sai cột / sai điều kiện", "Kết quả khác bảng mong đợi", "“Đếm lại số dòng, đọc tên cột: có đúng như đề không?”"),
            ("Chỉ dán kết quả, không dán câu lệnh", "Ô mã trống", "Yêu cầu dán đúng câu lệnh đã chạy để đối chiếu."),
            ("Giải thích chỉ mô tả cú pháp", "Không nhắc ý nghĩa an toàn dữ liệu", "“Câu lệnh này giúp giảm dữ liệu hay giữ phạm vi thế nào? Có thay được quyền hệ thống không?”"),
            ("Ghi “đã chạy” khi chưa chạy", "Kết quả trùng đáp án nhưng không có số dòng thật", "Nhắc chọn “Chưa chạy, mới dự đoán” nếu chưa có Python.")],
    "py": [("Sai tên khóa hoặc lát cắt", "KeyError, kết quả lệch ký tự", "“In rows[0] ra xem các khóa là gì; đếm vị trí ký tự.”"),
           ("Sửa thẳng dữ liệu gốc", "Ghi đè rows", "Tạo danh sách mới; dữ liệu gốc vẫn phải được quản lý."),
           ("Giải thích chỉ mô tả cú pháp", "Không nhắc ý nghĩa an toàn dữ liệu", "“Che, bỏ cột, tổng hợp đã đủ để gọi là ẩn danh chưa?”"),
           ("Ghi “đã chạy” khi chưa chạy", "Không có kết quả in ra thật", "Nhắc chọn “Chưa chạy, mới dự đoán”.")],
    "bi": [("Thiếu dòng ngày thứ hai", "Tổng 1.400 thay vì 1.770", "“FactDien có đủ 8 dòng chưa?”"),
           ("Sai kiểu dữ liệu hoặc quan hệ", "Không tạo được quan hệ, View as vẫn thấy tất cả", "Kiểm tra kiểu Date của Ngay, khóa duy nhất ở phía một, quan hệ đang hoạt động."),
           ("Dùng slicer thay cho RLS", "Giải thích “đã lọc A”", "“Người xem bỏ chọn slicer thì thấy gì?”"),
           ("Ghi đạt trên service khi mới thử Desktop", "Không có ảnh service", "Chỉ ghi đạt khi thử thật bằng tài khoản Viewer; còn lại ghi Chưa thử.")],
}


def _sim_link(i):
    return f'<a href="/static/labs/rls/index.html?bai=bi{i:02d}" target="_blank" rel="noopener">phòng thí nghiệm RLS – BI {i:02d}</a>'


# Làm trên phòng thí nghiệm RLS (app/static/labs/rls): (các bước bấm, [(phải thấy gì, số liệu)])
SIM = {
    1: (["Home → Enter data. Chép khối DimDonVi trong khung Đề bài, dán vào ô, đặt tên bảng DimDonVi → Load.",
         "Lặp lại với DimNgay và FactDien.",
         "Mở Table view (biểu tượng bảng bên trái). Chọn từng bảng, xem kiểu dữ liệu ở đầu cột. Nếu Ngay chưa là Date thì bấm tên kiểu để đổi."],
        [("Số dòng", "DimDonVi 3, DimNgay 2, FactDien 8"), ("Kiểu dữ liệu", "Ngay: Date ở cả hai bảng; kWh: Whole number; MaKH, MaDonVi: Text")]),
    2: (["Modeling → Manage relationships. Mục New relationship: Bảng (phía một) DimDonVi, cột MaDonVi; Bảng (phía nhiều) FactDien, cột MaDonVi → Kiểm tra → Create.",
         "Tạo tương tự DimNgay[Ngay] → FactDien[Ngay].",
         "Model view: bấm vào từng quan hệ, xem Cross filter direction là Single và Make this relationship active đang đánh dấu.",
         "Table view → DimNgay: hai dòng cùng Thang 2026-09; FactDien không có cột Thang."],
        [("Model view", "Hai đường liền nối DimDonVi và DimNgay tới FactDien, đầu 1 ở bảng danh mục, * ở FactDien"),
         ("Vì sao không nối theo Thang", "Thang trùng ở phía một (hai ngày cùng tháng) và FactDien không có cột Thang để nối")]),
    3: (["Home → New measure. Thanh công thức: Tong kWh = SUM(FactDien[kWh]) → Enter.",
         "Visualizations → Card, kéo (hoặc chọn) Tong kWh.",
         "Visualizations → Table, chọn DimDonVi[MaDonVi] và Tong kWh."],
        [("Card", "1.770"), ("Table", "DV_A 560, DV_B 810, DV_C 400; tổng 1.770")]),
    4: (["New measure: So KH = DISTINCTCOUNT(FactDien[MaKH]).", "New measure: So dong = COUNTROWS(FactDien).", "Thêm hai Card cho hai thước đo."],
        [("So KH", "6"), ("So dong", "8 – KH001 và KH004 có dòng ở cả hai ngày")]),
    5: (["Visualizations → Slicer, trường DimDonVi[MaDonVi].", "Bấm DV_A trên slicer: đọc Card.", "Bấm lại DV_A để bỏ chọn: đọc Card."],
        [("Chọn DV_A", "Tong kWh 560, So KH 3"), ("Bỏ chọn", "1.770 và 6 – ai mở báo cáo cũng bỏ chọn được")]),
    6: (['Modeling → Manage roles → Create. Tên DonVi_A, bảng DimDonVi, biểu thức [MaDonVi] = "DV_A" → kiểm tra (✓) → Save.',
         "Tạo DonVi_B tương tự với \"DV_B\".",
         "Modeling → View as → đánh dấu DonVi_A → OK. Đọc Card và slicer. Stop viewing.", "View as DonVi_B."],
        [("View as DonVi_A", "560; slicer chỉ còn DV_A"), ("View as DonVi_B", "810; slicer chỉ còn DV_B"),
         ("Ma trận kiểm thử", "Hai dòng “Desktop – View as” tự ghi")]),
    7: (["Model view: bấm vào đường DimDonVi – FactDien, bỏ đánh dấu Make this relationship active (đường thành nét đứt).",
         "Modeling → View as DonVi_A: đọc Card và slicer.", "Stop viewing, đánh dấu lại Make this relationship active, View as DonVi_A lần nữa."],
        [("Quan hệ tắt", "Slicer chỉ còn DV_A nhưng Card vẫn 1.770: RLS lọc DimDonVi nhưng không truyền sang FactDien"),
         ("Bật lại", "560"), ("Ma trận kiểm thử", "Dòng quan hệ tắt có đánh dấu, dòng sau ra 560")]),
    8: (["Modeling → View as: đánh dấu cả DonVi_A và DonVi_B → OK.", "Bỏ mọi lựa chọn trên slicer, đọc Card."],
        [("Hai role", "1.370 kWh, 5 khách, slicer có DV_A và DV_B – hợp quyền, không phải phần giao")]),
    9: (["Visualizations → Slicer, trường DimNgay[Ngay].", "Chọn riêng 2026-09-01, đọc Card; rồi riêng 2026-09-02.", "Bỏ chọn."],
        [("2026-09-01", "1.400 kWh, 6 khách"), ("2026-09-02", "370 kWh, 2 khách"), ("Cả kỳ", "1.770 kWh, 6 khách (không phải 8)")]),
    10: (["Home → Publish (chuyển sang chế độ service).",
          "Menu trái Security (RLS): role DonVi_A thêm nguoixem.a, DonVi_B thêm nguoixem.b. Không thêm khong.gan.",
          "Workspace → Manage access: thêm nguoixem.a, nguoixem.b, khong.gan làm Viewer; thanhvien làm Member.",
          "Ô “Đang đăng nhập” góc trên: chọn lần lượt từng người, mở báo cáo, đọc Card."],
         [("nguoixem.a", "560, chỉ DV_A"), ("nguoixem.b", "810, chỉ DV_B"),
          ("khong.gan", "Mọi hình ảnh báo “Không thể tải dữ liệu” – mặc định từ chối"),
          ("thanhvien (Member)", "1.770 – Member không chịu RLS dù theo nghiệp vụ chỉ cần DV_A"),
          ("Lưu ý", "Test as role trong Security chỉ thử bộ lọc, không thêm thành viên; người chưa được thêm vẫn bị chặn")]),
}


def _sim(i):
    steps, seen = SIM[i]
    return ("Làm trên phòng thí nghiệm RLS", [
        LAB_SOLUTION(f"bi{i:02d}"),
        P(f"Học viên mở {_sim_link(i)}. Khung Đề bài bên phải có danh sách tự kiểm tra: đủ dấu ✓ là đạt phần thao tác. "
          "Mỗi lần View as, Test as role hoặc đổi tài khoản đăng nhập, ma trận kiểm thử tự ghi một dòng; học viên bấm chép để dán vào bài nộp."),
        {"t": "list", "ordered": True, "items": [{"html": s, "level": 0} for s in steps]},
        TABLE(["Phải thấy", "Số liệu trên mô phỏng"], *[list(r) for r in seen]),
        P("Bài làm trên mô phỏng lưu trong trình duyệt của học viên; nút “↺ Làm lại” đưa bài về trạng thái ban đầu.")])


def _fmt(v):
    if isinstance(v, list):
        return " | ".join(_fmt(x) for x in v)
    if isinstance(v, dict):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def _lab(kind, ex):
    if kind == "bi":
        code = "\n".join(f"{i}. {t}" for i, t in enumerate(ex["tasks"], 1)) + ("\n\n" + ex["code"] if ex.get("code") else "")
        result = ex["answer"].split(". ")[0] + "."
        more = [("Thao tác mẫu", [P(f"Bám slide {ex['slides']}."), *([CODE(ex["code"])] if ex.get("code") else [])]),
                _sim(int(ex["title"][3:5]))]
    else:
        code = ex["solution"]
        result = "\n".join(_fmt(r) for r in ex["expected"])
        more = [("Lời giải và kết quả mong đợi", [CODE(ex["solution"]),
                                                  TABLE(["Kết quả in ra / bảng kết quả"], *[[_fmt(r)] for r in ex["expected"]])])]
    return key(
        ex["answer"],
        {"code": code, "result": result, "explain": ex["answer"], "run_state": [{"state": "Đã chạy / đã thao tác"}]},
        read=[P(f"Ba ô phía trên là bài nộp mẫu đạt 10 điểm: {ex['goal'].rstrip('.').lower()}. "
                "Mã của học viên viết khác vẫn đạt nếu cho cùng kết quả và giải thích đúng ý.")],
        more=more + [("Cách đối chiếu nhanh", [P("Học viên ghi “Chưa chạy, mới dự đoán” thì chấm phần mã và giải thích, ghi nhận chưa chạy; "
                                                 "không trừ điểm nếu lớp chưa cài được Python hoặc chưa có Power BI.")])],
        rubric=[("Mã hoặc thao tác đúng", "4", "Điền đúng chỗ trống hoặc làm đủ các bước; chạy ra đúng kết quả."),
                ("Kết quả và đối chiếu", "3", "Ghi số dòng, số liệu thực tế và so với kết quả mong đợi."),
                ("Ý nghĩa an toàn dữ liệu", "3", "Giải thích đúng như ô giải thích mẫu, không chỉ mô tả cú pháp.")],
        mistakes=MISTAKES[kind],
    )


KEYS = {}
for _no, _sets in ((6, (("sql", _labs.SQL), ("py", _labs.PYTHON))), (7, (("bi", _labs.BI),))):
    for _kind, _exs in _sets:
        for _i, _ex in enumerate(_exs, 1):
            KEYS[f"m{_no:02d}-{_kind}{_i:02d}-v1"] = _lab(_kind, _ex)
