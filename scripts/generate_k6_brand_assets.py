import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_banner():
    width, height = 1200, 420
    # Base image
    img = Image.new('RGBA', (width, height), (11, 15, 25, 255))
    draw = ImageDraw.Draw(img)
    
    # Background gradient & decorative tech elements
    for y in range(height):
        # subtle vertical gradient from #0d1322 to #070a12
        r = int(13 - (y / height) * 6)
        g = int(19 - (y / height) * 9)
        b = int(34 - (y / height) * 16)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
        
    # Subtle glow behind the logo
    glow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse([60, 40, 400, 380], fill=(255, 103, 29, 38))
    glow_draw.ellipse([700, -50, 1150, 400], fill=(125, 100, 255, 20))
    glow = glow.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)
    
    # Subtle border & corner accents
    border_color = (30, 41, 59, 255)
    draw.rectangle([1, 1, width - 2, height - 2], outline=border_color, width=2)
    
    # Tech corner ticks
    accent_orange = (255, 103, 29, 255)
    accent_purple = (125, 100, 255, 255)
    draw.line([(10, 10), (40, 10)], fill=accent_orange, width=3)
    draw.line([(10, 10), (10, 40)], fill=accent_orange, width=3)
    draw.line([(width - 40, height - 10), (width - 10, height - 10)], fill=accent_purple, width=3)
    draw.line([(width - 10, height - 40), (width - 10, height - 10)], fill=accent_purple, width=3)
    
    # Load and place k6 logo
    logo_path = 'codelabs/tutorials/assets/images/k6-logo.png'
    if os.path.exists(logo_path):
        k6_img = Image.open(logo_path).convert('RGBA')
        # Resize maintaining aspect ratio
        k6_img.thumbnail((260, 260), Image.Resampling.LANCZOS)
        # Center vertically around y=210
        img.paste(k6_img, (85, 80), k6_img)
        
    # Fonts
    font_bold_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
    font_en_bold = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    font_en = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    
    f_badge = ImageFont.truetype(font_en_bold, 13)
    f_title1 = ImageFont.truetype(font_en_bold, 54)
    f_title2 = ImageFont.truetype(font_en_bold, 54)
    f_sub = ImageFont.truetype(font_bold_path, 25)
    f_desc = ImageFont.truetype(font_bold_path, 16)
    f_tag = ImageFont.truetype(font_bold_path, 13)
    
    # Text positions (x starting at 400)
    tx = 400
    
    # Badge: GRAFANA LABS · PERFORMANCE TESTING
    badge_text = "GRAFANA LABS  |  OPEN SOURCE PERFORMANCE TESTING"
    draw.rounded_rectangle([tx, 65, tx + 450, 95], radius=6, fill=(35, 24, 20, 255), outline=(255, 103, 29, 180), width=1)
    draw.text((tx + 16, 72), badge_text, fill=(255, 160, 100, 255), font=f_badge)
    
    # Title: Grafana k6
    draw.text((tx, 112), "Grafana ", fill=(255, 255, 255, 255), font=f_title1)
    w_grafana = draw.textlength("Grafana ", font=f_title1)
    draw.text((tx + w_grafana, 112), "k6", fill=(255, 103, 29, 255), font=f_title2)
    
    # Subtitle: 現代化 Testing as Code 效能測試與可觀測性指南
    draw.text((tx, 185), "現代化 Testing as Code 效能測試手把手實戰", fill=(240, 246, 255, 255), font=f_sub)
    
    # English slogan
    draw.text((tx, 226), "Like unit testing, for performance. Built on Go Goroutines & ES6.", fill=(154, 165, 184, 255), font=f_desc)
    
    # Tags / feature highlights at bottom
    tags = [
        ("五大流量科學建模", (0, 229, 255)),
        ("Exit 99 CI 門禁", (255, 171, 0)),
        ("99:1 全鏈路混合壓測", (0, 230, 118)),
        ("Prometheus 串流對齊", (187, 134, 252))
    ]
    tag_x = tx
    for tag_text, tag_color in tags:
        tag_w = int(draw.textlength(tag_text, font=f_tag) + 24)
        draw.rounded_rectangle([tag_x, 280, tag_x + tag_w, 314], radius=16, fill=(18, 25, 38, 255), outline=tag_color, width=1)
        draw.text((tag_x + 12, 289), tag_text, fill=(235, 240, 250, 255), font=f_tag)
        tag_x += tag_w + 14
        
    out_path = 'codelabs/tutorials/assets/images/grafana-k6-banner.png'
    img.save(out_path, 'PNG', optimize=True)
    print(f"Created {out_path} ({width}x{height})")

def create_square_icon():
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Rounded dark box
    draw.rounded_rectangle([4, 4, size - 4, size - 4], radius=40, fill=(18, 24, 38, 255), outline=(255, 103, 29, 200), width=3)
    
    # Paste logo in center
    logo_path = 'codelabs/tutorials/assets/images/k6-logo.png'
    if os.path.exists(logo_path):
        k6_img = Image.open(logo_path).convert('RGBA')
        k6_img.thumbnail((170, 170), Image.Resampling.LANCZOS)
        w_l, h_l = k6_img.size
        px = (size - w_l) // 2
        py = (size - h_l) // 2
        img.paste(k6_img, (px, py), k6_img)
        
    out_path = 'codelabs/tutorials/assets/images/k6-icon-square.png'
    img.save(out_path, 'PNG', optimize=True)
    print(f"Created {out_path} ({size}x{size})")

def create_arch_diagram():
    w, h = 1100, 360
    img = Image.new('RGBA', (w, h), (11, 15, 25, 255))
    draw = ImageDraw.Draw(img)
    
    # Outer border
    draw.rectangle([1, 1, w - 2, h - 2], outline=(30, 41, 59, 255), width=2)
    
    font_bold_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
    font_en_bold = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    
    f_header = ImageFont.truetype(font_bold_path, 20)
    f_sub = ImageFont.truetype(font_bold_path, 12)
    f_card_title = ImageFont.truetype(font_bold_path, 15)
    f_bullet = ImageFont.truetype(font_bold_path, 12)
    
    # Header
    draw.text((40, 24), "k6 Testing as Code 核心架構與全鏈路閉環工作流", fill=(255, 255, 255, 255), font=f_header)
    draw.text((40, 56), "從開發端宣告式測試碼，經由輕量 Goroutine 引擎執行，到 CI/CD 門禁與雲原生監控時間軸對齊", fill=(148, 163, 184, 255), font=f_sub)
    
    cards = [
        {
            "num": "01",
            "title": "腳本撰寫 (Code)",
            "color": (0, 229, 255),
            "bg": (16, 28, 38),
            "bullets": ["JavaScript ES6 標準語法", "k6/http, k6/browser 模組", "check() 斷言與 group() 語意"]
        },
        {
            "num": "02",
            "title": "併發引擎 (Engine)",
            "color": (255, 103, 29),
            "bg": (32, 22, 18),
            "bullets": ["Go Goroutines 輕量協程", "每 VU 僅 1-4 KB 記憶體", "單機輕易發起萬級 RPS 流量"]
        },
        {
            "num": "03",
            "title": "品質門禁 (Gates)",
            "color": (255, 171, 0),
            "bg": (34, 26, 18),
            "bullets": ["宣告式 Thresholds 門檻", "自訂業務指標 Rate / Trend", "SLO 違規拋出 Exit Code 99"]
        },
        {
            "num": "04",
            "title": "全域可觀測 (O11y)",
            "color": (187, 134, 252),
            "bg": (26, 22, 38),
            "bullets": ["原生即時 Web 儀表板", "Prometheus Remote Write", "Grafana Pod CPU 限流對齊"]
        }
    ]
    
    card_w = 230
    card_h = 240
    start_x = 40
    gap = 40
    top_y = 95
    
    for i, c in enumerate(cards):
        cx = start_x + i * (card_w + gap)
        # Card shape
        draw.rounded_rectangle([cx, top_y, cx + card_w, top_y + card_h], radius=10, fill=c["bg"], outline=c["color"], width=1)
        
        # Step Number Badge
        draw.rounded_rectangle([cx + 14, top_y + 14, cx + 54, top_y + 38], radius=6, fill=(10, 15, 22, 255), outline=c["color"], width=1)
        draw.text((cx + 22, top_y + 18), c["num"], fill=c["color"], font=f_card_title)
        
        # Card Title
        draw.text((cx + 64, top_y + 18), c["title"], fill=(255, 255, 255, 255), font=f_card_title)
        
        # Divider line
        draw.line([(cx + 14, top_y + 52), (cx + card_w - 14, top_y + 52)], fill=(40, 50, 65, 255), width=1)
        
        # Bullets
        by = top_y + 68
        for b in c["bullets"]:
            draw.text((cx + 16, by), "●", fill=c["color"], font=f_bullet)
            draw.text((cx + 32, by), b, fill=(203, 213, 225, 255), font=f_bullet)
            by += 44
            
        # Arrow connecting cards
        if i < len(cards) - 1:
            ax = cx + card_w + 10
            ay = top_y + card_h // 2
            draw.line([(ax, ay), (ax + 20, ay)], fill=(100, 116, 139, 255), width=2)
            draw.polygon([(ax + 20, ay - 5), (ax + 28, ay), (ax + 20, ay + 5)], fill=(100, 116, 139, 255))
            
    out_path = 'codelabs/tutorials/assets/images/grafana-k6-arch.png'
    img.save(out_path, 'PNG', optimize=True)
    print(f"Created {out_path} ({w}x{h})")

if __name__ == '__main__':
    create_banner()
    create_square_icon()
    create_arch_diagram()
