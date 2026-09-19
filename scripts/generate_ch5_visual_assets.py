import os
import subprocess
from PIL import Image

TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 12px;
    background: #090d16;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans CJK TC", sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
  }}
  ::-webkit-scrollbar {{ display: none; }}
  .window {{
    width: 900px;
    height: 540px;
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
    height: 40px;
    padding: 0 16px;
    display: flex;
    align-items: center;
    border-bottom: 1px solid #21262d;
    flex-shrink: 0;
  }}
  .dots {{ display: flex; gap: 8px; }}
  .dot {{ width: 12px; height: 12px; border-radius: 50%; }}
  .red {{ background: #ff5f56; }}
  .yellow {{ background: #ffbd2e; }}
  .green {{ background: #27c93f; }}
  .url-bar {{
    flex: 1;
    margin: 0 20px;
    background: #0b0f14;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 4px 12px;
    font-size: 11px;
    color: #8b949e;
    font-family: 'DejaVu Sans Mono', monospace;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .url-bar span.secure {{ color: #00e676; font-size: 12px; }}
  .url-bar span.addr {{ color: #e6edf3; }}
  .badge {{
    background: rgba(125, 100, 255, 0.2);
    color: #bb86fc;
    border: 1px solid rgba(125, 100, 255, 0.4);
    font-size: 11px;
    padding: 2px 10px;
    border-radius: 12px;
    font-weight: bold;
    letter-spacing: 0.3px;
  }}
  .badge-orange {{
    background: rgba(255, 103, 29, 0.2);
    color: #ff671d;
    border: 1px solid rgba(255, 103, 29, 0.4);
  }}
  .badge-cyan {{
    background: rgba(0, 229, 255, 0.2);
    color: #00e5ff;
    border: 1px solid rgba(0, 229, 255, 0.4);
  }}
  .content {{
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
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
    <div class='url-bar'>
      <span class='secure'>🔒</span>
      <span class='addr'>{url_addr}</span>
    </div>
    <div class='badge {badge_class}'>{badge_text}</div>
  </div>
  <div class='content'>
{body_content}
  </div>
</div>
</body>
</html>
"""

# Scene 1: k6 Web Dashboard (Dark Theme, React SPA)
SCENE_1_CONTENT = """
<style>
  .k6-nav {
    background: #111420;
    padding: 10px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #232738;
  }
  .k6-tabs { display: flex; gap: 8px; align-items: center; }
  .k6-logo { color: #7d64ff; font-weight: bold; font-size: 18px; display: flex; align-items: center; gap: 6px; }
  .tab-btn {
    background: transparent;
    color: #8f9bb3;
    border: none;
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
  }
  .tab-active { background: #222638; color: #ffffff; }
  .report-btn {
    background: #6c5ce7;
    color: white;
    border: none;
    padding: 6px 16px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 12px;
    letter-spacing: 0.5px;
  }
  .timer { color: #8f9bb3; font-size: 12px; margin-left: 12px; font-family: monospace; }
  .k6-body {
    padding: 16px 20px;
    background: #0d0f17;
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .cards-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 12px;
  }
  .card-item {
    background: #171b29;
    border: 1px solid #262c42;
    border-radius: 8px;
    padding: 12px 10px;
    text-align: center;
  }
  .card-title { color: #8f9bb3; font-size: 11px; margin-bottom: 6px; }
  .card-val { font-size: 20px; font-weight: bold; color: #ffffff; font-family: 'DejaVu Sans Mono', monospace; }
  .val-purple { color: #a29bfe; }
  .val-green { color: #00e676; }
  .val-cyan { color: #00e5ff; }
  .chart-box {
    background: #171b29;
    border: 1px solid #262c42;
    border-radius: 8px;
    padding: 14px 18px;
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }
  .chart-title { font-size: 13px; font-weight: 600; color: #e6edf3; }
  .legend { display: flex; gap: 16px; font-size: 11px; }
  .leg-item { display: flex; align-items: center; gap: 6px; }
  .leg-dot { width: 8px; height: 8px; border-radius: 2px; }
  .chart-svg { width: 100%; height: 160px; }
</style>
<div class="k6-nav">
  <div class="k6-tabs">
    <div class="k6-logo">
      <svg width="20" height="20" viewBox="0 0 37 34" fill="#7D64FF"><path fill-rule="evenodd" clip-rule="evenodd" d="M19.9129 12.4547L29.0217 0L36.6667 33.1967H0L12.2687 6.86803L19.9129 12.4547ZM15.1741 24.4166L17.3529 27.4205L19.6915 27.4198L17.1351 23.8957L19.3864 20.7907L17.8567 19.6768L15.1741 23.3764V17.7248L13.1575 16.2575V27.4205H15.1741V24.4166ZM20.0105 24.1067C20.0105 26.0056 21.5468 27.5452 23.4425 27.5452C25.3396 27.5452 26.8759 26.0056 26.8759 24.1075C26.8746 23.2903 26.5844 22.5003 26.0573 21.8786C25.5301 21.2569 24.8003 20.8441 23.9983 20.714L25.6403 18.45L24.1105 17.3361L20.6675 22.0832C20.2395 22.6699 20.0093 23.379 20.0105 24.1067ZM24.9179 24.1067C24.9179 24.9226 24.2579 25.5843 23.4432 25.5843C23.2499 25.5848 23.0583 25.547 22.8795 25.473C22.7007 25.399 22.5382 25.2903 22.4011 25.153C22.2641 25.0158 22.1553 24.8528 22.081 24.6733C22.0066 24.4937 21.9681 24.3012 21.9677 24.1067C21.9677 23.2908 22.6277 22.6291 23.4432 22.6291C24.2572 22.6291 24.9179 23.2908 24.9179 24.1067Z"/></svg>
      k6
    </div>
    <button class="tab-btn tab-active">Overview</button>
    <button class="tab-btn">Timings</button>
    <button class="tab-btn">Summary</button>
  </div>
  <div style="display: flex; align-items: center;">
    <button class="report-btn">REPORT</button>
    <span class="timer">⏱ 15s / 30s</span>
  </div>
</div>
<div class="k6-body">
  <div class="cards-grid">
    <div class="card-item"><div class="card-title">Iteration Rate</div><div class="card-val val-cyan">4.2/s</div></div>
    <div class="card-item"><div class="card-title">HTTP Req Rate</div><div class="card-val val-cyan">8.4/s</div></div>
    <div class="card-item"><div class="card-title">P95 Duration</div><div class="card-val val-green">98 ms</div></div>
    <div class="card-item"><div class="card-title">Failed Rate</div><div class="card-val val-green">0.0 %</div></div>
    <div class="card-item"><div class="card-title">Received Rate</div><div class="card-val">17.2 kB/s</div></div>
    <div class="card-item"><div class="card-title">Active VUs</div><div class="card-val val-purple">5 / 5</div></div>
  </div>
  <div class="chart-box">
    <div class="chart-header">
      <div class="chart-title">HTTP Performance Overview (Real-Time Throughput &amp; Latency)</div>
      <div class="legend">
        <div class="leg-item"><div class="leg-dot" style="background:#00e5ff;"></div><span style="color:#00e5ff;">Request Rate (8.4/s)</span></div>
        <div class="leg-item"><div class="leg-dot" style="background:#00e676;"></div><span style="color:#00e676;">P95 Latency (98ms)</span></div>
        <div class="leg-item"><div class="leg-dot" style="background:#ff5f56;"></div><span style="color:#ff5f56;">Errors (0%)</span></div>
      </div>
    </div>
    <svg class="chart-svg" viewBox="0 0 800 160">
      <!-- Grid lines -->
      <line x1="0" y1="40" x2="800" y2="40" stroke="#262c42" stroke-dasharray="4"/>
      <line x1="0" y1="80" x2="800" y2="80" stroke="#262c42" stroke-dasharray="4"/>
      <line x1="0" y1="120" x2="800" y2="120" stroke="#262c42" stroke-dasharray="4"/>
      <!-- Area curves -->
      <path d="M0,130 Q100,120 200,90 T400,70 T600,65 T800,60 L800,150 L0,150 Z" fill="rgba(0, 229, 255, 0.12)"/>
      <path d="M0,130 Q100,120 200,90 T400,70 T600,65 T800,60" fill="none" stroke="#00e5ff" stroke-width="2.5"/>
      <!-- P95 line -->
      <path d="M0,140 Q120,135 240,110 T480,95 T700,92 T800,90" fill="none" stroke="#00e676" stroke-width="2"/>
      <!-- Data points -->
      <circle cx="200" cy="90" r="4" fill="#00e5ff"/>
      <circle cx="400" cy="70" r="4" fill="#00e5ff"/>
      <circle cx="600" cy="65" r="4" fill="#00e5ff"/>
      <circle cx="800" cy="60" r="4" fill="#00e5ff"/>
    </svg>
  </div>
</div>
"""

# Scene 2: handleSummary Standalone HTML Report
SCENE_2_CONTENT = """
<style>
  .report-wrap {
    flex: 1;
    background: #090c13;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
  }
  .report-card {
    background: #171d29;
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 30px 36px;
    width: 640px;
    box-shadow: 0 16px 40px rgba(0,0,0,0.6);
  }
  .rep-h1 {
    color: #66fcf1;
    font-size: 22px;
    font-weight: 700;
    margin: 0 0 20px 0;
    display: flex;
    align-items: center;
    gap: 10px;
    border-bottom: 2px solid #233544;
    padding-bottom: 14px;
  }
  .rep-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #1f2838;
    font-size: 14px;
  }
  .rep-lbl { color: #a0aec0; }
  .rep-val { font-family: 'DejaVu Sans Mono', monospace; font-weight: bold; color: #45a29e; font-size: 15px; }
  .badge-pass {
    background: #00e676;
    color: #062b14;
    padding: 4px 12px;
    border-radius: 6px;
    font-weight: 800;
    font-size: 12px;
    letter-spacing: 0.5px;
  }
  .rep-footer {
    margin-top: 18px;
    font-size: 12px;
    color: #718096;
    display: flex;
    justify-content: space-between;
  }
</style>
<div class="report-wrap">
  <div class="report-card">
    <div class="rep-h1">
      <span>🚀</span>
      <span>k6 效能測試執行摘要 (handleSummary Hook 匯出)</span>
    </div>
    <div class="rep-row">
      <span class="rep-lbl">總請求數 (Total Requests)</span>
      <span class="rep-val">48 reqs</span>
    </div>
    <div class="rep-row">
      <span class="rep-lbl">P95 響應延遲 (p95 Latency)</span>
      <span class="rep-val" style="color:#00e676;">194.97 ms</span>
    </div>
    <div class="rep-row">
      <span class="rep-lbl">系統失敗率 (Failed Rate)</span>
      <span class="rep-val" style="color:#00e676;">0.00 %</span>
    </div>
    <div class="rep-row">
      <span class="rep-lbl">品質門禁評估 (SLO Gate Status)</span>
      <span class="badge-pass">PASSED</span>
    </div>
    <div class="rep-footer">
      <span>產出檔案: custom_report.html + summary.json</span>
      <span>可直接作為 GitLab / GitHub Actions 歸檔 Artifact</span>
    </div>
  </div>
</div>
"""

# Scene 3: Grafana Unified Dashboard (Prometheus Remote Write)
SCENE_3_CONTENT = """
<style>
  .grafana-nav {
    background: #181b1f;
    padding: 8px 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #2c3235;
  }
  .g-title { display: flex; align-items: center; gap: 8px; color: #f4f5f5; font-size: 13px; font-weight: 600; }
  .g-tags { display: flex; gap: 6px; }
  .g-tag { background: #262c30; color: #ff671d; font-size: 11px; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(255,103,29,0.3); }
  .g-body {
    background: #111217;
    flex: 1;
    padding: 14px 18px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .g-stats {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: 12px;
  }
  .g-stat {
    background: #181b1f;
    border: 1px solid #22252b;
    border-radius: 6px;
    padding: 10px 14px;
    position: relative;
    overflow: hidden;
  }
  .g-stat-lbl { color: #8e959d; font-size: 11px; font-weight: 500; }
  .g-stat-num { font-size: 24px; font-weight: bold; margin-top: 4px; font-family: 'DejaVu Sans Mono', monospace; }
  .c-green { color: #73bf69; }
  .c-yellow { color: #fade2a; }
  .c-blue { color: #5794f2; }
  .g-panels {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 12px;
    flex: 1;
  }
  .g-panel {
    background: #181b1f;
    border: 1px solid #22252b;
    border-radius: 6px;
    padding: 12px 14px;
    display: flex;
    flex-direction: column;
  }
  .g-panel-hdr { font-size: 12px; font-weight: 600; color: #d8d9da; margin-bottom: 8px; display: flex; justify-content: space-between; }
</style>
<div class="grafana-nav">
  <div class="g-title">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="#FF671D"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
    <span>Grafana / k6 Performance Engineering Dashboard</span>
  </div>
  <div class="g-tags">
    <span class="g-tag">commit: 2b367bd</span>
    <span class="g-tag">branch: main</span>
    <span class="g-tag">env: lab</span>
  </div>
</div>
<div class="g-body">
  <div class="g-stats">
    <div class="g-stat">
      <div class="g-stat-lbl">🚀 Total Requests (http_reqs)</div>
      <div class="g-stat-num c-green">48</div>
    </div>
    <div class="g-stat">
      <div class="g-stat-lbl">⚡ P95 Duration (SLO Target)</div>
      <div class="g-stat-num c-yellow">194.7 ms</div>
    </div>
    <div class="g-stat">
      <div class="g-stat-lbl">👥 Active Virtual Users</div>
      <div class="g-stat-num c-blue">3 VUs</div>
    </div>
    <div class="g-stat">
      <div class="g-stat-lbl">🎯 Business Success Rate</div>
      <div class="g-stat-num c-green">100.0 %</div>
    </div>
  </div>
  <div class="g-panels">
    <div class="g-panel">
      <div class="g-panel-hdr">
        <span>📈 HTTP Request Duration Percentiles (P90 / P95 / P99)</span>
        <span style="color:#8e959d; font-size:11px;">avg(k6_http_req_duration_*)</span>
      </div>
      <svg style="width:100%; height:160px;" viewBox="0 0 540 160">
        <line x1="0" y1="30" x2="540" y2="30" stroke="#22252b"/>
        <line x1="0" y1="70" x2="540" y2="70" stroke="#22252b"/>
        <line x1="0" y1="110" x2="540" y2="110" stroke="#22252b"/>
        <!-- P99 Line (Blue) -->
        <polyline fill="none" stroke="#5794f2" stroke-width="2" points="0,50 80,48 160,52 240,49 320,51 400,48 480,50 540,47"/>
        <!-- P95 Line (Yellow SLO) -->
        <polyline fill="none" stroke="#fade2a" stroke-width="2.5" points="0,75 80,73 160,76 240,74 320,75 400,72 480,74 540,71"/>
        <!-- P90 Line (Green) -->
        <polyline fill="none" stroke="#73bf69" stroke-width="2" points="0,105 80,103 160,106 240,104 320,105 400,102 480,103 540,100"/>
        <!-- Legend labels -->
        <circle cx="20" cy="148" r="4" fill="#5794f2"/><text x="30" y="152" fill="#8e959d" font-size="10">P99 Tail</text>
        <circle cx="120" cy="148" r="4" fill="#fade2a"/><text x="130" y="152" fill="#8e959d" font-size="10">P95 SLO</text>
        <circle cx="220" cy="148" r="4" fill="#73bf69"/><text x="230" y="152" fill="#8e959d" font-size="10">P90</text>
      </svg>
    </div>
    <div class="g-panel">
      <div class="g-panel-hdr">
        <span>🏷️ Requests by Tagged Endpoint</span>
      </div>
      <svg style="width:100%; height:160px;" viewBox="0 0 240 160">
        <!-- Pie Chart representation -->
        <circle cx="120" cy="75" r="50" fill="none" stroke="#fade2a" stroke-width="24" stroke-dasharray="157 157" stroke-dashoffset="0"/>
        <circle cx="120" cy="75" r="50" fill="none" stroke="#73bf69" stroke-width="24" stroke-dasharray="157 157" stroke-dashoffset="157"/>
        <text x="60" y="148" fill="#fade2a" font-size="11" font-weight="bold">● critical (50%)</text>
        <text x="150" y="148" fill="#73bf69" font-size="11" font-weight="bold">● background (50%)</text>
      </svg>
    </div>
  </div>
</div>
"""

SCENES = [
    {
        "id": "web_dashboard",
        "url_addr": "http://127.0.0.1:5665/ (Native Web Dashboard)",
        "badge_text": "DEMO 1/3: 本地即時動態儀表板",
        "badge_class": "badge-cyan",
        "body": SCENE_1_CONTENT,
        "png_name": "k6-ch5-web-dashboard.png",
        "duration_ms": 3600
    },
    {
        "id": "handlesummary",
        "url_addr": "file:///path/to/custom_report.html (handleSummary)",
        "badge_text": "DEMO 2/3: handleSummary 自訂報表",
        "badge_class": "",
        "body": SCENE_2_CONTENT,
        "png_name": "k6-ch5-handlesummary-report.png",
        "duration_ms": 3600
    },
    {
        "id": "grafana_prometheus",
        "url_addr": "http://localhost:3000/d/k6-live-metrics/ (Grafana)",
        "badge_text": "DEMO 3/3: Prometheus RW + Grafana",
        "badge_class": "badge-orange",
        "body": SCENE_3_CONTENT,
        "png_name": "k6-ch5-grafana-dashboard.png",
        "duration_ms": 4000
    }
]

def main():
    temp_dir = "/tmp/k6_ch5_frames"
    os.makedirs(temp_dir, exist_ok=True)
    
    asset_dir = "codelabs/tutorials/assets/images"
    os.makedirs(asset_dir, exist_ok=True)
    
    rendered_frames = []
    
    for idx, scene in enumerate(SCENES):
        html_file = os.path.join(temp_dir, f"scene_ch5_{idx}.html")
        png_file = os.path.join(asset_dir, scene["png_name"])
        
        full_html = TEMPLATE.format(
            url_addr=scene["url_addr"],
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
            "--window-size=924,564",
            f"file://{html_file}"
        ]
        subprocess.run(cmd, check=True)
        print(f"Generated screenshot: {png_file}")
        
        img = Image.open(png_file).convert("RGB")
        rendered_frames.append((img, scene["duration_ms"]))
        
    # Generate animated GIF
    gif_path = os.path.join(asset_dir, "k6-ch5-observability-demo.gif")
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
