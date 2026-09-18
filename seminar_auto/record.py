import platform
import subprocess
from pathlib import Path

from . import config


def _ffmpeg_input_args() -> list[str]:
    system = platform.system()
    device = config.AUDIO_INPUT_DEVICE
    if system == "Windows":
        # デバイス名は `ffmpeg -list_devices true -f dshow -i dummy` で確認できる。
        return ["-f", "dshow", "-i", device or "audio=default"]
    if system == "Darwin":
        # デバイス番号は `ffmpeg -f avfoundation -list_devices true -i ""` で確認できる。
        return ["-f", "avfoundation", "-i", device or ":0"]
    # Linux (PulseAudio)。デバイス名は `pactl list sources short` で確認できる。
    return ["-f", "pulse", "-i", device or "default"]


def start_recording(output_path: Path) -> subprocess.Popen:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", *_ffmpeg_input_args(), "-ac", "1", "-ar", "44100", str(output_path)]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def stop_recording(proc: subprocess.Popen) -> None:
    # ffmpegは標準入力に'q'を受け取るとファイルを正しく閉じて終了する。
    if proc.stdin:
        try:
            proc.stdin.write(b"q")
            proc.stdin.flush()
        except OSError:
            pass
    try:
        proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        proc.terminate()
        proc.wait(timeout=15)
