# Grafana k6 線上課程錄製備課全指南與進度記憶存檔

> **存檔時間**：2026-09-19  
> **專案路徑**：`/home/nathan/Project/o11y_lab_for_dummies/k6/slides`  
> **原始投影片備份**：`/home/nathan/Project/o11y_lab_for_dummies/k6/slides_backup`  

---

## 📌 今日工作成果總覽 (Executive Status)

我們已完成全系列 6 大章節（共 59 頁投影片，每章精準結構平衡）的逐頁視覺、架構與技術深度審查。

### 核心調整目標
1. **Chapter 1: Modern Performance Testing with k6 (10 頁齊全)**：
   - 擁抱 Test as Code、Goroutine 極致並發、全平台安裝、4 階段生命週期、group()、check()、http.url 防護與 10 行關鍵程式碼實戰。
2. **Chapter 6 獨立全新篇章：k6 x agent ── AI 驅動的效能測試新紀元 (7 頁完整體系)**：
   - **Slide 1: 封面與全景導覽**（從 Test as Code 躍升至 AI Agent 自主工程，4 大支柱總覽）。
   - **Slide 2: 自動化雙引擎解密**（技能包注入與原生 MCP 註冊，零外部依賴打通 AI 與本地 k6）。
   - **Slide 3: 安全防護與冪等性機制**（擁有者標籤 Owner Tag、--dry-run 預檢與自訂代碼防護守門員）。
   - **Slide 4: 常用 CLI 指令速查與 6 大編輯器環境適配**（init, --all, status, skills list 與 Cursor/Claude Code/Copilot 適配矩陣）。
   - **Slide 5: 內建 5 大 AI 技能深度剖析**（Planner, Load, Smoke, Browser, Playwright 轉譯專家級壓測工作流）。
   - **Slide 6: 企業導入實作 Checklist**（配置治理、AI 閉環自癒工程、記憶體防護與官方生態資源）。
   - **Slide 7: 隨堂實作練習指引**（初始化、QuickPizza 冒煙閉環自癒、Playwright 轉譯三大任務路線圖）。
   - **Ch3**：原 Slide 2（Lab Guide 實作指引）調整至全章最後一頁（Slide 10）。
   - **Ch4**：原 Slide 2（Flight Pre-check 起飛前清單）調整至 Slide 9（實作前檢核）。
   - **Ch5**：原 Slide 2（企業導入 Checklist Takeaway）調整至 Slide 9（實作前總結）。
3. **圖片像素級技術勘誤 (Patching)**：
   - **Ch4 Slide 8**：修正 `options: { options: { browser: { type: 'chromium' } } }` 為標準 `browser: { type: 'chromium' }`。
   - **Ch5 Slide 10**：修正 Task 3 Docker 編譯指令中的 `-v $(pwd):/build` 為 `-v $(pwd):/xk6`。
   - **Ch2 Slide 1**：修正 `esport` 為 `export`，以及相關標記。
4. **課程錄影核心演示規劃 (Live Demo Script)**：
   - 各章關鍵實機演示點均已規劃完畢（如 Exit Code 99 驗證、Grafana CPU CFS Throttling 雙時間軸對齊等）。

---

## 📚 各章節詳細檢驗、順序調整與講稿避坑備忘

### Chapter 1: Modern Performance Testing with k6 (10 頁)
* **建議時長**：18 ~ 20 分鐘
* **學習動線**：
  1. Slide 1: 擁抱 Test as Code ── 從 JMeter 邁向 Grafana k6 的效能測試新範式
  2. Slide 2: 極致資源利用率：為什麼 k6 單機就能榨出數萬併發？ (Goroutine vs OS Thread)
  3. **Slide 3: 工欲善其事：k6 全平台快速安裝指南 (Linux, macOS, Windows, Docker)**
  4. **Slide 4: 壓測進入 AI 時代：k6 CLI x AI 現代化工作流 (k6 MCP Server & Agent Bootstrapping)**
  5. Slide 5: 掌握執行順序：k6 腳本的 4 階段生命週期 (Lifecycle)
  6. Slide 6: 讓測試結果一目瞭然：使用 group() 進行業務分組
  7. Slide 7: 效能測試中的軟性斷言：check() 非中斷機制
  8. Slide 8: 防範記憶體炸彈：使用 http.url 處理動態 URL
  9. Slide 9: 將觀念融會貫通：10 行關鍵程式碼實戰
  10. Slide 10: Module 1 核心重點複習 & 準備起飛
* **講師避坑點**：
  - **全平台安裝 (Slide 3)**：強調 k6 為 Go 編譯之單一二進位檔（免 Node.js/Go 依賴）；Windows 用戶推薦搭配 WSL2 Ubuntu；CI/CD Runner 推薦官方 Docker 映像檔。
  - **AI 現代化工作流 (Slide 4)**：重點解說 `k6 x mcp`（新版 k6 內建子命令，無須 npx）與核心工具（`validate_script`、`run_script`、`get_documentation`），強調 Agent 能讀取 OpenAPI/HAR 逆向生成測試情境，並以 1 VU 冒煙閉環自癒，將傳統數天手寫流程壓縮至秒級交付！
  - **check() 軟斷言 (Slide 7)**：口播預告「如果需要讓 CI/CD 失敗中斷，我們會在 Chapter 3 介紹 Thresholds」。
  - **http.url 記憶體防護 (Slide 8)**：務必加重語氣警示新手常犯的動態 ID 字串拼接，會導致 Prometheus 高基數維度爆炸 (OOM)。
  - **Live Demo (Slide 9)**：執行 `k6 run k6/demos/ch1_lifecycle_and_checks.js`，引導學員觀察 Init $\rightarrow$ Setup $\rightarrow$ VU 1&2 $\rightarrow$ Teardown 印出順序。

---

### Chapter 2: Scientific k6 Traffic Modeling (10 頁)
* **建議時長**：18 ~ 22 分鐘
* **學習動線**：5 大流量型態 $\rightarrow$ stages 寫法 $\rightarrow$ 協調性漏測 (Coordinated Omission) 盲點 $\rightarrow$ ramping-arrival-rate 開放模型 $\rightarrow$ Little's Law 精算 (preAllocatedVUs vs maxVUs) $\rightarrow$ SharedArray 記憶體拯救 $\rightarrow$ Thresholds & Exit Code 99。
* **順序說明**：Slide 2 晶片總覽在口播中定義為「今日學習地圖」。
* **講師避坑點**：
  - Slide 1 封面代碼：`export default function ()`（已修正）。
  - Slide 9 `SharedArray`：口播提醒模組引入 `import { SharedArray } from 'k6/data'`。
  - **Live Demo 推薦**：以 FastAPI 延遲 API 演示閉環（RPS被拖垮）與開放模型（自動加 VU 維持 RPS）的差異。

---

### Chapter 3: k6 Quality Gates (10 頁)
* **建議時長**：18 ~ 20 分鐘
* **學習動線**：
  * **調整後新順序**：
    1. Slide 1: 封面與核心架構
    2. 原 Slide 3: 一眼看穿系統健康度 (RED Method)
    3. 原 Slide 4: 尾端延遲深度解析 (Tail Latency p95/p99)
    4. 原 Slide 5: k6 內建核心指標全覽
    5. 原 Slide 6: 4 大自訂指標型態 (Counter/Gauge/Rate/Trend)
    6. 原 Slide 7: 斷言三部曲完整對照 (check vs thresholds vs expect)
    7. 原 Slide 8: 精準控制 API SLO (Thresholds 與 Tags 過濾)
    8. 原 Slide 9: CI/CD 自動卡關實務 (Exit Code 99 傳遞鏈)
    9. 原 Slide 10: 模組綜合實戰 (架構化 SLO 代碼)
    10. **原 Slide 2: 隨堂實作練習指引 (Lab Guide) -> 移至最後一頁自然過渡上機**
* **講師避坑點**：
  - **必備補充 `abortOnFail`**：口播提醒緊急熔斷機制，避免壓測一開始就報錯卻空跑 1 小時浪費 CI 資源。
  - **Live Demo 推薦**：在終端機故意讓門檻破功，輸入 `echo $?` 印出大大的 `99`。

---

### Chapter 4: Precision k6 Hybrid Testing (11 頁)
* **建議時長**：20 ~ 23 分鐘
* **學習動線**：
  * **最新順序**：
    1. Slide 1: 封面與全鏈路觀測 (SPA 前端盲區)
    2. Slide 2: HAR 轉換工作流 (瀏覽器活動快照)
    3. Slide 3: Chrome DevTools 網路操作錄製 (Incognito, Preserve log, Clear, Export HAR)
    4. Slide 4: CLI 轉譯與 401 死資料陷阱 (過期 Token 危機)
    5. Slide 5: 腳本清理 3 大黃金法則 (去靜態、動態 Token 關聯、結構化模組)
    6. Slide 6: Protocol-Level vs Browser-Level 世紀決戰
    7. Slide 7: k6/browser 核心語法與 finally page.close() 軍規安全防護
    8. Slide 8: 全鏈路混合壓測與 99:1 黃金配比架構設計
    9. **Slide 9: 實戰成果：QuickPizza 99:1 全鏈路混合壓測現場 (Live Verification & Web Vitals 雙向會師)**
    10. Slide 10: 壓測上線前防呆 Checklist (Flight Pre-check 實作前逐項確認)
    11. Slide 11: 隨堂練習指引 (QuickPizza 實戰任務四步路線圖)
* **技術勘誤與實作落實**：
  - Slide 8：已修正 `browser: { type: 'chromium' }` 頂層語法。
  - **Slide 9 現場實戰數據**：
    - 後端協定層：280 次 API 請求 (27.3/s)，平均延遲 98.25ms，P95 193.65ms，錯誤率 0.00%，140/140 Checks 成功。
    - 前端瀏覽器層：真實無頭 Chromium 採樣，LCP 2.1s (門檻 <3.5s ✓)，FCP 2.1s，INP 24ms (極速響應)，TTFB 587.9ms，CLS 0.00。
* **講師避坑點**：
  - **三大清理法則實作**：以 `k6/demos/recording_cleaned.js` 展示在 `setup()` 動態向 `/api/users/token/login` 取 Token，解決 401 陷阱；移除 `google-analytics.com` 貫徹「Don't load test Google!」。
  - **finally close 記憶體警示**：務必強調遺漏 `await page.close()` 會產生殭屍 Chromium 行程耗盡伺服器。
  - **Live Demo 指引**：一鍵執行 `k6 run k6/demos/ch4_hybrid_99_to_1.js`，向學員證明普通筆電即可同時驗證後端高壓與前端流暢度，省下 90% 機器開銷。

---

### Chapter 5: k6 Observability and Modular Architecture (10 頁)
* **建議時長**：15 ~ 20 分鐘
* **學習動線**：
  * **調整後新順序**：
    1. Slide 1: 封面與全景預覽
    2. 原 Slide 3: 原生 Web Dashboard 即時監控 (Port=-1 退場技巧)
    3. 原 Slide 4: 匯出靜態 HTML 測試報告
    4. 原 Slide 5: xk6 擴充機制解剖 (Go-to-JS Bridge)
    5. 原 Slide 6: 擴充套件雙引擎 (JS Extensions vs Output Extensions)
    6. 原 Slide 7: xk6 build 與 Docker CI 確定性編譯
    7. 原 Slide 8: Prometheus Remote Write 與 Commit Tag 綁定
    8. 原 Slide 9: Grafana 全視角對齊 (CPU CFS Throttling 破除孤島)
    9. **原 Slide 2: 企業導入實作 Checklist (Takeaway) -> 全章總結回顧**
    10. 原 Slide 10: 隨堂練習指引 (Hands-on Practice)
* **技術勘誤修復**：
  - Slide 10 任務三：已修正 Docker 掛載路徑為 `-v $(pwd):/xk6`。
* **講師避坑點**：
  - Slide 8 需口播提醒 Prometheus 需開啟 `--web.enable-remote-write-receiver`，並設定 `K6_PROMETHEUS_RW_SERVER_URL`。
  - 口頭補充 `handleSummary(data)` 自訂報表 Hook 與 OpenTelemetry 分散式追蹤觀念。
  - **Live Demo 推薦**：展示 Grafana 雙十字準星，貫穿 API Latency 尖峰與 K8s Pod CPU 限流線。

---

### Chapter 6: k6 x agent ── AI 驅動的效能測試新紀元 (7 頁)
* **建議時長**：18 ~ 22 分鐘
* **學習動線**：
  1. Slide 1: 封面與全景導覽 ── 從 Test as Code 躍升至 AI Agent 自主工程 (4 大支柱總覽)
  2. Slide 2: 自動化雙引擎解密 ── Bundled Skills 技能包注入 + k6 x mcp 原生註冊
  3. Slide 3: 安全防護與冪等性 ── 擁有者標籤 (Owner Tag) 與 --dry-run 企業級守門員
  4. Slide 4: 常用 CLI 指令速查與 6 大編輯器環境適配 ── init, --all, status, skills list 與 Cursor/Claude Code/Copilot
  5. Slide 5: 內建 5 大 AI 技能深度剖析 ── Planner, Load, Smoke, Browser, Playwright 轉譯專家級壓測工作流
  6. Slide 6: 企業導入實作 Checklist ── AI 壓測工程化最佳實踐、高基數防護與官方生態資源
  7. Slide 7: 隨堂實作練習指引 ── 循序完成三大任務：初始化、QuickPizza 冒煙閉環自癒、Playwright 轉譯
* **講師避坑點**：
  - **雙引擎架構 (Slide 2)**：務必向學員強調「完全零外部依賴」，底層由 Go 原生驅動，不需要安裝 Node.js、npm 或 Python 環境即可享受 AI 壓測。
  - **安全冪等性 (Slide 3)**：重點展示 `<!-- generated by k6 x agent -->` 標籤，解答學員對於「AI 會不會把我們團隊寫好的自訂規則給蓋掉？」的疑慮。
  - **環境適配 (Slide 4)**：推薦跨職能團隊使用 `k6 x agent init --all`，並展示 `status` 檢查指令。
  - **高基數記憶體防護 (Slide 6)**：強調 AI 技能包中內建的語法規則，強制將動態 ID 端點以 `http.url` 標籤包覆，防止 Prometheus 記憶體爆炸 (OOM)。
  - **Live Demo 推薦**：在 Cursor 或 Claude Code 中輸入自然語言提示詞，展示 AI 呼叫 `validate_script` 預檢與 `run_script` 跑 1 VU 冒煙閉環自癒。

---

## 🎯 接續工作清單已全數達成 (Action Plan Status: Completed ✅)

所有昨日規劃的四項核心工作已全數完成並通過自動化實機檢驗：

1. [x] **檢視已更新順序與修正後的 PPTX 效果**：
   - 全 6 份 PPTX 均已採用標準 16:9 寬螢幕解析度（17.78 x 10.00 inches）。
   - 簡報邏輯順序（Ch3、Ch4、Ch5 調整防劇透結構；Ch6 為完整 7 頁獨立 AI 篇章）已完美落實。
2. [x] **針對 Ch2 Slide 1 的細微排版微調**：
   - 已修正 `export default function () {`，修復 `esport` 拼寫錯誤。
3. [x] **準備各章配套的 Live Demo 程式碼腳本**：
   - 已在目錄 [`k6/demos/`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos) 建置完成全系列專屬演示腳本，均已通過本地執行驗證（包含 `k6/browser` 驅動 Chromium 實測、99:1 混合壓測、Prometheus Remote Write 與 Exit Code 99 驗證）。
   - 配套完整說明文件：[`k6/demos/README.md`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/README.md)。
4. [x] **產出全章節完整錄課逐字稿與講者提詞卡**：
   - **專屬廣播級逐字稿全集目錄**：[`k6/slides/transcripts/`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/slides/transcripts)
     - [Ch1 逐字稿 (10 頁, ~20 mins)](file:///home/nathan/Project/o11y_lab_for_dummies/k6/slides/transcripts/Ch1_逐字稿_Modern_Performance_Testing_with_k6.md)
     - [Ch2 逐字稿 (10 頁, ~20 mins)](file:///home/nathan/Project/o11y_lab_for_dummies/k6/slides/transcripts/Ch2_逐字稿_Scientific_k6_Traffic_Modeling.md)
     - [Ch3 逐字稿 (10 頁, ~20 mins)](file:///home/nathan/Project/o11y_lab_for_dummies/k6/slides/transcripts/Ch3_逐字稿_k6_Quality_Gates.md)
     - [Ch4 逐字稿 (11 頁, ~22 mins)](file:///home/nathan/Project/o11y_lab_for_dummies/k6/slides/transcripts/Ch4_逐字稿_Precision_k6_Hybrid_Testing.md)
     - [Ch5 逐字稿 (11 頁, ~20 mins)](file:///home/nathan/Project/o11y_lab_for_dummies/k6/slides/transcripts/Ch5_逐字稿_k6_Observability_and_Modular_Architecture.md)
     - [Ch6 逐字稿 (7 頁, ~18 mins)](file:///home/nathan/Project/o11y_lab_for_dummies/k6/slides/transcripts/Ch6_逐字稿_k6_AI_Agent_Engineering.md)
   - **精簡版提詞手冊**：[`k6/slides/LECTURE_SCRIPTS.md`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/slides/LECTURE_SCRIPTS.md)

---

## 🎬 錄課即時作業指引 (Recording Quickstart)
* **副螢幕（逐字稿提詞）**：開啟對應章節的 [`k6/slides/transcripts/`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/slides/transcripts) 逐字稿檔案。
* **主螢幕（簡報播放）**：使用 [`k6/slides/`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/slides) 目錄下的 5 份最新 `.pptx`。
* **終端機演示位置**：在專案根目錄執行 `k6 run k6/demos/<腳本名稱>.js`。

---

## 🌐 線上 Codelabs 教學專欄已建立 (Online Interactive Codelabs)
* **首頁網址**：`https://tedmax100.github.io/o11y_lab_for_dummies/` (已加入專屬橘色 k6 課程卡片)
* **k6 專欄教學入口**：[`k6-performance-testing/index.html`](file:///home/nathan/Project/o11y_lab_for_dummies/codelabs/generated/k6-performance-testing/index.html)
* **教學原始 Markdown**：[`codelabs/tutorials/k6-performance-testing.md`](file:///home/nathan/Project/o11y_lab_for_dummies/codelabs/tutorials/k6-performance-testing.md)
* **包含章節步驟**：
  1. 課程簡介與導讀 (3 min)
  2. Chapter 1: k6 核心哲學與腳本基礎手把手 (15 min)
  3. Chapter 2: 科學化流量建模與協調性漏測破解 (20 min)
  4. Chapter 3: 效能指標解讀與 SLO 門檻自動化 (Quality Gates) (20 min)
  5. Chapter 4: 邁向真實用戶體驗：流量錄製與 k6 Browser 混合壓測 (20 min)
  6. Chapter 5: 生態系擴充與全視角可觀測性整合 (20 min)
  7. 總結與企業導入實作指南 (5 min)


