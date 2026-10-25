"""Bản xem của học viên: bỏ lời dặn dành cho giảng viên, gắn hoạt động vào đúng chỗ trong bài.

Chạy sau production_copy.polish. Hàm apply() chạy lại nhiều lần vẫn cho cùng kết quả.
Block mới {"t": "activity", "id": ..., "title": ..., "inline": bool, "questions": [...]}:
inline = học viên trả lời ngay trong bài; ngược lại là thẻ bấm để mở bài làm.
Giảng viên vẫn là người mở/đóng hoạt động.
"""
import html
import re

HIDE_SECTIONS = re.compile(r"^Buổi này tiếp nối buổi trước")
QUESTION_H3 = re.compile(r"^Câu hỏi của (buổi|chương)")
WARMUP_H3 = re.compile(r"^Khởi động")
SUMMARY_TITLE = "Tóm tắt"

# đoạn chỉ dành cho giảng viên: ẩn với học viên, giảng viên vẫn thấy (nhãn "Chỉ giảng viên")
TEACHER_P = re.compile(
    r"^(Giảng viên hỏi lớp|Cho giảng viên:|Cách tổ chức:|Hỏi lớp:|Giảng viên lật tờ|Giảng viên đọc to|"
    r"Tùy chọn cho giảng viên|Dùng cho trò chơi thẻ màu|Hầu như lớp nào cũng có người|"
    r"Tờ \"Việc hẹn sửa sau\")")

# đổi cách nói hướng tới giảng viên thành lời cho người học
PREFIX_REWRITES = [
    ("Demo cho giảng viên – ", "Minh họa – "),
    ("Minh họa cho giảng viên – ", "Minh họa – "),
    ("Ví dụ cho giảng viên (", "Ví dụ ("),
    ("Chiếu email sau (", "Email mẫu ("),
    ("Giảng viên có thể chạy đoạn mã dưới đây để cả lớp thấy ba kỹ thuật khác nhau thế nào.",
     "Đoạn mã dưới đây cho thấy ba kỹ thuật khác nhau thế nào."),
    ("Câu hỏi cho lớp sau khi chạy:", "Câu hỏi suy ngẫm:"),
    ("Câu hỏi cho lớp trước khi giảng:", "Câu hỏi suy ngẫm:"),
    ("Câu hỏi cho lớp:", "Câu hỏi suy ngẫm:"),
]
INLINE_REWRITES = [
    ("Giảng viên làm, học viên làm theo (", "Các bước thực hiện ("),
]
# câu cuối đoạn chỉ có ý nghĩa với người dạy
DROP_SENTENCES = re.compile(
    r"\s*(Kỳ vọng:[^\n]*$|Thường sẽ có người trả lời có\.|Ghi lại các lý do để dùng trong Thực hành \d+\.|"
    r"Giảng viên ghi lại danh sách\.|Giảng viên thu thẻ[^.]*\.)")
DROP_ITEM = re.compile(r"[Gg]iảng viên (mời|chọn|gọi|nhận xét chung)")
QUOTE = re.compile(r"[\"“]([^\"”]{15,})[\"”]")


def _plain(b):
    return b.get("plain") or b.get("text") or ""


def _rewrite(b):
    if b["t"] != "p" or b.get("teacher"):
        return
    p = _plain(b)
    q = p
    for a, c in PREFIX_REWRITES:
        if q.startswith(a):
            q = c + q[len(a):]
    for a, c in INLINE_REWRITES:
        q = q.replace(a, c)
    q = DROP_SENTENCES.sub("", q).strip()
    if q == p:
        return
    h = b.get("html", "")
    for a, c in PREFIX_REWRITES + INLINE_REWRITES:
        h = h.replace(html.escape(a, quote=False), c).replace(a, c)
    h = DROP_SENTENCES.sub("", h).strip()
    b["html"], b["plain"] = h, q


def _activity_block(a, inline):
    blk = {"t": "activity", "id": a["id"], "title": a["title"], "inline": inline}
    if inline:
        blk["questions"] = [qq["text"] for qq in a["questions"]]
    return blk


def apply(doc):
    no = doc["no"]
    acts = {a["id"]: a for a in doc["activities"]}
    new_acts = []
    placed = set()
    for s in doc["sections"]:
        if HIDE_SECTIONS.match(s["title"]):
            s["kind"] = "teacher"
        for b in s["blocks"]:
            if b["t"] == "activity":
                placed.add(b["id"])
            if b["t"] == "p" and not b.get("teacher") and TEACHER_P.match(_plain(b)):
                b["teacher"] = True
        out = []
        blocks = s["blocks"]
        i = 0
        while i < len(blocks):
            b = blocks[i]
            if b["t"] == "list" and not b.get("teacher"):
                keep = [it for it in b["items"] if not DROP_ITEM.search(it.get("plain") or it.get("html", ""))]
                if keep and len(keep) != len(b["items"]):
                    b["items"] = keep
            _rewrite(b)
            if b["t"] == "h3" and b["text"] == "Cách tổ chức":
                b["text"] = "Cách làm bài"
            out.append(b)
            # "Câu hỏi của buổi": danh sách câu hỏi -> ô trả lời ngay trong bài
            if b["t"] == "h3" and QUESTION_H3.match(b["text"]) and s["kind"] == "content":
                j = i + 1
                while j < len(blocks) and blocks[j]["t"] == "p" and blocks[j].get("teacher"):
                    j += 1
                if j < len(blocks) and blocks[j]["t"] == "list":
                    out.extend(blocks[i + 1:j])
                    aid = f"m{no:02d}-opening"
                    a = acts.get(aid) or {
                        "id": aid, "type": "open", "scope": "student", "title": b["text"],
                        "intro": "Trả lời bằng suy nghĩ của bạn trước khi vào bài. Phần \"Quay lại tình huống\" cuối buổi giúp bạn đối chiếu.",
                        "questions": [{"id": f"q{k}", "text": it.get("plain") or re.sub(r"<[^>]+>", "", it["html"])}
                                      for k, it in enumerate(blocks[j]["items"], 1)],
                    }
                    if aid not in acts:
                        new_acts.append(a); acts[aid] = a
                    out.append(_activity_block(a, True)); placed.add(aid)
                    i = j + 1
                    continue
            # "Khởi động": câu hỏi trong ngoặc kép -> một ô trả lời
            if b["t"] == "h3" and WARMUP_H3.match(b["text"]) and i + 1 < len(blocks) and blocks[i + 1]["t"] == "p":
                p = blocks[i + 1]
                m = QUOTE.search(_plain(p))
                aid = f"m{no:02d}-warmup"
                if m and aid not in placed:
                    a = acts.get(aid) or {
                        "id": aid, "type": "open", "scope": "student", "title": b["text"],
                        "intro": "Chia sẻ một trường hợp từ công việc của bạn. Không ghi dữ liệu thật của khách hàng.",
                        "questions": [{"id": "q1", "text": m.group(1).strip()}],
                    }
                    if aid not in acts:
                        new_acts.append(a); acts[aid] = a
                    p["teacher"] = True  # lời dặn tổ chức; câu hỏi đã chuyển vào ô trả lời
                    out.append(p)
                    out.append(_activity_block(a, True)); placed.add(aid)
                    i += 2
                    continue
            i += 1
        s["blocks"] = out
        # phần thực hành: thẻ vào bài làm ngay đầu phần
        aid = s.get("activity")
        if aid and aid in acts and aid not in placed and s["kind"] in ("practice", "content"):
            s["blocks"].insert(0, _activity_block(acts[aid], False)); placed.add(aid)

    # trò chơi thẻ C – I – A đặt cạnh bảng tình huống của Bài 1
    cia = f"m{no:02d}-cia"
    if cia in acts and cia not in placed:
        for s in doc["sections"]:
            for k, b in enumerate(s["blocks"]):
                if b["t"] == "p" and _plain(b).startswith("Dùng cho trò chơi thẻ màu"):
                    s["blocks"].insert(k + 1, _activity_block(acts[cia], False)); placed.add(cia)
                    break
            if cia in placed:
                break

    # các bài còn lại (kiểm tra nhanh, ôn tập, kiểm tra cuối khóa) đặt cuối phần Tóm tắt
    summary = next((s for s in doc["sections"] if s["title"].startswith(SUMMARY_TITLE) or s["title"].startswith("Tổng kết khóa học")), None)
    if summary:
        for a in doc["activities"]:
            if a["id"] not in placed and a.get("scope") == "student":
                summary["blocks"].append(_activity_block(a, False)); placed.add(a["id"])

    doc["activities"] = new_acts + doc["activities"]
    return doc


if __name__ == "__main__":
    # áp dụng trực tiếp lên JSON đã dựng (không cần file Word nguồn)
    import json
    from pathlib import Path
    out = Path(__file__).resolve().parent.parent / "app" / "content"
    for f in sorted(out.glob("m*.json")):
        d = apply(json.loads(f.read_text(encoding="utf-8")))
        f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        n = sum(1 for s in d["sections"] for b in s["blocks"] if b["t"] == "activity")
        print(f.name, n, "vị trí hoạt động")
