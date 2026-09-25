/**
 * Chapter 1 Demo：用 group() 把一趟使用者旅程分段統計
 *
 * 真實使用者做的是「一趟旅程」而不是「一個請求」。這支腳本模擬 QuickPizza 上的典型旅程：
 *   1. 瀏覽首頁 → 2. 取得披薩推薦 → 3. 登入後送出評分
 * 每一段用 group() 包起來，k6 就會依段落分開統計；每段的停頓 (think time) 也依情境不同。
 *
 * 執行（加上 --summary-mode=full 才會在摘要中看到依 group 拆開的統計）：
 *   k6 run --summary-mode=full k6/demos/ch1_group_journey.js
 */
import http from 'k6/http';
import { group, check, sleep } from 'k6';

const BASE = 'https://quickpizza.grafana.com';
const DEMO_TOKEN = 'abcdef0123456789'; // QuickPizza 公開的示範 token，只用於取得推薦
const JSON_HEADERS = { 'Content-Type': 'application/json' };

export const options = {
  vus: 5,
  duration: '1m',
  // 公開的 QuickPizza 位於負載平衡器後方，靠 cookie 把同一個使用者黏在同一台機器上。
  // k6 預設每次迭代都會清空 cookie；關掉它，這個 VU 註冊的帳號與 token 才會一直有效。
  noCookiesReset: true,
  thresholds: {
    // group 也能當成門檻的篩選條件（Chapter 3 會再深入）
    'http_req_duration{group:::送出評分}': ['p(95)<1500'],
  },
};

// 每個 VU 第一次迭代時註冊並登入一次，之後重複使用這個 token
let userToken;

function loginOnce() {
  if (userToken) return;
  const username = `k6_journey_${__VU}_${Date.now()}`;
  const creds = JSON.stringify({ username, password: 'k6-demo-pass' });
  http.post(`${BASE}/api/users`, creds, { headers: JSON_HEADERS, tags: { name: 'register' } });
  const res = http.post(`${BASE}/api/users/token/login`, creds, { headers: JSON_HEADERS, tags: { name: 'login' } });
  userToken = res.json('token');
}

export default function () {
  loginOnce();

  group('瀏覽首頁', function () {
    const res = http.get(`${BASE}/`);
    check(res, { '首頁 200': (r) => r.status === 200 });
    sleep(Math.random() * 2 + 1); // 掃一眼：1～3 秒
  });

  group('取得推薦', function () {
    const res = http.post(`${BASE}/api/pizza`, JSON.stringify({}), {
      headers: { ...JSON_HEADERS, Authorization: `token ${DEMO_TOKEN}` },
    });
    check(res, { '推薦 200': (r) => r.status === 200 });
    sleep(Math.random() * 5 + 3); // 挑選猶豫：3～8 秒
  });

  group('送出評分', function () {
    const res = http.post(`${BASE}/api/ratings`, JSON.stringify({ stars: 5, pizza_id: 1 }), {
      headers: { ...JSON_HEADERS, Authorization: `token ${userToken}` },
    });
    check(res, { '評分 201': (r) => r.status === 201 });
    sleep(Math.random() * 3 + 2); // 給分前想一想：2～5 秒
  });
}
