# BÁO CÁO TIẾN ĐỘ TUẦN 1 - ĐỀ TÀI SERVERLESS THUMBNAIL GENERATOR TRÊN AWS

* **Môn học**: Điện toán đám mây (Cloud Computing)
* **Nhóm sinh viên thực hiện**:
  1. **Bùi Nguyễn Duy Trung** – MSSV: **24110363** (Trưởng nhóm, GitHub: [@bndt0103](https://github.com/bndt0103))
  2. **Đỗ Anh Tuấn** – MSSV: **24110369** (Thành viên, GitHub: [@DoAnhTuan-24110369](https://github.com/DoAnhTuan-24110369))
* **Đường dẫn GitHub Repository (Public)**: [https://github.com/bndt0103/aws-thumbnail](https://github.com/bndt0103/aws-thumbnail)
* **Lịch sử Commit đầy đủ (13 commits)**: [https://github.com/bndt0103/aws-thumbnail/commits/main](https://github.com/bndt0103/aws-thumbnail/commits/main)
* **Trạng thái CI/CD (GitHub Actions)**: ![Kiểm thử mã nguồn](https://github.com/bndt0103/aws-thumbnail/actions/workflows/tests.yml/badge.svg) **Passing (19/19 Test Cases Đạt 100%)**

---

## 1. MỤC TIÊU & TỔNG QUAN HỆ THỐNG
Dự án xây dựng hệ thống tạo ảnh thu nhỏ tự động trên **Amazon Web Services (AWS)**, kết hợp giao diện web để tải ảnh và xem kết quả. Theo thiết kế, ảnh tải lên S3 sẽ được Lambda xử lý thành ba ảnh JPEG có cạnh dài tối đa **150, 400 và 1000 pixel**, giữ nguyên tỷ lệ, loại bỏ EXIF, thêm watermark và lưu thông tin vào DynamoDB. Trong tuần 1, nhóm đã chuẩn bị tài nguyên AWS và kiểm thử mã nguồn bằng dịch vụ giả lập; việc tích hợp toàn bộ luồng trên AWS là bước tiếp theo.

### Sơ đồ luồng xử lý dữ liệu:
```
[User / Browser] 
       │ 
       ▼ (1. Upload Ảnh gốc)
[S3 Input: cloudphoto-input-103308504802]
       │
       ▼ (2. Trigger s3:ObjectCreated:*)
[AWS Lambda + Pillow: dự kiến tích hợp]
       │
       ├────► (3. Lưu ảnh 150/400/1000 px) ──► [S3 Output: cloudphoto-output-103308504802]
       │
       └────► (4. Ghi metadata và khóa ảnh S3) ──► [DynamoDB: cloud-photo-metadata]
```

---

## 2. KẾT QUẢ ĐẠT ĐƯỢC TRONG TUẦN 1
1. **Thiết lập hạ tầng AWS Cloud (AWS Academy)**:
   * Khởi tạo **02 bucket S3**: `cloudphoto-input-103308504802` và `cloudphoto-output-103308504802`; bật chặn truy cập công khai, Bucket owner enforced và mã hóa SSE-S3.
   * Khởi tạo bảng **Amazon DynamoDB**: `cloud-photo-metadata`, khóa phân vùng `image_id` kiểu String, không có sort key, chế độ On-demand.
   * Tạo **Pillow Layer** `cloud-photo-pillow` phiên bản 1, tương thích Python 3.12 và kiến trúc x86_64; kiểm tra `LabRole`. Đã chuẩn bị mã Lambda, chưa hoàn tất kết nối trigger S3 và kiểm thử tích hợp trên AWS.
2. **Module Xử lý ảnh nâng cao (`src/processor/image_tools.py`)**:
   * Tự động xoay ảnh theo đúng chiều chuẩn dựa trên EXIF Orientation.
   * Xử lý thu nhỏ kích thước giữ nguyên tỷ lệ (Aspect Ratio) không bị méo.
   * Loại bỏ toàn bộ metadata EXIF (GPS, thiết bị) để bảo vệ quyền riêng tư người dùng.
   * Thêm watermark mặc định "CLOUD PHOTO" vào góc dưới bên phải của ảnh.
   * Xử lý chuyển đổi hệ màu `RGBA/LA -> RGB` tránh lỗi khi ghi file JPEG.
3. **Ứng dụng Web Gallery (`src/web/`)**:
   * Xây dựng giao diện Web Flask cho phép xác thực đăng nhập, kéo thả upload ảnh trực tiếp, xem trước (preview) và tải về các phiên bản thumbnail.
4. **Kiểm thử tự động & CI/CD**:
   * Hoàn thành **19 ca kiểm thử Unit Tests** (`pytest`) bao phủ logic xử lý ảnh, bảo mật web và mock dịch vụ AWS S3/DynamoDB.
   * Cấu hình **GitHub Actions Workflow** tự động chạy kiểm thử khi push/pull request. Toàn bộ 19 test cases đều Passed trên môi trường Ubuntu CI.

---

## 3. BẢNG PHÂN CÔNG CÔNG VIỆC & MINH CHỨNG COMMIT TRÊN GITHUB

Phân công và số commit dưới đây đối chiếu bản mã nguồn tuần 1 tại f92ab84. Các commit bổ sung minh chứng ảnh và khai báo AI được dẫn riêng ở mục 5:

| STT | Thành viên & MSSV | GitHub Account | Trách nhiệm đảm nhiệm chính | Số Commit |
| :---: | :--- | :--- | :--- | :---: |
| 1 | **Bùi Nguyễn Duy Trung**<br>MSSV: `24110363` *(Trưởng nhóm)* | [@bndt0103](https://github.com/bndt0103) | • Thiết kế kiến trúc & thiết lập AWS Academy<br>• Xây dựng module xử lý ảnh Pillow (`image_tools.py`)<br>• Xây dựng AWS Lambda handler (`lambda_function.py`)<br>• Viết kịch bản build package Lambda & Viết tài liệu | **6 commits** |
| 2 | **Đỗ Anh Tuấn**<br>MSSV: `24110369` *(Thành viên)* | [@DoAnhTuan-24110369](https://github.com/DoAnhTuan-24110369) | • Xây dựng ứng dụng Flask Web Gallery (`src/web/`)<br>• Thiết kế giao diện HTML5/CSS/JS responsive<br>• Xây dựng bộ 19 ca kiểm thử tự động (`tests/`)<br>• Cấu hình CI Pipeline GitHub Actions tự động test | **7 commits** |

### Chi tiết các Commit và Link từng file trên GitHub:

#### A. Đóng góp của BÙI NGUYỄN DUY TRUNG (MSSV: 24110363 - @bndt0103)
* **Commit [`589896d`](https://github.com/bndt0103/aws-thumbnail/commit/589896d939b63b115d88c226088db7e7919d76c6)** – *chore: khởi tạo dự án với editorconfig và gitignore*:
  * Files: [.gitignore](https://github.com/bndt0103/aws-thumbnail/blob/main/.gitignore), [.editorconfig](https://github.com/bndt0103/aws-thumbnail/blob/main/.editorconfig), [.gitattributes](https://github.com/bndt0103/aws-thumbnail/blob/main/.gitattributes)
* **Commit [`1c41d75`](https://github.com/bndt0103/aws-thumbnail/commit/1c41d751d490f3493a5ba7d2e87df52ba40966ca)** – *feat(processor): xử lý thumbnail giữ tỷ lệ, watermark và xoá EXIF bằng Pillow*:
  * Files: [src/processor/image_tools.py](https://github.com/bndt0103/aws-thumbnail/blob/main/src/processor/image_tools.py)
* **Commit [`e50cb0c`](https://github.com/bndt0103/aws-thumbnail/commit/e50cb0c19bfa43d8dafe2d9b67bbe24e82343dc9)** – *feat(lambda): xây dựng handler nhận sự kiện S3 và ghi metadata vào DynamoDB*:
  * Files: [src/processor/lambda_function.py](https://github.com/bndt0103/aws-thumbnail/blob/main/src/processor/lambda_function.py)
* **Commit [`213b093`](https://github.com/bndt0103/aws-thumbnail/commit/213b09383c10cc6ea84c203ebd86ae7b4951e1b4)** – *feat(aws): ghi nhận thông số tài nguyên AWS Academy và script đóng gói*:
  * Files: [config/aws-resources.json](https://github.com/bndt0103/aws-thumbnail/blob/main/config/aws-resources.json), [scripts/build_packages.py](https://github.com/bndt0103/aws-thumbnail/blob/main/scripts/build_packages.py)
* **Commit [`03eef0a`](https://github.com/bndt0103/aws-thumbnail/commit/03eef0a52c65bc2f80d92ec55fa66f8e7af8c24a)** – *docs: mô tả kiến trúc hệ thống, sơ đồ luồng và hướng dẫn triển khai*:
  * Files: [README.md](https://github.com/bndt0103/aws-thumbnail/blob/main/README.md)
* **Commit [`f92ab84`](https://github.com/bndt0103/aws-thumbnail/commit/f92ab842641c61cba4c7c790ba85613f33ca26ae)** – *docs(report): bổ sung báo cáo tuần 1 với ảnh minh chứng AWS console*:
  * Files: [Report/BaoCaoTuan1_24110363_24110369.docx](https://github.com/bndt0103/aws-thumbnail/blob/main/Report/BaoCaoTuan1_24110363_24110369.docx)

#### B. Đóng góp của ĐỖ ANH TUẤN (MSSV: 24110369 - @DoAnhTuan-24110369)
* **Commit [`5eeb86d`](https://github.com/bndt0103/aws-thumbnail/commit/5eeb86df90d849c819e2232371bef5b696331bb8)** – *chore: khai báo thư viện phát triển pytest, Pillow, Flask và cấu hình pytest*:
  * Files: [pytest.ini](https://github.com/bndt0103/aws-thumbnail/blob/main/pytest.ini), [requirements-dev.txt](https://github.com/bndt0103/aws-thumbnail/blob/main/requirements-dev.txt), [src/web/requirements.txt](https://github.com/bndt0103/aws-thumbnail/blob/main/src/web/requirements.txt)
* **Commit [`176296e`](https://github.com/bndt0103/aws-thumbnail/commit/176296eb0b8238b3355654616ec25d50e6dedf40)** – *test(fixtures): tạo script sinh ảnh mẫu cho kiểm thử*:
  * Files: [scripts/create_samples.py](https://github.com/bndt0103/aws-thumbnail/blob/main/scripts/create_samples.py)
* **Commit [`30838ce`](https://github.com/bndt0103/aws-thumbnail/commit/30838ce3994c9d3e83d65fd40cef4bd047ee7b17)** – *test(images): viết 10 ca kiểm thử xử lý ảnh bao phủ mọi trường hợp*:
  * Files: [tests/test_images.py](https://github.com/bndt0103/aws-thumbnail/blob/main/tests/test_images.py)
* **Commit [`f3e62ba`](https://github.com/bndt0103/aws-thumbnail/commit/f3e62ba4a663a9d6cdd46d500ce0a2ab2fcf6ec9)** – *test(worker): viết 5 ca kiểm thử Lambda worker với mock S3 và DynamoDB*:
  * Files: [tests/test_worker.py](https://github.com/bndt0103/aws-thumbnail/blob/main/tests/test_worker.py)
* **Commit [`9b0aca9`](https://github.com/bndt0103/aws-thumbnail/commit/9b0aca9be588f0f496a228b456741a8b9bfc7c80)** – *feat(web): xây dựng giao diện Flask cho gallery ảnh*:
  * Files: [src/web/app.py](https://github.com/bndt0103/aws-thumbnail/blob/main/src/web/app.py), [src/web/templates/index.html](https://github.com/bndt0103/aws-thumbnail/blob/main/src/web/templates/index.html), [src/web/templates/login.html](https://github.com/bndt0103/aws-thumbnail/blob/main/src/web/templates/login.html), [src/web/static/app.js](https://github.com/bndt0103/aws-thumbnail/blob/main/src/web/static/app.js), [src/web/static/style.css](https://github.com/bndt0103/aws-thumbnail/blob/main/src/web/static/style.css)
* **Commit [`c4fa1ad`](https://github.com/bndt0103/aws-thumbnail/commit/c4fa1adae7f7a51c4a08bbf24bca7e905060d0da)** – *test(web): viết 4 ca kiểm thử bảo mật và upload cho Flask*:
  * Files: [tests/test_web.py](https://github.com/bndt0103/aws-thumbnail/blob/main/tests/test_web.py)
* **Commit [`be74109`](https://github.com/bndt0103/aws-thumbnail/commit/be7410979679823718063dd9a78bfcefecae44c8)** – *ci: thiết lập GitHub Actions chạy pytest tự động khi push*:
  * Files: [.github/workflows/tests.yml](https://github.com/bndt0103/aws-thumbnail/blob/main/.github/workflows/tests.yml)

---

## 4. TÀI LIỆU ĐÍNH KÈM & MINH CHỨNG AWS
* Báo cáo chi tiết: [BaoCaoTuan1_24110363_24110369.docx](https://github.com/bndt0103/aws-thumbnail/blob/main/Report/BaoCaoTuan1_24110363_24110369.docx), kèm ảnh cấu hình S3, DynamoDB và Pillow Layer trên AWS Academy. [Commit bổ sung báo cáo](https://github.com/bndt0103/aws-thumbnail/commit/f92ab842641c61cba4c7c790ba85613f33ca26ae).

---

---
* Danh mục ảnh cấu hình đã khôi phục: [24 ảnh gốc và vị trí đối chiếu](https://github.com/bndt0103/aws-thumbnail/blob/10b9d9898afbf21da8adf8e0b6dd2735377caee6/evidence/tuan-1/README.md); [CSV gốc](https://github.com/bndt0103/aws-thumbnail/blob/10b9d9898afbf21da8adf8e0b6dd2735377caee6/evidence/tuan-1/DANH_MUC_MINH_CHUNG.csv); [commit 10b9d98](https://github.com/bndt0103/aws-thumbnail/commit/10b9d9898afbf21da8adf8e0b6dd2735377caee6).


---

## 5. KHAI BÁO SỬ DỤNG AI VÀ MINH CHỨNG HOÀN THIỆN

Nhóm sử dụng ChatGPT Sol 6.1 hỗ trợ chủ yếu phần mã nguồn và hướng dẫn cấu hình; sinh viên trực tiếp thực hiện cấu hình trên máy và AWS Academy. Google Gemini hỗ trợ tóm lược/rà soát commit, hướng dẫn push GitHub và trình bày Markdown. Bản khai báo bổ sung ghi rõ hai phạm vi này cùng phần nhóm hoàn thiện và link commit đối chiếu.

Thông tin công cụ được cập nhật theo xác nhận của nhóm ngày 15/10/2026. Các prompt dưới đây là bản tóm lược yêu cầu đã trao đổi, không giả định là bản chép nguyên văn hội thoại. Model ChatGPT ghi Sol 6.1 theo xác nhận của nhóm; phiên bản Gemini không được suy đoán khi chưa ghi nhận chính xác.

### 1. ChatGPT — Hỗ trợ mã nguồn, hướng dẫn cấu hình và rà soát báo cáo

**Công cụ AI:** ChatGPT

**Phiên bản/model:** Sol 6.1 (theo xác nhận của nhóm)

**Prompt đã dùng (tóm lược theo xác nhận của nhóm):**

> Hướng dẫn xây dựng hệ thống tạo thumbnail trên AWS bằng S3, Lambda, DynamoDB và Pillow; hỗ trợ mã nguồn xử lý ảnh, web và kiểm thử, hướng dẫn cấu hình từng bước để nhóm thực hiện trên máy và AWS Academy.

**Nội dung AI tạo ra/hỗ trợ:** Hướng dẫn kiến trúc và cấu hình, đề xuất/soạn mã Python xử lý ảnh, Lambda worker, giao diện Flask và các thành phần kiểm thử; hỗ trợ tổ chức tài liệu và rà soát hồ sơ nộp lại. Đây là công cụ hỗ trợ phần code và hướng dẫn cấu hình chủ yếu theo xác nhận của nhóm.

**Phần sinh viên đã sửa/hoàn thiện và minh chứng:**

- **Bùi Nguyễn Duy Trung:** Trực tiếp thực hiện các bước cấu hình trên máy và AWS Academy: Python/Git, hai bucket S3, bảo mật bucket, LabRole, DynamoDB và Pillow Layer. Khôi phục 24 ảnh gốc cùng danh mục; 17 ảnh khớp SHA-256 với ảnh trong Word. Commit này ghi nhận việc khôi phục minh chứng, không phải ngày tạo tài nguyên. [Mã nguồn đối chiếu](https://github.com/bndt0103/aws-thumbnail/blob/10b9d9898afbf21da8adf8e0b6dd2735377caee6/evidence/tuan-1/README.md) · [Commit 10b9d98](https://github.com/bndt0103/aws-thumbnail/commit/10b9d9898afbf21da8adf8e0b6dd2735377caee6).
- **Bùi Nguyễn Duy Trung:** Đối chiếu tên tài nguyên và thông số thật: cloudphoto-input-103308504802, cloudphoto-output-103308504802, bảng cloud-photo-metadata chỉ có khóa image_id; Python 3.12 và x86_64 của layer. Ghi lại cấu hình và chuẩn bị script đóng gói. [Mã nguồn đối chiếu](https://github.com/bndt0103/aws-thumbnail/blob/213b09383c10cc6ea84c203ebd86ae7b4951e1b4/config/aws-resources.json#L4-L31) · [Commit 213b093](https://github.com/bndt0103/aws-thumbnail/commit/213b09383c10cc6ea84c203ebd86ae7b4951e1b4).
- **Bùi Nguyễn Duy Trung:** Áp dụng và hoàn thiện mã Pillow theo yêu cầu dự án: JPEG/PNG tĩnh, giới hạn 10 MiB/24 triệu pixel, cạnh dài tối đa 150/400/1000 px, giữ tỷ lệ, ghép nền trắng cho ảnh trong suốt, watermark CLOUD PHOTO và loại EXIF. Mã có AI hỗ trợ; commit được dẫn để đối chiếu phiên bản hoàn thiện. [Mã nguồn đối chiếu](https://github.com/bndt0103/aws-thumbnail/blob/1c41d751d490f3493a5ba7d2e87df52ba40966ca/src/processor/image_tools.py#L7-L75) · [Commit 1c41d75](https://github.com/bndt0103/aws-thumbnail/commit/1c41d751d490f3493a5ba7d2e87df52ba40966ca).
- **Bùi Nguyễn Duy Trung:** Hoàn thiện worker với cấu hình bucket/prefix, ba ảnh đầu ra và metadata trạng thái; kiểm tra các nhánh sự kiện trùng/lỗi qua kiểm thử giả lập. Chưa khai báo đã tích hợp đầy đủ Lambda trên AWS trong tuần 1. [Mã nguồn đối chiếu](https://github.com/bndt0103/aws-thumbnail/blob/e50cb0c19bfa43d8dafe2d9b67bbe24e82343dc9/src/processor/lambda_function.py#L30-L167) · [Commit e50cb0c](https://github.com/bndt0103/aws-thumbnail/commit/e50cb0c19bfa43d8dafe2d9b67bbe24e82343dc9).
- **Đỗ Anh Tuấn:** Theo phân công trong repo, hoàn thiện phần Flask có AI hỗ trợ: đăng nhập, CSRF, tải ảnh bằng tên khóa duy nhất, gallery và header bảo mật; đối chiếu bằng kiểm thử web. [Mã nguồn đối chiếu](https://github.com/bndt0103/aws-thumbnail/blob/9b0aca9be588f0f496a228b456741a8b9bfc7c80/src/web/app.py#L100-L229) · [Commit 9b0aca9](https://github.com/bndt0103/aws-thumbnail/commit/9b0aca9be588f0f496a228b456741a8b9bfc7c80).
- **Đỗ Anh Tuấn:** Hoàn thiện 10 ca ảnh: bốn hình dạng, RGBA, ba đầu vào không hợp lệ, GIF và EXIF; kiểm tra các kích thước và tỷ lệ đầu ra. [Mã nguồn đối chiếu](https://github.com/bndt0103/aws-thumbnail/blob/30838ce3994c9d3e83d65fd40cef4bd047ee7b17/tests/test_images.py#L17-L60) · [Commit 30838ce](https://github.com/bndt0103/aws-thumbnail/commit/30838ce3994c9d3e83d65fd40cef4bd047ee7b17).
- **Đỗ Anh Tuấn:** Hoàn thiện năm ca worker dùng mock S3/DynamoDB và bốn ca Flask; cấu hình kiểm thử tự động. Log CI của bản f92ab84 ghi nhận 19/19 ca đạt, không phải kiểm thử AWS tích hợp. [Mã nguồn đối chiếu](https://github.com/bndt0103/aws-thumbnail/blob/f3e62ba4a663a9d6cdd46d500ce0a2ab2fcf6ec9/tests/test_worker.py#L59-L133) · [Commit f3e62ba](https://github.com/bndt0103/aws-thumbnail/commit/f3e62ba4a663a9d6cdd46d500ce0a2ab2fcf6ec9).

### 2. Google Gemini — Tóm lược, rà soát commit và hướng dẫn trình bày Markdown

**Công cụ AI:** Google Gemini

**Phiên bản/model:** Không ghi nhận chính xác phiên bản/model

**Prompt đã dùng (tóm lược theo xác nhận của nhóm):**

> Xem và tóm lược lịch sử commit của dự án, kiểm tra commit/phân công đã phù hợp chưa, hướng dẫn push lên GitHub và cách viết file Markdown trình bày nội dung nộp tuần 1.

**Nội dung AI tạo ra/hỗ trợ:** Gợi ý cách rà soát và tóm lược commit, hướng dẫn thao tác push GitHub và bố cục Markdown cho báo cáo. Không kê khai Gemini là công cụ chủ yếu sinh code hoặc viết các bài kiểm thử.

**Phần sinh viên đã sửa/hoàn thiện và minh chứng:**

- **Nhóm sinh viên:** Đối chiếu từng link commit với tệp thật và trách nhiệm thành viên; giữ 13 commit mã nguồn tuần 1 làm mốc, bổ sung riêng commit khôi phục ảnh. Các commit mới ghi đúng thời điểm khôi phục/biên tập, không sửa lịch sử cũ. [Mã nguồn đối chiếu](https://github.com/bndt0103/aws-thumbnail/blob/10b9d9898afbf21da8adf8e0b6dd2735377caee6/evidence/tuan-1/DOI_CHIEU_ANH.json) · [Commit 10b9d98](https://github.com/bndt0103/aws-thumbnail/commit/10b9d9898afbf21da8adf8e0b6dd2735377caee6).
- **Nhóm sinh viên:** Thống nhất lại phạm vi sử dụng AI theo xác nhận thực tế; trình bày phần hỗ trợ, phần hoàn thiện và link minh chứng trong Markdown. Bản bổ sung có ChatGPT hỗ trợ rà soát và biên tập; nhóm kiểm tra lại thông tin trước khi nộp. [Mã nguồn đối chiếu](https://github.com/bndt0103/aws-thumbnail/blob/27b1e83c8cd6b2e42d302e32527d18e33f87e64a/AI_DISCLOSURE.md) · [Commit 27b1e83](https://github.com/bndt0103/aws-thumbnail/commit/27b1e83c8cd6b2e42d302e32527d18e33f87e64a).

### Danh mục ảnh cấu hình đã khôi phục

[24 ảnh và vị trí trong báo cáo](https://github.com/bndt0103/aws-thumbnail/blob/10b9d9898afbf21da8adf8e0b6dd2735377caee6/evidence/tuan-1/README.md) · [Danh mục CSV gốc](https://github.com/bndt0103/aws-thumbnail/blob/10b9d9898afbf21da8adf8e0b6dd2735377caee6/evidence/tuan-1/DANH_MUC_MINH_CHUNG.csv) · [Commit khôi phục 10b9d98](https://github.com/bndt0103/aws-thumbnail/commit/10b9d9898afbf21da8adf8e0b6dd2735377caee6).

Các ảnh được khôi phục nguyên tệp từ bản lưu cục bộ; 17 ảnh khớp SHA-256 với ảnh nhúng trong Word. Giữ nguyên ngày chụp/người chụp chưa được xác nhận trong danh mục. Commit mới minh chứng việc khôi phục hồ sơ, không được dùng làm ngày chụp hay ngày tạo tài nguyên.

### Phạm vi và kết quả kiểm chứng

Các commit được dẫn ghi nhận phiên bản mã nguồn nhóm đã hoàn thiện và đưa vào repo. Lịch sử hiện tại chủ yếu là các commit thêm file; repo không lưu riêng bản nháp AI để so sánh trước–sau. Vì vậy, link commit dùng để đối chiếu nội dung, người đứng tên commit và kết quả kiểm thử; không dùng để khẳng định Git tự chứng minh từng dòng do AI hay sinh viên viết.

Lần chạy GitHub Actions tại commit f92ab842641c61cba4c7c790ba85613f33ca26ae ghi nhận 19 passed trên Python 3.12, gồm 10 ca ảnh, 5 ca worker và 4 ca Flask. S3/DynamoDB trong các bài thử được giả lập; kết quả này chưa chứng minh luồng S3 → Lambda → S3/DynamoDB đã chạy hoàn chỉnh trên AWS. Ảnh cấu hình AWS trong báo cáo được giữ để minh chứng phần tài nguyên đã chuẩn bị.

[Minh chứng CI 19/19](https://github.com/bndt0103/aws-thumbnail/actions/runs/38563088053) · [Lịch sử repo](https://github.com/bndt0103/aws-thumbnail/commits/main).
