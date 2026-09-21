#!/usr/bin/env python3
"""
Rebuild `k6/slides/Ch1_Modern_Performance_Testing_with_k6.pptx` with 3 dedicated `k6 x agent` slides (Slides 5, 6, 7),
and generate a standalone 3-slide presentation `k6/slides/k6_x_agent.pptx`.
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

TARGET_URL = 'https://tedmax100.github.io/o11y_lab_for_dummies/k6-performance-testing/'
DISPLAY_URL = 'tedmax100.github.io/o11y_lab_for_dummies/k6-performance-testing/'

SLIDE_IMGS = [
    'k6/slides/assets/slide_k6_x_agent_1.png',
    'k6/slides/assets/slide_k6_x_agent_2.png',
    'k6/slides/assets/slide_k6_x_agent_3.png'
]

def add_hotspot(slide, x, y, w, h, url):
    l, t, width, height = px(x, y, w, h)
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, width, height)
    shape.fill.background()
    shape.line.fill.background()
    shape.click_action.hyperlink.address = url
    return shape

def add_codelab_badge(slide):
    for s in list(slide.shapes):
        if s.name == "Codelabs_Link_Badge":
            sp = s._element
            sp.getparent().remove(sp)

    left = Inches(0.55)
    top = Inches(9.70)
    width = Inches(6.60)
    height = Inches(0.24)
    
    badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    badge.name = "Codelabs_Link_Badge"
    badge.fill.solid()
    badge.fill.fore_color.rgb = RGBColor(255, 255, 255)
    badge.line.color.rgb = RGBColor(203, 213, 225)
    badge.line.width = Pt(1)
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
    r1.font.name = 'Noto Sans CJK TC'
    r1.font.size = Pt(8.5)
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(51, 65, 85)

    r2 = p.add_run()
    r2.text = DISPLAY_URL
    r2.font.name = 'Noto Sans CJK TC'
    r2.font.size = Pt(8.5)
    r2.font.bold = False
    r2.font.color.rgb = RGBColor(2, 132, 199)

def build_standalone_pptx():
    prs = pptx.Presentation()
    prs.slide_width = SW
    prs.slide_height = SH
    blank_layout = prs.slide_layouts[6]
    
    for idx, img_path in enumerate(SLIDE_IMGS):
        slide = prs.slides.add_slide(blank_layout)
        slide.shapes.add_picture(img_path, 0, 0, width=SW, height=SH)
        if idx == 2: # Slide 3 has hyperlinks
            add_hotspot(slide, 180, 700, 380, 18, "https://github.com/grafana/xk6-subcommand-agent")
            add_hotspot(slide, 170, 720, 560, 18, "https://grafana.com/docs/k6/latest/set-up/configure-ai-assistant/bootstrap-with-k6-x-agent/")
        add_codelab_badge(slide)

    out_path = 'k6/slides/k6_x_agent.pptx'
    prs.save(out_path)
    print(f"Created standalone 3-slide presentation: {out_path}")

def update_ch1_pptx():
    # Start fresh from backup or base Ch1 to ensure deterministic slide order
    base_ch1 = 'k6/slides_backup/Ch1_Modern_Performance_Testing_with_k6.pptx'
    prs = pptx.Presentation(base_ch1)
    
    # Base has 8 slides. Slide 1, 2, 5, 6, 7, 8 in original were:
    # 0: Cover
    # 1: Goroutines
    # 2: Lifecycle
    # 3: Group
    # 4: Check
    # 5: http.url
    # 6: 10-line script
    # 7: Summary
    # Wait, earlier we noticed current Ch1 had 10 slides because Slide 3 (Installation) and Slide 4 (AI/MCP) were added!
    # Let's extract the slides from current Ch1:
    current_ch1 = 'k6/slides/Ch1_Modern_Performance_Testing_with_k6.pptx'
    prs_curr = pptx.Presentation(current_ch1)
    
    # We want a new clean presentation with SW, SH
    prs_new = pptx.Presentation()
    prs_new.slide_width = SW
    prs_new.slide_height = SH
    blank = prs_new.slide_layouts[6]

    # Let's verify what images we have from earlier extraction:
    # /tmp/ch1_extracted/slide_1.png to slide_10.png
    # slide_1: Cover
    # slide_2: Goroutine
    # slide_3: Installation
    # slide_4: AI / MCP concept
    # Then we insert the 3 new k6 x agent slides!
    # slide_5 (orig): Lifecycle
    # slide_6 (orig): Group
    # slide_7 (orig): Check
    # slide_8 (orig): http.url
    # slide_9 (orig): 10-line code
    # slide_10 (orig): Summary
    
    slide_sequence = [
        ('/tmp/ch1_extracted/slide_1.png', False),
        ('/tmp/ch1_extracted/slide_2.png', False),
        ('/tmp/ch1_extracted/slide_3.png', False),
        ('/tmp/ch1_extracted/slide_4.png', False),
        # 3 New k6 x agent slides:
        ('k6/slides/assets/slide_k6_x_agent_1.png', False),
        ('k6/slides/assets/slide_k6_x_agent_2.png', False),
        ('k6/slides/assets/slide_k6_x_agent_3.png', True), # has hyperlinks
        # Remaining slides:
        ('/tmp/ch1_extracted/slide_5.png', False),
        ('/tmp/ch1_extracted/slide_6.png', False),
        ('/tmp/ch1_extracted/slide_7.png', False),
        ('/tmp/ch1_extracted/slide_8.png', False),
        ('/tmp/ch1_extracted/slide_9.png', False),
        ('/tmp/ch1_extracted/slide_10.png', False),
    ]

    for img_path, has_links in slide_sequence:
        s = prs_new.slides.add_slide(blank)
        s.shapes.add_picture(img_path, 0, 0, width=SW, height=SH)
        if has_links:
            add_hotspot(s, 180, 700, 380, 18, "https://github.com/grafana/xk6-subcommand-agent")
            add_hotspot(s, 170, 720, 560, 18, "https://grafana.com/docs/k6/latest/set-up/configure-ai-assistant/bootstrap-with-k6-x-agent/")
        add_codelab_badge(s)

    prs_new.save('k6/slides/Ch1_Modern_Performance_Testing_with_k6.pptx')
    print(f"Rebuilt Ch1 PPTX with {len(prs_new.slides)} slides!")

if __name__ == '__main__':
    build_standalone_pptx()
    update_ch1_pptx()
