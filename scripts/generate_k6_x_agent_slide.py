#!/usr/bin/env python3
"""
Generate a pixel-perfect, high-definition slide image for `k6 x agent`:
Grafana k6 內建的 AI 子命令擴充套件（Subcommand Extension）
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

f_title = ImageFont.truetype(FONT_TC_BOLD, 28)
f_subtitle = ImageFont.truetype(FONT_TC_REG, 14)
f_pill = ImageFont.truetype(FONT_TC_BOLD, 12)
f_h2 = ImageFont.truetype(FONT_TC_BOLD, 15)
f_body_bold = ImageFont.truetype(FONT_TC_BOLD, 11)
f_body_reg = ImageFont.truetype(FONT_TC_REG, 10.5)
f_term_comment = ImageFont.truetype(FONT_TC_REG, 10.5)
f_term_cmd = ImageFont.truetype(FONT_MONO_BOLD, 11)
f_link_label = ImageFont.truetype(FONT_TC_BOLD, 10)
f_link_url = ImageFont.truetype(FONT_EN_REG, 10)
f_footer = ImageFont.truetype(FONT_TC_REG, 10)

def create_slide():
    img = Image.new('RGBA', (W, H), (248, 247, 242, 255))
    draw = ImageDraw.Draw(img)

    # 1. Header
    badge_x, badge_y = 48, 32
    draw.rounded_rectangle([badge_x, badge_y, badge_x + 184, badge_y + 24], radius=6, fill=(238, 242, 255), outline=(199, 210, 254), width=1)
    draw.text((badge_x + 10, badge_y + 4), "AI SUBCOMMAND EXTENSION", font=f_pill, fill=(79, 70, 229))

    draw.text((badge_x + 196, badge_y - 3), "k6 x agent ：一鍵配置 AI 編輯器與 Agent 壓測工作流", font=f_title, fill=(15, 23, 42))

    sub_y = badge_y + 35
    draw.text((badge_x, sub_y), "Grafana k6 原生 AI 子命令擴充套件 (xk6-subcommand-agent) ── 執行一次命令，自動完成「安裝 5 大技能包」與「註冊 k6 MCP 伺服器」", font=f_subtitle, fill=(71, 85, 105))

    # ----------------------------------------------------
    # CARD 1: 💡 k6 x agent 幫你自動處理哪些事？ (Left Top)
    # ----------------------------------------------------
    c1_x, c1_y, c1_w, c1_h = 48, 102, 634, 342
    draw.rounded_rectangle([c1_x, c1_y, c1_x + c1_w, c1_y + c1_h], radius=10, fill=(255, 255, 255), outline=(226, 232, 240), width=1)

    draw.rounded_rectangle([c1_x + 16, c1_y + 14, c1_x + 16 + 92, c1_y + 14 + 22], radius=4, fill=(254, 243, 199), outline=(252, 211, 77), width=1)
    draw.text((c1_x + 22, c1_y + 17), "核心自動化", font=f_pill, fill=(180, 83, 9))
    draw.text((c1_x + 118, c1_y + 15), "k6 x agent 幫你自動處理哪些事？", font=f_h2, fill=(15, 23, 42))

    # Item 1: Bundled Skills
    it1_y = c1_y + 46
    draw.rounded_rectangle([c1_x + 16, it1_y, c1_x + c1_w - 16, it1_y + 84], radius=8, fill=(248, 250, 252), outline=(241, 245, 249), width=1)
    draw.rounded_rectangle([c1_x + 16, it1_y, c1_x + 20, it1_y + 84], radius=2, fill=(99, 102, 241))
    draw.text((c1_x + 28, it1_y + 8), "1. 自動安裝內建 AI 技能 (Bundled Skills)", font=f_body_bold, fill=(30, 41, 59))
    draw.text((c1_x + 28, it1_y + 28), "• 將標準 SKILL.md 或 Cursor 的 .mdc Rules 自動寫入編輯器讀取的專屬目錄。", font=f_body_reg, fill=(71, 85, 105))
    draw.text((c1_x + 28, it1_y + 46), "• 當你在 AI 聊天視窗輸入 \"write a smoke test\" 或 \"convert this Playwright script\"，", font=f_body_reg, fill=(71, 85, 105))
    draw.text((c1_x + 28, it1_y + 64), "  AI 助手就會自動觸發對應的 k6 專業技能，按最佳實踐產出腳本。", font=f_body_bold, fill=(79, 70, 229))

    # Item 2: Auto Register MCP
    it2_y = it1_y + 92
    draw.rounded_rectangle([c1_x + 16, it2_y, c1_x + c1_w - 16, it2_y + 88], radius=8, fill=(248, 250, 252), outline=(241, 245, 249), width=1)
    draw.rounded_rectangle([c1_x + 16, it2_y, c1_x + 20, it2_y + 88], radius=2, fill=(16, 185, 129))
    draw.text((c1_x + 28, it2_y + 8), "2. 自動註冊 k6 MCP 伺服器 (Auto-Register k6 x mcp)", font=f_body_bold, fill=(30, 41, 59))
    draw.text((c1_x + 28, it2_y + 28), "• 自動將 k6 x mcp 寫入編輯器的 MCP 設定檔（.mcp.json、.cursor/mcp.json 等）。", font=f_body_reg, fill=(71, 85, 105))
    draw.text((c1_x + 28, it2_y + 46), "• AI 助手無需手動設定即可直接呼叫 k6 專屬 MCP 工具：", font=f_body_reg, fill=(71, 85, 105))
    draw.text((c1_x + 28, it2_y + 66), "  - validate_script：語法預檢與規範驗證    - run_script：本機一鍵跑壓測與指標解析", font=f_body_bold, fill=(5, 150, 105))

    # Item 3: Safety & Idempotency
    it3_y = it2_y + 96
    draw.rounded_rectangle([c1_x + 16, it3_y, c1_x + c1_w - 16, it3_y + 88], radius=8, fill=(248, 250, 252), outline=(241, 245, 249), width=1)
    draw.rounded_rectangle([c1_x + 16, it3_y, c1_x + 20, it3_y + 88], radius=2, fill=(245, 158, 11))
    draw.text((c1_x + 28, it3_y + 8), "3. 安全與冪等性 (Safety & Idempotency)", font=f_body_bold, fill=(30, 41, 59))
    draw.text((c1_x + 28, it3_y + 28), "• 產生的檔案帶有擁有者標籤 (Owner Tag)，重複執行 init 絕不覆蓋你手動修改過的檔案。", font=f_body_reg, fill=(71, 85, 105))
    draw.text((c1_x + 28, it3_y + 46), "• 支援在寫入前用 --dry-run 預覽將產生的目錄、檔案路徑與變更內容。", font=f_body_reg, fill=(71, 85, 105))
    draw.text((c1_x + 28, it3_y + 66), "• 唯有明確加上 --force 旗標時才會強制重新覆蓋，兼具便利與工程安全。", font=f_body_bold, fill=(217, 119, 6))

    # ----------------------------------------------------
    # CARD 2: 🎯 支援的 AI 編輯器與 Agent 目標 (Left Bottom)
    # ----------------------------------------------------
    c2_x, c2_y, c2_w, c2_h = 48, 456, 634, 196
    draw.rounded_rectangle([c2_x, c2_y, c2_x + c2_w, c2_y + c2_h], radius=10, fill=(255, 255, 255), outline=(226, 232, 240), width=1)

    draw.rounded_rectangle([c2_x + 16, c2_y + 14, c2_x + 16 + 92, c2_y + 14 + 22], radius=4, fill=(224, 231, 255), outline=(199, 210, 254), width=1)
    draw.text((c2_x + 22, c2_y + 17), "環境支援度", font=f_pill, fill=(67, 56, 202))
    draw.text((c2_x + 118, c2_y + 15), "支援的 AI 編輯器與 Agent 目標", font=f_h2, fill=(15, 23, 42))

    editors = [
        ("Claude Code", "claude-code", "Anthropic 終端 Agent", (249, 115, 22), (255, 247, 237)),
        ("Cursor", "cursor", "支援 .mdc Rules 與 MCP", (147, 51, 234), (250, 245, 255)),
        ("GitHub Copilot", "vscode-copilot", "VS Code 官方原生整合", (37, 99, 235), (239, 246, 255)),
        ("OpenAI Codex CLI", "codex-cli", "OpenAI 原生終端工作流", (16, 185, 129), (236, 253, 245)),
        ("OpenCode", "opencode", "開源終端 AI 助手環境", (217, 119, 6), (254, 243, 199)),
        ("Cline", "cline", "VS Code 自主 Agent 插件", (225, 29, 72), (255, 241, 242))
    ]

    for idx, (name, slug, desc, col, bg_col) in enumerate(editors):
        col_idx = idx % 3
        row_idx = idx // 3
        ex = c2_x + 16 + col_idx * 199
        ey = c2_y + 44 + row_idx * 68
        ew, eh = 193, 62
        draw.rounded_rectangle([ex, ey, ex + ew, ey + eh], radius=6, fill=bg_col, outline=col, width=1)
        draw.text((ex + 10, ey + 7), name, font=f_body_bold, fill=(15, 23, 42))
        
        # Pill for slug
        slug_bbox = draw.textbbox((0, 0), slug, font=f_term_cmd)
        slug_w = slug_bbox[2] - slug_bbox[0] + 12
        draw.rounded_rectangle([ex + 10, ey + 24, ex + 10 + slug_w, ey + 40], radius=3, fill=(255, 255, 255), outline=col, width=1)
        draw.text((ex + 16, ey + 26), slug, font=f_term_cmd, fill=col)
        draw.text((ex + 10, ey + 44), desc, font=f_footer, fill=(100, 116, 139))


    # ----------------------------------------------------
    # CARD 3: 💻 常用 CLI 命令與快速上手 (Right Top)
    # ----------------------------------------------------
    c3_x, c3_y, c3_w, c3_h = 694, 102, 634, 236
    draw.rounded_rectangle([c3_x, c3_y, c3_x + c3_w, c3_y + c3_h], radius=10, fill=(255, 255, 255), outline=(226, 232, 240), width=1)

    draw.rounded_rectangle([c3_x + 16, c3_y + 14, c3_x + 16 + 92, c3_y + 14 + 22], radius=4, fill=(209, 250, 229), outline=(167, 243, 208), width=1)
    draw.text((c3_x + 22, c3_y + 17), "終端快速上手", font=f_pill, fill=(4, 120, 87))
    draw.text((c3_x + 118, c3_y + 15), "常用 CLI 命令速查", font=f_h2, fill=(15, 23, 42))

    # Terminal Box
    term_x, term_y, term_w, term_h = c3_x + 16, c3_y + 44, c3_w - 32, 178
    draw.rounded_rectangle([term_x, term_y, term_x + term_w, term_y + term_h], radius=8, fill=(15, 23, 42))
    
    # Terminal header dots
    draw.ellipse([term_x + 12, term_y + 8, term_x + 20, term_y + 16], fill=(239, 68, 68))
    draw.ellipse([term_x + 25, term_y + 8, term_x + 33, term_y + 16], fill=(245, 158, 11))
    draw.ellipse([term_x + 38, term_y + 8, term_x + 46, term_y + 16], fill=(34, 197, 94))
    draw.text((term_x + 58, term_y + 6), "bash ── k6 專案根目錄", font=f_footer, fill=(148, 163, 184))

    code_lines = [
        ("# 1. 為指定的編輯器進行初始化 (例如 Cursor 或 Claude Code)", (148, 163, 184), False),
        ("k6 x agent init cursor      k6 x agent init claude-code", (56, 189, 248), True),
        ("# 2. 一鍵初始化所有支援的編輯器", (148, 163, 184), False),
        ("k6 x agent init --all", (52, 211, 153), True),
        ("# 3. 預覽將產生的檔案與路徑（不安裝）", (148, 163, 184), False),
        ("k6 x agent init --dry-run cursor", (251, 191, 36), True),
        ("# 4. 檢查當前連線狀態        # 5. 查看內建 AI 技能清單", (148, 163, 184), False),
        ("k6 x agent status         k6 x agent skills list", (192, 132, 252), True),
    ]

    cy = term_y + 24
    for text, color, is_cmd in code_lines:
        prefix = "$ " if is_cmd else ""
        font = f_term_cmd if is_cmd else f_term_comment
        draw.text((term_x + 14, cy), prefix + text, font=font, fill=color)
        cy += 18.5


    # ----------------------------------------------------
    # CARD 4: 📦 內建 5 大專業 AI 技能 (Right Bottom)
    # ----------------------------------------------------
    c4_x, c4_y, c4_w, c4_h = 694, 350, 634, 302
    draw.rounded_rectangle([c4_x, c4_y, c4_x + c4_w, c4_y + c4_h], radius=10, fill=(255, 255, 255), outline=(226, 232, 240), width=1)

    draw.rounded_rectangle([c4_x + 16, c4_y + 14, c4_x + 16 + 92, c4_y + 14 + 22], radius=4, fill=(254, 242, 242), outline=(254, 202, 202), width=1)
    draw.text((c4_x + 22, c4_y + 17), "開箱即用套件", font=f_pill, fill=(185, 28, 28))
    draw.text((c4_x + 118, c4_y + 15), "內建的 5 大 AI 技能 (Bundled Skills)", font=f_h2, fill=(15, 23, 42))

    skills = [
        ("k6-test-planner", "規劃與設計壓測策略", "觸發詞：\"plan tests\", \"design a test strategy\"", (99, 102, 241), (238, 242, 255)),
        ("k6-load-test", "撰寫標準負載測試/壓力/浸泡腳本", "支援標準 Load、極限 Stress 與長時間浸泡 Soak 測試", (16, 185, 129), (236, 253, 245)),
        ("k6-smoke-test", "撰寫快速連通性冒煙測試", "以極低 VU (1~2 VU) 快速驗證 API 基本可用性與回傳契約", (245, 158, 11), (254, 243, 199)),
        ("k6-browser-test", "撰寫前端 UI 瀏覽器壓測", "基於 k6/browser 驅動無頭瀏覽器，測量真實 Web Vitals 指標", (14, 165, 233), (240, 249, 255)),
        ("k6-playwright-converter", "Playwright 測試無痛轉換", "將現有的 Playwright E2E 腳本一鍵轉換為 k6/browser 腳本", (217, 70, 239), (253, 244, 255))
    ]

    for idx, (skill_name, skill_desc, trigger, accent, bg_col) in enumerate(skills):
        sy = c4_y + 44 + idx * 50
        draw.rounded_rectangle([c4_x + 16, sy, c4_x + c4_w - 16, sy + 44], radius=6, fill=bg_col, outline=accent, width=1)
        
        # Skill badge (auto width)
        skill_bbox = draw.textbbox((0, 0), skill_name, font=f_term_cmd)
        skill_w = skill_bbox[2] - skill_bbox[0] + 16
        draw.rounded_rectangle([c4_x + 24, sy + 10, c4_x + 24 + skill_w, sy + 34], radius=4, fill=(255, 255, 255), outline=accent, width=1)
        draw.text((c4_x + 32, sy + 13), skill_name, font=f_term_cmd, fill=accent)
        
        # Desc
        desc_x = c4_x + 24 + skill_w + 14
        draw.text((desc_x, sy + 8), skill_desc, font=f_body_bold, fill=(15, 23, 42))
        draw.text((desc_x, sy + 25), trigger, font=f_footer, fill=(100, 116, 139))


    # ----------------------------------------------------
    # BOTTOM FOOTER / BANNER & LOGO
    # ----------------------------------------------------
    # Left Callout banner:
    foot_x, foot_y, foot_w, foot_h = 48, 664, 930, 80
    draw.rounded_rectangle([foot_x, foot_y, foot_x + foot_w, foot_y + foot_h], radius=8, fill=(255, 255, 255), outline=(203, 213, 225), width=1)
    
    # Left highlight badge
    draw.rounded_rectangle([foot_x + 12, foot_y + 12, foot_x + 88, foot_y + 34], radius=4, fill=(240, 253, 250), outline=(94, 234, 212), width=1)
    draw.text((foot_x + 18, foot_y + 15), "💡 官方資源", font=f_pill, fill=(13, 148, 136))
    
    draw.text((foot_x + 98, foot_y + 14), "想在你的編輯器（如 Cursor 或 VS Code/GitHub Copilot）中親手試試看一鍵配置嗎？", font=f_body_bold, fill=(30, 41, 59))
    
    draw.text((foot_x + 18, foot_y + 42), "• GitHub 開源專案：", font=f_link_label, fill=(100, 116, 139))
    draw.text((foot_x + 124, foot_y + 42), "https://github.com/grafana/xk6-subcommand-agent", font=f_link_url, fill=(2, 132, 199))
    
    draw.text((foot_x + 18, foot_y + 58), "• 官方配置指南：", font=f_link_label, fill=(100, 116, 139))
    draw.text((foot_x + 112, foot_y + 58), "https://grafana.com/docs/k6/latest/set-up/configure-ai-assistant/bootstrap-with-k6-x-agent/", font=f_link_url, fill=(2, 132, 199))

    # Paste Grafana / k6 full logo at bottom right
    full_logo_path = '/tmp/k6_grafana_full_branding.png'
    if os.path.exists(full_logo_path):
        logo_img = Image.open(full_logo_path)
        img.paste(logo_img, (990, 655))

    out_path = 'k6/slides/assets/slide_k6_x_agent.png'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.convert('RGB').save(out_path, quality=95)
    img.convert('RGB').save('k6/slides/k6_x_agent_slide.png', quality=95)
    print(f"Generated slide image: {out_path} and k6/slides/k6_x_agent_slide.png")

if __name__ == '__main__':
    create_slide()
