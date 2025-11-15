/**
 * 尖峰測試 (Spike Test)
 * 測試系統應對突然流量激增的能力
 * 模擬短時間內流量暴增的情況
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const successRate = new Rate('success_rate');
const responseTime = new Trend('response_time');

export const options = {
  stages: [
    // 1. 正常負載：10個用戶
    { duration: '30s', target: 10 },
    // 2. 突然尖峰：10秒內升到100個用戶
    { duration: '10s', target: 100 },
    // 3. 維持尖峰：30秒
    { duration: '30s', target: 100 },
    // 4. 快速降載：10秒內降回10個用戶
    { duration: '10s', target: 10 },
    // 5. 恢復階段：維持10個用戶觀察系統恢復
    { duration: '1m', target: 10 },
    // 6. 第二次尖峰：10秒內升到150個用戶
    { duration: '10s', target: 150 },
    // 7. 維持第二次尖峰：30秒
    { duration: '30s', target: 150 },
    // 8. 降載：20秒內降到0
    { duration: '20s', target: 0 },
  ],

  thresholds: {
    http_req_failed: ['rate<0.10'], // 允許10%的失敗率
    http_req_duration: ['p(90)<3000'], // 90% 請求 < 3秒
    success_rate: ['rate>0.85'], // 成功率 > 85%
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const SERVICE_A_URL = __ENV.SERVICE_A_URL || 'http://localhost:8001';

export function setup() {
  console.log('⚡ 開始尖峰測試 - 模擬流量突然激增');

  // 確認服務可用
  const health = http.get(`${BASE_URL}/health`);
  if (health.status !== 200) {
    throw new Error('服務健康檢查失敗，無法進行測試');
  }

  return {
    startTime: Date.now(),
    testId: Math.random().toString(36).substring(7),
  };
}

export default function(data) {
  const startTime = Date.now();

  // 主要流程測試
  const res = http.get(`${BASE_URL}/api/process`, {
    tags: { test_id: data.testId, endpoint: 'process' },
    timeout: '30s',
  });

  const duration = Date.now() - startTime;
  responseTime.add(duration);

  const success = check(res, {
    '狀態正常': (r) => r.status === 200 || r.status === 503, // 尖峰時允許503
    '回應有效或超時': (r) => {
      if (r.status === 200) {
        try {
          return r.json('status') !== undefined;
        } catch (e) {
          return false;
        }
      }
      return r.status === 503; // 503 也算預期內的回應
    },
    '響應時間可接受': (r) => r.timings.duration < 10000, // 10秒內
  });

  successRate.add(success && res.status === 200);

  // 記錄異常狀況
  if (res.status === 503) {
    console.warn(`⚠️  服務暫時不可用 (503) - 這在尖峰測試中是預期的`);
  } else if (res.status !== 200) {
    console.error(`❌ 非預期的狀態碼: ${res.status}`);
  }

  // 30% 的請求會同時查詢統計
  if (Math.random() < 0.3) {
    const statsRes = http.get(`${SERVICE_A_URL}/stats`, {
      tags: { test_id: data.testId, endpoint: 'stats' },
      timeout: '10s',
    });

    check(statsRes, {
      'Stats 可用或忙碌': (r) => r.status === 200 || r.status === 503,
    });
  }

  // 短暫等待，但在尖峰期間等待時間更短
  sleep(Math.random() * 0.5);
}

export function teardown(data) {
  const totalDuration = (Date.now() - data.startTime) / 1000;
  console.log(`🏁 尖峰測試完成`);
  console.log(`   測試ID: ${data.testId}`);
  console.log(`   總耗時: ${totalDuration.toFixed(2)} 秒`);
}

export function handleSummary(data) {
  let summary = '\n⚡ 尖峰測試結果\n';
  summary += '='.repeat(60) + '\n\n';

  summary += '📈 測試目標:\n';
  summary += '  測試系統應對突然流量激增的能力\n';
  summary += '  觀察系統在尖峰期間和恢復期間的表現\n\n';

  if (data.metrics.http_reqs) {
    summary += `總請求數: ${data.metrics.http_reqs.values.count}\n`;
    summary += `平均請求速率: ${data.metrics.http_reqs.values.rate.toFixed(2)} req/s\n\n`;
  }

  if (data.metrics.http_req_failed) {
    const failRate = (data.metrics.http_req_failed.values.rate * 100).toFixed(2);
    const failCount = data.metrics.http_req_failed.values.count || 0;
    summary += `失敗統計:\n`;
    summary += `  失敗數量: ${failCount}\n`;
    summary += `  失敗率: ${failRate}%\n\n`;
  }

  if (data.metrics.http_req_duration) {
    summary += `響應時間分析:\n`;
    summary += `  平均值: ${data.metrics.http_req_duration.values.avg.toFixed(2)} ms\n`;
    summary += `  中位數 (P50): ${data.metrics.http_req_duration.values['p(50)'].toFixed(2)} ms\n`;
    summary += `  P90: ${data.metrics.http_req_duration.values['p(90)'].toFixed(2)} ms\n`;
    summary += `  P95: ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)} ms\n`;
    summary += `  P99: ${data.metrics.http_req_duration.values['p(99)'].toFixed(2)} ms\n`;
    summary += `  最大值: ${data.metrics.http_req_duration.values.max.toFixed(2)} ms\n\n`;
  }

  if (data.metrics.success_rate) {
    const successRate = (data.metrics.success_rate.values.rate * 100).toFixed(2);
    summary += `成功率: ${successRate}%\n\n`;
  }

  summary += '💡 分析建議:\n';
  summary += '  1. 檢查尖峰期間的錯誤率和響應時間\n';
  summary += '  2. 觀察系統在恢復期間是否能快速恢復正常\n';
  summary += '  3. 在 Grafana 中查看對應時間段的 metrics 和 traces\n';
  summary += '  4. 檢查是否有資源瓶頸（CPU、記憶體、資料庫連接等）\n\n';

  summary += '='.repeat(60) + '\n';

  return {
    'stdout': summary,
    'spike-test-results.json': JSON.stringify(data, null, 2),
  };
}
