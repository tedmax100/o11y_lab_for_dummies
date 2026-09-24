# Chapter 4 完整錄課逐字稿：Precision k6 Hybrid Testing

> **課程名稱**：現代化效能測試實戰：從 k6 到雲原生可觀測性  
> **章節名稱**：Module 4: 邁向真實用戶體驗：流量錄製與 k6 Browser 混合壓測  
> **預估時長**：20 ~ 23 分鐘 (共 11 頁投影片)  
> **配套簡報**：[`k6/slides/Ch4_Precision_k6_Hybrid_Testing.pptx`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/slides/Ch4_Precision_k6_Hybrid_Testing.pptx)  
> **配套演示**：  
> - [`k6/demos/recording_cleaned.js`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/recording_cleaned.js) (HAR 錄製轉譯與三大清理法則實作)  
> - [`k6/demos/ch4_browser_quickpizza.js`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/ch4_browser_quickpizza.js) (Headless Chromium 操作與 Web Vitals 採集)  
> - [`k6/demos/ch4_hybrid_99_to_1.js`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/ch4_hybrid_99_to_1.js) (99:1 全鏈路混合壓測黃金配比)

---

## 🎬 錄製前準備檢核清單 (Pre-recording Checklist)
- [ ] 簡報切換至 Chapter 4 封面（投影片共 11 頁，包含最新第 9 頁現場壓測數據雙向會師）。
- [ ] 確認本機 Chromium / Google Chrome 安裝正常。
- [ ] 終端機預先測試指令：`k6 run k6/demos/recording_cleaned.js`（確認動態登入取得 Token 成功）。
- [ ] 終端機預先測試指令：`k6 run k6/demos/ch4_browser_quickpizza.js`（確認 QuickPizza 正常可連）。
- [ ] 終端機預先測試指令：`k6 run k6/demos/ch4_hybrid_99_to_1.js`（確認雙場景混合壓測正常）。
- [ ] 講述提示：突顯「99:1 黃金比例」如何幫企業省下 90% 雲端壓測機器費用。

---

## 🎞️ 錄製分段 Run Sheet

> **標記圖例**：✂️ 分段點（停錄、開新片段）· 🖥️ 切到終端機 · 📘 切到 Codelab · 🌐 切到瀏覽器 (Grafana / Dashboard) · 🎞️ 切回投影片
> **開錄前**：在專案根目錄執行 `./k6/demos/preflight.sh ch4`，全部 PASS 才開錄。

| 片段 | 內容 | 畫面 | 預估 | 備註 |
| :-- | :-- | :-- | :-: | :-- |
| **A 觀念** | Slide 1 → Slide 8 | 🎞️ 投影片 | 17 分 | Slide 3 若想示範 DevTools 錄製，**先錄好**再剪進來，不要現場錄 HAR |
| **B Demo** | Slide 9：`k6 run k6/demos/ch4_hybrid_99_to_1.js` | 🖥️ 終端機 | 2.5 分 | Chromium 第一次啟動慢，**preflight 已兼暖機**；實際數字會與投影片不同，口播用「大約」 |
| **A2 觀念** | Slide 10 起飛前 Checklist | 🎞️ 投影片 | 1.5 分 | |
| **C Codelab** | Slide 11 前半 → Codelab [#4 Chapter 4](https://tedmax100.github.io/o11y_lab_for_dummies/k6-performance-testing/index.html#4) 三個實作點 | 📘 Codelab | 3.5 分 | 本章實作分散在三個小節，照講稿跳 |
| **D 收尾** | Slide 11 後半：第五章預告 | 🎞️ 投影片 | 0.5 分 | |

---

## 🎙️ 逐頁口播逐字稿與操作指引

### 【Slide 1: 模組封面與四大核心柱石】 (預估時間: 00:00 - 02:00)

* **畫面焦點**：簡報封面「邁向真實用戶體驗：流量錄製與 k6 Browser 混合壓測」，左側 API 終端機對齊右側披薩網頁 DOM 渲染（標示 Core Web Vitals LCP 1.2s, FCP 0.8s）。
* **螢幕動作**：講師出鏡，點出當前微服務「只測後端、忽視前端」的盲區。

**【口播逐字稿】**：
> 「哈囉大家好，歡迎來到第四章！  
> 
> 在前面三個章節中，我們學會了如何寫出高併發的 API 壓測腳本、建立嚴格的 SLO 品質門禁。很多後端團隊做到這裡，就覺得自己已經無懈可擊了。  
> 但大家有沒有遇過這樣令人崩潰的情境：  
> 生產環境剛上線，使用者紛紛在社群網站抱怨：『你們網站好卡！按鈕點了沒反應！結帳頁面轉圈圈轉了 3 秒鐘！』  
> 後端工程師一查 Grafana 儀表板，卻一臉無辜地說：『怎麼可能？我們的 API P95 延遲才 45 毫秒，資料庫負載不到 30%，系統明明超順暢啊！』  
> 
> 這是現代軟體架構中最嚴重的觀測斷層！在現代充滿 React、Vue、Angular 的單頁應用（SPA）時代，後端 API 快，**絕對不等於使用者在螢幕前看到的畫面快！**  
> 如果使用者的瀏覽器被肥大的 JavaScript Bundle 塞滿、或者 DOM 渲染發生了昂貴的重排（Reflow），使用者的真實體驗依然是極度痛苦的。  
> 
> 傳統的壓測工具只能發送 HTTP 封包，根本看不到瀏覽器前端；而傳統的 UI 自動化工具（如 Selenium）又太過笨重，一台機器開 20 個瀏覽器就直接卡死，根本跑不了大規模壓測。  
> 今天，在第四章中，我們將透過 k6 原生內建的 **k6/browser**，徹底打破這道界線！我們會學習如何錄製 HAR 流量並清理腳本，最後打造出業界最頂尖的 **99:1 全鏈路混合壓測架構**。讓我們立刻展開旅程！」

---

### 【Slide 2 (原S3): 無痛產生複雜場景：HAR 轉換工作流】 (預估時間: 02:00 - 03:45)

* **畫面焦點**：四步管線圖：1. 錄製操作 (Record) $\rightarrow$ 2. 導出檔案 (Export .har) $\rightarrow$ 3. CLI 轉譯 (Convert) $\rightarrow$ 4. k6 腳本 (Script)。
* **螢幕動作**：【動作：滑鼠指引四步管線，強調 HAR 的概念】。

**【口播逐字稿】**：
> 「在實戰中，要手刻一個包含登入、搜尋、篩選、多層級驗證的完整使用者旅程，往往要手寫幾十支 API 的 Request Payload，非常耗時費力。  
> 因此，業界最常用的加速捷徑就是 **HAR 轉換工作流 (HAR Workflow)**。  
> 
> 什麼是 HAR？它的全名是 **HTTP Archive**，是現代所有瀏覽器（Chrome、Firefox、Edge）原生支援的一種標準 JSON 格式檔案。當你在瀏覽器開啟 Network 面板時，瀏覽器會把每一次網路交互的 Request Headers、Cookie、Query Parameters、Response Body 完整無缺地記錄在 HAR 檔案中。  
> 透過轉換工具，我們可以直接將這個 `.har` 檔案自動轉譯成初版的 k6 JavaScript 腳本，直接省去幾十個小時手動刻 API 的繁瑣苦工。  
> 
> 但我必須在進入實作前發出最高警示：**錄製只是起點，直接把轉譯出來的腳本拿去壓測，保證是一場災難！** 為什麼？我們看接下來的具體操作與避坑指南。」

---

### 【Slide 3 (原S4): 實作步驟 1：Chrome DevTools 網路操作錄製】 (預估時間: 03:45 - 06:00)

* **畫面焦點**：Chrome DevTools Network 面板截圖，以紅色圈出四大操作關鍵點：Incognito 模式、Preserve log、Clear、Export HAR。
* **螢幕動作**：【動作：依序圈選四個操作焦點，加重語氣提醒 Preserve log】。

**【口播逐字稿】**：
> 「打開 Chrome 瀏覽器錄製流量時，請大家務必在動手前嚴格落實這四個標準動作：  
> 
> 第一個動作：**永遠使用無痕視窗 (Incognito Window)**！  
> 這一點很多新手會忘記。如果你在一般視窗錄製，你瀏覽器裡安裝的密碼管理器、廣告攔截插件、Grammarly、翻譯外掛，會在背景瘋狂發送幾十個第三方請求。這些垃圾請求會全部混進 HAR 檔裡，污染你的壓測數據。  
> 
> 第二個動作：**務必勾選 Preserve log（保留日誌）**！  
> 這顆核彈級的勾選按鈕請一定要打勾！在真實的業務流程中，使用者在點擊『登入』或『送出訂單』時，頁面往往會發生 HTTP 302 重定向（Redirect）或是切換網址。如果你沒有勾選 Preserve log，瀏覽器跳轉的瞬間會自動清空 Network 面板，前面最重要的登入認證請求直接被沖刷得一乾二淨！  
> 
> 第三個動作：**清空日誌 (Clear Log)**：打開面板後，先點擊左上角的禁止符號清空所有初始化快取請求，再開始點擊頁面。  
> 
> 第四個動作：**匯出 HAR (Export HAR)**：依照真實使用者的節奏，完成一次完整的下單交易，最後點擊面板上的 Export 按鈕，儲存為 `recording.har`。」

---

### 【Slide 4 (原S5): 實作步驟 2：CLI 自動轉譯與 401 死資料陷阱】 (預估時間: 06:00 - 08:30)

* **畫面焦點**：終端機指令 `npx har-to-k6`，自動產生的腳本中寫死的 `Bearer eyJhbGci...` 上被打了一個大紅叉。
* **螢幕動作**：【動作：圈選寫死的 Token，語氣嚴肅提醒】。

**【口播逐字稿】**：
> 「拿到 HAR 檔案後，我們可以在終端機執行官方轉譯工具：  
> `npx har-to-k6 recording.har -o generated_script.js`  
> 工具會非常快速地幫我們產生出模組化的 k6 腳本。  
> 
> 這時候，很多工程師二話不說，立刻 `k6 run generated_script.js`，甚至開了 1,000 個 VU。  
> 然後神奇的事情發生了：測試跑得飛快，P95 延遲只要 5 毫秒，工程師開心地去慶功。  
> 結果隔天上線，伺服器瞬間掛掉！為什麼？  
> 
> 大家請看螢幕上這個大紅叉——這就是惡名昭彰的 **401 死資料陷阱 (The Stale Data Trap)**！  
> 錄製出來的腳本，裡面夾帶的 Authorization Token、Session ID、CSRF 防偽標籤，是你**在錄製當下那個瞬間**的靜態快照！  
> 這些 Token 通常只有幾分鐘的時效性。當你過了一小時拿去壓測，Token 早已過期失效！  
> 你的 1,000 個虛擬用戶送出的每一筆請求，在第一關 API Gateway 就直接被退回 401 Unauthorized！後端的資料庫與業務運算根本連一個指令都沒執行到！你以為很順，其實是系統直接把所有請求拒於門外！這就是為什麼錄製檔必須經過嚴格的加工與清理。」

---

### 【Slide 5 (原S6): 實作步驟 3：腳本清理與加工三大黃金法則】 (預估時間: 08:30 - 11:00)

* **畫面焦點**：三大法則卡片：1. 去靜態資源 (Don't load test Google) $\rightarrow$ 2. 動態關聯 (Correlation) $\rightarrow$ 3. 模組化封裝。
* **螢幕動作**：【動作：逐一介紹三大法則，加強「不要壓測 Google」的名言】。

**【口播逐字稿】**：
> 「要將一份死硬的錄製腳本改造成具備戰鬥力的生產級腳本，請牢記這三大黃金法則：  
> 
> 第一大法則：**剝離靜態資源與第三方服務——『Don't load test Google!』**  
> 這是壓測界的至理名言。在錄製檔裡，你往往會看到 Google Analytics、Facebook Pixel、外部字型 CDN、Sentry 的追蹤封包。請無情地把它們全部砍掉！你的目標是找出自家的系統瓶頸，而不是去對 Google 的伺服器發動 DDoS 攻擊！  
> 
> 第二大法則：**動態關聯 (Dynamic Correlation)**：  
> 把寫死的 Token 徹底替換掉！我們在 Chapter 1 學過的 `setup()` 階段在這裡大顯身手：在測試開始前發送一次正式的登入請求，動態抓取最新的 JWT Token，並在 VU 程式碼中透過 Header 動態注入；如果涉及訂單 ID，則透過前一個 API 的 Response JSON 動態萃取後，傳遞給下一個結帳 API。  
> 
> 第三大法則：**模組化封裝**：  
> 將零散的 API 呼叫包裝成具備語意的函式（例如 `login()`、`addToCart()`），並補上關鍵的 `check()` 軟斷言，確保業務邏輯百分之百正確執行。」

---

### 【Slide 6 (原S7): 兩個世界的對決：Protocol-Level vs Browser-Level】 (預估時間: 11:00 - 13:30)

* **畫面焦點**：對決圖：左側 Protocol-Level（API 協定級：超低成本、十萬併發、無前端 DOM），右側 Browser-Level（真實 Chromium、完整渲染、Core Web Vitals、資源昂貴）。
* **螢幕動作**：【動作：對比兩者的極致優點與致命缺點】。

**【口播逐字稿】**：
> 「在清理完協定級腳本後，我們現在把鏡頭拉高，來看這場效能工程的世紀對決：  
> 
> 左邊代表的是 **Protocol-Level（協定層測試）**：  
> 也就是我們前面一直在做的，發送純粹的 HTTP 請求。  
> 它的優點是**極致高效、極低成本**！因為它不需要解析 HTML，一台 4 核心伺服器就能輕鬆打出上萬併發，是測試後端資料庫與叢集負載的絕對主力。  
> 但它的缺點是：它對前端的真實渲染狀況**完全是個瞎子**！它不知道使用者等了多久才看到第一張圖片，也不知道按鈕有沒有因為 JavaScript 阻塞而按不下去。  
> 
> 右邊代表的是 **Browser-Level（瀏覽器層測試）**：  
> 它在背景啟動真實的 Headless Chromium 瀏覽器，完整下載 CSS、執行 JavaScript、渲染 DOM 樹，並精確測量 Google 定義的 **Core Web Vitals**——包含衡量首屏載入的 **LCP**、衡量排版穩定度的 **CLS**、以及衡量互動延遲的 **INP**。它能 100% 反映真實人眼的體驗！  
> 但它的致命痛點是什麼？**資源極度昂貴！** 一個 Chromium 處理序動輒消耗數百 MB 記憶體與大量 CPU，一台普通測試機跑個 20~30 個瀏覽器實例就已經是極限了，根本不可能用它來模擬千人或萬人併發！  
> 
> 難道我們只能在『高併發的大規模壓力』與『端到端的真實體驗』之間痛苦二選一嗎？答案是：小孩子才做選擇，成熟的架構師兩個都要！」

---

### 【Slide 7 (原S8): k6/browser 實戰語法與資源管理】 (預估時間: 13:30 - 16:00)

* **畫面焦點**：修正後的乾淨語法展示：`options.scenarios` 宣告 `browser: { type: 'chromium' }`，下方展示 `try-finally` 確保 `await page.close()`。
* **螢幕動作**：【動作：圈選 Chromium 宣告，隨後以最高亮標注 finally 區塊】。

**【口播逐字稿】**：
> 「在 k6 最新的版本中，原本需要外掛的瀏覽器模組已經全面原生內建為 `k6/browser`！  
> 
> 它的語法非常現代、優雅，與目前最流行的 Playwright 高度相容。大家看代碼：  
> 首先，我們在 scenario 的 options 中宣告：`browser: { type: 'chromium' }`；  
> 接著在非同步函式中，我們呼叫 `const page = await browser.newPage()` 開啟分頁；  
> 使用 `await page.goto('https://...')` 導航至網頁；  
> 透過現代化的 CSS 選擇器 `page.locator('button[name="checkout"]')` 定位按鈕並點擊。  
> 
> 但是，請大家把目光聚焦在第 35 行到第 40 行的 **try...finally** 區塊！  
> 這是我在審閱過無數企業腳本後，看過最多人犯的致命錯誤：**漏掉 await page.close()**！  
> 如果你的腳本在瀏覽器操作中發生異常跳出，而你沒有把它包在 finally 裡面執行 `page.close()`，這個 Chromium 分頁就會變成孤兒行程，永遠卡在記憶體中！當你的測試跑了 100 次迭代，伺服器背景就會殘留 100 個 Chrome 殭屍行程，直到系統當場凍結為止！務必確保每次操作後徹底釋放資源！  
> 
> 如果大家想深入了解 `k6/browser` 在真實電商系統中的全流程自動化（例如商品選購、購物車結帳、截圖留存與 `BrowserContext` 多帳號隔離），推薦研讀我在個人專欄發表的技術長文：《Grafana k6 瀏覽器測試》（`ganhua.wang/grafana-k6-browser`），裡面有非常詳盡的手把手步驟拆解，推薦大家搭配研讀！」

---

### 【Slide 8: 全鏈路混合壓測：99:1 黃金配比架構】 (預估時間: 15:30 - 17:30)

* **畫面焦點**：雙 Scenario 疊加架構圖：上方 99% Protocol Load 洪水般轟炸後端，下方 1% Browser Probe 探測針精準採樣真實用戶體驗。
* **螢幕動作**：【動作：講師手指分別劃過上方協定負載與下方瀏覽器探針，強調成本節省 90%】。

**【口播逐字稿】**：
> 「這就是本章最驕傲的核心架構設計——**99:1 全鏈路混合壓測黃金配比 (Golden Ratio Hybrid Architecture)**！  
> 
> 我們在同一個腳本中宣告兩個並行的 Scenarios：  
> **場景一：Protocol Load（99% 協定流量）**  
> 我們配置大量的 VU 或開放模型，用極低成本的 HTTP 請求對著後端 API 瘋狂施壓，把資料庫、快取與微服務叢集打到接近滿載的高壓狀態；  
> **場景二：Browser Probe（1% 瀏覽器探測針）**  
> 我們只需要配置 1 個或極少數的 Headless Chromium 實例，在背景負載建立起來之後優雅進場。這支探測針會模擬真實使用者打開瀏覽器、操作前端頁面，並在後端狂風暴雨的高負載環境下，精確採集出真實的 LCP 與 Web Vitals！  
> 
> 這樣一來，你用單單一台普通伺服器，就同時達成了『萬人規模的後端高壓』與『端到端的前端渲染體驗測量』！整體硬體成本直接省下 90% 以上！」

---

### 【Slide 9: 實戰成果：QuickPizza 99:1 全鏈路混合壓測現場】 (預估時間: 17:30 - 20:00)

* **畫面焦點**：左側展示協定層 280 次 API 請求與 P95 193ms 終端機卡片；右側展示真實 Chromium 探針採集的五大 Core Web Vitals 儀表（LCP 2.1s, FCP 2.1s, INP 24ms, TTFB 587.9ms, CLS 0.00），底部標注雙向會師核心洞察。
* **螢幕動作**：【動作：切換至終端機，執行 `k6 run k6/demos/ch4_hybrid_99_to_1.js`，現場展示雙線壓測與即時產出的真實指標】。

**【口播逐字稿】**：
> 「現在，讓我們立刻在終端機見證這個奇蹟！  
> ✂️ **【分段點 A → B】** 停錄；切到終端機開新片段。  
> 
> 【動作：切換至終端機】  
> 請大家看我的操作，我直接執行：  
> `k6 run k6/demos/ch4_hybrid_99_to_1.js`  
> 
> 【動作：手指指向終端機雙線進度】  
> 大家看控制台！背景的 `protocol_flood` 正在以每秒 27 次的速度狂轟 API；而在測試啟動 2 秒後，我們的無頭 Chromium 探針優雅進場，模擬真實使用者造訪 QuickPizza 商城、點擊推薦披薩按鈕！  
> 
> 🎞️ **【切回投影片 Slide 9】** 終端機的數字每次都會略有不同，接下來改用投影片上的數據講解。  
> 
> 測試完畢！請大家看簡報第 9 頁的真實執行數據：  
> 左邊是我們**後端協定層的戰果**：在 10 秒內打出了 **280 次 API 請求**，平均延遲僅 98ms，P95 延遲 193.65ms，錯誤率為漂亮的 **0.00%**，140 個業務斷言全部綠燈！證明後端微服務在滿載壓力下依然穩如泰山！  
> 
> 更精彩的是右邊——**前端真實瀏覽器的體驗數據**！  
> 在後端承受如此巨量 API 轟炸的同時，我們的 Chromium 探針測量出：  
> - **LCP (最大內容繪製)**：只有 **2.1 秒**，遠優於業界良好標準 2.5 秒！  
> - **INP (互動反應延遲)**：僅僅 **24 毫秒**，達到極速等級！代表使用者在點餐時完全感受不到任何卡頓！  
> - **TTFB (伺服器首位元)**：**587.9 毫秒**；**CLS 版面位移**：完美的 **0.00**！  
> 
> 請大家看底部的核心洞察：**『後端扛得住，前端流暢不卡頓！』**  
> 我們只用了一台普通筆電，沒有花費昂貴的雲端算力，就同時驗證了後端資料庫極限與前端真實人眼視覺體驗！這就是 99:1 混合架構帶給企業的極致價值！」

---

✂️ **【分段點 B → A2】** 停錄；切回投影片 Slide 10。

---

### 【Slide 10 (原S9): 壓測上線前防呆 Checklist】 (預估時間: 20:00 - 21:30)

* **畫面焦點**：起飛前檢核表卡片（錄製防呆、清理防呆、混合執行防呆）。
* **螢幕動作**：【動作：以嚴肅、專業的態度逐條叮嚀】。

**【口播逐字稿】**：
> 「在我們將這套武器應用到實戰之前，請大家把這張 **Flight Pre-check（起飛前防呆清單）** 印出來貼在螢幕旁邊。每一次發動大規模混合壓測前，請像民航機飛行員一樣逐項確認：  
> 
> 1. **錄製階段**：是否確實開啟無痕模式？是否勾選了 Preserve log 保留跨頁請求？  
> 2. **清理階段**：是否已剔除所有第三方 CDN 與 Google 追蹤碼？Token 是否已在 setup() 動態產生？關鍵 API 是否已補上狀態碼檢查？  
> 3. **混合執行階段**：瀏覽器 VU 是否嚴格控制在 10% 以內？腳本末端是否確實執行了 `await page.close()`？  
> 4. **資安與基礎設施**：是否已提前知會 SRE 與資安維運團隊？避免壓測流量被公司的 WAF 防火牆誤判為黑客攻擊而把你的 IP 封鎖！  
> 只要這份清單全數勾選通過，你的壓測就具備了最高級別的安全與專業度。」

---

### 【Slide 11 (原S10): 隨堂實作練習指引】 (預估時間: 21:30 - 23:00)

* **畫面焦點**：QuickPizza 實戰任務說明卡片，從錄製、轉譯、清理到升級 Hybrid 的四步練習路線圖。
* **螢幕動作**：【動作：展示 QuickPizza 網站與本章練習目標】。

**【口播逐字稿】**：
> 「現在輪到大家動手挑戰了！  
> 請大家開啟本章的實作專案：  
> 任務一：打開 `k6/demos/recording_cleaned.js`，體會如何用 `setup()` 破除 401 死資料陷阱；  
> 任務二：執行 `k6/demos/ch4_browser_quickpizza.js`，親眼看著 Chromium 在背景採集出 LCP 與 TTFB 前端指標；  
> 任務三：執行 `k6/demos/ch4_hybrid_99_to_1.js`，觀察多場景疊加時，背景協定流量與前端探針是如何協同運作的。  
> 
> 📘 **【切到 Codelab #4】** 念完三個任務後停在這裡，切到 Codelab 錄〈📘 Codelab 導覽講稿〉，錄完再 ✂️ 切回本頁唸下一段預告。  
> 
> 當我們掌握了前端與後端的全鏈路壓測數據後，最後一塊關鍵拼圖來了：  
> 這些寶貴的效能數據，該如何匯出成美觀的 HTML 報告分享給團隊？又該如何把數據推播進企業級的 Prometheus 與 Grafana 儀表板，與系統硬體指標進行雙時間軸對齊？  
> 歡迎進入第五章：《k6 Observability and Modular Architecture》。我們下節課見！」

---

## 📘 Codelab 導覽講稿（C 段，約 3.5 分鐘）

> **網址**：[https://tedmax100.github.io/o11y_lab_for_dummies/k6-performance-testing/index.html#4](https://tedmax100.github.io/o11y_lab_for_dummies/k6-performance-testing/index.html#4)
> **提示**：本章實作分散在三個小節，依序跳轉即可；左側目錄只到章節層級，請用捲動或 `Ctrl+F` 搜尋小節標題。

### C-1｜任務一：HAR 清理後的腳本

* **螢幕動作**：【📘 點左側「Chapter 4」，捲到「HAR 三大清理法則」→「程式碼對比：Raw HAR vs 清理後生產級腳本」】

**【口播逐字稿】**：
> 「Codelab 第 4 頁的實作不像前幾章集中在最後，而是跟著觀念走，我帶大家跳三個地方。
>
> 第一個在『HAR 三大清理法則』。這裡把 `recording_raw.js` 跟 `recording_cleaned.js` 左右對照：raw 版本裡有 Google Analytics、有寫死的 Bearer Token；清理後的版本把第三方請求刪掉、在 `setup()` 裡動態登入拿 Token。
> 【動作：捲到「實作演練：驗證清理後的 HAR 腳本」】
> 往下就是實作指令 `k6 run k6/demos/recording_cleaned.js`，下面附了真實的輸出，你跑完的 checks 應該要是 100%。如果你看到 401，恭喜你親身踩到了投影片講的死資料陷阱，回頭檢查 `setup()`。」

### C-2｜任務二：k6/browser 單元測試

* **螢幕動作**：【📘 捲到「k6 Browser：真實 Chromium 渲染與 Core Web Vitals」→ 圈紅色 Negative 框 →「瀏覽器單元測試實作」】

**【口播逐字稿】**：
> 「第二個在『k6 Browser』這一節。先看這個紅色框，**`page.close()` 一定要放在 `finally` 裡**，不然每次失敗都會留下一個殭屍 Chromium 程序，跑久了你的壓測機記憶體會被吃光。
> 下面的『瀏覽器單元測試實作』就是 `ch4_browser_quickpizza.js`。跑的時候注意兩件事：第一次啟動 Chromium 會比較慢，這是正常的；跑完請在輸出裡找 `browser_web_vital_lcp` 跟 `browser_web_vital_fcp`，這就是真實瀏覽器量到的前端指標。」

### C-3｜任務三：99:1 混合壓測

* **螢幕動作**：【📘 捲到「99:1 全鏈路混合壓測黃金架構」→「混合壓測多情境腳本架構」→「實作演練：執行 99:1 混合全鏈路壓測」】

**【口播逐字稿】**：
> 「第三個就是我剛剛 Demo 的 99:1。請先別急著跑，先看上面的『多情境腳本架構』：一個 `scenarios` 裡放兩個場景，`protocol_flood` 用 10 個 VU 轟 API，`browser_sample` 只放 1 個瀏覽器 VU 當探針，兩邊的 threshold 用 `{scenario:...}` 標籤分開管。
> 看懂了再跑 `k6 run k6/demos/ch4_hybrid_99_to_1.js`。你的數字不會跟我一模一樣，沒關係，重點是兩邊的門檻都要綠燈。
>
> 好，三個任務都完成，我們回到投影片。」

* **螢幕動作**：【🎞️ 切回投影片 Slide 11，唸「當我們掌握了前端與後端……」預告段】
