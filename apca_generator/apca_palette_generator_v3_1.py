
# APCA palette generator v3 (family-agnostic)
# Modes:
#   --mode gray  -> neutral palette (C=0), ramps toward #FFF/#000 per APCA targets
#   --mode color -> hold base hue, taper chroma to ends (no family curves)

import math, json, argparse

TARGETS = {
  "25": -106,
  "50": -104,
  "75": -103,
  "100": -101,
  "125": -94,
  "150": -87,
  "175": -80,
  "200": 32,
  "250": 36,
  "275": 41,
  "300": 48,
  "350": 55,
  "400": 63,
  "450": 70,
  "500": 77,
  "550": 80,
  "600": 83,
  "650": 87,
  "700": 90,
  "725": 93,
  "750": 97,
  "775": 100,
  "800": 102,
  "850": 103,
  "875": 104,
  "900": 105,
  "925": 105,
  "950": 106,
  "975": 106,
}
BG_MAP = {
  "25": "black",
  "50": "black",
  "75": "black",
  "100": "black",
  "125": "black",
  "150": "black",
  "175": "black",
  "200": "white",
  "250": "white",
  "275": "white",
  "300": "white",
  "350": "white",
  "400": "white",
  "450": "white",
  "500": "white",
  "550": "white",
  "600": "white",
  "650": "white",
  "700": "white",
  "725": "white",
  "750": "white",
  "775": "white",
  "800": "white",
  "850": "white",
  "875": "white",
  "900": "white",
  "925": "white",
  "950": "white",
  "975": "white",
}

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

def solve_L_for_apca(target_Lc, bg_rgb, H_deg, C_val):
    lo, hi = 0.02, 0.98
    last = None
    for _ in range(28):
        mid = (lo+hi)/2
        r,g,b = oklab_to_rgb(*oklch_to_oklab(mid, C_val, H_deg))
        rgb = (int(round(r)), int(round(g)), int(round(b)))
        Lc = apca_Lc(rgb, bg_rgb)
        if target_Lc >= 0:
            if Lc < target_Lc: hi = mid
            else: lo = mid
        else:
            if Lc > target_Lc: lo = mid
            else: hi = mid
        last = mid
    return last


# --- additions below ---

def oklch_to_srgb_with_clipcheck(L,C,H):
    """Return (rgb8, clipped_flag, preclamp_rgb_float)"""
    # Convert without clamping to detect gamut
    rad = math.radians(H)
    a = C*math.cos(rad); b = C*math.sin(rad)
    l_ = L + 0.3963377774*a + 0.2158037573*b
    m_ = L - 0.1055613458*a - 0.0638541728*b
    s_ = L - 0.0894841775*a - 1.2914855480*b
    l = l_**3; m = m_**3; s = s_**3
    r = +4.0767416621*l - 3.3077115913*m + 0.2309699292*s
    g = -1.2684380046*l + 2.6097574011*m - 0.3413193965*s
    b = -0.0041960863*l - 0.7034186147*m + 1.7076147010*s

    def to8(x):
        # linear->srgb without clamp for check
        sr = 12.92*x if x <= 0.0031308 else 1.055*(x**(1/2.4)) - 0.055
        return 255.0*sr

    rf = to8(r); gf = to8(g); bf = to8(b)

    clipped = (rf<0 or rf>255 or gf<0 or gf>255 or bf<0 or bf>255)
    # Now clamp for output
    def clamp8(v): return int(round(min(255, max(0, v))))
    return (clamp8(rf), clamp8(gf), clamp8(bf)), clipped, (rf,gf,bf)

def match_apca_with_gamut(base_H, base_C, target_Lc, bg_rgb, tol=0.6, min_L_nongray=0.06):
    """Solve for L, and shrink C if out-of-gamut or too close to black, while staying within APCA tol."""
    # First, binary search L at given C
    lo, hi = 0.02, 0.98
    L = None
    for _ in range(28):
        mid = (lo+hi)/2
        rgb8, clipped, _ = oklch_to_srgb_with_clipcheck(mid, base_C, base_H)
        Lc = apca_Lc(rgb8, bg_rgb)
        if target_Lc >= 0:
            if Lc < target_Lc: hi = mid
            else: lo = mid
        else:
            if Lc > target_Lc: lo = mid
            else: hi = mid
        L = mid

    # If clipped or nearly black, progressively reduce C and (if needed) slightly raise L within tolerance
    C = base_C
    for _ in range(16):
        rgb8, clipped, f = oklch_to_srgb_with_clipcheck(L, C, base_H)
        Lc = apca_Lc(rgb8, bg_rgb)

        # too close to black (visually collapsed)?
        too_black = max(rgb8) <= 6  # all channels <= 6 ~ "#000007"
        if not clipped and not too_black and abs(Lc - target_Lc) <= tol:
            return L, C, rgb8, Lc

        # reduce chroma to pull back in gamut and lift channels
        C *= 0.75

        # small nudge on L to stay within tol
        if target_Lc >= 0 and L < 0.10:
            L = min(0.10, L + 0.01)
        elif target_Lc < 0 and L < 0.06:
            L = min(0.08, L + 0.006)

    # fallback: return whatever is closest
    rgb8, clipped, _ = oklch_to_srgb_with_clipcheck(L, max(0.0, C), base_H)
    return L, max(0.0, C), rgb8, apca_Lc(rgb8, bg_rgb)


def chroma_profile(t, power=1.0):
    x = 1.0 - abs(2*t - 1.0)
    return x**power

def generate_palette(base_hex="#955AAA", mode="color", chroma_strength=1.0, chroma_power=1.0):
    steps = sorted(TARGETS.keys())
    base_rgb = hex_to_rgb(base_hex)
    L0,a0,b0 = rgb_to_oklab(*base_rgb)
    L0, C0, H0 = oklab_to_oklch(L0,a0,b0)
    out = []
    n = len(steps)
    for i, s in enumerate(steps):
        tgt = TARGETS[s]
        bg_rgb = (255,255,255) if BG_MAP[s] == "white" else (0,0,0)
        t = i/(n-1)
        if mode == "gray":
            H = 0.0; C = 0.0
        else:
            H = H0
            C = C0 * chroma_strength * chroma_profile(t, power=chroma_power)
        # Gamut-aware APCA match to avoid collapsing to #000
        L, C, rgb, Lc_actual = match_apca_with_gamut(H, C, tgt, bg_rgb)
        out.append({
            "token": f"color-{s}",
            "hex": rgb_to_hex(*rgb),
            "APCA_target": tgt,
            "APCA_vs_white": round(apca_Lc(rgb,(255,255,255)),1),
            "APCA_vs_black": round(apca_Lc(rgb,(0,0,0)),1),
            "OKLCH_L": round(L,4), "OKLCH_C": round(C,4), "OKLCH_H": round(H,2),
        })
    return out

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["gray","color"], default="color")
    p.add_argument("--base", default="#955AAA")
    p.add_argument("--chroma-strength", type=float, default=1.0)
    p.add_argument("--chroma-power", type=float, default=1.0)
    p.add_argument("--out", default="palette.json")
    args = p.parse_args()
    data = generate_palette(args.base, args.mode, args.chroma_strength, args.chroma_power)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("Wrote", args.out, "mode", args.mode, "base", args.base)

if __name__ == "__main__":
    main()
