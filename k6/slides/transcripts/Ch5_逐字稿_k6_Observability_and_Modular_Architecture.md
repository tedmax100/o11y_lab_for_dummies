# Chapter 5 完整錄課逐字稿：k6 Observability and Modular Architecture

> **課程名稱**：現代化效能測試實戰：從 k6 到雲原生可觀測性  
> **章節名稱**：Module 5: 生態系擴充與監控儀表板帶領 — 邁向企業級可觀測性  
> **預估時長**：27 ~ 30 分鐘  
> **配套簡報**：[`k6/slides/Ch5_k6_Observability_and_Modular_Architecture.pptx`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/slides/Ch5_k6_Observability_and_Modular_Architecture.pptx)  
> **配套演示**：  
> - [`k6/demos/ch5_dashboard_and_html_summary.js`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/ch5_dashboard_and_html_summary.js) (原生 Web 儀表板與 handleSummary 自訂報告)  
> - [`k6/demos/ch5_prometheus_remote_write.sh`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/ch5_prometheus_remote_write.sh) (Prometheus 時序推播直連與 Git Commit Tag)  
> - [`k6/demos/ch5_xk6_docker_build.sh`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/ch5_xk6_docker_build.sh) (Docker 確定性編譯自訂擴充引擎)

---

## 🎬 錄製前準備檢核清單 (Pre-recording Checklist)
- [ ] 簡報切換至 Chapter 5 封面（共 11 頁投影片，確認順序：Takeaway Checklist 在第 9 頁，延伸閱讀在第 10 頁，隨堂練習在第 11 頁）。
- [ ] 瀏覽器預先開啟 Grafana 登入頁面：`http://localhost:3000`（若 Docker Compose 已啟動）。
- [ ] 終端機預先測試指令：`K6_WEB_DASHBOARD=true k6 run k6/demos/ch5_dashboard_and_html_summary.js`。
- [ ] 講述提示：突顯 Slide 11「雙十字準星對齊 CPU CFS Throttling」為全課高潮點，並在 Slide 13 隆重引薦講師技術專欄。

---

## 🎞️ 錄製分段 Run Sheet

> **標記圖例**：✂️ 分段點（停錄、開新片段）· 🖥️ 切到終端機 · 📘 切到 Codelab · 🌐 切到瀏覽器 (Grafana / Dashboard) · 🎞️ 切回投影片
> **開錄前**：在專案根目錄執行 `./k6/demos/preflight.sh ch5`，全部 PASS 才開錄。

| 片段 | 內容 | 畫面 | 預估 | 備註 |
| :-- | :-- | :-- | :-: | :-- |
| **A 觀念** | Slide 1 → Slide 2 | 🎞️ 投影片 | 3.5 分 | |
| **B1 Demo** | Web Dashboard：`K6_WEB_DASHBOARD=true k6 run …` → 🌐 `localhost:5665` | 🖥️ + 🌐 | 1.5 分 | 腳本跑 30 秒，Enter 後**立刻**切到瀏覽器 |
| **A2 觀念** | Slide 3 → Slide 6 | 🎞️ 投影片 | 9 分 | |
| **B2 Demo** | xk6：只秀 `bin/k6-custom version`，**不現場編譯** | 🖥️ 終端機 | 0.5 分 | 錄影前先跑 `ch5_xk6_docker_build.sh` |
| **A3 觀念** | Slide 7 | 🎞️ 投影片 | 2 分 | |
| **B3 Demo** | `./k6/demos/ch5_prometheus_remote_write.sh` → 🌐 Grafana `k6-live-metrics` | 🖥️ + 🌐 | 2.5 分 | **需 docker compose**；開錄前 10 分鐘先起，Grafana 才有曲線 |
| **A4 觀念** | Slide 8 → Slide 13 | 🎞️ 投影片 | 14 分 | Slide 8–10 儀表板與 Soak 判讀；Slide 11 是全課高潮 |
| **C Codelab** | Slide 14 前半 → Codelab [#5 Chapter 5](https://tedmax100.github.io/o11y_lab_for_dummies/k6-performance-testing/index.html#5) 實作演練 | 📘 Codelab | 3 分 | |
| **D 收尾** | Slide 14 後半：第六章預告 | 🎞️ 投影片 | 0.5 分 | |

---

## 🎙️ 逐頁口播逐字稿與操作指引

### 【Slide 1: 模組封面與全景預覽】 (預估時間: 00:00 - 01:45)

* **畫面焦點**：簡報封面「Module 5: 生態系擴充與監控儀表板帶領 — 邁向企業級可觀測性」，右側電路板連線串接 SQL、Kafka、HTTP 至儀表板與報告。
* **螢幕動作**：講師出鏡，點出壓測若停留在個人終端機就是「數據孤島」。

**【口播逐字稿】**：
> 「哈囉大家好，歡迎來到《現代化效能測試實戰》系列課程的最終章！  
> 
> 在前面四個章節中，我們學會了生命週期、掌握了科學流量建模、建立了 Exit Code 99 品質門禁，甚至征服了 99:1 的前端混合壓測。此時此刻，你已經具備了打造世界級壓測腳本的所有能力。  
> 
> 但在軟體工程的最後一哩路，我們必須面對一個非常現實的企業級命題：  
> 如果你的壓測數據，每次都只印在工程師本機的終端機黑色視窗裡，那這些數據就只是一座座彼此割裂的**『數據孤島』**！  
> 產品經理看不到、架構師無法做跨版本歷史對比、維運工程師也沒辦法把壓測數據與資料庫 CPU、記憶體的健康狀態放在同一個時間軸上交叉比對。  
> 
> 在這最後一章，我們要帶領大家把 k6 徹底接入當前雲原生最成熟的可觀測性生態圈——**Grafana、Prometheus 與 OpenTelemetry 宇宙**！  
> 我們將解鎖開箱即用的原生即時 Web 儀表板、學會用一行環境變數匯出獨立 HTML 靜態報告，深入剖析 xk6 擴充架構，並掌握如何用 Git Commit Tag 實現歷史效能回溯。讓我們一起進入這場可觀測性的巔峰之戰！」

---

### 【Slide 2 (原S3): 原生 Web Dashboard 即時監控】 (預估時間: 01:45 - 03:45)

* **畫面焦點**：展示終端機指令 `K6_WEB_DASHBOARD=true k6 run script.js`，預設位址 `http://127.0.0.1:5665`，搭配動態流暢的 Web Dashboard 介面截圖。
* **螢幕動作**：【動作：圈選環境變數指令與瀏覽器連接埠號碼】。

**【口播逐字稿】**：
> 「很多使用 k6 的工程師，第一步就急著去架設 Prometheus、設定 InfluxDB、裝 Grafana，結果光是配環境就花了一整天。  
> 其實很多人不知道：**k6 現在已經原生自帶了一個極為華麗的即時 Web 儀表板！**  
> 
> 大家看螢幕上的指令：  
> 你不需要安裝任何外部依賴、不需要開任何資料庫，只要在執行時加上一個環境變數：  
> `K6_WEB_DASHBOARD=true k6 run script.js`  
> 
> k6 就會在背景自動啟動一個極輕量的本機 Web 伺服器，預設監聽在 `http://127.0.0.1:5665`。  
> 打開瀏覽器，你就能看到即時動態刷新的折線圖！它會即時呈現當前的 RPS、P95 延遲、錯誤率，甚至會動態繪製出各個 HTTP 階段（connecting, waiting, receiving）的細部耗時拆解。當你在本地微調腳本或進行小規模探測時，這個內建儀表板就是你最高效的視覺化利器！」

---

✂️ **【分段點 A → B1】** 停錄；切到終端機。

> 🖥️ 「我們直接開起來看。  
> `K6_WEB_DASHBOARD=true k6 run k6/demos/ch5_dashboard_and_html_summary.js`  
> 【動作：按下 Enter，立刻切到 🌐 瀏覽器開 `http://127.0.0.1:5665`】  
> 大家看，RPS、P95、VU 數的曲線正在即時長出來。這支腳本跑 30 秒，我什麼監控系統都沒架，只有一個 k6 執行檔。」

✂️ **【分段點 B1 → A2】** 停錄；切回投影片 Slide 3。

---

### 【Slide 3 (原S4): 匯出靜態 HTML 測試報告：Port -1 退場技巧】 (預估時間: 03:45 - 06:00)

* **畫面焦點**：展示指令 `K6_WEB_DASHBOARD_PORT=-1` 與 `K6_WEB_DASHBOARD_EXPORT=report.html`，下方展示可獨立分享的靜態 HTML 報表。
* **螢幕動作**：【動作：加強口吻說明為什麼需要 Port=-1】。

**【口播逐字稿】**：
> 「剛才那個 Web Dashboard 非常好用，但在 CI/CD 環境中，我們卻會遇到一個頭痛的難題：  
> 在無人值守的 GitLab CI 或 GitHub Actions 容器裡，測試跑完之後，如果 Web Dashboard 的 HTTP 伺服器一直開著等待連線，整個 CI Job 就會永遠卡在背景、無法正常退出結束！  
> 
> 這時候，請大家務必學會這個在社群中被奉為神技的參數組合：  
> **設定 `K6_WEB_DASHBOARD_PORT=-1`，並指定 `K6_WEB_DASHBOARD_EXPORT=k6_report.html`！**  
> 
> 當連接埠設定為 `-1` 時，k6 會進入一個極為聰明的無頭模式（Headless Mode）：它在測試期間完全不開啟任何網路 Port，但在測試結束的那一個瞬間，它會將所有的動態折線圖、Thresholds 檢驗結果與統計指標，自動渲染並封裝成單一、獨立的靜態 HTML 檔案！  
> 這份 HTML 不需要任何外部伺服器，直接用瀏覽器點擊就能開啟。你可以把它作為 CI/CD 的 Build Artifact 上傳，隨時下載分享給產品團隊、前端團隊或是客戶，成為跨部門溝通效能表現的權威憑據！」

---

### 【Slide 4 (原S5): xk6 擴充機制解剖：Go-to-JS Bridge】 (預估時間: 06:00 - 08:30)

* **畫面焦點**：xk6 齒輪引擎架構圖，展示 Go Native 程式碼如何跨越 Bridge，映射為前端 JavaScript 可調用的模組；左下方特別標註講師實戰專欄卡片。
* **螢幕動作**：【動作：指引 Go 底層到 JS 的橋接流程，並點出左下方專欄卡片】。

**【口播逐字稿】**：
> 「k6 的原生 HTTP 與 Browser 功能已經非常完整，但真實的企業架構往往更加複雜：  
> 如果你想直接對 Apache Kafka 的 Topic 生產並消費大量訊息呢？如果你想直接連線 PostgreSQL、MySQL 執行高併發的 Raw SQL 壓力測試呢？或者是你想測試 gRPC 雙向串流、MQTT 物聯網協議呢？  
> 
> 這就要引出 k6 生態系中最具擴展性的黑科技——**xk6 (eXtensible k6)**。  
> 大家請看這張架構解剖圖：  
> k6 的本質是一個用 Go 語言編寫的模組化引擎。Grafana 官方設計了一套 **Go-to-JS Bridge** 橋接架構。任何人都可以使用 Go 語言編寫底層模組，調用 Go 生態圈中無數個高效能的第三方庫；編譯時，xk6 會自動將這些 Go 的資料結構與方法，映射成 k6 JavaScript 腳本可以直接 `import` 的模組！  
> 這代表你既能享受 JavaScript 的動態與快速迭代，又能同時擁有 Go 語言的原生底層速度與網路通訊能力！  
> 
> 大家看投影片左下角我特別標註的技術手記：如果大家想看一個真正生產級的 Go 擴充插件完整開發案例，推薦閱讀我在專欄寫的《Grafana xk6: 手把手從開發 k6 插件程式到編譯出 k6 插件》（`ganhua.wang/grafana-xk6`）。文章以 Web3 動態身份驗證為例，手把手帶大家實作 `RootModule`、`ModuleInstance` 與 `modules.Register`，開發出能高併發動態生成 OTP 一次性金鑰密碼的自訂模組，非常值得大家課後實作！」

---

### 【Slide 5 (原S6): 擴充套件雙引擎：JS vs Output Extensions】 (預估時間: 08:30 - 10:30)

* **畫面焦點**：兩大引擎分類圖：左側 JS Extensions（操作中間件與協定），右側 Output Extensions（時序數據匯出）。
* **螢幕動作**：【動作：對比兩種擴充機制的職責區分】。

**【口播逐字稿】**：
> 「在 xk6 生態系中，擴充套件主要被清晰地劃分為兩大引擎：  
> 
> 第一大引擎是 **JS Extensions（協定與邏輯擴充）**：  
> 它的職責是『擴充測試手段』。例如官方維護的 `xk6-sql` 讓你可以直接執行 `db.query()`；`xk6-kafka` 讓你直接對著 Kafka Broker 發送 Avro/JSON 訊息；還有針對 Redis、gRPC、Kubernetes API 的專用套件。如果你的壓測不只侷限在 REST API，這就是你的武器庫。  
> 
> 第二大引擎是 **Output Extensions（指標輸出擴充）**：  
> 它的職責是『擴充觀測維度』。預設情況下 k6 把指標印在終端機，但透過 Output 擴充，k6 可以將每秒產生的海量時序數據，即時推送到外部的企業級資料庫——例如直接打入 InfluxDB、Datadog、Amazon CloudWatch，或是發布至 Kafka 進行二次流式分析。  
> 搞清楚這兩大分類，你在架構自己的客製化壓測引擎時就能游刃有餘。」

---

### 【Slide 6 (原S7): xk6 build 與 Docker 確定性編譯】 (預估時間: 10:30 - 12:45)

* **畫面焦點**：展示 Docker 指令：`docker run --rm -it -u $(id -u):$(id -g) -v $(pwd):/xk6 grafana/xk6 build latest --with ...`，圈出關鍵掛載路徑 `-v $(pwd):/xk6`。
* **螢幕動作**：【動作：圈選 Docker 指令中的用戶權限與掛載路徑】。

**【口播逐字稿】**：
> 「很多同學一聽到『要編譯客製化二進位檔』，心裡就開始退縮：『天啊，我是不是要在我電腦上安裝 Go 語言開發環境、設定 GOPATH、處理一堆編譯依賴？』  
> 完全不需要！Grafana 官方為我們提供了最優雅的解法：**Docker 確定性編譯容器 (grafana/xk6)**。  
> 
> 大家請看螢幕上這行標準指令：  
> 我們直接調用 `grafana/xk6` 映像檔，加上 `--with github.com/grafana/xk6-sql`。  
> 在這裡，請大家務必把螢幕上的兩個參數看清楚，這是踩坑的血淚精華：  
> 第一，**`-u $(id -u):$(id -g)`**：這行非常重要！如果不加這行，容器產出的檔案會被 root 權限鎖死，你在宿主機甚至連刪除或執行都必須 sudo；  
> 第二，**`-v $(pwd):/xk6`**：注意冒號後面一定要是容器內的 `/xk6` 目錄！這樣容器內部編譯完成的自訂 `k6` 執行檔，才會精準地直接掉在你的本機當前目錄底下！  
> 
> 容器會自動在隔離環境完成所有的 Go 下載、鏈接與編譯，最後吐出一個體積小巧、原生整合了 SQL 擴充的單一執行檔。團隊中的每一個人、甚至 CI/CD 容器，都能在零配置的前提下產出百分之百一致的執行環境！」

---

✂️ **【分段點 A2 → B2】** 停錄；切到終端機（`bin/k6-custom` 需事先編譯好）。

> 🖥️ 「編譯要花幾分鐘，我已經先用剛才那行 Docker 指令編好了。我們直接驗收成果：  
> `./bin/k6-custom version`  
> 大家看輸出的 Extensions 區塊，多了一行 `xk6-sql`。一個執行檔，原生支援資料庫壓測。」

✂️ **【分段點 B2 → A3】** 停錄；切回投影片 Slide 7。

---

### 【Slide 7 (原S8): Prometheus Remote Write 與 Commit Tag 綁定】 (預估時間: 12:45 - 15:00)

* **畫面焦點**：展示指令 `k6 run -o experimental-prometheus-rw --tag commit_id=$(git rev-parse --short HEAD)`，展示資料流入 Prometheus 的架構圖。
* **螢幕動作**：【動作：切換至終端機執行 Prometheus Remote Write 腳本】。

**【口播逐字稿】**：
> 「在現代企業級可觀測性體系中，最強大的輸出模式就是 **Prometheus Remote Write（時序直連直寫）**！  
> 
> 請大家留意：在我們這套開源實驗室環境中，`docker-compose.yaml` 裡的 Prometheus 已經預先啟動了 `--web.enable-remote-write-receiver` 參數。這代表我們的 Prometheus 隨時準備接收外部推播進來的指標！  
> 
> 當我們執行 k6 時加上 `-o experimental-prometheus-rw`，k6 就會以高吞吐量的時序數據流，直接將每秒的 P95、錯誤率、請求數即時寫入 Prometheus。  
> 更關鍵的是畫面高亮圈選的這行參數：  
> `--tag commit_id=$(git rev-parse --short HEAD)`！  
> 
> 大家想想看這能帶來什麼威力？  
> 每次你在 CI/CD 執行壓測，我們動態將當前 Git 的短版 Commit Hash 作為標籤注入指標中。  
> 當你打開 Grafana 儀表板時，最上方會出現一個下拉選單：你可以點選『Commit abc1234』與『Commit def5678』，兩個不同版本的延遲波形圖立刻重疊在一起！前後兩個發布版本的效能退化（Regression）瞬間無所遁形！這才叫真正的專業級效能工程治理！」

---

✂️ **【分段點 A3 → B3】** 停錄；切到終端機（Prometheus / Grafana 需已啟動）。

> 🖥️ 「我們實際推一次。  
> `./k6/demos/ch5_prometheus_remote_write.sh`  
> 大家看最上面這幾行，腳本自動抓了我現在的 commit id 和 branch，當作標籤注入。  
> 【動作：跑完後切到 🌐 `http://localhost:3000/d/k6-live-metrics/`】  
> 打開 Grafana 的 k6 儀表板，右上角的下拉選單就是 `commit_id`。選我剛剛這個 commit，曲線就是剛才那次壓測。下次換一個 commit 再跑，兩條線疊在一起，退化一目了然。」

✂️ **【分段點 B3 → A4】** 停錄；切回投影片 Slide 8。

---

### 【Slide 8 (新增): 看懂儀表板：8 種經典曲線型態】 (預估時間: 15:00 - 17:30)

* **畫面焦點**：4×2 八張迷你折線圖卡片，每張下方有「看到／代表」兩行。副標：負載軸與反應軸疊在一起看。
* **螢幕動作**：【動作：依 ①→⑧ 順序逐張指出；講到 ② 時用游標停在 RPS 走平、P95 抬頭的交會點】。

**【口播逐字稿】**：
> 「數據已經全部串進 Grafana 了。但儀表板上滿滿的曲線，**你看得懂嗎？** Chapter 3 我們學了讀結尾摘要，摘要只告訴你『P95 等於 812 毫秒』；曲線才會告訴你『第 35 秒、負載到 45 RPS 的時候開始抬頭』。這個**拐點**才是容量規劃真正要的答案。  
> 
> 看儀表板只有一個心法：**永遠把負載軸和反應軸疊在一起看。** 負載軸是 VUs 和 RPS，反應軸是 P95、P99 和錯誤率。單看延遲上升沒有意義，因為負載本來就在加。  
> 
> 八種最常見的型態：  
> **第一種，健康線性。** VUs 和 RPS 同比例往上，P95 平平的，代表還有餘裕，繼續加壓。  
> **第二種，飽和平台，這是最重要的一張。** VUs 還在加，RPS 卻走平了，同一時間 P95 開始爬。還記得利特爾法則嗎？RPS 等於 VUs 除以回應時間，VU 變多但 RPS 不變，回應時間就一定變長了。**拐點當下的 RPS，就是你系統的容量。**  
> **第三種，崩潰懸崖。** P95 垂直暴衝，錯誤率同時竄升，RPS 反而往下掉，這是佇列溢出、逾時、連線池耗盡。  
> **第四種，尾巴張開。** P90、P95 都很平穩，只有 P99 越拉越開，代表少數請求受害，常見原因是 GC 停頓、鎖競爭、快取失效。  
> **第五種，緩慢爬坡。** 負載完全沒變，延遲卻隨時間慢慢往上，這是 Soak 測試最想抓到的訊號。進一步看 P50 有沒有一起爬：一起爬通常是記憶體或 GC 壓力；只有特定端點變慢，則是資料越積越多。  
> **第六種，週期鋸齒。** 固定間隔出現尖峰，去查排程任務、GC 週期、快取 TTL 同時到期，或自動擴縮容。  
> **第七種，錯誤率階梯。** 負載不變，錯誤率卻一階一階往上跳。階梯代表某種有限資源正在被用完，最常見的是資料庫連線池借出不還，每跳一階，池子就又少了幾條。  
> **第八種，吞吐下滑，但 P95 持平。** 這張最容易被誤判：延遲看起來沒事，RPS 卻一直掉，同時 blocked 在上升。還記得 Chapter 3 講過，blocked 和 connecting 不算在 duration 裡嗎？問題在連線建立層，而且第一個要排除的，是壓測機自己的連線有沒有用完。」

---

### 【Slide 9 (新增): Soak 判讀：趨勢比門檻重要】 (預估時間: 17:30 - 20:00)

* **畫面焦點**：左上「全程綠燈也可能失敗」折線圖（P95 緩升、門檻線未破）；左下三個判讀習慣；右側「k6 端的果 → 後端的因」對照表。
* **螢幕動作**：【動作：先指左上圖的斜率，再掃過左下三個習慣，最後逐列講右側對照表】。

**【口播逐字稿】**：
> 「剛才的 ⑤、⑦、⑧ 三種型態，都特別容易在 Soak 長跑中出現。Soak 有一個反直覺的地方：**全程綠燈，也可能是失敗的 Soak。**  
> 看左上這張圖：門檻是 P95 小於 800 毫秒，一個小時裡 P95 從 300 爬到 700，門檻一次都沒破。但照這個斜率，第八小時就會紅燈。所以 Soak 的門檻仍然是裁判，但真正要看的是**斜率**。  
> 
> 三個判讀習慣：第一，**量化斜率**。只取固定負載那一段，每 5 分鐘分一桶，算出每條線的趨勢，不要用眼睛估。第二，**一定要看恢復**。負載歸零後，系統有沒有回到基準？正常的系統幾分鐘內就恢復，有洩漏的系統不會，因為被佔住的資源不會自己還回來。結束後再跑一次 Smoke，如果還是慢，這就是你不需要任何後端數據就能拿出的硬證據。第三，**守住窗口**：負載取撐得住的六到八成，期間不部署、不重啟、不跑批次。  
> 
> 右邊這張表很重要：k6 端看到的都是『果』，根因要到後端去找。P95 緩升，去對記憶體和 GC；錯誤率階梯，去對資料庫連線池和 open files；RPS 下滑，去對連線數，也包括壓測機自己。我們的 Lab 沒有收集 runtime 指標，所以表上也列了替代方案，例如用 docker stats 定時記錄記憶體、查 pg_stat_activity 看連線數。  
> 這一頁的判讀思路參考了 iThome 鐵人賽一篇很棒的 Soak 文章，連結放在 Codelab 的延伸閱讀裡。」

---

### 【Slide 10 (新增): 儀表板判讀 4 步驟 SOP】 (預估時間: 20:00 - 22:00)

* **畫面焦點**：左側 4 個步驟卡片；右上 Web Dashboard 分頁地圖（Overview／Timings／Summary）；右下三個判讀陷阱。
* **螢幕動作**：【動作：先由上而下講完左側 4 步，再指右下陷阱卡；講到步驟 4 時預告「下一頁」】。

**【口播逐字稿】**：
> 「把這些型態串起來，就是這一頁的四步驟 SOP。  
> **第一步，確認壓力真的打出去了。** VUs 和 RPS 符合你的腳本設計嗎？有沒有 dropped_iterations？流量配比對不對？壓力沒打出去，後面都不用看。  
> **第二步，找出拐點時間。** 延遲或錯誤率第一次偏離平穩的那一刻，記下當下的 VUs 和 RPS。  
> **第三步，定位是哪一段變慢。** 切到 Web Dashboard 的 Timings 分頁：Waiting 漲是後端運算，Blocked、Connecting 漲是連線層，Receiving 漲是 Payload 太大。  
> **第四步，對齊後端指標找根因。** 把拐點時間帶進 Grafana，用共享十字準星對齊 CPU、記憶體、DB 連線池——這就是下一頁的破案現場。  
> 
> 右下角三個陷阱，我看過太多人踩：  
> 第一，Web Dashboard Overview 最上排那個 HTTP Request Duration 大數字，**是平均值，不是 P95**！延遲請看下方的 P95、P99 曲線。  
> 第二，**百分位數不能再取平均。** 如果用傳統的 Trend Stats 模式，k6 會先算好每條序列的 P95 再推過去，你在 Grafana 上對它取 avg()，得到的根本不是真正的 P95。所以本專案改用 Native Histogram：k6 推送完整分佈，Grafana 再用 `histogram_quantile()` 算出真正的 P95。  
> 第三，如果 RPS 走平，但後端 CPU 很閒、延遲也沒漲，**瓶頸可能是壓測機自己**，請去看 k6 那台主機的 CPU 和網卡。  
> 好，帶著這四個步驟，我們來看一個真實的破案現場。」

---

### 【Slide 11 (原S9): Grafana 全視角對齊：CPU CFS Throttling 破除孤島】 (預估時間: 22:00 - 24:30)

* **畫面焦點**：Grafana 雙十字準星（Shared Crosshair）對齊畫面：上方 k6 延遲突然飆高至 2 秒，下方 Kubernetes CPU CFS Throttling（CPU 限流）在同一秒狂飆至 80%。
* **螢幕動作**：【動作：以極度震撼、解密的口吻，指引雙時間軸在 14:02 分的完全對齊】。

**【口播逐字稿】**：
> 「各位觀眾，請看現在畫面上這張圖——這就是整門課程最精彩的封頂高光時刻！  
> 
> 這是一個真實的生產故障重現。大家看 Grafana 的共享十字準星（Shared Crosshair）：  
> 在下午 14:02 分的時候，上方由 k6 匯入的 API P95 延遲曲線，突然毫無徵兆地從平常健康的 40 毫秒，一路垂直暴衝到了 2.2 秒！  
> 
> 如果在過去傳統的壓測孤島模式下，後端工程師看到這張圖只會陷入無盡的痛苦：是資料庫 Slow Query？是代碼寫出死迴圈？還是網路交換機有問題？工程師必須花好幾個小時盲猜排查。  
> 
> 但是！請大家把目光往下移，看同一個時間軸底下、由 Node Exporter 採集的容器系統指標：  
> 在 14:02 分同一秒，這個微服務 Pod 的 **CPU CFS Throttling（容器配額強制限流）**，直接飆升到了 85%！  
> 
> 一秒破案！真兇瞬間抓到！根本不是程式碼有 Bug，而是 Kubernetes 的 Pod CPU Limit 設得太低，導致 Linux 核心在流量稍大時，強制對容器進行降頻凍結（Throttling）！  
> 當我們把壓測指標與基礎設施指標在 Grafana 上完美對齊時，所有的通靈猜測通通結束，效能瓶頸在第一時間化為確鑿的客觀證據！這就是將壓測接入現代可觀測性生態圈的終極魅力！」

---

### 【Slide 12 (原S2): 企業導入實作 Checklist (Takeaway)】 (預估時間: 24:30 - 26:15)

* **畫面焦點**：企業落地三大清單面向（本地開發與協作、CI/CD 整合、進階擴充與全域遙測）。
* **螢幕動作**：【動作：平穩回顧全課程重點，做最後的精華收斂】。

**【口播逐字稿】**：
> 「在全系列課程的尾聲，我為大家精心整理了這份 **Enterprise Implementation Checklist（企業導入實作清單）**，這也是大家帶回團隊落地時的行動準則：  
> 
> 第一個層次，**本地開發與團隊協作**：  
> 告別個人主觀判斷。本地測試習慣啟用 Web Dashboard；產出報告統一使用靜態 HTML 作為跨部門對齊的基準線；  
> 第二個層次，**CI/CD 流水線防線**：  
> 在自動化流水線中善用 `Port=-1` 確保流程乾淨退出；為關鍵端點配置 Tagged Thresholds，並使用 Exit Code 99 在門檻違規時自動中止部署；  
> 第三個層次，**進階擴充與全域觀測閉環**：  
> 善用 xk6 Docker 編譯擴充套件打破 HTTP 限制；透過 Prometheus Remote Write 直連推播時序指標，並以 Git Commit Tag 實現歷史版本追蹤；在 Grafana 建立整合儀表板，將業務延遲與伺服器資源雙軸對齊。  
> 只要團隊按照這三個層次循序漸進，你們的系統穩定度與交付品質將會迎來質的飛躍！」

---

### 【Slide 13: 推薦延伸閱讀 — 講師深度實戰專欄 (Author's Deep-Dive Articles)】 (預估時間: 26:15 - 28:45)

* **畫面焦點**：展示三大主題專欄卡片（xk6 模組擴充、前端混壓測試、全鏈路閉環），搭配專屬色彩邊框、關鍵亮點與專欄連結按鈕。
* **螢幕動作**：【動作：逐一指引三張技術卡片，以沉穩專業口吻介紹每篇文章解決的進階架構痛點】。

**【口播逐字稿】**：
> 「在進入最後的實操動手做之前，我特別為大家準備了這頁**『講師深度實戰專欄』**！  
> 這三篇文章是我在業界實戰與社群貢獻中，針對 k6 進階自訂與端到端前線戰場親手撰寫的深度解析。它們與本系列課程相輔相成，非常適合作為大家課後的進階秘笈：  
> 
> 第一篇，**模組擴充篇**：  
> 《Grafana xk6: 手把手從開發 k6 插件程式到編譯出 k6 插件》（`ganhua.wang/grafana-xk6`）。  
> 當官方內建的 HTTP、gRPC 無法滿足你公司的特殊需求（例如自訂的加密簽名演算法、Web3 身份驗證、或私有二進位通訊協定）時，這篇文章手把手帶你用 Go 語言寫出 `k6/x/otp` 插件，從模組架構、註冊生命週期到 Docker 確定性編譯，全面解鎖 xk6 的終極客製化潛能！  
> 
> 第二篇，**前端混壓篇**：  
> 《Grafana k6 瀏覽器測試》（`ganhua.wang/grafana-k6-browser`）。  
> 這篇文章深度探討我們在第四章學過的 `k6/browser`。它全面拆解了 Playwright 相容 API、展示如何利用 `BrowserContext` 在單一進程實現多用戶獨立 Session 與 Cookie 隔離，並以 OpenTelemetry Demo 購物車為例，完整走過加入購物車、表單送出、Web Vitals 採集與自動截圖保存錯誤現場的全流程！  
> 
> 第三篇，**全鏈路閉環篇**：  
> 《Getting Started with Grafana k6: Hands-on Practice》（`ganhua.wang/getting-started-with-grafana-k6-hands-on-practice`）。  
> 這篇文章從工程落地視角，教你如何用 `group` 與 `check` 撰寫結構化腳本，並示範如何將壓測指標對接 OpenTelemetry Collector，與微服務的分散式追蹤、日誌三位一體無縫整合，甚至無縫嵌入 GitLab CI 流水線建立自動化品質防線。  
> 
> 投影片上的卡片都可以直接點擊連結，大家在做完本章隨堂練習後，務必抽空將這三篇精讀一遍，保證能讓你的效能工程戰力再升級一個維度！」

---

### 【Slide 14: 隨堂練習指引與全系列結語】 (預估時間: 28:45 - 30:30)

* **畫面焦點**：Ch5 實作任務清單（啟動 Docker Lab、執行 Prometheus 推播腳本、開啟 Grafana 查看自訂 Commit Tag）。
* **螢幕動作**：【動作：展示終端機腳本，向學員做深情而有力的結業致詞】。

**【口播逐字稿】**：
> 「最後一章的實作任務，請大家按照畫面指引：  
> 任務一：在終端機啟動本專案的 `docker compose up -d` 實驗室環境；  
> 任務二：執行我們為大家準備好的腳本：`./k6/demos/ch5_prometheus_remote_write.sh`，親眼看著壓測指標帶上你當前的 Git Commit Hash，即時推入 Prometheus；  
> 任務三：打開本機的 Grafana 儀表板，搜尋你剛剛注入的標籤，親自體驗一次現代化效能對齊的極致快感！  
> 
> 📘 **【切到 Codelab #5】** 念完三個任務後停在這裡，切到 Codelab 錄〈📘 Codelab 導覽講稿〉，錄完再 ✂️ 切回本頁唸下一段。  
> 
> 到這裡，我們從 k6 哲學出發，穿越了科學流量建模、征服了品質門禁、實踐了全鏈路混合壓測，也讓壓測數據走出了終端機、進入了 Grafana。
>
> 但是回頭看，這五章裡最花時間的是什麼？是翻 API 文件、手寫腳本、一次又一次地修語法錯誤。如果這些苦工，可以交給一個懂 k6 最佳實踐、還能自己跑測試、自己修 bug 的 AI 助手呢？
>
> 歡迎進入最終章——第六章：《k6 x agent：AI 驅動的效能測試新紀元》。我們下一章見！」

---

## 📘 Codelab 導覽講稿（C 段，約 3 分鐘）

> **網址**：[https://tedmax100.github.io/o11y_lab_for_dummies/k6-performance-testing/index.html#5](https://tedmax100.github.io/o11y_lab_for_dummies/k6-performance-testing/index.html#5)
> **螢幕動作**：【📘 點左側「Chapter 5」，捲到小節「手把手實作演練：可觀測性全鏈路閉環」】

**【口播逐字稿】**：
> 「Codelab 第 5 頁，拉到『手把手實作演練：可觀測性全鏈路閉環』，這裡有四個實作，剛好對應今天的四個 Demo。
>
> 【動作：圈選實作 1】
> **實作 1**，Web Dashboard。腳本會跑 30 秒，Enter 按下去就趕快打開 5665 這個網址，跑完之後 dashboard 會跟著關掉。
>
> 【動作：圈選實作 2】
> **實作 2** 是 CI 用的：`K6_WEB_DASHBOARD_PORT=-1` 不開伺服器，只在結束時吐出一份 HTML。跑完請確認資料夾裡多了**三個檔案**：官方格式的 `offline_report.html`，還有 `handleSummary` 自己產的 `custom_report.html` 和 `summary.json`。
> 這裡提醒一個我自己踩過的坑：**如果測試跑太短，官方 HTML 報告會被跳過**，終端機會印一行 `report generation was skipped (not enough data)`。範例腳本已經調成 30 秒，你自己的腳本如果很短，記得加上 `K6_WEB_DASHBOARD_PERIOD=1s`。
>
> 【動作：圈選實作 3】
> **實作 3**，xk6 Docker 編譯。第一次要下載 Go 相依套件，大概要幾分鐘，請耐心等；編完用 `bin/k6-custom version` 驗收。
>
> 【動作：圈選實作 4，再往下指向 Grafana 網址與帳密】
> **實作 4**，Prometheus Remote Write。前提是 docker compose 已經起來。跑完打開這個 Grafana 網址，帳密是 admin / admin，右上角用 `commit_id` 篩選。建議你改一行程式、commit、再跑一次，就能在同一張圖上看到兩個版本的對比。
>
> 【動作：捲到下方「推薦延伸閱讀」停 2 秒】
> 最下面是我寫的三篇延伸文章，xk6 插件開發、k6 browser、還有一篇完整的上手實戰，想深入的同學可以慢慢看。好，我們回到投影片。」

* **螢幕動作**：【🎞️ 切回投影片 Slide 14，唸第六章預告段】
