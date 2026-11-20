# AI workflow

This is the short public runbook. The paid guide adds setup screenshots, reusable prompts, channel/account setup, and a recurring unattended workflow.

## Discover and capture

1. Use a user-provided video or live link when available. Otherwise run `python find_streams.py "GTA 6 gameplay" --max 25 --json` and review the full candidate list. YouTube search order is based on view count, not current concurrent viewers.
2. Use only sources covered by the user's standing source-rights policy. If there is no policy or rights are unclear, ask once and do not capture until resolved.
3. Open and inspect the actual source video. Confirm gameplay is visible on screen; a title, thumbnail, commentary, or facecam alone is not enough. If the source cannot be visually inspected, ask for a screenshot or use a user-provided video.
4. Capture only after confirming gameplay and source authorization: `python clip.py STREAM_URL --gameplay-confirmed --max-seconds 0 --clip-len 30 --lead-in 6 --top 2`. For a local video, use test mode: `python clip.py --file "C:\videos\gameplay.mp4" --test --clip-len 30`.
5. The clipper ranks by live-chat reactions by default. It falls back to audio and speech if chat is unavailable or a chunk has no chat. Use `--moment-source combined` for chat, audio, and speech together, or `--moment-source audio` for audio and speech only. YouTube chat uses `YOUTUBE_API_KEY`; Twitch chat needs private Twitch credentials.

## Review and add motion graphics

6. Inspect each `output/*.mp4` and matching `output/*.json`. Confirm the lead-in and payoff are present, gameplay fills the 9:16 frame, captions are legible and synchronized, audio is intelligible, and metadata is accurate. The clipper keeps English in English and renders Hindi as romanized Hinglish; unsupported or uncertain speech has no captions. Source audio is unchanged.
7. To add motion graphics, install and use the optional Remotion renderer as described in [docs/MOTION-RENDERING.md](docs/MOTION-RENDERING.md). Render a review copy to `test_out`:

   ```powershell
   python motion_renderer.py "output\CLIP_ID.mp4" "test_out\CLIP_ID-motion-preview.mp4" --title "ACCURATE HOOK" --start 0 --duration 20 --style gta
   ```

   Choose `--style clean` for the restrained look. The clipper's MP4 already has burned-in captions, so do not add `--whisper-captions` to that input. Use that flag only for footage without captions. Remotion is the default renderer; `--renderer ffmpeg` selects the lower-memory fallback. Review that the title and HUD do not hide gameplay or existing captions.
8. A `motion_renderer.py` output is only an MP4; it does not create or update JSON metadata. Do not publish a `test_out` preview. If the motion-rendered version is the one to publish, save it under `output/` with a matching JSON file, set its `video` field to the final MP4 filename, and keep `approved` false until that exact video and metadata have been reviewed.

## Preview and publish

9. Preview the matching clip and metadata with `python zernio_publish.py output/CLIP_ID --scheduled-for YYYY-MM-DDTHH:MM:SS+05:30`. The dry run sends nothing.
10. For ordinary publishing, add `--publish` only for a specific clip the user approved. For unattended scheduled posting without per-clip approval, require one-time account/Zernio setup, `GTA_UNATTENDED_POSTS=1`, `--unattended`, a future schedule, and the user's standing source-rights policy. Never publish test clips or use `--now` in unattended mode.

Keep the Zernio API key and account IDs in the private environment, outside prompts, logs, metadata, and tracked files. A scheduled post may publish while the computer sleeps; finding sources, capturing streams, and rendering clips require an awake, connected computer.

For a no-plugin, copy-and-paste assistant prompt, see [GTA-CLIPPING-PROMPT.txt](GTA-CLIPPING-PROMPT.txt). Pasting the prompt requires no special AI setup; automatic clipping still requires access to this repository and its local dependencies.

## Standing unattended mode

After one-time setup, a user can set `GTA_UNATTENDED_POSTS=1` in the private environment and grant the agent a standing source-rights policy. The agent must use only authorized creators, use `--unattended`, set a future `--scheduled-for` time, and review Zernio's returned status. It must not use `--now` for unattended mode.
