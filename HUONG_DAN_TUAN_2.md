# HƯỚNG DẪN TUẦN 2 — TÍCH HỢP LAMBDA, S3 VÀ GALLERY CỤC BỘ

> Phạm vi: hoàn thiện luồng xử lý ảnh chạy thật trên AWS và kết nối gallery Flask chạy trên máy phát triển. Tuần này chưa triển khai gallery lên EC2; đó là đầu việc tuần 3.

Trạng thái ngày 18/10/2026: nhóm chưa bắt đầu triển khai tuần 2. Hướng dẫn đã đối chiếu với repo hiện tại và kế hoạch ở thư mục cũ trong Downloads. Báo cáo Word đi kèm là bản chuẩn bị, chưa phải báo cáo kết quả hoàn thành.

Các phần kế thừa đúng: hai bucket riêng tư, DynamoDB khóa image_id không có sort key, Python 3.12/x86_64, LabRole và Layer phiên bản 1, đầu ra 150/400/1000 pixel. Không cần chép lại toàn bộ thư mục cũ; các script hỗ trợ trong đó không có trong repo hiện tại. Mục 5 dùng trực tiếp Flask; mục 6 hướng dẫn tạo test event trên Console. Báo cáo, ảnh, nhật ký AI và commit được tách riêng cho tuần 2.

## 1. Mục tiêu và trạng thái đầu vào

Cuối tuần 2, nhóm cần chứng minh một ảnh được tải vào `uploads/` của bucket input sẽ kích hoạt Lambda, tạo ba ảnh JPEG có watermark, ghi metadata `COMPLETE` vào DynamoDB và xuất hiện trong gallery chạy cục bộ. Cần có ảnh Console/log/thử nghiệm thật cho từng mắt xích; kết quả pytest dùng mock không thay thế được minh chứng AWS.

Repo `bndt0103/aws-thumbnail` trên nhánh `main` tại snapshot `92d3812` đã có mã worker, xử lý ảnh, Flask, mẫu ảnh và 19 kiểm thử cục bộ. Báo cáo tuần 1 ghi nhận các tài nguyên nền: hai bucket S3, bảng `cloud-photo-metadata`, Pillow Layer v1; chưa có minh chứng luồng Lambda nhận trigger và xử lý end-to-end. Repo không có sẵn các script `make_web_config.py`, `run_local_web.py`, `make_test_event.py`, `capture_context.py` hoặc `export_results.py` được nhắc trong một số tài liệu nguồn. Hướng dẫn này chỉ dùng tệp và lệnh đang có trong repo, trừ khi nêu rõ thao tác Console.

Trước khi bắt đầu, đọc `README.md`, `config/aws-resources.json`, `src/processor/lambda_function.py`, `src/processor/image_tools.py`, `src/web/app.py` và hướng dẫn này. Xác minh trạng thái hiện tại trên AWS Console; file cấu hình trong repo là sổ ghi nhận, không thay cho việc kiểm tra tài nguyên thật. Không reset lịch sử, force-push hay chạy lại các lệnh khởi tạo Git từ tài liệu tuần 1.

### Phân công và kế hoạch giờ

| Thành viên | Công việc tuần 2 | Giờ kế hoạch |
|---|---|---:|
| Bùi Nguyễn Duy Trung (SV A) | Đóng gói worker; cấu hình Lambda và trigger; xác minh metadata, retry/idempotency; ghi worklog | 3 + 2 + 2 + 1 = 8 giờ |
| Đỗ Anh Tuấn (SV B) | Chạy gallery cục bộ với AWS; xác minh upload/trạng thái; thực hiện ca kiểm thử; ghi worklog | 3 + 2 + 2 + 1 = 8 giờ |

Đây là giờ kế hoạch theo phân công, không phải giờ đã làm. Mỗi người ghi ngày, nhiệm vụ, thời gian thực tế, kết quả, mã minh chứng và commit sau từng buổi. Nếu công việc chia sẻ, ghi người thực hiện/cùng thực hiện; không sao chép giờ giữa thành viên.

## 2. Chuẩn bị trước khi cấu hình

1. Khởi động AWS Academy Learner Lab và chờ trạng thái chạy. Mở Console tại Region `us-east-1` (N. Virginia). Chụp ảnh môi trường nếu cần nhưng không mở hoặc chụp AWS Details/credentials.
2. Trong S3, kiểm tra bucket input `cloudphoto-input-103308504802`, bucket output `cloudphoto-output-103308504802`, cấu hình private và tiền tố `uploads/`. Xác nhận hai bucket khác nhau.
3. Trong DynamoDB, kiểm tra bảng `cloud-photo-metadata`, trạng thái Active, partition key `image_id` kiểu String và cùng Region.
4. Trong Lambda > Layers, kiểm tra `cloud-photo-pillow` phiên bản 1, runtime Python 3.12, kiến trúc x86_64.
5. Trong IAM, xác nhận role lab có sẵn `LabRole`. Không tạo role mới, không chỉnh policy dùng chung và không đưa access key vào hàm. Nếu tên/Region/tài khoản đang chạy khác cấu hình, dừng trước khi tạo tài nguyên trùng và cập nhật sổ tài nguyên sau khi nhóm thống nhất.
6. Kiểm tra quyền của `LabRole` cho S3 input/output, DynamoDB và CloudWatch Logs. Nếu thiếu quyền, lưu lại lỗi và hỏi quản lý lab/GVHD; không tự gắn policy rộng như `AdministratorAccess`.

Giá trị AWS Academy là tạm thời. Không commit, gửi qua chat, đưa vào ảnh chụp, `.env`, mã nguồn, biến môi trường Lambda hoặc báo cáo. Credential cục bộ chỉ được đặt tạm trong tiến trình Flask theo mục 5.

## 3. Đóng gói và triển khai Lambda worker

### 3.1 Tạo ZIP mã Lambda

Mở PowerShell tại gốc repo `aws-thumbnail`. Dùng Python 3.12 đã có trong môi trường nhóm:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe scripts\build_packages.py --skip-layer
```

Tùy chọn `--skip-layer` chỉ đóng gói worker, không tạo lại Pillow Layer đã có. Gói cần tải lên là `dist/lambda_processor.zip`; ZIP phải có `lambda_function.py` và `image_tools.py` ở thư mục gốc. Kiểm tra nội dung trước khi tải:

```powershell
py -3.12 -c "import zipfile; z=zipfile.ZipFile('dist/lambda_processor.zip'); print('\n'.join(z.namelist()))"
```

`dist/` bị Git ignore. Không cần commit ZIP; nếu hệ thống nộp bài yêu cầu artifact thì nộp riêng theo kênh được chỉ định.

### 3.2 Tạo hoặc cập nhật hàm

Trong AWS Console > Lambda, trước tiên tìm `cloud-photo-processor`. Nếu đã có hàm thì kiểm tra và cập nhật đúng hàm đó; nếu chưa có thì tạo:

- Function name: `cloud-photo-processor`.
- Runtime: Python 3.12; Architecture: x86_64.
- Execution role: `LabRole` có sẵn trong Learner Lab.
- Handler: `lambda_function.lambda_handler`.
- Upload `dist/lambda_processor.zip` trong mục Code; kiểm tra Deploy hoàn tất.
- Gắn layer `cloud-photo-pillow`, version 1.
- General configuration: Memory 1024 MB, Timeout 60 seconds, Ephemeral storage 512 MB.
- Environment variables:

| Tên | Giá trị |
|---|---|
| `INPUT_BUCKET` | `cloudphoto-input-103308504802` |
| `OUTPUT_BUCKET` | `cloudphoto-output-103308504802` |
| `TABLE_NAME` | `cloud-photo-metadata` |
| `WATERMARK_TEXT` | `CLOUD PHOTO` |

Không đặt `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN` hay `AWS_REGION` trong cấu hình Lambda. SDK của Lambda lấy quyền từ execution role. Để function không ở VPC nếu đề tài chưa yêu cầu VPC. Không bật provisioned concurrency. Giữ cơ chế retry bất đồng bộ mặc định; nếu giao diện Console hiện cấu hình retry, ghi lại giá trị thay vì tự ý thay đổi.

Tại CloudWatch Logs, sau lần invoke đầu tiên sẽ có log group `/aws/lambda/cloud-photo-processor`. Đặt retention 7 ngày và gắn tag theo quy ước dự án khi Console cho phép. Ảnh E08a/E08b cần cho thấy đúng runtime/handler/layer/cấu hình, không để lộ credentials.

## 4. Gắn trigger S3 và xác minh worker

### 4.1 Cấu hình nguồn sự kiện

Trong Lambda > `cloud-photo-processor` > Add trigger:

1. Source: S3; chọn bucket `cloudphoto-input-103308504802`.
2. Event type: `All object create events` (`s3:ObjectCreated:*`).
3. Prefix: `uploads/`; để trống suffix.
4. Xác nhận cảnh báo recursive invocation rồi thêm trigger.
5. Trong Lambda Configuration > Triggers và S3 bucket notification, kiểm tra chỉ bucket input có trigger tới hàm và Lambda có resource-based permission cho S3. Không thêm trigger cho bucket output.

Bucket đầu ra riêng biệt và bộ lọc `uploads/` tránh việc ảnh `thumbnails/...` kích hoạt lại worker. AWS cũng cảnh báo về vòng lặp khi output ghi vào chính bucket gọi hàm; xem [AWS Lambda: S3 trigger tutorial](https://docs.aws.amazon.com/lambda/latest/dg/with-s3-example.html) và [S3 key filters](https://docs.aws.amazon.com/AmazonS3/latest/userguide/notification-how-to-filtering.html).

### 4.2 Chạy một ảnh thật

1. Tải `tests/samples/landscape.jpg` lên bucket input với key duy nhất, ví dụ `uploads/w2-smoke/landscape-YYYYMMDD-HHMM.jpg`. Thay timestamp bằng thời điểm thực; không dùng lại key đang được thử nghiệm khác.
2. Trong Lambda > Monitor > View CloudWatch logs, mở log stream mới nhất. Chờ dòng JSON `COMPLETE` và dòng `REPORT` của invocation. Nếu có lỗi, ghi lại exception và xử lý trước khi kết luận.
3. Trong output bucket, tìm `thumbnails/<image_id>/150.jpg`, `400.jpg` và `1000.jpg`. Mã `image_id` có trong log và item DynamoDB. Xác nhận object là JPEG, có watermark, metadata server-side encryption AES256.
4. Trong bảng DynamoDB, tìm item đúng `image_id`. Với ảnh hợp lệ, mong đợi `status=COMPLETE`, `source_bucket`, `source_key`, `original`, ba phần tử `variants`, `output_bucket`, `watermark`, `completed_at` và `processing_ms`.
5. Chụp minh chứng E10–E14; giữ Account/Region/thời gian có thể đối chiếu, không chụp credential. Log `REPORT Duration` không đồng nghĩa thời gian từ lúc người dùng bấm upload đến lúc gallery cập nhật.

Kết quả kỳ vọng của worker trong mã hiện tại:

- Đầu vào hợp lệ: ba key `thumbnails/<image_id>/<150|400|1000>.jpg`, trạng thái `COMPLETE`.
- JPG/PNG sai hoặc ảnh vượt giới hạn xử lý: item `REJECTED`; đây là từ chối có kiểm soát, không được gọi là retry thành công.
- Lỗi dịch vụ như đọc/ghi S3 hoặc DynamoDB: log `FAILED`, item có thể được ghi trạng thái `FAILED`, lỗi được ném lại để Lambda retry. Số lần retry và kết quả phải lấy từ cấu hình/log thật.
- Sự kiện trùng cùng một revision sau khi hoàn tất: trả `DUPLICATE`, log `DUPLICATE_SKIPPED`, không tạo thêm bộ object.

Không khẳng định retry khôi phục mọi trường hợp. Timeout hoặc lỗi giữa lúc ghi ba object có thể để lại trạng thái/bản ghi cần điều tra thủ công.

## 5. Chạy gallery Flask cục bộ kết nối AWS

Repo không có script tạo cấu hình web tự động. Chạy ứng dụng trực tiếp từ PowerShell và giữ credential trong đúng cửa sổ tiến trình.

### 5.1 Cài đặt biến môi trường tạm

Nếu chưa cài dependency trong môi trường ảo, lệnh ở mục 3.1 đã cài `requirements-dev.txt`. Trong cùng cửa sổ PowerShell:

```powershell
$env:INPUT_BUCKET = 'cloudphoto-input-103308504802'
$env:OUTPUT_BUCKET = 'cloudphoto-output-103308504802'
$env:TABLE_NAME = 'cloud-photo-metadata'
$env:AWS_DEFAULT_REGION = 'us-east-1'

$rng = [Security.Cryptography.RandomNumberGenerator]::Create()
$bytes = New-Object byte[] 32
$rng.GetBytes($bytes)
$env:APP_SECRET = [Convert]::ToBase64String($bytes)
$rng.Dispose()

$env:GALLERY_PASSWORD_HASH = (& .\.venv\Scripts\python.exe -c "from getpass import getpass; from werkzeug.security import generate_password_hash; print(generate_password_hash(getpass('Mật khẩu gallery: ')))")
```

Lệnh cuối nhập mật khẩu mà không hiển thị; hash chỉ tồn tại trong biến của tiến trình hiện tại. Chọn một mật khẩu demo không dùng ở nơi khác.

Nhập ba credential tạm của Lab bằng prompt ẩn, không dán chúng vào một dòng lệnh:

```powershell
function Set-TemporaryAwsCredential([string]$Name) {
    $secure = Read-Host $Name -AsSecureString
    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try {
        [Environment]::SetEnvironmentVariable($Name, [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer), 'Process')
    } finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    }
}
Set-TemporaryAwsCredential 'AWS_ACCESS_KEY_ID'
Set-TemporaryAwsCredential 'AWS_SECRET_ACCESS_KEY'
Set-TemporaryAwsCredential 'AWS_SESSION_TOKEN'
```

Các biến này chỉ ở process PowerShell; không ghi ra file và không chụp cửa sổ prompt. Hết buổi, đóng cửa sổ PowerShell để xóa biến khỏi process. Khi session Learner Lab hết hạn, khởi động Lab và nhập credential mới.

### 5.2 Mở và kiểm tra gallery

Tại gốc repo, chạy:

```powershell
.\.venv\Scripts\python.exe src\web\app.py
```

Mở `http://127.0.0.1:5000`, đăng nhập bằng mật khẩu demo đã chọn. Gallery chạy trên máy cục bộ, nhưng gọi S3/DynamoDB AWS thật qua Boto3 credential chain. Flask bind vào `127.0.0.1`, không mở ra Internet. Tải một ảnh mẫu qua web, đợi worker hoàn tất rồi làm mới gallery. Gallery đọc DynamoDB và cấp URL ký sẵn 300 giây cho thumbnail; không xử lý ảnh trong trình duyệt.

Ảnh W2-L01 cần thể hiện gallery sau khi một ảnh thật đã thành `COMPLETE`; ảnh W2-L02 có thể ghi nhận trạng thái `REJECTED`/lỗi hoặc phản hồi 401/403 khi thử đúng ca bảo mật. Không để lộ password, session token hay URL ký sẵn còn hiệu lực trong ảnh/video chia sẻ.

## 6. Ma trận kiểm tra tuần 2

Mỗi lần thử ghi: ID, ngày/giờ UTC+7, commit, key đầu vào, `image_id`, kết quả quan sát, mã ảnh/log, Pass/Fail/Chưa thử và lỗi. Không điền Pass trước khi chạy thật.

| ID | Thử nghiệm | Tiêu chí cần đối chiếu |
|---|---|---|
| T01 | Upload `landscape.jpg` qua gallery | `COMPLETE`; ba JPEG có watermark; giữ tỷ lệ |
| T02 | Upload `portrait.jpg` | Ảnh dọc, không méo; ba variant được ghi |
| T03 | Upload `square.png` | Ảnh vuông; ba variant được ghi |
| T04 | Upload `transparent.png` | Vùng trong suốt thành nền trắng; output JPEG |
| T05 | Upload `small.png` | Không phóng to; kích thước output thực có thể giống nhau |
| T06 | Upload `broken.jpg` | `REJECTED`, metadata lỗi phù hợp, không có variant thành công |
| T07 | Upload ảnh hợp lệ lớn hơn 10 MiB qua gallery | Web chặn và trả lỗi kích thước; thử S3 trực tiếp chỉ khi cần xác minh worker từ chối file quá lớn |
| T08 | Chạy hai lần cùng một JSON event Lambda | Lần hai trả `DUPLICATE`; log `DUPLICATE_SKIPPED`; không tăng object do lần lặp |
| T09 | Ghi object thử nghiệm vào bucket output | Không có invocation mới do output object |
| T10 | Upload hai lần cùng tên file qua gallery | Hai key UUID khác nhau, hai item/kết quả độc lập |
| T11 | Logout, gọi `/api/photos` | HTTP 401 |
| T12 | Gửi POST thiếu CSRF token | HTTP 403; không phát sinh upload |

### Cách chạy kiểm thử duplicate T08

Chọn object đã xử lý và ghi lại bucket, key, eTag cùng một revision. Tạo JSON Test event trong Lambda Console với `eventSource: "aws:s3"`, `eventName: "ObjectCreated:Put"`, đúng bucket, key đã URL-encode và eTag thật. Có thể dùng sequencer cố định để sự kiện mô phỏng có ID ổn định. Chạy JSON một lần, lưu `image_id`/log; chạy lại chính xác JSON đó lần hai và kiểm tra `DUPLICATE_SKIPPED`.

ID tạo từ JSON thử tay có thể khác ID từ sự kiện S3 tự phát nếu revision khác. Vì vậy chỉ so sánh hai lần chạy cùng JSON; không cộng bản ghi thử tay vào kết quả upload thật và không coi khác ID là lỗi của test duplicate.

`T07` qua gallery được endpoint Flask chặn trước khi gửi lên S3: tệp vượt 10 MiB trả HTTP 400 nếu request chưa vượt giới hạn 11 MiB; request lớn hơn 11 MiB trả HTTP 413. Không ghi nhận có invocation Lambda cho lần bị web từ chối. Nếu thử upload trực tiếp S3 để xác minh worker, dùng ảnh không nhạy cảm, key riêng; worker mới là nơi kiểm tra giới hạn 10 MiB ở đường đi này. Không thử bằng cách chỉnh quyền hoặc làm hỏng tài nguyên chung. `T09` cần đối chiếu cấu hình trigger, log/metrics trong khoảng thời gian quan sát được ghi lại; không suy ra “không có invocation” chỉ từ một lần refresh.

Các ca T13–T16 (URL private/hết hạn, khởi động lại gallery, kiểm tra tag/cấu hình sâu) có thể bổ sung nếu thời gian cho phép; bài trình diễn EC2 thuộc tuần 3. Chạy pytest cục bộ nếu lịch phân công yêu cầu, nhưng ghi riêng là mock/local test. Không thay kết quả đó cho T01–T10 AWS.

## 7. Bộ ảnh minh chứng và vị trí lưu

Đặt tên ảnh `MÃ_mô-tả_YYYYMMDD-HHMM.png` theo giờ Việt Nam, ví dụ `E09_s3-trigger_20261017-1430.png`. Mỗi ảnh chỉ chứng minh điều thấy được trên màn hình; ghi chú riêng thời gian, Region, Account ID đã che/ghi nhận an toàn và commit đang chạy. Không chỉnh sửa nội dung để làm cho kết quả đẹp hơn.

| Mã | Nội dung cần chụp | Dùng trong báo cáo |
|---|---|---|
| E07 | Function dùng execution role `LabRole` | Bảo mật/role |
| E08a | Runtime, architecture, handler, layer | Cấu hình worker |
| E08b | Memory, timeout, ephemeral storage, tên biến môi trường (ẩn giá trị nhạy cảm) | Cấu hình worker |
| E09 | S3 trigger đúng bucket input, `ObjectCreated:*`, prefix `uploads/`; permission invoke | Kích hoạt |
| E10 | Object ảnh gốc được tải vào key `uploads/...` | Đầu vào |
| E11 | Ba key thumbnail cùng `image_id` trong bucket output | Đầu ra |
| E12 | Ba ảnh JPEG thật, watermark và thông số chiều rộng/cao | Chất lượng ảnh |
| E13 | Item DynamoDB trạng thái `COMPLETE`, original/variants/processing_ms | Metadata |
| E14 | Log `COMPLETE` và `REPORT` duration/memory | Theo dõi |
| E15 | Lambda Invocations/Errors/Duration quanh thời gian thử | Chỉ số |
| E19 | Lần gọi lặp với log `DUPLICATE_SKIPPED` | Idempotency |
| W2-L01 | Flask cục bộ hiển thị ảnh vừa xử lý thật | Gallery |
| W2-L02 | Một trạng thái lỗi/từ chối hoặc phản hồi kiểm soát truy cập thật | Kiểm tra lỗi/bảo mật |

Không cần chụp tất cả ảnh trong một khung nếu chữ khó đọc. Một mã có thể có ảnh tổng quan và ảnh chi tiết. Nếu chưa chạy được ca nào, để trạng thái Chưa thử và ghi lý do; không dùng ảnh tuần 1 để giả làm minh chứng tuần 2. Mã E16/E17 thuộc gallery trên EC2 tuần 3.

## 8. Cập nhật repo và báo cáo

Sau khi có kết quả thật:

1. Giữ `config/aws-resources.json` làm mốc cấu hình tuần 1. Ghi cấu hình Lambda, trigger và log group đã kiểm tra vào `progress/week-2/trung-aws.md`; chỉ bổ sung cấu hình máy đọc được khi có dữ liệu thật. Không sửa `stage` thành tuần 2 để ngụ ý đã triển khai.
2. Ghi kết quả T01–T12, actual worklog của từng người, issue và cách khắc phục. Nếu chưa có tệp CSV trong clone, không khai báo đã tạo/chạy `scripts/export_results.py`; tạo bảng theo mẫu trong báo cáo hoặc bổ sung script riêng có commit.
3. Lưu ảnh gốc và cập nhật `evidence/tuan-2/DANH_MUC_MINH_CHUNG.csv`. Script `scripts/build_week2_report.py` chèn ảnh đã có trực tiếp vào phần tương ứng của báo cáo, căn giữa và giới hạn kích thước theo khổ trang. Chạy lại script sau khi cập nhật ảnh và các bảng kết quả; không đổi tên ảnh tuần 1 thành ảnh tuần 2.
4. Khai báo đúng công cụ AI đã dùng tuần 2, phần được hỗ trợ, phần nhóm tự sửa và cách kiểm chứng. Không sao chép nguyên tuyên bố AI tuần 1 nếu tuần 2 khác.
5. Trước commit chạy `git status --short`, kiểm tra không có `.env`, credential, file key, ảnh cá nhân hoặc token. Commit hướng dẫn/báo cáo và mã nguồn theo phạm vi được nhóm thống nhất; không commit artifact ZIP hoặc bí mật.

## 9. Tiêu chí hoàn tất tuần 2

- Lambda `cloud-photo-processor` dùng Python 3.12, `LabRole`, Pillow Layer v1 và cấu hình đã đối chiếu.
- Trigger chỉ theo dõi bucket input và tiền tố `uploads/`; không có trigger lên output.
- Ít nhất một ảnh hợp lệ đã đi qua S3 → Lambda → ba thumbnail → DynamoDB và được kiểm tra trong CloudWatch.
- Flask chạy tại `127.0.0.1:5000`, đọc metadata/URL từ AWS thật và hiện kết quả upload; không xử lý thumbnail cục bộ.
- Các ca đã chạy có kết quả và minh chứng thật; ca chưa chạy được ghi rõ. Mock test và AWS integration được tách bạch.
- Worklog actual hours, tài nguyên và khai báo AI được cập nhật theo thực tế; không biến giờ kế hoạch thành giờ đã làm.

Tuần 2 đạt mốc “core flow chạy thật” khi có minh chứng end-to-end; EC2/tunnel và triển khai gallery trên AWS để dành cho tuần 3.

## 10. Trình tự riêng cho từng thành viên

### Bùi Nguyễn Duy Trung — Lambda, trigger và dữ liệu AWS

1. Thực hiện mục 2, 3 và 4 theo đúng thứ tự; dùng lại tài nguyên tuần 1. Chỉ chuyển sang thử ảnh khi runtime, handler, layer và bốn biến cấu hình đã đúng.
2. Chụp cấu hình role/worker/trigger; thử một ảnh từ S3 Console. Đối chiếu cùng `image_id` trong output S3, DynamoDB và CloudWatch.
3. Phụ trách thử T08 (duplicate) và T09 (không kích hoạt từ output), phối hợp với Tuấn chạy T01–T06 từ gallery.
4. Ghi cấu hình và kết quả vào `progress/week-2/trung-aws.md`; ghi thời gian thực tế vào `trung-worklog.csv`; ghi AI hỗ trợ và phần đã kiểm tra vào `trung-ai.md` cùng thư mục.
5. Lưu ảnh do mình chụp trong `evidence/tuan-2/trung/`. Báo cho Tuấn đường dẫn, ngày chụp và test ID để cập nhật danh mục ảnh chung. Chỉ commit cấu hình/kết quả đã kiểm tra; không đổi tác giả commit của người khác.

### Đỗ Anh Tuấn — Gallery, kiểm thử và tổng hợp báo cáo

1. Chờ Trung xác nhận thử ảnh từ S3 đã thành công, sau đó làm mục 5 để chạy Flask tại máy mình. Nếu mỗi người dùng lab khác nhau thì dùng đúng tài nguyên của lab đó, không chia sẻ tài khoản hoặc credential qua Git/chat.
2. Chạy T01–T07 và T10–T12; với ca AWS, ghi key, `image_id`, trạng thái và ảnh/log thực tế. Không dùng kết quả mock 19/19 để điền Pass cho các ca tích hợp.
3. Ghi cấu hình không bí mật và kết quả vào `progress/week-2/tuan-gallery.md`; cập nhật `test-results.csv`, `tuan-worklog.csv` và `tuan-ai.md`.
4. Lưu ảnh trong `evidence/tuan-2/tuan/`, tổng hợp danh mục ảnh từ cả hai người. Ảnh minh chứng có nội dung trùng nhau chỉ cần chọn bản rõ nhất cho báo cáo.
5. Cập nhật `progress/week-2/report-status.json` theo kết quả, rồi chạy:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements-report.txt
   .\.venv\Scripts\python.exe scripts/build_week2_report.py
   ```

   Mở Word, cập nhật mục lục nếu cần và kiểm tra ảnh/chú thích. Báo cáo tuần 1 được giữ riêng. Chỉ đổi trạng thái báo cáo khỏi bản chuẩn bị khi đã ghi kết quả thật; các ca còn thiếu vẫn phải ghi rõ.

### Mốc hoàn thành và bàn giao

| Mốc | Người chính | Điều kiện bàn giao |
|---|---|---|
| A | Trung | Lambda chạy một ảnh từ S3, có output, item COMPLETE và log |
| B | Tuấn | Gallery upload ảnh lên AWS và hiển thị kết quả thật |
| C | Cả hai | Các ca đã thử có dòng kết quả, ảnh/log, giờ thực tế và commit |
| D | Tuấn tổng hợp, Trung rà soát | Word tuần 2 và nội dung nộp khớp với kết quả/commit trên main |

## 11. Commit và push bằng tài khoản của từng thành viên

Mỗi người làm trên clone của mình, tốt nhất trên máy riêng. Commit ghi đúng người thực hiện và thời điểm hiện tại. Không sửa ngày, đổi tác giả commit cũ hoặc tạo commit thay cho công việc chưa làm. Các tệp đang chuẩn bị trong bộ hướng dẫn chưa phải minh chứng đã cấu hình AWS.

### 11.1 Chuẩn bị clone và danh tính

Nếu đã có clone thì không clone đè. Kiểm tra `git status --short`, lưu/commit thay đổi đang làm trước khi chuyển nhánh. Trong mỗi clone sạch:

```powershell
git remote -v
git switch main
git pull --ff-only origin main
git config --local user.name "HO_TEN_NGUOI_DANG_LAM"
git config --local user.email "EMAIL_DA_XAC_MINH_TREN_GITHUB"
git var GIT_AUTHOR_IDENT
```

Trung điền tên `Bùi Nguyễn Duy Trung`, dùng tài khoản GitHub `bndt0103`; Tuấn điền tên `Đỗ Anh Tuấn`, dùng `DoAnhTuan-24110369`. Email phải là email được xác minh hoặc email noreply trong GitHub Settings của chính người đó. Khi push, đăng nhập đúng tài khoản; `user.name` không đổi tài khoản đăng nhập GitHub. Chủ repo mời Tuấn trong Settings → Collaborators nếu chưa có quyền ghi.

### 11.2 Trung đưa phần AWS lên nhánh riêng

```powershell
git switch -c tuan-2/trung-lambda
# Thực hiện cấu hình, ghi kết quả, lưu ảnh rồi mới stage.
git add progress/week-2/trung-aws.md progress/week-2/trung-worklog.csv progress/week-2/trung-ai.md
git add evidence/tuan-2/trung/
git diff --cached --stat
git diff --cached --check
git commit -m "Tuần 2: ghi nhận cấu hình Lambda, trigger S3 và kết quả xử lý ảnh"
git push -u origin tuan-2/trung-lambda
```

Lệnh thêm thư mục ảnh chỉ chạy khi đã có ảnh thật. Nếu sửa worker thì stage đúng tệp đã sửa, chạy lại pytest và ghi thêm một commit mô tả lỗi/cách sửa, ví dụ `Tuần 2: khắc phục lỗi đọc ảnh trong Lambda`. Không tạo thay đổi mã nguồn chỉ để có thêm commit.

Mở pull request từ `tuan-2/trung-lambda` vào `main`, nhờ Tuấn đối chiếu cấu hình và kết quả. Merge sau khi kiểm tra. Giữ các commit gốc của Trung khi hợp nhất.

### 11.3 Tuấn đưa gallery và kiểm thử lên nhánh riêng

Sau khi phần AWS của Trung đã vào main, Tuấn cập nhật clone sạch rồi làm:

```powershell
git switch main
git pull --ff-only origin main
git switch -c tuan-2/tuan-gallery
# Thực hiện gallery/kiểm thử và ghi kết quả trước khi stage.
git add progress/week-2/tuan-gallery.md progress/week-2/test-results.csv
git add progress/week-2/tuan-worklog.csv progress/week-2/tuan-ai.md
git add evidence/tuan-2/tuan/ evidence/tuan-2/DANH_MUC_MINH_CHUNG.csv
git diff --cached --stat
git diff --cached --check
git commit -m "Tuần 2: ghi nhận gallery kết nối AWS và kết quả kiểm thử tích hợp"
git push -u origin tuan-2/tuan-gallery
```

Mở pull request để Trung rà soát. Nếu có sửa Flask/kiểm thử, stage đúng tệp và chạy pytest trước commit; không đưa các sửa đổi không thuộc nhiệm vụ vào cùng commit.

### 11.4 Chốt minh chứng AI và báo cáo sau khi merge

Mỗi người lấy SHA thật bằng `git log --oneline --author="TEN_HOAC_EMAIL"` và mở commit trên GitHub. Với mỗi nhiệm vụ AI, ghi rõ công cụ đã dùng, prompt tóm lược, nội dung AI hỗ trợ, phần đã sửa/kiểm tra, link `https://github.com/bndt0103/aws-thumbnail/commit/SHA_THAT` và link `blob/SHA_THAT/duong/dan/tep#Lx-Ly`.

Link commit phải mở được trên GitHub, không chỉ tồn tại cục bộ. Không dùng commit tuần 1 để tuyên bố công việc triển khai tuần 2 đã hoàn tất. Các link mã nguồn tuần 1 chỉ là tài liệu kế thừa; commit tuần 2 phải chứa nhật ký/ảnh/kết quả hoặc sửa đổi thực tế của tuần 2.

Tuấn tổng hợp các link thật vào `KHAI_BAO_AI_TUAN2.md`, `BAO_CAO_NOP_BAI_TUAN2.md` và `progress/week-2/report-status.json`, chạy lại script tạo Word. Trên nhánh tổng hợp riêng, stage từng tệp rồi commit:

```powershell
git add Report/BaoCaoTuan2_24110363_24110369.docx
git add KHAI_BAO_AI_TUAN2.md BAO_CAO_NOP_BAI_TUAN2.md progress/week-2/report-status.json
git diff --cached --stat
git commit -m "Tuần 2: tổng hợp báo cáo, khai báo AI và liên kết minh chứng"
git push
```

Chỉ nộp khi main đã có các phần việc, link mở được và bản Word đúng kết quả đã thực hiện. Dùng `git add` theo tệp; không dùng `git add .` khi chưa kiểm tra toàn bộ thay đổi, đặc biệt tệp nộp tuần 1 đang sửa.

### 11.5 Đưa bộ chuẩn bị lên repo trước khi hai người bắt đầu

Bộ tài liệu được soạn ngày 18/10/2026 với AI hỗ trợ. Đây là một commit chuẩn bị chung, không chia thành hai commit giả lập phần việc của hai người. Người thực sự rà soát và đưa tài liệu lên repo dùng tài khoản của mình để tạo nhánh `tuan-2/chuan-bi`, stage đúng các tệp sau:

```powershell
git switch -c tuan-2/chuan-bi
git add HUONG_DAN_TUAN_2.md requirements-report.txt scripts/build_week2_report.py
git add progress/week-2/ evidence/tuan-2/README.md evidence/tuan-2/DANH_MUC_MINH_CHUNG.csv
git add KHAI_BAO_AI_TUAN2.md BAO_CAO_NOP_BAI_TUAN2.md
git add .gitignore Report/BaoCaoTuan2_24110363_24110369.docx
git diff --cached --stat
git diff --cached --check
git commit -m "Tuần 2: chuẩn bị hướng dẫn tích hợp, phân công và mẫu báo cáo"
git push -u origin tuan-2/chuan-bi
```

Rà soát pull request và merge main trước khi Trung/Tuấn tạo nhánh thực hiện. Bộ chuẩn bị không sửa hoặc commit tệp BAO_CAO_NOP_BAI.md của tuần 1 đang có thay đổi cục bộ.

### 11.6 Cập nhật dữ liệu đầu vào cho Word

- `test-results.csv`: mỗi ca cập nhật kết quả thực tế, trạng thái, ngày, người thực hiện, ảnh/log và SHA đã push.
- Hai tệp worklog: thêm dòng công việc thật, không dùng giờ kế hoạch làm giờ thực tế.
- `DANH_MUC_MINH_CHUNG.csv`: điền `file` tương đối, ví dụ `trung/lambda-trigger_20261018-1430.png`; thêm nhiều dòng cùng mã nếu cần. Cột caption dùng câu ngắn dễ hiểu, không chứa link bí mật.
- `report-status.json`: giữ `preparation` khi chưa triển khai; dùng `in_progress` khi đang làm và ghi rõ phần thiếu; chỉ dùng `completed` sau khi đối chiếu tiêu chí mục 9. Cập nhật `group_status`, `aws_summary`, `gallery_summary` và các mục AI theo thực tế.
- `week2_commits`: thêm mỗi nhiệm vụ một đối tượng có `member`, `task`, `url` (link commit thật) và `file_links` (danh sách đối tượng `label`, `url`). `ai_tools` ghi công cụ thực dùng, `student_changes`, `evidence_links`, `commit_links`; không thêm công cụ chưa dùng.

Đóng bản Word tuần 2 trước khi tạo lại. Script không tự kiểm chứng nội dung ảnh hay link GitHub. Khi chạy lại, script ghi đè Word từ dữ liệu; các sửa trực tiếp riêng trong Word cần đưa lại vào dữ liệu/script trước. Sau khi mở Word, bấm Ctrl+A rồi F9 để cập nhật mục lục và rà soát trước khi nộp.

## Tài liệu AWS tham khảo

- [Python runtimes for Lambda](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- [Tutorial: Using an Amazon S3 trigger to invoke Lambda](https://docs.aws.amazon.com/lambda/latest/dg/with-s3-example.html)
- [Filtering S3 event notifications by object key](https://docs.aws.amazon.com/AmazonS3/latest/userguide/notification-how-to-filtering.html)
- [Prevent recursive Lambda invocation loops](https://docs.aws.amazon.com/lambda/latest/dg/invocation-recursion.html)
