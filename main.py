"""The job: Young's modulus of every gel type, and how much it depends on the smoothing.

Run from the project folder:  python main.py
"""
import mechanics

STORE = "data/gels.zarr"

# Three smoothing widths, in points (every experiment has one point every
# 0.1 % strain, so 10 points = 1 % strain): one too small, the one you trust,
# one too large. Change these numbers to your choice, and justify them in README.md.
WIDTHS_POINTS = [0, 0, 0]          # <- replace with your three widths

for width in WIDTHS_POINTS:
    summary = mechanics.run_pipeline(STORE, width)
    cells = []
    for gel_type, result in summary.items():
        mean_kpa = result["mean_E_pa"] / 1000
        sd_kpa = result["sd_E_pa"] / 1000
        cells.append(f"{gel_type}: {mean_kpa:6.2f} ± {sd_kpa:4.2f} kPa (n = {result['n']})")
    print(f"width {width:>3} points ({width / 10:.1f} % strain) | " + " | ".join(cells))
