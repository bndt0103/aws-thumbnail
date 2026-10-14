# Khai báo sử dụng AI và đối chiếu minh chứng tuần 1

Đề tài: Xử lý ảnh tự động, tạo thumbnail khi upload lên S3. Nhóm: Bùi Nguyễn Duy Trung (24110363), Đỗ Anh Tuấn (24110369).

## ChatGPT

- **Model:** Sol 6.1, theo thông tin nhóm xác nhận.
- **Prompt (tóm lược):** Hướng dẫn xây dựng hệ thống thumbnail bằng S3/Lambda/DynamoDB/Pillow; hỗ trợ code, web, kiểm thử và cấu hình từng bước để sinh viên thực hiện trên máy và AWS Academy.
- **AI hỗ trợ:** Mã nguồn và hướng dẫn cấu hình là phần được ChatGPT hỗ trợ chủ yếu; lần bổ sung hồ sơ có hỗ trợ rà soát repo và biên tập khai báo.
- **Sinh viên thực hiện:** Trực tiếp cấu hình môi trường thật, đối chiếu giá trị tài nguyên, áp dụng/hoàn thiện mã theo yêu cầu và kiểm tra kết quả. Trách nhiệm từng thành viên theo phân công repo; không khai mã có AI hỗ trợ là hoàn toàn tự viết.

Minh chứng cấu hình: [commit khôi phục ảnh](https://github.com/bndt0103/aws-thumbnail/commit/10b9d9898afbf21da8adf8e0b6dd2735377caee6), [danh mục ảnh](https://github.com/bndt0103/aws-thumbnail/blob/10b9d9898afbf21da8adf8e0b6dd2735377caee6/evidence/tuan-1/README.md), [CSV gốc](https://github.com/bndt0103/aws-thumbnail/blob/10b9d9898afbf21da8adf8e0b6dd2735377caee6/evidence/tuan-1/DANH_MUC_MINH_CHUNG.csv).

Minh chứng mã: [Pillow — 1c41d75](https://github.com/bndt0103/aws-thumbnail/commit/1c41d751d490f3493a5ba7d2e87df52ba40966ca), [worker — e50cb0c](https://github.com/bndt0103/aws-thumbnail/commit/e50cb0c19bfa43d8dafe2d9b67bbe24e82343dc9), [cấu hình — 213b093](https://github.com/bndt0103/aws-thumbnail/commit/213b09383c10cc6ea84c203ebd86ae7b4951e1b4), [web — 9b0aca9](https://github.com/bndt0103/aws-thumbnail/commit/9b0aca9be588f0f496a228b456741a8b9bfc7c80).

Minh chứng kiểm thử: [ảnh — 30838ce](https://github.com/bndt0103/aws-thumbnail/commit/30838ce3994c9d3e83d65fd40cef4bd047ee7b17), [worker — f3e62ba](https://github.com/bndt0103/aws-thumbnail/commit/f3e62ba4a663a9d6cdd46d500ce0a2ab2fcf6ec9), [Flask — c4fa1ad](https://github.com/bndt0103/aws-thumbnail/commit/c4fa1adae7f7a51c4a08bbf24bca7e905060d0da), [workflow — be74109](https://github.com/bndt0103/aws-thumbnail/commit/be7410979679823718063dd9a78bfcefecae44c8), [CI 19/19](https://github.com/bndt0103/aws-thumbnail/actions/runs/38563088053).

## Google Gemini

- **Model:** Không ghi nhận chính xác phiên bản.
- **Prompt (tóm lược):** Xem/tóm lược lịch sử commit, kiểm tra phân công và commit đã phù hợp chưa, hướng dẫn push GitHub và trình bày file Markdown để nộp tuần 1.
- **AI hỗ trợ:** Hướng dẫn rà soát commit, thao tác Git/push và bố cục Markdown.
- **Sinh viên thực hiện:** Đối chiếu tệp với commit, thống nhất nội dung đúng phạm vi tuần 1, ghi đầy đủ link và cập nhật hồ sơ. Không gán cho Gemini việc sinh code/test khi phạm vi thực tế nhóm xác nhận là rà soát commit và tài liệu.

## Cách hiểu minh chứng

24 ảnh được khôi phục nguyên tệp từ bản lưu cục bộ của nhóm; 17 ảnh khớp SHA-256 với ảnh nhúng trong báo cáo. Commit khôi phục không phải ngày chụp/ngày tạo tài nguyên. Danh mục không tự điền thời gian và người chụp chưa được xác nhận.

Các commit mã nguồn chủ yếu là commit thêm file, dùng để xác định phiên bản hoàn thiện và trách nhiệm được ghi nhận. Repo không lưu riêng bản nháp AI để làm diff trước–sau; không dùng link Git để khẳng định từng dòng do ai viết. Prompt trên là bản tóm lược theo xác nhận của nhóm, không giả định là bản chép nguyên văn hội thoại.

Tuần 1 có tài nguyên AWS và 19 ca kiểm thử với AWS giả lập. Chưa hoàn tất trigger S3/Lambda và kiểm thử end-to-end trên AWS; ảnh bucket output/DynamoDB rỗng phản ánh đúng trạng thái đó. Claude không nằm trong bản kê khai đã xác nhận này.
