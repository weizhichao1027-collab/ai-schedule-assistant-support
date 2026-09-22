#!/usr/bin/env python3
"""Rebuild site image assets from the App Store screenshot sources.

Source of truth: 04_上架资料/多语言商店截图_2026-09-11/raw/<locale>/*.png
Outputs into dist/assets/: product screenshots (WebP) and Open Graph cards (PNG).

Run from the website repo root:
    python3 tools/build_assets.py
"""

from pathlib import Path
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
RAW = REPO.parent / "多语言商店截图_2026-09-11" / "raw"
OUT = REPO / "dist" / "assets"
ICON = REPO / "dist" / "assets" / "app-icon-192.png"

# Screens shown in the product-page gallery, in display order.
SHOTS = ["hero", "calendar", "accounting", "input", "statistics", "analysis"]
SHOT_WIDTH = 520  # 2x of the ~260px CSS rendering width

LOCALES = {"zh": "zh-Hans", "en": "en"}

CJK = "/System/Library/Fonts/Hiragino Sans GB.ttc"
LATIN = "/System/Library/Fonts/SFNS.ttf"

OG_TEXT_WIDTH = 540

OG = {
    "zh": {
        "font": CJK,
        "title": "记一下 JotIt",
        "lead": "说一句，日程和账目一起记好。",
        "meta": "iPhone · iOS 17+ · App Store 免费下载",
        "shots": ["hero", "calendar", "statistics"],
    },
    "en": {
        "font": LATIN,
        "title": "JotIt",
        "lead": "Plans and expenses, together.",
        "meta": "iPhone · iOS 17+ · Free on the App Store",
        "shots": ["hero", "calendar", "statistics"],
    },
}


def webp(src: Image.Image, dest: Path, quality: int = 80) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        src.save(tmp.name)
        subprocess.run(
            ["cwebp", "-quiet", "-q", str(quality), "-m", "6", tmp.name, "-o", str(dest)],
            check=True,
        )
    Path(tmp.name).unlink()


def build_shots() -> list[str]:
    written = []
    for lang, raw_locale in LOCALES.items():
        for name in SHOTS:
            src = RAW / raw_locale / f"{name}.png"
            im = Image.open(src).convert("RGB")
            height = round(im.height * SHOT_WIDTH / im.width)
            im = im.resize((SHOT_WIDTH, height), Image.LANCZOS)
            dest = OUT / "shots" / lang / f"{name}.webp"
            webp(im, dest)
            written.append(f"{dest.relative_to(OUT)} {SHOT_WIDTH}x{height} {dest.stat().st_size // 1024}KB")
    return written


def rounded(im: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius, fill=255)
    out = Image.new("RGBA", im.size)
    out.paste(im, (0, 0), mask)
    return out


def wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    if draw.textlength(text, font=font) <= width:
        return [text]
    lines, current = [], ""
    for word in text.split(" "):
        candidate = f"{current} {word}".strip()
        if current and draw.textlength(candidate, font=font) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def build_og() -> list[str]:
    written = []
    for lang, spec in OG.items():
        card = Image.new("RGB", (1200, 630), "#191a2b")
        draw = ImageDraw.Draw(card)
        draw.rectangle([0, 0, 1200, 8], fill="#7774ee")

        title_font = ImageFont.truetype(spec["font"], 62)
        lead_font = ImageFont.truetype(spec["font"], 32)
        meta_font = ImageFont.truetype(spec["font"], 25)

        icon = Image.open(ICON).convert("RGBA").resize((96, 96), Image.LANCZOS)
        card.paste(rounded(icon, 22), (80, 96), rounded(icon, 22))

        draw.text((80, 236), spec["title"], font=title_font, fill="#ffffff")
        y = 332
        for line in wrap(draw, spec["lead"], lead_font, OG_TEXT_WIDTH):
            draw.text((80, y), line, font=lead_font, fill="#d7d7e7")
            y += 46
        draw.text((80, 452), spec["meta"], font=meta_font, fill="#aaa6ff")
        draw.text((80, 500), "qishanlabs.com", font=meta_font, fill="#83839c")

        # Overlapping device shots, fanned out on the right.
        for index, name in enumerate(reversed(spec["shots"])):
            shot = Image.open(RAW / LOCALES[lang] / f"{name}.png").convert("RGB")
            shot = shot.resize((200, round(shot.height * 200 / shot.width)), Image.LANCZOS)
            shot = rounded(shot, 24)
            card.paste(shot, (640 + (2 - index) * 160, 98), shot)

        dest = OUT / f"og-jotit-{lang}.png"
        card.save(dest, optimize=True)
        written.append(f"{dest.name} 1200x630 {dest.stat().st_size // 1024}KB")
    return written


def build_favicon() -> list[str]:
    """Browsers and crawlers request /favicon.ico regardless of the <link> tags."""
    dest = OUT.parent / "favicon.ico"
    icon = Image.open(ICON).convert("RGBA")
    icon.save(dest, sizes=[(16, 16), (32, 32), (48, 48)])
    return [f"{dest.name} 16/32/48 {dest.stat().st_size // 1024}KB"]


if __name__ == "__main__":
    for line in build_shots() + build_og() + build_favicon():
        print(line)
