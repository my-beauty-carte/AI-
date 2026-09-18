import os
from pathlib import Path

ANTHROPIC_MODEL = "claude-opus-5"
OPENAI_WHISPER_MODEL = "whisper-1"

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
NARRATION_LANG = os.environ.get("SEMINAR_NARRATION_LANG", "ja")
