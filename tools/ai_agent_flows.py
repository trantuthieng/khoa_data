"""Mô hình động dạng sơ đồ khối cho khóa AI Agent (dùng trong tools/ai_agent_course.py).

Mỗi hàm trả về spec cho component FlowDemo (app/static/flowdemo.js): khối, mũi tên và các tình huống chạy
từng bước. Bước 0 là toàn cảnh như hình tĩnh; từ bước 1 dữ liệu chạy dọc mũi tên. Số liệu, tên đơn vị là
giả lập, khớp với ví dụ trong bài.
"""


def N(id, x, y, w, h, t, k="note"):
    return {"id": id, "x": x, "y": y, "w": w, "h": h, "t": t, "k": k}


def E(id, a, b, d=None, lb=None):
    e = {"id": id, "a": a, "b": b}
    if d:
        e["d"] = d
    if lb:
        e["lb"] = lb
    return e


def S(s, t, x=None, on=(), go=(), msg=None, tag=None, tone=None, set=None, code=None):
    st = {"s": s, "t": t, "on": list(on), "go": list(go)}
    for k, v in (("x", x), ("msg", msg), ("tag", tag), ("tone", tone), ("set", set), ("code", code)):
        if v:
            st[k] = v
    return st


def C(name, intro, steps, set=None):
    c = {"name": name, "intro": intro, "steps": steps}
    if set:
        c["set"] = set
    return c


def spec(label, w, h, nodes, edges, scenarios, notes=None):
    sp = {"label": label, "w": w, "h": h, "nodes": nodes, "edges": edges, "scenarios": scenarios}
    if notes:
        sp["notes"] = notes
    return sp


# ================================================================ Tổng quan – LLM đoán chữ tiếp theo

def fl_doan_chu():
    nodes = [N("in", 10, 26, 240, 70, ["Câu đang viết", "“Thủ đô của Việt Nam là”"]),
             N("llm", 290, 26, 130, 70, ["LLM", "tính xác suất", "cho mọi chữ"], "brand"),
             N("pick", 460, 26, 140, 70, ["Chọn chữ", "xác suất cao nhất"]),
             N("end", 636, 26, 74, 70, ["Dừng", "gặp dấu", "kết thúc"], "ok")]
    edges = [E("e1", "in", "llm"), E("e2", "llm", "pick"), E("e4", "pick", "end"),
             E("e3", "pick", "in", d="M530,96 V132 H130 V98", lb="nối chữ vừa chọn vào câu, đoán tiếp")]
    a = C("Câu có trong kiến thức",
          "LLM viết từng chữ một: tính xác suất cho chữ kế tiếp, chọn một chữ, nối vào câu rồi lặp lại.",
          [S("Đọc câu", "LLM đọc phần câu đã có",
             "Đầu vào là đoạn chữ đã có: “Thủ đô của Việt Nam là”. LLM không tra cứu ở đâu – nó chỉ dùng những gì học "
             "được lúc huấn luyện.", on=["in"]),
           S("Tính xác suất", "Chấm điểm mọi chữ có thể đứng tiếp theo",
             "Với mỗi chữ trong vốn từ, LLM tính khả năng nó đứng tiếp theo.", on=["llm"], go=["e1"],
             msg="Thủ đô của Việt Nam là", code="Hà Nội      91%\nmột         4%\nthành phố   3%\nnơi         1%\n…"),
           S("Chọn chữ", "Chọn “Hà Nội”", "Chữ có xác suất cao nhất được chọn.", on=["pick"], go=["e2"],
             msg="Hà Nội · 91%", tag={"pick": "Hà Nội · 91%"}, tone={"pick": "ok"}),
           S("Nối, đoán tiếp", "Nối vào câu và đoán chữ kế tiếp",
             "Câu mới lại thành đầu vào. Một câu trả lời dài là hàng trăm vòng như thế này.", on=["in"], go=["e3"],
             msg="Hà Nội", set={"in": ["Câu đang viết", "“…Việt Nam là Hà Nội”"]}),
           S("Dừng", "Chọn dấu chấm và dừng",
             "Câu trả lời đúng vì “Hà Nội” xuất hiện rất nhiều lần trong dữ liệu huấn luyện.", on=["end"], go=["e4"],
             msg=".", tone={"end": "ok"}, set={"in": ["Câu đang viết", "“…Việt Nam là Hà Nội.”"]})])
    b = C("Thiếu dữ kiện → ảo giác",
          "Cùng cơ chế, nhưng câu hỏi về điều LLM chưa từng thấy: doanh thu của Nhà Xanh (đơn vị giả lập).",
          [S("Đọc câu", "LLM đọc phần câu đã có", "Đầu vào: “Doanh thu quý III của Nhà Xanh là”.", on=["in"]),
           S("Tính xác suất", "Xác suất chia đều cho nhiều con số",
             "LLM chưa từng thấy số liệu này nên không chữ nào nổi trội.", on=["llm"], go=["e1"],
             msg="Doanh thu quý III…", code="12 tỷ   18%\n15 tỷ   16%\n9 tỷ    14%\n20 tỷ   11%\n…"),
           S("Chọn chữ", "Vẫn phải chọn một con số",
             "LLM không có lựa chọn “tôi không biết” – trừ khi được dặn trong prompt.", on=["pick"], go=["e2"],
             msg="12 tỷ · 18%", tag={"pick": "12 tỷ · 18%"}, tone={"pick": "bad"}),
           S("Nối, đoán tiếp", "Câu trôi chảy dần", on=["in"], go=["e3"], msg="12 tỷ",
             x="LLM tiếp tục viết cho tròn câu, giọng rất tự tin.",
             set={"in": ["Câu đang viết", "“…của Nhà Xanh là", "12 tỷ đồng”"]}),
           S("Dừng", "Câu trả lời bịa nhưng nghe hợp lý",
             "Đây là <strong>ảo giác</strong>. Cách chữa: đưa dữ kiện vào ngữ cảnh (RAG – buổi 2) và dặn “thiếu dữ kiện "
             "thì nói không biết”.", on=["end"], go=["e4"], msg=".", tone={"end": "bad"},
             set={"in": ["Câu đang viết", "“…của Nhà Xanh là", "12 tỷ đồng.”"]})],
          set={"in": ["Câu đang viết", "“Doanh thu quý III", "của Nhà Xanh là”"]})
    return spec("LLM đoán chữ tiếp theo", 720, 146, nodes, edges, [a, b])


# ================================================================ Buổi 1 – vòng lặp Agent

def fl_agent_loop():
    nodes = [N("goal", 10, 20, 110, 64, ["Mục tiêu", "người dùng giao"]),
             N("per", 160, 20, 170, 64, ["1. Nhận thức", "đọc yêu cầu, tài liệu,", "kết quả công cụ"], "brand"),
             N("think", 390, 20, 170, 64, ["2. Suy luận", "lập kế hoạch,", "chọn công cụ"], "brand"),
             N("done", 600, 20, 110, 64, ["Xong", "trả kết quả", "hoặc chờ duyệt"], "ok"),
             N("act", 390, 150, 170, 64, ["3. Hành động", "gọi công cụ,", "tạo bản nháp"], "warn"),
             N("obs", 160, 150, 170, 64, ["Quan sát", "kết quả hành động", "thành dữ kiện mới"])]
    edges = [E("g1", "goal", "per"), E("g2", "per", "think"), E("g3", "think", "done", lb="đủ"),
             E("g4", "think", "act", lb="chưa đủ"), E("g5", "act", "obs"), E("g6", "obs", "per", lb="lặp lại")]
    a = C("Đơn NX-1024 có kịp thứ Bảy?",
          "Khách hỏi: <em>“Đơn NX-1024 của tôi bao giờ giao? Có kịp thứ Bảy không?”</em> Agent CSKH của Nhà Xanh có công "
          "cụ <code>tra_cuu_don_hang</code>.",
          [S("Nhận việc", "Agent nhận mục tiêu",
             "Trả lời khách: đơn NX-1024 giao khi nào, có kịp thứ Bảy 07/11/2026 không.", on=["goal"]),
           S("Nhận thức", "Đọc yêu cầu", "Agent tách ra hai dữ kiện: mã đơn NX-1024 và mốc thứ Bảy 07/11.",
             on=["per"], go=["g1"], msg="NX-1024 · thứ Bảy?"),
           S("Suy luận", "Chưa đủ dữ kiện",
             "Đã trả lời được chưa? Chưa – không biết lịch giao. Kế hoạch: gọi <code>tra_cuu_don_hang</code>.",
             on=["think"], go=["g2"], tag={"think": "chưa biết lịch giao"}, tone={"think": "warn"}),
           S("Hành động", "Gọi công cụ", "Agent viết yêu cầu gọi công cụ; hệ thống chạy công cụ thật.",
             on=["act"], go=["g4"], msg="tra_cuu_don_hang",
             code='{"goi_ham": "tra_cuu_don_hang",\n "tham_so": {"ma_don": "NX-1024", "thong_tin": "lich_giao"}}'),
           S("Quan sát", "Nhận kết quả", "Kết quả công cụ trở thành dữ kiện mới trong ngữ cảnh.",
             on=["obs"], go=["g5"], msg="dự kiến 06/11",
             code='{"ma_don": "NX-1024", "trang_thai": "dang_giao", "du_kien_giao": "06/11/2026"}'),
           S("Suy luận lại", "Đủ dữ kiện",
             "Vòng thứ hai: Agent đọc lại yêu cầu cùng kết quả. Dự kiến giao thứ Sáu 06/11 – trước thứ Bảy. Đủ để trả lời.",
             on=["per", "think"], go=["g6", "g2"], tag={"think": "đủ: 06/11 trước thứ Bảy"}, tone={"think": "ok"}),
           S("Xong", "Trả lời khách",
             "“Đơn NX-1024 đang được giao, dự kiến đến thứ Sáu 06/11/2026 – kịp trước thứ Bảy ạ.” Agent dừng vì đã đạt "
             "mục tiêu.", on=["done"], go=["g3"], tone={"done": "ok"})])
    b = C("Không cần công cụ",
          "Khách hỏi: <em>“Đổi trả trong mấy ngày?”</em> Chính sách đổi trả đã có sẵn trong ngữ cảnh của Agent.",
          [S("Nhận việc", "Agent nhận mục tiêu", "Trả lời thời hạn đổi trả.", on=["goal"]),
           S("Nhận thức", "Đọc yêu cầu và tài liệu", "Đoạn “Đổi trả trong 7 ngày” đã nằm trong ngữ cảnh.",
             on=["per"], go=["g1"], msg="Đổi trả mấy ngày?"),
           S("Suy luận", "Đủ ngay", "Không cần hành động nào thêm.", on=["think"], go=["g2"],
             tag={"think": "đủ ngay"}, tone={"think": "ok"}),
           S("Xong", "Trả lời", "“Trong 7 ngày kể từ ngày nhận hàng… (Nguồn: Đổi trả trong 7 ngày).” Agent tự quyết số "
             "vòng lặp: đủ dữ kiện thì dừng ngay – khác Workflow luôn đi đủ các bước vẽ sẵn.",
             on=["done"], go=["g3"], tone={"done": "ok"})])
    c = C("Việc cần người duyệt",
          "Khách nhắn: <em>“Hủy đơn NX-1024 giúp tôi.”</em> Hủy đơn nằm ở mức <strong>cần duyệt</strong> trong bảng "
          "quyền quyết định.",
          [S("Nhận việc", "Agent nhận mục tiêu", "Khách muốn hủy đơn NX-1024.", on=["goal"]),
           S("Nhận thức", "Đọc yêu cầu", on=["per"], go=["g1"], msg="Hủy đơn NX-1024"),
           S("Suy luận", "Không được tự hủy", "Theo bảng quyền: Agent chỉ được tạo bản nháp yêu cầu hủy.",
             on=["think"], go=["g2"], tag={"think": "mức: cần duyệt"}, tone={"think": "warn"}),
           S("Hành động", "Tạo bản nháp", on=["act"], go=["g4"], msg="nháp yêu cầu hủy",
             x="Agent tạo bản nháp, không gọi hàm hủy đơn (nó cũng không được cấp hàm đó)."),
           S("Quan sát", "Bản nháp đã tạo", on=["obs"], go=["g5"], msg="nháp #H-102"),
           S("Dừng", "Chờ con người",
             "“Em đã chuyển yêu cầu hủy đơn NX-1024 cho nhân viên CSKH, anh/chị sẽ nhận xác nhận trong ít phút.” Điều kiện "
             "dừng ở đây là <strong>cần con người</strong>.", on=["per", "think", "done"], go=["g6", "g2", "g3"],
             tone={"done": "warn"}, set={"done": ["Chờ duyệt", "nhân viên CSKH", "bấm Duyệt"]})])
    return spec("Vòng lặp của Agent", 720, 228, nodes, edges, [a, b, c])


# ================================================================ Buổi 1 – System Instructions chạy thế nào

def fl_system_instructions():
    nodes = [N("msg", 10, 115, 110, 60, ["Tin nhắn", "của khách"]),
             N("scope", 150, 115, 120, 60, ["SCOPE", "trong phạm vi?"], "brand"),
             N("inp", 300, 115, 130, 60, ["INPUT CHECK", "đủ thông tin?"], "brand"),
             N("kb", 460, 115, 110, 60, ["Knowledge", "tra chính sách"]),
             N("out", 600, 115, 110, 60, ["OUTPUT", "+ BOUNDARIES"], "ok"),
             N("ask", 300, 228, 130, 50, ["Hỏi lại", "tối đa 2 câu"], "warn"),
             N("esc", 150, 12, 120, 50, ["ESCALATION", "chuyển bộ phận"], "bad")]
    edges = [E("s1", "msg", "scope"), E("s2", "scope", "inp", lb="trong"), E("s3", "inp", "kb", lb="đủ"),
             E("s4", "kb", "out"), E("s5", "inp", "ask", lb="thiếu"), E("s6", "scope", "esc", lb="ngoài")]
    a = C("Thiếu thông tin", "Tin nhắn: <em>“Khách bảo hàng bị lỗi, muốn trả.”</em>",
          [S("Tin nhắn", "Agent đọc tin nhắn", "WORKFLOW bắt đầu từ bước 1.", on=["msg"]),
           S("SCOPE", "Trong phạm vi", "Đổi trả thuộc phạm vi của Agent → đi tiếp.", on=["scope"], go=["s1"],
             msg="hàng lỗi, muốn trả", tag={"scope": "đổi trả: trong phạm vi"}, tone={"scope": "ok"}),
           S("INPUT CHECK", "Thiếu thông tin bắt buộc",
             "INPUT CHECK ghi: đổi trả cần ngày nhận hàng và tình trạng sản phẩm. Tin nhắn chưa có.", on=["inp"],
             go=["s2"], tag={"inp": "thiếu ngày nhận, lỗi gì"}, tone={"inp": "warn"}),
           S("Hỏi lại", "Hỏi gộp một lượt",
             "“Anh/chị cho em xin ngày nhận hàng (hoặc mã đơn) và sản phẩm lỗi thế nào ạ?” WORKFLOW dừng ở đây – chưa tra "
             "tài liệu khi chưa đủ dữ kiện.", on=["ask"], go=["s5"], tone={"ask": "ok"})])
    b = C("Đủ thông tin", "Tin nhắn: <em>“Khách nhận nồi chiên 3 ngày trước, chưa dùng, còn hộp, muốn đổi màu khác.”</em>",
          [S("Tin nhắn", "Agent đọc tin nhắn", on=["msg"]),
           S("SCOPE", "Trong phạm vi", on=["scope"], go=["s1"], msg="đổi màu nồi chiên",
             tag={"scope": "đổi trả: trong phạm vi"}, tone={"scope": "ok"}),
           S("INPUT CHECK", "Đủ thông tin", "Có ngày nhận (3 ngày trước) và tình trạng (chưa dùng, còn hộp).",
             on=["inp"], go=["s2"], tag={"inp": "đủ: 3 ngày, còn hộp"}, tone={"inp": "ok"}),
           S("Knowledge", "Tra chính sách", on=["kb"], go=["s3"], msg="đổi ý trong 7 ngày?",
             tag={"kb": "mục Đổi trả trong 7 ngày"}),
           S("OUTPUT", "Trả lời theo khuôn",
             "“<strong>Được đổi.</strong> Khách đổi ý trong 7 ngày, sản phẩm còn tem, hộp thì được đổi; khách chịu phí vận "
             "chuyển hai chiều. (Nguồn: Đổi trả trong 7 ngày)” – câu đầu trả lời thẳng, tối đa 5 câu, có nguồn; BOUNDARIES: "
             "không hứa gì ngoài chính sách.", on=["out"], go=["s4"], tone={"out": "ok"})])
    c = C("Ngoài phạm vi", "Tin nhắn: <em>“Máy sấy tóc bốc khói khi đang dùng, khách bị bỏng nhẹ.”</em>",
          [S("Tin nhắn", "Agent đọc tin nhắn", on=["msg"]),
           S("SCOPE", "Ngoài phạm vi", "SCOPE liệt kê sự cố an toàn sản phẩm là ngoài phạm vi.", on=["scope"],
             go=["s1"], msg="bốc khói, bỏng", tag={"scope": "sự cố an toàn"}, tone={"scope": "bad"}),
           S("ESCALATION", "Chuyển bộ phận an toàn",
             "“Đây là sự cố an toàn – anh/chị đề nghị khách ngừng dùng, rút phích cắm và chuyển ngay bộ phận Kỹ thuật – An "
             "toàn sản phẩm.” Agent không tra chính sách đổi trả, không hứa bồi thường.", on=["esc"], go=["s6"],
             tone={"esc": "ok"})])
    return spec("System Instructions: một tin nhắn đi qua các khối", 720, 290, nodes, edges, [a, b, c])


# ================================================================ Buổi 2 – RAG hai giai đoạn

def fl_rag():
    xs, w = [10, 155, 300, 445, 590], 118
    r1 = [("doc", ["Tài liệu gốc", "PDF 39 trang"], "note"), ("clean", ["Làm sạch", "Markdown, CSV"], "note"),
          ("chunk", ["Cắt đoạn", "cha và con"], "note"), ("emb", ["Embedding", "chữ → vector"], "note"),
          ("vdb", ["Vector DB", "lưu đoạn + vector"], "brand")]
    r2 = [("q", ["Câu hỏi", "của thí sinh"], "note"), ("rw", ["Viết lại", "câu hỏi đủ nghĩa"], "note"),
          ("srch", ["Tìm Top-K", "Hybrid"], "brand"), ("pr", ["Ghép prompt", "đoạn + câu hỏi"], "note"),
          ("llm", ["LLM trả lời", "kèm nguồn"], "ok")]
    nodes = [N(i, xs[k], 30, w, 54, t, kk) for k, (i, t, kk) in enumerate(r1)]
    nodes += [N(i, xs[k], 140, w, 54, t, kk) for k, (i, t, kk) in enumerate(r2)]
    edges = [E(f"a{k}", r1[k - 1][0], r1[k][0]) for k in range(1, 5)]
    edges += [E(f"b{k}", r2[k - 1][0], r2[k][0]) for k in range(1, 5)]
    edges.append(E("v", "vdb", "srch", d="M649,84 V110 H359 V138", lb="tìm theo nghĩa và từ khóa"))
    notes = [{"x": 10, "y": 20, "t": "① Nạp tài liệu – làm một lần, làm lại khi tài liệu thay đổi"},
             {"x": 10, "y": 130, "t": "② Hỏi đáp – mỗi câu hỏi"}]
    ingest = C("Nạp tài liệu",
               "Giai đoạn ① là chặng 1–4 của bài: đưa thông báo tuyển sinh vào Knowledge Base. Làm một lần, làm lại khi tài liệu đổi.",
               [S("Tài liệu gốc", "PDF 39 trang", "Giữ nguyên bản gốc, ghi mã thông báo, ngày, số trang.", on=["doc"],
                  tag={"doc": "2805/TB-ĐHĐT"}),
                S("Làm sạch", "Chọn phần cần dùng, đối chiếu",
                  "Bốn Markdown: thông tin chung, 12 dòng ngành, 53 tổ hợp, mục 5.1–5.3. Mỗi mục bắt đầu bằng đề mục ##.", on=["clean"],
                  go=["a1"], msg="PDF 39 trang", tag={"clean": "4 file .md"}),
                S("Cắt đoạn", "Mỗi mục một đoạn cha, mỗi dòng một đoạn con", "Cấu hình của bài cho 72 đoạn cha và 474 đoạn con.",
                  on=["chunk"], go=["a2"], msg="4 file sạch", tag={"chunk": "72 cha, 474 con"}),
                S("Embedding", "Đổi mỗi đoạn con thành vector",
                  "Mô hình embedding đổi mỗi đoạn con thành một dãy hàng nghìn con số biểu diễn nghĩa.", on=["emb"],
                  go=["a3"], msg="474 đoạn con", tag={"emb": "1 đoạn → 1 vector"}),
                S("Lưu kho", "Vector DB lưu đoạn + vector",
                  "Kho sẵn sàng. Từ giờ mỗi câu hỏi chỉ chạy giai đoạn ②.", on=["vdb"], go=["a4"], msg="474 vector",
                  tone={"vdb": "ok"}, tag={"vdb": "sẵn sàng"})])
    normal = C("Câu hỏi thường", "Giai đoạn ②, câu hỏi: <em>“Phương thức 100 có cộng điểm chứng chỉ ngoại ngữ không?”</em>",
               [S("Câu hỏi", "Thí sinh hỏi", on=["q"], set={"q": ["Câu hỏi", "“PT 100 có cộng", "điểm chứng chỉ?”"]}),
                S("Viết lại", "Câu hỏi đã đủ nghĩa", "Không phải câu nối tiếp nên giữ nguyên.", on=["rw"], go=["b1"],
                  msg="PT 100 cộng điểm?", tag={"rw": "giữ nguyên"}),
                S("Tìm Top-K", "Tìm đoạn gần nhất trong kho",
                  "Câu hỏi được đổi thành vector, so với 474 đoạn con. Đoạn con về chứng chỉ khớp nhất, kéo theo cả đoạn cha 5.2. Điểm 0,682 lấy từ log lần chạy thật.",
                  on=["srch", "vdb"], go=["b2", "v"], msg={"b2": "PT 100 cộng điểm?", "v": "474 vector"},
                  tag={"srch": "đầu bảng 0,682: mục 5.2"}),
                S("Ghép prompt", "Điền đoạn và câu hỏi vào prompt", on=["pr"], go=["b3"], msg="6 đoạn cha",
                  code="Chỉ sử dụng bằng chứng trong NGỮ CẢNH…\nNGỮ CẢNH:\n5.2. Điểm cộng và quy đổi điểm chứng chỉ ngoại ngữ\n- Với phương thức 100, chứng chỉ ngoại ngữ dùng để quy đổi điểm môn…\nUSER: Phương thức 100 có cộng điểm chứng chỉ ngoại ngữ không?"),
                S("Trả lời", "LLM trả lời kèm nguồn",
                  "“Không. Với phương thức 100, chứng chỉ dùng để quy đổi điểm môn, không dùng để cộng điểm. Nguồn: mục 5.2, trang PDF 19.”",
                  on=["llm"], go=["b4"], tone={"llm": "ok"})])
    follow = C("Câu hỏi nối tiếp",
               "Thí sinh vừa hỏi Mầm non cao đẳng, giờ hỏi tiếp: <em>“Còn đại học thì sao?”</em>",
               [S("Câu hỏi", "Câu hỏi thiếu chủ ngữ", "Đem “Còn đại học thì sao?” đi tìm sẽ lạc.", on=["q"],
                  set={"q": ["Câu hỏi", "“Còn đại học", "thì sao?”"]}),
                S("Viết lại", "Bổ sung từ lịch sử chat",
                  "Khối viết lại đọc lịch sử, thay “còn … thì sao” bằng nội dung cụ thể. Bạn dựng khối này ở chặng 6.", on=["rw"], go=["b1"],
                  msg="Còn đại học thì sao?", tag={"rw": "→ Mầm non đại học"}, tone={"rw": "warn"},
                  code="Chỉ tiêu dự kiến của Giáo dục Mầm non trình độ đại học là bao nhiêu?"),
                S("Tìm Top-K", "Tìm bằng câu đã viết lại", on=["srch", "vdb"], go=["b2", "v"],
                  msg={"b2": "Mầm non đại học", "v": "474 vector"}, tag={"srch": "đầu bảng: mã 7140201"},
                  x="Nhờ câu đầy đủ nghĩa, đoạn Mầm non đại học đứng đầu."),
                S("Ghép prompt", "Điền đoạn và câu đã viết lại", on=["pr"], go=["b3"], msg="6 đoạn cha"),
                S("Trả lời", "Trả lời đúng mạch hội thoại", "“Giáo dục Mầm non trình độ đại học (mã 7140201) có chỉ tiêu dự kiến 450.” kèm nguồn trang 13.",
                  on=["llm"], go=["b4"], tone={"llm": "ok"})])
    trap = C("Câu bẫy: tài liệu không có",
             "Câu hỏi: <em>“Học phí bao nhiêu?”</em> Bộ mẫu không có trang học phí.",
             [S("Câu hỏi", "Thí sinh hỏi", on=["q"], set={"q": ["Câu hỏi", "“Học phí", "bao nhiêu?”"]}),
              S("Viết lại", "Giữ nguyên", on=["rw"], go=["b1"], msg="Học phí bao nhiêu?", tag={"rw": "giữ nguyên"}),
              S("Tìm Top-K", "Vẫn có đoạn trả về",
                "Đoạn đứng đầu là tổ hợp X10, điểm 0,427 theo log, chẳng liên quan gì học phí. Ngưỡng đang tắt nên kết quả không rỗng.",
                on=["srch", "vdb"], go=["b2", "v"], msg={"b2": "Học phí…", "v": "474 vector"},
                tag={"srch": "0,427: không liên quan"}, tone={"srch": "warn"}),
              S("Ghép prompt", "Ngữ cảnh có đoạn nhưng không có câu trả lời", on=["pr"], go=["b3"], msg="6 đoạn không liên quan",
                code="NGỮ CẢNH:\nTổ hợp X10 - SPD - năm 2026 …\nUSER: Học phí bao nhiêu?"),
              S("Trả lời", "Nói rõ là chưa có",
                "“Bộ tài liệu mẫu chưa có thông tin này.” Đúng là nhờ nguyên tắc 1 và 5 trong prompt: LLM đánh giá bằng chứng, không đoán con số.", on=["llm"], go=["b4"], tone={"llm": "ok"})])
    return spec("Hệ thống RAG hai giai đoạn", 720, 204, nodes, edges, [ingest, normal, follow, trap], notes)


# ================================================================ Buổi 3 – workflow 3 nhánh + Evaluator

def fl_workflow():
    nodes = [N("start", 10, 120, 80, 60, ["Start", "sys.query"]),
             N("qc", 105, 120, 92, 60, ["Question", "Classifier"], "brand"),
             N("ext", 212, 120, 92, 60, ["Parameter", "Extractor"], "brand"),
             N("cond", 320, 120, 84, 60, ["IF/ELIF", "/ELSE"], "warn"),
             N("ask", 430, 14, 150, 48, ["ELIF: thiếu dữ liệu", "hỏi lại thí sinh"]),
             N("code", 430, 120, 70, 60, ["Code", "tính điểm"], "ok"),
             N("wri", 515, 120, 80, 60, ["LLM", "Viết"], "brand"),
             N("ev", 610, 120, 100, 60, ["LLM", "Evaluator"], "ok"),
             N("conf", 430, 238, 150, 48, ["IF: mâu thuẫn", "nêu chênh lệch"], "warn"),
             N("out", 610, 238, 100, 48, ["Answer", "có nguồn"], "ok")]
    edges = [E("w0", "start", "qc"), E("w1", "qc", "ext"), E("w2", "ext", "cond"), E("w3", "cond", "ask", lb="thiếu"),
             E("w4", "cond", "code", lb="đủ"), E("w5", "cond", "conf", lb="lệch"), E("w6", "code", "wri"),
             E("w7", "wri", "ev"), E("w8", "ev", "wri", d="M640,180 V206 H555 V182", lb="chưa đạt"), E("w9", "ev", "out", lb="đạt")]
    a = C("Thiếu dữ liệu", "Thí sinh: <em>“Tính điểm giúp em.”</em>",
          [S("Phân loại", "Xếp vào Tư vấn cá nhân", on=["qc"], go=["w0"], msg="Tính điểm giúp em", tag={"qc": "Tư vấn cá nhân"}),
           S("Trích xuất", "Không nêu thì để trống", "Thí sinh không nêu số nên <code>tong_diem</code>, <code>muc_uu_tien</code> trống. Khối không đoán.", on=["ext"], go=["w1"], tag={"ext": "tong_diem = trống"}, tone={"ext": "warn"}),
           S("Rẽ nhánh", "Biến điểm rỗng", on=["cond"], go=["w2"], tag={"cond": "ELIF"}),
           S("Hỏi lại", "Hỏi gộp hai ô thiếu", "Không gọi LLM viết bài, không gọi khối Code. Lượt này gần như không tốn tiền.", on=["ask"], go=["w3"], tone={"ask": "ok"})])
    b = C("Mâu thuẫn", "Thí sinh: <em>“Nghe nói Sư phạm Toán tuyển 200, đúng không?”</em>",
          [S("Phân loại", "Tư vấn cá nhân", on=["qc"], go=["w0"], msg="…tuyển 200, đúng không?"),
           S("Trích xuất", "Bắt được con số tự nêu", on=["ext"], go=["w1"], tag={"ext": "so_tu_neu = 200"}),
           S("Rẽ nhánh", "Có số tự nêu", "Điều kiện IF: <code>so_tu_neu</code> không rỗng. Nhánh này xét trước, vì câu này không cần điểm.", on=["cond"], go=["w2"], tag={"cond": "IF"}, tone={"cond": "warn"}),
           S("Đối chiếu", "Tài liệu ghi 115", "Trợ lý nêu rõ con số khác tài liệu, không xác nhận theo lời người hỏi, và nhắc kiểm tra thông báo bổ sung.", on=["conf"], go=["w5"], tone={"conf": "ok"})])
    c = C("Đủ dữ liệu", "Thí sinh: <em>“Em được 24,5, ưu tiên 0,5.”</em>",
          [S("Phân loại, trích xuất", "Đủ hai biến bắt buộc", on=["ext"], go=["w0", "w1"], msg="24,5 và 0,5", tag={"ext": "24.5 · 0.5"}, tone={"ext": "ok"}),
           S("Rẽ nhánh", "Đi ELSE", on=["cond"], go=["w2"], tag={"cond": "ELSE"}, tone={"cond": "ok"}),
           S("Code", "Quy tắc cứng tính điểm", "Công thức (1), (2) của thông báo. Không để LLM tính.", on=["code"], go=["w4"], tag={"code": "24,87"}, tone={"code": "ok"}),
           S("Viết lần 1", "LLM viết, quên nguồn", on=["wri"], go=["w6"], tag={"wri": "thiếu Nguồn"}, tone={"wri": "warn"}),
           S("Evaluator", "Trả CHUA_DAT kèm lỗi", on=["ev"], go=["w7"], tag={"ev": "CHUA_DAT"}, tone={"ev": "bad"}),
           S("Viết lần 2", "Sửa đúng lỗi được nêu", "Vòng sửa có giới hạn: hết số vòng mà chưa đạt thì chuyển người.", on=["wri"], go=["w8"], tag={"wri": "có Nguồn"}, tone={"wri": "ok"}),
           S("Trả lời", "Evaluator đạt", on=["out"], go=["w7", "w9"], tone={"out": "ok", "ev": "ok"}, tag={"ev": "DAT"})])
    return spec("Workflow của trợ lý tuyển sinh", 720, 296, nodes, edges, [a, b, c])


def fl_quy_trinh():
    steps = [("doc", "1. Đọc tin nhắn", "LLM trích xuất", "brand"), ("thieu", "2. Thiếu gì?", "Điều kiện", "warn"), ("tra", "3. Tra quy định", "Knowledge Retrieval", "brand"),
             ("tinh", "4. Tính điểm", "Code", "ok"), ("soan", "5. Soạn trả lời", "LLM viết", "brand"), ("nguoi", "6. Ngoại lệ", "Con người", "warn")]
    nodes = [N(i, 8 + k * 119, 36, 108, 74, [a, b], kk) for k, (i, a, b, kk) in enumerate(steps)]
    edges = [E(f"q{k}", steps[k][0], steps[k + 1][0]) for k in range(5)]
    why = ["Cán bộ đọc tin nhắn tự do của thí sinh. Cần hiểu câu chữ, nên dùng LLM.", "“Có đủ điểm và mức ưu tiên chưa?” là quy tắc rõ ràng, không cần LLM.",
           "Cán bộ mở thông báo tuyển sinh. Trên Dify là tìm trong kho của Buổi 2.", "Công thức có hai nhánh, phải chính xác tuyệt đối: quy tắc cứng. LLM đọc số theo token nên dễ sai.",
           "Viết cho thí sinh hiểu là việc cần ngôn ngữ: LLM, dựa trên kết quả các bước trước.", "Ngưỡng 15 có ngoại lệ, hồ sơ đặc thù, khiếu nại: thuộc thẩm quyền cán bộ. Máy không quyết."]
    a = C("Từ cách cán bộ làm sang khối", "Đi từng bước một chuyên viên tuyển sinh giỏi đang làm, và hỏi: việc này cần hiểu ngôn ngữ, cần quy tắc, hay cần trách nhiệm?",
          [S(steps[k][1], steps[k][2], why[k], on=[steps[k][0]], go=[f"q{k - 1}"] if k else []) for k in range(6)])
    return spec("Từ cách cán bộ tuyển sinh làm sang các khối", 720, 130, nodes, edges, [a])


def fl_intent():
    nodes = [N("msg", 10, 96, 110, 66, ["Tin nhắn", "của thí sinh"]),
             N("rule", 145, 104, 165, 50, ["IF/ELSE từ khóa", "lo điểm, khiếu nại, kiện"], "warn"),
             N("llm", 350, 104, 150, 50, ["Question Classifier", "mô tả lớp + ví dụ"], "brand")]
    labels = [("nhay", "Nhạy cảm", "chuyển cán bộ", "bad"), ("tra", "Tra cứu", "tìm kho, trả lời có nguồn", "note"),
              ("tv", "Tư vấn cá nhân", "trích tham số, tính điểm", "note"), ("khac", "Khác", "nói rõ phạm vi", "warn")]
    nodes += [N(i, 560, 16 + k * 58, 150, 44, [a, b], kk) for k, (i, a, b, kk) in enumerate(labels)]
    edges = [E("i1", "msg", "rule"), E("i2", "rule", "llm"), E("i0", "rule", "nhay", d="M227,104 V38 H558", lb="khớp: chuyển ngay")]
    edges += [E("l" + i, "llm", i) for i, *_ in labels[1:]]

    def via_rule(name, t, hit):
        return C(name, f"Thí sinh: <em>“{t}”</em>",
                 [S("Tin nhắn", "Thí sinh nhắn", on=["msg"], msg=t[:26]),
                  S("Quy tắc", "Khớp từ khóa", "Quy tắc chạy trước LLM, chắc chắn, tức thì và không tốn lượt gọi mô hình.", on=["rule"], go=["i1"], tag={"rule": "khớp: " + hit}, tone={"rule": "bad"}),
                  S("Chuyển cán bộ", "Không qua LLM", on=["nhay"], go=["i0"], tone={"nhay": "bad"})])

    def via_llm(name, t, lid, x):
        return C(name, f"Thí sinh: <em>“{t}”</em>",
                 [S("Tin nhắn", "Thí sinh nhắn", on=["msg"], msg=t[:26]),
                  S("Quy tắc", "Không có từ khóa nhạy cảm", on=["rule"], go=["i1"], tag={"rule": "không khớp"}),
                  S("LLM phân loại", "Đọc mô tả các lớp", x, on=["llm"], go=["i2"]),
                  S("Đi đúng nhánh", dict((i, a) for i, a, *_ in labels)[lid], on=[lid], go=["l" + lid], tone={lid: "ok"})])

    sc = [via_rule("Lo điểm", "Có cách nào lo điểm để chắc đậu không ạ?", "lo điểm"),
          via_llm("Hỏi lịch", "Hạn cuối điều chỉnh nguyện vọng là khi nào?", "tra", "Thông tin chung, không có dữ liệu riêng của người hỏi."),
          via_llm("Có điểm riêng", "Em được 26 điểm thì có được miễn học phí không?", "tv", "Có điểm riêng nên cần tính và đối chiếu điều kiện, dù cũng có chữ “học phí”. Đây là ca giáp ranh cần luật ưu tiên."),
          via_llm("Ngoài phạm vi", "Cho em hỏi giá vé xe về Cao Lãnh", "khac", "Không có lớp Khác thì câu này bị ép vào Tra cứu.")]
    return spec("Nhận diện ý định: quy tắc và LLM", 720, 262, nodes, edges, sc)


def fl_function_calling():
    nodes = [N("user", 10, 50, 100, 64, ["Thí sinh"]),
             N("llm", 170, 50, 120, 64, ["LLM", "đọc mô tả", "công cụ"], "brand"),
             N("rt", 360, 50, 140, 64, ["Runtime", "kiểm tham số,", "quyền hạn"], "warn"),
             N("api", 580, 50, 130, 64, ["API hồ sơ", "hệ thống thật"], "ok"),
             N("staff", 360, 168, 140, 48, ["Cán bộ tuyển sinh"], "warn")]
    edges = [E("f1", "user", "llm", d="M110,70 H168"), E("f1r", "llm", "user", d="M170,96 H112"),
             E("f2", "llm", "rt", d="M290,70 H358"), E("f2r", "rt", "llm", d="M360,96 H292"),
             E("f3", "rt", "api", d="M500,70 H578"), E("f3r", "api", "rt", d="M580,96 H502"),
             E("f4", "llm", "staff", d="M230,114 V192 H358")]
    notes = [{"x": 360, "y": 18, "t": "LLM chỉ viết yêu cầu gọi hàm, runtime quyết định có chạy hay không", "a": "middle"}]
    a = C("Tra hồ sơ đủ thông tin", "Thí sinh: <em>“Tra hồ sơ TS26-0002, em sinh ngày 2008-07-02.”</em>",
          [S("LLM chọn hàm", "Khớp phần “Dùng khi…”", "Khớp mô tả, có đủ hai tham số bắt buộc.", on=["llm"], go=["f1"], msg="TS26-0002", tag={"llm": "tra_ho_so"}),
           S("Runtime", "Kiểm tra trước khi chạy", on=["rt"], go=["f2"], msg="JSON gọi hàm", tag={"rt": "đúng định dạng, quyền đọc"}, tone={"rt": "ok"}),
           S("API", "Chạy và trả kết quả", on=["api"], go=["f3"], tag={"api": "Thiếu minh chứng"}),
           S("Kết quả về LLM", "Kết quả được gửi lại", on=["llm"], go=["f3r", "f2r"]),
           S("Trả lời", "Dựa trên kết quả", "LLM không tự biết trạng thái hồ sơ: thông tin đến từ công cụ.", on=["user"], go=["f1r"], msg="Thiếu giấy xác nhận khu vực", tone={"user": "ok"})])
    b = C("Thiếu ngày sinh", "Thí sinh: <em>“Tra giúp em hồ sơ TS26-0002.”</em>",
          [S("LLM đọc required", "Thiếu một tham số", "<code>ngay_sinh</code> bắt buộc mà thí sinh chưa nêu. Không gọi hàm, không đoán.", on=["llm"], go=["f1"], tag={"llm": "thiếu ngay_sinh"}, tone={"llm": "warn"}),
           S("Hỏi lại", "Xin ngày sinh để xác thực", on=["user"], go=["f1r"], msg="Cho mình xin ngày sinh", tone={"user": "ok"})])
    c = C("Yêu cầu hủy hồ sơ", "Thí sinh: <em>“Hủy hồ sơ TS26-0001 giúp em.”</em>",
          [S("LLM đọc mô tả", "Khớp phần “KHÔNG dùng…”", "Không công cụ nào được phép làm việc này.", on=["llm"], go=["f1"], tag={"llm": "không gọi hàm"}, tone={"llm": "warn"}),
           S("Chuyển người", "Cán bộ xử lý", on=["staff"], go=["f4"], tone={"staff": "ok"})])
    d = C("Mã sai định dạng", "Thí sinh: <em>“Tra hồ sơ TS26-77, em sinh ngày 2008-07-02.”</em>",
          [S("LLM vẫn gọi", "LLM không phải lúc nào cũng phát hiện", on=["llm"], go=["f1"], tag={"llm": "tra_ho_so"}),
           S("Runtime chặn", "Sai định dạng", "Kiểm tra bằng mã: chắc chắn và không tốn lượt gọi API. Đây là nơi đặt chốt chặn.", on=["rt"], go=["f2"], tag={"rt": "TS26-77 sai dạng"}, tone={"rt": "bad"}),
           S("Báo lại", "Lỗi cũng là dữ liệu", "Lỗi quay về LLM để hỏi lại thí sinh. Cần giới hạn số lần thử.", on=["user"], go=["f2r", "f1r"], msg="Bạn kiểm tra lại mã giúp mình", tone={"user": "ok"})])
    return spec("Function Calling: bốn đường đi của tin nhắn", 720, 226, nodes, edges, [a, b, c, d], notes=notes)


def fl_injection():
    nodes = [N("web", 10, 50, 130, 70, ["Trang web", "có câu lệnh", "chèn vào"], "bad"),
             N("in", 175, 50, 120, 70, ["Lớp đầu vào", "thẻ dữ liệu,", "luật prompt"], "warn"),
             N("llm", 330, 50, 95, 70, ["LLM", "đọc nội dung"], "brand"),
             N("tool", 460, 50, 110, 70, ["Lớp quyền", "công cụ nào", "được gắn"], "warn"),
             N("hitl", 605, 50, 105, 70, ["Người duyệt", "trước khi gửi"], "warn"),
             N("harm", 460, 170, 250, 48, ["Danh sách hồ sơ bị gửi ra ngoài"], "bad")]
    edges = [E("j1", "web", "in"), E("j2", "in", "llm"), E("j3", "llm", "tool"), E("j4", "tool", "hitl"), E("j5", "hitl", "harm", d="M657,120 V168")]
    a = C("Không có lớp nào", "Trợ lý tự tìm trên mạng, đọc được hồ sơ, và có công cụ tự gửi thư.",
          [S("Đọc nội dung", "“Bỏ qua mọi chỉ dẫn trước…”", on=["llm"], go=["j1", "j2"], msg="lệnh chèn", tag={"llm": "làm theo"}, tone={"llm": "bad"}),
           S("Gọi công cụ", "Không có gì chặn", on=["tool"], go=["j3"], tag={"tool": "tự gửi"}, tone={"tool": "bad"}),
           S("Hậu quả", "Dữ liệu ra ngoài", "Đủ bộ ba: dữ liệu riêng, nội dung ngoài, khả năng gửi đi.", on=["harm"], go=["j4", "j5"], tone={"harm": "bad"})])
    b = C("Đủ ba lớp", "Có thẻ dữ liệu, công cụ chỉ đọc và tạo nháp, người duyệt ở cuối.",
          [S("Lớp đầu vào", "Nội dung là dữ liệu", on=["in"], go=["j1"], msg="lệnh chèn", tag={"in": "bọc thẻ"}, tone={"in": "ok"}),
           S("LLM", "Không làm theo, báo đáng ngờ", on=["llm"], go=["j2"], tag={"llm": "báo đáng ngờ"}, tone={"llm": "ok"}),
           S("An toàn", "Dừng tại đây", "Không có hành động nào được thực hiện.", on=["llm"], tone={"llm": "ok"})])
    c = C("Lớp đầu vào bị lọt", "Lời dặn trong prompt không chặn được 100%. Giả sử lần này LLM vẫn làm theo.",
          [S("Lớp đầu vào", "Có nhưng bị lọt", on=["in"], go=["j1"], msg="lệnh chèn", tag={"in": "lọt"}, tone={"in": "warn"}),
           S("LLM", "Làm theo lệnh", on=["llm"], go=["j2"], tag={"llm": "muốn gửi thư"}, tone={"llm": "bad"}),
           S("Lớp quyền", "Không có công cụ gửi", "LLM “muốn” nhưng không có tay chân để làm. Đây là lớp chắc chắn.", on=["tool"], go=["j3"], tag={"tool": "không có công cụ gửi"}, tone={"tool": "ok"})])
    return spec("Nội dung trên mạng chứa lệnh độc", 720, 228, nodes, edges, [a, b, c])


def fl_multi_agent():
    nodes = [N("u", 10, 92, 92, 56, ["Yêu cầu"]),
             N("r", 125, 92, 100, 56, ["Router", "chỉ phân việc"], "warn"),
             N("tv", 260, 10, 130, 52, ["Worker Tư vấn", "kho + tính điểm"], "brand"),
             N("hs", 260, 92, 130, 52, ["Worker Hồ sơ", "API chỉ đọc"], "brand"),
             N("wr", 260, 174, 130, 52, ["Writer", "viết theo brief"], "brand"),
             N("ed", 425, 174, 130, 52, ["Editor", "chấm rubric"], "ok"),
             N("rv", 425, 10, 130, 52, ["Kiểm số", "đối chiếu nguồn"], "ok"),
             N("h", 590, 174, 120, 52, ["Người", "duyệt, xử lý"], "warn"),
             N("o", 590, 60, 120, 52, ["Kết quả"], "ok")]
    edges = [E("m1", "u", "r"), E("m2", "r", "tv"), E("m3", "r", "hs"), E("m4", "r", "wr"), E("m5", "wr", "ed", d="M390,192 H423"), E("m6", "ed", "wr", d="M425,212 H392", lb="REJECT"),
             E("m7", "ed", "h", d="M555,200 H588", lb="hết vòng"), E("m8", "tv", "rv"), E("m9", "rv", "o"), E("m10", "hs", "o", d="M390,110 H588"),
             E("m11", "r", "h", d="M175,148 V248 H650 V228", lb="nhạy cảm")]
    a = C("Thí sinh tính điểm", "<em>“Em được 24,5, ưu tiên 0,5 thì điểm xét tuyển bao nhiêu?”</em>",
          [S("Router", "Chọn Worker Tư vấn", "Router không tự trả lời, chỉ trả JSON.", on=["r"], go=["m1"], msg="24,5 và 0,5", tag={"r": "next: Tư vấn"}),
           S("Worker", "Gọi công cụ tính điểm", on=["tv"], go=["m2"], tag={"tv": "24,87"}),
           S("Kiểm số", "Đối chiếu kết quả công cụ", on=["rv"], go=["m8"], tag={"rv": "DAT"}, tone={"rv": "ok"}),
           S("Kết quả", "Gửi thí sinh", on=["o"], go=["m9"], tone={"o": "ok"})])
    b = C("Cán bộ cần bài viết", "<em>“Viết bài nhắc hạn đăng ký theo brief B01.”</em>",
          [S("Router", "Chọn Writer", on=["r"], go=["m1"], msg="brief B01", tag={"r": "next: Writer"}),
           S("Writer", "Vòng 1", on=["wr"], go=["m4"], tag={"wr": "bản 1"}),
           S("Editor", "Trả lại kèm lý do", on=["ed"], go=["m5"], tag={"ed": "REJECT"}, tone={"ed": "bad"}),
           S("Writer", "Sửa đúng lỗi được nêu", "Thông điệp bàn giao luôn kèm phản hồi của Editor.", on=["wr"], go=["m6"], tag={"wr": "bản 2"}),
           S("Editor", "Duyệt", on=["ed"], go=["m5"], tag={"ed": "APPROVE"}, tone={"ed": "ok"}),
           S("Người", "Cán bộ bấm đăng", "Đăng ra công chúng vẫn cần người duyệt.", on=["h"], go=["m7"], tone={"h": "ok"})])
    c = C("Yêu cầu nhạy cảm", "<em>“Viết bài đính chính vì đăng nhầm chỉ tiêu.”</em>",
          [S("Router", "Nhận ra việc nhạy cảm", on=["r"], go=["m1"], msg="đính chính", tag={"r": "next: Người"}, tone={"r": "warn"}),
           S("Người", "Chuyển thẳng", "Router đoán bừa tệ hơn chuyển cho người.", on=["h"], go=["m11"], tone={"h": "ok"})])
    return spec("Phòng tuyển sinh ảo", 720, 262, nodes, edges, [a, b, c])


def fl_vong_doi():
    nodes = [N("mon", 25, 92, 150, 46, ["1. Theo dõi", "log, phản hồi, chỉ số"], "brand"),
             N("col", 155, 23, 150, 46, ["2. Thu thập lỗi", "mỗi lỗi → đề Eval mới"], "brand"),
             N("cause", 415, 23, 150, 46, ["3. Tìm nguyên nhân", "thứ tự debug buổi 1"], "brand"),
             N("fix", 545, 92, 150, 46, ["4. Sửa một điểm", "ghi Improvement Log"], "brand"),
             N("run", 415, 161, 150, 46, ["5. Chạy lại Eval", "so với bản trước"], "ok"),
             N("rel", 155, 161, 150, 46, ["6. Phát hành", "có số phiên bản"], "brand")]
    edges = [E("v1", "mon", "col", d="M100,92 V46 H153"), E("v2", "col", "cause", d="M305,46 H413"),
             E("v3", "cause", "fix", d="M565,46 H620 V90"), E("v4", "fix", "run", d="M620,138 V184 H567"),
             E("v5", "run", "rel", d="M415,184 H307", lb="không suy thoái"), E("v6", "rel", "mon", d="M155,184 H100 V140"),
             E("vb", "run", "cause", d="M470,161 V71", lb="có suy thoái")]
    notes = [{"x": 300, "y": 112, "t": "Người phụ trách", "a": "middle"}, {"x": 300, "y": 128, "t": "rà soát hằng tháng", "a": "middle"}]
    a = C("Có thông báo bổ sung", "Trường đổi một mốc đăng ký sau khi trợ lý đã chạy.",
          [S("Theo dõi", "Thí sinh báo trả lời sai hạn", on=["mon"], tag={"mon": "sai hạn"}, tone={"mon": "warn"}),
           S("Thu thập", "Thêm đề vào bộ Eval", on=["col"], go=["v1"], tag={"col": "đề mới"}),
           S("Nguyên nhân", "Tầng dữ liệu", "Tìm đúng, viết đúng, nhưng tài liệu trong kho đã cũ.", on=["cause"], go=["v2"], tag={"cause": "Knowledge"}),
           S("Sửa", "Cập nhật tài liệu, lập chỉ mục lại", on=["fix"], go=["v3"]),
           S("Chạy lại", "Cả bộ đề", on=["run"], go=["v4"], tag={"run": "không suy thoái"}, tone={"run": "ok"}),
           S("Phát hành", "Ghi phiên bản, ngày, người duyệt", on=["rel"], go=["v5"], tone={"rel": "ok"})])
    b = C("Đổi mô hình rẻ hơn", "Muốn giảm chi phí, người phụ trách thử mô hình rẻ hơn cho khối viết.",
          [S("Sửa một điểm", "Chỉ đổi mô hình", on=["fix"], tag={"fix": "khối viết"}),
           S("Chạy lại", "Hỏng hai đề suy luận", "C08 và C12 vừa đúng nay trượt, dù token giảm khoảng 30%.", on=["run"], go=["v4"], tag={"run": "2 đề suy thoái"}, tone={"run": "bad"}),
           S("Quay lại", "Không phát hành", "Sai về quy định tuyển sinh không chấp nhận được. Có thể giữ mô hình rẻ cho Router, không dùng cho khối viết.", on=["cause"], go=["vb"], tone={"cause": "warn"})])
    return spec("Vòng đời bảo trì trợ lý", 720, 220, nodes, edges, [a, b], notes=notes)


def fl_thi_mo():
    nodes = [N("q", 10, 46, 130, 66, ["Câu hỏi", "“Mầm non cao đẳng", "mã nào?”"]),
             N("kb", 180, 46, 130, 66, ["R – Tìm", "trong kho tài liệu"], "brand"),
             N("pr", 350, 46, 130, 66, ["A – Ghép", "đoạn vào prompt"]),
             N("llm", 520, 46, 110, 66, ["G – LLM", "sinh câu trả lời"], "brand"),
             N("a", 670, 46, 100, 66, ["Câu trả lời"], "ok")]
    edges = [E("e1", "q", "kb"), E("e2", "kb", "pr"), E("e3", "pr", "llm"), E("e4", "llm", "a"),
             E("d", "q", "llm", d="M75,46 V18 H575 V44", lb="không có tài liệu: đi thẳng")]
    closed = C("Thi đóng: LLM thuần", "Chưa có tài liệu nào. Mô hình chỉ có thứ đã học lúc huấn luyện, giống bạn làm bài <strong>thi đóng</strong>.",
               [S("Câu hỏi", "Hỏi thẳng mô hình", on=["q"]),
                S("LLM đoán", "Không có gì để tra", "Mô hình không tra cứu; nó sinh ra chuỗi chữ có xác suất cao nhất. Câu về một trường cụ thể cũng được trả lời trôi chảy.",
                  on=["llm"], go=["d"], msg="Mầm non cao đẳng mã nào?", tag={"llm": "không có nguồn"}, tone={"llm": "warn"}),
                S("Trả lời", "Nghe hợp lý, không kiểm chứng được", "Một mã số và một chỉ tiêu trông rất thật. Bạn vừa thử điều này ở bước đầu chặng 1.",
                  on=["a", "llm"], go=["e4"], msg="mã số tự nghĩ", tone={"a": "bad"}, tag={"a": "ảo giác"})])
    opened = C("Thi mở: RAG", "Cùng câu hỏi, nhưng hệ thống được phép <strong>mở tài liệu</strong> trước khi trả lời.",
               [S("Câu hỏi", "Câu hỏi đi vào hệ thống", on=["q"]),
                S("Retrieval", "Tìm đoạn gần nhất", "Đổi câu hỏi thành vector, tìm trong kho. Đoạn về Giáo dục Mầm non (CĐ) đứng đầu.",
                  on=["kb"], go=["e1"], msg="Mầm non cao đẳng mã nào?", tag={"kb": "đoạn trang 13"}),
                S("Augmented", "Ghép đoạn vào prompt", "LLM không đọc cả 39 trang, chỉ đọc vài đoạn liên quan cùng câu hỏi.",
                  on=["pr"], go=["e2"], msg="đoạn trang 13",
                  code="NGỮ CẢNH:\nGiáo dục Mầm non (CĐ) - mã xét tuyển 51140201\n- Trình độ: Cao đẳng.\n- Chỉ tiêu dự kiến: 100.\n\nCÂU HỎI: Mầm non cao đẳng mã nào?"),
                S("Generation", "LLM viết câu trả lời", on=["llm"], go=["e3"], msg="prompt đầy đủ", x="Mô hình vẫn là mô hình đó, chỉ khác là có dữ liệu thật trước mặt."),
                S("Trả lời", "Có nguồn, kiểm chứng được", "“Mã 51140201, chỉ tiêu dự kiến 100. Nguồn: mục 4.1, trang PDF 13.”",
                  on=["a"], go=["e4"], msg="mã thật + nguồn", tone={"a": "ok"}, tag={"a": "có nguồn"})])
    return spec("LLM thuần so với RAG", 790, 130, nodes, edges, [closed, opened])


def fl_gigo():
    nodes = [N("raw", 10, 34, 140, 72, ["Bản gốc", "PDF trang 13"]),
             N("ex", 190, 34, 140, 72, ["Đưa vào kho"], "brand"),
             N("ch", 370, 34, 150, 72, ["Đoạn con", "được tìm thấy"]),
             N("a", 560, 34, 160, 72, ["Câu trả lời"], "ok")]
    edges = [E("e1", "raw", "ex"), E("e2", "ex", "ch"), E("e3", "ch", "a")]
    dirty = C("Nạp thẳng bản thô", "Câu hỏi: <em>“Mầm non cao đẳng chỉ tiêu bao nhiêu?”</em> Không làm sạch, nạp nguyên bản trích xuất.",
              [S("Bản gốc", "Bảng trong PDF", "Trên PDF, tên ngành, tổ hợp, chỉ tiêu và phương thức cùng một hàng.", on=["raw"]),
               S("Trích xuất", "Bảng vỡ thành các dòng rời", on=["ex"], go=["e1"], msg="trang 13",
                 x="Bộ trích xuất đọc từng dòng chữ, không hiểu cột.",
                 code="1 51140201 Giáo dục Mầm non (CĐ) X70, X74, X01,\nM00, M05, NL1 100\nPT 100\nPT 301\nPT 416\nPT 402"),
               S("Tìm kiếm", "Con số nằm khác dòng với tên ngành", on=["ch"], go=["e2"], msg="đoạn rời",
                 x="Đoạn con “M00, M05, NL1 100” không nói gì về Mầm non. Chuỗi chữ ký số ở cuối trang 1 cũng thành một đoạn rác.",
                 tag={"ch": "100 của ai?"}, tone={"ch": "bad"}),
               S("Trả lời", "Sai hoặc từ chối", "LLM nhận mảnh rời nên dễ gán nhầm con số, hoặc nói không tìm thấy. Prompt tốt mấy cũng không cứu được.", on=["a"], go=["e3"], msg="mảnh rời", tone={"a": "bad"}, tag={"a": "rác vào, rác ra"})])
    clean = C("Nạp bản đã làm sạch", "Cùng câu hỏi, nhưng mỗi dòng ngành đã thành một khối Markdown đối chiếu với PDF.",
              [S("Bản gốc", "Bảng trong PDF", "Vẫn giữ nguyên PDF để đối chiếu.", on=["raw"]),
               S("Làm sạch", "Mỗi ngành một khối đủ ý", on=["ex"], go=["e1"], msg="trang 13", tone={"ex": "ok"},
                 code="## Giáo dục Mầm non (CĐ) - mã xét tuyển 51140201 - năm 2026\nNguồn: …, trang PDF 13, mục 4.1, dòng 1.\n- Trình độ: Cao đẳng.\n- Chỉ tiêu dự kiến: 100."),
               S("Tìm kiếm", "Đoạn đứng được một mình", on=["ch"], go=["e2"], msg="đoạn đủ ý", x="Tên ngành, mã, chỉ tiêu và nguồn cùng một đoạn cha.", tag={"ch": "đủ tên, số, nguồn"}, tone={"ch": "ok"}),
               S("Trả lời", "Đúng và có nguồn", "“Chỉ tiêu dự kiến 100. Nguồn: mục 4.1, trang PDF 13.”", on=["a"], go=["e3"], msg="đoạn đủ ý", tone={"a": "ok"}, tag={"a": "kiểm chứng được"})])
    return spec("Rác vào, rác ra trên trang 13", 730, 118, nodes, edges, [dirty, clean])


def fl_parent_child():
    nodes = [N("q", 10, 34, 130, 76, ["Câu hỏi", "“Sư phạm Toán", "chỉ tiêu?”"]),
             N("c", 180, 34, 170, 76, ["Đoạn con khớp"], "brand"),
             N("p", 390, 34, 170, 76, ["Đoạn đưa cho LLM"]),
             N("a", 600, 34, 130, 76, ["Câu trả lời"], "ok")]
    edges = [E("e1", "q", "c"), E("e2", "c", "p"), E("e3", "p", "a")]
    small = C("General, đoạn nhỏ", "Cắt theo <code>\\n\\n</code>: khớp đoạn nào thì LLM nhận đúng đoạn đó.",
              [S("Câu hỏi", "Câu hỏi đi tìm", on=["q"]),
               S("Khớp", "Đoạn có chữ chỉ tiêu", on=["c"], go=["e1"], msg="Sư phạm Toán chỉ tiêu?", code="- Trình độ: Đại học.\n- Chỉ tiêu dự kiến: 115.\n- Tổ hợp được liệt kê: A00;A01;…", x="Đoạn này khớp tốt, nhưng dòng tên ngành đã nằm ở đoạn khác.", tag={"c": "khớp, nhưng thiếu tên"}, tone={"c": "warn"}),
               S("Đưa LLM", "LLM chỉ nhận đúng đoạn nhỏ", on=["p"], go=["e2"], msg="1 đoạn nhỏ", x="Không có tên ngành và không có ghi chú “115 là của cả dòng ngành”.", tag={"p": "thiếu điều kiện"}, tone={"p": "bad"}),
               S("Trả lời", "Dễ gán nhầm", "LLM không chắc đoạn đó là của ngành nào, và không biết chỉ tiêu được tính cho cả hai chuyên ngành.", on=["a"], go=["e3"], msg="thiếu ngữ cảnh", tone={"a": "bad"})])
    pc = C("Parent-child", "Tìm bằng đoạn con nhỏ, nhưng LLM đọc <strong>cả đoạn cha</strong> chứa nó.",
           [S("Câu hỏi", "Câu hỏi đi tìm", on=["q"]),
            S("Khớp", "Dòng tên ngành khớp chính xác", on=["c"], go=["e1"], msg="Sư phạm Toán chỉ tiêu?", code="Sư phạm Toán học - mã xét tuyển 7140209 - năm 2026", x="Đoạn con ngắn nên điểm sát câu hỏi.", tag={"c": "khớp chính xác"}, tone={"c": "ok"}),
            S("Đưa LLM", "Trả về cả đoạn cha", on=["p"], go=["e2"], msg="đoạn con → cha", tone={"p": "ok"}, tag={"p": "đủ điều kiện, nguồn"},
              code="Sư phạm Toán học - mã xét tuyển 7140209 - năm 2026\nNguồn: …, trang PDF 13, mục 4.1, dòng 8.\n- Chỉ tiêu dự kiến: 115.\n- Ghi chú: Có 02 chuyên ngành… Chỉ tiêu 115 là của dòng ngành, không chia đều."),
            S("Trả lời", "Đúng và đủ", "“Chỉ tiêu dự kiến 115 cho cả dòng ngành, gồm hai chuyên ngành. Nguồn: trang PDF 13.”", on=["a"], go=["e3"], msg="đủ ngữ cảnh", tone={"a": "ok"})])
    return spec("General và Parent-child", 740, 124, nodes, edges, [small, pc])


def fl_hai_tang():
    nodes = [N("q", 10, 34, 120, 76, ["Query Text", "câu đem đi tìm"]),
             N("kho", 170, 34, 170, 76, ["Tầng kho", "Hybrid 0,7/0,3", "Top K 6, ngưỡng tắt"], "brand"),
             N("node", 380, 34, 170, 76, ["Tầng khối", "Top K 6", "ngưỡng tắt"], "brand"),
             N("r", 590, 34, 140, 76, ["result", "đưa cho khối sau"], "ok")]
    edges = [E("e1", "q", "kho"), E("e2", "kho", "node"), E("e3", "node", "r")]
    base = C("Cấu hình của bài", "Câu hỏi: <em>so sánh Mầm non cao đẳng và đại học</em>. Mỗi tầng có Top K và ngưỡng riêng; tầng kho chạy trước.",
             [S("Vào", "Khối nhận câu hỏi", on=["q"]),
              S("Tầng kho", "Tìm theo cấu hình của kho", on=["kho"], go=["e1"], msg="Mầm non CĐ và ĐH", tag={"kho": "6 đoạn"}, x="Cấu hình đặt khi tạo kho quyết định cách tìm: Hybrid, trọng số, Top K, ngưỡng."),
              S("Tầng khối", "Lọc tiếp ở khối", on=["node"], go=["e2"], msg="6 đoạn", tag={"node": "giữ 6"}, x="Khối áp thêm Top K và ngưỡng của mình lên kết quả nhận được."),
              S("Ra", "Đầu ra result", on=["r"], go=["e3"], msg="6 đoạn", tone={"r": "ok"}, tag={"r": "đủ hai trình độ"})])
    cut = C("Tầng khối cắt còn 1", "Tầng kho vẫn tốt, nhưng Top K của khối đặt bằng 1.",
            [S("Vào", "Khối nhận câu hỏi", on=["q"]),
             S("Tầng kho", "Vẫn tìm được 6 đoạn", on=["kho"], go=["e1"], msg="Mầm non CĐ và ĐH", tag={"kho": "6 đoạn"}),
             S("Tầng khối", "Chỉ giữ 1", on=["node"], go=["e2"], msg="6 đoạn", tag={"node": "Top K 1"}, tone={"node": "warn"}),
             S("Ra", "Thiếu một vế", "Câu so sánh chỉ còn một trình độ. Log tầng khối cho thấy 1 đoạn, dù Hit Test của kho trông vẫn ổn.", on=["r"], go=["e3"], msg="1 đoạn", tone={"r": "bad"}, tag={"r": "thiếu một vế"})])
    tight = C("Tầng kho chỉ trả 1", "Top K của kho đặt bằng 1, còn khối vẫn để 6.",
              [S("Vào", "Khối nhận câu hỏi", on=["q"]),
               S("Tầng kho", "Chỉ trả 1 đoạn", on=["kho"], go=["e1"], msg="Mầm non CĐ và ĐH", tag={"kho": "Top K 1"}, tone={"kho": "warn"}),
               S("Tầng khối", "Không có gì để nới", "Khối đặt 6 nhưng chỉ nhận được 1. Vì vậy có lúc sửa ở khối mà kết quả không đổi: lỗi nằm ở tầng kho.", on=["node"], go=["e2"], msg="1 đoạn", tag={"node": "vẫn 1"}),
               S("Ra", "Thiếu một vế", on=["r"], go=["e3"], msg="1 đoạn", tone={"r": "bad"}, tag={"r": "thiếu một vế"})])
    return spec("Hai tầng lọc của truy xuất", 740, 124, nodes, edges, [base, cut, tight])


def fl_bien():
    nodes = [N("s", 10, 70, 120, 62, ["1. Start"]), N("k", 165, 70, 130, 62, ["2. Knowledge", "Retrieval"], "brand"),
             N("i", 330, 70, 100, 62, ["3. IF/ELSE"]), N("l", 470, 10, 110, 62, ["4. LLM"], "brand"),
             N("a1", 620, 10, 120, 62, ["5. Answer", "có nguồn"], "ok"), N("a2", 470, 132, 270, 62, ["6. Answer", "báo chưa đủ thông tin"], "ok")]
    edges = [E("e1", "s", "k"), E("e2", "k", "i"), E("e3", "i", "l", lb="IF"), E("e4", "l", "a1"), E("e5", "i", "a2", lb="ELSE")]
    yes = C("Có đoạn trả về", "Mỗi khối đọc biến của khối trước và tạo biến mới. Theo dõi gói dữ liệu trên mũi tên: đó chính là thứ bạn chọn bằng trình chọn biến.",
            [S("Start", "Tạo sys.query", on=["s"], tag={"s": "sys.query"}, code="sys.query = \"Phương thức 100 có cộng điểm chứng chỉ ngoại ngữ không?\""),
             S("Tìm", "Query Text đọc sys.query, tạo result", on=["k"], go=["e1"], msg="sys.query", tag={"k": "result: 6 đoạn"}),
             S("Rẽ nhánh", "Đọc result, không đọc nội dung", on=["i"], go=["e2"], msg="result", tag={"i": "is not empty"}),
             S("LLM", "Context đọc result, User đọc sys.query, tạo text", on=["l"], go=["e3"], msg="result + sys.query", tag={"l": "text"}),
             S("Answer", "Nội dung là biến text", on=["a1"], go=["e4"], msg="text", tone={"a1": "ok"})])
    no = C("result rỗng", "Bật ngưỡng 0,99 để ép kết quả rỗng khi kiểm thử.",
           [S("Start", "Tạo sys.query", on=["s"], tag={"s": "sys.query"}),
            S("Tìm", "Không đoạn nào vượt ngưỡng", on=["k"], go=["e1"], msg="sys.query", tag={"k": "result: rỗng"}, tone={"k": "warn"}),
            S("Rẽ nhánh", "Mảng rỗng, đi ELSE", on=["i"], go=["e2"], msg="[ ]", tag={"i": "ELSE"}),
            S("Answer cố định", "Khối 4 không chạy", "Không gọi mô hình nên không tốn lượt; nội dung là câu cố định bạn đã dán.", on=["a2"], go=["e5"], msg="câu cố định", tone={"a2": "ok"})])
    miss = C("Quên gán Context", "Lỗi hay gặp nhất: prompt đẹp nhưng biến Context trống.",
             [S("Start", "Tạo sys.query", on=["s"], tag={"s": "sys.query"}),
              S("Tìm", "Vẫn tìm đúng", on=["k"], go=["e1"], msg="sys.query", tag={"k": "result: 6 đoạn"}, tone={"k": "ok"}),
              S("Rẽ nhánh", "Vẫn đi IF", on=["i"], go=["e2"], msg="result"),
              S("LLM", "result không được đưa vào", "Mũi tên chỉ đưa sys.query sang, Context trống. Log vẫn báo thành công. Mở prompt thực tế mới thấy phần NGỮ CẢNH rỗng.", on=["l"], go=["e3"], msg="chỉ có sys.query", tag={"l": "Context trống"}, tone={"l": "bad"}),
              S("Answer", "Từ chối oan hoặc nói chung chung", on=["a1"], go=["e4"], msg="text", tone={"a1": "bad"})])
    return spec("Biến đi qua sáu khối", 750, 204, nodes, edges, [yes, no, miss])


def fl_rewrite():
    nodes = [N("h", 10, 4, 180, 52, ["Lịch sử chat", "Mầm non cao đẳng: dự kiến 100"]),
             N("q", 10, 92, 150, 62, ["Câu mới", "“Còn đại học thì sao?”"]),
             N("rw", 200, 92, 140, 62, ["Viết lại câu hỏi", "(LLM)"], "brand"),
             N("k", 380, 92, 130, 62, ["Tìm tài liệu"], "brand"), N("a", 550, 92, 180, 62, ["Câu trả lời"], "ok")]
    edges = [E("e0", "h", "rw", d="M190,30 H270 V90"), E("e1", "q", "rw"), E("e2", "rw", "k"), E("e3", "k", "a")]
    off = C("Chưa viết lại", "Bản sáu khối gốc: đem nguyên câu đi tìm.",
            [S("Câu mới", "Câu thiếu chủ ngữ", on=["q"]),
             S("Đi thẳng", "Không ai đọc lịch sử", "Khối viết lại chưa có, câu đi nguyên trạng.", on=["rw"], go=["e1"], msg="Còn đại học thì sao?", set={"rw": ["(chưa có khối này)"]}, tone={"rw": "warn"}),
             S("Tìm", "Hàng loạt đoạn “Trình độ: Đại học”", "Không còn biết đang nói ngành nào, các đoạn có điểm gần bằng nhau.", on=["k"], go=["e2"], msg="Còn đại học thì sao?", tag={"k": "lạc đề"}, tone={"k": "bad"}),
             S("Trả lời", "Hỏi ngược hoặc trả lời sai ngành", on=["a"], go=["e3"], msg="đoạn lạc đề", tone={"a": "bad"})])
    on = C("Có khối viết lại", "Thêm một khối LLM chạy trước bước tìm, bật Memory để đọc lịch sử.",
           [S("Câu mới", "Câu thiếu chủ ngữ", on=["q", "h"]),
            S("Viết lại", "Thay “còn … thì sao” bằng nội dung cụ thể", on=["rw"], go=["e0", "e1"], msg={"e0": "lịch sử", "e1": "câu mới"}, tag={"rw": "chỉ trả câu hỏi"},
              code="Chỉ tiêu dự kiến của Giáo dục Mầm non trình độ đại học là bao nhiêu?"),
            S("Tìm", "Tìm bằng câu đủ nghĩa", "Đầu ra text của khối viết lại là Query Text của khối tìm. Thêm lời giải thích vào đầu ra thì lời giải thích cũng bị đem đi tìm.", on=["k"], go=["e2"], msg="text", tag={"k": "mã 7140201 đứng đầu"}, tone={"k": "ok"}),
            S("Trả lời", "Đúng mạch hội thoại", "“Mầm non đại học (mã 7140201) có chỉ tiêu dự kiến 450. Nguồn: trang PDF 13.”", on=["a"], go=["e3"], msg="đoạn đúng", tone={"a": "ok"})])
    return spec("Viết lại câu hỏi nối tiếp", 745, 166, nodes, edges, [off, on])


def fl_loi_ba_tang():
    nodes = [N("d", 10, 34, 150, 66, ["Tầng dữ liệu", "tài liệu, cắt đoạn"]), N("r", 210, 34, 150, 66, ["Tầng truy xuất", "tìm, Top K, ngưỡng"], "brand"),
             N("g", 410, 34, 150, 66, ["Tầng sinh", "prompt, Context"], "brand"), N("a", 610, 34, 120, 66, ["Câu trả lời"], "ok")]
    edges = [E("e1", "d", "r"), E("e2", "r", "g"), E("e3", "g", "a")]

    def ca(name, intro, tang, tag, x_tang, x_sua):
        steps, go = [], {"d": ["e1"], "r": ["e1"], "g": ["e1", "e2"]}[tang]
        order = ["d", "r", "g"]
        for t in order[:order.index(tang)]:
            steps.append(S({"d": "Dữ liệu", "r": "Truy xuất", "g": "Sinh"}[t], "Tầng này ổn", on=[t], tone={t: "ok"}))
        steps.append(S("Lỗi ở đây", tag, x_tang, on=[tang], go=[go[-1]] if tang != "d" else [], tone={tang: "bad"}, tag={tang: tag}))
        steps.append(S("Cách sửa", "Sửa đúng tầng này", x_sua, on=[tang, "a"], tone={tang: "ok"}))
        return C(name, intro, steps)

    return spec("Năm kiểu lỗi RAG nằm ở ba tầng", 745, 112, nodes, edges, [
        ca("Tài liệu không có", "Hỏi học phí, bộ mẫu chưa có.", "d", "chưa có trang học phí", "Không đoạn nào chứa câu trả lời. Agent phải nói “chưa có”, không được bịa.", "Muốn trả lời được thì xử lý thêm trang học phí, đối chiếu rồi nạp."),
        ca("Có nhưng không tìm thấy", "Tài liệu ghi “quy đổi”, người hỏi “chứng chỉ đổi ra điểm”.", "r", "đoạn đúng không lên", "Dữ liệu có, nhưng đoạn đúng không nằm trong kết quả.", "Hybrid, viết lại câu hỏi, thêm FAQ bằng lời người dùng."),
        ca("Tìm thấy đoạn sai", "Hỏi Mầm non đại học, bốc Mầm non cao đẳng.", "d", "hai đoạn quá giống nhau", "Đoạn không ghi rõ trình độ nên điểm hai đoạn gần bằng nhau.", "Làm sạch, cắt theo đề mục, ghi rõ trình độ trong đoạn."),
        ca("Tìm đúng, trả lời sai", "Đoạn ghi dự kiến 115, Agent trả lời “mỗi chuyên ngành 115”.", "g", "suy diễn từ đoạn đúng", "Đoạn đúng đã nằm trong prompt, nhưng LLM diễn giải sai.", "Siết prompt, thêm nguyên tắc riêng, giảm temperature. Đổi Top K không có tác dụng."),
        ca("Tài liệu lỗi thời", "Trả lời theo thông báo đã có bản bổ sung.", "d", "bản cũ còn trong kho", "Tìm đúng và trả lời đúng theo bản cũ, nên log không báo gì.", "Gỡ bản cũ, gắn ngày hiệu lực, giao người bảo trì kho."),
    ])
