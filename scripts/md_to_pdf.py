#!/usr/bin/env python3
"""
深度分析报告 Markdown → PDF 转换脚本 (WeasyPrint版)
用法: python md_to_pdf.py input.md output.pdf [--title "报告标题"] [--author "作者"]

依赖: pip install weasyprint markdown --break-system-packages
"""

import sys
import os
import re
import argparse
import markdown

# ── CSS 样式 ──
CSS_TEMPLATE = """
@page {
    size: A4;
    margin: 25mm 20mm 20mm 20mm;

    @top-center {
        content: "HEADER_TEXT";
        font-family: "Droid Sans Fallback", Helvetica, Arial, sans-serif;
        font-size: 8pt;
        color: #95a5a6;
        border-bottom: 0.5pt solid #ecf0f1;
        padding-bottom: 3mm;
    }

    @bottom-center {
        content: "第 " counter(page) " 页";
        font-family: "Droid Sans Fallback", Helvetica, Arial, sans-serif;
        font-size: 8pt;
        color: #95a5a6;
        border-top: 0.8pt solid #1a5276;
        padding-top: 2mm;
    }
}

@page :first {
    @top-center { content: none; }
    @bottom-center { content: none; }
}

body {
    font-family: "Droid Sans Fallback", Helvetica, Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.75;
    color: #2c3e50;
    text-align: justify;
}

/* 封面 */
.cover {
    page-break-after: always;
    text-align: center;
    padding-top: 45%;
}
.cover h1 {
    font-size: 28pt;
    color: #1a5276;
    margin-bottom: 8mm;
    font-weight: bold;
    letter-spacing: 2pt;
}
.cover .subtitle {
    font-size: 14pt;
    color: #95a5a6;
    margin-bottom: 6mm;
}
.cover .meta {
    font-size: 11pt;
    color: #95a5a6;
    margin-bottom: 4mm;
}
.cover .divider {
    width: 60%;
    margin: 8mm auto;
    border: none;
    border-top: 1.5pt solid #1a5276;
}

/* 一级标题 */
h1 {
    font-size: 20pt;
    color: #1a5276;
    margin-top: 16mm;
    margin-bottom: 6mm;
    padding-bottom: 3mm;
    border-bottom: 2pt solid #1a5276;
    page-break-before: always;
    font-weight: bold;
}

/* 二级标题 */
h2 {
    font-size: 14pt;
    color: #1e8449;
    margin-top: 10mm;
    margin-bottom: 5mm;
    font-weight: bold;
}

/* 三级标题 */
h3 {
    font-size: 12pt;
    color: #2e86c1;
    margin-top: 6mm;
    margin-bottom: 3mm;
    font-weight: bold;
}

h4 {
    font-size: 11pt;
    color: #5b2c6f;
    margin-top: 5mm;
    margin-bottom: 2mm;
    font-weight: bold;
}

/* 段落 */
p {
    margin-top: 1.5mm;
    margin-bottom: 1.5mm;
    orphans: 3;
    widows: 3;
}

/* 引用块 */
blockquote {
    margin: 4mm 0;
    padding: 4mm 4mm 4mm 10mm;
    background: #f8f9fa;
    border-left: 3pt solid #1a5276;
    color: #5d6d7e;
    font-size: 10pt;
}
blockquote p {
    margin: 1mm 0;
}

/* 粗体 */
strong, b {
    font-weight: bold;
    color: #1a252f;
}

/* 行内代码 */
code {
    font-family: "Courier New", Courier, monospace;
    background: #fdf2e9;
    color: #c0392b;
    padding: 0.5mm 1.5mm;
    border-radius: 2pt;
    font-size: 9.5pt;
}

/* 表格 */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 4mm 0;
    font-size: 9.5pt;
}
thead th {
    background: #1a5276;
    color: white;
    padding: 3mm;
    text-align: left;
    font-weight: bold;
}
tbody td {
    padding: 2.5mm 3mm;
    border-bottom: 0.5pt solid #bdc3c7;
}
tbody tr:nth-child(even) {
    background: #f8f9fa;
}

/* 分隔线 */
hr {
    border: none;
    border-top: 0.5pt solid #bdc3c7;
    margin: 4mm 0;
}

/* 列表 */
ul, ol {
    margin: 2mm 0;
    padding-left: 8mm;
}
li {
    margin-bottom: 1mm;
}

/* 链接 */
a {
    color: #2e86c1;
    text-decoration: none;
}
"""


def md_to_html(md_text, title="深度分析报告", meta_line="", author="微信公众号: 熵息茶馆", qr_path=None):
    """将 Markdown 转为带封面的 HTML，去除副标题和二维码"""

    # 用 markdown 库转换正文
    html_body = markdown.markdown(
        md_text,
        extensions=['tables', 'fenced_code', 'nl2br'],
        output_format='html5'
    )

    # 移除正文中的第一个 h1（会用在封面上）
    first_h1_match = re.search(r'<h1>(.*?)</h1>', html_body)
    if first_h1_match:
        extracted_title = first_h1_match.group(1)
        if not title or title == "深度分析报告":
            title = extracted_title
        html_body = html_body.replace(first_h1_match.group(0), '', 1)

    # 替换 CSS 中的页眉占位符（仅保留标题）
    css = CSS_TEMPLATE.replace("HEADER_TEXT", title)

    # 构建封面（不含副标题，二维码放在作者下方）
    qr_img_html = f"<img src='file://{qr_path}' style='margin-top:5mm; width:120px;'/>" if qr_path else ''
    cover_html = f"""
    <div class=\"cover\">
        <h1 style=\"page-break-before: avoid; border: none;\">{title}</h1>
        {"<div class='meta'>" + meta_line + "</div>" if meta_line else ""}
        <hr class=\"divider\">
        <div class=\"meta\">{author}</div>
        {qr_img_html}
    </div>
    """

    full_html = f"""
<!DOCTYPE html>
<html lang=\"zh-CN\">
<head>
    <meta charset=\"UTF-8\">
    <style>{css}</style>
</head>
<body>
{cover_html}
{html_body}
</body>
</html>"""

    return full_html

def main():
    parser = argparse.ArgumentParser(description="深度分析法报告 Markdown → PDF")
    parser.add_argument("input", help="输入的 Markdown 文件路径")
    parser.add_argument("output", help="输出的 PDF 文件路径")
    parser.add_argument("--title", default=None, help="报告标题")
    parser.add_argument("--author", default="微信公众号: 熵息茶馆", help="作者名")
    parser.add_argument("--subtitle", default=None, help="封面副标题（如研究时间|领域|对象类型）")
    parser.add_argument("--qr", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "references", "shangxichaguan.png")), help="封面二维码图片路径（默认熵息茶馆二维码）")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        md_text = f.read()

    # 提取元信息（用于封面副标题）
    meta_line = ""
    for line in md_text.split("\n"):
        stripped = line.strip().lstrip(">").strip()
        if "研究时间" in stripped or "所属领域" in stripped or "研究对象类型" in stripped:
            meta_line = stripped
            break

    # 从正文中移除元信息行，避免重复出现
    if meta_line:
        # 删除可能的 blockquote 前缀并去除整行
        md_text_body = md_text.replace(f"> {meta_line}", "")
    else:
        md_text_body = md_text

    html = md_to_html(
        md_text_body,
        title=args.title or "深度分析报告",
        meta_line=meta_line,
        author=args.author,
        qr_path=args.qr,
    )

    # 保存中间 HTML（便于调试）
    html_path = args.output.replace('.pdf', '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[OK] HTML 已生成: {html_path}")

    # 转 PDF
    # 优先尝试 WeasyPrint，失败则自动 fallback 到 Chrome headless
    pdf_ok = False

    try:
        from weasyprint import HTML
        HTML(string=html).write_pdf(args.output)
        pdf_ok = True
        print("[OK] PDF 引擎: WeasyPrint")
    except Exception as e:
        print(f"[WARN] WeasyPrint 不可用 ({e})，尝试 Chrome headless fallback...")

    if not pdf_ok:
        # Chrome headless fallback
        # 注意：必须使用 --no-pdf-header-footer（Chrome 112+ 的正确参数）
        # 旧参数 --print-to-pdf-no-header 在新版 Chrome 中已失效，会导致首页出现时间戳和文件路径
        import shutil, subprocess, urllib.parse
        chrome_candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            shutil.which("google-chrome") or "",
            shutil.which("chromium") or "",
        ]
        chrome_bin = next((c for c in chrome_candidates if c and os.path.exists(c)), None)
        if not chrome_bin:
            raise RuntimeError("WeasyPrint 不可用，且找不到 Chrome/Chromium，无法生成 PDF。")

        # 将 HTML 路径转为 file:// URL（需要 URL 编码中文路径）
        html_url = "file://" + urllib.parse.quote(html_path)
        cmd = [
            chrome_bin,
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            f"--print-to-pdf={args.output}",
            "--no-pdf-header-footer",   # 去除 Chrome 默认的时间戳/文件路径/页码页眉页脚
                                        # ⚠️  不要用 --print-to-pdf-no-header，该参数在 Chrome 112+ 已失效
            html_url,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 or not os.path.exists(args.output):
            raise RuntimeError(f"Chrome headless 转换失败:\n{result.stderr}")
        print("[OK] PDF 引擎: Chrome headless (--no-pdf-header-footer)")

    size_kb = os.path.getsize(args.output) / 1024
    print(f"[OK] PDF 已生成: {args.output} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
