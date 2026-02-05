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


def _scenario_table(title: str, rows: Iterable[List[str]], styles, font_name: str, bg_color: colors.Color) -> List[Any]:
    """시나리오별 테이블 생성 (배경색 포함)."""
    story: List[Any] = [Paragraph(f"<b>{title}</b>", styles["Heading3"])]
    story.append(Spacer(1, 6))
    table = Table(list(rows), hAlign="LEFT")
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), font_name),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, 0), bg_color),  # 헤더 배경색
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ]))
    story.append(table)
    story.append(Spacer(1, 12))
    return story


@mcp.tool()
def generate_simulation_report(output_path: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
    """시뮬레이션 리포트 PDF 생성. 시나리오별 색상 구분 포함."""
    font_name = _register_font(report_data.get("font_path"))
    styles = getSampleStyleSheet()
    styles["Heading1"].fontName = font_name
    styles["Heading2"].fontName = font_name
    styles["Heading3"].fontName = font_name
    styles["BodyText"].fontName = font_name

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(str(output_file), pagesize=A4)
    story: List[Any] = []
    story.append(Paragraph(report_data.get("title", "5G 저가 요금제 시뮬레이션 리포트"), styles["Heading1"]))
    story.append(Spacer(1, 12))

    sections = report_data.get("sections", {})

    # 요약 섹션
    if "요약" in sections:
        story.extend(_section("요약", sections["요약"], styles, font_name))

    # 신규 요금제 스펙
    if "신규 요금제 스펙" in sections:
        story.extend(_section("신규 요금제 스펙", sections["신규 요금제 스펙"], styles, font_name))

    # 경쟁사 비교
    if "경쟁사 비교" in sections:
        story.extend(_section("경쟁사 비교", sections["경쟁사 비교"], styles, font_name))

    # 시나리오 분석 (색상 구분)
    if "시나리오 분석" in sections:
        story.append(Paragraph("<b>시나리오 분석</b>", styles["Heading2"]))
        story.append(Spacer(1, 6))
        scenario_colors = {
            "보수적": colors.HexColor("#FF6B6B"),  # 빨간색
            "기준": colors.HexColor("#4ECDC4"),  # 청록색
            "낙관적": colors.HexColor("#95E1D3"),  # 연한 청록색
        }
        scenario_data = sections["시나리오 분석"]
        if isinstance(scenario_data, dict):
            for scenario_name, rows in scenario_data.items():
                bg_color = scenario_colors.get(scenario_name, colors.lightgrey)
                story.extend(_scenario_table(scenario_name, rows, styles, font_name, bg_color))
        else:
            # 리스트 형태인 경우
            story.extend(_section("시나리오 분석", scenario_data, styles, font_name))

    # 고가 요금제 옵션
    if "고가 요금제 옵션" in sections:
        story.extend(_section("고가 요금제 옵션", sections["고가 요금제 옵션"], styles, font_name))

    # 권고사항
    if "권고사항" in sections:
        story.extend(_section("권고사항", sections["권고사항"], styles, font_name))

    # 비고
    if notes := report_data.get("notes"):
        story.append(Paragraph("<b>비고</b>", styles["Heading3"]))
        story.append(Spacer(1, 6))
        story.append(Paragraph(str(notes), styles["BodyText"]))

    doc.build(story)
    return {"output_path": str(output_file)}


if __name__ == "__main__":
    mcp.run()
