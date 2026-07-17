#!/usr/bin/env python3
"""
EngAI Xchange — offline YouTube thumbnail generator

Edit config.yaml (or pass flags), then:

    python generate.py
    python generate.py --image speakers/you.jpg --speaker "Name" --title "Talk title" --date "Mon D, YYYY"

Output: 1280×720 PNG in ./output/  (YouTube recommended size)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:
    print("Pillow is required. Install with:  pip install Pillow")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Brand
# ---------------------------------------------------------------------------

W, H = 1280, 720

INK = (15, 16, 20)
INK_SOFT = (26, 28, 36)
INK_MUTED = (44, 47, 58)
ROSE = (226, 154, 180)
ROSE_DEEP = (196, 92, 126)
ROSE_SOFT = (243, 208, 220)
WHITE = (255, 255, 255)
WHITE_DIM = (220, 218, 224)
WHITE_MUTED = (160, 162, 172)

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
OUTPUT_DIR = ROOT / "output"
SPEAKERS_DIR = ROOT / "speakers"
DEFAULT_CONFIG = ROOT / "config.yaml"

# Windows system fonts (Outfit-like geometric feel via Segoe UI)
FONT_REG = Path(r"C:\Windows\Fonts\segoeui.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\segoeuib.ttf")
FONT_SEMI = Path(r"C:\Windows\Fonts\seguisb.ttf")  # may not exist on all systems
FONT_FALLBACK = Path(r"C:\Windows\Fonts\arial.ttf")
FONT_FALLBACK_B = Path(r"C:\Windows\Fonts\arialbd.ttf")


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = []
    if bold:
        candidates += [FONT_BOLD, FONT_SEMI, FONT_FALLBACK_B, FONT_REG, FONT_FALLBACK]
    else:
        candidates += [FONT_SEMI if FONT_SEMI.exists() else None, FONT_REG, FONT_FALLBACK]
    for path in candidates:
        if path and path.exists():
            try:
                return ImageFont.truetype(str(path), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:60].strip("-") or "thumbnail"


def load_config(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return data if isinstance(data, dict) else {}
    except ImportError:
        # Minimal YAML-ish parser for our simple config (key: value)
        data: dict = {}
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                continue
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            data[key] = val
        return data


def resolve_path(p: str | Path) -> Path:
    path = Path(p)
    if not path.is_absolute():
        path = ROOT / path
    return path


def fit_cover(img: Image.Image, box_w: int, box_h: int) -> Image.Image:
    """Scale + center-crop to fill box (object-fit: cover)."""
    src_w, src_h = img.size
    scale = max(box_w / src_w, box_h / src_h)
    new_w = max(1, int(src_w * scale))
    new_h = max(1, int(src_h * scale))
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - box_w) // 2
    top = (new_h - box_h) // 2
    return img.crop((left, top, left + box_w, top + box_h))


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask


def wrap_text(
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
    draw: ImageDraw.ImageDraw,
    max_lines: int = 3,
) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
            if len(lines) >= max_lines:
                break
    if len(lines) < max_lines:
        lines.append(current)
    # Ellipsis if overflow
    if len(lines) == max_lines:
        remaining = " ".join(words[sum(len(l.split()) for l in lines[:-1]) :])
        # rebuild last line with ellipsis if needed
        last = lines[-1]
        if draw.textlength(last, font=font) > max_width or len(words) > sum(
            len(l.split()) for l in lines
        ):
            while last and draw.textlength(last + "…", font=font) > max_width:
                last = last[:-1].rstrip()
            lines[-1] = (last + "…") if last else "…"
    return lines


def draw_grid(base: Image.Image, color: tuple[int, int, int], alpha: int = 18) -> None:
    grid = Image.new("RGBA", base.size, (0, 0, 0, 0))
    g = ImageDraw.Draw(grid)
    step = 36
    for x in range(0, W, step):
        g.line([(x, 0), (x, H)], fill=(*color, alpha), width=1)
    for y in range(0, H, step):
        g.line([(0, y), (W, y)], fill=(*color, alpha), width=1)
    # Soft radial fade so grid is stronger mid-right
    base.alpha_composite(grid)


def paste_logo(canvas: Image.Image, dest: tuple[int, int], max_h: int = 56) -> int:
    """Paste logo-mark if present; return width used."""
    for name in ("logo-mark.png", "logo.png"):
        path = ASSETS / name
        if not path.exists():
            continue
        logo = Image.open(path).convert("RGBA")
        # Prefer the dark-bg mark; scale to max_h
        ratio = max_h / logo.height
        logo = logo.resize((max(1, int(logo.width * ratio)), max_h), Image.Resampling.LANCZOS)
        canvas.paste(logo, dest, logo)
        return logo.width
    return 0


def generate(
    image_path: Path,
    speaker: str,
    title: str,
    institution: str = "",
    date: str = "",
    badge: str = "Talk",
    output: Path | None = None,
) -> Path:
    if not image_path.exists():
        raise FileNotFoundError(f"Speaker image not found: {image_path}")

    canvas = Image.new("RGBA", (W, H), (*INK, 255))
    draw = ImageDraw.Draw(canvas)

    # Background gradient blocks
    for i in range(H):
        t = i / H
        r = int(INK[0] * (1 - t) + INK_SOFT[0] * t)
        g = int(INK[1] * (1 - t) + 24 * t)
        b = int(INK[2] * (1 - t) + 32 * t)
        draw.line([(0, i), (W, i)], fill=(r, g, b, 255))

    # Rose glow (right side, behind photo)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((W - 520, -80, W + 80, 520), fill=(*ROSE_DEEP, 40))
    gd.ellipse((W - 380, 280, W + 40, H + 120), fill=(*ROSE, 28))
    canvas = Image.alpha_composite(canvas, glow)
    draw = ImageDraw.Draw(canvas)

    draw_grid(canvas, ROSE, alpha=16)

    # Left accent bar
    draw.rectangle((0, 0, 10, H), fill=(*ROSE, 255))

    # ---- Photo panel (right) ----
    photo_w, photo_h = 460, 560
    photo_x = W - photo_w - 56
    photo_y = (H - photo_h) // 2

    speaker_img = Image.open(image_path).convert("RGB")
    speaker_img = fit_cover(speaker_img, photo_w, photo_h)

    # Soft vignette on photo
    photo_rgba = speaker_img.convert("RGBA")
    vignette = Image.new("L", (photo_w, photo_h), 0)
    vd = ImageDraw.Draw(vignette)
    vd.rounded_rectangle((0, 0, photo_w, photo_h), radius=28, fill=255)
    photo_rgba.putalpha(vignette)

    # Rose ring frame
    frame_pad = 6
    frame = Image.new("RGBA", (photo_w + frame_pad * 2, photo_h + frame_pad * 2), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)
    fd.rounded_rectangle(
        (0, 0, frame.width - 1, frame.height - 1),
        radius=32,
        outline=(*ROSE, 230),
        width=4,
    )
    # subtle outer glow
    glow_frame = frame.filter(ImageFilter.GaussianBlur(8))
    canvas.alpha_composite(glow_frame, (photo_x - frame_pad, photo_y - frame_pad))
    canvas.paste(photo_rgba, (photo_x, photo_y), photo_rgba)
    canvas.alpha_composite(frame, (photo_x - frame_pad, photo_y - frame_pad))
    draw = ImageDraw.Draw(canvas)

    # ---- Text column (left) ----
    left = 56
    text_max = photo_x - left - 48
    y = 48

    # Brand row
    logo_w = paste_logo(canvas, (left, y - 4), max_h=52)
    draw = ImageDraw.Draw(canvas)
    brand_font = load_font(28, bold=True)
    brand = "ENGAI XCHANGE"
    brand_x = left + (logo_w + 16 if logo_w else 0)
    # If logo already includes wordmark, still add clean text for legibility at small size
    if logo_w < 120:
        draw.text((brand_x, y + 8), brand, font=brand_font, fill=WHITE)
        brand_end = brand_x + int(draw.textlength(brand, font=brand_font))
    else:
        brand_end = left + logo_w

    y = 48 + 64

    # Badge + date chips
    chip_font = load_font(20, bold=True)
    chips = []
    if badge:
        chips.append((badge.upper(), ROSE_DEEP, WHITE))
    if date:
        chips.append((date, INK_MUTED, ROSE_SOFT))

    cx = left
    for label, bg, fg in chips:
        pad_x, pad_y = 14, 8
        tw = int(draw.textlength(label, font=chip_font))
        chip_w, chip_h = tw + pad_x * 2, 34
        draw.rounded_rectangle((cx, y, cx + chip_w, y + chip_h), radius=17, fill=bg)
        draw.text((cx + pad_x, y + pad_y - 1), label, font=chip_font, fill=fg)
        cx += chip_w + 12

    y += 56

    # Kicker
    kicker_font = load_font(18, bold=False)
    draw.text((left, y), "WEEKLY RESEARCH EXCHANGE", font=kicker_font, fill=ROSE)
    y += 36

    # Speaker name
    name_font = load_font(56, bold=True)
    name_lines = wrap_text(speaker, name_font, text_max, draw, max_lines=2)
    for line in name_lines:
        draw.text((left, y), line, font=name_font, fill=WHITE)
        y += 62

    # Institution
    if institution:
        inst_font = load_font(24, bold=False)
        draw.text((left, y), institution, font=inst_font, fill=WHITE_MUTED)
        y += 40

    # Accent line
    y += 8
    draw.rounded_rectangle((left, y, left + 72, y + 5), radius=3, fill=ROSE)
    y += 28

    # Title
    title_font = load_font(30, bold=False)
    title_lines = wrap_text(title, title_font, text_max, draw, max_lines=3)
    for line in title_lines:
        draw.text((left, y), line, font=title_font, fill=WHITE_DIM)
        y += 40

    # Bottom tagline
    foot_font = load_font(18, bold=False)
    footer = "engai-exchange.github.io"
    draw.text((left, H - 52), footer, font=foot_font, fill=WHITE_MUTED)

    # Corner rose dots (subtle brand mark)
    for i, (dx, dy) in enumerate([(W - 36, 28), (W - 28, 40), (W - 44, 40)]):
        r = 4 if i else 5
        draw.ellipse((dx - r, dy - r, dx + r, dy + r), fill=ROSE if i == 0 else ROSE_DEEP)

    # Export
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if output is None:
        base = slugify(f"{speaker}-{date or 'session'}")
        output = OUTPUT_DIR / f"{base}.png"
    else:
        output = resolve_path(output)
        if output.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            output = output.with_suffix(".png")
        output.parent.mkdir(parents=True, exist_ok=True)

    rgb = Image.new("RGB", (W, H), INK)
    rgb.paste(canvas, mask=canvas.split()[-1])
    rgb.save(output, "PNG", optimize=True)
    return output


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Generate EngAI Xchange YouTube thumbnails")
    p.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to config.yaml")
    p.add_argument("--image", help="Speaker image path")
    p.add_argument("--speaker", help="Speaker name")
    p.add_argument("--title", help="Talk title")
    p.add_argument("--institution", default=None, help="Affiliation")
    p.add_argument("--date", default=None, help="Date label")
    p.add_argument("--badge", default=None, help="Badge text (Talk, LIVE, …)")
    p.add_argument("--output", default=None, help="Output path")
    return p


def main() -> int:
    args = build_parser().parse_args()
    cfg = load_config(Path(args.config)) if args.config else {}

    image = args.image or cfg.get("image")
    speaker = args.speaker or cfg.get("speaker")
    title = args.title or cfg.get("title")
    institution = (
        args.institution if args.institution is not None else cfg.get("institution", "")
    )
    date = args.date if args.date is not None else cfg.get("date", "")
    badge = args.badge if args.badge is not None else cfg.get("badge", "Talk")
    out = args.output or cfg.get("output") or None

    missing = [k for k, v in [("image", image), ("speaker", speaker), ("title", title)] if not v]
    if missing:
        print(f"Missing required fields: {', '.join(missing)}")
        print("Edit config.yaml or pass --image / --speaker / --title")
        return 1

    out_path = Path(out) if out else None
    if out_path and not out_path.is_absolute() and out_path.parent == Path("."):
        out_path = OUTPUT_DIR / out_path.name

    try:
        result = generate(
            image_path=resolve_path(image),
            speaker=str(speaker),
            title=str(title),
            institution=str(institution or ""),
            date=str(date or ""),
            badge=str(badge or "Talk"),
            output=out_path,
        )
    except Exception as e:
        print(f"Error: {e}")
        return 1

    print(f"Saved: {result}")
    print(f"Size:  {W}×{H} (YouTube thumbnail)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
