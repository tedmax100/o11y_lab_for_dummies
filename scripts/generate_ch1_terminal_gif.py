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
    background: rgba(255, 103, 29, 0.18);
    color: #ff671d;
    border: 1px solid rgba(255, 103, 29, 0.4);
    font-size: 11px;
    padding: 2px 10px;
    border-radius: 12px;
    font-weight: bold;
    letter-spacing: 0.3px;
  }}
  .badge-purple {{
    background: rgba(125, 100, 255, 0.18);
    color: #bb86fc;
    border: 1px solid rgba(125, 100, 255, 0.4);
  }}
  .badge-cyan {{
    background: rgba(0, 229, 255, 0.18);
    color: #00e5ff;
    border: 1px solid rgba(0, 229, 255, 0.4);
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
  .yellow-txt {{ color: #ffd600; font-weight: bold; }}
  .dim {{ color: #6e7681; }}
  .white-bold {{ color: #ffffff; font-weight: bold; }}
  .tag {{
    display: inline-block;
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: bold;
  }}
  .tag-get {{ background: #005fb8; color: #ffffff; }}
  .tag-res {{ background: #0f6e38; color: #ffffff; }}
  .cursor {{
    display: inline-block;
    width: 8px;
    height: 14px;
    background: #00e5ff;
    vertical-align: middle;
    margin-left: 2px;
    animation: blink 1s infinite;
  }}
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
    <div><span class='prompt'>nathan@o11y-lab</span>:<span class='path'>~/demos</span>$ <span class='cmd'>k6 run k6/demos/ch1_lifecycle_and_checks.js</span></div>
    <div style='margin-top: 6px;' class='cyan'>          /\\      Grafana   /‾‾/  </div>
    <div class='cyan'>     /\\  /  \\     |\\  __   /  /   </div>
    <div class='cyan'>    /  \\/    \\    | |/ /  /   ‾‾\\ </div>
    <div class='cyan'>   /          \\   |   (  |  (‾)  |</div>
    <div class='cyan'>  / __________ \\  |_|\\_\\  \\_____/ </div>
    <div style='margin-top: 6px;' class='dim'>     execution: <span class='white-bold'>local</span> | script: <span class='white-bold'>k6/demos/ch1_lifecycle_and_checks.js</span></div>
    <div class='dim'>     scenarios: <span class='white-bold'>1 scenario, 2 max VUs, 4 iters</span> (options: vus: 2, iterations: 4)</div>
    <div style='margin-top: 6px;'><span class='dim'>[Init]</span> VU 1, VU 2 初始化腳本環境 (不可發送 HTTP)...</div>
    <div><span class='accent'>&gt;&gt;&gt; [Setup]</span> 正在準備全域測試環境 (取得 mock-jwt-token)...</div>
    <div><span class='dim'>[VU Code]</span> VU 1 &amp; 2 輪番發動：01_健康檢查交易 &amp; 02_核心業務流程...</div>
    <div><span class='accent'>&lt;&lt;&lt; [Teardown]</span> 壓測完成！4/4 次迭代全數通過，清理全域狀態...</div>
    <div style='margin-top: 6px;' class='white-bold'>  █ THRESHOLDS</div>
    <div>    checks .............: <span class='green-txt'>✓ 'rate&gt;0.9'</span> rate=100.00%</div>
    <div>    http_req_duration ..: <span class='green-txt'>✓ 'p(95)&lt;1000'</span> p(95)=0.74ms</div>
    <div>    http_req_failed ....: <span class='green-txt'>✓ 'rate&lt;0.05'</span> rate=0.00%</div>
    <div style='margin-top: 6px;' class='white-bold'>  █ TOTAL RESULTS</div>
    <div>    <span class='green-txt'>✓</span> 健康檢查狀態碼為 200        <span class='dim'>[4/4 passed]</span></div>
    <div>    <span class='green-txt'>✓</span> 健康檢查回應包含 healthy     <span class='dim'>[4/4 passed]</span></div>
    <div>    <span class='green-txt'>✓</span> 核心流程狀態碼為 200        <span class='dim'>[4/4 passed]</span></div>
    <div style='margin-top: 6px;' class='green-txt'>default ✓ [ 100% ] 2 VUs  00m01.0s/10m0s  4/4 shared iters</div>
"""

SCENE_2_BODY = """
    <div><span class='prompt'>nathan@o11y-lab</span>:<span class='path'>~/demos</span>$ <span class='cmd'>k6 run --vus 10 --duration 30s k6/demos/ch1_lifecycle_and_checks.js</span></div>
    <div style='margin-top: 6px;' class='cyan'>          /\\      Grafana   /‾‾/  </div>
    <div class='cyan'>     /\\  /  \\     |\\  __   /  /   </div>
    <div class='cyan'>    /  \\/    \\    | |/ /  /   ‾‾\\ </div>
    <div class='cyan'>   /          \\   |   (  |  (‾)  |</div>
    <div class='cyan'>  / __________ \\  |_|\\_\\  \\_____/ </div>
    <div style='margin-top: 6px;' class='dim'>     execution: <span class='white-bold'>local</span> | script: <span class='white-bold'>k6/demos/ch1_lifecycle_and_checks.js</span></div>
    <div class='dim'>     scenarios: <span class='yellow-txt'>* default: 10 looping VUs for 30s</span> <span class='accent'>(CLI Flags Overrides Script!)</span></div>
    <div style='margin-top: 6px;'><span class='yellow-txt'>[CLI Override]</span> 成功動態覆蓋！規模擴增：2 VUs ➔ <span class='white-bold'>10 VUs</span>，時間：<span class='white-bold'>30 秒穩態加壓</span></div>
    <div><span class='accent'>&gt;&gt;&gt; [Setup]</span> 全域初始化完成，並行調度 10 條 Goroutines 協程高頻壓測...</div>
    <div style='margin-top: 8px;'>running (0m03.2s), <span class='white-bold'>10/10 VUs</span>, 48 complete and 0 interrupted iterations</div>
    <div class='yellow-txt'>default   [  11% ] 10 VUs  03.2s/30s  <span class='dim'>████░░░░░░░░░░░░░░░░░░░░</span></div>
    <div style='margin-top: 8px;' class='white-bold'>  █ REAL-TIME METRICS (10 VUs Concurrent)</div>
    <div>    http_reqs ............: <span class='white-bold'>96 reqs</span> (30.0 reqs/sec 穩定輸出)</div>
    <div>    http_req_duration ....: avg=<span class='green-txt'>1.38ms</span>  min=0.21ms  p(95)=<span class='green-txt'>2.39ms</span></div>
    <div>    iteration_duration ...: avg=504ms (遵循 sleep(0.5) 模擬真實使用者思考時間)</div>
    <div style='margin-top: 6px;' class='white-bold'>  █ THRESHOLDS GATES</div>
    <div>    checks ...............: <span class='green-txt'>✓ 'rate&gt;0.9'</span> rate=100.00% (144/144 passed)</div>
    <div>    http_req_failed ......: <span class='green-txt'>✓ 'rate&lt;0.05'</span> rate=0.00% <span class='green-txt'>[SLO PASS]</span></div>
"""

SCENE_3_BODY = """
    <div><span class='prompt'>nathan@o11y-lab</span>:<span class='path'>~/demos</span>$ <span class='cmd'>k6 run --vus 1 --iterations 1 --http-debug k6/demos/ch1_lifecycle_and_checks.js</span></div>
    <div style='margin-top: 6px;'><span class='dim'>[Init]</span> VU 1 初始化... | <span class='accent'>&gt;&gt;&gt; [Setup]</span> 取得 mock-jwt-token-12345</div>
    <div style='margin-top: 6px; border-left: 3px solid #005fb8; padding-left: 8px;'>
      <div class='dim'>time="23:14:02" level=info source=http-debug group="::01_健康檢查交易" name=health_check</div>
      <div><span class='tag tag-get'>REQUEST</span> <span class='cyan'>GET /health HTTP/1.1</span> | Host: 127.0.0.1:8080 | User-Agent: Grafana k6/2.2.0</div>
      <div><span class='tag tag-res'>RESPONSE</span> <span class='green-txt'>HTTP/1.1 200 OK</span> | Content-Type: application/json</div>
      <div class='green-txt'>{ "status": "healthy", "service": "api-gateway" }</div>
    </div>
    <div style='margin-top: 8px; border-left: 3px solid #7d64ff; padding-left: 8px;'>
      <div class='dim'>time="23:14:02" level=info source=http-debug group="::02_核心業務流程" name=core_process_api</div>
      <div><span class='tag tag-get'>REQUEST</span> <span class='cyan'>GET /api/process?item_id=16 HTTP/1.1</span></div>
      <div class='dim'>  Authorization: Bearer mock-jwt-token-12345 | Accept-Encoding: gzip</div>
      <div><span class='tag tag-res'>RESPONSE</span> <span class='green-txt'>HTTP/1.1 200 OK</span> | Content-Type: application/json</div>
      <div class='green-txt'>{ "status": "ok", "result": "processed", "item_id": 16 }</div>
    </div>
    <div style='margin-top: 8px;'><span class='accent'>&lt;&lt;&lt; [Teardown]</span> 冒煙驗證完成！HTTP 通訊與 JSON 結構 100% 符合預期。</div>
    <div style='margin-top: 6px;' class='white-bold'>  █ SMOKE CHECK SUMMARY</div>
    <div>    ✓ 健康檢查狀態碼為 200 | ✓ 回應包含 healthy | ✓ 核心流程狀態碼為 200</div>
    <div style='margin-top: 4px;' class='green-txt'>default ✓ [ 100% ] 1 VUs  00m00.5s/10m0s  1/1 shared iters</div>
"""

SCENES = [
    {
        "id": "cmd1",
        "badge_text": "DEMO 1/3: 腳本預設 (vus: 2, iters: 4)",
        "badge_class": "",
        "body": SCENE_1_BODY,
        "png_name": "k6-ch1-cmd1-lifecycle.png",
        "duration_ms": 3200
    },
    {
        "id": "cmd2",
        "badge_text": "DEMO 2/3: CLI 覆蓋 (--vus 10 --duration 30s)",
        "badge_class": "badge-cyan",
        "body": SCENE_2_BODY,
        "png_name": "k6-ch1-cmd2-override.png",
        "duration_ms": 3500
    },
    {
        "id": "cmd3",
        "badge_text": "DEMO 3/3: 協定除錯 (--http-debug 封包透視)",
        "badge_class": "badge-purple",
        "body": SCENE_3_BODY,
        "png_name": "k6-ch1-cmd3-httpdebug.png",
        "duration_ms": 3800
    }
]

def main():
    temp_dir = "/tmp/k6_frames"
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
        
        # Load for animated GIF
        img = Image.open(png_file).convert("RGB")
        rendered_frames.append((img, scene["duration_ms"]))
        
    # Generate animated GIF
    gif_path = os.path.join(asset_dir, "k6-ch1-cli-options.gif")
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
    
    # Also update k6-demo.gif with this rich course-specific demo!
    k6_demo_path = os.path.join(asset_dir, "k6-demo.gif")
    first_img.save(
        k6_demo_path,
        save_all=True,
        append_images=other_imgs,
        duration=durations,
        loop=0,
        optimize=True
    )
    print(f"Updated: {k6_demo_path}")

if __name__ == "__main__":
    main()
