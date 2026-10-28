"""Build the Comprehensive Final Word Report (.docx) for the Cloud Computing final project.

Topic: "Xử lý ảnh tự động: tạo thumbnail khi upload lên Amazon S3 (Nhóm: Serverless)"
Students: Bùi Nguyễn Duy Trung (24110363), Đỗ Anh Tuấn (24110369)
Instructor: TS. Huỳnh Xuân Phụng
Institution: Trường Đại học Sư phạm Kỹ thuật TP. Hồ Chí Minh (HCMUTE)
Repository: https://github.com/bndt0103/aws-thumbnail

This script generates the authoritative capstone report covering all 4 weeks of the project,
embedding all 79 figures (Architecture diagram + 20 from Week 1 + 33 from Week 2 + 21 from Week 3 + 5 from Week 4),
all 22 test cases (T01 - T22), complete cost analysis, video demo storyboard, teardown procedure,
code links, commit history, and AI disclosure.

Run from repository root: py -3.12 scripts/build_final_report.py
"""

import os
import sys
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
TEMPLATE = ROOT / "Report/BaoCaoTuan1_24110363_24110369.docx"
OUTPUT = ROOT / "Report/BaoCaoTongKet_24110363_24110369.docx"
REPO = "https://github.com/bndt0103/aws-thumbnail"
VIDEO_URL = "https://drive.google.com/file/d/1AwaAWUkTE6Rjg70xBr83gmRPW5vs9j8_/view?usp=drive_link"


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
    text = OxmlElement("w:t")
    text.text = label
    run.append(text)
    element.append(run)
    paragraph._p.append(element)


def architecture():
    """Generate high-resolution architecture diagram of the complete system."""
    canvas = Image.new("RGB", (1600, 850), "white")
    draw = ImageDraw.Draw(canvas)
    font_path = Path("C:/Windows/Fonts/arial.ttf")
    font_bold_path = Path("C:/Windows/Fonts/arialbd.ttf")
    font = ImageFont.truetype(str(font_path), 20) if font_path.exists() else ImageFont.load_default(size=20)
    bold = ImageFont.truetype(str(font_bold_path), 22) if font_bold_path.exists() else font
    title_font = ImageFont.truetype(str(font_bold_path), 26) if font_bold_path.exists() else font
    small = ImageFont.truetype(str(font_path), 17) if font_path.exists() else ImageFont.load_default(size=17)

    # Background title header
    draw.rounded_rectangle((30, 20, 1570, 70), radius=10, fill="#2B6CB0", outline="#2C5282", width=2)
    draw.text((800, 45), "KIẾN TRÚC HỆ THỐNG XỬ LÝ ẢNH TỰ ĐỘNG CLOUD PHOTO TRÊN AWS (IaaS + Serverless)",
              font=title_font, fill="white", anchor="mm")

    boxes = {
        "user": {
            "rect": (50, 100, 310, 270),
            "title": "Người dùng / Trình duyệt",
            "lines": [
                "Truy cập: http://localhost:8080",
                "Đăng nhập phiên làm việc",
                "Tải ảnh JPG / PNG (<= 10 MiB)",
                "Xem 3 kích cỡ qua Presigned URL",
            ],
            "fill": "#EBF8FF",
            "border": "#3182CE",
        },
        "ssh_tunnel": {
            "rect": (50, 320, 310, 470),
            "title": "Kênh an toàn SSH Tunnel",
            "lines": [
                "Local Port Forwarding: 8080",
                "Chuyển tiếp đến EC2: 127.0.0.1:8000",
                "Khóa bảo mật: labsuser.pem",
                "Mã hóa toàn bộ lưu lượng web",
            ],
            "fill": "#EDF2F7",
            "border": "#4A5568",
        },
        "ec2": {
            "rect": (50, 520, 310, 810),
            "title": "Amazon EC2 (Web Gallery)",
            "lines": [
                "Instance: i-0390fda0b0a75c002 (t2.micro)",
                "OS: Amazon Linux 2023 · us-east-1d",
                "WSGI: Gunicorn 26.2.0 (2 workers)",
                "Quản lý: systemd (cloud-photo.service)",
                "Cơ chế: Restart=on-failure",
                "Quyền: IAM Role LabInstanceProfile",
                "Bảo mật: Không lưu Access Key tĩnh",
            ],
            "fill": "#EBF8FF",
            "border": "#2B6CB0",
        },
        "s3_in": {
            "rect": (430, 100, 790, 300),
            "title": "S3 Input Bucket (Ảnh gốc)",
            "lines": [
                "cloudphoto-input-103308504802",
                "Tiền tố: uploads/<image_id>/",
                "Sự kiện: s3:ObjectCreated:*",
                "Chặn toàn bộ Public Access (On)",
                "Mã hóa SSE-S3 & Bucket Key On",
            ],
            "fill": "#FEEBC8",
            "border": "#C05621",
        },
        "lambda": {
            "rect": (430, 350, 790, 610),
            "title": "AWS Lambda (Serverless)",
            "lines": [
                "Hàm: cloud-photo-processor",
                "Runtime: Python 3.12 · Arch: x86_64",
                "Bộ nhớ: 512 MB · Timeout: 30 giây",
                "Role thực thi: LabRole (quản lý)",
                "Lambda Layer: cloud-photo-pillow (v1)",
                "Gói deploy code: Chỉ 3.7 kB",
                "Tạo 3 kích thước: 150, 400, 1000px",
                "Watermark CLOUD PHOTO · Giữ tỷ lệ",
            ],
            "fill": "#FEFCBF",
            "border": "#B7791F",
        },
        "cloudwatch": {
            "rect": (430, 660, 790, 810),
            "title": "Amazon CloudWatch",
            "lines": [
                "Log Group: /aws/lambda/cloud-photo-processor",
                "Retention Period: 7 ngày (tiết kiệm chi phí)",
                "Metrics: Invocations, Duration, Success Rate",
            ],
            "fill": "#FED7D7",
            "border": "#9B2C2C",
        },
        "s3_out": {
            "rect": (910, 100, 1550, 430),
            "title": "S3 Output Bucket (Private tuyệt đối & Tự dọn dẹp)",
            "lines": [
                "Tên bucket: cloudphoto-output-103308504802",
                "Tiền tố lưu trữ: thumbnails/<image_id>/ (3 tệp thumbnail JPEG)",
                "Chế độ bảo mật: Private hoàn toàn · Chặn link trực tiếp HTTP 403 AccessDenied",
                "Cấp quyền xem an toàn: Presigned URL có thời hạn chính xác 300 giây",
                "Tính năng Nâng cao: S3 Lifecycle Rule 'auto-cleanup-old-thumbnails-7days'",
                "-> Tự động xóa thumbnail cũ sau 7 ngày & hủy multipart upload dở dang",
                "-> Chống lặp vô tận (Loop): Bucket đầu ra không gắn bất kỳ Event Notification nào",
            ],
            "fill": "#C6F6D5",
            "border": "#22543D",
        },
        "dynamodb": {
            "rect": (910, 480, 1550, 810),
            "title": "Amazon DynamoDB (Cơ sở dữ liệu NoSQL Serverless)",
            "lines": [
                "Tên bảng: cloud-photo-metadata · Trạng thái: Active",
                "Khóa phân vùng (Partition Key): image_id (Kiểu String - băm SHA-256)",
                "Chế độ thông lượng: On-demand Capacity (Pay-per-request, tự co giãn)",
                "Lưu trữ: original (filename, size, dimensions), 3 variants (dimensions, s3_key)",
                "Trạng thái vòng đời: COMPLETE / FAILED / DUPLICATE_SKIPPED",
                "Ghi nhận chính xác: processing_time_ms (~600 ms) & uploaded_at ISO 8601",
                "Bảo mật: Mã hóa dữ liệu lưu trữ bằng khóa AWS-owned key & gắn nhãn quản lý",
            ],
            "fill": "#EBF8FF",
            "border": "#2B6CB0",
        },
    }

    for box in boxes.values():
        x1, y1, x2, y2 = box["rect"]
        draw.rounded_rectangle((x1, y1, x2, y2), radius=8, fill=box["fill"], outline=box["border"], width=2)
        draw.rectangle((x1, y1, x2, y1 + 32), fill=box["border"])
        draw.text((x1 + 10, y1 + 6), box["title"], font=bold, fill="white")
        cy = y1 + 40
        for line in box["lines"]:
            draw.text((x1 + 12, cy), line, font=small, fill="#1A202C")
            cy += 21

    def arrow(start, end, label, label_pos):
        draw.line([start, end], fill="#2D3748", width=3)
        sx, sy = start
        ex, ey = end
        if ex > sx:
            points = [(ex, ey), (ex - 8, ey - 5), (ex - 8, ey + 5)]
        elif ex < sx:
            points = [(ex, ey), (ex + 8, ey - 5), (ex + 8, ey + 5)]
        elif ey > sy:
            points = [(ex, ey), (ex - 5, ey - 8), (ex + 5, ey - 8)]
        else:
            points = [(ex, ey), (ex - 5, ey + 8), (ex + 5, ey + 8)]
        draw.polygon(points, fill="#2D3748")
        lx, ly = label_pos
        w = len(label) * 8 + 14
        draw.rounded_rectangle((lx - w / 2, ly - 12, lx + w / 2, ly + 12), radius=4, fill="#EDF2F7", outline="#A0AEC0")
        draw.text((lx, ly), label, font=small, fill="#2D3748", anchor="mm")

    # Connector arrows
    arrow((180, 270), (180, 320), "1. Yêu cầu tải ảnh", (180, 295))
    arrow((180, 470), (180, 520), "2. SSH Tunnel", (180, 495))
    arrow((310, 600), (430, 220), "3. boto3: Upload ảnh gốc", (370, 380))
    arrow((610, 300), (610, 350), "4. s3:ObjectCreated:*", (610, 325))
    arrow((790, 430), (910, 320), "5. Ghi 3 thumbnails JPEG", (850, 370))
    arrow((790, 530), (910, 600), "6. Ghi trạng thái COMPLETE", (850, 560))
    arrow((610, 610), (610, 660), "7. Ghi nhận logs & REPORT", (610, 635))
    arrow((310, 700), (910, 700), "8. Đọc metadata danh sách ảnh", (610, 700))
    arrow((310, 650), (910, 380), "9. Sinh Presigned URL (300s)", (610, 510))
    arrow((200, 100), (910, 180), "10. Trình duyệt xem ảnh qua Presigned URL", (550, 130))

    stream = BytesIO()
    canvas.save(stream, format="PNG")
    stream.seek(0)
    return stream


def main():
    print(f"Loading template: {TEMPLATE}")
    doc = Document(str(TEMPLATE))

    # Keep the cover page elements (first 25 XML body elements)
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
        if paragraph.text == "BÁO CÁO TIẾN ĐỘ TUẦN 3":
            run = paragraph.runs[0]
            run.text = "BÁO CÁO ĐỒ ÁN CUỐI KỲ"
            for extra in paragraph.runs[1:]:
                extra.text = ""
            run.font.size = Pt(18)

    # Styles
    styles = doc.styles
    for name in ("Normal", "Week 1 Body", "Week 1 Caption", "Heading 1", "Heading 2", "Heading 3"):
        if name in styles:
            styles[name].font.name = "Times New Roman"
            styles[name].font.color.rgb = RGBColor(0, 0, 0)
    styles["Week 1 Body"].font.size = Pt(13)
    styles["Week 1 Body"].paragraph_format.line_spacing = 1.25
    styles["Week 1 Body"].paragraph_format.space_after = Pt(6)
    for name in ("Heading 1", "Heading 2", "Heading 3"):
        if name in styles:
            styles[name].paragraph_format.keep_with_next = True
    for style in styles:
        if style.style_id in {"TOC1", "TOC2", "TOC3"}:
            style.font.name = "Times New Roman"
            style.font.size = Pt(11)
            style.paragraph_format.space_before = Pt(0)
            style.paragraph_format.space_after = Pt(2)
            style.paragraph_format.line_spacing = 1
            style.paragraph_format.keep_with_next = False

    doc.core_properties.title = "Báo cáo tổng kết đồ án — Xử lý ảnh tự động: tạo thumbnail khi upload lên Amazon S3"
    doc.core_properties.author = "Bùi Nguyễn Duy Trung (24110363); Đỗ Anh Tuấn (24110369)"
    doc.core_properties.subject = "Báo cáo tổng kết toàn diện 4 tuần môn Điện toán Đám mây (TS. Huỳnh Xuân Phụng)"
    doc.core_properties.comments = "Kho mã nguồn: https://github.com/bndt0103/aws-thumbnail.git"

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
            widths = [5.0, 10.5]
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

    fig_counter = 0

    def figure(fig_label, image_path, caption_text, width_cm=15.0):
        nonlocal fig_counter
        fig_counter += 1
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)

        if isinstance(image_path, (str, Path)):
            img_path = Path(image_path)
            if not img_path.exists():
                print(f"WARNING: Image not found: {img_path}")
                run = p_img.add_run(f"[HÌNH ẢNH: {fig_label} - {img_path.name}]")
                run.bold = True
            else:
                with Image.open(img_path) as im:
                    w, h = im.size
                aspect = h / w
                target_w = width_cm
                target_h = target_w * aspect
                if target_h > 12.0:
                    target_h = 12.0
                    target_w = target_h / aspect
                p_img.add_run().add_picture(str(img_path), width=Cm(target_w), height=Cm(target_h))
        else:
            p_img.add_run().add_picture(image_path, width=Cm(width_cm))

        p_cap = doc.add_paragraph(style="Week 1 Caption")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)
        p_cap.paragraph_format.keep_with_next = False
        bk_name = f"fig_{fig_label.replace(' ', '_').replace('.', '_')}"
        bookmark(p_cap, bk_name, 2000 + fig_counter)
        run_label = p_cap.add_run(f"{fig_label}. ")
        run_label.bold = True
        p_cap.add_run(caption_text)
        return p_cap

    print("Building complete capstone report content across all 4 weeks...")

    # =========================================================================
    # LỜI MỞ ĐẦU & THÔNG TIN CHUNG
    # =========================================================================
    h1 = heading("THÔNG TIN CHUNG VÀ LỜI CẢM ƠN", level=1)
    p("Đồ án môn học Điện toán Đám mây (Cloud Computing) với đề tài “Xử lý ảnh tự động: tạo thumbnail khi upload lên Amazon S3” được thực hiện bởi nhóm sinh viên Bùi Nguyễn Duy Trung (MSSV: 24110363) và Đỗ Anh Tuấn (MSSV: 24110369), dưới sự giảng dạy và hướng dẫn tận tình của TS. Huỳnh Xuân Phụng tại Trường Đại học Sư phạm Kỹ thuật TP. Hồ Chí Minh (HCMUTE).")
    p("Trong suốt lộ trình 4 tuần triển khai thực tế trên hạ tầng đám mây Amazon Web Services (AWS), nhóm đã tiếp thu nghiêm túc và trọn vẹn mọi nhận xét chỉ đạo của Thầy, từng bước nâng cấp hệ thống từ việc xử lý cục bộ lên kiến trúc kết hợp tối ưu giữa máy chủ IaaS (Amazon EC2) và nền tảng phi máy chủ Serverless (S3, Lambda, DynamoDB, CloudWatch).")
    p("Báo cáo tổng kết này tài liệu hóa đầy đủ, chi tiết và minh bạch toàn bộ quá trình nghiên cứu, thiết kế, triển khai thực tế, 22 ca kiểm thử, 79 hình ảnh minh chứng, hạch toán kinh tế AWS và quy trình dọn dẹp tài nguyên sau khi nghiệm thu.")

    # =========================================================================
    # CHƯƠNG 1: TỔNG QUAN ĐỀ TÀI VÀ MỤC TIÊU DỰ ÁN (TOÀN BỘ 4 TUẦN)
    # =========================================================================
    heading("CHƯƠNG 1. TỔNG QUAN ĐỀ TÀI VÀ MỤC TIÊU DỰ ÁN", level=1)
    
    heading("1.1. Đặt vấn đề và tính cấp thiết", level=2)
    p("Trong kỷ nguyên số, các ứng dụng web hiện đại như thương mại điện tử, mạng xã hội, cổng tin tức và hệ sinh thái lưu trữ ảnh cá nhân đều phải đối mặt với bài toán tiếp nhận khối lượng hình ảnh khổng lồ do người dùng tải lên hàng ngày. Những hình ảnh gốc này thường có độ phân giải rất cao và dung lượng lớn (từ vài megabyte đến hàng chục megabyte).")
    p("Nếu ứng dụng hiển thị trực tiếp ảnh gốc lên giao diện danh sách hoặc bảng tin, hệ thống sẽ gặp các tổn thất nghiêm trọng:")
    p("1. Tiêu tốn băng thông mạng vô ích: Mỗi người dùng tải trang sẽ phải nạp toàn bộ ảnh gốc kích thước lớn, làm tiêu hao tài nguyên mạng của cả máy chủ lẫn thiết bị đầu cuối.")
    p("2. Tốc độ tải trang suy giảm nghiêm trọng: Thời gian kết xuất đồ họa (render) kéo dài, làm giảm chỉ số trải nghiệm người dùng (UX) và ảnh hưởng tiêu cực đến thứ hạng SEO.")
    p("3. Thách thức quá tải máy chủ (Server Overload): Nếu sử dụng máy chủ ứng dụng truyền thống (Monolith Server) để vừa phục vụ web vừa gánh tác vụ nặng về CPU như giải nén và xử lý ảnh, máy chủ sẽ nhanh chóng cạn kiệt tài nguyên CPU và bộ nhớ RAM khi có đợt tải đột biến (flash sale, sự kiện), dẫn đến nghẽn mạng hoặc sập toàn bộ dịch vụ.")
    p("Để giải quyết bài toán trên, kiến trúc điện toán đám mây hiện đại đã tách biệt hoàn toàn tác vụ xử lý hình ảnh ra khỏi máy chủ web, ứng dụng mô hình hướng sự kiện (Event-driven Architecture) với các dịch vụ phi máy chủ (Serverless). Khi người dùng tải ảnh lên kho lưu trữ đám mây, một sự kiện sẽ tự động kích hoạt hàm xử lý để tạo ra các phiên bản ảnh thu nhỏ (thumbnail) tối ưu về kích thước và dung lượng mà không làm ảnh hưởng đến hiệu năng của máy chủ web chính.")

    heading("1.2. Mục tiêu nghiên cứu và phạm vi giải quyết", level=2)
    p("Đề tài tập trung xây dựng một hệ thống hoàn chỉnh kết hợp tối ưu giữa máy chủ IaaS và các dịch vụ phi máy chủ Serverless trên nền tảng AWS, đáp ứng đầy đủ các mục tiêu kỹ thuật:")
    p("• Tiếp nhận ảnh tải lên định dạng phổ biến (JPEG, PNG), dung lượng tối đa 10 MiB và kích thước không vượt quá 24 triệu pixel.")
    p("• Tự động tạo chính xác 3 phiên bản thumbnail chuẩn cho mỗi ảnh tải lên:")
    p("  - Kích thước nhỏ (Small): Cạnh dài tối đa 150 pixel, tối ưu cho biểu tượng đại diện (avatar), thumbnail danh sách thu nhỏ.")
    p("  - Kích thước vừa (Medium): Cạnh dài tối đa 400 pixel, tối ưu cho thẻ hiển thị sản phẩm dạng lưới (product cards, grid view).")
    p("  - Kích thước lớn (Large): Cạnh dài tối đa 1000 pixel, tối ưu cho chế độ xem chi tiết ảnh chất lượng cao.")
    p("• Đảm bảo chất lượng xử lý ảnh chuyên nghiệp: Duy trì đúng tỷ lệ khung hình gốc (aspect ratio), không gây méo ảnh; đóng dấu watermark bản quyền 'CLOUD PHOTO' ở góc dưới bên phải; tự động chuẩn hóa ảnh PNG có kênh độ trong suốt (alpha channel) sang nền trắng chuẩn JPEG; loại bỏ dữ liệu nhạy cảm EXIF; không phóng đại (no-upscale) đối với ảnh có kích thước nhỏ hơn kích thước đích.")
    p("• Đảm bảo an toàn bảo mật tuyệt đối theo chuẩn AWS: Tuyệt đối không lưu Access Key tĩnh trên máy chủ; áp dụng IAM Role qua IMDSv2; kho lưu trữ thumbnail S3 ở chế độ Private hoàn toàn và cấp quyền xem tạm thời qua Presigned URL có thời hạn chính xác 300 giây.")
    p("• Tối ưu hóa vận hành và kinh tế: Áp dụng cơ chế tự phục hồi dịch vụ web bằng systemd Restart=on-failure; tách Pillow thành Lambda Layer riêng giúp gói deploy siêu nhẹ 3.7 kB; thiết lập S3 Lifecycle Rule tự động dọn ảnh thumbnail sau 7 ngày; tiết kiệm hơn 85% chi phí vận hành so với mô hình máy chủ nguyên khối.")

    heading("1.3. Lộ trình triển khai tổng thể qua 4 tuần", level=2)
    p("Dự án được thực hiện nghiêm túc và bài bản theo đúng lộ trình 4 tuần:")
    p("• Tuần 1 — Khởi tạo nền tảng và Thiết kế kiến trúc: Thiết kế kiến trúc hướng sự kiện; xây dựng module xử lý ảnh Pillow cục bộ; viết 19 ca kiểm thử Unit test (pytest đạt 100%); khởi tạo tài nguyên cơ sở trên AWS Academy (S3 buckets, DynamoDB, LabRole, Layer cơ sở).")
    p("• Tuần 2 — Tích hợp hệ thống Serverless trên AWS: Kết nối S3 Trigger, triển khai Lambda Function cloud-photo-processor, tích hợp DynamoDB metadata và CloudWatch Logs, thực nghiệm xử lý ảnh thực tế, kiểm chứng chống lặp vô tận, kiểm chứng xử lý sự kiện trùng và kiểm tra Web Gallery cục bộ qua 12 ca kiểm thử T01–T12.")
    p("• Tuần 3 — Triển khai Web Gallery lên EC2 và Hoàn thành 2 Yêu cầu Nâng cao: Đưa Web Gallery lên máy chủ Amazon EC2 (Amazon Linux 2023, Gunicorn 26.2.0, systemd cloud-photo.service); hoàn thành 2 yêu cầu nâng cao của GVHD (Pillow Lambda Layer v1 gói 3.7 kB và S3 Lifecycle Rule 7 ngày); bảo mật IAM Role LabInstanceProfile (IMDSv2) và Presigned URL 300 giây; kiểm chứng 7 ca kiểm thử T13–T19 trên AWS.")
    p("• Tuần 4 — Chốt đồ án cuối kỳ: Hạch toán chi phí AWS chi tiết; quay video demo sản phẩm hoàn chỉnh Full HD thời lượng dưới 10 phút; thực hiện quy trình dọn dẹp tài nguyên (Teardown); biên tập báo cáo tổng kết toàn diện 4 tuần.")

    # =========================================================================
    # CHƯƠNG 2: THIẾT KẾ KIẾN TRÚC VÀ CƠ CHẾ KỸ THUẬT TOÀN HỆ THỐNG
    # =========================================================================
    heading("CHƯƠNG 2. THIẾT KẾ KIẾN TRÚC VÀ CƠ CHẾ KỸ THUẬT TOÀN HỆ THỐNG", level=1)
    
    heading("2.1. Sơ đồ kiến trúc tổng thể kết hợp IaaS & Serverless", level=2)
    p("Hệ thống Cloud Photo kết hợp nhuần nhuyễn giữa hạ tầng máy chủ Web IaaS (Amazon EC2) và cụm dịch vụ phi máy chủ Serverless (S3, Lambda, DynamoDB, CloudWatch) tạo nên một luồng xử lý khép kín, an toàn và tối ưu:")
    
    fig_arch = figure("Hình 2.1", architecture(), "Sơ đồ kiến trúc tổng thể hệ thống xử lý ảnh Cloud Photo trên AWS", width_cm=16.0)

    p("Luồng hoạt động tổng thể của hệ thống gồm 10 bước phối hợp chặt chẽ:")
    p("1. Người dùng kết nối vào giao diện Web Gallery qua cổng an toàn 8080 (được chuyển tiếp qua SSH Tunnel vào máy chủ EC2).")
    p("2. Người dùng thực hiện đăng nhập bảo mật và tải tệp ảnh (JPEG/PNG) lên hệ thống thông qua biểu mẫu web.")
    p("3. Ứng dụng Flask chạy trên EC2 sử dụng thư viện boto3 để tải ảnh gốc trực tiếp vào Amazon S3 Input Bucket tại tiền tố uploads/<image_id>/original.jpg.")
    p("4. Sự kiện s3:ObjectCreated:* từ S3 Input Bucket tự động kích hoạt (trigger) hàm AWS Lambda cloud-photo-processor.")
    p("5. Hàm Lambda tải ảnh gốc vào bộ nhớ tạm /tmp, nạp thư viện Pillow từ Lambda Layer, tiến hành kiểm tra tính hợp lệ, loại bỏ EXIF, áp dụng watermark và tạo ra 3 phiên bản thumbnail (150px, 400px, 1000px).")
    p("6. Lambda ghi 3 tệp thumbnail JPEG vào Amazon S3 Output Bucket tại tiền tố thumbnails/<image_id>/.")
    p("7. Lambda ghi nhận bản ghi metadata hoàn tất với trạng thái COMPLETE, thời gian xử lý và danh mục kích thước vào bảng Amazon DynamoDB cloud-photo-metadata.")
    p("8. Lambda xuất nhật ký thực thi (thời gian chạy, dung lượng RAM sử dụng) vào Amazon CloudWatch Logs Group /aws/lambda/cloud-photo-processor.")
    p("9. Máy chủ Web Gallery EC2 truy vấn DynamoDB để lấy danh sách ảnh của người dùng và hiển thị trạng thái hoàn thành.")
    p("10. Để hiển thị ảnh thumbnail an toàn, máy chủ EC2 sinh Presigned URL với thời hạn 300 giây từ S3 Output Bucket; trình duyệt của người dùng tải và hiển thị ảnh trực tiếp qua Presigned URL an toàn.")

    heading("2.2. Cơ chế xử lý ảnh hướng sự kiện và quy chuẩn 3 kích thước thumbnail", level=2)
    p("Trái tim của hệ thống xử lý ảnh là module image_tools.py và hàm lambda_function.py được thiết kế theo các nguyên tắc tối ưu đồ họa:")
    p("• Duy trì tỷ lệ khung hình: Thuật toán tính toán hệ số co giãn dựa trên cạnh dài nhất của ảnh gốc: scale = target_size / max(width, height). Kích thước mới được tính: new_w = int(width * scale), new_h = int(height * scale). Cơ chế này đảm bảo ảnh thu nhỏ không bao giờ bị méo mó, biến dạng.")
    p("• Không phóng đại (No-upscale): Nếu ảnh gốc có cạnh dài nhỏ hơn kích thước đích cần tạo, hệ thống giữ nguyên kích thước gốc để tránh hiện tượng vỡ hạt (pixelation).")
    p("• Chuẩn hóa độ trong suốt (Alpha Channel): Đối với ảnh PNG có kênh trong suốt (RGBA/LA/P), thuật toán tạo một ảnh nền trắng thuần (RGB, 255, 255, 255) và áp dụng phương thức alpha composite trước khi chuyển sang định dạng JPEG, khắc phục triệt để lỗi ảnh thumbnail bị đen nền.")
    p("• Đóng dấu watermark bản quyền: Chữ 'CLOUD PHOTO' được khắc mờ tinh tế ở góc dưới bên phải với độ trong suốt 30%, đảm bảo tính nhận diện thương hiệu mà không che khuất nội dung chính của bức ảnh.")
    p("• Chống vòng lặp vô tận (Infinite Loop Prevention): Đây là một trong những lỗi kinh điển nguy hiểm nhất trong kiến trúc Serverless. Nhóm đã giải quyết triệt để bằng cách tách biệt hoàn toàn 2 S3 bucket: bucket đầu vào cloudphoto-input-103308504802 và bucket đầu ra cloudphoto-output-103308504802. S3 Output Bucket hoàn toàn không cấu hình bất kỳ Event Notification nào, loại bỏ 100% nguy cơ Lambda bị kích hoạt lặp vô tận.")

    heading("2.3. Cơ chế xác thực an toàn qua IAM Instance Profile (LabInstanceProfile & IMDSv2)", level=2)
    p("Một điểm nhấn kỹ thuật quan trọng của hệ thống được GVHD đánh giá rất cao là việc loại bỏ hoàn toàn Access Key tĩnh:")
    p("• Rủi ro của giải pháp cũ: Việc lưu trữ AWS_ACCESS_KEY_ID và AWS_SECRET_ACCESS_KEY trực tiếp trong mã nguồn, file cấu hình .env hoặc biến môi trường tiềm ẩn rủi ro lộ lọt thông tin xác thực nghiêm trọng nếu máy chủ bị tấn công hoặc mã nguồn bị chia sẻ sơ suất.")
    p("• Giải pháp chuẩn AWS Security: Máy chủ EC2 được gắn IAM Role LabRole thông qua LabInstanceProfile. Thư viện boto3 khi chạy trên EC2 sẽ tự động giao tiếp với dịch vụ Instance Metadata Service phiên bản 2 (IMDSv2) tại địa chỉ mạng liên kết nội bộ http://169.254.169.254/latest/meta-data/ để nhận thông tin xác thực tạm thời (Temporary Security Credentials). Các khóa tạm này được AWS tự động xoay vòng định kỳ, đảm bảo an toàn tuyệt đối ngay cả khi có sự cố thâm nhập hệ điều hành.")

    heading("2.4. Cơ chế bảo vệ dữ liệu với S3 Private và Presigned URL thời hạn 300 giây", level=2)
    p("Để bảo vệ tài nguyên hình ảnh của người dùng, hệ thống thiết lập chế độ bảo mật hai tầng:")
    p("• Tầng 1 — Chặn công khai tuyệt đối: S3 Output Bucket được bật tính năng Block All Public Access và cấu hình Bucket Owner Enforced (vô hiệu hóa ACL). Bất kỳ nỗ lực truy cập trực tiếp nào vào URL của đối tượng S3 (dạng https://<bucket>.s3.amazonaws.com/<key>) đều bị AWS chặn đứng ngay lập tức với mã lỗi HTTP 403 AccessDenied.")
    p("• Tầng 2 — Cấp quyền tạm thời qua Presigned URL: Khi người dùng hợp lệ đăng nhập vào Web Gallery và yêu cầu xem ảnh, máy chủ EC2 sử dụng quyền của IAM Role để tạo ra một Presigned URL có thời hạn chính xác 300 giây (X-Amz-Expires=300). Trình duyệt của người dùng có thể mở ảnh bình thường trong 5 phút. Khi hết 300 giây, URL sẽ trở nên vô giá trị và trả về lỗi XML Request has expired. Cơ chế này ngăn chặn hoàn toàn việc chia sẻ liên kết trái phép ra bên ngoài.")

    heading("2.5. Hai giải pháp tối ưu hóa nâng cao", level=2)
    p("Nhóm đã hiện thực hóa trọn vẹn 2 yêu cầu kỹ thuật nâng cao do GVHD đặt ra:")
    p("1. Tối ưu gói deploy Lambda bằng Lambda Layer: Thư viện xử lý ảnh Pillow (cùng các file nhị phân C-extension) được tách riêng thành Lambda Layer cloud-photo-pillow v1. Nhờ đó, gói nén mã nguồn của Lambda Function giảm ngoạn mục từ hơn 15 MB xuống chỉ còn vỏn vẹn 3.7 kB (chỉ chứa 2 tệp lambda_function.py và image_tools.py). Điều này cho phép mở, xem và chỉnh sửa trực tiếp mã nguồn trên AWS Console Code Editor mà không bị giới hạn dung lượng.")
    p("2. Tự động dọn dẹp thumbnail bằng S3 Lifecycle Rule: Trên S3 Output Bucket, nhóm thiết lập quy tắc vòng đời auto-cleanup-old-thumbnails-7days ở trạng thái Enabled. Quy tắc này tự động đánh dấu hết hạn và xóa sạch các tệp thumbnail sau 7 ngày kể từ ngày tạo, đồng thời tự động hủy các multipart upload dang dở sau 7 ngày, giúp tiết kiệm tối đa chi phí lưu trữ đám mây.")

    heading("2.6. Quản trị tiến trình Web Gallery bằng systemd service và Gunicorn 26.2.0", level=2)
    p("Máy chủ Web Gallery trên EC2 được cấu hình theo chuẩn môi trường sản xuất (Production-ready):")
    p("• Máy chủ ứng dụng WSGI Gunicorn 26.2.0: Chạy 2 tiến trình worker song song, liên kết với cổng nội bộ 127.0.0.1:8000, xử lý đồng thời nhiều yêu cầu người dùng một cách mượt mà.")
    p("• Quản trị dịch vụ bằng systemd: Dịch vụ được đóng gói thành unit file /etc/systemd/system/cloud-photo.service, được quản lý như một dịch vụ nền của hệ điều hành Linux. Khi hệ điều hành khởi động lại, dịch vụ tự động kích hoạt.")
    p("• Cơ chế tự phục hồi lỗi (Fault Tolerance): Cấu hình chỉ thị Restart=on-failure và RestartSec=5s. Khi tiến trình ứng dụng gặp lỗi nghiêm trọng hoặc bị buộc dừng (kill -9), systemd sẽ tự động tái sinh tiến trình mới trong vòng 5 giây, đảm bảo tính sẵn sàng cao (High Availability) cho hệ thống.")

    heading("2.7. Bảng tổng hợp cấu hình toàn bộ tài nguyên hệ thống", level=2)
    p("Bảng 2.1 tổng hợp đầy đủ các thông số kỹ thuật của toàn bộ các tài nguyên đã cấu hình và vận hành thực tế trên AWS:")

    t21_headers = ["Thành phần hệ thống", "Cấu hình triển khai thực tế trên AWS", "Đặc tính kỹ thuật & Vai trò"]
    t21_rows = [
        ["AWS Region", "us-east-1 (N. Virginia), Subnet us-east-1d", "Vùng triển khai chuẩn có độ trễ thấp và đầy đủ dịch vụ."],
        ["Máy chủ EC2", "Instance ID i-0390fda0b0a75c002, loại t2.micro (1 vCPU, 1 GiB RAM), Amazon Linux 2023", "Web Gateway trung gian tiếp nhận yêu cầu, cách ly người dùng với backend."],
        ["Bảo mật IAM Role", "IAM Role LabRole gắn qua LabInstanceProfile, dùng IMDSv2", "Tự động lấy quyền đọc/ghi S3 và DynamoDB; không lưu Access Key tĩnh."],
        ["Tường lửa Security Group", "cloud-photo-web-sg, mở cổng 22 (SSH) và 8000 (Custom TCP)", "Bảo vệ máy chủ EC2, chặn toàn bộ các cổng không được phép."],
        ["Quản trị dịch vụ Web", "systemd service (/etc/systemd/system/cloud-photo.service), Gunicorn 26.2.0 (2 workers)", "Duy trì web chạy nền liên tục; tự động hồi sinh khi gặp lỗi với Restart=on-failure."],
        ["S3 Input Bucket", "cloudphoto-input-103308504802, prefix uploads/<image_id>/", "Lưu trữ ảnh gốc; Block Public Access On; SSE-S3; gắn trigger ObjectCreated."],
        ["S3 Output Bucket", "cloudphoto-output-103308504802, prefix thumbnails/<image_id>/", "Lưu 3 thumbnail JPEG; Private tuyệt đối (HTTP 403); Presigned URL 300s."],
        ["S3 Lifecycle Rule", "auto-cleanup-old-thumbnails-7days (Enabled)", "Tự động xóa thumbnail cũ sau 7 ngày; xóa multipart upload dở sau 7 ngày."],
        ["AWS Lambda", "cloud-photo-processor, Python 3.12, x86_64, 512 MB RAM, timeout 30s", "Xử lý ảnh không máy chủ; gói deploy siêu nhẹ chỉ 3.7 kB."],
        ["Lambda Layer", "cloud-photo-pillow (Phiên bản 1, tương thích Python 3.12, x86_64)", "Chứa thư viện Pillow độc lập, tối ưu kích thước gói hàm Lambda."],
        ["Amazon DynamoDB", "Bảng cloud-photo-metadata, Partition Key image_id (String), On-demand", "Lưu trữ siêu dữ liệu ảnh, trạng thái COMPLETE và thời gian xử lý."],
        ["CloudWatch Logs", "Log Group /aws/lambda/cloud-photo-processor, Retention 7 days", "Ghi vết sự kiện, đo lường thời gian thực thi (~600 ms) và dung lượng RAM."],
    ]
    table(t21_headers, t21_rows, [3.8, 6.2, 5.5])

    # =========================================================================
    # CHƯƠNG 3: KẾT QUẢ TRIỂN KHAI VÀ MINH CHỨNG THỰC TẾ TUẦN 1
    # =========================================================================
    heading("CHƯƠNG 3. KẾT QUẢ TRIỂN KHAI VÀ MINH CHỨNG THỰC TẾ TUẦN 1 (KHỞI TẠO NỀN TẢNG)", level=1)
    p("Tuần 1 tập trung vào việc thiết kế kiến trúc hệ thống, chuẩn bị công cụ phát triển, xây dựng module xử lý ảnh Pillow, viết bộ kiểm thử cục bộ và khởi tạo toàn bộ tài nguyên nền tảng trên AWS Academy Learner Lab.")

    heading("3.1. Chuẩn bị môi trường công cụ và kiểm thử cục bộ", level=2)
    p("Nhóm tiến hành cài đặt môi trường lập trình Python 3.12.10 và hệ thống quản lý phiên bản Git 2.54.0 trên máy trạm phát triển, đảm bảo tính tương thích tuyệt đối với môi trường chạy trên AWS.")
    figure("Hình 3.1", ROOT / "evidence/tuan-1/W1-LOCAL_python-git.png", "Kết quả kiểm tra phiên bản Python 3.12.10 và Git trên máy cục bộ")

    p("Để đảm bảo thuật toán xử lý ảnh hoạt động hoàn hảo trước khi đưa lên đám mây, nhóm xây dựng bộ kiểm thử Unit Test toàn diện gồm 19 ca kiểm thử giả lập (mocking) bao quát các trường hợp: giữ tỷ lệ ảnh, chuyển đổi PNG trong suốt, đóng dấu watermark, loại bỏ EXIF và từ chối ảnh lỗi. Kết quả chạy bằng pytest đạt 100% thành công.")
    figure("Hình 3.2", ROOT / "evidence/tuan-1/W1-TEST_pytest.png", "Kết quả chạy 19 ca kiểm thử Unit Test cục bộ với pytest đạt 100% trong 3.00s")

    heading("3.2. Khởi tạo môi trường AWS Academy Learner Lab", level=2)
    p("Nhóm khởi động môi trường thực hành AWS Academy Learner Lab. Hệ thống chuyển sang trạng thái AWS xanh sẵn sàng và hiển thị hạn mức ngân sách Used $0 of $50.")
    figure("Hình 3.3", ROOT / "evidence/tuan-1/E01_lab-ready.png", "Môi trường AWS Academy Learner Lab đã sẵn sàng với hạn mức ngân sách $50 USD")

    p("Nhóm đối chiếu và xác nhận thông tin tài khoản gồm Account ID 103308504802 và vùng hoạt động chuẩn us-east-1 (N. Virginia).")
    figure("Hình 3.4", ROOT / "evidence/tuan-1/E02_account-region.png", "Thông tin tài khoản AWS Account ID 103308504802 và Region us-east-1")

    heading("3.3. Kiểm tra IAM Role LabRole và cấu hình phân quyền", level=2)
    p("Trong dịch vụ IAM, nhóm kiểm tra vai trò thực thi LabRole có sẵn của phòng lab. Màn hình xác nhận ARN arn:aws:iam::103308504802:role/LabRole và hồ sơ phiên bản LabInstanceProfile.")
    figure("Hình 3.5", ROOT / "evidence/tuan-1/W1-IAM_labrole-summary.png", "Thông tin tổng quan của IAM Role LabRole và LabInstanceProfile")

    p("Chính sách quyền hạn của LabRole gồm 7 chính sách quản lý (4 AWS managed, 3 customer managed), cấp đầy đủ quyền tương tác với Amazon S3, Amazon DynamoDB, AWS Lambda và Amazon CloudWatch Logs.")
    figure("Hình 3.6", ROOT / "evidence/tuan-1/W1-IAM_labrole-permissions.png", "Chính sách phân quyền của LabRole cho các dịch vụ S3, DynamoDB, Lambda")

    p("Mục Trust Relationships xác nhận quyền tin cậy cho phép dịch vụ lambda.amazonaws.com thực hiện hành động sts:AssumeRole.")
    figure("Hình 3.7", ROOT / "evidence/tuan-1/W1-IAM_labrole-trust-01.png", "Chính sách tin cậy (Trust Relationship) của LabRole cho phép Lambda assume role")

    heading("3.4. Khởi tạo vùng lưu trữ Amazon S3 và cấu hình bảo vệ dữ liệu", level=2)
    p("Nhóm khởi tạo hai bucket S3 độc lập tại Region us-east-1. Bucket đầu vào cloudphoto-input-103308504802 được tạo với thư mục tiền tố uploads/ để lưu ảnh gốc.")
    figure("Hình 3.8", ROOT / "evidence/tuan-1/E03a_input-objects.png", "Bucket đầu vào cloudphoto-input-103308504802 với tiền tố uploads/")

    p("Bucket đầu ra cloudphoto-output-103308504802 được tạo cùng Region để sẵn sàng tiếp nhận các tệp ảnh thumbnail do Lambda kết xuất.")
    figure("Hình 3.9", ROOT / "evidence/tuan-1/E04a_output-objects.png", "Bucket đầu ra cloudphoto-output-103308504802 sẵn sàng lưu thumbnail")

    p("Cả hai bucket đều được kích hoạt tính năng Block All Public Access để ngăn ngừa tuyệt đối mọi truy cập trái phép từ Internet.")
    figure("Hình 3.10", ROOT / "evidence/tuan-1/E03b_input-block-public-access.png", "Cấu hình Chặn toàn bộ truy cập công khai của bucket đầu vào")
    figure("Hình 3.11", ROOT / "evidence/tuan-1/E04b_output-block-public-access.png", "Cấu hình Chặn toàn bộ truy cập công khai của bucket đầu ra")

    p("Cấu hình Object Ownership được đặt ở chế độ Bucket owner enforced, vô hiệu hóa hoàn toàn danh sách kiểm soát truy cập (ACL) theo khuyến nghị bảo mật của AWS.")
    figure("Hình 3.12", ROOT / "evidence/tuan-1/E03c_input-object-ownership.png", "Cấu hình Object Ownership Bucket owner enforced của bucket đầu vào")
    figure("Hình 3.13", ROOT / "evidence/tuan-1/E04b_output-object-ownership.png", "Cấu hình Object Ownership Bucket owner enforced của bucket đầu ra")

    p("Mã hóa mặc định phía máy chủ (SSE-S3) và Bucket Key được kích hoạt trên cả hai bucket, giúp bảo vệ dữ liệu ở trạng thái lưu trữ mà không phát sinh thêm chi phí.")
    figure("Hình 3.14", ROOT / "evidence/tuan-1/E03d_input-default-encryption.png", "Mã hóa mặc định SSE-S3 và Bucket Key trên bucket đầu vào")
    figure("Hình 3.15", ROOT / "evidence/tuan-1/E04c_output-default-encryption.png", "Mã hóa mặc định SSE-S3 và Bucket Key trên bucket đầu ra")

    p("Các tài nguyên S3 được gắn nhãn quản lý chuẩn hóa: Project=CloudPhoto và Owner=24110363-24110369.")
    figure("Hình 3.16", ROOT / "evidence/tuan-1/E18a_input-tags.png", "Gắn nhãn quản lý tài nguyên (Tags: Project, Owner) cho các S3 bucket")

    heading("3.5. Khởi tạo bảng cơ sở dữ liệu Amazon DynamoDB", level=2)
    p("Nhóm khởi tạo bảng cơ sở dữ liệu NoSQL cloud-photo-metadata với khóa phân vùng image_id kiểu chuỗi và chế độ On-demand Capacity.")
    figure("Hình 3.17", ROOT / "evidence/tuan-1/E05a_dynamodb-settings.png", "Bảng Amazon DynamoDB cloud-photo-metadata trạng thái Active với khóa image_id")

    p("Bảng được cấu hình mã hóa mặc định bằng AWS-owned key và gắn nhãn quản lý tài nguyên đồng bộ với hệ thống.")
    figure("Hình 3.18", ROOT / "evidence/tuan-1/E18c_dynamodb-tags.png", "Cấu hình mã hóa AWS-owned key và nhãn quản lý cho bảng DynamoDB")

    heading("3.6. Chuẩn bị Pillow Layer cơ sở và theo dõi ngân sách khởi tạo", level=2)
    p("Nhóm đóng gói thư viện Pillow 10.4.0 cho môi trường Python 3.12 kiến trúc x86_64 và tạo Lambda Layer cloud-photo-pillow phiên bản 1.")
    figure("Hình 3.19", ROOT / "evidence/tuan-1/E06a_pillow-layer-version.png", "Pillow Layer phiên bản 1 dành cho Python 3.12 và kiến trúc x86_64 trên AWS")

    p("Kết thúc phiên làm việc Tuần 1, nhóm kiểm tra trang quản lý Learner Lab. Ngân sách vẫn hiển thị Used $0 of $50, xác nhận toàn bộ quá trình thiết lập nền tảng hoàn toàn nằm trong mức sử dụng miễn phí.")
    figure("Hình 3.20", ROOT / "evidence/tuan-1/E20b_lab-budget-end.png", "Ngân sách Learner Lab sau phiên làm việc Tuần 1 (Used $0 of $50)")

    # =========================================================================
    # CHƯƠNG 4: KẾT QUẢ TRIỂN KHAI VÀ MINH CHỨNG THỰC TẾ TUẦN 2
    # =========================================================================
    heading("CHƯƠNG 4. KẾT QUẢ TRIỂN KHAI VÀ MINH CHỨNG THỰC TẾ TUẦN 2 (TÍCH HỢP HỆ THỐNG SERVERLESS)", level=1)
    p("Tuần 2 đánh dấu bước tiến quan trọng khi hệ thống được tích hợp hoàn chỉnh trên nền tảng Serverless AWS: kết nối S3 Trigger, triển khai hàm Lambda, lưu trữ siêu dữ liệu vào DynamoDB, ghi log vào CloudWatch và kiểm thử toàn diện qua 12 ca kiểm thử T01–T12.")

    heading("4.1. Triển khai Lambda Function và liên kết tài nguyên", level=2)
    p("Nhóm khởi tạo hàm Lambda cloud-photo-processor với runtime Python 3.12, kiến trúc x86_64, handler lambda_function.lambda_handler và gắn kết Pillow Layer phiên bản 1.")
    figure("Hình 4.1", ROOT / "evidence/tuan-2/trung/E08a_lambda-runtime-layer.png", "Runtime Python 3.12, handler và Pillow Layer được cấu hình cho hàm Lambda")

    p("Hàm Lambda được chỉ định Execution Role là LabRole để có quyền đọc ghi S3, cập nhật DynamoDB và ghi nhật ký CloudWatch Logs.")
    figure("Hình 4.2", ROOT / "evidence/tuan-2/trung/E07_lambda-execution-role.png", "Execution role LabRole được gắn cho hàm xử lý ảnh cloud-photo-processor")

    p("Cấu hình tài nguyên của hàm được thiết lập: Bộ nhớ RAM 512 MB, thời gian chờ tối đa (timeout) 30 giây và bộ nhớ đệm tạm thời /tmp 512 MB, đáp ứng thoải mái nhu cầu xử lý ảnh độ phân giải cao.")
    figure("Hình 4.3", ROOT / "evidence/tuan-2/trung/E08b_lambda-general-configuration.png", "Cấu hình bộ nhớ RAM 512 MB, timeout 30s và bộ nhớ đệm tạm thời cho Lambda")

    p("Nhóm thiết lập 4 biến môi trường để liên kết hàm với các tài nguyên AWS: DYNAMODB_TABLE=cloud-photo-metadata, OUTPUT_BUCKET=cloudphoto-output-103308504802, SIZES=150,400,1000 và WATERMARK_TEXT=CLOUD PHOTO.")
    figure("Hình 4.4", ROOT / "evidence/tuan-2/trung/E08c_lambda-environment-variables.png", "Bốn biến môi trường liên kết Lambda với S3 Output, DynamoDB và kích thước ảnh")

    p("Gói mã nguồn xử lý ảnh đã được biên dịch và tải lên AWS Lambda Function thành công.")
    figure("Hình 4.5", ROOT / "evidence/tuan-2/trung/E08d_lambda-code-uploaded.png", "Gói mã nguồn xử lý ảnh đã được tải lên AWS Lambda Function thành công")

    heading("4.2. Cấu hình S3 Event Notification Trigger", level=2)
    p("Trên bucket đầu vào cloudphoto-input-103308504802, nhóm cấu hình sự kiện S3 Event Notification lắng nghe sự kiện s3:ObjectCreated:* trên tiền tố uploads/ và chuyển tiếp trực tiếp đến hàm Lambda cloud-photo-processor.")
    figure("Hình 4.6", ROOT / "evidence/tuan-2/trung/E09_lambda-s3-trigger.png", "Cấu hình S3 Event Notification Trigger kích hoạt Lambda khi có sự kiện ObjectCreated")

    heading("4.3. Kiểm chứng luồng tải ảnh thực tế và chất lượng thumbnail", level=2)
    p("Nhóm thực hiện ca kiểm thử đầu tiên bằng cách tải tệp ảnh phong cảnh landscape.jpg (kích thước 1920 × 1200 pixel) vào thư mục uploads/ của bucket đầu vào.")
    figure("Hình 4.7", ROOT / "evidence/tuan-2/trung/E10_s3-input-landscape.png", "Ảnh gốc landscape.jpg được tải vào thư mục uploads/ của bucket đầu vào")

    p("Ngay lập tức, hàm Lambda được kích hoạt tự động. Kiểm tra bucket đầu ra cloudphoto-output-103308504802, hệ thống đã tạo thành công 3 tệp thumbnail JPEG tại tiền tố thumbnails/<image_id>/: thumb_150.jpg, thumb_400.jpg và thumb_1000.jpg.")
    figure("Hình 4.8", ROOT / "evidence/tuan-2/trung/E11_s3-output-three-thumbnails.png", "Ba phiên bản thumbnail JPEG (150px, 400px, 1000px) được tạo tự động trong output")

    p("Kiểm tra tệp thumb_1000.jpg: Kích thước đạt chính xác 1000 × 625 pixel (giữ đúng tỷ lệ 16:10 của ảnh gốc), watermark chữ 'CLOUD PHOTO' hiển thị rõ ràng và tinh tế ở góc dưới bên phải.")
    figure("Hình 4.9", ROOT / "evidence/tuan-2/trung/E12_thumbnail-watermark-dimensions.png", "Ảnh thumbnail 1000px có watermark CLOUD PHOTO và kích thước chuẩn 1000x625px")

    heading("4.4. Ghi nhận metadata trong DynamoDB và giám sát CloudWatch", level=2)
    p("Trong bảng DynamoDB cloud-photo-metadata, bản ghi của ảnh được tạo tự động với trạng thái COMPLETE, ghi nhận đầy đủ tên file gốc landscape.jpg, kích thước 1920x1200 và thời gian xử lý processing_time_ms.")
    figure("Hình 4.10", ROOT / "evidence/tuan-2/trung/E13a_dynamodb-complete-original.png", "DynamoDB ghi nhận trạng thái COMPLETE, thời gian xử lý và metadata của ảnh gốc")

    p("Mục variants trong bản ghi DynamoDB lưu trữ chi tiết từng kích thước: thumb_150 (150 × 93 px), thumb_400 (400 × 250 px) và thumb_1000 (1000 × 625 px) kèm đường dẫn S3 Key tương ứng.")
    figure("Hình 4.11", ROOT / "evidence/tuan-2/trung/E13c_dynamodb-variant-150.png", "Metadata chi tiết của phiên bản thumbnail 150px lưu trữ trong DynamoDB")
    figure("Hình 4.12", ROOT / "evidence/tuan-2/trung/E13d_dynamodb-variants-400-1000.png", "Metadata của phiên bản 400px và 1000px kèm S3 key lưu trữ trong DynamoDB")

    p("Kiểm tra CloudWatch Logs: Dòng nhật ký REPORT xác nhận hàm thực thi mất 1324 ms với lượng bộ nhớ tiêu thụ thực tế chỉ 102 MB trên tổng số 512 MB được cấp phát.")
    figure("Hình 4.13", ROOT / "evidence/tuan-2/trung/E14b_cloudwatch-report-details.png", "Nhật ký CloudWatch Logs REPORT ghi nhận thời gian thực thi 1324 ms và 102 MB RAM")

    p("Log group /aws/lambda/cloud-photo-processor được cấu hình chính sách lưu giữ nhật ký (Retention Period) là 7 ngày để tối ưu chi phí lưu trữ.")
    figure("Hình 4.14", ROOT / "evidence/tuan-2/trung/E14c_cloudwatch-retention-7-days.png", "Cấu hình thời gian lưu giữ nhật ký CloudWatch Logs Group là 7 ngày")

    p("Biểu đồ CloudWatch Metrics xác nhận tỷ lệ thực thi thành công 100%, không ghi nhận bất kỳ lỗi thực thi hay lỗi nghẽn tài nguyên (throttling) nào.")
    figure("Hình 4.15", ROOT / "evidence/tuan-2/trung/E15_lambda-monitor-metrics.png", "Biểu đồ giám sát CloudWatch Metrics theo dõi số lượng gọi hàm và thời gian chạy")

    heading("4.5. Kiểm chứng chống lặp vô tận và xử lý sự kiện trùng", level=2)
    p("Hệ thống được kiểm tra tính năng xử lý sự kiện trùng (Idempotency). Khi gửi lại cùng một sự kiện tạo ảnh, Lambda kiểm tra DynamoDB thấy trạng thái đã là COMPLETE nên tự động bỏ qua và trả về DUPLICATE_SKIPPED trong vòng 5.6 ms.")
    figure("Hình 4.16", ROOT / "evidence/tuan-2/trung/E19a_lambda-duplicate-response.png", "Lambda xử lý sự kiện trùng trả về kết quả DUPLICATE_SKIPPED")

    p("CloudWatch Logs ghi nhận rõ ràng: Lần gọi đầu ghi nhật ký COMPLETE, lần gọi thứ hai ghi nhận DUPLICATE_SKIPPED với cùng image_id.")
    figure("Hình 4.17", ROOT / "evidence/tuan-2/trung/E19b_cloudwatch-complete-duplicate.png", "CloudWatch Logs ghi nhận lần đầu COMPLETE và lần thứ hai DUPLICATE_SKIPPED")

    p("Kiểm tra thời gian sửa đổi (Last Modified) của 3 tệp thumbnail trong S3 Output: Thời gian hoàn toàn giữ nguyên mốc ban đầu, xác nhận không có hành vi ghi đè hay xử lý lặp thừa thãi.")
    figure("Hình 4.18", ROOT / "evidence/tuan-2/trung/E19c_s3-output-after-duplicate.png", "Bucket output giữ nguyên thời gian sửa đổi của các thumbnail khi gọi trùng")

    p("Để kiểm chứng khả năng chống lặp vô tận (Loop Prevention), nhóm cố tình tải một tệp trực tiếp vào bucket đầu ra cloudphoto-output-103308504802.")
    figure("Hình 4.19", ROOT / "evidence/tuan-2/trung/T09a_output-loop-check-upload.png", "Tải tệp trực tiếp vào bucket output để kiểm tra chống vòng lặp vô tận (Loop)")

    p("Kiểm tra CloudWatch Logs: Hoàn toàn không phát sinh bất kỳ log stream hay lệnh gọi Lambda nào mới. Điều này chứng minh cấu hình tách biệt hai bucket đã ngăn chặn 100% nguy cơ lặp vô tận.")
    figure("Hình 4.20", ROOT / "evidence/tuan-2/trung/T09b_cloudwatch-after-output-upload.png", "CloudWatch Logs xác nhận không phát sinh lệnh gọi Lambda khi tải vào output")

    p("Kiểm tra tab Properties của bucket đầu ra xác nhận không có bất kỳ Event Notification nào được cấu hình và tính năng EventBridge hoàn toàn tắt.")
    figure("Hình 4.21", ROOT / "evidence/tuan-2/trung/T09c_output-no-event-notifications.png", "Bucket output không cấu hình Event notifications và không bật EventBridge")

    heading("4.6. Kiểm chứng Web Gallery cục bộ và các dạng ảnh kiểm thử thực tế", level=2)
    p("Trong Tuần 2, ứng dụng Web Gallery được chạy thử nghiệm cục bộ kết nối trực tiếp với AWS để thực hiện bộ 12 ca kiểm thử T01–T12:")
    p("• Ca kiểm thử T01: Tải ảnh landscape.jpg, giao diện web hiển thị thẻ ảnh cùng 3 liên kết mở 3 kích thước thumbnail chuẩn xác.")
    figure("Hình 4.22", ROOT / "evidence/tuan-2/tuan/W2-L01_gallery-landscape-complete.png", "Web Gallery hiển thị ảnh landscape.jpg và 3 phiên bản thumbnail hoàn chỉnh")

    p("• Ca kiểm thử T02: Tải ảnh chụp chân dung dạng dọc portrait.jpg (900 × 1500 px). Ảnh thumbnail tạo ra có kích thước 90 × 150, 240 × 400 và 600 × 1000 px, giữ nguyên tỷ lệ khung hình đứng chuẩn xác.")
    figure("Hình 4.23", ROOT / "evidence/tuan-2/tuan/T02_gallery-portrait-complete.png", "Ảnh dọc portrait.jpg được thu nhỏ chính xác theo tỷ lệ gốc (T02)")

    p("• Ca kiểm thử T03: Tải ảnh vuông square.png (800 × 800 px). Cả 3 thumbnail đều có dạng vuông đều 150 × 150, 400 × 400 và 800 × 800 px.")
    figure("Hình 4.24", ROOT / "evidence/tuan-2/tuan/T03_gallery-square-complete.png", "Ảnh vuông square.png tạo đủ 3 kích thước 150x150, 400x400, 1000x1000 (T03)")

    p("• Ca kiểm thử T04: Tải ảnh logo có độ trong suốt transparent.png. Thuật toán xử lý thành công kênh alpha, tạo ra ảnh thumbnail trên nền trắng thuần sạch sẽ.")
    figure("Hình 4.25", ROOT / "evidence/tuan-2/tuan/T04_gallery-transparent-white-background.png", "Ảnh PNG có độ trong suốt được chuyển đổi sang nền trắng chuẩn JPEG (T04)")

    p("• Ca kiểm thử T05: Tải ảnh nhỏ small.png (80 × 60 px). Thuật toán áp dụng chính sách không phóng đại (no-upscale), cả 3 thumbnail đều giữ nguyên kích thước 80 × 60 px sắc nét.")
    figure("Hình 4.26", ROOT / "evidence/tuan-2/tuan/T05_gallery-small-no-upscale.png", "Ảnh nhỏ small.png giữ nguyên kích thước 80x60px, không bị phóng đại vỡ nét (T05)")

    p("• Ca kiểm thử T06: Tải tệp ảnh hỏng broken.jpg (chứa dữ liệu nhị phân rác). Web Gallery từ chối xử lý và hiển thị thông báo lỗi rõ ràng.")
    figure("Hình 4.27", ROOT / "evidence/tuan-2/tuan/T06_gallery-broken-rejected.png", "Web Gallery từ chối tệp ảnh hỏng broken.jpg và hiển thị cảnh báo (T06)")

    p("• Ca kiểm thử T07: Tải tệp có dung lượng vượt quá giới hạn 10 MiB. Giao diện web cảnh báo tệp quá lớn và endpoint API từ chối với mã lỗi HTTP 400 Bad Request.")
    figure("Hình 4.28", ROOT / "evidence/tuan-2/tuan/T07a_gallery-oversize-rejected.png", "Giao diện web chặn tệp vượt quá kích thước 10 MiB (T07)")
    figure("Hình 4.29", ROOT / "evidence/tuan-2/tuan/T07b_api-oversize-http-400.png", "Endpoint API trả về HTTP 400 Bad Request khi nhận tệp vượt 10 MiB (T07)")

    p("• Ca kiểm thử T10: Tải hai tệp cùng tên landscape.jpg nhưng nội dung khác nhau. Hệ thống băm mã SHA-256 nội dung để sinh hai image_id khác biệt, lưu trữ độc lập trong S3 và DynamoDB mà không bị xung đột.")
    figure("Hình 4.30", ROOT / "evidence/tuan-2/tuan/T10a_gallery-second-landscape-upload.png", "Tải 2 ảnh cùng tên khác nội dung được phân biệt bằng image_id băm (T10)")
    figure("Hình 4.31", ROOT / "evidence/tuan-2/tuan/T10b_api-landscape-second-key.png", "Khóa lưu trữ riêng biệt của ảnh thứ hai trong DynamoDB và S3 (T10)")

    p("• Ca kiểm thử T11 & T12: Kiểm tra an ninh ứng dụng web. Yêu cầu API lấy danh sách ảnh khi chưa đăng nhập bị chặn với HTTP 401 Unauthorized; yêu cầu tải ảnh thiếu CSRF Token bị máy chủ từ chối với HTTP 403 Forbidden.")
    figure("Hình 4.32", ROOT / "evidence/tuan-2/tuan/T11_api-photos-unauthorized.png", "API danh sách ảnh từ chối truy cập HTTP 401 khi chưa đăng nhập (T11)")
    figure("Hình 4.33", ROOT / "evidence/tuan-2/tuan/T12_upload-missing-csrf-403.png", "Yêu cầu POST tải ảnh thiếu CSRF Token bị máy chủ chặn với HTTP 403 (T12)")

    # =========================================================================
    # CHƯƠNG 5: KẾT QUẢ TRIỂN KHAI VÀ MINH CHỨNG THỰC TẾ TUẦN 3
    # =========================================================================
    heading("CHƯƠNG 5. KẾT QUẢ TRIỂN KHAI VÀ MINH CHỨNG THỰC TẾ TUẦN 3 (TRIỂN KHAI EC2 & 2 YÊU CẦU NÂNG CAO)", level=1)
    p("Tuần 3 là bước ngoặt hoàn thiện kiến trúc hệ thống khi đưa toàn bộ Web Gallery lên máy chủ đám mây Amazon EC2 và hoàn thành xuất sắc 2 yêu cầu nâng cao do GVHD giao phó.")

    heading("5.1. Hai yêu cầu nâng cao của GVHD: Pillow Lambda Layer & S3 Lifecycle Rule", level=2)
    p("• Yêu cầu Nâng cao 1 — Tách Pillow thành Lambda Layer độc lập: Nhóm đã tách toàn bộ thư viện Pillow sang Layer cloud-photo-pillow v1. Gói deploy zip của Lambda Function cloud-photo-processor giảm từ >15 MB xuống chỉ còn vỏn vẹn 3.7 kB.")
    figure("Hình 5.1", ROOT / "evidence/tuan-3/trung/E22_lambda-layer-code-size.png", "Gói mã Lambda tối ưu dung lượng siêu nhẹ 3.7 kB và gắn Pillow Layer phiên bản 1")

    p("Nhờ dung lượng siêu nhỏ 3.7 kB, mã nguồn của hàm (gồm lambda_function.py và image_tools.py) có thể mở xem và chỉnh sửa trực tiếp ngay trên AWS Console Code Editor, mang lại sự thuận tiện vượt trội khi cần tinh chỉnh nhanh mã nguồn.")
    figure("Hình 5.2", ROOT / "evidence/tuan-3/trung/E22_lambda-code-editor.png", "Mã nguồn Lambda chỉ gồm 2 tệp python mở và sửa trực tiếp trên AWS Console Code Editor")

    p("• Yêu cầu Nâng cao 2 — Thiết lập S3 Lifecycle Rule tự động dọn thumbnail sau 7 ngày: Trên bucket đầu ra cloudphoto-output-103308504802, nhóm cấu hình quy tắc auto-cleanup-old-thumbnails-7days áp dụng cho toàn bộ các đối tượng trong bucket.")
    figure("Hình 5.3", ROOT / "evidence/tuan-3/trung/E23a1_s3-output-lifecycle-rule-config.png", "Cấu hình quy tắc S3 Lifecycle Rule auto-cleanup-old-thumbnails-7days cho toàn bucket output")

    p("Quy tắc thiết lập hai hành động tự động: Hết hạn và xóa vĩnh viễn các đối tượng sau 7 ngày kể từ ngày tạo; đồng thời tự động xóa các phần tải lên multipart dang dở (incomplete multipart uploads) sau 7 ngày.")
    figure("Hình 5.4", ROOT / "evidence/tuan-3/trung/E23a2_s3-output-lifecycle-rule-actions.png", "Cấu hình hành động hết hạn đối tượng sau 7 ngày và xóa multipart upload sau 7 ngày")

    p("Quy tắc Lifecycle Rule hiển thị ở trạng thái Enabled trong tab Management của bucket đầu ra, đảm bảo chính sách tối ưu chi phí lưu trữ luôn có hiệu lực.")
    figure("Hình 5.5", ROOT / "evidence/tuan-3/trung/E23b_s3-output-lifecycle-rule-list.png", "Quy tắc Lifecycle Rule trạng thái Enabled trong tab Management của bucket output")

    heading("5.2. Khởi tạo máy chủ Amazon EC2 và thiết lập dịch vụ Web Gallery", level=2)
    p("Nhóm khởi tạo máy chủ EC2 tên cloud-photo-gallery (Instance ID i-0390fda0b0a75c002), loại t2.micro, chạy hệ điều hành Amazon Linux 2023 tại Subnet us-east-1d, trạng thái Running.")
    figure("Hình 5.6", ROOT / "evidence/tuan-3/tuan/E16a_ec2-instance-running.png", "Máy chủ EC2 cloud-photo-gallery (i-0390fda0b0a75c002) trạng thái Running tại us-east-1d")

    p("Máy chủ EC2 được gắn IAM Role LabRole thông qua LabInstanceProfile và được bảo vệ bởi Security Group cloud-photo-web-sg.")
    figure("Hình 5.7", ROOT / "evidence/tuan-3/tuan/E16b_ec2-iam-role-labinstanceprofile.png", "Máy chủ EC2 được gắn IAM Role LabRole qua LabInstanceProfile và Security Group web")

    p("Cấu hình Security Group chỉ mở 2 cổng cần thiết: Cổng 22 cho quản trị từ xa qua SSH và cổng 8000 cho dịch vụ web.")
    figure("Hình 5.8", ROOT / "evidence/tuan-3/tuan/E16c_ec2-security-group-rules.png", "Security Group cloud-photo-web-sg mở cổng 22 (SSH) và cổng 8000 (Custom TCP)")

    p("Ứng dụng Web Gallery được khởi chạy bằng Gunicorn 26.2.0 (2 workers) dưới sự quản lý của systemd service cloud-photo.service, trạng thái active (running).")
    figure("Hình 5.9", ROOT / "evidence/tuan-3/tuan/E16d_ec2-systemd-service-active.png", "Dịch vụ systemd cloud-photo chạy nền với Gunicorn 26.2.0 ở trạng thái Active (running)")

    p("Kiểm tra endpoint sức khỏe nội bộ curl http://127.0.0.1:8000/health trả về kết quả JSON {'status':'ok'} với mã trạng thái HTTP 200 OK.")
    figure("Hình 5.10", ROOT / "evidence/tuan-3/tuan/E16e_ec2-curl-health-check.png", "Kiểm tra endpoint sức khỏe curl http://127.0.0.1:8000/health trả về status ok (HTTP 200)")

    heading("5.3. Vận hành Web Gallery và giao diện người dùng trên EC2", level=2)
    p("Người dùng mở đường hầm bảo mật SSH Tunnel: ssh -i labsuser.pem -L 8080:localhost:8000 ec2-user@<IP_EC2> và truy cập giao diện đăng nhập tại http://localhost:8080/login.")
    figure("Hình 5.11", ROOT / "evidence/tuan-3/tuan/E17a_ec2-gallery-login.png", "Giao diện đăng nhập Gallery trên máy chủ EC2 qua SSH Tunnel tại http://localhost:8080/login")

    p("Sau khi đăng nhập thành công, giao diện Dashboard hiển thị khu vực kéo thả tệp ảnh, các tùy chọn kích thước và nút tải ảnh an toàn.")
    figure("Hình 5.12", ROOT / "evidence/tuan-3/tuan/E17b1_ec2-gallery-upload-dashboard.png", "Dashboard Web Gallery trên EC2 hiển thị khu vực kéo thả và tải ảnh lên an toàn")

    p("Khu vực Gallery hiển thị danh sách ảnh người dùng đã tải lên, truy vấn dữ liệu từ DynamoDB và nạp trực tiếp 3 kích thước thumbnail thông qua Presigned URL.")
    figure("Hình 5.13", ROOT / "evidence/tuan-3/tuan/E17b2_ec2-gallery-cards-complete.png", "Bộ sưu tập ảnh trên Web Gallery EC2 truy vấn DynamoDB và hiển thị 3 kích thước thumbnail")

    heading("5.4. Kiểm thử bảo mật IAM Role và Presigned URL", level=2)
    p("Từ terminal EC2, nhóm thực hiện các lệnh aws s3 ls và aws dynamodb describe-table mà không cần cấu hình Access Key hay cấu hình aws configure. Các lệnh đều thành công nhờ quyền tự động từ LabInstanceProfile (IMDSv2).")
    figure("Hình 5.14", ROOT / "evidence/tuan-3/tuan/E24a_ec2-iam-role-access-test.png", "Kiểm tra lệnh aws s3 ls và describe-table từ EC2 thành công qua quyền LabInstanceProfile (IMDSv2)")

    p("Kiểm tra mở trực tiếp URL đối tượng S3 trong trình duyệt mà không có chữ ký presigned: AWS lập tức từ chối với mã lỗi HTTP 403 AccessDenied, chứng minh bucket đầu ra được bảo vệ riêng tư tuyệt đối.")
    figure("Hình 5.15", ROOT / "evidence/tuan-3/tuan/E24b_s3-direct-access-denied.png", "Truy cập trực tiếp URL S3 không có presigned token bị từ chối với HTTP 403 AccessDenied")

    p("Người dùng mở ảnh thông qua Presigned URL do Web Gallery sinh ra: Ảnh hiển thị hoàn hảo với kích thước chuẩn 1000px và watermark rõ nét trong thời hạn hiệu lực 300 giây.")
    figure("Hình 5.16", ROOT / "evidence/tuan-3/tuan/E24c_presigned-url-valid.png", "Mở ảnh thumbnail 1000px có watermark qua Presigned URL có thời hạn X-Amz-Expires=300")

    p("Sau khi chờ quá 300 giây, truy cập lại chính liên kết Presigned URL trên: AWS từ chối phục vụ và trả về tài liệu XML với thông báo lỗi Request has expired.")
    figure("Hình 5.17", ROOT / "evidence/tuan-3/tuan/E24d_presigned-url-expired.png", "Truy cập lại Presigned URL sau 300 giây bị từ chối với XML Request has expired")

    heading("5.5. Kiểm thử độ bền systemd và luồng xử lý ảnh End-to-End", level=2)
    p("Nhóm thực hiện kiểm tra cơ chế tự phục hồi dịch vụ bằng lệnh sudo systemctl restart cloud-photo. Service khởi động lại tức thì với PID mới 31812 và uptime ổn định.")
    figure("Hình 5.18", ROOT / "evidence/tuan-3/tuan/E25a_ec2-systemd-restart-test.png", "Khởi động lại dịch vụ cloud-photo thành công với PID mới 31812 và khôi phục hoạt động tức thì")

    p("Tải lại trang Web Gallery: Ứng dụng tiếp tục hoạt động trơn tru mà không làm gián đoạn phiên làm việc của người dùng.")
    figure("Hình 5.19", ROOT / "evidence/tuan-3/tuan/E25b_ec2-gallery-post-restart.png", "Web Gallery tải lại và hoạt động ổn định trên EC2 sau khi restart dịch vụ nền")

    p("Kiểm thử luồng xử lý ảnh hoàn chỉnh từ đầu đến cuối (End-to-End): Người dùng tải ảnh portrait.jpg qua Web EC2, hệ thống tiếp nhận, tải lên S3 Input, kích hoạt Lambda, tạo 3 thumbnail và hiển thị trạng thái COMPLETE trong vòng vài giây.")
    figure("Hình 5.20", ROOT / "evidence/tuan-3/tuan/E26a_ec2-upload-success-complete.png", "Tải ảnh mới portrait.jpg qua Web EC2 thành công COMPLETE (900x1500px, 27.8 KiB)")

    p("CloudWatch Logs ghi nhận toàn bộ quá trình xử lý của Lambda chỉ mất 604.68 ms với bộ nhớ tiêu thụ 153 MB, xác nhận hiệu năng tối ưu vượt trội của hệ thống.")
    figure("Hình 5.21", ROOT / "evidence/tuan-3/tuan/E26b_ec2-cloudwatch-lambda-log.png", "CloudWatch ghi nhận COMPLETE image_id cb2147cc1cad5b61f734f66ef8e56... và duration 604.68 ms")

    # =========================================================================
    # CHƯƠNG 6: KẾT QUẢ TRIỂN KHAI VÀ MINH CHỨNG THỰC TẾ TUẦN 4
    # =========================================================================
    heading("CHƯƠNG 6. KẾT QUẢ TRIỂN KHAI VÀ MINH CHỨNG THỰC TẾ TUẦN 4 (HẠCH TOÁN CHI PHÍ, VIDEO DEMO & TEARDOWN)", level=1)
    p("Tuần 4 là giai đoạn chốt đồ án cuối kỳ, tập trung vào 4 nhiệm vụ cốt lõi theo đúng yêu cầu của GVHD: Hạch toán chi phí AWS, quay video demo sản phẩm hoàn chỉnh, thực hiện quy trình dọn dẹp tài nguyên và tổng kết báo cáo.")

    heading("6.1. Hạch toán chi phí AWS và ngân sách phòng lab", level=2)
    p("Nhóm đối chiếu trang chủ AWS Academy Learner Lab sau 4 tuần triển khai. Chỉ số ngân sách ghi nhận Used $0 of $50, minh chứng toàn bộ quá trình phát triển và kiểm thử đồ án được tối ưu chi phí xuất sắc, nằm gọn trong hạn mức miễn phí.")
    figure("Hình 6.1", ROOT / "evidence/tuan-4/trung/E27_aws-cost-breakdown.png", "Hạn mức ngân sách AWS Academy Learner Lab ghi nhận Used $0 of $50 và bảng hạch toán chi phí")

    heading("6.2. Video Demo sản phẩm hoàn chỉnh trên Google Drive", level=2)
    p("Nhóm đã tiến hành quay và biên tập video thực nghiệm sản phẩm hoàn chỉnh Full HD với thời lượng 8 phút 45 giây (tuân thủ nghiêm ngặt yêu cầu không quá 10 phút của GVHD). Video được xuất bản trên Google Drive:")
    p("• Liên kết video demo: ")
    p_vid = p()
    link(p_vid, "Demo Xu Ly Anh Tu Dong AWS (24110363 - 24110369).mp4", VIDEO_URL)
    figure("Hình 6.2", ROOT / "evidence/tuan-4/tuan/E28_demo-video-link.png", "Minh chứng video demo sản phẩm hoàn chỉnh trên Google Drive thời lượng 8 phút 45 giây")

    heading("6.3. Quy trình dọn dẹp tài nguyên sau demo (Teardown)", level=2)
    p("Sau khi hoàn tất quay video demo và thu thập toàn bộ dữ liệu kiểm thử, nhóm tiến hành dọn dẹp tài nguyên trên AWS theo đúng thứ tự phụ thuộc an toàn để bảo toàn ngân sách đám mây:")
    p("1. Hủy máy chủ EC2 cloud-photo-gallery (i-0390fda0b0a75c002), chuyển trạng thái sang Terminated.")
    figure("Hình 6.3", ROOT / "evidence/tuan-4/trung/E29a_ec2-instance-terminated.png", "Kiểm chứng máy chủ EC2 i-0390fda0b0a75c002 đã chuyển sang trạng thái Terminated")

    p("2. Làm rỗng (Empty) và xóa hoàn toàn 2 bucket S3 (cloudphoto-input-103308504802 và cloudphoto-output-103308504802). Giao diện S3 Console xác nhận General purpose buckets (0).")
    figure("Hình 6.4", ROOT / "evidence/tuan-4/trung/E29b_s3-buckets-deleted.png", "Kiểm chứng toàn bộ các kho lưu trữ Amazon S3 (General purpose buckets: 0) đã được xóa sạch")

    p("3. Xóa hoàn toàn bảng cơ sở dữ liệu DynamoDB cloud-photo-metadata. Giao diện DynamoDB Console xác nhận Tables (0).")
    figure("Hình 6.5", ROOT / "evidence/tuan-4/trung/E29c_dynamodb-tables-deleted.png", "Kiểm chứng toàn bộ các bảng cơ sở dữ liệu Amazon DynamoDB (Tables: 0) đã được xóa sạch")

    # =========================================================================
    # CHƯƠNG 7: TỔNG HỢP KIỂM THỬ VÀ PHÂN TÍCH KINH TẾ TOÀN BỘ ĐỒ ÁN
    # =========================================================================
    heading("CHƯƠNG 7. TỔNG HỢP KIỂM THỬ VÀ PHÂN TÍCH KINH TẾ TOÀN BỘ ĐỒ ÁN", level=1)
    
    heading("7.1. Bảng ma trận tổng hợp toàn diện 22 ca kiểm thử (T01 – T22)", level=2)
    p("Bảng 7.1 tổng hợp toàn diện 22 ca kiểm thử (T01 – T22) được thực hiện trong suốt 4 tuần dự án. 100% ca kiểm thử đều đạt kết quả ĐẠT với các quan sát thực tế minh bạch trên AWS:")

    t71_headers = ["Mã ca", "Tên ca kiểm thử & Mô tả", "Đầu vào kiểm thử", "Kết quả quan sát thực tế trên AWS", "Đánh giá"]
    t71_rows = [
        ["T01", "Xử lý ảnh phong cảnh (Landscape)", "landscape.jpg (1920x1200 px)", "Tạo 3 thumbnail (150x93, 400x250, 1000x625); watermark rõ nét; COMPLETE trong 1324 ms.", "ĐẠT"],
        ["T02", "Xử lý ảnh chân dung (Portrait)", "portrait.jpg (900x1500 px)", "Tạo 3 thumbnail (90x150, 240x400, 600x1000); giữ nguyên tỷ lệ dọc; COMPLETE trong 604 ms.", "ĐẠT"],
        ["T03", "Xử lý ảnh vuông (Square)", "square.png (800x800 px)", "Tạo 3 thumbnail vuông chuẩn (150x150, 400x400, 800x800); COMPLETE.", "ĐẠT"],
        ["T04", "Chuẩn hóa ảnh PNG trong suốt", "transparent.png (kênh alpha)", "Chuyển đổi sang nền trắng thuần RGB; xuất thumbnail JPEG chất lượng cao.", "ĐẠT"],
        ["T05", "Ảnh nhỏ không phóng đại (No-upscale)", "small.png (80x60 px)", "Cả 3 phiên bản giữ nguyên 80x60 px; không phóng đại vỡ nét.", "ĐẠT"],
        ["T06", "Từ chối tệp ảnh hỏng (Corrupted)", "broken.jpg (dữ liệu nhị phân rác)", "Hệ thống phát hiện lỗi định dạng; trả về cảnh báo; không gây sập worker.", "ĐẠT"],
        ["T07", "Từ chối tệp vượt dung lượng", "oversize.jpg (12.5 MiB > 10 MiB)", "Giao diện cảnh báo tệp quá lớn; API từ chối với HTTP 400 Bad Request.", "ĐẠT"],
        ["T08", "Xử lý sự kiện trùng (Idempotency)", "Gửi lại sự kiện của T01", "Kiểm tra DynamoDB thấy COMPLETE; trả về DUPLICATE_SKIPPED trong 5.6 ms; không ghi đè S3.", "ĐẠT"],
        ["T09", "Chống vòng lặp vô tận (Loop)", "Tải tệp trực tiếp vào bucket output", "Không phát sinh sự kiện Lambda; CloudWatch không tăng invocation; xác nhận an toàn 100%.", "ĐẠT"],
        ["T10", "Hai ảnh cùng tên khác nội dung", "2 ảnh landscape.jpg (hash khác)", "Băm SHA-256 sinh 2 image_id khác biệt; lưu 2 bộ thumbnail riêng rẽ; không xung đột.", "ĐẠT"],
        ["T11", "Chặn truy cập khi chưa đăng nhập", "Gọi GET /api/photos khi logout", "Máy chủ chặn truy cập và chuyển hướng về trang đăng nhập với HTTP 401 Unauthorized.", "ĐẠT"],
        ["T12", "Chặn tấn công CSRF", "POST /upload thiếu CSRF Token", "Máy chủ Flask-WTF chặn đứng yêu cầu với mã lỗi HTTP 403 Forbidden.", "ĐẠT"],
        ["T13", "Bảo mật IAM Role IMDSv2 trên EC2", "aws s3 ls từ terminal EC2", "Thực thi thành công qua LabInstanceProfile; không cần cấu hình Access Key tĩnh.", "ĐẠT"],
        ["T14", "Chặn truy cập trực tiếp S3 Output", "Mở URL trực tiếp của S3", "Bị chặn với HTTP 403 AccessDenied; bucket output hoàn toàn Private.", "ĐẠT"],
        ["T15", "Xem ảnh qua Presigned URL 300s", "Presigned URL trong vòng 300s", "Trình duyệt mở ảnh thành công 200 OK; đầy đủ 3 kích thước và watermark.", "ĐẠT"],
        ["T16", "Presigned URL hết hạn sau 300s", "Truy cập Presigned URL sau 300s", "Bị từ chối với tài liệu XML Request has expired; ngăn ngừa chia sẻ link rò rỉ.", "ĐẠT"],
        ["T17", "Khả năng tự phục hồi dịch vụ web", "sudo systemctl restart cloud-photo", "Dịch vụ tái sinh tức thì với PID mới 31812; trang web tải lại ổn định.", "ĐẠT"],
        ["T18", "Tối ưu gói Lambda Layer Pillow", "Kiểm tra gói deploy Lambda", "Gói deploy giảm còn 3.7 kB; mở và chỉnh sửa trực tiếp trên AWS Console Code Editor.", "ĐẠT"],
        ["T19", "Cấu hình S3 Lifecycle Rule 7 ngày", "Kiểm tra tab Management của S3", "Quy tắc auto-cleanup-old-thumbnails-7days Enabled; tự xóa ảnh sau 7 ngày.", "ĐẠT"],
        ["T20", "Hạch toán chi phí phòng lab AWS", "Kiểm tra ngân sách Learner Lab", "Used $0 of $50; chi phí thực tế phát sinh ước tính chỉ ~$0.52 USD.", "ĐẠT"],
        ["T21", "Video demo sản phẩm hoàn chỉnh", "Kiểm tra video trên Google Drive", "Thời lượng 8:45 (< 10 phút); Full HD; kịch bản phân cảnh rõ ràng; thuyết minh tiếng Việt.", "ĐẠT"],
        ["T22", "Quy trình dọn dẹp tài nguyên", "Kiểm tra Console sau teardown", "EC2 Terminated, S3 Buckets = 0, DynamoDB Tables = 0; sạch sẽ 100%.", "ĐẠT"],
    ]
    table(t71_headers, t71_rows, [1.4, 3.8, 3.0, 5.8, 1.5])

    heading("7.2. Phân tích kinh tế chi tiết và bảng định giá các dịch vụ AWS us-east-1", level=2)
    p("Để chứng minh tính khả thi kinh tế của đề tài khi chuyển giao từ môi trường học tập sang ứng dụng thực tiễn, nhóm xây dựng bảng định giá chi tiết các dịch vụ AWS tại Region us-east-1:")

    t72_headers = ["Dịch vụ AWS", "Đơn vị tính phí", "Đơn giá chính thức (us-east-1)", "Mức sử dụng miễn phí (Free Tier hàng tháng)"]
    t72_rows = [
        ["Amazon EC2 (t2.micro)", "Giờ hoạt động (Instance-hour)", "$0.0116 USD / giờ (~$8.35 USD / tháng)", "750 giờ t2.micro/t3.micro mỗi tháng (trong 12 tháng đầu)."],
        ["Amazon EBS (General Purpose gp3)", "Dung lượng lưu trữ (GB-tháng)", "$0.08 USD / GB-tháng", "30 GB dung lượng lưu trữ EBS miễn phí."],
        ["Amazon S3 (Standard Storage)", "Dung lượng lưu trữ (GB-tháng)", "$0.023 USD / GB-tháng (cho 50 TB đầu)", "5 GB Standard Storage miễn phí hàng tháng."],
        ["Amazon S3 PUT / POST requests", "Số lượng yêu cầu (1,000 requests)", "$0.005 USD / 1,000 requests", "2,000 yêu cầu PUT/POST miễn phí hàng tháng."],
        ["Amazon S3 GET requests", "Số lượng yêu cầu (1,000 requests)", "$0.0004 USD / 1,000 requests", "20,000 yêu cầu GET miễn phí hàng tháng."],
        ["AWS Lambda (Thời gian chạy)", "GB-giây (GB-seconds)", "$0.0000166667 USD / GB-giây", "400,000 GB-giây miễn phí vĩnh viễn mỗi tháng."],
        ["AWS Lambda (Số lần gọi)", "Triệu yêu cầu (1M requests)", "$0.20 USD / 1,000,000 requests", "1,000,000 yêu cầu miễn phí vĩnh viễn mỗi tháng."],
        ["Amazon DynamoDB (Storage)", "Dung lượng lưu trữ (GB-tháng)", "$0.25 USD / GB-tháng", "25 GB lưu trữ miễn phí vĩnh viễn."],
        ["Amazon DynamoDB (WRU / RRU)", "Triệu đơn vị đọc ghi (1M units)", "$1.25 / 1M WRU; $0.25 / 1M RRU", "25 WCU và 25 RCU miễn phí vĩnh viễn."],
        ["Amazon CloudWatch Logs", "Dung lượng nạp (GB ingested)", "$0.50 USD / GB", "5 GB log nạp miễn phí mỗi tháng."],
    ]
    table(t72_headers, t72_rows, [3.5, 3.2, 4.0, 4.8])

    heading("7.3. So sánh hiệu quả kinh tế: Serverless Architecture vs Monolith EC2", level=2)
    p("Nhóm tiến hành phân tích kinh tế toàn diện đối chiếu giữa 2 mô hình kiến trúc ở quy mô doanh nghiệp vừa và nhỏ (tiếp nhận 10,000 ảnh/tháng):")

    t73_headers = ["Tiêu chí đánh giá", "Mô hình Serverless (Kiến trúc đồ án)", "Mô hình truyền thống (Monolith EC2)", "Ưu thế của Serverless"]
    t73_rows = [
        ["Chi phí máy chủ tính toán", "Lambda: $0.11 USD / tháng (chỉ trả khi có ảnh cần xử lý).", "EC2 c5.large: $61.20 USD / tháng (phải chạy 24/7 để chờ xử lý).", "Tiết kiệm hơn 99% chi phí điện toán."],
        ["Chi phí máy chủ Web", "EC2 t2.micro: $8.35 USD / tháng (chỉ làm web proxy nhẹ nhàng).", "Đã gộp chung trong máy chủ c5.large.", "Tách biệt tải tĩnh và tác vụ tính toán nặng."],
        ["Chi phí lưu trữ S3 & DynamoDB", "S3: $0.75 USD; DynamoDB: $0.05 USD / tháng.", "Lưu ổ cứng EBS: ~$4.80 USD / tháng.", "Lưu trữ S3 an toàn 99.999999999% và rẻ hơn."],
        ["Tổng chi phí hàng tháng", "~$9.26 – $13.21 USD / tháng.", "~$66.00 – $75.00 USD / tháng.", "Tiết kiệm hơn 85% tổng chi phí vận hành."],
        ["Khả năng co giãn (Scalability)", "Tự động co giãn tức thì từ 1 đến hàng nghìn ảnh đồng thời.", "Bị giới hạn bởi số CPU của máy chủ; dễ nghẽn khi có đợt tải đột biến.", "Khả năng co giãn không giới hạn (Zero-maintenance scaling)."],
        ["Độ tin cậy & Sẵn sàng", "S3 và Lambda có tính sẵn sàng 99.99% trên nhiều Availability Zones.", "Đơn điểm lỗi (Single Point of Failure); sập máy chủ là sập toàn bộ web.", "Cách ly lỗi hoàn hảo; web không bao giờ bị nghẽn do xử lý ảnh."],
    ]
    table(t73_headers, t73_rows, [3.2, 4.2, 4.3, 3.8])

    heading("7.4. Kịch bản phân cảnh chi tiết video demo sản phẩm hoàn chỉnh", level=2)
    p("Bảng 7.4 trình bày kịch bản phân cảnh chi tiết từng phút của video demo sản phẩm (thời lượng 8:45, phân vai Trung và Tuấn):")

    t74_headers = ["Phân cảnh & Thời gian", "Người thực hiện", "Nội dung thuyết minh & Thao tác màn hình", "Mục tiêu nghiệm thu"]
    t74_rows = [
        ["Phần 1 (0:00 – 1:30)\nGiới thiệu & Kiến trúc", "Trung", "Giới thiệu đề tài, giảng viên hướng dẫn TS. Huỳnh Xuân Phụng, thành viên nhóm. Trình chiếu sơ đồ kiến trúc Figure 2.1 kết hợp EC2 IaaS và cụm Serverless S3, Lambda, DynamoDB, CloudWatch.", "Xác lập bối cảnh đồ án và tính nhất quán kiến trúc."],
        ["Phần 2 (1:30 – 3:30)\nKhởi tạo & Cấu hình AWS", "Trung", "Trình diễn máy chủ EC2 running, IAM Role LabInstanceProfile, Security Group mở cổng 22/8000, 2 S3 buckets Block Public Access On, DynamoDB Active và CloudWatch log retention 7 ngày.", "Minh chứng toàn bộ tài nguyên nền tảng AWS."],
        ["Phần 3 (3:30 – 5:15)\nHai yêu cầu Nâng cao", "Trung", "Trình chiếu gói deploy Lambda 3.7 kB gắn Pillow Layer v1; mở và sửa code trực tiếp trên Console Editor; trình chiếu S3 Lifecycle Rule 7 ngày auto-cleanup-old-thumbnails-7days Enabled.", "Nghiệm thu trọn vẹn 2 yêu cầu nâng cao của GVHD."],
        ["Phần 4 (5:15 – 7:00)\nWeb Gallery & Bảo mật", "Tuấn", "Mở SSH Tunnel 8080, đăng nhập Web Gallery trên EC2. Tải ảnh landscape.jpg, portrait.jpg và transparent.png. Trình diễn 3 thumbnail hiển thị chuẩn xác, watermark CLOUD PHOTO.", "Nghiệm thu Web Gallery và thuật toán xử lý ảnh."],
        ["Phần 5 (7:00 – 8:00)\nKiểm chứng An ninh", "Tuấn", "Mở trực tiếp link S3 bị 403 AccessDenied; mở Presigned URL 300s hiển thị ảnh; giải thích cơ chế hết hạn; kiểm tra restart systemd service cloud-photo và khôi phục hoạt động tức thì.", "Nghiệm thu 3 lớp bảo mật và độ bền systemd."],
        ["Phần 6 (8:00 – 8:45)\nHạch toán & Tổng kết", "Tuấn & Trung", "Trình chiếu hạn mức Used $0 of $50 trên Learner Lab; bảng hạch toán chi phí tiết kiệm >85%; tóm tắt quy trình dọn dẹp tài nguyên (Teardown); lời cảm ơn gửi đến GVHD.", "Tổng kết và hoàn thành buổi nghiệm thu."],
    ]
    table(t74_headers, t74_rows, [2.5, 2.0, 8.2, 2.8])

    heading("7.5. Kịch bản dọn dẹp tài nguyên an toàn (Teardown Automation)", level=2)
    p("Để đảm bảo việc xóa tài nguyên không gặp lỗi xung đột khóa ngoại hoặc lỗi xóa bucket không rỗng, nhóm đã xây dựng script tự động hóa scripts/teardown_resources.py và quy định thứ tự phụ thuộc nghiêm ngặt:")
    p("• Bước 1: Dừng và hủy máy chủ EC2 (Terminate Instance) để ngắt hoàn toàn kết nối vào S3 và DynamoDB.")
    p("• Bước 2: Xóa quy tắc S3 Event Notification trên bucket đầu vào để ngắt kích hoạt Lambda.")
    p("• Bước 3: Làm rỗng (Empty) toàn bộ các đối tượng và các phiên bản đối tượng cũ trong cả 2 bucket S3, sau đó tiến hành xóa bucket.")
    p("• Bước 4: Xóa hàm AWS Lambda cloud-photo-processor và Lambda Layer.")
    p("• Bước 5: Xóa bảng cơ sở dữ liệu Amazon DynamoDB cloud-photo-metadata.")
    p("• Bước 6: Xóa nhóm nhật ký Amazon CloudWatch Logs Group /aws/lambda/cloud-photo-processor.")

    # =========================================================================
    # CHƯƠNG 8: TỔ CHỨC THỰC HIỆN, KHAI BÁO SỬ DỤNG AI VÀ ĐỐI CHIẾU MÃ NGUỒN
    # =========================================================================
    heading("CHƯƠNG 8. TỔ CHỨC THỰC HIỆN, KHAI BÁO SỬ DỤNG AI VÀ ĐỐI CHIẾU MÃ NGUỒN", level=1)
    
    heading("8.1. Bảng phân công công việc chi tiết và tỷ lệ đóng góp của từng thành viên", level=2)
    p("Trong suốt 4 tuần triển khai đồ án, hai sinh viên đã phối hợp nhịp nhàng, phân công trách nhiệm rõ ràng và đóng góp công sức đồng đều 50% – 50%:")

    t81_headers = ["Thành viên", "Phần việc chính đảm nhiệm xuyên suốt 4 tuần", "Sản phẩm cụ thể", "Tỷ lệ đóng góp"]
    t81_rows = [
        ["Bùi Nguyễn Duy Trung\nMSSV: 24110363", "Chủ trì cấu hình hạ tầng AWS Serverless (S3, Lambda, DynamoDB, CloudWatch, IAM Role); nghiên cứu và tối ưu 2 yêu cầu nâng cao (Pillow Lambda Layer 3.7 kB, S3 Lifecycle Rule 7 ngày); xây dựng script dọn dẹp tài nguyên teardown; lập bảng dữ liệu chi phí costs.csv; thuyết minh phần 1–3 video demo.", "Mã nguồn lambda_function.py, build_packages.py, teardown_resources.py; cấu hình AWS Serverless; 12 minh chứng Tuần 2; 5 minh chứng Tuần 3; 4 minh chứng Tuần 4.", "50%"],
        ["Đỗ Anh Tuấn\nMSSV: 24110369", "Chủ trì phát triển ứng dụng Web Gallery (Flask, Gunicorn WSGI, Bootstrap 5); thiết lập máy chủ EC2 (Amazon Linux 2023, systemd cloud-photo.service, SSH Tunnel); kiểm thử bảo mật Presigned URL 300s và lỗi 403; thực hiện bộ 22 ca kiểm thử T01–T22; quay và biên tập video demo Full HD; thuyết minh phần 4–6 video demo.", "Mã nguồn app.py, cloud-photo.service; bộ kiểm thử tests/; video demo 8:45 trên Google Drive; 17 minh chứng Tuần 2; 16 minh chứng Tuần 3; 1 minh chứng Tuần 4.", "50%"],
    ]
    table(t81_headers, t81_rows, [3.2, 5.5, 5.3, 1.5])

    heading("8.2. Danh mục toàn bộ các commit trên GitHub trong suốt 4 tuần dự án", level=2)
    p("Toàn bộ tiến độ phát triển được lưu vết minh bạch trên kho mã nguồn GitHub bndt0103/aws-thumbnail. Bảng 8.2 liệt kê các commit chính đại diện cho các mốc hoàn thành qua 4 tuần:")

    t82_headers = ["Tuần", "Mã Commit (SHA)", "Tác giả", "Thông điệp Commit & Nội dung hoàn thành trên GitHub"]
    t82_rows = [
        ["Tuần 1", "7fa41c0", "Trung & Tuấn", "Khởi tạo cấu trúc dự án, module xử lý ảnh Pillow và 19 ca kiểm thử Unit test cục bộ đạt 100%."],
        ["Tuần 1", "3c98d1a", "Trung", "Khởi tạo tài nguyên S3 buckets, DynamoDB, LabRole và Pillow Layer v1 trên AWS Academy."],
        ["Tuần 2", "5e19f4a", "Trung", "Triển khai Lambda processor, kết nối S3 trigger, DynamoDB metadata và kiểm chứng chống loop."],
        ["Tuần 2", "a12bc73", "Tuấn", "Tích hợp Web Gallery cục bộ với AWS, thực hiện và ghi nhận 12 ca kiểm thử T01-T12."],
        ["Tuần 3", "8b23c91", "Trung", "Thực hiện 2 yêu cầu nâng cao: tách Pillow Layer v1 (gói 3.7 kB) và S3 Lifecycle Rule 7 ngày."],
        ["Tuần 3", "2c45e89", "Tuấn", "Triển khai Web Gallery trên EC2 chạy Gunicorn systemd, kiểm thử IAM Role và Presigned URL 300s."],
        ["Tuần 3", "4eadf70", "Tuấn", "Hoàn thiện báo cáo nộp bài Markdown và tài liệu Word Tuần 3."],
        ["Tuần 4", "a72a92c", "Trung", "Cấu hình kịch bản dọn dẹp tài nguyên, dữ liệu chi phí và sửa lỗi nhận xét Tuần 3."],
        ["Tuần 4", "700d73e", "Trung", "Bổ sung minh chứng ngân sách AWS (E27) và bộ 3 ảnh kiểm chứng dọn dẹp tài nguyên (E29a, E29b, E29c)."],
        ["Tuần 4", "f068057", "Tuấn", "Bổ sung minh chứng video demo sản phẩm hoàn chỉnh trên Google Drive thời lượng 8:45 (E28)."],
        ["Tuần 4", "89a1034", "Tuấn", "Đối chiếu danh mục minh chứng tổng kết và bảng nghiệm thu đồ án cuối kỳ."],
        ["Tuần 4", "e00182e", "Trung & Tuấn", "Nộp Báo cáo tổng kết đồ án Word và Báo cáo nộp bài Markdown hoàn thiện toàn diện 4 tuần."],
    ]
    table(t82_headers, t82_rows, [1.5, 1.8, 2.2, 10.0])

    heading("8.3. Liên kết trực tiếp tới 9 file mã nguồn và cấu hình chính", level=2)
    p("Theo đúng nhắc nhở của GVHD, toàn bộ mã nguồn và cấu hình hệ thống được dẫn liên kết trực tiếp vào kho mã nguồn GitHub để thuận tiện cho việc đối chiếu, chấm điểm:")
    
    files_to_link = [
        ("Mã nguồn xử lý sự kiện AWS Lambda:", "src/processor/lambda_function.py", f"{REPO}/blob/main/src/processor/lambda_function.py"),
        ("Module xử lý đồ họa Pillow & Watermark:", "src/processor/image_tools.py", f"{REPO}/blob/main/src/processor/image_tools.py"),
        ("Ứng dụng Web Gallery máy chủ EC2:", "src/web/app.py", f"{REPO}/blob/main/src/web/app.py"),
        ("Cấu hình dịch vụ nền systemd trên EC2:", "deploy/cloud-photo.service", f"{REPO}/blob/main/deploy/cloud-photo.service"),
        ("Script tự động đóng gói Lambda & Layer:", "scripts/build_packages.py", f"{REPO}/blob/main/scripts/build_packages.py"),
        ("Script tự động dọn dẹp tài nguyên AWS:", "scripts/teardown_resources.py", f"{REPO}/blob/main/scripts/teardown_resources.py"),
        ("Bộ kiểm thử Unit Test xử lý ảnh:", "tests/test_images.py", f"{REPO}/blob/main/tests/test_images.py"),
        ("Bộ kiểm thử Unit Test Worker Lambda:", "tests/test_worker.py", f"{REPO}/blob/main/tests/test_worker.py"),
        ("Bộ kiểm thử Unit Test Web Gallery & CSRF:", "tests/test_web.py", f"{REPO}/blob/main/tests/test_web.py"),
    ]
    for desc, fname, furl in files_to_link:
        pf = p()
        pf.add_run(f"• {desc} ")
        link(pf, fname, furl)

    heading("8.4. Khai báo sử dụng AI chi tiết, trung thực và minh bạch", level=2)
    p("Nhóm cam kết tính trung thực học thuật và xin khai báo đầy đủ, minh bạch việc sử dụng công cụ Trí tuệ Nhân tạo (AI) trong quá trình thực hiện đồ án:")
    p("• Các công cụ và phiên bản mô hình AI sử dụng:")
    p("  1. Google Gemini: Phiên bản mô hình Gemini 3.8 Flash (High).")
    p("  2. OpenAI ChatGPT: Phiên bản mô hình GPT-4o.")
    p("• Nội dung AI hỗ trợ:")
    p("  - Tra cứu cấu trúc cú pháp SDK boto3 và AWS Pricing API để xây dựng công thức tính toán chi phí chi tiết.")
    p("  - Tư vấn bố cục phân cảnh kịch bản video demo sản phẩm (giới hạn dưới 10 phút, phân vai thuyết minh tiếng Việt).")
    p("  - Gợi ý cấu trúc mã nguồn cho script tự động hóa dọn dẹp tài nguyên scripts/teardown_resources.py.")
    p("  - Hỗ trợ xây dựng kịch bản tự động hóa biên tập tài liệu Word (python-docx kết hợp Pillow) để sinh báo cáo đồ án chuẩn học thuật.")
    p("• Phần sinh viên trực tiếp thực hiện và kiểm chứng:")
    p("  - Trực tiếp cấu hình, thao tác và quản trị toàn bộ các dịch vụ trên AWS Management Console và EC2 Terminal trong suốt 4 tuần.")
    p("  - Trực tiếp chạy, kiểm tra và ghi nhận kết quả của 22 ca kiểm thử T01–T22.")
    p("  - Trực tiếp quay, thuyết minh và biên tập video demo Full HD (8:45), tải lên Google Drive và chụp ảnh minh chứng E28.")
    p("  - Trực tiếp thực hiện dọn dẹp tài nguyên trên AWS và kiểm chứng kết quả Terminated / Buckets 0 / Tables 0 (E27, E29a, E29b, E29c).")
    p("  - Trực tiếp thực hiện toàn bộ các commit và đẩy lên GitHub theo đúng quy trình phối hợp nhóm.")

    # =========================================================================
    # CHƯƠNG 9: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN
    # =========================================================================
    heading("CHƯƠNG 9. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", level=1)
    
    heading("9.1. Đánh giá mức độ hoàn thành so với mục tiêu đề tài", level=2)
    p("Trải qua 4 tuần nỗ lực nghiên cứu và thực nghiệm nghiêm túc, nhóm đã hoàn thành xuất sắc 100% mục tiêu đề tài đặt ra ban đầu:")
    p("1. Xây dựng thành công một hệ thống xử lý ảnh tự động hoàn chỉnh, kết hợp tối ưu giữa máy chủ Web IaaS (EC2) và các dịch vụ phi máy chủ Serverless (S3, Lambda, DynamoDB, CloudWatch).")
    p("2. Hiện thực hóa trọn vẹn 3 lớp bảo mật khép kín theo đúng chuẩn AWS Security: IAM Role LabInstanceProfile (IMDSv2, không static keys) -> S3 Output Private tuyệt đối (HTTP 403) -> Cấp quyền xem tạm thời qua Presigned URL chính xác 300 giây.")
    p("3. Hoàn thành xuất sắc 2 yêu cầu kỹ thuật nâng cao của GVHD: Tối ưu gói deploy Lambda đạt kích thước siêu nhẹ 3.7 kB bằng Lambda Layer Pillow v1 và thiết lập S3 Lifecycle Rule tự động xóa ảnh sau 7 ngày.")
    p("4. Chứng minh ưu thế vượt trội về mặt kinh tế của kiến trúc Serverless, giúp tiết kiệm hơn 85% chi phí so với mô hình máy chủ nguyên khối truyền thống.")
    p("5. Hoàn thiện bộ 22 ca kiểm thử đạt 100% ĐẠT, video demo Full HD 8:45, thu thập đầy đủ 79 hình ảnh minh chứng và thực hiện quy trình dọn dẹp tài nguyên sạch sẽ.")

    heading("9.2. Những kiến thức và kỹ năng thực tế thu nhận được", level=2)
    p("Qua quá trình thực hiện đồ án, hai sinh viên đã tích lũy được nhiều bài học kinh nghiệm và kỹ năng thực tế vô cùng quý báu:")
    p("• Hiểu sâu sắc triết lý thiết kế kiến trúc hướng sự kiện (Event-driven Architecture) và cách các dịch vụ đám mây AWS tương tác với nhau thông qua sự kiện.")
    p("• Nắm vững các nguyên tắc bảo mật đám mây: Phân quyền theo nguyên tắc đặc quyền tối thiểu (Least Privilege), cơ chế xoay vòng thông tin xác thực tạm thời bằng IMDSv2 và bảo vệ tài nguyên lưu trữ bằng Presigned URL.")
    p("• Nâng cao kỹ năng quản trị hệ thống Linux trên đám mây: Cấu hình WSGI Gunicorn, quản trị tiến trình nền với systemd, thiết lập cơ chế tự phục hồi dịch vụ khi gặp sự cố.")
    p("• Rèn luyện tư duy tối ưu hóa chi phí (FinOps) trong điện toán đám mây: Biết cách phân tích bảng giá, lựa chọn loại tài nguyên phù hợp và thiết lập chính sách vòng đời tự động để tiết kiệm ngân sách.")

    heading("9.3. Hạn chế của môi trường thực hành và hướng phát triển", level=2)
    p("Bên cạnh những kết quả nổi bật đã đạt được, hệ thống vẫn còn một số điểm hạn chế do giới hạn chính sách của môi trường thực hành AWS Academy Learner Lab:")
    p("• Hạn chế 1: Chưa thể gán địa chỉ IP tĩnh (Elastic IP) cho máy chủ EC2 do Learner Lab không cấp quyền cấp phát Elastic IP. Mỗi lần máy chủ khởi động lại, Public IP sẽ bị thay đổi.")
    p("• Hạn chế 2: Chưa triển khai bộ cân bằng tải ứng dụng (Application Load Balancer - ALB) và nhóm tự động co giãn máy chủ (Auto Scaling Group - ASG) cho tầng Web Gallery do giới hạn hạn mức tài nguyên phòng lab.")
    p("• Hạn chế 3: Đường truyền truy cập Web Gallery hiện tại phải đi qua kênh SSH Local Port Forwarding để đảm bảo bảo mật nội bộ thay vì gắn chứng chỉ SSL/TLS công khai (HTTPS qua AWS Certificate Manager).")
    p("Hướng phát triển khi chuyển giao hệ thống sang môi trường sản xuất thương mại thực tế:")
    p("1. Triển khai kiến trúc Web đa vùng sẵn sàng (Multi-AZ): Đặt máy chủ EC2 vào Auto Scaling Group nằm sau Application Load Balancer để tự động tăng giảm số lượng máy chủ web theo lưu lượng truy cập thực tế.")
    p("2. Tích hợp mạng phân phối nội dung Amazon CloudFront: Đặt CloudFront làm lớp đệm (cache) phía trước S3 Output Bucket để phân phối các ảnh thumbnail với độ trễ siêu thấp đến người dùng trên toàn cầu, kết hợp chứng chỉ SSL miễn phí từ AWS Certificate Manager (ACM).")
    p("3. Ứng dụng trí tuệ nhân tạo (AI/ML): Tích hợp dịch vụ Amazon Rekognition vào luồng xử lý của Lambda để tự động gắn nhãn (auto-tagging), phát hiện khuôn mặt, kiểm duyệt nội dung nhạy cảm và trích xuất văn bản từ hình ảnh tự động.")

    # =========================================================================
    # TÀI LIỆU THAM KHẢO
    # =========================================================================
    heading("TÀI LIỆU THAM KHẢO", level=1)
    refs = [
        "Amazon Web Services, “AWS Lambda Developer Guide,” AWS Documentation, 2026. [Online]. Available: https://docs.aws.amazon.com/lambda/",
        "Amazon Web Services, “Amazon Simple Storage Service User Guide,” AWS Documentation, 2026. [Online]. Available: https://docs.aws.amazon.com/s3/",
        "Amazon Web Services, “Amazon DynamoDB Developer Guide,” AWS Documentation, 2026. [Online]. Available: https://docs.aws.amazon.com/dynamodb/",
        "Amazon Web Services, “Amazon EC2 User Guide for Linux Instances,” AWS Documentation, 2026. [Online]. Available: https://docs.aws.amazon.com/ec2/",
        "Amazon Web Services, “Working with Lambda Layers,” AWS Documentation, 2026. [Online]. Available: https://docs.aws.amazon.com/lambda/latest/dg/chapter-layers.html",
        "Amazon Web Services, “Managing your storage lifecycle,” Amazon S3 User Guide, 2026. [Online]. Available: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html",
        "Pillow Contributors, “Pillow (PIL Fork) Documentation,” Read the Docs, 2026. [Online]. Available: https://pillow.readthedocs.io/",
        "Pallets Projects, “Flask Documentation (3.0.x),” Pallets, 2026. [Online]. Available: https://flask.palletsprojects.com/",
        "Benoit Chesneau, “Gunicorn - WSGI HTTP Server for UNIX,” Gunicorn Documentation, 2026. [Online]. Available: https://docs.gunicorn.org/",
        "TS. Huỳnh Xuân Phụng, “Bài giảng môn học Điện toán Đám mây,” Trường Đại học Sư phạm Kỹ thuật TP. Hồ Chí Minh, 2026.",
    ]
    for ref in refs:
        pref = p()
        pref.paragraph_format.left_indent = Cm(1.0)
        pref.paragraph_format.first_line_indent = Cm(-1.0)
        pref.add_run(ref)

    # Save document
    print(f"Saving final report to: {OUTPUT}")
    doc.save(str(OUTPUT))
    print(f"Successfully generated: {OUTPUT}")
    print(f"Total evidence figures inserted: {fig_counter}/79")


if __name__ == "__main__":
    main()
