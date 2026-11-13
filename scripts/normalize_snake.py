#!/usr/bin/env python3
"""Limit snk SVG intrinsic width while preserving its original viewBox/animation."""
import re
import sys
from pathlib import Path
import xml.etree.ElementTree as ET


def normalize(source: Path, destination: Path):
    svg = source.read_text()
    root = ET.fromstring(svg)
    if root.tag != '{http://www.w3.org/2000/svg}svg':
        raise ValueError('Expected an SVG image')
    width = float(root.attrib['width'].removesuffix('px'))
    height = float(root.attrib['height'].removesuffix('px'))
    if width <= 0 or height <= 0:
        raise ValueError('Invalid snake dimensions')
    match = re.search(r'<svg\b[^>]*>', svg)
    tag = match.group()
    if 'viewBox=' not in tag:
        tag = tag[:-1] + f' viewBox="0 0 {width:g} {height:g}">'
    tag = re.sub(r'\bwidth="[^"]*"', 'width="480"', tag, count=1)
    tag = re.sub(r'\bheight="[^"]*"', f'height="{480*height/width:.2f}"', tag, count=1)
    normalized = svg[:match.start()] + tag + svg[match.end():]
    ET.fromstring(normalized)
    temporary = destination.with_suffix('.tmp')
    temporary.write_text(normalized)
    temporary.replace(destination)


if __name__ == '__main__':
    normalize(Path(sys.argv[1]), Path(sys.argv[2]))
