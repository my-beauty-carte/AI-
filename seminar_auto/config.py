import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_MODEL = "claude-opus-5"
OPENAI_WHISPER_MODEL = "whisper-1"
OPENAI_TTS_MODEL = "gpt-4o-mini-tts"
OPENAI_IMAGE_MODEL = "gpt-image-1"

WORK_DIR = Path(os.environ.get("SEMINAR_WORK_DIR", "./seminar_output"))
AUDIO_PATH = WORK_DIR / "recording.wav"
TRANSCRIPT_PATH = WORK_DIR / "transcript.txt"
OUTLINE_PATH = WORK_DIR / "outline.json"
SLIDES_PATH = WORK_DIR / "slides.pptx"
VIDEO_PATH = WORK_DIR / "recap.mp4"

# 振り返り動画の目標の長さと、スライド1枚あたりの目安秒数。
# 目標秒数 ÷ 1枚あたりの秒数で、生成するスライド枚数を決める。
TARGET_VIDEO_SECONDS = int(os.environ.get("SEMINAR_TARGET_VIDEO_SECONDS", "180"))
SECONDS_PER_SLIDE = int(os.environ.get("SEMINAR_SECONDS_PER_SLIDE", "18"))
MIN_SLIDE_SECONDS = float(os.environ.get("SEMINAR_MIN_SLIDE_SECONDS", "6"))

# 会場PCのマイク入力デバイス名。未指定ならOSごとの既定デバイスを使う。
AUDIO_INPUT_DEVICE = os.environ.get("SEMINAR_AUDIO_DEVICE")

# 文字起こし・画像生成・音声合成を並列実行する数。長いセミナー録音でも
# 休憩時間内に処理を終えられるよう、API呼び出しを並列化する際に使う。
MAX_PARALLEL_REQUESTS = int(os.environ.get("SEMINAR_MAX_PARALLEL_REQUESTS", "4"))

# ナレーション音声(OpenAI TTS)。alloy/echo/fable/onyx/nova/shimmerから選べる。
# novaは明るく元気なトーン。落ち着いた声にしたい場合はshimmerやfableに変更できる。
NARRATION_VOICE = os.environ.get("SEMINAR_NARRATION_VOICE", "nova")

# gpt-4o-mini-ttsは、この指示文で話し方(トーン)を調整できる。
NARRATION_INSTRUCTIONS = os.environ.get(
    "SEMINAR_NARRATION_INSTRUCTIONS",
    "とても明るく元気に、笑顔が伝わるような弾んだトーンで話してください。",
)
