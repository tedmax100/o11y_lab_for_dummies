/**
 * Chapter 4 Live Demo: 全鏈路混合壓測 (Hybrid Testing 99:1 黃金配比實戰)
 * 
 * 核心教學亮點：
 * 1. 為什麼需要混合壓測？
 *    - 若 100% 都用無頭瀏覽器 (Browser)，1000 VU 可能需要 50 台高規格機器，成本失控。
 *    - 若 100% 都用協定級 (Protocol HTTP)，測不出 SPA 前端渲染阻塞與真實使用者的 Core Web Vitals。
 * 2. 99:1 黃金架構 (Golden Ratio Architecture)：
 *    - 99% 協定級流量 (Protocol-Level)：低成本、極致併發，模擬數千用戶轟炸後端 API。
 *    - 1% 瀏覽器級流量 (Browser-Level)：精準探測在高負載狀態下，真實使用者的 LCP/CLS 前端渲染體驗是否劣化！
 * 
 * 執行指令：
 * k6 run k6/demos/ch4_hybrid_99_to_1.js
 */

import http from 'k6/http';
import { browser } from 'k6/browser';
import { check, sleep } from 'k6';

export const options = {
  scenarios: {
    // ----------------------------------------------------
    // 場景 1：99% 協定級高負載 (Protocol Level API Flood)
    // ----------------------------------------------------
    protocol_flood: {
      executor: 'constant-vus',
      vus: 10,                 // 模擬後端併發背景負載
      duration: '10s',
      exec: 'protocolScenario',
    },

    // ----------------------------------------------------
    // 場景 2：1% 瀏覽器端真實體驗採樣 (Browser Level Web Vitals)
    // ----------------------------------------------------
    browser_sample: {
      executor: 'shared-iterations',
      vus: 1,                  // 少量真實瀏覽器探測針 (Probe)
      iterations: 1,
      startTime: '2s',         // 等待背景負載建立後再進場
      options: {
        browser: {
          type: 'chromium',
        },
      },
      exec: 'browserScenario',
    },
  },

  thresholds: {
    // 協定級指標門檻
    'http_req_duration{scenario:protocol_flood}': ['p(95)<1000'],
    'http_req_failed{scenario:protocol_flood}': ['rate<0.05'],

    // 瀏覽器體驗指標門檻 (受背景負載影響之下的真實感受)
    'browser_web_vital_lcp{scenario:browser_sample}': ['p(90)<3500'],
  },
};

// ----------------------------------------------------
// 協定級執行函式
// ----------------------------------------------------
export function protocolScenario() {
  const res = http.get('https://test.k6.io/contacts.php', {
    tags: { scenario: 'protocol_flood' },
  });

  check(res, {
    'Protocol 狀態碼為 200': (r) => r.status === 200,
  });

  sleep(0.5);
}

// ----------------------------------------------------
// 瀏覽器級執行函式
// ----------------------------------------------------
export async function browserScenario() {
  const page = await browser.newPage();
  try {
    console.log('[Hybrid Demo] 瀏覽器探測針進場，正在測量背景負載下的真實體驗...');
    await page.goto('https://quickpizza.grafana.com');

    const pizzaButton = page.locator('button[name="pizza-please"]');
    await pizzaButton.waitFor({ state: 'visible', timeout: 5000 });
    await pizzaButton.click();
    await page.waitForTimeout(1000);

    console.log('[Hybrid Demo] 瀏覽器成功取得披薩並完成 Web Vitals 採樣！');
  } finally {
    await page.close();
  }
}
