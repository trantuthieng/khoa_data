"""Chuyển các file giáo trình .docx thành JSON nội dung cho webapp.

Chạy lại mỗi khi sửa giáo trình:
    python tools/build_content.py "<thư mục chứa .docx>"

Kết quả: app/content/mNN.json (NN = 00 cho Tổng quan, 01..10 cho từng buổi)
và ảnh trong app/static/content/.
"""
import html
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from course_revision import revise
from beginner_labs import build_pack
from production_copy import polish
from student_view import apply as student_view
from compact_lessons import apply as compact
from log_investigation import add_log_investigation

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
PKG_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "app" / "content"
IMG_OUT = ROOT / "app" / "static" / "content"

CALLOUTS = [
    ("Hiểu nhầm hay gặp", "misconception"),
    ("Câu hỏi cho lớp", "question"),
    ("Ví dụ", "example"),
    ("Áp dụng", "apply"),
    ("Lưu ý", "note"),
    ("Điểm chữa bài", "note"),
    ("Điểm chung", "note"),
]

# H2 chỉ giáo viên thấy
TEACHER_SECTIONS = re.compile(r"^(Ghi chú cho giảng viên|Chuẩn bị khóa học|Phụ lục B)")
# H3 chỉ giáo viên thấy (trong mọi phần)
TEACHER_H3 = re.compile(r"^(Chuẩn bị của giảng viên|Chuẩn bị trước buổi)")
# H3/đoạn bắt đầu vùng đáp án, chỉ hiện khi giáo viên công bố
ANSWER_H3 = re.compile(r"^((Vòng \d+ – )?Đáp án|Điểm chữa bài|Lỗi (hay gặp|nhóm hay mắc))")
ANSWER_P = re.compile(r"^(Đáp án (tham khảo|gợi ý)|Câu từ chối mẫu)")
STAGE_H3 = re.compile(r"^Đợt (\d+)")


def esc(s):
    return html.escape(s, quote=False)


class Doc:
    def __init__(self, path: Path, module_no: int):
        self.z = zipfile.ZipFile(path)
        self.module_no = module_no
        self.doc = ET.fromstring(self.z.read("word/document.xml"))
        self.rels = {}
        rels = ET.fromstring(self.z.read("word/_rels/document.xml.rels"))
        for r in rels.iter(PKG_REL + "Relationship"):
            self.rels[r.get("Id")] = r.get("Target")
        self.numfmt = self._numbering()
        self.img_count = 0

    def _numbering(self):
        try:
            x = ET.fromstring(self.z.read("word/numbering.xml"))
        except KeyError:
            return {}
        abstract = {}
        for an in x.iter(W + "abstractNum"):
            lv = {}
            for l in an.findall(W + "lvl"):
                f = l.find(W + "numFmt")
                lv[l.get(W + "ilvl")] = f.get(W + "val") if f is not None else "bullet"
            abstract[an.get(W + "abstractNumId")] = lv
        nums = {}
        for n in x.iter(W + "num"):
            a = n.find(W + "abstractNumId").get(W + "val")
            nums[n.get(W + "numId")] = abstract.get(a, {})
        return nums

    # ---------- inline ----------
    def runs_html(self, p):
        out = []
        plain = []
        for el in p:
            if el.tag == W + "r":
                h, t = self.run_html(el)
                out.append(h)
                plain.append(t)
            elif el.tag == W + "hyperlink":
                inner_h, inner_t = [], []
                for r in el.iter(W + "r"):
                    h, t = self.run_html(r)
                    inner_h.append(h)
                    inner_t.append(t)
                target = self.rels.get(el.get(R + "id"), "")
                # link nội bộ giữa các tài liệu (claude.ai) không dùng được trong webapp
                if target.startswith("http") and "claude.ai" not in target:
                    out.append(f'<a href="{html.escape(target)}" target="_blank" rel="noopener noreferrer">{"".join(inner_h)}</a>')
                else:
                    out.append("".join(inner_h))
                plain.append("".join(inner_t))
            elif el.tag in (W + "ins", W + "smartTag", W + "sdt"):
                for r in el.iter(W + "r"):
                    h, t = self.run_html(r)
                    out.append(h)
                    plain.append(t)
        return "".join(out), "".join(plain)

    def run_html(self, r):
        parts = []
        for c in r:
            if c.tag == W + "t":
                parts.append(c.text or "")
            elif c.tag == W + "br":
                parts.append("\n")
            elif c.tag == W + "tab":
                parts.append("\t")
        text = "".join(parts)
        if not text:
            return "", ""
        h = esc(text)
        rpr = r.find(W + "rPr")
        if rpr is not None:
            b = rpr.find(W + "b")
            if b is not None and b.get(W + "val") not in ("0", "false"):
                h = f"<strong>{h}</strong>"
            i = rpr.find(W + "i")
            if i is not None and i.get(W + "val") not in ("0", "false"):
                h = f"<em>{h}</em>"
        return h, text

    def images(self, p):
        found = []
        for blip in p.iter(A + "blip"):
            rid = blip.get(R + "embed")
            target = self.rels.get(rid)
            if not target:
                continue
            data = self.z.read("word/" + target.lstrip("/"))
            self.img_count += 1
            ext = Path(target).suffix
            name = f"m{self.module_no:02d}_{self.img_count}{ext}"
            IMG_OUT.mkdir(parents=True, exist_ok=True)
            (IMG_OUT / name).write_bytes(data)
            found.append({"t": "img", "src": f"/static/content/{name}"})
        return found

    # ---------- blocks ----------
    def para_style(self, p):
        st = p.find(f"{W}pPr/{W}pStyle")
        return st.get(W + "val") if st is not None else ""

    def blocks(self):
        body = self.doc.find(W + "body")
        for el in self._flatten(body):
            if el.tag == W + "p":
                yield from self.para(el)
            elif el.tag == W + "tbl":
                yield self.table(el)

    def _flatten(self, parent):
        for el in parent:
            if el.tag == W + "sdt":
                c = el.find(W + "sdtContent")
                if c is not None:
                    yield from self._flatten(c)
            else:
                yield el

    def para(self, p):
        yield from self.images(p)
        style = self.para_style(p)
        h, text = self.runs_html(p)
        if not text.strip():
            return
        if style.startswith("Heading"):
            lvl = int(re.sub(r"\D", "", style) or 4)
            yield {"t": f"h{lvl}", "text": text.strip()}
            return
        if style == "Code":
            yield {"t": "code", "text": text}
            return
        if style in ("Quote", "IntenseQuote"):
            yield {"t": "quote", "html": h}
            return
        num = p.find(f"{W}pPr/{W}numPr")
        if num is not None or style == "ListParagraph":
            ordered, level = False, 0
            if num is not None:
                nid = num.find(W + "numId")
                ilvl = num.find(W + "ilvl")
                level = int(ilvl.get(W + "val")) if ilvl is not None else 0
                fmt = self.numfmt.get(nid.get(W + "val") if nid is not None else "", {}).get(str(level), "bullet")
                ordered = fmt not in ("bullet", "none")
            yield {"t": "li", "html": h, "plain": text, "ordered": ordered, "level": level}
            return
        kind = None
        for prefix, k in CALLOUTS:
            if text.startswith(prefix) and ":" in text[: len(prefix) + 45]:
                kind = k
                break
        b = {"t": "p", "html": h, "plain": text}
        if kind:
            b["callout"] = kind
        yield b

    def table(self, tbl):
        rows = []
        for tr in tbl.findall(W + "tr"):
            cells = []
            for tc in tr.findall(W + "tc"):
                span = tc.find(f"{W}tcPr/{W}gridSpan")
                paras = []
                plains = []
                for p in tc.iter(W + "p"):
                    h, t = self.runs_html(p)
                    if t.strip():
                        paras.append(h)
                        plains.append(t)
                cell = {"html": "<br>".join(paras), "plain": "\n".join(plains)}
                if span is not None:
                    cell["span"] = int(span.get(W + "val"))
                cells.append(cell)
            rows.append(cells)
        return {"t": "table", "rows": rows}


def group_lists(blocks):
    out = []
    for b in blocks:
        if b["t"] == "li":
            prev = out[-1] if out else None
            attrs = {k: b.get(k) for k in ("teacher", "reveal", "stage")}
            if prev and prev["t"] == "list" and prev["ordered"] == b["ordered"] and all(prev.get(k) == v for k, v in attrs.items()):
                prev["items"].append({"html": b["html"], "level": b["level"], "plain": b["plain"]})
                continue
            nb = {"t": "list", "ordered": b["ordered"], "items": [{"html": b["html"], "level": b["level"], "plain": b["plain"]}]}
            nb.update({k: v for k, v in attrs.items() if v is not None})
            out.append(nb)
        else:
            out.append(b)
    return out


def section_kind(title):
    if TEACHER_SECTIONS.match(title):
        return "teacher"
    if title.startswith("Câu hỏi ôn tập"):
        return "review"
    if title.startswith("Bài kiểm tra cuối khóa"):
        return "exam"
    if title.startswith("Thực hành"):
        return "practice"
    return "content"


def parse_doc(path: Path, module_no: int):
    d = Doc(path, module_no)
    title, sections, intro = None, [], []
    cur = None
    for b in d.blocks():
        if b["t"] == "h1" and title is None:
            title = b["text"]
            continue
        if b["t"] == "h2":
            cur = {"title": b["text"], "kind": section_kind(b["text"]), "blocks": []}
            sections.append(cur)
            continue
        (cur["blocks"] if cur else intro).append(b)
    # bỏ dòng ngày tháng · tác giả ngay dưới tiêu đề
    intro = [b for b in intro if not (b["t"] == "p" and re.match(r"^\w{3} \d{1,2}, \d{4}", b.get("plain", "")))]
    if intro:
        sections.insert(0, {"title": "Giới thiệu", "kind": "content", "blocks": intro})
    for i, s in enumerate(sections):
        s["id"] = f"s{i}"
    return title, sections


def mark_regions(module_no, sections):
    """Gắn cờ teacher / reveal / stage cho từng block trong phần thực hành."""
    practice_no = None
    for s in sections:
        m = re.match(r"Thực hành (\d+)", s["title"])
        if s["kind"] == "practice" and m:
            practice_no = int(m.group(1))
            s["activity"] = f"m{module_no:02d}-th{practice_no}"
        teacher = reveal = stage = None
        for b in s["blocks"]:
            if b["t"] == "h3":
                teacher = True if TEACHER_H3.match(b["text"]) else None
                reveal = s.get("activity") if (s["kind"] == "practice" and ANSWER_H3.match(b["text"])) else None
                sm = STAGE_H3.match(b["text"])
                stage = int(sm.group(1)) if (sm and s["kind"] == "practice") else None
            elif b["t"] == "p" and s["kind"] == "practice" and ANSWER_P.match(b.get("plain", "")):
                reveal = s.get("activity")
            if teacher:
                b["teacher"] = True
            if reveal:
                b["reveal"] = reveal
            if stage:
                b["stage"] = stage
        s["blocks"] = group_lists(s["blocks"])


def cell(c):
    return c["plain"].strip()


def review_activity(module_no, section):
    qs = []
    for b in section["blocks"]:
        if b["t"] != "table":
            continue
        for row in b["rows"][1:]:
            if len(row) >= 3 and cell(row[1]):
                qs.append({"id": f"q{len(qs) + 1}", "text": cell(row[1]), "answer": cell(row[2])})
    return {
        "id": f"m{module_no:02d}-review",
        "type": "open",
        "title": "Câu hỏi ôn tập",
        "scope": "student",
        "intro": "Tự trả lời từng câu bằng lời của mình. Gợi ý đáp án hiện ra khi giảng viên công bố.",
        "questions": qs,
    }


OPT_RE = re.compile(r"\s*·\s*(?=[A-D]\.\s)")


def parse_mcq(text):
    m = re.match(r"^\(Buổi (\d+)\)\s*(.*?)\s+A\.\s(.*)$", text.strip(), re.S)
    if not m:
        return None
    module, stem, rest = int(m.group(1)), m.group(2).strip(), "A. " + m.group(3)
    opts = []
    for part in OPT_RE.split(rest):
        mm = re.match(r"^([A-D])\.\s(.*)$", part.strip(), re.S)
        if mm:
            opts.append({"key": mm.group(1), "text": mm.group(2).strip()})
    return {"module": module, "text": stem, "options": opts}


def exam_questions(section):
    qs, key = [], {}
    for b in section["blocks"]:
        if b["t"] == "list":
            for it in b["items"]:
                q = parse_mcq(it["plain"])
                if q:
                    qs.append(q)
        elif b["t"] == "p" and b["plain"].startswith("Đáp án:"):
            for n, k in re.findall(r"(\d+)([A-D])", b["plain"]):
                key[int(n)] = k
    for i, q in enumerate(qs, 1):
        q["id"] = f"q{i}"
        q["correct"] = key.get(i)
    return qs


CIA_MAP = {"Bí mật": "C", "Toàn vẹn": "I", "Sẵn sàng": "A"}


def cia_activity(sections):
    for s in sections:
        for b in s["blocks"]:
            if b["t"] == "table" and len(b["rows"][0]) >= 3 and cell(b["rows"][0][0]).startswith("Sự việc giả lập") and "Mục tiêu bị phá" in cell(b["rows"][0][1]):
                qs = []
                for row in b["rows"][1:]:
                    target = cell(row[1])
                    correct = sorted({v for k, v in CIA_MAP.items() if k.lower() in target.lower()}, key="CIA".index)
                    qs.append({
                        "id": f"q{len(qs) + 1}",
                        "text": cell(row[0]),
                        "options": [{"key": "C", "text": "C – Bí mật"}, {"key": "I", "text": "I – Toàn vẹn"}, {"key": "A", "text": "A – Sẵn sàng"}],
                        "correct": correct,
                        "explain": f"{target}. Kiểm soát gợi ý: {cell(row[2])}" + (f" (học kỹ ở buổi {cell(row[3])})" if len(row) > 3 and cell(row[3]) not in ("", "–") else ""),
                    })
                return {
                    "id": "m01-cia",
                    "type": "multi",
                    "title": "Trò chơi thẻ C – I – A: sự việc này phá mục tiêu nào?",
                    "scope": "student",
                    "intro": "Với mỗi sự việc, chọn mọi mục tiêu bảo mật bị phá (có thể chọn nhiều).",
                    "questions": qs,
                }
    return None


def main(src_dir: Path):
    build_pack()
    files = sorted(src_dir.glob("*.docx"))
    OUT.mkdir(parents=True, exist_ok=True)
    if IMG_OUT.exists():
        for f in IMG_OUT.iterdir():
            f.unlink()
    modules = {}
    for f in files:
        m = re.match(r"Buổi (\d+)", f.name)
        if m:
            modules[int(m.group(1))] = f
        elif "Tổng quan" in f.name:
            modules[0] = f
    exam = None
    parsed = {}
    for no in sorted(modules):
        title, sections = parse_doc(modules[no], no)
        mark_regions(no, sections)
        parsed[no] = (title, sections)
        for s in sections:
            if s["kind"] == "exam":
                exam = exam_questions(s)

    index = []
    for no, (title, sections) in parsed.items():
        activities = []
        cia = cia_activity(sections) if no == 1 else None
        if cia:
            activities.append(cia)
        if exam and 1 <= no <= 9:
            qs = [dict(q) for q in exam if q["module"] == no]
            if qs:
                for i, q in enumerate(qs, 1):
                    q["id"] = f"q{i}"
                activities.append({"id": f"m{no:02d}-quiz", "type": "mcq", "title": "Kiểm tra nhanh", "scope": "student",
                                   "intro": "Mỗi câu chọn một đáp án đúng nhất.", "questions": qs})
        for s in sections:
            if s["kind"] == "practice" and s.get("activity"):
                activities.append({"id": s["activity"], "type": "practice", "title": s["title"], "scope": "student", "section": s["id"]})
            elif s["kind"] == "review":
                activities.append(review_activity(no, s))
            elif s["kind"] == "exam" and exam:
                activities.append({"id": f"m{no:02d}-exam", "type": "mcq", "title": "Bài kiểm tra cuối khóa (20 câu)", "scope": "student",
                                   "intro": "Mỗi câu chọn một đáp án đúng nhất. Mỗi câu ghi buổi liên quan để biết cần ôn phần nào.", "questions": exam})
        short = re.sub(r"^(Buổi \d+|Giáo trình[^–]*)\s*–\s*", "", title)
        doc = {"no": no, "title": title, "short": short, "sections": sections, "activities": activities}
        doc = add_log_investigation(compact(student_view(polish(revise(doc)))))
        (OUT / f"m{no:02d}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        index.append({"no": no, "title": title, "short": short})
        print(f"m{no:02d}: {len(doc['sections'])} phần, {len(doc['activities'])} hoạt động – {title}")
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else ROOT.parent))
