# Phân công commit tuần 2 theo từng file

Ngày lập: 18/10/2026. Kho mã nguồn: https://github.com/bndt0103/aws-thumbnail.

Đây là kế hoạch cho các thay đổi đang có trong workspace, chưa phải lịch sử commit đã thực hiện. Trung phụ trách AWS và worker; Tuấn phụ trách gallery, kiểm thử và tổng hợp báo cáo. Người phụ trách trong bảng sẽ rà soát và commit phần được giao bằng tài khoản của mình; cách chia thư mục ảnh không xác nhận riêng ai đã chụp hoặc thao tác.

Hiện không có thay đổi mới trong mã worker, Flask hoặc bộ test Python. Các commit dưới đây ghi nhận minh chứng và tài liệu tuần 2; không cần tạo lại commit mã nguồn tuần 1.

## 1. Phân công và thứ tự

| Mã | Người phụ trách | Nội dung | Số file |
|---|---|---|---:|
| C01 | Trung | Chuẩn bị tài liệu và quy tắc Git tuần 2 | 3 |
| C02 | Trung | Minh chứng cấu hình Lambda và trigger S3 | 6 |
| C03 | Trung | Minh chứng xử lý ảnh, metadata và giám sát | 10 |
| C04 | Trung | Minh chứng sự kiện trùng và tách bucket đầu ra | 6 |
| C05 | Tuấn | Minh chứng gallery xử lý các dạng ảnh hợp lệ | 5 |
| C06 | Tuấn | Minh chứng giới hạn upload, ảnh cùng tên và kiểm soát truy cập | 8 |
| C07 | Tuấn | Danh mục ảnh và kết quả kiểm thử chung | 4 |
| C08 | Tuấn | Công cụ tạo Word và bộ báo cáo hoàn chỉnh | 7 |

Trung: Bùi Nguyễn Duy Trung — 24110363 — GitHub `bndt0103`.

Tuấn: Đỗ Anh Tuấn — 24110369 — GitHub `DoAnhTuan-24110369`.

Thứ tự: Trung thực hiện C01–C04, Tuấn thực hiện C05–C08. C01 chứa quy tắc cho phép Git lưu minh chứng và Word. C07–C08 tổng hợp cả hai phần nên thực hiện sau khi ảnh của Trung và Tuấn đã có trong nhánh tổng hợp.

## 2. Danh sách từng file

### C01 — Trung: Chuẩn bị tài liệu và quy tắc Git tuần 2

Nội dung commit: `Tuần 2: bổ sung hướng dẫn, phân công commit và quy tắc lưu minh chứng`.

| File | Nội dung được rà soát và đưa lên Git |
|---|---|
| `.gitignore` | Cho phép lưu Word và minh chứng tuần 2; bỏ qua dữ liệu cục bộ. |
| `HUONG_DAN_TUAN_2.md` | Tài liệu hướng dẫn triển khai và kế hoạch tuần 2. |
| `PHAN_CONG_COMMIT_TUAN2.md` | Bảng phân công commit theo từng file. |

### C02 — Trung: Minh chứng cấu hình Lambda và trigger S3

Nội dung commit: `Tuần 2: ghi nhận cấu hình Lambda, Pillow Layer và trigger S3`.

| File | Nội dung được rà soát và đưa lên Git |
|---|---|
| `evidence/tuan-2/trung/E07_lambda-execution-role.png` | Execution role LabRole. |
| `evidence/tuan-2/trung/E08a_lambda-runtime-layer.png` | Runtime, kiến trúc, handler và Pillow Layer. |
| `evidence/tuan-2/trung/E08b_lambda-general-configuration.png` | Memory và timeout. |
| `evidence/tuan-2/trung/E08c_lambda-environment-variables.png` | Các biến cấu hình Lambda. |
| `evidence/tuan-2/trung/E08d_lambda-code-uploaded.png` | Gói mã đã tải lên Lambda. |
| `evidence/tuan-2/trung/E09_lambda-s3-trigger.png` | Trigger từ bucket input, prefix uploads/. |

### C03 — Trung: Minh chứng xử lý ảnh, metadata và giám sát

Nội dung commit: `Tuần 2: bổ sung kết quả S3, metadata DynamoDB và log CloudWatch`.

| File | Nội dung được rà soát và đưa lên Git |
|---|---|
| `evidence/tuan-2/trung/E10_s3-input-landscape.png` | Ảnh đầu vào trên S3. |
| `evidence/tuan-2/trung/E11_s3-output-three-thumbnails.png` | Ba object thumbnail đầu ra. |
| `evidence/tuan-2/trung/E12_thumbnail-watermark-dimensions.png` | Watermark và kích thước thumbnail. |
| `evidence/tuan-2/trung/E12_output-thumbnail-1000x625.jpg` | Tệp JPEG kết quả tải từ S3. |
| `evidence/tuan-2/trung/E13a_dynamodb-complete-original.png` | Trạng thái COMPLETE và thông tin ảnh gốc. |
| `evidence/tuan-2/trung/E13c_dynamodb-variant-150.png` | Metadata của phiên bản 150 pixel. |
| `evidence/tuan-2/trung/E13d_dynamodb-variants-400-1000.png` | Metadata của phiên bản 400 và 1000 pixel. |
| `evidence/tuan-2/trung/E14b_cloudwatch-report-details.png` | Log REPORT: thời gian và bộ nhớ. |
| `evidence/tuan-2/trung/E14c_cloudwatch-retention-7-days.png` | Retention 1 tuần. |
| `evidence/tuan-2/trung/E15_lambda-monitor-metrics.png` | Chỉ số invocation, duration và errors. |

### C04 — Trung: Minh chứng sự kiện trùng và tách bucket đầu ra

Nội dung commit: `Tuần 2: ghi nhận kiểm tra duplicate và notification của bucket output`.

| File | Nội dung được rà soát và đưa lên Git |
|---|---|
| `evidence/tuan-2/trung/E19a_lambda-duplicate-response.png` | Response DUPLICATE khi chạy lại sự kiện. |
| `evidence/tuan-2/trung/E19b_cloudwatch-complete-duplicate.png` | Log COMPLETE và DUPLICATE_SKIPPED. |
| `evidence/tuan-2/trung/E19c_s3-output-after-duplicate.png` | Thời gian sửa object sau phép thử duplicate. |
| `evidence/tuan-2/trung/T09a_output-loop-check-upload.png` | Upload tệp kiểm tra vào bucket output. |
| `evidence/tuan-2/trung/T09b_cloudwatch-after-output-upload.png` | Log được quan sát sau upload output. |
| `evidence/tuan-2/trung/T09c_output-no-event-notifications.png` | Output không có event notification; EventBridge tắt. |

### C05 — Tuấn: Minh chứng gallery xử lý các dạng ảnh hợp lệ

Nội dung commit: `Tuần 2: bổ sung minh chứng gallery xử lý ảnh hợp lệ`.

| File | Nội dung được rà soát và đưa lên Git |
|---|---|
| `evidence/tuan-2/tuan/W2-L01_gallery-landscape-complete.png` | Ảnh ngang và ba phiên bản. |
| `evidence/tuan-2/tuan/T02_gallery-portrait-complete.png` | Ảnh dọc, giữ tỷ lệ. |
| `evidence/tuan-2/tuan/T03_gallery-square-complete.png` | Ảnh vuông. |
| `evidence/tuan-2/tuan/T04_gallery-transparent-white-background.png` | PNG trong suốt chuyển sang nền trắng. |
| `evidence/tuan-2/tuan/T05_gallery-small-no-upscale.png` | Ảnh nhỏ giữ nguyên kích thước. |

### C06 — Tuấn: Minh chứng giới hạn upload, ảnh cùng tên và kiểm soát truy cập

Nội dung commit: `Tuần 2: bổ sung kiểm tra ảnh lỗi, giới hạn upload, tên trùng và xác thực`.

| File | Nội dung được rà soát và đưa lên Git |
|---|---|
| `evidence/tuan-2/tuan/T06_gallery-broken-rejected.png` | Từ chối dữ liệu ảnh hỏng. |
| `evidence/tuan-2/tuan/T07a_gallery-oversize-rejected.png` | Giao diện từ chối tệp vượt 10 MiB. |
| `evidence/tuan-2/tuan/T07b_api-oversize-http-400.png` | API trả HTTP 400 cho tệp vượt giới hạn. |
| `evidence/tuan-2/tuan/T10a_gallery-second-landscape-upload.png` | Gallery sau lần upload thứ hai cùng tên. |
| `evidence/tuan-2/tuan/T10b_api-landscape-second-key.png` | source_key và image_id của lần upload thứ hai. |
| `evidence/tuan-2/tuan/T10c_api-landscape-first-key.png` | source_key và image_id của lần upload đầu. |
| `evidence/tuan-2/tuan/T11_api-photos-unauthorized.png` | API photos trả HTTP 401 sau đăng xuất. |
| `evidence/tuan-2/tuan/T12_upload-missing-csrf-403.png` | Upload thiếu CSRF token trả HTTP 403. |

### C07 — Tuấn: Danh mục ảnh và kết quả kiểm thử chung

Nội dung commit: `Tuần 2: đối chiếu danh mục minh chứng và kết quả 12 tình huống kiểm thử`.

| File | Nội dung được rà soát và đưa lên Git |
|---|---|
| `evidence/tuan-2/DANH_MUC_MINH_CHUNG.csv` | Danh mục đường dẫn, chú thích, SHA-256 và ảnh chọn cho Word. |
| `evidence/tuan-2/DOI_CHIEU_ANH.json` | Ánh xạ tên ảnh gốc sang tên mới và mã băm. |
| `evidence/tuan-2/README.md` | Giải thích bộ minh chứng và cách phân loại. |
| `progress/week-2/test-results.csv` | Kết quả T01–T12, đối chiếu với ảnh thực tế. |

### C08 — Tuấn: Công cụ tạo Word và bộ báo cáo hoàn chỉnh

Nội dung commit: `Tuần 2: hoàn thiện báo cáo Word, khai báo AI và dữ liệu tổng hợp`.

| File | Nội dung được rà soát và đưa lên Git |
|---|---|
| `requirements-report.txt` | Phụ thuộc để tạo báo cáo Word. |
| `scripts/build_week2_report.py` | Script tạo báo cáo từ nội dung và minh chứng. |
| `progress/week-2/report-content.json` | Nội dung chính thức, bảng và vị trí chèn ảnh. |
| `progress/week-2/report-status.json` | Trạng thái, kết quả tổng hợp và thông tin AI. |
| `KHAI_BAO_AI_TUAN2.md` | Khai báo hỗ trợ AI và phần nhóm thực hiện. |
| `BAO_CAO_NOP_BAI_TUAN2.md` | Nội dung mô tả nộp bài tuần 2. |
| `Report/BaoCaoTuan2_24110363_24110369.docx` | Báo cáo Word 24 trang, 29 ảnh minh chứng. |

## 3. Lệnh stage và commit theo nhóm

Chạy từ thư mục gốc của repo. Mỗi người thực hiện trong clone của mình, trên nhánh riêng. Các file mới phải được sao chép sang đúng clone trước khi chạy lệnh. Kiểm tra `git var GIT_AUTHOR_IDENT` để xác nhận danh tính Git; không thay tác giả hoặc ngày của commit cũ.

Mỗi khối dưới đây chỉ stage đúng danh sách file trong nhóm đó. Trước khi commit, danh sách `git diff --cached --name-only` phải khớp nhóm; nếu đã có file khác được stage thì xử lý riêng trước khi tiếp tục.

### Trung

Nhánh đề nghị: `tuan-2/trung-lambda`.

**C01**

```powershell
git add -- `
  ".gitignore" `
  "HUONG_DAN_TUAN_2.md" `
  "PHAN_CONG_COMMIT_TUAN2.md"
git diff --cached --name-only
git diff --cached --check
git commit -m "Tuần 2: bổ sung hướng dẫn, phân công commit và quy tắc lưu minh chứng"
```

**C02**

```powershell
git add -- `
  "evidence/tuan-2/trung/E07_lambda-execution-role.png" `
  "evidence/tuan-2/trung/E08a_lambda-runtime-layer.png" `
  "evidence/tuan-2/trung/E08b_lambda-general-configuration.png" `
  "evidence/tuan-2/trung/E08c_lambda-environment-variables.png" `
  "evidence/tuan-2/trung/E08d_lambda-code-uploaded.png" `
  "evidence/tuan-2/trung/E09_lambda-s3-trigger.png"
git diff --cached --name-only
git diff --cached --check
git commit -m "Tuần 2: ghi nhận cấu hình Lambda, Pillow Layer và trigger S3"
```

**C03**

```powershell
git add -- `
  "evidence/tuan-2/trung/E10_s3-input-landscape.png" `
  "evidence/tuan-2/trung/E11_s3-output-three-thumbnails.png" `
  "evidence/tuan-2/trung/E12_thumbnail-watermark-dimensions.png" `
  "evidence/tuan-2/trung/E12_output-thumbnail-1000x625.jpg" `
  "evidence/tuan-2/trung/E13a_dynamodb-complete-original.png" `
  "evidence/tuan-2/trung/E13c_dynamodb-variant-150.png" `
  "evidence/tuan-2/trung/E13d_dynamodb-variants-400-1000.png" `
  "evidence/tuan-2/trung/E14b_cloudwatch-report-details.png" `
  "evidence/tuan-2/trung/E14c_cloudwatch-retention-7-days.png" `
  "evidence/tuan-2/trung/E15_lambda-monitor-metrics.png"
git diff --cached --name-only
git diff --cached --check
git commit -m "Tuần 2: bổ sung kết quả S3, metadata DynamoDB và log CloudWatch"
```

**C04**

```powershell
git add -- `
  "evidence/tuan-2/trung/E19a_lambda-duplicate-response.png" `
  "evidence/tuan-2/trung/E19b_cloudwatch-complete-duplicate.png" `
  "evidence/tuan-2/trung/E19c_s3-output-after-duplicate.png" `
  "evidence/tuan-2/trung/T09a_output-loop-check-upload.png" `
  "evidence/tuan-2/trung/T09b_cloudwatch-after-output-upload.png" `
  "evidence/tuan-2/trung/T09c_output-no-event-notifications.png"
git diff --cached --name-only
git diff --cached --check
git commit -m "Tuần 2: ghi nhận kiểm tra duplicate và notification của bucket output"
```

### Tuấn

Nhánh đề nghị: `tuan-2/tuan-gallery`.

**C05**

```powershell
git add -- `
  "evidence/tuan-2/tuan/W2-L01_gallery-landscape-complete.png" `
  "evidence/tuan-2/tuan/T02_gallery-portrait-complete.png" `
  "evidence/tuan-2/tuan/T03_gallery-square-complete.png" `
  "evidence/tuan-2/tuan/T04_gallery-transparent-white-background.png" `
  "evidence/tuan-2/tuan/T05_gallery-small-no-upscale.png"
git diff --cached --name-only
git diff --cached --check
git commit -m "Tuần 2: bổ sung minh chứng gallery xử lý ảnh hợp lệ"
```

**C06**

```powershell
git add -- `
  "evidence/tuan-2/tuan/T06_gallery-broken-rejected.png" `
  "evidence/tuan-2/tuan/T07a_gallery-oversize-rejected.png" `
  "evidence/tuan-2/tuan/T07b_api-oversize-http-400.png" `
  "evidence/tuan-2/tuan/T10a_gallery-second-landscape-upload.png" `
  "evidence/tuan-2/tuan/T10b_api-landscape-second-key.png" `
  "evidence/tuan-2/tuan/T10c_api-landscape-first-key.png" `
  "evidence/tuan-2/tuan/T11_api-photos-unauthorized.png" `
  "evidence/tuan-2/tuan/T12_upload-missing-csrf-403.png"
git diff --cached --name-only
git diff --cached --check
git commit -m "Tuần 2: bổ sung kiểm tra ảnh lỗi, giới hạn upload, tên trùng và xác thực"
```

**C07**

```powershell
git add -- `
  "evidence/tuan-2/DANH_MUC_MINH_CHUNG.csv" `
  "evidence/tuan-2/DOI_CHIEU_ANH.json" `
  "evidence/tuan-2/README.md" `
  "progress/week-2/test-results.csv"
git diff --cached --name-only
git diff --cached --check
git commit -m "Tuần 2: đối chiếu danh mục minh chứng và kết quả 12 tình huống kiểm thử"
```

**C08**

```powershell
git add -- `
  "requirements-report.txt" `
  "scripts/build_week2_report.py" `
  "progress/week-2/report-content.json" `
  "progress/week-2/report-status.json" `
  "KHAI_BAO_AI_TUAN2.md" `
  "BAO_CAO_NOP_BAI_TUAN2.md" `
  "Report/BaoCaoTuan2_24110363_24110369.docx"
git diff --cached --name-only
git diff --cached --check
git commit -m "Tuần 2: hoàn thiện báo cáo Word, khai báo AI và dữ liệu tổng hợp"
```

## 4. File chưa đưa vào các commit trên

Các file dưới đây vẫn là nhật ký mẫu hoặc thông tin cần cá nhân xác nhận. Giữ riêng cho tới khi nội dung phản ánh đúng phần việc thực tế.

| File | Phụ trách | Nội dung còn cần hoàn thiện |
|---|---|---|
| `progress/week-2/trung-aws.md` | Trung | Cập nhật trạng thái cũ và gắn minh chứng AWS thực tế. |
| `progress/week-2/trung-ai.md` | Trung | Ghi phần hỗ trợ AI Trung thực sự sử dụng, phần đã kiểm tra và link thật. |
| `progress/week-2/trung-worklog.csv` | Trung | Ghi thời gian làm thực tế; hiện mới có dòng tiêu đề. |
| `progress/week-2/tuan-gallery.md` | Tuấn | Cập nhật trạng thái cũ bằng kết quả gallery đã đối chiếu. |
| `progress/week-2/tuan-ai.md` | Tuấn | Ghi phần hỗ trợ AI Tuấn thực sự sử dụng, phần đã kiểm tra và link thật. |
| `progress/week-2/tuan-worklog.csv` | Tuấn | Ghi thời gian làm thực tế; hiện mới có dòng tiêu đề. |
| `progress/week-2/local-verification.txt` | Trung rà soát | Giữ kết quả 19 test giả lập; làm rõ câu trạng thái AWS cũ thuộc thời điểm kiểm tra chuẩn bị cục bộ. |

Khi các nhật ký đã hoàn chỉnh, Trung gom ba file cá nhân thành một commit; Tuấn gom ba file cá nhân thành một commit. Kết quả thao tác được ghi nguồn nhóm nếu chưa xác nhận riêng người thực hiện. Không suy ra giờ làm từ thời gian chụp ảnh.

## 5. File nằm ngoài đợt commit tuần 2

| File hoặc thư mục | Cách xử lý |
|---|---|
| `BAO_CAO_NOP_BAI.md` | Có thay đổi cục bộ thuộc tuần 1; để riêng, không gộp vào các commit trên. |
| `tests/oversize.local.jpg` | Tệp thử dung lượng hơn 10 MiB dùng cục bộ; không đưa vào đợt commit này. |
| `tests/samples/loop-check.jpg.jpg` | Bản sao dùng để thao tác thử; minh chứng phép thử đã nằm trong C04. |
| `evidence/tuan-2/anhminhchung/` | Lưu các ảnh bổ trợ tại máy; đang được Git bỏ qua. |
| `Report/BaoCaoTuan2_24110363_24110369.pdf` | Bản xuất để nộp; Git hiện bỏ qua PDF. Word được commit trong C08. |
| `dist/`, `.venv/`, `.env`, `.aws/` | Giữ theo quy tắc bỏ qua hiện có. |

## 6. Đối chiếu sau khi đưa lên GitHub

Sau khi các commit được push và hợp nhất, Tuấn tổng hợp link commit thật vào `KHAI_BAO_AI_TUAN2.md`, `BAO_CAO_NOP_BAI_TUAN2.md` và `progress/week-2/report-status.json` khi tài liệu có nội dung cần cập nhật. Tạo lại Word nếu dữ liệu báo cáo thay đổi, rồi commit phần cập nhật trong một commit chốt riêng. Không điền SHA dự kiến hoặc đổi commit tuần 1 thành minh chứng triển khai tuần 2.

Đây là bảng phân công; trạng thái thực hiện được đối chiếu bằng lịch sử Git và các commit đã có trên GitHub. Không dùng `git add .` cho workspace hiện tại vì còn thay đổi tuần 1, nhật ký mẫu và file thử cục bộ.
