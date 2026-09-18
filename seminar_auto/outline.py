import json

from anthropic import Anthropic

from . import config

SYSTEM_PROMPT = (
    "あなたはセミナーの文字起こしから、参加者が最後に見る「本日の振り返り動画」の"
    "スライド構成を作るアシスタントです。これは司会進行のメモではなく、"
    "セミナーを受けた参加者に向けて「本日は〇〇を行いました」「〇〇を学びました」"
    "のように、その日の内容を一緒に振り返るような語りかけの文章にしてください。"
    "話の要点だけを厳選し、話された順序に沿って構成してください。"
    "最も重要な制約: 文字起こしに実際に書かれている内容だけを使ってください。"
    "文字起こしに含まれていない情報を推測・創作・一般論での補完で追加することは"
    "絶対に禁止です。文字起こしの量が少ない場合は、無理に埋めようとせず、"
    "スライドの枚数を減らしてください。"
)


def generate_outline(transcript: str, target_seconds: int, seconds_per_slide: int) -> list[dict]:
    target_slide_count = max(3, round(target_seconds / seconds_per_slide))
    client = Anthropic()
    response = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": (
                "以下はセミナーの文字起こしです。振り返り用の動画スライドとして"
                f"最大{target_slide_count}枚程度の構成を日本語で作ってください。"
                "枚数はあくまで上限の目安であり、文字起こしの内容がそれより少ない"
                "場合は、内容に見合った枚数にしてください。"
                "各スライドはタイトルと2〜4個の短い箇条書きにしてください。"
                "箇条書きは体言止め・常体ではなく、「です・ます」調の丁寧な文体で"
                "書いてください。\n\n"
                f"---文字起こし---\n{transcript}"
            ),
        }],
        output_config={
            "format": {
                "type": "json_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "slides": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "bullets": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                },
                                "required": ["title", "bullets"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["slides"],
                    "additionalProperties": False,
                },
            },
        },
    )
    text = next(block.text for block in response.content if block.type == "text")
    return json.loads(text)["slides"]
