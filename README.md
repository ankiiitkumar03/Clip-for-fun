# GTA Auto Clipper

SO built GTA Auto Clipper to find exciting moments in live gameplay and turn them into full-screen 9:16 clips. It adds short pop-up captions where each spoken word appears in yellow, and saves the finished video and its metadata on your computer.

I also added an optional Remotion motion-graphics workflow for titles and gaming-style overlays. The original clipping workflow still works on its own. When a clip is ready, a separate command can schedule it to YouTube and Instagram through Zernio.



## What SO built

- Search YouTube Live for a phrase such as `GTA 6` and return candidates as JSON.
- Require a visual gameplay check before live capture, so a title, discussion, or facecam-only stream is not mistaken for gameplay.
- Record live video in rolling chunks and find likely highlights. Chat reactions are the default signal; when chat is unavailable or has no messages, the clipper falls back to audio and speech. Combined scoring is also available.
- Include a lead-in before the detected moment (6 seconds by default), so the clip has context.
- Make English captions for English speech and romanized Hinglish captions for Hindi speech. Uncertain or unsupported speech is left without captions. Captions are short, one-line phrases of up to three words at a fixed position. Each spoken word pops in yellow, earlier words turn white, and the next phrase replaces the previous one. The source audio stays unchanged.
- Place captions in the lower third of the visible gameplay panel.
- Fill the 9:16 frame with gameplay by default (`--layout fill`). The crop is centered on the player, can shift away from a persistent side facecam, and can isolate gameplay in stacked portrait streams. Use `--layout fit` to show the full source over a blurred background.
- Reset audio and video timestamps before burning in captions.
- Mask swear words and sexual words in captions (for example, `s***`) while leaving the audio unchanged.
- Save MP4 clips and JSON metadata in `output/`. Clipping itself never posts anything.
- Schedule reviewed clips through Zernio with a dry run by default. Unattended scheduling is optional and requires account setup and a standing source-rights policy.

## Install

You need Python 3.10 or newer, FFmpeg in `PATH`, and Node.js or Deno. `yt-dlp` needs a JavaScript runtime to read YouTube; the clipper uses Node automatically when Deno is missing. OpenCV is used for face detection with `--crop`. A stable internet connection is needed for first-run speech-model downloads.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

For live-stream search and optional YouTube live-chat scoring, set a YouTube Data API key in your terminal. Keep keys out of prompts, source files, and GitHub:

```powershell
$env:YOUTUBE_API_KEY = "YOUR_YOUTUBE_DATA_API_KEY"
python find_streams.py "GTA 6" --max 25 --json
```

YouTube returns live search candidates in view-count order. That is not a reliable ranking of current concurrent viewers, so open and check a candidate before using it.

## Make clips

Before recording, open the candidate and confirm that actual GTA gameplay is visible. A GTA title, thumbnail, or talking head is not enough. Then start capture; it keeps running until you press `Ctrl+C`. Chat is used first by default. If chat is unavailable or has no messages for a chunk, the clipper uses audio and speech instead. Highlights are saved to `output/`.

```powershell
python clip.py "https://www.youtube.com/watch?v=VIDEO_ID" --gameplay-confirmed --max-seconds 0 --clip-len 30 --lead-in 6 --top 2
```

| Option | Default | Purpose |
| --- | ---: | --- |
| `--max-seconds` | `0` | Capture duration; `0` runs until stopped |
| `--chunk` | `90` | Analysis chunk size in seconds |
| `--clip-len` | `30` | Length of each rendered highlight |
| `--lead-in` | `6` | Seconds included before the detected moment |
| `--top` | `1` | Highlights kept from each chunk |
| `--gameplay-confirmed` | required for live capture | Confirm you inspected the stream and saw actual gameplay before recording |
| `--min-score` | `2.5` | Minimum moment score |
| `--layout` | `fill` | `fill` covers the 9:16 screen with gameplay; `fit` shows the full source over a blurred background |
| `--crop` | off | Older flag; same as `--layout fill` |
| `--moment-source` | `chat` | Choose `chat`, `combined`, or `audio` for highlight selection |
| `--spoken-language` | `auto` | Detect language and lock to Hindi (Hinglish captions) when the stream is clearly Hindi; use `hi` or `en` to force a language |
| `--no-chat` | off | Skip live-chat collection and use audio and speech only |
| `--output-dir` | `output/` | Choose another destination folder |

With `--moment-source chat`, chat reactions are used first. `combined` scores chat, audio, and speech together. `audio` uses audio and speech only. Chat mode falls back to audio and speech when it has no chat data.

To try a local video first, use test mode. Test clips go to `test_out/` and are not publishable:

```powershell
python clip.py --file "C:\videos\gameplay.mp4" --test --clip-len 30
```

## Preview motion overlays

I added an optional Remotion renderer for motion graphics. The Windows setup, rendering commands, templates, Whisper captions, and troubleshooting are in [docs/MOTION-RENDERING.md](docs/MOTION-RENDERING.md). This renderer is separate from the existing `clip.py` and publishing workflows.

## Schedule to YouTube and Instagram

Connect your YouTube account and an Instagram Creator or Business account to Zernio. Set the key and account IDs in your private environment:

```powershell
$env:ZERNIO_API_KEY = "YOUR_ZERNIO_API_KEY"
$env:ZERNIO_YOUTUBE_ACCOUNT_ID = "YOUR_YOUTUBE_ACCOUNT_ID"
$env:ZERNIO_INSTAGRAM_ACCOUNT_ID = "YOUR_INSTAGRAM_ACCOUNT_ID"
```

Review the clip and its JSON metadata, then set `"approved": true` in the metadata for the clip you want to publish. Preview the schedule first:

```powershell
python zernio_publish.py "output\gta-CLIP-ID" --scheduled-for "2026-11-18T12:00:00+05:30"
```

The preview is a dry run and sends nothing. To schedule the approved clip to both accounts, add `--publish`:

```powershell
python zernio_publish.py "output\gta-CLIP-ID" --scheduled-for "2026-11-18T12:00:00+05:30" --publish
```

For unattended posting, first test the output and make sure the AI agent only uses sources you have the right to use. Then set `GTA_UNATTENDED_POSTS=1` in the machine's private environment and run with `--publish --unattended`. A post already accepted by Zernio can publish while your computer is asleep; discovering sources and rendering clips still require an awake, connected computer.

