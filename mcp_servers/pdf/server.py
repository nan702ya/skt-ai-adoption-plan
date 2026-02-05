from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List

from mcp.server.fastmcp import FastMCP
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


mcp = FastMCP("pdf-mcp")

# macOS/Linux/Windows 한글 폰트 경로 후보
KOREAN_FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/AppleGothic.ttf",  # macOS
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",  # macOS (newer)
    "/Library/Fonts/AppleGothic.ttf",  # macOS alternative
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",  # Ubuntu
    "C:/Windows/Fonts/malgun.ttf",  # Windows
]


def _find_korean_font() -> str | None:
    """시스템에서 한글 폰트를 자동으로 찾습니다."""
    for font_path in KOREAN_FONT_CANDIDATES:
        if Path(font_path).exists():
            return font_path
    return None


def _register_font(font_path: str | None) -> str:
    """폰트를 등록하고 폰트명을 반환합니다. 한글 폰트 자동 탐지."""
    # 명시적 경로가 없으면 한글 폰트 자동 탐지
    if not font_path:
        font_path = _find_korean_font()

    if not font_path:
        return "Helvetica"

    font_file = Path(font_path)
    if not font_file.exists():
        return "Helvetica"

    font_name = font_file.stem
    try:
        pdfmetrics.registerFont(TTFont(font_name, str(font_file)))
        return font_name
    except Exception:
        return "Helvetica"


def _section(title: str, rows: Iterable[List[str]], styles, font_name: str) -> List[Any]:
    story: List[Any] = [Paragraph(f"<b>{title}</b>", styles["Heading3"])]
    story.append(Spacer(1, 6))
    table = Table(list(rows), hAlign="LEFT")
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), font_name),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 12))
    return story


@mcp.tool()
def generate_spec_document(output_path: str, spec: Dict[str, Any]) -> Dict[str, Any]:
    """요금제 스펙 문서 PDF 생성. 한글 폰트 자동 탐지."""
    font_name = _register_font(spec.get("font_path"))
    styles = getSampleStyleSheet()
    styles["Heading1"].fontName = font_name
    styles["Heading2"].fontName = font_name
    styles["Heading3"].fontName = font_name
    styles["BodyText"].fontName = font_name

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(str(output_file), pagesize=A4)
    story: List[Any] = []
    story.append(Paragraph(spec.get("title", "요금제 설계 스펙"), styles["Heading1"]))
    story.append(Spacer(1, 12))

    sections = spec.get("sections", {})
    for section_title, rows in sections.items():
        story.extend(_section(section_title, rows, styles, font_name))

    if notes := spec.get("notes"):
        story.append(Paragraph("<b>비고</b>", styles["Heading3"]))
        story.append(Spacer(1, 6))
        story.append(Paragraph(str(notes), styles["BodyText"]))

    doc.build(story)
    return {"output_path": str(output_file)}


if __name__ == "__main__":
    mcp.run()
