/**
 * 壓力測試 (Stress Test)
 * 測試系統在高負載下的表現
 * 逐步增加負載直到系統出現瓶頸
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate } from 'k6/metrics';

const errorCounter = new Counter('errors');
const successRate = new Rate('success_rate');

export const options = {
  stages: [
    // 1. 預熱：10秒內升到10個用戶
    { duration: '10s', target: 10 },
    // 2. 穩定階段：維持10個用戶30秒
    { duration: '30s', target: 10 },
    // 3. 壓力階段1：30秒內升到50個用戶
    { duration: '30s', target: 50 },
    // 4. 維持壓力：維持50個用戶1分鐘
    { duration: '1m', target: 50 },
    // 5. 壓力階段2：30秒內升到100個用戶
    { duration: '30s', target: 100 },
    // 6. 高壓維持：維持100個用戶1分鐘
    { duration: '1m', target: 100 },
    // 7. 極限壓力：30秒內升到200個用戶
    { duration: '30s', target: 200 },
    // 8. 極限維持：維持200個用戶1分鐘
    { duration: '1m', target: 200 },
    // 9. 降載：30秒內降到0
    { duration: '30s', target: 0 },
  ],

  thresholds: {
    // 壓力測試允許較高的失敗率
    http_req_failed: ['rate<0.05'], // 失敗率 < 5%
    http_req_duration: ['p(95)<5000'], // 95% 請求 < 5秒
    success_rate: ['rate>0.90'], // 成功率 > 90%
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';

export function setup() {
  console.log('🔥 開始壓力測試 - 逐步增加負載');
  return { startTime: Date.now() };
}

export default function() {
  const res = http.get(`${BASE_URL}/api/process`, {
    timeout: '30s',
  });

  const success = check(res, {
    '狀態碼是 200': (r) => r.status === 200,
    '回應有效': (r) => {
      try {
        return r.json('status') !== undefined;
      } catch (e) {
        return false;
      }
    },
  });

  successRate.add(success);

  if (!success) {
    errorCounter.add(1);
    console.error(`請求失敗 - 狀態碼: ${res.status}, 錯誤: ${res.error}`);
  }

  // 隨機等待時間，模擬真實用戶行為
  sleep(Math.random() * 3);
}

export function teardown(data) {
  const duration = (Date.now() - data.startTime) / 1000;
  console.log(`🏁 壓力測試完成，總耗時: ${duration.toFixed(2)} 秒`);
}

export function handleSummary(data) {
  let summary = '\n💪 壓力測試結果\n';
  summary += '='.repeat(60) + '\n\n';

  if (data.metrics.http_reqs) {
    summary += `總請求數: ${data.metrics.http_reqs.values.count}\n`;
    summary += `請求速率: ${data.metrics.http_reqs.values.rate.toFixed(2)} req/s\n`;
  }

  if (data.metrics.http_req_failed) {
    const failCount = data.metrics.http_req_failed.values.count || 0;
    const failRate = (data.metrics.http_req_failed.values.rate * 100).toFixed(2);
    summary += `失敗請求數: ${failCount}\n`;
    summary += `請求失敗率: ${failRate}%\n`;
  }

  if (data.metrics.http_req_duration) {
    summary += `\n響應時間統計:\n`;
    summary += `  平均: ${data.metrics.http_req_duration.values.avg.toFixed(2)} ms\n`;
    summary += `  最小: ${data.metrics.http_req_duration.values.min.toFixed(2)} ms\n`;
    summary += `  最大: ${data.metrics.http_req_duration.values.max.toFixed(2)} ms\n`;
    summary += `  P50: ${data.metrics.http_req_duration.values['p(50)'].toFixed(2)} ms\n`;
    summary += `  P95: ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)} ms\n`;
    summary += `  P99: ${data.metrics.http_req_duration.values['p(99)'].toFixed(2)} ms\n`;
  }

  if (data.metrics.errors) {
    summary += `\n總錯誤數: ${data.metrics.errors.values.count}\n`;
  }

  summary += '\n' + '='.repeat(60) + '\n';

  return {
    'stdout': summary,
    'stress-test-results.json': JSON.stringify(data, null, 2),
  };
}
