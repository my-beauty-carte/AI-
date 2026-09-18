import json

from anthropic import Anthropic

from . import config

SYSTEM_PROMPT = (
    "あなたはセミナーの文字起こしから、聴衆が最後に短時間で振り返るための"
    "まとめスライドの構成を作るアシスタントです。話の要点だけを厳選し、"
    "話された順序に沿って構成してください。"
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
                f"{target_slide_count}枚程度の構成を日本語で作ってください。"
                "各スライドはタイトルと2〜4個の短い箇条書きにしてください。\n\n"
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
