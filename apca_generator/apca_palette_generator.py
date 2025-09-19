
# APCA palette generator
# Generated from your uploaded palette to preserve stepwise ΔH and C-ratio, and to target APCA per step.
# Usage:
#   python apca_palette_generator.py --base "#2A9D8F" --out "palette.json"
# or import and call generate_palette(base_hex)

import math, json, argparse

APCA_TARGET = {
  "25": -106.0,
  "50": -104.0,
  "75": -102.0,
  "100": -100.0,
  "125": -94.0,
  "150": -87.0,
  "175": -81.0,
  "200": 32.0,
  "250": 36.0,
  "275": 41.0,
  "300": 49.0,
  "350": 55.0,
  "400": 62.0,
  "450": 68.0,
  "500": 73.0,
  "550": 78.0,
  "600": 83.0,
  "650": 86.0,
  "700": 89.0,
  "725": 93.0,
  "750": 97.0,
  "775": 100.0,
  "800": 102.0,
  "850": 103.0,
  "875": 104.0,
  "900": 105.0,
  "925": 105.0,
  "950": 106.0,
  "975": 106.0
}
DELTA_H = {
  "25": 0.9099999999999682,
  "50": 8.490000000000009,
  "75": 5.8700000000000045,
  "100": 4.509999999999991,
  "125": 3.240000000000009,
  "150": 6.329999999999984,
  "175": 5.079999999999984,
  "200": 3.9399999999999977,
  "250": 3.4599999999999795,
  "275": 3.009999999999991,
  "300": 2.5399999999999636,
  "350": 2.0500000000000114,
  "400": 1.5500000000000114,
  "450": 0.9900000000000091,
  "500": 0.0,
  "550": -0.5,
  "600": -1.3100000000000023,
  "650": -2.3600000000000136,
  "700": -3.0400000000000205,
  "725": -3.819999999999993,
  "750": -4.350000000000023,
  "775": -5.1299999999999955,
  "800": -5.199999999999989,
  "850": -4.310000000000002,
  "875": -3.340000000000032,
  "900": -3.240000000000009,
  "925": -3.2900000000000205,
  "950": -0.8900000000000432,
  "975": 4.740000000000009
}
C_RATIO = {
  "25": 0.04378043382027446,
  "50": 0.08839088092076139,
  "75": 0.13241478530323153,
  "100": 0.17683709606020365,
  "125": 0.2527999114652501,
  "150": 0.3465582115980523,
  "175": 0.42567507746790617,
  "200": 0.5250110668437362,
  "250": 0.5758078795927402,
  "275": 0.628187250996016,
  "300": 0.6846834882691457,
  "350": 0.7440681717574148,
  "400": 0.8048804780876495,
  "450": 0.8692452412571935,
  "500": 1.0,
  "550": 1.1503098716246127,
  "600": 1.3017817618415228,
  "650": 1.436100044267375,
  "700": 1.386111111111111,
  "725": 1.3358012394864986,
  "750": 1.2738933156263834,
  "775": 1.2104138999557326,
  "800": 1.0854913678618858,
  "850": 0.9543824701195219,
  "875": 0.8205289951305887,
  "900": 0.680920761398849,
  "925": 0.5333886675520142,
  "950": 0.37359451084550693,
  "975": 0.24143426294820716
}

STEPS = sorted(APCA_TARGET.keys())

def srgb_to_linear(c):
    c = c/255.0
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4

def linear_to_srgb(c):
    c = max(0.0, min(1.0, c))
    return 255.0 * (12.92*c if c <= 0.0031308 else 1.055*(c**(1/2.4)) - 0.055)

def rel_luminance_from_rgb(r8,g8,b8):
    R = srgb_to_linear(r8); G = srgb_to_linear(g8); B = srgb_to_linear(b8)
    return 0.2126*R + 0.7152*G + 0.0722*B

def apca_Lc(fg_rgb, bg_rgb):
    Yt = rel_luminance_from_rgb(*fg_rgb)
    Yb = rel_luminance_from_rgb(*bg_rgb)
    Yt_ = Yt/(Yt + 0.022); Yb_ = Yb/(Yb + 0.022)
    Lt = Yt_**0.57; Lb = Yb_**0.62
    if Lb > Lt:
        return 1.14 * (Lb**0.56 - Lt**0.57) * 100.0
    else:
        return -1.14 * (Lt**0.62 - Lb**0.57) * 100.0

def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0,2,4))

def rgb_to_hex(r, g, b):
    return "#{:02X}{:02X}{:02X}".format(int(round(r)), int(round(g)), int(round(b)))

def rgb_to_oklab(r8,g8,b8):
    def lin(x): 
        x = x/255.0
        return x/12.92 if x <= 0.04045 else ((x+0.055)/1.055)**2.4
    r = lin(r8); g = lin(g8); b = lin(b8)
    l = 0.4122214708*r + 0.5363325363*g + 0.0514459929*b
    m = 0.2119034982*r + 0.6806995451*g + 0.1073969566*b
    s = 0.0883024619*r + 0.2817188376*g + 0.6299787005*b
    l_= l**(1/3); m_= m**(1/3); s_= s**(1/3)
    L = 0.2104542553*l_ + 0.7936177850*m_ - 0.0040720468*s_
    a = 1.9779984951*l_ - 2.4285922050*m_ + 0.4505937099*s_
    b = 0.0259040371*l_ + 0.7827717662*m_ - 0.8086757660*s_
    return L, a, b

def oklab_to_rgb(L,a,b):
    l_ = L + 0.3963377774*a + 0.2158037573*b
    m_ = L - 0.1055613458*a - 0.0638541728*b
    s_ = L - 0.0894841775*a - 1.2914855480*b
    l = l_**3; m = m_**3; s = s_**3
    r = +4.0767416621*l - 3.3077115913*m + 0.2309699292*s
    g = -1.2684380046*l + 2.6097574011*m - 0.3413193965*s
    b = -0.0041960863*l - 0.7034186147*m + 1.7076147010*s
    def comp(x): 
        x = max(0.0, min(1.0, x))
        return 255.0 * (12.92*x if x <= 0.0031308 else 1.055*(x**(1/2.4)) - 0.055)
    return (comp(r), comp(g), comp(b))

def oklab_to_oklch(L,a,b):
    C = math.hypot(a,b)
    h = (math.degrees(math.atan2(b,a)) + 360.0) % 360.0
    return L, C, h

def oklch_to_oklab(L,C,h):
    rad = math.radians(h)
    a = C*math.cos(rad); b = C*math.sin(rad)
    return L,a,b

def solve_L_for_apca(target_Lc, H_deg, C_val):
    lo, hi = 0.02, 0.98
    bg = (255,255,255) if target_Lc >= 0 else (0,0,0)
    for _ in range(22):
        mid = (lo+hi)/2
        r,g,b = oklab_to_rgb(*oklch_to_oklab(mid, C_val, H_deg))
        rgb = (int(round(r)), int(round(g)), int(round(b)))
        Lc = apca_Lc(rgb, bg)
        if target_Lc >= 0:
            if Lc < target_Lc:
                hi = mid
            else:
                lo = mid
        else:
            if Lc > target_Lc:
                lo = mid
            else:
                hi = mid
    return (lo+hi)/2

def generate_palette(base_hex="#6B5BFA"):
    base_rgb = hex_to_rgb(base_hex)
    L0,a0,b0 = rgb_to_oklab(*base_rgb)
    L0, C0, H0 = oklab_to_oklch(L0,a0,b0)
    out = []
    for s in STEPS:
        target = APCA_TARGET[s]
        H = (H0 + float(DELTA_H[s])) % 360.0
        C = max(0.0, C0 * float(C_RATIO[s]))
        L = solve_L_for_apca(target, H, C)
        r,g,b = oklab_to_rgb(*oklch_to_oklab(L,C,H))
        rgb = (int(round(r)), int(round(g)), int(round(b)))
        out.append({
            "token": f"color-{s}",
            "hex": rgb_to_hex(*rgb),
            "APCA_target": target,
            "APCA_vs_white": round(apca_Lc(rgb,(255,255,255)),1),
            "APCA_vs_black": round(apca_Lc(rgb,(0,0,0)),1),
            "OKLCH_L": round(L,4),
            "OKLCH_C": round(C,4),
            "OKLCH_H": round(H,2),
        })

    return out

def main():
    import argparse, json
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="#2A9D8F", help="Base color HEX (e.g. #2A9D8F)")
    p.add_argument("--out", default="palette.json", help="Output JSON filename")
    args = p.parse_args()
    data = generate_palette(args.base)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("Wrote", args.out, "for base", args.base)

if __name__ == "__main__":
    main()
