#!/usr/bin/env python3
"""
Build a print-ready paperback cover for "The First Key"
KDP specs: 5.5" x 8.5" trim, 0.540" spine, 216 pages, cream paper, B&W interior
Output: 3537 x 2625 px at 300 DPI
"""

from PIL import Image, ImageDraw, ImageFont
import os

# === PATHS ===
COVERS_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(COVERS_DIR, "assets")
FRONT_BG = os.path.join(ASSETS_DIR, "front-cover-bg.png")
AUTHOR_PHOTO = os.path.join(ASSETS_DIR, "randyonblack.png")
OUTPUT = os.path.join(COVERS_DIR, "first-key-cover.png")

# === DIMENSIONS ===
# 216 pages, cream paper, 5.5x8.5 trim
# Spine: 216 * 0.0025 = 0.540" = 162px
# Total: 0.125 + 5.5 + 0.540 + 5.5 + 0.125 = 11.790" x 8.75"
W, H = 3537, 2625
SPINE_START = 1687
SPINE_END = 1849
SPINE_W = 162
MARGIN = 150
BLEED = 37
DPI = 300

# === COLORS ===
BURNT_ORANGE = (210, 140, 50)
GOLD = (200, 168, 78)
CREAM = (212, 197, 160)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# === FONTS ===
FD = "/System/Library/Fonts/Supplemental"
F_BOLD = f"{FD}/Georgia Bold.ttf"
F_REG = f"{FD}/Georgia.ttf"
F_ITAL = f"{FD}/Georgia Italic.ttf"

def ft(p, s): return ImageFont.truetype(p, s)
def ts(d, t, f):
    b = d.textbbox((0, 0), t, font=f)
    return b[2] - b[0], b[3] - b[1]
def ctr(d, t, f, c, cx, y):
    w, h = ts(d, t, f)
    d.text((cx - w // 2, y), t, font=f, fill=c)
    return h
def ctr_shadow(d, t, f, c, cx, y):
    """Draw centered text with black shadow for readability over images."""
    w, h = ts(d, t, f)
    x = cx - w // 2
    # Shadow
    for dx in range(-4, 5):
        for dy in range(-4, 5):
            d.text((x + dx, y + dy), t, font=f, fill=BLACK)
    # Outline
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            if dx * dx + dy * dy <= 9:
                d.text((x + dx, y + dy), t, font=f, fill=BLACK)
    d.text((x, y), t, font=f, fill=c)
    return h


def wrap(d, text, f, color, x, y, mw, sp,
         zone_x=None, zone_y=None, zone_h=None):
    """Word-wrap with optional barcode zone avoidance."""
    words = text.split()
    i = 0
    _, sh = ts(d, "Ag", f)
    while i < len(words):
        aw = mw
        if zone_x and zone_y and zone_h:
            if y < zone_y + zone_h and y + sh > zone_y:
                narrowed = zone_x - x - 30
                if narrowed > 200:
                    aw = min(aw, narrowed)
        ln = ""
        while i < len(words):
            t = f"{ln} {words[i]}".strip()
            if ts(d, t, f)[0] <= aw:
                ln = t
                i += 1
            else:
                break
        if not ln and i < len(words):
            ln = words[i]; i += 1
        d.text((x, y), ln, font=f, fill=color)
        y += sh + sp
    return y


def add_text_gradient(img, start_y, height, opacity=220, from_top=True):
    """Add a dark gradient overlay for text readability."""
    from PIL import ImageFilter
    overlay = Image.new("RGBA", (img.width, img.height), (0, 0, 0, 0))
    for i in range(height):
        if from_top:
            y = start_y + i
            alpha = int(opacity * (1 - i / height) ** 1.5)
        else:
            y = start_y + height - 1 - i
            alpha = int(opacity * (1 - i / height) ** 1.5)
        if 0 <= y < img.height:
            for x in range(img.width):
                overlay.putpixel((x, y), (0, 0, 0, alpha))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)
    return img.convert("RGB")


def build():
    cvr = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(cvr)

    # ============== FRONT COVER ==============
    # Paste the DALL-E background onto front panel
    front_bg = Image.open(FRONT_BG).convert("RGB")
    front_w = W - SPINE_END
    front_h = H
    front_bg = front_bg.resize((front_w, front_h), Image.LANCZOS)

    # Add dark gradients for text zones
    front_bg = add_text_gradient(front_bg, 0, int(front_h * 0.55), opacity=220, from_top=True)
    front_bg = add_text_gradient(front_bg, int(front_h * 0.60), int(front_h * 0.40), opacity=240, from_top=False)

    cvr.paste(front_bg, (SPINE_END, 0))
    d = ImageDraw.Draw(cvr)

    fcx = SPINE_END + front_w // 2  # front cover center x
    fc_margin = front_w // 10
    usable_w = front_w - 2 * fc_margin

    # Title sizing — match ebook cover layout
    title_lines = ["THE", "FIRST", "KEY"]
    title_scale = 1.2

    longest = max(title_lines, key=len)
    base_size = 250
    while ts(d, longest, ft(F_BOLD, base_size))[0] > usable_w and base_size > 40:
        base_size -= 2
    base_size = int(base_size * title_scale)

    line_info = []
    for line in title_lines:
        size = int(base_size * 0.55) if len(line) <= 3 else base_size
        font = ft(F_BOLD, size)
        _, h = ts(d, line, font)
        line_info.append((line, font, size, h))

    gap_the_first = front_w // 30
    gap_first_key = gap_the_first * 2
    total_title_h = sum(li[3] for li in line_info) + gap_the_first + gap_first_key

    # Position title — upper area, moved up 1.5 inches from centered
    original_title_y = (H - total_title_h) // 3
    title_y_start = original_title_y - int(1.5 * DPI)

    y = title_y_start
    gaps = [gap_the_first, gap_first_key]
    for i, (line, font, size, h) in enumerate(line_info):
        ctr_shadow(d, line, font, BURNT_ORANGE, fcx, y)
        gap = gaps[i] if i < len(gaps) else 0
        y += h + gap

    # Author name at bottom
    author_size = max(56, int(base_size * 0.45))
    author_font = ft(F_BOLD, author_size)
    author_text = "RANDY PELLEGRINI"
    _, ah = ts(d, author_text, author_font)
    quarter_inch = int(0.25 * DPI)
    author_y = H - fc_margin - ah - fc_margin + quarter_inch
    ctr_shadow(d, author_text, author_font, BURNT_ORANGE, fcx, author_y)
    author_bottom = author_y + ah

    # Subtitle — moved down 1.5 inches, white
    sub_size = max(44, int(base_size * 0.35))
    sub_font = ft(F_ITAL, sub_size)
    sub_lines = ["Book Three of", "The Architecture of Survival"]
    original_sub_y = (H - total_title_h) // 3 + total_title_h + fc_margin
    subtitle_y = original_sub_y + int(1.5 * DPI) + quarter_inch

    for sl in sub_lines:
        h = ctr_shadow(d, sl, sub_font, WHITE, fcx, subtitle_y)
        subtitle_y += h + 8

    # ============== SPINE ==============
    scx = SPINE_START + SPINE_W // 2
    max_spine_text_w = SPINE_W - 40

    spine_avail_h = H - 2 * MARGIN - 160
    max_text_len = spine_avail_h // 2 - 40

    spine_items = [
        ("THE FIRST KEY", F_BOLD, True),
        ("RANDY PELLEGRINI", F_REG, False),
    ]
    common_fs = 200
    for txt, fp, _ in spine_items:
        fs = common_fs
        sf = ft(fp, fs)
        tw, th = ts(d, txt, sf)
        while (th > max_spine_text_w or tw > max_text_len) and fs > 12:
            fs -= 2
            sf = ft(fp, fs)
            tw, th = ts(d, txt, sf)
        common_fs = min(common_fs, fs)
    common_fs = int(common_fs * 0.8)
    print(f"Spine common font size: {common_fs}px")

    for txt, fp, top in spine_items:
        sf = ft(fp, common_fs)
        tw, th = ts(d, txt, sf)
        pad = 30
        si = Image.new("RGBA", (tw + 2 * pad, th + 2 * pad), (0, 0, 0, 0))
        ImageDraw.Draw(si).text((pad, pad), txt, font=sf, fill=BURNT_ORANGE)
        r = si.rotate(-90, expand=True)
        bbox = r.getbbox()
        content_cx = (bbox[0] + bbox[2]) // 2
        rx = scx - content_cx
        if top:
            ry = MARGIN + 80
        else:
            ry = H - MARGIN - 80 - r.height
        cvr.paste(r, (rx, ry), r)
        print(f"Spine '{txt}': font={common_fs}px, text_w={tw}px, text_h={th}px")

    # ============== BACK COVER ==============
    bl = MARGIN
    br = SPINE_START - MARGIN
    bw = br - bl

    # Barcode zone (bottom-right of back cover)
    bcw, bch = 600, 360
    bcx = br - bcw
    bcy = H - MARGIN - bch

    # --- Author Photo (upper-left) ---
    photo = Image.open(AUTHOR_PHOTO).convert("RGBA")
    photo_w = bw // 2 - 20
    photo_h = int(photo.height * (photo_w / photo.width))
    photo = photo.resize((photo_w, photo_h), Image.LANCZOS)
    photo_py = MARGIN + 30
    cvr.paste(photo, (bl, photo_py), photo)

    d = ImageDraw.Draw(cvr)  # refresh after paste

    # --- Author Bio (right of photo) ---
    f_bio = ft(F_REG, 46)
    bio_sp = 10
    bio_text = (
        "Randy Pellegrini writes thrillers that explore the patterns "
        "hiding in plain sight throughout human history. When he\u2019s not "
        "writing about conspiracies or genetic memory, he\u2019s traveling "
        "the world to research locations first-hand, wondering why "
        "civilizations keep making the same mistakes."
    )
    py = MARGIN + 130
    bio_left = bl + photo_w + 40 + 38
    bio_width = br - bio_left - 13
    bio_y = wrap(d, bio_text, f_bio, CREAM, bio_left, py, bio_width, bio_sp)

    # Gold divider
    div_y = bio_y + 80
    d.line([(bl, div_y), (br, div_y)], fill=GOLD, width=2)
    cy = div_y + 85

    # --- Blurb ---
    f_blurb = ft(F_REG, 44)
    blurb_sp = 14

    blurb1 = (
        "What if humanity\u2019s greatest secret was hidden in plain sight "
        "for three thousand years?"
    )
    blurb2 = (
        "Egyptian physician Nefertari discovers a pattern in plague and "
        "death \u2014 something that splits mankind into two warring factions. "
        "She forges seven bronze keys to protect this knowledge, but her "
        "choice dooms everyone she loves."
    )
    blurb3 = (
        "Nine centuries of shadow war follow. Real battles. Real blood. "
        "Real history shaped by a conspiracy spanning Alexander\u2019s "
        "conquests to Egypt\u2019s fall."
    )
    blurb4 = (
        "One faction fights to prevent humanity\u2019s collapse. The other "
        "seeks to control it."
    )
    blurb5 = (
        "But as the bronze keys surface and ancient enemies close in, "
        "Nefertari faces an impossible truth: the greatest threat isn\u2019t "
        "what she discovered."
    )
    blurb6 = "It\u2019s what she became to protect it."
    blurb7 = (
        "Some choices echo through eternity. Some wars are written in "
        "our blood."
    )

    for blurb in [blurb1, blurb2, blurb3, blurb4, blurb5, blurb6, blurb7]:
        cy = wrap(d, blurb, f_blurb, CREAM, bl, cy, bw, blurb_sp,
                  zone_x=bcx, zone_y=bcy, zone_h=bch)
        cy += 26

    # Bottom gold divider
    div2_y = cy + 40
    d.line([(bl, div2_y), (br, div2_y)], fill=GOLD, width=2)

    # --- Series tagline + website below bottom divider, left of barcode ---
    small_text = (
        "The First Key is the third book in The Architecture of Survival, "
        "a thriller series spanning 3,289 years of real history. "
        "Start with The Aethelred Cipher. "
        "Read more at randypellegrini.com"
    )
    small_x = bl
    small_w = bcx - bl - 46
    # Auto-size to fit between bottom divider and bottom margin
    small_avail_h = (H - MARGIN) - (div2_y + 30)
    small_fs = 38
    test_img = Image.new("RGB", (W, H), BLACK)
    test_d = ImageDraw.Draw(test_img)
    while small_fs > 12:
        f_small = ft(F_ITAL, small_fs)
        test_y = wrap(test_d, small_text, f_small, CREAM, 0, 0, small_w, 6)
        if test_y <= small_avail_h:
            break
        small_fs -= 2
    f_small = ft(F_ITAL, small_fs)
    # Measure text height, then bottom-align with front cover author name bottom
    test_img2 = Image.new("RGB", (W, H), BLACK)
    test_d2 = ImageDraw.Draw(test_img2)
    text_block_h = wrap(test_d2, small_text, f_small, CREAM, 0, 0, small_w, 6)
    small_y = author_bottom - text_block_h
    wrap(d, small_text, f_small, CREAM, small_x, small_y, small_w, 6)
    print(f"ISBN side text: font={small_fs}px, avail_h={small_avail_h}px")

    safe = H - MARGIN
    status = "OK" if cy <= safe else "WARNING: OVERFLOW"
    print(f"Back text ends y={cy}/{safe} -- {status} ({safe - cy}px remaining)")

    # === SAVE ===
    cvr.save(OUTPUT, "PNG", dpi=(300, 300))
    print(f"Saved: {OUTPUT} ({W}x{H})")

    pdf_output = os.path.join(COVERS_DIR, "first-key-cover.pdf")
    cvr_rgb = cvr.convert("RGB")
    cvr_rgb.save(pdf_output, "PDF", resolution=300)
    print(f"PDF saved: {pdf_output}")


if __name__ == "__main__":
    build()
