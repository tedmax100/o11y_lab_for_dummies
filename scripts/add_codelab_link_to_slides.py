import os
import sys
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

THEMES = {
    'Ch1': {
        'bg': RGBColor(255, 255, 255),
        'border': RGBColor(203, 213, 225),
        'label': RGBColor(51, 65, 85),
        'url': RGBColor(2, 132, 199),
    },
    'Ch2': {
        'bg': RGBColor(13, 32, 43),
        'border': RGBColor(14, 116, 144),
        'label': RGBColor(165, 243, 252),
        'url': RGBColor(56, 189, 248),
    },
    'Ch3': {
        'bg': RGBColor(248, 250, 252),
        'border': RGBColor(148, 163, 184),
        'label': RGBColor(30, 41, 59),
        'url': RGBColor(37, 99, 235),
    },
    'Ch4': {
        'bg': RGBColor(20, 21, 25),
        'border': RGBColor(16, 185, 129),
        'label': RGBColor(52, 211, 153),
        'url': RGBColor(110, 231, 183),
    },
    'Ch5': {
        'bg': RGBColor(6, 16, 30),
        'border': RGBColor(2, 132, 199),
        'label': RGBColor(186, 230, 253),
        'url': RGBColor(56, 189, 248),
    },
    'Ch6': {
        'bg': RGBColor(255, 255, 255),
        'border': RGBColor(203, 213, 225),
        'label': RGBColor(51, 65, 85),
        'url': RGBColor(79, 70, 229),
    }
}

DECKS = [
    ('Ch1', 'k6/slides/Ch1_Modern_Performance_Testing_with_k6.pptx'),
    ('Ch2', 'k6/slides/Ch2_Scientific_k6_Traffic_Modeling.pptx'),
    ('Ch3', 'k6/slides/Ch3_k6_Quality_Gates.pptx'),
    ('Ch4', 'k6/slides/Ch4_Precision_k6_Hybrid_Testing.pptx'),
    ('Ch5', 'k6/slides/Ch5_k6_Observability_and_Modular_Architecture.pptx'),
    ('Ch6', 'k6/slides/Ch6_k6_AI_Agent_Engineering.pptx'),
]

TARGET_URL = 'https://tedmax100.github.io/o11y_lab_for_dummies/k6-performance-testing/'
DISPLAY_URL = 'tedmax100.github.io/o11y_lab_for_dummies/k6-performance-testing/'

def add_badge_to_slide(slide, theme, left, top, width, height):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.name = "Codelabs_Link_Badge"
    shape.fill.solid()
    shape.fill.fore_color.rgb = theme['bg']
    shape.line.color.rgb = theme['border']
    shape.line.width = Pt(1)
    
    try:
        shape.click_action.hyperlink.address = TARGET_URL
    except Exception as e:
        print(f"Warning: could not set click_action: {e}")
        
    tf = shape.text_frame
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
    r1.font.color.rgb = theme['label']
    
    r2 = p.add_run()
    r2.text = DISPLAY_URL
    r2.font.name = 'Noto Sans CJK TC'
    r2.font.size = Pt(8.5)
    r2.font.bold = False
    r2.font.color.rgb = theme['url']

def main():
    total_slides = 0
    for ch_key, filepath in DECKS:
        prs = pptx.Presentation(filepath)
        theme = THEMES[ch_key]
        num_slides = len(prs.slides)
        print(f"Processing {ch_key} ({num_slides} slides)...")
        
        for idx, slide in enumerate(prs.slides):
            slide_num = idx + 1
            
            # Remove any existing badge for idempotency
            shapes_to_remove = [s for s in slide.shapes if s.name == "Codelabs_Link_Badge"]
            for s in shapes_to_remove:
                sp = s._element
                sp.getparent().remove(sp)
            
            # Default placement: bottom left
            left = Inches(0.55)
            top = Inches(9.70)
            width = Inches(6.6)
            height = Inches(0.24)
            
            # Custom layout exceptions
            if ch_key == 'Ch1' and slide_num == 10:
                # Slide 10 has k6 x Grafana on left; place in center footer
                left = Inches(3.8)
                top = Inches(9.70)
            elif ch_key == 'Ch3' and slide_num == 9:
                # Slide 9 has bottom quote; place in clean top-right header
                left = Inches(10.2)
                top = Inches(0.35)
            elif ch_key == 'Ch4' and slide_num == 8:
                # Slide 8 has bottom callout; place beside subtitle above architecture
                left = Inches(5.1)
                top = Inches(1.75)
                
            add_badge_to_slide(slide, theme, left, top, width, height)
            
        prs.save(filepath)
        print(f"Saved {filepath} with {num_slides} badges.")
        total_slides += num_slides

    print(f"\nAll done! Successfully added Codelabs link badge to all {total_slides} slides across 5 decks.")

if __name__ == '__main__':
    main()
