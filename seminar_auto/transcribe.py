import re
import subprocess
import tempfile
from pathlib import Path

from openai import OpenAI

from . import config

# OpenAIの音声文字起こしAPIは1ファイル25MBまで。長いセミナー録音でも
# 安全に収まるよう、10分単位に分割してから順に文字起こしする。
CHUNK_SECONDS = 600


def _split_audio(audio_path: Path, chunk_dir: Path) -> list[Path]:
    chunk_dir.mkdir(parents=True, exist_ok=True)
    pattern = str(chunk_dir / "chunk_%03d.wav")
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(audio_path),
            "-f", "segment", "-segment_time", str(CHUNK_SECONDS), "-c", "copy",
            pattern,
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    def chunk_index(path: Path) -> int:
        match = re.search(r"(\d+)", path.stem)
        return int(match.group(1)) if match else 0

    return sorted(chunk_dir.glob("chunk_*.wav"), key=chunk_index)


def transcribe(audio_path: Path) -> str:
    client = OpenAI()
    with tempfile.TemporaryDirectory() as tmp:
        chunks = _split_audio(audio_path, Path(tmp))
        texts = []
        for chunk in chunks:
            with open(chunk, "rb") as f:
                result = client.audio.transcriptions.create(
                    model=config.OPENAI_WHISPER_MODEL,
                    file=f,
                    language="ja",
                )
            texts.append(result.text)
    return "\n".join(texts)
