"""Bản gọn của buổi 5 và 6: viết lại bốn bài lý thuyết, thêm sơ đồ, bỏ đoạn mã không cần.

Chạy sau student_view.apply. Hàm apply() chạy lại nhiều lần vẫn cho cùng kết quả.
Block mới {"t": "figure", "html": <svg hoặc html>, "caption": ..., "plain": ...}: sơ đồ vẽ bằng SVG,
màu lấy từ biến CSS nên tự đổi theo giao diện sáng/tối.
File luyện tập của Thực hành 6, 7 do tools/practice_files.py tạo, học viên tải từ bài.
"""
import html
import re

COLORS = ("mut", "brand", "ok", "bad", "acc")


def esc(s):
    return html.escape(str(s), quote=False)


def rich(s):
    """**đậm** → <strong>; phần còn lại được escape."""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(s))


def plain(s):
    return s.replace("**", "")


# ---------- block ----------
def P(s, **flags):
    return {"t": "p", "plain": plain(s), "html": rich(s), **flags}


def LINK(href, label, after=""):
    return {"t": "p", "plain": label + after, "html": f'<a href="{href}" download>{esc(label)}</a>{esc(after)}'}


def H(s):
    return {"t": "h3", "text": s}


def UL(*items, ordered=False):
    return {"t": "list", "ordered": ordered, "items": [{"plain": plain(i), "html": rich(i), "level": 0} for i in items]}


def OL(*items):
    return UL(*items, ordered=True)


def T(*rows, **flags):
    return {"t": "table", "rows": [[{"plain": plain(c), "html": rich(c)} for c in r] for r in rows], **flags}


def CODE(s):
    return {"t": "code", "text": s}


def FIG(fig, caption):
    body = fig.render() if isinstance(fig, Fig) else fig
    return {"t": "figure", "html": body, "caption": caption, "plain": caption}


def MISS(s):
    return P("**Hiểu nhầm hay gặp:** " + s, callout="misconception")


# ---------- SVG ----------
class Fig:
    def __init__(self, name, w, h, label):
        self.name, self.w, self.h, self.label = name, w, h, label
        self.parts = []

    def rect(self, x, y, w, h, cls="box", rx=8, dash=False):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}{" dash" if dash else ""}"/>')

    def poly(self, pts, cls="box"):
        self.parts.append(f'<polygon points="{" ".join(f"{x},{y}" for x, y in pts)}" class="{cls}"/>')

    def text(self, x, y, s, cls="", size=13, anchor="middle", bold=False):
        segs = s if isinstance(s, list) else [(s, "")]
        inner = "".join(f'<tspan class="{c}">{esc(t)}</tspan>' if c else esc(t) for t, c in segs)
        attrs = (f' class="{cls}"' if cls else "") + (' font-weight="600"' if bold else "")
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}"{attrs}>{inner}</text>')

    def box(self, x, y, w, h, lines, cls="box", size=13, bold=True, dash=False, rx=8, sub=1.5):
        """Hộp có chữ căn giữa; dòng đầu đậm, các dòng sau nhỏ hơn một chút. Dòng: str hoặc (nội dung, class)."""
        self.rect(x, y, w, h, cls, rx, dash)
        lines = [ln if isinstance(ln, tuple) else (ln, "") for ln in lines]
        lh = size * 1.32
        y0 = y + h / 2 - (len(lines) - 1) * lh / 2 + size * 0.35
        for i, (t, c) in enumerate(lines):
            self.text(round(x + w / 2, 1), round(y0 + i * lh, 1), t, c, size if i == 0 else size - sub, bold=bold and i == 0)

    def arrow(self, x1, y1, x2, y2, color="mut", label=None, lx=None, ly=None, dash=False, both=False, lcls="f-mut", lsize=12):
        m = f"url(#{self.name}-{color})"
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="l-{color}{" dash" if dash else ""}" '
                          f'marker-end="{m}"{f" marker-start={chr(34)}{m}{chr(34)}" if both else ""}/>')
        if label:
            self.text(lx if lx is not None else (x1 + x2) / 2, ly if ly is not None else (y1 + y2) / 2 - 8, label, lcls, lsize)

    def line(self, x1, y1, x2, y2, color="mut", dash=False):
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="l-{color}{" dash" if dash else ""}"/>')

    def path(self, d, color="mut", dash=False, arrow=True):
        m = f' marker-end="url(#{self.name}-{color})"' if arrow else ""
        self.parts.append(f'<path d="{d}" class="ln l-{color}{" dash" if dash else ""}"{m}/>')

    def render(self):
        defs = "".join(f'<marker id="{self.name}-{c}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                       f'orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" class="m-{c}"/></marker>' for c in COLORS)
        return (f'<svg class="dg" viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{html.escape(self.label)}" '
                f'xmlns="http://www.w3.org/2000/svg"><defs>{defs}</defs>{"".join(self.parts)}</svg>')


def chevrons(f, steps, x0, y, w, h, step, tip=14, size=12):
    """Dãy bước hình mũi tên. steps: [(dòng..., class)]."""
    for i, (lines, cls) in enumerate(steps):
        x = x0 + i * step
        pts = [(x, y), (x + w - tip, y), (x + w, y + h / 2), (x + w - tip, y + h), (x, y + h)]
        if i:
            pts.append((x + tip, y + h / 2))
        f.poly(pts, cls)
        lh = size * 1.3
        y1 = y + h / 2 - (len(lines) - 1) * lh / 2 + size * 0.35
        cx = x + w / 2 + (tip / 2 if i else 0) - tip / 2
        for k, t in enumerate(lines):
            f.text(round(cx, 1), round(y1 + k * lh, 1), t, "" if k < 2 else "f-mut", size if k < 2 else size - 1, bold=k == 0)


# ====================== Buổi 5: sơ đồ ======================
def d5_hanh_trinh():
    f = Fig("m5-ht", 720, 250, "Hành trình file danh sách nợ qua sáu chặng và biện pháp bảo vệ ở mỗi chặng")
    f.rect(10, 7, 14, 11, "r-brand", 3); f.text(30, 17, "Đang lưu", anchor="start", size=12)
    f.rect(110, 7, 14, 11, "r-ok", 3); f.text(130, 17, "Đang dùng", anchor="start", size=12)
    f.arrow(215, 13, 248, 13, "acc"); f.text(255, 17, "Đang truyền – HTTPS/TLS bảo vệ trên đường đi", anchor="start", size=12)
    nodes = [(["Hệ thống", "(CSDL)"], "r-brand", ["Phân quyền", "tài khoản"], ["Ai cũng", "xuất đủ cột"]),
             (["Laptop", "chị Dung"], "r-brand", ["BitLocker", "(mã hóa ổ đĩa)"], ["Mất máy là", "mất file"]),
             (["Mở file,", "lọc cột"], "r-ok", ["Khóa màn hình", "khi rời ghế"], ["Người qua lại", "nhìn, chụp"]),
             (["File mới", "đã mã hóa"], "r-brand", ["Mật khẩu mở", "file mạnh"], ["Ai có file", "là đọc được"]),
             (["OneDrive", "(cloud)"], "r-brand", ["Link 1 người,", "hạn 7 ngày"], ["Link Anyone:", "ai cũng mở"]),
             (["Máy", "đối tác"], "r-ok", ["Hợp đồng,", "cam kết xóa"], ["Đơn vị hết", "cách kiểm soát"])]
    links = ["acc", "mut", "mut", "acc", "acc"]
    f.text(1, 116, "Cái gì bảo vệ:", "f-mut", 11.5, "start")
    f.text(1, 170, "Nếu thiếu:", "f-bad", 11.5, "start")
    for i, (name, cls, keep, miss) in enumerate(nodes):
        x = 1 + i * 123
        f.box(x, 40, 102, 58, name, cls, 12.5, sub=0)
        for k, t in enumerate(keep):
            f.text(x + 51, 134 + k * 16, t, "", 12)
        for k, t in enumerate(miss):
            f.text(x + 51, 188 + k * 16, t, "f-bad", 12)
        if i < 5:
            f.arrow(x + 102, 69, x + 123, 69, links[i])
    f.text(360, 240, "Một lớp bảo vệ không đi theo dữ liệu suốt hành trình: mỗi chặng cần biện pháp riêng.", "f-mut", 12.5)
    return f


def d5_doi_xung():
    f = Fig("m5-dx", 720, 240, "So sánh mã hóa đối xứng và bất đối xứng")
    for row, (y, name, sub, k1, k2) in enumerate([
            (40, "Đối xứng", "một khóa chung", "mã hóa bằng khóa K", "giải mã bằng cùng khóa K"),
            (140, "Bất đối xứng", "một cặp khóa", "khóa công khai của B", "chỉ khóa bí mật của B")]):
        f.text(10, y + 20, name, "", 14, "start", True)
        f.text(10, y + 38, sub, "f-mut", 12, "start")
        f.box(140, y, 140, 46, ["Bản rõ", ("KH001, 0900000001", "mono")], "box", 12.5)
        f.box(360, y, 140, 46, ["Bản mã", ("gAAAAABq21QP…", "mono")], "r-warn", 12.5)
        f.box(580, y, 130, 46, ["Bản rõ", ("KH001, 0900000001", "mono")], "box", 12.5)
        f.arrow(280, y + 23, 360, y + 23, "brand" if row == 0 else "ok", k1, 320, y - 8, lcls="", lsize=12)
        f.arrow(500, y + 23, 580, y + 23, "brand" if row == 0 else "bad", k2, 540, y - 8, lcls="", lsize=12)
        if row == 0:
            f.line(10, 108, 710, 108, "mut", dash=True)
    f.text(360, 224, "HTTPS dùng cả hai: bất đối xứng để thỏa thuận khóa phiên, rồi đối xứng để chở dữ liệu cho nhanh.", "f-mut", 12.5)
    return f


def d5_bam():
    f = Fig("m5-bam", 720, 200, "Hàm băm: khác một ký tự cho dấu vân tay khác hẳn")
    for y, last, out in [(30, "1", "40d27f42d6f78620…"), (100, "2", "5bb597cc9a5faf9d…")]:
        f.rect(10, y, 200, 40, "box")
        f.text(110, y + 25, [("KH001, 090000000", "mono"), (last, "mono f-bad b")], size=13)
        f.box(510, y, 200, 40, [(out, "mono")], "r-brand", 13, bold=False)
    f.box(280, 48, 160, 74, ["Hàm băm", "SHA-256", ("không dùng khóa", "f-mut")], "r-note", 13)
    f.arrow(210, 50, 280, 72); f.arrow(210, 120, 280, 98)
    f.arrow(440, 72, 510, 50); f.arrow(440, 98, 510, 120)
    f.text(360, 166, "Khác 1 chữ số → dấu vân tay khác hẳn. Từ dấu vân tay không suy ngược được dữ liệu gốc.", "", 12.5)
    f.text(360, 188, "Nhưng số điện thoại chỉ có khoảng 1 tỷ khả năng: băm thử hết là dò ra → băm không phải ẩn danh.", "f-bad", 12.5)
    return f


def d5_chu_ky():
    f = Fig("m5-ck", 720, 296, "Chữ ký số: ký bằng khóa bí mật, kiểm tra bằng khóa công khai")
    f.text(10, 18, "KÝ – người gửi dùng khóa bí mật", "", 13, "start", True)
    f.box(10, 30, 150, 44, ["Văn bản"], "box")
    f.box(270, 30, 150, 44, ["Dấu vân tay"], "r-note")
    f.box(530, 30, 180, 44, ["Chữ ký", ("gửi kèm văn bản", "f-mut")], "r-brand", 13)
    f.arrow(160, 52, 270, 52, label="băm", ly=44)
    f.arrow(420, 52, 530, 52, "bad", "khóa bí mật", ly=44, lcls="f-bad")
    f.line(10, 96, 710, 96, "mut", dash=True)
    f.text(10, 120, "KIỂM TRA – người nhận dùng khóa công khai", "", 13, "start", True)
    f.box(10, 132, 150, 40, ["Văn bản nhận được"], "box", 12.5)
    f.box(270, 132, 150, 40, ["Dấu vân tay A"], "r-note", 12.5)
    f.box(10, 196, 150, 40, ["Chữ ký"], "r-brand", 12.5)
    f.box(270, 196, 150, 40, ["Dấu vân tay B"], "r-note", 12.5)
    f.arrow(160, 152, 270, 152, label="băm lại", ly=145)
    f.arrow(160, 216, 270, 216, "ok", "khóa công khai", ly=209, lcls="f-ok")
    f.box(530, 150, 180, 70, ["A = B ?", ("khớp: chữ ký hợp lệ", "f-ok"), ("lệch: văn bản đã bị sửa", "f-bad")], "r-warn", 13, sub=1)
    f.arrow(420, 152, 530, 172); f.arrow(420, 216, 530, 198)
    f.text(360, 264, "Chứng minh ba điều: toàn vẹn (không bị sửa) · xác thực (đúng người giữ khóa) · chống chối bỏ.", "", 12.5)
    f.text(360, 284, "Chữ ký số không giữ bí mật: văn bản vẫn đọc được. Cần bí mật thì mã hóa thêm.", "f-mut", 12.5)
    return f


def d5_lop():
    f = Fig("m5-lop", 720, 250, "Các lớp bảo vệ dữ liệu đang lưu và kiểu rủi ro mỗi lớp để lọt")
    f.rect(10, 10, 420, 230, "r-note")
    f.text(22, 30, "Phân quyền – ai được mở thư mục, hệ thống", "", 12.5, "start", True)
    f.rect(30, 44, 380, 184, "r-brand")
    f.text(42, 64, "Mã hóa ổ đĩa (BitLocker)", "", 12.5, "start", True)
    f.rect(50, 78, 340, 138, "r-ok")
    f.text(62, 98, "Mã hóa file (mật khẩu mở, 7-Zip AES-256)", "", 12.5, "start", True)
    f.box(120, 128, 200, 70, ["File danh sách", "khách hàng"], "box", 13, bold=False, sub=0)
    f.text(460, 24, "Mỗi lớp vẫn để lọt:", "", 13, "start", True)
    for y, cls, a, b in [(52, "r-note", "Phân quyền: lọt khi dữ liệu đã ra", "file xuất, bản in, file tạm"),
                         (106, "r-brand", "Mã hóa ổ đĩa: lọt khi máy đang mở,", "chưa khóa màn hình"),
                         (160, "r-ok", "Mã hóa file: lọt khi người có mật", "khẩu mở ra rồi chuyển tiếp"),
                         (214, "box", "Sao lưu là thêm một bản sao đầy đủ:", "cũng cần phân quyền và mã hóa")]:
        f.rect(460, y - 10, 12, 12, cls, 3)
        f.text(480, y, a, "", 12.5, "start")
        f.text(480, y + 17, b, "f-mut", 12.5, "start")
    return f


def d5_321():
    f = Fig("m5-321", 720, 236, "Nguyên tắc sao lưu 3-2-1")
    f.text(14, 26, "Trụ sở – cùng một mạng", "f-mut", 12, "start")
    f.rect(10, 34, 450, 124, "r-note", dash=True)
    f.box(24, 56, 160, 56, ["Bản gốc", "máy chủ file"], "box")
    f.box(280, 56, 160, 56, ["Bản sao 1", "ổ sao lưu NAS"], "box")
    f.arrow(184, 84, 280, 84, label="sao lưu đêm", ly=76)
    f.text(235, 142, "Mã độc tống tiền trong mạng có thể mã hóa cả hai bản này", "f-bad", 12)
    f.text(494, 26, "Nơi khác, tách mạng", "f-ok", 12, "start")
    f.rect(490, 34, 220, 124, "r-ok", dash=True)
    f.box(515, 52, 170, 68, ["Bản sao 2", "ngoại tuyến hoặc", "không sửa được"], "box")
    f.arrow(440, 84, 515, 84, "ok")
    for i, (t, cls) in enumerate([("3 bản dữ liệu", "r-brand"), ("2 loại phương tiện", "r-brand"),
                                  ("1 bản ở nơi khác", "r-ok"), ("+ thử khôi phục: 0 lỗi", "r-warn")]):
        f.box(10 + i * 180, 172, 170, 28, [t], cls, 12.5, rx=14)
    f.text(360, 226, "Đồng bộ OneDrive không phải sao lưu: file bị xóa hay bị mã hóa cũng được đồng bộ y như vậy.", "f-mut", 12.5)
    return f


def d5_hai_kenh():
    f = Fig("m5-kenh", 720, 196, "File và mật khẩu đi hai kênh khác nhau")
    f.box(10, 60, 130, 86, ["Chị Dung"], "r-brand", 14)
    f.box(580, 60, 130, 86, ["Đối tác", "(người nhận)"], "r-brand", 14)
    f.box(250, 4, 220, 44, ["Người đọc trộm email", ("chỉ có file, không có mật khẩu", "f-bad")], "r-bad", 12.5, sub=0.5)
    f.line(360, 48, 360, 76, "bad", dash=True)
    f.arrow(140, 80, 580, 80, "brand", "Kênh 1: file đã mã hóa (email / OneDrive)", 360, 98, lcls="", lsize=12.5)
    f.arrow(140, 126, 580, 126, "ok", "Kênh 2: mật khẩu – gọi điện theo số trong hợp đồng", 360, 144, lcls="", lsize=12.5)
    f.text(360, 182, "Sai phổ biến nhất: ghi mật khẩu ngay trong email gửi file – lớp mã hóa thành vô nghĩa.", "f-bad", 12.5)
    return f


def d5_tls():
    f = Fig("m5-tls", 720, 282, "Các bước bắt tay TLS giữa trình duyệt và máy chủ")
    f.box(60, 6, 180, 44, ["Trình duyệt của bạn"], "r-brand")
    f.box(440, 6, 260, 44, ["Máy chủ", ("cskh.dienlucminhan.example", "mono")], "r-brand", 13, sub=1)
    f.line(150, 50, 150, 274, "mut", dash=True)
    f.line(570, 50, 570, 274, "mut", dash=True)
    f.arrow(150, 84, 570, 84, label="1. Xin kết nối, xin “giấy tờ” của máy chủ", ly=76, lcls="")
    f.arrow(570, 122, 150, 122, label="2. Gửi chứng thư số: tên miền, CA đã cấp, hạn dùng", ly=114, lcls="")
    f.box(14, 136, 300, 52, ["3. Kiểm tra: CA tin cậy? còn hạn?", "đúng tên miền đang mở? Sai → cảnh báo"], "r-warn", 12.5, sub=0)
    f.arrow(150, 214, 570, 214, both=True, label="4. Thỏa thuận khóa phiên (bất đối xứng)", ly=206, lcls="")
    f.box(150, 236, 420, 28, ["5. Dữ liệu đi bằng khóa phiên (đối xứng), có kiểm tra toàn vẹn"], "r-ok", 12.5, rx=14)
    return f


D5_URL = (
    '<div class="dg-url">'
    '<div class="u-tag">Trang thật</div>'
    '<div class="url-row"><span class="u-seg"><span class="u-txt">https://</span></span>'
    '<span class="u-seg u-dim"><span class="u-txt">cskh.</span><small>tên phụ</small></span>'
    '<span class="u-seg u-ok"><span class="u-txt">dienlucminhan.example</span><small>chủ thật → đúng trang</small></span>'
    '<span class="u-seg"><span class="u-txt">/tra-cuu</span></span></div>'
    '<div class="u-tag">Trang giả</div>'
    '<div class="url-row"><span class="u-seg"><span class="u-txt">https://</span></span>'
    '<span class="u-seg u-dim"><span class="u-txt">cskh.dienlucminhan.example.</span><small>chỉ là phần đầu – ai cũng đặt được</small></span>'
    '<span class="u-seg u-bad"><span class="u-txt">xacminh-tk.example</span><small>chủ thật → trang giả</small></span>'
    '<span class="u-seg"><span class="u-txt">/login</span></span></div>'
    '<div class="u-hint">← Tìm dấu / đầu tiên sau https:// rồi đọc ngược sang trái: phần ngay trước đuôi (.vn, .com, .example…) là chủ thật.</div>'
    '</div>')


def d5_ong():
    f = Fig("m5-ong", 720, 204, "TLS chỉ bảo vệ đường truyền")
    f.box(10, 30, 140, 60, ["Máy của bạn"], "box")
    f.box(570, 30, 140, 60, ["Máy chủ", "OneDrive"], "box")
    f.text(360, 34, "Ổ khóa HTTPS chỉ bảo vệ đoạn này", "f-mut", 12)
    f.box(150, 44, 420, 32, ["TLS: chống nghe lén, chống sửa giữa đường"], "r-ok", 13, rx=16)
    f.text(10, 126, "TLS không lo:", "f-bad", 13, "start", True)
    for i, lines in enumerate([["File sau khi", "đã tải về máy"], ["Ai được mở link", "(link Anyone)"],
                               ["Email nằm trong", "hộp thư hai bên"], ["Trang giả có", "chứng thư hợp lệ"]]):
        f.box(10 + i * 180, 138, 170, 56, lines, "r-bad", 12.5, bold=False, sub=0)
    return f


def d5_5buoc():
    f = Fig("m5-5b", 720, 122, "Quy trình chia sẻ 5 bước")
    chevrons(f, [(["1", "Duyệt nội dung", "đúng bản, đúng người"], "r-brand"),
                 (["2", "Giảm dữ liệu", "bỏ cột, sheet ẩn"], "r-warn"),
                 (["3", "Bảo vệ file", "mã hóa thật"], "r-brand"),
                 (["4", "Gửi đúng kênh", "mật khẩu kênh khác"], "r-brand"),
                 (["5", "Kiểm tra, thu hồi", "đóng link, xóa tạm"], "r-warn")], 2, 8, 140, 84, 143, size=12.5)
    for i in (1, 4):
        f.text(2 + i * 143 + 70, 112, "hay bị bỏ qua", "f-bad", 11.5)
    return f


def d5_mat_khau():
    f = Fig("m5-mk", 720, 182, "Phân biệt mã hóa thật với các kiểu chỉ chặn sửa")
    f.box(10, 62, 150, 56, ["Đóng file,", "mở lại"], "box", 13, sub=0)
    f.box(210, 50, 210, 80, ["Hỏi mật khẩu trước khi", "thấy bất kỳ nội dung nào?"], "r-warn", 13, bold=False, sub=0)
    f.box(480, 8, 232, 74, ["Có → mã hóa thật", "Encrypt with Password,", "mật khẩu mở PDF"], "r-ok", 13, sub=1)
    f.box(480, 100, 232, 74, ["Không → chỉ chặn sửa/in", "Protect Sheet, Mark as Final,", "Password to modify, quyền PDF"], "r-bad", 13, sub=1)
    f.arrow(160, 90, 210, 90)
    f.arrow(420, 78, 480, 46, "ok"); f.arrow(420, 102, 480, 136, "bad")
    return f


# ====================== Buổi 6: sơ đồ ======================
def d6_loai_truong():
    f = Fig("m6-lt", 720, 250, "Chín cột của file sản lượng xếp vào bốn loại trường")
    cols = [("Định danh trực tiếp", "một mình chỉ ra người", "r-bad", ["ho_ten", "dien_thoai"], "→ Bỏ", "không cần cho dự báo"),
            ("Định danh gián tiếp", "ghép lại thì ra người", "r-warn", ["ma_kh", "dia_chi", "phuong"], "→ Bỏ / gộp lên phường", "giữ phuong, xét nhóm nhỏ"),
            ("Thuộc tính nhạy cảm", "nói điều riêng tư", "r-bad", ["so_tien_no"], "→ Bỏ", "ngoài mục đích"),
            ("Dữ liệu phân tích", "nội dung cần dùng", "r-ok", ["loai_kh", "thang", "kwh"], "→ Giữ, tổng hợp", "theo phường – tháng")]
    for i, (name, d, cls, chips, act, note) in enumerate(cols):
        x = 4 + i * 179
        f.box(x, 6, 170, 52, [name, (d, "f-mut")], cls, 13, sub=1)
        for k, c in enumerate(chips):
            f.box(x + 25, 72 + k * 34, 120, 26, [(c, "mono")], "box", 12.5, bold=False, rx=13)
        f.arrow(x + 85, 176, x + 85, 192)
        f.box(x, 194, 170, 50, [act, (note, "f-mut")], "box", 12.5, sub=1)
    return f


def d6_pho():
    f = Fig("m6-pho", 720, 222, "Các mức giảm dữ liệu từ dữ liệu gốc đến khử nhận dạng")
    f.path("M8,34 V26 H432 V34", "bad", arrow=False)
    f.text(220, 18, "Vẫn là dữ liệu cá nhân", "f-bad", 12.5, bold=True)
    f.path("M437,34 V26 H712 V34", "ok", arrow=False)
    f.text(574, 18, "Có thể không còn – chỉ khi đã kiểm tra", "f-ok", 12.5, bold=True)
    items = [("Dữ liệu gốc", [("Nguyễn Văn A", "mono"), ("0912345678", "mono")], "r-bad"),
             ("Che (masking)", [("091****678", "mono"), ("vẫn đoán, nối được", "f-mut")], "r-bad"),
             ("Giả danh hóa", [("P-7F3A9C", "mono"), ("ai giữ khóa nối lại", "f-mut")], "r-bad"),
             ("Tổng hợp", ["An Phú, tháng 9:", "174 KH, 64.263 kWh"], "r-ok"),
             ("Khử nhận dạng", [("không còn nhận ra", "f-mut"), ("người – có đánh giá", "f-mut")], "r-ok")]
    for i, (name, lines, cls) in enumerate(items):
        f.box(8 + i * 143, 40, 132, 96, [name] + lines, cls, 13, sub=1.5)
    f.arrow(8, 158, 712, 158)
    f.text(360, 178, "Mức chi tiết giảm dần · khả năng nhận ra người giảm dần", "f-mut", 12)
    f.text(360, 208, "Che số điện thoại là giảm lộ, chưa phải ẩn danh. Dự báo theo phường: tổng hợp thường là đủ và an toàn nhất.", "", 12.5)
    return f


def d6_gia_danh():
    f = Fig("m6-gd", 720, 222, "Giả danh hóa mã khách hàng bằng HMAC và khóa bí mật")
    f.path("M625,52 V22 H75 V52", "mut", dash=True)
    f.text(350, 14, "Ai giữ khóa (hoặc bảng đối chiếu) nối ngược lại được → vẫn là dữ liệu cá nhân", "f-mut", 12)
    f.box(10, 52, 130, 50, [("KH001", "mono")], "box", 14, bold=False)
    f.box(230, 42, 220, 70, ["HMAC-SHA256", ("mã + khóa bí mật", "f-mut")], "r-brand", 13.5, sub=1.5)
    f.box(540, 52, 170, 50, [("P-4EE2E067", "mono")], "r-ok", 14, bold=False)
    f.arrow(140, 77, 230, 77); f.arrow(450, 77, 540, 77)
    f.box(250, 158, 180, 50, ["Khóa bí mật", ("cất riêng, ít người giữ", "f-mut")], "r-warn", 13, sub=1)
    f.arrow(340, 158, 340, 112, "acc")
    f.text(10, 176, "Băm thường, không có khóa:", "f-bad", 12, "start")
    f.text(10, 194, "thử hết các mã là dò ra.", "f-bad", 12, "start")
    f.text(460, 176, "Cùng khóa → cùng mã thay thế:", "", 12, "start")
    f.text(460, 194, "nối được dữ liệu nhiều tháng.", "", 12, "start")
    return f


def d6_bon_phep():
    f = Fig("m6-4p", 720, 246, "Bốn phép kiểm tra tái nhận diện với số liệu chương 6")
    titles = ["1. Nhóm nhỏ", "2. Ngoại lai", "3. Áp đảo", "4. Phép trừ"]
    fixes = ["→ Gộp, không hiện riêng", "→ Không giao từng hộ", "→ Tách khách hàng lớn", "→ Mọi bảng cùng cách gộp"]
    for i in range(4):
        x = 4 + i * 179
        f.rect(x, 4, 170, 236, "box")
        f.text(x + 85, 26, titles[i], "", 13.5, bold=True)
        f.text(x + 85, 228, fixes[i], "f-ok", 11.5, bold=True)
    # 1. nhóm nhỏ
    x = 4
    for k, (p, n) in enumerate([("An Phú", 174), ("Tân Lập", 163), ("Bình Minh", 148), ("Đông Hòa", 130), ("Phú Thượng", 121), ("Cảng Mới", 1)]):
        y = 44 + k * 20
        bad = n < 10
        f.text(x + 8, y + 10, p, "f-bad" if bad else "", 11, "start")
        f.rect(x + 74, y + 1, max(2, round(n * 64 / 174)), 12, "r-bad" if bad else "r-brand", 2)
        f.text(x + 78 + max(2, round(n * 64 / 174)), y + 11, str(n), "f-bad" if bad else "f-mut", 10.5, "start")
    f.text(x + 85, 184, "1 khách hàng:", "f-bad", 11.5)
    f.text(x + 85, 200, "tổng chính là của xưởng", "f-bad", 11.5)
    # 2. ngoại lai
    x = 183
    for k, hgt in enumerate([10, 12, 9, 11, 13, 10, 9, 110]):
        f.rect(x + 12 + k * 19, 170 - hgt, 12, hgt, "r-bad" if hgt > 50 else "r-brand", 2)
    f.text(x + 12 + 7 * 19 + 6, 54, "3.370", "f-bad", 11, bold=True)
    f.line(x + 8, 170, x + 162, 170, "mut")
    f.text(x + 85, 188, "hộ sinh hoạt An Phú;", "f-mut", 11)
    f.text(x + 85, 203, "trung bình phường ≈ 300 kWh", "f-mut", 11)
    # 3. áp đảo
    x = 362
    f.text(x + 85, 70, "Đông Hòa + Cảng Mới", "", 11.5)
    f.rect(x + 10, 80, 70, 30, "r-bad", 3)
    f.rect(x + 80, 80, 80, 30, "r-brand", 3)
    f.text(x + 10, 130, "Xưởng: 46%", "f-bad", 11.5, "start", True)
    f.text(x + 10, 148, "130 hộ còn lại: 54%", "f-mut", 11.5, "start")
    f.text(x + 85, 184, "Qua ngưỡng 10 khách hàng", "", 11.5)
    f.text(x + 85, 200, "nhưng vẫn ước được xưởng", "f-bad", 11.5)
    # 4. phép trừ
    x = 541
    for y, t in [(48, "Bảng A – gộp:"), (64, "Đông Hòa + Cảng Mới"), (104, "Bảng B – riêng:"), (120, "Đông Hòa")]:
        f.text(x + 12, y, t, "f-mut" if t.startswith("Bảng") else "", 11.5, "start")
    f.text(x + 158, 82, "91.587 kWh", "mono", 12, "end")
    f.text(x + 158, 138, "− 49.228 kWh", "mono", 12, "end")
    f.line(x + 12, 148, x + 158, 148, "mut")
    f.text(x + 158, 166, "= 42.359 kWh", "mono f-bad", 12, "end", True)
    f.text(x + 85, 184, "đúng bằng sản lượng", "f-bad", 11.5)
    f.text(x + 85, 200, "của xưởng", "f-bad", 11.5)
    return f


def d6_7buoc():
    f = Fig("m6-7b", 720, 84, "Quy trình giảm dữ liệu 7 bước")
    steps = [("1. Mục đích,", "người nhận"), ("2. Phân loại", "cột"), ("3. Chọn", "kỹ thuật"), ("4. Thực hiện", ""),
             ("5. Kiểm tra", "nhận diện"), ("6. Chủ dữ liệu", "duyệt"), ("7. Ghi nhận,", "xóa bản tạm")]
    chevrons(f, [([a, b] if b else [a], "r-warn" if i in (4, 6) else "r-brand") for i, (a, b) in enumerate(steps)],
             2, 8, 104, 64, 102, tip=12, size=11.5)
    return f


def d6_view():
    f = Fig("m6-view", 720, 196, "Khung nhìn (view) chỉ cho đọc đúng phần đã tổng hợp")
    f.path("M95,62 V32 H630 V44", "bad", dash=True)
    f.text(362, 18, "Không được đọc thẳng bảng gốc", "f-bad", 12, bold=True)
    f.text(362, 37, "✕", "f-bad", 15, bold=True)
    f.box(10, 62, 170, 76, ["Anh Minh", "Power BI", ("tài khoản riêng, chỉ đọc", "f-mut")], "r-brand", 13, sub=1)
    f.box(270, 52, 190, 96, ["Khung nhìn (view)", "phường · tháng ·", "số KH · tổng kWh", ("chỉ nhóm ≥ 10 KH", "f-mut")], "r-ok", 13, sub=1)
    f.box(550, 44, 160, 112, ["Bảng gốc", ("ho_ten, dien_thoai", "mono"), ("dia_chi, so_tien_no", "mono"), ("… 8.500 dòng", "f-mut")], "box", 13, sub=1.5)
    f.arrow(180, 100, 270, 100, "ok", "chỉ đọc", ly=92)
    f.arrow(460, 100, 550, 100, label="CNTT dựng sẵn", ly=92, lsize=11.5)
    f.text(360, 184, "Quyền tối thiểu trên cơ sở dữ liệu: đúng cửa sổ, chỉ đọc, có người duyệt và có ngày rà soát.", "f-mut", 12.5)
    return f


def d6_sqli():
    f = Fig("m6-sqli", 720, 252, "Ghép chuỗi so với truy vấn có tham số")
    f.text(10, 18, "Ghép chuỗi – dữ liệu lẫn vào câu lệnh", "f-bad", 13, "start", True)
    f.box(10, 32, 160, 44, [("Hai Lúa's Shop", "mono")], "r-warn", 13, bold=False)
    f.text(90, 92, "khách gõ vào ô tìm kiếm", "f-mut", 11.5)
    f.arrow(170, 54, 220, 54)
    f.rect(220, 30, 490, 48, "r-bad")
    f.text(465, 59, [("…WHERE dia_chi LIKE '%Hai Lúa'", "mono"), ("s Shop%'", "mono f-bad b")], size=13)
    f.text(465, 96, "Dấu nháy trong tên đóng chuỗi sớm → phần tô đỏ rơi ra ngoài chuỗi, thành lệnh sai → báo lỗi", "f-bad", 12)
    f.line(10, 114, 710, 114, "mut", dash=True)
    f.text(10, 138, "Truy vấn có tham số – câu lệnh và dữ liệu gửi riêng", "f-ok", 13, "start", True)
    f.rect(10, 152, 280, 38, "box")
    f.text(150, 176, [("câu lệnh: ", "f-mut"), ("…LIKE ?", "mono")], size=13)
    f.rect(10, 204, 280, 38, "box")
    f.text(150, 228, [("dữ liệu: ", "f-mut"), ("%Hai Lúa's Shop%", "mono")], size=13)
    f.box(380, 172, 130, 52, ["Cơ sở dữ liệu"], "r-brand", 13)
    f.box(570, 172, 140, 52, ["Tìm đúng", ("KH101", "mono")], "r-ok", 13, sub=0)
    f.arrow(290, 171, 380, 188); f.arrow(290, 223, 380, 208); f.arrow(510, 198, 570, 198, "ok")
    return f


def d6_csv():
    f = Fig("m6-csv", 720, 212, "CSV injection: nội dung từ bên ngoài bị Excel hiểu thành công thức")
    f.text(10, 20, "Dữ liệu bị hiểu thành lệnh – lần này trong Excel", "", 13, "start", True)
    f.box(10, 36, 150, 60, ["Cổng góp ý", ("người ngoài gõ", "f-mut")], "box", 13, sub=1)
    f.box(200, 36, 150, 60, ["CNTT xuất", "ra file CSV"], "box", 13, sub=1)
    f.box(390, 36, 150, 60, ["Mở bằng Excel", ("(bấm đúp)", "f-mut")], "box", 13, sub=1)
    f.box(580, 30, 130, 72, ["Ô bắt đầu bằng", ("= + − @", "mono f-bad b"), "thành công thức"], "r-bad", 12.5, bold=False, sub=0)
    f.arrow(160, 66, 200, 66); f.arrow(350, 66, 390, 66); f.arrow(540, 66, 580, 66, "bad")
    f.text(10, 130, "Chặn ở đâu:", "f-ok", 12.5, "start", True)
    f.box(200, 140, 150, 64, ["Hệ thống", "thêm dấu ' trước", "ô ký tự đặc biệt"], "r-ok", 12.5, sub=0.5)
    f.box(390, 140, 150, 64, ["Người dùng", "Data → From Text/CSV;", "không bấm cho phép"], "r-ok", 12.5, sub=0.5)
    f.line(275, 140, 275, 96, "ok", dash=True); f.line(465, 140, 465, 96, "ok", dash=True)
    return f


# ====================== Buổi 5: nội dung ======================
M05 = {
    "Bài 1 –": lambda: [
        P("Bài này trả lời câu hỏi 1 của buổi: ở mỗi chặng file đi qua, cái gì bảo vệ nó. Muốn trả lời, cần biết dữ liệu đang ở trạng thái nào, và mỗi công cụ mật mã làm được gì, không làm được gì."),
        H("1.1. Ba trạng thái của dữ liệu"),
        T(["Trạng thái", "Ví dụ", "Rủi ro điển hình", "Biện pháp chính"],
          ["**Đang lưu**", "File trên laptop, USB, bản sao lưu", "Mất máy, mất USB, bản sao lưu bị lấy", "Mã hóa ổ đĩa/file, phân quyền"],
          ["**Đang truyền**", "File lên OneDrive, email gửi đối tác", "Nghe lén, trang giả, gửi nhầm", "HTTPS/TLS, VPN, kiểm tra người nhận"],
          ["**Đang dùng**", "Hồ sơ mở trên màn hình, bản in", "Người đứng sau nhìn, chụp màn hình", "Windows + L, kiểm soát in/chụp"]),
        P("Dữ liệu đang dùng luôn ở dạng rõ: mã hóa không giúp được lúc bạn đang đọc file. Vì vậy kẻ gian thường không phá mã mà đợi người dùng mở file, hoặc chiếm tài khoản để hệ thống mở hộ (buổi 4)."),
        FIG(d5_hanh_trinh(), "Hành trình file danh sách nợ của chị Dung (chương 5): dữ liệu đổi trạng thái nhiều lần, mỗi chặng cần một biện pháp riêng."),
        P("Câu cần nhớ: một lớp mã hóa không bảo vệ cả vòng đời dữ liệu. Khi file đã sang máy đối tác, thứ còn lại chỉ là hợp đồng và việc đã bỏ bớt cột từ trước – chị Dung bỏ cột số điện thoại nên ở chặng cuối không còn số điện thoại để lộ."),
        H("1.2. Mã hóa đối xứng và bất đối xứng"),
        P("Mã hóa biến **bản rõ** (KH001, 0900000001) thành **bản mã** vô nghĩa với người không có **khóa**. Thuật toán chuẩn như AES là công khai; bí mật chỉ nằm ở khóa. Khóa để cạnh dữ liệu thì mã hóa mất ý nghĩa."),
        FIG(d5_doi_xung(), "Đối xứng: một khóa để khóa và mở. Bất đối xứng: ai cũng khóa được bằng khóa công khai, chỉ khóa bí mật mở được."),
        T(["", "Đối xứng", "Bất đối xứng"],
          ["Hình ảnh", "Két sắt: một chìa để khóa và mở", "Hòm thư có khe: ai cũng bỏ thư vào, chỉ chủ hòm mở được"],
          ["Tốc độ", "Nhanh, dùng cho dữ liệu lớn", "Chậm; dùng để trao khóa và ký"],
          ["Bài toán khó", "Trao khóa cho người kia thế nào", "Chắc khóa công khai đúng là của người kia (→ chứng thư số, Bài 3)"],
          ["Ví dụ", "BitLocker, Excel có mật khẩu mở, 7-Zip AES-256", "HTTPS (lúc bắt tay), chữ ký số, passkey"]),
        P("File Excel của chị Dung dùng mã hóa đối xứng: mật khẩu chính là chìa két. Báo mật khẩu qua điện thoại theo số trong hợp đồng là trao chìa qua một đường khác với đường đi của két."),
        P("Không tự chế cách “mã hóa” như đảo số hay thay chữ bằng số: nhìn vài dòng là đoán ra quy luật. Dùng tính năng mã hóa có sẵn của công cụ được duyệt.", callout="note"),
        H("1.3. Băm: dấu vân tay của dữ liệu"),
        P("Hàm băm biến dữ liệu bất kỳ thành một chuỗi ngắn cố định (SHA-256 luôn cho 64 ký tự). Băm **không dùng khóa** và **không giải ngược được**. MD5, SHA-1 đã yếu, không dùng cho mục đích an ninh."),
        FIG(d5_bam(), "Hai dữ liệu chỉ khác một chữ số cho hai dấu vân tay không có gì giống nhau."),
        UL("**Kiểm tra file không bị sửa:** so giá trị băm với giá trị nhà cung cấp công bố. Trên Windows: Get-FileHash .\\TenFile.xlsx -Algorithm SHA256.",
           "**Lưu mật khẩu:** hệ thống chỉ lưu giá trị băm (kèm “muối”), nên CNTT chỉ đặt lại được, không xem lại được mật khẩu cũ (buổi 4).",
           "**Giữ bằng chứng:** băm bản sao log khi thu thập, ghi vào biên bản; sau này băm lại, trùng thì chứng minh chưa bị sửa (buổi 10)."),
        MISS("“Số điện thoại đã băm là ẩn danh.” → Một cột số điện thoại đã băm vẫn là dữ liệu cá nhân. Buổi 6 dạy cách làm đúng hơn: mã thay thế hoặc băm có khóa bí mật (HMAC)."),
        H("1.4. Chữ ký số"),
        FIG(d5_chu_ky(), "Chữ ký số dùng cặp khóa theo chiều ngược với mã hóa: ký bằng khóa bí mật, ai có khóa công khai cũng kiểm tra được."),
        UL("Ảnh chữ ký scan dán vào văn bản **không phải** chữ ký số: ai cũng sao chép được, và nó không chứng minh nội dung chưa bị sửa.",
           "Token và mã PIN giữ như con dấu. Đưa người khác “ký hộ” là mất cả ba điều chữ ký số chứng minh.",
           "Dùng cho văn bản điện tử, hóa đơn điện tử, hợp đồng điện tử (Luật Giao dịch điện tử 2023). Chứng thư chữ ký số do tổ chức chứng thực cấp, gắn khóa công khai với người ký."),
        H("1.5. Những thứ hay bị tưởng là mã hóa"),
        T(["Thứ hay bị nhầm", "Người không có mật khẩu làm được gì"],
          ["Base64, ví dụ S0gwMDEsIDA5MDAwMDAwMDE=", "Giải ra KH001, 0900000001 trong một giây"],
          ["Ẩn cột, ẩn sheet", "Chuột phải → Unhide là thấy"],
          ["Đổi đuôi file (.xlsx thành .dat)", "Đổi lại đuôi là mở"],
          ["ZIP không mật khẩu, hoặc ZIP mật khẩu kiểu cũ (ZipCrypto)", "Giải nén, hoặc phá bằng công cụ phổ biến – khi nén phải chọn AES-256"],
          ["Protect Sheet trong Excel", "Mở và đọc toàn bộ, chỉ bị chặn sửa (Bài 4)"]),
        H("1.6. Mật khẩu file phải mạnh hơn mật khẩu đăng nhập"),
        P("Đăng nhập có hệ thống chặn sau vài lần sai; file thì không: ai có file có thể cho máy đoán thử không giới hạn, không ai biết. MinhAn2026 (tên đơn vị + năm) nằm trong những thứ được thử đầu tiên. Dùng cụm từ dài, không liên quan đơn vị hay ngày tháng, theo quy định của đơn vị. Với thuật toán chuẩn và mật khẩu mạnh, phá mã trực tiếp là không khả thi – kẻ gian nhắm vào mật khẩu yếu, khóa để cạnh dữ liệu, hoặc lúc file đang mở."),
        H("1.7. Áp dụng"),
        UL("Với mỗi file nhạy cảm, tự hỏi: lúc này nó đang lưu, đang truyền hay đang dùng – cái gì đang bảo vệ nó?",
           "Rời ghế là bấm Windows + L – biện pháp rẻ nhất cho dữ liệu đang dùng.",
           "Hỏi CNTT laptop của mình đã bật mã hóa ổ đĩa (BitLocker / Device encryption) chưa.",
           "Không coi Base64, ẩn cột, đổi đuôi file là bảo vệ; không đưa token ký số cho người khác."),
        MISS("“File đã mã hóa thì gửi đi đâu cũng được.” → Người nhận mở xong là có bản rõ và chuyển tiếp được. Vẫn phải chọn đúng người nhận và đúng kênh (Bài 4)."),
    ],
    "Bài 2 –": lambda: [
        P("Bài này trả lời câu hỏi 2: vì sao chị Dung không ghi mật khẩu vào cùng email, và quên mật khẩu thì sao. Muốn trả lời, cần biết mỗi lớp bảo vệ khi lưu chặn được gì, và “khóa” – với người dùng thường là mật khẩu file – phải giữ thế nào."),
        H("2.1. Các lớp bảo vệ khi lưu trữ"),
        FIG(d5_lop(), "Các lớp lồng nhau: mỗi lớp chặn một kiểu rủi ro và để lọt một kiểu khác. Hiểu giới hạn của từng lớp quan trọng hơn nhớ tên công cụ."),
        T(["Lớp", "Chặn được", "Ghi chú"],
          ["Mã hóa ổ đĩa (BitLocker, FileVault)", "Laptop, ổ cứng bị mất khi máy đang tắt hoặc đã khóa", "Khóa khôi phục do CNTT giữ, không dán cạnh máy"],
          ["Mã hóa file (Office, 7-Zip AES-256, PDF)", "File bị gửi nhầm, bị sao chép ra ngoài", "Bảo vệ đi theo file; .zip vẫn lộ tên file bên trong"],
          ["Mã hóa cơ sở dữ liệu (TDE)", "Kẻ gian lấy được file dữ liệu hoặc bản sao lưu CSDL", "Việc của CNTT; không thay cho phân quyền"],
          ["Phân quyền trong ứng dụng", "Người không có quyền xem trong hệ thống", "Không kiểm soát file xuất, bản in, file tạm"]),
        P("Ví dụ – quên laptop trên taxi, trong máy có danh sách nợ đủ cột:"),
        T(["Tình trạng máy", "Người nhặt được làm được gì"],
          ["Không mã hóa ổ đĩa", "Tháo ổ cứng, đọc toàn bộ – không cần mật khẩu Windows"],
          ["Có BitLocker, máy tắt hoặc đã khóa", "Không đọc được; chỉ còn là mất tài sản (vẫn báo theo quy trình)"],
          ["Có BitLocker nhưng máy đang mở", "Đọc và sao chép như chủ máy"],
          ["Có BitLocker và file mã hóa riêng", "Máy đang mở, file vẫn hỏi mật khẩu"]),
        H("2.2. Mã hóa một file"),
        UL("**Excel/Word:** File → Info → Protect Workbook (Protect Document) → Encrypt with Password → lưu, đóng và mở lại để kiểm tra.",
           "**7-Zip:** chuột phải → 7-Zip → Add to archive… → nhập mật khẩu, chọn AES-256. Dùng .7z và đánh dấu “Encrypt file names” nếu cần giấu cả tên file.",
           "**PDF:** dùng mật khẩu mở tài liệu (open password), không phải mật khẩu quyền hạn."),
        P("Chọn số lớp theo nhãn (buổi 1) và nơi file sẽ đi. Bảng tổng hợp Nội bộ trong thư mục phòng: phân quyền + mã hóa ổ đĩa. Danh sách khách hàng (Mật) gửi ra ngoài: giảm cột + mã hóa file + kênh có kiểm soát + hợp đồng với bên nhận."),
        H("2.3. Sao lưu theo 3-2-1"),
        FIG(d5_321(), "Ba bản, hai loại phương tiện, một bản ở nơi khác – thêm một bản ngoại tuyến hoặc không sửa được để chống mã độc tống tiền."),
        UL("Sao lưu chỉ có giá trị khi **đã thử khôi phục** thành công.",
           "**Đồng bộ không phải sao lưu.** Lịch sử phiên bản và thùng rác của OneDrive cứu được trong thời hạn giữ lại, nhưng đó không phải kế hoạch sao lưu.",
           "**Không tự sao lưu** ra USB riêng hay Google Drive cá nhân “cho chắc”: đó là thêm một bản sao ngoài kiểm soát.",
           "Bản sao lưu giữ cả dữ liệu đã xóa ở hệ thống chính cho đến khi hết vòng giữ."),
        P("Ví dụ ở Minh An: thư mục phòng Kinh doanh sao lưu mỗi đêm sang NAS cùng phòng máy và chưa từng thử khôi phục – thiếu bản thứ ba, không có bản ở nơi khác, mã độc mã hóa được cả NAS. Người dùng không tự sửa được, nhưng nên hỏi CNTT: dữ liệu phòng mình sao lưu ở đâu, có bản ngoại tuyến không, lần thử khôi phục gần nhất là khi nào.", callout="example"),
        H("2.4. Quản lý khóa: mật khẩu file"),
        FIG(d5_hai_kenh(), "File và mật khẩu đi hai đường khác nhau. Người đọc trộm được một đường vẫn không mở được file."),
        UL("**Tách khỏi dữ liệu:** không ghi mật khẩu trong cùng email, trong tên file hay trong “matkhau.txt” cạnh file.",
           "**Mỗi đợt một mật khẩu mới**, sinh ngẫu nhiên. Một mật khẩu dùng cả năm cho năm đối tác thì đối tác này mở được file của đối tác kia, người nghỉ việc vẫn mở được file cũ.",
           "**Giới hạn người biết:** chỉ người nhận có tên trong danh sách.",
           "**Tính đến khôi phục:** file cần giữ lâu thì lưu mật khẩu theo quy trình của đơn vị (trình quản lý mật khẩu được duyệt hoặc kho khóa của CNTT)."),
        P("Mẹo đọc qua điện thoại: cụm 4–5 từ không dấu chọn ngẫu nhiên, ví dụ ghe-may-nuoc-tram-lua (chỉ là ví dụ, đừng dùng). Trình quản lý mật khẩu thường có sẵn chức năng sinh cụm từ như vậy.", callout="example"),
        P("**Trả lời câu hỏi 2.** Nếu mật khẩu nằm cùng email, ai đọc được email – người nhận nhầm, người được chuyển tiếp, kẻ đã chiếm hộp thư – đều mở được file. Quên mật khẩu của file gửi đối tác thì xuất lại và gửi lại với mật khẩu mới; quên mật khẩu của file lưu trữ lâu dài (như biên bản sự cố) là mất dữ liệu – vi phạm tính sẵn sàng."),
        H("2.5. Áp dụng"),
        UL("☐ Laptop làm việc đã bật mã hóa ổ đĩa; khóa khôi phục do CNTT giữ.",
           "☐ File Mật trên máy có lịch xóa; không tự sao lưu ra USB, cloud cá nhân.",
           "☐ Nén file có mật khẩu thì chọn AES-256.",
           "☐ Mỗi đợt gửi một mật khẩu mới, đi kênh khác với file."),
        MISS("“Có sao lưu rồi nên không sợ mã độc tống tiền.” → Bản sao lưu nối mạng có thể bị mã hóa cùng lúc. Nhiều nhóm tống tiền còn lấy cắp dữ liệu trước khi mã hóa – sao lưu không lấy lại được dữ liệu đã bị mang đi (buổi 10)."),
    ],
    "Bài 3 –": lambda: [
        P("Bài này giải thích ổ khóa trên thanh địa chỉ nói gì và không nói gì, để trả lời câu hỏi 3: trang OneDrive có HTTPS, vậy link “Anyone” của anh Cường có an toàn không."),
        H("3.1. HTTPS và chứng thư số"),
        P("HTTPS là cuộc nói chuyện giữa trình duyệt và website, đi trong một “ống” mã hóa bằng TLS (tên cũ là SSL). **Chứng thư số** là giấy tờ tùy thân của website: tên miền được cấp, tổ chức chứng thực (CA) đã cấp, thời hạn hiệu lực. Trình duyệt có sẵn danh sách CA đáng tin."),
        P("Lưu ý quan trọng: chứng thư chỉ xác nhận ai kiểm soát tên miền, không xác nhận người đó trung thực. Kẻ lừa đảo mua tên miền dienluc-minhan.example và xin được chứng thư hoàn toàn hợp lệ.", callout="note"),
        H("3.2. Bắt tay TLS"),
        FIG(d5_tls(), "Bắt tay TLS (đơn giản hóa): kiểm tra giấy tờ, thỏa thuận khóa phiên, rồi mọi dữ liệu đi bằng khóa phiên."),
        P("Bước 4–5 là điều Bài 1 đã nói: bất đối xứng để trao khóa, đối xứng để chở dữ liệu. Phiên bản nên dùng là TLS 1.2 và 1.3; SSL và TLS 1.0/1.1 đã lỗi thời."),
        P("Ví dụ đời thường: bảo vệ kiểm tra giấy tờ, hai bên thống nhất một mật hiệu, sau đó chỉ nói bằng mật hiệu – người đứng nghe không hiểu gì. Nhưng nếu ngay từ đầu bạn vào nhầm văn phòng giả có giấy tờ thật của chính nó, mật hiệu không cứu được bạn.", callout="example"),
        H("3.3. Xem chứng thư trên trình duyệt"),
        OL("Bấm biểu tượng bên trái thanh địa chỉ → Connection is secure → Certificate is valid (tên mục có thể khác theo phiên bản).",
           "Đọc ba dòng: cấp cho tên miền nào, ai cấp, hiệu lực đến ngày nào.",
           "So tên miền trong chứng thư với tên miền trên thanh địa chỉ."),
        H("3.4. Đọc tên miền cho đúng"),
        FIG(D5_URL, "Ổ khóa chỉ bảo đảm đúng tên miền đang hiển thị; đọc tên miền là việc của bạn."),
        T(["Địa chỉ (trang thật: cskh.dienlucminhan.example)", "Chủ thật", "Kết luận"],
          ["https://cskh.dienlucminhan.example/tra-cuu", "dienlucminhan.example", "Thật"],
          ["https://dienluc-minhan.example/tra-cuu", "dienluc-minhan.example (thêm dấu gạch)", "Giả"],
          ["https://dienlucrninhan.example", "dienlucrninhan.example (“rn” giả làm “m”)", "Giả"],
          ["https://cskh.dienlucminhan.example.xacminh-tk.example/login", "xacminh-tk.example", "Giả – tên thật chỉ là phần đầu"],
          ["https://evn-hotro.example", "evn-hotro.example", "Giả – mượn tên thương hiệu quen"]),
        P("Cả năm địa chỉ đều có thể có ổ khóa hợp lệ. Vào hệ thống quan trọng bằng bookmark hoặc gõ tay, không bấm từ tin nhắn hay email (buổi 8)."),
        H("3.5. Cảnh báo của trình duyệt"),
        T(["Cảnh báo", "Nên làm gì"],
          ["Lỗi chứng thư / “Kết nối của bạn không phải là kết nối riêng tư”", "Không bấm “Vẫn tiếp tục”; chụp màn hình, báo CNTT"],
          ["“Không an toàn” trên thanh địa chỉ (trang HTTP)", "Không nhập mật khẩu hay dữ liệu nhạy cảm"],
          ["Hệ thống nội bộ “vẫn hay bị” cảnh báo", "Báo CNTT sửa. Quen bấm qua cảnh báo của hệ thống nội bộ thì sẽ bấm qua cả cảnh báo thật"]),
        H("3.6. TLS bảo vệ gì, không bảo vệ gì"),
        FIG(d5_ong(), "TLS chỉ bảo vệ đường truyền. Những gì nằm ngoài “ống” cần biện pháp khác."),
        P("Email cũng vậy: TLS giữa các máy chủ email chỉ bảo vệ lúc truyền, email vẫn nằm dạng đọc được trong hộp thư hai bên – không phải mã hóa đầu–cuối. Trong nhiều tổ chức, kết nối TLS còn kết thúc ở cổng an ninh để kiểm tra theo chính sách – một lý do không dùng máy công ty cho việc riêng tư."),
        P("**Wi-Fi công cộng:** TLS giảm rủi ro nghe lén, nhưng Wi-Fi giả có thể dẫn tới trang giả. Làm việc với dữ liệu khách hàng từ xa thì dùng VPN của đơn vị hoặc Wi-Fi phát từ điện thoại mình; không nhập mật khẩu công việc vào trang đăng nhập Wi-Fi lạ; gặp cảnh báo chứng thư thì ngắt kết nối."),
        H("3.7. Trả lời câu hỏi 3"),
        P("Link “Anyone” của anh Cường mở bằng HTTPS hợp lệ: TLS mã hóa đường truyền cho **bất kỳ ai có link** – nhân viên công ty thu hộ, người được họ chuyển tiếp, hay người nhặt được chiếc điện thoại có tin nhắn đó. Ổ khóa làm đúng việc của nó; vấn đề nằm ở chỗ khác:"),
        T(["Vấn đề của link “Anyone”", "Thuộc về", "TLS có giúp không"],
          ["Ai có link đều mở được, không cần đăng nhập", "Kiểm soát truy cập (buổi 3)", "Không"],
          ["Link dán vào Zalo, nằm trên điện thoại ngoài quản lý", "Kênh chia sẻ (Bài 4)", "Không"],
          ["Không đặt hạn, đến nay vẫn mở được", "Vòng đời bản sao (buổi 1)", "Không"],
          ["File đủ cột, kể cả số điện thoại", "Tối thiểu hóa (buổi 1, 2)", "Không"],
          ["Nhật ký chỉ ghi “khách” đã mở, không biết là ai", "Giám sát (buổi 9)", "Không"]),
        P("“Có HTTPS” chỉ trả lời câu “trên đường đi có ai đọc trộm không”, không trả lời câu “ai được mở” – với link “Anyone”, câu trả lời là bất kỳ ai."),
        MISS("“Gửi qua email công ty là đã mã hóa rồi, không cần đặt mật khẩu file.” → Email chỉ được bảo vệ lúc truyền; nó nằm dạng đọc được trong hộp thư hai bên, không thu hồi được khi gửi nhầm và đi theo mọi lần chuyển tiếp."),
    ],
    "Bài 4 –": lambda: [
        P("Bài này ghép ba bài trước thành một quy trình dùng mỗi khi gửi file có dữ liệu khách hàng ra khỏi máy mình, và trả lời câu hỏi 4: hai cách gửi khác nhau ở đâu, nếu chỉ được sửa một điều ở cấp đơn vị thì sửa gì."),
        H("4.1. Quy trình chia sẻ 5 bước"),
        FIG(d5_5buoc(), "Bước 2 và bước 5 là hai bước hay bị bỏ qua nhất."),
        OL("**Duyệt nội dung:** đúng phiên bản, đúng kỳ; người nhận có căn cứ nhận (phiếu yêu cầu, hợp đồng) và cần để làm gì.",
           "**Giảm dữ liệu:** bỏ cột, sheet, dòng ngoài mục đích; tạo file mới thay vì ẩn.",
           "**Bảo vệ file:** mã hóa thật (mục 4.3), mật khẩu mới cho đợt này; đóng file, mở lại để kiểm tra.",
           "**Gửi đúng kênh:** kênh được duyệt (mục 4.2); gõ lại hoặc chọn địa chỉ từ danh bạ, không tin tính năng tự điền; mật khẩu đi kênh khác.",
           "**Kiểm tra và thu hồi:** xác nhận người nhận đã nhận; đóng link khi hết nhu cầu; xóa bản trung gian; ghi sổ theo dõi; đề nghị đối tác xác nhận xóa khi hết đợt."),
        P("Một file Excel có thể chứa nhiều thứ không nhìn thấy. Kiểm tra trước khi gửi:"),
        T(["Chỗ dữ liệu hay “trốn”", "Cách kiểm tra", "Cách xử lý"],
          ["Sheet, cột, dòng ẩn", "Chuột phải tên sheet → Unhide; chữ cái cột bị nhảy (A, B, E…)", "Xóa hẳn, hoặc chép phần cần sang file mới"],
          ["Bảng Pivot", "Bấm đúp vào một ô là hiện chi tiết từng dòng", "Sao chép kết quả → Paste Values sang file mới"],
          ["Công thức liên kết về file gốc", "Data → Edit Links (Workbook Links)", "Dán giá trị, ngắt liên kết"],
          ["Ghi chú, bình luận, tên tác giả", "File → Info → Check for Issues → Inspect Document", "Xóa bằng Inspect Document"],
          ["Bộ lọc đang lọc", "Dòng bị lọc vẫn nằm trong file", "Xóa dòng không cần, không chỉ lọc"]),
        P("Nếu được, cấp quyền xem cho người cụ thể trên file gốc thay vì gửi bản sao: cần thì thu hồi quyền, không có bản sao nào trôi nổi.", callout="apply"),
        H("4.2. Chọn kênh"),
        T(["Kênh", "Rủi ro chính", "Dùng cho"],
          ["Email đính kèm không mã hóa", "Gửi nhầm; nằm mãi trong hộp thư; không thu hồi được", "Nội bộ"],
          ["Email + file mã hóa, mật khẩu qua kênh khác", "Người nhận mở xong có thể chuyển tiếp bản đã giải mã", "Mật, gửi một lần"],
          ["Link OneDrive/SharePoint cho người cụ thể", "Cấu hình nhầm thành “Anyone”", "Mật, làm việc chung – thu hồi được, có hạn, có nhật ký"],
          ["Link “Anyone with the link”", "Ai có link đều mở được, kể cả khi bị chuyển tiếp", "Chỉ tài liệu Công khai"],
          ["Cổng trao đổi file/SFTP của đơn vị", "Cần hạ tầng", "Trao đổi định kỳ với đối tác"],
          ["Zalo/Messenger cá nhân", "Ngoài quản lý; tự lưu vào điện thoại; khó thu hồi", "Không dùng cho dữ liệu khách hàng"],
          ["USB", "Mất, lây mã độc", "Chỉ USB được cấp, có mã hóa"]),
        P("Chọn nhanh theo nhãn (buổi 1): **Công khai** – kênh nào cũng được. **Nội bộ** – kênh công vụ, trong đơn vị. **Mật** – link người cụ thể có hạn, hoặc file mã hóa + mật khẩu kênh khác, hoặc cổng trao đổi file. **Hạn chế cao** – như Mật, thêm phê duyệt, chặn tải về và danh sách người nhận có tên."),
        H("4.3. Các kiểu “mật khẩu” trong Office và PDF"),
        FIG(d5_mat_khau(), "Cách kiểm tra nhanh: đóng file, mở lại. Hỏi mật khẩu trước khi hiện nội dung mới là mã hóa thật."),
        P("Đây là điểm hay nhầm nhất: Protect Sheet, Protect Workbook (Structure), Mark as Final, Password to modify và mật khẩu quyền hạn của PDF đều **không** mã hóa nội dung. Ai có file vẫn đọc được, và các hạn chế này dễ bị gỡ bằng công cụ phổ biến."),
        H("4.4. Chia sẻ qua OneDrive/SharePoint cho đúng"),
        T(["Kiểu liên kết", "Ai mở được", "Dùng khi"],
          ["Anyone (Bất kỳ ai có liên kết)", "Ai có link, không cần đăng nhập", "Chỉ tài liệu Công khai"],
          ["People in [tên tổ chức]", "Mọi người có tài khoản trong tổ chức", "Tài liệu Nội bộ"],
          ["People with existing access", "Chỉ người đã có quyền", "Gửi lại link cho người đã có quyền"],
          ["Specific people (Người cụ thể)", "Chỉ các địa chỉ email được nhập", "Tài liệu Mật, gửi đối tác"]),
        P("Với Specific people: chọn Can view, đặt ngày hết hạn, bật Block download nếu người nhận chỉ cần xem; sau này vào Manage access để xem ai đang có quyền và thu hồi. Người nhận bên ngoài thường mở được bằng mã xác minh gửi tới email của họ, không cần tài khoản Microsoft – tùy cấu hình đơn vị. Nếu cấu hình không cho, hỏi CNTT cách chia sẻ ra ngoài được duyệt, đừng chuyển sang “Anyone”."),
        H("4.5. Trả lời câu hỏi 4: so sánh hai cách gửi"),
        T(["Bước", "Chị Dung", "Anh Cường (tháng trước)", "Hậu quả nếu link/file lọt ra ngoài"],
          ["1. Duyệt nội dung", "Đối chiếu phiếu yêu cầu, đúng đợt", "Xuất theo thói quen", "Có thể gửi thừa hộ ngoài danh sách thu hộ"],
          ["2. Giảm dữ liệu", "4 cột, file mới", "Đủ cột, có số điện thoại", "Lộ thêm số điện thoại và sản lượng của hàng trăm hộ"],
          ["3. Bảo vệ file", "Mã hóa, cụm từ dài", "Không", "Ai có file là đọc được"],
          ["4. Gửi đúng kênh", "Link cho đúng một người, hạn 7 ngày; mật khẩu qua điện thoại", "Link Anyone dán vào Zalo", "Ai có link là mở được, không biết ai đã mở"],
          ["5. Kiểm tra/thu hồi", "Gọi xác nhận, ghi sổ, theo dõi xóa", "Không; link vẫn mở đến nay", "Rủi ro kéo dài vô thời hạn"]),
        P("Hai cách khác nhau ở cả năm bước. Nhưng nhắc anh Cường “lần sau cẩn thận” là chưa đủ: lần sau một người khác vội vàng vẫn bấm được “Anyone”. Theo cách nhìn của buổi 2, cần sửa điều kiện cho phép sai: quản trị viên tắt kiểu link “Anyone” (hoặc tối thiểu bắt buộc hạn và chỉ xem), rồi rà soát, đóng các link đang mở – bắt đầu từ link của anh Cường. Việc này cần CNTT và lãnh đạo duyệt nên được ghi lên tờ “Việc hẹn sửa sau”."),
        H("4.6. Bốn tình huống hay gặp"),
        UL("**Gửi nhầm email** (tự điền ra một địa chỉ khác): báo ngay quản lý và đầu mối an toàn thông tin; thử thu hồi nếu hệ thống hỗ trợ; đề nghị người nhận nhầm xóa và xác nhận bằng văn bản; ghi nhận sự cố (buổi 10). File đã mã hóa và chưa báo mật khẩu thì mức độ nghiêm trọng giảm hẳn.",
           "**Đối tác xin gửi qua Zalo “cho tiện”:** từ chối lịch sự, gửi qua kênh trong hợp đồng; kênh khó dùng thì nhờ CNTT hỗ trợ đối tác, không đổi kênh.",
           "**Đồng nghiệp xin “file gốc để đối chiếu”:** hỏi đối chiếu gì, cần cột nào; gửi đúng phần đó.",
           "**Cơ quan bên ngoài yêu cầu nộp bằng USB:** xác minh văn bản và thẩm quyền qua bộ phận pháp chế; dùng USB được cấp, có mã hóa; ghi biên bản giao nhận."),
        H("4.7. Áp dụng"),
        UL("☐ Mỗi lần gửi file có dữ liệu khách hàng: đi đủ 5 bước, không bỏ bước 2 và 5.",
           "☐ Chia sẻ ra ngoài bằng Specific people, chỉ xem, có hạn.",
           "☐ Mở mục “Đã chia sẻ” (Shared) trong OneDrive của mình, đóng các link không còn cần.",
           "☐ Ghi sổ các lần gửi dữ liệu ra ngoài: ngày, nội dung, người nhận, kênh, hạn, ngày xác nhận xóa."),
        MISS("“Link dài và loạn thế kia ai mà đoán được.” → Link không cần bị đoán: nó bị chuyển tiếp, bị chụp màn hình, nằm trong tin nhắn của một chiếc điện thoại bị mất, hoặc bị dán nhầm vào nhóm chat đông người."),
    ],
}

# ====================== Buổi 6: nội dung ======================
M06 = {
    "Bài 1 –": lambda: [
        P("Bài này trả lời câu hỏi 1: anh Minh cần gì, không cần gì, và “bỏ tên rồi” đã là ẩn danh chưa. Cần ba việc: biết mỗi cột thuộc loại nào, biết các kỹ thuật giảm dữ liệu, và kiểm tra kết quả còn nhận ra người không."),
        H("1.1. Mỗi mục đích chỉ cần một phần"),
        T(["Mục đích dùng lại", "Cần", "Không cần"],
          ["Dự báo nhu cầu điện theo khu vực", "Phường, tháng, sản lượng, loại khách hàng", "Tên, điện thoại, địa chỉ chi tiết, số nợ"],
          ["Thử nghiệm phần mềm mới", "Dữ liệu đúng định dạng, đủ nhiều", "Dữ liệu thật của bất kỳ ai"],
          ["Đưa vào công cụ AI phân tích khiếu nại", "Nội dung, loại vấn đề, thời gian xử lý", "Tên, số điện thoại, địa chỉ lẫn trong nội dung"]),
        P("Nguyên tắc gốc là tối thiểu hóa (buổi 1): chỉ đưa ra phần đủ cho mục đích. Câu “cứ để đủ cột, AI tự lọc” của anh Minh đi ngược nguyên tắc này: lúc AI “tự lọc”, toàn bộ dữ liệu đã nằm trên công cụ AI rồi."),
        H("1.2. Bốn loại trường dữ liệu"),
        FIG(d6_loai_truong(), "Chín cột của file sản lượng quý III xếp vào bốn loại trường, kèm cách xử lý cho mục đích dự báo theo phường."),
        P("Thuộc tính nhạy cảm còn gồm: bị cắt điện, hộ nghèo được hỗ trợ tiền điện, chuỗi sản lượng theo giờ (lộ giờ đi về). Áp vào chương 6 – các cột của file sản lượng quý III:"),
        T(["Cột", "Loại", "Xử lý"],
          ["ma_kh", "Định danh gián tiếp (tra ngược được trên hóa đơn)", "Bỏ nếu chỉ dự báo theo phường; giả danh hóa nếu cần theo dõi từng hộ qua tháng"],
          ["ho_ten, dien_thoai", "Định danh trực tiếp", "Bỏ"],
          ["dia_chi", "Định danh gián tiếp", "Bỏ – đã có cột phuong"],
          ["phuong", "Định danh gián tiếp yếu", "Giữ, kiểm tra nhóm nhỏ"],
          ["loai_kh", "Dữ liệu phân tích", "Giữ nếu dự báo theo loại; cẩn thận vì tách nhóm nhỏ hơn"],
          ["thang, kwh", "Dữ liệu phân tích", "Tổng hợp theo phường – tháng"],
          ["so_tien_no", "Thuộc tính nhạy cảm", "Bỏ"]),
        H("1.3. Che, giả danh hóa, ẩn danh hóa và tổng hợp"),
        P("Ví dụ bài thi: **che** một phần tên bằng băng dính – người quen vẫn đoán ra; **giả danh hóa** – thay tên bằng số phách, hội đồng giữ bảng đối chiếu nên vẫn nối lại được; **ẩn danh hóa** – chỉ công bố “điểm trung bình cả tỉnh là 6,8”, không còn cách nào biết điểm từng em.", callout="example"),
        FIG(d6_pho(), "Từ dữ liệu gốc đến khử nhận dạng: chỉ hai mức cuối có thể không còn là dữ liệu cá nhân – và chỉ khi đã kiểm tra."),
        P("**Căn cứ pháp lý.** Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15, Điều 2: dữ liệu cá nhân sau khi **khử nhận dạng** thì không còn là dữ liệu cá nhân – với điều kiện không còn xác định được người. Che số điện thoại hay thay mã khách hàng chưa đạt điều kiện đó. Theo GDPR và hướng dẫn của EDPB, dữ liệu giả danh hóa cũng vẫn là dữ liệu cá nhân."),
        H("1.4. Kỹ thuật giảm dữ liệu"),
        T(["Kỹ thuật", "Trước → sau", "Lưu ý"],
          ["Loại bỏ", "Cột Họ tên → (không còn)", "An toàn nhất; mặc định cho cột không cần"],
          ["Che một phần", "0912345678 → 091****678", "Vẫn liên kết, đoán được"],
          ["Thay thế", "Nguyễn Văn A → Khách hàng 0001", "Hợp cho môi trường thử nghiệm"],
          ["Giả danh hóa", "PE0100123456 → P-7F3A9C", "Nối được nhiều bảng, nhiều tháng; vẫn là dữ liệu cá nhân"],
          ["Tổng quát hóa", "Số nhà → phường; 245 kWh → “201–300 kWh”", "Giữ xu hướng, giảm độ chính xác"],
          ["Tổng hợp", "174 hộ → “An Phú, tháng 9: 174 khách hàng, 64.263 kWh”", "Rất hợp cho báo cáo, dự báo; nhóm nhỏ vẫn lộ người"],
          ["Làm nhiễu, xáo trộn", "245 → 248; đổi giá trị giữa các dòng", "Chỉ hợp phân tích thống kê; cần chuyên môn"]),
        H("1.5. Masking tĩnh và masking động"),
        UL("**Tĩnh:** tạo một bản mới đã xử lý rồi giao bản đó – dùng khi gửi file, làm dữ liệu thử nghiệm, đưa vào AI. Đây là cách thực hành hôm nay.",
           "**Động:** dữ liệu gốc giữ nguyên, hệ thống che khi hiển thị theo quyền người xem (giao dịch viên thấy 091****678, trưởng phòng thấy đủ)."),
        P("Masking động không thay phân quyền hay mã hóa: nếu chức năng “Xuất danh sách” lấy từ dữ liệu gốc, file xuất vẫn đủ cột rõ dù màn hình đang che – điều cần hỏi CNTT."),
        H("1.6. Tái nhận diện: vì sao “đã bỏ tên” chưa đủ"),
        P("File đã bỏ tên và điện thoại, chỉ còn phường – loại nhà – sản lượng: nếu trong phường chỉ có một biệt thự dùng 3.000 kWh/tháng, ai biết khu đó nhận ra ngay. Bốn phép kiểm tra dùng trước khi giao bất kỳ bản nào:"),
        FIG(d6_bon_phep(), "Bốn phép kiểm tra với số liệu chương 6 (tháng 9/2026)."),
        T(["Phép kiểm tra", "Câu hỏi", "Xử lý"],
          ["Nhóm nhỏ", "Còn nhóm nào có quá ít người?", "Gộp với nhóm lân cận hoặc không hiển thị riêng"],
          ["Ngoại lai", "Có dòng nào khác hẳn phần còn lại?", "Không giao dữ liệu từng hộ; trong bản tổng hợp hộ này “chìm” trong 174 hộ"],
          ["Áp đảo", "Một khách hàng có chiếm phần lớn tổng của nhóm?", "Tách khách hàng lớn ra xử lý riêng (Thực hành 7)"],
          ["Phép trừ", "Hai bảng giao đi trừ nhau có ra một người?", "Mọi bảng giao cho cùng người nhận dùng cùng một cách gộp"]),
        P("Ngưỡng nhóm gần với khái niệm k-anonymity: mỗi tổ hợp đặc điểm phải có ít nhất k người giống nhau. Giá trị k và ngưỡng áp đảo do đơn vị quy định; con số 10 trong giáo trình chỉ là ví dụ. Xưởng Cảng Mới dù là hộ kinh doanh hay doanh nghiệp thì sản lượng cũng không nên lộ qua một dòng tổng hợp."),
        H("1.7. Áp dụng"),
        UL("Trước mỗi yêu cầu dữ liệu, hỏi lại: để làm gì, cần cột nào, chi tiết từng hộ hay theo nhóm?",
           "Mặc định là tổng hợp; chỉ giao dữ liệu từng dòng khi mục đích thật sự cần và có phê duyệt.",
           "Không gọi “ẩn danh” cho file mới bỏ tên hay che số; ghi đúng “đã che”, “đã giả danh hóa” và vẫn bảo vệ như dữ liệu cá nhân.",
           "Chạy bốn phép kiểm tra ở mục 1.6 trước khi giao bản tổng hợp."),
        MISS("“AI tự lọc được, cứ đưa hết vào.” → Lúc AI lọc, dữ liệu đã nằm trên công cụ đó – một bản sao mới, ở nơi mới, theo điều khoản của nhà cung cấp (buổi 1, 2). Giảm dữ liệu phải làm trước khi dữ liệu rời khỏi tay mình."),
    ],
    "Bài 2 –": lambda: [
        P("Bài này đưa các kỹ thuật của Bài 1 vào một quy trình, rồi chỉ cách làm bằng Excel, SQL hoặc Python. Không cần biết lập trình: Excel làm được mọi việc của bài. Các bài ngắn SQL và Python cuối buổi dành cho ai muốn luyện thêm."),
        H("2.1. Quy trình 7 bước"),
        FIG(d6_7buoc(), "Bảy bước từ yêu cầu đến bản giao. Bước 2–6 ứng với năm bước của slide 61; bước 5 và 7 hay bị bỏ qua."),
        T(["Bước", "Câu hỏi kiểm tra"],
          ["1. Mục đích, người nhận", "Dùng ở đâu (nội bộ, đối tác, công cụ AI)? Công cụ AI đó đã được đơn vị cho phép chưa?"],
          ["2. Phân loại cột", "Có cột văn bản tự do (ghi chú, nội dung khiếu nại) không?"],
          ["3. Chọn kỹ thuật", "Mặc định là loại bỏ. Mỗi cột giữ lại có lý do viết ra được không?"],
          ["4. Thực hiện", "Làm trên môi trường được phép? File gốc có bị sửa nhầm? File trung gian nằm đâu?"],
          ["5. Kiểm tra", "Cột, sheet ẩn, ghi chú? Bốn phép kiểm tra ở mục 1.6 đạt chưa?"],
          ["6. Phê duyệt", "Chủ dữ liệu đã xem file thật, không chỉ xem mô tả?"],
          ["7. Ghi nhận, xóa bản tạm", "Đã ghi giao gì, cho ai, bao giờ xóa? Đã xóa bản đủ cột trung gian? Khóa, bảng đối chiếu lưu riêng?"]),
        P("Bước 7 đặc biệt quan trọng ở Điện lực X: chức năng xuất luôn ra đủ cột, nên mỗi lần làm bản giao là có thêm một file đủ cột trên máy người làm (buổi 1: đếm bản sao)."),
        P("Cùng một cột, mục đích khác thì xử lý khác:"),
        T(["Trường", "Dự báo nội bộ", "Gửi đơn vị tư vấn", "Môi trường thử nghiệm", "Đưa vào công cụ AI"],
          ["Họ tên", "Loại bỏ", "Loại bỏ", "Thay bằng tên giả", "Loại bỏ"],
          ["Số điện thoại", "Loại bỏ", "Loại bỏ", "Thay bằng số giả", "Loại bỏ"],
          ["Mã khách hàng", "Giả danh hóa nếu cần nối bảng", "Giả danh hóa", "Thay bằng mã giả", "Loại bỏ"],
          ["Địa chỉ", "Phường/xã", "Quận/huyện", "Địa chỉ giả", "Loại bỏ hoặc quận/huyện"],
          ["Sản lượng tháng", "Giữ", "Chia khoảng hoặc tổng hợp", "Giữ phân bố, xáo trộn", "Tổng hợp"],
          ["Tình trạng nợ", "Chỉ khi đúng mục đích", "Loại bỏ", "Giá trị giả", "Loại bỏ"]),
        H("2.2. SQL – lấy đúng phần cần"),
        T(["Từ khóa", "Ý nghĩa", "Vai trò trong giảm dữ liệu"],
          ["SELECT", "Chọn cột nào", "Chỉ liệt kê cột cần – cột không ghi là không ra"],
          ["WHERE", "Lọc dòng nào", "Chỉ lấy đơn vị, thời gian cần"],
          ["GROUP BY", "Gộp theo nhóm", "Tổng hợp thay vì chi tiết từng hộ"],
          ["HAVING", "Lọc nhóm sau khi gộp", "Loại nhóm quá ít người"]),
        CODE("SELECT phuong, thang, COUNT(*) AS so_kh, SUM(kwh) AS tong_kwh\nFROM   san_luong\nWHERE  nam = 2026\nGROUP  BY phuong, thang\nHAVING COUNT(*) >= 10;"),
        P("Đọc bằng lời: “Lấy số khách hàng và tổng kWh theo phường, tháng năm 2026; chỉ giữ nhóm từ 10 khách hàng trở lên.” Kết quả không có tên, điện thoại, mã khách hàng."),
        P("HAVING bỏ nhóm nhỏ nhưng cũng làm mất sản lượng của nhóm đó – mất cả phường Cảng Mới là sai số lớn cho dự báo. Cách thường dùng là gộp nhóm nhỏ vào phường lân cận; Thực hành 7 sẽ cho thấy gộp vẫn chưa đủ khi một khách hàng chiếm gần nửa tổng."),
        P("Mẫu yêu cầu gửi bộ phận dữ liệu, thay vì xin “file đủ cột”: “Đề nghị xuất số khách hàng và tổng kWh theo phường và tháng, quý III/2026, Điện lực X; không kèm cột định danh; nhóm dưới [ngưỡng đơn vị] khách hàng gộp với phường lân cận; mục đích: dự báo nhu cầu, người nhận: phòng Kế hoạch.”", callout="example"),
        H("2.3. Python – che và giả danh hóa việc lặp lại hằng tháng"),
        P("Python hợp với file lớn hoặc việc lặp lại mỗi tháng. Hai thao tác cốt lõi chỉ cần hai dòng:"),
        CODE('sdt_che = sdt[:3] + "****" + sdt[-3:]          # 0900000001 → 090****001\n'
             'ma_moi  = hmac.new(KHOA, ma_kh.encode(), hashlib.sha256).hexdigest()[:8]   # KH001 → 4ee2e067'),
        FIG(d6_gia_danh(), "Giả danh hóa bằng HMAC: cùng khóa cho cùng mã thay thế nên nối được dữ liệu nhiều tháng; ai giữ khóa nối ngược lại được."),
        P("Vì sao cần khóa bí mật? Mã khách hàng, số điện thoại có số giá trị hữu hạn: băm thường thì kẻ gian băm thử mọi giá trị rồi so lại (buổi 5). Khóa phải được bảo vệ như dữ liệu Hạn chế cao, đọc từ kho khóa hoặc biến môi trường, không ghi trong file code. Muốn luyện tay: Python 02 (che số điện thoại) và SQL 01–07 ở cuối buổi."),
        H("2.4. Excel – cách làm cho người không lập trình"),
        T(["Việc cần làm", "Cách làm trong Excel"],
          ["Loại bỏ cột", "Xóa cột (không chỉ ẩn); hoặc chép riêng các cột cần sang file mới bằng Paste Values"],
          ["Che số điện thoại", "=LEFT(C2;3)&\"****\"&RIGHT(C2;3) (dấu ; hoặc , tùy máy); định dạng cột gốc là Text để giữ số 0 đầu. Sau đó Paste Values và xóa cột gốc"],
          ["Thay mã khách hàng", "Tạo cột mã thay thế (P0001, P0002…); bảng đối chiếu mã thật – mã thay thế lưu ở file riêng có mã hóa; xóa cột mã thật khỏi file giao"],
          ["Tổng quát hóa sản lượng", "=FLOOR(F2;100)&\"–\"&FLOOR(F2;100)+99 cho ra “200–299”"],
          ["Tổng hợp", "Insert → PivotTable: hàng = phường, cột = tháng, giá trị = Count của mã KH và Sum của kWh. Chép kết quả → Paste Values sang file mới (PivotTable giữ dữ liệu gốc bên trong)"],
          ["Kiểm tra nhóm nhỏ", "Conditional Formatting tô màu ô đếm dưới ngưỡng"],
          ["Kiểm tra cuối", "Unhide sheet, cột; File → Info → Check for Issues → Inspect Document"]),
        H("2.5. Lỗi thường gặp"),
        T(["Lỗi", "Vì sao nguy hiểm"],
          ["Ẩn cột thay vì xóa", "Người nhận chỉ cần Unhide"],
          ["Gửi nguyên PivotTable", "Bấm đúp vào ô tổng là hiện lại toàn bộ dòng chi tiết"],
          ["Chỉ che tên, giữ mã khách hàng thật", "Mã khách hàng tra ngược được trên hệ thống hoặc hóa đơn"],
          ["Quên dữ liệu trong văn bản tự do", "Cột “Ghi chú” có ghi “chị Lan, số nhà 12, SĐT 09…”"],
          ["Gửi bảng đối chiếu (hoặc khóa) cùng file", "Giả danh hóa mất tác dụng"],
          ["Dùng HAVING bỏ nhóm nhỏ nhưng giao thêm bảng tổng toàn đơn vị", "Lấy tổng trừ các nhóm còn lại là ra nhóm bị ẩn"],
          ["Gọi là “đã ẩn danh” khi mới bỏ tên", "Người nhận hạ mức bảo vệ vì tưởng không còn là dữ liệu cá nhân"]),
        H("2.6. Áp dụng"),
        UL("Khi nhận yêu cầu dữ liệu, trả lời bằng một phiếu: mục đích, người nhận, cột giữ, cột bỏ, mức tổng hợp, ngưỡng nhóm, người duyệt, ngày xóa.",
           "Xóa bản đủ cột trung gian ngay sau khi tạo xong bản giao.",
           "Khóa giả danh hóa và bảng đối chiếu lưu riêng, ít người có quyền, không bao giờ đi cùng file.",
           "Bản tổng hợp làm từ Excel: luôn Paste Values sang file mới, không gửi PivotTable."),
    ],
    "Bài 3 –": lambda: [
        P("Người dùng nghiệp vụ ngày càng kết nối thẳng vào dữ liệu: Excel (Power Query), Power BI, công cụ truy vấn. Bài này trả lời câu hỏi 3: có nên cho anh Minh kết nối thẳng vào cơ sở dữ liệu không, và với điều kiện gì."),
        H("3.1. Người dùng “chạm” vào cơ sở dữ liệu ở đâu"),
        T(["Điểm chạm", "Ai kiểm soát điều bạn thấy"],
          ["Màn hình ứng dụng (tra cứu, nhập phiếu)", "Ứng dụng: phân quyền, masking động"],
          ["Chức năng xuất ra Excel/CSV", "Ứng dụng – nhưng xuất xong thì không ai kiểm soát nữa"],
          ["Kết nối trực tiếp (Power Query, Power BI, công cụ SQL)", "Quyền của tài khoản kết nối trên cơ sở dữ liệu"],
          ["File nhận từ người khác (CSV từ cổng góp ý…)", "Không ai – người mở tự chịu"]),
        P("Càng xuống dưới bảng, kiểm soát của hệ thống càng mỏng và trách nhiệm của người dùng càng lớn."),
        H("3.2. Tình huống hay gặp"),
        T(["Tình huống", "Rủi ro", "Cách làm đúng"],
          ["Kết nối bằng tài khoản có quyền ghi/xóa để làm báo cáo", "Truy vấn sai có thể sửa, xóa dữ liệu thật", "Tài khoản chỉ đọc, chỉ trên khung nhìn cần thiết"],
          ["Cả phòng dùng chung một tài khoản kết nối", "Không biết ai đã lấy gì (như truc_ca ở buổi 4)", "Mỗi người một tài khoản"],
          ["Lưu mật khẩu kết nối trong file rồi gửi đi", "Người nhận có luôn quyền vào cơ sở dữ liệu", "Không lưu mật khẩu trong file chia sẻ"],
          ["Gửi file Excel/Power BI có kết nối dữ liệu", "File đã làm mới chứa sẵn bản sao dữ liệu, kể cả bảng không hiển thị", "Coi đó là một bản xuất; chia sẻ báo cáo qua dịch vụ có phân quyền (buổi 7)"],
          ["Truy vấn hệ thống vận hành giờ cao điểm", "Làm chậm hệ thống (sẵn sàng)", "Dùng bản sao báo cáo hoặc kho dữ liệu"],
          ["Kết nối từ máy cá nhân, ngoài mạng đơn vị", "Dữ liệu rơi vào thiết bị không quản lý", "Chỉ từ máy công ty, qua VPN nếu ở xa"]),
        H("3.3. Khung nhìn (view) và quyền tối thiểu"),
        FIG(d6_view(), "Khung nhìn là “cửa sổ” CNTT dựng sẵn: anh Minh chỉ thấy đúng cột và nhóm đã chọn, không chạm được bảng gốc."),
        P("Kết hợp khung nhìn với quyền chỉ đọc là cách áp dụng “quyền tối thiểu” của buổi 3 vào cơ sở dữ liệu. Việc dựng khung nhìn và cấp quyền do CNTT làm; người dùng cần hiểu để đề nghị đúng: “cho tôi đọc khung nhìn tổng hợp theo phường – tháng”, thay vì “cho tôi vào bảng khách hàng”."),
        H("3.4. Trả lời câu hỏi 3: có cho anh Minh kết nối thẳng không?"),
        P("Có thể – nếu đủ các điều kiện dưới đây. Không đủ thì tiếp tục giao bản tổng hợp hằng tháng."),
        T(["Điều kiện", "Vì sao", "Nối với"],
          ["Tài khoản cá nhân của anh Minh, không dùng chung", "Biết ai lấy gì", "Buổi 4"],
          ["Chỉ đọc, chỉ trên khung nhìn tổng hợp, không trên bảng gốc", "Tối thiểu hóa, quyền tối thiểu", "Buổi 1, 3"],
          ["Kết nối vào bản sao báo cáo hoặc kho dữ liệu, không vào hệ thống vận hành", "Không ảnh hưởng sẵn sàng", "Mục 3.2"],
          ["Chủ dữ liệu duyệt; ghi vào Access Matrix; có ngày rà soát", "Quyền có người chịu trách nhiệm và có hạn", "Buổi 3"],
          ["Không lưu mật khẩu trong file; file kết nối được coi là một bản xuất", "File chứa dữ liệu đã làm mới", "Buổi 5"],
          ["Công cụ AI nhận dữ liệu đã được đơn vị cho phép", "Dữ liệu không đi tiếp ra ngoài phạm vi", "Buổi 1, 2"],
          ["Có nhật ký truy cập", "Phát hiện truy vấn bất thường", "Buổi 9"]),
        H("3.5. Khi xuất dữ liệu và khi mua phần mềm"),
        P("Nếu chức năng xuất chỉ có một kiểu “đủ cột” như ở Điện lực X, mỗi lần xuất là một bản sao đủ cột – và ai có quyền xuất (kể cả kẻ gian chiếm được tài khoản) đều lấy được đủ cột. Khi mua hoặc thuê phần mềm, bộ phận nghiệp vụ có thể đề nghị đưa vào yêu cầu:"),
        UL("Xuất theo mẫu cột được duyệt; quyền xuất tách khỏi quyền xem; giới hạn số dòng mỗi lần xuất; ghi nhật ký mọi lần xuất.",
           "Masking động cho các trường định danh trực tiếp theo vai trò.",
           "Nhà cung cấp lập trình an toàn, có kết quả kiểm thử bảo mật trước nghiệm thu, vá lỗi trong thời hạn thỏa thuận."),
        MISS("“Chỉ đọc thì vô hại.” → Chỉ đọc chặn được sửa và xóa, không chặn được đọc và mang đi. Quyền đọc toàn bảng khách hàng vẫn là quyền lấy được 8.500 dòng."),
    ],
    "Bài 4 –": lambda: [
        P("Bài này trả lời câu hỏi 4: lỗi lạ khi gõ dấu nháy đơn nói lên điều gì, và chị Dung nên làm gì. Lớp học chỉ giải thích nguyên lý và cách phòng ngừa: không có chuỗi tấn công mẫu, học viên không quét hay thử trên bất kỳ hệ thống nào."),
        H("4.1. Ví dụ đời thường: phiếu có chỗ trống"),
        P("Phiếu in sẵn: “Thủ kho hãy xuất hồ sơ của khách hàng: ______”. Nếu ai đó ghi vào chỗ trống một câu dạng mệnh lệnh (“KH001, và xuất luôn toàn bộ hồ sơ còn lại”) mà thủ kho làm theo nguyên văn, dữ liệu đã thành mệnh lệnh – đó là bản chất của **SQL injection**. Thủ kho cẩn thận chỉ coi nội dung chỗ trống là một mã cần tìm, dù nó viết gì – đó là **truy vấn có tham số**."),
        H("4.2. Nguyên nhân: ghép chuỗi"),
        FIG(d6_sqli(), "Cùng một tên cửa hàng hợp lệ: ghép chuỗi thì câu lệnh vỡ, dùng tham số thì tìm đúng."),
        P("**Giải thích lỗi ở chương 6.** Trong SQL, dấu nháy đơn ' mở và đóng một chuỗi chữ. Ghép “Hai Lúa's Shop” vào câu lệnh thì dấu nháy trong tên đóng chuỗi sớm, câu lệnh sai cú pháp và cơ sở dữ liệu báo lỗi. Màn hình hiện nguyên lỗi kèm đoạn SQL là hai dấu hiệu cùng lúc: ứng dụng đang ghép chuỗi, và đang để lộ lỗi chi tiết ra ngoài."),
        P("Truy vấn có tham số không chỉ chặn kẻ gian mà còn sửa lỗi cho khách hàng bình thường có dấu nháy trong tên, địa chỉ. Tham số không dùng được cho tên bảng, tên cột – khi đó dùng danh sách cho phép (allow-list)."),
        H("4.3. Hậu quả và phòng thủ nhiều lớp"),
        P("Khai thác được SQL injection có thể đọc trộm toàn bộ bảng, kể cả bảng không liên quan (bí mật); sửa hoặc xóa dữ liệu (toàn vẹn, sẵn sàng); vượt qua màn hình đăng nhập; trong một số cấu hình còn chạy lệnh trên máy chủ. Nhóm lỗi Injection luôn nằm trong nhóm rủi ro hàng đầu của OWASP Top 10."),
        T(["Lớp phòng thủ (OWASP)", "Ai làm"],
          ["1. Truy vấn có tham số – biện pháp chính", "Lập trình viên"],
          ["2. Danh sách cho phép cho tên bảng, tên cột, chiều sắp xếp", "Lập trình viên"],
          ["3. Quyền tối thiểu cho tài khoản ứng dụng – quyết định thiệt hại lớn đến đâu", "Quản trị CSDL, quản trị hệ thống"],
          ["4. Không hiển thị lỗi chi tiết ra màn hình", "Lập trình viên"],
          ["5. Tường lửa ứng dụng web (WAF), giám sát – lớp bổ sung, không thay lớp 1", "An ninh mạng"],
          ["6. Rà soát mã, kiểm thử bảo mật có phép trước khi đưa vào dùng", "ATTT, nhà cung cấp"]),
        P("Lỗi ở chương 6 cho thấy lớp 1 và lớp 4 đều có vấn đề."),
        H("4.4. CSV injection: họ hàng trong Excel"),
        P("Cùng nguyên lý “dữ liệu bị hiểu thành lệnh” còn có chèn lệnh hệ điều hành, chèn công thức vào CSV và chèn lệnh vào AI (prompt injection, buổi 1). CSV injection là loại người dùng nghiệp vụ gặp trực tiếp nhất:"),
        FIG(d6_csv(), "Nội dung người ngoài gõ vào cổng góp ý có thể thành công thức khi mở CSV bằng Excel."),
        P("Công thức do người ngoài soạn có thể tạo liên kết tới trang lừa đảo, hoặc cố gửi nội dung các ô khác ra ngoài khi người mở bấm cho phép. Vì vậy với file từ nguồn bên ngoài: không bấm cho phép các cảnh báo bảo mật của Excel (bật nội dung, kết nối dữ liệu ngoài, cập nhật liên kết); thấy ô có công thức lạ thì báo CNTT."),
        H("4.5. Trả lời câu hỏi 4 và vai trò của người dùng"),
        P("Lỗi khi gõ “Hai Lúa's Shop” là dấu hiệu màn hình tra cứu đang ghép chuỗi và hiển thị lỗi chi tiết – một lỗ hổng tiềm ẩn. Chị Dung nên:"),
        UL("Ghi lại thời gian, màn hình nào, đã gõ gì; chụp thông báo lỗi.",
           "Báo ngay bộ phận kỹ thuật và đầu mối an toàn thông tin của Công ty (chị Lan).",
           "Tiếp tục công việc bình thường; cần tra địa chỉ đó thì tra theo mã khách hàng."),
        P("Không nên: tự gõ thêm ký tự để “xem nó còn lỗi gì”, rủ đồng nghiệp thử, hay đăng ảnh lỗi lên nhóm chat. Tự ý thử tấn công một hệ thống, kể cả của đơn vị mình, có thể vi phạm quy định nội bộ và pháp luật; ảnh lỗi có cấu trúc bảng là thông tin hữu ích cho kẻ gian.", callout="note"),
        P("Ngoài ra, người dùng còn là người quyết định tài khoản kết nối của mình có bao nhiêu quyền (chỉ đọc, đúng phạm vi), người đối chiếu trường và số dòng trước khi chuyển tiếp bản xuất, và người đưa yêu cầu lập trình an toàn vào hợp đồng khi mua phần mềm (mục 3.5)."),
        MISS("“Đó là việc của lập trình viên, người dùng không liên quan.” → Người dùng thường là người đầu tiên thấy dấu hiệu (lỗi lạ, dữ liệu không liên quan hiện ra) – báo sớm là cách góp phần chặn lỗi trước khi bị khai thác."),
    ],
}

LESSONS = {5: M05, 6: M06}

# Câu trong ghi chú giảng viên/lịch buổi học trỏ tới mục đã đổi số hoặc đoạn mã đã bỏ.
TEXT_FIXES = {
    5: [("Bài 1 (1.2–1.10) và Bài 2", "Bài 1 (1.2–1.7) và Bài 2"),
        ("Giảng viên có thể chạy đoạn Python ở mục 1.8 hoặc chuẩn bị sẵn kết quả để đối chiếu.",
         "Dùng các sơ đồ ở mục 1.2–1.4 để so sánh mã hóa, băm và chữ ký số.")],
    6: [("Giảng viên chạy demo", "Giảng viên chiếu sơ đồ"),
        ("Tạo bản tổng hợp theo phường × tháng (SQL do giảng viên chạy, hoặc PivotTable).",
         "Tạo bản tổng hợp theo phường × tháng bằng PivotTable (mục 2.4)."),
        ("Tạo bản che từng dòng (Python do giảng viên chạy, hoặc công thức Excel).",
         "Tạo bản che từng dòng bằng công thức Excel (mục 2.4)."),
        ("(3) bảng so sánh đầu vào – đầu ra; (4)", "(3) bảng so sánh đầu vào – đầu ra và bảng chọn phương án xử lý; (4)")],
}

TH6_FILE = "/static/labs/BaoCao_Thang.xlsx"
TH7_FILE = "/static/labs/DLX_SanLuong_Q3.csv"


# ====================== Thực hành 6, 7: hướng dẫn từng bước ======================
def d_th6():
    f = Fig("th6-flow", 720, 200, "Tám bước của Phần A Thực hành 6")
    chevrons(f, [(["1", "Khảo sát", "sheet ẩn, cột ẩn"], "r-warn"),
                 (["2", "File mới", "chỉ TongHop, dán giá trị"], "r-brand"),
                 (["3", "Dọn file", "Inspect Document"], "r-brand"),
                 (["4", "Mã hóa", "đặt mật khẩu mở file"], "r-brand")], 2, 8, 176, 84, 179, size=12.5)
    chevrons(f, [(["5", "Thử mở lại", "mật khẩu sai → từ chối"], "r-ok"),
                 (["6", "So sánh", "với Protect Sheet"], "r-note"),
                 (["7", "Gửi đi", "mật khẩu kênh khác"], "r-brand"),
                 (["8", "Thu hồi", "xóa file trung gian"], "r-warn")], 2, 106, 176, 84, 179, size=12.5)
    return f


def d_th7():
    f = Fig("th7-flow", 720, 232, "Từ file đủ cột ra hai bản: bản che từng dòng và bản tổng hợp")
    f.box(10, 82, 150, 68, ["DLX_SanLuong_Q3.csv", ("2.211 dòng × 9 cột", "f-mut")], "box", 12.5)
    f.box(222, 14, 214, 72, ["Bước 3: bản che", ("bỏ tên, địa chỉ, số nợ;", "f-mut"), ("che SĐT; mã thay thế HMAC", "f-mut")], "r-warn", 12.5)
    f.box(222, 146, 214, 72, ["Bước 4–8: tổng hợp", ("phường × tháng;", "f-mut"), ("bốn phép kiểm tra", "f-mut")], "r-brand", 12.5)
    f.box(492, 14, 218, 72, ["DLX_BanChe.csv", ("vẫn là dữ liệu cá nhân", "f-bad"), ("không giao", "f-bad")], "r-bad", 12.5)
    f.box(492, 146, 218, 72, ["DLX_TongHop_PA2.csv", ("chỉ số đếm và tổng", "f-ok"), ("giao sau khi được duyệt", "f-ok")], "r-ok", 12.5)
    f.arrow(160, 108, 220, 54)
    f.arrow(160, 124, 220, 180)
    f.arrow(436, 50, 490, 50, "bad")
    f.arrow(436, 182, 490, 182, "ok")
    return f


def EXPECT(s):
    return P("**Kết quả mong đợi:** " + s, callout="apply")


def TH6_A():
    return [
        FIG(d_th6(), "Phần A gồm tám bước. Mỗi bước có phần kết quả mong đợi để bạn tự kiểm tra trước khi sang bước sau."),
        P("Chuẩn bị: tạo thư mục **TH6** ở ổ dữ liệu (không để trên Desktop) và lưu file BaoCao_Thang.xlsx vào đó. Mọi file bạn tạo trong bài đều lưu trong thư mục này."),
        H4("Bước 1 – Khảo sát file (5 phút)"),
        OL("Mở BaoCao_Thang.xlsx. Nếu Excel hiện thanh vàng **Protected View**, bấm **Enable Editing**.",
           "Nhìn các thẻ sheet ở cạnh dưới cửa sổ, ghi lại tên từng sheet.",
           "Chuột phải vào một thẻ sheet bất kỳ → **Unhide…**. Mục này bấm được nghĩa là còn sheet đang ẩn: chọn tên sheet trong hộp thoại → **OK**. Mục này mờ nghĩa là không còn sheet ẩn.",
           "Mở từng sheet, nhìn hàng chữ cái tiêu đề cột. Chữ cái nhảy cóc (ví dụ H rồi J) là có cột ẩn ở giữa: bôi đen hai cột hai bên (H đến J) → chuột phải → **Unhide**.",
           "Ghi vào bài: file có bao nhiêu sheet, sheet nào ẩn, cột nào ẩn, trong đó chứa gì, thông tin nào nhạy cảm."),
        EXPECT("bạn liệt kê được mọi sheet và mọi cột, kể cả phần đang ẩn. Bỏ sót cũng không sao: Inspect Document ở bước 3 sẽ báo lại, nhưng khi chữa bài giảng viên sẽ hỏi vì sao bạn không thấy."),
        H4("Bước 2 – Tạo file mới chỉ có bảng tổng hợp (5 phút)"),
        OL("Mở sheet **TongHop** → bấm ô A1 → **Ctrl+A** để chọn cả bảng → **Ctrl+C**.",
           "**Ctrl+N** để mở một workbook trống.",
           "Bấm ô A1 → **Home → Paste ▾ → Values** (biểu tượng 123). Cách nhanh: **Ctrl+Alt+V** → chọn **Values** → **OK**.",
           "Bấm vào một ô số, nhìn thanh công thức: phải là con số, không bắt đầu bằng dấu =. Có dấu = là còn công thức trỏ về file gốc → dán lại bằng Values.",
           "**File → Save As** → chọn thư mục TH6 → đặt tên **BaoCao_T10_TongHop.xlsx** → **Save**."),
        EXPECT("file mới chỉ có 1 sheet, 5 dòng (1 dòng tiêu đề và 4 vùng), không có tên hay số điện thoại khách hàng nào."),
        P("Không sửa thẳng trên file gốc rồi xóa bớt sheet: dễ sót sheet ẩn, tên vùng (Name), liên kết. Tạo file mới rồi chỉ dán thứ cần gửi là cách chắc nhất.", callout="note"),
        H4("Bước 3 – Dọn thông tin ẩn bằng Inspect Document (5 phút)"),
        OL("Trong file BaoCao_T10_TongHop.xlsx: **File → Info → Check for Issues → Inspect Document**. Nếu Excel hỏi có lưu không, chọn **Yes**.",
           "Để nguyên các mục đã được đánh dấu → bấm **Inspect**.",
           "Mục **Document Properties and Personal Information** (tên tác giả, người sửa cuối) → **Remove All**.",
           "Nếu thấy **Hidden Worksheets**, **Hidden Rows and Columns** hoặc **Links to Other Files** là bạn đã chép thừa: đóng file, làm lại bước 2.",
           "Bấm **Close** → **Ctrl+S**. Chụp màn hình kết quả Inspect để nộp."),
        EXPECT("sau khi bấm Remove All, các mục đều có dấu tích, không còn sheet ẩn hay liên kết."),
        P("Thao tác Remove All không hoàn tác được. Vì vậy chỉ chạy Inspect Document trên file mới, không chạy trên file gốc.", callout="note"),
        H4("Bước 4 – Mã hóa file (10 phút)"),
        P("**Cách 1 – Bằng Excel (mọi học viên đều làm):**"),
        OL("Vẫn ở file BaoCao_T10_TongHop.xlsx: **File → Info → Protect Workbook → Encrypt with Password**.",
           "Gõ mật khẩu → **OK** → gõ lại đúng mật khẩu đó → **OK**. Dòng Protect Workbook chuyển màu vàng, ghi “A password is required to open this workbook”.",
           "Bấm **Ctrl+S**. Chưa lưu thì mã hóa chưa có hiệu lực.",
           "Đóng file."),
        P("**Chọn mật khẩu:** cụm 4–5 từ ngẫu nhiên, từ 16 ký tự trở lên, không chứa tên đơn vị, tên người, ngày tháng. **Quên mật khẩu là mất file**: Microsoft cũng không mở lại được. Lưu mật khẩu trong trình quản lý mật khẩu đơn vị cho phép, không ghi trong email, trong tên file hay trên giấy dán màn hình.", callout="note"),
        P("**Cách 2 – Bằng Python (tùy chọn, khi phải mã hóa nhiều file mỗi tháng).** Kết quả giống hệt Cách 1: Excel hỏi mật khẩu khi mở file."),
        OL("Mở Command Prompt (**Windows + R** → gõ cmd → Enter). Cài thư viện, chỉ cần làm một lần: **pip install msoffcrypto-tool**. Nếu báo không nhận lệnh pip, dùng **py -m pip install msoffcrypto-tool**.",
           "Mở Notepad, chép đoạn mã dưới đây, **File → Save As** → chọn thư mục TH6, Save as type: **All files**, tên **ma_hoa.py**, Encoding: **UTF-8**.",
           "Trong Command Prompt, chuyển vào thư mục TH6: **cd /d** rồi dán đường dẫn thư mục (lấy bằng cách bấm vào thanh địa chỉ của File Explorer).",
           "Chạy **python ma_hoa.py**. Gõ mật khẩu hai lần (màn hình không hiện ký tự – đó là bình thường) → Enter."),
        CODE('''# ma_hoa.py – mã hóa file Excel bằng mật khẩu, giống Encrypt with Password
from getpass import getpass
from msoffcrypto.format.ooxml import OOXMLFile

vao = "BaoCao_T10_TongHop.xlsx"          # file chưa mã hóa (phải là .xlsx)
ra = "BaoCao_T10_TongHop_MaHoa.xlsx"     # file sẽ gửi đi, đặt tên khác file vào

mat_khau = getpass("Mật khẩu: ")         # gõ không hiện chữ; không ghi mật khẩu trong code
if mat_khau != getpass("Gõ lại mật khẩu: "):
    raise SystemExit("Hai lần gõ không khớp, chạy lại.")

with open(vao, "rb") as f_vao, open(ra, "wb") as f_ra:
    OOXMLFile(f_vao).encrypt(mat_khau, f_ra)
print("Đã tạo", ra)'''),
        EXPECT("dòng “Đã tạo BaoCao_T10_TongHop_MaHoa.xlsx”; mở file đó bằng Excel thì hiện hộp thoại hỏi mật khẩu. Sau khi kiểm tra xong ở bước 5, xóa bản chưa mã hóa."),
        H4("Bước 5 – Thử mở lại bằng mật khẩu sai (5 phút)"),
        OL("Mở file đã mã hóa → Excel hỏi mật khẩu.",
           "Cố ý gõ sai (ví dụ thiếu một chữ) → **OK**.",
           "Chụp màn hình thông báo từ chối (**Windows + Shift + S**) để nộp.",
           "Mở lại, gõ đúng mật khẩu → thấy bảng 4 vùng."),
        EXPECT("thông báo “The password you supplied is not correct…” và không thấy dữ liệu nào. Nếu file mở ra mà không hỏi mật khẩu là bạn chưa bấm Ctrl+S ở bước 4."),
        H4("Bước 6 – So sánh với Protect Sheet (5 phút)"),
        OL("Mở file gốc BaoCao_Thang.xlsx → **File → Save As** → đặt tên **BanSao_ProtectSheet.xlsx**.",
           "Mở sheet ChiTiet → **Review → Protect Sheet** → gõ mật khẩu → **OK** → gõ lại → **OK** → **Ctrl+S** → đóng file.",
           "Mở lại BanSao_ProtectSheet.xlsx. Excel có hỏi mật khẩu không? Bạn có đọc được tên, số nợ không? Thử gõ vào một ô.",
           "Ghi vào bài: Protect Sheet chặn được gì, không chặn được gì; khác Encrypt with Password ở đâu. Xong thì xóa bản sao này."),
        H4("Bước 7 – Chọn kênh gửi và cách báo mật khẩu (5 phút)"),
        UL("**Người nhận:** họ tên, chức vụ, địa chỉ email công vụ – chọn từ danh bạ, không gõ tay.",
           "**Kênh gửi file:** kênh nào, gửi file nào (chỉ file đã mã hóa, không kèm file gốc).",
           "**Kênh báo mật khẩu:** phải khác kênh gửi file; báo vào lúc nào (ví dụ sau khi người nhận xác nhận đã nhận file)."),
        H4("Bước 8 – Kế hoạch thu hồi, lưu giữ (5 phút)"),
        UL("Khi nào xóa các file trung gian trên máy bạn (bản chưa mã hóa, bản sao Protect Sheet), và nhớ dọn cả Recycle Bin.",
           "Ai xác nhận đã nhận file, xác nhận bằng cách nào, trong bao lâu.",
           "File gốc lưu ở đâu, ai được truy cập."),
    ]


def TH6_B():
    return [
        OL("Mở BaoCao_Thang.xlsx → sheet **ChiTiet** → bấm một ô trong bảng → **Data → Filter**.",
           "Bấm mũi tên ở tiêu đề **SoTienNo** → **Number Filters → Greater Than…** → gõ **0** → **OK**. Thanh trạng thái góc dưới bên trái ghi số dòng tìm được.",
           "**Ctrl+A** → **Ctrl+C** → **Ctrl+N** → bấm ô A1 → dán bằng **Values**. Excel chỉ chép các dòng đang hiện sau khi lọc.",
           "Trong file mới, xóa hẳn các cột không cần: bấm chữ cái tiêu đề cột DienThoai, giữ **Ctrl** và bấm thêm các cột Vung, kWh_T10, SoNgayQuaHan, GhiChuNoiBo → chuột phải → **Delete**. Cột đang ẩn ở file gốc có thể bị chép theo: kiểm tra hàng chữ cái cột có nhảy cóc không.",
           "Kiểm tra: chỉ còn đúng 4 cột **MaKH, TenKH, DiaChi, SoTienNo**. Bấm vào chữ cái cột A, nhìn **Count** ở thanh trạng thái: 107 (1 dòng tiêu đề và 106 hộ).",
           "Lưu thành **DSNo_T10_CongTyThuHo.xlsx**, chạy Inspect Document (bước 3), mã hóa (bước 4), thử mật khẩu sai (bước 5).",
           "Viết cách chia sẻ: OneDrive → chuột phải file → **Share** → mục quyền chọn **Specific people** → nhập đúng một địa chỉ bên công ty thu hộ → chọn **Can view** (hoặc cho tải nếu hợp đồng yêu cầu) → đặt **expiration date** 7 ngày → **Send**. Mật khẩu báo qua điện thoại theo số ghi trong hợp đồng.",
           "Trả lời: vì sao bỏ cột DienThoai, kWh_T10, SoNgayQuaHan, GhiChuNoiBo? Nếu công ty thu hộ nói “cần số điện thoại để gọi nhắc”, bạn xử lý thế nào?"),
        EXPECT("thanh trạng thái ở bước 2 ghi “106 of 400 records found”; file gửi có đúng 4 cột, 106 hộ, hỏi mật khẩu khi mở."),
    ]


def TH7_STEPS():
    return [
        FIG(d_th7(), "Cùng một file đủ cột, bạn tạo hai bản rồi kiểm tra cả hai: bản che từng dòng vẫn là dữ liệu cá nhân, bản tổng hợp qua kiểm tra mới được đề xuất giao."),
        H4("Bước 0 – Chuẩn bị máy (5 phút)"),
        OL("Mở Command Prompt (**Windows + R** → gõ cmd → Enter), gõ **python --version**. Cần Python 3.10 trở lên. Chưa có Python: máy cơ quan thì nhờ CNTT cài; máy riêng thì tải từ python.org, khi cài nhớ đánh dấu **Add python.exe to PATH**.",
           "Cài thư viện pandas, chỉ cần làm một lần: **pip install pandas** (báo không nhận lệnh pip thì dùng **py -m pip install pandas**).",
           "Tạo thư mục **TH7**, lưu file DLX_SanLuong_Q3.csv vào đó.",
           "Mở Notepad, **File → Save As** → thư mục TH7, Save as type: **All files**, tên **th7.py**, Encoding: **UTF-8**.",
           "Trong Command Prompt: **cd /d** rồi dán đường dẫn thư mục TH7."),
        P("Cách làm ở mỗi bước dưới đây: chép đoạn mã **nối vào cuối** th7.py → Ctrl+S → chạy **python th7.py** trong Command Prompt → so với phần kết quả mong đợi rồi mới sang bước sau. Dòng bắt đầu bằng # là chú thích, không cần chép."),
        P("Máy không cài được Python: làm bước 4–9 bằng PivotTable như mục 2.4 và ghi rõ trong bài là bạn dùng Excel.", callout="note"),
        H4("Bước 1 – Đọc file, xem các cột"),
        CODE('''import pandas as pd

df = pd.read_csv("DLX_SanLuong_Q3.csv", encoding="utf-8-sig",
                 dtype={"dien_thoai": str})   # đọc số điện thoại dạng chữ để giữ số 0 đầu
print(df.shape)                               # (số dòng, số cột)
print(df.columns.tolist())'''),
        EXPECT("(2211, 9) và danh sách 9 cột ma_kh, ho_ten, dien_thoai, dia_chi, phuong, loai_kh, thang, kwh, so_tien_no. Báo lỗi FileNotFoundError là Command Prompt chưa đứng ở thư mục TH7."),
        H4("Bước 2 – Phân loại cột (không cần mã)"),
        P("Xếp 9 cột vào 4 loại ở mục 1.2: định danh trực tiếp, định danh gián tiếp, thuộc tính nhạy cảm, dữ liệu phân tích. Mỗi cột ghi anh Minh có cần cho dự báo theo phường không. Bảng này là phần (1) của bài nộp."),
        H4("Bước 3 – Tạo bản che từng dòng (masking và giả danh hóa)"),
        P("Bản che giữ từng dòng nhưng bỏ hẳn cột không cần, che số điện thoại và thay mã khách hàng bằng mã thay thế. Bạn tạo bản này để **kiểm tra** nó an toàn đến đâu ở bước 8, không phải để giao."),
        CODE('''import hashlib, hmac, os
from getpass import getpass

# Khóa bí mật không ghi trong code. Ở lớp: gõ một cụm từ dài khi được hỏi, nhớ để lần sau gõ lại đúng.
khoa = (os.environ.get("KHOA_GIA_DANH") or getpass("Khóa giả danh: ")).encode()

def ma_thay_the(ma_kh):
    """Cùng khóa và cùng mã khách hàng → luôn ra cùng một mã thay thế 8 ký tự."""
    return hmac.new(khoa, ma_kh.encode(), hashlib.sha256).hexdigest()[:8]

def che_sdt(sdt):
    """0900000001 → 090****001; ô trống hoặc số quá ngắn → để trống."""
    if pd.isna(sdt) or len(sdt) < 7:
        return ""
    return sdt[:3] + "****" + sdt[-3:]

che = df.drop(columns=["ho_ten", "dia_chi", "so_tien_no"])   # bỏ hẳn cột, không chỉ ẩn
che["ma_kh"] = che["ma_kh"].map(ma_thay_the)
che["dien_thoai"] = che["dien_thoai"].map(che_sdt)
che.to_csv("DLX_BanChe.csv", index=False, encoding="utf-8-sig")
print(che.head(3))'''),
        EXPECT("3 dòng đầu có dien_thoai dạng 090****001, ma_kh là 8 ký tự gồm chữ a–f và số; cả 3 dòng (3 tháng của cùng một khách hàng) có cùng mã thay thế. Mã của bạn khác mã của bạn bên cạnh vì mỗi người dùng một khóa. File DLX_BanChe.csv mở bằng Excel có 6 cột."),
        P("Thử chạy lại và gõ một khóa khác: mã thay thế đổi hết. Vì vậy khóa phải giữ cố định và bí mật – ai có khóa và danh sách mã khách hàng là nối ngược lại được (mục 2.3).", callout="question"),
        H4("Bước 4 – Tổng hợp theo phường × tháng"),
        CODE('''def tong_hop(bang):
    """Mỗi phường – tháng: số khách hàng, tổng kWh, kWh của khách lớn nhất và tỷ trọng của khách đó (%)."""
    th = (bang.groupby(["phuong", "thang"])
              .agg(so_kh=("ma_kh", "nunique"), tong_kwh=("kwh", "sum"), kwh_max=("kwh", "max"))
              .reset_index())
    th["ty_trong_max"] = (th["kwh_max"] / th["tong_kwh"] * 100).round(1)
    return th

A = tong_hop(df)
print(A[A["thang"] == "2026-09"].sort_values("so_kh"))'''),
        EXPECT("6 dòng của tháng 2026-09, xếp từ phường ít khách hàng nhất. Để tự kiểm tra: dòng An Phú có tong_kwh = 64263. Ra số khác thì xem lại bước 1."),
        H4("Bước 5 – Kiểm tra nhóm nhỏ và áp đảo, thử gộp nhóm"),
        CODE('''NGUONG = 10                                   # ngưỡng nhóm tối thiểu dùng trong lớp
print(A[A["so_kh"] < NGUONG])                 # phép 1: nhóm nhỏ
print(A.sort_values("ty_trong_max", ascending=False).head(5))   # phép 3: một khách chiếm bao nhiêu % tổng nhóm'''),
        P("Ghi lại: phường nào dưới ngưỡng, ở những tháng nào; phường nào có một khách hàng chiếm tỷ trọng cao bất thường. Sau đó thử cách hay dùng – gộp phường nhỏ vào phường lân cận **Đông Hòa**. Sửa chữ Tên phường nhỏ thành tên phường bạn vừa tìm được, rồi chạy lại:"),
        CODE('''GOP = {"Tên phường nhỏ": "Đông Hòa"}           # sửa tên phường cho đúng kết quả ở trên
gop = df.copy()
gop["phuong"] = gop["phuong"].replace(GOP)
D = tong_hop(gop)
print(D[D["thang"] == "2026-09"].sort_values("ty_trong_max", ascending=False))'''),
        P("Gộp xong, nhóm mới đã qua ngưỡng chưa? Trong nhóm mới, khách hàng lớn nhất chiếm bao nhiêu phần trăm tổng? Người biết mức tiêu thụ bình thường của Đông Hòa có ước được số của khách đó không?", callout="question"),
        H4("Bước 6 – Kiểm tra ngoại lai"),
        CODE('''sh = df[(df["thang"] == "2026-09") & (df["loai_kh"] == "Sinh hoạt")]
print(sh.groupby("phuong")["kwh"].agg(["mean", "max"]).round(0))   # trung bình và lớn nhất của hộ sinh hoạt'''),
        P("Phường nào có hộ sinh hoạt dùng điện vượt xa trung bình? Trong bản tổng hợp, hộ đó có lộ ra không? Còn trong bản che từng dòng thì sao?", callout="question"),
        H4("Bước 7 – Phương án 2: chỉ tổng hợp nhóm Sinh hoạt và Kinh doanh"),
        CODE('''pa2 = df[df["loai_kh"].isin(["Sinh hoạt", "Kinh doanh"])]
F = tong_hop(pa2)
print("Nhóm nhỏ nhất:", F["so_kh"].min(), "khách hàng")
print("Tỷ trọng lớn nhất:", F["ty_trong_max"].max(), "%")'''),
        P("So với ngưỡng 10 và với kết quả bước 5: phương án này đạt chưa? Khách hàng loại khác bị tách ra không có trong bản này – ghi vào đề xuất để anh Minh dự báo riêng phần đó, đừng để dự báo bị thiếu mà không ai biết."),
        H4("Bước 8 – Kiểm tra bản che bằng bốn phép"),
        CODE('''print(che.groupby(["phuong", "loai_kh"])["ma_kh"].nunique().sort_values().head(3))  # nhóm nhỏ trong bản che
print(che.sort_values("kwh", ascending=False).head(3))                               # dòng nổi bật
mot_ma = che["ma_kh"].iloc[0]
print(che[che["ma_kh"] == mot_ma][["ma_kh", "thang", "kwh"]])                        # theo dõi một hộ qua 3 tháng'''),
        P("Bản che có qua được phép nhóm nhỏ, ngoại lai không? Mã thay thế cố định có cho phép theo dõi từng hộ qua các tháng không? Phép trừ: nếu anh Minh có cả bản tổng hợp thô (bước 4) và bản phương án 2 (bước 7), lấy bản này trừ bản kia thì ra số của ai?", callout="question"),
        H4("Bước 9 – So sánh và chọn phương án xử lý"),
        P("Đến đây bạn có bốn cách làm bản tổng hợp: A (thô), D (gộp Cảng Mới vào Đông Hòa), F (phương án 2) và một cách nữa hay gặp – B: bỏ hẳn các nhóm dưới ngưỡng, giống HAVING trong SQL. Đặt cả bốn cạnh nhau theo cùng ba con số rồi mới chọn:"),
        CODE('''B = A[A["so_kh"] >= NGUONG]                   # phương án B: bỏ nhóm dưới ngưỡng
tong = df["kwh"].sum()                         # tổng sản lượng quý III của file đủ cột
for ten, bang in [("A thô", A), ("B bỏ nhóm nhỏ", B), ("D gộp", D), ("F phương án 2", F)]:
    print(ten.ljust(15),
          "nhóm nhỏ nhất:", bang["so_kh"].min(),
          "| tỷ trọng lớn nhất:", bang["ty_trong_max"].max(), "%",
          "| giữ:", round(bang["tong_kwh"].sum() / tong * 100, 1), "% sản lượng")'''),
        EXPECT("4 dòng. A: 1 – 100,0% – 100,0%. B: 121 – 5,2% – 86,6%. D: 121 – 49,5% – 100,0% (49,5% là tháng 2026-08; riêng tháng 2026-09 là 46,3%). F: 121 – 5,2% – 86,6%."),
        T(["Con số", "Đạt khi", "Không đạt thì"],
          ["Nhóm nhỏ nhất", "Từ ngưỡng 10 khách hàng trở lên", "Dòng tổng hợp chính là số của một vài người"],
          ["Tỷ trọng lớn nhất", "Không ai chiếm phần lớn tổng nhóm – ngang mức các phường khác (vài %)", "Ai biết mức bình thường của phường sẽ ước được số của khách lớn"],
          ["Giữ % sản lượng", "100%, hoặc phần bị tách ra được ghi trong đề xuất và có cách dự báo riêng", "Dự báo thiếu mà không ai biết"]),
        P("B và F ra cùng con số. Vậy khác nhau ở đâu? Phần sản lượng bị bỏ (100% − 86,6%) là của ai, anh Minh có biết không? Tháng sau một phường có thêm khách hàng sản xuất thì cách nào vẫn cho kết quả đúng?", callout="question"),
        P("Ghi số liệu và lựa chọn vào bảng **Chọn phương án xử lý dữ liệu** của bài nộp: mỗi phương án một dòng, chọn hay không và vì sao. Làm bằng Excel: mỗi phương án là một PivotTable (lọc loai_kh, hoặc sửa phuong Cảng Mới thành Đông Hòa trên bản sao); lấy Count of ma_kh nhỏ nhất, Max of kwh chia Sum of kwh lớn nhất, Sum of kwh so với tổng của file."),
        H4("Bước 10 – Lưu bản đề xuất giao và đọc lại để kiểm tra"),
        CODE('''giao = F[["phuong", "thang", "so_kh", "tong_kwh"]]   # bỏ kwh_max, ty_trong_max: đó là số của đúng một khách hàng
giao.to_csv("DLX_TongHop_PA2.csv", index=False, encoding="utf-8-sig")

kt = pd.read_csv("DLX_TongHop_PA2.csv", encoding="utf-8-sig")
print(kt.shape, kt.columns.tolist())
cam = {"ma_kh", "ho_ten", "dien_thoai", "dia_chi", "so_tien_no", "loai_kh"}
print("Cột không được có:", cam & set(kt.columns) or "không có – đạt")'''),
        EXPECT("(15, 4) với 4 cột phuong, thang, so_kh, tong_kwh và dòng “Cột không được có: không có – đạt”. Mở DLX_TongHop_PA2.csv bằng Excel để xem lại lần cuối."),
        H4("Bước 11 – Hoàn thiện bài"),
        OL("Lập bảng so sánh đầu vào – đầu ra: mỗi cột trong 9 cột bị bỏ, giữ hay biến đổi, vì sao.",
           "Ghi kết quả bốn phép kiểm tra cho bản tổng hợp và bản che.",
           "Điền bảng chọn phương án xử lý (bước 9) và ghi phần sản lượng bị tách ra được báo cho anh Minh thế nào.",
           "Quyết định bản nào được đưa vào môi trường AI thử nghiệm, bản nào không; cần ai duyệt; cần xác nhận gì về công cụ AI.",
           "Viết đoạn đề xuất gửi anh Tuấn.",
           "Sau khi chữa bài: xóa DLX_SanLuong_Q3.csv và DLX_BanChe.csv khỏi máy (Shift+Delete hoặc dọn Recycle Bin). Giữ th7.py: tháng sau chỉ cần đổi tên file và chạy lại."),
    ]


def TH7_PHUONG_AN():
    """Đáp án bảng chọn phương án xử lý (bước 9), hiện khi công bố."""
    r = {"reveal": "m06-th7"}
    return [
        P("Chọn phương án xử lý (bước 9, số của cả quý III):", **r),
        T(["Phương án", "Nhóm nhỏ nhất", "Tỷ trọng lớn nhất", "Giữ sản lượng", "Chọn?", "Vì sao"],
          ["A – Tổng hợp thô", "1 KH", "100%", "100%", "Không", "Dòng Cảng Mới là sản lượng của đúng một xưởng"],
          ["B – Bỏ nhóm dưới 10", "121 KH", "5,2%", "86,6%", "Không", "Số đạt nhưng mất xưởng Cảng Mới (13,4% sản lượng) mà không ai biết; tháng sau có thêm nhóm nhỏ là mất tiếp"],
          ["D – Gộp Cảng Mới vào Đông Hòa", "121 KH", "49,5%", "100%", "Không", "Qua ngưỡng nhóm nhưng xưởng chiếm gần nửa tổng – vẫn ước được số của xưởng"],
          ["F – Phương án 2", "121 KH", "5,2%", "86,6%", "Chọn", "Đạt cả hai phép; phần tách ra là khách hàng sản xuất, ghi trong đề xuất để dự báo riêng theo hợp đồng"],
          **r),
        P("Phần không có trong bản giao: khách hàng sản xuất Cảng Mới, 128.185 kWh quý III. Ghi trong đề xuất và báo anh Minh: phần này không nằm trong bản tổng hợp, dự báo riêng theo hợp đồng cung cấp điện.", **r),
    ]


def _fix_text(value, fixes):
    if isinstance(value, list):
        return [_fix_text(v, fixes) for v in value]
    if isinstance(value, dict):
        new = {k: _fix_text(v, fixes) for k, v in value.items()}
        # html có thẻ <strong> nên có thể không khớp chuỗi cần thay: dựng lại từ plain
        if "plain" in new and new["plain"] != value["plain"] and new.get("html") == value.get("html"):
            new["html"] = esc(new["plain"])
        return new
    if isinstance(value, str):
        for a, b in fixes:
            value = value.replace(a, b)
    return value


def H4(s):
    return {"t": "h4", "text": s}


def _is_link(b, href):
    return b.get("html", "").startswith(f'<a href="{href}"')


def _replace(blocks, start, stop, new):
    """Thay các block nằm sau tiêu đề h3 `start` cho tới block đầu tiên thỏa `stop` (giữ cả hai)."""
    i = next(k for k, b in enumerate(blocks) if b["t"] == "h3" and b["text"] == start)
    j = next(k for k in range(i + 1, len(blocks)) if stop(blocks[k]))
    return blocks[:i + 1] + new + blocks[j:]


def _th6(blocks):
    """Bỏ script tạo file; học viên tải file luyện tập, giảng viên giữ số liệu đối chiếu; nhiệm vụ viết thành từng bước."""
    out = []
    for b in blocks:
        p = b.get("plain", "")
        if _is_link(b, TH6_FILE) or b.get("teacher") and (
                b["t"] == "code" or p.startswith(("Có thể tạo file", "Kết quả khi chạy", "Trước buổi học", "Số liệu để đối chiếu"))):
            continue
        out.append(b)
        if b["t"] == "table" and b.get("teacher"):
            out += [P("Trước buổi học: kiểm tra Excel trên máy lớp có mục Encrypt with Password. Nếu cho học viên làm Cách 2 ở bước 4, cài sẵn Python và chạy py -m pip install msoffcrypto-tool trên máy lớp.", teacher=True),
                    P("Số liệu để đối chiếu khi chữa bài: 400 hộ, 106 hộ còn nợ. TongHop: Phường Bắc 89 hộ / 40.707 kWh; Phường Nam 100 / 47.559; Xã Đông 94 / 42.083; Xã Tây 117 / 55.170.", teacher=True)]
    at = next(i for i, b in enumerate(out) if b["t"] == "list") + 1
    out.insert(at, LINK(TH6_FILE, "Tải file luyện tập BaoCao_Thang.xlsx", " (dữ liệu giả lập, mở bằng Excel)."))
    out = _replace(out, "Nhiệm vụ – Phần A", lambda b: b.get("plain", "").startswith("Đầu ra Phần A"), TH6_A())
    return _replace(out, "Nhiệm vụ – Phần B (làm như chị Dung)", lambda b: b["t"] == "h3", TH6_B())


def _th7(blocks):
    """Bỏ ba script của giảng viên; thay bằng file CSV tải sẵn, bảng kết quả kiểm tra và hướng dẫn Python từng bước."""
    drop = ("Ba script Python", "Script 1", "Script 2", "Script 3", "Kết quả", "File DLX_SanLuong_Q3.csv được tạo sẵn", "Bước 9 (so sánh")
    out = []
    for b in blocks:
        p = b.get("plain", "")
        if _is_link(b, TH7_FILE) or b.get("teacher") and (
                b["t"] == "code" or p.startswith(drop) or b["t"] == "table" and b["rows"][0][0]["plain"] == "Bước"):
            continue
        if b.get("reveal") and (p.startswith(("Chọn phương án xử lý", "Phần không có trong bản giao")) or b["t"] == "table" and b["rows"][0][0]["plain"] == "Phương án"):
            continue
        out.append(b)
        if b.get("reveal") and b["t"] == "table" and [c["plain"] for c in b["rows"][0][:2]] == ["Bản", "Đưa vào AI thử nghiệm?"]:
            out += TH7_PHUONG_AN()
        if b["t"] == "h3" and b.get("teacher"):
            out += [
                P("File DLX_SanLuong_Q3.csv được tạo sẵn với hai “bẫy”: phường Cảng Mới chỉ có một xưởng sản xuất; một hộ sinh hoạt ở An Phú dùng điện rất lớn. Kết quả kiểm tra để chữa bài (tháng 2026-09):", teacher=True),
                T(["Bước", "Kiểm tra", "Kết quả chính"],
                  ["A", "Tổng hợp thô theo phường", "Cảng Mới 1 KH / 42.359 kWh; Phú Thượng 121 / 50.321; Đông Hòa 130 / 49.228; Bình Minh 148 / 50.969; Tân Lập 163 / 62.234; An Phú 174 / 64.263"],
                  ["B", "Nhóm dưới 10 khách hàng", "Cảng Mới, cả 3 tháng (1 khách hàng)"],
                  ["C", "Hộ sinh hoạt lớn nhất so với trung bình", "An Phú 3.370 kWh, trung bình 303; các phường khác 470–517"],
                  ["D", "Gộp Cảng Mới vào Đông Hòa", "Đông Hòa và Cảng Mới: 131 KH / 91.587 kWh – qua ngưỡng nhóm"],
                  ["E", "Tỷ trọng khách hàng lớn nhất trong nhóm", "Đông Hòa và Cảng Mới 46,3%; các phường khác 3,6–5,2%"],
                  ["F", "Phương án 2: chỉ Sinh hoạt và Kinh doanh", "Mọi phường từ 121 KH, không ai quá 5,2% – đạt"],
                  ["Bản che", "Bỏ tên, địa chỉ, nợ; che điện thoại; mã thay thế HMAC", "Còn nhóm nhỏ: Cảng Mới – Sản xuất 1, Bình Minh – Kinh doanh 8; nổi bật dòng 42.359 và 3.370 kWh; mã thay thế cố định qua 3 tháng"],
                  teacher=True),
                P("Bước 9 (so sánh 4 phương án, cả quý): A 1 KH – 100% – giữ 100%; B 121 – 5,2% – 86,6%; D 121 – 49,5% (tháng 8) – 100%; F 121 – 5,2% – 86,6%. Phần 13,4% bị tách là xưởng Cảng Mới (128.185 kWh). B và F cùng số nhưng B bỏ mất xưởng mà không báo ai; F tách có chủ đích và ghi trong đề xuất.", teacher=True),
                P("Kết quả học viên chạy mã ở các bước 4–10 phải ra đúng các số trên. Hay lệch vì: bỏ dtype ở bước 1 (mất số 0 đầu số điện thoại); đếm count thay vì nunique; quên lọc tháng 2026-09 khi so sánh. Mã thay thế ở bước 3 khác nhau giữa các học viên vì mỗi người dùng một khóa – đúng như mong đợi.", teacher=True)]
    at = next(i for i, b in enumerate(out) if b.get("plain", "").startswith("Dữ liệu để làm bài")) + 1
    out.insert(at, LINK(TH7_FILE, "Tải file luyện tập DLX_SanLuong_Q3.csv", " (dữ liệu giả lập; mở bằng Excel qua Data → From Text/CSV)."))
    return _replace(out, "Nhiệm vụ", lambda b: b.get("plain", "").startswith("Bài cần nộp"), TH7_STEPS())


def apply(module):
    no = module.get("no")
    lessons = LESSONS.get(no)
    if not lessons:
        return module
    for section in module["sections"]:
        title = section["title"]
        for prefix, build in lessons.items():
            if title.startswith(prefix) and section["kind"] == "content":
                section["blocks"] = build()
        if not title.startswith("Bài "):
            section["blocks"] = _fix_text(section["blocks"], TEXT_FIXES[no])
        if section.get("activity") == "m05-th6":
            section["blocks"] = _th6(section["blocks"])
        if section.get("activity") == "m06-th7":
            section["blocks"] = _th7(section["blocks"])
    return module


if __name__ == "__main__":
    # Áp bản gọn vào JSON hiện có mà không cần dựng lại từ file Word.
    import json
    from pathlib import Path
    out = Path(__file__).resolve().parent.parent / "app" / "content"
    for n in LESSONS:
        f = out / f"m{n:02d}.json"
        doc = apply(json.loads(f.read_text(encoding="utf-8")))
        f.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f.name, len(f.read_text(encoding="utf-8")))
