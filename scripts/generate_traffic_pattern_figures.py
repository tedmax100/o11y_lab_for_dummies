#!/usr/bin/env python3
"""
Render the Chapter 2 traffic-pattern figures for the k6 codelab, plotted from the
exact `stages` arrays shown next to each figure (k6 ramps linearly between stages):

    codelabs/tutorials/assets/images/k6-ch2-load-pattern.png
    codelabs/tutorials/assets/images/k6-ch2-stress-pattern.png
    codelabs/tutorials/assets/images/k6-ch2-spike-pattern.png

If you change a `stages` example in the codelab, update STAGES here and re-run.
Single series per chart, so no legend: the title names it and phases are labelled
directly on the plot.
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.ticker import FuncFormatter, MultipleLocator  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "codelabs", "tutorials", "assets", "images")

for fam in ("Noto Sans CJK TC", "Noto Sans CJK HK", "Noto Sans CJK JP"):
    if any(f.name == fam for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam
        break

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
LINE = "#2a78d6"
FILL = "#cde2fb"

# (duration seconds, target VUs) -- mirrors the codelab examples
STAGES = {
    "load": [(180, 50), (600, 50), (180, 0)],
    "stress": [(120, 50), (180, 50), (120, 100), (180, 100), (120, 200), (180, 200),
               (120, 300), (180, 300), (180, 0)],
    "spike": [(30, 10), (10, 200), (60, 200), (10, 10), (120, 10), (10, 0)],
}


def points(stages):
    t, v = [0], [0]
    for dur, target in stages:
        t.append(t[-1] + dur)
        v.append(target)
    return t, v


def base_axes(title, subtitle, xmax, ymax, x_step, fmt):
    fig, ax = plt.subplots(figsize=(10, 3.6), dpi=150, facecolor=SURFACE)
    fig.subplots_adjust(left=0.075, right=0.98, top=0.78, bottom=0.16)
    ax.set_facecolor(SURFACE)
    fig.text(0.075, 0.93, title, fontsize=13.5, fontweight="bold", color=INK)
    fig.text(0.075, 0.855, subtitle, fontsize=10, color=INK_2)
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.xaxis.set_major_locator(MultipleLocator(x_step))
    ax.xaxis.set_major_formatter(FuncFormatter(fmt))
    ax.tick_params(colors=MUTED, labelsize=9, length=0)
    ax.grid(axis="y", color=GRID, lw=0.8)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.set_ylabel("VUs", color=MUTED, fontsize=9.5)
    return fig, ax


def draw(ax, t, v):
    ax.fill_between(t, v, color=FILL, lw=0, zorder=1)
    ax.plot(t, v, color=LINE, lw=2.2, solid_joinstyle="round", zorder=3)


def phase(ax, x0, x1, y, text, color=INK_2):
    ax.annotate("", xy=(x0, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1, shrinkA=0, shrinkB=0))
    ax.text((x0 + x1) / 2, y + 0.02 * ax.get_ylim()[1] + 1, text, ha="center", va="bottom", fontsize=9.5, color=color)


def save(fig, name):
    out = os.path.join(IMG_DIR, name)
    fig.savefig(out, facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {out}")


def minutes(x, _):
    return f"{int(x // 60)}m"


def mmss(x, _):
    return f"{int(x // 60)}:{int(x % 60):02d}"


def load():
    t, v = points(STAGES["load"])
    fig, ax = base_axes("Load Test 流量波形：爬坡 → 高原穩態 → 降載",
                        "stages：3m 爬升至 50 VUs → 維持 10m → 3m 降至 0（共 16 分鐘）",
                        t[-1], 70, 120, minutes)
    draw(ax, t, v)
    phase(ax, 0, 180, 57, "爬坡 Ramp-up")
    phase(ax, 180, 780, 57, "高原穩態 Plateau：觀察資源是否穩定")
    phase(ax, 780, 960, 57, "降載 Ramp-down")
    save(fig, "k6-ch2-load-pattern.png")


def stress():
    t, v = points(STAGES["stress"])
    fig, ax = base_axes("Stress Test 流量波形：階梯加壓，尋找拐點",
                        "stages：每階 2m 爬升＋3m 維持，50 → 100 → 200 → 300 VUs，最後 3m 冷卻（共 23 分鐘）",
                        t[-1], 360, 180, minutes)
    draw(ax, t, v)
    for (x_mid, level) in ((210, 50), (510, 100), (810, 200), (1110, 300)):
        ax.text(x_mid, level + 10, f"{level} VUs", ha="center", va="bottom", fontsize=9.5, color=INK_2, fontweight="bold")
    ax.annotate("每一階都觀察：RPS 是否還跟著 VUs 上升？\nP95 與錯誤率何時開始抬頭？",
                xy=(1020, 300), xytext=(300, 250), fontsize=9.5, color=INK_2, va="center",
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1))
    save(fig, "k6-ch2-stress-pattern.png")


def spike():
    t, v = points(STAGES["spike"])
    fig, ax = base_axes("Spike Test 流量波形：瞬間暴衝 → 急降 → 自癒觀察",
                        "stages：基準 10 VUs → 10 秒內暴增至 200 VUs（20 倍）→ 維持 1m → 10 秒急降 → 觀察 2m",
                        t[-1], 240, 30, mmss)
    draw(ax, t, v)
    ax.annotate("10 秒內暴增 20 倍", xy=(35, 110), xytext=(55, 175), fontsize=9.5, color=INK_2,
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1))
    phase(ax, 40, 100, 212, "高壓衝擊 1m")
    phase(ax, 110, 230, 45, "自癒觀察期 Recovery：延遲與錯誤率能否回到基準？")
    save(fig, "k6-ch2-spike-pattern.png")


def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    load()
    stress()
    spike()


if __name__ == "__main__":
    main()
