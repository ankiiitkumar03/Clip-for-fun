# Motion rendering on Windows

This guide is for people using the GTA Auto Clipper repository on Windows 11. The optional motion renderer adds a Remotion/React overlay to an existing video, uses FFmpeg to composite the result with the footage and audio, and can generate word-timed captions with the repository's local Whisper model.

It is a separate step from `clip.py`: it does not change the capture workflow, create publishing metadata, or post to Zernio. Keep the input clip and review the rendered MP4 before using it elsewhere.

## Requirements

- Python dependencies from `requirements.txt` and FFmpeg in `PATH`.
- Node.js and npm.
- Enough free memory to render with Chrome. Remotion is configured for one browser worker and serial encoding; render one clip at a time. Use the FFmpeg fallback if Remotion does not fit available memory.

## Install Remotion

Run these commands from the repository root in PowerShell:

```powershell
Set-Location motion
npm ci
node .\node_modules\@remotion\cli\remotion-cli.js browser ensure
Set-Location ..
```

`npm ci` installs the pinned packages from `motion/package-lock.json`. The browser command downloads Remotion's local Chrome Headless Shell. Run it again after a fresh `npm ci`, since npm may recreate `node_modules`.

The Remotion packages are not vendored in Git. They are installed locally in `motion/node_modules`, which is ignored by Git. Remotion's license terms provide a free license for eligible individuals and teams of up to three; check the [Remotion license FAQ](https://www.remotion.dev/docs/license/faq) for eligibility details.

## Render one clip

With the repository's virtual environment active, render a 20-second preview from a clip produced by the existing clipper:

```powershell
python .\motion_renderer.py ".\output\gta-CLIP-ID.mp4" ".\test_out\motion-preview.mp4" --title "GTA 6 STORY MODE" --start 0 --duration 20 --style gta
```

Replace `gta-CLIP-ID.mp4` with the actual source filename, and choose a title that matches the footage. The command writes only an MP4 preview to `test_out`; it leaves the source video and JSON metadata unchanged.

For a raw video that has no captions, ask local Whisper to generate timed captions:

```powershell
python .\motion_renderer.py ".\path\to\gameplay.mp4" ".\test_out\motion-preview.mp4" --title "GTA 6 STORY MODE" --start 0 --duration 20 --style gta --whisper-captions
```

The existing clipper already burns captions into its MP4 output, so do not add `--whisper-captions` when rendering one of those clips; that would duplicate the captions. The local Whisper model runs on the CPU. English and Hinglish are supported by the current clipper caption logic.

## Choose a style or fallback

- `--style gta` adds neon HUD corner marks.
- `--style clean` uses a restrained title-card look and is the default.
- `--renderer ffmpeg` selects the lower-memory ASS overlay fallback.
- `--captions-only` with `--whisper-captions` adds captions without another title card or HUD, for video that already contains a motion overlay.
- `--start` and `--duration` are seconds. The default duration is 20 seconds.

Remotion renders the transparent overlay as ProRes 4444 with one worker. FFmpeg then composites it with the video, crops the result to 9:16, preserves the source audio, and encodes the final MP4. Temporary overlays are removed after rendering.

## Troubleshooting

- **Chrome Headless Shell is missing:** from the `motion` folder, run `node .\node_modules\@remotion\cli\remotion-cli.js browser ensure`.
- **The `npm ci` output warns about `esbuild` scripts:** if npm exits successfully and reports the packages installed, continue. The Windows binary is supplied separately by npm; approve the install script only if Remotion reports an esbuild runtime error.
- **Remotion runs out of memory or is too slow:** render only one clip at a time, close memory-heavy applications, or use `--renderer ffmpeg`.
- **Need to publish the result:** review it first. This command does not update clip metadata or publish; use the project's established approval and Zernio workflow.
