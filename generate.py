#!/usr/bin/env python3
"""Deterministic generator for the Republic of Ostara passport spread (1024x1024).

Builds entry.png from portrait.jpg with PIL only. No network, no randomness,
no timestamps: re-running produces a byte-identical file.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
NAVY = (22, 38, 70)
NAVY2 = (38, 62, 110)
CREAM = (244, 238, 221)
CREAM2 = (238, 231, 208)
INK = (26, 34, 54)
GREYBLUE = (96, 110, 140)
BLUE = (31, 63, 143)
VIOLET = (106, 61, 154)
REDBROWN = (166, 58, 46)
GREEN = (46, 110, 78)

FD = "/usr/share/fonts/truetype/dejavu/"
FL = "/usr/share/fonts/truetype/liberation/"


def F(name, size):
    return ImageFont.truetype(name, size)


SERIF = lambda s: F(FD + "DejaVuSerif.ttf", s)
SERIFB = lambda s: F(FD + "DejaVuSerif-Bold.ttf", s)
SERIFI = lambda s: F(FL + "LiberationSerif-Italic.ttf", s)
SANS = lambda s: F(FD + "DejaVuSans.ttf", s)
SANSB = lambda s: F(FD + "DejaVuSans-Bold.ttf", s)
MONO = lambda s: F(FD + "DejaVuSansMono.ttf", s)
MONOB = lambda s: F(FD + "DejaVuSansMono-Bold.ttf", s)


def wrap(text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if font.getlength(t) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def field(d, x, y, label, value, vsize=15, label_size=9, value_font=None, w=280):
    d.text((x, y), label, font=SANS(label_size), fill=GREYBLUE)
    vf = value_font or SANSB(vsize)
    # shrink value until it fits
    vs = vsize
    while vf.getlength(value) > w and vs > 9:
        vs -= 1
        vf = SANSB(vs)
    d.text((x, y + label_size + 3), value, font=vf, fill=INK)
    return y + label_size + 3 + vs + 8


def guilloche(d, x0, y0, x1, y1, step=16, color=(206, 214, 228), amp=3):
    """Fine wavy horizontal security lines."""
    yy = y0
    while yy < y1:
        pts = []
        x = x0
        while x <= x1:
            pts.append((x, yy + amp * math.sin((x - x0) / 26.0)))
            x += 6
        d.line(pts, fill=color, width=1)
        yy += step


def arc_text(d, cx, cy, r, text, font, fill, start_deg, end_deg, flip=False):
    """Draw text along a circular arc, centred between start and end angles.
    Auto-shrinks the font until the text fits the arc."""
    span = math.radians(end_deg - start_deg)
    size = font.size
    while size > 6:
        f = SANSB(size)
        total = sum(f.getlength(ch) for ch in text)
        if total <= 0.92 * r * span:
            break
        size -= 1
    font = SANSB(size)
    total = sum(font.getlength(ch) for ch in text)
    if flip:
        # bottom arc: read left-to-right, so iterate angle decreasing
        ang = math.radians(end_deg) - (span - total / r) / 2
        step = -1
    else:
        ang = math.radians(start_deg) + (span - total / r) / 2
        step = 1
    for ch in text:
        wch = font.getlength(ch)
        a = ang + step * (wch / 2) / r
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        layer = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.text((30 - wch / 2, 30 - font.size / 2), ch, font=font, fill=fill)
        if flip:
            rot = 90 - math.degrees(a)
        else:
            rot = -(math.degrees(a) + 90)
        layer = layer.rotate(rot, resample=Image.BICUBIC, center=(30, 30))
        d._image.paste(layer, (int(x - 30), int(y - 30)), layer)
        ang += step * (wch / r)


def round_stamp(base, cx, cy, r, top_text, bottom_text, centre_lines, color,
                angle=0, arc=True):
    s = r * 2 + 40
    layer = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = s // 2
    col = color + (215,)
    d.ellipse([c - r, c - r, c + r, c + r], outline=col, width=3)
    d.ellipse([c - r + 9, c - r + 9, c + r - 9, c + r - 9], outline=col, width=1)
    if arc:
        arc_text(d, c, c, r - 12, top_text, SANSB(11), col, 180, 360)
        arc_text(d, c, c, r - 12, bottom_text, SANSB(11), col, 0, 180, flip=True)
    n = len(centre_lines)
    lh = 15 if n <= 2 else 13
    fs = (13 if arc else 15) if n <= 2 else (11 if n == 3 else 10)
    y = c - n * lh // 2 - 2
    for ln in centre_lines:
        f = SANSB(fs if len(ln) <= 10 else max(8, fs - 2))
        d.text((c - f.getlength(ln) / 2, y), ln, font=f, fill=col)
        y += lh
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    base.paste(layer, (int(cx - s / 2), int(cy - s / 2)), layer)


def rect_stamp(base, x, y, w, h, station, kind, date, color, angle):
    pad = 26
    layer = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    col = color + (215,)
    d.rounded_rectangle([pad, pad, pad + w, pad + h], radius=8, outline=col, width=3)
    d.rounded_rectangle([pad + 5, pad + 5, pad + w - 5, pad + h - 5], radius=6,
                        outline=col, width=1)
    cx = pad + w / 2
    # station name, wrapped to fit
    fs = 11
    lines = wrap(station, SANSB(fs), w - 22)
    while len(lines) > 2 and fs > 8:
        fs -= 1
        lines = wrap(station, SANSB(fs), w - 22)
    yy = pad + 10
    for ln in lines:
        f = SANSB(fs)
        d.text((cx - f.getlength(ln) / 2, yy), ln, font=f, fill=col)
        yy += fs + 3
    d.line([pad + 14, yy + 2, pad + w - 14, yy + 2], fill=col, width=1)
    yy += 8
    f = SANSB(14)
    d.text((cx - f.getlength(kind) / 2, yy), kind, font=f, fill=col)
    yy += 20
    f = MONOB(13)
    d.text((cx - f.getlength(date) / 2, yy), date, font=f, fill=col)
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    base.paste(layer, (int(x - pad), int(y - pad)), layer)


def emblem(d, cx, cy, r, color=NAVY):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=2)
    d.ellipse([cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4], outline=color, width=1)
    # post horn: small cone + bell above three waves
    d.polygon([(cx - 9, cy - 4), (cx + 9, cy - 4), (cx + 3, cy - 13), (cx - 3, cy - 13)],
              outline=color, width=2)
    d.ellipse([cx + 7, cy - 16, cx + 13, cy - 10], outline=color, width=2)
    for k, yy in enumerate((cy + 2, cy + 8, cy + 14)):
        pts = [(cx - r + 9 + t, yy + 2 * math.sin(t / 5.0))
               for t in range(0, 2 * r - 18, 3)]
        d.line(pts, fill=color, width=1)


def build():
    img = Image.new("RGB", (W, H), (18, 28, 50))
    d = ImageDraw.Draw(img)

    # ---- pages ----
    d.rectangle([10, 10, 508, 1014], fill=CREAM)
    d.rectangle([516, 10, 1014, 1014], fill=CREAM2)
    # spine shading
    for i in range(14):
        d.line([508 - i, 10, 508 - i, 1014], fill=(210, 202, 178))
        d.line([516 + i, 10, 516 + i, 1014], fill=(205, 197, 172))
    d.rectangle([10, 10, 508, 1014], outline=NAVY, width=3)
    d.rectangle([516, 10, 1014, 1014], outline=NAVY, width=3)
    guilloche(d, 16, 16, 502, 1008)
    guilloche(d, 522, 16, 1008, 1008)

    # ================= LEFT: DATA PAGE =================
    LX0, LX1 = 32, 486
    d.text((LX1 - SANSB(11).getlength("No. OST472918"), 26),
           "No. OST472918", font=SANSB(11), fill=NAVY2)
    emblem(d, 259, 60, 27)
    t = "REPUBLIC OF OSTARA"
    f = SERIFB(21)
    d.text((259 - f.getlength(t) / 2, 94), t, font=f, fill=NAVY)
    t = "OSTARA REPUBLIK"
    f = SANS(11)
    d.text((259 - f.getlength(t) / 2, 120), t, font=f, fill=GREYBLUE)
    t = "PASSPORT  ·  FARÐABRÉF"
    f = SANSB(14)
    tw = f.getlength(t)
    d.text((259 - tw / 2, 138), t, font=f, fill=NAVY)
    d.line([LX0, 160, 259 - tw / 2 - 10, 160], fill=NAVY, width=1)
    d.line([259 + tw / 2 + 10, 160, LX1, 160], fill=NAVY, width=1)

    # portrait
    port = Image.open("portrait.jpg").convert("RGB")
    pw, ph = 148, 192
    port = port.resize((pw * 3, ph * 3), Image.LANCZOS)
    # centre-crop to target ratio
    tw_, th_ = pw * 3, ph * 3
    src = Image.open("portrait.jpg").convert("RGB")
    sw, sh = src.size
    target = pw / ph
    if sw / sh > target:
        nw = int(sh * target)
        src = src.crop(((sw - nw) // 2, 0, (sw - nw) // 2 + nw, sh))
    else:
        nh = int(sw / target)
        src = src.crop((0, 0, sw, nh))
    port = src.resize((pw, ph), Image.LANCZOS)
    img.paste(port, (LX0, 170))
    d.rectangle([LX0, 170, LX0 + pw, 170 + ph], outline=NAVY, width=2)

    # ghost portrait
    ghost = src.resize((100, 130), Image.LANCZOS).convert("RGBA")
    ghost.putalpha(58)
    cream_bg = Image.new("RGBA", (100, 130), CREAM + (255,))
    ghost = Image.alpha_composite(cream_bg, ghost)
    img.paste(ghost.convert("RGB"), (386, 170))
    d.rectangle([386, 170, 486, 300], outline=(150, 158, 180), width=1)

    # fields right of photo
    fx, fy = 198, 170
    fy = field(d, fx, fy, "SURNAME  /  ÆTTARNAMN", "MARLOW", w=180)
    fy = field(d, fx, fy, "GIVEN NAMES  /  FORNAMN", "ELIAS", w=180)
    fy = field(d, fx, fy, "NATIONALITY  /  ÞJÓÐARN", "OSTARIAN", w=180)
    fy = field(d, fx, fy, "DATE OF BIRTH  /  FØDINGARDAG", "07 JUN 1982", w=180)
    fy = field(d, fx, fy, "PLACE OF BIRTH  /  FØDINGARSTAD", "LOWICK-ON-TIDE", w=180)
    fy = field(d, fx, fy, "SEX  /  KYNN", "M", w=180)

    d.line([LX0, 384, LX1, 384], fill=NAVY, width=1)
    y = 396
    y = field(d, LX0, y, "DATE OF ISSUE  /  ÚTGÁFUDAG", "12 FEB 2024", w=210)
    y = field(d, LX0, y, "DATE OF EXPIRY  /  GILDISTÍD", "11 FEB 2034", w=210)
    y = field(d, LX0, y, "AUTHORITY  /  ÚTGÁFUSTAÐUR",
              "PASSPORT OFFICE, LOWICK-ON-TIDE", vsize=12, w=210)
    y2 = 396
    y2 = field(d, 262, y2, "PERSONAL No.  /  KENNITALA", "TML1187OST", w=224)
    y2 = field(d, 262, y2, "OCCUPATION  /  STARF", "TIDAL MAIL CARRIER", vsize=13, w=224)
    y2 = field(d, 262, y2, "TIDAL MAIL LICENCE", "TML-1187", w=224)

    # signature box
    d.rectangle([LX0, 548, LX0 + 210, 626], outline=NAVY, width=1)
    d.text((LX0 + 8, 554), "SIGNATURE  /  UNDIRSKRIFT", font=SANS(8), fill=GREYBLUE)
    sig = Image.new("RGBA", (220, 60), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sig)
    sd.text((14, 8), "Elias Marlow", font=SERIFI(30), fill=(30, 40, 90, 255))
    sig = sig.rotate(-3, resample=Image.BICUBIC, expand=False)
    img.paste(sig, (LX0, 566), sig)
    d.line([LX0 + 8, 616, LX0 + 202, 616], fill=GREYBLUE, width=1)

    # licence round stamp beside signature (straight lines: too small for arc text)
    round_stamp(img, 374, 587, 42, "", "",
                ["TIDAL MAIL", "LICENCE", "TML-1187", "VALID"], BLUE, angle=-6,
                arc=False)

    # observations
    d.rectangle([LX0, 642, LX1, 742], outline=NAVY, width=1)
    d.text((LX0 + 8, 648), "OBSERVATIONS  /  ATHUGASEMDIR", font=SANS(8),
           fill=GREYBLUE)
    obs = ("HOLDER IS A LICENSED TIDAL MAIL CARRIER (LIC. TML-1187). "
           "TIDAL CROSSINGS PERMITTED ONLY WITHIN THE LOW-WATER WINDOWS "
           "OF THE OFFICIAL OSTARA TIDE TABLE.")
    yy = 664
    for ln in wrap(obs, SANS(11), LX1 - LX0 - 16):
        d.text((LX0 + 8, yy), ln, font=SANS(11), fill=INK)
        yy += 15

    # address block
    y = 758
    y = field(d, LX0, y, "HOLDER'S ADDRESS", "14 CAUSEWAY COTTAGES, LOWICK-ON-TIDE",
              vsize=12, w=454)
    y = field(d, LX0, y, "EMERGENCY CONTACT", "M. MARLOW — HARBOURMASTERS' QUAY",
              vsize=12, w=454)
    fp = ("THIS PASSPORT REMAINS THE PROPERTY OF THE REPUBLIC OF OSTARA "
          "AND MUST BE SURRENDERED ON DEMAND TO A PASSPORT OFFICER.")
    yy = y + 6
    for ln in wrap(fp, SANS(8), LX1 - LX0):
        f8 = SANS(8)
        d.text((259 - f8.getlength(ln) / 2, yy), ln, font=f8, fill=GREYBLUE)
        yy += 11

    # issuing-office round stamp overlapping the photo corner only
    round_stamp(img, 150, 340, 30, "", "",
                ["PASSPORT OFFICE", "OSTARA", "12 FEB 2024"], NAVY2, angle=8,
                arc=False)

    # MRZ
    d.rectangle([LX0, 928, LX1, 994], fill=(255, 255, 255))
    d.rectangle([LX0, 928, LX1, 994], outline=NAVY, width=1)
    m1 = "P<OSTMARLOW<<ELIAS<<<<<<<<<<<<<<<<<<<<<<<<<<"
    m2 = "OST4729186OST8206071M3402111TML1187OST<<<<01"
    fm = MONO(16)
    d.text((259 - fm.getlength(m1) / 2, 936), m1, font=fm, fill=INK)
    d.text((259 - fm.getlength(m2) / 2, 960), m2, font=fm, fill=INK)

    # ================= RIGHT: VISAS PAGE =================
    RX0, RX1 = 538, 992
    t = "VISAS"
    f = SERIFB(19)
    d.text((RX0, 26), t, font=f, fill=NAVY)
    t = "VEGABRÉF"
    f = SANS(11)
    d.text((RX0, 50), t, font=f, fill=GREYBLUE)
    t = "PAGE 12"
    f = SANSB(11)
    d.text((RX1 - f.getlength(t), 26), t, font=f, fill=NAVY2)
    t = "PASSPORT No. OST472918"
    f = SANS(10)
    d.text((RX1 - f.getlength(t), 50), t, font=f, fill=GREYBLUE)

    # endorsement box
    d.rectangle([RX0, 72, RX1, 176], outline=NAVY, width=2)
    d.text((RX0 + 8, 78), "ENDORSEMENT  /  ÁRITUN", font=SANSB(9), fill=NAVY)
    end = ("TIDAL MAIL MAY BE CARRIED ONLY BETWEEN THE LOW-WATER WINDOWS "
           "IN THE OFFICIAL TIDE TABLE. CROSSINGS OUTSIDE THE WINDOW ARE "
           "FORBIDDEN. VALID ONLY WITH TIDAL MAIL LICENCE TML-1187. — "
           "HARBOURMASTER, LOWICK-ON-TIDE")
    yy = 94
    for ln in wrap(end, SANS(10), RX1 - RX0 - 16):
        d.text((RX0 + 8, yy), ln, font=SANS(10), fill=INK)
        yy += 13

    # visa sticker
    vx0, vy0, vx1, vy1 = RX0, 190, RX1, 396
    d.rectangle([vx0, vy0, vx1, vy1], fill=(219, 233, 220))
    d.rectangle([vx0, vy0, vx1, vy1], outline=GREEN, width=2)
    d.rectangle([vx0 + 5, vy0 + 5, vx1 - 5, vy1 - 5], outline=GREEN, width=1)
    # diagonal guilloche inside sticker
    for k in range(-vy1, vx1, 12):
        d.line([vx0 + 6 + k, vy1 - 6, vx0 + 6 + k + (vy1 - vy0 - 12), vy0 + 6],
               fill=(198, 216, 200), width=1)
    t = "VISA"
    f = SERIFB(20)
    d.text((vx0 + 12, vy0 + 10), t, font=f, fill=GREEN)
    t = "ISLE OF KESTRELWICK — TIDAL ISLAND"
    f = SANSB(12)
    d.text((vx0 + 78, vy0 + 16), t, font=f, fill=GREEN)
    d.line([vx0 + 12, vy0 + 40, vx1 - 12, vy0 + 40], fill=GREEN, width=1)
    vy = vy0 + 48
    vy = field(d, vx0 + 12, vy, "VISA No.", "VK-2025-0441", vsize=13, w=200)
    vy = field(d, vx0 + 12, vy, "TYPE", "MULTIPLE ENTRY", vsize=13, w=200)
    vy = field(d, vx0 + 12, vy, "PURPOSE", "TIDAL MAIL DELIVERY", vsize=13, w=200)
    vy2 = vy0 + 48
    vy2 = field(d, vx0 + 232, vy2, "VALID FROM", "01 MAY 2025", vsize=13, w=200)
    vy2 = field(d, vx0 + 232, vy2, "VALID UNTIL", "31 OCT 2025", vsize=13, w=200)
    vy2 = field(d, vx0 + 232, vy2, "ISSUED", "22 APR 2025", vsize=13, w=200)
    d.line([vx0 + 12, vy1 - 34, vx1 - 12, vy1 - 34], fill=GREEN, width=1)
    t = "CONDITION: LANDING ONLY AT LOW WATER."
    f = SANSB(10)
    d.text((vx0 + 12, vy1 - 28), t, font=f, fill=GREEN)

    # PAID toll stamp overlapping the visa sticker
    round_stamp(img, 925, 360, 50, "TIDAL CAUSEWAY LEVY", "12 MAY 2025",
                ["PAID", "2 KORUNA"], REDBROWN, angle=12)

    # entry/exit stamps, chronological, 2 columns x 4 rows
    stamps = [
        ("LOWICK SORTING OFFICE", "DEPARTURE", "18 MAR 2024", BLUE, -4),
        ("KESTRELWICK ISLAND POST OFFICE", "ARRIVAL", "18 MAR 2024", VIOLET, 3),
        ("KESTRELWICK ISLAND POST OFFICE", "DEPARTURE", "29 APR 2024", VIOLET, 5),
        ("LOWICK SORTING OFFICE", "ARRIVAL", "29 APR 2024", BLUE, -3),
        ("TIDE STATION NORTH FLATS", "DEPARTURE", "12 MAY 2025", REDBROWN, -5),
        ("KESTRELWICK ISLAND POST OFFICE", "ARRIVAL", "12 MAY 2025", VIOLET, 4),
        ("KESTRELWICK ISLAND POST OFFICE", "DEPARTURE", "30 SEP 2025", VIOLET, -4),
        ("HARBOURMASTERS' QUAY", "ARRIVAL", "30 SEP 2025", BLUE, 3),
    ]
    xs = [548, 772]
    ys = [420, 552, 684, 816]
    for i, (st, kind, dt, col, ang) in enumerate(stamps):
        rect_stamp(img, xs[i % 2], ys[i // 2], 210, 118, st, kind, dt, col, ang)

    # tide-table strip
    t1 = "LOW WATER · KESTRELWICK CAUSEWAY"
    t2 = "12 MAY 2025  06:42 / 19:05    ·    30 SEP 2025  07:11 / 19:38"
    f = MONOB(11)
    d.text((765 - f.getlength(t1) / 2, 950), t1, font=f, fill=NAVY2)
    f = MONO(11)
    d.text((765 - f.getlength(t2) / 2, 970), t2, font=f, fill=GREYBLUE)

    img.save("entry.png", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    build()
