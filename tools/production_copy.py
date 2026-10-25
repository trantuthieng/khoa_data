"""Biên tập câu chữ cho bản phát hành, không thay mã bài hay mã thực hành."""
import html
import re
from html.parser import HTMLParser


REWRITES = {
    'Bộ giáo trình này giúp cán bộ vận hành và nghiệp vụ ngành điện bảo vệ dữ liệu khách hàng trong công việc hằng ngày, qua 10 buổi học trong 5 ngày. Mỗi buổi là một tài liệu riêng; tài liệu này là phần mở đầu, bản đồ và phụ lục chung.':
        'Khóa học gồm 10 buổi trong 5 ngày, dành cho cán bộ quản lý, nhân sự CNTT và vận hành hệ thống trong đơn vị điện lực. Nội dung tập trung vào bảo vệ dữ liệu, quản lý truy cập, kiểm tra báo cáo và phối hợp xử lý sự cố. Phần Tổng quan giới thiệu lộ trình, tình huống thực hành và các biểu mẫu dùng trong khóa.',
    'Cán bộ vận hành, kinh doanh, chăm sóc khách hàng, kế hoạch, tổng hợp báo cáo – những người hằng ngày xem, xuất, gửi và phân tích dữ liệu.':
        'Cán bộ quản lý, quản trị cơ sở dữ liệu, phát triển phần mềm, quản trị hệ thống, vận hành CNTT, viễn thông, đo xa và SCADA trong các đơn vị điện lực.',
    'Không cần nền tảng CNTT hay an toàn thông tin. Không cần biết lập trình: các đoạn code trong giáo trình do giảng viên chạy mẫu, học viên chỉ cần hiểu ý nghĩa.':
        'Học viên cần quen với tài khoản, tệp dữ liệu và các hệ thống phục vụ công việc. Bài SQL, Python và Power BI có hướng dẫn theo từng bước. Giảng viên lựa chọn bài phù hợp với kinh nghiệm và nhiệm vụ của từng học viên.',
    'Cán bộ CNTT, an toàn thông tin và quản lý có thể dùng giáo trình để thống nhất cách nói với người dùng nghiệp vụ.':
        'Khóa học giúp thống nhất cách đánh giá rủi ro, đề xuất kiểm soát và phối hợp giữa cán bộ quản lý, kỹ thuật và nghiệp vụ. Mỗi học viên làm bài cá nhân, ghi kết quả kiểm tra và giải thích phương án của mình.',
    'Phần lớn sự cố dữ liệu không bắt đầu từ một cuộc tấn công tinh vi. Chúng bắt đầu từ những việc rất bình thường: một file xuất đủ cột, một link chia sẻ "ai có link đều xem được", một mật khẩu dùng lại, một lần bấm "Chấp nhận" trên điện thoại. Vì vậy khóa học dành cho người trực tiếp thao tác với dữ liệu, không chỉ cho cán bộ CNTT.':
        'Sự cố dữ liệu có thể bắt đầu từ thao tác hằng ngày: xuất thừa trường, chia sẻ liên kết công khai, dùng lại mật khẩu hoặc chấp thuận yêu cầu MFA ngoài dự kiến. Khóa học sử dụng các tình huống này để xác định điểm cần kiểm soát, người chịu trách nhiệm và bằng chứng kiểm tra.',
    'Từ 01/01/2026, Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 có hiệu lực. Luật quy định rõ vai trò của bên kiểm soát, bên xử lý, mốc thông báo vi phạm chậm nhất 72 giờ và mức phạt tới 3 tỷ đồng với tổ chức cho các vi phạm thông thường. Bảo vệ dữ liệu khách hàng vì vậy vừa là trách nhiệm với khách hàng, vừa là nghĩa vụ pháp lý.':
        'Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 có hiệu lực từ ngày 01/01/2026. Khi xử lý dữ liệu, đơn vị cần xác định vai trò, trách nhiệm và nghĩa vụ áp dụng cho từng hoạt động. Phần pháp luật trong khóa học phục vụ nhận thức và phối hợp với đầu mối pháp chế; nghĩa vụ thông báo và thời hạn được xem xét theo trường hợp cụ thể.',
    'PDPA không phải một luật duy nhất; đây là tên viết tắt của luật bảo vệ dữ liệu cá nhân ở một số nước như Singapore, Thái Lan. Khi slide nhắc "PDPA", trong bối cảnh Việt Nam nên hiểu là Luật 91/2025/QH15.':
        'PDPA là tên viết tắt được sử dụng cho pháp luật bảo vệ dữ liệu cá nhân tại một số quốc gia, chẳng hạn Singapore. Khi tài liệu nhắc PDPA, cần xác định rõ quốc gia và điều kiện áp dụng. Không đồng nhất tên gọi này với Luật Bảo vệ dữ liệu cá nhân của Việt Nam.',
    'Khóa học gồm 10 buổi, mỗi buổi 3,5 giờ (sáng 08:00–11:30, chiều 13:30–17:00, có 15 phút nghỉ). Bấm tên buổi để mở tài liệu của buổi đó.':
        'Khóa học gồm 10 buổi trong 5 ngày. Khung giờ theo tài liệu trình chiếu: sáng 08:00–11:30, chiều 13:30–16:30. Lịch chi tiết và thời gian nghỉ do giảng viên thông báo. Chọn buổi học trong danh sách để xem nội dung đã được mở.',
    'Thời lượng, slide, đầu vào, đầu ra; mạch nối với buổi trước và buổi sau; mục tiêu học tập':
        'Lịch học, nội dung cần chuẩn bị, sản phẩm thực hành và mục tiêu của buổi học',
    'Không cần kiến thức trước. Học viên mang theo kinh nghiệm công việc hằng ngày với dữ liệu khách hàng':
        'Kinh nghiệm sử dụng tài khoản, tệp dữ liệu hoặc báo cáo trong công việc; không sử dụng dữ liệu thật khi làm bài',
    'Không có "con số đúng chung". Thời hạn lưu giữ, thời gian hết phiên, chu kỳ rà soát quyền do quy định của từng đơn vị quyết định; giáo trình chỉ đưa ví dụ.':
        'Thời hạn lưu giữ, thời gian hết phiên và chu kỳ rà soát quyền phải căn cứ quy định áp dụng của đơn vị. Các con số trong bài là ví dụ để thực hành.',
    'Hỏi khi chưa chắc là hành vi đúng, không phải yếu kém. Báo sớm một nghi ngờ hóa ra không phải sự cố không bao giờ bị khiển trách.':
        'Khi chưa rõ, học viên cần hỏi lại và báo sớm dấu hiệu nghi ngờ qua đầu mối phù hợp. Trong lớp, việc chia sẻ tình huống được trao đổi trên tinh thần học hỏi, không quy kết cá nhân.',
    'SQL là "ngôn ngữ hỏi" cơ sở dữ liệu. Bốn từ khóa cần biết:':
        'SQL được dùng để truy vấn dữ liệu. Bốn từ khóa dưới đây giúp chọn trường, lọc phạm vi và tổng hợp kết quả:',
    'Đăng nhập qua SSO của đơn vị nếu có, để khóa một chỗ là khóa mọi ứng dụng':
        'Sử dụng SSO của đơn vị nếu đã triển khai; khi thu hồi truy cập, kiểm tra quyền và phiên tại các ứng dụng liên quan',
    'Chiếm nv_c là chiếm mọi ứng dụng dùng SSO; vì vậy MFA ở cửa SSO phải mạnh':
        'Tài khoản nv_c bị chiếm có thể làm lộ quyền truy cập các ứng dụng liên kết SSO; cần bảo vệ tài khoản trung tâm và kiểm tra phiên tại từng ứng dụng',
    'Vì vậy mật khẩu file càng dài càng tốt.':
        'Vì vậy, cần dùng mật khẩu dài, khó đoán và không dùng lại, theo quy định của đơn vị.',
    'Trang "đăng nhập Wi-Fi" không bao giờ cần mật khẩu email công ty.':
        'Không nhập mật khẩu công việc vào trang đăng nhập Wi-Fi chưa được xác minh. Nếu đơn vị dùng SSO, thực hiện theo hướng dẫn chính thức và kiểm tra tên miền trước khi đăng nhập.',
    'Quên mật khẩu thì không ai mở được, kể cả CNTT':
        'Nếu thiếu mật khẩu và không có phương án khôi phục đã thiết lập, có thể mất khả năng mở file',
    'Nếu chị quên mật khẩu, không ai mở được file đó, kể cả CNTT.':
        'Nếu mất mật khẩu và chưa thiết lập phương án khôi phục, chị có thể không mở lại được file.',
    'Dòng cuối cần nhấn mạnh: tin nhắn chương 8 không có link, không có file, không có lỗi chính tả. Mọi mẹo "soi link" đều vô dụng; chỉ còn câu hỏi về yêu cầu và kênh.':
        'Tin nhắn ở chương 8 không có liên kết, tệp đính kèm hoặc lỗi chính tả. Việc kiểm tra hình thức thông điệp chưa đủ; cần đối chiếu yêu cầu và xác minh người gửi qua kênh độc lập.',
    'Thông báo rõ: CNTT không bao giờ yêu cầu bấm Chấp nhận MFA, đọc OTP, hay liên lạc qua Zalo cá nhân để thay đổi hệ thống.':
        'Thông báo kênh hỗ trợ CNTT chính thức. Nhắc người dùng không cung cấp mật khẩu, OTP hoặc chấp thuận yêu cầu đăng nhập ngoài dự kiến qua tin nhắn hỗ trợ.',
    'CNTT không bao giờ yêu cầu bấm Chấp nhận MFA, đọc OTP hay liên lạc qua Zalo cá nhân':
        'Không cung cấp mật khẩu, OTP hoặc chấp thuận yêu cầu đăng nhập ngoài dự kiến; xác minh hỗ trợ qua kênh CNTT chính thức',
    'Phát file log vòng 2 ở dạng giờ UTC và không nhắc trước; để học viên đọc nhầm 19:10 rồi mới chỉ ra – bài học về múi giờ sẽ không ai quên.':
        'Giảng viên yêu cầu học viên xác định múi giờ trước khi phân tích nhật ký vòng 2. Khi chữa bài, đối chiếu ảnh hưởng của việc đọc nhầm UTC và giờ địa phương.',
    'In và cắt sáu thẻ vai cho mỗi nhóm; năm phiếu tình tiết cho vào phong bì đánh số, phiếu đợt 3 giữ kín tuyệt đối.':
        'Chuẩn bị sáu thẻ vai để từng học viên xác định trách nhiệm của các bên. Công bố năm đợt tình tiết theo tiến độ bài học; chỉ mở đợt 3 khi đến phần tương ứng.',
    'Bài 1 cho biết giao gì. Bài này trả lời câu hỏi 2: làm thế nào, theo trình tự nào, bằng công cụ gì. Người dùng nghiệp vụ không cần tự viết code; cần đọc hiểu để đặt yêu cầu đúng cho bộ phận dữ liệu, và biết cách làm tương đương trong Excel.':
        'Bài này hướng dẫn chọn và giảm dữ liệu bằng SQL, Python hoặc Excel. Học viên đối chiếu mã, kết quả và phạm vi bản xuất; giảng viên lựa chọn mức thực hành phù hợp với nhiệm vụ và kinh nghiệm của từng người.',
    'Chạy đoạn Python ở mục 1.8 nếu lớp có máy chiếu; nếu không, ghi sẵn kết quả lên slide. Mục tiêu là thấy ba loại "chuỗi lạ" khác nhau, không phải học lập trình.':
        'Giảng viên có thể chạy đoạn Python ở mục 1.8 hoặc chuẩn bị sẵn kết quả để đối chiếu. Học viên cần phân biệt đầu ra của mã hóa, hàm băm và chữ ký số.',
    'Người chưa biết lập trình chỉ cần đọc "đọc bằng lời" của mỗi đoạn mã; giảng viên chạy script, học viên đọc kết quả và trả lời "dòng nào đáng lo".':
        'Giảng viên chọn bài theo kinh nghiệm của học viên. Người mới bắt đầu làm các bài ngắn có mẫu điền tiếp; người đã sử dụng SQL/Python tập trung vào kết quả, phạm vi dữ liệu và bằng chứng kiểm tra. Chỉ ghi đã thực hiện khi đã chạy mã trên dữ liệu giả lập.',
    'Bám slide 58–68. Có 8 bài SQL và 8 bài Python, mỗi bài khoảng 5–10 phút. Làm cá nhân. Trong giờ chọn bài phù hợp, các bài còn lại để luyện thêm; không bắt buộc làm hết trong một buổi.':
        'Có 8 bài SQL và 8 bài Python, mỗi bài tập trung một thao tác và thường cần 5–10 phút. Học viên làm cá nhân theo bài được giao. Các bài còn lại dùng để ôn tập hoặc luyện thêm.',
    'Slide 72 dùng DimNgay và dữ liệu theo ngày. Bài lớn trong giáo trình dùng DimThang và số liệu đã tổng hợp theo tháng. Cả hai đều có thể phù hợp, nhưng không trộn bảng và công thức giữa hai mức chi tiết.':
        'Bộ bài này dùng DimNgay và dữ liệu theo ngày. Thực hành 8 dùng DimThang cùng dữ liệu tổng hợp theo tháng. Khi làm bài, cần sử dụng đúng bảng, quan hệ và công thức của từng bộ dữ liệu.',
    'Slide 81 yêu cầu cả sản lượng và số khách hàng, trong khi sơ đồ slide 72 chỉ nêu MaDonVi, Ngay, kWh. Bộ bài nhỏ thêm MaKH giả lập để thực hành DISTINCTCOUNT. Đây là cột thêm phục vụ bài đếm, không phải yêu cầu đưa mã khách thật vào mọi báo cáo.':
        'Bộ dữ liệu thực hành có thêm MaKH giả lập để phân biệt số dòng với số khách hàng duy nhất khi dùng DISTINCTCOUNT. Trong báo cáo thực tế, chỉ sử dụng trường định danh khi có mục đích và phê duyệt phù hợp.',
    'Bắt đầu Power BI – Nối mô hình ngày trong slide với bài học': 'Chuẩn bị thực hành Power BI – Mô hình dữ liệu theo ngày',
    'Bắt đầu SQL và Python – Dữ liệu nhỏ, mỗi bài một việc': 'Chuẩn bị thực hành SQL và Python',
    'Hai vị trí trên service được minh họa trong slide': 'Gán thành viên và kiểm tra vai trò trên Power BI service',
    'Ảnh trích từ slide 76: thêm người dùng vào role ở Security của semantic model. Đây là ảnh tài liệu, giao diện môi trường của bạn có thể khác.':
        'Trong mục Security của semantic model, chọn vai trò RLS rồi thêm người dùng hoặc nhóm phù hợp. Hình minh họa trích từ tài liệu trình chiếu; giao diện có thể khác theo phiên bản.',
    'Ảnh trích từ slide 77: mở menu của role để chọn Test as role. Sau đó vẫn cần kiểm tra bằng tài khoản Viewer thật nếu có service thực hành.':
        'Mở menu của vai trò và chọn Test as role để đối chiếu kết quả. Sau đó kiểm tra bằng tài khoản Viewer trong môi trường thực hành trước khi xác nhận quyền người xem.',
    'Gộp bằng GROUP BY, bám slide 62.': 'Tổng hợp kết quả theo đơn vị bằng GROUP BY.',
    'Truyền giá trị riêng bằng sqlite3, bám slide 66.': 'Truyền giá trị qua tham số của sqlite3, tách giá trị khỏi cấu trúc truy vấn.',
    'Dùng lát cắt chuỗi như slide 63.': 'Dùng lát cắt chuỗi để che một phần số điện thoại giả lập.',
    'Tạo quan hệ một–nhiều, bám slide 72.': 'Tạo và kiểm tra hai quan hệ một–nhiều trong mô hình thực hành.',
    'Bài cần nộp: điền ba mục trong mẫu trên web. Nêu rõ dữ kiện, cách xử lý và cách kiểm tra kết quả.':
        'Nộp bài cá nhân theo mẫu. Nêu rõ dữ kiện, phương án xử lý và cách kiểm tra kết quả.',
    'Mở rộng cho nhóm làm nhanh': 'Bài thực hành mở rộng',
    'nhóm đóng vai quản lý cũ': 'người xem xét từ vai trò quản lý cũ',
    'in mỗi nhóm một bộ': 'chuẩn bị một bộ cho mỗi học viên',
    'thực hành cá nhân hoặc theo cặp trên máy': 'thực hành cá nhân trên máy',
    'Excel cho nhóm không lập trình': 'Excel cho học viên chọn cách xử lý không dùng lập trình',
    'giảng viên chạy demo SQL/Python': 'giảng viên minh họa SQL/Python và hướng dẫn thực hành',
    'Bắt đầu SQL và Python hoặc Bắt đầu Power BI': 'Chuẩn bị thực hành SQL và Python hoặc Chuẩn bị thực hành Power BI',
    'suyệt tin': 'suýt tin',
    'soi kỹ': 'kiểm tra kỹ',
    'một mẹo dễ đọc qua điện thoại': 'một cách tạo cụm từ thuận tiện khi trao đổi qua điện thoại',
    'đây là mẹo kiểm thử nhanh': 'có thể dùng số liệu này để kiểm tra nhanh',
    '4.2. Điều người mới hay hiểu sai': '4.2. Những điểm cần phân biệt khi quản lý phiên',
    '4.2. Bài log mẫu có bẫy': '4.2. Nhật ký mẫu có điểm cần đối chiếu',
    'Vòng 1 (25 phút): log mẫu 5 dòng của slide (mục 4.2) – luyện cách làm, có bẫy.':
        'Vòng 1 (25 phút): phân tích nhật ký mẫu 5 dòng ở mục 4.2; đối chiếu thứ tự sự kiện trước khi kết luận.',
    'Giảng viên giữ kín': 'Giảng viên chỉ công bố theo tiến độ bài học',
    'Một sự cố có thể ảnh hưởng đồng thời nhiều mục tiêu CIA.': 'Một sự cố có thể đồng thời ảnh hưởng đến nhiều mục tiêu CIA.',
}

TEXT_KEYS = {'plain', 'text', 'title', 'short', 'intro', 'label', 'hint', 'answer', 'explain'}


def polish_text(text):
    for old, new in REWRITES.items():
        text = text.replace(old, new)
    return text


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def handle_starttag(self, tag, attrs):
        if tag == 'br':
            self.parts.append('\n')


def plain_from_html(value):
    parser = _Text()
    parser.feed(value)
    return ''.join(parser.parts)


def _walk(value):
    if isinstance(value, list):
        return [_walk(v) for v in value]
    if not isinstance(value, dict) or value.get('t') == 'code':
        return value
    out = {k: polish_text(v) if k in TEXT_KEYS and isinstance(v, str) else _walk(v) for k,v in value.items()}
    if 'html' in value:
        out['html'] = polish_text(value['html'])
        if out.get('plain') != value.get('plain') and re.sub(r'\s+', ' ', plain_from_html(out['html'])).strip() != re.sub(r'\s+', ' ', out['plain']).strip():
            out['html'] = html.escape(out['plain']).replace('\n', '<br>')
    if 'title' in out:
        # Giữ thời lượng và tên bài, bỏ số slide khỏi nhãn điều hướng.
        out['title'] = re.sub(r'\s*\(slide\s+[\d–,\s]+\)', '', out['title'], flags=re.I)
        out['title'] = re.sub(r',\s*slide\s+[\d–,\s]+(?=\))', '', out['title'], flags=re.I)
    return out


def polish(module):
    module = _walk(module)
    no = module['no']
    for section in module['sections']:
        if section['title'] == 'Thông tin buổi học':
            for block in section['blocks']:
                if block['t'] != 'table':
                    continue
                for row in block['rows']:
                    if len(row) < 2:
                        continue
                    label = row[0]['plain']
                    if label == 'Thời gian' and no % 2 == 0:
                        text = re.sub(r'13:30–17:00 \(3,5 giờ', '13:30–16:30 (3 giờ', row[1]['plain'])
                        row[1]['plain'] = row[1]['html'] = text
                    if label == 'Slide':
                        row[0]['plain'] = row[0]['html'] = 'Tài liệu trình chiếu'
                        if no == 10:
                            row[1]['plain'] = row[1]['html'] = '102–110'
        if section['kind'] == 'teacher':
            section['blocks'].insert(0, {'t':'p','plain':'Giảng viên điều chỉnh phân bổ thời gian theo lịch học chính thức và bài được giao. Các bài thực hành đều nộp cá nhân.',
                                       'html':'Giảng viên điều chỉnh phân bổ thời gian theo lịch học chính thức và bài được giao. Các bài thực hành đều nộp cá nhân.'})
    if no == 0:
        for section in module['sections']:
            for b in section['blocks']:
                if b['t'] != 'table':
                    continue
                for row in b['rows']:
                    for cell in row:
                        if cell.get('plain') == 'Chiều (13:30–17:00)':
                            cell['plain'] = cell['html'] = 'Chiều (13:30–16:30)'
                        if cell.get('plain') == 'Hai bảng log: log mẫu của slide 100–101 và log 12 dòng đêm 20/10 (bản không kèm lời giải)':
                            cell['plain'] = cell['html'] = 'Hai bảng nhật ký: mẫu 5 dòng và nhật ký 17 dòng đêm 20–21/10, giờ UTC; bản dành cho học viên không kèm lời giải'
    return module
