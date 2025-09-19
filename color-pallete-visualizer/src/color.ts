// @ts-nocheck

import Color from "colorjs.io";

/** ==== CONSTANTS FROM YOUR UPPSALA FILE (Blue as reference) ==== */
/** Steps (29 tokens) */
const STEPS = [25, 50, 75, 100, 125, 150, 175, 200, 250, 275, 300, 350, 400, 450, 500, 550, 600, 650, 700, 725, 750, 775, 800, 850, 875, 900, 925, 950, 975];

/** APCA targets by token (positive = measured vs white, negative = vs black) */
const APCA_TARGET = {
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
};

/** ΔH (degrees) relative to step-500 hue, per token (from Blue) */
const DELTA_H = {
  "25": 0.91,
  "50": 8.49,
  "75": 5.87,
  "100": 4.51,
  "125": 3.24,
  "150": 6.33,
  "175": 5.08,
  "200": 3.94,
  "250": 3.46,
  "275": 3.01,
  "300": 2.54,
  "350": 2.05,
  "400": 1.55,
  "450": 0.99,
  "500": 0.0,
  "550": -0.5,
  "600": -1.31,
  "650": -2.36,
  "700": -3.04,
  "725": -3.82,
  "750": -4.35,
  "775": -5.13,
  "800": -5.2,
  "850": -4.31,
  "875": -3.34,
  "900": -3.24,
  "925": -3.29,
  "950": -0.89,
  "975": 4.74
};

/** Chroma multiplier relative to step-500 chroma (from Blue) */
const C_RATIO = {
  "25": 0.0438,
  "50": 0.0884,
  "75": 0.1325,
  "100": 0.1768,
  "125": 0.2528,
  "150": 0.3467,
  "175": 0.4257,
  "200": 0.5250,
  "250": 0.5757,
  "275": 0.6281,
  "300": 0.6845,
  "350": 0.7443,
  "400": 0.8048,
  "450": 0.8691,
  "500": 1.0,
  "550": 1.1505,
  "600": 1.3016,
  "650": 1.4361,
  "700": 1.386,
  "725": 1.3356,
  "750": 1.2733,
  "775": 1.2105,
  "800": 1.0855,
  "850": 0.9544,
  "875": 0.8207,
  "900": 0.6812,
  "925": 0.5332,
  "950": 0.3738,
  "975": 0.2414
};

/** ==== HELPERS ==== */

const BW = Color.contrastAPCA(new Color("#000"), "white");
const WB = Color.contrastAPCA(new Color("#fff"), "black");

// If your runtime gives the opposite (as your log shows), flip all results
const SIGN_OK = (BW > 0 && WB < 0);
function apcaSigned(fg, bg) {
  const v = Color.contrastAPCA(fg, bg);
  return SIGN_OK ? v : -v;
}

// Convenience wrappers
const apcaVsWhite = c => apcaSigned(c, "white");
const apcaVsBlack = c => apcaSigned(c, "black");

// Make OKLCH color
const ok = (L, C, H) => new Color("oklch", [L, C, ((H % 360) + 360) % 360]);

// Hex (clipped to sRGB by Color.js)
const toHex = c => c.to("srgb").toString({ format: "hex" });

// APCA with Color.js
const apca = (fg, bg) => fg.contrastAPCA(bg); // positive=dark-on-light, negative=light-on-dark

// Per-step feasible APCA bounds given H & C
function feasibleRangeForStep(H, C) {
  const maxPos = apcaVsWhite(ok(0.02, C, H));  // darkest we allow
  const minNeg = apcaVsBlack(ok(0.98, C, H));  // lightest we allow
  // Safety margin so we don't chase asymptotes
  return { min: Math.max(minNeg, -106.0), max: Math.min(maxPos, 106.0) };
}

// Solve L so APCA hits target; H & C fixed
function solveLForAPCA(targetLc, H, C, iters = 22) {
  const useWhite = targetLc >= 0;
  let lo = 0.02, hi = 0.98;
  for (let i = 0; i < iters; i++) {
    const mid = (lo + hi) / 2;
    const col = ok(mid, C, H);
    const Lc = useWhite ? apcaVsWhite(col) : apcaVsBlack(col);
    if (useWhite) { if (Lc < targetLc) hi = mid; else lo = mid; }
    else          { if (Lc > targetLc) lo = mid; else hi = mid; }
  }
  return (lo + hi) / 2;
}
console.log("BW:", apcaVsWhite(new Color("#000"))); // should be ~ +106
console.log("WB:", apcaVsBlack(new Color("#fff"))); // should be ~ -106

export function generateAPCAPalette({
  base = "#59626F",
  steps = STEPS,
  targets = APCA_TARGET,
  deltaH = DELTA_H,
  cRatio = C_RATIO,
  anchor500 = false,
  // optional: soft-compress instead of hard-clip when shifting
  anchorStrategy = "clip" // "clip" | "scale"
} = {}) {
  const baseOK = new Color(base).to("oklch");
  const [L0, C0, H0] = baseOK.coords;

  // shift targets so 500 passes through base (if anchoring)
  let tShifted = targets;
  if (anchor500) {
    const t500 = targets["500"];
    const baseAPCA = (t500 >= 0) ? apcaVsWhite(baseOK) : apcaVsBlack(baseOK);
    const offset = baseAPCA - t500;

    if (anchorStrategy === "scale") {
      // compress highs so they don’t exceed limit after shifting
      // find the largest positive after shift and scale the positive side
      const shifted = Object.fromEntries(
        Object.entries(targets).map(([k, v]) => [k, v + offset])
      );
      const posMax = Math.max(...Object.values(shifted).filter(v => v > 0));
      const cap = 105.5; // keep a tiny headroom
      const scale = posMax > cap ? (cap / posMax) : 1;
      tShifted = Object.fromEntries(
        Object.entries(shifted).map(([k, v]) =>
          [k, v > 0 ? v * scale : v] // only compress the positive side
        )
      );
    } else {
      // default: linear shift; we’ll clip per-step below
      tShifted = Object.fromEntries(
        Object.entries(targets).map(([k, v]) => [k, v + offset])
      );
    }
  }

  const out = [];
  for (const s of steps) {
    const key = String(s);
    const H = H0 + (deltaH[key] ?? 0);
    const C = Math.max(0, C0 * (cRatio[key] ?? 1));

    const { min, max } = feasibleRangeForStep(H, C);
    let target = tShifted[key];

    let capped = false;
    if (target > max) { target = max; capped = true; }
    if (target < min) { target = min; capped = true; }

    let col, L;
    if (anchor500 && s === 500) {
      col = baseOK;
      L = baseOK.coords[0];
    } else {
      L = solveLForAPCA(target, H, C);
      col = ok(L, C, H);
    }

    out.push({
      token: `color-${s}`,
      hex: toHex(col),
      OKLCH: { L: +L.toFixed(4), C: +C.toFixed(4), H: +(((H % 360)+360)%360).toFixed(2) },
      APCA_vs_white: +apcaVsWhite(col).toFixed(1),
      APCA_vs_black: +apcaVsBlack(col).toFixed(1),
      APCA_target: targets[key],
      APCA_target_effective: +tShifted[key].toFixed(1),
      APCA_target_clamped: capped ? +target.toFixed(1) : undefined
    });
  }
  return out;
}