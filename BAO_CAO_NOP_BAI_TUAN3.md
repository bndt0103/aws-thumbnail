# BÁO CÁO TIẾN ĐỘ TUẦN 3

**Đề tài:** Xử lý ảnh tự động: tạo thumbnail khi upload lên Amazon S3.

**Giảng viên hướng dẫn:** TS. Huỳnh Xuân Phụng.

**Nhóm thực hiện:** Bùi Nguyễn Duy Trung — MSSV 24110363; Đỗ Anh Tuấn — MSSV 24110369.

**Ngày đối chiếu kết quả:** 27/10/2026.

**Kho mã nguồn:** [bndt0103/aws-thumbnail](https://github.com/bndt0103/aws-thumbnail).

---

## 1. Mục tiêu và phạm vi tuần 3

Sau khi hoàn thành tích hợp luồng xử lý ảnh Serverless cốt lõi ở Tuần 2 và được Giảng viên hướng dẫn duyệt thông qua, mục tiêu trọng tâm của Tuần 3 là chuyển dịch toàn bộ ứng dụng người dùng (Web Gallery) từ môi trường chạy cục bộ lên máy chủ đám mây **Amazon EC2**, thiết lập cơ chế bảo mật xác thực danh tính đám mây, bảo vệ quyền riêng tư dữ liệu ảnh và hiện thực hóa hai yêu cầu nâng cao theo chỉ đạo trực tiếp của Giảng viên hướng dẫn:

1. **Triển khai Web Gallery trên Amazon EC2:** Đóng gói ứng dụng Flask, cấu hình máy chủ ứng dụng công nghiệp **Gunicorn WSGI**, quản lý tiến trình bằng **systemd service** (`cloud-photo.service`) nhằm đảm bảo khả năng hoạt động liên tục, tự động khởi động cùng hệ thống và tự phục hồi khi có sự cố.
2. **Cơ chế xác thực an toàn qua IAM Role (`LabInstanceProfile`):** Máy chủ EC2 giao tiếp trực tiếp với Amazon S3 và DynamoDB hoàn toàn dựa vào IAM Role thông qua dịch vụ Instance Metadata (IMDSv2), tuyệt đối **không lưu trữ cứng Access Key / Secret Key** trong mã nguồn hay file cấu hình của máy chủ.
3. **Bảo mật truy cập dữ liệu với S3 Private và Presigned URL:** Toàn bộ bucket S3 đầu ra được giữ ở trạng thái riêng tư tuyệt đối (chặn toàn bộ truy cập công khai trực tiếp từ Internet nhận mã lỗi HTTP 403 `AccessDenied`). Web Gallery cấp quyền truy cập ảnh tạm thời cho trình duyệt thông qua **Presigned URL** với thời hạn hợp lệ chính xác **300 giây (`X-Amz-Expires=300`)**. Sau 300 giây, liên kết tự động vô hiệu hóa (`Request has expired`).
4. **Kiểm thử khả năng tự phục hồi dịch vụ (Self-healing):** Xác minh dịch vụ Gunicorn tự động hồi sinh khi tiến trình bị restart hoặc gặp lỗi dừng đột ngột mà không gây gián đoạn hệ thống.
5. **Thực hiện đầy đủ 2 yêu cầu NÂNG CAO theo nhận xét của GVHD:**
   - **Nâng cao 1 — Tối ưu dung lượng gói deploy bằng Lambda Layer:** Tách toàn bộ thư viện Pillow thành Lambda Layer riêng biệt (`cloud-photo-pillow` v1, dung lượng ~5 MB). Nhờ đó, gói mã nguồn triển khai của Lambda Function `cloud-photo-processor` giảm siêu tối ưu từ >15 MB xuống chỉ còn **3.7 kB** (chỉ chứa 2 file mã nguồn `lambda_function.py` và `image_tools.py`), cho phép mở và chỉnh sửa trực tiếp trên AWS Management Console Code Editor.
   - **Nâng cao 2 — Thiết lập S3 Lifecycle Rule dọn dẹp thumbnail cũ:** Thiết lập quy tắc vòng đời (`auto-cleanup-old-thumbnails-7days`) trên bucket output `cloudphoto-output-103308504802`, tự động hết hạn và xóa các ảnh thumbnail sau 7 ngày kể từ thời điểm tạo, đồng thời dọn dẹp các tệp tải lên phân đoạn dang dở (incomplete multipart uploads sau 7 ngày) để tối ưu chi phí lưu trữ đám mây.

---

## 2. Công việc và kết quả triển khai

| Thành phần / Tiêu chí | Cấu hình kỹ thuật và kết quả thực tế trên AWS |
|---|---|
| **AWS Region** | `us-east-1` — N. Virginia (Subnet `us-east-1d`). |
| **Máy chủ EC2** | Instance ID `i-0390fda0b0a75c002`; loại `t2.micro`; OS Amazon Linux 2023 (kernel 6.1); Public IPv4 `100.31.151.65`; Private IPv4 `172.31.16.240`. |
| **Bảo mật IAM Role** | Gắn IAM Role `LabRole` thông qua `LabInstanceProfile`. Ứng dụng tự động lấy quyền đọc/ghi S3 và DynamoDB qua IMDSv2 mà không cần cấu hình Access Key. |
| **Security Group** | `cloud-photo-web-sg`; Inbound Rule chỉ mở cổng 22 (SSH) và cổng 8000 (Custom TCP); Outbound Rule cho phép toàn bộ lưu lượng ra Internet (0.0.0.0/0). |
| **Quản lý tiến trình** | Systemd service `/etc/systemd/system/cloud-photo.service`; chạy Gunicorn 26.2.0 với 2 sync workers; cơ chế tự phục hồi `Restart=on-failure`, `RestartSec=5s`. |
| **Kênh truy cập an toàn** | Sử dụng SSH Local Port Forwarding qua cổng 8080 (`ssh -i labsuser.pem -L 8080:localhost:8000 ec2-user@100.31.151.65`); truy cập giao diện qua `http://localhost:8080`. |
| **Kiểm tra sức khỏe** | Endpoint `GET http://127.0.0.1:8000/health` trả về JSON `{"status":"ok"}` với mã phản hồi HTTP 200 OK. |
| **Nâng cao 1: Lambda Layer** | Tách thư viện Pillow thành Layer v1; gói deploy Lambda `cloud-photo-processor` đạt **3.7 kB** (chỉ gồm `lambda_function.py` và `image_tools.py`), hiển thị trực quan trên Code Editor. |
| **Nâng cao 2: S3 Lifecycle** | Quy tắc `auto-cleanup-old-thumbnails-7days` trạng thái **Enabled** trên bucket output `cloudphoto-output-103308504802`; tự động xóa objects sau 7 ngày và hủy multipart uploads sau 7 ngày. |
| **Bảo mật S3 & Presigned URL** | Bucket output chặn truy cập trực tiếp (HTTP 403 `AccessDenied`); cấp Presigned URL có thời hạn hợp lệ chính xác 300 giây (`X-Amz-Expires=300`); hết hạn trả về `Request has expired`. |
| **Xử lý ảnh End-to-End** | Tải ảnh `portrait.jpg` (900 × 1500 px) qua Web EC2; S3 kích hoạt Lambda tạo 3 thumbnail; DynamoDB ghi nhận trạng thái `COMPLETE`; CloudWatch ghi Duration 604.68 ms, memory 153 MB; Web hiển thị ảnh thứ 10. |

---

## 3. Tổng hợp kiểm thử

Nhóm đã thực hiện và đối chiếu thực nghiệm 7 ca kiểm thử Tuần 3 (tiếp nối bộ kiểm thử T01–T12 của Tuần 2) trên môi trường AWS thực tế:

| Mã | Tình huống kiểm thử | Kỳ vọng | Kết quả quan sát thực tế | Đánh giá |
|---|---|---|---|:---:|
| **T13** | Chặn truy cập trực tiếp S3 object | Không cho phép mở trực tiếp URL S3 khi chưa được ký | Trình duyệt mở trực tiếp URL object nhận XML lỗi `AccessDenied` (HTTP 403); bucket bảo mật riêng tư tuyệt đối. | **Đạt** |
| **T14** | Thời hạn hiệu lực của Presigned URL (300s) | Mở được ảnh trong 300s; sau 300s liên kết phải hết hạn | Trong vòng 300s, ảnh thumbnail 1000px hiển thị rõ nét; sau 300s làm mới trang, AWS trả về XML `Request has expired` (HTTP 403). | **Đạt** |
| **T15** | Tự phục hồi dịch vụ sau restart app / EC2 | Tiến trình Gunicorn tự động hồi sinh, Web Gallery hoạt động lại | Chạy `systemctl restart cloud-photo`; service chuyển sang `active (running)` với PID mới (31812); Gallery hoạt động bình thường, không mất dữ liệu. | **Đạt** |
| **T16** | Quyền IAM Role LabInstanceProfile của EC2 | Đọc/ghi S3 và DynamoDB từ EC2 không cần AWS credentials | Lệnh `aws s3 ls` và `aws dynamodb describe-table` thực thi thành công từ terminal EC2 thông qua IAM Role được gắn tự động. | **Đạt** |
| **T17** | **Nâng cao 1:** Tối ưu kích thước gói deploy qua Lambda Layer | Gói zip mã nguồn < 50 KB; mở được code trên Console | Gói deploy giảm xuống **3.7 kB** (giảm >99% size); Lambda gắn Pillow Layer v1; AWS Console hiển thị đầy đủ 2 file `.py` trên trình chỉnh sửa code. | **Đạt** |
| **T18** | **Nâng cao 2:** S3 Lifecycle Rule dọn thumbnail cũ | Quy tắc dọn dẹp kích hoạt thành công trên bucket output | Lifecycle Rule `auto-cleanup-old-thumbnails-7days` ở trạng thái **Enabled**; thiết lập tự xóa thumbnail sau 7 ngày và dọn multipart uploads. | **Đạt** |
| **T19** | Luồng xử lý ảnh End-to-End từ Web EC2 | Upload ảnh qua Web EC2 được xử lý hoàn chỉnh và hiển thị thumbnail | Upload `portrait.jpg` qua Web EC2; S3 trigger Lambda xử lý trong 604.68 ms; DynamoDB cập nhật `COMPLETE`; Web hiển thị bộ sưu tập ảnh thứ 10. | **Đạt** |

Nhóm đã đối chiếu 7 tình huống trên với ảnh chụp màn hình và log thực tế trên AWS. Toàn bộ 21 hình ảnh minh chứng được lưu trữ đầy đủ trong thư mục `evidence/tuan-3/` và được liên kết đối chiếu trong báo cáo chi tiết.

---

## 4. Phân công thực hiện

| Thành viên | Tài khoản GitHub | Phạm vi phụ trách |
|---|---|---|
| **Bùi Nguyễn Duy Trung** — 24110363 | [bndt0103](https://github.com/bndt0103) | Đóng gói Pillow thành Lambda Layer riêng biệt, tối ưu gói code deploy xuống 3.7 kB; thiết lập S3 Lifecycle Rule tự dọn dẹp thumbnail sau 7 ngày; cấu hình systemd service cho EC2; đo đạc log CloudWatch. |
| **Đỗ Anh Tuấn** — 24110369 | [DoAnhTuan-24110369](https://github.com/DoAnhTuan-24110369) | Khởi tạo máy chủ EC2, cấu hình môi trường ảo Python 3.12 và Gunicorn; thiết lập IAM Role; kiểm thử chặn truy cập trực tiếp S3; kiểm thử thời hạn Presigned URL 300s; kiểm thử tự phục hồi service; kiểm thử End-to-End upload ảnh. |

Nhóm phối hợp chặt chẽ giữa việc triển khai hạ tầng EC2, cấu hình tối ưu Serverless trên AWS Console và kiểm thử tích hợp thực tế. Ảnh và bảng kiểm thử ghi nhận kết quả thực tế trên tài nguyên AWS Academy của nhóm.

---

## 5. Báo cáo đính kèm

[Báo cáo Word tuần 3 — BaoCaoTuan3_24110363_24110369.docx](https://github.com/bndt0103/aws-thumbnail/blob/main/Report/BaoCaoTuan3_24110363_24110369.docx).

Báo cáo gồm 28 trang, trình bày chi tiết kiến trúc mở rộng trên EC2, cấu hình bảo mật IAM Role, quy trình kiểm thử T13–T19 và tích hợp đầy đủ **21 ảnh minh chứng thực tế** được chèn trực tiếp trong các phần tương ứng.

### Liên kết trực tiếp các file mã nguồn (theo nhận xét của GVHD):
Theo đúng nhận xét và chỉ đạo của Giảng viên hướng dẫn: *"Tuần này em chỉ link đúng một file docx, tuần sau link luôn các file code (worker, gallery, tests) vào báo cáo để thầy đối chiếu nhanh, không phải vào repo tìm"*, nhóm xin cung cấp liên kết trực tiếp tới từng file mã nguồn chính trong dự án:

- **Worker xử lý ảnh Lambda:** [`src/processor/lambda_function.py`](https://github.com/bndt0103/aws-thumbnail/blob/main/src/processor/lambda_function.py) — Xử lý sự kiện S3 ObjectCreated, kiểm tra chống trùng lặp, gọi Pillow và cập nhật metadata DynamoDB.
- **Thư viện xử lý ảnh Pillow:** [`src/processor/image_tools.py`](https://github.com/bndt0103/aws-thumbnail/blob/main/src/processor/image_tools.py) — Tạo 3 kích thước thumbnail (150px, 400px, 1000px), chèn watermark `CLOUD PHOTO`, chuẩn hóa RGB và loại bỏ EXIF.
- **Ứng dụng Web Gallery EC2:** [`src/web/app.py`](https://github.com/bndt0103/aws-thumbnail/blob/main/src/web/app.py) — Ứng dụng Flask hỗ trợ xác thực đăng nhập, bảo vệ CSRF, tải ảnh lên S3, đọc DynamoDB và sinh Presigned URL an toàn.
- **Cấu hình dịch vụ Systemd:** [`deploy/cloud-photo.service`](https://github.com/bndt0103/aws-thumbnail/blob/main/deploy/cloud-photo.service) — File cấu hình quản trị tiến trình Gunicorn chạy nền trên Amazon Linux 2023, tự động khởi động cùng hệ thống và tự phục hồi khi có sự cố.
- **Kịch bản tự động hóa đóng gói:** [`scripts/build_packages.py`](https://github.com/bndt0103/aws-thumbnail/blob/main/scripts/build_packages.py) — Script Python đóng gói gói mã nguồn siêu nhẹ cho Lambda (`lambda_processor.zip` chỉ 3.7 kB), web application (`web_app.zip`) và Lambda Layer Pillow.
- **Bộ kiểm thử Unit Test xử lý ảnh:** [`tests/test_images.py`](https://github.com/bndt0103/aws-thumbnail/blob/main/tests/test_images.py) — 10 ca kiểm thử các trường hợp ảnh ngang, dọc, vuông, trong suốt, dung lượng lớn, định dạng hỏng.
- **Bộ kiểm thử Unit Test Worker Lambda:** [`tests/test_worker.py`](https://github.com/bndt0103/aws-thumbnail/blob/main/tests/test_worker.py) — 5 ca kiểm thử logic worker bằng giả lập AWS mock.
- **Bộ kiểm thử Unit Test Web Gallery:** [`tests/test_web.py`](https://github.com/bndt0103/aws-thumbnail/blob/main/tests/test_web.py) — 4 ca kiểm thử giao diện, kiểm soát quyền truy cập và CSRF protection.

---

## 6. Khai báo hỗ trợ AI

**Công cụ:** Google Gemini. **Phiên bản model:** Gemini 3.8 Flash (High).

**Prompt đã dùng — tóm lược:** Hướng dẫn cấu hình dịch vụ systemd trên Linux; phân tích cơ chế xác thực không dùng khóa thông qua IAM Instance Profile và IMDSv2; hướng dẫn thiết lập chính sách S3 Lifecycle Rule dọn dẹp thumbnail sau 7 ngày; hướng dẫn sinh và kiểm tra thời hạn S3 Presigned URL (ExpiresIn=300); giải thích log CloudWatch và hỗ trợ biên tập báo cáo nộp bài bám sát ý kiến nhận xét của Giảng viên hướng dẫn.

**Nội dung AI hỗ trợ:** Đề xuất cấu trúc file unit systemd cho Gunicorn, hỗ trợ giải thích cấu hình biến môi trường (`APP_SECRET`, `TABLE_NAME`), phân tích mã lỗi HTTP và cơ chế bảo mật IAM Role / Presigned URL, hỗ trợ định dạng tài liệu Word và Markdown. AI cũng hỗ trợ rà soát các lệnh Git theo yêu cầu và ủy quyền của nhóm.

**Phần sinh viên thực hiện và kiểm chứng:** Nhóm trực tiếp khởi tạo và cấu hình máy chủ EC2 trên AWS Academy Learner Lab, cài đặt Gunicorn, cấu hình service qua systemctl, thiết lập S3 Lifecycle Rule và Lambda Layer trên Console, thực hiện toàn bộ 7 ca kiểm thử T13–T19 và chụp 21 ảnh minh chứng thực tế; đối chiếu thời gian xử lý, URL hết hạn sau 300s và số liệu log CloudWatch.

**Phần mã nguồn, cấu hình và minh chứng commit đối chiếu:** Các commit dưới đây ghi nhận các phần việc nhóm đã hoàn thiện trong Tuần 3 có AI hỗ trợ và đã được đẩy lên nhánh main của kho mã nguồn [bndt0103/aws-thumbnail](https://github.com/bndt0103/aws-thumbnail):

| Phần phân công | Nội dung đã hoàn thiện và được kiểm chứng | Commit đối chiếu |
|---|---|:---:|
| **Trung — Cấu hình S3 Lifecycle & Kịch bản deploy EC2** | Thiết lập S3 Lifecycle Rule dọn thumbnail cũ sau 7 ngày, viết file cấu hình dịch vụ systemd `deploy/cloud-photo.service`, cập nhật script đóng gói và gitignore. | [a75a35a](https://github.com/bndt0103/aws-thumbnail/commit/a75a35a2d58f2f63a2d556a37c9d464ffd9005e1) |
| **Trung — Minh chứng nâng cao Lambda Layer & S3 Lifecycle** | Bổ sung minh chứng gói deploy Lambda siêu nhẹ 3.7 kB gắn Pillow Layer v1 (`E22`, `E22-CODE`), quy tắc S3 Lifecycle Rule trạng thái Enabled trên bucket output (`E23a1`, `E23a2`, `E23b`). | [87e3a73](https://github.com/bndt0103/aws-thumbnail/commit/87e3a730afe0428ec418f21b4e333ff475c8f172) |
| **Tuấn — Cấu hình Gunicorn & Khởi tạo EC2 Gallery** | Cập nhật `src/web/requirements.txt`, khởi tạo EC2 running, gán IAM Role `LabInstanceProfile`, Security Group mở port 22/8000, systemd service active và curl health check (`E16a`–`E16e`). | [fd3e8f5](https://github.com/bndt0103/aws-thumbnail/commit/fd3e8f5a2d90cef94a541479b0b6f3dfbbb6f6b7) |
| **Tuấn — Kiểm thử Gallery EC2, Presigned URL & Tự phục hồi** | Bổ sung minh chứng giao diện Gallery login & dashboard (`E17*`), lệnh AWS CLI bằng IAM Role (`E24a`), chặn URL S3 trực tiếp (`E24b`), Presigned URL hợp lệ & hết hạn 300s (`E24c`, `E24d`), restart service tự phục hồi (`E25*`), upload End-to-End (`E26*`). | [138ac4e](https://github.com/bndt0103/aws-thumbnail/commit/138ac4e52312436585386dd34030c1bac713c732) |
| **Tuấn — Đối chiếu danh mục minh chứng & kết quả kiểm thử** | Tổng hợp và đối chiếu danh mục 21 minh chứng (`DANH_MUC_MINH_CHUNG.csv`), kết quả 7 ca kiểm thử tích hợp T13–T19 (`test-results.csv`) và tài liệu hướng dẫn Tuần 3 (`README.md`). | [070be51](https://github.com/bndt0103/aws-thumbnail/commit/070be51e5a57c016a9a5a8cf0ca386555f55cba4) |

Phần mã nguồn và cấu hình có AI hỗ trợ; các link commit dùng để đối chiếu phiên bản hoàn thiện và phần việc được phân công, không khẳng định toàn bộ mã được sinh viên viết độc lập.

---

## 7. Đánh giá và hướng tiếp theo

Nhóm hoàn thành xuất sắc mốc triển khai Tuần 3 trong toàn bộ phạm vi đã đề ra. Kiến trúc kết hợp giữa máy chủ IaaS (EC2) và các dịch vụ Serverless (S3, Lambda, DynamoDB) hoạt động trơn tru, tin cậy; loại bỏ hoàn toàn việc lưu trữ access key nhờ IAM Role `LabInstanceProfile`; bảo vệ quyền riêng tư qua Presigned URL có thời hạn 300 giây; và hiện thực hóa trọn vẹn cả 2 yêu cầu nâng cao về tối ưu dung lượng mã nguồn (3.7 kB) và tự động dọn dẹp lưu trữ sau 7 ngày.

Do giới hạn của môi trường học tập AWS Academy Learner Lab, máy chủ EC2 chưa được gán Elastic IP cố định và chưa thiết lập cân bằng tải tự động (ALB/Auto Scaling).

Tuần 4 dự kiến hoàn thiện hạch toán chi phí AWS, quay video demo sản phẩm hoàn chỉnh và chuẩn bị báo cáo tổng kết đồ án cuối kỳ.

Tuần 4 dự kiến hoàn thiện hạch toán chi phí AWS, quay video demo sản phẩm hoàn chỉnh và chuẩn bị báo cáo tổng kết đồ án cuối kỳ.

