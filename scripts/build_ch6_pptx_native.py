#!/usr/bin/env python3
"""
Build Chapter 6 PowerPoint presentation using 100% NATIVE PowerPoint shapes,
text frames, cards, and text boxes (NO full-slide PNG background images):
`k6/slides/Ch6_k6_AI_Agent_Engineering.pptx`

Clean, elegant design adhering strictly to Chapter 1 visual hierarchy and aesthetics:
- Unified top-left header across all 7 slides (Title + Subtitle, no displaced pills).
- Clear, spacious card grids (white cards, subtle borders, generous margins).
- Explicit left-aligned typography (eliminates awkward centered greeting-card text).
- Sleek dark terminal boxes for code/CLI/prompts.
- Clickable DevSite Codelabs Link Badge on every slide.
- Clickable hyperlinks for GitHub and Grafana documentation on Slide 6.
- Crisp Grafana k6 logo at bottom-right.
"""
import os
import pptx
from pptx.util import Inches, Pt, Emu
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

SW = Emu(16256000)
SH = Emu(9144000)
EMU_PER_PX_X = 16256000 / 1376
EMU_PER_PX_Y = 9144000 / 768

def px(x, y, w, h):
    return (
        int(x * EMU_PER_PX_X),
        int(y * EMU_PER_PX_Y),
        int(w * EMU_PER_PX_X),
        int(h * EMU_PER_PX_Y)
    )

# ---------------------------------------------------------
# COLOR PALETTE (Clean, Modern Slate & Vibrant Accents)
# ---------------------------------------------------------
COLOR_BG = RGBColor(248, 249, 250)         # Clean soft background (#F8F9FA)
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_TITLE = RGBColor(15, 23, 42)          # Slate 900 (#0F172A)
COLOR_SUBTITLE = RGBColor(100, 116, 139)    # Slate 500 (#64748B)
COLOR_CARD_TITLE = RGBColor(30, 41, 59)     # Slate 800 (#1E293B)
COLOR_BODY = RGBColor(71, 85, 105)          # Slate 600 (#475569)
COLOR_MUTED = RGBColor(148, 163, 184)       # Slate 400 (#94A3B8)
COLOR_BORDER = RGBColor(226, 232, 240)      # Slate 200 (#E2E8F0)

# Terminal
COLOR_TERM_BG = RGBColor(15, 23, 42)        # Slate 900 (#0F172A)
COLOR_TERM_BORDER = RGBColor(51, 65, 85)    # Slate 700 (#334155)
COLOR_TERM_CMD = RGBColor(56, 189, 248)     # Sky 400 (#38BDF8)
COLOR_TERM_COMMENT = RGBColor(148, 163, 184)# Slate 400 (#94A3B8)
COLOR_TERM_TEXT = RGBColor(241, 245, 249)   # Slate 100 (#F1F5F9)
COLOR_TERM_YELLOW = RGBColor(251, 191, 36)  # Amber 400 (#FBBF24)
COLOR_TERM_GREEN = RGBColor(74, 222, 128)   # Green 400 (#4ADE80)

# Theme Badges / Accents
COLOR_INDIGO = RGBColor(79, 70, 229)        # #4F46E5
COLOR_INDIGO_BG = RGBColor(238, 242, 255)   # #EEF2FF
COLOR_INDIGO_BORDER = RGBColor(199, 210, 254)

COLOR_EMERALD = RGBColor(5, 150, 105)       # #059669
COLOR_EMERALD_BG = RGBColor(209, 250, 229)
COLOR_EMERALD_BORDER = RGBColor(167, 243, 208)

COLOR_AMBER = RGBColor(180, 83, 9)          # #B45309
COLOR_AMBER_BG = RGBColor(254, 243, 199)
COLOR_AMBER_BORDER = RGBColor(252, 211, 77)

COLOR_BLUE = RGBColor(37, 99, 235)          # #2563EB
COLOR_BLUE_BG = RGBColor(239, 246, 255)
COLOR_BLUE_BORDER = RGBColor(191, 219, 254)

COLOR_PURPLE = RGBColor(124, 58, 237)       # #7C3AED
COLOR_PURPLE_BG = RGBColor(245, 243, 255)
COLOR_PURPLE_BORDER = RGBColor(221, 214, 254)

COLOR_ROSE = RGBColor(225, 29, 72)          # #E11D48
COLOR_ROSE_BG = RGBColor(255, 241, 242)
COLOR_ROSE_BORDER = RGBColor(254, 205, 211)

FONT_TC_BOLD = "Noto Sans CJK TC"
FONT_TC_REG = "Noto Sans CJK TC"
FONT_MONO = "DejaVu Sans Mono"

TARGET_URL = 'https://tedmax100.github.io/o11y_lab_for_dummies/k6-performance-testing/'
DISPLAY_URL = 'tedmax100.github.io/o11y_lab_for_dummies/k6-performance-testing/'

def set_shape_style(shape, fill_rgb, border_rgb=None, border_width=1.0):
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    if border_rgb:
        shape.line.color.rgb = border_rgb
        shape.line.width = Pt(border_width)
    else:
        shape.line.fill.background()

def add_background(slide):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SW, SH)
    set_shape_style(bg, COLOR_BG)
    return bg

def add_header(slide, title_text, subtitle_text):
    """
    Unified, clean top-left header system matching Chapter 1:
    - Title: x=56, y=32, size 25pt bold, slate 900
    - Subtitle: x=56, y=76, size 12.5pt regular, slate 500
    """
    l_t, t_t, w_t, h_t = px(56, 32, 1264, 40)
    tb_t = slide.shapes.add_textbox(l_t, t_t, w_t, h_t)
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True
    tf_t.vertical_anchor = MSO_ANCHOR.TOP
    tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.alignment = PP_ALIGN.LEFT
    r_t = p_t.add_run()
    r_t.text = title_text
    r_t.font.name = FONT_TC_BOLD
    r_t.font.size = Pt(25)
    r_t.font.bold = True
    r_t.font.color.rgb = COLOR_TITLE

    l_s, t_s, w_s, h_s = px(56, 76, 1264, 28)
    tb_s = slide.shapes.add_textbox(l_s, t_s, w_s, h_s)
    tf_s = tb_s.text_frame
    tf_s.word_wrap = True
    tf_s.vertical_anchor = MSO_ANCHOR.TOP
    tf_s.margin_left = tf_s.margin_right = tf_s.margin_top = tf_s.margin_bottom = 0
    p_s = tf_s.paragraphs[0]
    p_s.alignment = PP_ALIGN.LEFT
    r_s = p_s.add_run()
    r_s.text = subtitle_text
    r_s.font.name = FONT_TC_REG
    r_s.font.size = Pt(12.5)
    r_s.font.color.rgb = COLOR_SUBTITLE

def add_codelab_badge(slide):
    left = Inches(0.55)
    top = Inches(9.70)
    width = Inches(6.60)
    height = Inches(0.24)
    
    badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    badge.name = "Codelabs_Link_Badge"
    set_shape_style(badge, COLOR_WHITE, COLOR_BORDER, 1.0)
    badge.click_action.hyperlink.address = TARGET_URL

    tf = badge.text_frame
    tf.word_wrap = False
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.12)
    tf.margin_right = Inches(0.12)
    tf.margin_top = Inches(0)
    tf.margin_bottom = Inches(0)

    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT

    r1 = p.add_run()
    r1.text = '▶ 課程實戰 Codelabs：'
    r1.font.name = FONT_TC_BOLD
    r1.font.size = Pt(8.5)
    r1.font.bold = True
    r1.font.color.rgb = COLOR_CARD_TITLE

    r2 = p.add_run()
    r2.text = DISPLAY_URL
    r2.font.name = FONT_TC_REG
    r2.font.size = Pt(8.5)
    r2.font.bold = False
    r2.font.color.rgb = COLOR_BLUE

def add_branding_logo(slide):
    logo_path = 'k6/slides/assets/k6_grafana_full_branding.png'
    if not os.path.exists(logo_path):
        logo_path = '/tmp/k6_grafana_full_branding.png'
    if os.path.exists(logo_path):
        l, t, w, h = px(990, 642, 330, 80)
        slide.shapes.add_picture(logo_path, l, t, width=w, height=h)

def add_bottom_bar(slide, badge_label, main_text, sub_text, badge_fg=COLOR_INDIGO):
    """Clean takeaway bar on bottom-left matching Ch1"""
    l, t, w, h = px(56, 642, 914, 78)
    bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h)
    set_shape_style(bar, COLOR_WHITE, COLOR_BORDER, 1.0)

    tb = slide.shapes.add_textbox(l + px(18, 0, 0, 0)[0], t + px(0, 10, 0, 0)[1], w - px(36, 0, 0, 0)[0], h - px(0, 20, 0, 0)[1])
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    p1 = tf.paragraphs[0]
    p1.alignment = PP_ALIGN.LEFT
    r_b = p1.add_run()
    r_b.text = f"【{badge_label}】 "
    r_b.font.name = FONT_TC_BOLD
    r_b.font.size = Pt(10)
    r_b.font.bold = True
    r_b.font.color.rgb = badge_fg

    r_m = p1.add_run()
    r_m.text = main_text
    r_m.font.name = FONT_TC_BOLD
    r_m.font.size = Pt(10)
    r_m.font.bold = True
    r_m.font.color.rgb = COLOR_CARD_TITLE
    p1.space_after = Pt(3)

    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.LEFT
    r_s = p2.add_run()
    r_s.text = sub_text
    r_s.font.name = FONT_TC_REG
    r_s.font.size = Pt(9.5)
    r_s.font.color.rgb = COLOR_BODY

def create_card_base(slide, x, y, w, h, bg_color=COLOR_WHITE, border_color=COLOR_BORDER, border_width=1.0):
    l, t, width, height = px(x, y, w, h)
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, width, height)
    set_shape_style(shape, bg_color, border_color, border_width)
    return shape

def add_terminal_box(slide, x, y, w, h, lines, header_title="bash"):
    """
    Renders a sleek, dark terminal box with top macOS-style dots and monospace text.
    lines is a list of tuples: (text, type) where type in ('cmd', 'comment', 'out', 'key', 'green', 'yellow')
    """
    create_card_base(slide, x, y, w, h, bg_color=COLOR_TERM_BG, border_color=COLOR_TERM_BORDER, border_width=1.0)
    
    # Terminal header bar text
    l_th, t_th, w_th, h_th = px(x + 14, y + 8, w - 28, 20)
    tb_th = slide.shapes.add_textbox(l_th, t_th, w_th, h_th)
    tf_th = tb_th.text_frame
    tf_th.word_wrap = False
    tf_th.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_th.margin_left = tf_th.margin_right = tf_th.margin_top = tf_th.margin_bottom = 0
    p_th = tf_th.paragraphs[0]
    p_th.alignment = PP_ALIGN.LEFT
    
    r_dots = p_th.add_run()
    r_dots.text = "● ● ●  "
    r_dots.font.name = FONT_MONO
    r_dots.font.size = Pt(9)
    r_dots.font.color.rgb = RGBColor(100, 116, 139)
    
    r_th = p_th.add_run()
    r_th.text = header_title
    r_th.font.name = FONT_MONO
    r_th.font.size = Pt(8.5)
    r_th.font.color.rgb = RGBColor(148, 163, 184)

    # Terminal body text
    l_tb, t_tb, w_tb, h_tb = px(x + 16, y + 30, w - 32, h - 36)
    tb_b = slide.shapes.add_textbox(l_tb, t_tb, w_tb, h_tb)
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True
    tf_b.vertical_anchor = MSO_ANCHOR.TOP
    tf_b.margin_left = tf_b.margin_right = tf_b.margin_top = tf_b.margin_bottom = 0

    first = True
    for line_text, line_type in lines:
        p = tf_b.paragraphs[0] if first else tf_b.add_paragraph()
        first = False
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = line_text
        r.font.name = FONT_MONO
        r.font.size = Pt(9)
        
        if line_type == 'cmd':
            r.font.bold = True
            r.font.color.rgb = COLOR_TERM_CMD
            p.space_after = Pt(2)
        elif line_type == 'comment':
            r.font.bold = False
            r.font.color.rgb = COLOR_TERM_COMMENT
            p.space_after = Pt(1)
        elif line_type == 'yellow':
            r.font.bold = True
            r.font.color.rgb = COLOR_TERM_YELLOW
            p.space_after = Pt(1.5)
        elif line_type == 'green':
            r.font.bold = True
            r.font.color.rgb = COLOR_TERM_GREEN
            p.space_after = Pt(1.5)
        else: # 'out' / normal
            r.font.bold = False
            r.font.color.rgb = COLOR_TERM_TEXT
            p.space_after = Pt(1.5)

# ==============================================================================
# SLIDE 1: 全景導覽 (Overview & Paradigm Shift)
# ==============================================================================
def build_slide_1(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide)
    add_header(slide,
               "Module 6: k6 x agent ── AI 驅動的效能測試新紀元",
               "Grafana k6 原生 AI 子命令擴充套件 (xk6-subcommand-agent) · 一鍵配置 AI 編輯器與 Agent 壓測工作流")

    # 1. Top Hero Card: Paradigm Shift
    create_card_base(slide, 56, 120, 1264, 82)
    tb_h = slide.shapes.add_textbox(*px(76, 130, 1224, 62))
    tf_h = tb_h.text_frame
    tf_h.word_wrap = True
    tf_h.vertical_anchor = MSO_ANCHOR.TOP
    tf_h.margin_left = tf_h.margin_right = tf_h.margin_top = tf_h.margin_bottom = 0

    p_h1 = tf_h.paragraphs[0]
    p_h1.alignment = PP_ALIGN.LEFT
    r_hb = p_h1.add_run()
    r_hb.text = "【核心變革】 "
    r_hb.font.name = FONT_TC_BOLD
    r_hb.font.size = Pt(11)
    r_hb.font.bold = True
    r_hb.font.color.rgb = COLOR_INDIGO

    r_ht = p_h1.add_run()
    r_ht.text = "從「手寫測試代碼 (Test as Code)」躍升至「AI Agent 自主效能工程」"
    r_ht.font.name = FONT_TC_BOLD
    r_ht.font.size = Pt(12)
    r_ht.font.bold = True
    r_ht.font.color.rgb = COLOR_TITLE
    p_h1.space_after = Pt(4)

    p_h2 = tf_h.add_paragraph()
    p_h2.alignment = PP_ALIGN.LEFT
    r_hd = p_h2.add_run()
    r_hd.text = "過去配置 AI 壓測需繁瑣手動設定 MCP JSON、編寫 Prompt 規則，且 AI 常缺乏專業上下文而產生過期語法。"
    r_hd.font.name = FONT_TC_REG
    r_hd.font.size = Pt(10)
    r_hd.font.color.rgb = COLOR_BODY

    p_h3 = tf_h.add_paragraph()
    p_h3.alignment = PP_ALIGN.LEFT
    r_hd2 = p_h3.add_run()
    r_hd2.text = "k6 x agent 專為工程自動化而生：單一命令自動完成「安裝 5 大 AI 技能包」與「註冊 k6 MCP 伺服器」，秒級打通 AI 助手！"
    r_hd2.font.name = FONT_TC_BOLD
    r_hd2.font.size = Pt(10)
    r_hd2.font.bold = True
    r_hd2.font.color.rgb = COLOR_CARD_TITLE

    # 2. 3 Clean Columns (400px wide each, gap=32px)
    cols = [
        (56, 218, 400, 406, "ENGINE 1", "5 大 Bundled Skills", COLOR_INDIGO, [
            ("標準目錄注入", "自動將標準 SKILL.md 或 Cursor .mdc 規則寫入專屬目錄，即裝即用。"),
            ("自然語言意圖", "在 AI 視窗輸入 \"write smoke test\" 即刻自動調用專家級提示詞規範。"),
            ("官方最佳實踐", "預設注入動態 URL 標籤化防護，徹底杜絕記憶體洩漏與高基數 OOM 爆炸。"),
            ("全鏈路場景覆蓋", "涵蓋架構規劃、負載爬坡、冒煙檢驗、前端瀏覽器渲染到 Playwright 轉譯。")
        ]),
        (488, 218, 400, 406, "ENGINE 2", "原生 k6 MCP 伺服器", COLOR_EMERALD, [
            ("零配置自動註冊", "自動將 k6 x mcp 寫入 .mcp.json 或 .cursor/mcp.json，免手動翻找設定。"),
            ("AST 靜態語法預檢", "提供 validate_script 工具，執行前預檢抓出語法瑕疵與未宣告變數。"),
            ("本地閉環自癒", "提供 run_script 工具，直接由本機跑通 1 VU 冒煙驗證與報錯自主修復。"),
            ("無外部環境依賴", "由 Go 原生二進位直接驅動，免預裝 Node.js、npm 或 Python 執行環境。")
        ]),
        (920, 218, 400, 406, "GOVERNANCE", "企業級安全與多環境適配", COLOR_AMBER, [
            ("擁有者標籤保護", "透過 Owner Tag 精確識別，重複執行 init 絕不覆蓋工程師自訂代碼。"),
            ("寫入前安全預覽", "支援 --dry-run 旗標，零副作用預覽所有將建立與更新的檔案路徑。"),
            ("6 大主流環境", "全面適配 Cursor、Claude Code、GitHub Copilot、Codex CLI、OpenCode 等。"),
            ("Git 友善協同", "所有產出收斂於專案本地工作區目錄內，變更乾淨透明，極便於 PR 審查。")
        ])
    ]

    for cx, cy, cw, ch, tag, title, accent, bullets in cols:
        create_card_base(slide, cx, cy, cw, ch)
        
        tb = slide.shapes.add_textbox(*px(cx + 20, cy + 18, cw - 40, ch - 36))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

        p_t = tf.paragraphs[0]
        p_t.alignment = PP_ALIGN.LEFT
        r_tag = p_t.add_run()
        r_tag.text = f"{tag}  "
        r_tag.font.name = FONT_MONO
        r_tag.font.size = Pt(10)
        r_tag.font.bold = True
        r_tag.font.color.rgb = accent

        r_title = p_t.add_run()
        r_title.text = title
        r_title.font.name = FONT_TC_BOLD
        r_title.font.size = Pt(13)
        r_title.font.bold = True
        r_title.font.color.rgb = COLOR_CARD_TITLE
        p_t.space_after = Pt(16)

        for b_title, b_desc in bullets:
            p_b = tf.add_paragraph()
            p_b.alignment = PP_ALIGN.LEFT
            
            r_dot = p_b.add_run()
            r_dot.text = "• "
            r_dot.font.name = FONT_TC_BOLD
            r_dot.font.size = Pt(10)
            r_dot.font.bold = True
            r_dot.font.color.rgb = accent

            r_bt = p_b.add_run()
            r_bt.text = f"{b_title}："
            r_bt.font.name = FONT_TC_BOLD
            r_bt.font.size = Pt(10.5)
            r_bt.font.bold = True
            r_bt.font.color.rgb = COLOR_CARD_TITLE

            r_bd = p_b.add_run()
            r_bd.text = b_desc
            r_bd.font.name = FONT_TC_REG
            r_bd.font.size = Pt(9.5)
            r_bd.font.color.rgb = COLOR_BODY
            p_b.space_after = Pt(14)

    add_bottom_bar(slide, "一鍵起飛",
                   "終端一行指令即刻完成全套配置：$ k6 x agent init --all",
                   "接下來我們將依序深入架構雙引擎、安全冪等性、CLI 指令速查、5 大專業技能與企業導入實務！")
    add_branding_logo(slide)
    add_codelab_badge(slide)

# ==============================================================================
# SLIDE 2: 自動化雙引擎解密 (Dual Engines Architecture)
# ==============================================================================
def build_slide_2(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide)
    add_header(slide,
               "自動化雙引擎解密：技能包注入與原生 MCP 註冊",
               "告別手動繁瑣 JSON 配置與提示詞編寫，單一原生命令打通 AI Agent 與本地壓測工具鏈")

    # 2 Balanced Columns (w=616 each, gap=32px)
    cols = [
        (56, 120, 616, 504, "自動化引擎 1", "自動安裝內建 AI 技能 (Bundled Skills)", COLOR_INDIGO,
         "將 Grafana 官方壓測心智模型與最佳實踐注入 AI 編輯器",
         [("標準規格目錄寫入", "自動將標準 SKILL.md 或 Cursor 的 .mdc Rules 寫入專屬目錄（如 .cursor/rules/），讓 AI 編輯器開箱即具備 k6 專業規範與模板。"),
          ("自然語言意圖觸發", "在 AI 視窗輸入 \"write a smoke test\" 或 \"convert Playwright\"，AI 助手即自動觸發對應技能，精準產出高質量代碼。"),
          ("最佳實踐標準注入", "內建 Grafana 團隊嚴選的最佳實踐，防範動態字串拼接引發 High Cardinality 記憶體爆炸，並自動加入軍規資源釋放。"),
          ("跨開發者團隊一致性", "團隊成員只需執行一次 init 命令，即可在不同機台間維持完全統一的 AI 壓測提示詞與自動化腳本生成水準，杜絕風格斷層。")
         ]),
        (704, 120, 616, 504, "自動化引擎 2", "自動註冊 k6 MCP 伺服器 (Auto-Register MCP)", COLOR_EMERALD,
         "賦予 AI 助手即時語法靜態預檢與本機壓測自癒執行力",
         [("一鍵配置通訊協議", "自動將 k6 x mcp 寫入編輯器設定檔（如 .mcp.json、.cursor/mcp.json 或 .vscode/mcp.json），免除手動翻找文檔設定。"),
          ("零外部環境依賴", "直接呼叫 Go 原生二進位執行檔，完全無需預裝 Node.js、npm 或 Python 執行環境，環境極致乾淨且啟動效能極高。"),
          ("validate_script 語法預檢", "賦予 AI 靜態檢查能力：執行前由 AST 預檢語法結構、生命週期階段與 Thresholds 宣告合規性，杜絕低級語法錯誤。"),
          ("run_script 本地閉環自癒", "賦予 AI 執行能力：直接在聊天室驅動 1 VU 本地冒煙，即時結構化解析 RPS、P95 延遲與 HTTP 狀態碼進行自主迭代修正。")
         ])
    ]

    for cx, cy, cw, ch, pill_txt, title, col, card_sub, items in cols:
        create_card_base(slide, cx, cy, cw, ch)

        tb = slide.shapes.add_textbox(*px(cx + 24, cy + 22, cw - 48, ch - 44))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

        # Title
        p_t = tf.paragraphs[0]
        p_t.alignment = PP_ALIGN.LEFT
        r_pill = p_t.add_run()
        r_pill.text = f"【{pill_txt}】 "
        r_pill.font.name = FONT_TC_BOLD
        r_pill.font.size = Pt(11)
        r_pill.font.bold = True
        r_pill.font.color.rgb = col

        r_title = p_t.add_run()
        r_title.text = title
        r_title.font.name = FONT_TC_BOLD
        r_title.font.size = Pt(13)
        r_title.font.bold = True
        r_title.font.color.rgb = COLOR_TITLE
        p_t.space_after = Pt(4)

        # Card Subtitle
        p_sub = tf.add_paragraph()
        p_sub.alignment = PP_ALIGN.LEFT
        r_cs = p_sub.add_run()
        r_cs.text = card_sub
        r_cs.font.name = FONT_TC_REG
        r_cs.font.size = Pt(10)
        r_cs.font.color.rgb = COLOR_SUBTITLE
        p_sub.space_after = Pt(18)

        # 4 Clean bullet rows
        for term, desc in items:
            p_b = tf.add_paragraph()
            p_b.alignment = PP_ALIGN.LEFT
            
            r_dot = p_b.add_run()
            r_dot.text = "◆ "
            r_dot.font.name = FONT_TC_BOLD
            r_dot.font.size = Pt(10.5)
            r_dot.font.bold = True
            r_dot.font.color.rgb = col

            r_term = p_b.add_run()
            r_term.text = f"{term}："
            r_term.font.name = FONT_TC_BOLD
            r_term.font.size = Pt(11)
            r_term.font.bold = True
            r_term.font.color.rgb = COLOR_CARD_TITLE

            r_desc = p_b.add_run()
            r_desc.text = desc
            r_desc.font.name = FONT_TC_REG
            r_desc.font.size = Pt(10)
            r_desc.font.color.rgb = COLOR_BODY
            p_b.space_after = Pt(18)

    add_bottom_bar(slide, "雙引擎協同",
                   "技能包 (Skills) 負責「高品質代碼生成」，MCP 伺服器負責「執行與驗證自癒」",
                   "兩大引擎相互配合，讓 AI 助手具備從『產生腳本』到『本地驗證修復』的完整工程自癒閉環！")
    add_branding_logo(slide)
    add_codelab_badge(slide)

# ==============================================================================
# SLIDE 3: 安全防護與冪等性 (Safety & Idempotency)
# ==============================================================================
def build_slide_3(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide)
    add_header(slide,
               "安全防護與冪等性：企業級配置守門員",
               "非破壞性寫入、智慧辨識自訂規則，確保多次重複執行絕不毀損既有專案代碼")

    # Left Column: 3 Clean Safety Feature Cards (w=580, h=156 each, gap=18)
    left_cards = [
        (56, 120, 580, 156, "防護機制 1", "擁有者標籤保護 (Owner Tag)", COLOR_INDIGO,
         "<!-- generated by k6 x agent - DO NOT EDIT THIS BLOCK -->",
         "所有產出的規則檔案均附帶系統專屬識別標記。重複執行 init 時，系統自動比對標籤，精確區隔系統自動產生與工程師客製內容，安全無虞。"),
        (56, 294, 580, 156, "防護機制 2", "寫入前安全預覽 (--dry-run)", COLOR_BLUE,
         "$ k6 x agent init cursor --dry-run",
         "支援在真正寫入磁碟前加上 --dry-run 旗標進行安全排查。終端會清晰預覽列印出所有將新增、修改或保留的檔案清單與完整路徑，完全零副作用。"),
        (56, 468, 580, 156, "防護機制 3", "客製保護與智慧略過 (Custom Guard & --force)", COLOR_PURPLE,
         "$ k6 x agent init cursor --force",
         "偵測到使用者已手動修改過的檔案時，系統會自動跳過保護，絕不覆蓋你的客製規則；唯有在需要官方版本升級時，顯式加上 --force 才會覆蓋更新。")
    ]

    for cx, cy, cw, ch, badge, title, col, snippet, desc in left_cards:
        create_card_base(slide, cx, cy, cw, ch)
        tb = slide.shapes.add_textbox(*px(cx + 20, cy + 14, cw - 40, ch - 28))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

        p1 = tf.paragraphs[0]
        p1.alignment = PP_ALIGN.LEFT
        r_b = p1.add_run()
        r_b.text = f"【{badge}】 "
        r_b.font.name = FONT_TC_BOLD
        r_b.font.size = Pt(10.5)
        r_b.font.bold = True
        r_b.font.color.rgb = col

        r_t = p1.add_run()
        r_t.text = title
        r_t.font.name = FONT_TC_BOLD
        r_t.font.size = Pt(12)
        r_t.font.bold = True
        r_t.font.color.rgb = COLOR_CARD_TITLE
        p1.space_after = Pt(6)

        # Code snippet badge
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.LEFT
        r_snip = p2.add_run()
        r_snip.text = f"  {snippet}  "
        r_snip.font.name = FONT_MONO
        r_snip.font.size = Pt(9)
        r_snip.font.bold = True
        r_snip.font.color.rgb = col
        p2.space_after = Pt(8)

        # Description
        p3 = tf.add_paragraph()
        p3.alignment = PP_ALIGN.LEFT
        r_d = p3.add_run()
        r_d.text = desc
        r_d.font.name = FONT_TC_REG
        r_d.font.size = Pt(9.5)
        r_d.font.color.rgb = COLOR_BODY

    # Right Column: Sleek Decision Logic Terminal Box (w=664, h=504)
    term_lines = [
        ("# 1. 執行安全預覽 (零副作用確認磁碟變更)", 'comment'),
        ("$ k6 x agent init cursor --dry-run", 'cmd'),
        ("", 'out'),
        ("# 2. 檔案衝突判定決策流程 (Decision Tree)", 'comment'),
        ("掃描專案規則目錄 (.cursor/rules/*.mdc) ...", 'out'),
        ("  ├── 檔案不存在 ──> [寫入新檔] 並標記 Owner Tag 註解", 'green'),
        ("  └── 檔案已存在 ──> 比對內容是否包含識別標籤：", 'yellow'),
        ("         ├── 含標籤 (未修改) ──> [安全同步更新] 升級至官方標準", 'out'),
        ("         └── 不含標籤 (已修改) ──> [智慧略過保護] 保留開發者客製！", 'yellow'),
        ("", 'out'),
        ("# 3. 若確定要同步官方最新版，才使用 --force 強制覆蓋", 'comment'),
        ("$ k6 x agent init cursor --force", 'cmd'),
        ("", 'out'),
        ("# 4. 規則標籤範例 (.cursor/rules/k6-load-test.mdc)", 'comment'),
        ("<!-- generated by k6 x agent - DO NOT EDIT THIS BLOCK -->", 'green'),
        ("description: \"Execute standard production-grade load tests with k6\"", 'out'),
        ("globs: [\"**/*.js\", \"**/*.ts\"]", 'out')
    ]
    add_terminal_box(slide, 656, 120, 664, 504, term_lines, header_title="衝突防護決策邏輯 (Conflict Resolution Logic)")

    add_bottom_bar(slide, "核心價值",
                   "安全標籤機制讓你在敏捷迭代中享受 AI 自動化的便利，同時對現有專案保有 100% 絕對控制權！",
                   "支援所有產出檔案完全收斂於專案本地工作區目錄內，絕不污染全域環境，非常適合團隊納入 Git 版控審查。")
    add_branding_logo(slide)
    add_codelab_badge(slide)

# ==============================================================================
# SLIDE 4: CLI 指令速查與 6 大編輯器環境適配 (CLI Matrix & Editors)
# ==============================================================================
def build_slide_4(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide)
    add_header(slide,
               "常用 CLI 指令速查與 6 大編輯器環境適配",
               "在專案根目錄終端執行直覺的子命令，一鍵適配主流 AI 編輯器與自主 Agent 環境")

    # Left Column: Terminal box with CLI commands (w=580, h=504)
    term_lines = [
        ("# 1. 為指定編輯器進行初始化 (例如 Cursor 或 Claude Code)", 'comment'),
        ("$ k6 x agent init cursor", 'cmd'),
        ("$ k6 x agent init claude-code", 'cmd'),
        ("", 'out'),
        ("# 2. 一鍵初始化所有支援的編輯器 (團隊協作最佳實踐)", 'comment'),
        ("$ k6 x agent init --all", 'cmd'),
        ("", 'out'),
        ("# 3. 預覽將產生的檔案與路徑 (安全檢查，不寫入磁碟)", 'comment'),
        ("$ k6 x agent init --dry-run cursor", 'cmd'),
        ("", 'out'),
        ("# 4. 強制覆蓋重置所有技能與 MCP 設定 (版本升級專用)", 'comment'),
        ("$ k6 x agent init --force cursor", 'cmd'),
        ("", 'out'),
        ("# 5. 檢查當前專案的 AI 技能與 MCP 伺服器連線狀態", 'comment'),
        ("$ k6 x agent status", 'cmd'),
        ("", 'out'),
        ("# 6. 查看內建的所有 AI 技能清單與詳細描述", 'comment'),
        ("$ k6 x agent skills list", 'cmd')
    ]
    add_terminal_box(slide, 56, 120, 580, 504, term_lines, header_title="bash ── 在 k6 專案根目錄執行")

    # Right Column: 6 Editors in a neat 2-column x 3-row grid (cx=656, w=664)
    editors = [
        (0, 0, "Cursor", "cursor", "支援 .cursor/rules/*.mdc 與 .cursor/mcp.json，自然語言無縫調度 k6 工具。", COLOR_INDIGO),
        (1, 0, "Claude Code", "claude-code", "Anthropic 官方終端 Agent CLI，完美支援 skills 技能包與本地工具鏈。", COLOR_AMBER),
        (0, 1, "GitHub Copilot", "vscode-copilot", "微軟 VS Code 原生工作區，自動配置 .vscode/mcp.json，IDE 體驗極致流暢。", COLOR_BLUE),
        (1, 1, "OpenAI Codex CLI", "codex-cli", "OpenAI 原生終端工作流，支援命令行環境下的全自動逆向生成與壓測驗證。", COLOR_EMERALD),
        (0, 2, "OpenCode", "opencode", "開源終端 AI 助手環境，提供完全開源自主可控的 Agent 壓測配置方案。", COLOR_PURPLE),
        (1, 2, "Cline", "cline", "VS Code 開源自主 Agent 插件，支援檔案讀寫、終端執行與 MCP 閉環反饋。", COLOR_ROSE)
    ]

    for c_idx, r_idx, name, arg, desc, accent in editors:
        ex = 656 + c_idx * (322 + 20)
        ey = 120 + r_idx * (154 + 21)
        create_card_base(slide, ex, ey, 322, 154)

        tb = slide.shapes.add_textbox(*px(ex + 16, ey + 16, 290, 122))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

        p1 = tf.paragraphs[0]
        p1.alignment = PP_ALIGN.LEFT
        r_name = p1.add_run()
        r_name.text = name
        r_name.font.name = FONT_TC_BOLD
        r_name.font.size = Pt(12.5)
        r_name.font.bold = True
        r_name.font.color.rgb = accent

        r_arg = p1.add_run()
        r_arg.text = f"  ({arg})"
        r_arg.font.name = FONT_MONO
        r_arg.font.size = Pt(9)
        r_arg.font.color.rgb = COLOR_MUTED
        p1.space_after = Pt(8)

        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.LEFT
        r_desc = p2.add_run()
        r_desc.text = desc
        r_desc.font.name = FONT_TC_REG
        r_desc.font.size = Pt(9.5)
        r_desc.font.color.rgb = COLOR_BODY

    add_bottom_bar(slide, "協同優勢",
                   "無論團隊成員偏好 VS Code、Cursor 還是終端 Agent，執行 init --all 即可完全抹平環境差異！",
                   "多編輯器設定共享同一份核心壓測規範，讓每位工程師在自己熟悉的工具中享有完全一致的 AI 賦能體驗。")
    add_branding_logo(slide)
    add_codelab_badge(slide)

# ==============================================================================
# SLIDE 5: 內建 5 大 AI 技能深度剖析 (5 Bundled Skills Deep Dive - 2-Column Grid)
# ==============================================================================
def build_slide_5(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide)
    add_header(slide,
               "內建 5 大 AI 技能深度剖析：專家級壓測工作流",
               "從測試策略、負載爬坡、冒煙檢驗、前端真實渲染到 E2E 腳本轉譯的全鏈路覆蓋")

    # 2 Columns (w=616 each, gap=32px): Left = Core Generation (3 cards), Right = Advanced & Hybrid (3 cards)
    # Left column: 3 Cards (h=156 each, sy=120, 294, 468)
    left_skills = [
        ("k6-test-planner", "壓測策略規劃", COLOR_INDIGO,
         "分析 API 架構、端點特徵與預期吞吐量，自動規劃流量模型、計算並發 VU 與爬坡階段，並設計合理的 P95 延遲門檻與 SLO 門禁規範。",
         "\"plan tests for order service\", \"design a test strategy\", \"recommend VU and RPS\""),

        ("k6-load-test", "生產級負載壓測", COLOR_PURPLE,
         "生成具備 stages 階梯爬坡、arrival-rate 開放模型與動態 Token 關聯的生產級標準腳本，嚴格遵循 SharedArray 跨 VU 記憶體共享最佳實踐。",
         "\"write a load test\", \"stress test this endpoint\", \"soak test with 500 RPS\""),

        ("k6-smoke-test", "極速冒煙檢驗", COLOR_EMERALD,
         "以極低資源開銷（1 到 2 個 VU）在 5 秒內快速驗證 API 基礎可用性、HTTP 200/201 與 Check 軟斷言，適合作為 CI/CD 門禁的第一道快速防線。",
         "\"write a smoke test\", \"quick sanity check\", \"verify health check endpoint\"")
    ]

    for idx, (name, role, col, desc, triggers) in enumerate(left_skills):
        sy = 120 + idx * (156 + 18)
        create_card_base(slide, 56, sy, 616, 156)

        tb = slide.shapes.add_textbox(*px(76, sy + 14, 576, 128))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

        p1 = tf.paragraphs[0]
        p1.alignment = PP_ALIGN.LEFT
        r_name = p1.add_run()
        r_name.text = name
        r_name.font.name = FONT_MONO
        r_name.font.size = Pt(11)
        r_name.font.bold = True
        r_name.font.color.rgb = col

        r_role = p1.add_run()
        r_role.text = f"  【{role}】"
        r_role.font.name = FONT_TC_BOLD
        r_role.font.size = Pt(11)
        r_role.font.bold = True
        r_role.font.color.rgb = COLOR_CARD_TITLE
        p1.space_after = Pt(6)

        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.LEFT
        r_desc = p2.add_run()
        r_desc.text = desc
        r_desc.font.name = FONT_TC_REG
        r_desc.font.size = Pt(9.5)
        r_desc.font.color.rgb = COLOR_BODY
        p2.space_after = Pt(6)

        p3 = tf.add_paragraph()
        p3.alignment = PP_ALIGN.LEFT
        r_tlabel = p3.add_run()
        r_tlabel.text = "💬 觸發詞： "
        r_tlabel.font.name = FONT_TC_BOLD
        r_tlabel.font.size = Pt(9)
        r_tlabel.font.bold = True
        r_tlabel.font.color.rgb = col

        r_tval = p3.add_run()
        r_tval.text = triggers
        r_tval.font.name = FONT_MONO
        r_tval.font.size = Pt(8.5)
        r_tval.font.color.rgb = COLOR_MUTED

    # Right column: 2 Skills + 1 Synergy Matrix Card
    right_skills = [
        ("k6-browser-test", "前端真實渲染", COLOR_AMBER,
         "透過 k6/browser 驅動真實無頭 Chromium，量測 LCP、CLS、INP 等 Core Web Vitals 前端性能指標，並自動注入 finally page.close() 軍規防護。",
         "\"browser test for login UI\", \"measure Web Vitals\", \"hybrid 99:1 test\""),

        ("k6-playwright-converter", "Playwright 轉譯", COLOR_ROSE,
         "讀取現有的 Playwright 或 Puppeteer E2E 功能測試代碼，自動提取選擇器與業務流程，無痛轉譯為相容 k6 高併發架構的混合壓測腳本。",
         "\"convert Playwright script\", \"migrate E2E test to k6\", \"transform ui test\"")
    ]

    for idx, (name, role, col, desc, triggers) in enumerate(right_skills):
        sy = 120 + idx * (156 + 18)
        create_card_base(slide, 704, sy, 616, 156)

        tb = slide.shapes.add_textbox(*px(724, sy + 14, 576, 128))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

        p1 = tf.paragraphs[0]
        p1.alignment = PP_ALIGN.LEFT
        r_name = p1.add_run()
        r_name.text = name
        r_name.font.name = FONT_MONO
        r_name.font.size = Pt(11)
        r_name.font.bold = True
        r_name.font.color.rgb = col

        r_role = p1.add_run()
        r_role.text = f"  【{role}】"
        r_role.font.name = FONT_TC_BOLD
        r_role.font.size = Pt(11)
        r_role.font.bold = True
        r_role.font.color.rgb = COLOR_CARD_TITLE
        p1.space_after = Pt(6)

        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.LEFT
        r_desc = p2.add_run()
        r_desc.text = desc
        r_desc.font.name = FONT_TC_REG
        r_desc.font.size = Pt(9.5)
        r_desc.font.color.rgb = COLOR_BODY
        p2.space_after = Pt(6)

        p3 = tf.add_paragraph()
        p3.alignment = PP_ALIGN.LEFT
        r_tlabel = p3.add_run()
        r_tlabel.text = "💬 觸發詞： "
        r_tlabel.font.name = FONT_TC_BOLD
        r_tlabel.font.size = Pt(9)
        r_tlabel.font.bold = True
        r_tlabel.font.color.rgb = col

        r_tval = p3.add_run()
        r_tval.text = triggers
        r_tval.font.name = FONT_MONO
        r_tval.font.size = Pt(8.5)
        r_tval.font.color.rgb = COLOR_MUTED

    # Bottom Right Card: Skill Synergy Matrix
    sy_m = 120 + 2 * (156 + 18)
    create_card_base(slide, 704, sy_m, 616, 156)
    tb_m = slide.shapes.add_textbox(*px(724, sy_m + 14, 576, 128))
    tf_m = tb_m.text_frame
    tf_m.word_wrap = True
    tf_m.vertical_anchor = MSO_ANCHOR.TOP
    tf_m.margin_left = tf_m.margin_right = tf_m.margin_top = tf_m.margin_bottom = 0

    p_m1 = tf_m.paragraphs[0]
    p_m1.alignment = PP_ALIGN.LEFT
    r_mt = p_m1.add_run()
    r_mt.text = "【五大技能協同矩陣】 Full-Lifecycle Synergy"
    r_mt.font.name = FONT_TC_BOLD
    r_mt.font.size = Pt(12)
    r_mt.font.bold = True
    r_mt.font.color.rgb = COLOR_BLUE
    p_m1.space_after = Pt(6)

    p_m2 = tf_m.add_paragraph()
    p_m2.alignment = PP_ALIGN.LEFT
    r_md = p_m2.add_run()
    r_md.text = "5 大技能無縫銜接：由 planner 制定階梯目標 ➔ smoke 驗證端點存活 ➔ load 執行大並發壓測 ➔ browser 捕捉 Web Vitals 體驗，並透過 converter 無痛搬遷現有 E2E 資產！"
    r_md.font.name = FONT_TC_REG
    r_md.font.size = Pt(9.5)
    r_md.font.color.rgb = COLOR_BODY
    p_m2.space_after = Pt(6)

    p_m3 = tf_m.add_paragraph()
    p_m3.alignment = PP_ALIGN.LEFT
    r_mb = p_m3.add_run()
    r_mb.text = "🎯 工程綜效：從 API 到前端全視角覆蓋，建構標準化、可複製的 AI 效能工程工作流。"
    r_mb.font.name = FONT_TC_BOLD
    r_mb.font.size = Pt(9.5)
    r_mb.font.bold = True
    r_mb.font.color.rgb = COLOR_CARD_TITLE

    add_bottom_bar(slide, "技能協同",
                   "5 大技能相輔相成：先規劃策略、再產出冒煙、擴展至高負載與前端渲染，建構全視角壓測工程！",
                   "無論面對單純 REST API 還是複雜前後端混合流程，均有專門預設最佳實踐的技能包即刻就緒支援。")
    add_branding_logo(slide)
    add_codelab_badge(slide)

# ==============================================================================
# SLIDE 6: 企業導入實作 Checklist (Enterprise Checklist & Best Practices)
# ==============================================================================
def build_slide_6(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide)
    add_header(slide,
               "企業導入實作 Checklist：AI 壓測工程化最佳實踐",
               "將 AI Agent 融入團隊研發管線、建立腳本審計、記憶體防護與閉環自癒機制")

    cards_data = [
        (56, 120, 616, 242, "配置治理與團隊協作 (Configuration Governance)", COLOR_INDIGO, [
            ("Git 版本控管審計", "將 .cursor/rules 或 CLAUDE.md 納入 Git 版控，全團隊共享統一壓測標準。"),
            ("環境敏感資訊分離", "Token 與私有 API 網址透過環境變數注入，嚴禁寫入 AI 規則或公開設定。"),
            ("跨編輯器配置同步", "定期執行 k6 x agent init --all，確保跨職能開發者在不同工具間體驗對齊。"),
            ("CI/CD 狀態檢核", "在 CI Pipeline 整合 k6 x agent status，確保 Runner 環境與本地配置一致。")
        ]),
        (704, 120, 616, 242, "AI 閉環自癒工程 (Agentic Self-Healing Loop)", COLOR_EMERALD, [
            ("AST 靜態語法預檢", "生成腳本後，AI 必須自動調用 validate_script 抓出未定義變數與生命週期錯誤。"),
            ("1 VU 冒煙閉環先驗", "嚴格落實「大併發前先跑 1 VU 冒煙」，確認 HTTP 200 與 check 通過再壓測。"),
            ("日誌結構化解析", "AI 讀取 k6 終端報錯（如 401 Unauthorized、Thresholds 破功），自主迭代修正。"),
            ("減少手動排錯成本", "將傳統手動除錯 30 分鐘流程縮短為秒級 AI 閉環自癒，大幅加速交付。")
        ]),
        (56, 382, 616, 242, "高基數記憶體爆炸防護 (Memory Leak Prevention)", COLOR_AMBER, [
            ("強制 http.url 標籤", "AI 技能規則嚴格禁止以模板字串拼接動態 ID（如 /users/${id}）。"),
            ("防範維度爆炸 (OOM)", "動態端點強制經由 http.url 標籤函數聚合，阻斷 Prometheus 時間序列爆炸。"),
            ("SharedArray 記憶體優化", "大量測試帳號與參數強制使用 SharedArray 載入，跨 VU 共享不膨脹。"),
            ("資源洩漏軍規防護", "前端瀏覽器測試強制包含 finally { await page.close() }，避免殭屍行程。")
        ]),
        (704, 382, 616, 242, "官方生態系資源與持續演進 (Official Ecosystem)", COLOR_BLUE, [
            ("GitHub 官方開源專案", "https://github.com/grafana/xk6-subcommand-agent (開源倉庫與社群支援)"),
            ("Grafana 官方配置指南", "https://grafana.com/docs/k6/latest/set-up/configure-ai-assistant/bootstrap-with-k6-x-agent/"),
            ("定期顯式更新升級", "每季執行 k6 x agent init --force，同步 Grafana 官方最新進化技能包。"),
            ("無縫銜接可觀測性", "搭配 Chapter 5 的 Prometheus Remote Write 與 Grafana Dashboard 達成全鏈路監控。")
        ])
    ]

    for cx, cy, cw, ch, title, col, bullets in cards_data:
        create_card_base(slide, cx, cy, cw, ch)

        tb = slide.shapes.add_textbox(*px(cx + 22, cy + 18, cw - 44, ch - 36))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

        p_t = tf.paragraphs[0]
        p_t.alignment = PP_ALIGN.LEFT
        r_title = p_t.add_run()
        r_title.text = title
        r_title.font.name = FONT_TC_BOLD
        r_title.font.size = Pt(12)
        r_title.font.bold = True
        r_title.font.color.rgb = col
        p_t.space_after = Pt(12)

        for b_title, b_desc in bullets:
            p_b = tf.add_paragraph()
            p_b.alignment = PP_ALIGN.LEFT

            r_dot = p_b.add_run()
            r_dot.text = "• "
            r_dot.font.name = FONT_TC_BOLD
            r_dot.font.size = Pt(10)
            r_dot.font.bold = True
            r_dot.font.color.rgb = col

            r_bt = p_b.add_run()
            r_bt.text = f"{b_title}："
            r_bt.font.name = FONT_TC_BOLD
            r_bt.font.size = Pt(10)
            r_bt.font.bold = True
            r_bt.font.color.rgb = COLOR_CARD_TITLE

            if b_desc.startswith("https://"):
                url_part = b_desc.split(" ")[0]
                rest_part = b_desc[len(url_part):]
                r_link = p_b.add_run()
                r_link.text = url_part
                r_link.font.name = FONT_MONO
                r_link.font.size = Pt(9)
                r_link.font.underline = True
                r_link.font.color.rgb = COLOR_BLUE
                r_link.hyperlink.address = url_part

                if rest_part:
                    r_rest = p_b.add_run()
                    r_rest.text = rest_part
                    r_rest.font.name = FONT_TC_REG
                    r_rest.font.size = Pt(9.5)
                    r_rest.font.color.rgb = COLOR_BODY
            else:
                r_bd = p_b.add_run()
                r_bd.text = b_desc
                r_bd.font.name = FONT_TC_REG
                r_bd.font.size = Pt(9.5)
                r_bd.font.color.rgb = COLOR_BODY
            p_b.space_after = Pt(7)

    add_bottom_bar(slide, "最佳實踐",
                   "遵循上述 Checklist，讓 AI Agent 成為團隊中可靠、安全且高效的效能測試工程夥伴！",
                   "結合版本控管、高基數防護、閉環預檢與官方生態演進，建構可持續長久運行的工程化壓測體系。")
    add_branding_logo(slide)
    add_codelab_badge(slide)

# ==============================================================================
# SLIDE 7: 隨堂實作練習指引 (Hands-on Practice & Lab Guide)
# ==============================================================================
def build_slide_7(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide)
    add_header(slide,
               "隨堂實作練習指引：AI 輔助壓測三部曲",
               "請依序完成三大實戰任務，親身體驗 k6 x agent 的一鍵配置與 AI 輔助壓測閉環")

    # 3 Sequential Clean Task Cards (w=1264, h=156 each, gap=18px, starting y=120)
    tasks = [
        ("任務一：一鍵初始化本地 AI 編輯器與狀態檢核",
         "為你的主力編輯器（例如 Cursor 或 Claude Code）配置 k6 技能與 MCP 伺服器，並驗證連線健康度。",
         COLOR_INDIGO,
         [("$ k6 x agent init cursor       # 初始化 Cursor (或改用 claude-code)", "cmd"),
          ("$ k6 x agent status            # 檢查 MCP 伺服器連線狀態與 5 大技能清單", "cmd")],
         "驗證標準：.cursor/rules/ 下成功產生 5 個 .mdc 規則檔，且 .cursor/mcp.json 正確註冊 k6 x mcp。"),

        ("任務二：AI 逆向生成 QuickPizza 冒煙測試並閉環自癒",
         "利用內建 k6-smoke-test 技能與 MCP 工具，逆向生成冒煙測試並由 AI 本機跑通 1 VU 冒煙。",
         COLOR_EMERALD,
         [("Prompt: \"針對 QuickPizza 的 /api/pizza 端點撰寫 1 VU 冒煙測試腳本，包含 check 軟斷言與", "out"),
          ("         http.url 標籤，並請使用 validate_script 工具預檢腳本合法性。\"", "yellow")],
         "驗證標準：AI 產生合規腳本並主動調用 validate_script 驗證通過，無語法錯誤且無動態 URL 拼接。"),

        ("任務三：Playwright 登入測試無痛轉譯為 k6 混合壓測",
         "利用 k6-playwright-converter 技能將 E2E 測試升級為具備真實瀏覽器性能測量的混合壓測腳本。",
         COLOR_AMBER,
         [("Prompt: \"請將這段 Playwright 登入測試轉譯為 k6 browser 腳本，加入 finally page.close()", "out"),
          ("         軍規保護，並設定 99:1 混合流量模型。\"", "yellow")],
         "驗證標準：產出標準 k6/browser 語法，加入 try...finally 關閉瀏覽器，並具備 Web Vitals 採樣。")
    ]

    for idx, (title, goal, col, code_lines, verify) in enumerate(tasks):
        sy = 120 + idx * (156 + 18)
        create_card_base(slide, 56, sy, 1264, 156)

        # Title & Goal line
        tb_t = slide.shapes.add_textbox(*px(76, sy + 10, 1224, 22))
        tf_t = tb_t.text_frame
        tf_t.word_wrap = True
        tf_t.vertical_anchor = MSO_ANCHOR.TOP
        tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
        p_t = tf_t.paragraphs[0]
        p_t.alignment = PP_ALIGN.LEFT

        r_t = p_t.add_run()
        r_t.text = f"{title}   "
        r_t.font.name = FONT_TC_BOLD
        r_t.font.size = Pt(11.5)
        r_t.font.bold = True
        r_t.font.color.rgb = col

        r_g = p_t.add_run()
        r_g.text = f"目標：{goal}"
        r_g.font.name = FONT_TC_REG
        r_g.font.size = Pt(9.5)
        r_g.font.color.rgb = COLOR_BODY

        # Code block inside card (h=68, comfortably accommodates 2-3 lines with zero overflow)
        add_terminal_box(slide, 76, sy + 36, 1224, 70, code_lines, header_title="實戰指令與 Prompt 指引")

        # Verification check line (well separated at sy + 116)
        tb_v = slide.shapes.add_textbox(*px(76, sy + 116, 1224, 24))
        tf_v = tb_v.text_frame
        tf_v.word_wrap = True
        tf_v.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf_v.margin_left = tf_v.margin_right = tf_v.margin_top = tf_v.margin_bottom = 0
        p_v = tf_v.paragraphs[0]
        p_v.alignment = PP_ALIGN.LEFT
        r_v = p_v.add_run()
        r_v.text = f"✅ {verify}"
        r_v.font.name = FONT_TC_BOLD
        r_v.font.size = Pt(9.5)
        r_v.font.bold = True
        r_v.font.color.rgb = COLOR_CARD_TITLE

    add_bottom_bar(slide, "課程通關",
                   "恭喜完成 Chapter 6 全章節！你已掌握了現代化 AI Agent 壓測工程的核心心智模型與實戰技能！",
                   "立即打開你的終端機，執行 $ k6 x agent init，開始你的 AI 效能工程新體驗吧！")
    add_branding_logo(slide)
    add_codelab_badge(slide)

# ==============================================================================
# MAIN BUILD PIPELINE
# ==============================================================================
def main():
    prs = pptx.Presentation()
    prs.slide_width = SW
    prs.slide_height = SH

    print("Building Slide 1: Executive Overview & 3 Columns...")
    build_slide_1(prs)

    print("Building Slide 2: Dual Engines Architecture...")
    build_slide_2(prs)

    print("Building Slide 3: Safety & Idempotency...")
    build_slide_3(prs)

    print("Building Slide 4: CLI Matrix & 6 Editors...")
    build_slide_4(prs)

    print("Building Slide 5: 5 Bundled Skills Deep Dive (2-Column Grid)...")
    build_slide_5(prs)

    print("Building Slide 6: Enterprise Checklist...")
    build_slide_6(prs)

    print("Building Slide 7: Hands-on Practice Guide...")
    build_slide_7(prs)

    output_path = 'k6/slides/Ch6_k6_AI_Agent_Engineering.pptx'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prs.save(output_path)
    print(f"Presentation successfully saved to: {output_path}")

    # Synchronize build_ch6_pptx.py
    with open(__file__, 'r') as f_src:
        content = f_src.read()
    with open('scripts/build_ch6_pptx.py', 'w') as f_dst:
        f_dst.write(content)
    print("Synchronized with scripts/build_ch6_pptx.py")

if __name__ == '__main__':
    main()
