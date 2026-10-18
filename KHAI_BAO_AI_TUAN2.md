# Khai báo sử dụng AI — Tuần 2

Công cụ: ChatGPT/Codex.

Phiên bản/model: không ghi nhận chính xác phiên bản cụ thể trong hồ sơ tuần 2.

Prompt đã dùng (tóm lược): Tiếp tục từ nền tảng tuần 1; hướng dẫn tích hợp S3–Lambda–DynamoDB và gallery cục bộ, xác định minh chứng cần chụp, giải thích kết quả kiểm thử và biên tập báo cáo tuần 2 theo ảnh thực tế.

Nội dung AI tạo ra/hỗ trợ: rà soát hướng dẫn, giải thích cấu hình AWS, đề xuất lệnh khởi chạy và yêu cầu thử API, hỗ trợ đọc log, phân loại ảnh và trình bày báo cáo Word. Mã xử lý ảnh, Lambda, Flask và bộ kiểm thử được kế thừa từ tuần 1.

Phần sinh viên đã thực hiện, sửa và kiểm chứng:

- Cấu hình Lambda, Pillow Layer, LabRole, biến môi trường và trigger đúng tài nguyên thực tế. Minh chứng: [runtime/Layer](evidence/tuan-2/trung/E08a_lambda-runtime-layer.png), [trigger S3](evidence/tuan-2/trung/E09_lambda-s3-trigger.png).
- Upload ảnh và đối chiếu thumbnail, metadata COMPLETE, thời gian và bộ nhớ của cùng lần xử lý. Minh chứng: [DynamoDB](evidence/tuan-2/trung/E13a_dynamodb-complete-original.png), [CloudWatch REPORT](evidence/tuan-2/trung/E14b_cloudwatch-report-details.png).
- Thực hiện phép thử sự kiện trùng và kiểm tra bucket output không làm nguồn kích hoạt. Minh chứng: [COMPLETE/DUPLICATE_SKIPPED](evidence/tuan-2/trung/E19b_cloudwatch-complete-duplicate.png), [notification của output](evidence/tuan-2/trung/T09c_output-no-event-notifications.png).
- Chạy gallery cục bộ và các tình huống ảnh hợp lệ, ảnh hỏng, dung lượng, tải cùng tên, đăng xuất và thiếu CSRF. Minh chứng: [gallery](evidence/tuan-2/tuan/W2-L01_gallery-landscape-complete.png), [HTTP 400](evidence/tuan-2/tuan/T07b_api-oversize-http-400.png), [HTTP 401](evidence/tuan-2/tuan/T11_api-photos-unauthorized.png), [HTTP 403](evidence/tuan-2/tuan/T12_upload-missing-csrf-403.png).

Các ảnh được đối chiếu theo kết quả thực tế ngày 18/10/2026. Kết quả pytest cục bộ 19/19 dùng AWS giả lập; 12 tình huống kiểm tra vận hành được ghi riêng trong [bảng kết quả tuần 2](progress/week-2/test-results.csv).

Mã nguồn nền đã có trên GitHub: [commit Lambda](https://github.com/bndt0103/aws-thumbnail/commit/e50cb0c19bfa43d8dafe2d9b67bbe24e82343dc9), [commit Pillow](https://github.com/bndt0103/aws-thumbnail/commit/1c41d751d490f3493a5ba7d2e87df52ba40966ca), [commit Flask](https://github.com/bndt0103/aws-thumbnail/commit/9b0aca9be588f0f496a228b456741a8b9bfc7c80). Đây là commit kế thừa từ tuần 1, không phải commit ghi nhận cấu hình AWS của tuần 2.
