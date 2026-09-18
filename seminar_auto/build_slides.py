import base64
import concurrent.futures
import tempfile
from pathlib import Path

import requests
from openai import OpenAI
from pptx import Presentation
from pptx.oxml.ns import qn
from pptx.oxml.xmlchemy import OxmlElement
from pptx.text.text import _Run
from pptx.util import Inches, Pt

from . import config

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

IMAGE_PROMPT_TEMPLATE = (
    "プロのカメラで撮影したような、自然でリアルな写真。テーマ: {title}。"
    "自然光で写実的な質感にすること。人物の顔がはっきり写らないアングルにする"
    "(手元・後ろ姿・物のみなど)。文字やテキストは一切含めないこと。"
)


def _set_japanese_font(run: _Run, font_name: str) -> None:
    run.font.name = font_name
    rPr = run.font._rPr
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = OxmlElement("a:ea")
        rPr.append(ea)
    ea.set("typeface", font_name)


def _generate_slide_image(title: str) -> bytes:
    client = OpenAI()
    response = client.images.generate(
        model=config.OPENAI_IMAGE_MODEL,
        prompt=IMAGE_PROMPT_TEMPLATE.format(title=title),
        size="1024x1024",
        n=1,
    )
    image_data = response.data[0]
    # response_format(b64_json/url)を明示指定できないAPIバージョンでも動くよう、
    # 実際に返ってきた方の形式(base64 or URL)を使う。
    if image_data.b64_json:
        return base64.b64decode(image_data.b64_json)
    return requests.get(image_data.url, timeout=30).content


def build(slides: list[dict], output_path: Path) -> None:
    # 画像生成はスライドごとに独立したAPI呼び出しなので並列に実行する。
    with concurrent.futures.ThreadPoolExecutor(max_workers=config.MAX_PARALLEL_REQUESTS) as executor:
        images = list(executor.map(lambda s: _generate_slide_image(s["title"]), slides))

    prs = Presentation()
    layout = prs.slide_layouts[1]  # タイトル + 本文
    for slide_data, image_bytes in zip(slides, images):
        slide = prs.slides.add_slide(layout)
        slide.shapes.title.text = slide_data["title"]
        for run in slide.shapes.title.text_frame.paragraphs[0].runs:
            _set_japanese_font(run, JAPANESE_FONT)

        # 箇条書きは左半分、イラストは右半分に配置する。
        body = slide.placeholders[1]
        body.left = Inches(0.5)
        body.top = Inches(1.7)
        body.width = Inches(5.3)
        body.height = Inches(5.3)
        text_frame = body.text_frame
        text_frame.clear()
        for i, bullet in enumerate(slide_data["bullets"]):
            paragraph = text_frame.paragraphs[0] if i == 0 else text_frame.add_paragraph()
            paragraph.text = bullet
            paragraph.font.size = Pt(28)
            for run in paragraph.runs:
                _set_japanese_font(run, JAPANESE_FONT)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(image_bytes)
            image_path = Path(f.name)
        try:
            slide.shapes.add_picture(str(image_path), Inches(6.0), Inches(1.9), height=Inches(3.6))
        finally:
            image_path.unlink()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))
