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

SCENE_1 = """
<div><span class='prompt'>nathan@o11y-lab</span>:<span class='path'>~/Project/o11y_lab_for_dummies</span>$ <span class='cmd'>k6 x agent status</span></div>
<div class='dim'>time="2026-09-21T23:55:00+08:00" level=info msg="Using cached k6 binary" artifact_id=976b21276989 deps="map[k6:v2.2.0 subcommand:agent:v0.2.1]"</div>
<br>
<div class='white-bold'>Agent installation status</div>
<br>
<div><span class='green-txt'>[+]</span> <span class='white-bold'>Claude Code</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class='green-txt'>.mcp.json detected</span> &nbsp;<span class='dim'>(skills in .claude/skills/)</span></div>
<div><span class='dim'>[-]</span> <span class='white-bold'>Cline</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class='dim'>Not detected in this workspace (Hint: k6 x agent init cline)</span></div>
<div><span class='dim'>[-]</span> <span class='white-bold'>OpenAI Codex CLI</span> &nbsp;&nbsp;&nbsp;<span class='dim'>Missing: .codex/mcp.json (Hint: k6 x agent init codex-cli)</span></div>
<div><span class='green-txt'>[+]</span> <span class='white-bold'>Cursor</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class='green-txt'>.cursor/mcp.json detected</span> &nbsp;<span class='dim'>(rules in .cursor/rules/)</span></div>
<div><span class='dim'>[-]</span> <span class='white-bold'>OpenCode</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class='dim'>Missing: opencode.json (Hint: k6 x agent init opencode)</span></div>
<div><span class='dim'>[-]</span> <span class='white-bold'>VSCode Copilot</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class='dim'>Missing: .vscode/mcp.json (Hint: k6 x agent init vscode-copilot)</span></div>
<br>
<div><span class='green-txt'>[+]</span> <span class='white-bold'>k6 MCP support</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class='cyan'>Found at /usr/bin/k6 (subcommand:mcp:v0.6.1 active)</span></div>
<br>
<div class='dim'># 狀態更新：Claude Code 與 Cursor 雙編輯器均已就緒，MCP 與技能均正常掛載！</div>
"""

SCENE_SKILLS = """
<div><span class='prompt'>nathan@o11y-lab</span>:<span class='path'>~/Project/o11y_lab_for_dummies</span>$ <span class='cmd'>k6 x agent skills list</span></div>
<div class='dim'>time="2026-09-21T23:55:01+08:00" level=info msg="Using cached k6 binary" artifact_id=976b21276989 deps="map[k6:v2.2.0 subcommand:agent:v0.2.1]"</div>
<br>
<div class='cyan'><span style='display:inline-block;width:240px;'>NAME</span> <span>DESCRIPTION</span></div>
<div><span class='white-bold' style='display:inline-block;width:240px;'>k6-browser-test</span> <span class='dim'>Write a k6 browser test that drives headless Chromium...</span></div>
<div><span class='white-bold' style='display:inline-block;width:240px;'>k6-cloud-investigate-test</span> <span class='dim'>Investigate Grafana Cloud k6 test runs and diagnostics...</span></div>
<div><span class='white-bold' style='display:inline-block;width:240px;'>k6-docs</span> <span class='dim'>Look up official k6 documentation with `k6 x docs`...</span></div>
<div><span class='white-bold' style='display:inline-block;width:240px;'>k6-load-test</span> <span class='dim'>Generate production-grade load test scripts with stages...</span></div>
<div><span class='white-bold' style='display:inline-block;width:240px;'>k6-playwright-converter</span> <span class='dim'>Convert Playwright/Puppeteer scripts to k6 browser tests...</span></div>
<div><span class='white-bold' style='display:inline-block;width:240px;'>k6-smoke-test</span> <span class='dim'>Quick 1-2 VU smoke test to verify basic endpoint health...</span></div>
<div><span class='white-bold' style='display:inline-block;width:240px;'>k6-test-planner</span> <span class='dim'>Plan k6 test suites from natural-language requirements...</span></div>
<div><span class='white-bold' style='display:inline-block;width:240px;'>k6-trend-analysis</span> <span class='dim'>Analyze Grafana Cloud test trends and detect regressions...</span></div>
<br>
<div><span class='prompt'>nathan@o11y-lab</span>:<span class='path'>~/Project/o11y_lab_for_dummies</span>$ <span class='cmd'>k6 x agent skills show k6-smoke-test | head -n 4</span></div>
<div class='green-txt'>You are a senior k6 performance engineer. You create lightweight smoke tests</div>
<div class='green-txt'>that verify an application's basic functionality under minimal load...</div>
"""

SCENE_2 = """
<div><span class='prompt'>nathan@o11y-lab</span>:<span class='path'>~/Project/o11y_lab_for_dummies</span>$ <span class='cmd'>k6 x agent init cursor --dry-run</span></div>
<div class='dim'>time="2026-09-21T23:33:05+08:00" level=info msg="Using cached k6 binary" artifact_id=976b21276989 deps="map[k6:v2.2.0 subcommand:agent:v0.2.1]"</div>
<br>
<div class='white-bold'>Initializing k6 agents for Cursor</div>
<br>
<div class='cyan'>Cursor (dry-run):</div>
<div>  <span class='green-txt'>[create]</span> .cursor/rules/k6-browser-test.mdc <span class='dim'>(3,750 bytes)</span></div>
<div>  <span class='green-txt'>[create]</span> .cursor/rules/k6-cloud-investigate-test.mdc <span class='dim'>(15,278 bytes)</span></div>
<div>  <span class='green-txt'>[create]</span> .cursor/rules/k6-docs.mdc <span class='dim'>(3,716 bytes)</span></div>
<div>  <span class='green-txt'>[create]</span> .cursor/rules/k6-load-test.mdc <span class='dim'>(5,025 bytes)</span></div>
<div>  <span class='green-txt'>[create]</span> .cursor/rules/k6-manage.mdc <span class='dim'>(47,410 bytes)</span></div>
<div>  <span class='green-txt'>[create]</span> .cursor/rules/k6-perf-test-website.mdc <span class='dim'>(13,565 bytes)</span></div>
<div>  <span class='green-txt'>[create]</span> .cursor/rules/k6-playwright-converter.mdc <span class='dim'>(6,851 bytes)</span></div>
<div>  <span class='green-txt'>[create]</span> .cursor/rules/k6-smoke-test.mdc <span class='dim'>(2,569 bytes)</span></div>
<div>  <span class='green-txt'>[create]</span> .cursor/rules/k6-test-maintenance.mdc <span class='dim'>(9,691 bytes)</span></div>
<div>  <span class='green-txt'>[create]</span> .cursor/rules/k6-test-planner.mdc <span class='dim'>(2,981 bytes)</span></div>
<div>  <span class='green-txt'>[create]</span> .cursor/rules/k6-trend-analysis.mdc <span class='dim'>(19,072 bytes)</span></div>
<div>  <span class='yellow-txt'>[merge]</span>  .cursor/mcp.json <span class='dim'>(117 bytes)</span></div>
<br>
<div class='accent'>✨ 預覽模式完成：零副作用，未寫入磁碟。確認路徑正確後即可正式執行 init。</div>
"""

SCENE_3 = """
<div><span class='prompt'>nathan@o11y-lab</span>:<span class='path'>~/Project/o11y_lab_for_dummies</span>$ <span class='cmd'>k6 x agent init cursor</span></div>
<div class='dim'>Initializing k6 agents for Cursor ...</div>
<div class='green-txt'>Cursor: Updated 1 file(s) and generated 11 bundled skills rules. Done.</div>
<br>
<div><span class='prompt'>nathan@o11y-lab</span>:<span class='path'>~/Project/o11y_lab_for_dummies</span>$ <span class='cmd'>cat .cursor/mcp.json</span></div>
<div class='dim'>{</div>
<div>  <span class='cyan'>"mcpServers"</span>: {</div>
<div>    <span class='accent'>"k6"</span>: {</div>
<div>      <span class='cyan'>"command"</span>: <span class='green-txt'>"k6"</span>,</div>
<div>      <span class='cyan'>"args"</span>: [<span class='yellow-txt'>"x"</span>, <span class='yellow-txt'>"mcp"</span>]</div>
<div>    }</div>
<div>  }</div>
<div class='dim'>}</div>
<br>
<div><span class='prompt'>nathan@o11y-lab</span>:<span class='path'>~/Project/o11y_lab_for_dummies</span>$ <span class='cmd'>head -n 6 .cursor/rules/k6-smoke-test.mdc</span></div>
<div class='dim'>---</div>
<div><span class='cyan'>description</span>: <span class='dim'>"Use this skill when the user wants a quick k6 smoke test to verify basic endpoint health"</span></div>
<div><span class='cyan'>globs</span>: <span class='yellow-txt'>["*.js", "*.ts"]</span></div>
<div><span class='cyan'>alwaysApply</span>: <span class='accent'>false</span></div>
<div class='dim'>---</div>
<div class='dim'>&lt;!-- generated by k6 x agent --&gt;</div>
"""

SCENE_4 = """
<div><span class='prompt'>AI-Agent</span>:<span class='path'>MCP-Client</span>$ <span class='cmd'>call_tool("k6", "validate_script", { script: "ch6_quickpizza_smoke_agent.js" })</span></div>
<div class='dim'>[MCP JSON-RPC 2.0] Invoking k6 x mcp validate_script (1 VU, 1 iteration probe)...</div>
<br>
<div class='green-txt'>✓ Validation Result (Exit Code 0, Response 200 OK):</div>
<div class='dim'>{</div>
<div>  <span class='cyan'>"valid"</span>: <span class='green-txt'>true</span>,</div>
<div>  <span class='cyan'>"summary"</span>: { <span class='cyan'>"status"</span>: <span class='green-txt'>"success"</span>, <span class='cyan'>"issue_count"</span>: 0, <span class='cyan'>"ready_to_run"</span>: <span class='green-txt'>true</span> },</div>
<div>  <span class='cyan'>"stdout"</span>: <span class='dim'>"checks_succeeded: 100.00% (7/7) | http_req_duration: p(95)=194.4ms | failed: 0.00%"</span>,</div>
<div>  <span class='cyan'>"checks"</span>: [<span class='green-txt'>"✓ 首頁 200 OK"</span>, <span class='green-txt'>"✓ Config API 200"</span>, <span class='green-txt'>"✓ Quotes API 200"</span>],</div>
<div>  <span class='cyan'>"recommendations"</span>: [</div>
<div>    <span class='dim'>"✓ Validation passed! Your script is ready for load testing"</span>,</div>
<div>    <span class='dim'>"Recommended testing workflow: validate → run (small load) → analyze → scale up"</span></div>
<div>  ]</div>
<div class='dim'>}</div>
<br>
<div class='accent'>🤖 AI 助手自癒反饋：AST 語法結構通過，端點檢驗無誤，門檻 100% 達成。腳本已準備好進行大併發壓測！</div>
"""

SCENES = [
    {
        "id": "status",
        "badge_text": "STEP 1: 狀態診斷",
        "badge_class": "badge-cyan",
        "body": SCENE_1,
        "png_name": "k6-ch6-agent-status.png",
        "duration_ms": 3500
    },
    {
        "id": "skills_list",
        "badge_text": "STEP 2: 技能清單與檢索",
        "badge_class": "badge-purple",
        "body": SCENE_SKILLS,
        "png_name": "k6-ch6-agent-skills-list.png",
        "duration_ms": 3500
    },
    {
        "id": "dryrun",
        "badge_text": "STEP 3: 安全預覽",
        "badge_class": "badge-yellow",
        "body": SCENE_2,
        "png_name": "k6-ch6-agent-init-dryrun.png",
        "duration_ms": 3500
    },
    {
        "id": "init_cursor",
        "badge_text": "STEP 4: 編輯器初始化",
        "badge_class": "",
        "body": SCENE_3,
        "png_name": "k6-ch6-agent-init-cursor.png",
        "duration_ms": 3500
    },
    {
        "id": "mcp_validate",
        "badge_text": "STEP 5: MCP 閉環驗證",
        "badge_class": "badge-purple",
        "body": SCENE_4,
        "png_name": "k6-ch6-mcp-validation.png",
        "duration_ms": 4000
    }
]

def main():
    temp_dir = "/tmp/k6_ch6_terminal_frames"
    os.makedirs(temp_dir, exist_ok=True)
    
    asset_dir = "codelabs/tutorials/assets/images"
    os.makedirs(asset_dir, exist_ok=True)
    
    rendered_frames = []
    
    for idx, scene in enumerate(SCENES):
        html_file = os.path.join(temp_dir, f"scene_ch6_{idx}.html")
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
        
    gif_path = os.path.join(asset_dir, "k6-ch6-agent-workflow.gif")
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
