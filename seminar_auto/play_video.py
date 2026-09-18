import subprocess
from pathlib import Path


def play(video_path: Path) -> None:
    subprocess.run(["ffplay", "-fs", "-autoexit", str(video_path)])
