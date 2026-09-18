import json

from . import build_slides, config, outline, play_video, record, render_video, transcribe


def main() -> None:
    print("=== セミナー録音 → 自動スライド動画化パイプライン ===")
    input("Enterキーを押すと録音を開始します...")
    proc = record.start_recording(config.AUDIO_PATH)
    print("録音中です。セミナーが終わったら、もう一度Enterキーを押して録音を停止してください。")
    input()
    record.stop_recording(proc)
    print("録音を停止しました。ここから自動処理に入ります(休憩・質疑応答の間にお待ちください)。")

    print("[1/4] 音声を文字起こし中...")
    transcript = transcribe.transcribe(config.AUDIO_PATH)
    config.TRANSCRIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    config.TRANSCRIPT_PATH.write_text(transcript, encoding="utf-8")

    print("[2/4] スライド構成を生成中...")
    slides = outline.generate_outline(transcript, config.TARGET_VIDEO_SECONDS, config.SECONDS_PER_SLIDE)
    config.OUTLINE_PATH.write_text(json.dumps(slides, ensure_ascii=False, indent=2), encoding="utf-8")

    print("[3/4] スライド(.pptx)を生成中...")
    build_slides.build(slides, config.SLIDES_PATH)

    print("[4/4] 動画を生成中...")
    render_video.render(config.SLIDES_PATH, slides, config.VIDEO_PATH)

    play_video.play(config.VIDEO_PATH)


if __name__ == "__main__":
    main()
