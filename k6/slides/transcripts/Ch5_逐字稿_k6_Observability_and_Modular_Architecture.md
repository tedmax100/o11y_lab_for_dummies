# Chapter 5 完整錄課逐字稿：k6 Observability and Modular Architecture

> **課程名稱**：現代化效能測試實戰：從 k6 到雲原生可觀測性  
> **章節名稱**：Module 5: 生態系擴充與監控儀表板帶領 — 邁向企業級可觀測性  
> **預估時長**：15 ~ 20 分鐘  
> **配套簡報**：[`k6/slides/Ch5_k6_Observability_and_Modular_Architecture.pptx`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/slides/Ch5_k6_Observability_and_Modular_Architecture.pptx)  
> **配套演示**：  
> - [`k6/demos/ch5_dashboard_and_html_summary.js`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/ch5_dashboard_and_html_summary.js) (原生 Web 儀表板與 handleSummary 自訂報告)  
> - [`k6/demos/ch5_prometheus_remote_write.sh`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/ch5_prometheus_remote_write.sh) (Prometheus 時序推播直連與 Git Commit Tag)  
> - [`k6/demos/ch5_xk6_docker_build.sh`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/ch5_xk6_docker_build.sh) (Docker 確定性編譯自訂擴充引擎)

---

## 🎬 錄製前準備檢核清單 (Pre-recording Checklist)
- [ ] 簡報切換至 Chapter 5 封面（確認順序：Takeaway Checklist 已移至第 9 頁作為總結）。
- [ ] 瀏覽器預先開啟 Grafana 登入頁面：`http://localhost:3000`（若 Docker Compose 已啟動）。
- [ ] 終端機預先測試指令：`K6_WEB_DASHBOARD=true k6 run k6/demos/ch5_dashboard_and_html_summary.js`。
- [ ] 講述提示：突顯 Slide 8「雙十字準星對齊 CPU CFS Throttling」為全課高潮點。

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

* **畫面焦點**：xk6 齒輪引擎架構圖，展示 Go Native 程式碼如何跨越 Bridge，映射為前端 JavaScript 可調用的模組。
* **螢幕動作**：【動作：指引 Go 底層到 JS 的橋接流程】。

**【口播逐字稿】**：
> 「k6 的原生 HTTP 與 Browser 功能已經非常完整，但真實的企業架構往往更加複雜：  
> 如果你想直接對 Apache Kafka 的 Topic 生產並消費大量訊息呢？如果你想直接連線 PostgreSQL、MySQL 執行高併發的 Raw SQL 壓力測試呢？或者是你想測試 gRPC 雙向串流、MQTT 物聯網協議呢？  
> 
> 這就要引出 k6 生態系中最具擴展性的黑科技——**xk6 (eXtensible k6)**。  
> 大家請看這張架構解剖圖：  
> k6 的本質是一個用 Go 語言編寫的模組化引擎。Grafana 官方設計了一套 **Go-to-JS Bridge** 橋接架構。任何人都可以使用 Go 語言編寫底層模組，調用 Go 生態圈中無數個高效能的第三方庫；編譯時，xk6 會自動將這些 Go 的資料結構與方法，映射成 k6 JavaScript 腳本可以直接 `import` 的模組！  
> 這代表你既能享受 JavaScript 的動態與快速迭代，又能同時擁有 Go 語言的原生底層速度與網路通訊能力！」

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

### 【Slide 8 (原S9): Grafana 全視角對齊：CPU CFS Throttling 破除孤島】 (預估時間: 15:00 - 17:30)

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

### 【Slide 9 (原S2): 企業導入實作 Checklist (Takeaway)】 (預估時間: 17:30 - 19:15)

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

### 【Slide 10: 隨堂練習指引與全系列結語】 (預估時間: 19:15 - 21:00)

* **畫面焦點**：Ch5 實作任務清單（啟動 Docker Lab、執行 Prometheus 推播腳本、開啟 Grafana 查看自訂 Commit Tag）。
* **螢幕動作**：【動作：展示終端機腳本，向學員做深情而有力的結業致詞】。

**【口播逐字稿】**：
> 「最後一章的實作任務，請大家按照畫面指引：  
> 任務一：在終端機啟動本專案的 `docker compose up -d` 實驗室環境；  
> 任務二：執行我們為大家準備好的腳本：`./k6/demos/ch5_prometheus_remote_write.sh`，親眼看著壓測指標帶上你當前的 Git Commit Hash，即時推入 Prometheus；  
> 任務三：打開本機的 Grafana 儀表板，搜尋你剛剛注入的標籤，親自體驗一次現代化效能對齊的極致快感！  
> 
> 各位工程師夥伴，恭喜大家完整走完了五大章節的全部旅程！  
> 我們從最初的 k6 哲學出發，穿越了科學流量建模、征服了品質門禁、實踐了全鏈路混合壓測，最後抵達了現代化可觀測性的核心殿堂。效能工程不是一門理論，而是一門需要大家親自動手實踐的藝術。  
> 
> 非常榮幸能陪伴大家走過這趟充實的學習之旅。期待大家將這套方法論帶回你的工作崗位，守護每一次產品發布，打造出堅不可摧的高效能系統！我是講師，我們在未來的架構世界中，頂峰相見！」
