"""Nạp nội dung giáo trình (JSON do tools/build_content.py sinh ra) và lọc theo quyền xem."""
import copy
import json
from pathlib import Path

from .practice import OVERRIDES, template_for

CONTENT_DIR = Path(__file__).parent / "content"
STUDENT_KINDS = ("content", "practice")

# Mỗi lớp học theo một khóa. Khóa mặc định (lớp tạo trước khi có nhiều khóa) nằm thẳng trong content/,
# khóa khác nằm trong thư mục con. Mã hoạt động phải khác nhau giữa các khóa (VD m01-…, ai01-…).
DEFAULT_COURSE = "atdl"
COURSES = {
    "atdl": {"title": "An toàn ứng dụng & Dữ liệu", "subtitle": "dành cho cán bộ vận hành", "dir": CONTENT_DIR},
    "ai-agent": {"title": "AI Agent – Nhân sự ảo cho doanh nghiệp", "subtitle": "từ kiến trúc đến đội hình Multi-Agent",
                 "dir": CONTENT_DIR / "ai_agent"},
}

ACTIVITIES = {}
for course_id, course in COURSES.items():
    course["modules"] = {}
    for f in sorted(course["dir"].glob("m*.json")):
        m = json.loads(f.read_text(encoding="utf-8"))
        for a in m["activities"]:
            a["module"] = m["no"]
            a["course"] = course_id
            if a["type"] == "practice":
                if a["id"] in OVERRIDES:
                    a["fields"] = OVERRIDES[a["id"]]
                a.setdefault("fields", template_for(a["id"]))
            ACTIVITIES[a["id"]] = a
        m["has_stages"] = any(b.get("stage") for s in m["sections"] for b in s["blocks"])
        course["modules"][m["no"]] = m
    course["index"] = [{"no": m["no"], "title": m["title"], "short": m["short"]} for m in course["modules"].values()]

MODULES = COURSES[DEFAULT_COURSE]["modules"]
INDEX = COURSES[DEFAULT_COURSE]["index"]


def course_modules(course):
    return COURSES.get(course or DEFAULT_COURSE, COURSES[DEFAULT_COURSE])["modules"]


def section_index(module_no, section_id, course=DEFAULT_COURSE):
    for i, s in enumerate(course_modules(course)[module_no]["sections"]):
        if s["id"] == section_id:
            return i
    return 0


def student_module(module_no, view, revealed, course=DEFAULT_COURSE):
    """Bản nội dung học viên được thấy.

    view: dòng class_modules (unlocked, stage) hoặc None (= mở toàn bộ, dùng cho Tổng quan).
    revealed: tập activity_id đã được giảng viên công bố đáp án.
    """
    m = course_modules(course)[module_no]
    unlocked = len(m["sections"]) if view is None else view["unlocked"]
    stage = 99 if view is None else view["stage"]
    sections = []
    for i, s in enumerate(m["sections"]):
        if i > unlocked or s["kind"] not in STUDENT_KINDS:
            continue
        blocks = []
        for b in s["blocks"]:
            if b.get("teacher"):
                continue
            if b.get("reveal") and b["reveal"] not in revealed:
                continue
            if b.get("stage") and b["stage"] > stage:
                continue
            blocks.append(b)
        sec = {"id": s["id"], "title": s["title"], "kind": s["kind"], "blocks": blocks}
        if s.get("activity"):
            sec["activity"] = s["activity"]
        sections.append(sec)
    return {"no": m["no"], "title": m["title"], "short": m["short"], "sections": sections}


def public_activity(a, status):
    """Định nghĩa hoạt động gửi cho học viên: chỉ kèm đáp án khi đã công bố."""
    out = {k: v for k, v in a.items() if k != "questions"}
    out["status"] = status
    if "questions" in a:
        qs = copy.deepcopy(a["questions"])
        if status != "revealed":
            for qq in qs:
                for k in ("answer", "correct", "explain"):
                    qq.pop(k, None)
        out["questions"] = qs
    return out


def score(a, payload):
    """Chấm điểm câu trắc nghiệm. Trả về (điểm, điểm tối đa) hoặc (None, None)."""
    if a["type"] not in ("mcq", "multi"):
        return None, None
    answers = payload.get("answers", {}) if isinstance(payload, dict) else {}
    pts = 0
    for qq in a["questions"]:
        given = answers.get(qq["id"])
        if a["type"] == "mcq":
            pts += 1 if given == qq.get("correct") else 0
        else:
            pts += 1 if isinstance(given, list) and sorted(given) == sorted(qq.get("correct", [])) else 0
    return pts, len(a["questions"])
