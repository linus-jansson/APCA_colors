# --- APCA+Palette generator (OKLCH ramp) ---
# Paste into a Python file or notebook.

import math

# ---------- Color utils: sRGB <-> linear ----------
def srgb_to_linear(c):
    c = c/255.0
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4

def linear_to_srgb(c):
    c = max(0.0, min(1.0, c))
    return 255.0 * (12.92*c if c <= 0.0031308 else 1.055*(c**(1/2.4)) - 0.055)

def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0,2,4))

def rgb_to_hex(r, g, b):
    return "#{:02X}{:02X}{:02X}".format(int(round(r)), int(round(g)), int(round(b)))

# ---------- OKLab/OKLCH conversions (Björn Ottosson) ----------
# sRGB (D65) <-> OKLab
def rgb_to_oklab(r8,g8,b8):
    r = srgb_to_linear(r8)
    g = srgb_to_linear(g8)
    b = srgb_to_linear(b8)
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
    return (linear_to_srgb(r), linear_to_srgb(g), linear_to_srgb(b))

def oklab_to_oklch(L,a,b):
    C = math.hypot(a,b)
    h = (math.degrees(math.atan2(b,a)) + 360.0) % 360.0
    return L, C, h

def oklch_to_oklab(L,C,h):
    rad = math.radians(h)
    a = C*math.cos(rad); b = C*math.sin(rad)
    return L,a,b

# ---------- APCA (approx 0.98G core) ----------
def rel_luminance_from_rgb(r8,g8,b8):
    R = srgb_to_linear(r8); G = srgb_to_linear(g8); B = srgb_to_linear(b8)
    return 0.2126*R + 0.7152*G + 0.0722*B

def apca_Lc(fg_rgb, bg_rgb):
    Yt = rel_luminance_from_rgb(*fg_rgb)
    Yb = rel_luminance_from_rgb(*bg_rgb)
    # soft clamp
    Yt_ = Yt/(Yt + 0.022); Yb_ = Yb/(Yb + 0.022)
    # perceptual tone
    Lt = Yt_**0.57
    Lb = Yb_**0.62
    if Lb > Lt:  # dark text on light bg -> positive
        Lc = 1.14 * (Lb**0.56 - Lt**0.57) * 100.0
    else:        # light text on dark bg -> negative
        Lc = -1.14 * (Lt**0.62 - Lb**0.57) * 100.0
    return Lc

# ---------- Palette generation ----------
def ease(t, gamma=1.15):
    # compress mids slightly; t in [0,1]
    return t**gamma

def generate_scale(base_hex="#6B5BFA", steps=list(range(25, 1000, 25)),
                   L_light=0.98, L_dark=0.10, chroma_taper=0.75):
    base_rgb = hex_to_rgb(base_hex)
    L0, a0, b0 = rgb_to_oklab(*base_rgb)
    _, C0, H0 = oklab_to_oklch(L0, a0, b0)

    out = []
    n = len(steps)
    for i, token in enumerate(steps):
        # t goes 0=lightest ... 1=darkest (token 25 -> 0, 975 -> 1)
        t = i/(n-1)
        Lt = L_light*(1-ease(t)) + L_dark*ease(t)

        # chroma tapers toward ends so very light/dark don't look neon
        taper = 1 - chroma_taper*(abs(0.5 - t)/0.5)  # 1 at center, (1-chroma_taper) at ends
        Ct = C0 * max(0.0, taper)

        L,a,b = oklch_to_oklab(Lt, Ct, H0)
        r,g,b = oklab_to_rgb(L,a,b)
        r8,g8,b8 = int(round(r)), int(round(g)), int(round(b))
        hexv = rgb_to_hex(r8,g8,b8)

        Lc_on_white = apca_Lc((r8,g8,b8), (255,255,255))
        Lc_on_black = apca_Lc((r8,g8,b8), (0,0,0))
        out.append({
            "token": f"color-{token}",
            "hex": hexv,
            "oklch_L": round(Lt,4),
            "oklch_C": round(Ct,4),
            "oklch_H": round(H0,2),
            "APCA_vs_white": round(Lc_on_white, 1),
            "APCA_vs_black": round(Lc_on_black, 1),
        })
    return out

# Example usage:
if __name__ == "__main__":
    palette = generate_scale(base_hex="#7A3093")  # put your base color here
    for row in palette:
        print(row)
