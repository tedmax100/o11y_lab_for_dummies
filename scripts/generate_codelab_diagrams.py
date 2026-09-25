#!/usr/bin/env python3
"""
Render the k6 codelab's former ASCII diagrams as figures:

    codelabs/tutorials/assets/images/k6-diagram-*.png

Flow / architecture diagrams are drawn as boxes and arrows with the same content as
the ASCII they replace; diagrams that were really data (tollbooth, RPS formula,
SharedArray memory, 14:02 crosshair) are drawn as charts. Shared light palette:
one blue accent for structure, status colours (with ✓ / × and a label) only for
pass / fail outcomes.
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "codelabs", "tutorials", "assets", "images")

for fam in ("Noto Sans CJK TC", "Noto Sans CJK HK", "Noto Sans CJK JP"):
    if any(f.name == fam for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = fam
        break
MONO = "Noto Sans Mono CJK TC"
if not any(f.name == MONO for f in font_manager.fontManager.ttflist):
    MONO = "monospace"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
BORDER = "#c3c2b7"
CARD = "#ffffff"
BLUE = "#2a78d6"
BLUE_DARK = "#1c5cab"
BLUE_TINT = "#e8f1fc"
ORANGE = "#eb6834"
GOOD = "#0ca30c"
GOOD_TEXT = "#006300"
GOOD_TINT = "#e9f6e9"
CRIT = "#d03b3b"
CRIT_TINT = "#fbeaea"


# ---------------------------------------------------------------------------
# drawing helpers (canvas in abstract units; 1 unit = 0.5 inch)
# ---------------------------------------------------------------------------
def canvas(w, h):
    fig = plt.figure(figsize=(w / 2, h / 2), dpi=150, facecolor=SURFACE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    ax.set_facecolor(SURFACE)
    return fig, ax


def box(ax, x, y, w, h, fc=CARD, ec=BORDER, lw=1.2, r=0.18):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, zorder=2))


def label(ax, x, y, text, size=11, color=INK, bold=False, ha="center", va="center", mono=False, ls=1.35):
    ax.text(x, y, text, fontsize=size, color=color, fontweight="bold" if bold else "normal",
            ha=ha, va=va, linespacing=ls, zorder=3, family=MONO if mono else None)


def arrow(ax, p0, p1, color=MUTED, lw=1.6, text=None, text_off=(0, 0.25), size=9.5, rad=0.0):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=14, color=color, lw=lw,
                                 connectionstyle=f"arc3,rad={rad}", zorder=1, shrinkA=0, shrinkB=0))
    if text:
        mx, my = (p0[0] + p1[0]) / 2 + text_off[0], (p0[1] + p1[1]) / 2 + text_off[1]
        ax.text(mx, my, text, fontsize=size, color=INK_2, ha="center", va="bottom", zorder=3)


def title(fig, text, sub=None, y=0.955):
    fig.text(0.02, y, text, fontsize=14, fontweight="bold", color=INK, va="top")
    if sub:
        fig.text(0.02, y - 0.075 * (4.5 / fig.get_size_inches()[1]) ** 0.7, sub, fontsize=10, color=INK_2, va="top")


def save(fig, name):
    out = os.path.join(IMG_DIR, f"k6-diagram-{name}.png")
    fig.savefig(out, facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {out}")


def chart_axes(ax):
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=MUTED, labelsize=9, length=0)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)


# ---------------------------------------------------------------------------
# 1. course roadmap
# ---------------------------------------------------------------------------
def roadmap():
    chapters = [
        ("Chapter 1", "核心哲學", ["Test as Code", "Goroutine 架構", "4 階段生命週期", "Group & Check", "http.url 防指標爆炸"]),
        ("Chapter 2", "流量建模", ["5 大流量模式", "協調性漏測", "開放模型 (Little's Law)", "SharedArray 記憶體優化", "dropped_iterations 告警"]),
        ("Chapter 3", "品質門禁", ["RED Method", "P95 / P99 尾端延遲", "4 大自訂指標", "Exit Code 99 卡關", "abortOnFail 熔斷"]),
        ("Chapter 4", "混合壓測", ["HAR 錄製轉譯", "401 死資料陷阱", "k6/browser Chromium", "99:1 全鏈路黃金架構", "Flight Pre-check"]),
        ("Chapter 5", "可觀測性閉環", ["原生 Web Dashboard", "HTML 靜態報告 (Port=-1)", "xk6 Docker 確定性編譯", "Prometheus Remote Write", "CPU CFS Throttling 對齊"]),
        ("Chapter 6", "AI Agent 工程", ["k6 x agent 雙引擎", "11 個 Bundled Skills", "原生 k6 x mcp 註冊", "Owner Tag 冪等性防護", "6 大編輯器全面支援"]),
    ]
    W, H = 34, 9.4
    fig, ax = canvas(W, H)
    cw, gap, x0 = 4.9, 0.72, 0.3
    for i, (ch, name, items) in enumerate(chapters):
        x = x0 + i * (cw + gap)
        box(ax, x, 0.3, cw, 6.6, fc=CARD)
        box(ax, x, 6.4, cw, 2.6, fc=BLUE, ec=BLUE)
        label(ax, x + cw / 2, 8.15, ch, size=10, color="#dbe8fa")
        label(ax, x + cw / 2, 7.3, name, size=13.5, color="#ffffff", bold=True)
        for j, it in enumerate(items):
            yy = 5.55 - j * 1.15
            ax.plot([x + 0.35], [yy], marker="o", ms=4, color=BLUE, zorder=3)
            label(ax, x + 0.65, yy, it, size=10, color=INK, ha="left")
        if i < len(chapters) - 1:
            arrow(ax, (x + cw + 0.08, 7.7), (x + cw + gap - 0.08, 7.7), color=BLUE_DARK, lw=1.8)
    save(fig, "course-roadmap")


# ---------------------------------------------------------------------------
# 2. k6 x agent bootstrap workflow
# ---------------------------------------------------------------------------
def agent_workflow():
    steps = ["專案代碼 / OpenAPI\n/ HAR 規格", "AI Agent\n自主解析", "生成全情境\n壓測腳本",
             "validate_script（1 VU 冒煙）\n＋ run_script", "自動自癒\n微調", "生產就緒\n測試套件"]
    W, H = 35.6, 4.2
    fig, ax = canvas(W, H)
    bw, gap = 4.7, 1.0
    widths = [bw, bw, bw, bw + 1.6, bw, bw]
    x = 0.3
    for i, s in enumerate(steps):
        w = widths[i]
        last = i == len(steps) - 1
        box(ax, x, 0.7, w, 2.8, fc=BLUE if last else CARD, ec=BLUE if last else BORDER)
        label(ax, x + w / 2, 2.1, s, size=11.5, color="#ffffff" if last else INK, bold=last)
        if not last:
            arrow(ax, (x + w + 0.1, 2.1), (x + w + gap - 0.1, 2.1), color=BLUE_DARK)
        x += w + gap
    save(fig, "agent-workflow")


# ---------------------------------------------------------------------------
# 3. options precedence
# ---------------------------------------------------------------------------
def options_precedence():
    levels = [("1. CLI Flags", "最高", "#1c5cab", "#ffffff"), ("2. Environment\nVariables", "", "#2a78d6", "#ffffff"),
              ("3. In-script\noptions", "", "#86b6ef", INK), ("4. Default Values", "最低", "#cde2fb", INK)]
    W, H = 30, 5.2
    fig, ax = canvas(W, H)
    bw, gap, x = 6.3, 1.3, 0.3
    for i, (name, tag, fc, tc) in enumerate(levels):
        box(ax, x, 0.6, bw, 2.8, fc=fc, ec=fc)
        label(ax, x + bw / 2, 2.0, name, size=12.5, color=tc, bold=True)
        if tag:
            label(ax, x + bw / 2, 3.9, f"優先權{tag}", size=10.5, color=INK_2, bold=True)
        if i < len(levels) - 1:
            arrow(ax, (x + bw + 0.12, 2.0), (x + bw + gap - 0.12, 2.0), color=BLUE_DARK, text="覆蓋", text_off=(0, 0.2))
        x += bw + gap
    save(fig, "options-precedence")


# ---------------------------------------------------------------------------
# 4. tollbooth analogy (closed vs open model) -- chart
# ---------------------------------------------------------------------------
def tollbooth():
    fig, (a, b) = plt.subplots(1, 2, figsize=(13, 4.4), dpi=150, facecolor=SURFACE, sharey=True,
                               gridspec_kw={"width_ratios": [1, 1.6]})
    fig.subplots_adjust(left=0.065, right=0.985, top=0.72, bottom=0.14, wspace=0.12)
    fig.text(0.02, 0.965, "收費站卡死 100 秒：閉環模型 vs 開放模型看到的延遲", fontsize=14, fontweight="bold", color=INK, va="top")
    fig.text(0.02, 0.885, "平常每秒抵達 1 輛車、每輛通過耗時 1 秒（平均延遲 1s、RPS = 1）。某一刻收費閘道卡死 100 秒：",
             fontsize=10, color=INK_2, va="top")
    for ax in (a, b):
        chart_axes(ax)
        ax.set_ylim(0, 115)
        ax.set_xlabel("第幾輛車（請求序號）", fontsize=9.5, color=MUTED)
    a.set_ylabel("等待時間（秒）", fontsize=9.5, color=MUTED)

    a.bar([1], [100], width=0.6, color=ORANGE)
    a.set_xlim(0, 6)
    a.set_xticks([1, 2, 3, 4, 5])
    a.set_title("A. 閉環模型（傳統 VU 迴圈）", loc="left", fontsize=12, fontweight="bold", color=INK, pad=10)
    a.text(1.6, 88, "工具必須等車 1 通過才送出車 2：\n故障 100 秒內只送出 1 個請求。\n報表：1 筆、延遲 100s、RPS ≈ 0\n→ 看起來只有 1 個人受影響",
           fontsize=9.5, color=INK_2, va="top")

    n = list(range(1, 101))
    b.bar(n, [101 - i for i in n], width=0.8, color=BLUE)
    b.set_xlim(0, 101)
    b.set_title("B. 開放模型（真實世界：車輛照常以固定頻率抵達）", loc="left", fontsize=12, fontweight="bold", color=INK, pad=10)
    b.text(42, 88, "100 個請求全部受害：\n車 1 等 100s、車 2 等 99s … 車 100 等 1s\n總等待 5,050 秒，平均延遲 50.5 秒",
           fontsize=9.5, color=INK_2, va="top")
    save(fig, "tollbooth")


# ---------------------------------------------------------------------------
# 5. closed-loop RPS formula -- chart
# ---------------------------------------------------------------------------
def rps_formula():
    import numpy as np
    fig, ax = plt.subplots(figsize=(11, 4.4), dpi=150, facecolor=SURFACE)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.74, bottom=0.14)
    chart_axes(ax)
    fig.text(0.02, 0.965, "閉環模型的吞吐量：RPS ＝ VUs ÷（回應時間 ＋ sleep）", fontsize=14, fontweight="bold", color=INK, va="top")
    fig.text(0.02, 0.885, "固定 10 個 VU、sleep = 0：後端越慢，工具送出的請求就越少——等於自動替故障中的系統「放水」",
             fontsize=10, color=INK_2, va="top")
    x = np.logspace(np.log10(0.04), np.log10(6), 300)
    ax.plot(x, 10 / x, color=BLUE, lw=2.2)
    ax.set_xscale("log")
    ax.set_xlim(0.04, 6)
    ax.set_ylim(0, 260)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}s"))
    ax.set_xticks([0.05, 0.1, 0.5, 1, 5])
    ax.set_xlabel("回應時間（對數刻度）", fontsize=9.5, color=MUTED)
    ax.set_ylabel("RPS（10 VUs）", fontsize=9.5, color=MUTED)
    for (px_, py_, t, dx, dy) in ((0.05, 200, "正常：50ms → 10 ÷ 0.05 = 200 RPS", 0.09, 225),
                                  (5, 2, "故障：5s → 10 ÷ 5 = 2 RPS", 1.1, 70)):
        ax.plot([px_], [py_], marker="o", ms=8, color=BLUE, mec=SURFACE, mew=2, zorder=4)
        ax.annotate(t, xy=(px_, py_), xytext=(dx, dy), fontsize=10, color=INK, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=MUTED, lw=1))
    save(fig, "closed-loop-rps")


# ---------------------------------------------------------------------------
# 6. why dropped_iterations happens
# ---------------------------------------------------------------------------
def dropped_mechanism():
    W, H = 30, 3.9
    fig, ax = canvas(W, H)
    steps = [
        ("排程器：時間到！\n該發送第 501 個迭代", CARD, BORDER, INK, 8.2),
        ("檢查 VU 池\npreAllocatedVUs 已用完\nmaxVUs 50 / 50 全部卡在等待後端 DB 回應", CARD, BORDER, INK, 10.0),
        ("× 沒有可用 VU\n被迫丟棄這次迭代\ndropped_iterations ＋1", CRIT_TINT, CRIT, INK, 8.2),
    ]
    x, gap = 0.3, 1.4
    for i, (t, fc, ec, tc, w) in enumerate(steps):
        box(ax, x, 0.35, w, 3.2, fc=fc, ec=ec, lw=1.6 if ec == CRIT else 1.2)
        label(ax, x + w / 2, 1.95, t, size=11.5, color=tc, bold=(i == 2))
        if i < len(steps) - 1:
            arrow(ax, (x + w + 0.12, 1.95), (x + w + gap - 0.12, 1.95), color=BLUE_DARK)
        x += w + gap
    save(fig, "dropped-iterations-mechanism")


# ---------------------------------------------------------------------------
# 7. dropped_iterations two-branch diagnosis
# ---------------------------------------------------------------------------
def dropped_tree():
    W, H = 30, 11.2
    fig, ax = canvas(W, H)
    box(ax, 10.5, 8.9, 9, 1.9, fc=BLUE, ec=BLUE)
    label(ax, 15, 9.85, "dropped_iterations > 0", size=14, color="#ffffff", bold=True, mono=True)
    branches = [
        (0.4, "分支 A：受測後端崩潰", "http_req_duration 暴增",
         [("特徵", "http_req_duration 延遲暴增、\n504 Gateway Timeout 或連線重置"),
          ("根因", "後端 CPU / DB 飽和、連線堆積；\nVU 耗盡是後端故障引發的連鎖反應"),
          ("解法", "優化後端瓶頸、加大 DB 連線池")]),
        (15.6, "分支 B：壓測機資源配置失衡", "後端延遲正常（< 50ms）",
         [("特徵", "後端延遲完全正常，\n但 dropped_iterations 仍然增加"),
          ("根因", "maxVUs 設太小，撐不起目標 RPS；\n或壓測主機 CPU 100% / 記憶體耗盡"),
          ("解法", "依 Little's Law 調高 maxVUs；\n檢查壓測機資源")]),
    ]
    for x, head, cond, rows in branches:
        cw = 14.0
        left = x < 10
        arrow(ax, (12.5 if left else 17.5, 8.8), (x + cw / 2, 7.65), color=BLUE_DARK, rad=0.0)
        label(ax, x + cw / 2 + (0.3 if left else -0.3), 8.35, cond, size=10, color=INK_2, bold=True,
              ha="right" if left else "left")
        box(ax, x, 0.3, cw, 7.2)
        label(ax, x + 0.5, 6.75, head, size=13, bold=True, ha="left")
        y = 5.75
        for k, v in rows:
            label(ax, x + 0.5, y, k, size=10, color=BLUE_DARK, bold=True, ha="left", va="top")
            label(ax, x + 1.9, y, v, size=11, color=INK, ha="left", va="top")
            y -= 1.8
    save(fig, "dropped-iterations-diagnosis")


# ---------------------------------------------------------------------------
# 8. SharedArray memory -- chart
# ---------------------------------------------------------------------------
def shared_array():
    import numpy as np
    vus = ["100 VU", "1,000 VU", "5,000 VU", "10,000 VU"]
    trad = [5, 50, 250, 500]            # GB (50 MB × VUs)
    shared = [0.060, 0.065, 0.080, 0.100]  # GB
    fig, ax = plt.subplots(figsize=(11, 4.6), dpi=150, facecolor=SURFACE)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.7, bottom=0.12)
    chart_axes(ax)
    fig.text(0.02, 0.965, "載入 50 MB 測試資料：傳統 Array vs SharedArray 的總記憶體", fontsize=14, fontweight="bold", color=INK, va="top")
    fig.text(0.02, 0.885, "傳統 Array：每個 VU 都在自己的 JS Heap 深拷貝一份 → 50 MB × VU 數；SharedArray：全部 VU 共用一份唯讀資料（對數刻度）",
             fontsize=10, color=INK_2, va="top")
    x = np.arange(len(vus))
    w = 0.36
    b1 = ax.bar(x - w / 2 - 0.01, trad, w, color=ORANGE)
    b2 = ax.bar(x + w / 2 + 0.01, shared, w, color=BLUE)
    ax.set_yscale("log")
    ax.set_ylim(0.02, 3000)
    ax.set_xticks(x, vus)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g} GB" if v >= 1 else f"{v * 1000:g} MB"))
    ax.tick_params(axis="x", colors=INK_2, labelsize=10.5)
    for bar, v in zip(b1, trad):
        ax.text(bar.get_x() + bar.get_width() / 2, v * 1.25, f"{v} GB", ha="center", va="bottom", fontsize=9.5, color=INK_2)
    for bar, v in zip(b2, shared):
        ax.text(bar.get_x() + bar.get_width() / 2, v * 1.25, f"~{v * 1000:.0f} MB", ha="center", va="bottom", fontsize=9.5, color=INK_2)
    from matplotlib.ticker import NullLocator
    ax.yaxis.set_minor_locator(NullLocator())
    ax.legend([b1, b2], ["傳統 Array（每個 VU 各拷貝一份）", "SharedArray（全部 VU 共用一份）"],
              loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, frameon=False, fontsize=10, labelcolor=INK_2)
    save(fig, "sharedarray-memory")


# ---------------------------------------------------------------------------
# 9. exit code chain
# ---------------------------------------------------------------------------
def exit_code():
    W, H = 30, 7.2
    fig, ax = canvas(W, H)
    box(ax, 0.3, 2.5, 6.4, 2.2, fc=BLUE, ec=BLUE)
    label(ax, 3.5, 3.6, "k6 測試執行結束", size=13, color="#ffffff", bold=True)
    outcomes = [
        (4.5, "所有 Thresholds 門檻全數通過", "✓  Exit Code 0", "CI 通過，允許上線", GOOD_TINT, GOOD, GOOD_TEXT),
        (0.4, "任何一條 Threshold 門檻違規", "×  Exit Code 99", "CI 失敗，自動阻斷部署", CRIT_TINT, CRIT, CRIT),
    ]
    for y, cond, code, meaning, fc, ec, tc in outcomes:
        arrow(ax, (6.8, 3.6), (11.9, y + 1.1), color=MUTED, rad=0.0)
        box(ax, 12.0, y, 17.7, 2.2, fc=fc, ec=ec, lw=1.6)
        label(ax, 12.6, y + 1.55, cond, size=10.5, color=INK_2, bold=True, ha="left")
        label(ax, 12.6, y + 0.7, code, size=15, color=tc, bold=True, ha="left", mono=True)
        label(ax, 20.6, y + 0.7, meaning, size=12, color=INK, ha="left")
    save(fig, "exit-code-chain")


# ---------------------------------------------------------------------------
# 10. 99:1 hybrid architecture
# ---------------------------------------------------------------------------
def hybrid():
    W, H = 30, 7.0
    fig, ax = canvas(W, H)
    box(ax, 0.3, 2.3, 6.6, 2.4, fc=BLUE, ec=BLUE)
    label(ax, 3.6, 3.5, "全鏈路混合壓測\nHybrid Script", size=12.5, color="#ffffff", bold=True)
    rows = [
        (4.3, "99% Protocol Load", "1000 VU・輕量 HTTP 協定", "後端 API 與資料庫打到滿載"),
        (0.4, "1% Browser Probe", "1 VU・真實 Chromium", "即時採集風暴下的 LCP / CLS"),
    ]
    for y, head, sub, target in rows:
        arrow(ax, (7.0, 3.5), (9.9, y + 1.15), color=BLUE_DARK)
        box(ax, 10.0, y, 8.6, 2.3)
        label(ax, 10.5, y + 1.5, head, size=12.5, bold=True, ha="left")
        label(ax, 10.5, y + 0.65, sub, size=10.5, color=INK_2, ha="left")
        arrow(ax, (18.7, y + 1.15), (20.9, y + 1.15), color=BLUE_DARK)
        box(ax, 21.0, y, 8.7, 2.3, fc=BLUE_TINT, ec=BLUE_TINT)
        label(ax, 25.35, y + 1.15, target, size=11.5, color=INK)
    save(fig, "hybrid-99-1")


# ---------------------------------------------------------------------------
# 11. Grafana unified observability hub
# ---------------------------------------------------------------------------
def grafana_hub():
    W, H = 32, 12
    fig, ax = canvas(W, H)
    box(ax, 9.5, 9.6, 13, 2.1, fc=BLUE, ec=BLUE)
    label(ax, 16, 10.95, "Grafana 統一可觀測性監控中心", size=14, color="#ffffff", bold=True)
    label(ax, 16, 10.15, "Unified Observability Hub", size=10.5, color="#dbe8fa")
    cols = [
        ("應用層分散式追蹤", "OpenTelemetry Collector", ["Trace ID / Span 鏈路耗時", "Database SQL 慢查詢", "跨微服務下游 RPC 呼叫"]),
        ("系統基礎設施時序", "Prometheus（cAdvisor / Node）", ["Pod CPU CFS Throttling 限流", "記憶體 WorkingSet / OOMKilled", "網路連線池 Socket 佔用"]),
        ("k6 壓測客戶端時序", "Prometheus Remote Write", ["http_req_duration（P95 / P99）", "即時吞吐量（RPS）", "dropped_iterations 容量告警"]),
    ]
    cw, gap, x0 = 9.9, 0.75, 0.3
    ax.text(16, 8.45, "時間軸同步・共享十字準星", fontsize=10.5, color=INK_2, fontweight="bold", ha="center", va="center",
            zorder=4, bbox=dict(boxstyle="round,pad=0.35", fc=SURFACE, ec="none"))
    for i, (head, src, items) in enumerate(cols):
        x = x0 + i * (cw + gap)
        arrow(ax, (16, 9.5), (x + cw / 2, 7.25), color=BLUE_DARK)
        box(ax, x, 0.3, cw, 6.85)
        label(ax, x + 0.5, 6.25, head, size=13, bold=True, ha="left")
        label(ax, x + 0.5, 5.35, src, size=10.5, color=BLUE_DARK, bold=True, ha="left")
        for j, it in enumerate(items):
            yy = 4.0 - j * 1.3
            ax.plot([x + 0.65], [yy], marker="o", ms=4, color=BLUE, zorder=3)
            label(ax, x + 0.95, yy, it, size=10.5, ha="left")
    save(fig, "grafana-unified-hub")


# ---------------------------------------------------------------------------
# 12. xk6 Go-to-JS bridge
# ---------------------------------------------------------------------------
def xk6_bridge():
    W, H = 30, 13.2
    fig, ax = canvas(W, H)
    x, w = 0.3, 19
    box(ax, x, 9.6, w, 3.3)
    label(ax, x + 0.5, 12.25, "壓測工程師編寫的 JavaScript 腳本", size=12, bold=True, ha="left")
    label(ax, x + 0.5, 10.75, "import sql from 'k6/x/sql';\nsql.query(\"SELECT * FROM users WHERE id = ?\", 101);",
          size=10.5, color=BLUE_DARK, ha="left", mono=True)
    arrow(ax, (x + w / 2, 9.5), (x + w / 2, 7.85), color=BLUE_DARK)
    label(ax, x + w / 2 + 0.4, 8.7, "Goja JS Runtime", size=10, color=INK_2, ha="left")
    box(ax, x, 5.4, w, 2.35, fc=BLUE_TINT, ec=BLUE_TINT)
    label(ax, x + w / 2, 6.575, "Go-to-JS Bridge 模組橋接層（Type Reflection）", size=12, bold=True)
    arrow(ax, (x + w / 2, 5.3), (x + w / 2, 3.65), color=BLUE_DARK)
    label(ax, x + w / 2 + 0.4, 4.5, "Go Native Code", size=10, color=INK_2, ha="left")
    box(ax, x, 0.3, w, 3.25, fc=BLUE, ec=BLUE)
    label(ax, x + w / 2, 1.925, "Go 原生驅動程式\ndatabase/sql・lib/pq・pgx", size=12, color="#ffffff", bold=True)
    arrow(ax, (x + w + 0.12, 1.925), (21.4, 1.925), color=BLUE_DARK)
    box(ax, 21.5, 0.3, 8.2, 3.25)
    label(ax, 25.6, 1.925, "直接壓測\nPostgreSQL / MySQL", size=12, bold=True)
    save(fig, "xk6-bridge")


# ---------------------------------------------------------------------------
# 13. 14:02 crosshair convergence -- chart
# ---------------------------------------------------------------------------
def crosshair():
    import numpy as np
    rng = np.random.default_rng(7)
    t = np.arange(0, 481, 5)              # seconds from 13:58:00
    event = 240                           # 14:02:00
    p95 = np.where(t < event, 45 + rng.normal(0, 3, t.size), 2200 + rng.normal(0, 60, t.size))
    cfs = np.where(t < event, 6 + rng.normal(0, 1.2, t.size), 85 + rng.normal(0, 2.5, t.size))
    fig, (a, b) = plt.subplots(2, 1, figsize=(11, 5.4), dpi=150, facecolor=SURFACE, sharex=True)
    fig.subplots_adjust(left=0.1, right=0.97, top=0.8, bottom=0.1, hspace=0.45)
    fig.text(0.02, 0.975, "共享十字準星：同一秒，兩張圖一起破案", fontsize=14, fontweight="bold", color=INK, va="top")
    fig.text(0.02, 0.91, "示意數據。上：k6 推到 Prometheus 的 API P95；下：同一服務 Pod 的 CPU CFS Throttling。",
             fontsize=10, color=INK_2, va="top")
    for ax, y, color, ttl, fmt, top in ((a, p95, BLUE, "k6：API P95 延遲", "{:g} ms", 2600),
                                         (b, cfs, ORANGE, "K8s：Pod CPU CFS Throttling 比率", "{:g}%", 100)):
        chart_axes(ax)
        ax.plot(t, y, color=color, lw=2)
        ax.set_ylim(0, top)
        ax.set_title(ttl, loc="left", fontsize=11.5, fontweight="bold", color=INK, pad=6)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _, f=fmt: f.format(v)))
        ax.axvline(event, color=INK_2, lw=1.2, ls=(0, (3, 2)), zorder=1)
    a.annotate("45ms → 2,200ms", xy=(event + 5, 2150), xytext=(event + 40, 1400), fontsize=10, color=INK, fontweight="bold",
               arrowprops=dict(arrowstyle="->", color=MUTED, lw=1))
    b.annotate("同一秒飆到 85%", xy=(event + 5, 84), xytext=(event + 40, 45), fontsize=10, color=INK, fontweight="bold",
               arrowprops=dict(arrowstyle="->", color=MUTED, lw=1))
    a.text(event - 4, 2450, "14:02:00", ha="right", va="center", fontsize=10, color=INK_2, fontweight="bold")
    b.set_xticks(range(0, 481, 60))
    b.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{13 + (58 + int(v) // 60) // 60}:{(58 + int(v) // 60) % 60:02d}"))
    save(fig, "crosshair-1402")


def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    for fn in (roadmap, agent_workflow, options_precedence, tollbooth, rps_formula, dropped_mechanism,
               dropped_tree, shared_array, exit_code, hybrid, grafana_hub, xk6_bridge, crosshair):
        fn()


if __name__ == "__main__":
    main()
