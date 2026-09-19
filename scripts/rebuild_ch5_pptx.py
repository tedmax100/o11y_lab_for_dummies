#!/usr/bin/env python3
"""
Rebuild k6/slides/Ch5_k6_Observability_and_Modular_Architecture.pptx
1. Add author article callout box on Slide 4.
2. Insert new Slide 10: "推薦延伸閱讀：講師深度實戰專欄 (Author's Deep-Dive Articles)"
3. Retain original Slide 10 as Slide 11: "隨堂練習指引 (Hands-on Practice)"
4. Ensure Codelabs top banner is present on all 11 slides.
"""
import os
import zipfile
from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.util import Pt, Emu
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

FONT_HEADING = "Noto Sans CJK TC"
FONT_BODY = "Noto Sans CJK TC"
FONT_CODE = "Noto Sans Mono CJK TC"

def style_box(shape, fill_rgb, line_rgb=None, line_width=1):
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    if line_rgb:
        shape.line.color.rgb = line_rgb
        shape.line.width = Pt(line_width)
    else:
        shape.line.fill.background()

def extract_original_images():
    os.makedirs('/tmp/ch5_extracted', exist_ok=True)
    with zipfile.ZipFile('k6/slides/Ch5_k6_Observability_and_Modular_Architecture.pptx') as z:
        for i in range(1, 11):
            with open(f'/tmp/ch5_extracted/image{i}.png', 'wb') as f:
                f.write(z.read(f'ppt/media/image{i}.png'))
    print("Extracted 10 original slide images.")

def create_slide10_background():
    img = Image.open('/tmp/ch5_extracted/image10.png').copy()
    draw = ImageDraw.Draw(img)
    # Clean title and cards area, keeping the outer sci-fi tech border & bottom logo
    draw.rectangle([50, 45, 1320, 715], fill=(18, 25, 38))
    bg_path = '/tmp/ch5_extracted/slide10_bg.png'
    img.save(bg_path)
    return bg_path

def add_codelab_banner(slide):
    # Top banner matching add_codelab_link_to_slides.py
    l, t, w, h = px(40, 735, 510, 24)
    badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h)
    style_box(badge, RGBColor(10, 20, 32), RGBColor(0, 180, 216), 1)
    tf = badge.text_frame
    tf.word_wrap = False
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Emu(int(8 * EMU_PER_PX_X))
    tf.margin_right = Emu(int(8 * EMU_PER_PX_X))
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)
    
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    
    r1 = p.add_run()
    r1.text = "▶ 課程實戰 Codelabs："
    r1.font.name = FONT_HEADING
    r1.font.size = Pt(8.5)
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(255, 255, 255)
    
    r2 = p.add_run()
    r2.text = "tedmax100.github.io/o11y_lab_for_dummies/k6-performance-testing/"
    r2.font.name = FONT_CODE
    r2.font.size = Pt(8.5)
    r2.font.color.rgb = RGBColor(102, 252, 241)
    
    # Add hyperlink
    url = "https://tedmax100.github.io/o11y_lab_for_dummies/k6-performance-testing/"
    badge.click_action.hyperlink.address = url
    r2.hyperlink.address = url

def build_presentation():
    extract_original_images()
    s10_bg = create_slide10_background()
    
    prs = Presentation()
    prs.slide_width = SW
    prs.slide_height = SH
    blank = prs.slide_layouts[6]
    
    # 1. Slide 1 to 3: Original with banner
    for i in range(1, 4):
        s = prs.slides.add_slide(blank)
        s.shapes.add_picture(f'/tmp/ch5_extracted/image{i}.png', 0, 0, width=SW, height=SH)
        add_codelab_banner(s)
        
    # 2. Slide 4: Original + Callout on left
    s4 = prs.slides.add_slide(blank)
    s4.shapes.add_picture('/tmp/ch5_extracted/image4.png', 0, 0, width=SW, height=SH)
    
    # Add callout card on bottom-left: x=50, y=475, w=280, h=215
    l, t, w, h = px(50, 475, 280, 215)
    callout = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h)
    style_box(callout, RGBColor(22, 26, 38), RGBColor(140, 90, 255), 1.5)
    
    tf4 = callout.text_frame
    tf4.word_wrap = True
    tf4.vertical_anchor = MSO_ANCHOR.TOP
    tf4.margin_left = Emu(int(14 * EMU_PER_PX_X))
    tf4.margin_right = Emu(int(14 * EMU_PER_PX_X))
    tf4.margin_top = Emu(int(12 * EMU_PER_PX_Y))
    tf4.margin_bottom = Emu(int(12 * EMU_PER_PX_Y))
    
    # Badge
    p0 = tf4.paragraphs[0]
    r_badge = p0.add_run()
    r_badge.text = "💡 講師深度實戰專欄"
    r_badge.font.name = FONT_HEADING
    r_badge.font.size = Pt(10.5)
    r_badge.font.bold = True
    r_badge.font.color.rgb = RGBColor(187, 134, 252)
    p0.space_after = Pt(5)
    
    # Article Title
    p1 = tf4.add_paragraph()
    r_title = p1.add_run()
    r_title.text = "Grafana xk6: 手把手從開發到編譯出 k6 插件"
    r_title.font.name = FONT_HEADING
    r_title.font.size = Pt(11)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(255, 255, 255)
    p1.space_after = Pt(6)
    
    # Highlights
    p2 = tf4.add_paragraph()
    r_desc = p2.add_run()
    r_desc.text = "• Web3 OTP 動態金鑰簽名插件\n• RootModule / ModuleInstance 解密\n• 突破原生極限支援私有協定"
    r_desc.font.name = FONT_BODY
    r_desc.font.size = Pt(9.5)
    r_desc.font.color.rgb = RGBColor(195, 200, 210)
    p2.space_after = Pt(8)
    
    # URL Tag
    p3 = tf4.add_paragraph()
    r_url = p3.add_run()
    r_url.text = "🔗 閱讀專欄：ganhua.wang/grafana-xk6"
    r_url.font.name = FONT_CODE
    r_url.font.size = Pt(9.5)
    r_url.font.bold = True
    r_url.font.color.rgb = RGBColor(102, 252, 241)
    callout.click_action.hyperlink.address = "https://ganhua.wang/grafana-xk6"
    
    add_codelab_banner(s4)
    
    # 3. Slide 5 to 9: Original with banner
    for i in range(5, 10):
        s = prs.slides.add_slide(blank)
        s.shapes.add_picture(f'/tmp/ch5_extracted/image{i}.png', 0, 0, width=SW, height=SH)
        add_codelab_banner(s)
        
    # 4. Slide 10: NEW Recommended Reading Slide (3 Cards)
    s10 = prs.slides.add_slide(blank)
    s10.shapes.add_picture(s10_bg, 0, 0, width=SW, height=SH)
    
    # Title
    l_title, t_title, w_title, h_title = px(60, 48, 1100, 65)
    title_box = s10.shapes.add_textbox(l_title, t_title, w_title, h_title)
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_t = tf_title.paragraphs[0]
    
    r_t1 = p_t.add_run()
    r_t1.text = "推薦延伸閱讀 "
    r_t1.font.name = FONT_HEADING
    r_t1.font.size = Pt(22)
    r_t1.font.bold = True
    r_t1.font.color.rgb = RGBColor(255, 255, 255)
    
    r_t2 = p_t.add_run()
    r_t2.text = "(Author's Deep-Dive Articles)"
    r_t2.font.name = FONT_HEADING
    r_t2.font.size = Pt(17)
    r_t2.font.color.rgb = RGBColor(102, 252, 241)
    
    p_sub = tf_title.add_paragraph()
    r_sub = p_sub.add_run()
    r_sub.text = "講師親撰之 k6 系列技術專欄 — 深入外掛生態系開發、前端真實體驗混合壓測與微服務全鏈路可觀測性閉環"
    r_sub.font.name = FONT_BODY
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = RGBColor(154, 160, 166)
    
    # 3 Cards definition
    cards_data = [
        {
            "x": 60, "w": 395,
            "badge": "xk6 模組擴充 (Go Extension)",
            "badge_color": RGBColor(187, 134, 252),
            "border_color": RGBColor(124, 77, 255),
            "bg_color": RGBColor(25, 22, 38),
            "title": "Grafana xk6: 手把手從開發到編譯插件",
            "subtitle": "核心：Go-to-JS Bridge 與動態密碼插件實戰",
            "url_text": "ganhua.wang/grafana-xk6",
            "url": "https://ganhua.wang/grafana-xk6",
            "bullets": [
                ("Go-to-JS Bridge 架構", "深度解析 RootModule、ModuleInstance 與 modules.Register 註冊機制，掌握 Go 結構體映射至 JS 類別的核心原理。"),
                ("Web3 OTP 實戰案例", "以動態身份驗證為例，親手實作 k6/x/otp 擴充套件，在百萬併發壓測中動態生成一次性金鑰密碼與簽名。"),
                ("Docker 確定性編譯", "使用 grafana/xk6 官方容器抹平各 OS 開發環境依賴，在零配置前提下一鍵編譯出團隊專屬客製化 k6 二進位檔。")
            ]
        },
        {
            "x": 490, "w": 395,
            "badge": "前端混壓測試 (k6-browser)",
            "badge_color": RGBColor(0, 230, 118),
            "border_color": RGBColor(0, 180, 216),
            "bg_color": RGBColor(16, 28, 34),
            "title": "Grafana k6 瀏覽器測試實戰",
            "subtitle": "核心：Playwright 相容與 Core Web Vitals",
            "url_text": "ganhua.wang/grafana-k6-browser",
            "url": "https://ganhua.wang/grafana-k6-browser",
            "bullets": [
                ("Playwright 相容生態", "全面採用 chromium.launch()、page.goto() 與語意化 Locator，前端工程師無需轉換思維即可上手。"),
                ("BrowserContext 隔離", "在單一瀏覽器處理程序中實現多用戶完全獨立的 Session、Cookie 與 LocalStorage，大幅降低記憶體開銷。"),
                ("電商全流程自動化", "以 OpenTelemetry Demo 購物車為例，完整模擬加購物車與結帳，採集真實 Web Vitals 並自動截圖保存錯誤現場。")
            ]
        },
        {
            "x": 920, "w": 395,
            "badge": "全鏈路閉環 (Observability)",
            "badge_color": RGBColor(255, 171, 0),
            "border_color": RGBColor(251, 140, 0),
            "bg_color": RGBColor(32, 26, 18),
            "title": "Getting Started with Grafana k6",
            "subtitle": "核心：OpenTelemetry 串流與 GitLab CI",
            "url_text": "ganhua.wang/getting-started-with-grafana-k6",
            "url": "https://ganhua.wang/getting-started-with-grafana-k6-hands-on-practice",
            "bullets": [
                ("語意化測試組織", "運用 k6/http、check 與 group 模組化封裝業務邏輯，產出結構清晰且具備業務意義的階層化壓測報表。"),
                ("OTel 串流全面整合", "直連 OpenTelemetry Collector，將客戶端壓測指標與後端分散式 Traces、Logs 進行跨維度時間軸對齊。"),
                ("GitLab CI 自動化門禁", "將 k6 壓測無縫嵌入 CI/CD 流水線，以 Exit Code 99 自動攔截效能退化代碼，守護生產主幹穩定。")
            ]
        }
    ]
    
    for c in cards_data:
        l_c, t_c, w_c, h_c = px(c["x"], 130, c["w"], 505)
        card_shape = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l_c, t_c, w_c, h_c)
        style_box(card_shape, c["bg_color"], c["border_color"], 1.5)
        
        tf_c = card_shape.text_frame
        tf_c.word_wrap = True
        tf_c.vertical_anchor = MSO_ANCHOR.TOP
        tf_c.margin_left = Emu(int(16 * EMU_PER_PX_X))
        tf_c.margin_right = Emu(int(16 * EMU_PER_PX_X))
        tf_c.margin_top = Emu(int(14 * EMU_PER_PX_Y))
        tf_c.margin_bottom = Emu(int(12 * EMU_PER_PX_Y))
        
        # Badge paragraph
        p_badge = tf_c.paragraphs[0]
        r_b = p_badge.add_run()
        r_b.text = f"● {c['badge']}"
        r_b.font.name = FONT_HEADING
        r_b.font.size = Pt(10.5)
        r_b.font.bold = True
        r_b.font.color.rgb = c["badge_color"]
        p_badge.space_after = Pt(4)
        
        # Title paragraph
        p_title = tf_c.add_paragraph()
        r_t = p_title.add_run()
        r_t.text = c["title"]
        r_t.font.name = FONT_HEADING
        r_t.font.size = Pt(12.5)
        r_t.font.bold = True
        r_t.font.color.rgb = RGBColor(255, 255, 255)
        p_title.space_after = Pt(2)
        
        # Subtitle paragraph
        p_sub = tf_c.add_paragraph()
        r_s = p_sub.add_run()
        r_s.text = c["subtitle"]
        r_s.font.name = FONT_BODY
        r_s.font.size = Pt(9)
        r_s.font.color.rgb = RGBColor(160, 170, 185)
        p_sub.space_after = Pt(10)
        
        # Bullets
        for b_title, b_desc in c["bullets"]:
            p_b = tf_c.add_paragraph()
            r_bt = p_b.add_run()
            r_bt.text = f"• {b_title}：\n  "
            r_bt.font.name = FONT_HEADING
            r_bt.font.size = Pt(9.5)
            r_bt.font.bold = True
            r_bt.font.color.rgb = RGBColor(245, 245, 250)
            
            r_bd = p_b.add_run()
            r_bd.text = b_desc
            r_bd.font.name = FONT_BODY
            r_bd.font.size = Pt(9)
            r_bd.font.color.rgb = RGBColor(185, 190, 200)
            p_b.space_after = Pt(8)
            
        # Bottom Link Button inside card
        l_btn, t_btn, w_btn, h_btn = px(c["x"] + 16, 585, c["w"] - 32, 36)
        btn_shape = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l_btn, t_btn, w_btn, h_btn)
        style_box(btn_shape, RGBColor(32, 44, 62), c["border_color"], 1.5)
        tf_btn = btn_shape.text_frame
        tf_btn.word_wrap = False
        tf_btn.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_btn = tf_btn.paragraphs[0]
        p_btn.alignment = PP_ALIGN.CENTER
        r_btn = p_btn.add_run()
        r_btn.text = f"📖 閱讀文章 ➔ {c['url_text']}"
        r_btn.font.name = FONT_CODE
        r_btn.font.size = Pt(9.5)
        r_btn.font.bold = True
        r_btn.font.color.rgb = RGBColor(102, 252, 241)
        btn_shape.click_action.hyperlink.address = c["url"]
            
    # Bottom callout banner: x=60, y=648, w=1255, h=48
    l_bot, t_bot, w_bot, h_bot = px(60, 648, 1255, 48)
    bot_box = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l_bot, t_bot, w_bot, h_bot)
    style_box(bot_box, RGBColor(20, 28, 42), RGBColor(0, 180, 216), 1)
    tf_bot = bot_box.text_frame
    tf_bot.word_wrap = True
    tf_bot.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_bot.margin_left = Emu(int(14 * EMU_PER_PX_X))
    tf_bot.margin_right = Emu(int(14 * EMU_PER_PX_X))
    
    p_bot = tf_bot.paragraphs[0]
    r_bot1 = p_bot.add_run()
    r_bot1.text = "💡 學習價值： "
    r_bot1.font.name = FONT_HEADING
    r_bot1.font.size = Pt(10)
    r_bot1.font.bold = True
    r_bot1.font.color.rgb = RGBColor(255, 215, 0)
    
    r_bot2 = p_bot.add_run()
    r_bot2.text = "本課程奠定企業級效能工程體系，專欄文章則引領大家攻克真實業務中的前沿自訂挑戰，推薦課後務必搭配精讀！"
    r_bot2.font.name = FONT_BODY
    r_bot2.font.size = Pt(9.5)
    r_bot2.font.color.rgb = RGBColor(220, 225, 235)
    
    add_codelab_banner(s10)
    
    # 5. Slide 11: Original Slide 10 (Hands-on Practice) with banner
    s11 = prs.slides.add_slide(blank)
    s11.shapes.add_picture('/tmp/ch5_extracted/image10.png', 0, 0, width=SW, height=SH)
    add_codelab_banner(s11)
    
    output_path = 'k6/slides/Ch5_k6_Observability_and_Modular_Architecture.pptx'
    prs.save(output_path)
    print(f"Successfully saved {len(prs.slides)} slides to {output_path}")

if __name__ == '__main__':
    build_presentation()
