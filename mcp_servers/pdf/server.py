from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List

from mcp.server.fastmcp import FastMCP
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table


mcp = FastMCP("pdf-mcp")


def _maybe_register_font(font_path: str | None) -> str:
    if not font_path:
        return "Helvetica"
    font_file = Path(font_path)
    if not font_file.exists():
        return "Helvetica"
    font_name = font_file.stem
    pdfmetrics.registerFont(TTFont(font_name, str(font_file)))
    return font_name


def _section(title: str, rows: Iterable[List[str]], styles) -> List[Any]:
    story: List[Any] = [Paragraph(f"<b>{title}</b>", styles["Heading3"])]
    story.append(Spacer(1, 6))
    table = Table(list(rows), hAlign="LEFT")
    story.append(table)
    story.append(Spacer(1, 12))
    return story


@mcp.tool()
def generate_spec_document(output_path: str, spec: Dict[str, Any]) -> Dict[str, Any]:
    """요금제 스펙 문서 PDF 생성."""
    font_name = _maybe_register_font(spec.get("font_path"))
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
        story.extend(_section(section_title, rows, styles))

    if notes := spec.get("notes"):
        story.append(Paragraph("<b>비고</b>", styles["Heading3"]))
        story.append(Spacer(1, 6))
        story.append(Paragraph(str(notes), styles["BodyText"]))

    doc.build(story)
    return {"output_path": str(output_file)}


if __name__ == "__main__":
    mcp.run()
