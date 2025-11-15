/**
 * OpenTelemetry 可觀測性實驗室 - K6 負載測試腳本
 *
 * 此腳本測試以下端點：
 * - API Gateway: /api/process (主要流程)
 * - API Gateway: /api/info (服務資訊)
 * - Service A: /health (健康檢查)
 * - Service A: /stats (統計資訊)
 *
 * 測試場景包括：
 * 1. 漸增負載測試 (Ramp-up)
 * 2. 穩定負載測試 (Steady state)
 * 3. 壓力測試 (Stress test)
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';

// 自定義指標
const processErrors = new Counter('process_errors');
const processSuccessRate = new Rate('process_success_rate');
const processDuration = new Trend('process_duration');

// 配置選項
export const options = {
  // 定義多個測試階段
  stages: [
    // 1. 預熱階段：5 秒內從 0 到 5 個虛擬用戶
    { duration: '10s', target: 5 },
    // 2. 穩定負載：維持 5 個虛擬用戶運行 30 秒
    { duration: '30s', target: 5 },
    // 3. 增加負載：20 秒內增加到 20 個虛擬用戶
    { duration: '20s', target: 20 },
    // 4. 高負載維持：維持 20 個虛擬用戶運行 1 分鐘
    { duration: '1m', target: 20 },
    // 5. 峰值測試：10 秒內增加到 50 個虛擬用戶
    { duration: '10s', target: 50 },
    // 6. 峰值維持：維持 50 個虛擬用戶運行 30 秒
    { duration: '30s', target: 50 },
    // 7. 降載：20 秒內降回到 5 個虛擬用戶
    { duration: '20s', target: 5 },
    // 8. 冷卻：5 秒內降到 0
    { duration: '10s', target: 0 },
  ],

  // 性能閾值 (thresholds)
  thresholds: {
    // HTTP 請求失敗率應小於 1%
    http_req_failed: ['rate<0.01'],
    // 95% 的請求應在 2 秒內完成
    http_req_duration: ['p(95)<2000'],
    // 99% 的請求應在 5 秒內完成
    'http_req_duration{name:process}': ['p(99)<5000'],
    // process 端點成功率應大於 99%
    process_success_rate: ['rate>0.99'],
  },
};

// 基礎 URL
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const SERVICE_A_URL = __ENV.SERVICE_A_URL || 'http://localhost:8001';

/**
 * 設置函數 - 在測試開始前執行一次
 */
export function setup() {
  console.log('🚀 開始負載測試...');
  console.log(`API Gateway: ${BASE_URL}`);
  console.log(`Service A: ${SERVICE_A_URL}`);

  // 檢查服務是否可用
  const healthCheck = http.get(`${BASE_URL}/health`);
  if (healthCheck.status !== 200) {
    throw new Error('API Gateway 健康檢查失敗');
  }

  console.log('✅ 服務健康檢查通過');
  return { startTime: new Date().toISOString() };
}

/**
 * 主要測試函數 - 每個虛擬用戶重複執行
 */
export default function(data) {
  // 測試場景 1: API Gateway 主要處理流程
  testProcessEndpoint();

  // 隨機等待 1-3 秒
  sleep(Math.random() * 2 + 1);

  // 測試場景 2: 獲取服務資訊
  if (Math.random() < 0.3) { // 30% 的請求會調用 info
    testInfoEndpoint();
  }

  // 測試場景 3: Service A 統計資訊
  if (Math.random() < 0.2) { // 20% 的請求會調用 stats
    testStatsEndpoint();
  }

  // 測試場景 4: 健康檢查
  if (Math.random() < 0.1) { // 10% 的請求會進行健康檢查
    testHealthCheck();
  }
}

/**
 * 測試主要處理端點
 */
function testProcessEndpoint() {
  const startTime = new Date();

  const res = http.get(`${BASE_URL}/api/process`, {
    tags: { name: 'process' },
    timeout: '30s',
  });

  const duration = new Date() - startTime;
  processDuration.add(duration);

  const success = check(res, {
    '狀態碼是 200': (r) => r.status === 200,
    '回應包含 status': (r) => r.json('status') !== undefined,
    '回應包含 data': (r) => r.json('data') !== undefined,
    '回應時間 < 5秒': (r) => r.timings.duration < 5000,
  });

  processSuccessRate.add(success);

  if (!success) {
    processErrors.add(1);
    console.error(`❌ Process 請求失敗: 狀態碼 ${res.status}`);
  }

  // 記錄 trace_id 以便後續分析
  if (res.status === 200 && res.json('data.trace_id')) {
    console.log(`✅ Trace ID: ${res.json('data.trace_id')}`);
  }
}

/**
 * 測試服務資訊端點
 */
function testInfoEndpoint() {
  const res = http.get(`${BASE_URL}/api/info`, {
    tags: { name: 'info' },
  });

  check(res, {
    'Info 狀態碼是 200': (r) => r.status === 200,
    'Info 回應包含 service': (r) => r.json('service') === 'api-gateway',
  });
}

/**
 * 測試統計端點
 */
function testStatsEndpoint() {
  const res = http.get(`${SERVICE_A_URL}/stats`, {
    tags: { name: 'stats' },
  });

  check(res, {
    'Stats 狀態碼是 200': (r) => r.status === 200,
    'Stats 回應包含 service': (r) => r.json('service') === 'service-a',
    'Stats 回應包含統計數據': (r) => r.json('stats') !== undefined,
  });
}

/**
 * 測試健康檢查端點
 */
function testHealthCheck() {
  const endpoints = [
    { url: `${BASE_URL}/health`, name: 'API Gateway' },
    { url: `${SERVICE_A_URL}/health`, name: 'Service A' },
  ];

  endpoints.forEach(endpoint => {
    const res = http.get(endpoint.url, {
      tags: { name: 'health' },
    });

    check(res, {
      [`${endpoint.name} 健康檢查通過`]: (r) => r.status === 200 && r.json('status') === 'healthy',
    });
  });
}

/**
 * 拆解函數 - 測試結束後執行一次
 */
export function teardown(data) {
  console.log('🏁 負載測試完成');
  console.log(`測試開始時間: ${data.startTime}`);
  console.log(`測試結束時間: ${new Date().toISOString()}`);
}

/**
 * 處理摘要報告
 */
export function handleSummary(data) {
  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    'summary.json': JSON.stringify(data),
  };
}

// 生成文字摘要
function textSummary(data, options) {
  const indent = options.indent || '';
  const enableColors = options.enableColors || false;

  let summary = '\n';
  summary += `${indent}📊 測試結果摘要\n`;
  summary += `${indent}${'='.repeat(50)}\n\n`;

  // 基本指標
  if (data.metrics.http_reqs) {
    summary += `${indent}總請求數: ${data.metrics.http_reqs.values.count}\n`;
  }

  if (data.metrics.http_req_duration) {
    summary += `${indent}平均響應時間: ${data.metrics.http_req_duration.values.avg.toFixed(2)} ms\n`;
    summary += `${indent}P95 響應時間: ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)} ms\n`;
    summary += `${indent}P99 響應時間: ${data.metrics.http_req_duration.values['p(99)'].toFixed(2)} ms\n`;
  }

  if (data.metrics.http_req_failed) {
    const failRate = (data.metrics.http_req_failed.values.rate * 100).toFixed(2);
    summary += `${indent}請求失敗率: ${failRate}%\n`;
  }

  summary += `\n${indent}${'='.repeat(50)}\n`;

  return summary;
}
