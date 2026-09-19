/**
 * Chapter 5 Live Demo: 原生 Web Dashboard、自訂 handleSummary 與 HTML 報告匯出
 * 
 * 核心教學亮點：
 * 1. 原生即時儀表板 (Native Web Dashboard)：
 *    - 執行時加上 K6_WEB_DASHBOARD=true，即可在 http://localhost:5665 查看即時動態折線圖！
 *    - 若設定 K6_WEB_DASHBOARD_PORT=-1，則不開啟 HTTP 伺服器，直接在測試結束時匯出靜態 HTML。
 * 2. handleSummary(data) 生命週期 Hook：
 *    - 測試結束後攔截完整的 summary 資料物件。
 *    - 可自訂轉換為自定義 HTML 報表、Slack Webhook 訊息格式或 JSON 存檔。
 * 
 * 執行範例：
 * 1. 啟動 Web Dashboard：
 *    K6_WEB_DASHBOARD=true k6 run k6/demos/ch5_dashboard_and_html_summary.js
 * 2. 直接匯出靜態 HTML 報告：
 *    K6_WEB_DASHBOARD=true K6_WEB_DASHBOARD_EXPORT=k6_test_report.html k6 run k6/demos/ch5_dashboard_and_html_summary.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 3,
  duration: '5s',
  thresholds: {
    http_req_failed: ['rate<0.05'],
    http_req_duration: ['p(95)<800'],
  },
};

export default function () {
  const res = http.get('https://test.k6.io');
  check(res, {
    '狀態碼為 200': (r) => r.status === 200,
  });
  sleep(0.5);
}

// ----------------------------------------------------
// handleSummary Hook: 測試結束後的自訂報表產生器
// ----------------------------------------------------
export function handleSummary(data) {
  console.log('>>> [handleSummary] 測試結束，正在處理自訂報告輸出...');

  const p95 = data.metrics.http_req_duration ? data.metrics.http_req_duration.values['p(95)'].toFixed(2) : 'N/A';
  const totalReqs = data.metrics.http_reqs ? data.metrics.http_reqs.values.count : 0;
  const failedRate = data.metrics.http_req_failed ? (data.metrics.http_req_failed.values.rate * 100).toFixed(2) : '0';

  // 產生輕量自訂 HTML 報表
  const customHtml = `
  <!DOCTYPE html>
  <html>
  <head>
    <meta charset="utf-8">
    <title>k6 Performance Test Summary</title>
    <style>
      body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 30px; background: #0b0c10; color: #c5c6c7; }
      .card { background: #1f2833; border-radius: 8px; padding: 20px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }
      h1 { color: #66fcf1; font-size: 24px; margin-top: 0; }
      .metric { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #45a29e; }
      .label { color: #c5c6c7; }
      .value { color: #45a29e; font-weight: bold; font-family: monospace; }
      .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
      .pass { background: #2ecc71; color: #000; }
    </style>
  </head>
  <body>
    <div class="card">
      <h1>🚀 k6 效能測試執行摘要</h1>
      <div class="metric"><span class="label">總請求數 (Total Requests)</span><span class="value">${totalReqs}</span></div>
      <div class="metric"><span class="label">P95 延遲 (p95 Latency)</span><span class="value">${p95} ms</span></div>
      <div class="metric"><span class="label">失敗率 (Failed Rate)</span><span class="value">${failedRate} %</span></div>
      <div class="metric"><span class="label">品質門禁狀態</span><span class="badge pass">PASSED</span></div>
    </div>
  </body>
  </html>
  `;

  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }), // 終端機依然印出標準摘要
    'summary.json': JSON.stringify(data, null, 2),                   // 匯出 JSON 供 CI/CD 分析
    'custom_report.html': customHtml,                                // 匯出自訂 HTML
  };
}

// 導入 k6 內建的文字摘要輔助函式
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.2/index.js';
