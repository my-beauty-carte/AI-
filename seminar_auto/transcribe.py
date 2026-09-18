import concurrent.futures
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


def _transcribe_chunk(client: OpenAI, chunk: Path) -> str:
    with open(chunk, "rb") as f:
        result = client.audio.transcriptions.create(
            model=config.OPENAI_WHISPER_MODEL,
            file=f,
            language="ja",
        )
    return result.text


def transcribe(audio_path: Path) -> str:
    client = OpenAI()
    with tempfile.TemporaryDirectory() as tmp:
        chunks = _split_audio(audio_path, Path(tmp))
        # 90分クラスの長いセミナーでも休憩時間内に終わるよう、チャンクごとの
        # 文字起こしを並列に実行する(順序はexecutor.mapが呼び出し順を保持する)。
        with concurrent.futures.ThreadPoolExecutor(max_workers=config.MAX_PARALLEL_REQUESTS) as executor:
            texts = list(executor.map(lambda chunk: _transcribe_chunk(client, chunk), chunks))
    return "\n".join(texts)
