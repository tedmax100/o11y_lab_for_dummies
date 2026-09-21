#!/usr/bin/env python3
"""
Generate 3 high-definition, beautifully spaced slide images for `k6 x agent`:
- Slide 1: 核心概念、自動化雙引擎與安全冪等性 (Core Concept & Automation Engines)
- Slide 2: 常用 CLI 指令速查與 6 大編輯器支援 (CLI Commands & Supported Editors)
- Slide 3: 內建 5 大專業 AI 技能全解析與官方資源 (5 Bundled Skills & Ecosystem)
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

f_title = ImageFont.truetype(FONT_TC_BOLD, 26)
f_subtitle = ImageFont.truetype(FONT_TC_REG, 13.5)
f_pill = ImageFont.truetype(FONT_TC_BOLD, 11.5)
f_h2 = ImageFont.truetype(FONT_TC_BOLD, 15)
f_card_title = ImageFont.truetype(FONT_TC_BOLD, 13.5)
f_body_bold = ImageFont.truetype(FONT_TC_BOLD, 11.5)
f_body_reg = ImageFont.truetype(FONT_TC_REG, 11)
f_term_comment = ImageFont.truetype(FONT_TC_REG, 10.5)
f_term_cmd = ImageFont.truetype(FONT_MONO_BOLD, 11.5)
f_link_label = ImageFont.truetype(FONT_TC_BOLD, 10.5)
f_link_url = ImageFont.truetype(FONT_EN_REG, 10.5)
f_footer = ImageFont.truetype(FONT_TC_REG, 10)

def draw_header(draw, part_num, title, subtitle):
    badge_x, badge_y = 48, 30
    pill_text = f"AI SUBCOMMAND EXTENSION · PART {part_num}"
    pill_bbox = draw.textbbox((0, 0), pill_text, font=f_pill)
    pill_w = pill_bbox[2] - pill_bbox[0] + 18
    
    draw.rounded_rectangle([badge_x, badge_y, badge_x + pill_w, badge_y + 25], radius=6, fill=(238, 242, 255), outline=(199, 210, 254), width=1)
    draw.text((badge_x + 9, badge_y + 4), pill_text, font=f_pill, fill=(79, 70, 229))

    title_x = badge_x + pill_w + 16
    draw.text((title_x, badge_y - 2), title, font=f_title, fill=(15, 23, 42))

    sub_y = badge_y + 36
    draw.text((badge_x, sub_y), subtitle, font=f_subtitle, fill=(71, 85, 105))

def paste_branding(img):
    logo_path = '/tmp/k6_grafana_full_branding.png'
    if os.path.exists(logo_path):
        logo_img = Image.open(logo_path)
        img.paste(logo_img, (990, 655))


# ==============================================================================
# SLIDE 1: 核心概念、自動化雙引擎與安全冪等性
# ==============================================================================
def create_slide_1():
    img = Image.new('RGBA', (W, H), (248, 247, 242, 255))
    draw = ImageDraw.Draw(img)

    draw_header(
        draw, 1,
        "k6 x agent (一) ：核心概念、自動化雙引擎與安全防護",
        "Grafana k6 原生 AI 子命令擴充套件 (xk6-subcommand-agent) ── 專為一鍵配置 AI 編輯器與 Agent 壓測流而設計"
    )

    # Left Column: 雙大核心自動化引擎 (x=48, w=634)
    # Right Column: 安全防護與冪等性 (x=694, w=634)

    # Left Card 1: 引擎一 - 自動安裝內建技能
    c1_x, c1_y, c1_w, c1_h = 48, 104, 634, 256
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
    py = c1_y + 48
    for term, l1, l2 in points_1:
        draw.text((c1_x + 20, py), f"• {term}：", font=f_body_bold, fill=(79, 70, 229))
        draw.text((c1_x + 120, py), l1, font=f_body_reg, fill=(71, 85, 105))
        draw.text((c1_x + 120, py + 18), l2, font=f_body_reg, fill=(71, 85, 105))
        py += 48

    # Left Card 2: 引擎二 - 自動註冊 k6 MCP 伺服器
    c2_y = 372
    draw.rounded_rectangle([c1_x, c2_y, c1_x + c1_w, c2_y + c1_h], radius=10, fill=(255, 255, 255), outline=(226, 232, 240), width=1)
    draw.rounded_rectangle([c1_x + 18, c2_y + 14, c1_x + 18 + 84, c2_y + 14 + 22], radius=4, fill=(209, 250, 229), outline=(167, 243, 208), width=1)
    draw.text((c1_x + 24, c2_y + 17), "自動化引擎 2", font=f_pill, fill=(5, 150, 105))
    draw.text((c1_x + 112, c2_y + 15), "自動註冊 k6 MCP 伺服器 (Auto-Register MCP)", font=f_h2, fill=(15, 23, 42))

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
    py = c2_y + 48
    for term, l1, l2 in points_2:
        draw.text((c1_x + 20, py), f"• {term}：", font=f_body_bold, fill=(5, 150, 105))
        draw.text((c1_x + 124, py), l1, font=f_body_reg, fill=(71, 85, 105))
        draw.text((c1_x + 124, py + 18), l2, font=f_body_reg, fill=(71, 85, 105))
        py += 48

    # Right Card: 安全防護與工程冪等性
    c3_x, c3_y, c3_w, c3_h = 694, 104, 634, 524
    draw.rounded_rectangle([c3_x, c3_y, c3_x + c3_w, c3_y + c3_h], radius=10, fill=(255, 255, 255), outline=(226, 232, 240), width=1)
    draw.rounded_rectangle([c3_x + 18, c3_y + 14, c3_x + 18 + 92, c3_y + 14 + 22], radius=4, fill=(254, 243, 199), outline=(252, 211, 77), width=1)
    draw.text((c3_x + 24, c3_y + 17), "工程安全設計", font=f_pill, fill=(180, 83, 9))
    draw.text((c3_x + 120, c3_y + 15), "安全防護與冪等性機制 (Safety & Idempotency)", font=f_h2, fill=(15, 23, 42))

    safety_cards = [
        ("◆ 擁有者標籤保護 (Owner Tag)",
         "產生的檔案均附帶擁有者識別標記。重複執行 init 時，",
         "系統自動比對變更，絕不覆蓋任何手動修改過的內容，安全無憂。",
         (245, 158, 11), (254, 243, 199)),
        ("◆ 寫入前安全預覽 (--dry-run)",
         "支援在真正寫入磁碟前加上 --dry-run 旗標。終端機會清晰",
         "預覽列印出所有將新增、修改或保留的檔案清單與完整路徑。",
         (59, 130, 246), (239, 246, 255)),
        ("◆ 顯式強制更新覆蓋 (--force)",
         "唯有當官方發布重大更新或需要全面重置技能規範時，",
         "才需在命令後顯式加上 --force 參數，把寫入控制權徹底交還開發者。",
         (168, 85, 247), (250, 245, 255)),
        ("◆ 零全域污染與 Git 友善",
         "所有產出的技能檔與設定皆收斂於專案本地工作區目錄內",
         "（如 .cursor/rules 與 .vscode/），不污染全域環境，並隨 Git 版控。",
         (16, 185, 129), (236, 253, 245))
    ]

    sy = c3_y + 48
    for title, l1, l2, col, bg in safety_cards:
        draw.rounded_rectangle([c3_x + 18, sy, c3_x + c3_w - 18, sy + 106], radius=8, fill=bg, outline=col, width=1)
        draw.text((c3_x + 28, sy + 14), title, font=f_card_title, fill=(15, 23, 42))
        draw.text((c3_x + 28, sy + 44), l1, font=f_body_reg, fill=(71, 85, 105))
        draw.text((c3_x + 28, sy + 66), l2, font=f_body_reg, fill=(71, 85, 105))
        sy += 116

    # Bottom Banner
    foot_x, foot_y, foot_w, foot_h = 48, 664, 930, 72
    draw.rounded_rectangle([foot_x, foot_y, foot_x + foot_w, foot_y + foot_h], radius=8, fill=(255, 255, 255), outline=(203, 213, 225), width=1)
    draw.rounded_rectangle([foot_x + 14, foot_y + 12, foot_x + 78, foot_y + 34], radius=4, fill=(240, 253, 250), outline=(94, 234, 212), width=1)
    draw.text((foot_x + 20, foot_y + 15), "核心價值", font=f_pill, fill=(13, 148, 136))
    draw.text((foot_x + 88, foot_y + 14), "告別過去手動翻找 JSON 與手寫 Rules 的繁重負擔，執行一次命令即可在數秒內打通 AI 與 k6！", font=f_body_bold, fill=(30, 41, 59))
    draw.text((foot_x + 18, foot_y + 44), "下一頁：我們將實際檢驗常用的 CLI 命令速查，以及它所原生支援的 6 大熱門 AI 編輯器環境！", font=f_footer, fill=(100, 116, 139))

    paste_branding(img)
    img.convert('RGB').save('k6/slides/k6_x_agent_slide_1.png', quality=95)
    img.convert('RGB').save('k6/slides/assets/slide_k6_x_agent_1.png', quality=95)
    print("Generated Slide 1 (Perfected)")


# ==============================================================================
# SLIDE 2: 常用 CLI 指令速查與 6 大編輯器支援
# ==============================================================================
def create_slide_2():
    img = Image.new('RGBA', (W, H), (248, 247, 242, 255))
    draw = ImageDraw.Draw(img)

    draw_header(
        draw, 2,
        "k6 x agent (二) ：常用 CLI 指令速查與 6 大編輯器支援",
        "在專案根目錄終端機執行直覺的子命令，一鍵適配主流 AI 代碼編輯器與自主 Agent 環境"
    )

    c1_x, c1_y, c1_w, c1_h = 48, 104, 634, 524
    draw.rounded_rectangle([c1_x, c1_y, c1_x + c1_w, c1_y + c1_h], radius=10, fill=(255, 255, 255), outline=(226, 232, 240), width=1)
    draw.rounded_rectangle([c1_x + 18, c1_y + 14, c1_x + 18 + 92, c1_y + 14 + 22], radius=4, fill=(209, 250, 229), outline=(167, 243, 208), width=1)
    draw.text((c1_x + 24, c1_y + 17), "終端快速上手", font=f_pill, fill=(4, 120, 87))
    draw.text((c1_x + 120, c1_y + 15), "常用 CLI 命令速查與情境解析", font=f_h2, fill=(15, 23, 42))

    # Big Terminal Box
    term_x, term_y, term_w, term_h = c1_x + 18, c1_y + 48, c1_w - 36, 456
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
        ("# 4. 強制覆蓋重置所有技能與 MCP 設定",
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
    c2_x, c2_y, c2_w, c2_h = 694, 104, 634, 524
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
    for name, slug, desc, col, bg in editors_detail:
        draw.rounded_rectangle([c2_x + 18, ey, c2_x + c2_w - 18, ey + 71], radius=8, fill=bg, outline=col, width=1)
        # Title + Slug
        draw.text((c2_x + 28, ey + 11), name, font=f_card_title, fill=(15, 23, 42))
        slug_box = draw.textbbox((0, 0), slug, font=f_term_cmd)
        sw = slug_box[2] - slug_box[0] + 16
        draw.rounded_rectangle([c2_x + 180, ey + 8, c2_x + 180 + sw, ey + 30], radius=4, fill=(255, 255, 255), outline=col, width=1)
        draw.text((c2_x + 188, ey + 11), slug, font=f_term_cmd, fill=col)
        # Desc
        draw.text((c2_x + 28, ey + 42), desc, font=f_body_reg, fill=(71, 85, 105))
        ey += 78

    # Bottom Banner
    foot_x, foot_y, foot_w, foot_h = 48, 664, 930, 72
    draw.rounded_rectangle([foot_x, foot_y, foot_x + foot_w, foot_y + foot_h], radius=8, fill=(255, 255, 255), outline=(203, 213, 225), width=1)
    draw.rounded_rectangle([foot_x + 14, foot_y + 12, foot_x + 78, foot_y + 34], radius=4, fill=(254, 242, 242), outline=(254, 202, 202), width=1)
    draw.text((foot_x + 20, foot_y + 15), "團隊建議", font=f_pill, fill=(185, 28, 28))
    draw.text((foot_x + 88, foot_y + 14), "團隊成員使用不同編輯器時，直接執行 k6 x agent init --all 即可共享相同的壓測技能！", font=f_body_bold, fill=(30, 41, 59))
    draw.text((foot_x + 18, foot_y + 44), "下一頁：我們將深入剖析執行 init 後，AI 助手獲得的 5 大開箱即用 AI 專業壓測技能！", font=f_footer, fill=(100, 116, 139))

    paste_branding(img)
    img.convert('RGB').save('k6/slides/k6_x_agent_slide_2.png', quality=95)
    img.convert('RGB').save('k6/slides/assets/slide_k6_x_agent_2.png', quality=95)
    print("Generated Slide 2 (Perfected)")


# ==============================================================================
# SLIDE 3: 內建 5 大專業 AI 技能全解析與官方資源
# ==============================================================================
def create_slide_3():
    img = Image.new('RGBA', (W, H), (248, 247, 242, 255))
    draw = ImageDraw.Draw(img)

    draw_header(
        draw, 3,
        "k6 x agent (三) ：內建 5 大 AI 技能深度剖析與官方資源",
        "執行 init 後自動注入編輯器的 5 大專業壓測技能，全方位覆蓋規劃、負載、冒煙、瀏覽器與腳本轉換"
    )

    # 5 Big Skill Cards (Height ~98px each)
    skills = [
        ("k6-test-planner", "規劃與設計效能測試策略",
         "觸發提示詞：\"plan tests\", \"design a test strategy\", \"請幫我規劃這支訂單 API 的壓測策略\"",
         "核心能力：依據端點業務特質與架構特徵，自動推薦合適的流量模型、計算並發 VU 與坡度、並設計合理的 P95 延遲門檻與 SLO 門禁。",
         (99, 102, 241), (238, 242, 255)),
        
        ("k6-load-test", "撰寫標準負載 / 壓力 / 浸泡測試腳本",
         "觸發提示詞：\"write a load test\", \"stress test\", \"soak test\", \"產生標準負載測試\"",
         "核心能力：精準產出包含 stages 爬坡階段、arrival-rate 開放模型、Thresholds 門檻與動態 Token 關聯的生產級標準測試代碼。",
         (16, 185, 129), (236, 253, 245)),
        
        ("k6-smoke-test", "撰寫快速連通性冒煙測試腳本",
         "觸發提示詞：\"write a smoke test\", \"verify connectivity\", \"快速冒煙驗證\"",
         "核心能力：以極低資源（1~2 VU）於 5 秒內快速驗證 API 基礎可用性、HTTP 200/201 回傳碼與核心 JSON 欄位契約，適合作為 CI 卡關第一線。",
         (245, 158, 11), (254, 243, 199)),
        
        ("k6-browser-test", "撰寫前端 UI 瀏覽器真實渲染壓測",
         "觸發詞：\"browser test\", \"measure Web Vitals\", \"前端瀏覽器壓測\", \"驗證 LCP/CLS\"",
         "核心能力：基於 k6/browser 驅動無頭 Chromium，模擬真實用戶點擊、量測 LCP、FCP、INP 等核心 Web Vitals 指標，防範 SPA 前端效能盲區。",
         (14, 165, 233), (240, 249, 255)),
        
        ("k6-playwright-converter", "將 Playwright 測試無痛轉換為 k6",
         "觸發詞：\"convert this Playwright script\", \"migrate e2e test to k6\", \"轉譯端到端測試\"",
         "核心能力：讀取既有的 Playwright TypeScript/JavaScript E2E 腳本，自動將 Page Actions 轉譯為合規的 k6/browser 效能混合壓測腳本。",
         (217, 70, 239), (253, 244, 255))
    ]

    sy = 104
    for name, title, trigger, capability, col, bg in skills:
        draw.rounded_rectangle([48, sy, 48 + 1280, sy + 98], radius=8, fill=bg, outline=col, width=1)
        
        # Skill Badge
        name_box = draw.textbbox((0, 0), name, font=f_term_cmd)
        nw = name_box[2] - name_box[0] + 18
        draw.rounded_rectangle([64, sy + 10, 64 + nw, sy + 34], radius=4, fill=(255, 255, 255), outline=col, width=1)
        draw.text((73, sy + 13), name, font=f_term_cmd, fill=col)

        # Title
        draw.text((64 + nw + 16, sy + 11), title, font=f_h2, fill=(15, 23, 42))

        # Trigger line
        draw.text((64, sy + 44), trigger, font=f_body_bold, fill=(79, 70, 229) if col != (99, 102, 241) else (15, 23, 42))

        # Capability
        draw.text((64, sy + 68), capability, font=f_body_reg, fill=(71, 85, 105))

        sy += 108

    # Bottom Callout / Links
    foot_x, foot_y, foot_w, foot_h = 48, 660, 930, 84
    draw.rounded_rectangle([foot_x, foot_y, foot_x + foot_w, foot_y + foot_h], radius=8, fill=(255, 255, 255), outline=(203, 213, 225), width=1)
    draw.rounded_rectangle([foot_x + 14, foot_y + 12, foot_x + 86, foot_y + 34], radius=4, fill=(240, 253, 250), outline=(94, 234, 212), width=1)
    draw.text((foot_x + 20, foot_y + 15), "官方資源", font=f_pill, fill=(13, 148, 136))

    draw.text((foot_x + 98, foot_y + 14), "想在你的編輯器中親手試試看一鍵配置嗎？歡迎查閱官方開源專案與文件指南：", font=f_body_bold, fill=(30, 41, 59))
    draw.text((foot_x + 20, foot_y + 42), "• GitHub 開源倉庫：", font=f_link_label, fill=(100, 116, 139))
    draw.text((foot_x + 135, foot_y + 42), "https://github.com/grafana/xk6-subcommand-agent", font=f_link_url, fill=(2, 132, 199))
    draw.text((foot_x + 20, foot_y + 60), "• 官方配置指南：", font=f_link_label, fill=(100, 116, 139))
    draw.text((foot_x + 124, foot_y + 60), "https://grafana.com/docs/k6/latest/set-up/configure-ai-assistant/bootstrap-with-k6-x-agent/", font=f_link_url, fill=(2, 132, 199))

    paste_branding(img)
    img.convert('RGB').save('k6/slides/k6_x_agent_slide_3.png', quality=95)
    img.convert('RGB').save('k6/slides/assets/slide_k6_x_agent_3.png', quality=95)
    print("Generated Slide 3 (Perfected)")

if __name__ == '__main__':
    os.makedirs('k6/slides/assets', exist_ok=True)
    create_slide_1()
    create_slide_2()
    create_slide_3()
