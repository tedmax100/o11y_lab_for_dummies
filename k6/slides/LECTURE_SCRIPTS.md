# Grafana k6 線上課程全章節錄課逐字稿與講者提詞卡 (Master Lecture Scripts & Prompter Cards)

> **講師專用手冊**：本檔案專為錄製線上課程設計。您可以將此文件置於副螢幕作為即時提詞小卡 (Teleprompter)，每一頁投影片均包含**核心心智模型**、**口播逐字提詞**、**避坑警示**與**實機演示切換點**。

---

## 📑 快速章節導航
- [Chapter 1: Modern Performance Testing with k6 (18~20 mins)](#chapter-1-modern-performance-testing-with-k6)
- [Chapter 2: Scientific k6 Traffic Modeling (18~22 mins)](#chapter-2-scientific-k6-traffic-modeling)
- [Chapter 3: k6 Quality Gates & SLO Enforcement (18~20 mins)](#chapter-3-k6-quality-gates--slo-enforcement)
- [Chapter 4: Precision k6 Hybrid Testing (18~22 mins)](#chapter-4-precision-k6-hybrid-testing)
- [Chapter 5: k6 Observability and Modular Architecture (15~20 mins)](#chapter-5-k6-observability-and-modular-architecture)
- [Chapter 6: k6 x agent AI Agent Engineering (18~22 mins)](#chapter-6-k6-x-agent-ai-agent-engineering)

---

# Chapter 1: Modern Performance Testing with k6
**建議錄製時長**：18 ~ 20 分鐘 (共 10 頁投影片)  
**章節主旨**：破除傳統 XML 壓測工具的繁重包袱，帶領學員建立「測試即代碼 (Testing as Code)」的現代化壓測心智模型、掌握全平台安裝、k6 CLI x AI (MCP & Agent) 新一代工作流與 4 階段生命週期。

---

### Slide 1: 封面與核心定位 - 擁抱 Test as Code
* **視覺焦點**：JMeter XML 痛點三卡片 vs k6 核心定位 (Test as Code) 與雙引擎三卡片。
* **心智模型**：現代軟體工程（CI/CD、微服務、雲原生）需要開發者友善、版本控管且極致高效的壓測工具。
* **🎤 口播逐字稿**：
  > 「大家好，歡迎來到這堂課程。在過去十年，談到效能壓測，很多工程師腦海浮現的是笨重的 GUI 介面、巨大且難以維護的 XML 檔，還有每次想把壓測整合進 CI/CD 時那種痛苦的折磨。  
  > 傳統工具帶來配置維護地獄、開發體驗斷層與 CI/CD 整合困難。而 k6 的核心哲學是 **Testing as Code**：以標準 JavaScript/ES6 撰寫測試，享有 Git 版本控制，並擁有 Go + JS 雙引擎威力。在第一章，我將帶大家建立完整的現代化效能測試心智模型。」

---

### Slide 2: 極致資源利用率 - Goroutine vs 傳統執行緒
* **視覺焦點**：Java Thread (1MB+ per thread) vs k6 VU (~1–5MB per VU，goroutine 本身僅 ~2KB) 記憶體與架構對照圖。
* **心智模型**：k6 底層由 Go 語言編寫，利用 Goroutines 實現極高併發與極低記憶體佔用。
* **🎤 口播逐字稿**：
  > 「很多學員會好奇：『k6 寫的是 JavaScript，效能真的會好嗎？』  
  > 這是一個極為關鍵的架構觀念：**k6 只有腳本解析層是 JavaScript，底層真正的執行引擎完全是由 Go 語言打造的！**  
  > 傳統 JVM 工具一個虛擬用戶 (VU) 綁定一條 OS 執行緒，堆疊開銷 1MB 到 2MB，幾千併發就把記憶體吃光並觸發 GC 暫停。  
  > 而 k6 利用 Go 的 Goroutine 排程，Goroutine 初始堆疊僅 2KB 到 4KB、Context Switch 成本極低。但要注意，一個 k6 VU 還帶著獨立的 JS Runtime，官方估算簡單腳本每個 VU 約 1 到 5MB；一台高規格機器可跑到三到四萬個 VU。實務上請先用 100 VU 實測記憶體再等比例推估。」

---

### Slide 3: 工欲善其事 - k6 全平台快速安裝指南
* **視覺焦點**：Linux、macOS、Windows、Docker 四大平台卡片與底端 `k6 version` 驗證欄。
* **心智模型**：k6 是 Go 編譯的單一二進位檔（Single Binary），免 Node.js/Go 依賴，跨平台一分鐘裝好。
* **🎤 口播逐字稿**：
  > 「了解架構後，如何把環境準備好？k6 是 Go 編譯的單一二進位執行檔，不需要預裝 Node.js 或 Go Runtime：  
  > 1. **Linux**：Ubuntu/Debian 透過官方 GPG 與 APT 安裝；Fedora/RHEL/CentOS 用 RPM 套件庫一鍵 dnf；Arch Linux 用 pacman；亦支援 Snap。  
  > 2. **macOS**：Homebrew 使用者一行 `brew install k6`，原生支援 Apple Silicon ARM64。  
  > 3. **Windows**：微軟官方 `winget install k6 --source winget`，或用 Chocolatey、MSI 安裝檔；更推薦搭配 WSL2 Ubuntu 享受純粹 Linux 網路棧。  
  > 4. **Docker 容器**：CI/CD Runner 或免安裝環境直接跑 `docker run --rm -i grafana/k6 run - < script.js`。  
  > 最後在終端機敲入 `k6 version`，確認輸出版本號即代表環境就緒！」

---

### Slide 4: 壓測進入 AI 時代 - k6 CLI x AI 現代化工作流
* **視覺焦點**：左側 k6 MCP Server 配置與三大 Tools；右側 Bootstrap with k6 x Agent 自主逆向生成流程圖。
* **心智模型**：利用 Model Context Protocol (MCP) 與 AI Agent，將數天的手寫腳本流程縮短為秒級逆向生成與自癒驗證。
* **🎤 口播逐字稿**：
  > 「在手寫第一行腳本前，我們要看 2025/2026 最振奮人心的突破——**k6 CLI x AI 現代化工作流！**  
  > 新版 k6 內建 MCP 子命令 `k6 x mcp`（無須 Node.js / npx），透過 Model Context Protocol (MCP) 串接 Claude Code、Cursor、VS Code Copilot 等 AI 助手。  
  > AI 助手具備三大超能力：`validate_script`（以 1 VU、1 次迭代實際執行預檢）、`run_script`（對話內直接執行壓測並解析 P95 與錯誤）、`get_documentation`（動態檢索官方最新 API）。  
  > 更具革命性的是 **Bootstrap with k6 x Agent**：給予專案 OpenAPI 規格或 HAR 錄製檔，Agent 自動逆向生成 Smoke、Load、Stress 完整情境，並自主調用 `validate_script` 跑 1 VU 冒煙閉環自癒，秒級交付可立即上線的企業級測試套件！」

---

### Slide 5: k6 四階段生命週期 (Lifecycle Architecture)
* **視覺焦點**：Init $\rightarrow$ Setup $\rightarrow$ default function $\rightarrow$ Teardown 四個方塊流向。
* **心智模型**：明確區分「全域準備」與「高頻迭代」，避免在 VU 迴圈內重複做昂貴操作。
* **🎤 口播逐字稿**：
  > 「要寫好 k6 腳本，必須先掌握它的 4 階段生命週期：  
  > 第一階段 **Init**：解析腳本、載入模組，注意只跑一次且『絕對不能發送 HTTP 請求』。  
  > 第二階段 **setup()**：壓測開始前全域執行一次。呼叫登入 API 取得全域 Token，並傳遞給後續 VU。  
  > 第三階段 **default function (VU Code)**：壓測的心臟！所有虛擬用戶會依照排程反覆執行這裡的請求與斷言。  
  > 第四階段 **teardown()**：測試結束後全域執行一次，用來清理測試帳號、刪除暫存資料。  
  > 劃分清楚這四階段，結構清晰且絕不浪費資源。」
* **⚠️ 避坑警示**：特別強調「Init 階段發 HTTP 請求會直接拋出異常錯誤」。

---

### Slide 6: 讓測試結果一目瞭然 - 使用 group() 進行業務分組
* **視覺焦點**：指標混雜（未分組）的亂線圖 vs 使用 `group('Login_Flow')` 後的清晰長條圖。
* **心智模型**：將數個 API 打包成語意化的 User Journey，Console 與 Grafana 獨立統計。
* **🎤 口播逐字稿**：
  > 「真實的使用者旅程包含多個連續步驟（瀏覽、登入、搜尋、結帳）。如果全部寫在一起，指標會全部混雜，無法定位瓶頸。  
  > 透過 `group()`，我們可以把相關 API 打包成邏輯事務。k6 控制台與 Grafana 都會為該 Group 建立獨立統計維度，實現精準監控。」

---

### Slide 7: 效能測試中的軟性斷言 - check() 非中斷機制
* **視覺焦點**：傳統 Assert 撞牆崩潰 vs k6 Check 軟斷言如穿過感應門持續執行。
* **心智模型**：`check()` 是軟性斷言，只記錄成功率到 `checks` 指標，絕不中斷高壓流量產生。
* **🎤 口播逐字稿**：
  > 「這解決了 90% 單元測試背景工程師的疑惑。單元測試中 assert 失敗立刻中斷，但在高併發壓測中，偶發 1 次錯誤不應該讓整場測試夭折，而是要精確算出 99.9% 的成功率。  
  > k6 的 `check()` 是**軟性斷言**，驗證失敗依然會讓 VU 繼續跑，背景默默記錄成功率。若需要因失敗中斷 CI/CD，我們將在 Chapter 3 用 Thresholds 來實現。」

---

### Slide 8: 防範記憶體炸彈 - 使用 http.url 處理動態 URL
* **視覺焦點**：`/api/orders/123` 導致的 High Cardinality 爆炸 vs `http.url` 模板聚合漏斗。
* **心智模型**：動態參數 URL 必須使用 `http.url` 標籤模板收斂，避免 Prometheus/Grafana OOM 當機。
* **🎤 口播逐字稿**：
  > 「這頁價值百萬！很多團隊把公司監控打掛就是因為這個低級錯誤。  
  > 測試 RESTful API 時，若寫 `http.get('/api/users/' + id)`，k6 預設會為每個不同 URL 在記憶體建立一條時間序列。10 萬次請求產生 10 萬條時序，Prometheus 會瞬間 OOM 癱瘓！  
  > 正確做法是使用 `http.url` 標籤模板：``http.url`https://api.example.com/users/${id}` ``，所有動態請求自動聚合在同一個名為 `/users/${id}` 的指標下，兼顧真實請求與監控穩定。」

---

### Slide 9: 10 行關鍵程式碼實戰 (The 10-line Essence Script)
* **視覺焦點**：包含 options、group、http.url、check 的 10 行生產級精華代碼與四周註釋。
* **心智模型**：生命週期 options $\rightarrow$ VU default 函式 $\rightarrow$ group 業務封裝 $\rightarrow$ http.url 收斂 $\rightarrow$ check 軟斷言。
* **🎤 口播逐字稿**：
  > 「這份 10 行代碼將剛才所學融會貫通：頂部宣告 options 配置 VU 與時長，default 函式內使用 group 封裝業務，搭配 http.url 收斂動態指標與 check 宣告軟斷言。  
  > 簡潔、純粹、易維護。」
* **💻 Live Demo 時機**：
  > 「現在切換至終端機，執行演示腳本：`k6 run k6/demos/ch1_lifecycle_and_checks.js`。大家看終端機：Init、Setup、VU 1 與 2 並行、Teardown 依序執行，2 秒內完成並印出漂亮的統計報表！」

---

### Slide 10: Module 1 核心重點複習 & 第二章預告
* **視覺焦點**：三大核心總結卡片（雙引擎超高效能、生命週期 4 階段、必備三大神器）與 Next Step 提示。
* **🎤 口播逐字稿**：
  > 「第一章我們掌握了四大心智模型：Testing as Code、Goroutine 高效架構、全平台安裝與 AI/MCP 工作流、以及生命週期與必備三大神器（group, check, http.url）。  
  > 但在真實世界中，流量是動態變化的！促銷搶購、尖峰波形該如何科學化定義？更重要的是，為什麼傳統的虛擬用戶壓測會隱瞞系統 90% 的真實延遲，陷入可怕的『協調性漏測』陷阱？  
  > 歡迎進入第二章：Scientific k6 Traffic Modeling！」

---

# Chapter 2: Scientific k6 Traffic Modeling
**建議錄製時長**：18 ~ 22 分鐘  
**章節主旨**：深入 5 大流量模式、破解「協調性漏測 (Coordinated Omission)」陷阱、運用 Little's Law 精算開放模型，並掌握 `SharedArray` 記憶體優化。

---

### Slide 1: 封面 - Scientific k6 Traffic Modeling
* **視覺焦點**：電路圖/流量藍圖背景，程式碼已修正為標準 `export default function ()`。
* **心智模型**：壓測不是無腦把 VU 設到最大，而是依據真實流量特徵進行科學建模。
* **🎤 口播逐字稿**：
  > 「歡迎回到第二章。很多團隊做壓測時，最常犯的錯誤就是：『隨便開 100 個 VU，跑跑看系統會不會死』。這種測試既測不出真實瓶頸，也無法指導架構優化。  
  > 本章我們將從科學建模的角度出發，探討負載測試、壓力測試、尖峰測試的差異，並深入揭露效能工程界著名的『協調性漏測』盲點。」

---

### Slide 2: 今日學習地圖 (Traffic Modeling Blueprint)
* **視覺焦點**：5 大流量晶片模組全景圖。
* **心智模型**：建立本章的導航地圖，從流量型態到開放模型與記憶體調優。
* **🎤 口播逐字稿**：
  > 「大家看到的這張藍圖，是我們今天整堂課的學習地圖。我們將依序穿越：  
  > 基礎的 Stages 階梯式加壓、突發流量 Spike 模擬、閉環與開放模型的本質對決、Little's Law 精準計算，最後解鎖能讓記憶體暴降 90% 的 `SharedArray` 神技。」

---

### Slide 3: 階梯式負載與冒煙測試 (Smoke & Load Testing)
* **視覺焦點**：Smoke Test 曲線 (1 VU, 短時間) vs Load Test 階梯曲線 (Ramp-up, Plateau, Ramp-down)。
* **心智模型**：Smoke 驗功能與腳本正確性，Load 驗證一般峰值下的穩定度。
* **🎤 口播逐字稿**：
  > 「首先看最基本的兩種型態：  
  > **Smoke Testing（冒煙測試）**：通常只用 1 個 VU 跑幾分鐘，目的不是壓垮系統，而是在上線或大幅修改後，確認 API 路由、鑑權 Token、資料庫連線是通的。  
  > 接著是 **Load Testing（常規負載測試）**：我們透過 `stages` 陣列定義三個階段：先用 5 分鐘緩慢爬坡 (Ramp-up) 避免熱點瞬間擊穿，接著在高負載高原期維持 15 分鐘觀察系統穩定性，最後平緩降速 (Ramp-down) 觀察連線資源是否正常釋放。」

---

### Slide 4: 壓力測試與尖峰測試 (Stress & Spike Testing)
* **視覺焦點**：Stress Test (衝向極限拐點) vs Spike Test (瞬間垂直衝天)。
* **心智模型**：Stress 找破壞點 (Breaking Point)，Spike 測自動擴展 (HPA) 與恢復彈性。
* **🎤 口播逐字稿**：
  > 「當系統通過常規負載後，接下來就要進入極限挑戰：  
  > **Stress Testing（壓力測試）**：不斷持續加壓，直到系統出現吞吐量下降、錯誤率飆升的拐點。它的目標只有一個：『找出系統在哪個併發數下會崩潰』，並評估自癒能力。  
  > **Spike Testing（尖峰突發測試）**：模擬名人發文、限量搶購，流量在數十秒內暴增數十倍。這考驗的是你的 Kubernetes HPA 自動水平擴展反應速度，以及快取與消息隊列的抗震能力。」

---

### Slide 5: 協調性漏測的致命盲點 (Coordinated Omission)
* **視覺焦點**：車流因車禍被堵在收費站，後方統計車流速度時出現「嚴重失真」的圖解。
* **心智模型**：當伺服器變慢時，閉環模型發不出請求，導致統計到的延遲數據「看起來很漂亮」，實際上卻是假象！
* **🎤 口播逐字稿**：
  > 「現在進入本章最精采、也是最高階的觀念：**協調性漏測 (Coordinated Omission)**，這是知名效能專家 Gil Tene 提出的經典理論。  
  > 傳統的壓測（例如只指定 10 個 VU）是**閉環模型 (Closed Loop)**。每個虛擬用戶必須等待前一個請求回應，才會發出下一個請求。  
  > 這會造成什麼災難？當後端突然卡頓 5 秒時，你的 10 個 VU 全部被卡住！在這 5 秒內，根本沒有新的請求送出。測試工具最後算出來的延遲可能只有幾百毫秒，但真實世界的使用者早就蜂擁而至，在外部排隊排到抓狂了！閉環模型無意中『協調』並隱瞞了系統最致命的延遲。」

---

### Slide 6: 閉環 vs 開放模型對決 (Closed vs Open Model)
* **視覺焦點**：Closed Model (VU 阻塞 RPS 暴跌) vs Open Model (抵達率固定，自動加派 VU)。
* **心智模型**：真實使用者的到達是獨立事件 (Open System)，測試工具必須能夠解耦 VU 與 RPS。
* **🎤 口播逐字稿**：
  > 「解決協調性漏測的唯一途徑，就是採用**開放模型 (Open Model)**。  
  > 在開放模型中，我們不再問『有幾個虛擬用戶』，而是宣告『每秒鐘抵達系統的請求數 (Arrival Rate) 必須是 500 RPS』！  
  > 當後端變慢時，k6 不會傻傻等著，它會啟動新的 Worker/Goroutine 強制繼續按照既定頻率發送請求。這樣才能真實模擬使用者湧入，並精準抓到隊列堆積後的長尾延遲 (Tail Latency)。」

---

### Slide 7: Little's Law 精算與 Ramping Arrival Rate
* **視覺焦點**：數學公式 $L = \lambda W$，`preAllocatedVUs` 與 `maxVUs` 設定對照。
* **心智模型**：Little's Law：在系統中的並行量 = 抵達率 $\lambda$ × 平均駐留時間 $W$。
* **🎤 口播逐字稿**：
  > 「要設定好開放模型，你必須學會利特爾法則（Little's Law）：$L = \lambda W$。  
  > 假設你的目標是每秒 100 個請求（$\lambda = 100$），系統預期平均耗時 200 毫秒（$W = 0.2$ 秒），那麼你在系統中平均只需要 $100 \times 0.2 = 20$ 個並行 VU。  
  > 因此在 k6 的 `ramping-arrival-rate` 執行器中：  
  > 我們把 `preAllocatedVUs` 設為 20；但萬一伺服器延遲飆升到 1 秒呢？這時就需要 100 個 VU！所以我們給予 `maxVUs: 150` 作為彈性池。  
  > 透過這套公式，你的壓測資源配置就具備了嚴謹的數學依據，不再靠猜測！」

---

### Slide 8: 多場景調度與 Dropped Iterations 預警
* **視覺焦點**：多個 Scenario 疊加圖形與 `dropped_iterations` 指標紅字。
* **心智模型**：當 `maxVUs` 耗盡仍無法維持目標 RPS 時，k6 會記錄 `dropped_iterations`。
* **🎤 口播逐字稿**：
  > 「在 k6 中，你可以同時定義多個 `scenarios`，讓 API 流量與登入流量在不同的時間軸交錯啟動。  
  > 在開放模型運作時，請大家緊盯一個關鍵指標：`dropped_iterations`。  
  > 如果這個指標大於 0，代表後端延遲已經大到連你的 `maxVUs` 都被佔滿了，k6 無法再發出設定的請求頻率。在 CI/CD 中，這是一個明確的系統崩潰信號！」
* **💻 Live Demo 時機**：
  > 「讓我們切換到終端機，執行 `k6 run k6/demos/ch2_closed_vs_open_model.js`，大家可以看到當端點有 1 秒延遲時，開放模型如何動態調用 VU 來守住我們的目標 RPS！」

---

### Slide 9: SharedArray 記憶體救援神技
* **視覺焦點**：普通 JS 陣列 (1000 份拷貝 OOM) vs `SharedArray` (單一唯讀記憶體映射)。
* **心智模型**：普通陣列隨 VU 複製，`SharedArray` 全域共享，節省 90% 記憶體。
* **🎤 口播逐字稿**：
  > 「很多學員在做萬人併發測試時，載入一個 50MB 的 CSV 測試帳號檔，結果 k6 剛啟動就記憶體不足崩潰 (OOM)。  
  > 原因在於：k6 為了執行緒安全，每個 VU 都有獨立的 JavaScript 虛擬機。如果你直接用 `JSON.parse` 載入，1,000 個 VU 就會複製 1,000 份，50MB 瞬間變成 50GB！  
  > 解決方案就是畫面上的 **SharedArray**（來自 `k6/data` 模組）。它採用底層 Go 的記憶體共享機制，整份資料在記憶體中永遠只有一份，所有 VU 唯讀存取，記憶體用量直接降到零頭！」
* **💻 Live Demo 時機**：
  > 「執行 `k6 run k6/demos/ch2_shared_array.js`，看 10,000 筆資料如何優雅地在多個 VU 間分發且瞬時啟動。」

---

### Slide 10: 第二章總結與品質門禁引言
* **視覺焦點**：科學流量建模總覽與 Exit Code 99 標誌。
* **🎤 口播逐字稿**：
  > 「恭喜大家完成第二章！我們學會了五大流量特徵、掌握了避免協調性漏測的開放模型，並學會了用 `SharedArray` 壓榨極限效能。  
  > 但是，壓測跑完了、圖表印出來了，到底怎樣算『通過』？怎樣算『失敗』？我們總不能叫維運工程師每次都用肉眼去盯報表吧？  
  > 下一章，我們將進入企業級 CI/CD 的靈魂核心——Chapter 3: k6 Quality Gates。」

---

# Chapter 3: k6 Quality Gates & SLO Enforcement
**建議錄製時長**：22 ~ 25 分鐘 (共 12 頁投影片)  
**章節主旨**：從 Google SRE 的 RED 方法論出發，建立百分位數 (p95/p99) 門禁，運用 4 大自訂指標，並以 Exit Code 99 實現 CI/CD 自動卡關。

---

### Slide 1: 封面 - k6 Quality Gates
* **視覺焦點**：自動化品質閘門、SLO、CI/CD 符號。
* **心智模型**：品質門禁是把「人肉肉眼看圖」轉換為「代碼自動裁決」的關鍵機制。
* **🎤 口播逐字稿**：
  > 「歡迎來到第三章。很多團隊建了漂亮的儀表板，但每次發版前依然在問：『這次效能到底能不能上線？』  
  > 現代軟體工程講究的是客觀的 **SLO (服務水準目標)**。如果壓測不能自動判定及格或不及格，不能在違規時自動中止部署，那壓測就只是做心安的裝飾品。  
  > 本章將教大家如何用 k6 的 Thresholds 機制，把 SRE 的品質門禁無縫嵌進你的 CI/CD Pipeline。」

---

### Slide 2: 一眼看穿系統健康度 (The RED Method)
* **視覺焦點**：Rate (吞吐量)、Errors (錯誤率)、Duration (延遲) 三位一體圖解。
* **心智模型**：微服務黃金監控法則，所有 SLO 與 Thresholds 均圍繞這三項指標展開。
* **🎤 口播逐字稿**：
  > 「在設定門檻前，我們要先認識微服務監控的黃金標準——**RED Method**：  
  > **Rate（請求速率）**：系統當前每秒正在處理多少個請求？  
  > **Errors（錯誤率）**：有多少請求以 5xx 或預期外的業務錯誤結束？  
  > **Duration（持續時間/延遲）**：請求消耗了多少時間？  
  > 在 k6 中，`http_reqs` 對應 Rate，`http_req_failed` 對應 Errors，而 `http_req_duration` 對應 Duration。掌握這三者，你就掌握了系統 90% 的健康真相。」

---

### Slide 3: 尾端延遲深度解析 (Tail Latency & Percentiles)
* **視覺焦點**：平均值 (Average) 隱瞞真相 vs P95 / P99 長尾延遲分佈圖。
* **心智模型**：千萬不要看 Average！在現代高併發分散式系統中，平均值毫無意義，長尾延遲決定用戶流失。
* **🎤 口播逐字稿**：
  > 「請大家在心裡默念三遍：**永遠不要在壓測中看平均值 (Average)！**  
  > 如果 99 個使用者的回應時間是 10 毫秒，只有 1 個使用者卡了 10 秒鐘，算出來的平均值依然只有大約 100 毫秒，看起來非常健康！但那個卡了 10 秒的用戶，往往是正在購物車結帳、準備掏錢的大客戶！  
  > 這就是為什麼我們必須看百分位數：  
  > **P95** 代表 95% 的請求都優於這個時間；**P99** 則精確捕捉了最倒楣的 1% 用戶體驗。在設定 Thresholds 時，一律以 P95 或 P99 作為驗收基準。」

---

### Slide 4: k6 內建核心指標全覽 (Built-in Metrics)
* **視覺焦點**：k6 內建指標分類與 6 個延遲細分指標 (blocked, connecting, tls, sending, waiting, receiving)。
* **心智模型**：了解延遲到底是塞在網路握手、伺服器計算 (TTFB)，還是回傳資料過大。
* **🎤 口播逐字稿**：
  > 「k6 把一次 HTTP 請求拆成六個細分指標：等待連線槽位（含 DNS）的 `http_req_blocked`、TCP 握手的 `http_req_connecting`、TLS 握手的 `http_req_tls_handshaking`，以及送出請求的 `http_req_sending`、最關鍵的伺服器處理時間 `http_req_waiting` (TTFB)、下載回應的 `http_req_receiving`。  
  > 注意：`http_req_duration` 只等於後三段（sending + waiting + receiving），前三段的連線時間不計入。  
  > 如果你的 duration 飆高，但 waiting 很低、receiving 很高，問題八成出在你的 API 回傳了過於龐大的無效 JSON Payload！」

---

### Slide 5: 看懂 k6 結尾摘要 (5 步驟判讀 SOP)
* **視覺焦點**：左側標註 ①～⑤ 的終端機摘要，右側 5 張判讀步驟卡。
* **心智模型**：判決 → 正確性 → 分佈形狀 → 壓測有效性 → 頻寬。門檻全綠不代表結果可信。
* **🎤 口播逐字稿**：
  > 「摘要不要從頭讀到尾，要照順序帶著問題讀：先看 THRESHOLDS 判決，再看 checks 正確性，接著看 HTTP 分佈形狀——中位數和 P95 差超過 3 倍就是長尾；然後看 EXECUTION，`dropped_iterations` 大於 0 或 vus 碰到 vus_max，代表流量根本沒打滿；最後看 NETWORK 頻寬。  
  > 這個例子五步走完，結論是：後端在約 50 RPS 就飽和了。」

---

### Slide 6: 延遲拆解 (http_req_duration 只算後 3 段)
* **視覺焦點**：6 格時間軸，左 3 格灰色不計入 duration，右 3 格紫色計入；下方 4 張診斷卡。
* **心智模型**：`http_req_duration = sending + waiting + receiving`；連線層問題只會拉長 `iteration_duration`。
* **🎤 口播逐字稿**：
  > 「很多人以為 duration 包含建立連線的時間，其實沒有。blocked、connecting、tls_handshaking 都不算在 duration 裡，所以連線層的問題只盯 duration 是看不到的。  
  > waiting 高是最常見的後端瓶頸，receiving 高是 Payload 太大。除錯時記得加 `--summary-mode=full`，才看得到這六個細分指標。」

---

### Slide 7: 四大自訂指標型態 (Custom Metrics)
* **視覺焦點**：Counter、Gauge、Rate、Trend 四種圖示與使用情境。
* **心智模型**：不僅監控 HTTP 網路層，更能監控業務語意層（如訂單成交數、自訂計算耗時）。
* **🎤 口播逐字稿**：
  > 「除了內建的 HTTP 指標，k6 允許我們定義四大自訂指標：  
  > 1. **Counter（累計器）**：只能累加，適合統計訂單成交總數、特定異常發生次數。  
  > 2. **Gauge（瞬時規）**：可增可減，用來記錄當下併發 Worker 數或記憶體水位。  
  > 3. **Rate（成功率）**：記錄 0 到 1 之間的值，用來計算業務交易成功率。  
  > 4. **Trend（統計趨勢）**：會自動計算 p90、p95、avg、med，極為適合用來記錄自訂的資料庫查詢耗時或外部微服務 RPC 時間。」

---

### Slide 8: 斷言三部曲完整對照 (check vs thresholds vs expect)
* **視覺焦點**：三者對照表（層級、是否中斷、輸出效果）。
* **心智模型**：`check` 是代碼軟斷言，`thresholds` 是全域硬門禁，`expect` 是 BDD 風格語法。
* **🎤 口播逐字稿**：
  > 「很多工程師會搞混 `check` 和 `thresholds`。我們做個權威對比：  
  > `check()` 發生在請求層級，即使斷言失敗，測試照樣跑，只在終端機印個小紅叉。  
  > 而 `thresholds` 是最高統治者，它是全域品質門禁！只要任何一條門檻未達標，測試結束後整個行程會被標記為失敗。  
  > 如果你在寫測試時習慣 Mocha 或 Jest 的 BDD 風格，k6 也支援 `k6/chai` 的 `expect()` 語法。」

---

### Slide 9: 精準控制 API SLO (Thresholds 與 Tags 組合技)
* **視覺焦點**：帶有 `{ api_type: 'critical' }` 標籤的宣告式門檻代碼。
* **心智模型**：不同等級的 API 要有不同的 SLO，不可一體適用。
* **🎤 口播逐字稿**：
  > 「在微服務架構中，你不可能對所有 API 設定同一套標準。報表下載 API 允許 3 秒，但結帳登入 API 超過 500 毫秒就是重大事故！  
  > 在 k6 中，我們可以結合 Tag 標籤進行精確過濾：  
  > 例如畫面上的 `'http_req_duration{api_type:critical}': ['p(95)<300']`。只有被標記為 critical 的請求才會被納入這條嚴格的門禁，其他次要端點則走寬鬆標準，實現多階層的精細化治理。」

---

### Slide 10: CI/CD 自動卡關實務 (Exit Code 99 傳遞鏈)
* **視覺焦點**：GitLab CI / GitHub Actions 流水線紅叉，終端機 `echo $?` 印出 `99`。
* **心智模型**：Unix 標準回傳碼 99 是 CI/CD 識別效能門禁破功的核心機制。
* **🎤 口播逐字稿**：
  > 「這是整堂課最值錢的自動化關鍵：**Exit Code 99**。  
  > 當 k6 測試結束時，如果所有 Thresholds 全部及格，行程回傳 exit code 0，CI/CD 繼續往下部署；  
  > 但只要有任何一項門檻未達標，k6 就會自動回傳 **99**！  
  > 在 Linux Shell 中，非 0 的回傳碼會直接讓 GitLab CI 或 GitHub Actions 判定該 Job 失敗，立刻終止有問題的代碼合併到主幹，守護生產環境！」
* **💻 Live Demo 時機**：
  > 「請看終端機演示：`k6 run -e FAIL_SLO=true k6/demos/ch3_quality_gates_exit99.js ; echo "CI Exit Code: $?"`，大家親眼看到終端機直接印出紅字與 `Exit Code 99`！」

---

### Slide 11: 模組綜合實戰 (架構化 SLO 代碼)
* **視覺焦點**：帶有 `abortOnFail: true` 的專業級腳本配置。
* **心智模型**：熔斷機制 (Circuit Breaker)，錯誤率飆高時及時止損。
* **🎤 口播逐字稿**：
  > 「在專業的壓測腳本中，我們還會配置 `abortOnFail: true`。  
  > 試想：如果你排程跑 2 個小時的壓力測試，結果前 30 秒資料庫就已經被寫爆了，後續 1 小時 59 分鐘完全是無效的空跑，白白浪費龐大的 CI Runner 與雲端伺服器費用。  
  > 加上 `abortOnFail: true` 與 `delayAbortEval: '5s'`，一旦錯誤率突破容忍極限，k6 會立刻腰斬測試並報警，這才是專業工程師的設計思維。」

---

### Slide 12: 隨堂實作練習指引 (Lab Guide)
* **視覺焦點**：三個實作任務清單。
* **🎤 口播逐字稿**：
  > 「本章的理論到此告一段落。請大家打開本章對應的 Lab Guide，動手完成三個任務：  
  > 第一，為你的登入 API 設定 P95 小於 500ms 的門檻；  
  > 第二，建立一個記錄結帳成功的 Custom Rate 指標；  
  > 第三，刻意製造一次延遲超標，在你的終端機中驗證是否順利拿到 Exit Code 99。做完實作後，我們在第四章見！」

---

# Chapter 4: Precision k6 Hybrid Testing
**建議錄製時長**：20 ~ 23 分鐘 (共 11 頁投影片)  
**章節主旨**：攻克現代 SPA 單頁應用壓測痛點，從 Chrome DevTools HAR 轉譯到 `k6/browser` 無頭瀏覽器，打造 99:1 全鏈路混合壓測黃金架構並完成真實雙向指標會師。

---

### Slide 1: 封面 - Precision k6 Hybrid Testing
* **視覺焦點**：全鏈路觀測、前端與後端融合架構。
* **心智模型**：單純測試後端 API 已經不夠了，使用者真實感受到的是瀏覽器 DOM 渲染與 Web Vitals。
* **🎤 口播逐字稿**：
  > 「歡迎來到第四章。現代 Web 應用充斥著大量的 React、Vue、Angular 單頁應用 (SPA)。  
  > 當使用者抱怨系統變慢時，後端的 API 延遲日誌可能只有 50 毫秒，但前端的 JavaScript 卻因為肥大的 Bundle 或昂貴的 DOM 渲染卡了整整 3 秒！  
  > 傳統的壓測工具只能測協定層（Protocol），完全看不到前端；而傳統的 UI 自動化工具（如 Selenium）又太過沉重，根本做不了高併發。  
  > 本章我們將打破這道界線，帶大家實踐 k6 最強大的**混合壓測 (Hybrid Testing)**。」

---

### Slide 2: HAR 轉換工作流 (HAR Workflow)
* **視覺焦點**：瀏覽器操作 $\rightarrow$ 匯出 .har 檔 $\rightarrow$ `har-to-k6` $\rightarrow$ 產出腳本。
* **心智模型**：善用錄製加速腳本編寫，但切記錄製出來的腳本「絕對不能直接拿去跑」！
* **🎤 口播逐字稿**：
  > 「要手寫幾十支 API 的壓測腳本非常繁瑣，因此我們常利用 HAR (HTTP Archive) 轉換流程：  
  > 打開瀏覽器操作真實業務流程，將網路請求匯出為 `.har` 檔案，再透過 CLI 工具將其轉化為 k6 腳本。  
  > 但我必須嚴肅提醒所有工程師：**錄製只是起點，錄出來的腳本是死代碼，千萬不能直接跑！** 為什麼？我們下一頁揭曉。」

---

### Slide 3: Chrome DevTools 錄製實作 (Recording Best Practices)
* **視覺焦點**：DevTools Network 面板截圖，圈出「Preserve log」、「無痕模式」、「Clear」與「Export HAR」。
* **心智模型**：錄製前清空干擾，確保環境純淨。
* **🎤 口播逐字稿**：
  > 「在進行 Chrome 錄製時，請務必遵守四個標準動作：  
  > 第一，**永遠使用無痕模式 (Incognito Window)**，避免瀏覽器擴充套件（如廣告攔截器、密碼管理器）發出的雜訊請求污染 HAR 檔案；  
  > 第二，**務必勾選 Preserve Log（保留日誌）**，這樣當頁面發生重定向 (Redirect) 或換頁跳轉時，前面的關鍵請求才不會被沖刷洗掉；  
  > 第三，**清空現有 Log**，排除快取干擾後開始操作業務流程；  
  > 第四，**匯出 HAR**，儲存為 `recording.har` 進行後續轉換。」

---

### Slide 4: CLI 轉譯與 401 死資料陷阱 (The Stale Data Trap)
* **視覺焦點**：寫死的 `Authorization: Bearer eyJhbGci...` 紅色警告標記。
* **心智模型**：錄製檔包含過期的靜態 Token 與 Session，必須動態關聯 (Dynamic Correlation)。
* **🎤 口播逐字稿**：
  > 「這就是為什麼錄製腳本直接跑一定會炸開：**401 死資料陷阱**。  
  > 錄製檔裡的 Auth Token、Cookie、CSRF Token 是你在錄製當下那個瞬間的快照。一旦過了 5 分鐘，Token 過期，你的 1000 個虛擬用戶全部只會收到 401 Unauthorized！  
  > 你以為系統很穩定，其實後端根本連業務邏輯都沒執行，直接在閘道層把請求退回去了。我們必須動態萃取 Token 進行參數關聯。」

---

### Slide 5: 腳本清理三大法則 (Script Cleanup Laws)
* **視覺焦點**：去靜態資源、動態關聯、模組化三步驟圖解。
* **心智模型**：Don't load test Google! 壓測只針對自己控制的核心伺服器。
* **🎤 口播逐字稿**：
  > 「拿到錄製腳本後，請落實腳本清理的三大法則：  
  > 法則一：**剝離第三方靜態資源**。業界有一句名言：『Don't load test Google!』請把 Google Analytics、字型 CDN、外鏈圖片全部過濾掉，不要去壓測別人的基礎設施；  
  > 法則二：**動態關聯 (Correlation)**。在 setup() 階段動態登入，將取回的 Token 注入到請求 Header 中；  
  > 法則三：**模組化封裝**。將重構後的 API 調用抽象成函式，方便跨團隊重用。」

---

### Slide 6: Protocol-Level vs Browser-Level 決戰
* **視覺焦點**：協定級 (超高併發、無 DOM、成本極低) vs 瀏覽器級 (真實 Chromium、DOM 渲染、Web Vitals、資源昂貴)。
* **心智模型**：明白兩者的優劣互補，而非二選一。
* **🎤 口播逐字稿**：
  > 「我們來看這場世紀對決：  
  > **Protocol-Level（協定級）**：發送純粹的 TCP/HTTP 請求，不解析 CSS、不執行 JS、不渲染 DOM。優點是速度極快、1 台機器能跑上萬併發，缺點是完全看不見使用者在前端的真實體驗。  
  > **Browser-Level（瀏覽器級）**：啟動真正的 Headless Chromium，執行所有前端代碼並測量 Core Web Vitals。優點是 100% 反映真實人眼感受，缺點是一台機器跑幾十個 Chrome 就會把記憶體與 CPU 榨乾。  
  > 難道我們只能在『高併發』與『真實體驗』之間二選一嗎？答案是不用！」

---

### Slide 7: k6/browser 核心語法與資源釋放
* **視覺焦點**：修正後的代碼 `browser: { type: 'chromium' }`，圈出 `try-finally` 與 `page.close()`。
* **心智模型**：`k6/browser` 語法類似 Playwright，必須嚴格管理瀏覽器分頁生命週期。
* **🎤 口播逐字稿**：
  > 「在 k6 最新版本中，`k6/browser` 已經原生內建！  
  > 語法非常親切，跟 Playwright 高度相仿。我們宣告 `browser: { type: 'chromium' }`，接著用 `const page = await browser.newPage()` 建立分頁，並透過 `page.locator()` 定位元素並觸發點擊。  
  > 請大家務必看好第 38 行：**所有瀏覽器操作必須包在 try...finally 區塊中，並在 finally 呼叫 await page.close()！** 如果漏掉這行，測試結束後伺服器會殘留大量的孤兒 Chrome 殭屍行程，直到伺服器崩潰為止！  
  > 如果想深入了解電商完整購物流程、BrowserContext 多帳號隔離與自動截圖除錯，推薦研讀我在專欄寫的長文《Grafana k6 瀏覽器測試》（`ganhua.wang/grafana-k6-browser`），裡面有手把手的完整教學！」

---

### Slide 8: 全鏈路混合壓測與 99:1 黃金配比
* **視覺焦點**：雙 Scenario 架構圖：99% Protocol Load + 1% Browser Probe。
* **心智模型**：用低成本協定流量製造暴風雨，用 1 根瀏覽器探針在風暴中量測真實體驗。
* **🎤 口播逐字稿**：
  > 「這就是頂尖架構師採用的 **99:1 黃金混合架構 (Golden Ratio Hybrid Architecture)**：  
  > 我們在同一個腳本中定義兩個 Scenarios：  
  > **99% 的流量**交給 Protocol-Level，用最低的機器成本模擬數千併發，把後端資料庫與快取壓到滿載；  
  > **1% 的流量**交給 `k6/browser` 作為『前端探測針 (Probe)』。當背景負載狂暴轟炸時，這支探測針默默地打開瀏覽器進行下單，即時採集 LCP、INP 與 CLS！  
  > 這樣一來，我們既達成了超大規模的後端壓力，又同時拿到了高負載下真實使用者的端到端前端體驗數據，成本只要原本純瀏覽器壓測的百分之一！」

---

### Slide 9: 實戰成果：QuickPizza 99:1 全鏈路混合壓測現場
* **視覺焦點**：左側展示協定層 280 次 API 請求與 P95 193ms 終端機卡片；右側展示真實 Chromium 探針採集的五大 Core Web Vitals 儀表（LCP 2.1s, FCP 2.1s, INP 24ms, TTFB 587.9ms, CLS 0.00）。
* **心智模型**：前後端指標雙向會師，印證「後端扛得住、前端不卡頓」。
* **🎤 口播逐字稿**：
  > 「現在我們直接看現場真實壓測成果！  
  > 請看左邊的後端數據：在 10 秒內打出 280 次 API 請求，P95 延遲僅 193.65 毫秒，錯誤率 0.00%，140 個業務斷言全部過關！  
  > 再看右邊的前端體驗：在背景滿載壓力下，我們的無頭 Chromium 探針實測出 LCP 僅 2.1 秒、INP 互動延遲只有 24 毫秒、版面位移 CLS 為完美的 0！  
  > 這證明了在後端高壓狀態下，前端使用者體驗完全沒有受到任何降級卡頓，全鏈路 SLO 門檻全數達標！」
* **💻 Live Demo 時機**：
  > 「執行 `k6 run k6/demos/ch4_hybrid_99_to_1.js`，現場展示背景協定高頻轟擊與無頭瀏覽器優雅進場的雙線即時日誌！」

---

### Slide 10: 壓測上線前防呆清單 (Flight Pre-check)
* **視覺焦點**：起飛前檢核表（錄製防呆、清理防呆、混合執行防呆）。
* **心智模型**：壓測如同飛機起飛，必須逐項 Checklist 勾選確認，防止打爆生產環境或誤觸防護。
* **🎤 口播逐字稿**：
  > 「在進行大規模混合壓測前，請像飛行員起飛一樣，逐一確認這份 Flight Pre-check：  
  > 1. 錄製階段是否開啟無痕模式並勾選了 Preserve log？  
  > 2. 清理階段是否剔除了第三方 CDN 並完成 setup() 動態登入？  
  > 3. 混合執行階段是否將瀏覽器 VU 控制在 10% 以內，且末端呼叫了 page.close()？  
  > 4. 是否已通知 SRE 與資安維運團隊，避免被 WAF 防火牆封鎖 IP？」

---

### Slide 11: 隨堂練習指引 (QuickPizza 實戰任務)
* **視覺焦點**：QuickPizza 實戰任務四步路線圖。
* **🎤 口播逐字稿**：
  > 「現在輪到大家動手了！請開啟本章 Lab：  
  > 任務一：打開 `recording_cleaned.js`，體會如何用 setup() 破除 401 死資料陷阱；  
  > 任務二：執行 `ch4_browser_quickpizza.js`，在本地採集第一份真實前端 Web Vitals 報告；  
  > 任務三：執行 `ch4_hybrid_99_to_1.js`，體驗 99:1 雙場景混合壓測的威力。動手做做看吧！」

---

# Chapter 5: k6 Observability and Modular Architecture
**建議錄製時長**：25 ~ 28 分鐘 (共 13 頁投影片)  
**章節主旨**：串聯 Grafana 可觀測性宇宙，運用 Web Dashboard、Prometheus Remote Write 與 Git Commit Tag 解除數據孤島，並掌握 xk6 擴充套件編譯架構與講師深度專欄。

---

### Slide 1: 封面 - k6 Observability and Modular Architecture
* **視覺焦點**：可觀測性三柱、xk6 擴充機制與架構整合。
* **心智模型**：壓測不是獨立工具，它是全面可觀測性體系（Observability）的一環。
* **🎤 口播逐字稿**：
  > 「歡迎來到全系列課程的最終章。在前面的章節，我們學會了寫出高效的腳本、建立了嚴格的品質門禁。  
  > 但在現代企業中，如果壓測數據只停留在測試人員的終端機裡，它就只是一座孤島。  
  > 本章我們要把 k6 徹底融入 Grafana 可觀測性宇宙！我們將解鎖原生即時儀表板、實現 Prometheus 時序數據直連，並學習如何透過 xk6 編譯出支援 Kafka、SQL 等各種協議的客製化 k6 引擎。」

---

### Slide 2: 原生 Web Dashboard 即時監控
* **視覺焦點**：k6 內建 Web Dashboard 截圖 (`http://localhost:5665`)。
* **心智模型**：免部屬外部資料庫，一行環境變數即可啟用現代化 Web 介面。
* **🎤 口播逐字稿**：
  > 「許多工程師不知道，k6 現在已經原生內建了非常漂亮的即時 Web Dashboard！  
  > 你不需要預先架設 Prometheus 或 InfluxDB，只要在執行時加上 `K6_WEB_DASHBOARD=true`，k6 就會在背景啟動一個本機伺服器。打開 `localhost:5665`，你就能看到即時動態刷新的 RPS、P95 延遲、錯誤率與請求細部拆解圖表！」

---

### Slide 3: 匯出靜態 HTML 測試報告 (Port -1 退場技巧)
* **視覺焦點**：`K6_WEB_DASHBOARD_PORT=-1` 與匯出獨立 HTML 檔案指令。
* **心智模型**：在無人值守的 CI/CD 環境中，不需要開 Web Port，只需直接匯出靜態 HTML 作為 Build Artifact。
* **🎤 口播逐字稿**：
  > 「在 CI/CD 流水線中，容器是無人值守的，我們不需要開一個 Web Port 等人連進去。  
  > 這時請記住這個高級技巧：**設定 `K6_WEB_DASHBOARD_PORT=-1` 並指定 `K6_WEB_DASHBOARD_EXPORT=report.html`**。  
  > 這樣 k6 不會啟動 HTTP 監聽，而是在測試結束的瞬間，自動將所有動態圖表封裝成一份單一的靜態 HTML 檔案，可直接上傳到 GitHub Actions 或 Jenkins Artifacts 供團隊下載查閱！」

---

### Slide 4: xk6 擴充機制解剖 (Go-to-JS Bridge)
* **視覺焦點**：xk6 齒輪引擎架構圖，Go Native Code 透過 Bridge 暴露為 JavaScript 模組；左下角高亮講師專欄卡片。
* **心智模型**：k6 本質是個 Go 編譯器，xk6 允許將任意 Go 語言生態庫打包成 k6 的 JS 模組。
* **🎤 口播逐字稿**：
  > 「k6 的原生功能已經很強，但如果你想直接對 Kafka 發送消息、想直接連 PostgreSQL 做 SQL 壓測、或是想打 gRPC 串流呢？  
  > 這就要提到 k6 的黑科技：**xk6 (eXtensible k6)**。  
  > xk6 的架構非常巧妙，它允許社群用 Go 語言撰寫擴充模組，底層透過 Go-to-JS Bridge 自動把 Go 函式暴露給前端的 JavaScript 腳本調用。你擁有了 JavaScript 的開發敏捷度，同時享有 Go 的原生執行效能！  
  > 如果想看生產級 Go 擴充插件實戰，推薦研讀我在專欄寫的《Grafana xk6: 手把手從開發 k6 插件程式到編譯出 k6 插件》（`ganhua.wang/grafana-xk6`），以 Web3 OTP 動態金鑰為例實作 `RootModule` 與 `modules.Register`！」

---

### Slide 5: 擴充套件雙引擎 (JS Extensions vs Output Extensions)
* **視覺焦點**：兩大擴充分類（協議驅動 vs 指標輸出驅動）。
* **心智模型**：擴充套件分為「擴展測試協議 (JS)」與「擴展數據匯出 (Output)」。
* **🎤 口播逐字稿**：
  > 「xk6 擴充模組主要分為兩大類別：  
  > 第一類是 **JS Extensions（協定擴充）**：例如 `xk6-kafka`、`xk6-sql`、`xk6-redis`，讓你的腳本可以直接操作底層中間件；  
  > 第二類是 **Output Extensions（輸出擴充）**：將測試產生的時序指標實時推播給不同的後端，例如推送到 Datadog、CloudWatch 或 Kafka。」

---

### Slide 6: xk6 build 與 Docker 確定性編譯
* **視覺焦點**：Docker 編譯指令，`-v $(pwd):/xk6` 與 `--with` 語法。
* **心智模型**：不需在本地安裝 Go 開發環境，利用官方容器實現確定性編譯。
* **🎤 口播逐字稿**：
  > 「要編譯擴充套件，最強烈推薦使用官方提供的 Docker 映像檔 `grafana/xk6`。  
  > 如螢幕上的指令所示：我們掛載本機目錄 `-v $(pwd):/xk6`，並加上 `--with github.com/grafana/xk6-sql`。  
  > 容器會自動下載依賴、完成 Go 編譯，並把編譯好的客製化 `k6` 二進位檔直接放回你的本機目錄。團隊所有成員不需要設定 Go 環境，就能擁有 100% 確定性的自訂引擎！」

---

### Slide 7: Prometheus Remote Write 與 Commit Tag 綁定
* **視覺焦點**：`k6 run -o experimental-prometheus-rw` 與 `--tag commit_id=...`。
* **心智模型**：將測試結果作為時序指標直接推送至 Prometheus，並打上版本標籤實現版本對比。
* **🎤 口播逐字稿**：
  > 「在企業環境中，最優雅的做法是使用 **Prometheus Remote Write**。  
  > 請注意：本專案 Lab 中的 Prometheus 已經在啟動參數加入了 `--web.enable-remote-write-receiver`。  
  > 當我們執行 k6 時加上 `-o experimental-prometheus-rw`，k6 就會以時序串流的方式把每秒的延遲與請求數直接推送給 Prometheus。  
  > 更妙的是，我們在指令中注入 `--tag commit_id=$(git rev-parse --short HEAD)`！如此一來，在 Grafana 上我們就能輕鬆下拉選擇不同 Git Commit，直接比對前後兩個版本的效能差異！」

---

### Slide 8: 看懂儀表板 (6 種經典曲線型態)
* **視覺焦點**：3×2 迷你折線圖：健康線性、飽和平台、崩潰懸崖、尾巴張開、緩慢爬坡、週期鋸齒。
* **心智模型**：永遠把負載軸（VUs / RPS）與反應軸（P95・P99 / 錯誤率）疊在一起看，找出拐點。
* **🎤 口播逐字稿**：
  > 「摘要告訴你 P95 是多少，曲線告訴你它從什麼時候開始變壞。最重要的是第二種『飽和平台』：VUs 還在加，RPS 卻走平，同時 P95 開始爬——拐點當下的 RPS 就是系統容量。  
  > 其他型態：崩潰懸崖是延遲和錯誤率一起暴衝；尾巴張開是只有 P99 發散；緩慢爬坡是負載不變延遲卻上升，代表資源洩漏；週期鋸齒要去查排程、GC 和快取 TTL。」

---

### Slide 9: 儀表板判讀 4 步驟 SOP
* **視覺焦點**：左側 4 步驟；右上 Web Dashboard 分頁地圖；右下三個判讀陷阱。
* **心智模型**：確認壓力打出去 → 找拐點 → Timings 定位哪一段 → Grafana 十字準星對齊後端。
* **🎤 口播逐字稿**：
  > 「四步驟：先確認壓力真的打出去，再找拐點時間，接著用 Timings 分頁定位哪一段變慢，最後帶著拐點時間到 Grafana 對齊後端指標。  
  > 三個陷阱：Overview 數字卡的 Duration 是平均值不是 P95；P95 不能再取平均，所以本專案改用 Native Histogram 加 `histogram_quantile()`；RPS 走平但後端很閒，瓶頸可能在壓測機自己。」

---

### Slide 10: Grafana 全視角對齊 (CPU CFS Throttling 破除孤島)
* **視覺焦點**：Grafana 雙十字準星對齊圖：上方 k6 API 延遲飆高，下方 Kubernetes CPU 限流線 (CFS Throttling)。
* **心智模型**：透過時間軸對齊，一眼看出延遲飆高的根本底層硬體原因。
* **🎤 口播逐字稿**：
  > 「這張畫面是整個可觀測性體系的巔峰時刻！大家看 Grafana 的共享十字準星（Shared Crosshair）：  
  > 上半部是 k6 匯入的 API P95 延遲曲線，在 14:02 分時突然從 50ms 衝到 2 秒；  
  > 如果沒有系統指標，工程師只能盲猜是資料庫慢還是代碼寫爛；  
  > 但請看下半部同一個時間點的 Node Exporter 指標：Pod 的 **CPU CFS Throttling（容器配額限流）** 在同一秒飆升到 80%！  
  > 真相大白！不是程式碼有 Bug，而是 K8s 的 CPU Limit 設得太緊，容器被 Linux 核心強迫降頻卡頓。這就是將壓測指標與基礎設施指標對齊帶來的神級除錯威力！」

---

### Slide 11: 企業導入實作 Checklist (Takeaway)
* **視覺焦點**：企業落地 5 大關鍵步驟（代碼化管理、SLO 明確化、CI/CD 卡關、全鏈路混合、可觀測性閉環）。
* **心智模型**：從個人測試走向團隊工程治理的行動指南。
* **🎤 口播逐字稿**：
  > 「在結束前，我為大家整理了這份企業落地 Checklist，也是這門課程的核心精華：  
  > 1. **測試代碼化**：所有 k6 腳本與應用代碼共存於 Git 倉庫；  
  > 2. **SLO 量化**：捨棄平均值，明確定義 P95/P99 門檻；  
  > 3. **門禁自動化**：用 Exit Code 99 在 CI/CD 中自動守護生產主幹；  
  > 4. **全鏈路混合**：運用 99:1 黃金配比同時兼顧後端負載與前端體驗；  
  > 5. **可觀測性閉環**：將 k6 指標推送至 Prometheus，在 Grafana 與系統日誌、追蹤雙向對齊。」

---

### Slide 12: 推薦延伸閱讀 (Author's Deep-Dive Articles)
* **視覺焦點**：三大專欄卡片（xk6 插件開發、k6-browser 前端混壓、OTel CI/CD 全鏈路實戰）。
* **心智模型**：課程建立體系框架，講師專欄深入前線自訂實戰，雙軌並進。
* **🎤 口播逐字稿**：
  > 「在進入最後隨堂動手做前，我特別為大家推薦我親自撰寫的三篇 k6 系列深度實戰專欄，作為大家的課後進階密技：  
  > 1. **《Grafana xk6: 手把手從開發 k6 插件程式到編譯出 k6 插件》**：深入 Go-to-JS Bridge，以 Web3 OTP 動態金鑰為例手把手開發擴充插件與 Docker 編譯；  
  > 2. **《Grafana k6 瀏覽器測試》**：解析 Playwright 相容語法、BrowserContext 隔離架構，並以電商購物車示範 Web Vitals 採集與自動截圖；  
  > 3. **《Getting Started with Grafana k6: Hands-on Practice》**：教大家用 group 與 check 組織語意化腳本，並直連 OpenTelemetry Collector 與 GitLab CI 門禁。  
  > 投影片上的卡片均可直接點擊開啟，強烈建議大家做完 Lab 後精讀這三篇專欄！」

---

### Slide 13: 隨堂練習指引 (Hands-on Practice)
* **視覺焦點**：Ch5 實作指引任務與全系列結業致詞。
* **🎤 口播逐字稿**：
  > 「最後的隨堂任務，請大家按照指引：  
  > 第一，啟動本機 Docker Compose Lab；  
  > 第二，執行 `./k6/demos/ch5_prometheus_remote_write.sh`，將壓測數據即時推送到 Prometheus；  
  > 第三，打開 Grafana，搜尋剛才注入的 Commit Tag 標籤，親自建立屬於你的效能對齊儀表板！  
  > 非常感謝大家的參與，祝大家壓測順利，打造出堅不可摧的高效能系統！」

---

# Chapter 6: k6 x agent AI Agent Engineering
**建議錄製時長**：18 ~ 22 分鐘 (共 7 頁投影片)  
**章節主旨**：迎接 AI Agent 與 AI 編輯器時代，全面掌握 Grafana k6 原生子命令擴充套件（`k6 x agent`）。透過「自動安裝 11 個技能包」與「自動註冊 k6 MCP 伺服器」雙引擎架構，建立零配置、具備工程冪等性防護、支援 6 大編輯器與自癒驗證的現代化 AI 壓測工程工作流。

---

### Slide 1: 封面與全景導覽 ── 從 Test as Code 躍升至 AI Agent 自主工程
* **視覺焦點**：頂部【核心變革】Hero 卡片，中央三大支柱卡片（ENGINE 1: Bundled Skills（投影片標示 5 大，口播補充共 11 個）、ENGINE 2: 原生 k6 MCP 註冊、GOVERNANCE: 企業級安全與多環境適配），底部 `$ k6 x agent init --all` 一鍵起飛指令。
* **心智模型**：從手動編寫腳本與複雜 MCP 配置，邁向單一命令打通 AI 助手與本地 k6 工具鏈的自主工程範式。
* **🎤 口播逐字稿**：
  > 「哈囉大家好，歡迎來到《現代化效能測試實戰》的第六章！  
  > 進入 AI 時代，我們寫壓測腳本的方式正在經歷翻天覆地的變革。過去在 AI 編輯器裡配置 k6 工作流，需要手寫 MCP JSON、配置 Node.js 依賴，而且 AI 往往會因為缺乏上下文而產生過期的語法或造成記憶體洩漏的動態 URL。  
  > Grafana 官方為此推出了原生的 AI 子命令擴充套件——`k6 x agent`。  
  > 只需執行一次指令，它就能自動完成『安裝 5 大專業技能包』與『註冊原生 k6 MCP 伺服器』！  
  > 在這全新一章中，我們將帶大家拆解底層自動化雙引擎、工程冪等性守門員、常用 CLI 指令矩陣、11 個技能中精講 5 大核心技能，以及如何建立企業級的 AI 閉環自癒工作流！」

---

### Slide 2: 自動化雙引擎解密 ── 技能包注入與原生 MCP 註冊
* **視覺焦點**：左側「引擎一：自動安裝內建 AI 技能 (Bundled Skills)」四大清單項 vs 右側「引擎二：自動註冊 k6 MCP 伺服器 (Auto-Register MCP)」四大清單項；底端為【雙引擎協同】總結列。
* **心智模型**：雙引擎協同——技能包賦予 AI「領域專業知識與最佳實踐」，MCP 伺服器賦予 AI「語法預檢與本機執行能力」。
* **🎤 口播逐字稿**：
  > 「我們首先來看 `k6 x agent` 底層最關鍵的自動化雙引擎：  
  > 左側是『引擎一：自動安裝內建 AI 技能』：它會將官方維護的 `SKILL.md` 或 Cursor 的 `.mdc` Rules 寫入專屬目錄。當你在對話框中輸入『write a smoke test』，AI 助手不再瞎猜，而是精準載入官方規範，從根本杜絕字串拼接引發的 High Cardinality 記憶體爆炸，讓全團隊的 AI 生成標準完全齊平！  
  > 右側是『引擎二：自動註冊 k6 MCP 伺服器』：自動將 `k6 x mcp` 寫入編輯器的 MCP 設定檔。最亮眼的特點是它由 Go 原生編譯直接驅動，免裝 Node.js 或 npm！同時解鎖了 `validate_script`（以 1 VU 實際執行的冒煙預檢）與 `run_script`（本機執行壓測與自癒修復）兩大核心工具。手動 7 步配置縮短為 1 秒一鍵搞定！」

---

### Slide 3: 安全防護與冪等性機制 ── 企業級配置守門員
* **視覺焦點**：左側 3 大安全防護機制白底卡片（Owner Tag、--dry-run、Custom Guard）附專屬指令標籤；右側深色終端窗口展示【衝突防護決策邏輯】決策樹與 Owner Tag 規則標籤範例；底端為【核心價值】說明列。
* **心智模型**：工程級冪等性——非破壞性寫入，精確辨識機器生成區塊，絕不破壞工程師既有客製規則。
* **🎤 口播逐字稿**：
  > 「很多資深工程師會擔心：『自動寫入會不會把我們團隊既有的自訂規則覆蓋掉？』  
  > 這正是 `k6 x agent` 展現工程成熟度的地方！它引入了嚴格的『擁有者標籤 (Owner Tag)』機制。  
  > 大家看右側終端機範例，所有自動產生的規則頂部都會打上 `<!-- generated by k6 x agent -->` 標記。  
  > 當重複執行 `init` 時，系統會檢查標籤：如果檔案被手動修改過或標籤已移除，系統會判定為使用者客製代碼，自動觸發『略過保護』，絕對不會強行覆蓋！  
  > 此外，加上 `--dry-run` 可以預覽所有將變更的路徑，零副作用安心檢核；只有在需要升級官方最新規範時，顯式加上 `--force` 才會覆蓋。所有產出均在本地專案目錄內，完全符合 Git 版本控管審計最佳實踐！」

---

### Slide 4: 常用 CLI 指令速查與 6 大編輯器環境適配
* **視覺焦點**：左側深色終端機展示 6 條常用 CLI 指令（init 指定環境、init --all、--dry-run、--force、status、skills list）；右側 2×3 網格卡片（Cursor, Claude Code, GitHub Copilot, Codex CLI, OpenCode, Cline）；底端為【協同優勢】說明列。
* **心智模型**：以一致的命令行介面，無縫打通多種不同型態的 AI 工具，抹平跨職能團隊的開發環境孤島。
* **🎤 口播逐字稿**：
  > 「接下來看終端機操作有多麼簡單優雅。在專案根目錄下：  
  > 1. 為指定編輯器初始化：如 `k6 x agent init cursor` 或 `k6 x agent init claude-code`；  
  > 2. 跨職能團隊強烈推薦：`k6 x agent init --all`，一行指令同時把 Cursor、VS Code、Claude 等所有環境通通配好；  
  > 3. 執行前預檢：`k6 x agent init --dry-run cursor`，只看路徑不落地；  
  > 4. 強制升級重置：`k6 x agent init --force cursor`；  
  > 5. 隨時健康診斷：`k6 x agent status`，確認 MCP 與技能連線狀態；  
  > 6. 查看技能庫：`k6 x agent skills list`！  
  > 右側展示了原生支援的 6 大主流環境：Cursor、Claude Code、GitHub Copilot、OpenAI Codex CLI、OpenCode 以及 Cline。無論團隊偏好哪種工具，都能在幾秒鐘內擁有一致的壓測體驗！」

---

### Slide 5: 內建 5 大 AI 技能深度剖析 ── 專家級壓測工作流
* **視覺焦點**：雙欄對稱矩陣（2-Column Grid）：左欄 3 大核心生成技能（k6-test-planner 策略規劃、k6-load-test 生產負載、k6-smoke-test 極速冒煙）；右欄 2 大進階轉譯技能（k6-browser-test 前端渲染、k6-playwright-converter 轉譯）與【五大技能協同矩陣】卡片；底端為【技能協同】說明列。
* **心智模型**：AI 助手不僅能寫代碼，更是透過官方技能包具備了涵蓋策略、負載、冒煙、瀏覽器渲染到測試搬遷的全鏈路專家工作流。
* **🎤 口播逐字稿**：
  > 「執行了 init 之後，AI 助手究竟掌握了哪些專業能力？請看 5 大專業技能庫：  
  > 1. `k6-test-planner`【壓測策略規劃師】：輸入『plan tests』，自動分析 API 特徵、規劃流量模型、計算並發 VU 與爬坡階段，並設計合理的 P95 與 SLO 門檻；  
  > 2. `k6-load-test`【生產級負載壓測】：輸入『write a load test』，產出具備 stages 爬坡、arrival-rate 開放模型與 SharedArray 共享記憶體的標準代碼；  
  > 3. `k6-smoke-test`【極速冒煙檢驗】：輸入『write a smoke test』，以 1 到 2 個 VU 在 5 秒內快速驗證 API 連通性與契約，適合作為 CI/CD 門禁第一道防線；  
  > 4. `k6-browser-test`【前端真實渲染】：輸入『browser test』，以 k6/browser 驅動無頭 Chromium，量測 LCP/CLS/INP 等 Web Vitals，並注入 finally page.close() 軍規防護；  
  > 5. `k6-playwright-converter`【Playwright 轉譯】：輸入『convert Playwright script』，將現有 E2E 腳本一鍵轉譯為 k6 混合壓測腳本！全鏈路覆蓋，威力無窮！」

---

### Slide 6: 企業導入實作 Checklist ── AI 壓測工程化最佳實踐
* **視覺焦點**：4 大策略維度白底卡片（維度 1：配置治理與團隊協作；維度 2：AI 閉環自癒工程；維度 3：高基數記憶體爆炸防護；維度 4：官方生態系資源與持續演進），附帶 GitHub 開源專案與官方文檔超連結；底端為【最佳實踐】總結列。
* **心智模型**：將 AI 壓測從「個人玩具」提升為「企業級工程治理規範」。
* **🎤 口播逐字稿**：
  > 「擁有了強大工具後，企業團隊該如何安全落地？請看 Slide 6 的企業導入 Checklist：  
  > 維度一【配置治理】：將 `.cursor/rules` 納入 Git 版控，全團隊共享統一標準；敏感 Token 透過環境變數注入，並在 CI 中以 `status` 檢查連線；  
  > 維度二【AI 閉環自癒】：建立標準研發紀律：『Prompt 生成 $\rightarrow$ validate_script 預檢 $\rightarrow$ 1 VU 冒煙先驗 $\rightarrow$ 正式壓測』，讓 AI 讀取報錯自主修復；  
  > 維度三【高基數記憶體防護】：強制使用 `http.url` 標籤函數聚合動態 ID，嚴禁模板字串拼接，杜絕 Prometheus OOM；大量資料強制用 `SharedArray`；  
  > 維度四【官方生態系】：關注 GitHub `grafana/xk6-subcommand-agent` 開源專案與官方文檔，每季定期執行 `init --force` 同步技能包演進！」

---

### Slide 7: 隨堂實作練習指引 ── AI 輔助壓測三部曲
* **視覺焦點**：三大實戰任務水平卡片（任務一：一鍵初始化本地 AI 編輯器與狀態檢核；任務二：AI 逆向生成 QuickPizza 冒煙測試並閉環自癒；任務三：Playwright 登入測試無痛轉譯為 k6 混合壓測），包含任務目標、深色終端指令/Prompt 與清晰的綠色勾勾驗證標準；底端為【課程通關】總結列。
* **心智模型**：透過實作驗證從環境配置、API 冒煙自癒到 E2E 轉譯的三大核心能力。
* **🎤 口播逐字稿**：
  > 「最後，讓我們進入本章的隨堂實作！請大家打開筆電完成三大任務：  
  > 任務一：在專案根目錄執行 `k6 x agent init cursor`（或 `claude-code`），接著輸入 `k6 x agent status`，確認 11 個技能與 MCP 正常連線；  
  > 任務二：在 AI 對話窗輸入：『針對 QuickPizza 的 /api/pizza 端點撰寫 1 VU 冒煙測試腳本，包含 check 斷言與 http.url 標籤，並使用 validate_script 驗證』，親身體驗 AI 語法預檢與閉環跑通；  
  > 任務三：輸入：『將這段 Playwright 登入測試轉譯為 k6 browser 腳本，加入 finally page.close() 軍規保護，並設定 99:1 混合流量模型』，驗證前端瀏覽器真實採樣與後端高併發的完美協同！  
  > 完成這三項實戰，你已正式掌握現代化可觀測性與新一代 AI Agent 壓測工程的全套實戰技能！祝大家壓測順利，打造出堅如磐石的高效能系統！」

---

