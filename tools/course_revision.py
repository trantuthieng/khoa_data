"""Biên tập bản dùng trên web; giữ nguyên tài liệu Word làm nguồn đối chiếu."""
import html
import re
from pathlib import Path
import json

from beginner_labs import add_labs


# Thay theo cụm có nghĩa, tránh đổi nhầm “nhóm dữ liệu”, “nhóm quyền”, nhóm ứng phó.
REPLACEMENTS = {
    'đây là mốc thận trọng, sớm nhất mà người có trách nhiệm đã nắm được dấu hiệu rõ.': 'đây là giả định của bài tính giờ, không phải quy tắc lấy thời điểm đầu mối nhận tin làm mốc phát hiện. Cần giữ cả mốc tổng đài nhận tin lúc 08:35 để đối chiếu.',
    'Việc chọn mốc là quyết định của pháp chế – khóa học chỉ minh họa cách tư duy.': 'Pháp chế phối hợp người có trách nhiệm xác định mốc phát hiện từ bằng chứng và quy định áp dụng; không tùy chọn mốc muộn để kéo dài thời hạn.',
    'Làm theo nhóm trong buổi': 'Làm cá nhân trong buổi',
    'thực hành nhóm 4–5 người': 'thực hành cá nhân',
    'vẽ sơ đồ theo nhóm trên giấy A3': 'tự vẽ và mô tả sơ đồ trong bài làm',
    'thực hành nhóm đóng vai': 'phân tích tình huống và tự đề xuất cách xử lý',
    'thực hành nhóm trên giấy A3 và Excel': 'thực hành cá nhân với bảng diễn biến và Excel',
    'thực hành nhóm': 'thực hành cá nhân',
    'Nhóm, giấy A3': 'Cá nhân, mô tả trên web',
    'Nhóm, đóng vai': 'Cá nhân, xem xét từng vai',
    'Nhóm nào quyết muộn hơn': 'Nếu bạn quyết định muộn hơn',
    'nhóm nào đó đọc nhầm': 'học viên đọc nhầm',
    'khi nhóm nào viết': 'khi học viên viết',
    'Nếu nhóm đề xuất': 'Nếu học viên đề xuất',
    'nhiều nhóm sẽ quên': 'nhiều học viên sẽ quên',
    'Giữ sơ đồ của các nhóm': 'Giữ sơ đồ của từng học viên',
    'Giữ ma trận của các nhóm': 'Giữ ma trận của từng học viên',
    'khuyến khích nhóm chọn quy trình B (của chính họ)': 'khuyến khích học viên chọn quy trình B (công việc của mình)',
    'nhóm hay ghi': 'học viên hay ghi',
    'làm ràng buộc cho nhóm': 'làm ràng buộc cho bài cá nhân',
    'cả nhóm tìm ra ngoại lệ hẹp': 'học viên xác định ngoại lệ có phạm vi hẹp',
    'Các nhóm không bắt đầu từ con số không': 'Bạn dùng lại bài đã làm ở buổi 9',
    'các nhóm tự quyết định': 'từng học viên tự đề xuất',
    'Các nhóm sẽ quyết chi tiết': 'Bạn sẽ đề xuất cụ thể',
    'do các nhóm tự phân tích': 'do từng học viên tự phân tích',
    'nhóm đề xuất, người có thẩm quyền quyết định': 'học viên đề xuất, người có thẩm quyền quyết định',
    'khung của các đầu ra thực hành. In sẵn cho lớp, hoặc chép bảng vào file làm việc của nhóm.': 'mẫu để ghi bài thực hành. Trên web, mỗi học viên điền mẫu của riêng mình.',
    'diễn tập trên bàn theo nhóm đóng vai': 'diễn tập trên bàn, mỗi học viên lập phương án theo các vai',
    'Chia lớp thành bốn nhóm; mỗi nhóm nhận một tình huống (15 phút chuẩn bị).': 'Mỗi học viên đọc cả bốn tình huống và điền bảng phân tích trong 15 phút.',
    'Mỗi nhóm đóng vai trước lớp (5 phút/nhóm): một người là kẻ giả mạo, cố gây áp lực; một người là nhân viên áp dụng quy trình 4 bước.': 'Giảng viên chọn một vài tình huống để cùng lớp trao đổi. Bạn trình bày cách áp dụng quy trình 4 bước và câu trả lời của mình.',
    'Nhiệm vụ của mỗi nhóm': 'Nhiệm vụ của bạn',
    'bảng phân tích của nhóm (theo mẫu bảng đáp án dưới đây) và phần đóng vai': 'bảng phân tích cá nhân theo mẫu trên web và câu trả lời cho từng yêu cầu',
    'Sáu vai mỗi nhóm và một thư ký': 'Sáu vai cần xem xét khi đề xuất quyết định',
    'Biên bản diễn tập của mỗi nhóm': 'Biên bản diễn tập của từng học viên',
    'Nhóm 6–7 người: sáu vai và một thư ký. Nhóm 5 người thì một người kiêm pháp chế và truyền thông, thư ký do điều phối kiêm.': 'Mỗi học viên đọc sáu vai và ghi rõ ai có quyền quyết định, ai thực hiện. Bạn tự ghi biên bản cho phương án của mình.',
    'Thời gian: 5 đợt × 12 phút, cộng 10 phút họp nhanh. Mỗi đợt: giảng viên đọc phiếu tình tiết (1 phút), nhóm thảo luận và quyết (8 phút), một nhóm trình bày nhanh (3 phút).': 'Thời gian: 5 đợt, mỗi đợt 12 phút; cuối bài dành 10 phút rút kinh nghiệm. Mỗi đợt gồm 1 phút đọc tình tiết, 8 phút tự cân nhắc và ghi quyết định, 3 phút trao đổi cùng lớp.',
    'Mỗi nhóm trả lời ba câu, thư ký ghi:': 'Bạn tự trả lời ba câu sau trong phần rút kinh nghiệm:',
    'Điều gì nhóm làm tốt?': 'Điều gì trong phương án của bạn đã làm tốt?',
    'quyết định của nhóm': 'quyết định trong bài làm của bạn',
    'Điều nhóm không trả lời được': 'Điều bạn chưa trả lời được',
    'Mạch nối': 'Buổi này tiếp nối buổi trước như thế nào?',
    'Mở rộng cho nhóm làm nhanh': 'Bài thêm nếu bạn hoàn thành sớm',
    'Tiêu chí đánh giá nhóm': 'Tiêu chí đánh giá bài làm',
    'Lỗi nhóm hay mắc': 'Những lỗi thường gặp khi làm bài',
    'Nhóm học viên đóng vai chị Dung': 'Bạn đóng vai chị Dung',
    'Các nhóm áp dụng cả bốn bài vào năm nhóm dữ liệu giả lập và làm ra bảng phân loại – đầu ra đầu tiên của khóa, dùng lại ở buổi 2 và buổi 3.': 'Bạn hãy phân loại năm nhóm dữ liệu dưới đây. Giữ lại bảng đã làm để dùng tiếp ở buổi 2 và buổi 3.',
    'Nhóm 4–5 người, mỗi nhóm một tờ A3 kẻ sẵn mẫu C1 (Phụ lục C, tài liệu Tổng quan).': 'Mỗi học viên điền một bảng phân loại theo mẫu C1 ngay trong bài làm trên web.',
    '20 phút làm, 15 phút hai nhóm trình bày, giảng viên chữa.': 'Bạn có 20 phút làm bài. Trong 15 phút còn lại, giảng viên mời một vài học viên trình bày và cùng lớp chữa bài.',
    'Nên xếp mỗi nhóm có người từ ít nhất hai bộ phận khác nhau (kinh doanh, kỹ thuật, tổng hợp) để nhìn dữ liệu từ nhiều phía.': 'Khi chữa bài, hãy so sánh góc nhìn của các bộ phận kinh doanh, kỹ thuật và tổng hợp.',
    'Nhóm chọn khác vẫn được nếu nêu rõ lý do và giả định.': 'Bạn có thể chọn nhãn khác nếu giải thích rõ lý do và giả định.',
    'Các nhóm vẽ sơ đồ cho một quy trình thật của chính mình và lập bảng rủi ro': 'Bạn hãy vẽ sơ đồ cho một quy trình quen thuộc và lập bảng rủi ro',
    'Một quy trình của nhóm': 'Một quy trình bạn đang thực hiện',
    'Vẽ quy trình trên giấy A3 theo ký hiệu của Bài 4.': 'Mô tả từng bước trong ô bài làm theo ký hiệu của Bài 4. Bạn có thể vẽ nháp trên giấy trước khi nhập.',
    '20 phút 2–3 nhóm trình bày': '20 phút trình bày và chữa bài',
    'bảng phân loại của nhóm': 'bảng phân loại bạn đã làm',
    '(bốn nhóm dữ liệu)': '(năm nhóm dữ liệu)',
    'Đóng vai (mỗi nhóm 4 người): chị Hà, quản lý Điện lực X (anh Tuấn), quản lý phòng Kế hoạch Điện lực Y, cán bộ CNTT.': 'Bạn hãy xem xét lần lượt góc nhìn của chị Hà, quản lý Điện lực X (anh Tuấn), quản lý phòng Kế hoạch Điện lực Y và cán bộ CNTT. Mỗi học viên nộp một phương án riêng.',
    'Nhóm phải trả lời': 'Bạn cần trả lời',
    'Câu hỏi nhóm phải quyết': 'Những quyết định bạn cần đề xuất',
    'Nhóm 4–5 người, mỗi nhóm một tờ A3 và một máy có Excel.': 'Mỗi học viên làm một bài riêng. Bạn có thể đọc nhật ký trên web hoặc dùng Excel để sắp xếp.',
    'Lập một timeline có múi giờ trên giấy A3 (trục ngang là thời gian, mỗi sự kiện một mốc).': 'Lập bảng diễn biến theo thời gian trong bài làm; ghi rõ múi giờ và mỗi sự kiện trên một dòng.',
    'Đổi file với bạn bên cạnh, thử mở bằng mật khẩu sai': 'Tự đóng file rồi thử mở lại bằng mật khẩu sai',
    'trong phạm vi thẩm quyền của nhóm': 'trong phạm vi thẩm quyền được giao',
    'Đầu ra của nhóm và tiêu chí đánh giá': 'Bài cần nộp và tiêu chí đánh giá',
    'Timeline': 'Diễn biến theo thời gian',
    'timeline': 'bảng diễn biến theo thời gian',
    'Đầu ra:': 'Bài cần nộp:',
    'Đầu vào:': 'Dữ liệu để làm bài:',
}


def edit_text(text):
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


def edit_tree(value):
    if isinstance(value, list):
        return [edit_tree(v) for v in value]
    if not isinstance(value, dict):
        return value
    # Không sửa mã, tên trường, địa chỉ, câu lệnh hay số liệu trong bài.
    if value.get('t') == 'code':
        return value
    return {k: edit_text(v) if k in ('text', 'plain', 'html', 'title', 'short', 'intro', 'answer', 'explain') and isinstance(v, str)
            else edit_tree(v) for k, v in value.items()}


def paragraph(text, **flags):
    return {'t': 'p', 'plain': text, 'html': html.escape(text), **flags}


def cell(text):
    return {'plain': text, 'html': html.escape(text)}


def table(rows, **flags):
    return {'t': 'table', 'rows': [[cell(c) for c in row] for row in rows], **flags}


def steps(items, **flags):
    return {'t': 'list', 'ordered': True, **flags,
            'items': [{'plain': t, 'html': html.escape(t), 'level': lv} for lv, t in items]}


# Bài làm mẫu Thực hành 4 theo đúng các module trên bảng; chỉ hiện khi giảng viên công bố.
TH4_BAI_MAU = [
    ('h3', 'Bài làm mẫu đầy đủ theo không gian bảng'),
    ('p', 'Bài mẫu dưới đây điền đủ các module trên bảng. Phương án khác vẫn đạt nếu quyền được thu hẹp đúng phạm vi, có người duyệt, có hạn và kiểm tra lại được.'),
    ('p', '① Người liên quan – mỗi người muốn gì, lo ngại gì'),
    ('table', [['Người liên quan', 'Muốn gì', 'Lo ngại gì'],
               ['Chị Hà', 'Bàn giao xong 37 hồ sơ; bắt đầu ngay việc mới ở phòng Kế hoạch Điện lực Y', 'Mất quyền đột ngột khi người kế nhiệm chưa nắm hồ sơ'],
               ['Anh Tuấn – quản lý Điện lực X', '37 khiếu nại được xử lý đúng hạn', 'Người kế nhiệm chưa nắm lịch sử từng hồ sơ'],
               ['Quản lý phòng Kế hoạch – Điện lực Y', 'Chị Hà có đúng quyền cho việc mới và tập trung cho phòng', 'Chị Hà bị kéo về việc cũ lâu dài; tài khoản người của phòng giữ dữ liệu của đơn vị khác'],
               ['Cán bộ CNTT', 'Có phiếu duyệt rõ: gỡ quyền gì, cấp quyền gì, hạn đến khi nào', 'Ngoại lệ không có hạn, không ai nhớ gỡ']]),
    ('p', '② Quyết định cho từng quyền của chị Hà'),
    ('table', [['Quyền', 'Quyết định', 'Lý do'],
               ['Xem toàn bộ khách hàng Điện lực X', 'Thu hẹp', 'Chỉ xem đúng 37 hồ sơ khiếu nại đang dở, không sửa, hết hạn sau 2 tuần. Tốt hơn nữa: giao 37 hồ sơ cho người kế nhiệm, chị Hà hướng dẫn trực tiếp, khi đó chọn Thu hồi và không cần ngoại lệ'],
               ['Xuất dữ liệu khách hàng Điện lực X', 'Thu hồi', 'Gỡ ngay. Bàn giao hồ sơ không cần mang dữ liệu ra khỏi hệ thống'],
               ['Vai trò Kế hoạch – Điện lực Y', 'Cấp mới', 'Theo ma trận quyền của phòng Kế hoạch Điện lực Y; không sao chép quyền cũ sang']]),
    ('p', '③ Năm bước xử lý, nối theo thứ tự 1 → 2 → 3 → 4 → 5'),
    ('list', [(0, 'Xác định nhu cầu bàn giao: anh Tuấn và chị Hà lập danh sách mã 37 hồ sơ và việc còn lại của từng hồ sơ. Chỉ cần xem (và ghi chú bàn giao nếu hệ thống hỗ trợ), không sửa, không xuất. Làm xong trong ngày đầu. Phụ trách: Anh Tuấn: thực hiện. Chị Hà: xác nhận.'),
              (0, 'Phê duyệt ngoại lệ và đặt hạn: anh Tuấn và chủ sở hữu dữ liệu ký phiếu ngoại lệ ghi phạm vi 37 hồ sơ, chỉ xem, ngày giờ hết hạn cụ thể (2 tuần kể từ ngày duyệt). Nếu đã giao hồ sơ cho người kế nhiệm thì ghi “không cần ngoại lệ”. Phụ trách: Anh Tuấn: duyệt. Quản lý phòng Kế hoạch – Điện lực Y: đồng ý cho chị Hà dành thời gian bàn giao.'),
              (0, 'Thu hồi quyền không còn cần: gỡ ngay quyền xuất và quyền xem toàn bộ khách hàng Điện lực X; nếu có ngoại lệ thì cấu hình quyền xem 37 hồ sơ, tự hết hạn đúng ngày; đăng xuất các phiên đang mở. Phụ trách: Cán bộ CNTT: thực hiện theo phiếu đã duyệt.'),
              (0, 'Cấp quyền mới ở Điện lực Y: gán vai trò Kế hoạch – Điện lực Y theo ma trận quyền. Phụ trách: Quản lý phòng Kế hoạch – Điện lực Y: duyệt. Cán bộ CNTT: thực hiện.'),
              (0, 'Kiểm tra lại bằng tài khoản chị Hà: mở một hồ sơ Điện lực X ngoài 37 hồ sơ → phải bị từ chối; xuất danh sách khách hàng Điện lực X → phải bị từ chối; mở chức năng của phòng Kế hoạch Điện lực Y → được phép. Ngày ngoại lệ hết hạn: mở một trong 37 hồ sơ → phải bị từ chối. Phụ trách: Cán bộ CNTT: thực hiện. Chị Hà: xác nhận.')]),
    ('p', '④ Bằng chứng'),
    ('table', [['Bằng chứng', 'Chứng minh điều gì', 'Nối với'],
               ['Báo cáo quyền của tài khoản chị Hà trước và sau khi xử lý', 'Quyền xem toàn bộ và quyền xuất Điện lực X đã gỡ; chỉ còn vai trò Điện lực Y (và ngoại lệ 37 hồ sơ nếu có)', 'Quyền xem, quyền xuất, quyền mới'],
               ['Phiếu ngoại lệ có phạm vi, người duyệt, ngày giờ hết hạn', 'Ngoại lệ hẹp, có người chịu trách nhiệm, có hạn', 'Bước 2'],
               ['Log gỡ quyền (ngày giờ, người thực hiện) và log đóng ngoại lệ khi hết hạn', 'Việc thu hồi đã làm thật, không chỉ đề nghị', 'Bước 3'],
               ['Kết quả các phép thử, kèm ảnh màn hình bị từ chối', 'Quyền cũ không còn dùng được', 'Bước 5']]),
    ('p', 'Email đề nghị gỡ quyền không phải bằng chứng hoàn tất: nó chỉ cho thấy đã có người yêu cầu.'),
    ('p', '⑤ Tóm tắt phương án mẫu'),
    ('p', 'Chị Hà chỉ cần xem 37 hồ sơ khiếu nại đang dở để bàn giao, không cần sửa hay xuất. Cán bộ CNTT gỡ ngay quyền xuất và quyền xem toàn bộ khách hàng Điện lực X; nếu chưa giao được hồ sơ cho người kế nhiệm, anh Tuấn và chủ sở hữu dữ liệu duyệt ngoại lệ chỉ xem đúng 37 hồ sơ, hết hạn sau 2 tuần. Chị Hà được cấp vai trò Kế hoạch – Điện lực Y theo ma trận quyền. Kiểm tra bằng tài khoản chị Hà: hồ sơ ngoài 37 hồ sơ và thao tác xuất đều phải bị từ chối. Lưu báo cáo quyền trước – sau, phiếu ngoại lệ và log gỡ quyền làm bằng chứng.'),
]


def th4_bai_mau(aid):
    make = {'h3': lambda v: {'t': 'h3', 'text': v, 'reveal': aid}, 'p': lambda v: paragraph(v, reveal=aid),
            'table': lambda v: table(v, reveal=aid), 'list': lambda v: steps(v, reveal=aid)}
    return [make[k](v) for k, v in TH4_BAI_MAU]


def revise(module):
    module = edit_tree(module)
    no = module['no']
    if not no:
        return module
    additions = json.loads((Path(__file__).parent / 'supplemental_exercises.json').read_text(encoding='utf-8'))
    lesson = additions[str(no)]
    # Giữ định nghĩa cũ để kết quả lớp đang có vẫn đọc đúng câu hỏi/đáp án.
    # Giảng viên có bộ câu hỏi mới để dùng trong buổi học.
    for activity in module['activities']:
        if activity['id'] == f'm{no:02d}-quiz':
            activity['title'] = 'Ôn câu hỏi cuối khóa (tùy chọn)'
    if no < 10:
        module['activities'].insert(0, {
            'id': f'm{no:02d}-check-v2', 'type': 'mcq', 'scope': 'student',
            'title': 'Kiểm tra nhanh: chọn cách xử lý',
            'intro': 'Chọn một phương án phù hợp nhất cho mỗi tình huống. Khi chữa bài, hãy giải thích vì sao bạn chọn cách đó.',
            'questions': [dict(q, id=f'q{i}') for i, q in enumerate(lesson['quiz'], 1)]})
    aid = f'm{no:02d}-case-v2'
    sid = f's{len(module["sections"])}'
    blocks = [paragraph('Bài làm cá nhân, khoảng 15–20 phút. Toàn bộ thông tin trong tình huống là giả lập.'),
              paragraph(lesson['scenario']), {'t': 'h3', 'text': 'Việc bạn cần làm'}]
    blocks.extend(paragraph(f'{i}. {task}') for i, task in enumerate(lesson['tasks'], 1))
    blocks += [paragraph('Bài cần nộp: điền ba mục trong mẫu trên web. Nêu rõ dữ kiện, cách xử lý và cách kiểm tra kết quả.'),
               paragraph('Tiêu chí chữa bài (10 điểm): hiểu đúng tình huống (3); đề xuất phù hợp và có lý do (4); kiểm chứng được kết quả (3). Giảng viên nhận xét, bài này không tự chấm điểm.'),
               {'t': 'h3', 'text': 'Gợi ý chữa bài', 'reveal': aid}, paragraph(lesson['answer'], reveal=aid)]
    module['sections'].append({'id': sid, 'title': lesson['title'], 'kind': 'practice', 'activity': aid, 'blocks': blocks})
    module['activities'].append({'id': aid, 'type': 'practice', 'scope': 'student', 'section': sid,
                                  'title': lesson['title'], 'intro': lesson['scenario'],
                                  'fields': [{'type': 'textarea', 'key': f'part{i}', 'label': task}
                                             for i, task in enumerate(lesson['tasks'], 1)]})
    for section in module['sections']:
        # “Nhóm” đứng riêng trong lịch tổ chức là cách làm bài, không phải nhóm dữ liệu.
        if section['title'] in ('Thông tin buổi học', 'Ghi chú cho giảng viên'):
            for b in section['blocks']:
                if b['t'] == 'table':
                    for row in b['rows']:
                        for cell in row:
                            if cell.get('plain') == 'Nhóm':
                                cell['plain'] = cell['html'] = 'Cá nhân'
        # Bảng lời giải CIA không xuất hiện trước khi học viên làm trò chơi.
        if no == 1:
            for b in section['blocks']:
                if b['t'] == 'table' and 'Sự việc giả lập' in str(b['rows'][0]):
                    b['reveal'] = 'm01-cia'
        # Kết quả phân tích log chỉ dành cho lúc chữa bài.
        if no == 9 and section['kind'] == 'practice' and section.get('activity') == 'm09-th10':
            for i, b in enumerate(section['blocks']):
                if b.get('plain') == 'Kết quả (rút gọn):':
                    b['reveal'] = 'm09-th10'
                    if i + 1 < len(section['blocks']):
                        section['blocks'][i + 1]['reveal'] = 'm09-th10'
        # Bài làm mẫu đặt ngay sau bảng đáp án gợi ý, trước điểm chữa bài.
        if section.get('activity') == 'm03-th4':
            blocks = section['blocks']
            at = next(i for i, b in enumerate(blocks) if b['t'] == 'table' and b.get('reveal') == 'm03-th4') + 1
            blocks[at:at] = th4_bai_mau('m03-th4')
        if section['kind'] == 'practice' and section.get('activity', '').endswith(tuple(f'-th{i}' for i in range(1, 12))):
            section['blocks'].insert(0, paragraph('Bạn làm và nộp bài cá nhân theo mẫu trên web. Lưu file, ảnh minh chứng trên máy; ghi tên file và kết quả kiểm tra vào bài làm. Khi chữa bài, giảng viên có thể yêu cầu bạn mở file để đối chiếu.'))
    return add_labs(module)
