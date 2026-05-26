#!/usr/bin/env python3
"""
Render every page of every PDF deck in assets/work/decks/ to JPGs.
Outputs to assets/work/slides/<deck-basename>/page-001.jpg etc.
Writes a manifest.json the front-end uses to build the inline viewer.

Re-run this whenever the source decks change. Idempotent (overwrites).

Usage:
    python3 scripts/render-decks.py
    python3 scripts/render-decks.py --zoom 2.4 --quality 80

Requirements: PyMuPDF (fitz) and Pillow.
    pip install PyMuPDF Pillow
"""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Missing dep: pip install PyMuPDF", file=sys.stderr)
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("Missing dep: pip install Pillow", file=sys.stderr)
    sys.exit(1)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DECKS_DIR    = PROJECT_ROOT / "assets" / "work" / "decks"
SLIDES_DIR   = PROJECT_ROOT / "assets" / "work" / "slides"
MANIFEST     = SLIDES_DIR / "manifest.json"


def render_deck(pdf_path: Path, out_dir: Path, zoom: float, quality: int) -> int:
    """Render every page of pdf_path to out_dir as page-NNN.jpg. Returns slide count."""
    # Wipe and recreate the deck folder so old slides don't linger after edits
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    n_pages = len(doc)
    matrix = fitz.Matrix(zoom, zoom)

    for i in range(n_pages):
        pix = doc[i].get_pixmap(matrix=matrix, alpha=False)
        # Convert via Pillow so we can control JPG quality and strip metadata
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        out_path = out_dir / f"page-{i+1:03d}.jpg"
        img.save(out_path, format="JPEG", quality=quality, optimize=True, progressive=True)
    doc.close()
    return n_pages


def main():
    ap = argparse.ArgumentParser(description="Render PDF decks → slide JPGs + manifest.")
    ap.add_argument("--zoom", type=float, default=2.0,
                    help="Render zoom factor. 2.0 ≈ 144 DPI. Higher = sharper, bigger files.")
    ap.add_argument("--quality", type=int, default=78,
                    help="JPG quality 1–95. 78 is a good web sweet spot.")
    args = ap.parse_args()

    if not DECKS_DIR.exists():
        print(f"No decks folder at {DECKS_DIR}", file=sys.stderr)
        sys.exit(1)

    pdfs = sorted(DECKS_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {DECKS_DIR}", file=sys.stderr)
        sys.exit(1)

    SLIDES_DIR.mkdir(parents=True, exist_ok=True)

    manifest = {}
    total_pages = 0
    total_bytes = 0

    for pdf in pdfs:
        deck_id = pdf.stem  # e.g. "03-motilal-oswal"
        out_dir = SLIDES_DIR / deck_id
        print(f"  → {deck_id} … ", end="", flush=True)
        n = render_deck(pdf, out_dir, args.zoom, args.quality)
        deck_bytes = sum(p.stat().st_size for p in out_dir.glob("*.jpg"))
        print(f"{n} slides, {deck_bytes/1024/1024:.1f} MB")
        manifest[deck_id] = n
        total_pages += n
        total_bytes += deck_bytes

    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"\n  Manifest written: {MANIFEST.relative_to(PROJECT_ROOT)}")
    print(f"  Total: {total_pages} slides, {total_bytes/1024/1024:.1f} MB across {len(pdfs)} decks.")


if __name__ == "__main__":
    main()
