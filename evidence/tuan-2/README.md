# Minh chứng tuần 2

Đã rà soát 48 ảnh chụp gốc ngày 18/10/2026 trong thư mục `anhminhchung` và đổi tên theo nội dung. Các ảnh được giữ nguyên byte dữ liệu; mã SHA-256 trong danh mục dùng để đối chiếu.

| Vị trí | Nội dung | Số lượng |
|---|---|---:|
| `trung/` | Cấu hình Lambda, trigger S3, output, DynamoDB, CloudWatch, duplicate và tránh vòng lặp | 21 ảnh chụp + 1 tệp JPEG kết quả |
| `tuan/` | Gallery và các ca kiểm thử ảnh, dung lượng, tải cùng tên, xác thực, CSRF | 13 ảnh chụp |
| `anhminhchung/_bo-tro/` | Ảnh trùng, điều hướng, cấu hình trung gian và lỗi thao tác; giữ để đối chiếu | 14 ảnh chụp |

Thư mục `trung` và `tuan` phân loại theo phần việc đã phân công. Đây không phải xác nhận riêng về người chụp hoặc người thao tác. Cột `member` ghi nguồn nhóm; người thực hiện từng nhiệm vụ cần xác nhận trong nhật ký cá nhân.

`DANH_MUC_MINH_CHUNG.csv` có đường dẫn tương đối, chú thích, test ID và mục báo cáo. Có 29 ảnh được chọn để chèn Word (`include_in_report=yes`); các ảnh bổ sung vẫn có trong danh mục với giá trị `no`. Không chèn ảnh lỗi thao tác hoặc ảnh cũ trước khi cấu hình vào phần kết quả hoàn thành.

`DOI_CHIEU_ANH.json` ghi tên tệp Screenshot ban đầu, tên mới và SHA-256 cho đủ 48 ảnh. Thời điểm `captured_at` được đọc từ tên tệp gốc, theo UTC+7; thời gian sự kiện AWS được đối chiếu riêng trong ảnh. Không dùng giờ chụp để suy ra số giờ thực tế đã làm.

`scripts/build_week2_report.py` đọc danh mục, chèn ảnh trực tiếp vào từng phần của Word và căn giữa. Không cần phụ lục ảnh riêng. Mã ảnh chỉ dùng để quản lý nội bộ; chú thích trong Word ghi nội dung hình, không in mã E07/E08.

Mỗi ảnh phải đọc được thông tin chính. Giữ bản gốc; che credential/password/token trước khi đưa lên GitHub. Không đưa URL ký sẵn còn hiệu lực vào minh chứng công khai.

Các mã có thể có nhiều dòng khi cần nhiều ảnh. Script đọc `include_in_report` và chỉ chèn ảnh được chọn vào phần tương ứng. Tệp JPEG tải từ S3 được giữ riêng và không chèn trùng với ảnh chụp watermark/kích thước.

Luồng upload S3 ban đầu, sự kiện duplicate thử tay và upload gallery là các lần thử khác nhau. Kết quả ban đầu có image_id `1a4c50af7f5bce6c5514d3c3e37a4322`; sự kiện duplicate có image_id `fbadbc0151913006011378f25f41f895`. Không gộp processing_ms của các lần thử này.

Bảng `progress/week-2/test-results.csv` đã gán đường dẫn minh chứng cho T01–T12 và ghi kết quả quan sát. Cột ngày giờ sử dụng thời gian chụp của ảnh đối chiếu; thời điểm upload/invocation được ghi riêng trong mô tả khi thấy trên màn hình. Người thực hiện từng ca chưa được xác nhận riêng nên bảng ghi nguồn nhóm. Với T09, kết luận dựa trên cấu hình không có notification của output và các log đã quan sát, không khẳng định mọi tình huống đều không thể có invocation.
