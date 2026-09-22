/**
 * ==============================================================================
 * Grafana k6 x agent 實戰演示腳本：Astronomy Shop (OpenTelemetry Demo)
 * ==============================================================================
 * 目標環境：https://appenvdev.field-eng-demo.grafana.net
 * 架構特徵：
 *   1. 具備商品瀏覽 (GET /api/products)、商品規格查詢與購物車操作 (POST /api/cart)
 *   2. 採用 SharedArray 跨 VU 共享熱門商品清單，極致節省記憶體
 *   3. 嚴格落實 tags: { name: '...' } 防範 Prometheus / 時序指標高基數爆炸
 *   4. 內建 100% 檢查率與 P95 < 600ms 嚴格品質門禁 (Quality Gates)
 *
 * 執行指令：
 *   k6 run k6/demos/ch6_otel_astronomy_shop.js
 * ==============================================================================
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';

// 1. 跨 VU 唯讀共享測試商品清單 (SharedArray 最佳實踐)
const TARGET_PRODUCTS = new SharedArray('Astronomy Products', function () {
  return [
    { id: 'OLJCESPC7Z', name: 'National Park Foundation Explorascope' },
    { id: '66VCHSJNUP', name: 'Starsense Explorer Refractor Telescope' },
    { id: '1YMWWN1N4O', name: 'Eclipsmart Travel Refractor Telescope' },
    { id: '2ZYFJ3GM2N', name: 'Roof Binoculars' },
    { id: '0PUK6V6EV0', name: 'Solar System Color Imager' },
  ];
});

// 2. 測試選項與門禁規範
export const options = {
  scenarios: {
    astronomy_shop_flow: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '3s', target: 3 },  // 快速爬坡驗證
        { duration: '5s', target: 3 },  // 穩態負載
        { duration: '2s', target: 0 },  // 降坡冷卻
      ],
      gracefulRampDown: '2s',
    },
  },
  thresholds: {
    // 全域門禁：錯誤率 < 1%，P95 延遲 < 800ms
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<800'],
    checks: ['rate==1.00'],

    // 端點級細緻門禁 (利用 tags 標籤精準過濾)
    'http_req_duration{name:GetProductCatalog}': ['p(95)<500'],
    'http_req_duration{name:GetProductDetail}': ['p(95)<400'],
    'http_req_duration{name:AddToCart}': ['p(95)<600'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://appenvdev.field-eng-demo.grafana.net';

export default function () {
  // 從 SharedArray 隨機選取一件天文商品
  const randomProduct = TARGET_PRODUCTS[Math.floor(Math.random() * TARGET_PRODUCTS.length)];
  const userId = `k6-user-${__VU}`;

  // 步驟 1：瀏覽全館商品目錄 (GET /api/products)
  const catalogRes = http.get(`${BASE_URL}/api/products`, {
    tags: { name: 'GetProductCatalog' },
  });
  check(catalogRes, {
    '商品目錄回應 200 OK': (r) => r.status === 200,
    '商品目錄包含有效商品': (r) => {
      try {
        const data = r.json();
        return Array.isArray(data) && data.length > 0;
      } catch (e) {
        return false;
      }
    },
  });

  // 步驟 2：點選特定望遠鏡商品詳情 (GET /api/products/{id})
  // 注意：以 tags: { name: 'GetProductDetail' } 統一聚合，避免動態 ID 導致 High Cardinality！
  const detailRes = http.get(`${BASE_URL}/api/products/${randomProduct.id}`, {
    tags: { name: 'GetProductDetail' },
  });
  check(detailRes, {
    '商品詳情回應 200 OK': (r) => r.status === 200,
    '回傳正確商品 ID': (r) => {
      try {
        const item = r.json();
        return item && item.id === randomProduct.id;
      } catch (e) {
        return false;
      }
    },
  });

  // 步驟 3：模擬加入購物車 (POST /api/cart)
  const cartPayload = JSON.stringify({
    userId: userId,
    item: {
      productId: randomProduct.id,
      quantity: 1,
    },
  });

  const cartRes = http.post(`${BASE_URL}/api/cart`, cartPayload, {
    headers: { 'Content-Type': 'application/json' },
    tags: { name: 'AddToCart' },
  });
  check(cartRes, {
    '加入購物車回應 200 OK': (r) => r.status === 200,
    '購物車包含目標商品': (r) => {
      try {
        const data = r.json();
        return data.items && data.items.some(i => i.productId === randomProduct.id);
      } catch (e) {
        return false;
      }
    },
  });

  // 模擬真實使用者閱讀與思考時間 (1 ~ 2 秒隨機 Think Time)
  sleep(1 + Math.random() * 1);
}
