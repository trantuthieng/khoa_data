"""Đáp án giảng viên – 26 bài ngắn SQL, Python (buổi 6) và Power BI (buổi 7).

Lời giải, kết quả mong đợi và giải thích lấy từ tools/beginner_labs.py (nguồn dựng bài), để sửa một chỗ là đủ.
"""
import importlib.util
import json
from pathlib import Path

from .kit import CODE, P, TABLE, key

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
        more = [("Thao tác mẫu", [P(f"Bám slide {ex['slides']}."), *([CODE(ex["code"])] if ex.get("code") else [])])]
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
