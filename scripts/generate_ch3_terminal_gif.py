import os
import subprocess
from PIL import Image

TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<style>
  * {{
    box-sizing: border-box;
  }}
  body {{
    margin: 0;
    padding: 12px;
    background: #090d16;
    font-family: 'DejaVu Sans Mono', 'Noto Sans Mono CJK TC', 'Liberation Mono', monospace;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
  }}
  ::-webkit-scrollbar {{
    display: none;
  }}
  .window {{
    width: 860px;
    height: 520px;
    background: #0d1117;
    border-radius: 10px;
    border: 1px solid #30363d;
    box-shadow: 0 20px 45px rgba(0,0,0,0.7);
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }}
  .titlebar {{
    background: #161b22;
    height: 38px;
    padding: 0 16px;
    display: flex;
    align-items: center;
    border-bottom: 1px solid #21262d;
    flex-shrink: 0;
  }}
  .dots {{
    display: flex;
    gap: 8px;
  }}
  .dot {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
  }}
  .red {{ background: #ff5f56; }}
  .yellow {{ background: #ffbd2e; }}
  .green {{ background: #27c93f; }}
  .title {{
    flex: 1;
    text-align: center;
    font-size: 12px;
    color: #8b949e;
    letter-spacing: 0.5px;
  }}
  .badge {{
    background: rgba(0, 230, 118, 0.18);
    color: #00e676;
    border: 1px solid rgba(0, 230, 118, 0.4);
    font-size: 11px;
    padding: 2px 10px;
    border-radius: 12px;
    font-weight: bold;
    letter-spacing: 0.3px;
  }}
  .badge-red {{
    background: rgba(255, 95, 86, 0.18);
    color: #ff5f56;
    border: 1px solid rgba(255, 95, 86, 0.4);
  }}
  .badge-yellow {{
    background: rgba(255, 171, 0, 0.18);
    color: #ffb300;
    border: 1px solid rgba(255, 171, 0, 0.4);
  }}
  .terminal {{
    padding: 16px 20px;
    color: #e6edf3;
    font-size: 12px;
    line-height: 1.48;
    flex: 1;
    overflow: hidden;
  }}
  .prompt {{ color: #00e5ff; font-weight: bold; }}
  .path {{ color: #bb86fc; }}
  .cmd {{ color: #ffffff; font-weight: bold; }}
  .accent {{ color: #ff671d; }}
  .cyan {{ color: #00e5ff; }}
  .green-txt {{ color: #00e676; font-weight: bold; }}
  .red-txt {{ color: #ff5f56; font-weight: bold; }}
  .yellow-txt {{ color: #ffd600; font-weight: bold; }}
  .dim {{ color: #6e7681; }}
  .white-bold {{ color: #ffffff; font-weight: bold; }}
</style>
</head>
<body>
<div class='window'>
  <div class='titlebar'>
    <div class='dots'>
      <div class='dot red'></div>
      <div class='dot yellow'></div>
      <div class='dot green'></div>
    </div>
    <div class='title'>nathan@o11y-lab: ~/Project/o11y_lab_for_dummies</div>
    <div class='badge {badge_class}'>{badge_text}</div>
  </div>
  <div class='terminal'>
{body_content}
  </div>
</div>
</body>
</html>
"""

SCENE_1_BODY = """
    <div><span class='prompt'>nathan@o11y-lab</span>:<span class='path'>~/demos</span>$ <span class='cmd'>k6 run -e FAIL_SLO=false k6/demos/ch3_quality_gates_exit99.js ; echo "CI Exit Code: $?"</span></div>
    <div style='margin-top: 6px;' class='dim'>     scenarios: <span class='white-bold'>1 scenario, 3 max VUs, 6 iters</span> (options: vus: 3, iterations: 6)</div>
    <div style='margin-top: 6px;' class='white-bold'>  █ THRESHOLDS (Tagged &amp; Grouped SLOs)</div>
    <div>    business_transaction_success .......: <span class='green-txt'>✓ 'rate&gt;=0.95'</span> rate=100.00%</div>
    <div>    custom_db_processing_duration ......: <span class='green-txt'>✓ 'p(90)&lt;500'</span> p(90)=92.56ms</div>
    <div>    http_req_duration<span class='cyan'>{api_type:critical}</span> .: <span class='green-txt'>✓ 'p(95)&lt;1500'</span> p(95)=194.72ms</div>
    <div>    http_req_duration<span class='path'>{group:::01_核心結帳交易}</span>: <span class='green-txt'>✓ 'p(95)&lt;1000'</span> p(95)=194.72ms</div>
    <div>    http_req_duration<span class='path'>{group:::02_背景報表查詢}</span>: <span class='green-txt'>✓ 'p(95)&lt;3000'</span> p(95)=193.96ms</div>
    <div>    http_req_failed ....................: <span class='green-txt'>✓ 'rate&lt;0.05'</span> rate=0.00%</div>
    <div style='margin-top: 6px;' class='white-bold'>  █ TOTAL RESULTS (4 Custom Metrics &amp; Tag Breakdown)</div>
    <div>    active_workers_gauge ...............: <span class='white-bold'>3</span> (Gauge: 當前並行 Worker 水位)</div>
    <div>    orders_submitted_total .............: <span class='white-bold'>6</span> (Counter: 累計成交訂單數)</div>
    <div>    business_transaction_success .......: <span class='green-txt'>100.00%</span> (Rate: 業務邏輯成功率)</div>
    <div>    custom_db_processing_duration ......: avg=<span class='green-txt'>80.1ms</span> p(95)=<span class='green-txt'>93.6ms</span> (Trend: 模擬 DB 查詢)</div>
    <div>    http_req_duration <span class='cyan'>{api_type:critical}</span> ...: avg=99.5ms p(95)=<span class='green-txt'>194.7ms</span> [核心交易端點]</div>
    <div>    http_req_duration <span class='dim'>{api_type:background}</span> .: avg=97.7ms p(95)=<span class='green-txt'>193.9ms</span> [背景報表端點]</div>
    <div style='margin-top: 6px;'><span class='green-txt'>default ✓ [ 100% ] 3 VUs  00m01.9s/10m0s  6/6 shared iters</span></div>
    <div style='margin-top: 4px;' class='green-txt'>CI Exit Code: 0  (所有品質門檻皆達標，CI/CD 放行自動部署！)</div>
"""

SCENE_2_BODY = """
    <div><span class='prompt'>nathan@o11y-lab</span>:<span class='path'>~/demos</span>$ <span class='cmd'>k6 run -e FAIL_SLO=true k6/demos/ch3_quality_gates_exit99.js ; echo "CI Exit Code: $?"</span></div>
    <div style='margin-top: 6px;' class='dim'>     scenarios: <span class='white-bold'>1 scenario, 3 max VUs, 6 iters</span> (刻意縮緊核心 SLO: p(95)&lt;1ms)</div>
    <div style='margin-top: 6px;' class='white-bold'>  █ THRESHOLDS GATES EVALUATION</div>
    <div>    business_transaction_success .......: <span class='green-txt'>✓ 'rate&gt;=0.95'</span> rate=100.00%</div>
    <div>    custom_db_processing_duration ......: <span class='green-txt'>✓ 'p(90)&lt;500'</span> p(90)=96.59ms</div>
    <div style='background: rgba(255, 95, 86, 0.15); border-left: 3px solid #ff5f56; padding-left: 6px; margin: 2px 0;'>
      <div>    http_req_duration<span class='cyan'>{api_type:critical}</span> .: <span class='red-txt'>✗ 'p(95)&lt;1'</span> <span class='red-txt'>p(95)=194.83ms [SLO BREACH!]</span></div>
    </div>
    <div>    http_req_duration<span class='path'>{group:::01_核心結帳交易}</span>: <span class='green-txt'>✓ 'p(95)&lt;1000'</span> p(95)=194.83ms</div>
    <div>    http_req_duration<span class='path'>{group:::02_背景報表查詢}</span>: <span class='green-txt'>✓ 'p(95)&lt;3000'</span> p(95)=193.29ms</div>
    <div>    http_req_failed ....................: <span class='green-txt'>✓ 'rate&lt;0.05'</span> rate=0.00%</div>
    <div style='margin-top: 6px;' class='white-bold'>  █ TAG ISOLATION 精準隔離效果展示</div>
    <div>    ★ <span class='cyan'>critical 端點</span> 超標違規 ➔ <span class='red-txt'>觸發門禁警報</span></div>
    <div>    ★ <span class='dim'>background 端點</span> 耗時正常 ➔ <span class='green-txt'>未受波及</span> (成功避免全域無差別誤報！)</div>
    <div style='margin-top: 6px;' class='red-txt'>time="23:21:13" level=error msg="thresholds on metrics 'http_req_duration{api_type:critical}' have been crossed"</div>
    <div style='margin-top: 4px;' class='red-txt'>CI Exit Code: 99  (偵測到 SLO 違規，k6 回傳 99，自動阻斷 CI/CD 流水線！)</div>
"""

SCENE_3_BODY = """
    <div><span class='prompt'>nathan@o11y-lab</span>:<span class='path'>~/demos</span>$ <span class='cmd'>k6 run -e ABORT_TEST=true k6/demos/ch3_quality_gates_exit99.js ; echo "CI Exit Code: $?"</span></div>
    <div style='margin-top: 6px;' class='dim'>     scenarios: <span class='white-bold'>1 scenario, 3 max VUs, 20 iters</span> (配置 abortOnFail: true 熔斷止損)</div>
    <div style='margin-top: 6px;'>running (00m01.0s), 3/3 VUs, 0 complete iterations  default [  0% ]</div>
    <div style='margin-top: 2px;' class='yellow-txt'>running (00m02.0s), 3/3 VUs, 6 complete iterations  default [ 30% ] 06/20 iters</div>
    <div style='margin-top: 6px;' class='white-bold'>  █ THRESHOLDS STATUS (CIRCUIT BREAKER TRIGGERED)</div>
    <div style='background: rgba(255, 171, 0, 0.15); border-left: 3px solid #ffb300; padding-left: 6px; margin: 2px 0;'>
      <div>    business_transaction_success: <span class='red-txt'>✗ 'rate&gt;=0.95'</span> rate=0.00% <span class='yellow-txt'>[abortOnFail: true 熔斷啟動]</span></div>
    </div>
    <div>    http_req_duration{api_type:critical} ..: <span class='green-txt'>✓ 'p(95)&lt;1500'</span> p(95)=194.06ms</div>
    <div style='margin-top: 6px;' class='red-txt'>running (00m02.0s), 0/3 VUs, 6 complete and 3 interrupted iterations</div>
    <div class='red-txt'>default ✗ [ 30% ] 3 VUs  00m02.0s/10m0s  06/20 shared iters  (測試腰斬強制停止！)</div>
    <div style='margin-top: 6px; border-left: 3px solid #ff5f56; padding-left: 8px;'>
      <div class='red-txt'>time="23:21:18" level=error msg="thresholds on metrics 'business_transaction_success' were crossed; at least one has abortOnFail enabled, stopping test prematurely"</div>
    </div>
    <div style='margin-top: 6px;' class='white-bold'>  █ CIRCUIT BREAKER 止損成果</div>
    <div>    ✓ 僅執行 30% (6/20 iters) 立即熔斷，節省 70% 伺服器開銷與磁碟垃圾日誌！</div>
    <div style='margin-top: 4px;' class='red-txt'>CI Exit Code: 99  (熔斷終止測試，CI 自動標記 Job Failed)</div>
"""

SCENES = [
    {
        "id": "cmd1_pass",
        "badge_text": "DEMO 1/3: 標籤分組與 SLO 通過 (Exit 0)",
        "badge_class": "",
        "body": SCENE_1_BODY,
        "png_name": "k6-ch3-cmd1-pass.png",
        "duration_ms": 3500
    },
    {
        "id": "cmd2_fail",
        "badge_text": "DEMO 2/3: 標籤精準門禁違規 (Exit 99)",
        "badge_class": "badge-red",
        "body": SCENE_2_BODY,
        "png_name": "k6-ch3-cmd2-fail-exit99.png",
        "duration_ms": 3800
    },
    {
        "id": "cmd3_abort",
        "badge_text": "DEMO 3/3: 熔斷急停 (abortOnFail 止損)",
        "badge_class": "badge-yellow",
        "body": SCENE_3_BODY,
        "png_name": "k6-ch3-cmd3-abort-on-fail.png",
        "duration_ms": 3800
    }
]

def main():
    temp_dir = "/tmp/k6_ch3_frames"
    os.makedirs(temp_dir, exist_ok=True)
    
    asset_dir = "codelabs/tutorials/assets/images"
    os.makedirs(asset_dir, exist_ok=True)
    
    rendered_frames = []
    
    for idx, scene in enumerate(SCENES):
        html_file = os.path.join(temp_dir, f"scene_{idx}.html")
        png_file = os.path.join(asset_dir, scene["png_name"])
        
        full_html = TEMPLATE.format(
            badge_text=scene["badge_text"],
            badge_class=scene["badge_class"],
            body_content=scene["body"]
        )
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(full_html)
            
        cmd = [
            "google-chrome",
            "--headless",
            "--disable-gpu",
            f"--screenshot={png_file}",
            "--window-size=884,544",
            f"file://{html_file}"
        ]
        subprocess.run(cmd, check=True)
        print(f"Generated screenshot: {png_file}")
        
        img = Image.open(png_file).convert("RGB")
        rendered_frames.append((img, scene["duration_ms"]))
        
    # Generate animated GIF
    gif_path = os.path.join(asset_dir, "k6-ch3-quality-gates.gif")
    first_img, first_duration = rendered_frames[0]
    other_imgs = [f[0] for f in rendered_frames[1:]]
    durations = [f[1] for f in rendered_frames]
    
    first_img.save(
        gif_path,
        save_all=True,
        append_images=other_imgs,
        duration=durations,
        loop=0,
        optimize=True
    )
    print(f"Generated animated GIF: {gif_path} ({os.path.getsize(gif_path)} bytes)")

if __name__ == "__main__":
    main()
