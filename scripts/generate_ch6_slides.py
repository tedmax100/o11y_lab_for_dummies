#!/usr/bin/env python3
"""
Generate 7 high-definition, beautifully structured slide images for Chapter 6:
`Module 6: k6 x agent ── AI 驅動的效能測試新紀元`

Slides:
- Slide 1: 封面與全景導覽 (Title & Executive Overview)
- Slide 2: 自動化雙引擎解密：技能包注入與原生 MCP 註冊 (Architecture & Dual Engines)
- Slide 3: 安全防護與冪等性：企業級配置守門員 (Safety & Idempotency)
- Slide 4: 常用 CLI 指令速查與 6 大編輯器環境適配 (CLI Workflow & Editor Matrix)
- Slide 5: 內建 5 大 AI 技能深度剖析：專家級壓測工作流 (5 Bundled Skills Deep Dive)
- Slide 6: 企業導入實作 Checklist：AI 壓測工程化最佳實踐 (Enterprise Takeaways)
- Slide 7: 隨堂實作練習指引：AI 輔助壓測三部曲 (Hands-on Practice & Lab Guide)
"""
import os
from PIL import Image, ImageDraw, ImageFont

W = 1376
H = 768

# Fonts
FONT_TC_BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
FONT_TC_REG = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
FONT_EN_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_EN_REG = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_MONO_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
FONT_MONO_REG = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'

f_cover_title = ImageFont.truetype(FONT_TC_BOLD, 28)
f_title = ImageFont.truetype(FONT_TC_BOLD, 24)
f_subtitle = ImageFont.truetype(FONT_TC_REG, 13.5)
f_pill = ImageFont.truetype(FONT_TC_BOLD, 11)
f_h2 = ImageFont.truetype(FONT_TC_BOLD, 14.5)
f_card_title = ImageFont.truetype(FONT_TC_BOLD, 13)
f_body_bold = ImageFont.truetype(FONT_TC_BOLD, 11.5)
f_body_reg = ImageFont.truetype(FONT_TC_REG, 11)
f_term_comment = ImageFont.truetype(FONT_TC_REG, 10.5)
f_term_cmd = ImageFont.truetype(FONT_MONO_BOLD, 11)
f_term_out = ImageFont.truetype(FONT_MONO_REG, 10.5)
f_link_label = ImageFont.truetype(FONT_TC_BOLD, 10.5)
f_link_url = ImageFont.truetype(FONT_EN_REG, 10.5)
f_footer = ImageFont.truetype(FONT_TC_REG, 10)

def draw_header(draw, part_num, title, subtitle, pill_prefix="AI SUBCOMMAND EXTENSION"):
    badge_x, badge_y = 48, 28
    pill_text = f"{pill_prefix} · PART {part_num}" if part_num else pill_prefix
    pill_bbox = draw.textbbox((0, 0), pill_text, font=f_pill)
    pill_w = pill_bbox[2] - pill_bbox[0] + 18
    
    draw.rounded_rectangle([badge_x, badge_y, badge_x + pill_w, badge_y + 24], radius=6, fill=(238, 242, 255), outline=(199, 210, 254), width=1)
    draw.text((badge_x + 9, badge_y + 4), pill_text, font=f_pill, fill=(79, 70, 229))

    title_x = badge_x + pill_w + 14
    draw.text((title_x, badge_y - 2), title, font=f_title, fill=(15, 23, 42))

    sub_y = badge_y + 35
    draw.text((badge_x, sub_y), subtitle, font=f_subtitle, fill=(71, 85, 105))

def paste_branding(img):
    logo_path = 'k6/slides/assets/k6_grafana_full_branding.png'
    if not os.path.exists(logo_path):
        logo_path = '/tmp/k6_grafana_full_branding.png'
    if os.path.exists(logo_path):
        logo_img = Image.open(logo_path)
        img.paste(logo_img, (990, 655))

def save_slide(img, slide_idx):
    out1 = f'k6/slides/assets/Ch6/slide_{slide_idx}.png'
    out2 = f'k6/slides/Ch6_slide_{slide_idx}.png'
    img.convert('RGB').save(out1, quality=95)
    img.convert('RGB').save(out2, quality=95)
    print(f"Saved Slide {slide_idx} -> {out1} & {out2}")

# ==============================================================================
# SLIDE 1: 封面與全景導覽 (Title & Executive Overview)
# ==============================================================================
def create_slide_1():
    img = Image.new('RGBA', (W, H), (248, 247, 242, 255))
    draw = ImageDraw.Draw(img)

    # Header
    draw_header(
        draw, None,
        "Module 6: k6 x agent ── AI 驅動的效能測試新紀元",
        "Grafana k6 原生 AI 子命令擴充套件 (xk6-subcommand-agent) · 一鍵配置 AI 編輯器與 Agent 壓測工作流",
        pill_prefix="MODULE 6 · GRAFANA K6 AI AGENT ENGINEERING"
    )

    # Hero Banner
    hero_x, hero_y, hero_w, hero_h = 48, 100, 1280, 104
    draw.rounded_rectangle([hero_x, hero_y, hero_x + hero_w, hero_y + hero_h], radius=10, fill=(255, 255, 255), outline=(226, 232, 240), width=1)
    draw.rounded_rectangle([hero_x + 18, hero_y + 12, hero_x + 18 + 92, hero_y + 12 + 22], radius=4, fill=(238, 242, 255), outline=(199, 210, 254), width=1)
    draw.text((hero_x + 24, hero_y + 15), "效能壓測新紀元", font=f_pill, fill=(79, 70, 229))
    draw.text((hero_x + 120, hero_y + 13), "從「手寫測試代碼 (Test as Code)」躍升至「AI Agent 自主工程」", font=f_h2, fill=(15, 23, 42))

    hero_desc1 = "過去手動配置 AI 壓測工作流需要繁複設定 MCP JSON、手寫 Prompt Rules、配置 Node.js 依賴，且 AI 常因缺乏上下文產生過期語法。"
    hero_desc2 = "k6 x agent 是 Grafana k6 原生子命令擴充套件：只需執行一次命令，即可自動完成「安裝 5 大技能包」與「註冊 k6 MCP 伺服器」，秒級打通 AI 助手！"
    draw.text((hero_x + 20, hero_y + 44), hero_desc1, font=f_body_reg, fill=(71, 85, 105))
    draw.text((hero_x + 20, hero_y + 68), hero_desc2, font=f_body_bold, fill=(30, 41, 59))

    # 4 Feature Cards (2x2 Grid)
    # Row 1: y=218, h=204
    # Col 1: x=48, w=630 | Col 2: x=698, w=630
    grid_cards = [
        # (x, y, w, h, pill_text, pill_bg, pill_border, pill_col, title, bullets)
        (48, 218, 630, 204,
         "核心引擎 1", (238, 242, 255), (199, 210, 254), (79, 70, 229),
         "自動注入 5 大 Bundled Skills 專業技能庫",
         [
             ("標準規格目錄寫入", "自動將 SKILL.md 或 Cursor .mdc 規則寫入專屬目錄。"),
             ("自然語言意圖觸發", "對話輸入 \"write smoke test\" 即刻載入專家級提示詞。"),
             ("最佳實踐預設注入", "嚴選官方標準樣板，徹底防範動態 URL 高基數記憶體洩漏。"),
             ("全鏈路壓測覆蓋", "涵蓋規劃、負載、冒煙、前端瀏覽器渲染到 Playwright 轉譯。")
         ]),
        (698, 218, 630, 204,
         "核心引擎 2", (209, 250, 229), (167, 243, 208), (5, 150, 105),
         "原生註冊 k6 MCP 伺服器 (Zero Config)",
         [
             ("原生協議一鍵寫入", "自動將 k6 x mcp 註冊至 .mcp.json 或 .cursor/mcp.json。"),
             ("AST 靜態語法預檢", "提供 validate_script 工具，執行前抓出語法與未定義變數。"),
             ("本機閉環自癒驗證", "提供 run_script 工具，直接由本機跑通 1 VU 冒煙閉環自癒。"),
             ("零外部執行環境依賴", "由 Go 原生編譯直接驅動，免裝 Node.js、npm 或 Python。")
         ]),
        (48, 434, 630, 204,
         "環境適配", (254, 243, 199), (252, 211, 77), (180, 83, 9),
         "6 大主流 AI 編輯器與自主 Agent 全面適配",
         [
             ("主流 IDE 深度整合", "全面支援 Cursor、Claude Code、GitHub Copilot (VS Code)。"),
             ("終端 Agent 完整覆蓋", "適配 OpenAI Codex CLI、OpenCode 以及 Cline 等開源工具。"),
             ("一鍵全環境配置", "提供 k6 x agent init --all，一次性打通所有支援環境。"),
             ("抹平團隊配置孤島", "團隊成員不論使用何種編輯器，皆享有一致的 AI 壓測體驗。")
         ]),
        (698, 434, 630, 204,
         "工程防護", (255, 241, 242), (254, 205, 211), (225, 29, 72),
         "安全防護、衝突處理與工程冪等性機制",
         [
             ("擁有者標籤 (Owner Tag)", "以標籤精準區隔系統產生與手動代碼，絕不覆蓋自訂規則。"),
             ("寫入前預覽 (--dry-run)", "預先輸出所有新增與修改路徑，零副作用安心檢核。"),
             ("明確強制覆蓋 (--force)", "版本升級時才以 --force 顯式同步，掌控權完全在工程師。"),
             ("Git 友善與審計追蹤", "所有產出收斂於專案工作區內，變更乾淨且便於 PR 審查。")
         ])
    ]

    for cx, cy, cw, ch, pill_txt, p_bg, p_bd, p_fg, title, bullets in grid_cards:
        draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=10, fill=(255, 255, 255), outline=(226, 232, 240), width=1)
        
        # Pill
        draw.rounded_rectangle([cx + 14, cy + 12, cx + 14 + 76, cy + 12 + 20], radius=4, fill=p_bg, outline=p_bd, width=1)
        draw.text((cx + 19, cy + 14), pill_txt, font=f_pill, fill=p_fg)
        draw.text((cx + 98, cy + 13), title, font=f_card_title, fill=(15, 23, 42))

        by = cy + 42
        for b_title, b_desc in bullets:
            draw.text((cx + 16, by), f"• {b_title}：", font=f_body_bold, fill=p_fg)
            draw.text((cx + 168, by), b_desc, font=f_body_reg, fill=(71, 85, 105))
            by += 38

    # Bottom Banner
    foot_x, foot_y, foot_w, foot_h = 48, 650, 930, 86
    draw.rounded_rectangle([foot_x, foot_y, foot_x + foot_w, foot_y + foot_h], radius=8, fill=(255, 255, 255), outline=(203, 213, 225), width=1)
    draw.rounded_rectangle([foot_x + 14, foot_y + 12, foot_x + 84, foot_y + 34], radius=4, fill=(240, 253, 250), outline=(94, 234, 212), width=1)
    draw.text((foot_x + 20, foot_y + 15), "一鍵起飛", font=f_pill, fill=(13, 148, 136))
    draw.text((foot_x + 94, foot_y + 14), "終端一行指令即刻完成全套配置： $ k6 x agent init --all", font=f_term_cmd, fill=(15, 23, 42))
    draw.text((foot_x + 18, foot_y + 48), "接下來我們將依序深入架構雙引擎、安全冪等性、CLI 指令矩陣、5 大專業技能與企業導入實務！", font=f_footer, fill=(100, 116, 139))

    paste_branding(img)
    save_slide(img, 1)

# ==============================================================================
# SLIDE 2: 自動化雙引擎解密 (Dual Automation Engines)
# ==============================================================================
def create_slide_2():
    img = Image.new('RGBA', (W, H), (248, 247, 242, 255))
    draw = ImageDraw.Draw(img)

    draw_header(
        draw, 1,
        "自動化雙引擎解密：技能包注入與原生 MCP 註冊",
        "告別手寫繁瑣 JSON 配置與提示詞編寫，單一原生命令打通 AI Agent 與本地壓測工具鏈",
        pill_prefix="ARCHITECTURE & ENGINES"
    )

    # Left Column: 引擎一 - 自動安裝內建技能 (x=48, w=634)
    # Right Column: 引擎二 - 自動註冊 k6 MCP 伺服器 (x=694, w=634)
    c1_x, c1_y, c1_w, c1_h = 48, 100, 634, 532
    draw.rounded_rectangle([c1_x, c1_y, c1_x + c1_w, c1_y + c1_h], radius=10, fill=(255, 255, 255), outline=(226, 232, 240), width=1)
    draw.rounded_rectangle([c1_x + 18, c1_y + 14, c1_x + 18 + 84, c1_y + 14 + 22], radius=4, fill=(238, 242, 255), outline=(199, 210, 254), width=1)
    draw.text((c1_x + 24, c1_y + 17), "自動化引擎 1", font=f_pill, fill=(79, 70, 229))
    draw.text((c1_x + 112, c1_y + 15), "自動安裝內建 AI 技能 (Bundled Skills)", font=f_h2, fill=(15, 23, 42))

    points_1 = [
        ("標準規格寫入", 
         "將標準 SKILL.md 或 Cursor 的 .mdc Rules 自動寫入專屬目錄",
         "（如 .cursor/rules），讓 AI 編輯器即刻掌握 k6 專業規範。"),
        ("自然語言觸發", 
         "在 AI 視窗輸入 \"write a smoke test\" 或 \"convert Playwright\"",
         "AI 助手即自動觸發對應的 k6 專業技能，按標準產出代碼。"),
        ("最佳實踐標準", 
         "內建 Grafana 團隊嚴選的最佳實踐，避免 AI 產生過期語法",
         "或動態字串拼接引發 High Cardinality 記憶體洩漏代碼。"),
        ("團隊一致性", 
         "團隊成員只需執行一次 init 命令，即可在不同開發機間",
         "擁有完全統一的 AI 壓測提示詞與自動化腳本生成水準。")
    ]
    py = c1_y + 50
    for term, l1, l2 in points_1:
        draw.rounded_rectangle([c1_x + 16, py, c1_x + c1_w - 16, py + 104], radius=8, fill=(248, 250, 252), outline=(226, 232, 240), width=1)
        draw.text((c1_x + 28, py + 14), f"◆ {term}", font=f_card_title, fill=(79, 70, 229))
        draw.text((c1_x + 28, py + 42), l1, font=f_body_reg, fill=(71, 85, 105))
        draw.text((c1_x + 28, py + 66), l2, font=f_body_reg, fill=(71, 85, 105))
        py += 116

    # Right Column: 引擎二 - 自動註冊 k6 MCP 伺服器
    c2_x = 694
    draw.rounded_rectangle([c2_x, c1_y, c2_x + c1_w, c1_y + c1_h], radius=10, fill=(255, 255, 255), outline=(226, 232, 240), width=1)
    draw.rounded_rectangle([c2_x + 18, c1_y + 14, c2_x + 18 + 84, c1_y + 14 + 22], radius=4, fill=(209, 250, 229), outline=(167, 243, 208), width=1)
    draw.text((c2_x + 24, c1_y + 17), "自動化引擎 2", font=f_pill, fill=(5, 150, 105))
    draw.text((c2_x + 112, c1_y + 15), "自動註冊 k6 MCP 伺服器 (Auto-Register MCP)", font=f_h2, fill=(15, 23, 42))

    points_2 = [
        ("一鍵配置協議", 
         "自動將 k6 x mcp 寫入編輯器設定檔（如 .mcp.json、",
         ".cursor/mcp.json 或 .vscode/mcp.json），免除手動翻找設定。"),
        ("零依賴原生驅動", 
         "直接呼叫 k6 原生子命令執行檔，完全無需預裝 Node.js、",
         "npm 或全域套件，環境乾淨且效能極高。"),
        ("validate_script", 
         "賦予 AI 靜態檢查能力：執行前由 AST 預檢語法結構、",
         "生命週期階段與 Thresholds 宣告合規性，杜絕基本錯誤。"),
        ("run_script 驗證", 
         "賦予 AI 執行能力：直接在聊天室驅動本地壓測，",
         "即時結構化解析 RPS、P95 延遲與 HTTP 狀態碼自癒修正。")
    ]
    py = c1_y + 50
    for term, l1, l2 in points_2:
        draw.rounded_rectangle([c2_x + 16, py, c2_x + c1_w - 16, py + 104], radius=8, fill=(240, 253, 250), outline=(204, 251, 241), width=1)
        draw.text((c2_x + 28, py + 14), f"◆ {term}", font=f_card_title, fill=(13, 148, 136))
        draw.text((c2_x + 28, py + 42), l1, font=f_body_reg, fill=(71, 85, 105))
        draw.text((c2_x + 28, py + 66), l2, font=f_body_reg, fill=(71, 85, 105))
        py += 116

    # Bottom Banner
    foot_x, foot_y, foot_w, foot_h = 48, 650, 930, 86
    draw.rounded_rectangle([foot_x, foot_y, foot_x + foot_w, foot_y + foot_h], radius=8, fill=(255, 255, 255), outline=(203, 213, 225), width=1)
    draw.rounded_rectangle([foot_x + 14, foot_y + 12, foot_x + 78, foot_y + 34], radius=4, fill=(240, 253, 250), outline=(94, 234, 212), width=1)
    draw.text((foot_x + 20, foot_y + 15), "架構價值", font=f_pill, fill=(13, 148, 136))
    draw.text((foot_x + 88, foot_y + 14), "告別過去手動翻找 JSON 與手寫 Rules 的繁重負擔，執行一次命令即可在數秒內打通 AI 與 k6！", font=f_body_bold, fill=(30, 41, 59))
    draw.text((foot_x + 18, foot_y + 48), "下一頁：我們將檢驗 k6 x agent 的安全防護與工程冪等性機制，如何保護你的客製代碼！", font=f_footer, fill=(100, 116, 139))

    paste_branding(img)
    save_slide(img, 2)

# ==============================================================================
# SLIDE 3: 安全防護、衝突處理與冪等性機制 (Safety & Idempotency)
# ==============================================================================
def create_slide_3():
    img = Image.new('RGBA', (W, H), (248, 247, 242, 255))
    draw = ImageDraw.Draw(img)

    draw_header(
        draw, 2,
        "安全防護與冪等性：企業級配置守門員",
        "非破壞性寫入、智慧辨識自訂規則，確保多次重複執行絕不毀損既有專案代碼",
        pill_prefix="SAFETY & IDEMPOTENCY"
    )

    # Top Half: 4 Safety Pillars (2x2 Grid)
    # Row 1: y=100, h=152 | Row 2: y=262, h=152
    # Left: x=48, w=630 | Right: x=698, w=630
    safety_cards = [
        (48, 100, 630, 152,
         "防護機制 1", (254, 243, 199), (252, 211, 77), (180, 83, 9),
         "◆ 擁有者標籤保護 (Owner Tag)",
         "產生的檔案均附帶 <!-- generated by k6 x agent --> 識別標記。",
         "重複執行 init 時，系統自動比對標籤，精確區隔系統自動產生與工程師客製內容，安全無虞。"),
        (698, 100, 630, 152,
         "防護機制 2", (239, 246, 255), (191, 219, 254), (37, 99, 235),
         "◆ 寫入前安全預覽 (--dry-run)",
         "支援在真正寫入磁碟前加上 --dry-run 旗標。",
         "終端機會清晰預覽列印出所有將新增、修改或保留的檔案清單與完整路徑，完全零副作用。"),
        (48, 262, 630, 152,
         "防護機制 3", (250, 245, 255), (233, 213, 255), (147, 51, 234),
         "◆ 客製保護與智慧略過 (Custom Guard)",
         "偵測到使用者已手動修改過的檔案時，系統會自動跳過保護，絕不覆蓋你的客製規則；",
         "唯有在需要官方版本升級時，才需在命令後加上 --force 顯式同步，把控制權交還開發者。"),
        (698, 262, 630, 152,
         "防護機制 4", (236, 253, 245), (167, 243, 208), (5, 150, 105),
         "◆ 零全域污染與 Git 友善 (Git Friendly)",
         "所有產出檔案均收斂於專案本地工作區目錄內（如 .cursor/rules 與 .mcp.json），",
         "不污染全域環境，變更乾淨無雜訊，非常適合團隊納入 Pull Request 進行版本審計。")
    ]

    for cx, cy, cw, ch, pill_txt, p_bg, p_bd, p_fg, title, l1, l2 in safety_cards:
        draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=8, fill=(255, 255, 255), outline=(226, 232, 240), width=1)
        draw.rounded_rectangle([cx + 14, cy + 12, cx + 14 + 76, cy + 12 + 20], radius=4, fill=p_bg, outline=p_bd, width=1)
        draw.text((cx + 19, cy + 14), pill_txt, font=f_pill, fill=p_fg)
        draw.text((cx + 98, cy + 13), title, font=f_card_title, fill=(15, 23, 42))
        draw.text((cx + 18, cy + 48), l1, font=f_body_reg, fill=(71, 85, 105))
        draw.text((cx + 18, cy + 74), l2, font=f_body_reg, fill=(71, 85, 105))

    # Bottom Half: Decision Logic Box (Left) & Rule Snippet Box (Right)
    # y=424, h=210
    # Left: x=48, w=630 | Right: x=698, w=630
    d_x, d_y, d_w, d_h = 48, 424, 630, 210
    draw.rounded_rectangle([d_x, d_y, d_x + d_w, d_y + d_h], radius=8, fill=(255, 255, 255), outline=(226, 232, 240), width=1)
    draw.rounded_rectangle([d_x + 14, d_y + 12, d_x + 14 + 76, d_y + 12 + 20], radius=4, fill=(240, 253, 250), outline=(94, 234, 212), width=1)
    draw.text((d_x + 19, d_y + 14), "決策邏輯", font=f_pill, fill=(13, 148, 136))
    draw.text((d_x + 98, d_y + 13), "k6 x agent 執行衝突與覆蓋防護決策樹", font=f_card_title, fill=(15, 23, 42))

    steps = [
        ("1. 觸發指令", "$ k6 x agent init <editor> 開始掃描專案目標路徑"),
        ("2. 檢查檔案", "檔案不存在 -> 立即建立新檔並標記 Owner Tag 註解"),
        ("3. 標籤比對", "檔案已存在 -> 比對是否含有 <!-- generated by k6 x agent -->"),
        ("4. 衝突裁決", "含有標籤 -> 安全同步更新；不含標籤（已修改） -> 🛡️ 自動跳過保護！")
    ]
    sy = d_y + 44
    for st, sd in steps:
        draw.text((d_x + 18, sy), f"• {st}：", font=f_body_bold, fill=(79, 70, 229))
        draw.text((d_x + 118, sy), sd, font=f_body_reg, fill=(51, 65, 85))
        sy += 38

    # Right: Dark Terminal Code Snippet showing the exact Owner Tag
    r_x, r_y, r_w, r_h = 698, 424, 630, 210
    draw.rounded_rectangle([r_x, r_y, r_x + r_w, r_y + r_h], radius=8, fill=(15, 23, 42))
    
    # Header dots
    draw.ellipse([r_x + 14, r_y + 12, r_x + 24, r_y + 22], fill=(239, 68, 68))
    draw.ellipse([r_x + 30, r_y + 12, r_x + 40, r_y + 22], fill=(245, 158, 11))
    draw.ellipse([r_x + 46, r_y + 12, r_x + 56, r_y + 22], fill=(34, 197, 94))
    draw.text((r_x + 70, r_y + 10), "規格檔案範例 ── .cursor/rules/k6-load-test.mdc", font=f_footer, fill=(148, 163, 184))

    code_lines = [
        ("<!-- generated by k6 x agent - DO NOT EDIT THIS BLOCK -->", (251, 191, 36)),
        ("---", (148, 163, 184)),
        ("description: \"Execute standard production-grade load tests with k6\"", (56, 189, 248)),
        ("globs: [\"**/*.js\", \"**/*.ts\"]", (56, 189, 248)),
        ("---", (148, 163, 184)),
        ("# k6 Load Testing Best Practices", (52, 211, 153)),
        ("- Use http.url tag to prevent Prometheus high-cardinality OOM.", (226, 232, 240)),
        ("- Always run 1 VU smoke test before ramping up concurrent VUs.", (226, 232, 240))
    ]
    cy = r_y + 36
    for line_text, col in code_lines:
        draw.text((r_x + 18, cy), line_text, font=f_term_out, fill=col)
        cy += 20

    # Bottom Banner
    foot_x, foot_y, foot_w, foot_h = 48, 650, 930, 86
    draw.rounded_rectangle([foot_x, foot_y, foot_x + foot_w, foot_y + foot_h], radius=8, fill=(255, 255, 255), outline=(203, 213, 225), width=1)
    draw.rounded_rectangle([foot_x + 14, foot_y + 12, foot_x + 78, foot_y + 34], radius=4, fill=(240, 253, 250), outline=(94, 234, 212), width=1)
    draw.text((foot_x + 20, foot_y + 15), "核心價值", font=f_pill, fill=(13, 148, 136))
    draw.text((foot_x + 88, foot_y + 14), "安全標籤機制讓你在敏捷迭代中享受 AI 自動化的便利，同時對現有專案保有 100% 控制權！", font=f_body_bold, fill=(30, 41, 59))
    draw.text((foot_x + 18, foot_y + 48), "下一頁：我們將實際檢驗常用的 CLI 命令速查，以及它所原生支援的 6 大熱門 AI 編輯器環境！", font=f_footer, fill=(100, 116, 139))

    paste_branding(img)
    save_slide(img, 3)

# ==============================================================================
# SLIDE 4: 常用 CLI 指令速查與 6 大編輯器環境適配 (CLI Workflow & Editor Matrix)
# ==============================================================================
def create_slide_4():
    img = Image.new('RGBA', (W, H), (248, 247, 242, 255))
    draw = ImageDraw.Draw(img)

    draw_header(
        draw, 3,
        "常用 CLI 指令速查與 6 大編輯器環境適配",
        "在專案根目錄終端機執行直覺的子命令，一鍵適配主流 AI 代碼編輯器與自主 Agent 環境",
        pill_prefix="ENVIRONMENT & CLI"
    )

    c1_x, c1_y, c1_w, c1_h = 48, 100, 634, 532
    draw.rounded_rectangle([c1_x, c1_y, c1_x + c1_w, c1_y + c1_h], radius=10, fill=(255, 255, 255), outline=(226, 232, 240), width=1)
    draw.rounded_rectangle([c1_x + 18, c1_y + 14, c1_x + 18 + 92, c1_y + 14 + 22], radius=4, fill=(209, 250, 229), outline=(167, 243, 208), width=1)
    draw.text((c1_x + 24, c1_y + 17), "終端快速上手", font=f_pill, fill=(4, 120, 87))
    draw.text((c1_x + 120, c1_y + 15), "常用 CLI 命令速查與情境解析", font=f_h2, fill=(15, 23, 42))

    # Big Terminal Box
    term_x, term_y, term_w, term_h = c1_x + 18, c1_y + 48, c1_w - 36, 464
    draw.rounded_rectangle([term_x, term_y, term_x + term_w, term_y + term_h], radius=8, fill=(15, 23, 42))
    
    # Header dots
    draw.ellipse([term_x + 14, term_y + 12, term_x + 24, term_y + 22], fill=(239, 68, 68))
    draw.ellipse([term_x + 30, term_y + 12, term_x + 40, term_y + 22], fill=(245, 158, 11))
    draw.ellipse([term_x + 46, term_y + 12, term_x + 56, term_y + 22], fill=(34, 197, 94))
    draw.text((term_x + 70, term_y + 10), "bash ── 在 k6 專案根目錄執行", font=f_footer, fill=(148, 163, 184))

    code_sections = [
        ("# 1. 為指定編輯器進行初始化 (例如 Cursor 或 Claude Code)",
         "k6 x agent init cursor\nk6 x agent init claude-code",
         (56, 189, 248)),
        ("# 2. 一鍵初始化所有支援的編輯器（團隊協作最佳實踐）",
         "k6 x agent init --all",
         (52, 211, 153)),
        ("# 3. 預覽將產生的檔案與路徑（安全檢查，不安裝）",
         "k6 x agent init --dry-run cursor",
         (251, 191, 36)),
        ("# 4. 強制覆蓋重置所有技能與 MCP 設定（版本升級）",
         "k6 x agent init --force cursor",
         (248, 113, 113)),
        ("# 5. 檢查當前專案的 AI 技能與 MCP 伺服器連線狀態",
         "k6 x agent status",
         (192, 132, 252)),
        ("# 6. 查看內建的所有 AI 技能清單與詳細描述",
         "k6 x agent skills list",
         (244, 114, 182))
    ]

    ty = term_y + 36
    for comment, cmd, col in code_sections:
        draw.text((term_x + 16, ty), comment, font=f_term_comment, fill=(148, 163, 184))
        ty += 18
        for line in cmd.split('\n'):
            draw.text((term_x + 16, ty), f"$ {line}", font=f_term_cmd, fill=col)
            ty += 21
        ty += 8

    # Right Column: 6 大支援編輯器
    c2_x, c2_y, c2_w, c2_h = 694, 100, 634, 532
    draw.rounded_rectangle([c2_x, c2_y, c2_x + c2_w, c2_y + c2_h], radius=10, fill=(255, 255, 255), outline=(226, 232, 240), width=1)
    draw.rounded_rectangle([c2_x + 18, c2_y + 14, c2_x + 18 + 92, c2_y + 14 + 22], radius=4, fill=(224, 231, 255), outline=(199, 210, 254), width=1)
    draw.text((c2_x + 24, c2_y + 17), "環境支援度", font=f_pill, fill=(67, 56, 202))
    draw.text((c2_x + 120, c2_y + 15), "原生支援的 6 大熱門 AI 編輯器與 Agent 目標", font=f_h2, fill=(15, 23, 42))

    editors_detail = [
        ("Cursor", "cursor", "支援 .cursor/rules/*.mdc 與 .cursor/mcp.json，自然語言無縫調度 k6 工具", (147, 51, 234), (250, 245, 255)),
        ("Claude Code", "claude-code", "Anthropic 官方終端 Agent CLI，完美支援 skills 技能包與本地工具鏈", (249, 115, 22), (255, 247, 237)),
        ("GitHub Copilot", "vscode-copilot", "微軟 VS Code 原生工作區，自動配置 .vscode/mcp.json，IDE 體驗極致流暢", (37, 99, 235), (239, 246, 255)),
        ("OpenAI Codex CLI", "codex-cli", "OpenAI 原生終端工作流，支援命令行環境下的全自動逆向生成與壓測驗證", (16, 185, 129), (236, 253, 245)),
        ("OpenCode", "opencode", "開源終端 AI 助手環境，提供完全開源自主可控的 Agent 壓測配置方案", (217, 119, 6), (254, 243, 199)),
        ("Cline", "cline", "VS Code 開源自主 Agent 插件，支援檔案讀寫、終端執行與 MCP 閉環反饋", (225, 29, 72), (255, 241, 242))
    ]

    ey = c2_y + 48
    for name, cmd_arg, desc, tag_col, bg_col in editors_detail:
        draw.rounded_rectangle([c2_x + 16, ey, c2_x + c2_w - 16, ey + 72], radius=6, fill=bg_col, outline=(226, 232, 240), width=1)
        
        draw.rounded_rectangle([c2_x + 26, ey + 10, c2_x + 26 + 140, ey + 32], radius=4, fill=(255, 255, 255), outline=tag_col, width=1)
        draw.text((c2_x + 34, ey + 13), name, font=f_card_title, fill=tag_col)
        
        draw.text((c2_x + 176, ey + 14), f"命令引數: {cmd_arg}", font=f_term_cmd, fill=(100, 116, 139))
        draw.text((c2_x + 26, ey + 42), desc, font=f_body_reg, fill=(51, 65, 85))
        ey += 78

    # Bottom Banner
    foot_x, foot_y, foot_w, foot_h = 48, 650, 930, 86
    draw.rounded_rectangle([foot_x, foot_y, foot_x + foot_w, foot_y + foot_h], radius=8, fill=(255, 255, 255), outline=(203, 213, 225), width=1)
    draw.rounded_rectangle([foot_x + 14, foot_y + 12, foot_x + 78, foot_y + 34], radius=4, fill=(240, 253, 250), outline=(94, 234, 212), width=1)
    draw.text((foot_x + 20, foot_y + 15), "協同優勢", font=f_pill, fill=(13, 148, 136))
    draw.text((foot_x + 88, foot_y + 14), "無論團隊成員偏好 VS Code、Cursor 還是終端 Agent，執行 init --all 即可完全抹平環境差異！", font=f_body_bold, fill=(30, 41, 59))
    draw.text((foot_x + 18, foot_y + 48), "下一頁：我們將逐一深度剖析 k6 x agent 內建的 5 大專業 AI 技能庫！", font=f_footer, fill=(100, 116, 139))

    paste_branding(img)
    save_slide(img, 4)

# ==============================================================================
# SLIDE 5: 內建 5 大專業 AI 技能庫深度剖析 (5 Bundled Skills Deep Dive)
# ==============================================================================
def create_slide_5():
    img = Image.new('RGBA', (W, H), (248, 247, 242, 255))
    draw = ImageDraw.Draw(img)

    draw_header(
        draw, 4,
        "內建 5 大 AI 技能深度剖析：專家級壓測工作流",
        "從測試策略、負載爬坡、冒煙檢驗、前端真實渲染到 E2E 腳本轉譯的全鏈路覆蓋",
        pill_prefix="BUNDLED SKILLS"
    )

    skills_data = [
        ("k6-test-planner", "壓測策略規劃",
         "分析 API 架構、端點特徵與預期吞吐量，自動規劃流量模型、計算並發 VU 與爬坡階段，並設計合理的 P95 延遲門檻與 SLO 門禁規範。",
         "\"plan tests for order service\", \"design a test strategy\", \"recommend VU and RPS\"",
         (79, 70, 229), (238, 242, 255)),
        ("k6-load-test", "生產級負載壓測",
         "生成具備 stages 階梯爬坡、arrival-rate 開放模型與動態 Token 關聯的生產級標準腳本，嚴格遵循 SharedArray 跨 VU 記憶體共享最佳實踐。",
         "\"write a load test\", \"stress test this endpoint\", \"soak test with 500 RPS\"",
         (124, 58, 237), (245, 243, 255)),
        ("k6-smoke-test", "極速冒煙檢驗",
         "以極低資源開銷（1 到 2 個 VU）在 5 秒內快速驗證 API 基礎可用性、HTTP 200/201 與 Check 軟斷言，適合作為 CI/CD 門禁的第一道快速防線。",
         "\"write a smoke test\", \"quick sanity check\", \"verify health check endpoint\"",
         (13, 148, 136), (240, 253, 250)),
        ("k6-browser-test", "前端真實渲染",
         "透過 k6/browser 驅動真實無頭 Chromium，量測 LCP、CLS、INP 等 Core Web Vitals 前端性能指標，並自動注入 finally page.close() 軍規防護。",
         "\"browser test for login UI\", \"measure Web Vitals\", \"hybrid 99:1 test\"",
         (217, 119, 6), (254, 243, 199)),
        ("k6-playwright-converter", "Playwright 轉譯",
         "讀取現有的 Playwright 或 Puppeteer E2E 功能測試代碼，自動提取選擇器與業務流程，無痛轉譯為相容 k6 高併發架構的混合壓測腳本。",
         "\"convert Playwright script\", \"migrate E2E test to k6\", \"transform ui test\"",
         (225, 29, 72), (255, 241, 242))
    ]

    sy = 100
    for skill_id, skill_badge, desc, prompt_eg, col, bg in skills_data:
        draw.rounded_rectangle([48, sy, 48 + 1280, sy + 98], radius=8, fill=(255, 255, 255), outline=(226, 232, 240), width=1)
        
        # Skill Badge Left Box
        draw.rounded_rectangle([62, sy + 14, 62 + 220, sy + 44], radius=6, fill=bg, outline=col, width=1)
        draw.text((74, sy + 20), skill_id, font=f_term_cmd, fill=col)
        
        draw.rounded_rectangle([62 + 230, sy + 16, 62 + 230 + 110, sy + 42], radius=4, fill=(248, 250, 252), outline=(203, 213, 225), width=1)
        draw.text((62 + 238, sy + 21), f"◆ {skill_badge}", font=f_pill, fill=(51, 65, 85))

        # Description
        draw.text((420, sy + 18), desc, font=f_body_reg, fill=(30, 41, 59))

        # Prompt trigger bar
        draw.rounded_rectangle([62, sy + 56, 48 + 1280 - 16, sy + 88], radius=4, fill=(248, 250, 252), outline=(226, 232, 240), width=1)
        draw.text((74, sy + 64), "💬 常見自然語言觸發詞：", font=f_body_bold, fill=(71, 85, 105))
        draw.text((236, sy + 64), prompt_eg, font=f_term_out, fill=col)

        sy += 108

    # Bottom Banner
    foot_x, foot_y, foot_w, foot_h = 48, 650, 930, 86
    draw.rounded_rectangle([foot_x, foot_y, foot_x + foot_w, foot_y + foot_h], radius=8, fill=(255, 255, 255), outline=(203, 213, 225), width=1)
    draw.rounded_rectangle([foot_x + 14, foot_y + 12, foot_x + 78, foot_y + 34], radius=4, fill=(240, 253, 250), outline=(94, 234, 212), width=1)
    draw.text((foot_x + 20, foot_y + 15), "技能協同", font=f_pill, fill=(13, 148, 136))
    draw.text((foot_x + 88, foot_y + 14), "5 大技能相輔相成：先規劃策略、再產出冒煙、擴展至高負載與前端渲染，建構全視角壓測工程！", font=f_body_bold, fill=(30, 41, 59))
    draw.text((foot_x + 18, foot_y + 48), "下一頁：我們將檢驗企業導入實作 Checklist 與 AI 壓測工程化最佳實踐！", font=f_footer, fill=(100, 116, 139))

    paste_branding(img)
    save_slide(img, 5)

# ==============================================================================
# SLIDE 6: 企業導入實作 Checklist & 最佳實踐 (Enterprise Takeaways)
# ==============================================================================
def create_slide_6():
    img = Image.new('RGBA', (W, H), (248, 247, 242, 255))
    draw = ImageDraw.Draw(img)

    draw_header(
        draw, 5,
        "企業導入實作 Checklist：AI 壓測工程化最佳實踐",
        "將 AI Agent 融入團隊研發管線、建立腳本審計、記憶體防護與閉環自癒機制",
        pill_prefix="ENTERPRISE CHECKLIST"
    )

    # 4 Takeaways Cards (2x2 Grid)
    # Col 1: x=48, w=630 | Col 2: x=698, w=630
    # Row 1: y=100, h=256 | Row 2: y=372, h=256
    takeaways = [
        (48, 100, 630, 256,
         "維度 1", (238, 242, 255), (199, 210, 254), (79, 70, 229),
         "配置治理與團隊協作 (Configuration Governance)",
         [
             ("Git 版本控管審計", "將 .cursor/rules 或 CLAUDE.md 納入 Git 版控，全團隊共享統一壓測標準。"),
             ("環境敏感資訊分離", "Token 與私有 API 網址透過環境變數注入，嚴禁寫入 AI 規則或公開設定。"),
             ("跨編輯器配置同步", "定期執行 k6 x agent init --all，確保跨職能開發者在不同工具間體驗對齊。"),
             ("CI/CD 狀態檢核", "在 CI Pipeline 整合 k6 x agent status，確保 Runner 環境與本地配置一致。")
         ]),
        (698, 100, 630, 256,
         "維度 2", (209, 250, 229), (167, 243, 208), (5, 150, 105),
         "AI 閉環自癒工程 (Agentic Self-Healing Loop)",
         [
             ("AST 靜態語法預檢", "生成腳本後，AI 必須自動調用 validate_script 抓出未定義變數與生命週期錯誤。"),
             ("1 VU 冒煙閉環先驗", "嚴格落實「大併發前先跑 1 VU 冒煙」，確認 HTTP 200 與 check 通過再壓測。"),
             ("日誌結構化解析", "AI 讀取 k6 終端報錯（如 401 Unauthorized、Thresholds 破功），自主迭代修正。"),
             ("減少手動排錯成本", "將傳統手動除錯 30 分鐘流程縮短為秒級 AI 閉環自癒，大幅加速交付。")
         ]),
        (48, 372, 630, 256,
         "維度 3", (254, 243, 199), (252, 211, 77), (180, 83, 9),
         "高基數記憶體炸彈防護 (Memory Leak Prevention)",
         [
             ("強制 http.url 標籤", "AI 技能規則嚴格禁止以模板字串拼接動態 ID（如 /users/${id}）。"),
             ("防範維度爆炸 (OOM)", "動態端點強制經由 http.url 標籤函數聚合，阻斷 Prometheus 時間序列爆炸。"),
             ("SharedArray 記憶體優化", "大量測試帳號與參數強制使用 SharedArray 載入，跨 VU 共享不膨脹。"),
             ("資源洩漏軍規防護", "前端瀏覽器測試強制包含 finally { await page.close() }，避免殭屍行程。")
         ]),
        (698, 372, 630, 256,
         "維度 4", (240, 253, 250), (153, 246, 228), (13, 148, 136),
         "官方生態系資源與持續演進 (Official Ecosystem)",
         [
             ("GitHub 官方開源專案", "github.com/grafana/xk6-subcommand-agent (開源倉庫與社群支援)。"),
             ("Grafana 官方配置指南", "grafana.com/docs/k6/latest/set-up/configure-ai-assistant/bootstrap-with-k6-x-agent/"),
             ("定期顯式更新升級", "每季執行 k6 x agent init --force，同步 Grafana 官方最新進化之技能包。"),
             ("無縫銜接可觀測性", "搭配 Chapter 5 的 Prometheus Remote Write 與 Grafana Dashboard 達成全鏈路監控。")
         ])
    ]

    for cx, cy, cw, ch, pill_txt, p_bg, p_bd, p_fg, title, bullets in takeaways:
        draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=10, fill=(255, 255, 255), outline=(226, 232, 240), width=1)
        
        draw.rounded_rectangle([cx + 14, cy + 12, cx + 14 + 68, cy + 12 + 20], radius=4, fill=p_bg, outline=p_bd, width=1)
        draw.text((cx + 19, cy + 14), pill_txt, font=f_pill, fill=p_fg)
        draw.text((cx + 90, cy + 13), title, font=f_card_title, fill=(15, 23, 42))

        by = cy + 46
        for b_title, b_desc in bullets:
            draw.text((cx + 16, by), f"• {b_title}：", font=f_body_bold, fill=p_fg)
            draw.text((cx + 168, by), b_desc, font=f_body_reg, fill=(71, 85, 105))
            by += 48

    # Bottom Banner
    foot_x, foot_y, foot_w, foot_h = 48, 650, 930, 86
    draw.rounded_rectangle([foot_x, foot_y, foot_x + foot_w, foot_y + foot_h], radius=8, fill=(255, 255, 255), outline=(203, 213, 225), width=1)
    draw.rounded_rectangle([foot_x + 14, foot_y + 12, foot_x + 78, foot_y + 34], radius=4, fill=(240, 253, 250), outline=(94, 234, 212), width=1)
    draw.text((foot_x + 20, foot_y + 15), "最佳實踐", font=f_pill, fill=(13, 148, 136))
    draw.text((foot_x + 88, foot_y + 14), "遵循上述 Checklist，讓 AI Agent 成為團隊中可靠、安全且高效的效能測試工程夥伴！", font=f_body_bold, fill=(30, 41, 59))
    draw.text((foot_x + 18, foot_y + 48), "下一頁：進入本章最後一哩路 ── 隨堂實作練習指引 (Hands-on Practice)！", font=f_footer, fill=(100, 116, 139))

    paste_branding(img)
    save_slide(img, 6)

# ==============================================================================
# SLIDE 7: 隨堂實作練習指引 (Hands-on Practice & Lab Guide)
# ==============================================================================
def create_slide_7():
    img = Image.new('RGBA', (W, H), (248, 247, 242, 255))
    draw = ImageDraw.Draw(img)

    draw_header(
        draw, 6,
        "隨堂實作練習指引：AI 輔助壓測三部曲",
        "請依序完成三大實戰任務，親身體驗 k6 x agent 的一鍵配置與 AI 輔助壓測閉環",
        pill_prefix="HANDS-ON PRACTICE"
    )

    tasks_data = [
        ("任務一：一鍵初始化本地 AI 編輯器與狀態檢核",
         "為你的主力編輯器（例如 Cursor 或 Claude Code）配置 k6 技能與 MCP 伺服器，並驗證連線健康度。",
         "$ k6 x agent init cursor       # 或使用 k6 x agent init claude-code\n$ k6 x agent status            # 檢查 MCP 與 5 大技能連線狀態",
         "驗證標準：.cursor/rules/ 下產生 5 個 .mdc 規則檔，且 .cursor/mcp.json 正確註冊 k6 x mcp。",
         (79, 70, 229), (238, 242, 255)),
        ("任務二：AI 逆向生成 QuickPizza 冒煙測試並閉環自癒",
         "利用內建 k6-smoke-test 技能與 MCP 工具，逆向生成冒煙測試並由 AI 本機跑通 1 VU 冒煙。",
         "Prompt: \"針對 QuickPizza 的 /api/pizza 端點撰寫 1 VU 冒煙測試腳本，包含 check 斷言與\n         http.url 標籤，並請使用 validate_script 驗證腳本合法性。\"",
         "驗證標準：AI 產生合規腳本並調用 validate_script 驗證通過，無語法錯誤與動態 URL 拼接。",
         (5, 150, 105), (209, 250, 229)),
        ("任務三：Playwright 登入測試無痛轉譯為 k6 混合壓測",
         "利用 k6-playwright-converter 技能將 E2E 測試升級為具備真實瀏覽器性能量測的混合壓測腳本。",
         "Prompt: \"請將這段 Playwright 登入測試轉譯為 k6 browser 腳本，加入 finally page.close()\n         軍規保護，並設定 99:1 混合流量模型。\"",
         "驗證標準：產出標準 k6/browser 語法，加入 try...finally 關閉瀏覽器，並具備 Web Vitals 採樣。",
         (217, 119, 6), (254, 243, 199))
    ]

    ty = 100
    for title, goal, cmd, criteria, tag_col, bg_col in tasks_data:
        draw.rounded_rectangle([48, ty, 48 + 1280, ty + 168], radius=8, fill=(255, 255, 255), outline=(226, 232, 240), width=1)
        
        # Pill & Title
        draw.rounded_rectangle([64, ty + 12, 64 + 90, ty + 34], radius=4, fill=bg_col, outline=tag_col, width=1)
        draw.text((70, ty + 15), "實戰任務", font=f_pill, fill=tag_col)
        draw.text((166, ty + 14), title, font=f_card_title, fill=(15, 23, 42))

        # Goal
        draw.text((64, ty + 42), f"• 任務目標：{goal}", font=f_body_reg, fill=(71, 85, 105))

        # Terminal Box / Prompt Box
        box_x, box_y, box_w, box_h = 64, ty + 66, 1280 - 32, 54
        draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=6, fill=(15, 23, 42))
        
        cy = box_y + 8
        for line in cmd.split('\n'):
            draw.text((box_x + 14, cy), line, font=f_term_cmd, fill=(52, 211, 153) if line.startswith('$') else (241, 245, 249))
            cy += 19

        # Criteria
        draw.text((64, ty + 130), f"✔ {criteria}", font=f_body_bold, fill=tag_col)

        ty += 180

    # Bottom Banner
    foot_x, foot_y, foot_w, foot_h = 48, 650, 930, 86
    draw.rounded_rectangle([foot_x, foot_y, foot_x + foot_w, foot_y + foot_h], radius=8, fill=(255, 255, 255), outline=(203, 213, 225), width=1)
    draw.rounded_rectangle([foot_x + 14, foot_y + 12, foot_x + 78, foot_y + 34], radius=4, fill=(240, 253, 250), outline=(94, 234, 212), width=1)
    draw.text((foot_x + 20, foot_y + 15), "課程通關", font=f_pill, fill=(13, 148, 136))
    draw.text((foot_x + 88, foot_y + 14), "恭喜完成 Chapter 6 全章節！你已掌握了現代化 AI Agent 壓測工程的核心心智模型與實戰技能！", font=f_body_bold, fill=(30, 41, 59))
    draw.text((foot_x + 18, foot_y + 48), "立即打開你的終端機，執行 k6 x agent init，開始你的 AI 效能工程新體驗吧！", font=f_footer, fill=(100, 116, 139))

    paste_branding(img)
    save_slide(img, 7)

def main():
    os.makedirs('k6/slides/assets/Ch6', exist_ok=True)
    create_slide_1()
    create_slide_2()
    create_slide_3()
    create_slide_4()
    create_slide_5()
    create_slide_6()
    create_slide_7()
    print("All 7 Ch6 slides generated successfully!")

if __name__ == '__main__':
    main()
