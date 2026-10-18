Đề tài: Xử lý ảnh tự động: tạo thumbnail khi upload lên Amazon S3.

Thành viên: Bùi Nguyễn Duy Trung — 24110363; Đỗ Anh Tuấn — 24110369.

GitHub: https://github.com/bndt0103/aws-thumbnail

Mục tiêu tuần 2: tích hợp Lambda, S3, DynamoDB và Pillow Layer; kiểm chứng luồng xử lý ảnh trên AWS và kết nối gallery Flask cục bộ.

Công việc và kết quả:

Triển khai cloud-photo-processor dùng Python 3.12, x86_64, LabRole và Pillow Layer phiên bản 1; cấu hình bộ nhớ 1024 MB, timeout 60 giây và các biến tài nguyên. Trigger theo dõi bucket input với s3:ObjectCreated:* và tiền tố uploads/.

Ảnh tải lên S3 đã được Lambda xử lý thành ba thumbnail có watermark, lưu vào bucket output và ghi metadata COMPLETE trong DynamoDB. CloudWatch ghi log và thông số thực thi; log group được đặt thời gian lưu 7 ngày.

Gallery tại 127.0.0.1:5000 đã tải và hiển thị ảnh từ AWS. Nhóm đối chiếu 12 tình huống về ảnh ngang, dọc, vuông, trong suốt, ảnh nhỏ, ảnh hỏng, quá dung lượng, sự kiện trùng, nguồn output, hai upload cùng tên, đăng xuất và CSRF. Các tình huống cho kết quả phù hợp với tiêu chí đã kiểm tra. Bộ kiểm thử cục bộ đạt 19/19 ca; kết quả này dùng AWS giả lập và được ghi riêng.

Phân công: Bùi Nguyễn Duy Trung phụ trách phần AWS và worker; Đỗ Anh Tuấn phụ trách gallery, kiểm thử và tổng hợp kết quả.

Đánh giá: hoàn thành mốc tích hợp tuần 2 trong phạm vi đã thử. Số liệu thời gian, bộ nhớ lấy từ các lần chạy đơn lẻ; chưa kết luận khả năng chịu tải hoặc tối ưu tài nguyên. Gallery chưa triển khai lên EC2, dự kiến tiếp tục trong tuần 3.

Tệp đính kèm: BaoCaoTuan2_24110363_24110369.docx, gồm kiến trúc, cấu hình, kết quả kiểm thử, ảnh minh chứng chèn trực tiếp trong từng phần và khai báo AI.
