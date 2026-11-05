"""Phòng thí nghiệm mini và bảng tham số Dify của Buổi 2 khóa AI Agent (dùng trong tools/ai_agent_course.py).

PARAMS là nguồn duy nhất cho giải thích tham số: cùng một nội dung sinh ra bảng trong bài (bang_tham_so) và nút “?” trong lab mini
(component DifyLab, app/static/difylab.js). Tên tham số theo giao diện tiếng Anh của Dify; giá trị “Bài này đặt” phải khớp cấu hình trong bài
và tệp DSL. Điều kiện nhiệm vụ (when) đọc trạng thái lab; test trong tests/test_courses.py kiểm tra đường dẫn hợp lệ.
"""

# khóa: (tên, để làm gì, bài này đặt, đổi thì sao, nối với kiến thức)
PARAMS = {
    # ---------------------------------------------------------------- kết nối mô hình
    "auth": ("Authorization Name", "Tên gợi nhớ của khóa, phân biệt khi workspace có nhiều khóa.", "<code>OpenAI tuyển sinh</code>",
             "Chỉ đổi tên hiển thị, không ảnh hưởng kết quả.", ""),
    "apikey": ("API Key", "Khóa để Dify gọi mô hình thay bạn; mọi lượt chạy tính vào tài khoản của khóa này.", "Khóa của bạn, nhập trực tiếp vào ô",
               "Sai hoặc hết hạn thì danh sách mô hình không hiện. Mọi thành viên workspace đều dùng được khóa đã lưu.",
               "Chi phí token ở chặng 1: mỗi lần lập chỉ mục và mỗi câu chat đều tốn tiền trên khóa này."),
    "apibase": ("API Base", "Đổi địa chỉ máy chủ khi đi qua cổng trung gian hoặc dịch vụ tương thích OpenAI.", "Giữ mặc định",
                "Sai địa chỉ thì mọi lời gọi báo lỗi kết nối.", ""),
    "defemb": ("Default Models → Embedding Model", "Mô hình đổi chữ thành vector, mặc định cho cả workspace.", "<code>text-embedding-3-large</code>",
               "Để trống dễ gặp lỗi <code>Default model not found for text-embedding</code>. Đổi mô hình sau khi nạp thì phải lập chỉ mục lại kho.",
               "Câu hỏi và tài liệu phải dùng cùng một mô hình embedding, nếu không vector không so được với nhau."),
    "defchat": ("Default Models → System Inference Model", "Mô hình chat mặc định cho các việc phụ của hệ thống, như sinh câu hỏi gợi ý.", "Mô hình chat đang có",
                "Không thay cho mô hình bạn chọn trong khối LLM.", ""),
    "defrerank": ("Default Models → Rerank Model", "Mô hình xếp hạng lại mặc định.", "Để trống trong bài này",
                  "Cần kết nối nhà cung cấp có mô hình rerank; mỗi lần dùng tốn thêm chi phí.", "Rerank ở chặng 4."),

    # ---------------------------------------------------------------- cắt đoạn
    "mode": ("Chunk Settings (General / Parent-child)", "<strong>General</strong>: một loại đoạn, khớp đoạn nào trả đoạn đó. <strong>Parent-child</strong>: tìm bằng đoạn con, trả về đoạn cha chứa nó.",
             "Parent-child", "Chế độ không đổi được sau khi tạo kho, các thông số còn lại thì đổi được. Parent-child chỉ chạy với High Quality.",
             "Đoạn nhỏ tìm chính xác, đoạn lớn đủ ngữ cảnh: Parent-child lấy cả hai ưu điểm."),
    "parentMode": ("Parent-chunk for Context (Paragraph / Full Doc)", "<strong>Paragraph</strong>: cắt tài liệu thành nhiều đoạn cha. <strong>Full Doc</strong>: cả tài liệu là một đoạn cha, chỉ xử lý 10.000 token đầu.",
                   "Paragraph", "Full Doc khiến mỗi câu hỏi kéo cả tài liệu vào prompt: tốn token và dễ “lost in the middle”.", "Context Window ở chặng 1."),
    "pdelim": ("Parent Delimiter (Parent-chunk for Context → Delimiter)", "Chuỗi đánh dấu chỗ được phép cắt đoạn cha; chuỗi này bị bỏ khỏi đoạn sau khi cắt.", "<code>\\n## </code> (có khoảng trắng cuối)",
               "Bộ SPD có dòng trống ngay sau đề mục, nên <code>\\n\\n</code> tách tên ngành khỏi số liệu.", "Cắt theo cấu trúc của chính tài liệu, không dùng một giá trị cho mọi file."),
    "pmax": ("Maximum Parent Length (Parent-chunk for Context → Maximum chunk length)", "Độ dài tối đa của đoạn cha, tính bằng ký tự. Vượt mức thì bị cắt cứng, bất kể dấu phân cách.", "3000 ký tự",
             "Quá nhỏ: đoạn cha bị cắt giữa chừng, mất điều kiện. Quá lớn: mỗi đoạn cha chở nhiều chữ thừa vào prompt.", "Chunk size và mục tiêu “mỗi đoạn trọn ý”."),
    "cdelim": ("Child Delimiter (Child-chunk for Retrieval → Delimiter)", "Chuỗi cắt đoạn cha thành đoạn con để tìm kiếm.", "<code>\\n</code> (mỗi dòng)",
               "Dùng <code>\\n\\n</code> thì mỗi đoạn con quá lớn, tìm kém chính xác.", "Đoạn nhỏ cho điểm tương đồng sát câu hỏi hơn."),
    "cmax": ("Maximum Child Length (Child-chunk for Retrieval → Maximum chunk length)", "Độ dài tối đa của đoạn con.", "512 ký tự", "Quá nhỏ thì một dòng dài bị cắt đôi; đoạn quá ngắn cho điểm thiếu ổn định.", ""),
    "delim": ("Delimiter (General)", "Chuỗi đánh dấu chỗ được phép cắt đoạn ở chế độ General.", "Bài này không dùng General",
              "<code>\\n\\n</code> hợp tài liệu mà mỗi mục là một khối liền, như sổ tay đã làm sạch.", "Chiến lược cắt theo cấu trúc."),
    "gmax": ("Maximum Chunk Length (General)", "Độ dài tối đa của đoạn, tính bằng ký tự. Vượt mức thì bị cắt cứng.", "Bài này không dùng General",
             "Gợi ý xuất phát: 500–800 ký tự với sổ tay ngắn.", "Đoạn to hay đoạn nhỏ."),
    "overlap": ("Chunk Overlap", "Số ký tự hai đoạn liền nhau dùng chung, để không mất ý nằm vắt ngang điểm cắt.", "Parent-child không cần",
                "Trên Dify, overlap chỉ có tác dụng khi một đoạn bị cắt cứng vì vượt độ dài. Đoạn đã tách đúng theo dấu phân cách thì không gối nhau.",
                "Chunk overlap thường gối 15–20% khi cắt theo độ dài cố định."),
    "ws": ("Replace consecutive spaces, newlines and tabs", "Gom khoảng trắng và dòng trống liên tiếp.", "Tắt",
           "Bộ mẫu đã sạch nên không cần; với bản chép từ PDF thì có ích.", "Loại bỏ nhiễu (GIGO)."),
    "url": ("Delete all URLs and email addresses", "Xóa đường dẫn và email khỏi đoạn.", "Tắt: giữ website và email liên hệ của trường",
            "Bật lên thì chatbot không còn chỉ được nơi kiểm tra.", "Làm sạch quá tay cũng làm mất dữ liệu."),
    "summary": ("Summary Auto-Gen", "Tự sinh tóm tắt cho đoạn để hỗ trợ tìm kiếm.", "Tắt", "Bật thì tốn thêm token khi lập chỉ mục.", ""),

    # ---------------------------------------------------------------- lập chỉ mục, tìm kiếm
    "index": ("Index Method", "<strong>High Quality</strong>: dùng embedding, tìm được theo nghĩa. <strong>Economical</strong>: không tốn token, mỗi đoạn 10 từ khóa, chỉ tìm theo từ khóa.",
              "High Quality", "Đã chọn High Quality thì không về Economical được. Parent-child không chạy với Economical.", "Embedding ở chặng 3."),
    "emb": ("Embedding Model", "Mô hình đổi đoạn và câu hỏi thành vector.", "<code>text-embedding-3-large</code>", "Đổi mô hình thì phải nạp lại toàn bộ kho.", "Chọn mô hình embedding, chặng 3."),
    "method": ("Retrieval Method", "<strong>Vector Search</strong> theo nghĩa, <strong>Full-Text Search</strong> theo từ khóa, <strong>Hybrid Search</strong> kết hợp cả hai.",
               "Hybrid Search", "Bộ này có cả câu hỏi đời thường lẫn mã như X70, nên một kiểu tìm đơn lẻ sẽ hụt một trong hai.", "Ba kiểu tìm kiếm."),
    "weight": ("Weight Settings: Semantic / Keyword", "Tỉ trọng giữa điểm theo nghĩa và điểm từ khóa khi Hybrid. Semantic bằng 1 là chỉ theo nghĩa, Keyword bằng 1 là chỉ theo từ khóa.",
               "0.7 / 0.3", "Tăng Keyword khi người dùng hay hỏi mã số; tăng Semantic khi họ hay diễn đạt khác tài liệu.", "BM25 và cosine."),
    "rerank": ("Rerank Model", "Mô hình đọc cùng lúc câu hỏi và từng đoạn để chấm lại, chính xác hơn nhưng chậm và tốn thêm.", "Tắt",
               "Bật khi Hit Test cho thấy đoạn đúng có mặt nhưng bị xếp thấp.", "Truy xuất hai tầng: tìm nhanh rồi xếp hạng kỹ."),
    "topk": ("Top K", "Số đoạn tối đa trả về. Dify mặc định 3.", "6",
             "Ít quá thì thiếu ý: câu so sánh hai trình độ cần ít nhất 2 đoạn. Nhiều quá thì tốn token và thêm nhiễu.", "Khuyến nghị chung 3–5; bài này đặt 6 vì có câu so sánh và các đoạn tổ hợp rất giống nhau."),
    "th": ("Score Threshold", "Điểm tối thiểu để giữ một đoạn. Dify mặc định 0,5 khi bật.", "Tắt",
           "Cao quá thì từ chối oan. Trên bộ này đoạn đúng 0,453 thấp hơn đoạn sai 0,491, nên không mức nào tách được hai trường hợp.", "Điểm tìm kiếm không phải xác suất câu trả lời đúng."),

    # ---------------------------------------------------------------- khối 1
    "inputs": ("Input Field", "Ô nhập do bạn thêm, người dùng điền trước khi chat. Mỗi ô thành một biến cho các khối sau.", "Để trống",
               "Thêm ô Select “ngành” thì lọc được theo ngành, nhưng người dùng phải điền form trước khi hỏi.", "Biến là cách dữ liệu đi giữa các khối."),
    "addfield": ("Thêm một ô nhập", "Có các loại Short Text, Paragraph, Select, Number, Checkbox, tệp. Mỗi ô có Label Name và Required.", "Không thêm",
                 "Ô bắt buộc mà người dùng không điền thì chưa chat được.", ""),
    "sysq": ("sys.query (bản mới ghi userinput.query)", "Biến có sẵn của Chatflow: câu người dùng vừa gõ.", "Dùng biến có sẵn",
             "Không cần tạo ô câu hỏi riêng. Tên biến khác nhau tùy phiên bản Dify, nên hãy chọn bằng trình chọn biến thay vì gõ tay.", ""),

    # ---------------------------------------------------------------- khối 2
    "kq": ("Query Text", "Biến chứa câu đem đi tìm.", "<code>sys.query</code>; từ chặng 6 đổi sang câu đã viết lại",
           "Chọn sai hoặc để trống thì khối không có gì để tìm. Câu nối tiếp mà không viết lại thì tìm sẽ lạc.", "R trong RAG: truy xuất bằng câu đủ nghĩa."),
    "kkb": ("Knowledge", "Kho được tìm; thêm được nhiều kho.", "Kho SPD vừa tạo",
            "Quên thêm kho thì result luôn rỗng. Nhập tệp DSL sang máy khác phải chọn lại kho.", "Phân quyền: chỉ đưa vào kho điều mọi người dùng được đọc."),
    "kmeta": ("Metadata Filtering", "Lọc theo thông tin của tài liệu trước khi trả kết quả. Mặc định tắt.", "Disabled",
              "Lọc sai thì đoạn đúng bị loại dù điểm cao.", "Metadata: lọc trước, tìm sau."),
    "krerank": ("Rerank Settings", "Cách gộp và chấm lại ở cấp khối: <strong>Weighted Score</strong> hoặc <strong>Rerank Model</strong>.", "Tắt rerank tại khối",
                "Một kho duy nhất thì kho đã tự chấm, chưa cần chấm lại lần hai.", "Rerank."),
    "ktop": ("Top K (khối)", "Số đoạn tối đa khối giữ lại, lấy từ những gì tầng kho đã trả.", "6",
             "Node chỉ cắt bớt, không nới được: kho trả 3 thì đặt khối 6 vẫn chỉ có 3.", "Top-K."),
    "kth": ("Score Threshold (khối)", "Bỏ đoạn dưới mức này, sau khi tầng kho đã lọc.", "Tắt",
            "Bật 0,99 để ép kết quả rỗng khi kiểm thử nhánh ELSE, xong nhớ tắt.", "Ngưỡng."),

    # ---------------------------------------------------------------- khối 3
    "ifvar": ("Biến kiểm tra", "Biến đem ra so sánh, chọn từ đầu ra của khối trước.", "<code>Tìm tài liệu SPD 2026 → result</code>",
              "Chọn nhầm biến thì mọi câu đi cùng một nhánh.", ""),
    "ifop": ("Toán tử", "Phép so sánh. Biến kiểu chữ có contains, is, starts with…; số có lớn hơn, nhỏ hơn; mảng như <code>result</code> dùng is empty, is not empty.", "<code>is not empty</code>",
             "Đảo thành <code>is empty</code> thì câu có tài liệu lại nhận câu từ chối.", "Có đoạn trả về không có nghĩa là đủ bằng chứng."),
    "iflogic": ("AND / OR", "Cách gộp khi có nhiều điều kiện.", "Một điều kiện", "AND cần tất cả đúng, OR cần một điều kiện đúng.", ""),
    "ifelif": ("ELIF", "Thêm nhánh kiểm tra tiếp khi IF sai, trước khi rơi xuống ELSE.", "Không dùng", "Dùng khi cần nhiều đường đi, ví dụ mỗi nhóm câu hỏi một kho.", "Mẫu rẽ nhánh của Prompt Chain."),

    # ---------------------------------------------------------------- khối 4
    "model": ("Model", "Mô hình sinh câu trả lời.", "OpenAI gpt-4.1, hoặc mô hình chat bạn có", "Mô hình đắt hơn không sửa được lỗi truy xuất.", "Sửa đúng tầng, chặng 7."),
    "temp": ("Temperature", "Độ ngẫu nhiên khi chọn chữ tiếp theo, thường từ 0 đến 1.", "0.1",
             "Cao thì câu chữ đa dạng hơn và mỗi lần một khác. Thấp giúp ổn định cách viết, không bảo đảm đúng.", "LLM chọn chữ theo xác suất, nên ổn định khác với chính xác."),
    "topp": ("Top P", "Chỉ chọn trong nhóm chữ có tổng xác suất đạt P.", "Giữ mặc định", "Thường chỉnh Temperature hoặc Top P, không chỉnh cả hai.", ""),
    "penalty": ("Frequency / Presence Penalty", "Giảm lặp từ, khuyến khích nói ý mới.", "Giữ mặc định", "Tăng cao có thể làm câu lệch khỏi thuật ngữ trong tài liệu.", ""),
    "maxt": ("Max Tokens", "Giới hạn độ dài câu trả lời.", "1400", "Thấp quá thì câu bị cắt giữa chừng, thường mất luôn dòng Nguồn ở cuối.", "Token và chi phí."),
    "ctx": ("Context", "Nhận đoạn tìm được để điền vào biến Context trong prompt.", "<code>Tìm tài liệu SPD 2026 → result</code>",
            "Không gán thì LLM không thấy tài liệu, dù khối 2 tìm đúng. Đây là lỗi hay gặp nhất.", "A trong RAG: tăng cường prompt bằng dữ liệu."),
    "sys": ("System Prompt", "Luật làm việc của mô hình, kèm biến Context.", "9 nguyên tắc và phần Cách trả lời",
            "Bỏ luật nào thì lỗi tương ứng xuất hiện; thử ngay trong lab.", "7 yếu tố của prompt hỏi đáp tài liệu."),
    "user": ("User Prompt", "Tin nhắn người dùng gửi mô hình, thường chỉ là biến câu hỏi.", "<code>{{#sys.query#}}</code>",
             "Để trống thì LLM có tài liệu nhưng không có câu hỏi.", ""),
    "mem": ("Memory", "Cho khối đọc lại lịch sử chat. Bật riêng cho từng khối, chỉ có ở Chatflow.", "Tắt ở khối 4",
            "Bật ở khối này chỉ giúp LLM hiểu mạch chuyện, không giúp khối 2 tìm đúng hơn.", "Query Rewrite ở chặng 6."),
    "vision": ("Vision", "Cho mô hình đọc ảnh đính kèm hoặc ảnh tìm được.", "Tắt", "Chỉ bật khi mô hình hỗ trợ; tốn thêm token.", ""),
    "structured": ("Structured Output", "Ép đầu ra theo cấu trúc JSON.", "Tắt", "Hợp với đầu ra trung gian cho khối sau đọc, không cần cho câu trả lời gửi người dùng.", "Thiết kế đầu ra trung gian, chặng 6."),
    "retry": ("Retry / Error Handling", "Thử lại khi lỗi, đổi nhánh hoặc dùng giá trị mặc định.", "Mặc định", "Nên cấu hình trước khi dùng thật, để lỗi mạng không thành màn hình trắng.", ""),

    # ---------------------------------------------------------------- khối 5, 6
    "acontent": ("Nội dung Answer", "Trộn chữ cố định và biến của các khối trước.", "Khối 5: <code>Tư vấn theo nguồn → text</code>. Khối 6: câu cố định",
                 "Dán cố định vào khối 5 thì mọi câu hỏi đều nhận một câu trả lời.", "G trong RAG: kết quả cuối người dùng nhìn thấy."),
    "astream": ("Thứ tự trong nội dung", "Answer phát dần đến biến đầu tiên chưa có giá trị rồi chờ. Thứ tự biến trong ô quyết định, không phải thứ tự chạy của các khối.", "Chỉ một biến",
                "Đặt chữ cố định trước biến thì người dùng thấy phản hồi ngay.", ""),
    "cite": ("Citation and Attributions", "Hiện danh sách tài liệu đã dùng dưới câu trả lời. Bật trong Features.", "Bật",
             "Danh sách chỉ cho biết tài liệu nào đã dùng, không chứng minh tài liệu đó hỗ trợ kết luận.", "Trích dẫn nguồn."),

    # ---------------------------------------------------------------- chặng 6
    "opener": ("Conversation Opener", "Lời chào và câu hỏi gợi ý trên trang chat.", "Lời chào và 3 câu gợi ý", "Lời chào nên nói rõ phạm vi để người dùng biết hỏi gì.", ""),
    "followup": ("Follow-up", "Tự gợi ý câu hỏi tiếp theo sau mỗi câu trả lời.", "Tắt", "Bật thì tốn thêm một lượt gọi mô hình, và câu gợi ý có thể nằm ngoài tài liệu.", ""),
    "moderation": ("Content Moderation", "Lọc nội dung đầu vào và đầu ra.", "Tắt", "Nên cân nhắc trước khi mở cho công chúng.", ""),
    "rwon": ("Khối LLM: Viết lại câu hỏi", "Biến câu nối tiếp thành câu đứng được một mình trước khi tìm.", "Thêm giữa khối 1 và khối 2", "Tốn thêm một lượt gọi mô hình cho mỗi câu.", "Prompt Chain: đầu ra bước trước là đầu vào bước sau."),
    "rwmem": ("Memory của khối viết lại", "Đưa lịch sử chat vào khối này.", "Bật", "Tắt thì khối không biết “còn đại học” đang nói về ngành nào.", "Đầu ra chỉ có câu hỏi, không kèm giải thích."),
    "rwwin": ("Window Size", "Số tin nhắn gần nhất được đưa vào.", "Giữ mặc định", "Bằng 0 thì như không có Memory; lớn quá thì tốn token và dễ kéo chủ đề cũ vào.", "Context Window."),
}


def _doc(key):
    n, a, v, c, k = PARAMS[key]
    return {"n": n, "a": a, "v": v, "c": c, "k": k}


def rows(*keys):
    """Dòng của bảng tham số trong bài: Tham số | Để làm gì | Bài này đặt | Đổi thì sao | Nối với kiến thức."""
    head = ["Tham số", "Để làm gì", "Bài này đặt", "Đổi thì sao", "Nối với kiến thức"]
    return [head] + [[f"<strong>{PARAMS[k][0]}</strong>", PARAMS[k][1], PARAMS[k][2], PARAMS[k][3], PARAMS[k][4] or "–"] for k in keys]


def M(t, when, why):
    return {"t": t, "when": when, "why": why}


def lab(kind, title, intro, docs=(), missions=(), caption=None, **extra):
    spec = {"lab": kind, "title": title, "intro": intro, "docs": {k: _doc(k) for k in docs}, "missions": list(missions)}
    spec.update(extra)
    return {"t": "widget", "name": "difylab", "spec": spec, "caption": caption, "plain": title}


Q_HIT = ["q3", "q1", "q2", "q4", "q5", "q6", "q11", "q12"]


def lab_context():
    return lab("context", "Nhồi cả tài liệu hay dùng RAG?",
               "Kéo số tài liệu lên để xem chuyện gì xảy ra khi đơn vị của bạn có cả kho văn bản chứ không chỉ một thông báo.")


def lab_clean():
    return lab("clean", "Làm sạch trang 13 của bản thô",
               "Đây là chữ thật trích từ trang 13 của PDF. Bật từng thao tác, nhìn ô cuối bên trái: tên ngành, chỉ tiêu và phương thức đã đứng cùng một dòng chưa?")


def lab_spot():
    return lab("spot", "Bắt lỗi AI khi chép số liệu",
               "Khối dưới đây chứa những lỗi AI thật sự hay mắc khi làm sạch bảng này. Đối chiếu với bản gốc rồi bấm vào chỗ sai.")


def lab_cosine():
    return lab("cosine", "Cosine bằng con số",
               "Kéo ba thanh để đổi nghĩa của câu hỏi, hoặc bấm câu mẫu. Thứ tự các đoạn đổi theo độ gần.")


def lab_chunk():
    return lab("chunk", "Cắt đoạn bốn file SPD",
               "Đây là bốn file bạn sắp nạp, được cắt thật theo cách Dify cắt. Cấu hình chuẩn của bài ra <strong>72 đoạn cha, 474 đoạn con</strong>, đúng bằng số trong log lần chạy thật trên Dify. "
               "Bấm <strong>?</strong> cạnh mỗi tham số để đọc giải thích.",
               docs=("mode", "parentMode", "pdelim", "pmax", "cdelim", "cmax", "delim", "gmax", "overlap", "ws", "url"),
               missions=[
                   M("Đổi <strong>Parent Delimiter</strong> sang <code>\\n\\n</code>. Ô “số liệu mất tên ngành” đổi thế nào?",
                     {"cs.mode": "parent", "cs.pdelim": "\\n\\n", "out.orphan": {"gt": 0}},
                     "12 đoạn cha chỉ còn số liệu, không biết của ngành nào, vì bộ mẫu có dòng trống ngay sau đề mục. Mở Hồ sơ 12 ngành để thấy. Đây là lý do chọn dấu phân cách theo cấu trúc tài liệu."),
                   M("Đưa Parent Delimiter về <code>\\n## </code>, rồi kéo <strong>Maximum Parent Length</strong> xuống dưới 300.",
                     {"cs.pdelim": "\\n## ", "cs.pmax": {"lt": 300}, "out.forced": {"gt": 0}},
                     "Đoạn vượt độ dài bị cắt cứng bất kể dấu phân cách: dòng Lưu ý và Ghi chú có thể tách khỏi tên ngành."),
                   M("Chuyển sang <strong>General</strong>, kéo <strong>Chunk Overlap</strong> lên 150. Số đoạn có đổi không?",
                     {"cs.mode": "general", "cs.overlap": {"gt": 140}},
                     "Không đổi, vì overlap chỉ có tác dụng khi một đoạn bị cắt cứng. Giờ kéo Maximum Chunk Length xuống 150: số đoạn tăng và các đoạn bắt đầu gối lên nhau."),
                   M("Bật <strong>Xóa URL và email</strong>, mở tệp Thông tin chung.", {"cs.url": True},
                     "Website và email tuyển sinh biến mất, nên chatbot không còn chỉ được nơi kiểm tra. Làm sạch quá tay cũng làm mất dữ liệu."),
               ])


def lab_retrieval():
    return lab("retrieval", "Hit Test ngay trong bài",
               "Tìm trên đúng 72 đoạn cha vừa cắt. Phần từ khóa tính thật; phần “theo nghĩa” là mô phỏng vì trình duyệt không có embedding, và thang điểm được chỉnh để câu đã chạy thật khớp log Dify ở cấu hình chuẩn. "
               "Dùng lab để hiểu xu hướng, còn con số phải đo bằng Retrieval Testing trên kho của bạn.",
               docs=("index", "method", "weight", "rerank", "topk", "th"), qs=Q_HIT, custom=True,
               missions=[
                   M("Chọn câu <strong>Tổ hợp X70</strong>, đổi sang <strong>Vector Search</strong>. Đoạn X70 có còn đứng đầu không?",
                     {"q": "q4", "rs.method": "vector", "out.topHit": False},
                     "Mã số gần như không mang nghĩa: hàng chục đoạn “tổ hợp” có điểm gần bằng nhau, đoạn X70 bị đẩy xuống. Tìm theo nghĩa yếu đúng ở chỗ này."),
                   M("Chọn câu <strong>IELTS thêm điểm</strong>, đổi sang <strong>Full-Text Search</strong>, xem điểm so với Vector.",
                     {"q": "q12", "rs.method": "full"},
                     "Điểm tụt mạnh: câu hỏi nói “IELTS, thêm điểm”, tài liệu ghi “chứng chỉ, quy đổi”. Mỗi kiểu tìm có điểm mù riêng, nên bài này dùng Hybrid."),
                   M("Về Hybrid, bật <strong>Score Threshold 0,47</strong>, chọn câu <strong>X70 có PT 200, Mầm non?</strong> Còn đoạn nào không?",
                     {"q": "q6", "rs.thEn": True, "rs.method": "hybrid", "out.count": 0},
                     "Đoạn đúng chỉ được 0,453 nên bị loại: chatbot từ chối oan."),
                   M("Giữ ngưỡng 0,47, chọn câu <strong>Thích cây cối</strong>. Có đoạn nào lọt không?",
                     {"q": "q11", "rs.thEn": True, "rs.th": {"lt": .49}, "rs.method": "hybrid", "out.count": {"gt": 0}},
                     "Đoạn không liên quan được 0,491 và vẫn lọt. Đoạn sai điểm cao hơn đoạn đúng, nên không mức ngưỡng nào tách được. Vì vậy bản demo tắt ngưỡng và giao việc đánh giá bằng chứng cho LLM."),
                   M("Tắt ngưỡng, chọn câu <strong>Học phí</strong>. Có đoạn trả về không, điểm bao nhiêu?",
                     {"q": "q5", "rs.thEn": False, "out.count": {"gt": 0}},
                     "Vẫn đủ 6 đoạn, dù bộ mẫu không có học phí. Có đoạn trả về không có nghĩa là có bằng chứng; điểm cũng không phải xác suất đúng."),
                   M("Chọn câu <strong>Mầm non CĐ và ĐH</strong>, kéo <strong>Top K</strong> xuống 1.",
                     {"q": "q1", "rs.top": 1},
                     "Câu so sánh cần hai đoạn nhưng chỉ còn một. Lỗi kiểu “thiếu một vế” thường bắt đầu từ Top K."),
               ])


def lab_start():
    return lab("start", "Khối Start",
               "Khối đầu tiên nhận tin nhắn và tạo biến. Gõ thử một câu, rồi thêm một ô nhập để xem khác gì.",
               docs=("inputs", "addfield"),
               missions=[M("Bật <strong>Thêm ô Select tên nganh</strong>. Khung chat và bảng biến đổi thế nào?", {"start.extra": True},
                           "Có thêm biến <code>Start → nganh</code> và một form trước khi chat. Bài này không cần vì <code>sys.query</code> đã có sẵn, và một chatbot hỏi đáp càng ít bước càng tốt.")])


def lab_kr():
    return lab("kr", "Khối Knowledge Retrieval: hai tầng lọc",
               "Tầng kho chạy trước với cấu hình của kho; tầng khối chạy sau trên kết quả đó. Quan sát ba con số và đầu ra <code>result</code>.",
               docs=("kq", "kkb", "kmeta", "ktop", "kth"), qs=["q1", "q3", "q5"],
               missions=[
                   M("Chọn câu <strong>Mầm non CĐ và ĐH</strong>, đặt Top K của <strong>khối</strong> bằng 1.", {"q": "q1", "node.top": 1, "rs.top": {"gt": 1}},
                     "Tầng kho vẫn trả nhiều đoạn nhưng khối chỉ giữ một, nên câu so sánh mất một vế."),
                   M("Đặt Top K của khối về 6, rồi kéo Top K của <strong>tầng kho</strong> xuống 1.", {"node.top": {"gt": 1}, "rs.top": 1},
                     "<code>result</code> vẫn chỉ có 1 đoạn: khối chỉ cắt bớt, không nới được những gì kho đã trả ra."),
                   M("Bật <strong>Score Threshold</strong> của khối lên 0,99.", {"node.thEn": True, "node.th": {"gt": .95}, "out.count": 0},
                     "<code>result</code> rỗng. Đây là cách ép đi nhánh ELSE khi kiểm thử ở chặng 7; xong nhớ tắt."),
                   M("Đặt <strong>Metadata Filtering</strong> là Chỉ Quy định 5.1–5.3, chọn câu Mầm non.", {"q": "q1", "node.filter": "quy_dinh_muc_5_1_den_5_3.md"},
                     "Kết quả rỗng dù kho có đoạn điểm cao: lọc diễn ra độc lập với điểm. Lọc đúng thì loại được đoạn sai bối cảnh, lọc sai thì mất luôn đoạn đúng."),
                   M("Đặt <strong>Query Text</strong> là (chưa chọn biến).", {"node.query": "empty"},
                     "Không có gì để tìm. Trên Dify, Checklist sẽ báo khối này thiếu biến trước khi bạn chạy."),
               ])


def lab_if():
    return lab("if", "Khối IF/ELSE: đi nhánh nào?",
               "Đổi câu hỏi và toán tử, xem đường đi sáng lên. Chú ý khối này không đọc nội dung đoạn.",
               docs=("ifvar", "ifop", "kth"), qs=["q3", "q5", "q11"],
               missions=[
                   M("Chọn câu <strong>Học phí</strong>. Đi nhánh nào?", {"q": "q5", "out.branch": "if"},
                     "Vẫn nhánh IF, dù tài liệu không có học phí: mảng có phần tử là đủ. Việc từ chối thuộc về prompt ở khối 4."),
                   M("Bật Score Threshold của khối 2 lên 0,99.", {"node.thEn": True, "node.th": {"gt": .95}, "out.branch": "else"},
                     "Mảng rỗng nên đi ELSE: khối 4 không chạy, không tốn lượt gọi mô hình, người dùng nhận câu cố định."),
                   M("Tắt ngưỡng, đổi toán tử thành <code>is empty</code>, chọn câu <strong>PT 100 và chứng chỉ</strong>.", {"cond.op": "empty", "node.thEn": False, "q": "q3"},
                     "Câu có tài liệu lại nhận câu từ chối: điều kiện đảo ngược. Vì vậy kiểm thử phải đi qua cả hai nhánh."),
               ])


def lab_llm(prompt):
    return lab("llm", "Khối LLM: prompt thực tế và câu trả lời",
               "Mở “Xem prompt thực tế” để thấy Context được điền vào đâu. Câu trả lời ở đây được <strong>soạn sẵn</strong> theo kết quả đã quan sát, không gọi mô hình thật: mục đích là thấy mỗi tham số, mỗi nguyên tắc gây ra lỗi gì.",
               docs=("temp", "topp", "maxt", "ctx", "user", "mem", "sys"), prompt=prompt, qs=["q3", "q5", "q2", "q6", "q7", "q8", "q9", "q10", "q11"],
               missions=[
                   M("Câu <strong>PT 100 và chứng chỉ</strong>: đặt <strong>Context</strong> thành (trống).", {"q": "q3", "llm.ctxOn": False},
                     "Khối 2 tìm đúng nhưng LLM không thấy gì nên từ chối oan. Log vẫn báo chạy thành công, nên phải mở prompt thực tế mới phát hiện."),
                   M("Bỏ <strong>nguyên tắc 1</strong>, chọn câu <strong>Học phí</strong>.", {"q": "q5", "off": {"has": 1}, "llm.ctxOn": True},
                     "Xuất hiện một con số không có trong tài liệu. Đó là ảo giác: lỗi nguy hiểm nhất của RAG."),
                   M("Bỏ <strong>nguyên tắc 3</strong>, chọn câu <strong>Sư phạm Toán</strong>.", {"q": "q2", "off": {"has": 3}},
                     "115 bị nhân cho từng chuyên ngành, đúng lỗi bạn đã bắt ở chặng 2. Đoạn tìm đúng mà vẫn trả lời sai: lỗi ở bước sinh."),
                   M("Bỏ <strong>nguyên tắc 4</strong>, chọn câu <strong>X70 có PT 200, Mầm non?</strong>", {"q": "q6", "off": {"has": 4}},
                     "LLM ghép chéo hai bảng thành một kết luận sai. Nguyên tắc này dành riêng cho kiểu bẫy của tài liệu tuyển sinh."),
                   M("Câu <strong>PT 100</strong>, kéo <strong>Max Tokens</strong> xuống dưới 40.", {"q": "q3", "llm.max": {"lt": 40}, "out.truncated": True},
                     "Câu bị cắt giữa chừng và mất dòng Nguồn. Max Tokens chỉ giới hạn độ dài, mô hình không tự viết ngắn lại."),
                   M("Kéo <strong>Temperature</strong> lên 1, bấm <strong>Lấy mẫu 20 lần</strong>.", {"llm.temp": {"gt": .9}},
                     "Xác suất dàn đều hơn, chữ sai cũng có cơ hội được chọn. Kéo về 0.1 thì gần như luôn cùng một chữ. Ổn định không có nghĩa là đúng: mô hình có thể ổn định ở một câu sai."),
                   M("Chọn câu <strong>Thích cây cối</strong>, giữ nguyên mọi nguyên tắc.", {"q": "q11"},
                     "Câu trả lời này lấy nguyên từ log bản mẫu: kiến thức ngoài được gắn nhãn “theo bộ dữ liệu”. Một prompt tốt vẫn có thể lọt, nên phải có bộ kiểm thử."),
               ])


def lab_answer():
    return lab("answer", "Khối Answer: phát chữ thế nào?",
               "Bấm <strong>Gửi câu hỏi</strong>, xem chữ hiện dần. Đổi nội dung rồi gửi lại, chú ý chỗ bị chờ.",
               docs=("acontent", "cite"), qs=["q3", "q2"],
               missions=[
                   M("Chọn <strong>Câu chào + biến LLM</strong>.", {"ans.tpl": "pre"}, "Câu chào hiện ngay, phần sau chờ LLM. Người dùng thấy hệ thống đã phản hồi."),
                   M("Chọn <strong>Dán sẵn một câu cố định</strong>.", {"ans.tpl": "fixed"}, "Mọi câu hỏi đều nhận cùng một câu, trong khi khối LLM vẫn chạy và vẫn tốn tiền. Khối 6 cố định là đúng vì không có LLM phía trước; khối 5 thì không."),
                   M("Tắt <strong>Citation and Attributions</strong>.", {"ans.cite": False}, "Danh sách tài liệu biến mất, nhưng dòng “Nguồn:” do LLM viết vẫn còn. Hai thứ này độc lập: một do nền tảng ghi, một do prompt yêu cầu."),
               ])


def lab_rewrite():
    return lab("rewrite", "Viết lại câu hỏi nối tiếp",
               "Người dùng vừa hỏi về Mầm non cao đẳng, giờ gõ “Còn đại học thì sao?”. Nhìn ô “Câu đem đi tìm” và câu trả lời.",
               docs=("rwon", "rwmem", "rwwin", "kq"), qs=["f1"],
               missions=[
                   M("Bật <strong>Có khối Viết lại câu hỏi</strong>.", {"rw.on": True, "rw.mem": True, "rw.win": {"gt": 0}, "node.query": "rw.text"},
                     "Câu đem đi tìm đã đủ nghĩa nên đoạn Mầm non đại học đứng đầu, chatbot trả lời đúng 450."),
                   M("Tắt <strong>Memory của khối này</strong>.", {"rw.on": True, "rw.mem": False},
                     "Không có lịch sử thì khối viết lại đành trả nguyên câu. Viết lại câu hỏi và Memory phải đi cùng nhau."),
                   M("Bật lại Memory, đổi <strong>Query Text của khối 2</strong> về <code>sys.query</code>.", {"rw.on": True, "rw.mem": True, "node.query": "sys.query"},
                     "Khối mới vẫn chạy và vẫn tốn tiền, nhưng khối 2 không dùng kết quả của nó. Thêm khối xong phải nối biến: đầu ra bước trước là đầu vào bước sau."),
               ])


def lab_all(prompt):
    return lab("all", "Chatflow thu nhỏ: chạy, cài lỗi, tìm tầng lỗi",
               "Đủ sáu khối với cấu hình của bài. Mở từng khối để đổi tham số, chọn câu hỏi, bấm <strong>Chạy</strong> và đọc Workflow Process như trên Dify. Phần tìm kiếm mô phỏng, câu trả lời soạn sẵn.",
               docs=("kq", "kkb", "kmeta", "ktop", "kth", "ifvar", "ifop", "temp", "topp", "maxt", "ctx", "user", "mem", "sys", "acontent", "cite", "inputs", "addfield"),
               prompt=prompt, custom=True, qs=["q1", "q6", "q3", "q7", "q8", "q9", "q10", "q5", "q11"],
               missions=[
                   M("<strong>Lỗi A:</strong> ở khối 4, đặt Context thành (trống), hỏi câu <strong>PT 100</strong>. Tìm trong Workflow Process: lỗi ở khối nào?",
                     {"q": "q3", "llm.ctxOn": False, "out.tone": "bad"}, "Khối 2 có đoạn đúng, khối 4 báo Context trống. Tầng sinh câu trả lời (ghép prompt)."),
                   M("<strong>Lỗi B:</strong> ở khối 2, đặt Top K bằng 1, hỏi câu <strong>Mầm non CĐ và ĐH</strong>.",
                     {"q": "q1", "node.top": 1, "out.tone": "bad"}, "Khối 2 chỉ trả một đoạn. Tầng truy xuất; sửa prompt không có tác dụng."),
                   M("<strong>Lỗi C:</strong> ở khối 4, bỏ nguyên tắc 1 và 5, hỏi câu <strong>Học phí</strong>.",
                     {"q": "q5", "off": {"has": 1}, "out.tone": "bad"}, "Không đoạn nào nói về học phí, nhưng câu trả lời vẫn khẳng định. Tầng sinh câu trả lời (luật prompt)."),
                   M("<strong>Ép nhánh ELSE:</strong> ở khối 2, bật Score Threshold 0,99, hỏi câu <strong>PT 100</strong>.",
                     {"q": "q3", "node.thEn": True, "node.th": {"gt": .95}, "out.branch": "else"}, "Khối 4 và 5 không chạy, khối 6 trả câu cố định."),
               ])
