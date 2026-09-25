# Grafana k6 線上課程配套實機演示腳本全集 (Course Live Demo Suite)

本目錄包含 6 大章節錄課時專屬的**實機 Live Demo 腳本與驗證工具**。每個腳本均對應簡報中的核心心智模型與避坑警示，可直接在終端機執行展示。

---

## ✅ 開錄前預檢：`preflight.sh`

```bash
./k6/demos/preflight.sh                 # 全部章節：檢查相依服務 + 實際跑一次每支 demo，比對 exit code
./k6/demos/preflight.sh ch2 ch3         # 只檢查指定章節
./k6/demos/preflight.sh --check-only    # 只檢查環境，不跑 k6
```

會檢查 k6 版本、QuickPizza / Astronomy Shop 連線、`localhost:8080` API Gateway、Prometheus Remote Write receiver、Grafana、Chromium、`grafana/xk6` 映像檔快取、`k6 x agent` / `k6 x mcp`，並確認 Ch2 `delay/3`、Ch3 `FAIL_SLO` / `ABORT_TEST` 真的回傳 **Exit 99**。demo 產出的報表寫到暫存目錄，不會弄髒專案。

---

## 📂 章節腳本與演示對照表

| 章節 | 腳本檔案 | 核心演示亮點與概念 | 終端機執行指令 |
| :--- | :--- | :--- | :--- |
| **Ch1** | [`ch1_lifecycle_and_checks.js`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/ch1_lifecycle_and_checks.js) | 四階段生命週期 (Init/Setup/VU/Teardown)、`check()` 軟斷言、`group()` 分組、避免高基數 URL 標籤化 | `k6 run k6/demos/ch1_lifecycle_and_checks.js` |
| **Ch1** | [`ch1_group_journey.js`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/ch1_group_journey.js) | 用 `group()` 把 QuickPizza 使用者旅程（瀏覽首頁 → 取得推薦 → 送出評分）分段統計，各段 think time 不同 | `k6 run --summary-mode=full k6/demos/ch1_group_journey.js` |
| **Ch2** | [`ch2_closed_vs_open_model.js`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/ch2_closed_vs_open_model.js) | 協調性漏測 (Coordinated Omission)、閉環模型被拖垮 vs 開放模型 Little's Law 自動調度與 `dropped_iterations` | `k6 run -e MODEL=open k6/demos/ch2_closed_vs_open_model.js` |
| **Ch2** | [`ch2_shared_array.js`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/ch2_shared_array.js) | `SharedArray` 唯讀共享記憶體神技，避免萬人併發時記憶體 OOM 崩潰 | `k6 run k6/demos/ch2_shared_array.js` |
| **Ch3** | [`ch3_quality_gates_exit99.js`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/ch3_quality_gates_exit99.js) | 4 大自訂指標 (Counter/Gauge/Rate/Trend)、精準 Tagged Thresholds、`abortOnFail` 熔斷、Exit Code 99 卡關 | `k6 run -e FAIL_SLO=true k6/demos/ch3_quality_gates_exit99.js ; echo "CI Exit: $?"` |
| **Ch4** | [`ch4_browser_quickpizza.js`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/ch4_browser_quickpizza.js) | `k6/browser` 驅動 Headless Chromium、QuickPizza 點餐互動、採集真實 Core Web Vitals (LCP/INP/CLS) | `k6 run k6/demos/ch4_browser_quickpizza.js` |
| **Ch4** | [`ch4_hybrid_99_to_1.js`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/ch4_hybrid_99_to_1.js) | **99:1 全鏈路混合壓測黃金架構**：99% Protocol 壓測後端 + 1% Browser 探測針測量高負載下的前端劣化 | `k6 run k6/demos/ch4_hybrid_99_to_1.js` |
| **Ch5** | [`ch5_dashboard_and_html_summary.js`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/ch5_dashboard_and_html_summary.js) | 原生 Web Dashboard (`localhost:5665`) 即時監控、`handleSummary(data)` Hook 匯出獨立 HTML 報表與 JSON | `K6_WEB_DASHBOARD=true k6 run k6/demos/ch5_dashboard_and_html_summary.js` |
| **Ch5** | [`ch5_prometheus_remote_write.sh`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/ch5_prometheus_remote_write.sh) | Prometheus Remote Write 時序資料推播、Git Commit ID / Branch 標籤綁定、破除壓測孤島 | `./k6/demos/ch5_prometheus_remote_write.sh` |
| **Ch5** | [`ch5_xk6_docker_build.sh`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/ch5_xk6_docker_build.sh) | Docker 確定性編譯 xk6 擴充套件，掛載 `-v $(pwd):/xk6` 輸出自訂二進位檔 | `./k6/demos/ch5_xk6_docker_build.sh` |
| **Ch6** | [`ch6_quickpizza_smoke_agent.js`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/ch6_quickpizza_smoke_agent.js) | AI 逆向生成之 QuickPizza 極速冒煙測試，遵循 Check 軟斷言與 tags 標籤防高基數最佳實踐 | `k6 run k6/demos/ch6_quickpizza_smoke_agent.js` |
| **Ch6** | [`ch6_otel_astronomy_shop.js`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/ch6_otel_astronomy_shop.js) | **Astronomy Shop (OTel Demo) 旗艦實戰**：SharedArray 跨 VU 共享、階梯負載、全鏈路購物車添加與精確 Tagged Thresholds | `k6 run k6/demos/ch6_otel_astronomy_shop.js` |

---

## 💡 講師錄課實機操作技巧 (Tips for Recording)

1. **終端機雙分割畫面 (Split Terminal)**：
   - 上半部：執行 k6 壓測指令。
   - 下半部：即時觀察日誌、Exit Code (`echo $?`) 或 Grafana / Prometheus 狀態。
2. **避免外網依賴**：
   - 若錄課環境無外網，可啟動專案的 `docker compose up -d`，並將 `TARGET_URL` 指向本機 `http://localhost:8080`。
3. **高潮點展示 (Showstopper Moments)**：
   - **Ch2**：展示開放模型在端點變慢時，依 Little's Law 預配置 40 VUs 守住 20 RPS（`dropped_iterations` = 0）；再把 `TARGET_URL` 改成 `/api/delay/3`，VU 池耗盡、`dropped_iterations` 飆紅並 Exit 99！
   - **Ch3**：故意讓門檻破功，印出醒目的 `Exit Code: 99`，點出 CI/CD pipeline 失敗卡關的原理。
   - **Ch4**：展示終端機中同時印出 HTTP 協定指標與 `browser_web_vital_lcp` 瀏覽器渲染指標。
