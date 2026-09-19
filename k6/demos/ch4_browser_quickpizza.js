/**
 * Chapter 4 Live Demo: k6/browser 端到端真實瀏覽器渲染測試 (QuickPizza 實戰)
 * 
 * 核心教學亮點：
 * 1. Protocol-Level vs Browser-Level 差異：
 *    - 協定級壓測只能收到 HTML 字串，無法執行 JavaScript、無法渲染 DOM、無法計算 Web Vitals。
 *    - k6/browser 驅動無頭瀏覽器 (Headless Chromium)，真實測量 LCP、FCP、CLS、TTFB 等前端核心體驗指標。
 * 2. 核心 API 生命週期與資源防漏：
 *    - const page = await browser.newPage() 建立分頁。
 *    - 使用 CSS 選擇器定位元素：page.locator('button[name="pizza-please"]').click()。
 *    - 必須在 finally 區塊調用 await page.close()，防止內存洩漏與 Chrome 殭屍行程！
 * 
 * 執行指令：
 * k6 run k6/demos/ch4_browser_quickpizza.js
 */

import { browser } from 'k6/browser';
import { check } from 'k6';

export const options = {
  scenarios: {
    ui_test: {
      executor: 'shared-iterations',
      vus: 1,
      iterations: 1,
      options: {
        browser: {
          type: 'chromium',
        },
      },
    },
  },
  thresholds: {
    checks: ['rate==1.0'],
    browser_web_vital_lcp: ['p(95)<3000'], // LCP 小於 3 秒
    browser_web_vital_fcp: ['p(95)<2500'], // FCP 小於 2.5 秒
  },
};

export default async function () {
  const page = await browser.newPage();

  try {
    console.log('[Browser] 正在啟動 Chromium 並造訪 QuickPizza...');
    await page.goto('https://quickpizza.grafana.com');

    // 驗證首頁標題
    const title = await page.title();
    check(page, {
      '頁面標題為 QuickPizza': () => title.includes('QuickPizza'),
    });

    // 尋找披薩推薦按鈕並點擊
    const pizzaButton = page.locator('button[name="pizza-please"]');
    await pizzaButton.waitFor({ state: 'visible', timeout: 5000 });
    
    console.log('[Browser] 找到下單推薦按鈕，觸發使用者點擊...');
    await pizzaButton.click();

    // 等待動態披薩配方生成
    await page.waitForTimeout(1500);

    console.log('[Browser] 披薩互動成功，順利採集到真實 Core Web Vitals！');

  } catch (err) {
    console.error(`[Browser] 執行發生錯誤: ${err.message}`);
    throw err;
  } finally {
    // 講稿避坑重點：務必確保 page.close()，否則會產生大量孤兒 Chromium 行程
    await page.close();
  }
}
