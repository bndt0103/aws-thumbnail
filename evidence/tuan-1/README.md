# Danh mục ảnh minh chứng tuần 1

Các tệp trong thư mục này được khôi phục ngày 15/10/2026 từ bản lưu cục bộ của nhóm, không tạo ảnh AWS mới và không thay đổi nội dung ảnh. Ngày khôi phục/commit không phải ngày chụp. Tên người chụp và thời điểm chưa được xác nhận trong danh mục gốc tiếp tục để trống.

Ảnh dùng để đối chiếu các bước sinh viên đã thực hiện trên máy và AWS Academy sau khi được ChatGPT hướng dẫn: môi trường Python/Git, kiểm thử cục bộ, Learner Lab, IAM, S3, DynamoDB, Pillow Layer và ngân sách. Ảnh output bucket rỗng/DynamoDB chưa có bản ghi phản ánh đúng trạng thái tuần 1; không được dùng để kết luận luồng Lambda đã tích hợp thành công.

- [Danh mục CSV gốc](DANH_MUC_MINH_CHUNG.csv): mã ảnh, mục báo cáo và ghi chú.
- [Đối chiếu và SHA-256](DOI_CHIEU_ANH.json): kiểm tra nội dung ảnh với ảnh nhúng trong báo cáo. Ảnh bổ trợ không chèn vào Word vẫn được giữ và ghi rõ.
- [Báo cáo Word](../../Report/BaoCaoTuan1_24110363_24110369.docx).

## Ảnh và vị trí đối chiếu

| Ảnh gốc | Vị trí trong báo cáo | Đối chiếu byte với ảnh Word |
|---|---|---|
| [E01_lab-ready.png](E01_lab-ready.png) | 3.2; Hình 3.3 | Khớp SHA-256 ảnh nhúng |
| [E02_account-region.png](E02_account-region.png) | Thông tin tài khoản tại mục 3.2; ảnh lưu hồ sơ, không chèn trong báo cáo | Ảnh bổ trợ; không khớp trực tiếp ảnh nhúng |
| [E03a_input-objects.png](E03a_input-objects.png) | 3.4; Hình 3.6 | Khớp SHA-256 ảnh nhúng |
| [E03b_input-block-public-access.png](E03b_input-block-public-access.png) | 3.5.1; Hình 3.8 | Khớp SHA-256 ảnh nhúng |
| [E03c_input-object-ownership.png](E03c_input-object-ownership.png) | 3.5.2; Hình 3.10 | Khớp SHA-256 ảnh nhúng |
| [E03d_input-default-encryption.png](E03d_input-default-encryption.png) | 3.5.3; Hình 3.12 | Khớp SHA-256 ảnh nhúng |
| [E03d_input-overview-versioning.png](E03d_input-overview-versioning.png) | 3.5.3; Hình 3.12 | Ảnh bổ trợ; không khớp trực tiếp ảnh nhúng |
| [E04a_output-objects.png](E04a_output-objects.png) | 3.4; Hình 3.7 | Khớp SHA-256 ảnh nhúng |
| [E04b_output-block-public-access.png](E04b_output-block-public-access.png) | 3.5.1 và 3.5.2; Hình 3.9 và Hình 3.11 | Khớp SHA-256 ảnh nhúng |
| [E04b_output-object-ownership.png](E04b_output-object-ownership.png) | 3.5.1 và 3.5.2; Hình 3.9 và Hình 3.11 | Khớp SHA-256 ảnh nhúng |
| [E04c_output-default-encryption.png](E04c_output-default-encryption.png) | 3.5.3; Hình 3.13 thể hiện mã hóa qua ảnh E18b; ảnh riêng lưu hồ sơ | Ảnh bổ trợ; không khớp trực tiếp ảnh nhúng |
| [E04c_output-overview-versioning.png](E04c_output-overview-versioning.png) | 3.5.3; Hình 3.13 thể hiện mã hóa qua ảnh E18b; ảnh riêng lưu hồ sơ | Ảnh bổ trợ; không khớp trực tiếp ảnh nhúng |
| [E05a_dynamodb-settings.png](E05a_dynamodb-settings.png) | 3.6; Hình 3.14 | Khớp SHA-256 ảnh nhúng |
| [E06a_pillow-layer-version.png](E06a_pillow-layer-version.png) | 3.7; Hình 3.16 | Khớp SHA-256 ảnh nhúng |
| [E18a_input-tags.png](E18a_input-tags.png) | 3.5.3; nội dung nhãn quản lý; ảnh riêng lưu hồ sơ | Ảnh bổ trợ; không khớp trực tiếp ảnh nhúng |
| [E18b_output-tags.png](E18b_output-tags.png) | 3.5.3; Hình 3.13 | Khớp SHA-256 ảnh nhúng |
| [E18c_dynamodb-tags.png](E18c_dynamodb-tags.png) | 3.6; Hình 3.15 | Khớp SHA-256 ảnh nhúng |
| [E20b_lab-budget-end.png](E20b_lab-budget-end.png) | 3.8; Hình 3.17 | Khớp SHA-256 ảnh nhúng |
| [W1-IAM_labrole-permissions.png](W1-IAM_labrole-permissions.png) | 3.3; Hình 3.4 và Hình 3.5 | Ảnh bổ trợ; không khớp trực tiếp ảnh nhúng |
| [W1-IAM_labrole-summary.png](W1-IAM_labrole-summary.png) | 3.3; Hình 3.4 và Hình 3.5 | Khớp SHA-256 ảnh nhúng |
| [W1-IAM_labrole-trust-01.png](W1-IAM_labrole-trust-01.png) | 3.3; Hình 3.4 và Hình 3.5 | Ảnh bổ trợ; không khớp trực tiếp ảnh nhúng |
| [W1-IAM_labrole-trust-02.png](W1-IAM_labrole-trust-02.png) | 3.3; Hình 3.4 và Hình 3.5 | Khớp SHA-256 ảnh nhúng |
| [W1-LOCAL_python-git.png](W1-LOCAL_python-git.png) | 3.1; Hình 3.1 | Khớp SHA-256 ảnh nhúng |
| [W1-TEST_pytest.png](W1-TEST_pytest.png) | 3.1; Hình 3.2 | Khớp SHA-256 ảnh nhúng |

## Phạm vi minh chứng AI và sinh viên

ChatGPT hỗ trợ mã nguồn và hướng dẫn thao tác. Theo xác nhận của Bùi Nguyễn Duy Trung, sinh viên trực tiếp cấu hình trên môi trường thật. Các ảnh ghi nhận thuộc tính đang hiển thị tại thời điểm chụp; commit khôi phục ghi nhận việc bổ sung tài liệu minh chứng vào repo, không phải thời điểm tạo tài nguyên hoặc chứng cứ triển khai end-to-end.

Gemini hỗ trợ tóm lược/rà soát commit, hướng dẫn push GitHub và trình bày Markdown. Không gán cho Gemini phần sinh mã kiểm thử khi nhóm chưa xác nhận nội dung đó.
