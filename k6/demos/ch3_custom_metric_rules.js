/**
 * Chapter 3 Demo：自訂指標的 5 個規則（不需連線任何服務，可直接執行）
 *
 *   k6 run k6/demos/ch3_custom_metric_rules.js
 */
import { sleep } from 'k6';
import { Counter, Gauge, Rate, Trend } from 'k6/metrics';

// 規則 1：一律在檔案最上層（init 區塊）宣告
// 規則 3：名稱只用英文字母、數字、底線
const ordersCompleted = new Counter('orders_completed');
const queueDepth      = new Gauge('queue_depth');
const checkoutSuccess = new Rate('checkout_success');
const dbQueryTime     = new Trend('db_query_time', true);   // 規則 2：時間型 Trend 加 true

export const options = {
  iterations: 5,
  thresholds: {
    'checkout_success': ['rate>0.9'],
    'db_query_time{endpoint:checkout}': ['p(95)<200'],     // 規則 4：用 tags 設門檻
  },
};

export default function () {
  const elapsedMs = 100 + __ITER * 10;                       // 模擬一次 DB 查詢耗時
  ordersCompleted.add(1);
  queueDepth.add(__ITER);
  checkoutSuccess.add(true);
  dbQueryTime.add(elapsedMs, { endpoint: 'checkout' });    // 規則 4：記錄時帶 tags
  sleep(1);
}
