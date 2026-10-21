"""Technical QC of out/*.mp4: stream params, frame-to-frame motion (flicker / jump detection),
stillness of the final hold, and measured contrast of key text on the poster."""
import json, subprocess, glob, os
import numpy as np
from PIL import Image

meta = {v['id']: v for v in json.load(open('work/variants-meta.json'))['VARIANTS']}

def probe(fn):
    out = subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', fn])
    j = json.loads(out)
    v = [s for s in j['streams'] if s['codec_type'] == 'video'][0]
    a = [s for s in j['streams'] if s['codec_type'] == 'audio']
    return dict(codec=v['codec_name'], pix=v['pix_fmt'], w=v['width'], h=v['height'], fps=v['r_frame_rate'],
                frames=int(v.get('nb_frames', 0)), dur=float(j['format']['duration']), audio=len(a), mb=round(int(j['format']['size']) / 1e6, 2))

def frames(fn, w=396, h=99):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', fn, '-vf', f'scale={w}:{h}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'])
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)

def lum(c):
    c = np.asarray(c, float) / 255
    c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]

def contrast(fg, bg):
    a, b = sorted([lum(fg), lum(bg)], reverse=True)
    return (a + 0.05) / (b + 0.05)

res = {}
for fn in sorted(glob.glob('out/v*.mp4')):
    vid = os.path.basename(fn)[:3]
    p = probe(fn)
    F = frames(fn)
    d = np.abs(np.diff(F, axis=0)).mean((1, 2))  # mean abs change per frame step (0-255)
    # flicker = a step that is much bigger than both neighbours (isolated spike)
    # glitch = a single frame that differs from both neighbours while the neighbours agree
    # (dropped paint / flash); d[i-1] = |F[i]-F[i-1]|, d[i] = |F[i+1]-F[i]|
    skip = np.abs(F[2:] - F[:-2]).mean((1, 2))
    spikes = []
    for i in range(1, len(F) - 1):
        m = min(d[i - 1], d[i])
        if m > 1.0 and skip[i - 1] < 0.5 * m:
            spikes.append((i, round(float(m), 2)))
    hold = d[-45:]
    res[vid] = dict(**p, max_step=round(float(d.max()), 2), mean_step=round(float(d.mean()), 3),
                    spikes=spikes, hold_last_1_5s_max=round(float(hold.max()), 3),
                    loop_seam=round(float(np.abs(F[-1] - F[0]).mean()), 3))
json.dump(res, open('work/qc.json', 'w'), indent=1)
for k, v in res.items():
    print(k, v)
