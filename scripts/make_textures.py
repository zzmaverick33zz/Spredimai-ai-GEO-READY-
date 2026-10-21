#!/usr/bin/env python3
"""Textures for the 3D beats, cut from the client's own photos (see MEDIA_MAP.md)."""
import os
from PIL import Image
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(R, 'source-media'); O = os.path.join(R, 'public', 'media', '3d'); os.makedirs(O, exist_ok=True)
site = sorted(f for f in os.listdir(S + '/site') if not f.endswith('logo-2.png'))
def crop(path, box, size, name, q=80):
    im = Image.open(path).convert('RGB'); w, h = im.size
    l, t, r, b = box
    im.crop((int(l * w), int(t * h), int(r * w), int(b * h))).resize(size, Image.LANCZOS).save(f'{O}/{name}.webp', quality=q, method=6)
# cut end with rings (fresh cross-section, zip 20.16.20), square around the rings
crop(S + '/zip-drive-download-1/WhatsApp Image 2026-10-09 at 20.16.20.jpeg', (0.053, 0.215, 0.787, 0.765), (1024, 1024), 'rings')
# dated disc with tape (chat 11)
crop(S + '/chat-photos/11.jpg', (0.106, 0.0, 0.856, 1.0), (1024, 1024), 'disc')
# opened trunk: golden-brown interior of the slab on the saw (chat 13), tall strip
crop(S + '/chat-photos/14.jpg', (0.29, 0.15, 0.71, 1.0), (512, 1380), 'inside')
# dark brushed oak surface for the bark (site photo 37 index)
crop(S + '/site/' + site[37], (0.0, 0.0, 1.0, 1.0), (1024, 768), 'bark')
# herringbone / chevron for the floor (site photo 61)
crop(S + '/site/' + site[61], (0.0, 0.2, 1.0, 0.8), (1024, 700), 'chevron')
for f in sorted(os.listdir(O)): print(f, os.path.getsize(f'{O}/{f}') // 1024, 'KB')
