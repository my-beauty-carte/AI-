# AI-

会場開催のセミナーを録音し、そこから自動で「振り返りスライド動画」を生成して
再生するまでのパイプライン (`seminar_auto`)。

## できること

1. 会場PC上でセミナーの音声を録音
2. 録音停止後、以下を**すべて自動で**実行
   - 文字起こし(OpenAI Whisper API)
   - 要点抽出とスライド構成の生成(Claude API)
   - スライド(.pptx)の生成
   - スライド + 音声ナレーション(自動読み上げ)による振り返り動画(.mp4)の生成
   - 生成した動画をフルスクリーンで自動再生

手を動かすのは「録音開始」と「録音終了」のEnterキー2回だけで、そこから動画再生まで
自動で進みます。

## 動画の長さについて

既定では **約3分(180秒)** の振り返り動画になります。
スライド1枚あたり目安18秒 × 枚数 で長さが決まる仕組みで、`.env` の
`SEMINAR_TARGET_VIDEO_SECONDS` / `SEMINAR_SECONDS_PER_SLIDE` で調整できます
(例: 5分の動画にしたい場合は `SEMINAR_TARGET_VIDEO_SECONDS=300`)。
セミナー本編の長さに関わらず、要点だけを厳選した短いダイジェストになります。

## 前提条件

会場のノートPC1台で完結する構成です。以下が必要です。

- Python 3.10以上
- インターネット接続(Whisper APIとClaude APIの呼び出しに使用)
- コマンドラインツール
  - `ffmpeg` / `ffprobe` / `ffplay`(録音・動画生成・再生に使用)
  - LibreOffice Impress(`soffice` + `libreoffice-impress`。core/commonだけではpptxの読み込みに失敗するため、Impressコンポーネントも必須)(スライド→PDF変換に使用)
  - `pdftoppm` (poppler-utils)(PDF→画像変換に使用)
  - 日本語フォント「Noto Sans JP」(macOSの場合 `brew install --cask font-noto-sans-jp`。
    macOS標準の「Hiragino Sans」はLibreOfficeのheadless実行では認識されず、日本語が
    表示されないため、通常のフォントファイルとしてインストールされるNoto Sans JPを使う)
- APIキー
  - `ANTHROPIC_API_KEY`(スライド構成生成)
  - `OPENAI_API_KEY`(文字起こし)

## セットアップ

```bash
pip install -r requirements.txt
cp .env.example .env   # ANTHROPIC_API_KEY / OPENAI_API_KEY を記入
```

マイク入力デバイスは通常OSの既定デバイスで動作します。うまく録音できない場合は、
以下でデバイス名を確認し `.env` の `SEMINAR_AUDIO_DEVICE` に設定してください。

- Windows: `ffmpeg -list_devices true -f dshow -i dummy`
- macOS: `ffmpeg -f avfoundation -list_devices true -i ""`
- Linux: `pactl list sources short`

## 使い方

```bash
python -m seminar_auto.pipeline
```

1. セミナー開始時にEnterキーを押す(録音開始)
2. セミナー終了時にもう一度Enterキーを押す(録音停止)
3. 休憩・質疑応答の間に自動処理(文字起こし→スライド生成→動画生成)が進む
4. 動画が自動で全画面再生される

出力ファイルは `seminar_output/`(`SEMINAR_WORK_DIR` で変更可)に保存されます。
