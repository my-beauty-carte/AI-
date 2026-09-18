import re
import subprocess
import tempfile
from pathlib import Path

from gtts import gTTS

from . import config


def _render_slide_images(pptx_path: Path, out_dir: Path) -> list[Path]:
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), str(pptx_path)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    pdf_path = out_dir / (pptx_path.stem + ".pdf")
    prefix = out_dir / "slide"
    subprocess.run(
        ["pdftoppm", "-png", "-r", "150", str(pdf_path), str(prefix)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    def page_number(path: Path) -> int:
        match = re.search(r"(\d+)$", path.stem)
        return int(match.group(1)) if match else 0

    return sorted(out_dir.glob("slide-*.png"), key=page_number)


def _narrate_slide(text: str, out_path: Path) -> float:
    gTTS(text=text, lang=config.NARRATION_LANG).save(str(out_path))
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(out_path)],
        check=True, capture_output=True, text=True,
    )
    return float(probe.stdout.strip())


def _build_segment(image_path: Path, audio_path: Path, duration: float, out_path: Path) -> None:
    subprocess.run(
        [
            "ffmpeg", "-y", "-loop", "1", "-i", str(image_path), "-i", str(audio_path),
            "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac",
            "-pix_fmt", "yuv420p", "-shortest", "-t", str(duration),
            str(out_path),
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def _concat_segments(segment_paths: list[Path], list_file: Path, out_path: Path) -> None:
    list_file.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in segment_paths), encoding="utf-8"
    )
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(out_path)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def render(pptx_path: Path, slides: list[dict], output_path: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        images = _render_slide_images(pptx_path, tmp_dir)
        segments = []
        for i, (image_path, slide_data) in enumerate(zip(images, slides)):
            narration_text = slide_data["title"] + "。" + "。".join(slide_data["bullets"])
            audio_path = tmp_dir / f"narration_{i:03d}.mp3"
            narration_seconds = _narrate_slide(narration_text, audio_path)
            duration = max(narration_seconds + 1.0, config.MIN_SLIDE_SECONDS)

            segment_path = tmp_dir / f"segment_{i:03d}.mp4"
            _build_segment(image_path, audio_path, duration, segment_path)
            segments.append(segment_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        _concat_segments(segments, tmp_dir / "concat.txt", output_path)
