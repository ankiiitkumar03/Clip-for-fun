"""Render an opt-in Remotion overlay, add Whisper captions, and composite with FFmpeg.

The existing clip.py and publishing workflows remain independent of this renderer.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


STYLES = {
    "clean": {
        "card": "&H30211A&",       # dark warm brown, ASS BGR order
        "accent": "&H8AD6B8&",     # muted mint
        "primary": "&HFAF6F0&",
        "secondary": "&HBDD2C8&",
        "kicker": "QUICK EXPLAINER",
    },
    "gta": {
        "card": "&H26150A&",
        "accent": "&H00E6FF&",
        "primary": "&HFFFFFF&",
        "secondary": "&H00E6FF&",
        "kicker": "CLIP HIGHLIGHT",
    },
}
HERE = Path(__file__).resolve().parent
MOTION_DIR = HERE / "motion"


def _ass_time(seconds):
    centiseconds = max(0, round(float(seconds) * 100))
    hours, centiseconds = divmod(centiseconds, 360000)
    minutes, centiseconds = divmod(centiseconds, 6000)
    secs, centiseconds = divmod(centiseconds, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"


def _ass_text(text):
    return (str(text).replace("\\", "\\\\").replace("{", "\\{")
            .replace("}", "\\}").replace("\n", " "))


def build_ass(title, duration, style="clean", include_motion=True):
    """Create a small animated title card and persistent progress rail."""
    colors = STYLES[style]
    end = _ass_time(duration)
    title = _ass_text(title)
    kicker = colors["kicker"]
    head = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n"
        "WrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\n"
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,"
        "Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,"
        "Alignment,MarginL,MarginR,MarginV,Encoding\n"
        f"Style: Title,Arial,76,{colors['primary']},&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,"
        "100,100,0,0,1,0,0,7,0,0,0,1\n"
        f"Style: Kicker,Arial,30,{colors['secondary']},&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,"
        "100,100,2,0,1,0,0,7,0,0,0,1\n"
        "Style: Art,Arial,30,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,"
        "100,100,0,0,1,0,0,7,0,0,0,1\n\n"
        "[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n"
    )
    events = [
        # Soft, translucent title card, placed over the lower body area.
        f"Dialogue: 0,0:00:00.00,0:00:03.50,Art,,0,0,0,,{{\\an7\\pos(66,1320)\\fad(180,350)\\p1\\bord0\\shad0\\1c{colors['card']}\\alpha&H28&}}m 0 0 l 948 0 l 948 202 l 0 202{{\\p0}}",
        f"Dialogue: 1,0:00:00.00,0:00:03.50,Art,,0,0,0,,{{\\an7\\pos(66,1320)\\fad(180,350)\\p1\\bord0\\shad0\\1c{colors['accent']}}}m 0 0 l 10 0 l 10 202 l 0 202{{\\p0}}",
        f"Dialogue: 2,0:00:00.00,0:00:03.50,Kicker,,0,0,0,,{{\\an7\\move(102,1376,102,1352,0,260)\\fad(160,300)}}{kicker}",
        f"Dialogue: 2,0:00:00.00,0:00:03.50,Title,,0,0,0,,{{\\an7\\move(98,1490,98,1430,0,300)\\fad(130,330)\\t(0,280,\\fscx103\\fscy103)\\t(280,420,\\fscx100\\fscy100)}}{title}",
        # Fine progress rail and moving mint marker.
        f"Dialogue: 0,0:00:00.00,{end},Art,,0,0,0,,{{\\an7\\pos(66,1854)\\p1\\bord0\\shad0\\1c&HFFFFFF&\\alpha&H90&}}m 0 0 l 948 0 l 948 4 l 0 4{{\\p0}}",
        f"Dialogue: 1,0:00:00.00,{end},Art,,0,0,0,,{{\\an7\\move(66,1854,1014,1854,0,{int(duration * 1000)})\\p1\\bord0\\shad0\\1c{colors['accent']}}}m 0 0 l 42 0 l 42 4 l 0 4{{\\p0}}",
    ]
    if include_motion and style == "gta":
        # Minimal corner marks hold a game HUD frame without covering the center.
        events.extend([
            f"Dialogue: 0,0:00:00.00,{end},Art,,0,0,0,,{{\\an7\\pos(42,52)\\p1\\bord0\\shad0\\1c{colors['accent']}\\alpha&H40&}}m 0 46 l 0 0 l 46 0 l 46 5 l 5 5 l 5 46{{\\p0}}",
            f"Dialogue: 0,0:00:00.00,{end},Art,,0,0,0,,{{\\an7\\pos(992,52)\\p1\\bord0\\shad0\\1c{colors['accent']}\\alpha&H40&}}m 0 0 l 46 0 l 46 46 l 41 46 l 41 5 l 0 5{{\\p0}}",
            f"Dialogue: 0,0:00:00.00,{end},Art,,0,0,0,,{{\\an7\\pos(42,1818)\\p1\\bord0\\shad0\\1c{colors['accent']}\\alpha&H40&}}m 0 0 l 5 0 l 5 41 l 46 41 l 46 46 l 0 46{{\\p0}}",
            f"Dialogue: 0,0:00:00.00,{end},Art,,0,0,0,,{{\\an7\\pos(992,1818)\\p1\\bord0\\shad0\\1c{colors['accent']}\\alpha&H40&}}m 41 0 l 46 0 l 46 46 l 0 46 l 0 41 l 41 41{{\\p0}}",
        ])
    return head + ("\n".join(events) if include_motion else "") + "\n"


def _merge_caption_events(motion_ass, caption_ass):
    """Combine the existing clipper's timed, masked captions with motion overlays."""
    style_lines = []
    dialogue_lines = []
    in_styles = False
    in_events = False
    for line in caption_ass.splitlines():
        if line == "[V4+ Styles]":
            in_styles, in_events = True, False
        elif line == "[Events]":
            in_styles, in_events = False, True
        elif line.startswith("["):
            in_styles = in_events = False
        elif in_styles and line.startswith("Style:"):
            style_lines.append(line)
        elif in_events and line.startswith("Dialogue:"):
            dialogue_lines.append(line)
    insertion = "\n".join(style_lines) + "\n\n[Events]"
    merged = motion_ass.replace("\n[Events]", "\n" + insertion, 1)
    return merged + "\n" + "\n".join(dialogue_lines) + "\n"


def _transcribe_words(source, start, duration, out_dir):
    """Transcribe the selected interval locally using the clipper's cached Whisper model."""
    from clip import WordTimings, load_audio, whisper_words

    with tempfile.NamedTemporaryFile(suffix=".wav", prefix="motion-audio-", dir=out_dir,
                                     delete=False) as wav_file:
        wav_path = Path(wav_file.name)
    try:
        extract = subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{start:.3f}",
            "-i", str(source), "-t", f"{duration:.3f}", "-vn", "-ac", "1", "-ar", "16000",
            "-c:a", "pcm_s16le", str(wav_path),
        ], capture_output=True, text=True)
        if extract.returncode:
            raise RuntimeError(extract.stderr[-1500:] or "Could not extract audio for Whisper")
        words = whisper_words(load_audio(str(wav_path)))
        words = WordTimings(
            words, getattr(words, "spoken_language", "unknown"),
            getattr(words, "caption_language", "English"),
            getattr(words, "caption_fallback_reason", None),
        )
        print(f"Whisper: {len(words)} word timings, caption language "
              f"{getattr(words, 'caption_language', 'English')}")
        return words
    finally:
        wav_path.unlink(missing_ok=True)


def _captions_ass(words, duration, out_dir):
    from clip import write_ass

    with tempfile.NamedTemporaryFile(suffix=".ass", prefix="motion-captions-", dir=out_dir,
                                     delete=False) as caption_file:
        caption_path = Path(caption_file.name)
    try:
        write_ass(str(caption_path), words, 0, duration, None, caption_margin_v=220)
        return caption_path.read_text(encoding="utf-8")
    finally:
        caption_path.unlink(missing_ok=True)


def _caption_groups(words, duration):
    """Group Whisper word timings into short, non-overlapping caption phrases."""
    from clip import mask_word

    if getattr(words, "caption_language", "English") not in {"English", "Hinglish"}:
        return []
    inside = []
    for start, end, word in words:
        clean = mask_word(re.sub(r"[^\w'!?.,-]", "", word)).upper()
        if clean and 0 <= start < duration:
            inside.append((float(start), min(float(end), duration), clean))
    groups, group = [], []
    for item in inside:
        if group:
            previous = group[-1]
            phrase_length = sum(len(part[2]) + 1 for part in group) + len(item[2])
            if item[0] - previous[1] > 0.6 or len(group) >= 3 or phrase_length > 18 or re.search(r"[.!?]$", previous[2]):
                groups.append(group)
                group = []
        group.append(item)
    if group:
        groups.append(group)
    result = []
    for index, phrase in enumerate(groups):
        phrase_end = min(float(duration), phrase[-1][1] + 0.35)
        if index + 1 < len(groups):
            phrase_end = min(phrase_end, groups[index + 1][0][0])
        chars = sum(len(item[2]) for item in phrase) + len(phrase) - 1
        result.append({
            "start": phrase[0][0],
            "end": phrase_end,
            "fontSize": max(46, min(68, int(1050 / (0.74 * max(1, chars))))),
            "words": [{"start": start, "end": end, "text": text} for start, end, text in phrase],
        })
    return result


def _render_remotion_overlay(props, overlay_path):
    node = shutil.which("node")
    renderer_script = MOTION_DIR / "render-overlay.mjs"
    if not node or not renderer_script.is_file():
        raise RuntimeError("Remotion project files are missing.")
    if not (MOTION_DIR / "node_modules").is_dir():
        raise RuntimeError("Remotion dependencies are not installed; run `cd motion; npm ci` first.")
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", prefix="motion-props-",
                                     dir=overlay_path.parent, delete=False) as props_file:
        json.dump(props, props_file, ensure_ascii=False)
        props_path = Path(props_file.name)
    try:
        result = subprocess.run([node, str(renderer_script), str(props_path), str(overlay_path)],
                                cwd=MOTION_DIR, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stderr[-2500:] or result.stdout[-2500:] or "Remotion render failed")
    finally:
        props_path.unlink(missing_ok=True)


def _composite_remotion(source, target, overlay_path, start, duration):
    graph = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[base];"
        "[1:v]format=rgba[overlay];[base][overlay]overlay=0:0:shortest=1:format=auto[v]"
    )
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{start:.3f}",
        "-i", str(source), "-i", str(overlay_path), "-t", f"{duration:.3f}",
        "-filter_complex", graph, "-map", "[v]", "-map", "0:a?", "-af", "asetpts=PTS-STARTPTS",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-threads", "2",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
        str(target),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        target.unlink(missing_ok=True)
        raise RuntimeError(result.stderr[-2000:] or "FFmpeg composition failed")


def render(input_path, output_path, title, start=0, duration=20, style="clean", whisper_captions=False,
           captions_only=False, renderer="remotion"):
    source = Path(input_path).expanduser().resolve()
    target = Path(output_path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if start < 0 or duration <= 0:
        raise ValueError("start must be nonnegative and duration must be positive")
    if renderer not in {"remotion", "ffmpeg"}:
        raise ValueError("renderer must be 'remotion' or 'ffmpeg'")
    target.parent.mkdir(parents=True, exist_ok=True)
    if renderer == "remotion" and not (MOTION_DIR / "node_modules").is_dir():
        raise RuntimeError("Remotion dependencies are not installed; run `cd motion; npm ci` first.")
    words = _transcribe_words(source, start, duration, target.parent) if whisper_captions else None

    if renderer == "remotion":
        with tempfile.TemporaryDirectory(prefix="motion-render-", dir=target.parent) as temp_dir:
            overlay_path = Path(temp_dir) / "overlay.webm"
            props = {
                "title": title,
                "style": style,
                "durationSeconds": duration,
                "fps": 30,
                "width": 1080,
                "height": 1920,
                "captions": _caption_groups(words, duration) if words is not None else [],
                "includeMotion": not captions_only,
            }
            _render_remotion_overlay(props, overlay_path)
            _composite_remotion(source, target, overlay_path, start, duration)
        return target

    # FFmpeg/ASS stays available as a lower-memory fallback.
    overlay_ass = build_ass(title, duration, style, include_motion=not captions_only)
    if words is not None:
        overlay_ass = _merge_caption_events(overlay_ass, _captions_ass(words, duration, target.parent))
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".ass", prefix="motion-",
                                     dir=target.parent, delete=False) as ass_file:
        ass_name = os.path.basename(ass_file.name)
    try:
        Path(target.parent / ass_name).write_text(overlay_ass, encoding="utf-8")
        command = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{start:.3f}",
            "-i", str(source), "-t", f"{duration:.3f}", "-vf", f"ass={ass_name}",
            "-map", "0:v:0", "-map", "0:a?", "-c:v", "libx264", "-preset", "ultrafast",
            "-crf", "24", "-threads", "2", "-pix_fmt", "yuv420p", "-c:a", "aac",
            "-b:a", "128k", "-movflags", "+faststart", str(target),
        ]
        result = subprocess.run(command, cwd=target.parent, capture_output=True, text=True)
        if result.returncode:
            target.unlink(missing_ok=True)
            raise RuntimeError(result.stderr[-2000:] or "FFmpeg render failed")
    finally:
        Path(target.parent / ass_name).unlink(missing_ok=True)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--title", required=True)
    parser.add_argument("--start", type=float, default=0)
    parser.add_argument("--duration", type=float, default=20)
    parser.add_argument("--style", choices=tuple(STYLES), default="clean")
    parser.add_argument("--whisper-captions", action="store_true",
                        help="transcribe the selected range locally and burn in word-timed captions")
    parser.add_argument("--captions-only", action="store_true",
                        help="render Whisper captions without adding another title/HUD overlay")
    parser.add_argument("--renderer", choices=("remotion", "ffmpeg"), default="remotion",
                        help="Remotion motion overlays (default) or low-memory FFmpeg fallback")
    args = parser.parse_args()
    try:
        rendered = render(args.input, args.output, args.title, args.start, args.duration, args.style,
                          args.whisper_captions, args.captions_only, args.renderer)
    except (OSError, ValueError, RuntimeError) as error:
        parser.error(str(error))
    print(rendered)


if __name__ == "__main__":
    main()
