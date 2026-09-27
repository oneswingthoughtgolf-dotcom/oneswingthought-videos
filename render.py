"""Render a One Swing Thought tip video (1080x1920, 30fps) from a tip dict."""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
GREEN, CREAM, GOLD, INK, MUTED = (15, 55, 41), (245, 241, 232), (201, 162, 74), (15, 55, 41), (96, 110, 100)
G = "/usr/share/fonts/truetype/google-fonts/"
BODY, BODYB = G + "Poppins-Regular.ttf", G + "Poppins-Medium.ttf"

FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def F(p, s):
    try: return ImageFont.truetype(p, s)
    except OSError: return ImageFont.truetype(FALLBACK, s)
def SERIF(s, w=620):
    try:
        f = ImageFont.truetype(G + "Lora-Italic-Variable.ttf", s); f.set_variation_by_axes([w]); return f
    except OSError:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf", s)

def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def ease(t): t = max(0, min(1, t)); return 1 - (1 - t) ** 3

def tracked(d, x, y, text, f, fill, track, center=False):
    ws = [d.textlength(c, font=f) for c in text]
    if center: x = x - (sum(ws) + track * (len(text) - 1)) / 2
    for c, w in zip(text, ws): d.text((x, y), c, font=f, fill=fill, anchor="lm"); x += w + track

def divider(d, cx, y, col, half=90):
    d.line((cx - half, y, cx - 20, y), fill=col, width=4); d.line((cx + 20, y, cx + half, y), fill=col, width=4)
    d.ellipse((cx - 10, y - 10, cx + 10, y + 10), fill=col)

def header(d, fg):
    d.ellipse((88, 128, 148, 188), outline=fg, width=3)
    d.text((118, 160), "1", font=SERIF(38), fill=fg, anchor="mm")
    tracked(d, 172, 158, "ONE SWING THOUGHT", F(BODYB, 26), fg, 5)

def progress(d, t, total, track):
    d.rectangle((88, 1784, W - 88, 1788), fill=track)
    d.rectangle((88, 1784, 88 + int((W - 176) * t / total), 1788), fill=GOLD)

def frame(tip, t, total):
    hook_end, thought_end = 2.6, 6.0
    end_start = total - 3.2
    if t < hook_end:
        img = Image.new("RGB", (W, H), GREEN); d = ImageDraw.Draw(img)
        header(d, CREAM)
        tracked(d, 88, 720, tip["label"].upper(), F(BODYB, 30), GOLD, 5)
        f = SERIF(120); y = 800
        for i, line in enumerate(wrap(d, tip["hook"], f, W - 176)):
            k = ease((t - 0.12 * i) / 0.5)
            if k > 0: d.text((88, y + int((1 - k) * 40)), line, font=f, fill=CREAM)
            y += 150
        track = (45, 82, 68)
    elif t < end_start:
        img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
        header(d, GREEN)
        k = ease((t - hook_end) / 0.5)
        tracked(d, 88, 330, "TODAY'S THOUGHT", F(BODYB, 30), GOLD, 5)
        f = SERIF(96); y = 400 + int((1 - k) * 40)
        for line in wrap(d, tip["thought"], f, W - 176):
            d.text((88, y), line, font=f, fill=GREEN); y += 124
        d.line((88, y + 50, 178, y + 50), fill=GOLD, width=4); d.ellipse((188, y + 40, 208, y + 60), fill=GOLD)
        by = y + 140; bf = F(BODY, 52)
        for i, beat in enumerate(tip["beats"]):
            appear = thought_end + i * (end_start - thought_end) / len(tip["beats"])
            kb = ease((t - appear) / 0.45)
            if kb <= 0: break
            yoff = int((1 - kb) * 30)
            d.text((88, by + yoff - 6), f"{i + 1}.", font=SERIF(64), fill=GOLD)
            yy = by + yoff
            for line in wrap(d, beat, bf, W - 176 - 110):
                d.text((198, yy), line, font=bf, fill=INK); yy += 76
            by = max(by + 76, yy) + 64
        track = (224, 217, 200)
    else:
        img = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(img)
        k = ease((t - end_start) / 0.6); yo = int((1 - k) * 40)
        d.ellipse((190, 470 + yo, 890, 1170 + yo), outline=GREEN, width=5)
        d.ellipse((212, 492 + yo, 868, 1148 + yo), outline=GREEN, width=2)
        d.text((540, 800 + yo), "One Swing", font=SERIF(112), fill=GREEN, anchor="ms")
        d.text((552, 910 + yo), "Thought", font=SERIF(112), fill=GREEN, anchor="ms")
        divider(d, 540, 975 + yo, GOLD, 80)
        tracked(d, 540, 1300, "TRY IT TODAY.", F(BODYB, 40), GREEN, 6, center=True)
        d.text((540, 1380), "Follow for tomorrow's  " + tip.get("handle", "@oneswingthoughtgolf"), font=F(BODY, 34), fill=MUTED, anchor="mm")
        return img
    progress(d, t, total, track)
    return img

def render(tip, out, total=20.0):
    tmp = out + ".frames"; os.makedirs(tmp, exist_ok=True)
    n = int(total * FPS)
    for i in range(n):
        frame(tip, i / FPS, total).save(f"{tmp}/{i:05d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/%05d.png",
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-c:a", "aac", out], check=True)
    subprocess.run(["rm", "-rf", tmp])

if __name__ == "__main__":
    tip = json.load(open(sys.argv[1])); render(tip, sys.argv[2])
