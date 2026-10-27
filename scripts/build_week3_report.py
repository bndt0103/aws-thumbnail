"""Build the Week 3 Word report (.docx) for the Cloud Computing final project.

Project: "Xử lý ảnh tự động: tạo thumbnail khi upload lên Amazon S3"
Students: Bùi Nguyễn Duy Trung (24110363), Đỗ Anh Tuấn (24110369)
Instructor: TS. Huỳnh Xuân Phụng
Run from the repository root: py -3.12 scripts/build_week3_report.py
"""

import csv
import os
from copy import deepcopy
from io import BytesIO
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence/tuan-3"
PROGRESS = ROOT / "progress/week-3"
TEMPLATE = ROOT / "Report/BaoCaoTuan1_24110363_24110369.docx"
OUTPUT = ROOT / "Report/BaoCaoTuan3_24110363_24110369.docx"
REPO = "https://github.com/bndt0103/aws-thumbnail"


def link(paragraph, label, url):
    """Add a clickable external hyperlink to a paragraph."""
    rel = paragraph.part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    element = OxmlElement("w:hyperlink")
    element.set(qn("r:id"), rel)
    run = OxmlElement("w:r")
    props = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "205493")
    props.append(color)
    run.append(props)
    text = OxmlElement("w:t")
    text.text = label
    run.append(text)
    element.append(run)
    paragraph._p.append(element)


def bookmark(paragraph, name, bookmark_id):
    """Insert a bookmark in a paragraph."""
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(bookmark_id))
    start.set(qn("w:name"), name)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(bookmark_id))
    paragraph._p.insert(0, start)
    paragraph._p.append(end)


def internal_link(paragraph, label, anchor):
    """Add an internal hyperlink jump within the Word document."""
    element = OxmlElement("w:hyperlink")
    element.set(qn("w:anchor"), anchor)
    run = OxmlElement("w:r")
    props = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "205493")
    props.append(color)
    run.append(props)
    value = OxmlElement("w:t")
    value.text = label
    run.append(value)
    element.append(run)
    paragraph._p.append(element)


def architecture():
    """Generate high-resolution architecture diagram for Week 3 using Pillow."""
    canvas = Image.new("RGB", (1600, 960), "white")
    draw = ImageDraw.Draw(canvas)
    font_path = Path("C:/Windows/Fonts/arial.ttf")
    font_title = ImageFont.truetype(str(font_path), 24) if font_path.exists() else ImageFont.load_default(size=24)
    font_body = ImageFont.truetype(str(font_path), 18) if font_path.exists() else ImageFont.load_default(size=18)
    font_label = ImageFont.truetype(str(font_path), 17) if font_path.exists() else ImageFont.load_default(size=17)
    font_tag = ImageFont.truetype(str(font_path), 16) if font_path.exists() else ImageFont.load_default(size=16)

    boxes = {
        "client": {
            "rect": (50, 70, 430, 240),
            "title": "Người dùng / Trình duyệt",
            "lines": ["Giao diện Web Gallery", "SSH Tunnel localhost:8080", "Xác thực phiên bảo vệ"],
            "fill": "#F0F4F8",
            "border": "#1A365D",
        },
        "ec2": {
            "rect": (50, 370, 430, 660),
            "title": "Amazon EC2 (t2.micro)",
            "lines": [
                "Instance: cloud-photo-gallery",
                "Amazon Linux 2023 · us-east-1d",
                "Gunicorn 26.2.0 · Systemd Service",
                "Cổng nội bộ 8000 · Python 3.12",
                "IAM Role: LabInstanceProfile",
                "(IMDSv2 · Không lưu Access Key)",
            ],
            "fill": "#EBF8FF",
            "border": "#2B6CB0",
        },
        "s3_in": {
            "rect": (590, 70, 1010, 240),
            "title": "S3 Input Bucket",
            "lines": [
                "cloudphoto-input-103308504802",
                "Tiền tố: uploads/<image_id>/",
                "Sự kiện: s3:ObjectCreated:*",
                "Chặn truy cập công khai",
            ],
            "fill": "#FEEBC8",
            "border": "#C05621",
        },
        "lambda": {
            "rect": (590, 370, 1010, 660),
            "title": "AWS Lambda (Serverless)",
            "lines": [
                "cloud-photo-processor",
                "Python 3.12 · x86_64 · 1024 MB",
                "Role thực thi: LabRole",
                "Layer: cloud-photo-pillow (v1)",
                "Gói code deploy: chỉ 3.7 kB",
                "Tạo 3 kích thước: 150, 400, 1000px",
            ],
            "fill": "#FEFCBF",
            "border": "#B7791F",
        },
        "s3_out": {
            "rect": (1170, 70, 1550, 330),
            "title": "S3 Output Bucket (Private)",
            "lines": [
                "cloudphoto-output-103308504802",
                "Tiền tố: thumbnails/<image_id>/",
                "Chặn link trực tiếp: HTTP 403",
                "Presigned URL có hạn 300 giây",
                "Lifecycle Rule: auto-cleanup-7days",
                "(Tự xóa thumbnail cũ sau 7 ngày)",
            ],
            "fill": "#C6F6D5",
            "border": "#22543D",
        },
        "dynamodb": {
            "rect": (1170, 420, 1550, 660),
            "title": "Amazon DynamoDB",
            "lines": [
                "Bảng: cloud-photo-metadata",
                "Khóa phân vùng: image_id (String)",
                "Lưu metadata, kích thước & trạng thái",
                "Chế độ On-demand Capacity",
                "Trạng thái: COMPLETE / FAILED",
            ],
            "fill": "#E9D8FD",
            "border": "#553C9A",
        },
        "cloudwatch": {
            "rect": (590, 750, 1010, 910),
            "title": "Amazon CloudWatch Logs & Metrics",
            "lines": [
                "Nhóm nhật ký: /aws/lambda/cloud-photo-processor",
                "Ghi nhận: Duration, Billed Duration, Memory Used",
                "Lưu trữ audit log: COMPLETE, DUPLICATE_SKIPPED",
            ],
            "fill": "#EDF2F7",
            "border": "#4A5568",
        },
    }

    for b in boxes.values():
        rect = b["rect"]
        draw.rounded_rectangle(rect, radius=14, fill=b["fill"], outline=b["border"], width=3)
        draw.text(((rect[0] + rect[2]) / 2, rect[1] + 28), b["title"], font=font_title, anchor="mm", fill=b["border"])
        draw.line([(rect[0] + 15, rect[1] + 48), (rect[2] - 15, rect[1] + 48)], fill=b["border"], width=1)
        for idx, line in enumerate(b["lines"]):
            draw.text(((rect[0] + rect[2]) / 2, rect[1] + 75 + idx * 28), line, font=font_body, anchor="mm", fill="#2D3748")

    def arrow(start, end, text="", pos=None):
        draw.line([start, end], fill="#2B6CB0", width=3)
        x, y = end
        dx, dy = end[0] - start[0], end[1] - start[1]
        if abs(dx) > abs(dy):
            direction = 1 if dx > 0 else -1
            points = [(x, y), (x - direction * 14, y - 8), (x - direction * 14, y + 8)]
        else:
            direction = 1 if dy > 0 else -1
            points = [(x, y), (x - 8, y - direction * 14), (x + 8, y - direction * 14)]
        draw.polygon(points, fill="#2B6CB0")
        if text and pos:
            draw.text(pos, text, font=font_label, anchor="mm", fill="#1A365D")

    # Arrows
    arrow((240, 240), (240, 370), "Truy cập Web & Upload", (330, 305))
    arrow((430, 480), (590, 180), "boto3: Upload S3", (530, 310))
    arrow((800, 240), (800, 370), "s3:ObjectCreated:*", (905, 305))
    arrow((1010, 470), (1170, 240), "Ghi 3 thumbnail JPEG", (1100, 335))
    arrow((1010, 550), (1170, 550), "Ghi metadata COMPLETE", (1090, 525))
    arrow((800, 660), (800, 750), "Ghi log & chỉ số", (885, 705))
    arrow((430, 580), (1170, 580), "Đọc trạng thái & metadata", (800, 610))
    arrow((430, 420), (1170, 300), "Sinh Presigned URL (300s)", (800, 350))
    arrow((430, 150), (1170, 150), "Xem ảnh qua Presigned URL", (800, 125))

    stream = BytesIO()
    canvas.save(stream, format="PNG")
    stream.seek(0)
    return stream


def main():
    doc = Document(TEMPLATE)
    cover = [deepcopy(element) for element in list(doc.element.body)[:25]]
    body = doc.element.body
    section = body.sectPr
    for element in list(body):
        if element is not section:
            body.remove(element)
    for element in cover:
        body.insert(len(body) - 1, element)

    # Update Title on cover page
    for paragraph in doc.paragraphs:
        if paragraph.text == "BÁO CÁO ĐỒ ÁN CUỐI KỲ":
            run = paragraph.runs[0]
            run.text = "BÁO CÁO TIẾN ĐỘ TUẦN 3"
            for extra in paragraph.runs[1:]:
                extra.text = ""
            run.font.size = Pt(18)

    # Styles
    styles = doc.styles
    for name in ("Normal", "Week 1 Body", "Week 1 Caption", "Heading 1", "Heading 2", "Heading 3"):
        styles[name].font.name = "Times New Roman"
        styles[name].font.color.rgb = RGBColor(0, 0, 0)
    styles["Week 1 Body"].font.size = Pt(13)
    styles["Week 1 Body"].paragraph_format.line_spacing = 1.25
    styles["Week 1 Body"].paragraph_format.space_after = Pt(6)
    for name in ("Heading 1", "Heading 2", "Heading 3"):
        styles[name].paragraph_format.keep_with_next = True
    for style in styles:
        if style.style_id in {"TOC1", "TOC2", "TOC3"}:
            style.font.name = "Times New Roman"
            style.font.size = Pt(11)
            style.paragraph_format.space_before = Pt(0)
            style.paragraph_format.space_after = Pt(2)
            style.paragraph_format.line_spacing = 1
            style.paragraph_format.keep_with_next = False

    doc.core_properties.title = "Báo cáo tiến độ tuần 3 — Triển khai Web Gallery trên EC2 và Tối ưu Serverless"
    doc.core_properties.author = "Bùi Nguyễn Duy Trung; Đỗ Anh Tuấn"
    doc.core_properties.subject = "Triển khai EC2 Gunicorn Systemd, IAM Role LabInstanceProfile, Presigned URL 300s, Lambda Layer và S3 Lifecycle Rule"
    doc.core_properties.comments = "Báo cáo nộp bài Tuần 3 môn Điện toán Đám mây (TS. Huỳnh Xuân Phụng)"

    for paragraph in doc.sections[0].first_page_footer.paragraphs:
        paragraph.clear()

    def p(text="", center=False):
        paragraph = doc.add_paragraph(text, style="Week 1 Body")
        if center:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        return paragraph

    def heading(text, level=2):
        paragraph = doc.add_heading(text, level=level)
        if level == 1:
            paragraph.paragraph_format.page_break_before = True
        return paragraph

    def table(headers, rows, widths=None):
        grid = doc.add_table(rows=1, cols=len(headers))
        grid.style = "Table Grid"
        if widths is None and len(headers) == 2:
            widths = [5.2, 10.3]
        if widths:
            grid.autofit = False
            for index, width in enumerate(widths):
                grid.columns[index].width = Cm(width)
        for cell, text in zip(grid.rows[0].cells, headers):
            cell.text = text
            shade = OxmlElement("w:shd")
            shade.set(qn("w:fill"), "E8EEF4")
            cell._tc.get_or_add_tcPr().append(shade)
        repeat = OxmlElement("w:tblHeader")
        grid.rows[0]._tr.get_or_add_trPr().append(repeat)
        for values in rows:
            for cell, text in zip(grid.add_row().cells, values):
                cell.text = str(text)
        for index, row in enumerate(grid.rows):
            cannot_split = OxmlElement("w:cantSplit")
            row._tr.get_or_add_trPr().append(cannot_split)
            for column_index, cell in enumerate(row.cells):
                if widths:
                    cell.width = grid.columns[column_index].width
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.space_after = Pt(4)
                    paragraph.paragraph_format.line_spacing = 1.05
                    for run in paragraph.runs:
                        run.font.name = "Times New Roman"
                        run.font.size = Pt(11)
                        run.bold = index == 0
        doc.add_paragraph().paragraph_format.space_after = Pt(0)

    # Evidence mapping from CSV
    evidence_csv = EVIDENCE / "DANH_MUC_MINH_CHUNG.csv"
    evidence_items = []
    with open(evidence_csv, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            evidence_items.append(row)

    figure_refs = {}
    figure_counter = 0
    bookmark_id_counter = 2000

    def add_evidence_figure(item_id, max_w=15.0, max_h=8.5):
        nonlocal figure_counter, bookmark_id_counter
        item = next((x for x in evidence_items if x["id"] == item_id), None)
        if not item:
            raise ValueError(f"Evidence ID not found: {item_id}")
        img_path = EVIDENCE / item["file"]
        if not img_path.is_file():
            raise FileNotFoundError(f"Image not found: {img_path}")

        with Image.open(img_path) as im:
            pw, ph = im.size

        scale = min(max_w / pw, max_h / ph)
        dw = pw * scale
        dh = ph * scale

        paragraph = p(center=True)
        paragraph.paragraph_format.space_before = Pt(4)
        paragraph.paragraph_format.space_after = Pt(3)
        paragraph.paragraph_format.line_spacing = 1
        paragraph.paragraph_format.keep_with_next = True
        paragraph.add_run().add_picture(str(img_path), width=Cm(dw), height=Cm(dh))

        figure_counter += 1
        anchor = f"w3fig{figure_counter}"
        caption = doc.add_paragraph(f"Hình 3.{figure_counter}. {item['caption']}", style="Week 1 Caption")
        caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
        caption.paragraph_format.space_before = Pt(0)
        caption.paragraph_format.space_after = Pt(8)
        caption.paragraph_format.line_spacing = 1.05
        caption.paragraph_format.keep_with_next = False

        bookmark_id_counter += 1
        bookmark(caption, anchor, bookmark_id_counter)
        figure_refs[item_id] = (f"Hình 3.{figure_counter}", anchor)

    def ref(paragraph, item_id):
        label, anchor = figure_refs[item_id]
        internal_link(paragraph, label, anchor)

    # ------------------ TABLE OF CONTENTS ------------------
    toc_title = p("MỤC LỤC")
    toc_title.paragraph_format.page_break_before = True
    toc_title.runs[0].bold = True
    toc_title.runs[0].font.size = Pt(16)
    toc = doc.add_paragraph()
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), 'TOC \\o "1-2" \\h \\z \\u')
    toc._p.append(field)

    # ------------------ CHƯƠNG 1 ------------------
    heading("CHƯƠNG 1. TỔNG QUAN ĐỀ TÀI VÀ MỤC TIÊU TUẦN 3", 1)

    heading("1.1. Bài toán và mục tiêu hoàn thiện hệ thống")
    p("Đề tài “Xử lý ảnh tự động: tạo thumbnail khi upload lên Amazon S3” hướng tới việc xây dựng một hệ thống phân tán hoàn chỉnh trên nền tảng điện toán đám mây Amazon Web Services (AWS), cho phép người dùng tải ảnh gốc một lần duy nhất và hệ thống sẽ tự động tạo ra 3 kích thước ảnh thu nhỏ (thumbnail) chuẩn hóa, gắn watermark bảo vệ quyền tác giả, cập nhật siêu dữ liệu và hiển thị an toàn trên giao diện web.")
    p("Trong các giai đoạn trước, hệ thống đã kiểm chứng thành công kiến trúc xử lý Serverless cục bộ và tích hợp các tài nguyên cốt lõi (S3, Lambda, DynamoDB, CloudWatch). Bước sang Tuần 3, mục tiêu quan trọng nhất là đưa toàn bộ ứng dụng người dùng (Web Gallery) lên máy chủ đám mây Amazon EC2 (Elastic Compute Cloud), thiết lập cơ chế xác thực danh tính an toàn qua IAM Role, bảo vệ quyền riêng tư cho kho ảnh S3 và triển khai các giải pháp tối ưu hóa mở rộng theo phản hồi định hướng của Giảng viên hướng dẫn.")
    paragraph_repo = p("Kho lưu trữ mã nguồn chính thức của đề tài: ")
    link(paragraph_repo, REPO, REPO)

    heading("1.2. Nền tảng kế thừa từ Tuần 2")
    p("Hệ thống bước vào Tuần 3 với nền tảng kỹ thuật vững chắc đã được triển khai, kiểm thử và đối chiếu thực nghiệm hoàn tất ở Tuần 2, bao gồm:")
    table(
        ["Thành phần kiến trúc", "Cấu hình kỹ thuật và trạng thái bàn giao từ Tuần 2"],
        [
            ["Amazon S3", "Hai bucket riêng biệt: cloudphoto-input-103308504802 (nhận ảnh uploads/) và cloudphoto-output-103308504802 (lưu thumbnail); chế độ truy cập riêng tư tuyệt đối (SSE-S3)."],
            ["AWS Lambda", "Hàm cloud-photo-processor; kiến trúc x86_64; bộ nhớ 1024 MB; timeout 60 giây; gắn quyền thực thi LabRole; kích hoạt tự động qua sự kiện S3 ObjectCreated."],
            ["Amazon DynamoDB", "Bảng cloud-photo-metadata; khóa phân vùng image_id kiểu String; chế độ On-demand capacity; lưu trữ tiến trình và thông số kỹ thuật ảnh."],
            ["Amazon CloudWatch", "Nhóm log /aws/lambda/cloud-photo-processor theo dõi sát sao thời gian thực thi (duration), dung lượng bộ nhớ tiêu thụ và nhật ký kiểm tra duplicate."],
            ["Bộ kiểm thử tích hợp", "12 ca kiểm thử T01–T12 (ảnh ngang, dọc, vuông, trong suốt, hỏng, quá dung lượng, trùng lặp...) đều đạt kết quả 100%."],
        ],
        widths=[5.0, 10.5]
    )

    heading("1.3. Tiếp thu ý kiến đánh giá của Giảng viên hướng dẫn và Phạm vi Tuần 3")
    p("Trong buổi nhận xét đánh giá tiến độ Tuần 2, Giảng viên hướng dẫn TS. Huỳnh Xuân Phụng đã kết luận: “Duyệt tuần 2. Lưu ý cho tuần sau: tuần này em chỉ link đúng một file docx, tuần sau link luôn các file code (worker, gallery, tests) vào báo cáo để thầy đối chiếu nhanh, không phải vào repo tìm. Nâng cao: đóng gói Pillow thành Lambda layer để giảm size gói deploy, thêm lifecycle rule cho bucket output tự dọn thumbnail cũ.”")
    p("Nhóm thực hiện đã nghiêm túc tiếp thu toàn diện các chỉ đạo trên và xác định phạm vi hành động cụ thể cho Tuần 3 như sau:")
    p("1. Triển khai máy chủ EC2: Khởi tạo instance Amazon EC2 chạy hệ điều hành Amazon Linux 2023, đóng gói ứng dụng Web Gallery bằng máy chủ ứng dụng công nghiệp Gunicorn WSGI và quản trị tiến trình chạy nền liên tục bằng systemd service (cloud-photo.service).")
    p("2. Ứng dụng IAM Instance Profile: Cấp quyền cho máy chủ EC2 đọc/ghi S3 và DynamoDB hoàn toàn dựa vào IAM Role LabRole (thông qua LabInstanceProfile), loại bỏ triệt để việc lưu trữ tĩnh Access Key / Secret Key trên máy chủ.")
    p("3. Bảo vệ dữ liệu với S3 Private và Presigned URL: Chặn toàn bộ truy cập công khai trực tiếp từ Internet vào S3 Output; chỉ cho phép tải và hiển thị thumbnail qua URL có chữ ký bảo mật tạm thời (Presigned URL) có thời hạn hiệu lực chính xác 300 giây (X-Amz-Expires=300).")
    p("4. Kiểm thử khả năng tự phục hồi dịch vụ (Self-healing): Xác minh dịch vụ web tự động khởi động lại và duy trì tính liên tục khi có lệnh restart hoặc sự cố tiến trình.")
    p("5. Hoàn thành Yêu cầu Nâng cao 1: Tách thư viện Pillow thành Lambda Layer riêng biệt, tối ưu kích thước gói nén triển khai của Lambda Function xuống chỉ còn 3.7 kB (cho phép mở và sửa trực tiếp trên AWS Console Code Editor).")
    p("6. Hoàn thành Yêu cầu Nâng cao 2: Thiết lập S3 Lifecycle Rule (auto-cleanup-old-thumbnails-7days) trên bucket output, tự động xóa thumbnail cũ sau 7 ngày để tối ưu chi phí lưu trữ.")
    p("7. Minh bạch mã nguồn: Tích hợp đầy đủ các liên kết trực tiếp (direct hyperlinks) đến từng file mã nguồn của dự án ngay trong báo cáo để giảng viên đối chiếu nhanh chóng.")

    # ------------------ CHƯƠNG 2 ------------------
    heading("CHƯƠNG 2. KIẾN TRÚC HỆ THỐNG VÀ NÂNG CẤP KỸ THUẬT TUẦN 3", 1)

    heading("2.1. Sơ đồ kiến trúc tổng thể")
    p("Hệ thống trong Tuần 3 đã được nâng cấp thành mô hình kiến trúc phân tán kết hợp hài hòa giữa hạ tầng máy chủ IaaS (Amazon EC2) và nền tảng Serverless hướng sự kiện (S3, Lambda, DynamoDB, CloudWatch):")

    paragraph_diag = p(center=True)
    paragraph_diag.paragraph_format.keep_with_next = True
    paragraph_diag.add_run().add_picture(architecture(), width=Cm(15.2))
    caption_diag = doc.add_paragraph("Hình 2.1. Sơ đồ kiến trúc tổng thể hệ thống Cloud Photo (Tuần 3)", style="Week 1 Caption")
    caption_diag.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption_diag.paragraph_format.space_after = Pt(8)

    p("Luồng dữ liệu xử lý trọn vẹn (End-to-End) diễn ra qua 6 giai đoạn chặt chẽ:")
    p("• Giai đoạn 1 (Tương tác người dùng): Người dùng kết nối vào Web Gallery thông qua kênh bảo mật SSH Local Port Forwarding tại http://localhost:8080 (chuyển tiếp tới cổng 8000 của Gunicorn trên máy chủ EC2). Người dùng đăng nhập bằng mật khẩu bảo vệ và tải ảnh lên.")
    p("• Giai đoạn 2 (Tải ảnh vào S3 Input): Ứng dụng Flask sử dụng SDK boto3 với quyền hạn từ IAM Role (LabInstanceProfile) để đẩy tệp ảnh gốc vào tiền tố uploads/<image_id>/ trên bucket cloudphoto-input-103308504802.")
    p("• Giai đoạn 3 (Kích hoạt Serverless): Sự kiện s3:ObjectCreated:* được S3 phát đi tức thì, kích hoạt hàm Lambda cloud-photo-processor.")
    p("• Giai đoạn 4 (Xử lý ảnh song song): Lambda nạp thư viện Pillow từ Lambda Layer v1 độc lập, thực hiện xử lý ảnh (giữ nguyên tỷ lệ, co giãn 3 kích thước 150px, 400px, 1000px, chuyển nền trong suốt sang màu trắng và dập watermark “CLOUD PHOTO”). Gói kết quả được đẩy vào bucket cloudphoto-output-103308504802.")
    p("• Giai đoạn 5 (Cập nhật trạng thái & Giám sát): Lambda ghi bản ghi trạng thái COMPLETE cùng các siêu dữ liệu vào bảng DynamoDB cloud-photo-metadata. Thông số thực thi được CloudWatch Logs lưu vết chi tiết.")
    p("• Giai đoạn 6 (Hiển thị an toàn qua Presigned URL): Web Gallery đọc DynamoDB để lấy danh sách ảnh đã xử lý thành công, sau đó tự động sinh S3 Presigned URL tạm thời có thời hạn 300 giây để trình duyệt người dùng nạp ảnh trực tiếp từ S3 Output mà không cần mở công khai bucket.")

    heading("2.2. Cơ chế xác thực an toàn bằng IAM Instance Profile (LabInstanceProfile)")
    p("Một trong những nguyên tắc cốt lõi của bảo mật đám mây (Cloud Security Best Practices) theo khung AWS Well-Architected Framework là: Tuyệt đối không lưu trữ cứng thông tin xác thực lâu dài (Long-term AWS Access Key ID và Secret Access Key) trên máy chủ hoặc trong mã nguồn ứng dụng.")
    p("Thay vào đó, hệ thống cấu hình gắn IAM Role LabRole cho máy chủ EC2 thông qua LabInstanceProfile. Khi ứng dụng Web Gallery gọi thư viện boto3, SDK của AWS sẽ tự động liên hệ với dịch vụ siêu dữ liệu nội bộ của EC2 (Instance Metadata Service - IMDSv2) tại địa chỉ mạng link-local http://169.254.169.254 để yêu cầu cấp các thông tin xác thực tạm thời (Temporary Credentials gồm AccessKey, SecretKey và SessionToken). Các token này có vòng đời ngắn hạn và được AWS tự động xoay vòng (auto-rotated) hoàn toàn ngầm định.")
    p("Nhờ giải pháp này, ngay cả trong trường hợp máy chủ EC2 bị xâm nhập tệp cấu hình, kẻ tấn công cũng không thể đánh cắp được bất kỳ khoá bảo mật vĩnh viễn nào của hệ thống.")

    heading("2.3. Cơ chế bảo vệ dữ liệu với S3 Private & Presigned URL có thời hạn 300 giây")
    p("Nhằm bảo vệ tối đa quyền riêng tư của người dùng, bucket cloudphoto-output-103308504802 được kích hoạt chính sách Chặn toàn bộ truy cập công khai (Block Public Access - On). Mọi nỗ lực truy cập trực tiếp bằng đường dẫn URL của S3 mà không có chữ ký bảo mật hợp lệ đều sẽ bị AWS từ chối lập tức với mã trạng thái HTTP 403 Forbidden kèm mã lỗi AccessDenied.")
    p("Để hiển thị được ảnh trên trình duyệt của người dùng hợp lệ, máy chủ Web Gallery sử dụng boto3 hàm generate_presigned_url('get_object', Params={'Bucket': ..., 'Key': ...}, ExpiresIn=300). Hàm này áp dụng thuật toán mã hóa HMAC-SHA256 để tạo ra một đường dẫn có chữ ký số chứa đầy đủ các tham số xác thực: X-Amz-Algorithm, X-Amz-Credential, X-Amz-Date, X-Amz-Expires=300, X-Amz-SignedHeaders và X-Amz-Signature.")
    p("Khi người dùng mở liên kết trong vòng 300 giây, AWS S3 xác thực chữ ký thành công và trả về tệp ảnh thumbnail. Khi thời gian vượt quá 300 giây, liên kết ngay lập tức hết hiệu lực; người dùng refresh trang sẽ nhận được thông báo lỗi Request has expired (HTTP 403), ngăn chặn hoàn toàn nguy cơ chia sẻ liên kết trái phép hoặc tấn công vét cạn dữ liệu.")

    heading("2.4. Tối ưu hóa triển khai Serverless: Lambda Layer và S3 Lifecycle Policy")
    p("Thực hiện 2 yêu cầu nâng cao theo chỉ đạo của Giảng viên hướng dẫn, nhóm đã triển khai hai cải tiến kỹ thuật đột phá:")
    p("1. Đóng gói Pillow thành Lambda Layer riêng biệt (Nâng cao 1): Thay vì đóng gói thư viện Pillow (>15 MB với các tệp nhị phân C shared library .so của Linux) chung vào file zip triển khai của Lambda Function, nhóm đã tách riêng toàn bộ thư viện này vào Layer độc lập cloud-photo-pillow phiên bản 1. Nhờ đó, tệp nén mã nguồn của hàm Lambda cloud-photo-processor giảm từ trên 15 MB xuống chỉ còn vỏn vẹn 3.7 kB (giảm hơn 99.9% dung lượng). Kích thước siêu nhẹ này giúp quá trình triển khai diễn ra tức thì, giảm thời gian khởi động nguội (Cold Start) và đặc biệt cho phép hiển thị trực quan toàn bộ mã nguồn trên trình soạn thảo AWS Console Code Editor.")
    p("2. Tự động hóa dọn dẹp bằng S3 Lifecycle Rule (Nâng cao 2): Trong các hệ thống xử lý ảnh thương mại, lượng ảnh thu nhỏ sinh ra tăng theo cấp số nhân khiến dung lượng lưu trữ phình to và làm đội chi phí duy trì. Nhóm đã cấu hình quy tắc Lifecycle Rule auto-cleanup-old-thumbnails-7days áp dụng cho toàn bộ bucket output. Quy tắc thiết lập tự động hết hạn và xóa vĩnh viễn (Permanently delete) các đối tượng ảnh sau 7 ngày kể từ ngày tạo, đồng thời tự động hủy các phiên tải lên phân đoạn dang dở (Delete expired multipart uploads sau 7 ngày), giúp kiểm soát ngân sách lưu trữ tối ưu mà không cần viết mã bảo trì thủ công.")

    heading("2.5. Bảng tổng hợp cấu hình tài nguyên hệ thống Tuần 3")
    table(
        ["Thành phần / Thông số", "Cấu hình triển khai thực tế trên AWS"],
        [
            ["AWS Region", "us-east-1 — N. Virginia (Subnet us-east-1d)."],
            ["Máy chủ EC2", "Instance ID i-0390fda0b0a75c002; Type t2.micro; AMI Amazon Linux 2023; Public IP 100.31.151.65; Private IP 172.31.16.240."],
            ["IAM Instance Profile", "Gắn LabRole vào EC2 thông qua LabInstanceProfile; tự động lấy quyền đọc/ghi S3 và DynamoDB qua IMDSv2."],
            ["Security Group", "cloud-photo-web-sg; Inbound: Port 22 (SSH) và Port 8000 (TCP); Outbound: Mở toàn bộ 0.0.0.0/0."],
            ["Máy chủ ứng dụng Web", "Gunicorn 26.2.0 chạy 2 workers; quản trị bởi systemd service /etc/systemd/system/cloud-photo.service (cơ chế Restart=on-failure)."],
            ["Kênh truy cập Web", "SSH Local Port Forwarding (-L 8080:localhost:8000); mở giao diện tại http://localhost:8080."],
            ["Lambda Function", "cloud-photo-processor; Python 3.12 (x86_64); 1024 MB RAM; timeout 60 giây; handler lambda_function.lambda_handler."],
            ["Kích thước gói deploy Lambda", "3.7 kB (chỉ gồm 2 tệp python lambda_function.py và image_tools.py)."],
            ["Lambda Layer", "cloud-photo-pillow phiên bản 1 (~5 MB), hỗ trợ đầy đủ các thư viện xử lý ảnh."],
            ["S3 Lifecycle Policy", "auto-cleanup-old-thumbnails-7days trên bucket output; tự động xóa tệp sau 7 ngày."],
            ["Bảo mật S3 & URL", "Bucket output chặn công khai; sinh Presigned URL với thời hạn hợp lệ chính xác 300 giây (X-Amz-Expires=300)."],
        ],
        widths=[5.5, 10.0]
    )

    # ------------------ CHƯƠNG 3 ------------------
    heading("CHƯƠNG 3. KẾT QUẢ TRIỂN KHAI VÀ MINH CHỨNG THỰC TẾ TRÊN AWS", 1)
    p("Ghi chú: Toàn bộ 21 hình ảnh minh chứng dưới đây được nhóm thực hiện trực tiếp trên AWS Management Console, Terminal EC2 và Trình duyệt Web Gallery vào ngày 27/10/2026. Mỗi minh chứng đều được đối chiếu mã SHA256 và lưu trữ trong thư mục evidence/tuan-3/ của kho mã nguồn.")

    heading("3.1. Minh chứng Nâng cao 1: Tối ưu gói mã Lambda và Pillow Layer")
    p("Thực hiện yêu cầu nâng cao thứ nhất của Giảng viên hướng dẫn, nhóm đã tách thành công gói thư viện Pillow thành Lambda Layer riêng. Kết quả kiểm chứng trên AWS Console cho thấy gói mã nguồn triển khai của hàm Lambda chỉ còn kích thước siêu nhẹ 3.7 kB, đồng thời hệ thống liên kết chính xác với Layer cloud-photo-pillow phiên bản 1:")
    add_evidence_figure("E22")
    p("Nhờ gói mã nguồn có kích thước nhỏ gọn (3.7 kB), AWS Management Console cho phép kích hoạt đầy đủ tính năng Code Editor trực quan. Nhóm có thể trực tiếp quan sát và rà soát hai tệp mã nguồn python nền tảng là lambda_function.py và image_tools.py ngay trên giao diện web mà không gặp bất kỳ giới hạn kích thước nào:")
    add_evidence_figure("E22-CODE")

    heading("3.2. Minh chứng Nâng cao 2: S3 Lifecycle Rule cho bucket output")
    p("Thực hiện yêu cầu nâng cao thứ hai của Giảng viên hướng dẫn, nhóm đã cấu hình quy tắc vòng đời auto-cleanup-old-thumbnails-7days áp dụng cho toàn bộ các đối tượng trong bucket cloudphoto-output-103308504802:")
    add_evidence_figure("E23a1")
    p("Trong mục cấu hình chi tiết hành động vòng đời (Lifecycle rule actions), nhóm thiết lập quy tắc tự động hết hạn và xóa các phiên bản hiện tại của đối tượng sau đúng 7 ngày (Expire current versions of objects after 7 days), đồng thời tự động hủy và xóa các tệp tải lên dang dở sau 7 ngày (Delete expired multipart uploads after 7 days):")
    add_evidence_figure("E23a2")
    p("Sau khi lưu cấu hình, tab Quản lý (Management) của bucket S3 đầu ra xác nhận quy tắc auto-cleanup-old-thumbnails-7days đã chuyển sang trạng thái kích hoạt (Enabled) và sẵn sàng tự động dọn dẹp theo chu kỳ của AWS:")
    add_evidence_figure("E23b")

    heading("3.3. Khởi tạo và thiết lập máy chủ EC2 Web Gallery")
    p("Nhóm khởi tạo thành công máy chủ Amazon EC2 với tên gọi cloud-photo-gallery, mã định danh i-0390fda0b0a75c002, loại cấu hình t2.micro, thuộc vùng khả dụng us-east-1d và sở hữu địa chỉ Public IPv4 là 100.31.151.65:")
    add_evidence_figure("E16a")
    p("Để đảm bảo tuân thủ nguyên tắc an toàn dữ liệu đám mây, máy chủ EC2 được gắn IAM Role LabRole thông qua LabInstanceProfile và được gán nhóm bảo mật cloud-photo-web-sg:")
    add_evidence_figure("E16b")
    p("Cấu hình tường lửa Inbound Rules của Security Group cloud-photo-web-sg được thiết lập chặt chẽ: chỉ cho phép kết nối cổng 22 (SSH) để quản trị từ xa và cổng 8000 (Custom TCP) cho dịch vụ ứng dụng web:")
    add_evidence_figure("E16c")
    p("Trên máy chủ EC2, ứng dụng Flask được triển khai bằng máy chủ WSGI Gunicorn (2 sync workers) và được quản trị bởi tiến trình dịch vụ systemd /etc/systemd/system/cloud-photo.service. Trạng thái dịch vụ xác nhận Active: active (running) ổn định:")
    add_evidence_figure("E16d")
    p("Kiểm tra sức khỏe nội bộ tại terminal EC2 thông qua lệnh curl http://127.0.0.1:8000/health nhận được phản hồi định dạng JSON chuẩn xác {\"status\":\"ok\"}:")
    add_evidence_figure("E16e")

    heading("3.4. Triển khai Web Gallery và xác thực người dùng trên EC2")
    p("Người dùng kết nối tới Web Gallery thông qua đường hầm bảo mật SSH Local Port Forwarding tại địa chỉ http://localhost:8080. Giao diện trang đăng nhập (Login) hiển thị chuyên nghiệp, yêu cầu người dùng cung cấp mật khẩu bảo vệ để mở quyền truy cập:")
    add_evidence_figure("E17a")
    p("Sau khi xác thực thành công, giao diện chuyển vào trang tổng quan (Dashboard). Khu vực tải ảnh lên cho phép người dùng kéo thả tệp hoặc chọn ảnh từ máy tính (hỗ trợ JPG/PNG tối đa 10 MiB) kèm chỉ dẫn rõ ràng về 3 phiên bản ảnh sẽ được hệ thống tự động sinh ra:")
    add_evidence_figure("E17b1")
    p("Khu vực bộ sưu tập (Gallery Cards) kết nối với bảng DynamoDB cloud-photo-metadata để truy xuất danh sách ảnh đã xử lý thành công. Mỗi thẻ ảnh hiển thị đầy đủ 3 phiên bản thu nhỏ (150px, 400px, 1000px) kèm watermark sắc nét:")
    add_evidence_figure("E17b2")

    heading("3.5. Kiểm thử bảo mật IAM Role và Presigned URL")
    p("Kiểm thử T16: Nhóm thực thi các lệnh aws s3 ls và aws dynamodb describe-table trực tiếp từ terminal của máy chủ EC2. Kết quả trả về thành công hoàn toàn mà không cần nhập hay cấu hình bất kỳ tệp access key nào, chứng minh IAM Role LabInstanceProfile đã hoạt động chính xác:")
    add_evidence_figure("E24a")
    p("Kiểm thử T13: Người dùng sao chép đường dẫn trực tiếp của một tệp ảnh trên S3 Output và mở trên trình duyệt web. Do bucket được cấu hình chặn công khai, AWS S3 phản hồi thông báo lỗi dạng XML với mã lỗi AccessDenied và mã HTTP 403:")
    add_evidence_figure("E24b")
    p("Kiểm thử T14 (Giai đoạn hợp lệ): Người dùng mở ảnh thông qua đường dẫn Presigned URL được sinh tự động bởi Web Gallery với tham số thời hạn X-Amz-Expires=300. Trong vòng 300 giây, ảnh thumbnail 1000px kèm watermark CLOUD PHOTO được tải về và hiển thị rõ ràng:")
    add_evidence_figure("E24c")
    p("Kiểm thử T14 (Giai đoạn hết hạn): Sau khi quá thời hạn 300 giây kể từ thời điểm URL được sinh ra, người dùng làm mới lại liên kết trên trình duyệt. AWS S3 ngay lập tức từ chối yêu cầu và trả về lỗi XML Request has expired (HTTP 403), chứng minh cơ chế bảo mật thời gian thực thi hiệu quả:")
    add_evidence_figure("E24d")

    heading("3.6. Kiểm thử độ bền và khả năng tự phục hồi dịch vụ")
    p("Kiểm thử T15: Để đánh giá khả năng chịu lỗi và tính sẵn sàng cao của ứng dụng trên máy chủ EC2, nhóm thực hiện câu lệnh khởi động lại dịch vụ: sudo systemctl restart cloud-photo. Nhật ký hệ thống xác nhận Gunicorn đã tự động tái sinh với mã định danh tiến trình mới (PID 31812) chỉ sau vài mili-giây mà không hề làm gián đoạn hệ thống:")
    add_evidence_figure("E25a")
    p("Ngay sau khi restart, nhóm truy cập lại giao diện Web Gallery trên trình duyệt. Ứng dụng nạp lại tức thì, phiên làm việc được bảo toàn và toàn bộ danh mục ảnh cùng trạng thái xử lý vẫn hoạt động trơn tru:")
    add_evidence_figure("E25b")

    heading("3.7. Kiểm thử luồng xử lý ảnh End-to-End từ EC2 đến AWS Serverless")
    p("Kiểm thử T19: Nhóm tiến hành thực nghiệm trọn vẹn luồng hoạt động bằng cách tải lên tệp ảnh mẫu mới portrait.jpg (kích thước gốc 900 × 1500 pixel, dung lượng 27.8 KiB) qua giao diện Web EC2. Sau vài giây, hệ thống hoàn tất xử lý, DynamoDB ghi nhận trạng thái COMPLETE và Web Gallery cập nhật hiển thị ảnh thứ 10 trong bộ sưu tập:")
    add_evidence_figure("E26a")
    p("Kiểm tra nhật ký CloudWatch Logs của hàm Lambda tương ứng với đợt xử lý ảnh này xác nhận luồng chạy hoàn hảo: hàm xử lý thành công ảnh có image_id cb2147cc1cad5b61f734f66ef8e56..., tổng thời gian thực thi (Duration) đạt 604.68 ms và lượng bộ nhớ tiêu thụ tối đa chỉ 153 MB trên 1024 MB được cấp phát:")
    add_evidence_figure("E26b")

    # ------------------ CHƯƠNG 4 ------------------
    heading("CHƯƠNG 4. TỔNG HỢP KẾT QUẢ KIỂM THỬ VÀ ĐỐI CHIẾU TIẾN ĐỘ", 1)

    heading("4.1. Bảng tổng hợp kết quả 7 ca kiểm thử Tuần 3 (T13 – T19)")
    p("Kế thừa bộ 12 ca kiểm thử T01–T12 của Tuần 2, nhóm đã tiến hành mở rộng và hoàn tất xuất sắc 7 ca kiểm thử tích hợp chuyên sâu cho Tuần 3 trên môi trường AWS thực tế:")
    table(
        ["Mã", "Tình huống kiểm thử", "Kết quả quan sát thực tế", "Đánh giá"],
        [
            ["T13", "Chặn truy cập trực tiếp S3 object", "Mở trực tiếp link S3 không có chữ ký nhận XML AccessDenied (HTTP 403); bucket hoàn toàn riêng tư.", "Đạt"],
            ["T14", "Thời hạn Presigned URL (300s)", "Trong 300s xem ảnh sắc nét; sau 300s refresh nhận XML Request has expired (HTTP 403); bảo mật quyền riêng tư.", "Đạt"],
            ["T15", "Tự phục hồi sau restart app / EC2", "Lệnh systemctl restart khởi động lại tiến trình với PID mới (31812); web gallery truy cập ổn định, không mất phiên.", "Đạt"],
            ["T16", "Quyền IAM Role LabInstanceProfile của EC2", "Lệnh aws s3 ls và describe-table từ EC2 thành công qua LabInstanceProfile; không có credentials cục bộ.", "Đạt"],
            ["T17", "Nâng cao 1: Tối ưu gói deploy qua Lambda Layer", "Gói zip deploy chỉ 3.7 kB (giảm >99% size); Layer Pillow ~5 MB được gắn dùng chung; code editor hiển thị trực tiếp 2 file python.", "Đạt"],
            ["T18", "Nâng cao 2: S3 Lifecycle Rule dọn thumbnail cũ", "Lifecycle rule auto-cleanup-old-thumbnails-7days kích hoạt Enabled trên bucket output; tự động expire objects sau 7 ngày.", "Đạt"],
            ["T19", "Luồng xử lý ảnh End-to-End từ Web EC2", "Tải portrait.jpg qua Web EC2 kích hoạt Lambda qua S3; DynamoDB ghi COMPLETE; Web hiển thị ảnh thứ 10; CloudWatch ghi 604.68 ms.", "Đạt"],
        ],
        widths=[1.5, 4.5, 7.5, 2.0]
    )

    heading("4.2. Bảng phân công thực hiện và đóng góp thành viên")
    table(
        ["Thành viên thực hiện", "Nội dung công việc phụ trách trong Tuần 3", "Mức độ đóng góp"],
        [
            [
                "Bùi Nguyễn Duy Trung\nMSSV: 24110363\nGitHub: bndt0103",
                "• Đóng gói Pillow thành Lambda Layer riêng biệt (v1), tối ưu gói mã deploy Lambda xuống 3.7 kB.\n• Thiết lập S3 Lifecycle Rule tự dọn dẹp thumbnail cũ sau 7 ngày trên bucket output.\n• Soạn thảo kịch bản cấu hình systemd service cho Gunicorn trên EC2.\n• Phân tích và đo đạc log hiệu năng CloudWatch Logs (thời gian, dung lượng bộ nhớ).",
                "50%\n(Hoàn thành xuất sắc)"
            ],
            [
                "Đỗ Anh Tuấn\nMSSV: 24110369\nGitHub: DoAnhTuan-24110369",
                "• Khởi tạo máy chủ EC2, cấu hình môi trường ảo Python 3.12, cài đặt Gunicorn và chạy service.\n• Thiết lập IAM Role LabInstanceProfile và kiểm tra quyền truy cập S3/DynamoDB.\n• Thực hiện các ca kiểm thử bảo mật: Chặn link S3 trực tiếp, kiểm thử thời hạn Presigned URL 300s.\n• Kiểm thử tự phục hồi service và kiểm thử tải ảnh End-to-End từ Web EC2.",
                "50%\n(Hoàn thành xuất sắc)"
            ],
        ],
        widths=[4.5, 8.5, 2.5]
    )

    heading("4.3. Đánh giá tồn tại và Kế hoạch triển khai Tuần 4")
    p("Đánh giá kết quả đạt được: Hệ thống đã vận hành ổn định trên kiến trúc hybrid (IaaS EC2 kết hợp Serverless AWS), loại bỏ hoàn toàn nguy cơ rò rỉ credentials nhờ IAM Role, đảm bảo tính riêng tư dữ liệu với Presigned URL và hoàn thành trọn vẹn 2 yêu cầu nâng cao về tối ưu gói mã và quản lý vòng đời lưu trữ.")
    p("Các điểm hạn chế cần khắc phục: Do sử dụng tài khoản học tập AWS Academy Learner Lab nên chưa thể gắn trực tiếp Elastic IP cố định cho EC2; máy chủ mới chỉ chạy ở quy mô single instance t2.micro mà chưa có bộ cân bằng tải Application Load Balancer (ALB) và Auto Scaling.")
    p("Kế hoạch chi tiết cho Tuần 4 (Giai đoạn hoàn thiện đồ án cuối kỳ):")
    p("1. Đo lường và phân tích chi phí: Xây dựng bảng hạch toán chi phí chi tiết theo mô hình AWS Pricing cho các dịch vụ EC2, S3, Lambda, DynamoDB và CloudWatch dưới các kịch bản tải thực tế.")
    p("2. Quay video demo hoàn chỉnh: Thực hiện video clip demo 3–5 phút thuyết minh toàn bộ luồng hoạt động từ Web Gallery trên EC2 đến các dịch vụ Serverless phía sau.")
    p("3. Hoàn thiện báo cáo tổng kết cuối kỳ: Tổng hợp kết quả thực nghiệm 4 tuần, hoàn thiện tài liệu hướng dẫn vận hành và slide thuyết trình nghiệm thu đồ án.")

    # ------------------ CHƯƠNG 5 ------------------
    heading("CHƯƠNG 5. ĐỐI CHIẾU MÃ NGUỒN VÀ KHAI BÁO SỬ DỤNG AI", 1)

    heading("5.1. Liên kết trực tiếp các file mã nguồn dự án")
    p("Thực hiện đúng yêu cầu của Giảng viên hướng dẫn: “tuần sau link luôn các file code (worker, gallery, tests) vào báo cáo để thầy đối chiếu nhanh, không phải vào repo tìm”, nhóm xin trân trọng cung cấp các liên kết trực tiếp (direct hyperlinks) đến từng file mã nguồn chính thức trên GitHub:")

    code_files = [
        ("Worker xử lý ảnh Lambda", "src/processor/lambda_function.py", "Xử lý sự kiện S3 ObjectCreated, kiểm tra duplicate, gọi Pillow và cập nhật DynamoDB."),
        ("Module xử lý ảnh Pillow", "src/processor/image_tools.py", "Tạo 3 kích thước thumbnail (150, 400, 1000px), dập watermark CLOUD PHOTO, xóa EXIF."),
        ("Ứng dụng Web Gallery Flask", "src/web/app.py", "Xác thực người dùng, bảo vệ CSRF, tải ảnh lên S3, đọc DynamoDB và sinh Presigned URL 300s."),
        ("File cấu hình dịch vụ Systemd", "deploy/cloud-photo.service", "File unit service quản lý tiến trình Gunicorn chạy nền trên EC2, tự phục hồi Restart=on-failure."),
        ("Kịch bản tự động hóa đóng gói", "scripts/build_packages.py", "Script đóng gói lambda_processor.zip (3.7 kB), web_app.zip và Lambda Layer Pillow."),
        ("Bộ kiểm thử Xử lý ảnh", "tests/test_images.py", "10 ca kiểm thử xử lý ảnh các định dạng ngang, dọc, vuông, trong suốt, hỏng, quá cỡ."),
        ("Bộ kiểm thử Lambda Worker", "tests/test_worker.py", "5 ca kiểm thử logic worker bằng dịch vụ AWS giả lập."),
        ("Bộ kiểm thử Web Gallery", "tests/test_web.py", "4 ca kiểm thử giao diện web, kiểm soát truy cập và phòng chống CSRF."),
    ]

    for label, path, desc in code_files:
        par = p()
        par.add_run(f"• {label} (").bold = True
        link(par, path, f"{REPO}/blob/main/{path}")
        par.add_run(f"): {desc}")

    heading("5.2. Danh sách các commit đã thực hiện trên GitHub trong Tuần 3")
    p("Tất cả các thay đổi mã nguồn, tệp cấu hình và minh chứng Tuần 3 đã được nhóm đóng góp theo thứ tự khoa học và đẩy lên nhánh main của kho mã nguồn:")

    commits_w3 = [
        ("a75a35a", "Bùi Nguyễn Duy Trung", "Cấu hình S3 Lifecycle Rule dọn thumbnail cũ và kịch bản deploy EC2", "https://github.com/bndt0103/aws-thumbnail/commit/a75a35a2d58f2f63a2d556a37c9d464ffd9005e1"),
        ("87e3a73", "Bùi Nguyễn Duy Trung", "Bổ sung minh chứng tối ưu Lambda Layer và S3 Lifecycle Rule", "https://github.com/bndt0103/aws-thumbnail/commit/87e3a730afe0428ec418f21b4e333ff475c8f172"),
        ("fd3e8f5", "Đỗ Anh Tuấn", "Cấu hình gunicorn cho web và minh chứng khởi tạo EC2 gallery", "https://github.com/bndt0103/aws-thumbnail/commit/fd3e8f5a2d90cef94a541479b0b6f3dfbbb6f6b7"),
        ("138ac4e", "Đỗ Anh Tuấn", "Bổ sung minh chứng kiểm thử gallery EC2, presigned URL và tự phục hồi service", "https://github.com/bndt0103/aws-thumbnail/commit/138ac4e52312436585386dd34030c1bac713c732"),
        ("070be51", "Đỗ Anh Tuấn", "Đối chiếu danh mục minh chứng và kết quả kiểm thử EC2 tích hợp", "https://github.com/bndt0103/aws-thumbnail/commit/070be51e5a57c016a9a5a8cf0ca386555f55cba4"),
    ]

    for sha, author, message, commit_url in commits_w3:
        par = p()
        link(par, f"Commit {sha}", commit_url)
        par.add_run(f" — {author}: {message}.")

    heading("5.3. Khai báo sử dụng AI minh bạch và chuẩn xác")
    p("Nhóm cam kết tính trung thực học thuật và xin khai báo đầy đủ việc sử dụng công cụ Trí tuệ Nhân tạo (AI) trong Tuần 3:")
    p("• Các mô hình AI sử dụng: Google Gemini (phiên bản mô hình Gemini 3.8 Flash High) và OpenAI ChatGPT (phiên bản mô hình GPT-4o).")
    p("• Tóm lược các prompt đã sử dụng: Hướng dẫn cấu hình dịch vụ systemd trên Linux; phân tích cơ chế xác thực không dùng khóa thông qua IAM Instance Profile và IMDSv2; hướng dẫn thiết lập chính sách S3 Lifecycle Rule dọn dẹp thumbnail sau 7 ngày; hướng dẫn sinh và kiểm tra thời hạn S3 Presigned URL (ExpiresIn=300); hỗ trợ biên soạn kịch bản tạo báo cáo Word tự động tích hợp 21 hình ảnh minh chứng.")
    p("• Nội dung AI hỗ trợ: Đề xuất cấu trúc file unit systemd; hỗ trợ giải thích các thông số kỹ thuật trong log CloudWatch; tư vấn bố cục trình bày báo cáo học thuật chuẩn mực.")
    p("• Phần sinh viên trực tiếp thực hiện và kiểm chứng: Trực tiếp thao tác trên môi trường AWS Academy Learner Lab; khởi tạo và SSH vào máy chủ EC2; biên dịch môi trường Python và cấu hình dịch vụ Gunicorn; thực hiện toàn bộ 7 ca kiểm thử thực tế T13–T19; chụp và kiểm chứng toàn bộ 21 ảnh minh chứng.")

    heading("5.4. Đánh giá vai trò của AI và cam kết của sinh viên")
    p("Công cụ AI đóng vai trò như một trợ lý lập trình và cố vấn giải pháp kỹ thuật, giúp nhóm tiết kiệm thời gian tra cứu tài liệu và nhanh chóng phát hiện các sai lệch cấu hình. Mọi quyết định thiết kế kiến trúc, cấu hình dịch vụ đám mây trên AWS, viết mã nguồn và kiểm chứng thực nghiệm đều do hai sinh viên trong nhóm tự tay thực hiện, đối chiếu và chịu trách nhiệm học thuật hoàn toàn.")

    # ------------------ TÀI LIỆU THAM KHẢO ------------------
    heading("TÀI LIỆU THAM KHẢO", 1)
    references = [
        ("AWS Documentation — Amazon EC2 User Guide for Linux Instances", "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html"),
        ("AWS Documentation — IAM roles for Amazon EC2 (Instance Profiles)", "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html"),
        ("AWS Documentation — Sharing Amazon S3 objects using presigned URLs", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html"),
        ("AWS Documentation — Managing your storage lifecycle on Amazon S3", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html"),
        ("AWS Documentation — Working with layers for Python AWS Lambda", "https://docs.aws.amazon.com/lambda/latest/dg/python-layers.html"),
        ("Gunicorn — Python WSGI HTTP Server for UNIX Documentation", "https://docs.gunicorn.org/en/stable/"),
        ("Kho lưu trữ mã nguồn đồ án Cloud Photo trên GitHub", REPO),
    ]

    for index, (label, url) in enumerate(references, 1):
        paragraph = p(f"{index}. ")
        link(paragraph, label, url)

    p("Báo cáo và các kết quả thực nghiệm được tổng hợp và đối chiếu ngày 27/10/2026.")

    # Preserve relationships & settings
    referenced = set()
    for element in doc.element.iter():
        for attr, value in element.attrib.items():
            if attr.startswith("{" + "http://schemas.openxmlformats.org/officeDocument/2006/relationships" + "}"):
                referenced.add(value)
    for rel_id, rel in list(doc.part.rels.items()):
        if rel.reltype.rsplit("/", 1)[-1] in {"image", "hyperlink"} and rel_id not in referenced:
            doc.part.drop_rel(rel_id)

    update = OxmlElement("w:updateFields")
    update.set(qn("w:val"), "true")
    doc.settings.element.append(update)
    preserve_images = OxmlElement("w:doNotAutoCompressPictures")
    doc.settings.element.append(preserve_images)

    doc.save(OUTPUT)
    print(f"Successfully generated: {OUTPUT}")
    print(f"Total evidence figures inserted: {figure_counter}/21")


if __name__ == "__main__":
    main()

