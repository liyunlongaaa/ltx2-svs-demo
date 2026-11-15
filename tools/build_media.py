#!/usr/bin/env python3
"""Rebuild web videos, posters and the demo manifest from ../../videos.

Usage: python3 tools/build_media.py [--force]

To feature different clips, edit SELECTION below: one ordered list of source
filenames per (language, length) group. The order of the list is the order the
cards appear on the page. Removed clips are deleted from assets/ on rebuild.
--force re-encodes every clip instead of keeping existing output files.
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(os.path.dirname(ROOT), "videos")
OUT_VIDEO = os.path.join(ROOT, "assets", "videos")
OUT_POSTER = os.path.join(ROOT, "assets", "posters")

# --------------------------------------------------------------------------
# WHICH CLIPS TO SHOW  <-- edit only this block when swapping songs
# Filenames are relative to ../videos/<lang>/<group>/ .
# --------------------------------------------------------------------------
SELECTION = {
    ("zh", "5s"): [
        "dualar_s0_dmd_step000600_b3_seed42.mp4",
        "dualar_s0_dmd_step000600_b4_seed42.mp4",
        "dualar_s0_dmd_step000600_b5_seed42.mp4",
    ],
    ("zh", "10s"): [
        "dualar_s0_dmd_step000600_b8_seed42.mp4",
        "dualar_s0_dmd_step000600_b9_seed42.mp4",
        "dualar_s0_dmd_step000600_b9_seed42 copy 2.mp4",
    ],
    ("zh", "60s"): [
        "dualar_s0_dmd_step000600_b60_seed42.mp4",
        "dualar_s0_dmd_step000600_b62_seed42.mp4",
        "dualar_s0_dmd_step000600_b65_seed42.mp4",
    ],
    ("en", "5s"): [
        "dualar_s0_dmd_step000600_b5_seed42_1.mp4",
        "dualar_s0_dmd_step000600_b5_seed42.mp4",
        "dualar_s0_dmd_step000600_b8_seed42.mp4",
    ],
    ("en", "10s"): [
        "dualar_s0_dmd_step000600_b8_seed42_.mp4",
        "dualar_s0_dmd_step000600_b8_seed42_2.mp4",
        "dualar_s0_dmd_step000600_b8_seed42.mp4",
    ],
    ("en", "60s"): [
        "dualar_s0_dmd_step000600_b60_seed42.mp4",
        "dualar_s0_dmd_step000600_b61_seed42.mp4",
        "dualar_s0_dmd_step000600_b65_seed42.mp4",
    ],
}
# --------------------------------------------------------------------------

LANGS = [("zh", "Mandarin"), ("en", "English")]
GROUPS = [("5s", "5 s"), ("10s", "10 s"), ("60s", "60 s")]


def probe(path, key):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", f"stream={key}", "-of", "csv=p=0", path])
    return out.decode().strip().split("\n")[0]


def main():
    force = "--force" in sys.argv
    os.makedirs(OUT_VIDEO, exist_ok=True)
    os.makedirs(OUT_POSTER, exist_ok=True)

    # Fail before touching anything if the selection names a missing file.
    missing = []
    for (lang, group), names in SELECTION.items():
        d = os.path.join(SRC, lang, group)
        for name in names:
            if not os.path.exists(os.path.join(d, name)):
                missing.append(f"videos/{lang}/{group}/{name}")
    if missing:
        sys.exit("Missing source clips:\n  " + "\n  ".join(missing))

    entries, index, expected = [], 0, set()
    for lang, lang_label in LANGS:
        for group, group_label in GROUPS:
            names = SELECTION.get((lang, group), [])
            for n, name in enumerate(names, 1):
                index += 1
                src = os.path.join(SRC, lang, group, name)
                dur = float(probe(src, "duration"))
                stem = f"{lang}-{group}-{n:02d}"
                vpath = os.path.join(OUT_VIDEO, stem + ".mp4")
                ppath = os.path.join(OUT_POSTER, stem + ".jpg")
                expected.update({stem + ".mp4", stem + ".jpg"})
                if force or not os.path.exists(vpath):
                    # Remux with faststart so playback can begin before the
                    # whole file has downloaded. No re-encode.
                    subprocess.check_call([
                        "ffmpeg", "-v", "error", "-y", "-i", src,
                        "-c", "copy", "-movflags", "+faststart", vpath])
                if force or not os.path.exists(ppath):
                    t = min(2.0, max(0.2, dur * 0.3))
                    subprocess.check_call([
                        "ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", src,
                        "-frames:v", "1", "-vf", "scale=512:512", "-q:v", "3", ppath])
                entries.append({
                    "id": stem,
                    "lang": lang,
                    "langLabel": lang_label,
                    "group": group,
                    "duration": round(dur, 2),
                    "video": f"assets/videos/{stem}.mp4",
                    "poster": f"assets/posters/{stem}.jpg",
                    "source": os.path.relpath(src, ROOT),
                })
                print(f"[{index}] {stem}  {dur:.1f}s  {name}")

    # Drop outputs that are no longer in the selection.
    for directory in (OUT_VIDEO, OUT_POSTER):
        for f in os.listdir(directory):
            if f not in expected:
                os.remove(os.path.join(directory, f))
                print(f"removed stale {os.path.relpath(os.path.join(directory, f), ROOT)}")

    with open(os.path.join(ROOT, "assets", "data", "videos.js"), "w") as f:
        f.write("// Generated by tools/build_media.py — edit that script, not this file.\n")
        f.write("window.DEMO_VIDEOS = ")
        json.dump(entries, f, indent=2, ensure_ascii=False)
        f.write(";\n")
    print(f"wrote {len(entries)} entries")


if __name__ == "__main__":
    main()
