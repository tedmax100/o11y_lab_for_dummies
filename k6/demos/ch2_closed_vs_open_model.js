/**
 * Chapter 2 Live Demo: 閉環模型 vs 開放模型與協調性漏測 (Coordinated Omission)
 * 
 * 核心教學亮點：
 * 1. 閉環模型 (Closed Model - VUs/Stages)：
 *    - 併發虛擬用戶數固定。
 *    - 致命缺陷：當目標 API 發生延遲 (Latency Spike) 時，VU 必須「卡住等待回應」，
 *      導致實際發出的請求頻率 (RPS) 被迫下降！這就是典型的協調性漏測 (Coordinated Omission)。
 * 2. 開放模型 (Open Model - Arrival Rate)：
 *    - 依據 Little's Law ($L = \lambda W$) 精算：併發用戶數 = 抵達率 (RPS) × 平均回應時間。
 *    - 強制鎖定目標 RPS，當後端變慢時，引擎會自動從 preAllocatedVUs 擴充至 maxVUs 維持流量。
 *    - 若 maxVUs 耗盡，將產生 dropped_iterations，精準告警系統承載已達天花板！
 * 
 * 執行範例：
 * - 測試閉環模型：k6 run -e MODEL=closed k6/demos/ch2_closed_vs_open_model.js
 * - 測試開放模型：k6 run -e MODEL=open k6/demos/ch2_closed_vs_open_model.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';

const MODEL = __ENV.MODEL || 'open'; // 可切換 'closed' 或 'open'
const TARGET_URL = __ENV.TARGET_URL || 'https://httpbin.test.k6.io/delay/1'; // 模擬有延遲的端點

// 依據環境變數動態切換 Scenario
export const options = {
  scenarios: {
    // ----------------------------------------------------
    // 場景 A：閉環模型 (Closed Loop Model)
    // ----------------------------------------------------
    ...(MODEL === 'closed' ? {
      closed_model_demo: {
        executor: 'constant-vus',
        vus: 5,
        duration: '15s',
      },
    } : {}),

    // ----------------------------------------------------
    // 場景 B：開放模型 (Open Model - Little's Law)
    // ----------------------------------------------------
    ...(MODEL === 'open' ? {
      open_model_demo: {
        executor: 'constant-arrival-rate',
        rate: 20,              // 目標：每秒精準產生 20 次迭代 (20 RPS)
        timeUnit: '1s',
        duration: '15s',
        preAllocatedVUs: 10,   // 預先配置的 Goroutine (基準併發)
        maxVUs: 50,            // 應對延遲飆高時的最大緩衝池 (根據 Little's Law: 20 RPS * 2s = 40 VUs)
      },
    } : {}),
  },

  thresholds: {
    // 若使用開放模型且 maxVUs 不足，dropped_iterations 必須為 0
    'dropped_iterations': ['count==0'],
    'http_req_duration': ['p(95)<3000'],
  },
};

export default function () {
  const start = Date.now();
  
  // 發送請求至帶有 1 秒延遲的端點
  const res = http.get(TARGET_URL, {
    tags: { scenario_model: MODEL },
    timeout: '5s',
  });

  const duration = Date.now() - start;

  check(res, {
    '狀態碼為 200': (r) => r.status === 200,
  });

  // 口播說明：在開放模型中，迭代頻率由排程器主導，不受程式碼內 sleep() 影響
}
