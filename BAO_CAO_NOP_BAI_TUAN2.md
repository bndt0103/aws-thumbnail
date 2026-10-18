# BÁO CÁO TIẾN ĐỘ TUẦN 2

**Đề tài:** Xử lý ảnh tự động: tạo thumbnail khi upload lên Amazon S3.

**Giảng viên hướng dẫn:** TS. Huỳnh Xuân Phụng.

**Nhóm thực hiện:** Bùi Nguyễn Duy Trung — MSSV 24110363; Đỗ Anh Tuấn — MSSV 24110369.

**Ngày đối chiếu kết quả:** 18/10/2026.

**Kho mã nguồn:** [bndt0103/aws-thumbnail](https://github.com/bndt0103/aws-thumbnail).

## 1. Mục tiêu và phạm vi tuần 2

Tuần 2 tập trung tích hợp các thành phần đã chuẩn bị trong tuần 1 thành luồng xử lý ảnh hoạt động trên AWS: S3 nhận ảnh gốc, Lambda kết hợp Pillow tạo thumbnail và watermark, bucket S3 riêng lưu kết quả, DynamoDB lưu metadata và CloudWatch ghi log. Gallery Flask chạy cục bộ để tải ảnh lên và hiển thị kết quả từ AWS.

Mã xử lý ảnh, worker Lambda, gallery và bộ kiểm thử được kế thừa từ tuần 1. Công việc tuần 2 tập trung vào cấu hình tài nguyên, triển khai, kiểm thử tích hợp và đối chiếu kết quả thực tế.

## 2. Công việc và kết quả triển khai

| Thành phần | Cấu hình và kết quả |
|---|---|
| AWS Region | `us-east-1` — N. Virginia. |
| Bucket input | `cloudphoto-input-103308504802`; trigger theo dõi tiền tố `uploads/` với sự kiện `s3:ObjectCreated:*`. |
| Lambda | `cloud-photo-processor`; Python 3.12; x86_64; handler `lambda_function.lambda_handler`; execution role `LabRole`; Pillow Layer phiên bản 1. |
| Tài nguyên Lambda | Bộ nhớ 1024 MB; timeout 60 giây; dung lượng lưu trữ tạm 512 MB. |
| Bucket output | `cloudphoto-output-103308504802`; thumbnail lưu trong `thumbnails/<image_id>/`. |
| DynamoDB | Bảng `cloud-photo-metadata`, khóa `image_id` kiểu String; lưu thông tin ảnh gốc, các phiên bản và trạng thái xử lý. |
| Xử lý ảnh | Cạnh dài tối đa 150, 400 và 1000 pixel; giữ tỷ lệ; không phóng lớn ảnh nhỏ; thêm watermark `CLOUD PHOTO`. |
| CloudWatch | Ghi nhận `COMPLETE`, `REPORT` và `DUPLICATE_SKIPPED`; thời gian lưu log 7 ngày. |
| Gallery | Flask tại `127.0.0.1:5000` kết nối S3/DynamoDB; hỗ trợ đăng nhập, upload, hiển thị trạng thái và xem ba phiên bản ảnh. |

Trong lần thử S3 ban đầu, ảnh `landscape.jpg` có kích thước 1600 × 1000 pixel được xử lý thành 150 × 94, 400 × 250 và 1000 × 625 pixel. Ảnh đầu ra có watermark và metadata trong DynamoDB chuyển sang `COMPLETE`.

Log ứng dụng của lần thử này ghi thời gian xử lý 529 ms. Báo cáo Lambda ghi Duration 579,67 ms và bộ nhớ sử dụng cao nhất 152 MB trên cấu hình 1024 MB. Đây là số liệu của một lần chạy, chưa đủ để đánh giá hiệu năng khi có nhiều yêu cầu đồng thời.

Khi gửi lại cùng sự kiện đã hoàn tất, hệ thống ghi `DUPLICATE_SKIPPED`; thời gian sửa các object đầu ra không thay đổi. Bucket output không có event notification và EventBridge đang tắt. Nhóm đối chiếu cấu hình này với log sau khi upload vào output để kiểm tra việc tách nguồn kích hoạt.

## 3. Tổng hợp kiểm thử

| Mã | Tình huống | Kết quả quan sát | Đánh giá |
|---|---|---|---|
| T01 | Ảnh ngang 1600 × 1000 | Tạo ảnh 150 × 94, 400 × 250 và 1000 × 625; có watermark. | Đạt |
| T02 | Ảnh dọc 900 × 1500 | Tạo ảnh 90 × 150, 240 × 400 và 600 × 1000; giữ tỷ lệ. | Đạt |
| T03 | Ảnh vuông 1000 × 1000 | Tạo ảnh 150 × 150, 400 × 400 và 1000 × 1000. | Đạt |
| T04 | PNG trong suốt 800 × 600 | Chuyển nền trắng; tạo ảnh 150 × 113, 400 × 300 và 800 × 600. | Đạt |
| T05 | Ảnh nhỏ 80 × 60 | Cả ba phiên bản giữ nguyên 80 × 60, không phóng lớn. | Đạt |
| T06 | Ảnh hỏng `broken.jpg` | Hiển thị trạng thái ảnh không hợp lệ và lý do từ chối. | Đạt |
| T07 | Tệp 10.517.445 byte, vượt 10 MiB | Giao diện từ chối; gửi trực tiếp tới API với CSRF hợp lệ nhận HTTP 400. | Đạt |
| T08 | Chạy lại cùng JSON event | Lần đầu `COMPLETE`, lần sau `DUPLICATE_SKIPPED`; không ghi lại ảnh đầu ra. | Đạt |
| T09 | Upload vào bucket output | Output không có notification, EventBridge tắt; log được quan sát phù hợp với cấu hình tách nguồn. | Đạt |
| T10 | Hai upload cùng tên `landscape.jpg` | Có `source_key` và `image_id` khác nhau; cả hai hoàn tất xử lý. | Đạt |
| T11 | Gọi `GET /api/photos` sau đăng xuất | Trả HTTP 401 UNAUTHORIZED. | Đạt |
| T12 | Gọi `POST /api/upload` thiếu CSRF token | Trả HTTP 403 FORBIDDEN. | Đạt |

Nhóm đã đối chiếu 12 tình huống trên với ảnh chụp và log thực tế. Kết quả được giới hạn theo đầu vào, cấu hình và thời điểm đã kiểm tra.

Bộ kiểm thử cục bộ đạt 19/19 ca, sử dụng dịch vụ AWS giả lập. Kết quả này được ghi riêng với kiểm thử tích hợp. Phép thử dung lượng thực tế trả HTTP 400; nhánh HTTP 413 cho request vượt giới hạn toàn bộ chưa được chạy để kiểm chứng.

## 4. Phân công thực hiện

| Thành viên | Tài khoản GitHub | Phạm vi phụ trách |
|---|---|---|
| Bùi Nguyễn Duy Trung — 24110363 | [bndt0103](https://github.com/bndt0103) | Triển khai Lambda và Pillow Layer; cấu hình trigger S3; đối chiếu S3, DynamoDB, CloudWatch; kiểm tra sự kiện trùng và nguồn output. |
| Đỗ Anh Tuấn — 24110369 | [DoAnhTuan-24110369](https://github.com/DoAnhTuan-24110369) | Kết nối gallery với AWS; kiểm thử upload, xử lý ảnh và truy cập API; tổng hợp kết quả và báo cáo. |

Nhóm phối hợp đối chiếu kết quả giữa giao diện, dữ liệu S3/DynamoDB và log CloudWatch. Ảnh và bảng kiểm thử ghi nguồn nhóm khi chưa xác nhận riêng người thao tác từng tình huống.

## 5. Báo cáo đính kèm

[Báo cáo Word tuần 2 — BaoCaoTuan2_24110363_24110369.docx](https://github.com/bndt0103/aws-thumbnail/blob/main/Report/BaoCaoTuan2_24110363_24110369.docx).

Báo cáo gồm 25 trang, trình bày kiến trúc, cấu hình triển khai, kết quả kiểm thử và 29 ảnh minh chứng được chèn trực tiếp trong các phần tương ứng.

## 6. Khai báo hỗ trợ AI

**Công cụ:** ChatGPT/Codex. Phiên bản model: 6.1 Sol

**Prompt đã dùng — tóm lược:** Tiếp tục tích hợp hệ thống từ tuần 1; hướng dẫn cấu hình S3–Lambda–DynamoDB và gallery; đề xuất cách kiểm thử, giải thích log và kết quả; tổ chức ảnh, biên tập báo cáo và tổng hợp nội dung nộp bài.

**Nội dung AI hỗ trợ:** Rà soát cấu hình và mã nguồn nền, đề xuất lệnh khởi chạy và thử API, giải thích lỗi, phân loại ảnh và biên tập Word/Markdown. AI cũng hỗ trợ thao tác Git theo yêu cầu và ủy quyền của nhóm.

**Phần sinh viên thực hiện và kiểm chứng:** Nhóm trực tiếp cấu hình trong Learner Lab, chạy gallery, upload ảnh và thực hiện các phép thử; đối chiếu kích thước, watermark, trạng thái xử lý, khóa S3 và số liệu log. Các ảnh là ảnh chụp kết quả thực tế.

**Phần mã nguồn và kiểm thử đã hoàn thiện:** Các commit dưới đây ghi nhận phiên bản nhóm đã hoàn thiện có AI hỗ trợ ở tuần 1 và sử dụng để triển khai trong tuần 2. Tuần 2 không phát sinh sửa đổi mã worker hoặc Flask; các link được dẫn để đối chiếu nội dung, không tính là thay đổi mã nguồn mới của tuần 2.

| Phần phân công | Nội dung đã hoàn thiện và được kiểm chứng | Commit đối chiếu |
|---|---|---|
| Trung — xử lý ảnh Pillow | Xử lý JPEG/PNG, giữ tỷ lệ, giới hạn kích thước, thêm watermark, chuyển nền trắng cho ảnh trong suốt và loại EXIF; đối chiếu bằng thumbnail thực tế. | [1c41d75](https://github.com/bndt0103/aws-thumbnail/commit/1c41d751d490f3493a5ba7d2e87df52ba40966ca) |
| Trung — Lambda worker | Nhận sự kiện S3, tạo ảnh đầu ra, ghi metadata DynamoDB, xử lý sự kiện trùng và ghi log; đối chiếu qua luồng tích hợp AWS. | [e50cb0c](https://github.com/bndt0103/aws-thumbnail/commit/e50cb0c19bfa43d8dafe2d9b67bbe24e82343dc9) |
| Tuấn — gallery Flask | Đăng nhập, CSRF, khóa upload riêng, giới hạn dung lượng và hiển thị ảnh qua URL ký sẵn; đối chiếu bằng các phép thử web/API. | [9b0aca9](https://github.com/bndt0103/aws-thumbnail/commit/9b0aca9be588f0f496a228b456741a8b9bfc7c80) |
| Tuấn — kiểm thử ảnh | Hoàn thiện 10 ca kiểm thử xử lý ảnh và điều kiện đầu vào. | [30838ce](https://github.com/bndt0103/aws-thumbnail/commit/30838ce3994c9d3e83d65fd40cef4bd047ee7b17) |
| Tuấn — kiểm thử worker và web | Hoàn thiện 5 ca worker và 4 ca Flask bằng AWS giả lập; ghi nhận riêng với kết quả tích hợp thực tế. | [f3e62ba](https://github.com/bndt0103/aws-thumbnail/commit/f3e62ba4a663a9d6cdd46d500ce0a2ab2fcf6ec9), [c4fa1ad](https://github.com/bndt0103/aws-thumbnail/commit/c4fa1adae7f7a51c4a08bbf24bca7e905060d0da) |

Phần mã nguồn có AI hỗ trợ; các link commit dùng để đối chiếu phiên bản hoàn thiện và phần việc được phân công, không khẳng định toàn bộ mã được sinh viên viết độc lập.

## 7. Đánh giá và hướng tiếp theo

Nhóm hoàn thành mốc tích hợp tuần 2 trong phạm vi đã kiểm tra. Luồng S3–Lambda–S3/DynamoDB hoạt động, gallery cục bộ tải và hiển thị kết quả, các tình huống đầu vào và kiểm soát truy cập cho phản hồi phù hợp.

Số liệu thời gian và bộ nhớ hiện lấy từ các lần chạy đơn lẻ. Nhóm chưa thử tải lớn hoặc kiểm chứng đầy đủ lỗi mạng, timeout, thiếu bộ nhớ và retry phục hồi trên AWS. Gallery chưa triển khai trên EC2.

Tuần 3 dự kiến triển khai gallery lên EC2, kiểm tra quyền truy cập S3/DynamoDB, liên kết ảnh riêng tư, thời hạn URL và khả năng hoạt động sau khi khởi động lại ứng dụng.
