# Danh mục ảnh minh chứng Tuần 3 — Nhóm Serverless (CloudPhoto)

Thư mục lưu trữ các ảnh chụp minh chứng trên AWS Console, Terminal EC2 và Trình duyệt Web Gallery trong đợt triển khai Tuần 3.

## Phân chia thư mục:
- `trung/`: Các ảnh minh chứng liên quan đến cấu hình AWS, Lambda Layer tối ưu dung lượng và S3 Lifecycle Rule do Bùi Nguyễn Duy Trung (24110363) thực hiện.
- `tuan/`: Các ảnh minh chứng liên quan đến triển khai máy chủ EC2, kiểm thử Web Gallery, kiểm thử Presigned URL và khả năng tự phục hồi do Đỗ Anh Tuấn (24110369) thực hiện.

## Danh sách ảnh minh chứng:
1. `trung/E22_lambda-layer-code-size.png`: Gói mã Lambda tối ưu dung lượng (~9 KB) và Layer Pillow.
2. `trung/E23a_s3-output-lifecycle-rule-config.png`: Cấu hình S3 Lifecycle Rule dọn thumbnail cũ sau 7 ngày.
3. `trung/E23b_s3-output-lifecycle-rule-list.png`: Danh sách Lifecycle Rule trạng thái Enabled trên bucket output.
4. `tuan/E16a_ec2-instance-running.png`: Instance EC2 `cloud-photo-gallery` trạng thái Running và Public IP.
5. `tuan/E16b_ec2-iam-role-labinstanceprofile.png`: EC2 gắn IAM Role `LabInstanceProfile`.
6. `tuan/E16c_ec2-security-group-rules.png`: Cấu hình Security Group `cloud-photo-web-sg` (port 22, 8000).
7. `tuan/E16d_ec2-systemd-service-active.png`: Dịch vụ `cloud-photo.service` trạng thái `active (running)` trên EC2.
8. `tuan/E16e_ec2-curl-health-check.png`: Kiểm tra `curl http://127.0.0.1:8000/health` trả về `{"status":"ok"}`.
9. `tuan/E17a_ec2-gallery-login.png`: Giao diện đăng nhập Gallery truy cập qua SSH Tunnel.
10. `tuan/E17b_ec2-gallery-dashboard.png`: Dashboard Web Gallery hiển thị danh sách ảnh trên EC2.
11. `tuan/E24a_ec2-iam-role-access-test.png`: Lệnh AWS CLI đọc S3/DynamoDB từ EC2 bằng IAM Role.
12. `tuan/E24b_s3-direct-access-denied.png`: Truy cập trực tiếp link S3 không ký bị 403 AccessDenied (Bucket Private).
13. `tuan/E24c_presigned-url-valid.png`: Mở ảnh thumbnail qua Presigned URL hợp lệ.
14. `tuan/E24d_presigned-url-expired.png`: Presigned URL hết hạn sau 300 giây bị lỗi `Request has expired`.
15. `tuan/E25a_ec2-systemd-restart-test.png`: Thao tác restart service và tiến trình tự động hồi sinh.
16. `tuan/E25b_ec2-gallery-post-restart.png`: Web Gallery hoạt động bình thường sau khi service khởi động lại.
17. `tuan/E26a_ec2-upload-success-complete.png`: Upload ảnh mới qua Web EC2 hoàn thành trạng thái COMPLETE.
18. `tuan/E26b_ec2-cloudwatch-lambda-log.png`: CloudWatch log stream ghi nhận xử lý sự kiện upload từ Web EC2.

