#!/usr/bin/env python3
"""
Replace the image on Ch1 slide 6 ("使用 group() 進行業務分組") with a native slide that
teaches group() as "one user journey, split into steps" (QuickPizza: 瀏覽首頁 → 取得推薦 →
送出評分), matching the codelab section and k6/demos/ch1_group_journey.js.

Edits the current deck in place (it is the Google Slides export with embedded fonts),
touching only slide 6. Re-running is a no-op once the full-slide picture is gone.
The p95 numbers are from a k6 v2.2 run of ch1_group_journey.js against QuickPizza.
"""
import io
import os
import sys

from PIL import Image
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_TICK_LABEL_POSITION, XL_TICK_MARK
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Pt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from add_metric_reading_slides import MONO, S, add_box, add_card_text, add_text, px, rgb  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECK = os.path.join(ROOT, "k6", "slides", "Ch1_Modern_Performance_Testing_with_k6.pptx")
SLIDE_INDEX = 5  # slide 6

BG = "EFEFF1"
INK = "111111"
BODY = "3F3F46"
MUTED = "71717A"
CARD = "FFFFFF"
BORDER = "D4D4D8"
ORANGE = "F97316"
BLUE = "2A78D6"
CODE_BG = "1F1F23"
C_TEXT = "E4E4E7"
C_KEY = "C4B5FD"
C_STR = "86EFAC"
C_DIM = "A1A1AA"

# p95 per group from `k6 run --summary-mode=full k6/demos/ch1_group_journey.js` (k6 v2.2)
P95 = [("瀏覽首頁", 201.6), ("取得推薦", 312.1), ("送出評分", 233.3)]


def arrow_down(slide, x, y1, y2, color=MUTED):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, *px(x, y1, 0, 0)[:2], *px(x, y2, 0, 0)[:2])
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(2)
    ln = c.line._get_or_add_ln()
    ln.append(ln.makeelement(qn("a:tailEnd"), {"type": "triangle", "w": "med", "len": "med"}))


def p95_chart(slide, x, y, w, h):
    cd = CategoryChartData()
    cd.categories = [n for n, _ in P95]
    cd.add_series("p95 (ms)", [v for _, v in P95])
    ch = slide.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, *px(x, y, w, h), cd).chart
    ch.has_legend = False
    ch.has_title = False
    plot = ch.plots[0]
    plot.gap_width = 60
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format = '0" ms"'
    dl.number_format_is_linked = False
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    dl.font.size = Pt(13)
    dl.font.bold = True
    dl.font.color.rgb = rgb(INK)
    ser = plot.series[0]
    for i, (_, v) in enumerate(P95):
        pt = ser.points[i]
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = rgb(ORANGE if v == max(p for _, p in P95) else BLUE)
    ca, va = ch.category_axis, ch.value_axis
    ca.reverse_order = True  # first group on top
    ca.tick_labels.font.size = Pt(13)
    ca.tick_labels.font.color.rgb = rgb(BODY)
    ca.format.line.color.rgb = rgb(BORDER)
    ca.major_tick_mark = XL_TICK_MARK.NONE
    va.visible = False
    va.has_major_gridlines = False
    va.minimum_scale = 0
    va.maximum_scale = 400
    va.tick_label_position = XL_TICK_LABEL_POSITION.NONE


def build(path=DECK):
    prs = Presentation(path)
    s = prs.slides[SLIDE_INDEX]
    full = [sh for sh in s.shapes if sh.shape_type == 13 and sh.width > prs.slide_width * 0.9]
    if not full:
        print("slide 6 already native; nothing to do")
        return
    src = Image.open(io.BytesIO(full[0].image.blob)).convert("RGB")
    sx = src.width / 1376
    logos = src.crop((int(855 * sx), int(700 * sx), int(965 * sx), int(762 * sx)))  # k6 + Grafana marks only
    s.shapes._spTree.remove(full[0]._element)
    badge = [sh for sh in s.shapes if sh._element.find(".//" + qn("a:hlinkClick")) is not None][0]._element

    add_box(s, 0, 0, 1376, 768, fill=BG, shape=MSO_SHAPE.RECTANGLE)
    add_text(s, 50, 24, 1276, 56, [[("讓測試結果一目瞭然：用 group() 把使用者旅程分段", S(30, INK, True))]], anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, 52, 80, 1276, 30, [[("真實使用者做的是「一趟旅程」而不是「一個請求」——分段之後，哪一段慢、慢多少一目瞭然", S(15, MUTED))]],
             anchor=MSO_ANCHOR.MIDDLE)

    # left: the journey
    add_box(s, 50, 128, 560, 564, fill=CARD, line=BORDER, radius=0.04)
    add_text(s, 74, 142, 512, 34, [[("一趟 QuickPizza 旅程", S(18, INK, True))]], anchor=MSO_ANCHOR.MIDDLE)
    steps = [
        ("1", "瀏覽首頁", "打開 QuickPizza 首頁", "停 1～3 秒：掃一眼就往下走"),
        ("2", "取得推薦", "請系統推薦一份披薩", "停 3～8 秒：看推薦、猶豫要不要換"),
        ("3", "送出評分", "登入後替這份披薩打分數", "停 2～5 秒：給分前想一想"),
    ]
    y = 190
    for i, (n, name, what, think) in enumerate(steps):
        add_box(s, 74, y, 512, 128, fill="FAFAFA", line=BORDER, radius=0.08)
        circ = add_box(s, 92, y + 38, 52, 52, fill=ORANGE if n == "2" else BLUE, shape=MSO_SHAPE.OVAL)
        add_card_text(circ, [[(n, S(20, "FFFFFF", True))]], anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER)
        add_text(s, 162, y + 10, 410, 108, [
            [(f"group('{name}')", S(17, INK, True, MONO))],
            [(what, S(14, BODY))],
            [(think, S(14, MUTED))],
        ], anchor=MSO_ANCHOR.MIDDLE, space_after=3)
        if i < len(steps) - 1:
            arrow_down(s, 330, y + 130, y + 150)
        y += 128 + 22
    add_text(s, 74, 640, 512, 40, [[("每段停頓不同，送出的流量節奏才像真人", S(14, BODY, True))]], anchor=MSO_ANCHOR.MIDDLE,
             align=PP_ALIGN.CENTER)

    # right top: code
    code = add_box(s, 634, 128, 692, 250, fill=CODE_BG, line=CODE_BG, radius=0.05)
    lines = [
        [("group", C_KEY), ("('瀏覽首頁'", C_STR), (", () => {", C_TEXT)],
        [("  http.get(`${BASE}/`);", C_TEXT)],
        [("  sleep(1 + Math.random() * 2);", C_TEXT), ("  // 1～3 秒", C_DIM)],
        [("});", C_TEXT)],
        [("group", C_KEY), ("('取得推薦'", C_STR), (", () => { /* POST /api/pizza */ });", C_TEXT)],
        [("group", C_KEY), ("('送出評分'", C_STR), (", () => { /* POST /api/ratings */ });", C_TEXT)],
        [("", C_TEXT)],
        [("$ k6 run --summary-mode=full ch1_group_journey.js", C_DIM)],
    ]
    add_card_text(code, [[(t, S(14.5, c, False, MONO)) for t, c in ln] for ln in lines],
                  anchor=MSO_ANCHOR.MIDDLE, margin=(24, 0, 20, 0), line_spacing=1.1)

    # right bottom: per-group p95
    add_box(s, 634, 394, 692, 298, fill=CARD, line=BORDER, radius=0.05)
    add_text(s, 658, 406, 644, 32, [[("--summary-mode=full：每一段自己的 http_req_duration p95", S(15, INK, True))]],
             anchor=MSO_ANCHOR.MIDDLE)
    p95_chart(s, 648, 440, 664, 176)
    add_text(s, 658, 622, 644, 58, [
        [("回報：", S(14.5, ORANGE, True)), ("「取得推薦」的 p95 是 312ms，比首頁慢 50%——", S(14.5, INK, True))],
        [("比「整體有點慢」有用得多", S(14.5, INK, True))],
    ], anchor=MSO_ANCHOR.MIDDLE, space_after=2)

    buf = io.BytesIO()
    logos.save(buf, "PNG")
    buf.seek(0)
    s.shapes.add_picture(buf, *px(1180, 704, 110, 62))

    tree = s.shapes._spTree
    tree.remove(badge)
    tree.append(badge)
    prs.save(path)
    print(f"updated slide 6 in {path}")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else DECK)
