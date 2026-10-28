# BÁO CÁO TIẾN ĐỘ TUẦN 4 — BÁO CÁO TỔNG KẾT ĐỒ ÁN CUỐI KỲ

**Đề tài:** Xử lý ảnh tự động: tạo thumbnail khi upload lên Amazon S3.

**Giảng viên hướng dẫn:** TS. Huỳnh Xuân Phụng.

**Nhóm thực hiện:** Bùi Nguyễn Duy Trung — MSSV 24110363; Đỗ Anh Tuấn — MSSV 24110369.

**Ngày đối chiếu kết quả:** 28/10/2026.

**Kho mã nguồn:** [bndt0103/aws-thumbnail](https://github.com/bndt0103/aws-thumbnail).

**Video Demo sản phẩm:** [Demo Xu Ly Anh Tu Dong AWS (24110363 - 24110369).mp4](https://drive.google.com/file/d/1AwaAWUkTE6Rjg70xBr83gmRPW5vs9j8_/view?usp=drive_link).

---

## 1. Mục tiêu và phạm vi đồ án sau 4 tuần

Trải qua 4 tuần nghiên cứu, thiết kế, triển khai và hoàn thiện thực nghiệm trên nền tảng điện toán đám mây **Amazon Web Services (AWS)**, nhóm đã xây dựng thành công một hệ thống xử lý ảnh tự động hoàn chỉnh kết hợp tối ưu giữa hạ tầng máy chủ **IaaS (Amazon EC2)** và nền tảng phi máy chủ **Serverless (S3, Lambda, DynamoDB, CloudWatch)**.

Lộ trình thực hiện của đồ án bám sát kế hoạch và tiếp thu nghiêm túc mọi nhận xét chỉ đạo của Giảng viên hướng dẫn qua từng tuần:

- **Tuần 1 — Khởi tạo nền tảng và Thiết kế kiến trúc:** Định hình kiến trúc hướng sự kiện (Event-driven Architecture), xây dựng module xử lý ảnh Pillow (tạo 3 kích thước 150px, 400px, 1000px, giữ tỷ lệ, watermark `CLOUD PHOTO`, loại bỏ EXIF, nền trắng cho PNG trong suốt), viết 19 ca kiểm thử giả lập đạt 100% và tạo tài nguyên nền tảng trên AWS.
- **Tuần 2 — Tích hợp hệ thống Serverless trên AWS:** Kết nối luồng sự kiện thực tế giữa S3 Input (`uploads/`), trigger Lambda `cloud-photo-processor`, ghi 3 thumbnail vào S3 Output (`thumbnails/`), cập nhật trạng thái `COMPLETE` vào DynamoDB và ghi vết CloudWatch Logs. Kiểm chứng 12 ca kiểm thử T01–T12 trên AWS.
- **Tuần 3 — Triển khai Web Gallery trên EC2 và Hoàn thành 2 yêu cầu Nâng cao của GVHD:**
  * Đưa Web Gallery lên máy chủ **Amazon EC2** chạy Amazon Linux 2023, máy chủ ứng dụng **Gunicorn WSGI (2 workers)**, quản trị tiến trình nền bằng **systemd service** (`cloud-photo.service`) có cơ chế tự phục hồi (`Restart=on-failure`).
  * Ứng dụng **IAM Role (`LabInstanceProfile`)** để máy chủ EC2 tự động nhận quyền đọc/ghi S3 và DynamoDB qua dịch vụ Instance Metadata (IMDSv2), tuyệt đối **không lưu trữ Access Key / Secret Key** tĩnh.
  * Giữ S3 Output ở chế độ **Private tuyệt đối** (chặn truy cập trực tiếp HTTP 403 `AccessDenied`), cấp quyền xem ảnh qua **Presigned URL có thời hạn chính xác 300 giây (`X-Amz-Expires=300`)**; quá 300 giây trả về `Request has expired`.
  * **Nâng cao 1:** Tách thư viện Pillow thành **Lambda Layer** riêng (`cloud-photo-pillow` v1), giúp gói zip deploy của Lambda Function giảm siêu tối ưu từ >15 MB xuống chỉ còn **3.7 kB** (chỉ chứa 2 file code), cho phép mở và sửa trực tiếp trên AWS Console Code Editor.
  * **Nâng cao 2:** Thiết lập **S3 Lifecycle Rule** (`auto-cleanup-old-thumbnails-7days`) trên bucket output, tự động dọn dẹp và xóa các ảnh thumbnail sau 7 ngày kể từ ngày tạo và hủy multipart uploads dở dang để tối ưu chi phí lưu trữ.
- **Tuần 4 — Chốt đồ án cuối kỳ theo 4 nhiệm vụ được GVHD phê duyệt:**
  1. **Hạch toán chi phí AWS chi tiết:** Phân tích mô hình định giá AWS Pricing (us-east-1) cho toàn bộ tài nguyên đã sử dụng; đối chiếu thực tế mức sử dụng trong phòng lab AWS Academy Learner Lab (**Used \$0 of \$50**; chi phí ước tính thực tế chỉ **\$0.52 USD**); hạch toán chi phí vận hành ở quy mô doanh nghiệp nhỏ (10,000 ảnh/tháng ~ \$13.21 USD/tháng) và chứng minh ưu thế tiết kiệm **hơn 85% chi phí** so với việc thuê máy chủ truyền thống (Monolith EC2).
  2. **Quay Video Demo sản phẩm hoàn chỉnh:** Xây dựng kịch bản phân cảnh chi tiết từng phút, phân vai Trung và Tuấn, quay video thực nghiệm Full HD thời lượng **dưới 10 phút**, trình diễn toàn bộ hệ thống từ EC2 Web Gallery đến các dịch vụ Serverless phía sau và các tính năng nâng cao, xuất bản lên Google Drive.
  3. **Quy trình dọn dẹp tài nguyên sau demo (Teardown):** Xây dựng script tự động hóa [`scripts/teardown_resources.py`] và thực hiện dọn dẹp sạch sẽ tài nguyên trên AWS theo đúng thứ tự phụ thuộc (Terminate EC2, Empty/Delete 2 S3 buckets, xóa Lambda, xóa DynamoDB table, xóa CloudWatch log group).
  4. **Báo cáo tổng kết đồ án cuối kỳ:** Biên tập tài liệu Word tổng kết toàn diện 4 tuần (`Report/BaoCaoTongKet_24110363_24110369.docx`) và báo cáo Markdown nộp bài, tích hợp đầy đủ toàn bộ 80 hình ảnh minh chứng thực tế của cả 4 tuần dự án (Tuần 1: 20 ảnh, Tuần 2: 33 ảnh, Tuần 3: 21 ảnh, Tuần 4: 5 ảnh và sơ đồ kiến trúc), sửa triệt để câu lặp ở Mục 7 theo đúng nhắc nhở của thầy.

---

## 2. Công việc và kết quả triển khai toàn bộ hệ thống

### 2.1 Bảng tổng hợp cấu hình kiến trúc toàn diện (Tuần 1 – Tuần 4)

| Thành phần kiến trúc | Cấu hình triển khai thực tế trên AWS | Đánh giá & Vai trò trong hệ thống |
|---|---|---|
| **AWS Region** | `us-east-1` — N. Virginia (Subnet `us-east-1d`). | Đảm bảo độ trễ thấp và hỗ trợ toàn diện các tính năng AWS. |
| **Máy chủ Web (EC2)** | Instance ID `i-0390fda0b0a75c002`; loại `t2.micro` (1 vCPU, 1 GiB RAM); Amazon Linux 2023; Public IP `100.31.151.65` (phiên Tuần 3) / `54.202.165.232` (phiên Tuần 4); Private IP `172.31.16.240`. | Đóng vai trò Web Gateway trung gian tiếp nhận yêu cầu tải ảnh từ người dùng; cách ly người dùng với hạ tầng backend. |
| **Bảo mật IAM Role** | Gắn IAM Role `LabRole` qua `LabInstanceProfile`. Ứng dụng lấy quyền đọc/ghi S3 và DynamoDB qua IMDSv2. | Loại bỏ triệt để việc lưu Access Key tĩnh; tự động xoay vòng thông tin xác thực tạm thời theo chuẩn AWS Security. |
| **Tường lửa Security Group** | `cloud-photo-web-sg`; Inbound chỉ mở cổng 22 (SSH) và cổng 8000 (Custom TCP); Outbound mở toàn bộ 0.0.0.0/0. | Đảm bảo an toàn mạng, chặn mọi kết nối trái phép vào các cổng không sử dụng. |
| **Quản trị tiến trình Web** | Systemd service `/etc/systemd/system/cloud-photo.service`; chạy Gunicorn 26.2.0 với 2 sync workers; `Restart=on-failure`, `RestartSec=5s`. | Duy trì dịch vụ web hoạt động liên tục 24/7; tự động hồi sinh khi tiến trình gặp sự cố mà không làm gián đoạn hệ thống. |
| **Kênh truy cập Web an toàn** | SSH Local Port Forwarding qua cổng 8080 (`ssh -i labsuser.pem -L 8080:localhost:8000 ec2-user@<IP>`); truy cập qua `http://localhost:8080`. | Mã hóa toàn bộ lưu lượng web qua đường hầm SSH; kiểm tra endpoint `/health` trả về `{"status":"ok"}`. |
| **S3 Input Bucket** | `cloudphoto-input-103308504802`; lưu ảnh gốc trong tiền tố `uploads/<image_id>/`; sự kiện kích hoạt `s3:ObjectCreated:*`. | Tiếp nhận ảnh gốc tải lên từ Web; phát tín hiệu sự kiện kích hoạt tức thì tới Lambda Function. |
| **Hàm xử lý Serverless (Lambda)**| `cloud-photo-processor`; Python 3.12 (x86_64); 1024 MB RAM; timeout 60 giây; handler `lambda_function.lambda_handler`; Role: `LabRole`. | Tự động co giãn theo tải (Scale-to-Zero khi rỗi, xử lý song song khi tải cao); thời gian xử lý trung bình chỉ **604.68 ms**, RAM tiêu thụ **153 MB**. |
| **Lambda Layer (Nâng cao 1)** | `cloud-photo-pillow` phiên bản 1 (~5 MB); tách riêng toàn bộ thư viện Pillow và các file nhị phân C shared library. | Giúp gói zip deploy của hàm Lambda đạt **3.7 kB** (giảm >99.9% dung lượng); hiển thị trực quan toàn bộ code trên AWS Console Code Editor. |
| **S3 Output Bucket** | `cloudphoto-output-103308504802`; lưu 3 kích thước thumbnail trong `thumbnails/<image_id>/` (`150.jpg`, `400.jpg`, `1000.jpg`). | Lưu trữ ảnh kết quả sau xử lý; áp dụng chính sách Block Public Access (Private tuyệt đối). |
| **S3 Lifecycle Rule (Nâng cao 2)**| Quy tắc `auto-cleanup-old-thumbnails-7days` trạng thái **Enabled** trên bucket output; tự xóa objects sau 7 ngày và dọn multipart uploads sau 7 ngày. | Tự động hóa quản lý vòng đời dữ liệu; ngăn chặn tích tụ dung lượng thumbnail cũ; tối ưu chi phí lưu trữ mà không cần viết mã dọn dẹp. |
| **Bảo mật Presigned URL** | Bucket output chặn truy cập trực tiếp (HTTP 403 `AccessDenied`); cấp Presigned URL có thời hạn hợp lệ chính xác **300 giây (`X-Amz-Expires=300`)**. | Bảo vệ bản quyền và quyền riêng tư ảnh; quá thời hạn 300 giây trình duyệt bị từ chối với mã lỗi `Request has expired`. |
| **Cơ sở dữ liệu DynamoDB** | Bảng `cloud-photo-metadata`; khóa phân vùng `image_id` (String); chế độ On-demand Capacity Mode. | Lưu trữ siêu dữ liệu ảnh (tên gốc, kích thước, thời gian, trạng thái `COMPLETE`/`FAILED`, các variant keys) để Web Gallery tra cứu. |
| **Giám sát CloudWatch Logs** | Nhóm log `/aws/lambda/cloud-photo-processor`; thời gian lưu trữ (retention) 7 ngày. | Lưu vết toàn bộ hoạt động thực thi: Duration, Billed Duration, Memory Used, phát hiện và bỏ qua sự kiện trùng lặp (`DUPLICATE_SKIPPED`). |
| **Hạch toán chi phí AWS** | Bảng chi phí thực tế và dự toán chi tiết tại `progress/week-4/costs.csv`. | Quá trình học tập thực tế tốn **\$0.52 USD** (Used \$0 of \$50); quy mô 10,000 ảnh/tháng tốn **\$13.21 USD/tháng**, tiết kiệm hơn 85% chi phí. |
| **Dọn dẹp tài nguyên (Teardown)** | Script tự động hóa `scripts/teardown_resources.py` dọn sạch EC2 (Terminated), S3 Buckets (0), DynamoDB Tables (0). | Đảm bảo tính chuyên nghiệp và tuân thủ nguyên tắc an toàn dữ liệu, bảo toàn ngân sách phòng lab. |

---

### 2.2 Bảng phân tích chi phí AWS chi tiết và so sánh hiệu quả kinh tế

| Dịch vụ AWS | Thành phần tính phí | Đơn giá AWS (us-east-1) | Mức dùng thực tế Lab | Chi phí thực tế Lab | Dự toán 10.000 ảnh/tháng | Chi phí 10.000 ảnh/tháng |
|---|---|---|---|:---:|---|:---:|
| **Amazon EC2** | `t2.micro` (1 vCPU, 1 GiB) | \$0.0116 / giờ | 12 giờ chạy | 0.14 USD | 720 giờ (chạy 24/7) | 8.35 USD |
| **Amazon EBS** | gp3 General Purpose SSD | \$0.08 / GB-tháng | 8 GiB × 0.5 tháng | 0.32 USD | 8 GiB × 1 tháng | 0.64 USD |
| **Amazon VPC** | Public IPv4 Address | \$0.005 / giờ | 12 giờ | 0.06 USD | 720 giờ | 3.60 USD |
| **Amazon S3** | Standard Storage | \$0.023 / GB-tháng | 0.05 GB | 0.00 USD | 15 GB (gốc + 3 thumbnail) | 0.35 USD |
| **Amazon S3** | Requests (PUT / POST) | \$0.005 / 1,000 requests | 50 requests | 0.00 USD | 40,000 requests | 0.20 USD |
| **Amazon S3** | Requests (GET) | \$0.0004 / 1,000 requests | 120 requests | 0.00 USD | 100,000 requests | 0.04 USD |
| **Amazon S3** | Lifecycle Expiration | **\$0.00 (Miễn phí)** | 30 objects | 0.00 USD | 30,000 objects | 0.00 USD |
| **AWS Lambda** | Invocations (Số lần gọi) | \$0.20 / 1,000,000 req | 15 invocations | 0.00 USD (Free Tier) | 10,000 invocations | 0.00 USD (Free Tier) |
| **AWS Lambda** | Compute Time (1024 MB ~0.6s) | \$0.0000166667 / GB-s | 9.0 GB-giây | 0.00 USD (Free Tier) | 6,000 GB-giây | 0.00 USD (Free Tier) |
| **Amazon DynamoDB**| Write Request Units (WRU) | \$1.25 / 1,000,000 WRU | 20 writes | 0.00 USD | 20,000 writes | 0.03 USD |
| **Amazon DynamoDB**| Read Request Units (RRU) | \$0.25 / 1,000,000 RRU | 80 reads | 0.00 USD | 150,000 reads | 0.04 USD |
| **Amazon DynamoDB**| Indexed Data Storage | \$0.25 / GB-tháng | 0.001 GB | 0.00 USD (Free Tier) | 0.02 GB | 0.00 USD (Free Tier) |
| **Amazon CloudWatch**| Log Ingestion & Storage | Ingestion \$0.50/GB; Storage \$0.03/GB | 0.01 GB | 0.00 USD (Free Tier) | 0.15 GB | 0.00 USD (Free Tier) |
| **Data Transfer** | Internet Data Transfer OUT | \$0.09 / GB | 0.05 GB | 0.00 USD (Free Tier) | 5.0 GB | 0.00 USD (Free Tier) |
| **TỔNG CỘNG** | **Toàn bộ hệ thống** | | **Thực tế Lab** | **0.52 USD** *(Used \$0 of \$50)* | **Doanh nghiệp nhỏ** | **13.21 USD / tháng** |

> **Phân tích so sánh kiến trúc:**
> - Nếu sử dụng giải pháp truyền thống (Pure EC2 Monolith chạy xử lý ảnh trực tiếp trên máy chủ), hệ thống bắt buộc phải thuê máy chủ cấu hình mạnh (`t3.medium` hoặc `c5.large`) với chi phí cố định từ **\$35.00 đến \$65.00 USD/tháng**. Nếu có tải đột biến (Spike), hệ thống buộc phải cấu hình thêm Application Load Balancer (ALB) và Auto Scaling Group, đẩy chi phí lên trên **\$100.00 USD/tháng** dù phần lớn thời gian máy chủ không có tải.
> - Ngược lại, kiến trúc phân tán Serverless kết hợp EC2 của nhóm: máy chủ EC2 chỉ đóng vai trò Web Gateway siêu nhẹ (`t2.micro`), toàn bộ tác vụ xử lý nặng do AWS Lambda đảm nhiệm theo cơ chế Pay-as-you-go (tính tiền đúng số mili-giây xử lý). Khi không có ảnh tải lên, chi phí xử lý = \$0.00. Với quy mô 10,000 ảnh/tháng, cụm Serverless S3+Lambda+DynamoDB chỉ tiêu tốn chưa tới **\$1.00 USD**, giúp tổng chi phí vận hành giảm xuống chỉ còn **\$13.21 USD/tháng**, mang lại hiệu quả tiết kiệm kinh tế **hơn 85%**.

---

## 3. Tổng hợp kiểm thử

Toàn bộ hệ thống đã trải qua quy trình kiểm thử thực nghiệm nghiêm ngặt gồm **19 ca kiểm thử trên AWS thực tế** (kế thừa trọn vẹn từ Tuần 2 và Tuần 3) cùng các hạng mục kiểm chứng hoàn tất của Tuần 4, đạt tỷ lệ thành công **100%**:

| Mã | Tình huống kiểm thử | Kỳ vọng | Kết quả quan sát thực tế trên AWS | Đánh giá |
|---|---|---|---|:---:|
| **T01** | Ảnh ngang 1600 × 1000 px | Tạo 3 ảnh thumbnail giữ tỷ lệ, có watermark | Tạo ảnh 150 × 94, 400 × 250 và 1000 × 625 px; có watermark `CLOUD PHOTO`. | **Đạt** |
| **T02** | Ảnh dọc 900 × 1500 px | Tạo 3 ảnh thumbnail dọc giữ tỷ lệ | Tạo ảnh 90 × 150, 240 × 400 và 600 × 1000 px; đúng tỷ lệ chiều dọc. | **Đạt** |
| **T03** | Ảnh vuông 1000 × 1000 px | Tạo 3 ảnh thumbnail vuông chuẩn | Tạo ảnh 150 × 150, 400 × 400 và 1000 × 1000 px. | **Đạt** |
| **T04** | PNG trong suốt 800 × 600 px | Chuyển nền trong suốt thành trắng, tạo JPEG | Nền trong suốt chuyển thành trắng; tạo ảnh 150 × 113, 400 × 300 và 800 × 600 px. | **Đạt** |
| **T05** | Ảnh nhỏ 80 × 60 px | Giữ nguyên kích thước gốc, không phóng to | Cả 3 phiên bản đều giữ nguyên 80 × 60 px, không upscale vỡ nét. | **Đạt** |
| **T06** | Tệp dữ liệu hỏng `broken.jpg` | Bắt lỗi hợp lệ, từ chối xử lý an toàn | DynamoDB ghi nhận trạng thái từ chối và lý do tệp ảnh không hợp lệ. | **Đạt** |
| **T07** | Tệp vượt giới hạn 10 MiB | Giao diện và API từ chối tải lên | Giao diện từ chối tệp 10.5 MiB; gửi trực tiếp qua POST nhận HTTP 400. | **Đạt** |
| **T08** | Chạy lại cùng JSON event | Chống lặp tác vụ (Idempotency) | Lần đầu `COMPLETE`, lần sau CloudWatch ghi `DUPLICATE_SKIPPED`; không ghi lại S3. | **Đạt** |
| **T09** | Tải tệp vào bucket output | Tách nguồn sự kiện, không lặp vô tận | Bucket output không có notification, EventBridge tắt; không kích hoạt lại Lambda. | **Đạt** |
| **T10** | Upload 2 ảnh cùng tên tệp | Phân biệt tệp bằng UUID, không ghi đè | Cấp 2 `image_id` và `source_key` khác nhau; cả 2 ảnh đều hoàn tất `COMPLETE`. | **Đạt** |
| **T11** | Gọi API sau khi đăng xuất | Kiểm soát truy cập người dùng | Gọi `GET /api/photos` khi hết phiên trả về HTTP 401 UNAUTHORIZED. | **Đạt** |
| **T12** | Gửi form thiếu CSRF token | Phòng chống tấn công Cross-Site | Gọi `POST /api/upload` thiếu token bảo mật trả về HTTP 403 FORBIDDEN. | **Đạt** |
| **T13** | Chặn truy cập trực tiếp S3 | Giữ kho ảnh kết quả riêng tư tuyệt đối | Mở trực tiếp link S3 Output nhận XML `AccessDenied` (HTTP 403 Forbidden). | **Đạt** |
| **T14** | Thời hạn Presigned URL (300s) | Mở được trong 300s, sau 300s hết hạn | Trong 300s hiển thị ảnh rõ nét; sau 300s refresh nhận XML `Request has expired`. | **Đạt** |
| **T15** | Tự phục hồi sau restart service | Gunicorn tự động hồi sinh qua systemd | Lệnh `systemctl restart cloud-photo` tạo lại tiến trình với PID mới (31812); web chạy ổn định. | **Đạt** |
| **T16** | Quyền IAM Role của EC2 | Đọc/ghi AWS không cần static keys | Lệnh `aws s3 ls` và `aws dynamodb describe-table` từ EC2 thành công qua `LabInstanceProfile`. | **Đạt** |
| **T17** | **Nâng cao 1:** Lambda Layer Pillow | Gói code deploy < 50 KB, mở Console | Gói deploy giảm xuống **3.7 kB** (giảm >99% size); mở xem trực tiếp trên Code Editor. | **Đạt** |
| **T18** | **Nâng cao 2:** S3 Lifecycle Rule | Quy tắc dọn dẹp thumbnail kích hoạt | Rule `auto-cleanup-old-thumbnails-7days` trạng thái **Enabled**; tự xóa objects sau 7 ngày. | **Đạt** |
| **T19** | Luồng End-to-End từ Web EC2 | Upload ảnh từ Web EC2 xử lý trọn vẹn | Upload `portrait.jpg` qua Web EC2; Lambda xử lý 604.68 ms / 153 MB; Web hiện ảnh thứ 10. | **Đạt** |
| **T20** | **Tuần 4:** Hạch toán chi phí AWS | Bảng chi phí thực tế và so sánh kiến trúc | Màn hình AWS Academy hiển thị `Used $0 of $50`; bảng chi phí thực tế đạt 0.52 USD. | **Đạt** |
| **T21** | **Tuần 4:** Video Demo sản phẩm | Video hoàn chỉnh ≤ 10 phút trên Drive | Video Full HD thời lượng 7 phút 20 giây trình diễn đầy đủ hệ thống trên Google Drive. | **Đạt** |
| **T22** | **Tuần 4:** Dọn dẹp tài nguyên AWS | Teardown sạch sẽ EC2, S3, DynamoDB | Script dọn dẹp thành công: EC2 `Terminated`, S3 `Buckets (0)`, DynamoDB `Tables (0)`. | **Đạt** |

---

## 4. Phân công thực hiện

Nhóm duy trì sự phân công công việc minh bạch, bình đẳng, đóng góp đồng đều xuyên suốt toàn bộ đồ án:

| Thành viên thực hiện | Tài khoản GitHub | Phạm vi phụ trách và Đóng góp chính | Tỷ lệ đóng góp |
|---|---|---|:---:|
| **Bùi Nguyễn Duy Trung**<br>MSSV: 24110363 | [bndt0103](https://github.com/bndt0103)<br>(Sinh viên A) | • **Tuần 1 & 2:** Thiết kế kiến trúc Serverless, đóng gói Lambda worker, cấu hình trigger S3, DynamoDB và CloudWatch.<br>• **Tuần 3:** Đóng gói Pillow thành Lambda Layer riêng (v1), tối ưu gói code deploy xuống 3.7 kB; thiết lập S3 Lifecycle Rule tự xóa thumbnail sau 7 ngày; viết kịch bản dịch vụ systemd cho EC2.<br>• **Tuần 4:** Xây dựng bảng hạch toán chi phí AWS chi tiết và so sánh hiệu quả kinh tế; viết script tự động hóa dọn dẹp tài nguyên `teardown_resources.py`; thực hiện dọn sạch môi trường Lab và kiểm chứng E27, E29a, E29b, E29c. | **100%**<br>*(Hoàn thành xuất sắc)* |
| **Đỗ Anh Tuấn**<br>MSSV: 24110369 | [DoAnhTuan-24110369](https://github.com/DoAnhTuan-24110369)<br>(Sinh viên B) | • **Tuần 1 & 2:** Xây dựng ứng dụng Web Gallery Flask, xử lý xác thực đăng nhập, CSRF, sinh UUID và hiển thị thumbnail qua Presigned URL; thực hiện 19 ca kiểm thử giả lập.<br>• **Tuần 3:** Khởi tạo máy chủ EC2 `cloud-photo-gallery`, cấu hình Gunicorn 26.2.0, gán IAM Role `LabInstanceProfile`, thiết lập SSH tunnel; thực hiện các ca kiểm thử bảo mật (T13–T16) và luồng upload End-to-End.<br>• **Tuần 4:** Xây dựng kịch bản chi tiết quay video demo sản phẩm; quay và biên tập video demo Full HD; xuất bản video lên Google Drive và kiểm chứng E28; tổng hợp danh mục minh chứng và bảng nghiệm thu đồ án. | **100%**<br>*(Hoàn thành xuất sắc)* |

Nhóm phối hợp chặt chẽ, hỗ trợ lẫn nhau trong mọi công đoạn từ thiết kế mã nguồn, triển khai trên AWS Academy Learner Lab cho đến quay video và hoàn thiện tài liệu báo cáo. Toàn bộ kết quả đều được đối chiếu chéo giữa hai thành viên và kiểm chứng trên tài nguyên thực tế.

---

## 5. Báo cáo đính kèm và Liên kết trực tiếp các tài nguyên dự án

Thực hiện nghiêm túc nhận xét và chỉ đạo của Giảng viên hướng dẫn: *"Tuần sau link luôn các file code (worker, gallery, tests) vào báo cáo để thầy đối chiếu nhanh, không phải vào repo tìm"*, nhóm xin cung cấp liên kết trực tiếp tới toàn bộ tài liệu báo cáo, video demo và từng file mã nguồn chính trong dự án:

### 5.1 Báo cáo hoàn thiện và Video Demo sản phẩm:
- **Báo cáo Word tổng kết cuối kỳ:** [BaoCaoTongKet_24110363_24110369.docx](https://github.com/bndt0103/aws-thumbnail/blob/main/Report/BaoCaoTongKet_24110363_24110369.docx) *(Báo cáo học thuật toàn diện 4 tuần, gồm 9 chương, dung lượng 13.7 MB, tích hợp sơ đồ kiến trúc, bảng hạch toán chi phí, kịch bản video demo, quy trình dọn tài nguyên và toàn bộ 80 hình ảnh minh chứng thực tế qua 4 tuần)*.
- **Video Demo sản phẩm hoàn chỉnh:** [Demo Xu Ly Anh Tu Dong AWS (24110363 - 24110369).mp4](https://drive.google.com/file/d/1AwaAWUkTE6Rjg70xBr83gmRPW5vs9j8_/view?usp=drive_link) *(Video Full HD thời lượng 7 phút 20 giây, thuyết minh đầy đủ các thành phần EC2, Web Gallery, S3, Lambda Layer 3.7 kB, DynamoDB, CloudWatch, Presigned URL 300s và khả năng tự phục hồi service)*.

### 5.2 Liên kết trực tiếp các file mã nguồn và cấu hình chính:
- **Worker xử lý ảnh Lambda:** [`src/processor/lambda_function.py`](https://github.com/bndt0103/aws-thumbnail/blob/main/src/processor/lambda_function.py) — Tiếp nhận sự kiện S3 `ObjectCreated:*`, xử lý chống trùng lặp (Idempotency), gọi module Pillow, ghi kết quả S3 và cập nhật DynamoDB.
- **Thư viện xử lý ảnh Pillow:** [`src/processor/image_tools.py`](https://github.com/bndt0103/aws-thumbnail/blob/main/src/processor/image_tools.py) — Co giãn 3 kích thước (150px, 400px, 1000px), giữ tỷ lệ khung hình, dập watermark `CLOUD PHOTO`, loại bỏ EXIF metadata và chuyển nền trong suốt thành trắng.
- **Ứng dụng Web Gallery EC2:** [`src/web/app.py`](https://github.com/bndt0103/aws-thumbnail/blob/main/src/web/app.py) — Ứng dụng Flask hỗ trợ xác thực mật khẩu, phòng chống CSRF, tải ảnh lên S3 qua boto3, đọc DynamoDB và sinh Presigned URL có thời hạn 300s.
- **Cấu hình dịch vụ Systemd:** [`deploy/cloud-photo.service`](https://github.com/bndt0103/aws-thumbnail/blob/main/deploy/cloud-photo.service) — File cấu hình quản trị tiến trình Gunicorn chạy nền trên Amazon Linux 2023, tự động khởi động cùng hệ thống và tự phục hồi khi có sự cố.
- **Kịch bản tự động hóa đóng gói:** [`scripts/build_packages.py`](https://github.com/bndt0103/aws-thumbnail/blob/main/scripts/build_packages.py) — Script đóng gói gói mã nguồn siêu nhẹ cho Lambda (`lambda_processor.zip` chỉ 3.7 kB), web application (`web_app.zip`) và Lambda Layer Pillow.
- **Kịch bản dọn dẹp tài nguyên AWS:** [`scripts/teardown_resources.py`](https://github.com/bndt0103/aws-thumbnail/blob/main/scripts/teardown_resources.py) — Script tự động hóa kiểm tra (`--dry-run`) và dọn dẹp an toàn (`--confirm`) toàn bộ tài nguyên dự án trên AWS sau khi kết thúc demo.
- **Bộ kiểm thử Unit Test xử lý ảnh:** [`tests/test_images.py`](https://github.com/bndt0103/aws-thumbnail/blob/main/tests/test_images.py) — 10 ca kiểm thử các trường hợp ảnh ngang, dọc, vuông, trong suốt, dung lượng lớn, định dạng hỏng.
- **Bộ kiểm thử Unit Test Worker Lambda:** [`tests/test_worker.py`](https://github.com/bndt0103/aws-thumbnail/blob/main/tests/test_worker.py) — 5 ca kiểm thử logic worker bằng giả lập AWS mock.
- **Bộ kiểm thử Unit Test Web Gallery:** [`tests/test_web.py`](https://github.com/bndt0103/aws-thumbnail/blob/main/tests/test_web.py) — 4 ca kiểm thử giao diện web, kiểm soát quyền truy cập và CSRF protection.

---

## 6. Khai báo hỗ trợ AI

Nhóm cam kết tính trung thực học thuật và xin khai báo đầy đủ, minh bạch việc sử dụng công cụ Trí tuệ Nhân tạo (AI) trong quá trình thực hiện đồ án:

- **Các công cụ và phiên bản mô hình AI sử dụng:**
  - **Google Gemini:** Phiên bản mô hình **Gemini 3.8 Flash (High)**.
- **Tóm lược các prompt đã sử dụng:**
  - Hướng dẫn tra cứu định giá chính thức của AWS (Region us-east-1), xây dựng công thức tính toán chi phí chi tiết cho EC2, S3, Lambda, DynamoDB, CloudWatch và lập bảng so sánh kinh tế giữa Serverless vs EC2 Monolith.
  - Tư vấn xây dựng khung kịch bản phân cảnh chi tiết cho video demo sản phẩm (giới hạn thời lượng dưới 10 phút, phân vai người nói, thao tác màn hình, lời thoại thuyết minh tiếng Việt).
  - Hướng dẫn xây dựng script Python `scripts/teardown_resources.py` ứng dụng boto3 để tự động hóa quy trình dọn dẹp tài nguyên theo đúng thứ tự phụ thuộc an toàn.
  - Hỗ trợ xây dựng script Python tự động hóa biên tập tài liệu Word (`python-docx` + `Pillow`) để sinh báo cáo tổng kết cuối kỳ chuyên nghiệp, tự động vẽ sơ đồ kiến trúc và nhúng toàn bộ 80 hình ảnh minh chứng của cả 4 tuần.
- **Nội dung AI hỗ trợ:**
  - Đề xuất các bảng dữ liệu hạch toán chi phí `progress/week-4/costs.csv`.
  - Hỗ trợ cấu trúc script kịch bản video demo `docs/HUONG_DAN_TUAN_4.md`.
  - Hỗ trợ giải thích và gỡ lỗi `NoCredentialsError` / `ModuleNotFoundError` khi chạy script trên môi trường máy tính cá nhân.
  - Hỗ trợ định dạng tài liệu báo cáo học thuật Word và Markdown nộp bài.
- **Phần sinh viên trực tiếp thực hiện và kiểm chứng:**
  - Trực tiếp thao tác cấu hình, vận hành và quản trị trên AWS Academy Learner Lab trong suốt 4 tuần.
  - Trực tiếp quay, thuyết minh và biên tập video demo sản phẩm hoàn chỉnh Full HD, tải video lên Google Drive và chụp ảnh minh chứng E28.
  - Trực tiếp thực hiện quy trình dọn dẹp tài nguyên trên AWS Management Console và kiểm chứng terminal sạch tài nguyên (E27, E29a, E29b, E29c).
  - Tự tay thực hiện toàn bộ 4 commit Tuần 4 và đẩy lên kho mã nguồn GitHub theo đúng quy trình phối hợp tránh xung đột.

### Phần mã nguồn, cấu hình và minh chứng commit đối chiếu trên GitHub (Tuần 4):

Toàn bộ 4 commit dưới đây đã được nhóm thực hiện thành công và đẩy lên nhánh `main` của kho mã nguồn [bndt0103/aws-thumbnail](https://github.com/bndt0103/aws-thumbnail):

| Phần phân công | Nội dung đã hoàn thiện và được kiểm chứng | Commit đối chiếu trên GitHub |
|---|---|:---:|
| **Trung — Kịch bản dọn dẹp, Dữ liệu chi phí & Sửa lỗi Tuần 3** | Viết script dọn dẹp tài nguyên an toàn `scripts/teardown_resources.py`, lập bảng dữ liệu hạch toán chi phí `progress/week-4/costs.csv`, cập nhật `.gitignore` và sửa dứt điểm lỗi lặp câu trong `BAO_CAO_NOP_BAI_TUAN3.md`. | [`a72a92c`](https://github.com/bndt0103/aws-thumbnail/commit/a72a92cdaec2da483eb26ea7f00e5b8214eb43e4) |
| **Trung — Minh chứng ngân sách AWS & Dọn dẹp tài nguyên** | Bổ sung minh chứng ngân sách AWS Academy Learner Lab `Used $0 of $50` (`E27`) và bộ 3 ảnh kiểm chứng dọn dẹp sạch sẽ tài nguyên sau demo: EC2 Terminated (`E29a`), S3 Buckets deleted (`E29b`), DynamoDB Tables deleted (`E29c`). | [`700d73e`](https://github.com/bndt0103/aws-thumbnail/commit/700d73e0e2aeb02cb86f418e9af4454e706f1fda) |
| **Tuấn — Minh chứng Video Demo sản phẩm hoàn chỉnh** | Bổ sung minh chứng liên kết video demo sản phẩm `Demo Xu Ly Anh Tu Dong AWS (24110363 - 24110369).mp4` thời lượng 7:20 trên Google Drive (`E28`) và cập nhật cấu hình file theo dõi `.gitignore`. | [`f068057`](https://github.com/bndt0103/aws-thumbnail/commit/f068057a85a20ffc4c321a5d87770d1f73fc0814) |
| **Tuấn — Đối chiếu danh mục minh chứng & Nghiệm thu đồ án** | Hoàn thiện bảng danh mục 5 minh chứng Tuần 4 (`evidence/tuan-4/DANH_MUC_MINH_CHUNG.csv`), tệp mô tả `README.md` và bảng nghiệm thu tổng kết 4 nhiệm vụ cốt lõi của đồ án (`progress/week-4/final-review.csv`). | [`89a1034`](https://github.com/bndt0103/aws-thumbnail/commit/89a1034fde391f38aefaddd8a40524e37ea321c4) |

*Phần mã nguồn, tài liệu và kịch bản có sự hỗ trợ của các công cụ AI; các liên kết commit trên được dẫn để đối chiếu minh chứng phiên bản hoàn thiện và phần việc được phân công, không khẳng định toàn bộ mã được sinh viên viết hoàn toàn độc lập.*

---

## 7. Kết luận và Tổng kết đồ án

Sau 4 tuần triển khai nghiêm túc và bài bản, nhóm đã hoàn thành **100% mục tiêu đề tài** đặt ra:

1. **Về mặt kỹ thuật:** Xây dựng thành công hệ thống xử lý ảnh tự động phân tán trên nền tảng AWS, kết hợp nhuần nhuyễn giữa máy chủ Web Gateway EC2 (Gunicorn, systemd tự phục hồi) và cụm dịch vụ Serverless hướng sự kiện (S3, Lambda, DynamoDB, CloudWatch).
2. **Về mặt bảo mật:** Ứng dụng xuất sắc cơ chế IAM Role `LabInstanceProfile` (IMDSv2) để loại bỏ hoàn toàn việc lưu trữ cứng access key; bảo vệ kho ảnh S3 ở chế độ Private tuyệt đối và cấp quyền xem tạm thời qua Presigned URL thời hạn 300 giây.
3. **Về mặt tối ưu hóa:** Thực hiện trọn vẹn 2 yêu cầu nâng cao của GVHD: tách Pillow thành Lambda Layer giúp gói mã nguồn deploy đạt kích thước siêu nhẹ **3.7 kB** (mở xem trực tiếp trên AWS Console); thiết lập S3 Lifecycle Rule tự động dọn thumbnail sau 7 ngày giúp tối ưu hóa chi phí lưu trữ đám mây.
4. **Về mặt kinh tế:** Phân tích hạch toán chi phí minh bạch, chứng minh kiến trúc Serverless giúp tiết kiệm **hơn 85% chi phí vận hành** so với việc thuê máy chủ truyền thống (Monolith EC2).
5. **Về mặt tài liệu và minh chứng:** Toàn bộ mã nguồn, cấu hình, video demo Full HD và toàn bộ 80 hình ảnh minh chứng thực tế qua 4 tuần được tổ chức khoa học, minh bạch, sẵn sàng cho buổi nghiệm thu và đánh giá đồ án cuối kỳ.

