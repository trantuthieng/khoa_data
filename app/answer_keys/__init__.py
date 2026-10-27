"""Đáp án dành cho giảng viên, theo mã hoạt động.

Chỉ gửi qua API giảng viên (/api/t/answers), không gắn vào ACTIVITIES nên không bao giờ tới trình duyệt học viên.

Mỗi đáp án:
  "fields": bài làm mẫu, cùng định dạng bài nộp của học viên (trường "board" là
            {nodes: [{id, kind, x, y, title?, text, tag?, p?}], links: [{id, from, to, <trường trên dây>}]}).
            Giao diện giảng viên hiển thị bằng chính mẫu làm bài của học viên ở chế độ chỉ đọc.
  "sections": phần giải thích, dạng khối nội dung như giáo trình (h3, p, list, table, code).
            Mục có "private": True (thang điểm, lỗi hay gặp) tự ẩn khi trình chiếu.
Mỗi buổi một tệp (m01.py …), bài ngắn SQL/Python/BI ở labs.py; tệp nào cũng có KEYS = {mã hoạt động: đáp án}.
"""
from . import labs, m01, m02, m03, m04, m05, m06, m07, m08, m09, m10

ANSWER_KEYS = {}
for _m in (m01, m02, m03, m04, m05, m06, m07, m08, m09, m10, labs):
    ANSWER_KEYS.update(_m.KEYS)
