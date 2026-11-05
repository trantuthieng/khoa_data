"""Danh mục file DSL Dify mẫu của khóa AI Agent.

Tệp nằm ở answer_keys/dify_dsl, ngoài /static, nên học viên chỉ tải được sau khi giảng viên chia sẻ cho lớp.
Đây là file xuất từ Dify 1.18.0 rồi bỏ mã kho và công cụ riêng của workspace; sửa prompt trong bài thì xuất lại.
"""
from pathlib import Path

DSL_DIR = Path(__file__).parent / "answer_keys" / "dify_dsl"
_NHAP = "Trên Dify: Studio → Create → Import App, chọn file."
_MO_HINH = "Workspace cần có mô hình OpenAI {}; không có thì đổi mô hình ở các khối."

DSL_FILES = {
    "b3-tro-ly": {
        "course": "ai-agent", "module": 3, "file": "b3_tro_ly_tuyen_sinh.yml",
        "title": "Trợ lý tuyển sinh, bản hoàn chỉnh Buổi 3",
        "desc": "Chatflow đủ 4 nhánh, tính điểm bằng Code, Evaluator và biến hội thoại.",
        "steps": [_NHAP, _MO_HINH.format("gpt-4.1-mini"),
                  "Chọn kho SPD 2026 ở 3 khối: Tìm tài liệu SPD 2026, KR Đối chiếu, KR quy định. Chưa chọn thì trợ lý chỉ báo chưa đủ thông tin."],
    },
    "b4-agent": {
        "course": "ai-agent", "module": 4, "file": "b4_agent_tuyen_sinh.yml",
        "title": "Agent tuyển sinh, bản hoàn chỉnh Buổi 4",
        "desc": "Agent có prompt đủ quy tắc và công cụ giờ hiện tại. Kho và 4 công cụ API phải thêm sau khi nhập.",
        "steps": [_NHAP, "Workspace cần có mô hình OpenAI gpt-4.1; không có thì đổi mô hình ở góc trên bên phải.",
                  "Tạo công cụ Swagger API theo chặng 2 của Buổi 4 nếu workspace chưa có.",
                  "Trong Agent, thêm kho SPD 2026 ở Knowledge và 4 công cụ: tinh_diem_xet_tuyen, tra_ho_so, tim_thong_bao, tao_nhap_lich_tu_van."],
    },
    "b4-http": {
        "course": "ai-agent", "module": 4, "file": "b4_goi_api_http.yml",
        "title": "Tra hồ sơ bằng HTTP Request, Buổi 4",
        "desc": "Chatflow gọi thẳng API tra hồ sơ, IF đọc status_code 200, 403, 404.",
        "steps": [_NHAP, _MO_HINH.format("gpt-4.1-mini"), "Không cần cấu hình thêm. Thử: Hồ sơ TS26-0001, em sinh 2008-03-15."],
    },
    "b5-phong": {
        "course": "ai-agent", "module": 5, "file": "b5_phong_tuyen_sinh_ao.yml",
        "title": "Phòng tuyển sinh ảo, bản chặng 6 Buổi 5",
        "desc": "Router và Writer ⇄ Editor có căn cứ từ kho. Nhánh Tư vấn, Hồ sơ là chỗ chờ nối luồng của Buổi 3, 4.",
        "steps": [_NHAP, _MO_HINH.format("gpt-4.1-mini"), "Chọn kho SPD 2026 ở khối KR căn cứ."],
    },
}


def dsl_out(key, shared=None):
    f = DSL_FILES[key]
    out = {"key": key, "module": f["module"], "file": f["file"], "title": f["title"], "desc": f["desc"], "steps": f["steps"]}
    if shared is not None:
        out["shared"] = shared
    return out
