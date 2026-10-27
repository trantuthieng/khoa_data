"""Hàm dựng đáp án giảng viên: khối nội dung, module và dây nối của bài làm mẫu, các mục giải thích chuẩn."""


def P(html):
    return {"t": "p", "html": html}


def UL(*items):
    return {"t": "list", "ordered": False, "items": [{"html": x, "level": 0} for x in items]}


def OL(*items):
    return {"t": "list", "ordered": True, "items": [{"html": x, "level": 0} for x in items]}


def TABLE(head, *rows):
    return {"t": "table", "rows": [[{"html": c} for c in r] for r in (head, *rows)]}


def CODE(text):
    return {"t": "code", "text": text}


def N(id, kind, x, y, text="", title=None, tag=None, p=None):
    """Một module trên bảng mẫu (cùng định dạng bài nộp của học viên)."""
    n = {"id": id, "kind": kind, "x": x, "y": y, "text": text}
    if title:
        n["title"] = title
    if tag:
        n["tag"] = tag
    if p:
        n["p"] = p
    return n


def L(a, b, **fields):
    """Dây nối a → b, kèm chữ ghi trên dây."""
    return {"id": "k_" + a + "_" + b, "from": a, "to": b, **fields}


def board(nodes, links=()):
    return {"nodes": list(nodes), "links": list(links)}


READ_BOARD = P("Bảng trên là một bài làm đạt điểm tối đa, dựng bằng đúng các module học viên có. Kéo nền để xem từng vùng; "
               "bấm <b>Xem toàn bộ</b> để thấy cả bảng. Bảng tổng hợp và bản đọc nhanh ở dưới bảng tự lập từ module và dây nối.")
NOT_EXACT = P("Học viên không cần đặt module đúng vị trí hay viết đúng từng chữ. Chấm theo quyết định, cách nối và lý do.")


def key(summary, fields, modules=None, links=None, more=(), rubric=None, mistakes=None, flow=None, read=None):
    """Đáp án theo bố cục chuẩn.

    modules: [(module, nội dung cần có, vì sao)]; links: [(dây nối, ghi trên dây, ý nghĩa)];
    more: [(tiêu đề, [khối])] chèn sau phần dây nối; rubric: [(tiêu chí, điểm, đạt khi)];
    mistakes: [(lỗi, dấu hiệu, nhận xét gợi ý)]; flow: [bước chữa bài].
    """
    sections = []
    if read is not False:
        sections.append({"title": "Cách đọc bài làm mẫu", "blocks": read or [READ_BOARD, NOT_EXACT]})
    if modules:
        sections.append({"title": "Từng module: ghi gì và vì sao", "blocks": [
            TABLE(["Module", "Nội dung cần có", "Vì sao – điều cần thấy trong bài học viên"], *modules)]})
    if links:
        sections.append({"title": "Các dây nối: nối thế nào", "blocks": [TABLE(["Dây nối", "Ghi trên dây", "Ý nghĩa"], *links)]})
    sections += [{"title": t, "blocks": b} for t, b in more]
    if rubric:
        sections.append({"title": "Thang điểm 10", "private": True, "blocks": [
            TABLE(["Tiêu chí", "Điểm", "Đạt đủ khi"], *rubric),
            P("Cảnh báo ⚠ trên bảng của học viên (nếu có) là dấu hiệu nhanh: còn cảnh báo nào thì tiêu chí tương ứng chưa đạt.")]})
    if mistakes:
        sections.append({"title": "Lỗi hay gặp và nhận xét gợi ý", "private": True, "blocks": [
            TABLE(["Lỗi", "Dấu hiệu trong bài", "Câu hỏi hoặc nhận xét gợi ý"], *mistakes)]})
    if flow:
        sections.append({"title": "Gợi ý chữa bài trên lớp", "blocks": [OL(*flow)]})
    return {"summary": summary, "fields": fields, "sections": sections}


def case_key(summary, parts, points, rubric, mistakes, flow=None):
    """Bài tập tình huống ba câu (part1–part3).

    parts: ba bài trả lời mẫu; points: [(câu, ý bắt buộc, chấp nhận thêm)];
    rubric: ba "đạt đủ khi" theo tiêu chí 3 – 4 – 3 điểm của đề.
    """
    return key(
        summary, {"part1": parts[0], "part2": parts[1], "part3": parts[2]},
        read=[P("Ba ô phía trên là bài trả lời mẫu đạt 10 điểm. Học viên viết bằng lời của mình; chấm theo các ý bắt buộc dưới đây, "
                "không chấm theo câu chữ.")],
        more=[("Ý cần có trong từng câu", [TABLE(["Câu", "Ý bắt buộc", "Chấp nhận thêm"], *points)])],
        rubric=[("Hiểu đúng tình huống", "3", rubric[0]), ("Đề xuất phù hợp, có lý do", "4", rubric[1]),
                ("Kiểm chứng được kết quả", "3", rubric[2])],
        mistakes=mistakes, flow=flow)
