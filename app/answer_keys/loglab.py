"""Đáp án bài 10.000 dòng. Tài liệu chỉ nằm ngoài static và API học viên."""
import html
from pathlib import Path
from .kit import P

BASE = Path(__file__).with_name('log_investigation')


def document_sections(filename):
    """Hiển thị nội dung markdown như văn bản an toàn, giữ tiêu đề để dễ tra cứu."""
    sections, blocks, title = [], [], 'Tài liệu giảng viên'
    for line in (BASE / filename).read_text(encoding='utf-8').splitlines():
        if line.startswith(('# ', '## ', '### ')):
            if blocks:
                sections.append({'title': title, 'blocks': blocks, 'private': True})
            title, blocks = line.lstrip('# ').strip(), []
        elif line.strip():
            blocks.append(P(html.escape(line)))
    if blocks:
        sections.append({'title': title, 'blocks': blocks, 'private': True})
    return sections


KEYS = {'m09-loglab-v1': {
    'summary': 'Bản đơn giản cho lớp trình độ trung bình: chấm việc có event_id, chép đúng giá trị trong log và biết nói điều chưa chắc. Có 60 tình huống thiết kế, không phải 60 sự cố xác nhận; học viên chỉ cần 5 phát hiện. Không gán người thật từ tên tài khoản.',
    'fields': {
        'pham_vi': '10.000 dòng; 29 nguồn; 5 vùng; 20–29/10/2026, giờ +07:00. Một dòng đọc kỹ trả lời đủ 5 câu: khi nào (ts), tài khoản (actor_id), từ đâu (src_ip/device_id), làm gì (event_type/resource_id), kết quả (result và details). Đủ 5 câu có giá trị thật từ log: 1,5 điểm.',
        'ho_so': 'Năm phát hiện dễ tìm bằng gợi ý: S16 (tìm anyone: EVT004405 chia sẻ file CONFIDENTIAL anyone_with_link, expiry null; EVT004413/4414/4420 guest tải về); S01 (tìm public_read: EVT000354 file orders public_read=true, EVT000355–358 guest tải không xác thực); S50 (tìm disabled: EVT009369 tắt luật, change_ticket null; EVT009371 xuất 8700 dòng, alert_fired=false); S34 (approved_ticket null: nv_bh_hn_01 xuất 200–249 dòng mỗi ngày 22–29/10, proxy tải lên personal-drive.example); S21 (nguồn backup: EVT000036 backup failure quota, EVT007093 restore_test failure, last_verified_restore 2026-09-12). Thao tác INFO đáng lo: S38 (EVT000315 miễn MFA không hạn, EVT002280 đăng nhập bypassed_by_policy từ unmanaged-admin-64), hoặc S16/S50. Mỗi phát hiện 0,8 điểm: có event và giá trị thật 0,4; lý do và việc làm tiếp hợp lý 0,4. Phát hiện khác có bằng chứng đúng vẫn được tính.',
        'phan_bien': 'Mẫu S44: EVT005812 đăng nhập 22:10 qua VPN công ty, passkey; EVT005816 xuất 10420 dòng nhưng có ticket FIN-9812, không có PII; EVT005817 người quản lý duyệt cửa sổ 22:00–23:00. Hạ mức nghi ngờ nhưng vẫn nên xác nhận ticket. Có thể dùng S46 (EVT006233–6236 gõ sai rồi MFA thành công) hoặc S45 (EVT005369/5370 tên O\'Brien, truy vấn tham số hóa). Chấm 1,5 nếu nêu nghi ban đầu, event xem thêm và lý do đổi hoặc giữ nhận định.',
        'timeline': 'Mẫu S50 (2 nguồn): EVT009369 29/10 08:30 siem tắt luật → EVT009371 08:32:40 audit xuất 8700 dòng, alert_fired=false → EVT009372 08:33 siem suppressed_alert_count=1. Nối bằng thời gian sát nhau và trạng thái luật; khác tài khoản (nv_it_01 tắt, nv_bh_dn_01 xuất) nên chưa chứng minh thông đồng. Mẫu khác: S16 (collaboration → storage), S44 (identity → audit). Đủ 3 event, 2 nguồn và một câu liên kết: 1,5 điểm.',
        'ban_giao': 'Ví dụ: (1) thu hồi link anyone/public của file khách hàng và kiểm tra ai đã tải; (2) bật lại luật cảnh báo, hỏi IT vì sao tắt không có ticket; (3) báo quản trị hệ thống về sao lưu lỗi và chưa khôi phục được. Giữ bản sao log gốc kèm SHA-256 và các event đã nêu. Hỏi trưởng bộ phận an toàn thông tin, IT vận hành, quản lý chi nhánh. Tối đa 150 từ; ưu tiên rõ, có bằng chứng: 1,5 điểm.',
    },
    'sections': document_sections('kich_ban.md') + document_sections('dap_an.md'),
}}
