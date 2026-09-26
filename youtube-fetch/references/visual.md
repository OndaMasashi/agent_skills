# 映像を確かめる

字幕では分からないこと（画面の様子・スライドの文字・編集のカット）を確かめるときだけ使う。

- 置き場所はスクラッチパッド（セッション専用の作業フォルダ）だけ。動画は著作物なので、プロジェクトに置かない・コミットしない。使い終わったらファイルを名指しで消す
- 以下は 2026-09-26 に Windows（Git Bash）で動作を確認したコマンド

## 1. 低画質で全体を取る

```bash
uvx yt-dlp -f "bv*[height<=480][ext=mp4]+ba[ext=m4a]/b[height<=480]" --merge-output-format mp4 -P "<スクラッチパッド>" -o "video.%(ext)s" "<URL>"
```

- 14 分の動画で約 28MB、数秒で終わる
- `No supported JavaScript runtime could be found` の警告は出るが、480p はこれで取れる
- 「形式が見つからない」エラーになったら、deno（yt-dlp が YouTube の仕掛けを解くのに使う実行環境）が要る。`winget install DenoLand.Deno` をユーザーに提案する（勝手に入れない）

## 2. コマを画像にして Read で見る

一覧画像（区間を等間隔で並べる。まず全体をつかむ）:

```bash
ffmpeg -hide_banner -loglevel error -y -ss <開始秒> -t <長さ秒> -i video.mp4 -vf "fps=1/<間隔秒>,scale=320:-1,tile=5x3" -frames:v 1 sheet.png
```

- タイルの枚数（5x3 = 15）× 間隔が区間の長さ以上になるように決める。足りないと後半が入らない
- 1 枚 320px 幅なら、焼き込み字幕の文字まで読める

その他:

| 目的 | コマンド |
| :--- | :--- |
| 1 コマだけ | `ffmpeg -ss <秒> -i video.mp4 -frames:v 1 frame.png` |
| 一部を拡大 | `-vf "crop=<幅>:<高さ>:<x>:<y>,scale=1500:-1"` を足す |
| 場面の切り替わり（カット）の時刻 | `ffmpeg -i video.mp4 -vf "select='gt(scene,0.04)',metadata=print:file=scenes.txt" -an -f null -` → `scenes.txt` の `pts_time` |

## 3. 高画質の一部だけ要るとき

```bash
timeout 300 uvx yt-dlp -f "bv*[height<=1080][ext=mp4]" --download-sections "*00:10:40-00:11:20" -P "<スクラッチパッド>" -o "hi.%(ext)s" "<URL>"
```

- ⚠ 区間指定（`--download-sections`）は止まることがある。2026-09-26 に、480p・4 秒の区間で 400 秒を超えても終わらなかった（別の日の 1080p では成功している）。**必ず `timeout` を付ける**
- `timeout` で止めても、子の ffmpeg と python が残って待ち続けることがある。親子関係を確かめて、自分が起動したものだけを止める
  ```powershell
  Get-CimInstance Win32_Process | Where-Object { $_.Name -in 'yt-dlp.exe','ffmpeg.exe' } | Select-Object ProcessId,ParentProcessId,CommandLine
  ```
- 止まったら、1080p で全体を取って手元の ffmpeg で切る
