#!/usr/bin/env python3
"""The Passport Page of a Country That Isn't There.

Writes /output/entry.png (1024x1024): an open passport spread of the
fictional Republic of Kestrelia. Left page: the data page with a portrait,
holder details and a machine-readable zone (ICAO 9303 check digits computed
for real). Right page: the visa/stamp page with a consistent travel history
(every stamp after the passport's issue date) and one telling piece of
paperwork: the Northern Marches permit condition.

Deterministic, procedural, no network, stdlib + Pillow only.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1024, 1024
OUT = os.environ.get("ENTRY_OUTPUT_PATH", "/output/entry.png")

NAVY = (27, 42, 74)
NAVY_D = (18, 30, 56)
GOLD = (176, 141, 62)
GOLD_L = (203, 172, 96)
CREAM = (244, 239, 228)
PAPER = (248, 244, 235)
INK = (32, 38, 52)
FAINT = (120, 116, 102)
STAMP_BLUE = (38, 84, 138)
STAMP_RED = (158, 52, 48)
STAMP_PURPLE = (104, 68, 128)
SKIN = (216, 178, 143)
SKIN_D = (198, 158, 122)
HAIR = (74, 52, 38)

F = "/usr/share/fonts/truetype/dejavu/"
FL = "/usr/share/fonts/truetype/liberation/"


def font(name, size):
    try:
        return ImageFont.truetype(F + name, size)
    except OSError:
        return ImageFont.truetype(FL + name, size)


SERIF = "DejaVuSerif.ttf"
SERIF_B = "DejaVuSerif-Bold.ttf"
SERIF_I = "LiberationSerif-Italic.ttf"  # DejaVu has no italic serif here
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"
MONO = "DejaVuSansMono.ttf"
MONO_B = "DejaVuSansMono-Bold.ttf"


def text_c(d, cx, y, s, f, fill, tracking=0):
    """Centered text, optionally letter-tracked."""
    if tracking:
        w = sum(d.textlength(ch, font=f) for ch in s) + tracking * (len(s) - 1)
        x = cx - w / 2
        for ch in s:
            d.text((x, y), ch, font=f, fill=fill)
            x += d.textlength(ch, font=f) + tracking
    else:
        d.text((cx, y), s, font=f, fill=fill, anchor="ma")


def mrz_check(s):
    vals = {c: i for i, c in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
    total = 0
    for i, ch in enumerate(s):
        v = 0 if ch == "<" else vals[ch]
        total += v * (7, 3, 1)[i % 3]
    return str(total % 10)


def mrz_lines():
    name = "VOSS<<ELARA<MIREN"
    line1 = ("P<KST" + name).ljust(44, "<")
    doc = "KST417283"
    nat = "KST"
    dob = "910612"
    sex = "F"
    exp = "340314"
    pers = "AURELINE<<<<<<"
    l2 = (doc + mrz_check(doc) + nat + dob + mrz_check(dob) + sex + exp
          + mrz_check(exp) + pers + mrz_check(pers))
    l2 += mrz_check(l2)
    return line1, l2


def guilloche(d, box, color, step=7, amp=3.0, waves=2):
    """Fine wavy security lines across a rectangle."""
    x0, y0, x1, y1 = box
    for y in range(y0, y1, step):
        pts = []
        for x in range(x0, x1 + 1, 4):
            yy = y + amp * math.sin((x - x0) / 26.0 * math.pi * waves / 4.0)
            pts.append((x, yy))
        d.line(pts, fill=color, width=1)


def stamp_layer(size, draw_fn, angle):
    """Draw a stamp on its own layer, rotate it, return the layer."""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(layer)
    draw_fn(dd)
    return layer.rotate(angle, resample=Image.BICUBIC, expand=False)


def coat_of_arms(d, cx, cy, r):
    """Kestrelia arms: navy roundel, gold shield, kestrel silhouette, star."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=NAVY, outline=GOLD, width=3)
    d.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6],
              outline=GOLD_L, width=1)
    # shield
    s = r * 0.62
    shield = [(cx - s, cy - s * 0.75), (cx + s, cy - s * 0.75),
              (cx + s, cy + s * 0.15), (cx, cy + s * 0.85),
              (cx - s, cy + s * 0.15)]
    d.polygon(shield, fill=GOLD, outline=(232, 205, 140), width=2)
    # kestrel: stylised bird in flight (navy silhouette)
    bx, by = cx, cy - s * 0.18
    d.polygon([(bx - s * 0.55, by), (bx - s * 0.15, by - s * 0.28),
               (bx + s * 0.05, by - s * 0.05), (bx + s * 0.55, by - s * 0.34),
               (bx + s * 0.35, by + s * 0.02), (bx + s * 0.5, by + s * 0.3),
               (bx + s * 0.05, by + s * 0.14), (bx - s * 0.2, by + s * 0.3),
               (bx - s * 0.45, by + s * 0.05)], fill=NAVY)
    # star above bird
    sx, sy, sr = cx, cy - s * 0.52, s * 0.16
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = sr if i % 2 == 0 else sr * 0.45
        pts.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
    d.polygon(pts, fill=NAVY)
    # motto ribbon
    d.rectangle([cx - r * 0.98, cy + r * 0.78, cx + r * 0.98, cy + r * 0.98],
                fill=NAVY, outline=GOLD, width=1)
    text_c(d, cx, cy + r * 0.81, "PER MARE · PER ASTRA", font(SANS_B, 7),
           GOLD_L, tracking=0)


def portrait(d, box):
    """Stylised engraved-style passport portrait of the holder."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    # backdrop: pale blue-grey
    d.rectangle(box, fill=(214, 222, 228), outline=NAVY, width=2)
    cx = (x0 + x1) // 2
    # shoulders / jacket
    d.polygon([(cx - w * 0.42, y1), (cx - w * 0.30, y0 + h * 0.72),
               (cx - w * 0.10, y0 + h * 0.66), (cx + w * 0.10, y0 + h * 0.66),
               (cx + w * 0.30, y0 + h * 0.72), (cx + w * 0.42, y1)],
              fill=(52, 62, 84))
    # white shirt + collar
    d.polygon([(cx - w * 0.10, y0 + h * 0.66), (cx, y0 + h * 0.78),
               (cx + w * 0.10, y0 + h * 0.66), (cx + w * 0.07, y0 + h * 0.62),
               (cx, y0 + h * 0.68), (cx - w * 0.07, y0 + h * 0.62)],
              fill=(240, 238, 230))
    # neck
    d.rectangle([cx - w * 0.07, y0 + h * 0.55, cx + w * 0.07, y0 + h * 0.68],
                fill=SKIN_D)
    # head
    d.ellipse([cx - w * 0.155, y0 + h * 0.10, cx + w * 0.155, y0 + h * 0.58],
              fill=SKIN)
    # hair: swept back with a low bun at the back of the head
    d.pieslice([cx - w * 0.165, y0 + h * 0.06, cx + w * 0.165, y0 + h * 0.42],
               start=180, end=360, fill=HAIR)
    d.ellipse([cx + w * 0.10, y0 + h * 0.05, cx + w * 0.20, y0 + h * 0.17],
              fill=HAIR)
    # brows, eyes, nose, mouth — light engraved lines
    for ex in (-1, 1):
        exx = cx + ex * w * 0.062
        d.line([(exx - w * 0.035, y0 + h * 0.335), (exx + w * 0.035, y0 + h * 0.33)],
               fill=(90, 60, 45), width=2)
        d.ellipse([exx - w * 0.011, y0 + h * 0.358, exx + w * 0.011, y0 + h * 0.374],
                  fill=(52, 38, 30))
    d.line([(cx, y0 + h * 0.37), (cx - 2, y0 + h * 0.45)], fill=SKIN_D, width=2)
    d.line([(cx - w * 0.03, y0 + h * 0.50), (cx + w * 0.03, y0 + h * 0.50)],
           fill=(150, 90, 75), width=2)
    # soft shading on one side of the face
    d.arc([cx - w * 0.155, y0 + h * 0.10, cx + w * 0.155, y0 + h * 0.58],
          start=300, end=90, fill=(190, 150, 115), width=3)
    # ghost image: faint repeat bottom-right (passport security feature)
    d.text((x1 - 36, y1 - 24), "KST", font=font(SANS_B, 9), fill=(150, 160, 170))


def field(d, x, y, label, value, vfont=None, label_w=118):
    d.text((x, y), label, font=font(SANS, 11), fill=FAINT)
    d.text((x + label_w, y - 1), value,
           font=vfont or font(SANS_B, 14), fill=INK)


def data_page(img, d, x0, y0, x1, y1):
    """Left page: the data page."""
    d.rectangle([x0, y0, x1, y1], fill=PAPER)
    guilloche(d, (x0 + 8, y0 + 8, x1 - 8, y1 - 8), (228, 222, 205), step=9)
    # header band
    d.rectangle([x0, y0, x1, y0 + 118], fill=NAVY)
    d.rectangle([x0, y0 + 118, x1, y0 + 122], fill=GOLD)
    text_c(d, (x0 + x1) // 2, y0 + 14, "REPUBLIC OF KESTRELIA",
           font(SERIF_B, 24), (238, 230, 205), tracking=2)
    text_c(d, (x0 + x1) // 2, y0 + 48, "P A S S P O R T",
           font(SERIF, 20), GOLD_L, tracking=3)
    text_c(d, (x0 + x1) // 2, y0 + 80, "PASSEPORT  ·  ORDINARY  ·  No. KST417283",
           font(SANS, 12), (190, 195, 210), tracking=1)
    # coat of arms, centred in the open space below the personal rows
    coat_of_arms(d, (x0 + x1) // 2, y0 + 668, 64)
    text_c(d, (x0 + x1) // 2, y0 + 748, "SEAL OF THE REPUBLIC",
           font(SANS_B, 10), NAVY, tracking=2)
    # portrait
    portrait(d, (x0 + 28, y0 + 158, x0 + 28 + 168, y0 + 158 + 210))
    d.text((x0 + 28, y0 + 374), "PHOTOGRAPH", font=font(SANS, 9), fill=FAINT)
    d.text((x0 + 28, y0 + 388), "HOLDER'S SIGNATURE", font=font(SANS, 9), fill=FAINT)
    d.text((x0 + 28, y0 + 406), "Elara Voss", font=font(SERIF_I, 20), fill=(48, 52, 96))
    d.line([(x0 + 28, y0 + 432), (x0 + 196, y0 + 432)], fill=INK, width=1)
    # data fields, right column
    fx = x0 + 218
    fy = y0 + 158
    field(d, fx, fy, "SURNAME", "VOSS")
    field(d, fx, fy + 34, "GIVEN NAMES", "ELARA MIREN")
    field(d, fx, fy + 68, "NATIONALITY", "KESTRELIAN")
    field(d, fx, fy + 102, "DATE OF BIRTH", "12 JUN 1991")
    field(d, fx, fy + 136, "PLACE OF BIRTH", "PORT AURELINE")
    field(d, fx, fy + 170, "SEX", "F")
    field(d, fx, fy + 204, "DATE OF ISSUE", "14 MAR 2024")
    field(d, fx, fy + 238, "DATE OF EXPIRY", "14 MAR 2034")
    field(d, fx, fy + 272, "AUTHORITY", "MINISTRY OF INTERIOR",
          vfont=font(SANS_B, 11))
    d.text((fx + 118, fy + 292), "PORT AURELINE", font=font(SANS_B, 12), fill=INK)
    # personal number + height/eyes row
    d.line([(x0 + 28, y0 + 470), (x1 - 28, y0 + 470)], fill=(200, 192, 170), width=1)
    d.text((x0 + 28, y0 + 482), "PERSONAL No.  AUR-1991-0612-7", font=font(SANS, 11), fill=INK)
    d.text((x0 + 28, y0 + 502), "HEIGHT  168 cm      EYES  BROWN      HAIR  BROWN", font=font(SANS, 11), fill=INK)
    d.text((x0 + 28, y0 + 522), "OCCUPATION  CARTOGRAPHER, ROYAL SURVEY OFFICE", font=font(SANS, 11), fill=INK)
    # MRZ
    l1, l2 = mrz_lines()
    d.rectangle([x0 + 14, y1 - 118, x1 - 14, y1 - 14], fill=(232, 227, 212))
    d.text((x0 + 28, y1 - 106), l1, font=font(MONO, 15), fill=INK)
    d.text((x0 + 28, y1 - 80), l2, font=font(MONO, 15), fill=INK)
    d.text((x0 + 28, y1 - 48), "P<KSTVOSS<<ELARA<MIREN — MACHINE READABLE ZONE", font=font(SANS, 8), fill=FAINT)


def stamp_rect(dd, box, color, label, lines, big=13):
    dd.rectangle(box, outline=color, width=3)
    dd.rectangle([box[0] + 4, box[1] + 4, box[2] - 4, box[3] - 4],
                 outline=color, width=1)
    cx = (box[0] + box[2]) // 2
    text_c(dd, cx, box[1] + 8, label, font(SANS_B, big), color, tracking=1)
    y = box[1] + 30
    for ln in lines:
        text_c(dd, cx, y, ln, font(SANS_B, 11), color)
        y += 16


def stamp_oval(dd, box, color, label, lines):
    dd.ellipse(box, outline=color, width=3)
    dd.ellipse([box[0] + 5, box[1] + 5, box[2] - 5, box[3] - 5],
               outline=color, width=1)
    cx = (box[0] + box[2]) // 2
    text_c(dd, cx, box[1] + 14, label, font(SANS_B, 12), color, tracking=1)
    y = box[1] + 34
    for ln in lines:
        text_c(dd, cx, y, ln, font(SANS, 10), color)
        y += 14


def visa_page(img, d, x0, y0, x1, y1):
    """Right page: visas, stamps, endorsements."""
    d.rectangle([x0, y0, x1, y1], fill=PAPER)
    guilloche(d, (x0 + 8, y0 + 8, x1 - 8, y1 - 8), (228, 222, 205), step=9)
    d.rectangle([x0, y0, x1, y0 + 64], fill=NAVY)
    d.rectangle([x0, y0 + 64, x1, y0 + 68], fill=GOLD)
    text_c(d, (x0 + x1) // 2, y0 + 12, "VISAS · STAMPS · ENDORSEMENTS",
           font(SERIF_B, 19), (238, 230, 205), tracking=1)
    text_c(d, (x0 + x1) // 2, y0 + 38, "PAGES 12 — 13",
           font(SANS, 10), (190, 195, 210), tracking=2)

    # --- Sularis visa vignette (top) ---
    vx0, vy0, vx1, vy1 = x0 + 28, y0 + 92, x1 - 28, y0 + 232
    d.rectangle([vx0, vy0, vx1, vy1], fill=(226, 232, 238),
                outline=STAMP_BLUE, width=2)
    d.rectangle([vx0 + 5, vy0 + 5, vx1 - 5, vy1 - 5], outline=STAMP_BLUE, width=1)
    d.text((vx0 + 14, vy0 + 10), "VISA — KINGDOM OF SULARIS", font=font(SANS_B, 13), fill=STAMP_BLUE)
    d.text((vx0 + 14, vy0 + 34), "SINGLE ENTRY  ·  TOURIST  ·  VALID 30 DAYS", font=font(SANS, 11), fill=INK)
    d.text((vx0 + 14, vy0 + 56), "ISSUED  02 SEP 2025  ·  SULARIS CONSULATE, PORT AURELINE", font=font(SANS, 11), fill=INK)
    d.text((vx0 + 14, vy0 + 78), "No. SUL-V-2025-118844   ·   FEE  25 AURELS PAID", font=font(SANS, 11), fill=INK)
    d.text((vx0 + 14, vy0 + 102), "NOT VALID FOR THE ISLE OF GREYTHORNE", font=font(SANS_B, 11), fill=STAMP_RED)

    # --- arrival / departure stamps (drawn on layers, rotated) ---
    def s1(dd):
        stamp_rect(dd, (10, 10, 210, 96), STAMP_BLUE, "★ ARRIVED ★",
                   ["PORT OF DRAVNA", "02 APR 2024", "OFFICER 17"])
    def s2(dd):
        stamp_rect(dd, (10, 10, 210, 96), STAMP_RED, "✈ DEPARTED",
                   ["PORT OF DRAVNA", "19 APR 2024", "OFFICER 09"])
    def s3(dd):
        stamp_oval(dd, (10, 10, 200, 92), STAMP_PURPLE, "ARRIVED",
                   ["KINGDOM OF SULARIS", "07 SEP 2025", "BORDER POST 4"])
    def s4(dd):
        stamp_oval(dd, (10, 10, 200, 92), STAMP_BLUE, "DEPARTED",
                   ["KINGDOM OF SULARIS", "21 SEP 2025", "BORDER POST 4"])
    def s5(dd):
        stamp_rect(dd, (10, 10, 210, 96), STAMP_RED, "★ ARRIVED ★",
                   ["MERIDIAN FREE PORT", "03 NOV 2026", "OFFICER 22"])
    stamps = [(s1, -6, (x0 + 30, y0 + 258)), (s2, 5, (x0 + 258, y0 + 262)),
              (s3, -4, (x0 + 30, y0 + 372)), (s4, 6, (x0 + 258, y0 + 376)),
              (s5, -7, (x0 + 30, y0 + 486))]
    for fn, ang, (px, py) in stamps:
        layer = stamp_layer((230, 120), fn, ang)
        img.paste(layer, (px, py), layer)

    # --- the telling detail: Northern Marches condition ---
    ex0, ey0, ex1, ey1 = x0 + 28, y0 + 612, x1 - 28, y0 + 742
    d.rectangle([ex0, ey0, ex1, ey1], fill=(250, 244, 224),
                outline=STAMP_RED, width=2)
    d.rectangle([ex0 + 5, ey0 + 5, ex1 - 5, ey1 - 5], outline=STAMP_RED, width=1)
    d.text((ex0 + 14, ey0 + 10), "ENDORSEMENT — MINISTRY OF THE INTERIOR", font=font(SANS_B, 12), fill=STAMP_RED)
    d.text((ex0 + 14, ey0 + 34),
           "HOLDER IS NOT PERMITTED TO ENTER THE", font=font(SANS_B, 12), fill=INK)
    d.text((ex0 + 14, ey0 + 54),
           "NORTHERN MARCHES WITHOUT A SEPARATE", font=font(SANS_B, 12), fill=INK)
    d.text((ex0 + 14, ey0 + 74),
           "PERMIT ISSUED BY THE WARDEN OF THE MARCHES.", font=font(SANS_B, 12), fill=INK)
    d.text((ex0 + 14, ey0 + 98),
           "Permit office: Fort Halvar, 3rd floor. Fee: 40 aurels.", font=font(SANS, 11), fill=INK)

    # --- fee / revenue stamp ---
    fx0, fy0, fx1, fy1 = x0 + 28, y0 + 762, x0 + 208, y0 + 852
    d.rectangle([fx0, fy0, fx1, fy1], fill=(238, 232, 205),
                outline=GOLD, width=2)
    text_c(d, (fx0 + fx1) // 2, fy0 + 8, "REVENUE", font(SANS_B, 11), GOLD)
    text_c(d, (fx0 + fx1) // 2, fy0 + 26, "40 AURELS", font(SERIF_B, 16), NAVY)
    text_c(d, (fx0 + fx1) // 2, fy0 + 50, "PAID · 14 MAR 2024", font(SANS, 10), INK)
    text_c(d, (fx0 + fx1) // 2, fy0 + 68, "No. R-0417283", font(MONO, 10), INK)

    # --- small map of Kestrelia ---
    mx0, my0, mx1, my1 = x0 + 228, y0 + 762, x1 - 28, y0 + 852
    d.rectangle([mx0, my0, mx1, my1], fill=(226, 234, 228),
                outline=NAVY, width=1)
    d.text((mx0 + 10, my0 + 6), "KESTRELIA — THE THREE ISLES", font=font(SANS_B, 10), fill=NAVY)
    # three isles, schematic
    d.polygon([(mx0 + 30, my0 + 66), (mx0 + 78, my0 + 40), (mx0 + 118, my0 + 52),
               (mx0 + 96, my0 + 78), (mx0 + 52, my0 + 80)], fill=(150, 180, 150),
              outline=NAVY)
    d.ellipse([mx0 + 150, my0 + 26, mx0 + 168, my0 + 40], fill=(150, 180, 150),
              outline=NAVY)
    d.ellipse([mx0 + 142, my0 + 60, mx0 + 162, my0 + 78], fill=(150, 180, 150),
              outline=NAVY)
    d.ellipse([mx0 + 70, my0 + 58, mx0 + 76, my0 + 64], fill=STAMP_RED)
    d.text((mx0 + 10, my0 + 74), "● PORT AURELINE", font=font(SANS_B, 8), fill=INK)
    d.text((mx1 - 72, my0 + 72), "1 : 2 400 000", font=font(SANS, 8), fill=FAINT)

    # --- footer: travel history line + page numbers ---
    d.line([(x0 + 28, y1 - 96), (x1 - 28, y1 - 96)], fill=(200, 192, 170), width=1)
    d.text((x0 + 28, y1 - 84),
           "TRAVEL HISTORY: DRAVNA (APR 2024) · SULARIS (SEP 2025) ·", font=font(SANS, 10), fill=INK)
    d.text((x0 + 28, y1 - 66),
           "MERIDIAN FREE PORT (NOV 2026). NO REFUSALS RECORDED.", font=font(SANS, 10), fill=INK)
    d.text((x0 + 28, y1 - 44), "THIS PASSPORT REMAINS THE PROPERTY OF THE", font=font(SANS, 9), fill=FAINT)
    d.text((x0 + 28, y1 - 30), "REPUBLIC OF KESTRELIA. IF FOUND, RETURN TO ANY CONSULATE.", font=font(SANS, 9), fill=FAINT)
    d.text((x1 - 34, y1 - 30), "13", font=font(SANS_B, 11), fill=INK)


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    # outer cover edge
    d.rectangle([0, 0, W - 1, H - 1], outline=NAVY_D, width=6)
    d.rectangle([8, 8, W - 9, H - 9], outline=GOLD, width=1)
    # spread: two pages with a centre gutter
    gutter = 512
    d.rectangle([gutter - 3, 10, gutter + 3, H - 10], fill=(210, 204, 188))
    d.rectangle([gutter - 1, 10, gutter + 1, H - 10], fill=(160, 152, 132))
    data_page(img, d, 12, 12, gutter - 6, H - 12)
    visa_page(img, d, gutter + 6, 12, W - 12, H - 12)
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    size = os.path.getsize(OUT)
    print(f"wrote {OUT} {W}x{H} {size} bytes")
    assert size <= 1_048_576, "over 1 MiB"
    assert img.size == (1024, 1024)


if __name__ == "__main__":
    main()
