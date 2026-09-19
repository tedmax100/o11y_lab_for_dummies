/**
 * Chapter 4: HAR 轉換後依據「三大清理法則」重構之生產級腳本
 * 
 * 核心教學展示：
 * 1. 痛點再現：原 HAR 錄製檔含有過期的 Authorization Token，若直接執行必落入「401 死資料陷阱」。
 * 2. 清理法則 1：去靜態資源 (Don't load test Google!)
 *    - 剔除第三方 Google Analytics (google-analytics.com) 與外部 CDN。
 * 3. 清理法則 2：動態關聯 (Dynamic Correlation)
 *    - 在 setup() 呼叫官方登入端點 (/api/users/token/login)，動態取得最新 Token 並傳給 VU。
 * 4. 清理法則 3：結構化模組
 *    - 將長腳本拆解為語意清晰的 browseHomepage 與 orderPizza 業務函式。
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';

export const options = {
  vus: 5,
  duration: '5s',
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate<0.01'], // 0% 錯誤率門檻
    checks: ['rate==1.0'],
  },
};

// -----------------------------------------------------------
// 法則 2：動態關聯 (Dynamic Correlation) - 在 setup() 動態登入
// -----------------------------------------------------------
export function setup() {
  console.log('[Setup] 執行前置動態登入，向 QuickPizza 取得即時 Auth Token...');
  
  const loginUrl = 'https://quickpizza.grafana.com/api/users/token/login';
  const loginPayload = JSON.stringify({ username: 'default', password: '123' });
  const params = { headers: { 'Content-Type': 'application/json' } };

  const res = http.post(loginUrl, loginPayload, params);
  const success = check(res, {
    '登入成功取得 200': (r) => r.status === 200,
    '取得有效 Token': (r) => r.json('token') !== undefined,
  });

  if (!success) {
    throw new Error('無法取得動態 Token，終止測試');
  }

  const token = res.json('token');
  console.log(`[Setup] 成功取得動態 Token: ${token}，傳遞給所有 VU！`);
  return { authToken: token };
}

// -----------------------------------------------------------
// 法則 3：結構化模組 - 語意化函式封裝
// -----------------------------------------------------------
function browseHomepage() {
  const res = http.get('https://quickpizza.grafana.com/');
  check(res, { '首頁載入成功 (200)': (r) => r.status === 200 });
}

function orderPizza(token) {
  const pizzaUrl = 'https://quickpizza.grafana.com/api/pizza';
  const payload = JSON.stringify({});
  const params = {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Token ${token}`, // 動態注入 setup() 傳入的 Token
    },
  };

  const res = http.post(pizzaUrl, payload, params);
  check(res, {
    '動態下單成功 (200)': (r) => r.status === 200,
    '披薩推薦生成成功': (r) => r.json('pizza.name') !== undefined,
  });
}

// -----------------------------------------------------------
// VU 執行核心
// -----------------------------------------------------------
export default function (data) {
  group('用戶旅程：瀏覽首頁並動態下單', function () {
    browseHomepage();
    sleep(0.5);
    orderPizza(data.authToken);
    sleep(0.5);
  });
}

export function teardown(data) {
  console.log('[Teardown] 壓測圓滿結束，成功破除 401 死資料陷阱！');
}
