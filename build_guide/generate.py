"""
generate.py - Assembles all parts into an HTML document and compiles to PDF via Chrome Headless
"""

import os
import subprocess
import sys

from styles import CSS_STYLES
from front_matter import get_front_matter_html
from part1_memory_registers import get_part1_html
from part2_object_architecture import get_part2_html
from part3_virtual_hardware import get_part3_html
from part4_concurrency_ordering import get_part4_html
from part5_hardware_arm_riscv import get_part5_html
from part6_security_attacks import get_part6_html
from part7_glossary import get_part7_html

def build_full_html():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Silicon Hardware Security Engineering: The Definitive Systems & Hardware Architecture Master Guide</title>
    <style>
{CSS_STYLES}
    </style>
</head>
<body>
{get_front_matter_html()}
{get_part1_html()}
{get_part2_html()}
{get_part3_html()}
{get_part4_html()}
{get_part5_html()}
{get_part6_html()}
{get_part7_html()}
</body>
</html>
"""

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_output_path = os.path.join(base_dir, "Silicon_Hardware_Security_Engineering_Guide.html")
    pdf_output_path = os.path.join(base_dir, "Silicon_Hardware_Security_Engineering_Guide.pdf")

    print(f"[*] Assembling full HTML document...")
    full_html = build_full_html()
    with open(html_output_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"[+] HTML document saved to: {html_output_path} ({len(full_html)} bytes)")

    print(f"[*] Compiling to PDF via Chrome Headless...")
    header_template = (
        '<div style="font-size:7pt; font-family:-apple-system, BlinkMacSystemFont, sans-serif; '
        'width:100%; text-align:right; color:#64748b; padding-right:14mm;">'
        'Silicon Hardware Security Engineering &bull; Low-Level C++ & Hardware Architecture'
        '</div>'
    )
    footer_template = (
        '<div style="font-size:7pt; font-family:-apple-system, BlinkMacSystemFont, sans-serif; '
        'width:100%; display:flex; justify-content:space-between; color:#64748b; padding:0 14mm;">'
        '<span>Master Engineering Reference &bull; Thesis Prep</span>'
        '<span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>'
        '</div>'
    )

    chrome_cmd = [
        "google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_output_path}",
        html_output_path
    ]

    result = subprocess.run(chrome_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[-] Chrome PDF compilation failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)

    if os.path.exists(pdf_output_path):
        pdf_size = os.path.getsize(pdf_output_path)
        print(f"[+] PDF compiled successfully: {pdf_output_path} ({pdf_size} bytes)")
    else:
        print("[-] PDF file not found after Chrome run!", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
