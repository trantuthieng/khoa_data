"""Bài điều tra buổi 9; giữ mã bài cũ để không ảnh hưởng bài đã nộp."""
from beginner_labs import append_section, p

AID = 'm09-loglab-v1'


def add_log_investigation(module):
    if module['no'] != 9 or any(a['id'] == AID for a in module['activities']):
        return module
    blocks = [
        p('Bạn nhận ca rà soát 10 ngày nhật ký của website, cổng nội bộ, quản trị bán hàng, báo cáo và hạ tầng. Làm cá nhân, khoảng 90 phút. Dữ liệu hoàn toàn giả lập. Bộ này độc lập với log 17 dòng của tình huống điện lực.'),
        {'t': 'p', 'plain': 'Mở bàn điều tra 10.000 dòng nhật ký',
         'html': '<a class="btn" href="/static/labs/logs/index.html" target="_blank" rel="noopener">🔎 Mở bàn điều tra 10.000 dòng nhật ký</a>'},
        p('Bàn điều tra có ô tìm kiếm, bộ lọc theo nguồn/ngày/mức log và nút xem chi tiết từng dòng. Không cần cài phần mềm, không cần đọc hết 10.000 dòng. Bản nháp lưu trên trình duyệt; bấm Chép báo cáo rồi dán vào các ô dưới đây và Nộp bài.'),
        {'t': 'h3', 'text': 'Bốn bước làm bài'},
        p('1. Làm quen (10 phút): ghi tổng số dòng, số nguồn, khoảng ngày. Mở một dòng bất kỳ, đọc cả phần details và trả lời: khi nào, tài khoản nào, từ đâu, làm gì, kết quả ra sao.'),
        p('2. Tìm dấu hiệu (45 phút): tìm 5 phát hiện, thuộc ít nhất 3 nhóm khác nhau (đăng nhập; quyền; chia sẻ dữ liệu; web/CSDL; sao lưu; giám sát/log). Ít nhất 1 phát hiện là thao tác thành công (INFO) nhưng vẫn đáng lo.'),
        p('Mỗi phát hiện ghi 4 dòng: (a) event_id và nguồn; (b) log cho thấy gì, chép trường và giá trị; (c) vì sao đáng lo, có cách giải thích hợp lệ nào không; (d) ưu tiên Cao/Vừa/Thấp và việc nên làm tiếp.'),
        p('Gợi ý chỗ bắt đầu: tìm “anyone” hoặc “public_read” (file mở cho người ngoài?); tìm “disabled” (cơ chế bảo vệ bị tắt?); tìm "approved_ticket":null (xuất dữ liệu không có phê duyệt?); chọn nguồn backup và xem các dòng failure; tìm “unmanaged” (thiết bị ngoài quản lý?). Thấy dòng lạ thì bấm vào tài khoản để xem tài khoản đó còn làm gì.'),
        p('3. Kiểm tra lại (15 phút): chọn 1 dòng thoạt nhìn đáng ngờ (xuất nhiều, ngoài giờ, nhập sai mật khẩu…), tìm thêm dòng liên quan và giải thích vì sao bạn hạ mức nghi ngờ hoặc vẫn giữ nghi ngờ.'),
        p('4. Bàn giao (20 phút): ghim 3–5 event của một phát hiện, từ ít nhất 2 nguồn, để lập một timeline. Viết bàn giao tối đa 150 từ: 3 việc ưu tiên, bằng chứng cần giữ, cần hỏi ai hoặc bộ phận nào.'),
        p('Lưu ý: tên tài khoản trong log chưa chứng minh ai đã thao tác; HTTP 200 hoặc không có cảnh báo chưa chứng minh an toàn. Thời gian trong log đã có +07:00, không cộng thêm 7 giờ.'),
        p('Thang 10 điểm: làm quen dữ liệu 1,5; năm phát hiện có bằng chứng 4; kiểm tra lại 1,5; timeline 1,5; bàn giao 1,5. Muốn làm thêm: tìm 8 phát hiện hoặc rà từng nguồn ở mục “Rà theo nguồn” của bàn điều tra.'),
        p('Giảng viên mở 📘 Đáp án để xem 60 tình huống, thẻ gợi ý, lưu ý S43 và nhịp dạy. Bài này bổ sung, không thay bài 17 dòng đã có.', teacher=True),
    ]
    fields = [
        {'type': 'textarea', 'key': k, 'label': label, 'hint': hint}
        for k, label, hint in [
            ('pham_vi', '1. Làm quen dữ liệu', 'Số dòng, số nguồn, khoảng ngày; một dòng đã đọc kỹ (event_id) và 5 câu: khi nào, tài khoản nào, từ đâu, làm gì, kết quả.'),
            ('ho_so', '2. Năm phát hiện', 'Mỗi phát hiện 4 dòng: event_id/nguồn; log cho thấy gì; vì sao đáng lo hoặc có thể hợp lệ; ưu tiên và việc làm tiếp.'),
            ('phan_bien', '3. Kiểm tra lại một nghi vấn', 'Ban đầu tôi nghi … vì … Sau khi xem thêm EVT… tôi thấy … nên tôi …'),
            ('timeline', '4. Một timeline', 'Dán phần timeline từ báo cáo (3–5 event, ít nhất 2 nguồn) và ghi một câu: các dòng này nối với nhau bằng gì.'),
            ('ban_giao', '5. Bàn giao ca', 'Tối đa 150 từ: 3 việc ưu tiên, bằng chứng cần giữ, cần hỏi ai.')
        ]
    ]
    append_section(module, 'Ca trực điều tra – 10.000 dòng nhật ký', blocks, {
        'id': AID, 'type': 'practice', 'scope': 'student',
        'title': 'Ca trực điều tra – 10.000 dòng nhật ký',
        'intro': 'Tìm dấu hiệu bất thường trong log, ghi rõ bằng chứng và kiểm tra lại trước khi kết luận.',
        'fields': fields,
        'instructions': [b for b in blocks if not b.get('teacher')],
    })
    return module
