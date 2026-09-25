#!/usr/bin/env python3
"""
Render the Chapter 3 "http_req_duration only covers the last 3 phases" timeline:

    codelabs/tutorials/assets/images/k6-ch3-latency-timeline.png   (codelab)
    k6/slides/assets/Ch3/latency_timeline.png                     (Ch3 slide 6, larger type)

One HTTP request drawn as six adjacent segments (illustrative widths, not to scale).
Connection-setup phases are neutral gray (not counted in http_req_duration); the three
counted phases use one blue ramp, with waiting (TTFB) darkest as the usual bottleneck.
Every segment is labelled in place, so the grouping never relies on colour alone.
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "codelabs", "tutorials", "assets", "images", "k6-ch3-latency-timeline.png")
OUT_SLIDE = os.path.join(ROOT, "k6", "slides", "assets", "Ch3", "latency_timeline.png")

for fam in ("Noto Sans CJK TC", "Noto Sans CJK HK", "Noto Sans CJK JP"):
    if any(f.name == fam for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam
        break

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
BRACKET_GRAY = "#898781"
BRACKET_BLUE = "#1c5cab"

# (metric, description, width, fill, text colour)
SEGMENTS = [
    ("blocked", "等待可用連線槽位\n（含 DNS 查詢）", 1.25, "#e1e0d9", INK),
    ("connecting", "TCP 三向握手", 1.25, "#d3d2ca", INK),
    ("tls_handshaking", "TLS 憑證協商", 1.5, "#c3c2b7", INK),
    ("sending", "送出請求", 1.0, "#86b6ef", INK),
    ("waiting (TTFB)", "伺服器處理運算", 3.2, "#2a78d6", "#ffffff"),
    ("receiving", "下載回應內容", 1.3, "#86b6ef", INK),
]
GAP = 0.05


def bracket(ax, x0, x1, y, text, color, k, below=False):
    tick = -0.12 if not below else 0.12
    ax.plot([x0, x0, x1, x1], [y + tick, y, y, y + tick], color=color, lw=1.6, solid_capstyle="round")
    ax.text((x0 + x1) / 2, y + (0.12 if not below else -0.12), text, ha="center",
            va="bottom" if not below else "top", fontsize=11.5 * k, color=color, fontweight="bold")


def render(out, k, surface=SURFACE):
    total = sum(w for _, _, w, _, _ in SEGMENTS) + GAP * (len(SEGMENTS) - 1)
    fig = plt.figure(figsize=(16, 2.35), dpi=150, facecolor=surface)
    ax = fig.add_axes([0.01, 0.02, 0.98, 0.96])
    ax.set_facecolor(surface)
    ax.set_xlim(-0.05, total + 0.05)
    ax.set_ylim(-1.0, 1.08)
    ax.axis("off")

    x = 0.0
    starts = []
    for name, desc, w, fill, fg in SEGMENTS:
        starts.append(x)
        ax.add_patch(FancyBboxPatch((x, -0.3), w, 0.72, boxstyle="round,pad=0,rounding_size=0.06",
                                    fc=fill, ec="none"))
        ax.text(x + w / 2, 0.06, name, ha="center", va="center", fontsize=11.5 * k, color=fg,
                fontweight="bold")
        ax.text(x + w / 2, -0.42, desc, ha="center", va="top", fontsize=10 * k, color=INK_2, linespacing=1.3)
        x += w + GAP

    conn_end = starts[3] - GAP
    bracket(ax, 0, conn_end, 0.62, "連線準備：不計入 http_req_duration（連線複用時 ≈ 0）", BRACKET_GRAY, k)
    bracket(ax, starts[3], total, 0.62, "http_req_duration = sending + waiting + receiving", BRACKET_BLUE, k)

    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, facecolor=surface)
    plt.close(fig)
    print(f"wrote {out}")


def main():
    render(OUT, 1.0)
    render(OUT_SLIDE, 1.3, surface="#f8fafc")  # match the Ch3 slide background


if __name__ == "__main__":
    main()
