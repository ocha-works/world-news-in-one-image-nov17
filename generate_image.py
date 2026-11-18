#!/usr/bin/env python3
"""Draw entry.png: the world news of Tuesday 17 November 2026 in one image.

A newspaper-front-page style infographic, drawn with Pillow so every word is
crisp (no generated-text garbling). Canvas is 1024x1024, the competition cap.
Run:  python3 generate_image.py   ->  writes entry.png beside this file.
The stories and their sources are listed in SOURCES.md.
"""

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
BG = (247, 242, 231)        # newsprint cream
INK = (22, 22, 26)          # near-black
RED = (178, 34, 44)         # headline red
PAPER_LINE = (203, 194, 172)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_B = f"{FONT_DIR}/liberation/LiberationSerif-Bold.ttf"
SANS_B = f"{FONT_DIR}/dejavu/DejaVuSans-Bold.ttf"
SANS = f"{FONT_DIR}/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap to max_w pixels; returns list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- icons
# Each icon draws inside a 92x92 box at (x, y) in its accent colour.

def icon_bridge(d, x, y, c):
    # Crimea Bridge: deck, two towers, suspension arcs, water below.
    d.line([x + 4, y + 58, x + 88, y + 58], fill=c, width=6)
    d.line([x + 22, y + 30, x + 22, y + 58], fill=c, width=5)
    d.line([x + 70, y + 30, x + 70, y + 58], fill=c, width=5)
    d.arc([x + 8, y + 18, x + 50, y + 58], start=180, end=360, fill=c, width=4)
    d.arc([x + 44, y + 18, x + 86, y + 58], start=180, end=360, fill=c, width=4)
    for wx in (8, 34, 60):
        d.arc([x + wx, y + 66, x + wx + 18, y + 82], start=0, end=180, fill=c, width=3)


def icon_ship_flame(d, x, y, c):
    # Tanker: long hull, deckhouse and bow, with a flame over the stern.
    d.polygon([(x + 2, y + 64), (x + 90, y + 64), (x + 80, y + 82), (x + 12, y + 82)], fill=c)
    d.rectangle([x + 14, y + 52, x + 52, y + 64], fill=c)          # deck tanks
    d.rectangle([x + 58, y + 44, x + 74, y + 64], fill=c)          # bridge tower
    fx, fy = x + 30, y + 6  # flame: layered teardrops above the tanks
    d.polygon([(fx, fy), (fx + 11, fy + 22), (fx + 4, fy + 34), (fx - 8, fy + 34), (fx - 11, fy + 22)], fill=(232, 119, 34))
    d.polygon([(fx, fy + 14), (fx + 6, fy + 26), (fx, fy + 34), (fx - 6, fy + 26)], fill=(245, 197, 66))


def icon_chart_down(d, x, y, c):
    # Falling market line with axes (world markets slide).
    d.line([x + 10, y + 10, x + 10, y + 78], fill=INK, width=4)
    d.line([x + 10, y + 78, x + 86, y + 78], fill=INK, width=4)
    pts = [(x + 16, y + 22), (x + 34, y + 34), (x + 48, y + 30), (x + 64, y + 52), (x + 80, y + 66)]
    d.line(pts, fill=RED, width=6, joint="curve")
    d.polygon([(x + 80, y + 66), (x + 66, y + 64), (x + 78, y + 52)], fill=RED)


def icon_globe(d, x, y, c):
    # Globe with meridians (Asia summits diplomacy).
    d.ellipse([x + 10, y + 10, x + 82, y + 82], outline=c, width=5)
    d.ellipse([x + 32, y + 10, x + 60, y + 82], outline=c, width=3)
    d.line([x + 10, y + 46, x + 82, y + 46], fill=c, width=3)
    d.arc([x + 10, y + 24, x + 82, y + 68], start=0, end=180, fill=c, width=3)
    d.arc([x + 10, y + 24, x + 82, y + 68], start=180, end=360, fill=c, width=3)


def icon_leaf(d, x, y, c):
    # Leaf with a vein (COP31 fossil-fuel exit draft).
    d.polygon([(x + 18, y + 74), (x + 30, y + 34), (x + 52, y + 16), (x + 78, y + 14),
               (x + 76, y + 40), (x + 60, y + 64), (x + 36, y + 76)], fill=c)
    d.line([x + 22, y + 72, x + 70, y + 22], fill=BG, width=4)
    d.line([x + 20, y + 76, x + 12, y + 86], fill=c, width=5)


def icon_aid(d, x, y, c):
    # Aid crate with a bold cross (Gaza crossings plea).
    d.rectangle([x + 12, y + 22, x + 80, y + 80], outline=c, width=6)
    d.rectangle([x + 38, y + 34, x + 54, y + 68], fill=RED)
    d.rectangle([x + 29, y + 43, x + 63, y + 59], fill=RED)
    d.line([x + 12, y + 22, x + 46, y + 6], fill=c, width=5)
    d.line([x + 80, y + 22, x + 46, y + 6], fill=c, width=5)


# ---------------------------------------------------------------- stories
STORIES = [
    ("UKRAINE", "DRONES HIT CRIMEA BRIDGE",
     "Ukraine fires a 1,300-drone barrage. Russia strikes Kyiv's bridges, cutting power and water.",
     icon_bridge, (38, 92, 160)),
    ("MIDDLE EAST", "TANKER ATTACKED IN HORMUZ",
     "Tanker ablaze, crew evacuated. Iran drones target a US radar in Bahrain; US jets hit Qeshm Island.",
     icon_ship_flame, (196, 90, 20)),
    ("MARKETS", "OIL, GOLD & STOCKS FALL",
     "World markets slide together. Nasdaq drops 2.5% into correction; Brent oil falls 3.6%.",
     icon_chart_down, RED),
    ("ASIA", "TRUMP IN MANILA FOR ASEAN",
     "US-ASEAN summit as APEC gathers in Shenzhen. Trump, Xi and Putin to meet on Thursday.",
     icon_globe, (20, 120, 110)),
    ("CLIMATE · COP31", "DRAFT DEAL: EXIT FOSSIL FUELS",
     "Climate talks call for \u201caccelerated action\u201d to move the world away from fossil fuels.",
     icon_leaf, (34, 139, 64)),
    ("GAZA", "ALLIES URGE: OPEN AID ROUTES",
     "Britain, Canada, Australia and Italy press Israel to open crossings as the aid crisis deepens.",
     icon_aid, (140, 40, 90)),
]

TICKER = ("ALSO TODAY:  US air-travel meltdown strands over a million passengers  \u2022  "
          "Houthis advance on Yemen's southern coast  \u2022  Thailand building fire kills 11  \u2022  "
          "US tightens AI chip export rules aimed at China")


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # ---- masthead ------------------------------------------------------
    d.rectangle([0, 0, W, 168], fill=INK)
    d.text((W // 2, 26), "WORLD NEWS \u00b7 IN ONE IMAGE", font=font(SANS_B, 30),
           fill=(245, 197, 66), anchor="ma")
    d.text((W // 2, 66), "TUESDAY 17 NOVEMBER 2026", font=font(SERIF_B, 62),
           fill=(255, 255, 255), anchor="ma")
    d.rectangle([0, 168, W, 176], fill=RED)

    # ---- story panels: 2 columns x 3 rows ------------------------------
    top, panel_h, margin, gap = 192, 218, 28, 16
    col_w = (W - 2 * margin - gap) // 2
    for i, (kicker, head, body, icon, accent) in enumerate(STORIES):
        cx = margin + (i % 2) * (col_w + gap)
        cy = top + (i // 2) * (panel_h + gap)
        d.rectangle([cx, cy, cx + col_w, cy + panel_h], fill=(255, 253, 247),
                    outline=PAPER_LINE, width=2)
        d.rectangle([cx, cy, cx + col_w, cy + 8], fill=accent)
        icon(d, cx + 22, cy + 30, accent)
        tx = cx + 128
        d.text((tx, cy + 26), kicker, font=font(SANS_B, 21), fill=accent)
        y = cy + 54
        for line in wrap(d, head, font(SANS_B, 27), cx + col_w - tx - 14):
            d.text((tx, y), line, font=font(SANS_B, 27), fill=INK)
            y += 33
        # body spans the full panel width under the icon row
        by = cy + 128
        for line in wrap(d, body, font(SANS, 22), col_w - 36):
            d.text((cx + 18, by), line, font=font(SANS, 22), fill=(52, 52, 58))
            by += 29

    # ---- ticker ---------------------------------------------------------
    tick_top = top + 3 * (panel_h + gap) + 2
    d.rectangle([0, tick_top, W, H], fill=INK)
    ty = tick_top + 16
    for line in wrap(d, TICKER, font(SANS_B, 23), W - 56):
        d.text((28, ty), line, font=font(SANS_B, 23), fill=(255, 255, 255))
        ty += 32

    img.save("entry.png", optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
