"""Bài ngắn theo slide 58–81. Dữ liệu giả lập, lời giải chỉ ở vùng công bố."""
import html
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CUSTOMERS = [
    {'id': f'KH{i:03}', 'name': f'Khach mau {i}', 'phone': f'0900000{i:03}',
     'address': f'So {i}, duong mau', 'region': region, 'kwh': kwh}
    for i, (region, kwh) in enumerate([
        ('DV_A', 100), ('DV_A', 150), ('DV_A', 200),
        ('DV_B', 250), ('DV_B', 300), ('DV_C', 400)], 1)
]
DIM_DONVI = [{'MaDonVi': v, 'TenDonVi': name} for v, name in
             [('DV_A', 'Dien luc A'), ('DV_B', 'Dien luc B'), ('DV_C', 'Dien luc C')]]
DIM_NGAY = [{'Ngay': '2026-09-01', 'Thang': '2026-09'}, {'Ngay': '2026-09-02', 'Thang': '2026-09'}]
FACT = [{'MaKH': r['id'], 'MaDonVi': r['region'], 'Ngay': '2026-09-01', 'kWh': r['kwh']} for r in CUSTOMERS]
FACT += [{'MaKH': 'KH001', 'MaDonVi': 'DV_A', 'Ngay': '2026-09-02', 'kWh': 110},
         {'MaKH': 'KH004', 'MaDonVi': 'DV_B', 'Ngay': '2026-09-02', 'kWh': 260}]


def connect_sample():
    import sqlite3
    connection = sqlite3.connect(':memory:')
    connection.execute('CREATE TABLE customers (id TEXT, name TEXT, phone TEXT, address TEXT, region TEXT, kwh INTEGER)')
    connection.executemany('INSERT INTO customers VALUES (:id,:name,:phone,:address,:region,:kwh)', CUSTOMERS)
    return connection


# Mỗi bài: tên, kỹ năng, hướng dẫn, mã điền tiếp, lời giải và kết quả để kiểm chứng.
SQL = [
    dict(title='SQL 01 – Chỉ lấy hai cột cần dùng', goal='Chọn cột bằng SELECT.',
         tasks=['Thay hai chỗ trống để chỉ lấy region và kwh, không lấy tên hay điện thoại.', 'Chạy truy vấn và ghi số dòng, tên hai cột kết quả.', 'Giải thích vì sao không dùng SELECT * khi người nhận chỉ cần hai cột.'],
         starter='SELECT ___, ___ FROM customers ORDER BY id;',
         solution='SELECT region, kwh FROM customers ORDER BY id;',
         expected=[['DV_A',100],['DV_A',150],['DV_A',200],['DV_B',250],['DV_B',300],['DV_C',400]],
         answer='Có 6 dòng, hai cột region và kwh. Việc bỏ các cột không cần giúp giảm dữ liệu trong bản xuất, chưa tự chứng minh dữ liệu đã ẩn danh.'),
    dict(title='SQL 02 – Chỉ lấy đơn vị được giao', goal='Lọc dòng bằng WHERE.',
         tasks=['Điền điều kiện để chỉ lấy DV_A.', 'Ghi ba mã khách hàng và sản lượng tìm được.', 'Giải thích: lọc trong câu SQL có thay thế quyền của tài khoản trên hệ thống không?'],
         starter="SELECT id, kwh FROM customers WHERE region = '___' ORDER BY id;",
         solution="SELECT id, kwh FROM customers WHERE region = 'DV_A' ORDER BY id;",
         expected=[['KH001',100],['KH002',150],['KH003',200]],
         answer='Có KH001, KH002, KH003. WHERE chỉ lọc kết quả câu hỏi này. Tài khoản vẫn cần được cấp đúng quyền và phạm vi, không dựa vào việc người dùng tự nhớ thêm điều kiện.'),
    dict(title='SQL 03 – Lọc mức sản lượng', goal='Dùng điều kiện >=.',
         tasks=['Lấy id và kwh của khách có sản lượng từ 250 kWh trở lên.', 'Ghi kết quả theo thứ tự mã khách hàng.', 'Cho biết trường hợp đúng 250 kWh có được lấy không và vì sao.'],
         starter='SELECT id, kwh FROM customers WHERE kwh ___ 250 ORDER BY id;',
         solution='SELECT id, kwh FROM customers WHERE kwh >= 250 ORDER BY id;',
         expected=[['KH004',250],['KH005',300],['KH006',400]], answer='Có 3 khách. Dấu >= gồm cả giá trị bằng 250. Trong công việc thật còn phải lọc đúng phạm vi đơn vị đã được cấp.'),
    dict(title='SQL 04 – Đếm khách và cộng sản lượng', goal='Dùng COUNT và SUM trên bảng mỗi khách một dòng.',
         tasks=['Hoàn thành COUNT(*) và SUM(kwh) trong truy vấn.', 'Ghi số khách và tổng kWh.', 'Nêu vì sao đếm dòng ở bảng này bằng số khách, còn bảng có nhiều ngày thì có thể khác.'],
         starter='SELECT ___(*) AS so_kh, ___(kwh) AS tong_kwh FROM customers;',
         solution='SELECT COUNT(*) AS so_kh, SUM(kwh) AS tong_kwh FROM customers;',
         expected=[[6,1400]], answer='Bảng này có 6 khách, tổng 1.400 kWh. Mỗi id chỉ xuất hiện một dòng. Khi một khách có nhiều dòng theo ngày, phải xác định cách đếm phù hợp, chẳng hạn COUNT(DISTINCT id).'),
    dict(title='SQL 05 – Tổng hợp theo đơn vị', goal='Gộp bằng GROUP BY, bám slide 62.',
         tasks=['Điền cùng tên cột ở SELECT và GROUP BY.', 'Ghi số khách và tổng kWh của từng đơn vị.', 'Kiểm tra kết quả không có cột tên hoặc điện thoại.'],
         starter='SELECT ___, COUNT(*) AS so_kh, SUM(kwh) AS tong_kwh\nFROM customers GROUP BY ___ ORDER BY region;',
         solution='SELECT region, COUNT(*) AS so_kh, SUM(kwh) AS tong_kwh FROM customers GROUP BY region ORDER BY region;',
         expected=[['DV_A',3,450],['DV_B',2,550],['DV_C',1,400]], answer='DV_A: 3 khách, 450 kWh; DV_B: 2 khách, 550 kWh; DV_C: 1 khách, 400 kWh. Tổng vẫn là 1.400 kWh. Riêng DV_C có một khách nên số tổng hợp vẫn tiết lộ sản lượng của khách đó.'),
    dict(title='SQL 06 – Tìm nhóm nhỏ trước khi giao', goal='Dùng HAVING để kiểm tra kết quả đã gộp.',
         tasks=['Lấy các đơn vị có ít nhất 2 khách bằng HAVING COUNT(*) >= 2.', 'So sánh tổng còn lại với 1.400 kWh ban đầu.', 'Giải thích vì sao không được tự coi ngưỡng 2 là tiêu chuẩn ẩn danh hoặc bỏ DV_C mà không báo.'],
         starter='SELECT region, COUNT(*) AS so_kh, SUM(kwh) AS tong_kwh\nFROM customers GROUP BY region HAVING ___ ORDER BY region;',
         solution='SELECT region, COUNT(*) AS so_kh, SUM(kwh) AS tong_kwh FROM customers GROUP BY region HAVING COUNT(*) >= 2 ORDER BY region;',
         expected=[['DV_A',3,450],['DV_B',2,550]], answer='Còn DV_A và DV_B, tổng 1.000 kWh, thiếu 400 kWh của DV_C. Số 2 chỉ để luyện cú pháp trên bộ nhỏ. Thực tế cần tiêu chí của đơn vị và đánh giá nhận diện, áp đảo, phép trừ; phải giải thích phần dữ liệu bị loại.'),
    dict(title='SQL 07 – Ghép hai điều kiện', goal='Giới hạn đơn vị và mức sản lượng bằng AND.',
         tasks=['Chỉ lấy khách DV_A có sản lượng từ 150 kWh trở lên.', 'Ghi mã và sản lượng kết quả.', 'Nêu điều kiện nào giữ phạm vi đơn vị, điều kiện nào phục vụ nhu cầu phân tích.'],
         starter="SELECT id, kwh FROM customers\nWHERE region = 'DV_A' ___ kwh >= 150 ORDER BY id;",
         solution="SELECT id, kwh FROM customers WHERE region = 'DV_A' AND kwh >= 150 ORDER BY id;",
         expected=[['KH002',150],['KH003',200]], answer='KH002: 150, KH003: 200. Điều kiện region giữ phạm vi dữ liệu của truy vấn; kwh chọn mức cần phân tích. Quyền truy cập thực tế vẫn phải được hệ thống thực thi.'),
    dict(title='SQL 08 – Tìm một mã bằng tham số', goal='Truyền giá trị riêng bằng sqlite3, bám slide 66.',
         tasks=['Điền dấu ? và bộ giá trị (customer_id,) vào hai chỗ trống.', 'Chạy với KH002. Sau đó thử giá trị KH002-khong-ton-tai và ghi hai kết quả.', 'Giải thích vì sao không nối trực tiếp customer_id vào câu SQL.'],
         starter='customer_id = "KH002"\nquery = "SELECT region, kwh FROM customers WHERE id = ___"\nresult = connection.execute(query, ___).fetchall()\nprint(result)',
         solution='customer_id = "KH002"\nquery = "SELECT region, kwh FROM customers WHERE id = ?"\nresult = connection.execute(query, (customer_id,)).fetchall()\nprint(result)',
         expected=[['DV_A',150]], answer='KH002 trả về DV_A, 150; mã không tồn tại trả về danh sách rỗng. Dấu ? là chỗ truyền giá trị của sqlite3. Dấu phẩy trong (customer_id,) tạo bộ một phần tử. Tham số hóa tách lệnh và dữ liệu, vẫn cần kiểm tra đầu vào và quyền.')
]

PYTHON = [
    dict(title='Python 01 – Đọc sáu bản ghi mẫu', goal='Đọc danh sách và một trường, chưa cần pandas.',
         tasks=['Mở python_lab.py và giữ nguyên phần đọc customers.json.', 'Thêm lệnh in số phần tử của rows và region ở dòng đầu.', 'Ghi kết quả đã chạy; nếu chưa có Python, ghi dự đoán và nêu rõ chưa chạy.'],
         starter='print(len(___))\nprint(rows[0]["___"])',
         solution='print(len(rows))\nprint(rows[0]["region"])', expected=[6,'DV_A'], answer='Kết quả là 6 và DV_A. len(rows) đếm bản ghi. rows[0] là bản ghi đầu tiên. rows là dữ liệu giả lập đọc từ file cùng thư mục.'),
    dict(title='Python 02 – Che một số điện thoại', goal='Dùng lát cắt chuỗi như slide 63.',
         tasks=['Điền hai lát cắt để giữ 3 ký tự đầu, 3 ký tự cuối và chèn bốn dấu *.', 'Thử với 0900000001 và 0900000002.', 'Giải thích vì sao che điện thoại chưa đủ để gọi là ẩn danh.'],
         starter='def mask_phone(phone):\n    return phone[___] + "****" + phone[___]\nprint(mask_phone("0900000001"))\nprint(mask_phone("0900000002"))',
         solution='def mask_phone(phone):\n    return phone[:3] + "****" + phone[-3:]\nprint(mask_phone("0900000001"))\nprint(mask_phone("0900000002"))',
         expected=['090****001','090****002'], answer='Hai kết quả là 090****001 và 090****002. Các đoạn còn lại vẫn có thể giúp nối dữ liệu. Bài chỉ dùng chuỗi mẫu hợp lệ; nếu công việc có ô trống hoặc dữ liệu sai dạng thì cần xử lý riêng.'),
    dict(title='Python 03 – Bỏ hẳn cột không cần', goal='Tạo danh sách mới chỉ có region và kwh.',
         tasks=['Hoàn thành vòng lặp để clean chỉ còn hai trường region và kwh.', 'In số dòng và các khóa của bản ghi đầu tiên.', 'Cho biết dữ liệu gốc rows có bị xóa theo không.'],
         starter='clean = []\nfor r in rows:\n    clean.append({"region": r["___"], "kwh": r["___"]})\nprint(len(clean))\nprint(list(clean[0].keys()))',
         solution='clean = []\nfor r in rows:\n    clean.append({"region": r["region"], "kwh": r["kwh"]})\nprint(len(clean))\nprint(list(clean[0].keys()))',
         expected=[6,['region','kwh']], answer='Có 6 dòng, chỉ còn region và kwh. rows vẫn còn bản gốc, nên phải quản lý cả nơi giữ bản gốc và bản xuất; chỉ gửi clean nếu được duyệt.'),
    dict(title='Python 04 – Lọc một đơn vị', goal='Dùng for và if để chọn DV_A.',
         tasks=['Điền điều kiện ở if và tên danh sách cần append.', 'In các mã khách được chọn.', 'So sánh với SQL 02 và nêu điều giống nhau.'],
         starter='selected = []\nfor r in rows:\n    if r["region"] == "___":\n        ___.append(r["id"])\nprint(selected)',
         solution='selected = []\nfor r in rows:\n    if r["region"] == "DV_A":\n        selected.append(r["id"])\nprint(selected)',
         expected=[['KH001','KH002','KH003']], answer='KH001, KH002, KH003. if tương ứng với việc chọn dòng theo điều kiện WHERE trong SQL 02. Mã này xử lý danh sách đã tải về, không cấp hay thu hồi quyền hệ thống.'),
    dict(title='Python 05 – Cộng sản lượng theo đơn vị', goal='Dùng từ điển để tổng hợp, so với SQL 05.',
         tasks=['Điền kwh vào dòng cộng tổng.', 'In totals và so với tổng của SQL 05.', 'Chỉ ra đơn vị chỉ có một khách và giải thích rủi ro của tổng đó.'],
         starter='totals = {}\nfor r in rows:\n    region = r["region"]\n    totals[region] = totals.get(region, 0) + r["___"]\nprint(totals)',
         solution='totals = {}\nfor r in rows:\n    region = r["region"]\n    totals[region] = totals.get(region, 0) + r["kwh"]\nprint(totals)',
         expected=[{'DV_A':450,'DV_B':550,'DV_C':400}], answer='DV_A 450; DV_B 550; DV_C 400 kWh. DV_C chỉ có KH006 nên tổng cũng là sản lượng riêng của khách đó. Không tự kết luận bảng tổng hợp đã ẩn danh.'),
    dict(title='Python 06 – Xử lý ô điện thoại trống', goal='Kiểm tra đầu vào trước khi cắt chuỗi.',
         tasks=['Điền điều kiện để None, chuỗi trống và số quá ngắn trả về chuỗi trống.', 'Thử lần lượt None, chuỗi trống, 123 và 0900000001.', 'Giải thích vì sao không chuyển None thành chuỗi rồi đưa vào bản gửi.'],
         starter='def mask_phone(phone):\n    if phone is None:\n        return ""\n    phone = str(phone).strip()\n    if len(phone) < ___:\n        return ""\n    return phone[:3] + "****" + phone[-3:]\nfor value in [None, "", "123", "0900000001"]:\n    print(repr(mask_phone(value)))',
         solution='def mask_phone(phone):\n    if phone is None:\n        return ""\n    phone = str(phone).strip()\n    if len(phone) < 6:\n        return ""\n    return phone[:3] + "****" + phone[-3:]\nfor value in [None, "", "123", "0900000001"]:\n    print(repr(mask_phone(value)))',
         expected=['','','','090****001'], answer='Ba trường hợp đầu trả về chuỗi trống, trường hợp cuối là 090****001. Đây là quy tắc luyện cắt chuỗi, chưa phải bộ kiểm tra số điện thoại hợp lệ. Khi không cần điện thoại, bỏ cả cột vẫn phù hợp hơn việc che.'),
    dict(title='Python 07 – Đổi chuỗi số thành số', goal='Dùng int trước khi tính.',
         tasks=['Điền hàm chuyển kiểu để cộng ba chuỗi số.', 'Ghi tổng nhận được.', 'Nêu cách xử lý nếu gặp giá trị khong-ro thay vì âm thầm coi là 0.'],
         starter='raw = ["100", "150", "200"]\ntotal = 0\nfor value in raw:\n    total = total + ___(value)\nprint(total)',
         solution='raw = ["100", "150", "200"]\ntotal = 0\nfor value in raw:\n    total = total + int(value)\nprint(total)',
         expected=[450], answer='Tổng là 450. Khi gặp giá trị không chuyển được, cần báo lỗi/đánh dấu để kiểm tra nguồn theo quy trình, không tự thay bằng 0 vì sẽ làm sai báo cáo.'),
    dict(title='Python 08 – Lưu và kiểm tra đúng bản gửi', goal='Xuất JSON rồi đọc lại để kiểm tra cột.',
         tasks=['Tạo clean như Python 03, rồi điền clean vào json.dump.', 'Chạy mã và mở ban_giao.json, ghi số dòng và danh sách trường còn lại.', 'Nêu ba điều phải kiểm tra trước khi đề nghị giao dữ liệu cho công cụ AI.'],
         starter='clean = [{"region": r["region"], "kwh": r["kwh"]} for r in rows]\nwith open("ban_giao.json", "w", encoding="utf-8") as f:\n    json.dump(___, f, ensure_ascii=False, indent=2)\nwith open("ban_giao.json", encoding="utf-8") as f:\n    check = json.load(f)\nprint(len(check))\nprint(list(check[0].keys()))',
         solution='clean = [{"region": r["region"], "kwh": r["kwh"]} for r in rows]\nwith open("ban_giao.json", "w", encoding="utf-8") as f:\n    json.dump(clean, f, ensure_ascii=False, indent=2)\nwith open("ban_giao.json", encoding="utf-8") as f:\n    check = json.load(f)\nprint(len(check))\nprint(list(check[0].keys()))',
         expected=[6,['region','kwh']], answer='File có 6 dòng, chỉ hai trường region và kwh. Cần kiểm tra nhận diện (đặc biệt DV_C), mục đích và người duyệt, công cụ AI được phép dùng. Bài chỉ lưu file cục bộ, không tải dữ liệu lên AI.')
]

BI = [
    dict(title='BI 01 – Nhập ba bảng nhỏ', goal='Nhập dữ liệu bằng Enter data.', slides='72, 81',
         tasks=['Tạo file Power BI mới. Mở huong_dan_BI.md trong gói thực hành. Dùng Home → Enter data, dán lần lượt ba bảng và đặt đúng tên DimDonVi, DimNgay, FactDien.', 'Đặt Ngay ở cả DimNgay và FactDien thành kiểu Date; kWh thành Whole number. Kiểm tra MaKH và MaDonVi là Text.', 'Ghi số dòng của từng bảng và lưu file bai_BI_ca_nhan.pbix trên máy.'],
         answer='DimDonVi có 3 dòng, DimNgay có 2 dòng, FactDien có 8 dòng. Cột Ngay phải là Date ở cả hai đầu quan hệ. Không nạp customers.json vào mô hình BI này; mô hình đã có đúng các cột cần cho bài.'),
    dict(title='BI 02 – Nối bảng đơn vị và ngày', goal='Tạo quan hệ một–nhiều, bám slide 72.', slides='71–72',
         tasks=['Trong Model view, nối DimDonVi[MaDonVi] (1) với FactDien[MaDonVi] (*).', 'Nối DimNgay[Ngay] (1) với FactDien[Ngay] (*). Giữ quan hệ hoạt động, hướng lọc Single từ bảng danh mục sang FactDien.', 'Ghi hai quan hệ và lưu ảnh mô hình. Nếu không tạo được, kiểm tra trùng khóa, giá trị rỗng và kiểu dữ liệu.'],
         answer='Có hai quan hệ hoạt động một–nhiều. DimDonVi có mã duy nhất và DimNgay có ngày duy nhất. Không tạo quan hệ theo Thang vì cả hai dòng DimNgay cùng tháng, làm trùng khóa ở phía một.'),
    dict(title='BI 03 – Tạo một thẻ tổng sản lượng', goal='Tạo measure SUM đơn giản.', slides='81',
         tasks=['Tạo New measure tên Tong kWh bằng SUM(FactDien[kWh]).', 'Đưa measure lên một Card. Tạo thêm bảng gồm DimDonVi[MaDonVi] và Tong kWh.', 'Ghi tổng toàn bộ và tổng từng đơn vị. Đối chiếu tổng các đơn vị có bằng Card không.'],
         code='Tong kWh = SUM(FactDien[kWh])',
         answer='Tổng 1.770 kWh. DV_A 560, DV_B 810, DV_C 400. Tổng của ba đơn vị bằng tổng Card. Nếu thấy 1.400 thì bạn mới nạp 6 dòng ngày đầu, thiếu hai dòng ngày thứ hai.'),
    dict(title='BI 04 – Đếm khách khác với đếm dòng', goal='Dùng DISTINCTCOUNT trên mã khách hàng.', slides='72, 81',
         tasks=['Tạo So KH = DISTINCTCOUNT(FactDien[MaKH]) và So dong = COUNTROWS(FactDien).', 'Đưa cả hai measure lên Card khi chưa lọc.', 'Giải thích chênh lệch. Nêu vì sao không áp dụng DISTINCTCOUNT(MaKH) cho bản tổng hợp theo tháng không còn mã khách.'],
         code='So KH = DISTINCTCOUNT(FactDien[MaKH])\nSo dong = COUNTROWS(FactDien)',
         answer='Có 6 khách nhưng 8 dòng vì KH001 và KH004 xuất hiện ở hai ngày. Bản tổng hợp tháng của giáo trình có cột SoKH, không có MaKH; phải dùng cách tính phù hợp với mức tổng hợp. Không tự thêm mã khách thật chỉ để đếm.'),
    dict(title='BI 05 – Thử slicer và hiểu giới hạn', goal='Dùng bộ lọc để phân tích.', slides='73',
         tasks=['Thêm slicer từ DimDonVi[MaDonVi], chọn DV_A.', 'Ghi Tong kWh và So KH khi chọn DV_A. Bỏ chọn rồi ghi lại tổng.', 'Giải thích vì sao lưu báo cáo đang lọc DV_A không đủ để giới hạn người khác chỉ thấy A.'],
         answer='Chọn A thấy 560 kWh và 3 khách. Bỏ chọn thấy 1.770 kWh và 6 khách. Slicer phục vụ phân tích và có thể đổi, cần cấu hình RLS và quyền chia sẻ để kiểm soát truy cập.'),
    dict(title='BI 06 – Thử RLS cho từng đơn vị', goal='Tạo RLS tĩnh và View as.', slides='74–77, 81',
         tasks=['Tạo role DonVi_A trên DimDonVi với [MaDonVi] = "DV_A". Tạo DonVi_B tương tự.', 'Bỏ lọc slicer rồi View as từng role riêng. Ghi tổng kWh và đơn vị còn thấy.', 'Khi View as A, thử chọn B trên slicer. Ghi kết quả thực tế và lưu ảnh.'],
         code='-- Role DonVi_A, quy tắc trên DimDonVi\n[MaDonVi] = "DV_A"\n\n-- Role DonVi_B\n[MaDonVi] = "DV_B"',
         answer='A thấy 560 kWh, chỉ A; B thấy 810 kWh, chỉ B. Slicer không mở được dòng B khi role A áp đúng và quan hệ đang hoạt động. Đây là thử Desktop, chưa xác nhận đã cấp đúng quyền người xem trên service.'),
    dict(title='BI 07 – Tìm lỗi quan hệ bị tắt', goal='Thấy vì sao RLS cần mô hình đúng.', slides='71–74, 79',
         tasks=['Lưu một bản sao file thực hành. Trong bản sao, tạm tắt quan hệ DimDonVi–FactDien.', 'Bỏ slicer và View as DonVi_A. So sánh Card Tong kWh với lúc quan hệ còn hoạt động.', 'Bật lại quan hệ, thử lại và ghi bằng chứng đã sửa. Chỉ làm trên dữ liệu giả lập.'],
         answer='Khi quan hệ bị tắt và không có đường lọc khác, Card lấy từ FactDien có thể hiện toàn bộ 1.770 dù DimDonVi bị lọc. Bật lại đúng quan hệ và thử A phải về 560. Không coi bảng danh mục chỉ hiện A là bằng chứng bảng số liệu đã được giới hạn.'),
    dict(title='BI 08 – Một người có hai role', goal='Kiểm tra quyền là hợp của các role.', slides='79',
         tasks=['Trong View as, chọn đồng thời DonVi_A và DonVi_B, bỏ mọi slicer.', 'Ghi các đơn vị, tổng kWh và số khách thấy được.', 'Nếu người xem chỉ cần A, ghi phần cấu hình cần rà lại trước khi chia sẻ.'],
         answer='Thấy A và B, tổng 1.370 kWh và 5 khách. Hai role mở rộng thành hợp quyền, không lấy phần giao để thu hẹp. Rà thành viên role, các nhóm liên quan, quyền workspace và kiểm thử lại đúng danh tính.'),
    dict(title='BI 09 – Lọc theo ngày', goal='Dùng DimNgay và kiểm tra tổng theo ngày.', slides='72',
         tasks=['Thêm slicer từ DimNgay[Ngay], dùng cột ngày trực tiếp thay vì Date hierarchy nếu giao diện tự chọn phân cấp.', 'Chọn riêng 01/09/2026 rồi 02/09/2026, ghi tổng kWh và số khách.', 'Bỏ lọc ngày. Giải thích vì sao cộng số khách hai ngày không cho số khách duy nhất của cả kỳ.'],
         answer='Ngày 01/09: 1.400 kWh, 6 khách; ngày 02/09: 370 kWh, 2 khách. Cả kỳ 1.770 kWh, 6 khách duy nhất. Hai khách ngày 02/09 đã có ở ngày 01/09, nên không cộng số khách theo ngày thành 8 khách.'),
    dict(title='BI 10 – Kiểm thử người xem trên service (tùy chọn)', goal='Phân biệt View as với quyền người dùng thật.', slides='75–78, 80–81',
         tasks=['Nếu có workspace thực hành và giấy phép phù hợp: publish bản có quan hệ đúng; mở Security của semantic model, gán tài khoản thử vào role A/B.', 'Dùng tài khoản Viewer thật để thử A, B và người chưa được cấp role. Ghi kỳ vọng, kết quả, quyền workspace và ảnh. Nếu chưa có service, chỉ lập kế hoạch và ghi rõ chưa thử.', 'Giải thích vì sao không dùng Member/Admin/Contributor để chứng minh RLS của người xem. Nêu cách chia sẻ phù hợp, không bật Publish to web.'],
         answer='Viewer A chỉ thấy A (560); Viewer B chỉ thấy B (810) khi cấp đúng role. Viewer chưa có quyền RLS phù hợp phải không đọc được dữ liệu; cần kiểm tra mọi nhóm/quyền khác trước khi kết luận. Admin/Member/Contributor có quyền sửa và không bị RLS giới hạn như Viewer. Chỉ ghi đạt service khi đã thử thật; kế hoạch chưa chạy cần ghi Chưa thử.')
]


def p(text, **flags):
    return {'t':'p', 'plain':text, 'html':html.escape(text), **flags}


def table(rows):
    return {'t':'table', 'rows':[[{'plain':str(c), 'html':html.escape(str(c))} for c in row] for row in rows]}


def append_section(module, title, blocks, activity=None):
    sid = f's{len(module["sections"])}'
    section = {'id':sid, 'title':title, 'kind':'practice' if activity else 'content', 'blocks':blocks}
    if activity:
        section['activity'] = activity['id']
        activity['section'] = sid
        module['activities'].append(activity)
    module['sections'].append(section)


def add_labs(module):
    no = module['no']
    if no not in (6, 7):
        return module
    download = {'t':'p', 'plain':'Tải gói thực hành cá nhân: bai_tap_SQL_Python_BI.zip',
                'html':'<a href="/static/labs/bai_tap_SQL_Python_BI.zip" download>Tải gói thực hành cá nhân (SQL, Python, dữ liệu BI và hướng dẫn)</a>'}
    if no == 6:
        append_section(module, 'Bắt đầu SQL và Python – Dữ liệu nhỏ, mỗi bài một việc', [
            p('Bám slide 58–68. Có 8 bài SQL và 8 bài Python, mỗi bài khoảng 5–10 phút. Làm cá nhân. Trong giờ chọn bài phù hợp, các bài còn lại để luyện thêm; không bắt buộc làm hết trong một buổi.'),
            download,
            p('Giải nén gói tải về. Nếu máy có Python 3, mở Terminal tại thư mục đó. Chạy python sql_lab.py để thử kết nối hoặc python python_lab.py để đọc dữ liệu. Trên một số máy Windows có thể dùng py thay cho python. Không cần cài pandas hay máy chủ SQL.'),
            p('SQL 01–07: sửa chuỗi query trong sql_lab.py rồi chạy lại. SQL 08: dùng phần connection đã tạo trong file và thay phần chạy query bằng đoạn mẫu của bài. Python 01–08: thay phần BÀI LÀM trong python_lab.py; chạy từng bài riêng, không ghép tất cả vào một file dài.'),
            p('Nếu chưa cài Python, bạn vẫn có thể đọc mã và ghi kết quả dự đoán, nhưng phải đánh dấu Chưa chạy. Việc chạy trên máy là thực hành thật; web chỉ nhận mã, kết quả và giải thích, không thực thi mã.'),
            p('Bảng customers có 6 khách, mỗi khách một dòng. region là mã đơn vị; kwh là sản lượng mẫu. Dữ liệu này khác bộ lớn của Thực hành 7, dùng để học thao tác trước.'),
            table([['id','name','phone','address','region','kwh']] + [[r[k] for k in ('id','name','phone','address','region','kwh')] for r in CUSTOMERS]),
            p('Chỉ dùng dữ liệu giả lập đi kèm. Tổng hợp hoặc che dữ liệu chưa tự chứng minh đã ẩn danh. Ngưỡng 2 ở bài ngắn chỉ để học câu lệnh, không dùng làm tiêu chuẩn công bố dữ liệu thật.')])
    else:
        append_section(module, 'Bắt đầu Power BI – Nối mô hình ngày trong slide với bài học', [
            p('Slide 72 dùng DimNgay và dữ liệu theo ngày. Bài lớn trong giáo trình dùng DimThang và số liệu đã tổng hợp theo tháng. Cả hai đều có thể phù hợp, nhưng không trộn bảng và công thức giữa hai mức chi tiết.'),
            p('Slide 81 yêu cầu cả sản lượng và số khách hàng, trong khi sơ đồ slide 72 chỉ nêu MaDonVi, Ngay, kWh. Bộ bài nhỏ thêm MaKH giả lập để thực hành DISTINCTCOUNT. Đây là cột thêm phục vụ bài đếm, không phải yêu cầu đưa mã khách thật vào mọi báo cáo.'),
            download,
            p('Mở huong_dan_BI.md để sao chép ba bảng vào Home → Enter data trong Power BI Desktop. Chưa cần Power BI service cho bài 01–09. Mỗi bài tập trung một thao tác; BI 10 chỉ làm khi có môi trường service thực hành.'),
            p('Mô hình nhỏ dùng ngày: DimDonVi[MaDonVi] (1) tới FactDien[MaDonVi] (*); DimNgay[Ngay] (1) tới FactDien[Ngay] (*). FactDien có 8 dòng, 6 khách, trong đó hai khách có thêm dữ liệu ngày thứ hai.'),
            p('Trong mô hình nhỏ, dùng DISTINCTCOUNT(FactDien[MaKH]) để đếm khách duy nhất trong phạm vi đang lọc. Trong bản tổng hợp tháng của giáo trình, SoKH đã là số tổng hợp; dùng chỉ tiêu phù hợp và giải thích ý nghĩa, không đếm số dòng như số khách.'),
            p('Mỗi bài khoảng 5–10 phút, riêng nhập dữ liệu và service có thể lâu hơn. Nộp cá nhân, lưu .pbix và ảnh trên máy, ghi kết quả vào mẫu web. Nếu chưa thực hiện trên service, chọn Chưa chạy và không ghi đã kiểm thử quyền người xem thật.')])
        module['sections'][-1]['blocks'] += [
            {'t':'h3','text':'Hai vị trí trên service được minh họa trong slide'},
            p('Ảnh trích từ slide 76: thêm người dùng vào role ở Security của semantic model. Đây là ảnh tài liệu, giao diện môi trường của bạn có thể khác.'),
            {'t':'img','src':'/static/labs/rls-members.png'},
            p('Ảnh trích từ slide 77: mở menu của role để chọn Test as role. Sau đó vẫn cần kiểm tra bằng tài khoản Viewer thật nếu có service thực hành.'),
            {'t':'img','src':'/static/labs/rls-test-role.png'}]
    sets = [('sql', SQL), ('py', PYTHON)] if no == 6 else [('bi', BI)]
    for kind, exercises in sets:
        for i, ex in enumerate(exercises, 1):
            aid = f'm{no:02d}-{kind}{i:02d}-v1'
            blocks = [p(ex['goal']), p('Bài cá nhân. Đọc phần Bắt đầu SQL và Python hoặc Bắt đầu Power BI trong buổi này để lấy dữ liệu và cách chạy.')]
            for j, task in enumerate(ex['tasks'], 1):
                blocks.append(p(f'{j}. {task}'))
            if ex.get('starter') or ex.get('code'):
                blocks += [p('Mẫu để làm tiếp:'), {'t':'code', 'text':ex.get('starter', ex.get('code'))}]
            rubric = 'Tiêu chí 10 điểm: mã hoặc thao tác đúng (4), kết quả và đối chiếu rõ (3), giải thích đúng ý nghĩa an toàn dữ liệu (3).'
            if kind == 'bi' and i == 10:
                rubric += ' Nếu chưa có môi trường service, giảng viên đánh giá kế hoạch và ghi nhận chưa thực hiện kiểm thử trên service.'
            blocks += [p('Nộp mã hoặc các bước thực hiện, kết quả kiểm tra và giải thích ngắn. Nếu chưa thực hiện, ghi rõ kết quả dự đoán và chọn trạng thái Chưa chạy.'),
                       p(rubric),
                       {'t':'h3','text':'Gợi ý chữa bài', 'reveal':aid}]
            if ex.get('solution'):
                blocks.append({'t':'code','text':ex['solution'], 'reveal':aid})
            blocks.append(p(ex['answer'], reveal=aid))
            fields = [
                {'type':'textarea','key':'code','label':{'sql':'Câu lệnh SQL hoặc mã thực thi','py':'Đoạn mã Python','bi':'Các bước thực hiện trên Power BI'}[kind],
                 'hint': 'Dán đoạn mã đã sử dụng để giảng viên đối chiếu.' if kind != 'bi' else 'Ghi các bước cấu hình, tài khoản hoặc vai trò đã kiểm tra.'},
                {'type':'textarea','key':'result','label':'Kết quả và cách đối chiếu',
                 'hint':'Ghi số dòng, số liệu hoặc thông báo thực tế.' if kind != 'bi' else 'Ghi số liệu thực tế và tên file hoặc ảnh đã lưu trên máy.'},
                {'type':'textarea','key':'explain','label':'Giải thích kết quả và điểm cần lưu ý'},
                {'type':'table','key':'run_state','label':'Trạng thái thực hiện', 'rows':['Bài này'],
                 'columns':[{'key':'state','label':'Trạng thái','options':['Đã chạy / đã thao tác','Chưa chạy, mới dự đoán','Đã thử nhưng còn lỗi']}]}]
            append_section(module, ex['title'], blocks, {'id':aid, 'type':'practice','scope':'student',
                'title':ex['title'], 'intro':ex['goal'], 'fields':fields,
                'instructions':[download] + [b for b in blocks[1:] if not b.get('reveal')]})
    return module


def build_pack():
    """Gói học viên chỉ có dữ liệu và khung làm bài, không kèm đáp án."""
    target = ROOT / 'app/static/labs'
    target.mkdir(parents=True, exist_ok=True)
    sql_starter = '''"""SQL cá nhân: dữ liệu giả lập, chạy hoàn toàn trong bộ nhớ."""
import json
import sqlite3
from pathlib import Path

rows = json.loads(Path(__file__).with_name("customers.json").read_text(encoding="utf-8"))
connection = sqlite3.connect(":memory:")
connection.execute("CREATE TABLE customers (id TEXT, name TEXT, phone TEXT, address TEXT, region TEXT, kwh INTEGER)")
connection.executemany("INSERT INTO customers VALUES (:id,:name,:phone,:address,:region,:kwh)", rows)

# BÀI LÀM: thay query bằng câu SQL của từng bài 01–07.
query = "SELECT * FROM customers ORDER BY id;"
for record in connection.execute(query).fetchall():
    print(record)

# Bài SQL 08: giữ phần tạo connection ở trên, thay phần query/vòng lặp
# bằng đoạn mẫu của SQL 08 trên web rồi điền các chỗ trống.
'''
    py_starter = '''"""Python cá nhân: dữ liệu giả lập, không cần thư viện ngoài."""
import json
from pathlib import Path

rows = json.loads(Path(__file__).with_name("customers.json").read_text(encoding="utf-8"))

# BÀI LÀM: thay phần dưới bằng mã của từng bài Python trên web.
print("Đã đọc dữ liệu mẫu. Điền bài làm tại đây.")
'''
    bi = ['# Nhập dữ liệu Power BI', '',
          'Dữ liệu giả lập. Mở Power BI Desktop, Home → Enter data. Sao chép riêng nội dung từng khối bên dưới, gồm hàng tiêu đề, rồi dán vào ô đầu tiên. Nếu tiêu đề chưa được nhận, chọn Use first row as headers. Đặt đúng tên bảng rồi Load.', '',
          'Không dán các dòng có dấu ``` hoặc tên bảng. Trong Table view, đặt Ngay thành Date ở cả hai bảng có ngày; kWh thành Whole number; MaKH/MaDonVi thành Text. Các ngày mẫu được ghi theo ISO YYYY-MM-DD.', '']
    for name, data in [('DimDonVi', DIM_DONVI), ('DimNgay', DIM_NGAY), ('FactDien', FACT)]:
        keys = list(data[0])
        bi += [f'## {name}', '', '```text', '\t'.join(keys)]
        bi += ['\t'.join(str(r[k]) for k in keys) for r in data]
        bi += ['```', '']
    bi += ['Tạo hai quan hệ một–nhiều đang hoạt động, hướng Single: DimDonVi[MaDonVi] → FactDien[MaDonVi] và DimNgay[Ngay] → FactDien[Ngay].', '',
           'Làm từng bài BI trên web. Lưu file và ảnh trên máy, nhập kết quả vào bài cá nhân. Bài service là tùy chọn và cần tài khoản/môi trường thực hành phù hợp.']
    readme = '''# Bộ bài cá nhân SQL, Python và Power BI

Tất cả dữ liệu trong gói đều là giả lập, không phải khách hàng thật.

1. Giải nén vào một thư mục riêng. Giữ customers.json cạnh hai file .py.
2. SQL/Python: dùng Python 3, không cần pandas hoặc máy chủ cơ sở dữ liệu.
   Mở Terminal trong thư mục, chạy `python sql_lab.py` hoặc `python python_lab.py`.
   Windows có thể dùng `py` thay `python`. Bài SQL 01–07 sửa query; SQL 08 thay phần chạy query bằng mã tham số hóa của đề. Bài Python thay phần BÀI LÀM.
3. BI: đọc huong_dan_BI.md và nhập ba bảng bằng Enter data. Chỉ BI 10 cần service.
4. Đề và nơi nộp nằm trên web lớp học. Mỗi bài làm riêng. Ghi mã/thao tác, kết quả và giải thích; chọn đúng trạng thái đã chạy/chưa chạy/còn lỗi.
5. Bài SQL/Python dùng bộ customers có 6 dòng, mỗi khách một dòng. BI dùng 8 dòng theo ngày, có hai khách lặp lại ở ngày thứ hai. Không trộn hai mức chi tiết.
6. Lưu file/ảnh ở máy để giảng viên đối chiếu. Web hiện chỉ nhận nội dung, chưa nhận tệp đính kèm.

Gói này không kèm đáp án. Giảng viên mở gợi ý chữa bài sau khi lớp nộp.
'''
    files = {'customers.json':json.dumps(CUSTOMERS, ensure_ascii=False, indent=2),
             'sql_lab.py':sql_starter, 'python_lab.py':py_starter,
             'huong_dan_BI.md':'\n'.join(bi), 'DOC_TRUOC.md':readme}
    with zipfile.ZipFile(target / 'bai_tap_SQL_Python_BI.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name, text in files.items():
            info = zipfile.ZipInfo(name, date_time=(2026,10,25,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, text.encode('utf-8'))
    return files
