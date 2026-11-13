#!/usr/bin/env python3
"""Generate a photo-derived ASCII portrait and local typing animation.

Requires Pillow: python -m pip install Pillow
Run from any directory:
  python scripts/generate_ascii_portrait.py --photo ../Snapchat-108467442.jpg
For another photo, set --crop LEFT TOP RIGHT BOTTOM (normalized coordinates).
No face generation, network calls, or modifications to the source photograph.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
BG = (6, 12, 16)
GREEN = (92, 248, 164)
CYAN = (97, 220, 236)
MUTED = (90, 117, 132)
RAMP = ' .,:;irsXA253hMHGS#9B&@'


def font(size: int, override: str | None = None) -> ImageFont.FreeTypeFont:
    candidates = [override] if override else []
    candidates += ['DejaVuSansMono.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
                   '/Library/Fonts/Courier New.ttf', 'C:/Windows/Fonts/consola.ttf']
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    raise SystemExit('Provide a monospace TrueType font with --font.')


def palette() -> Image.Image:
    """Fixed palette avoids flicker between animation frames."""
    colors = [BG]
    for target in [GREEN, CYAN, MUTED, (160, 133, 222)]:
        colors += [tuple(round(BG[c] + (target[c] - BG[c]) * n / 31) for c in range(3))
                   for n in range(1, 32)]
    colors += [BG] * (256 - len(colors))
    p = Image.new('P', (1, 1))
    p.putpalette([v for color in colors for v in color])
    return p


def indexed(im: Image.Image) -> Image.Image:
    return im.quantize(palette=palette(), dither=Image.Dither.NONE)


def terminal(size: tuple[int, int], label: str, face: ImageFont.FreeTypeFont) -> Image.Image:
    im = Image.new('RGB', size, BG)
    d = ImageDraw.Draw(im)
    for i, col in enumerate([GREEN, CYAN, (160, 133, 222)]):
        d.ellipse((18+i*13, 17, 23+i*13, 22), fill=col)
    d.text((65, 12), label, font=face, fill=MUTED)
    d.line((16, 36, size[0]-17, 36), fill=(28, 49, 58))
    return im


def portrait(photo: Path, out: Path, crop: list[float], columns: int, font_path: str | None) -> None:
    with Image.open(photo) as original:
        source = ImageOps.exif_transpose(original).convert('RGB')
    w, h = source.size
    box = tuple(round(v * (w if i % 2 == 0 else h)) for i, v in enumerate(crop))
    source = source.crop(box)
    gray = ImageOps.grayscale(source)
    gray = ImageOps.autocontrast(gray, cutoff=1)
    gray = ImageEnhance.Contrast(gray).enhance(1.18)
    gray = gray.filter(ImageFilter.UnsharpMask(radius=1.4, percent=120, threshold=3))
    glyph_font = font(12, font_path)
    small_font = font(10, font_path)
    cell_w, cell_h = 7, 12
    rows = round(columns * source.height / source.width * cell_w / cell_h)
    sampled = gray.resize((columns, rows), Image.Resampling.LANCZOS)
    # Sparse dark hair and dense facial highlights preserve the original light structure.
    values = list(sampled.get_flattened_data())
    chars = [RAMP[min(len(RAMP)-1, int((v/255)**0.85 * (len(RAMP)-1)))] for v in values]
    width, height = columns*cell_w+32, rows*cell_h+92
    base = terminal((width, height), 'manan@labs / portrait', small_font)
    final = base.copy()
    d = ImageDraw.Draw(final)
    for row in range(rows):
        for col in range(columns):
            idx = row*columns+col
            v = values[idx]
            target = CYAN if col > columns*.63 else GREEN
            strength = .40 + .60 * (v/255)
            color = tuple(round(c * strength) for c in target)
            d.text((16+col*cell_w, 47+row*cell_h), chars[idx], font=glyph_font, fill=color, stroke_width=0)
    d.text((16, height-25), '> portrait loaded_', font=small_font, fill=GREEN)
    final.save(out/'ascii-portrait.png', optimize=True)
    frames, durations = [indexed(base)], [350]
    steps = 36
    for step in range(1, steps+1):
        frame = base.copy()
        end = 47 + math.ceil(rows*step/steps)*cell_h
        frame.paste(final.crop((0, 38, width, end)), (0, 38))
        draw = ImageDraw.Draw(frame)
        if step < steps:
            draw.line((16, end, width-17, end), fill=(45, 97, 85))
            draw.text((16, height-25), f'> decoding {step*100//steps:02d}%_', font=small_font, fill=CYAN)
        else:
            frame = final.copy()
        frames.append(indexed(frame)); durations.append(75 if step < steps else 2600)
    for factor in [.8, .55, .3, .12]:
        frames.append(indexed(Image.blend(base, final, factor))); durations.append(90)
    frames[0].save(out/'ascii-portrait.gif', save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True, disposal=1)
    print(f'Portrait: {width}x{height}, {len(frames)} frames; crop={box}')


def typing(out: Path, font_path: str | None) -> None:
    face = font(16, font_path)
    small = font(10, font_path)
    frames, durations = [], []
    for role in ['AI/ML Engineer', 'Full-Stack Developer', 'Systems Developer', 'Aspiring Game Developer']:
        for end in range(0, len(role)+1, 2):
            im = terminal((352, 96), 'manan@labs / focus', small)
            ImageDraw.Draw(im).text((16, 54), '> '+role[:end]+'_', font=face, fill=CYAN)
            frames.append(indexed(im)); durations.append(85)
        im = terminal((352, 96), 'manan@labs / focus', small)
        ImageDraw.Draw(im).text((16, 54), '> '+role+'_', font=face, fill=GREEN)
        frames.append(indexed(im)); durations.append(1500)
    frames[0].save(out/'typing-intro.gif', save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True, disposal=1)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--photo', type=Path, default=ROOT.parent/'Snapchat-108467442.jpg')
    p.add_argument('--output', type=Path, default=ROOT/'assets')
    p.add_argument('--crop', type=float, nargs=4, default=[.306, .128, .718, .417],
                   metavar=('LEFT', 'TOP', 'RIGHT', 'BOTTOM'))
    p.add_argument('--columns', type=int, default=68)
    p.add_argument('--font', help='Path to a monospace TrueType font')
    args = p.parse_args()
    l, t, r, b = args.crop
    if not (0 <= l < r <= 1 and 0 <= t < b <= 1):
        p.error('--crop must be normalized coordinates inside the image')
    if not 32 <= args.columns <= 120:
        p.error('--columns must be between 32 and 120')
    args.output.mkdir(parents=True, exist_ok=True)
    portrait(args.photo, args.output, args.crop, args.columns, args.font)
    typing(args.output, args.font)
    for name in ['ascii-portrait.gif', 'ascii-portrait.png', 'typing-intro.gif']:
        print(f'{name}: {(args.output/name).stat().st_size:,} bytes')


if __name__ == '__main__':
    main()
