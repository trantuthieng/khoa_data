# Lớp học An toàn ứng dụng & Dữ liệu dành cho cán bộ vận hành

Webapp dạy khóa học 10 buổi. Mỗi buổi là một module; giảng viên điều khiển nhịp lớp, học viên đọc bài, làm trắc nghiệm, trả lời câu hỏi ôn tập và nộp bài thực hành. Mọi bài đều làm cá nhân, không chia nhóm.

- **Backend**: FastAPI (Python), chạy trên Render.
- **Cơ sở dữ liệu**: Postgres của Supabase (lớp, học viên, trạng thái bài tập, bài làm).
- **Nội dung**: sinh tự động từ các file `.docx` của giáo trình, nằm trong `app/content/`.

## Giảng viên làm được gì

| Việc | Cách làm |
|---|---|
| Tạo lớp | `/teacher` → đăng nhập → **Tạo lớp**. Mỗi lớp có một mã 6 ký tự để chiếu cho học viên |
| Chọn buổi học | Chọn buổi ở cột trái → **Bắt đầu buổi N**. Học viên chuyển sang buổi mới |
| Dẫn bài | Bấm **Phần sau / Phần trước** (hoặc phím ←/→, PageUp/PageDown của bút trình chiếu). Học viên chỉ thấy các phần đã trình bày và tự chuyển theo nếu bật “Học viên tự chuyển theo giảng viên” |
| Trình chiếu | **⛶ Trình chiếu**: ẩn bảng điều khiển, chữ lớn, ghi mã lớp ở góc. Phần chỉ dành cho giảng viên và đáp án chưa công bố tự ẩn |
| Bài tập | Cột phải: mỗi bài có 4 trạng thái **Ẩn → Mở → Đóng → Công bố**. Khi công bố: học viên thấy đáp án, điểm, tỉ lệ cả lớp; với bài thực hành thì phần “Đáp án gợi ý” trong giáo trình hiện ra |
| Đáp án giảng viên | Nút **📘 Đáp án** (trang danh sách lớp, cột Hoạt động, phần thực hành, trang kết quả): bài làm mẫu dựng trên bảng thật (module, dây nối, nội dung), giải thích từng module và từng dây, thang điểm, lỗi hay gặp. Chỉ gửi qua API giảng viên. Có cho cả 48 bài thực hành (11 bài bảng, 10 bài tình huống, 26 bài ngắn, 1 bài rà soát trên phòng thí nghiệm RLS). Dữ liệu ở `app/answer_keys/` (mỗi buổi một tệp; bài ngắn lấy lời giải từ `tools/beginner_labs.py`) |
| Xem kết quả | **Xem kết quả**: biểu đồ đáp án theo câu, bảng điểm, câu trả lời tự luận, bài thực hành của từng học viên |
| Diễn tập (buổi 10) | Nút **Đợt diễn tập học viên thấy: − / +** mở dần từng đợt tình tiết |
| Học viên | Tab **Học viên**: ai đang online, xóa người vào nhầm |
| Xuất kết quả | **Xuất kết quả CSV** (mở được bằng Excel) |

Các hoạt động trong khóa học:

- **Kiểm tra nhanh** (buổi 1–9): 18 câu tình huống mới, mỗi buổi 2 câu, tự chấm điểm. Các bài “Ôn câu hỏi cuối khóa (tùy chọn)” giữ nguyên để lớp đã học vẫn đọc được kết quả cũ; nên dùng vào phần ôn cuối khóa.
- **Trò chơi thẻ C–I–A** (buổi 1): chọn nhiều đáp án.
- **Câu hỏi ôn tập** (mọi buổi): tự luận, giảng viên công bố gợi ý trả lời.
- **Thực hành 1–11**: mỗi học viên làm một bài riêng theo mẫu C1–C12 (bảng, checklist, đoạn văn). Mẫu nằm trong `app/practice.py`.
- **Không gian bảng**: mọi bài thực hành chính (Thực hành 1–11) và bài tập thêm buổi 3 làm trên bảng rộng. Học viên kéo module, ghi nội dung trong module, kéo chấm tròn để nối module và ghi chú trên dây nối. Một số bảng có vùng phân loại (kéo thẻ vào vùng để xếp loại, VD gắn nhãn dữ liệu ở Thực hành 1), chip chọn nhiều, dây nối dựng sẵn cho quy trình nhiều bước. Bảng có danh sách nhiệm vụ tự đánh dấu, gợi ý tự kiểm tra, chế độ toàn màn hình, bản đọc nhanh dạng văn bản và bảng tổng hợp tự lập (ma trận C3, bảng C1, C2, C8…; ô đánh dấu `table` sửa ngay trong bảng). Cấu hình bảng (`BOARD_*`) nằm trong `app/practice.py`, giao diện nằm trong `static/board.js`. Bài nộp theo mẫu cũ vẫn hiện ở mục “Bài đã nộp theo mẫu cũ”.
- **10 bài tập tình huống bổ sung**: mỗi buổi một bài cá nhân, có đủ dữ kiện trong đề, ba mục trả lời, gợi ý chữa bài và tiêu chí 10 điểm. Không cần tải file bên ngoài để làm các bài này.
- **26 bài ngắn theo slide**: buổi 6 thêm 8 SQL + 8 Python, buổi 7 thêm 10 Power BI. Mỗi bài chỉ tập trung một thao tác. Phần “Bắt đầu…” có link tải dữ liệu giả lập và file khung. SQL/Python chỉ dùng thư viện chuẩn của Python 3; BI 01–09 dùng Desktop, BI 10 là phần service tùy chọn.
- **Phòng thí nghiệm RLS** (buổi 7, `app/static/labs/rls/`): mô phỏng Power BI Desktop và service chạy hoàn toàn trên trình duyệt, dùng khi máy học viên chưa có Power BI hoặc lớp chưa có workspace. Desktop có Enter data, Power Query (bỏ cột, che giá trị), Table/Model view, quan hệ, New measure/column (DAX rút gọn), Manage roles (RLS tĩnh, động, OLS), View as, Publish. Service có Manage access, App, Share, Security, Test as role, Manage permissions, Export data, Analyze in Excel, Publish to web, Admin portal, thư mục người dùng và nhật ký hoạt động. Ô “Đang đăng nhập” cho phép đóng vai từng người để kiểm thử quyền thật. Mỗi lần kiểm thử tự ghi vào ma trận C8. Mở bằng `/static/labs/rls/index.html?bai=<mã>`, trong đó mã là `bi01`…`bi10`, `th8` hoặc `rasoat`. Mỗi bài BI và Thực hành 8 có link tới đúng kịch bản, kèm danh sách tự kiểm tra. Bài mới **“Phòng thí nghiệm RLS – Rà soát báo cáo đang vận hành”** (`m07-rlslab-v1`) cài sẵn 13 lỗi phân quyền nối với buổi 1–7 (role tạm, Member/Contributor, dòng phân quyền cũ, người nghỉ việc, tài khoản dùng chung, hợp quyền, bảng thiếu quan hệ, che chỉ trên hình ảnh, Publish to web bản sao, nhãn sai…). Đáp án giảng viên có cách tái hiện, cách sửa, ma trận trước/sau và trình tự trình diễn. Bài làm trên mô phỏng chỉ lưu trong trình duyệt của học viên.
- **Bài kiểm tra cuối khóa** 20 câu (buổi 10).

### Theo dõi nộp bài và chấm điểm cá nhân

Chọn lớp → chọn bài → **Xem kết quả**. Giảng viên thấy số đã nộp, số chưa nộp, số đã chấm và danh sách học viên chưa nộp. Bài trắc nghiệm có điểm tự động. Với tự luận và thực hành, đọc bài, nhập điểm, điểm tối đa và nhận xét, rồi bấm **Lưu điểm và nhận xét**. Điểm áp dụng cho toàn bài.

Nên **Đóng** bài trước khi chấm. Nếu mở lại và học viên sửa bài, điểm cũ không áp dụng cho bản mới; giảng viên phải chấm lại. Hệ thống chặn lưu điểm khi bản đang chấm đã bị thay đổi. Học viên chỉ xem điểm và nhận xét của mình sau khi giảng viên **Công bố**. Bảng CSV có cả điểm chấm tay và nhận xét.

Ứng dụng nhận bài dạng văn bản, bảng và checklist; chưa nhận tệp đính kèm. Với bài thao tác Excel/Power BI, học viên lưu file và ảnh trên máy, ghi tên file, kết quả kiểm tra vào mẫu; giảng viên yêu cầu mở file để đối chiếu khi chữa bài. Các file mẫu của bài gốc cần được giảng viên chuẩn bị theo giáo trình.

Phần “Ghi chú cho giảng viên”, “Chuẩn bị của giảng viên”, đáp án, Phụ lục B không bao giờ gửi tới trình duyệt học viên trước khi giảng viên cho phép (lọc ở server, không chỉ ẩn bằng giao diện).

## Học viên

Vào trang chủ, nhập mã lớp và họ tên. Hệ thống cấp một **mã vào lại cá nhân** (bấm vào tên mình ở góc trên để xem) – dùng khi đổi máy hoặc lỡ xóa trình duyệt. Không cần tạo tài khoản.

## Deploy

### 1. Supabase – tạo cơ sở dữ liệu

1. Vào <https://supabase.com> → **New project**. Region nên chọn **Southeast Asia (Singapore)**. Ghi lại mật khẩu database.
2. Khi project chạy xong: bấm **Connect** (thanh trên cùng) → tab **Connection string** → chọn **Session pooler**.
   Chuỗi có dạng:
   ```
   postgresql://postgres.abcdefghijkl:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres
   ```
   Thay `[YOUR-PASSWORD]` bằng mật khẩu database. Đây là `DATABASE_URL`.
   - Phải dùng **pooler**, không dùng “Direct connection”: Render chỉ có IPv4, còn kết nối trực tiếp của Supabase là IPv6.
   - Nếu mật khẩu có ký tự đặc biệt (`@ : / ? #`), mã hóa URL chúng (VD `@` → `%40`), hoặc đặt lại mật khẩu chỉ gồm chữ và số.
3. Không cần tạo bảng: ứng dụng tự tạo khi khởi động và bật Row Level Security cho mọi bảng, để khóa `anon` công khai của Supabase không đọc được dữ liệu lớp học.

### 2. GitHub – đưa code lên

Tạo một repository **private** trên GitHub, rồi trong thư mục `webapp`:

```bash
git add .
git commit -m "Webapp lớp An toàn dữ liệu"
git branch -M main
git remote add origin https://github.com/<tài-khoản>/<repo>.git
git push -u origin main
```

### 3. Render – chạy ứng dụng

1. Vào <https://dashboard.render.com> → **New** → **Blueprint** → kết nối GitHub và chọn repo vừa tạo. Render đọc file `render.yaml`.
2. Render hỏi giá trị cho 2 biến:
   - `DATABASE_URL`: chuỗi kết nối Supabase ở bước 1.
   - `TEACHER_PASSWORD`: mật khẩu đăng nhập của giảng viên – đặt cụm từ dài, không dùng lại mật khẩu khác (đúng tinh thần buổi 4).
   `SECRET_KEY` được Render tự sinh.
3. Bấm **Apply**. Sau vài phút, ứng dụng chạy tại `https://<tên-service>.onrender.com`. Kiểm tra `https://<tên-service>.onrender.com/healthz` trả về `{"ok":true}`.

Lưu ý gói miễn phí:
- Render free **ngủ sau 15 phút không có truy cập**; lần mở đầu tiên mất khoảng 1 phút. Mở trang 5–10 phút trước giờ học. Trong giờ học, trình duyệt của lớp liên tục gọi server nên không bị ngủ. Muốn bỏ hẳn độ trễ này, nâng lên gói Starter.
- Supabase free **tạm dừng project sau 7 ngày không hoạt động** – vào dashboard bấm Restore nếu nghỉ dạy lâu.

## Sửa nội dung giáo trình

Sửa file `.docx` (giữ cấu trúc tiêu đề Heading 2/Heading 3 như hiện tại), rồi:

```bash
python tools/build_content.py "đường/dẫn/thư/mục/chứa/docx"
git add app/content app/static/content && git commit -m "Cập nhật giáo trình" && git push
```

Render tự deploy lại khi có commit mới. Script chỉ dùng thư viện chuẩn của Python.

Sau khi đọc Word, script áp dụng phần biên tập trong `tools/course_revision.py` và bài bổ sung trong `tools/supplemental_exercises.json`. Chỉnh hai tệp này nếu muốn sửa bản dạy trên web; chạy lại lệnh build sẽ giữ các thay đổi đó. Các tài liệu Word nguồn được giữ nguyên để đối chiếu.

Cuối bước dựng nội dung, `tools/production_copy.py` áp dụng phần biên tập cho bản phát hành: giới thiệu đối tượng học, câu chữ hướng dẫn, tham chiếu bài tập và lịch học. Xem `BIEN_TAP_NOI_DUNG.md` để biết phạm vi thay đổi. Mã hoạt động, trường bài nộp và đáp án chấm điểm được giữ nguyên.

Buổi 5 và 6 dùng bản gọn trong `tools/compact_lessons.py`: bốn bài lý thuyết được viết lại ngắn hơn, có 20 sơ đồ SVG (block `figure`, màu theo giao diện sáng/tối) và bỏ các đoạn mã dài. Chạy `python tools/compact_lessons.py` để áp bản gọn vào JSON hiện có mà không cần dựng lại từ Word. File luyện tập của Thực hành 6, 7 (`BaoCao_Thang.xlsx`, `DLX_SanLuong_Q3.xlsx` trong `app/static/labs/`) do `python tools/practice_files.py` tạo (cần openpyxl). `DLX_SanLuong_Q3.xlsx` có 16 cột, trong đó 7 cột thông tin cá nhân (CCCD, ngày sinh, giới tính, email, hộ chính sách, tài khoản ngân hàng, ghi chú tự do) để học viên phân loại; số sản lượng giữ như bản CSV trước nên đáp án không đổi; học viên tải từ bài, giảng viên có bảng số liệu đối chiếu.

Bài ngắn nằm trong `tools/beginner_labs.py`, được thêm khi build. Script cũng dựng gói học viên `app/static/labs/bai_tap_SQL_Python_BI.zip` chỉ có dữ liệu, file khung và hướng dẫn. Lời giải ở phần nội dung có cờ công bố, không nằm trong ZIP. Xem `DOI_CHIEU_SLIDE.md` để biết kết quả so sánh với 111 slide và cách chọn bài theo thời lượng. Dùng file BI mới cho bộ bài nhỏ theo ngày; bài lớn theo tháng giữ mô hình và công thức riêng.

Khi khởi động, ứng dụng tự tạo bảng `response_grades` cho điểm và nhận xét, kể cả trên cơ sở dữ liệu đã có. Mã hoạt động và bài nộp cũ được giữ lại.

Kiểm tra luồng nộp/chấm bài: cài thêm `httpx`, chạy `python -m unittest discover -s tests -v` trong thư mục `webapp`. Bộ kiểm tra dùng SQLite tạm, không dùng dữ liệu lớp thật.

Quy ước script nhận diện:
- Heading 2 = một phần (một “slide” của buổi). “Ghi chú cho giảng viên”, “Chuẩn bị khóa học”, “Phụ lục B” = chỉ giảng viên.
- Heading 2 “Câu hỏi ôn tập” → bài tự luận; “Thực hành N” → bài thực hành; “Bài kiểm tra cuối khóa” → trắc nghiệm.
- Trong phần Thực hành: Heading 3 bắt đầu bằng “Đáp án…”, “Điểm chữa bài”, “Lỗi hay gặp” hoặc đoạn bắt đầu bằng “Đáp án tham khảo/gợi ý” → ẩn đến khi công bố; “Chuẩn bị của giảng viên” → chỉ giảng viên; “Đợt N” → mở dần theo đợt.

## Chạy thử trên máy

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
set TEACHER_PASSWORD=matkhau-thu   # macOS/Linux: export TEACHER_PASSWORD=matkhau-thu
uvicorn app.main:app --reload
```

Không đặt `DATABASE_URL` thì ứng dụng dùng SQLite (`local.db`). Mở <http://localhost:8000/teacher>.
