#!/usr/bin/env python3
"""
Insert "how to read the results" slides into the Ch3 and Ch5 k6 decks,
built entirely from native PowerPoint shapes, text boxes and line charts
(no full-slide PNGs):

Ch3_k6_Quality_Gates.pptx  (inserted after Slide 4 "Built-in Metrics")
  - 看懂 k6 結尾摘要：5 步驟判讀 SOP
  - 延遲拆解：http_req_duration 只算後 3 段

Ch5_k6_Observability_and_Modular_Architecture.pptx
  (inserted after Slide 7 "Prometheus Remote Write", before the crosshair slide)
  - 看懂儀表板：8 種經典曲線型態
  - Soak 判讀：趨勢比門檻重要
  - 儀表板判讀 4 步驟 SOP

Idempotent: a deck that already contains the marker shape is skipped.
"""
import copy
import os
import sys

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLIDES_DIR = os.environ.get("K6_SLIDES_DIR", os.path.join(ROOT, "k6", "slides"))
CH3 = os.path.join(SLIDES_DIR, "Ch3_k6_Quality_Gates.pptx")
CH5 = os.path.join(SLIDES_DIR, "Ch5_k6_Observability_and_Modular_Architecture.pptx")
FIGURE = os.path.join(ROOT, "k6", "slides", "assets", "Ch5", "curve_patterns.png")  # generate_curve_patterns_figure.py

MARKER = "MetricReading_Marker"
CODELAB_URL = "https://tedmax100.github.io/o11y_lab_for_dummies/k6-performance-testing/"

FONT = "Noto Sans CJK TC"
MONO = "Noto Sans Mono CJK TC"

# Slide canvas is 16256000 x 9144000 EMU; lay out on a 1376 x 768 px grid
# to match the other generator scripts.
EMU_X = 16256000 / 1376
EMU_Y = 9144000 / 768


def px(x, y, w, h):
    return Emu(int(x * EMU_X)), Emu(int(y * EMU_Y)), Emu(int(w * EMU_X)), Emu(int(h * EMU_Y))


def rgb(hex_):
    return RGBColor.from_string(hex_)


# ---------------------------------------------------------------------------
# Shape helpers
# ---------------------------------------------------------------------------
def add_box(slide, x, y, w, h, fill=None, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06, line_w=1.0):
    shp = slide.shapes.add_shape(shape, *px(x, y, w, h))
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        shp.adjustments[0] = radius
    if fill:
        shp.fill.solid()
        shp.fill.fore_color.rgb = rgb(fill)
    else:
        shp.fill.background()
    if line:
        shp.line.color.rgb = rgb(line)
        shp.line.width = Pt(line_w)
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def fill_text(tf, paras, anchor=MSO_ANCHOR.TOP, margin=(0, 0, 0, 0), align=PP_ALIGN.LEFT, space_after=0, line_spacing=None):
    """paras: list of paragraphs; each paragraph is a list of (text, style) runs."""
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left, tf.margin_top, tf.margin_right, tf.margin_bottom = (Emu(int(m * EMU_X)) for m in margin)
    for i, runs in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if space_after:
            p.space_after = Pt(space_after)
        if line_spacing:
            p.line_spacing = line_spacing
        for text, st in runs:
            r = p.add_run()
            r.text = text
            f = r.font
            f.size = Pt(st.get("size", 14))
            f.bold = st.get("bold", False)
            f.color.rgb = rgb(st.get("color", "000000"))
            f.name = st.get("font", FONT)
            # East-Asian glyphs need the ea typeface set explicitly.
            rpr = r._r.get_or_add_rPr()
            for tag in ("a:ea",):
                el = rpr.find(qn(tag))
                if el is None:
                    el = rpr.makeelement(qn(tag), {})
                    rpr.append(el)
                el.set("typeface", st.get("font", FONT))


def add_text(slide, x, y, w, h, paras, **kw):
    tb = slide.shapes.add_textbox(*px(x, y, w, h))
    fill_text(tb.text_frame, paras, **kw)
    return tb


def add_card_text(shape, paras, **kw):
    fill_text(shape.text_frame, paras, **kw)


def S(size, color, bold=False, font=FONT):
    return {"size": size, "color": color, "bold": bold, "font": font}


# ---------------------------------------------------------------------------
# Deck plumbing
# ---------------------------------------------------------------------------
def blank_layout(prs):
    for layout in prs.slide_layouts:
        if layout.name == "Blank":
            return layout
    return prs.slide_layouts[6]


def move_slide(prs, slide, new_index):
    sld_id_lst = prs.slides._sldIdLst
    for sld_id in sld_id_lst:
        if prs.slides.part.related_part(sld_id.rId) is slide.part:
            sld_id_lst.remove(sld_id)
            sld_id_lst.insert(new_index, sld_id)
            return
    raise RuntimeError("slide not found in sldIdLst")


def copy_badge(prs, slide):
    """Clone the clickable Codelabs badge used on every existing slide."""
    for src in prs.slides:
        for shp in src.shapes:
            if shp.name == "Codelabs_Link_Badge":
                el = copy.deepcopy(shp._element)
                rid = slide.part.relate_to(CODELAB_URL, RT.HYPERLINK, is_external=True)
                for h in el.iter(qn("a:hlinkClick")):
                    h.set(qn("r:id"), rid)
                slide.shapes._spTree.append(el)
                return
    raise RuntimeError("Codelabs_Link_Badge not found")


def add_marker(slide):
    tb = slide.shapes.add_textbox(0, 0, Emu(1), Emu(1))
    tb.name = MARKER


def has_marker(prs):
    return any(shp.name == MARKER for s in prs.slides for shp in s.shapes)


# ---------------------------------------------------------------------------
# Ch3 (light theme, matches the Gemini-rendered Ch3 image slides)
# ---------------------------------------------------------------------------
L_BG = "F8FAFC"
L_TITLE = "0F172A"
L_BODY = "334155"
L_MUTED = "64748B"
L_BORDER = "E2E8F0"
L_ACCENT = "4F46E5"
L_ACCENT_BG = "EEF2FF"
L_ACCENT_BORDER = "C7D2FE"
T_BG = "0F172A"
T_TEXT = "E2E8F0"
T_DIM = "94A3B8"
T_RED = "F87171"
T_GREEN = "4ADE80"
T_AMBER = "FBBF24"
T_CYAN = "38BDF8"


def light_header(slide, title, subtitle):
    add_box(slide, 0, 0, 1376, 768, fill=L_BG, shape=MSO_SHAPE.RECTANGLE)
    add_text(slide, 60, 28, 1256, 56, [[(title, S(30, L_TITLE, True))]], anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, 60, 84, 1256, 30, [[(subtitle, S(15, L_MUTED))]], anchor=MSO_ANCHOR.MIDDLE)


def ch3_summary_sop(prs):
    s = prs.slides.add_slide(blank_layout(prs))
    light_header(s, "看懂 k6 結尾摘要：5 步驟判讀 SOP",
                 "不要從第一行讀到最後一行，要帶著問題、依固定順序讀（範例：constant-arrival-rate 目標 50 RPS × 60 秒）")

    # --- left: annotated terminal summary ---
    term = add_box(s, 60, 132, 640, 530, fill=T_BG, line="334155", radius=0.03)
    D, W, R, G, A, C = T_DIM, T_TEXT, T_RED, T_GREEN, T_AMBER, T_CYAN
    m = lambda n: ("  ◀" + n, S(14, A, True, MONO))
    lines = [
        [("█ THRESHOLDS", S(14, W, True, MONO))],
        [("  http_req_duration", S(14, D, font=MONO))],
        [("  ✗ 'p(95)<500' p(95)=812.4ms", S(14, R, True, MONO)), m("①")],
        [("  http_req_failed", S(14, D, font=MONO))],
        [("  ✓ 'rate<0.01' rate=0.84%", S(14, G, font=MONO))],
        [(" ", S(6, D, font=MONO))],
        [("█ TOTAL RESULTS", S(14, W, True, MONO))],
        [("  checks_succeeded: 99.58% 5895/5920", S(14, W, font=MONO)), m("②")],
        [("  ✗ status is 200  ↳ ✓ 2935 / ✗ 25", S(14, R, font=MONO))],
        [("  HTTP", S(14, C, True, MONO))],
        [("  http_req_duration: med=98ms", S(14, W, font=MONO)), m("③")],
        [("     avg=231ms p(95)=812ms max=4.21s", S(14, W, font=MONO))],
        [("  http_req_failed..: 0.84% 25/2960", S(14, W, font=MONO))],
        [("  http_reqs........: 2960  49.3/s", S(14, W, font=MONO))],
        [("  EXECUTION", S(14, C, True, MONO))],
        [("  dropped_iterations: 37", S(14, R, True, MONO)), m("④")],
        [("  vus..............: min=1 max=60", S(14, W, font=MONO))],
        [("  vus_max..........: 60", S(14, W, font=MONO))],
        [("  NETWORK", S(14, C, True, MONO))],
        [("  data_received....: 38 MB 630 kB/s", S(14, W, font=MONO)), m("⑤")],
    ]
    add_card_text(term, lines, anchor=MSO_ANCHOR.MIDDLE, margin=(24, 12, 16, 12), line_spacing=1.12)

    # --- right: 5 step cards ---
    steps = [
        ("THRESHOLDS：判決書", "過關了沒？只要一個 ✗ → Exit Code 99。先記下違規的指標與統計量。"),
        ("checks：功能正確性", "哪條斷言失敗？check 是軟斷言，不會擋 CI → 要加 checks 門檻。"),
        ("HTTP：分佈形狀", "p(95) ÷ med > 3 倍＝長尾；整體比 expected_response 還快＝錯誤在「快速失敗」。"),
        ("EXECUTION：壓測有效嗎", "dropped_iterations > 0 或 vus 碰到 vus_max → 目標流量沒打滿，結論作廢。"),
        ("NETWORK：頻寬與 Payload", "data_received ÷ 請求數＝回應大小；逼近網卡上限＝瓶頸在壓測機。"),
    ]
    y = 132
    for i, (title, desc) in enumerate(steps):
        card = add_box(s, 724, y, 592, 96, fill="FFFFFF", line=L_BORDER, radius=0.1)
        circ = add_box(s, 740, y + 26, 44, 44, fill=L_ACCENT, shape=MSO_SHAPE.OVAL)
        add_card_text(circ, [[("①②③④⑤"[i], S(18, "FFFFFF", True))]], anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
        add_text(s, 800, y + 8, 504, 82, [
            [(title, S(17, L_TITLE, True))],
            [(desc, S(13.5, L_BODY))],
        ], anchor=MSO_ANCHOR.MIDDLE, space_after=2)
        y += 96 + 12  # 5 cards: 132 → 664

    # --- bottom: conclusion callout ---
    concl = add_box(s, 60, 680, 1256, 50, fill=L_ACCENT_BG, line=L_ACCENT_BORDER, radius=0.2)
    add_card_text(concl, [[
        ("本例結論  ", S(14, L_ACCENT, True)),
        ("P95 違規 ① ＋ med→p(95) 差 8 倍長尾 ③ ＋ 丟 37 次迭代、VU 池見底 ④ → 後端約 50 RPS 已飽和，下一步去儀表板找拐點", S(13.5, L_TITLE)),
    ]], anchor=MSO_ANCHOR.MIDDLE, margin=(20, 0, 20, 0))

    copy_badge(prs, s)
    add_marker(s)
    s.notes_slide.notes_text_frame.text = (
        "結尾摘要 5 步驟：① THRESHOLDS 判決 ② checks 正確性 ③ HTTP 分佈形狀 ④ EXECUTION 壓測有效性 ⑤ NETWORK 頻寬。"
        "範例：P95 違規、8 倍長尾、dropped_iterations=37、vus 碰到 vus_max → 後端在約 50 RPS 飽和。")
    return s


def ch3_latency_breakdown(prs):
    s = prs.slides.add_slide(blank_layout(prs))
    light_header(s, "延遲拆解：http_req_duration 只算後 3 段",
                 "blocked / connecting / tls_handshaking 不計入 duration，只盯 duration 的話，連線層問題會完全隱形")

    # bracket labels over the timeline
    seg_w, gap, x0 = 202, 8.8, 60
    left_w = seg_w * 3 + gap * 2
    lab_l = add_box(s, x0, 134, left_w, 36, fill="F1F5F9", line="CBD5E1", radius=0.25)
    add_card_text(lab_l, [[("連線準備階段：不計入 duration，只拉長 iteration_duration", S(13, L_MUTED, True))]],
                  anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
    lab_r = add_box(s, x0 + left_w + gap, 134, left_w, 36, fill=L_ACCENT_BG, line=L_ACCENT_BORDER, radius=0.25)
    add_card_text(lab_r, [[("http_req_duration = sending + waiting + receiving", S(13.5, L_ACCENT, True, MONO))]],
                  anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)

    segs = [
        ("blocked", "等待可用連線槽位（含 DNS）", False),
        ("connecting", "TCP 三向握手", False),
        ("tls_handshaking", "TLS 憑證協商", False),
        ("sending", "送出請求封包", True),
        ("waiting (TTFB)", "伺服器處理運算", True),
        ("receiving", "下載回應內容", True),
    ]
    for i, (name, desc, counted) in enumerate(segs):
        x = x0 + i * (seg_w + gap)
        fill = ("6366F1" if name.startswith("waiting") else "818CF8") if counted else "E2E8F0"
        fg = "FFFFFF" if counted else L_BODY
        box = add_box(s, x, 180, seg_w, 76, fill=fill, radius=0.08)
        add_card_text(box, [
            [(name, S(14, fg, True, MONO))],
            [(desc, S(12, fg))],
        ], anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER, margin=(6, 0, 6, 0))

    # diagnosis cards
    diag = [
        ("blocked ↑", False, "壓測機本機埠耗盡、DNS 慢、沒有連線複用", "調整 ip_local_port_range、確認 Keep-Alive"),
        ("connecting / tls ↑", False, "每次請求都重建連線；壓測機與受測端 RTT 過高", "啟用 Keep-Alive 與 TLS Session Resumption，壓測機靠近受測端"),
        ("waiting (TTFB) ↑", True, "最常見的後端瓶頸：慢查詢、DB 連線池耗盡、CPU 飽和、下游 RPC 卡住", "用 Distributed Tracing 找出最慢的 Span"),
        ("receiving ↑", True, "回應 Payload 過大，頻寬被打滿", "分頁、精簡欄位、開啟 Gzip / Brotli"),
    ]
    cw, cg = 299, 20
    for i, (name, counted, cause, fix) in enumerate(diag):
        x = 60 + i * (cw + cg)
        add_box(s, x, 280, cw, 300, fill="FFFFFF", line=L_BORDER, radius=0.05)
        tag = add_box(s, x + 16, 296, 150 if counted else 170, 28,
                      fill=L_ACCENT_BG if counted else "F1F5F9",
                      line=L_ACCENT_BORDER if counted else "CBD5E1", radius=0.5)
        add_card_text(tag, [[("推高 duration" if counted else "duration 看不到", S(11.5, L_ACCENT if counted else L_MUTED, True))]],
                      anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
        add_text(s, x + 16, 334, cw - 32, 40, [[(name, S(18, L_TITLE, True, MONO))]], anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, x + 16, 382, cw - 32, 190, [
            [("可能病因", S(13, L_MUTED, True))],
            [(cause, S(15, L_BODY))],
            [(" ", S(6, L_BODY))],
            [("解法", S(13, L_MUTED, True))],
            [(fix, S(15, L_BODY))],
        ], space_after=3)

    # bottom terminal tip
    tip = add_box(s, 60, 604, 1256, 110, fill=T_BG, line="334155", radius=0.1)
    add_card_text(tip, [
        [("$ k6 run --summary-mode=full script.js", S(16, T_CYAN, True, MONO)),
         ("     # 預設 compact 模式不會列出這 6 個細分指標", S(14, T_DIM, font=MONO))],
        [("驗證：", S(14, T_AMBER, True)),
         ("sending + waiting + receiving 三個 avg 相加，剛好等於 http_req_duration 的 avg；Web Dashboard 的 Timings 分頁可看隨時間變化", S(14, T_TEXT))],
    ], anchor=MSO_ANCHOR.MIDDLE, margin=(22, 0, 22, 0), space_after=4)

    copy_badge(prs, s)
    s.notes_slide.notes_text_frame.text = (
        "官方定義 http_req_duration = sending + waiting + receiving。blocked、connecting、tls_handshaking 發生在請求送出前，"
        "只會拉長 iteration_duration。waiting 飆高是最常見的後端瓶頸，receiving 飆高代表 Payload 過大。")
    return s


# ---------------------------------------------------------------------------
# Ch5 (dark neon theme, reuses the deck's frame background)
# ---------------------------------------------------------------------------
D_TEXT = "D7DEEB"
D_WHITE = "FFFFFF"
D_MUTED = "9AA0A6"
D_CARD = "12202E"
D_CARD_BORDER = "324150"
D_CYAN = "66FCF1"
D_PURPLE = "BB86FC"
D_AMBER = "FFAB00"
D_ORANGE = "FB8C00"
D_RED = "FF5252"
D_GRAY = "9AA0A6"


def frame_background(prs):
    """Return the blob of the neon frame background used by Ch5's native slides."""
    best, best_n = None, 0
    for s in prs.slides:
        pics = [sh for sh in s.shapes if sh.shape_type == 13]
        texts = [sh for sh in s.shapes if sh.has_text_frame and sh.text_frame.text.strip()]
        if len(pics) == 1 and len(texts) > best_n:
            best, best_n = pics[0].image.blob, len(texts)
    if best is None:
        raise RuntimeError("frame background not found")
    return best


def dark_header(slide, bg_blob, title, subtitle):
    import io
    slide.shapes.add_picture(io.BytesIO(bg_blob), *px(0, 0, 1376, 768))
    add_text(slide, 60, 40, 1256, 50, [[(title, S(26, D_WHITE, True))]], anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, 60, 88, 1256, 30, [[(subtitle, S(14, D_CYAN))]], anchor=MSO_ANCHOR.MIDDLE)


def style_mini_chart(chart, colors, widths):
    chart.has_title = False
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.TOP
    chart.legend.include_in_layout = False
    chart.legend.font.size = Pt(9.5)
    chart.legend.font.color.rgb = rgb(D_TEXT)
    chart.legend.font.name = FONT
    va, ca = chart.value_axis, chart.category_axis
    va.visible = False
    va.has_major_gridlines = False
    va.minimum_scale, va.maximum_scale = 0, 10.5
    ca.visible = True
    ca.has_major_gridlines = False
    ca.tick_labels.font.size = Pt(1)
    ca.tick_labels.font.color.rgb = rgb(D_CARD)
    ca.format.line.color.rgb = rgb("3B4B5C")
    from pptx.enum.chart import XL_TICK_MARK, XL_TICK_LABEL_POSITION
    ca.major_tick_mark = XL_TICK_MARK.NONE
    ca.tick_label_position = XL_TICK_LABEL_POSITION.NONE
    for series, color, w in zip(chart.plots[0].series, colors, widths):
        series.smooth = False
        series.format.line.color.rgb = rgb(color)
        series.format.line.width = Pt(w)
        series.marker.style = None
        from pptx.enum.chart import XL_MARKER_STYLE
        series.marker.style = XL_MARKER_STYLE.NONE
    # transparent chart + plot area so the card colour shows through
    cs = chart._chartSpace
    for parent in (cs, cs.chart.plotArea):
        sppr = parent.find(qn("c:spPr"))
        if sppr is None:
            sppr = parent.makeelement(qn("c:spPr"), {})
            # c:spPr must precede c:txPr / externalData etc. in chartSpace; insert safely
            if parent is cs:
                anchor = cs.find(qn("c:txPr"))
                if anchor is None:
                    anchor = cs.find(qn("c:externalData"))
                if anchor is not None:
                    anchor.addprevious(sppr)
                else:
                    cs.append(sppr)
            else:
                parent.append(sppr)
        for child in list(sppr):
            sppr.remove(child)
        sppr.append(sppr.makeelement(qn("a:noFill"), {}))
        ln = sppr.makeelement(qn("a:ln"), {})
        ln.append(ln.makeelement(qn("a:noFill"), {}))
        sppr.append(ln)


def ch5_curve_patterns(prs, bg):
    s = prs.slides.add_slide(blank_layout(prs))
    dark_header(s, bg, "看懂儀表板：8 種經典曲線型態",
                "虛線＝負載軸（VUs / RPS），實線＝反應軸（延遲、錯誤率）；找出第一個偏離平穩的拐點")

    # Same figure as the codelab (scripts/generate_curve_patterns_figure.py), on a light card
    # so its validated light palette reads correctly on the dark slide.
    add_box(s, 60, 130, 1256, 586, fill="FCFCFB", line=D_CARD_BORDER, radius=0.025)
    img_w = 1226
    img_h = img_w * 1080 / 2400
    s.shapes.add_picture(FIGURE, *px(75, 130 + (586 - img_h) / 2, img_w, img_h))

    copy_badge(prs, s)
    s.notes_slide.notes_text_frame.text = (
        "8 種型態：① 健康線性 ② 飽和平台（RPS 走平＋P95 爬升，拐點即容量）③ 崩潰懸崖（P95 與錯誤率同時暴衝、RPS 下降）"
        "④ 尾巴張開（只有 P99 發散）⑤ 緩慢爬坡（負載不變延遲上升，看 P50 是否一起爬）⑥ 週期鋸齒（排程、GC、TTL）"
        "⑦ 錯誤率階梯（有限資源耗盡）⑧ 吞吐下滑＋blocked 上升（連線建立層，先排除壓測機）。")
    return s


def ch5_soak_reading(prs, bg):
    s = prs.slides.add_slide(blank_layout(prs))
    dark_header(s, bg, "Soak 判讀：趨勢比門檻重要",
                "負載固定時，時間是唯一的變數：看斜率、看恢復，再把 k6 端的「果」對齊後端的「因」")

    # left top: all-green but failing soak
    add_box(s, 60, 134, 600, 300, fill=D_CARD, line=D_CARD_BORDER, radius=0.05)
    add_text(s, 80, 146, 560, 34, [[("全程綠燈，也可能是失敗的 Soak", S(17, D_WHITE, True))]], anchor=MSO_ANCHOR.MIDDLE)
    x12 = list(range(12))
    cd = CategoryChartData()
    cd.categories = [str(v) for v in x12]
    cd.add_series("P95", [3.0 + 0.36 * i for i in x12])
    cd.add_series("門檻 p(95)<800", [8.0] * 12)
    gf = s.shapes.add_chart(XL_CHART_TYPE.LINE, *px(72, 184, 576, 170), cd)
    style_mini_chart(gf.chart, [D_AMBER, D_RED], [2.75, 1.5])
    add_text(s, 80, 360, 560, 66, [
        [("P95 從 300ms 爬到 700ms，門檻 800ms 沒破", S(13.5, D_TEXT))],
        [("→ 照這個斜率，第八小時就會紅燈。Soak 要看斜率，不是紅綠燈", S(13.5, D_AMBER, True))],
    ], space_after=4)

    # left bottom: three habits
    add_box(s, 60, 450, 600, 254, fill=D_CARD, line=D_CARD_BORDER, radius=0.05)
    add_text(s, 80, 462, 560, 32, [[("三個判讀習慣", S(17, D_CYAN, True))]], anchor=MSO_ANCHOR.MIDDLE)
    habits = [
        ("量化斜率", "只取固定負載段，5 分鐘一桶，算 P50 / P95 / 錯誤率 / RPS 的趨勢"),
        ("一定看恢復", "負載歸零後有沒有回到基準？結束後再跑一次 Smoke，仍慢就是硬證據"),
        ("守住窗口", "負載取撐得住的六到八成；期間不部署、不重啟、不跑批次"),
    ]
    add_text(s, 80, 500, 564, 196, [p for t, d in habits for p in (
        [("● ", S(14, D_CYAN, True)), (t, S(15.5, D_WHITE, True))],
        [("   " + d, S(14, D_TEXT))],
    )], space_after=9)

    # right: k6 signal -> backend data -> where in this lab
    add_box(s, 684, 134, 632, 570, fill=D_CARD, line=D_CARD_BORDER, radius=0.04)
    add_text(s, 704, 146, 592, 32, [[("k6 端的「果」→ 後端的「因」", S(17, D_CYAN, True))]], anchor=MSO_ANCHOR.MIDDLE)
    rows = [
        ("⑤ P95 緩慢爬升", "記憶體 heap、GC 次數與暫停", "docker stats 定時記錄容器記憶體"),
        ("⑤ 特定端點變慢", "資料庫查詢延遲", "4 Golden Signals：Database Query Latency"),
        ("⑦ 錯誤率階梯", "DB 連線池使用中／上限、open files", "pg_stat_activity 連線數、/proc/1/fd"),
        ("⑧ RPS 下滑", "伺服器／LB 連線數、壓測機連線", "壓測機 ss -s；Request Rate by Service"),
        ("所有訊號", "部署／重啟／排程的時間紀錄", "確認不是「有人動了它」"),
    ]
    add_text(s, 704, 184, 150, 26, [[("k6 訊號", S(12, D_MUTED, True))]], anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, 862, 184, 210, 26, [[("對照的後端數據", S(12, D_MUTED, True))]], anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, 1080, 184, 220, 26, [[("本 Lab 去哪看", S(12, D_MUTED, True))]], anchor=MSO_ANCHOR.MIDDLE)
    ry = 216
    for sig, backend, where in rows:
        add_box(s, 700, ry, 600, 84, fill="0A1420", line=D_CARD_BORDER, radius=0.1)
        add_text(s, 712, ry + 6, 146, 72, [[(sig, S(13.5, D_AMBER, True))]], anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, 862, ry + 6, 210, 72, [[(backend, S(13, D_WHITE))]], anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, 1080, ry + 6, 212, 72, [[(where, S(12.5, D_TEXT))]], anchor=MSO_ANCHOR.MIDDLE)
        ry += 84 + 12  # 216 -> 696
    add_text(s, 700, 704, 616, 22, [[("參考：iThome 鐵人賽〈Day 24｜Soak Test：從 k6 端數據推測伺服器在漏什麼〉", S(10, D_MUTED))]],
             anchor=MSO_ANCHOR.MIDDLE)

    copy_badge(prs, s)
    s.notes_slide.notes_text_frame.text = (
        "Soak 看斜率不看紅綠燈；量化趨勢（5 分鐘一桶）、一定看恢復（歸零後 + Smoke）、守住窗口。"
        "k6 只有果：P95 緩升對 heap/GC，錯誤階梯對連線池/open files，RPS 下滑對連線數與壓測機。")
    return s


def ch5_dashboard_sop(prs, bg):
    s = prs.slides.add_slide(blank_layout(prs))
    dark_header(s, bg, "儀表板判讀 4 步驟 SOP",
                "總結數字只告訴你「P95 = 812ms」，曲線才告訴你「第 35 秒、45 RPS 時開始抬頭」")

    steps = [
        ("確認壓力真的打出去", "VUs 與 RPS 符合腳本設計嗎？有沒有 dropped_iterations？流量配比對不對？"),
        ("找出拐點時間", "延遲或錯誤率第一次偏離平穩的時間點，記下當下的 VUs 與 RPS"),
        ("定位是哪一段變慢", "切到 Timings 分頁：Waiting＝後端運算、Blocked / Connecting＝連線層、Receiving＝Payload"),
        ("對齊後端指標找根因", "把拐點時間帶進 Grafana，用共享十字準星對齊 CPU、記憶體、DB 連線池 → 下一頁破案"),
    ]
    y = 134
    for i, (title, desc) in enumerate(steps):
        add_box(s, 60, y, 600, 132, fill=D_CARD, line=D_CARD_BORDER, radius=0.08)
        add_text(s, 80, y + 16, 70, 100, [[(str(i + 1), S(44, D_CYAN, True))]], anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
        add_text(s, 160, y + 14, 484, 104, [
            [(title, S(18, D_WHITE, True))],
            [(desc, S(14, D_TEXT))],
        ], anchor=MSO_ANCHOR.MIDDLE, space_after=4)
        y += 132 + 14  # 134 → 704

    # right: web dashboard tab map
    add_box(s, 684, 134, 632, 262, fill=D_CARD, line=D_CARD_BORDER, radius=0.05)
    add_text(s, 704, 146, 592, 32, [[("k6 Web Dashboard 分頁地圖", S(16, D_CYAN, True))]], anchor=MSO_ANCHOR.MIDDLE)
    tabs = [
        ("Overview", "HTTP Performance overview 把 RPS、P95、失敗率疊在同一張圖", "在什麼負載下開始變慢或出錯？"),
        ("Timings", "http_req_duration 的 6 個細分指標各一張圖", "變慢的是哪一段？"),
        ("Summary", "所有指標的結尾統計表", "等同終端機摘要，套用 5 步驟"),
    ]
    ty = 186
    for name, what, q in tabs:
        pill = add_box(s, 704, ty + 8, 112, 32, fill="0A1420", line=D_PURPLE, radius=0.5)
        add_card_text(pill, [[(name, S(13, D_PURPLE, True, MONO))]], anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
        add_text(s, 830, ty, 470, 64, [
            [(what, S(13, D_TEXT))],
            [("→ " + q, S(13.5, D_WHITE, True))],
        ], anchor=MSO_ANCHOR.MIDDLE, space_after=2)
        ty += 68

    # right: number traps
    add_box(s, 684, 412, 632, 292, fill="1A1626", line="5B4A1E", radius=0.05)
    add_text(s, 704, 424, 592, 32, [[("⚠ 三個判讀陷阱", S(16, D_AMBER, True))]], anchor=MSO_ANCHOR.MIDDLE)
    traps = [
        ("Overview 上排數字卡的 HTTP Request Duration 是 avg，不是 P95", "延遲請看下方 P95 / P99 曲線"),
        ("對 Trend Stats 推送的 k6_http_req_duration_p95 再取 avg()", "百分位數不能平均！本專案改用 Native Histogram ＋ histogram_quantile()"),
        ("RPS 走平，但後端 CPU 很閒、延遲也沒漲", "瓶頸可能在壓測機本身：看 k6 主機的 CPU、網卡與 dropped_iterations"),
    ]
    add_text(s, 704, 462, 596, 236, [p for t, fix in traps for p in (
        [("● ", S(14, D_AMBER, True)), (t, S(14.5, D_WHITE, True))],
        [("   " + fix, S(13.5, D_TEXT))],
    )], space_after=9)

    copy_badge(prs, s)
    s.notes_slide.notes_text_frame.text = (
        "判讀 4 步驟：確認壓力打出去 → 找拐點 → Timings 定位哪一段 → Grafana 十字準星對齊後端。"
        "陷阱：Overview 數字卡是 avg；P95 不能再取平均，要用 native histogram；RPS 走平但後端很閒要懷疑壓測機。")
    return s


# ---------------------------------------------------------------------------
def build_ch3():
    prs = Presentation(CH3)
    if has_marker(prs):
        print(f"skip (already has reading slides): {CH3}")
        return
    a = ch3_summary_sop(prs)
    b = ch3_latency_breakdown(prs)
    move_slide(prs, a, 4)  # after Slide 4 "Built-in Metrics"
    move_slide(prs, b, 5)
    prs.save(CH3)
    print(f"updated: {CH3}")


def build_ch5():
    prs = Presentation(CH5)
    if has_marker(prs):
        print(f"skip (already has reading slides): {CH5}")
        return
    bg = frame_background(prs)
    a = ch5_curve_patterns(prs, bg)
    b = ch5_soak_reading(prs, bg)
    c = ch5_dashboard_sop(prs, bg)
    add_marker(a)
    move_slide(prs, a, 7)  # after Slide 7 "Prometheus Remote Write", before the crosshair slide
    move_slide(prs, b, 8)
    move_slide(prs, c, 9)
    prs.save(CH5)
    print(f"updated: {CH5}")


if __name__ == "__main__":
    targets = sys.argv[1:] or ["ch3", "ch5"]
    if "ch3" in targets:
        build_ch3()
    if "ch5" in targets:
        build_ch5()
