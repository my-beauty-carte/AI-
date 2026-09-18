from pathlib import Path

from pptx import Presentation
from pptx.oxml.ns import qn
from pptx.oxml.xmlchemy import OxmlElement
from pptx.text.text import _Run
from pptx.util import Pt

# デフォルトのpptxテーマは東アジア用フォントが未指定で、日本語用のフォールバックが
# Windows専用の「ＭＳ Ｐゴシック」になっている。実行環境を問わず表示できるよう、
# 各テキストに東アジア用フォントを明示的に指定する。
#
# macOS標準の「Hiragino Sans」はシステム保護領域のフォントコンテナに格納されており、
# LibreOfficeをheadless(バックグラウンド)モードで実行した際にはこれを見つけられず、
# 日本語部分だけ表示されなくなることを確認した。通常のフォントファイルとして
# インストールされる「Noto Sans JP」(`brew install --cask font-noto-sans-jp`)は
# headlessモードでも問題なく認識されるため、こちらを使う。
JAPANESE_FONT = "Noto Sans JP"


def _set_japanese_font(run: _Run, font_name: str) -> None:
    run.font.name = font_name
    rPr = run.font._rPr
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = OxmlElement("a:ea")
        rPr.append(ea)
    ea.set("typeface", font_name)


def build(slides: list[dict], output_path: Path) -> None:
    prs = Presentation()
    layout = prs.slide_layouts[1]  # タイトル + 本文
    for slide_data in slides:
        slide = prs.slides.add_slide(layout)
        slide.shapes.title.text = slide_data["title"]
        for run in slide.shapes.title.text_frame.paragraphs[0].runs:
            _set_japanese_font(run, JAPANESE_FONT)

        body = slide.placeholders[1].text_frame
        body.clear()
        for i, bullet in enumerate(slide_data["bullets"]):
            paragraph = body.paragraphs[0] if i == 0 else body.add_paragraph()
            paragraph.text = bullet
            paragraph.font.size = Pt(28)
            for run in paragraph.runs:
                _set_japanese_font(run, JAPANESE_FONT)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))
