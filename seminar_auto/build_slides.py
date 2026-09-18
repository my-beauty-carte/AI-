from pathlib import Path

from pptx import Presentation
from pptx.util import Pt


def build(slides: list[dict], output_path: Path) -> None:
    prs = Presentation()
    layout = prs.slide_layouts[1]  # タイトル + 本文
    for slide_data in slides:
        slide = prs.slides.add_slide(layout)
        slide.shapes.title.text = slide_data["title"]
        body = slide.placeholders[1].text_frame
        body.clear()
        for i, bullet in enumerate(slide_data["bullets"]):
            paragraph = body.paragraphs[0] if i == 0 else body.add_paragraph()
            paragraph.text = bullet
            paragraph.font.size = Pt(28)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))
