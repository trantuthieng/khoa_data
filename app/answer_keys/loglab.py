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
    'summary': 'Chấm bằng chứng, phạm vi và cách phản biện. Có 60 tình huống thiết kế, không phải 60 sự cố xác nhận. Không yêu cầu tìm hết; không gán người thật từ tên tài khoản.',
    'fields': {
        'pham_vi': '10.000 bản ghi; 29 nguồn; 5 vùng; 20–29/10/2026. INFO=9637, WARN=337, ERROR=25, DEBUG=1. Rà cả nguồn hiếm và nhiều ngày. Phiếu phải ghi truy vấn và event thực, không chấm đủ phạm vi chỉ bằng số dòng đã mở.',
        'ho_so': 'Một bộ tám hồ sơ có thể chọn: S01 (EVT000354–358, ACL công khai và tải); S38 (EVT000315/EVT002280, miễn MFA và đăng nhập); S34 (16 event xuyên ngày, xuất nhỏ và proxy); S21 (backup/restore lặp lỗi); S12 (EVT003381–3386, API khác chi nhánh); S27 (EVT007716–7718, Member và dữ liệu vượt RLS); S31 (EVT008599–8600, chữ ký webhook và cập nhật thanh toán); S50 (EVT009369/9371/9372, tắt luật và bỏ cảnh báo). Mỗi hồ sơ cần nêu giới hạn, kiểm chứng và hành động; các event khác có lập luận đúng đều được chấp nhận. Chi tiết đầy đủ từng tình huống ở dưới.',
        'phan_bien': 'Đối chứng S44: EVT005812/5816/5817, ngoài giờ và 10420 dòng nhưng có VPN, passkey, ticket, scope và thời gian duyệt. S45: EVT005369/5370, tên có nháy nhưng query tham số hóa. Chưa kết luận S43: EVT004300/4303/4305, ts khác thứ tự hiệu lực quyền, có effective_at/cache/clock skew; cần policy và đồng bộ đồng hồ.',
        'timeline': 'Timeline 1: S38, EVT000315 ngày 20/10 07:35 +07:00 (iam, ngoại lệ MFA) → EVT002280 ngày 22/10 07:35 +07:00 (identity, bypass theo policy). Timeline 2: S50, EVT009369 ngày 29/10 08:30 (siem, disabled) → EVT009371 08:32:40 (audit, xuất 8700, alert_fired=false) → EVT009372 08:33 (siem, suppressed=1). Bài học viên cần chép cả ts và ingested_at từ log và giải thích liên kết, không chỉ nêu số event.',
        'ban_giao': 'Ưu tiên đánh giá đường dữ liệu công khai, phiên quản trị ngoại lệ và giám sát bị tắt. Giữ log gốc, hash, cấu hình, metadata file/phiên/ticket; phối hợp hạn chế ảnh hưởng theo thẩm quyền. Đề xuất cảnh báo thay đổi trạng thái luật giám sát, có ticket, thời hạn ngoại lệ và đầu mối trực; thử trên dữ liệu nền trước khi dùng vận hành. Không suy ra S50 là nguyên nhân duy nhất của phản ánh S58.',
    },
    'sections': document_sections('kich_ban.md') + document_sections('dap_an.md'),
}}
