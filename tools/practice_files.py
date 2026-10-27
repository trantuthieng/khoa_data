"""Tạo file luyện tập cho Thực hành 6 và 7 (toàn bộ dữ liệu giả lập).

    python tools/practice_files.py

Kết quả nằm trong app/static/labs/ để học viên tải từ bài học. Cùng seed cho cùng một file,
nên số liệu chữa bài trong giáo trình và đáp án giảng viên luôn khớp. Cần openpyxl.
"""
import csv
import random
from pathlib import Path

from openpyxl import Workbook

OUT = Path(__file__).resolve().parent.parent / "app" / "static" / "labs"


def bao_cao_thang():
    """Thực hành 6: BaoCao_Thang.xlsx – sheet VanHanh ẩn, cột GhiChuNoiBo ẩn."""
    random.seed(2026)
    vung_ds = ["Phường Bắc", "Phường Nam", "Xã Đông", "Xã Tây"]
    ho = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Võ", "Đặng", "Bùi"]
    dem = ["Văn", "Thị", "Minh", "Thu", "Đức", "Ngọc"]
    ten = ["An", "Bình", "Chi", "Dũng", "Hà", "Khoa", "Lan", "Nam", "Phúc", "Trang"]

    wb = Workbook()
    th = wb.active
    th.title = "TongHop"
    ct = wb.create_sheet("ChiTiet")
    vh = wb.create_sheet("VanHanh")
    ct.append(["MaKH", "TenKH", "DienThoai", "DiaChi", "Vung", "kWh_T10", "SoTienNo", "SoNgayQuaHan", "GhiChuNoiBo"])
    tong = {v: [0, 0] for v in vung_ds}
    for i in range(1, 401):
        vung = random.choice(vung_ds)
        kwh = random.randint(60, 900)
        no = random.choice([0, 0, 0, random.randint(150, 2500) * 1000])
        qua_han = random.randint(5, 60) if no else 0
        ct.append([f"KH{i:05d}", f"{random.choice(ho)} {random.choice(dem)} {random.choice(ten)}", f"0900{i:06d}",
                   f"Số {random.randint(1, 200)}, tổ {random.randint(1, 30)}, {vung}", vung, kwh, no, qua_han,
                   random.choice(["", "", "Hay khiếu nại", "Đã hẹn trả", "Hộ khó khăn"])])
        tong[vung][0] += 1
        tong[vung][1] += kwh
    ct.column_dimensions["I"].hidden = True
    th.append(["Vung", "SoHo", "SanLuong_kWh"])
    for v in vung_ds:
        th.append([v, *tong[v]])
    vh.append(["Tram", "Vung", "TaiCaoNhat_%", "SoLanMatDien_T10"])
    for k, v in enumerate(vung_ds, 1):
        vh.append([f"TBA-{k:02d}", v, random.randint(55, 98), random.randint(0, 6)])
    vh.sheet_state = "hidden"
    wb.save(OUT / "BaoCao_Thang.xlsx")
    no_count = sum(1 for r in ct.iter_rows(min_row=2, values_only=True) if r[6])
    print("BaoCao_Thang.xlsx:", ct.max_row - 1, "hộ;", no_count, "hộ còn nợ;", tong)


def san_luong_q3():
    """Thực hành 7: DLX_SanLuong_Q3.csv – Cảng Mới chỉ có một xưởng; một hộ An Phú dùng điện rất lớn."""
    random.seed(7)
    phuong_ds = {"An Phú": 160, "Bình Minh": 140, "Đông Hòa": 120, "Tân Lập": 150, "Phú Thượng": 110, "Cảng Mới": 0}
    ho = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Võ", "Đặng", "Bùi"]
    ten = ["An", "Bình", "Chi", "Dũng", "Hà", "Khoa", "Lan", "Nam", "Phúc", "Trang"]
    khach = []

    def them(phuong, loai, kwh_tb):
        i = len(khach) + 1
        khach.append({"ma_kh": f"PE{i:06d}", "ho_ten": f"{random.choice(ho)} Văn {random.choice(ten)}",
                      "dien_thoai": f"0900{i:06d}", "dia_chi": f"Số {random.randint(1, 300)}, {phuong}",
                      "phuong": phuong, "loai_kh": loai, "kwh_tb": kwh_tb})

    for p, n in phuong_ds.items():
        for _ in range(n):
            them(p, "Sinh hoạt", random.randint(120, 450))
        for _ in range(random.randint(8, 15) if n else 0):
            them(p, "Kinh doanh", random.randint(600, 2500))
    them("An Phú", "Sinh hoạt", 3200)
    them("Cảng Mới", "Sản xuất", 42000)
    with open(OUT / "DLX_SanLuong_Q3.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["ma_kh", "ho_ten", "dien_thoai", "dia_chi", "phuong", "loai_kh", "thang", "kwh", "so_tien_no"])
        for k in khach:
            for thang in ("2026-07", "2026-08", "2026-09"):
                kwh = round(k["kwh_tb"] * random.uniform(0.85, 1.15))
                no = random.choice([0, 0, 0, 0, round(kwh * 2.5) * 1000])
                w.writerow([k["ma_kh"], k["ho_ten"], k["dien_thoai"], k["dia_chi"], k["phuong"], k["loai_kh"], thang, kwh, no])
    print("DLX_SanLuong_Q3.csv:", len(khach), "khách hàng,", len(khach) * 3, "dòng")


if __name__ == "__main__":
    bao_cao_thang()
    san_luong_q3()
