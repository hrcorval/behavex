"""Generate a GitHub social preview image for BehaveX (1280x640 PNG)."""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1280, 640
OUT = os.path.join(os.path.dirname(__file__), "..", "img", "social_preview.png")

FONT_BOLD   = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_MONO   = "/System/Library/Fonts/Monaco.ttf"

BG          = (13, 17, 23)       # GitHub dark background
ACCENT      = (88, 166, 255)     # GitHub blue
TEXT_WHITE  = (230, 237, 243)
TEXT_MUTED  = (110, 118, 129)
PILL_BG     = (22, 27, 34)
PILL_BORDER = (48, 54, 61)

img  = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

# — subtle grid pattern —
for x in range(0, W, 60):
    draw.line([(x, 0), (x, H)], fill=(255, 255, 255, 8), width=1)
for y in range(0, H, 60):
    draw.line([(0, y), (W, y)], fill=(255, 255, 255, 8), width=1)

# — accent bar top —
draw.rectangle([(0, 0), (W, 4)], fill=ACCENT)

# — title —
font_title = ImageFont.truetype(FONT_BOLD, 96)
title = "BehaveX"
bbox = draw.textbbox((0, 0), title, font=font_title)
tw = bbox[2] - bbox[0]
draw.text(((W - tw) // 2, 120), title, font=font_title, fill=TEXT_WHITE)

# — tagline —
font_tag = ImageFont.truetype(FONT_REGULAR, 34)
tagline = "Production-grade test orchestration for Python BDD"
bbox = draw.textbbox((0, 0), tagline, font=font_tag)
tw = bbox[2] - bbox[0]
draw.text(((W - tw) // 2, 240), tagline, font=font_tag, fill=TEXT_MUTED)

# — divider —
draw.line([(W // 2 - 160, 308), (W // 2 + 160, 308)], fill=PILL_BORDER, width=1)

# — stat —
font_stat_num = ImageFont.truetype(FONT_BOLD, 48)
font_stat_lbl = ImageFont.truetype(FONT_REGULAR, 22)
stat_num = "121,000+"
stat_lbl = "monthly downloads"
bbox = draw.textbbox((0, 0), stat_num, font=font_stat_num)
tw = bbox[2] - bbox[0]
draw.text(((W - tw) // 2, 326), stat_num, font=font_stat_num, fill=ACCENT)
bbox = draw.textbbox((0, 0), stat_lbl, font=font_stat_lbl)
tw = bbox[2] - bbox[0]
draw.text(((W - tw) // 2, 386), stat_lbl, font=font_stat_lbl, fill=TEXT_MUTED)

# — feature pills —
font_pill = ImageFont.truetype(FONT_REGULAR, 22)
pills = ["Parallel Execution", "HTML · JSON · JUnit · Allure", "Auto-Retry  ·  @MUTE  ·  Ordering", "CI/CD Ready"]
pill_h = 42
pad_x = 24
gap = 20

total_w = sum(
    draw.textbbox((0, 0), p, font=font_pill)[2] - draw.textbbox((0, 0), p, font=font_pill)[0] + pad_x * 2
    for p in pills
) + gap * (len(pills) - 1)

x = (W - total_w) // 2
y = 466

for pill in pills:
    bbox = draw.textbbox((0, 0), pill, font=font_pill)
    pw = bbox[2] - bbox[0] + pad_x * 2
    r = pill_h // 2
    draw.rounded_rectangle([x, y, x + pw, y + pill_h], radius=r, fill=PILL_BG, outline=PILL_BORDER)
    draw.text((x + pad_x, y + (pill_h - (bbox[3] - bbox[1])) // 2), pill, font=font_pill, fill=TEXT_WHITE)
    x += pw + gap

# — PyPI badge line —
font_badge = ImageFont.truetype(FONT_REGULAR, 20)
badge_text = "pip install behavex"
font_badge_mono = ImageFont.truetype(FONT_MONO, 20)
bbox = draw.textbbox((0, 0), badge_text, font=font_badge_mono)
bw = bbox[2] - bbox[0] + 32
bh = 36
bx = (W - bw) // 2
by = 560
draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=6, fill=(22, 27, 34), outline=PILL_BORDER)
draw.text((bx + 16, by + (bh - (bbox[3] - bbox[1])) // 2), badge_text, font=font_badge_mono, fill=ACCENT)

# — accent bar bottom —
draw.rectangle([(0, H - 4), (W, H)], fill=ACCENT)

img.save(OUT, "PNG", optimize=True)
print(f"Saved: {os.path.abspath(OUT)}")
