#!/usr/bin/env python3
"""
Render the Chapter 5 "8 classic dashboard curve patterns" small-multiples figure
for the k6 codelab:

    codelabs/tutorials/assets/images/k6-ch5-curve-patterns.png

Colour follows the metric, never the panel: every metric keeps one colour in all
eight panels. Load-axis metrics (VUs, RPS) are dashed, response-axis metrics are
solid, and every line is direct-labelled so identity never relies on colour alone.
Percentiles (P90/P95/P99) are ordinal, so they use one blue ramp light -> dark.
Palettes validated with the dataviz skill's validate_palette.js (light mode).
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "codelabs", "tutorials", "assets", "images", "k6-ch5-curve-patterns.png")

for fam in ("Noto Sans CJK TC", "Noto Sans CJK HK", "Noto Sans CJK JP"):
    if any(f.name == fam for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam
        break

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
BASELINE = "#c3c2b7"

# metric -> (label, colour, dashed?)
M = {
    "vus": ("VUs", "#1baf7a", True),
    "rps": ("RPS", "#4a3aa7", True),
    "p90": ("P90", "#86b6ef", False),
    "p95": ("P95", "#2a78d6", False),
    "p99": ("P99", "#0d366b", False),
    "err": ("錯誤率", "#e34948", False),
    "blocked": ("blocked", "#e87ba4", False),
}

X = list(range(12))
lin = lambda a, b: [a + (b - a) * i / 11 for i in X]  # noqa: E731

PANELS = [
    ("① 健康線性", "VUs 與 RPS 同步上升，P95 平穩",
     [("vus", lin(0.6, 8.8)), ("rps", lin(0.4, 8.2)), ("p95", [1.6] * 12)], None),
    ("② 飽和平台（拐點）", "VUs 還在加，RPS 走平，P95 開始爬",
     [("vus", lin(0.6, 8.8)), ("rps", [0.4 + 0.8 * i if i < 7 else 5.9 for i in X]),
      ("p95", [1.6] * 7 + [2.6, 3.8, 5.0, 6.2, 7.4])], ("拐點", 6.5)),
    ("③ 崩潰懸崖", "P95 與錯誤率同時暴衝，RPS 反而下降",
     [("rps", [0.4 + 0.8 * i for i in range(7)] + [4.0, 3.2, 2.8, 2.6, 2.5]),
      ("p95", [1.6] * 7 + [8.5, 9.3, 9.5, 9.6, 9.6]),
      ("err", [0.2] * 7 + [4.5, 6.3, 6.8, 7.0, 7.1])], ("崩潰", 6.5)),
    ("④ 尾巴張開", "P90 / P95 平穩，只有 P99 越拉越開",
     [("p90", [1.6] * 12), ("p95", lin(2.6, 3.2)),
      ("p99", [3.8] * 5 + [4.6, 5.5, 6.4, 7.3, 8.2, 9.0, 9.7])], None),
    ("⑤ 緩慢爬坡（Soak）", "負載不變，P95 隨時間緩慢上升",
     [("vus", [6.5] * 12), ("p95", [1.6, 1.7, 1.9, 2.1, 2.4, 2.8, 3.2, 3.7, 4.2, 4.8, 5.4, 6.0])], None),
    ("⑥ 週期鋸齒", "固定間隔出現延遲尖峰",
     [("vus", [6.5] * 12), ("p95", [1.6, 1.6, 7.0, 1.6, 1.6, 7.2, 1.6, 1.6, 7.0, 1.6, 1.6, 7.1])], None),
    ("⑦ 錯誤率階梯（Soak）", "負載不變，錯誤率一階一階往上跳",
     [("vus", [6.5] * 12), ("err", [0.2] * 4 + [2.2] * 3 + [4.2] * 3 + [6.2] * 2)], None),
    ("⑧ 吞吐下滑・連線層（Soak）", "RPS 下滑、P95 持平、blocked 上升",
     [("rps", lin(8.0, 3.4)), ("p95", [1.6] * 12), ("blocked", lin(0.4, 5.6))], None),
]


def main():
    fig, axes = plt.subplots(2, 4, figsize=(16, 7.8), dpi=150, facecolor=SURFACE)
    fig.subplots_adjust(left=0.02, right=0.955, top=0.80, bottom=0.05, wspace=0.28, hspace=0.5)
    fig.text(0.02, 0.96, "儀表板的 8 種經典曲線型態", fontsize=17, fontweight="bold", color=INK)
    fig.text(0.02, 0.918, "虛線＝負載軸（VUs / RPS），實線＝反應軸（延遲、錯誤率）；同一個指標在每一格都用同一個顏色",
             fontsize=11, color=INK_2)

    for ax, (title, sub, series, mark) in zip(axes.flat, PANELS):
        ax.set_facecolor(SURFACE)
        ax.set_title(title, loc="left", fontsize=13.5, fontweight="bold", color=INK, pad=22)
        ax.text(0, 1.035, sub, transform=ax.transAxes, fontsize=10, color=INK_2, va="bottom")
        ends = []
        for key, ys in series:
            label, color, dashed = M[key]
            ax.plot(X, ys, color=color, lw=1.6 if dashed else 2.4,
                    ls=(0, (4, 3)) if dashed else "-", solid_capstyle="round", zorder=3)
            ends.append([ys[-1], label, color, ys[-1]])
        # direct labels at the line ends, nudged apart so they never collide
        ends.sort(key=lambda e: e[0])
        for i in range(1, len(ends)):
            if ends[i][0] - ends[i - 1][0] < 0.85:
                ends[i][0] = ends[i - 1][0] + 0.85
        for y, label, color, y_end in ends:
            ax.text(11.3, y, label, fontsize=9.5, color=INK_2, va="center", ha="left", fontweight="bold")
            ax.plot([11], [y_end], marker="o", ms=4, color=color, zorder=4, clip_on=False)
        if mark:
            text, xm = mark
            ax.axvline(xm, color=MUTED, lw=1, ls=(0, (2, 2)), zorder=1)
            ax.text(xm + 0.2, 10.2, text, fontsize=9.5, color=INK_2, va="top")
        ax.set_xlim(0, 11)
        ax.set_ylim(0, 10.6)
        ax.set_yticks([])
        ax.set_xticks([])
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(BASELINE)
        ax.set_xlabel("時間 →", fontsize=9, color=MUTED, loc="right", labelpad=2)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, facecolor=SURFACE)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
