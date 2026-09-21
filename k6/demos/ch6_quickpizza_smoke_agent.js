/**
 * Chapter 6 Live Demo: AI Agent 逆向生成與驗證的 QuickPizza 冒煙測試 (Smoke Test)
 * 
 * 本腳本由 k6 內建 AI 技能 (k6-smoke-test) 遵循最佳實踐規範自動生成：
 * 1. 嚴格遵循低負載原則：1 VU、單次迭代或極短時間 (3s) 快速驗證 API 基礎可用性。
 * 2. 避免高基數維度爆炸 (High Cardinality)：採用靜態 URL 標籤，不使用動態字串拼接。
 * 3. 宣告式 SLO 品質門檻：要求 100% checks 通過且失敗率為 0%。
 * 4. 相容 k6 MCP 伺服器：可透過 'validate_script' 與 'run_script' 進行語法與閉環自癒驗證。
 * 
 * 執行指令：
 * k6 run k6/demos/ch6_quickpizza_smoke_agent.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';

// ----------------------------------------------------
// 1. 冒煙測試配置 (Smoke Test Options)
// ----------------------------------------------------
export const options = {
  vus: 1,
  duration: '3s',
  thresholds: {
    // 冒煙品質門禁：不可有任何請求失敗，且 100% check 成功
    http_req_failed: ['rate==0.00'],
    http_req_duration: ['p(95)<1000'], // 95% 延遲小於 1 秒
    checks: ['rate==1.00'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://quickpizza.grafana.com';

// ----------------------------------------------------
// 2. VU 主執行邏輯 (Default function)
// ----------------------------------------------------
export default function () {
  // 1. 探測首頁 HTML
  const homeRes = http.get(BASE_URL, {
    tags: { name: 'GetHomePage' },
  });

  check(homeRes, {
    '首頁回應 200 OK': (r) => r.status === 200,
    '首頁包含 QuickPizza 標題': (r) => r.body && r.body.includes('QuickPizza'),
  });

  // 2. 探測系統組態 API (/api/config)
  const configRes = http.get(`${BASE_URL}/api/config`, {
    tags: { name: 'GetConfig' },
  });

  check(configRes, {
    'Config API 回應 200 OK': (r) => r.status === 200,
    'Config 回傳 JSON 格式': (r) => r.headers['Content-Type'] && r.headers['Content-Type'].includes('application/json'),
    'Config 包含環境資訊': (r) => {
      try {
        const data = r.json();
        return data && data.faro_app_environment !== undefined;
      } catch (e) {
        return false;
      }
    },
  });

  // 3. 查詢名言佳句 API (/api/quotes)
  const quotesRes = http.get(`${BASE_URL}/api/quotes`, {
    tags: { name: 'GetQuotes' },
  });

  check(quotesRes, {
    'Quotes API 回應 200 OK': (r) => r.status === 200,
    'Quotes 回傳陣列資料': (r) => {
      try {
        const data = r.json();
        return data && Array.isArray(data.quotes) && data.quotes.length > 0;
      } catch (e) {
        return false;
      }
    },
  });

  sleep(1);
}
