"""Bài điều tra buổi 9; giữ mã bài cũ để không ảnh hưởng bài đã nộp."""
from beginner_labs import append_section, p

AID = 'm09-loglab-v1'


def add_log_investigation(module):
    if module['no'] != 9 or any(a['id'] == AID for a in module['activities']):
        return module
    blocks = [
        p('Bạn nhận ca rà soát 10 ngày hoạt động của website, cổng nội bộ, quản trị bán hàng, báo cáo và hạ tầng. Làm cá nhân, khoảng 105 phút (chưa tính giờ nghỉ). Dữ liệu hoàn toàn giả lập. Bộ này độc lập với log 17 dòng của tình huống điện lực.'),
        {'t': 'p', 'plain': 'Mở bàn điều tra 10.000 dòng nhật ký',
         'html': '<a class="btn" href="/static/labs/logs/index.html" target="_blank" rel="noopener">🔎 Mở bàn điều tra 10.000 dòng nhật ký</a>'},
        p('Bàn điều tra có tìm kiếm toàn văn, bộ lọc, thống kê đủ nguồn/ngày, đọc JSON chi tiết, truy theo tài khoản/phiên/đối tượng, ghim bằng chứng và lập timeline. Không cần cài phần mềm. Bản nháp chỉ lưu trên trình duyệt; bấm Chép báo cáo rồi dán vào các ô dưới đây và Nộp bài để gửi giảng viên.'),
        {'t': 'h3', 'text': 'Năm chặng làm bài'},
        p('1. Nhận ca (15 phút): kiểm tra số dòng, nguồn, vùng, loại sự kiện, thời gian và cách sắp xếp. Đọc đầy đủ một bản ghi mỗi vùng, kể cả details.'),
        p('2. Quét phạm vi (25 phút): rà mọi nguồn và từng ngày. Mỗi nguồn/ngày phải có nhận xét cùng truy vấn hoặc event làm căn cứ. Nguồn nhiều dòng cần thống kê toàn nguồn và đọc ngoại lệ; mở đủ trang không chứng minh đã hiểu log.'),
        p('3. Điều tra (40 phút): ít nhất tám phát hiện, bao phủ năm trong sáu hướng: danh tính/phiên; quyền/nghiệp vụ; dữ liệu/chia sẻ; web/API/DB; vận hành/phục hồi; giám sát/bằng chứng. Có một chuỗi xuyên ngày, một thao tác thành công hoặc INFO đáng điều tra, một vấn đề của cơ chế giám sát hoặc chất lượng log.'),
        p('4. Phản biện (15 phút): tìm hai nghi vấn có căn cứ hạ mức nghi ngờ và một trường hợp chưa đủ dữ liệu kết luận. Ghi điều khiến bạn đổi nhận định.'),
        p('5. Bàn giao (10 phút): hai timeline, mỗi timeline ít nhất hai nguồn, một timeline xuyên ngày; chọn ba ưu tiên và viết bàn giao tối đa 300 từ. Đề xuất một quy tắc cảnh báo, điều kiện loại trừ và người nhận.'),
        p('Mỗi phát hiện ghi event_id, source, trường/giá trị, điều biết chắc, giả thuyết, kiểm chứng tiếp, CIA, ưu tiên và hành động đúng thẩm quyền. Tìm lại toàn file theo tài khoản, phiên, đối tượng và trường đích trong details; không chỉ tìm ERROR.'),
        p('Giữ nguyên log gốc. ts là giờ nguồn, ingested_at là giờ nhận; không cộng 7 giờ cho thời điểm đã có +07:00. Đồng hồ lệch có thể khiến sắp theo ts vẫn sai thứ tự thực tế. Tài khoản không chứng minh người thật; không có cảnh báo không chứng minh an toàn.'),
        p('Thang 10 điểm: rà nguồn/ngày 2; tám phát hiện có bằng chứng 3; hai timeline 2; phản biện 1,5; bàn giao và kiểm chứng tiếp 1,5. Bài mở rộng: 15 phát hiện, ba timeline và ba đối chứng.'),
        p('Giảng viên mở 📘 Đáp án để xem 60 tình huống, thẻ thử thách, lưu ý S43 và nhịp dạy. Bài này bổ sung, không thay bài 17 dòng đã có.', teacher=True),
    ]
    fields = [
        {'type': 'textarea', 'key': k, 'label': label, 'hint': hint}
        for k, label, hint in [
            ('pham_vi', '1–2. Bản đồ và phiếu rà soát nguồn/ngày', 'Dán báo cáo từ bàn điều tra; ghi truy vấn, mẫu nền, ngoại lệ và giới hạn phạm vi.'),
            ('ho_so', '3. Tám hồ sơ điều tra', 'Mỗi hồ sơ có event_id/source, dữ kiện, giả thuyết, kiểm chứng, CIA, ưu tiên, hành động.'),
            ('phan_bien', '4. Hai đối chứng và một trường hợp chưa thể kết luận', 'Ban đầu nghi gì; event nào làm đổi nhận định; còn thiếu gì?'),
            ('timeline', '5. Hai timeline nhiều nguồn', 'Ghi ts, ingested_at, event_id, nguồn, liên kết, giới hạn; một chuỗi xuyên ngày.'),
            ('ban_giao', 'Bàn giao ca và quy tắc cảnh báo', 'Tối đa 300 từ: ba ưu tiên, bằng chứng cần giữ, đầu mối, kiểm chứng và quy tắc cảnh báo.')
        ]
    ]
    append_section(module, 'Ca trực điều tra – 10.000 dòng nhật ký', blocks, {
        'id': AID, 'type': 'practice', 'scope': 'student',
        'title': 'Ca trực điều tra – 10.000 dòng nhật ký',
        'intro': 'Rà đủ phạm vi, truy vết nhiều nguồn và phản biện bằng bằng chứng.',
        'fields': fields,
        'instructions': [b for b in blocks if not b.get('teacher')],
    })
    return module
