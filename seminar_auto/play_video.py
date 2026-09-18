import platform
import subprocess
import time
from pathlib import Path


def play(video_path: Path) -> None:
    input("動画の準備ができました。再生するタイミングでEnterキーを押してください...")
    proc = subprocess.Popen(["ffplay", "-fs", "-autoexit", str(video_path)])

    if platform.system() == "Darwin":
        # ffplayはウィンドウを前面に出さないことがあるため、明示的に最前面に出す。
        time.sleep(1)
        subprocess.run(
            [
                "osascript", "-e",
                'tell application "System Events" to set frontmost of '
                '(first process whose name is "ffplay") to true',
            ],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )

    proc.wait()
