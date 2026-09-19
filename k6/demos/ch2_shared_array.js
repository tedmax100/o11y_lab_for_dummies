/**
 * Chapter 2 Live Demo: SharedArray 記憶體救援神技 (Memory Optimization)
 * 
 * 核心教學亮點：
 * 1. 記憶體爆炸陷阱：若在 default VU 程式碼或全域使用標準 JS Array 載入 50MB 測試資料，
 *    k6 為每個獨立的 JS Runtime (VU) 都會複製一份！1000 VU = 50GB 記憶體，直接 OOM Crash。
 * 2. SharedArray 神技：
 *    - 必須引入：import { SharedArray } from 'k6/data';
 *    - 底層採用 Read-only 唯讀共享記憶體，所有 VU 共享同一份記憶體區塊。
 *    - 無論併發 100 還是 10,000 VU，記憶體只佔用一次！
 * 
 * 執行指令：
 * k6 run k6/demos/ch2_shared_array.js
 */

import http from 'k6/http';
import { check } from 'k6';
import { SharedArray } from 'k6/data';

// ----------------------------------------------------
// 1. 使用 SharedArray 載入測試資料 (只在 Init 階段執行一次)
// ----------------------------------------------------
const users = new SharedArray('使用者資料集', function () {
  console.log('[SharedArray] 正在初始化 10,000 筆測試帳號至唯讀共享記憶體中...');
  
  // 模擬從 JSON 檔案或產生的龐大測試資料集
  const data = [];
  for (let i = 1; i <= 10000; i++) {
    data.push({
      userId: `user_${i}`,
      email: `test_user_${i}@example.com`,
      token: `auth_bearer_secret_token_${i}`,
      tier: i % 3 === 0 ? 'VIP' : 'Standard',
    });
  }
  return data;
});

export const options = {
  vus: 5,
  iterations: 10,
  thresholds: {
    'checks': ['rate==1.0'],
  },
};

export default function () {
  // 依據 VU ID 與 Iteration 分配資料，確保不重複或隨機取樣
  const userIndex = (__VU * 100 + __ITER) % users.length;
  const currentUser = users[userIndex];

  // 測試存取
  const isLoaded = check(currentUser, {
    '資料由 SharedArray 共享記憶體成功讀取': (u) => u && u.userId !== undefined,
    '使用者 Token 完整存在': (u) => u.token.startsWith('auth_bearer_'),
  });

  // 模擬發送帶有該用戶資料的請求
  const res = http.get(`https://test.k6.io/?user=${currentUser.userId}`);
  
  check(res, {
    '請求成功 200': (r) => r.status === 200,
  });
}
