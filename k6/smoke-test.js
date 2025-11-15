/**
 * 煙霧測試 (Smoke Test)
 * 用於驗證系統基本功能是否正常
 * 使用少量虛擬用戶進行短時間測試
 */

import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  // 單一虛擬用戶運行 1 分鐘
  vus: 1,
  duration: '1m',

  thresholds: {
    // 煙霧測試的嚴格要求
    http_req_failed: ['rate<0.01'], // 失敗率 < 1%
    http_req_duration: ['p(95)<1000'], // 95% 請求 < 1秒
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';

export default function() {
  // 測試主要流程
  const processRes = http.get(`${BASE_URL}/api/process`);

  check(processRes, {
    '主流程狀態碼是 200': (r) => r.status === 200,
    '主流程回應正確': (r) => {
      try {
        const json = r.json();
        return json.status === 'success' && json.data !== undefined;
      } catch (e) {
        return false;
      }
    },
  });

  sleep(1);

  // 測試服務資訊
  const infoRes = http.get(`${BASE_URL}/api/info`);

  check(infoRes, {
    'Info 狀態碼是 200': (r) => r.status === 200,
    'Info 回應正確': (r) => {
      try {
        return r.json().service === 'api-gateway';
      } catch (e) {
        return false;
      }
    },
  });

  sleep(1);
}

export function handleSummary(data) {
  console.log('🔍 煙霧測試完成');
  return {
    'stdout': generateSummary(data),
  };
}

function generateSummary(data) {
  let summary = '\n📊 煙霧測試結果\n';
  summary += '='.repeat(50) + '\n\n';

  if (data.metrics.http_reqs) {
    summary += `總請求數: ${data.metrics.http_reqs.values.count}\n`;
  }

  if (data.metrics.http_req_failed) {
    const failRate = (data.metrics.http_req_failed.values.rate * 100).toFixed(2);
    const passed = data.metrics.http_req_failed.values.rate < 0.01;
    summary += `請求失敗率: ${failRate}% ${passed ? '✅' : '❌'}\n`;
  }

  if (data.metrics.http_req_duration) {
    const p95 = data.metrics.http_req_duration.values['p(95)'];
    const passed = p95 < 1000;
    summary += `P95 響應時間: ${p95.toFixed(2)} ms ${passed ? '✅' : '❌'}\n`;
  }

  summary += '\n' + '='.repeat(50) + '\n';

  return summary;
}
