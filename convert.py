import io
import subprocess
import sys
from pathlib import Path
from PIL import Image
import pillow_heif
from tqdm import tqdm

# ── CONFIG ────────────────────────────────────────────────────────────────────
INPUT_DIR        = Path("input")
OUTPUT_DIR       = Path("output")
PHOTO_OUT_FORMAT = "jpeg"          # or "png"
PHOTO_QUALITY    = 95              # JPEG quality (1–100)
VIDEO_CRF        = 18              # Video quality (0=best, 51=worst)
# ─────────────────────────────────────────────────────────────────────────────

PHOTO_EXTENSIONS = {".heic", ".heif", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
VIDEO_EXTENSIONS = {".mov", ".mp4", ".avi", ".mkv", ".m4v", ".3gp"}

def setup():
    OUTPUT_DIR.mkdir(exist_ok=True)
    pillow_heif.register_heif_opener()

def already_converted(src: Path, is_video: bool) -> bool:
    ext = "mp4" if is_video else PHOTO_OUT_FORMAT
    expected = OUTPUT_DIR / src.with_suffix(f".{ext}").name
    return expected.exists()

def convert_photo(src: Path):
    dest = OUTPUT_DIR / src.with_suffix(f".{PHOTO_OUT_FORMAT}").name

    counter = 1
    while dest.exists():
        dest = OUTPUT_DIR / f"{src.stem}_{counter}.{PHOTO_OUT_FORMAT}"
        counter += 1

    # ── Step 1: If HEIC/HEIF, convert to a temp PNG first using Pillow ────────
    # FFmpeg on Windows often lacks HEIC decoder, so we use Pillow to decode
    # then FFmpeg to encode — guaranteeing clean output
    src_for_ffmpeg = src
    temp_png = None

    if src.suffix.lower() in {".heic", ".heif"}:
        temp_png = OUTPUT_DIR / f"_temp_{src.stem}.png"
        try:
            heif_file = pillow_heif.read_heif(str(src))
            img = Image.frombytes(
                "RGB",
                heif_file.size,
                heif_file.data,
                "raw",
                heif_file.mode,
            )
            # Save as temp PNG — no color profile, no EXIF, clean pixels
            img.save(temp_png, "PNG", icc_profile=None)
            src_for_ffmpeg = temp_png
        except Exception as e:
            return False, f"HEIC decode failed: {e}"

    # ── Step 2: Use FFmpeg to encode final JPEG — strips ALL metadata ─────────
    cmd = [
        "ffmpeg",
        "-i", str(src_for_ffmpeg),
        "-vf", "scale=iw:ih",        # keep original resolution
        "-pix_fmt", "yuvj420p",      # standard JPEG chroma, universally supported
        "-q:v", "2",                 # quality (1=best, 31=worst; 2 ≈ 95%)
        "-map_metadata", "-1",       # STRIP ALL metadata (EXIF, ICC, GPS, etc.)
        "-y",
        str(dest),
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True
        )
        # Clean up temp PNG if created
        if temp_png and temp_png.exists():
            temp_png.unlink()

        if result.returncode == 0:
            return True, dest.name
        else:
            err = result.stderr.strip().split("\n")[-1]
            return False, err
    except FileNotFoundError:
        return False, "FFmpeg not found — make sure it's installed and in your PATH"

def convert_video(src: Path):
    dest = OUTPUT_DIR / src.with_suffix(".mp4").name

    counter = 1
    while dest.exists():
        dest = OUTPUT_DIR / f"{src.stem}_{counter}.mp4"
        counter += 1

    cmd = [
        "ffmpeg",
        "-i", str(src),
        "-c:v", "libx264",
        "-crf", str(VIDEO_CRF),
        "-preset", "medium",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-map_metadata", "-1",       # Strip metadata here too
        "-y",
        str(dest),
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            return True, dest.name
        else:
            err = result.stderr.strip().split("\n")[-1]
            return False, err
    except FileNotFoundError:
        return False, "FFmpeg not found — make sure it's installed and in your PATH"

def main():
    setup()

    all_files = [f for f in INPUT_DIR.iterdir() if f.is_file()]
    if not all_files:
        print(f"\n⚠  No files found in '{INPUT_DIR}/' — paste your iPhone files there first.")
        sys.exit(0)

    photos  = [f for f in all_files if f.suffix.lower() in PHOTO_EXTENSIONS]
    videos  = [f for f in all_files if f.suffix.lower() in VIDEO_EXTENSIONS]
    skipped = [f for f in all_files if f not in photos + videos]

    photos_to_do   = [f for f in photos if not already_converted(f, is_video=False)]
    videos_to_do   = [f for f in videos if not already_converted(f, is_video=True)]
    photos_skipped = len(photos) - len(photos_to_do)
    videos_skipped = len(videos) - len(videos_to_do)

    print(f"\n📁 Found: {len(photos)} photo(s), {len(videos)} video(s), {len(skipped)} unrecognised")

    if photos_skipped or videos_skipped:
        print(f"⏭  Already converted (skipping): {photos_skipped} photo(s), {videos_skipped} video(s)")

    if not photos_to_do and not videos_to_do:
        print("\n✅ Everything is already converted. Nothing to do!\n")
        sys.exit(0)

    print(f"🔄 To convert: {len(photos_to_do)} photo(s), {len(videos_to_do)} video(s)\n")

    # ── Convert Photos ─────────────────────────────────────────────────────────
    if photos_to_do:
        print(f"🖼  Converting photos to JPEG via FFmpeg...")
        ok = fail = 0
        for f in tqdm(photos_to_do, unit="file"):
            success, info = convert_photo(f)
            if success:
                ok += 1
            else:
                fail += 1
                tqdm.write(f"  ✗ {f.name}: {info}")
        print(f"   ✓ {ok} converted  ✗ {fail} failed\n")

    # ── Convert Videos ─────────────────────────────────────────────────────────
    if videos_to_do:
        print("🎬  Converting videos to MP4...")
        ok = fail = 0
        for f in tqdm(videos_to_do, unit="file"):
            tqdm.write(f"  → {f.name}")
            success, info = convert_video(f)
            if success:
                ok += 1
                tqdm.write(f"  ✓ Saved as {info}")
            else:
                fail += 1
                tqdm.write(f"  ✗ Failed: {info}")
        print(f"\n   ✓ {ok} converted  ✗ {fail} failed\n")

    if skipped:
        print(f"⚠  Skipped {len(skipped)} unrecognised file(s):")
        for f in skipped:
            print(f"   - {f.name}")

    print(f"\n✅ Done! Check your '{OUTPUT_DIR}/' folder.\n")

if __name__ == "__main__":
    main()