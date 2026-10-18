# BÁO CÁO TIẾN ĐỘ TUẦN 2

**Đề tài:** Xử lý ảnh tự động: tạo thumbnail khi upload lên Amazon S3.

**Giảng viên hướng dẫn:** TS. Huỳnh Xuân Phụng.

**Nhóm thực hiện:** Bùi Nguyễn Duy Trung — MSSV 24110363; Đỗ Anh Tuấn — MSSV 24110369.

**Ngày đối chiếu kết quả:** 18/10/2026.

**Kho mã nguồn:** [bndt0103/aws-thumbnail](https://github.com/bndt0103/aws-thumbnail).

## 1. Mục tiêu và phạm vi tuần 2

Tuần 2 tập trung tích hợp các thành phần đã chuẩn bị trong tuần 1 thành luồng xử lý ảnh hoạt động trên AWS: S3 nhận ảnh gốc, Lambda kết hợp Pillow tạo thumbnail và watermark, S3 lưu ảnh đầu ra, DynamoDB lưu metadata, CloudWatch ghi log. Gallery Flask chạy cục bộ để tải ảnh lên và hiển thị kết quả thực tế.

Mã worker, Flask và bộ test được kế thừa từ tuần 1. Các commit tuần 2 ghi nhận cấu hình, minh chứng vận hành, kết quả kiểm thử và báo cáo; việc tạo tài nguyên được đối chiếu bằng ảnh chụp, không suy ra từ ngày commit.

## 2. Công việc và kết quả triển khai

| Thành phần | Cấu hình hoặc kết quả đã đối chiếu |
|---|---|
| AWS Region | us-east-1 — N. Virginia. |
| Bucket input | cloudphoto-input-103308504802; trigger theo dõi uploads/ với s3:ObjectCreated:*. |
| Lambda | cloud-photo-processor; Python 3.12; x86_64; handler lambda_function.lambda_handler; LabRole; Pillow Layer v1. |
| Tài nguyên Lambda | Memory 1024 MB; timeout 60 giây; ephemeral storage 512 MB. |
| Bucket output | cloudphoto-output-103308504802; ba thumbnail lưu trong thumbnails/<image_id>/. |
| DynamoDB | cloud-photo-metadata; khóa image_id kiểu String; lưu thông tin ảnh gốc, variants và trạng thái COMPLETE. |
| Watermark | CLOUD PHOTO; kích thước cạnh dài tối đa 150, 400 và 1000 pixel; giữ tỷ lệ, không phóng lớn ảnh nhỏ. |
| CloudWatch | Log COMPLETE, REPORT và DUPLICATE_SKIPPED; retention 1 tuần. |
| Gallery | Flask tại 127.0.0.1:5000 kết nối S3/DynamoDB; có đăng nhập, upload, trạng thái và liên kết ba phiên bản. |

Trong lần thử S3 ban đầu, ảnh landscape.jpg 1600 × 1000 được xử lý thành 150 × 94, 400 × 250 và 1000 × 625 pixel. Log ứng dụng ghi processing_ms = 529; báo cáo Lambda ghi Duration 579,67 ms và Max Memory Used 152 MB trên cấu hình 1024 MB. Đây là số liệu của một lần chạy, chưa đại diện cho tải lớn hoặc toàn bộ phiên làm việc.

Nhóm đã thử gửi lại cùng sự kiện và quan sát DUPLICATE_SKIPPED. Thời gian sửa các object đầu ra không thay đổi theo lần xử lý trùng. Bucket output không có event notification và EventBridge đang tắt; kết luận tránh tự kích hoạt được giới hạn theo cấu hình và log đã quan sát.

## 3. Tổng hợp kiểm thử

| Mã | Tình huống | Kết quả quan sát | Đánh giá |
|---|---|---|---|
| T01 | Ảnh ngang 1600 × 1000 | 150 × 94; 400 × 250; 1000 × 625; có watermark. | Đạt |
| T02 | Ảnh dọc 900 × 1500 | 90 × 150; 240 × 400; 600 × 1000; giữ tỷ lệ. | Đạt |
| T03 | Ảnh vuông 1000 × 1000 | 150 × 150; 400 × 400; 1000 × 1000. | Đạt |
| T04 | PNG trong suốt 800 × 600 | Nền trắng; 150 × 113; 400 × 300; bản lớn giữ 800 × 600. | Đạt |
| T05 | Ảnh nhỏ 80 × 60 | Ba phiên bản đều giữ 80 × 60, không phóng lớn. | Đạt |
| T06 | Ảnh hỏng broken.jpg | Hiển thị ảnh không hợp lệ và lý do từ chối. | Đạt |
| T07 | Tệp 10.517.445 byte | Giao diện từ chối; API với CSRF hợp lệ trả HTTP 400. | Đạt |
| T08 | Chạy lại cùng JSON event | COMPLETE ở lần đầu; DUPLICATE_SKIPPED ở lần sau; object không ghi lại. | Đạt |
| T09 | Upload vào bucket output | Output không có notification, EventBridge tắt; log phù hợp trong phạm vi quan sát. | Đạt |
| T10 | Hai upload cùng tên landscape.jpg | Hai source_key và image_id khác nhau; cả hai COMPLETE. | Đạt |
| T11 | GET /api/photos sau đăng xuất | HTTP 401 UNAUTHORIZED. | Đạt |
| T12 | POST /api/upload thiếu CSRF | HTTP 403 FORBIDDEN. | Đạt |

Cả 12 tình huống vận hành được đối chiếu với ảnh và log thực tế. Bộ pytest cục bộ ghi nhận 19/19 ca đạt, dùng dịch vụ AWS giả lập; kết quả này được ghi riêng và không thay cho kiểm thử tích hợp. Phép thử dung lượng thực tế trả HTTP 400; nhánh HTTP 413 của giới hạn toàn bộ request chưa được chạy để kiểm chứng.

[Bảng kết quả kiểm thử chi tiết](https://github.com/bndt0103/aws-thumbnail/blob/f4a4ad9cbb1af3ba38ab208463e53850af52864a/progress/week-2/test-results.csv) · [Danh mục ảnh minh chứng](https://github.com/bndt0103/aws-thumbnail/blob/f4a4ad9cbb1af3ba38ab208463e53850af52864a/evidence/tuan-2/DANH_MUC_MINH_CHUNG.csv).

## 4. Phân công và các mốc commit

| Thành viên | Tài khoản GitHub | Phạm vi phân công | Mốc commit đối chiếu |
|---|---|---|---|
| Bùi Nguyễn Duy Trung — 24110363 | [bndt0103](https://github.com/bndt0103) | Cấu hình Lambda/Layer/trigger, dữ liệu S3/DynamoDB, CloudWatch, duplicate và kiểm tra nguồn output. | C01–C04: 4 mốc. |
| Đỗ Anh Tuấn — 24110369 | [DoAnhTuan-24110369](https://github.com/DoAnhTuan-24110369) | Gallery, kiểm thử web/API, danh mục ảnh và tổng hợp báo cáo. | C05–C08: 4 mốc. |

Tám mốc dưới đây là các commit theo phân công tuần 2. Phần chốt hồ sơ sau khi tổng hợp link được theo dõi riêng trong lịch sử nhánh main.

### Bùi Nguyễn Duy Trung

**C01 — [a8f99ec](https://github.com/bndt0103/aws-thumbnail/commit/a8f99ecd6aea610eb882544076edfc074b33cd99): bổ sung hướng dẫn, phân công commit và quy tắc lưu minh chứng.**

- [.gitignore](https://github.com/bndt0103/aws-thumbnail/blob/a8f99ecd6aea610eb882544076edfc074b33cd99/.gitignore)
- [HUONG_DAN_TUAN_2.md](https://github.com/bndt0103/aws-thumbnail/blob/a8f99ecd6aea610eb882544076edfc074b33cd99/HUONG_DAN_TUAN_2.md)
- [PHAN_CONG_COMMIT_TUAN2.md](https://github.com/bndt0103/aws-thumbnail/blob/a8f99ecd6aea610eb882544076edfc074b33cd99/PHAN_CONG_COMMIT_TUAN2.md)

**C02 — [d792ca0](https://github.com/bndt0103/aws-thumbnail/commit/d792ca0e5762d76eef01c299ac0b6d36bcc02f4a): ghi nhận cấu hình Lambda, Pillow Layer và trigger S3.**

- [evidence/tuan-2/trung/E07_lambda-execution-role.png](https://github.com/bndt0103/aws-thumbnail/blob/d792ca0e5762d76eef01c299ac0b6d36bcc02f4a/evidence/tuan-2/trung/E07_lambda-execution-role.png)
- [evidence/tuan-2/trung/E08a_lambda-runtime-layer.png](https://github.com/bndt0103/aws-thumbnail/blob/d792ca0e5762d76eef01c299ac0b6d36bcc02f4a/evidence/tuan-2/trung/E08a_lambda-runtime-layer.png)
- [evidence/tuan-2/trung/E08b_lambda-general-configuration.png](https://github.com/bndt0103/aws-thumbnail/blob/d792ca0e5762d76eef01c299ac0b6d36bcc02f4a/evidence/tuan-2/trung/E08b_lambda-general-configuration.png)
- [evidence/tuan-2/trung/E08c_lambda-environment-variables.png](https://github.com/bndt0103/aws-thumbnail/blob/d792ca0e5762d76eef01c299ac0b6d36bcc02f4a/evidence/tuan-2/trung/E08c_lambda-environment-variables.png)
- [evidence/tuan-2/trung/E08d_lambda-code-uploaded.png](https://github.com/bndt0103/aws-thumbnail/blob/d792ca0e5762d76eef01c299ac0b6d36bcc02f4a/evidence/tuan-2/trung/E08d_lambda-code-uploaded.png)
- [evidence/tuan-2/trung/E09_lambda-s3-trigger.png](https://github.com/bndt0103/aws-thumbnail/blob/d792ca0e5762d76eef01c299ac0b6d36bcc02f4a/evidence/tuan-2/trung/E09_lambda-s3-trigger.png)

**C03 — [8f60594](https://github.com/bndt0103/aws-thumbnail/commit/8f6059487de15f78b8e0b503eea5412abba6f3e6): bổ sung kết quả S3, metadata DynamoDB và log CloudWatch.**

- [evidence/tuan-2/trung/E10_s3-input-landscape.png](https://github.com/bndt0103/aws-thumbnail/blob/8f6059487de15f78b8e0b503eea5412abba6f3e6/evidence/tuan-2/trung/E10_s3-input-landscape.png)
- [evidence/tuan-2/trung/E11_s3-output-three-thumbnails.png](https://github.com/bndt0103/aws-thumbnail/blob/8f6059487de15f78b8e0b503eea5412abba6f3e6/evidence/tuan-2/trung/E11_s3-output-three-thumbnails.png)
- [evidence/tuan-2/trung/E12_output-thumbnail-1000x625.jpg](https://github.com/bndt0103/aws-thumbnail/blob/8f6059487de15f78b8e0b503eea5412abba6f3e6/evidence/tuan-2/trung/E12_output-thumbnail-1000x625.jpg)
- [evidence/tuan-2/trung/E12_thumbnail-watermark-dimensions.png](https://github.com/bndt0103/aws-thumbnail/blob/8f6059487de15f78b8e0b503eea5412abba6f3e6/evidence/tuan-2/trung/E12_thumbnail-watermark-dimensions.png)
- [evidence/tuan-2/trung/E13a_dynamodb-complete-original.png](https://github.com/bndt0103/aws-thumbnail/blob/8f6059487de15f78b8e0b503eea5412abba6f3e6/evidence/tuan-2/trung/E13a_dynamodb-complete-original.png)
- [evidence/tuan-2/trung/E13c_dynamodb-variant-150.png](https://github.com/bndt0103/aws-thumbnail/blob/8f6059487de15f78b8e0b503eea5412abba6f3e6/evidence/tuan-2/trung/E13c_dynamodb-variant-150.png)
- [evidence/tuan-2/trung/E13d_dynamodb-variants-400-1000.png](https://github.com/bndt0103/aws-thumbnail/blob/8f6059487de15f78b8e0b503eea5412abba6f3e6/evidence/tuan-2/trung/E13d_dynamodb-variants-400-1000.png)
- [evidence/tuan-2/trung/E14b_cloudwatch-report-details.png](https://github.com/bndt0103/aws-thumbnail/blob/8f6059487de15f78b8e0b503eea5412abba6f3e6/evidence/tuan-2/trung/E14b_cloudwatch-report-details.png)
- [evidence/tuan-2/trung/E14c_cloudwatch-retention-7-days.png](https://github.com/bndt0103/aws-thumbnail/blob/8f6059487de15f78b8e0b503eea5412abba6f3e6/evidence/tuan-2/trung/E14c_cloudwatch-retention-7-days.png)
- [evidence/tuan-2/trung/E15_lambda-monitor-metrics.png](https://github.com/bndt0103/aws-thumbnail/blob/8f6059487de15f78b8e0b503eea5412abba6f3e6/evidence/tuan-2/trung/E15_lambda-monitor-metrics.png)

**C04 — [39678dc](https://github.com/bndt0103/aws-thumbnail/commit/39678dc6bdc112baa7a5682adfd09e63a9c87644): ghi nhận kiểm tra duplicate và notification của bucket output.**

- [evidence/tuan-2/trung/E19a_lambda-duplicate-response.png](https://github.com/bndt0103/aws-thumbnail/blob/39678dc6bdc112baa7a5682adfd09e63a9c87644/evidence/tuan-2/trung/E19a_lambda-duplicate-response.png)
- [evidence/tuan-2/trung/E19b_cloudwatch-complete-duplicate.png](https://github.com/bndt0103/aws-thumbnail/blob/39678dc6bdc112baa7a5682adfd09e63a9c87644/evidence/tuan-2/trung/E19b_cloudwatch-complete-duplicate.png)
- [evidence/tuan-2/trung/E19c_s3-output-after-duplicate.png](https://github.com/bndt0103/aws-thumbnail/blob/39678dc6bdc112baa7a5682adfd09e63a9c87644/evidence/tuan-2/trung/E19c_s3-output-after-duplicate.png)
- [evidence/tuan-2/trung/T09a_output-loop-check-upload.png](https://github.com/bndt0103/aws-thumbnail/blob/39678dc6bdc112baa7a5682adfd09e63a9c87644/evidence/tuan-2/trung/T09a_output-loop-check-upload.png)
- [evidence/tuan-2/trung/T09b_cloudwatch-after-output-upload.png](https://github.com/bndt0103/aws-thumbnail/blob/39678dc6bdc112baa7a5682adfd09e63a9c87644/evidence/tuan-2/trung/T09b_cloudwatch-after-output-upload.png)
- [evidence/tuan-2/trung/T09c_output-no-event-notifications.png](https://github.com/bndt0103/aws-thumbnail/blob/39678dc6bdc112baa7a5682adfd09e63a9c87644/evidence/tuan-2/trung/T09c_output-no-event-notifications.png)

### Đỗ Anh Tuấn

**C05 — [b0d72a2](https://github.com/bndt0103/aws-thumbnail/commit/b0d72a2e01e68c66671a12b02a6397dc7117c80a): bổ sung minh chứng gallery xử lý ảnh hợp lệ.**

- [evidence/tuan-2/tuan/T02_gallery-portrait-complete.png](https://github.com/bndt0103/aws-thumbnail/blob/b0d72a2e01e68c66671a12b02a6397dc7117c80a/evidence/tuan-2/tuan/T02_gallery-portrait-complete.png)
- [evidence/tuan-2/tuan/T03_gallery-square-complete.png](https://github.com/bndt0103/aws-thumbnail/blob/b0d72a2e01e68c66671a12b02a6397dc7117c80a/evidence/tuan-2/tuan/T03_gallery-square-complete.png)
- [evidence/tuan-2/tuan/T04_gallery-transparent-white-background.png](https://github.com/bndt0103/aws-thumbnail/blob/b0d72a2e01e68c66671a12b02a6397dc7117c80a/evidence/tuan-2/tuan/T04_gallery-transparent-white-background.png)
- [evidence/tuan-2/tuan/T05_gallery-small-no-upscale.png](https://github.com/bndt0103/aws-thumbnail/blob/b0d72a2e01e68c66671a12b02a6397dc7117c80a/evidence/tuan-2/tuan/T05_gallery-small-no-upscale.png)
- [evidence/tuan-2/tuan/W2-L01_gallery-landscape-complete.png](https://github.com/bndt0103/aws-thumbnail/blob/b0d72a2e01e68c66671a12b02a6397dc7117c80a/evidence/tuan-2/tuan/W2-L01_gallery-landscape-complete.png)

**C06 — [9795a3b](https://github.com/bndt0103/aws-thumbnail/commit/9795a3b5872e3b832846bc752712c307425e2ce9): bổ sung kiểm tra ảnh lỗi, giới hạn upload, tên trùng và xác thực.**

- [evidence/tuan-2/tuan/T06_gallery-broken-rejected.png](https://github.com/bndt0103/aws-thumbnail/blob/9795a3b5872e3b832846bc752712c307425e2ce9/evidence/tuan-2/tuan/T06_gallery-broken-rejected.png)
- [evidence/tuan-2/tuan/T07a_gallery-oversize-rejected.png](https://github.com/bndt0103/aws-thumbnail/blob/9795a3b5872e3b832846bc752712c307425e2ce9/evidence/tuan-2/tuan/T07a_gallery-oversize-rejected.png)
- [evidence/tuan-2/tuan/T07b_api-oversize-http-400.png](https://github.com/bndt0103/aws-thumbnail/blob/9795a3b5872e3b832846bc752712c307425e2ce9/evidence/tuan-2/tuan/T07b_api-oversize-http-400.png)
- [evidence/tuan-2/tuan/T10a_gallery-second-landscape-upload.png](https://github.com/bndt0103/aws-thumbnail/blob/9795a3b5872e3b832846bc752712c307425e2ce9/evidence/tuan-2/tuan/T10a_gallery-second-landscape-upload.png)
- [evidence/tuan-2/tuan/T10b_api-landscape-second-key.png](https://github.com/bndt0103/aws-thumbnail/blob/9795a3b5872e3b832846bc752712c307425e2ce9/evidence/tuan-2/tuan/T10b_api-landscape-second-key.png)
- [evidence/tuan-2/tuan/T10c_api-landscape-first-key.png](https://github.com/bndt0103/aws-thumbnail/blob/9795a3b5872e3b832846bc752712c307425e2ce9/evidence/tuan-2/tuan/T10c_api-landscape-first-key.png)
- [evidence/tuan-2/tuan/T11_api-photos-unauthorized.png](https://github.com/bndt0103/aws-thumbnail/blob/9795a3b5872e3b832846bc752712c307425e2ce9/evidence/tuan-2/tuan/T11_api-photos-unauthorized.png)
- [evidence/tuan-2/tuan/T12_upload-missing-csrf-403.png](https://github.com/bndt0103/aws-thumbnail/blob/9795a3b5872e3b832846bc752712c307425e2ce9/evidence/tuan-2/tuan/T12_upload-missing-csrf-403.png)

**C07 — [f4a4ad9](https://github.com/bndt0103/aws-thumbnail/commit/f4a4ad9cbb1af3ba38ab208463e53850af52864a): đối chiếu danh mục minh chứng và kết quả 12 tình huống kiểm thử.**

- [evidence/tuan-2/DANH_MUC_MINH_CHUNG.csv](https://github.com/bndt0103/aws-thumbnail/blob/f4a4ad9cbb1af3ba38ab208463e53850af52864a/evidence/tuan-2/DANH_MUC_MINH_CHUNG.csv)
- [evidence/tuan-2/DOI_CHIEU_ANH.json](https://github.com/bndt0103/aws-thumbnail/blob/f4a4ad9cbb1af3ba38ab208463e53850af52864a/evidence/tuan-2/DOI_CHIEU_ANH.json)
- [evidence/tuan-2/README.md](https://github.com/bndt0103/aws-thumbnail/blob/f4a4ad9cbb1af3ba38ab208463e53850af52864a/evidence/tuan-2/README.md)
- [progress/week-2/test-results.csv](https://github.com/bndt0103/aws-thumbnail/blob/f4a4ad9cbb1af3ba38ab208463e53850af52864a/progress/week-2/test-results.csv)

**C08 — [92d81a4](https://github.com/bndt0103/aws-thumbnail/commit/92d81a4a6aeb898cabb810a8e23d3b87e5372ac0): hoàn thiện báo cáo Word, khai báo AI và dữ liệu tổng hợp.**

- [BAO_CAO_NOP_BAI_TUAN2.md](https://github.com/bndt0103/aws-thumbnail/blob/92d81a4a6aeb898cabb810a8e23d3b87e5372ac0/BAO_CAO_NOP_BAI_TUAN2.md)
- [KHAI_BAO_AI_TUAN2.md](https://github.com/bndt0103/aws-thumbnail/blob/92d81a4a6aeb898cabb810a8e23d3b87e5372ac0/KHAI_BAO_AI_TUAN2.md)
- [Report/BaoCaoTuan2_24110363_24110369.docx](https://github.com/bndt0103/aws-thumbnail/blob/92d81a4a6aeb898cabb810a8e23d3b87e5372ac0/Report/BaoCaoTuan2_24110363_24110369.docx)
- [progress/week-2/report-content.json](https://github.com/bndt0103/aws-thumbnail/blob/92d81a4a6aeb898cabb810a8e23d3b87e5372ac0/progress/week-2/report-content.json)
- [progress/week-2/report-status.json](https://github.com/bndt0103/aws-thumbnail/blob/92d81a4a6aeb898cabb810a8e23d3b87e5372ac0/progress/week-2/report-status.json)
- [requirements-report.txt](https://github.com/bndt0103/aws-thumbnail/blob/92d81a4a6aeb898cabb810a8e23d3b87e5372ac0/requirements-report.txt)
- [scripts/build_week2_report.py](https://github.com/bndt0103/aws-thumbnail/blob/92d81a4a6aeb898cabb810a8e23d3b87e5372ac0/scripts/build_week2_report.py)

GitHub đã gắn các commit phần Tuấn với tài khoản DoAnhTuan-24110369 qua email trường 24110369@student.hcmute.edu.vn. Việc commit/push được thực hiện hộ từ môi trường Git của Trung theo ủy quyền, nên trường Committer ghi bndt0103. Thông tin này phân biệt người đứng tên tác giả với người thao tác Git. Các commit chưa được ký số; metadata email không phải bằng chứng Tuấn trực tiếp thao tác push.

[Metadata đối chiếu GitHub](https://github.com/bndt0103/aws-thumbnail/blob/main/progress/week-2/commit-verification.json) · [Lịch sử commit trên main](https://github.com/bndt0103/aws-thumbnail/commits/main).

## 5. Báo cáo và minh chứng đính kèm

- [Báo cáo Word tuần 2](https://github.com/bndt0103/aws-thumbnail/blob/main/Report/BaoCaoTuan2_24110363_24110369.docx), có kiến trúc, cấu hình, kết quả và 29 ảnh minh chứng chèn trong từng phần.
- [Mô tả bộ minh chứng](https://github.com/bndt0103/aws-thumbnail/blob/f4a4ad9cbb1af3ba38ab208463e53850af52864a/evidence/tuan-2/README.md).
- [Đối chiếu ảnh gốc, tên mới và mã SHA-256](https://github.com/bndt0103/aws-thumbnail/blob/f4a4ad9cbb1af3ba38ab208463e53850af52864a/evidence/tuan-2/DOI_CHIEU_ANH.json).

## 6. Khai báo hỗ trợ AI

Nhóm sử dụng ChatGPT/Codex để hỗ trợ hướng dẫn cấu hình, đề xuất lệnh kiểm thử, giải thích log, tổ chức ảnh, biên tập Word/Markdown và thực hiện thao tác Git theo ủy quyền. Phiên bản model cụ thể không được ghi nhận trong hồ sơ tuần 2.

**Prompt đã dùng — tóm lược:** Tiếp tục tích hợp hệ thống từ tuần 1; kiểm chứng luồng AWS và gallery bằng ảnh/log thật; viết báo cáo hoàn chỉnh; phân công commit từng file, commit/push bằng tiếng Việt và tổng hợp link thật làm minh chứng.

**Phần nhóm thực hiện và kiểm chứng:** trực tiếp cấu hình trong Learner Lab; chạy gallery và các phép thử; thu thập ảnh; đối chiếu kích thước, trạng thái, khóa S3 và số liệu log. Phần thao tác vận hành được ghi nguồn nhóm khi chưa xác nhận riêng người thực hiện. Các ảnh là ảnh chụp kết quả thực tế.

| Phần được đối chiếu | Commit và file minh chứng |
|---|---|
| Cấu hình Lambda và nguồn S3 | [d792ca0](https://github.com/bndt0103/aws-thumbnail/commit/d792ca0e5762d76eef01c299ac0b6d36bcc02f4a) · [Runtime và Layer](https://github.com/bndt0103/aws-thumbnail/blob/d792ca0e5762d76eef01c299ac0b6d36bcc02f4a/evidence/tuan-2/trung/E08a_lambda-runtime-layer.png) · [Trigger S3](https://github.com/bndt0103/aws-thumbnail/blob/d792ca0e5762d76eef01c299ac0b6d36bcc02f4a/evidence/tuan-2/trung/E09_lambda-s3-trigger.png) |
| Kiểm chứng đầu ra và metadata | [8f60594](https://github.com/bndt0103/aws-thumbnail/commit/8f6059487de15f78b8e0b503eea5412abba6f3e6) · [DynamoDB COMPLETE](https://github.com/bndt0103/aws-thumbnail/blob/8f6059487de15f78b8e0b503eea5412abba6f3e6/evidence/tuan-2/trung/E13a_dynamodb-complete-original.png) · [CloudWatch REPORT](https://github.com/bndt0103/aws-thumbnail/blob/8f6059487de15f78b8e0b503eea5412abba6f3e6/evidence/tuan-2/trung/E14b_cloudwatch-report-details.png) |
| Sự kiện trùng và nguồn output | [39678dc](https://github.com/bndt0103/aws-thumbnail/commit/39678dc6bdc112baa7a5682adfd09e63a9c87644) · [Log duplicate](https://github.com/bndt0103/aws-thumbnail/blob/39678dc6bdc112baa7a5682adfd09e63a9c87644/evidence/tuan-2/trung/E19b_cloudwatch-complete-duplicate.png) · [Notification output](https://github.com/bndt0103/aws-thumbnail/blob/39678dc6bdc112baa7a5682adfd09e63a9c87644/evidence/tuan-2/trung/T09c_output-no-event-notifications.png) |
| Gallery với ảnh hợp lệ | [b0d72a2](https://github.com/bndt0103/aws-thumbnail/commit/b0d72a2e01e68c66671a12b02a6397dc7117c80a) · [Gallery ảnh ngang](https://github.com/bndt0103/aws-thumbnail/blob/b0d72a2e01e68c66671a12b02a6397dc7117c80a/evidence/tuan-2/tuan/W2-L01_gallery-landscape-complete.png) · [Ảnh nhỏ](https://github.com/bndt0103/aws-thumbnail/blob/b0d72a2e01e68c66671a12b02a6397dc7117c80a/evidence/tuan-2/tuan/T05_gallery-small-no-upscale.png) |
| Đầu vào lỗi và kiểm soát truy cập | [9795a3b](https://github.com/bndt0103/aws-thumbnail/commit/9795a3b5872e3b832846bc752712c307425e2ce9) · [HTTP 400](https://github.com/bndt0103/aws-thumbnail/blob/9795a3b5872e3b832846bc752712c307425e2ce9/evidence/tuan-2/tuan/T07b_api-oversize-http-400.png) · [HTTP 401](https://github.com/bndt0103/aws-thumbnail/blob/9795a3b5872e3b832846bc752712c307425e2ce9/evidence/tuan-2/tuan/T11_api-photos-unauthorized.png) · [HTTP 403](https://github.com/bndt0103/aws-thumbnail/blob/9795a3b5872e3b832846bc752712c307425e2ce9/evidence/tuan-2/tuan/T12_upload-missing-csrf-403.png) |
| Tổng hợp minh chứng và báo cáo | [f4a4ad9](https://github.com/bndt0103/aws-thumbnail/commit/f4a4ad9cbb1af3ba38ab208463e53850af52864a) · [Danh mục ảnh](https://github.com/bndt0103/aws-thumbnail/blob/f4a4ad9cbb1af3ba38ab208463e53850af52864a/evidence/tuan-2/DANH_MUC_MINH_CHUNG.csv) · [Kết quả kiểm thử](https://github.com/bndt0103/aws-thumbnail/blob/f4a4ad9cbb1af3ba38ab208463e53850af52864a/progress/week-2/test-results.csv) |

Các commit ghi nhận phần hồ sơ đã hoàn thiện và đưa lên GitHub. Repo không lưu riêng bản nháp AI để so sánh từng dòng trước–sau; vì vậy, link file và commit dùng để đối chiếu nội dung, người đứng tên và kết quả kiểm thử, không tự xác định từng dòng do AI hay sinh viên viết. Metadata tác giả và người thao tác Git được dẫn ở mục 4.

## 7. Đánh giá và hướng tiếp theo

Nhóm hoàn thành mốc tích hợp tuần 2 trong phạm vi đã kiểm tra. Luồng S3–Lambda–S3/DynamoDB hoạt động, gallery cục bộ tải và hiển thị kết quả, các tình huống đầu vào và kiểm soát truy cập cho phản hồi phù hợp.

Số liệu hiệu năng hiện lấy từ các lần chạy đơn lẻ. Nhóm chưa thử tải lớn, lỗi mạng, timeout, thiếu bộ nhớ và retry phục hồi đầy đủ trên AWS. Gallery chưa triển khai trên EC2. Tuần 3 dự kiến triển khai gallery lên EC2, kiểm tra quyền truy cập, liên kết ảnh riêng tư, thời hạn URL và khởi động lại ứng dụng.
