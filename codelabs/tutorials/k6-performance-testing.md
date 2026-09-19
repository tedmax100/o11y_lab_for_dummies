author: 雷N
summary: Grafana k6 現代化效能測試與雲原生可觀測性實戰教學
id: k6-performance-testing
categories: k6,performance,observability,grafana,prometheus
environments: Web
status: Published
feedback link: https://github.com/tedmax100/o11y_lab_for_dummies/issues/new?template=codelabs-feedback.md&labels=codelabs,documentation

# 現代化效能測試實戰：Grafana k6 與雲原生可觀測性

## 課程簡介與導讀
Duration: 3

### 歡迎來到 Grafana k6 效能工程實戰！

![Grafana k6 Banner](assets/images/grafana-k6-banner.png)

在雲原生、微服務與 CI/CD 高速迭代的時代，傳統的效能測試往往面臨龐大瓶頸：笨重的 GUI 介面、難以維護的 XML 配置、昂貴的虛擬用戶資源開銷，以及與現代監控系統的嚴重脫節。

本教學為全系列 **5 大章節線上課程**的完整互動式實作指引，帶領你從零打造現代化、代碼化（Testing as Code）的企業級效能防線。

```
[Chapter 1: 核心哲學] ──> [Chapter 2: 流量建模] ──> [Chapter 3: 品質門禁] ──> [Chapter 4: 混合壓測] ──> [Chapter 5: 可觀測性閉環]
  - Test as Code           - 5大流量模式             - RED Method              - HAR 錄製轉譯            - 原生 Web Dashboard
  - Goroutine 架構         - 協調性漏測              - P95/P99 尾端延遲        - 401 死資料陷阱          - HTML 靜態報告 (Port=-1)
  - 4階段生命週期          - 開放模型 (Little's Law) - 4大自訂指標             - k6/browser Chromium     - xk6 Docker 確定性編譯
  - Group & Check          - SharedArray 記憶體優化  - Exit Code 99 卡關       - 99:1 全鏈路黃金架構     - Prometheus Remote Write
  - http.url 防指標爆炸    - dropped_iterations 告警 - abortOnFail 熔斷        - Flight Pre-check        - CPU CFS Throttling 對齊
```

### 你將學到什麼

- **Testing as Code**：告別 XML 點擊操作，使用標準 ES6 JavaScript 撰寫高維護性的測試腳本。
- **Go 語言並發威力**：理解 Goroutine 如何在單機上以極低記憶體驅動數萬並發用戶。
- **科學化流量建模**：破解「協調性漏測 (Coordinated Omission)」盲點，運用利特爾法則（Little's Law）配置開放模型。
- **精準品質門禁 (Quality Gates)**：設定 P95/P99 尾端延遲 SLO，以 **Exit Code 99** 在 CI/CD 中自動阻斷不良發布。
- **全鏈路混合壓測 (Hybrid Testing)**：打造 **99:1 黃金配比**，兼顧後端高壓與前端 Core Web Vitals (LCP/FID/CLS) 真實渲染體驗。
- **可觀測性閉環**：接入 Prometheus Remote Write 與 Grafana，實現 API 延遲突波與 Kubernetes CPU CFS Throttling 雙時間軸對齊除錯。

### 實驗環境要求

- **作業系統**：Linux、macOS 或 Windows (WSL2)
- **硬體建議**：至少 4 核心 CPU、8GB RAM
- **必要工具**：
  - `k6` CLI (v0.46.0+ 或更新版本)
  - `Docker` 與 `Docker Compose`
  - 現代 Chromium 核心瀏覽器（Google Chrome / Chromium）

Positive
: 本專案的所有配套演示腳本均已收錄於專案的 [`k6/demos/`](https://github.com/tedmax100/o11y_lab_for_dummies/tree/main/k6/demos) 目錄中，並通過本機環境完整實測！

---

## Chapter 1: k6 核心哲學與腳本基礎手把手
Duration: 15

### 傳統壓測痛點 vs Testing as Code

在過去十年間，Apache JMeter 是效能測試的代名詞。然而在現代 DevOps 與 GitOps 體系下，傳統工具帶來了三大致命痛點：

1. **配置維護地獄**：肥大且巢狀的 XML 格式無法進行有意義的 Git Diff 與 Code Review，團隊多人協作必定發生 Merge Conflict。
2. **開發體驗斷層**：後端與 SRE 工程師日常使用現代 IDE 與程式語言，卻被迫切換到老舊的 Java GUI 介面點擊拉節點，腳本淪為無人維護的技術債。
3. **CI/CD 自動化整合成本極高**：啟動耗時、資源沉重，難以在輕量 CI Runner 容器中快速執行與退出。

**Grafana k6** 的核心哲學是 **Testing as Code**：以純粹的 JavaScript/ES6 撰寫測試，享有現代模組化、Linter、自動補全與版本控制優勢。

- 🌐 **k6 官方網站 (Official Site)**：[https://grafana.com/docs/k6/latest/](https://grafana.com/docs/k6/latest/)（Grafana k6 官方網站與完整文件中心）
- 🐙 **GitHub 官方儲存庫 (Source Code)**：[https://github.com/grafana/k6](https://github.com/grafana/k6)（開源社群超過 25k+ Stars、純 Go 打造的高效能測試核心）

![k6 Testing as Code 核心架構與全鏈路閉環工作流](assets/images/grafana-k6-arch.png)

### 底層架構優勢：Goroutine vs 傳統執行緒

k6 雖然腳本寫的是 JavaScript，但其底層執行引擎完全由 **Go 語言** 編寫（內建 Goja JS Runtime）：

| 評估維度 | 傳統 JVM 工具 (JMeter) | Grafana k6 (Go 引擎) |
| :--- | :--- | :--- |
| **併發模型** | One OS Thread per Virtual User (VU) | Go Goroutine 輕量級協程 |
| **單 VU 記憶體開銷** | 1MB ~ 2MB (Thread Stack) | **僅約 2KB ~ 4KB** |
| **Context Switch 開銷** | 高 (由作業系統核心頻繁排程) | 極低 (由 Go Runtime 在使用者空間高效調度) |
| **單機併發能力** | 約 1,000 ~ 2,000 VUs 即達硬體瓶頸 | **單台普通機器可輕鬆驅動 30,000+ VUs** |

### k6 全平台安裝指南 (Installing k6)

k6 為單一獨立二進位檔（Single Binary），不依賴外部執行環境（無須預裝 Node.js 或 Go）。完整二進位發行檔可直接至 [k6 GitHub Releases](https://github.com/grafana/k6/releases) 取得，或依據您的作業系統選擇合適的套件管理員安裝：

#### 1. Linux 安裝

- **Debian / Ubuntu** (使用官方 GPG 金鑰與 APT 軟體庫)：
  ```bash
  sudo gpg -k
  sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
  echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
  sudo apt-get update
  sudo apt-get install k6
  ```

- **Fedora / CentOS / RHEL** (使用 DNF / YUM RPM 套件庫)：
  ```bash
  sudo dnf install https://dl.k6.io/rpm/repo.rpm
  sudo dnf install k6
  ```

- **Arch Linux**：
  ```bash
  sudo pacman -S k6
  ```

- **Snap** (跨發行版套件)：
  ```bash
  sudo snap install k6
  ```

#### 2. macOS 安裝 (Homebrew)

macOS 用戶強烈建議透過 Homebrew 安裝，原生支援 Apple Silicon (M1~M4, ARM64) 與 Intel (x86_64)：

```bash
brew install k6
```

#### 3. Windows 安裝

- **Windows 10/11 官方推薦 (Winget)**：
  ```powershell
  winget install k6 --source winget
  ```

- **Chocolatey**：
  ```powershell
  choco install k6
  ```

- **MSI 安裝檔**：前往 [k6 GitHub Releases](https://github.com/grafana/k6/releases) 下載最新的 `.msi` 雙擊安裝，安裝程式會自動將 k6 新增至系統環境變數 PATH。
- **WSL2**：強烈建議在 Windows 上的開發者搭配 WSL2 (Ubuntu)，並依照 Linux Debian/Ubuntu 流程安裝，享有與雲端環境完全一致的壓測效能。

#### 4. Docker 容器化執行（免本機安裝）

在 CI/CD Runner 或不希望變更本機系統的環境中，可直接拉取官方 Docker 映像檔：

```bash
# 透過管道 (Stdin) 直接執行腳本
docker run --rm -i grafana/k6 run - <script.js

# 或掛載當前專案目錄並執行
docker run --rm -v $(pwd):/app -w /app grafana/k6 run script.js
```

#### 5. 驗證安裝

打開終端機，執行以下指令驗證安裝成果：

```bash
k6 version
```

輸出範例：`k6 v0.50.0 (go1.22.1, linux/amd64)`，確認出現版本資訊即代表安裝成功！

---

### k6 CLI x AI 現代化工作流 (Configure AI Assistant & MCP)

隨著生成式 AI 技術成熟，現代效能工程不僅走向代碼化（Testing as Code），更邁入 **AI 智慧賦能時代**。Grafana k6 官方正式推出基於 **Model Context Protocol (MCP)** 的整合方案，將 k6 CLI 與現代 AI 助手（Cursor、Claude Desktop、VS Code Copilot、Antigravity 等）無縫串接。

#### 1. 什麼是 k6 MCP Server？

Model Context Protocol (MCP) 是一項開放協議，允許大語言模型安全地存取本地工具與上下文。Grafana 官方發布了 `@grafana/k6-mcp-server`，讓 AI 助手具備以下能力：
- 取得官方最新 k6 API 與最佳實踐文檔。
- 在代碼編輯器中自動語法靜態檢驗。
- 直接驅動 k6 執行壓測並即時解析測試指標。

#### 2. 快速設定 k6 MCP Server

在支援 MCP 的工具（如 Cursor、Claude Desktop 或 VS Code 擴充套件）的設定檔中，加入以下設定即可一鍵啟用（無需手動下載二進位檔，`npx` 會自動拉取執行）：

```json
{
  "mcpServers": {
    "k6": {
      "command": "npx",
      "args": [
        "-y",
        "@grafana/k6-mcp-server"
      ]
    }
  }
}
```

> 如果環境中未安裝 Node.js，亦可前往官方 Releases 下載對應 OS 的獨立編譯版本並直接配置執行路徑。

#### 3. MCP 工具庫 (Tools)、提示詞 (Prompts) 與資源 (Resources)

k6 MCP Server 為 AI 助手賦予了三類關鍵能力：

- **工具 (Tools)**：
  - `run_test`：允許 AI 助手直接在本機驅動 k6 執行指定的測試腳本，自動獲取並結構化解析 RPS、P95 延遲、錯誤碼等指標反饋。
  - `validate_script`：在執行壓測前，由底層 AST 解析器對腳本進行靜態檢查，提早揪出 ES6 模組引用錯誤、生命週期階段錯置或 Thresholds 宣告不合規。
  - `get_documentation`：動態向 k6 官方文檔庫檢索最新 API 規格（如 `k6/browser`、`k6/experimental/redis` 等），確保 AI 產出的代碼絕不幻覺過時的 API。
- **提示詞模板 (Prompts)**：
  - 內建產生常規負載測試（依據特定 RPS 與坡度自動編寫腳本）。
  - 將 OpenAPI/Swagger 規格或瀏覽器 HAR 錄製檔轉譯為 k6 測試情境。
  - 診斷效能門禁違規（分析為何延遲超過閾值並給出具體優化建議）。
- **資源 (Resources)**：即時提供官方範例庫、常用設定片段與各行業流量建模的最佳實踐模板。

#### 4. 使用 AI Agent 自主逆向生成完整測試套件 (Bootstrap with k6 x Agent)

以往為一套複雜的後端系統撰寫效能測試需要耗費數天：開發者必須逐一閱讀 API 文件、手寫身分驗證邏輯、設計隨機資料池並校驗斷言。

利用 **Bootstrap with k6 x Agent** 工作流，AI 代理能自主完成全套工程交付：

```
[專案代碼/OpenAPI/HAR 規格] ──> [AI Agent 自主解析] ──> [生成全情境壓測腳本] ──> [validate_script + run_test (1 VU 冒煙)] ──> [自動自癒微調] ──> [生產就緒測試套件]
```

1. **資產自動探索 (Asset Discovery)**：Agent 讀取專案中的 `openapi.yaml` 或前端網路請求錄製檔（`.har`）。
2. **情境自主建模 (Autonomous Modeling)**：自動拆解出 Smoke、Load、Stress 測試情境，並配置合理的 P95 閾值門禁。
3. **閉環驗證與自癒 (Self-Healing Loop)**：Agent 自動調用 `validate_script` 校驗語法，並以 1 個 VU 發動 `run_test` 驗證真實 API 通訊；一旦遇到 401 Unauthorized 或 422 Unprocessable Entity，Agent 自行修正請求標頭與 Body 格式，直到全數 Pass！

Positive
: 透過 k6 CLI 與 AI 助手的深度融合，效能測試從「少數效能專家的專屬重擔」，變成了「每位開發者在 IDE 內隨手即可生成的日常防線」！

---

### k6 四階段生命週期 (Lifecycle)

理解 k6 的生命週期是撰寫正確腳本的第一步：

```javascript
// 1. Init Context (初始化階段：每個 VU 載入時執行一次，嚴禁在此發送 HTTP 請求！)
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = { vus: 10, duration: '30s' };

// 2. Setup Context (全域準備階段：壓測開始前全域只跑一次)
export function setup() {
  const token = 'login-and-fetch-global-token';
  return { authToken: token };
}

// 3. VU Code / Default (預設執行階段：每個 VU 在測試期間依頻率反覆迴圈執行)
export default function (data) {
  const res = http.get('https://test.k6.io', {
    headers: { Authorization: `Bearer ${data.authToken}` },
  });
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}

// 4. Teardown Context (全域收尾階段：所有 VU 結束後全域只跑一次)
export function teardown(data) {
  console.log('壓測結束，清理測試資料...');
}
```

---

### k6 執行設定與常用 Options 全指南 (Configuration & Options Guide)

在上述生命週期範例中，我們看見了 `export const options = { vus: 10, duration: '30s' };`。
**Options（執行選項）** 是 k6 壓測的大腦與調度中樞，用來精準定義壓測的規模、時間、行為特徵、品質門檻與輸出目標。

官方文檔深入導讀：
- 官方設定指引教學：[How to set k6 options](https://grafana.com/docs/k6/latest/using-k6/k6-options/how-to/)
- 官方完整 Options 參考手冊：[k6 options reference](https://grafana.com/docs/k6/latest/using-k6/k6-options/reference/)

#### 1. 設定 Options 的三種主要途徑

以最常見的「**10 個虛擬使用者 (VUs)** 且**執行 30 秒 (Duration)**」為例，k6 提供了三種靈活的宣告途徑：

##### (1) 腳本內宣告 (In-script Options)
直接在 JavaScript 檔案頂層匯出名為 `options` 的物件。這是官方最推薦的標準作法（Testing as Code），可將測試規格直接納入 Git 版本控管：

```javascript
export const options = {
  vus: 10,
  duration: '30s',
};

export default function () {
  // 測試邏輯...
}
```

##### (2) 命令列旗標 (CLI Flags)
在執行 `k6 run` 時透過命令列參數直接傳入：

```bash
k6 run --vus 10 --duration 30s script.js
```

命令列旗標提供了最高靈活度，特別適合：
- 本機除錯時快速以 `--vus 1 --duration 5s` 進行冒煙驗證。
- CI/CD Pipeline 依據當前部署環境（如 Dev, Staging, Prod）動態傳入不同規模的壓測參數。

##### (3) 環境變數 (Environment Variables)
所有 k6 Options 都有對應的全大寫前綴 `K6_` 環境變數：

```bash
K6_VUS=10 K6_DURATION=30s k6 run script.js
```

非常適用於 Docker 容器執行、Kubernetes Job / Pod 宣告、或 CI/CD 的 Secret / ConfigMap 注入。

---

#### 2. Options 四層設定優先級 (Precedence Order)

當同一個 Option 同時在多處被設定時，k6 依照嚴格的**覆蓋原則（由高至低）**進行解析：

```
[1. CLI Flags (最高)] ──> [2. Environment Variables] ──> [3. In-script options] ──> [4. Default Values (最低)]
```

| 優先層級 | 設定方式 | 範例 | 說明 |
| :--- | :--- | :--- | :--- |
| **1 (最高)** | **CLI Flags** | `k6 run --vus 50` | 命令列傳入的旗標具備絕對最高覆蓋權 |
| **2 (次高)** | **Environment Variables** | `export K6_VUS=30` | 系統環境變數覆蓋腳本內建值 |
| **3 (中等)** | **In-script `options`** | `export const options = { vus: 10 }` | 腳本代碼內部宣告的值 |
| **4 (最低)** | **Default Values** | `vus: 1`, `iterations: 1` | 若完全未指定，k6 採用的預設安全值 |

Positive
: **實戰技巧**：這種階層優先級讓團隊可以將標準負載腳本提交到 Git（例如腳本內寫 `vus: 100, duration: '10m'`），但在本地開發或 CI 冒煙檢查時，只需加上 `k6 run --vus 1 -i 1 script.js` 即可瞬間覆蓋，完全不用改動程式碼！

---

#### 3. 常用 Options 實用分類速查表

在實際工程專案中，除了 `--vus` 與 `--duration` 之外，以下是業界最常用的 Options 清單：

##### A. 負載規模與時間控制 (Workload & Duration)

| Option 屬性 | CLI 旗標 | 型態 / 範例 | 說明與典型場景 |
| :--- | :--- | :--- | :--- |
| `vus` | `--vus`, `-u` | 數值（如 `10`） | **虛擬使用者數 (Virtual Users)**。同時並行執行的 VU 總數。 |
| `duration` | `--duration`, `-d` | 字串（如 `'30s'`, `'5m'`, `'1h'`） | **測試持續時間**。所有 VU 在此時間內反覆迴圈執行。 |
| `iterations` | `--iterations`, `-i` | 數值（如 `100`） | **總迭代次數**。所有 VU 累計完成指定次數後即結束（適合冒煙或批次測試）。 |
| `stages` | `--stage` | 陣列（如 `[{ duration: '1m', target: 50 }]`） | **階梯式負載**。依時間動態調整 VU 數量，實現漸進爬坡 (Ramp-up) 與降溫 (Ramp-down)。 |
| `scenarios` | *(無單一旗標)* | 物件 | **進階多情境調度**。支援不同 Executor（如按固定抵達率 RPS、或不同執行函式並行）。 |

##### B. 品質門禁與 SLA 判定 (Quality Gates & Thresholds)

| Option 屬性 | CLI 旗標 | 型態 / 範例 | 說明與典型場景 |
| :--- | :--- | :--- | :--- |
| `thresholds` | *(無單一旗標)* | 物件 | **宣告式 SLA/SLO 門檻**。例如 `http_req_duration: ['p(95)<200']`（95% 請求需在 200ms 內完成）。若失敗則 k6 退出碼非 0，直接熔斷 CI/CD。 |

##### C. 網路協定與連線行為 (Network & Protocols)

| Option 屬性 | CLI 旗標 | 型態 / 範例 | 說明與典型場景 |
| :--- | :--- | :--- | :--- |
| `noConnectionReuse` | `--no-connection-reuse` | 布林（預設 `false`） | **停用 HTTP 連線複用 (Keep-Alive)**。每次請求強制建立全新 TCP/TLS 握手，考驗伺服器高頻建連能力。 |
| `insecureSkipTLSVerify` | `--insecure-skip-tls-verify` | 布林（預設 `false`） | **跳過 SSL 憑證檢查**。在開發或 Staging 環境遇到自簽憑證或無效 HTTPS 時必備。 |
| `rps` | `--rps` | 數值（如 `500`） | **每秒最大請求數上限**。限制全域每秒發出的 HTTP 請求，防止壓測本機把受測系統徹底癱瘓。 |
| `userAgent` | `--user-agent` | 字串（如 `'k6-load-tester/1.0'`） | **自訂 User-Agent**。方便受測後端透過存取日誌過濾並辨識壓測流量。 |

##### D. 觀察性、除錯與報表輸出 (Observability & Debugging)

| Option 屬性 | CLI 旗標 | 型態 / 範例 | 說明與典型場景 |
| :--- | :--- | :--- | :--- |
| `httpDebug` | `--http-debug`, `--http-debug="full"` | 字串 / 布林 | **HTTP 詳細除錯模式**。在終端機完整印出所有發送與接收的 HTTP Header 及 Body，排查 4xx/5xx 首選。 |
| `summaryExport` | `--summary-export=summary.json` | 檔案路徑 | **匯出結構化測試摘要**。將最終統計數據存為 JSON，供 CI/CD Pipeline 解析或發送 Slack 通報。 |
| `tags` | `--tag key=value` | 物件 / 鍵值對 | **全域標籤**。為本次測試的所有指標打上維度標籤（如 `env: staging`, `service: payment`）。 |
| *(匯出串流)* | `-o`, `--out <plugin>` | 外掛名稱 / URL | **指標串流外銷**。將即時時序指標直接推送至 Prometheus、InfluxDB、Datadog 或 Grafana Cloud。 |

---

### 軟斷言 check() 與避免高基數爆炸

- **check() 是軟斷言**：與單元測試中斷執行的 `assert` 不同，k6 的 `check()` 失敗時**不會停止測試**，而是記錄成功率。這確保了在大規模壓測中能精確統計出 99.9% 成功率，而非因偶發錯誤中途夭折。
- **避免高基數維度爆炸 (High Cardinality)**：嚴禁寫出 `http.get('/api/users/' + userId)`。當萬人併發產生數萬個不同 URL 時，Prometheus/Grafana 會因時序暴增而 OOM 崩潰！正確寫法是使用模板標籤函式：``http.url`https://api.example.com/users/${userId}` ``，指標將自動聚合在同一名稱下。

### 實作演練：執行第一支生命週期測試與 CLI Options 實戰

![k6 CLI 終端實機執行展示 (3 大情境動態輪播)](assets/images/k6-ch1-cli-options.gif)

打開終端機，依序執行專案為您準備好的 3 組實戰指令，親身體驗生命週期、CLI 覆蓋與通訊除錯：

#### 步驟 1：依照腳本內預設 Options 執行 (vus: 2, iterations: 4)

體驗 k6 標準四階段生命週期的執行次序（Init ➔ Setup ➔ VU Code ➔ Teardown）與 100% 宣告式斷言：

```bash
k6 run k6/demos/ch1_lifecycle_and_checks.js
```

![DEMO 1: 腳本預設生命週期執行成果](assets/images/k6-ch1-cmd1-lifecycle.png)

#### 步驟 2：實踐 CLI 覆蓋技巧：動態改為 10 個 VU 執行 30 秒

透過 CLI 旗標瞬間覆蓋程式碼內部設定，同時調度 10 條 Goroutine 協程發動並行負載加壓：

```bash
k6 run --vus 10 --duration 30s k6/demos/ch1_lifecycle_and_checks.js
```

![DEMO 2: CLI Options 覆蓋實戰成果](assets/images/k6-ch1-cmd2-override.png)

#### 步驟 3：搭配 HTTP 除錯旗標觀察底層通訊 Header 與 Body (單一 VU 冒煙模式)

加上 `--http-debug` 旗標透視底層 HTTP Request（包含 Mock JWT Token）與 200 OK Response 封包細節：

```bash
k6 run --vus 1 --iterations 1 --http-debug k6/demos/ch1_lifecycle_and_checks.js
```

![DEMO 3: HTTP 除錯封包透視成果](assets/images/k6-ch1-cmd3-httpdebug.png)

Positive
: **實踐心得**：觀察終端機輸出，確認 Init、Setup、VU Code 與 Teardown 的執行順序！體驗 CLI 參數如何即時覆蓋腳本預設值，以及 `--http-debug` 如何在毫秒間抓出通訊異常。

---

## Chapter 2: 科學化流量建模與協調性漏測破解
Duration: 25

### 流量建模核心哲學：拒絕「盲測」

在現代效能工程中，最危險的迷思就是「**隨便開 100 個 VU，跑跑看系統會不會死**」。這種毫無章法的盲測存在三重致命缺陷：
1. **無法反映真實使用者行為**：真實世界的使用者並不會在同一個時間步調一致地發起請求，更不會在伺服器卡頓時集體暫停等待。
2. **掩蓋架構瓶頸**：盲目加壓只會引發無效的連線堆疊或本機埠耗盡，無法精確定位瓶頸究竟是在資料庫連線池、執行緒排隊、還是記憶體垃圾回收 (GC)。
3. **產出誤導性的 SLA 結論**：未經流量特徵調校的數據無法指導生產環境的 Kubernetes HPA（水平自動擴展）設定與容量規劃。

真正的**科學化流量建模 (Scientific Traffic Modeling)** 必須緊扣三大核心維度：
- **併發用戶數 (Virtual Users, VU)** vs **請求抵達率 (Arrival Rate, RPS)** 的本質解耦。
- **思考時間 (Think Time)** 與 **使用者會話週期 (User Session Lifecycle)** 的擬真分佈。
- **流量波形 (Traffic Waveforms)**：依據業務節奏設計階梯爬坡、穩態高原、突發尖峰與耐久浸泡。

---

### 五大經典壓測模式深度技術解剖

在撰寫 k6 測試前，必須先依據業務場景嚴格定義流量波形。以下解構業界最關鍵的五大經典壓測模式：

#### 1. Smoke Testing（冒煙測試 / 腳本驗證）

- **業務目標**：極小負載下的功能性「健康校驗」。通常在壓測腳本剛寫完、或微服務新版本部署至 Staging 環境時執行，確認 API 路由、鑑權 Token、資料庫連線通暢無阻。
- **流量特徵**：1~2 個 VU，測試時長 30 秒至 1 分鐘。
- **配置範例**：

```javascript
export const options = {
  vus: 1,
  duration: '1m',
  thresholds: {
    'http_req_failed': ['rate==0'], // 冒煙測試嚴禁出現任何錯誤
    'checks': ['rate==1.0'],        // 所有業務斷言必須百分之百通過
  },
};
```

#### 2. Load Testing（常規負載測試 / 階梯波形）

- **業務目標**：評估系統在預期的日常峰值流量下的吞吐量、平均延遲與 P95/P99 表現，驗證是否符合業務 SLA/SLO。
- **流量波形**：經典三段式波形：
  1. **預熱緩升 (Ramp-up)**：讓快取預熱、連線池逐步建立，避免冷啟動擊穿。
  2. **尖峰高原期 (Plateau / Steady State)**：維持高負載持續觀察系統資源是否穩定。
  3. **平緩降速 (Ramp-down)**：驗證連線資源、GC、執行緒池是否能優雅釋放與回收。

```
VU
 ^          ┌───────────────┐ (高原穩態 Plateau)
 |         /                 \
 |        /                   \
 |       /                     \
 |      / (爬坡 Ramp-up)        \ (降載 Ramp-down)
 0 ────┴─────────────────────────┴────> Time
```

- **配置範例**：

```javascript
export const options = {
  stages: [
    { duration: '3m', target: 50 },  // 3 分鐘內平緩爬升至 50 VUs
    { duration: '10m', target: 50 }, // 在 50 VUs 高原期維持 10 分鐘，觀察穩態
    { duration: '3m', target: 0 },   // 3 分鐘內平緩降載至 0，驗證資源釋放
  ],
  thresholds: {
    'http_req_duration': ['p(95)<1500'], // 95% 請求延遲必須在 1.5 秒以內
    'http_req_failed': ['rate<0.01'],    // 錯誤率必須低於 1%
  },
};
```

#### 3. Stress Testing（極限壓力測試 / 斷裂點探尋）

- **業務目標**：衝破安全水位，以漸進式階梯持續加壓，直到系統出現吞吐量下降、延遲陡增或錯誤率飆高的「拐點 (Knee Point)」。其目的不是驗證及格，而是找出「**系統極限承載力在哪裡**」以及「**系統在崩潰時能否優雅降級**」。
- **流量波形**：階梯式攀升 (Step-up Ladder)，步步進逼極限。

```
VU
 ^                  ┌───────┐
 |              ┌───┘       └───┐
 |          ┌───┘               └───┐
 |      ┌───┘                       └───┐
 0 ─────┴───────────────────────────────┴────> Time
```

- **配置範例**：

```javascript
export const options = {
  stages: [
    { duration: '2m', target: 50 },   // 第一階：50 VUs
    { duration: '3m', target: 50 },
    { duration: '2m', target: 100 },  // 第二階：加壓至 100 VUs
    { duration: '3m', target: 100 },
    { duration: '2m', target: 200 },  // 第三階：衝刺至 200 VUs
    { duration: '3m', target: 200 },
    { duration: '2m', target: 300 },  // 第四階：極限 300 VUs (尋找崩潰點)
    { duration: '3m', target: 300 },
    { duration: '3m', target: 0 },    // 冷卻收尾
  ],
  thresholds: {
    // 壓力測試允許較寬鬆的門檻，但需捕捉崩潰拐點
    'http_req_failed': ['rate<0.05'], 
  },
};
```

#### 4. Spike Testing（突發尖峰測試 / 閃崩衝擊）

- **業務目標**：模擬極端瞬時暴衝流量（例如限量球鞋開搶、全站推播促銷、地震即時速報），考驗微服務架構的「抗震力」與「彈性自癒能力 (Self-Healing)」。重點觀察：
  - Kubernetes HPA 水平擴展的反應延遲（從監控警報到 Pod Ready 是否太慢）。
  - Redis 快取與資料庫連線池是否瞬間被連鎖擊穿 (Thundering Herd)。
  - 消息隊列 (Kafka/RabbitMQ) 能否成功蓄洪緩衝。
- **流量波形**：垂直衝天型 (Vertical Surge)，數十秒內激增 10x ~ 50x，短暫停留後急降，再觀察自癒期。

```
VU
 ^          ┌┐ (瞬間暴衝 Spike)
 |          ||
 |          ||
 |      ────┘└─── (自癒觀察期 Recovery)
 0 ───────────────────────────────> Time
```

- **配置範例**：

```javascript
export const options = {
  stages: [
    { duration: '30s', target: 10 },   // 基準低負載
    { duration: '10s', target: 200 },  // 10 秒內瞬間暴增 20 倍至 200 VUs！
    { duration: '1m', target: 200 },   // 高壓衝擊維持 1 分鐘
    { duration: '10s', target: 10 },   // 10 秒內急降回基準 10 VUs
    { duration: '2m', target: 10 },    // 自癒觀察期：確認系統是否恢復正常響應
    { duration: '10s', target: 0 },
  ],
};
```

#### 5. Soak Testing（浸泡耐久測試 / 耐力長跑）

- **業務目標**：在系統安全水位（約 70%~80% 負載）下長跑數小時至數十小時，專門揪出短時間壓測看不出來的「**四大隱形殺手**」：
  1. **記憶體洩漏 (Memory Leak)**：底層全域變數、快取未設置 TTL 或 Event Listener 未解綁，長時間運行導致 JVM/V8 堆疊溢位 (OOM)。
  2. **連線池洩漏 (Connection Pool Exhaustion)**：資料庫 Query 或 HTTP Client 連線未顯式關閉，累積數小時後池化連線耗盡。
  3. **日誌與磁碟爆滿 (Disk Full)**：無上限日誌堆積填滿 Pod 磁碟空間引發 Evicted。
  4. **認證憑證失效 (Token Expiration)**：JWT/OAuth Token 長期運行未刷新，引發大面積 401 故障。
- **配置範例**：

```javascript
export const options = {
  stages: [
    { duration: '5m', target: 40 },    // 預熱
    { duration: '4h', target: 40 },    // 長跑 4 小時（生產級常跑 8~24 小時）
    { duration: '5m', target: 0 },     // 收尾
  ],
  thresholds: {
    'http_req_failed': ['rate<0.005'], // 長跑期間錯誤率必須嚴格小於 0.5%
    'http_req_duration': ['p(99)<2000'],
  },
};
```

#### 五大模式決策矩陣 (Traffic Pattern Decision Matrix)

| 模式名稱 | 併發量級 (VU) | 測試時長 | 核心測試目標 | CI/CD 觸發時機 | 典型失敗徵兆 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Smoke (冒煙)** | 1 ~ 2 VU | 30s ~ 1m | 腳本與 API 路由連通性 | 每次 Git Push / PR 構建 | 404/401、斷言失效率 > 0% |
| **Load (常規負載)** | 預估尖峰 100% | 15m ~ 30m | 驗證常態峰值 SLA/SLO | 每週 Release / 發版前審核 | P95 延遲超標、Thread 阻塞 |
| **Stress (極限壓力)** | 預估尖峰 150%~300% | 20m ~ 45m | 探尋崩潰拐點與防禦降級 | 重大版本升級 / 季度容量評估 | RPS 倒退、500 Internal Error |
| **Spike (突發尖峰)** | 瞬間暴衝 5x~20x | 3m ~ 5m | 檢驗 HPA 彈性擴展與快取抗震 | 促銷活動前夕 / 大促架構演練 | HPA 擴展滯後、快取擊穿崩潰 |
| **Soak (浸泡耐久)** | 安全水位 70%~80% | 2h ~ 24h | 揪出記憶體洩漏與連線池枯竭 | 週末排程 / 上線前最後耐久驗證 | 記憶體階梯上升、DB Connection Timeout |

---

### 徹底破解「協調性漏測 (Coordinated Omission)」致命數據謊言

由 Azul Systems 創辦人兼著名效能大師 **Gil Tene** 提出的 **Coordinated Omission（協調性漏測）**，被公認為效能工程歷史上最致命、最普遍的數據盲點！

#### 什麼是協調性漏測？

Negative
: 當受測系統發生延遲或卡頓時，測試工具「**無意中與受測系統同謀協調**」，自動延遲發送後續請求，導致測試報告中統計到的延遲數據「看似平穩正常」，實際上卻完全掩蓋了使用者端真實發生的災難性排隊延遲！

#### 收費站車禍心智模型 (The Tollbooth Analogy)

想像一座高速公路收費站，平時**每秒通行 1 輛車**，平均耗時 1 秒：

```
【正常通行】
車流: ───[車3]───[車2]───[車1]───> [收費站 (耗時 1s)] ───> 通行順暢 (平均延遲 1s, RPS = 1)
```

突然，收費閘道當機**卡死整整 100 秒**：

```
【情況 A：傳統閉環模型 (Closed Loop Model)】
車流: ──────────────[車1 卡住 100s]───> [收費站 (故障卡死)]
(測試工具規定：必須等「車1」通過後，才允許出發下一輛「車2」！)
結果：在整整 100 秒的故障期間，全系統只發送了 1 次請求。
測試報表顯示：「總共 1 筆請求，延遲 100s，平均 RPS 接近 0。」
看似只有一個人受到影響！
```

```
【情況 B：真實世界與開放模型 (Open Model)】
車流: ───[車100]──[車99]...[車3]──[車2]──[車1 卡住 100s]───> [收費站 (故障卡死)]
真實世界的使用者根本不知道前方卡死，後續車輛每秒以固定頻率（Arrival Rate）持續抵達！
第 1 輛車：等待 100 秒。
第 2 輛車：等待 99 秒。
第 3 輛車：等待 98 秒。
...
第 100 輛車：等待 1 秒。
結果：100 個人全被堵在路上！真實的總累積等待時間高達 5,050 秒，平均排隊延遲高達 50.5 秒！
```

#### 閉環模型 (Closed Loop Model) 的數學缺陷

在傳統壓測工具（包括 k6 使用 `vus: 10` 或 JMeter 預設 Thread Group）中，虛擬用戶的執行邏輯本質是閉環的：

```text
                   VU (虛擬用戶數)
RPS (吞吐量) = ────────────────────────────
                Response Time (延遲) + Sleep
```

- **正常狀態**：當後端服務響應飛快（`50ms = 0.05s`、`Sleep = 0`）時，10 個 VU 每秒可打出：  
  `10 / 0.05s = 200 RPS`
- **故障卡頓**：當後端資料庫死鎖、回應延遲飆升至 `5s` 時，10 個 VU 全部被卡死等待，實際發出頻率驟降至：  
  `10 / 5s = 2 RPS`

> **致命荒謬之處**：當被測系統越脆弱、卡頓越嚴重時，閉環測試工具反而**自動給被測系統大幅放水減壓**！這直接導致採樣點嚴重偏向系統正常時的請求，將真實的長尾延遲 (Tail Latency) 徹底隱匿！

---

### 開放模型實戰與利特爾法則 (Little's Law) 數學精算

為了解決協調性漏測，k6 推出了**開放模型 (Open Model / Arrival Rate Executors)**。開放模型將「**請求抵達率 (Arrival Rate)**」與「**虛擬用戶數 (VU)**」徹底解耦！

無論後端處理有多慢，排程器都會像真實世界的使用者一樣，精準按照設定的 RPS 持續發起請求。當後端變慢導致請求排隊時，k6 會自動調用額外的並發 VU 來維持目標 RPS。

#### 利特爾法則 (Little's Law) 精算公式

要在開放模型中精準設定資源配置，必須運用排隊理論的黃金定理——**利特爾法則**：

```text
L = λ × W

並行量 (VU) = 抵達率 (RPS) × 平均停留時間 (Latency 秒數)
```

- **`L`（Concurrency / 並行量）**：系統內同時存在的並行請求數（對應 k6 所需配置的 VU 數量）。
- **`λ`（Arrival Rate / 抵達率）**：單位時間內抵達系統的請求速率（目標 RPS）。
- **`W`（Latency / 平均停留時間）**：每個請求在系統中從發起到回應的平均耗時（秒）。

#### 三大生產級精算案例

##### 案例 1：輕量快取查詢 API (Cache-Hit Reads)
- 目標抵達率：`λ = 500 RPS`，預期平均延遲：`W = 20ms = 0.02 秒`。
- 基準所需並行量：`L = 500 × 0.02 = 10 VUs`。
- **k6 參數配置**：`preAllocatedVUs: 10`，彈性緩衝 `maxVUs: 30`。

##### 案例 2：重度電商下單 API (Database Transactions)
- 目標抵達率：`λ = 200 RPS`，預期平均延遲：`W = 250ms = 0.25 秒`。
- 基準所需並行量：`L = 200 × 0.25 = 50 VUs`。
- **k6 參數配置**：`preAllocatedVUs: 50`，彈性緩衝 `maxVUs: 150`。

##### 案例 3：長尾延遲突波防線 (Tail Latency Buffer)
- 假設在案例 2 的下單 API 中，一旦發生資料庫鎖競爭，P99 延遲飆升至 `1.5 秒`：
- 極端所需並行量：`L_spike = 200 × 1.5 = 300 VUs`！
- 若你的 `maxVUs` 只配置了 100，k6 的 VU 池將被瞬間耗盡，導致無法維持 200 RPS，進而產生 `dropped_iterations`。因此面對長尾延遲，`maxVUs` 應預留 3 ~ 5 倍於常態的容量空間。

#### k6 開放模型執行器配置範例

```javascript
export const options = {
  scenarios: {
    // 恆定抵達率開放模型 (Constant Arrival Rate)
    constant_rate_test: {
      executor: 'constant-arrival-rate',
      rate: 200,             // 強制鎖定：每秒發送 200 次迭代 (200 RPS)
      timeUnit: '1s',        // rate 的時間基準
      duration: '5m',        // 測試時長
      preAllocatedVUs: 50,   // 根據 Little's Law 精算的基準併發用戶池 (L = 200 * 0.25s)
      maxVUs: 300,           // 遭遇尾端延遲飆高時的最大動態擴展緩衝池
    },
    // 漸增抵達率開放模型 (Ramping Arrival Rate)
    ramping_rate_test: {
      executor: 'ramping-arrival-rate',
      startRate: 50,
      timeUnit: '1s',
      preAllocatedVUs: 50,
      maxVUs: 400,
      stages: [
        { duration: '2m', target: 100 }, // 2 分鐘內將抵達率由 50 RPS 提升至 100 RPS
        { duration: '5m', target: 100 }, // 維持 100 RPS 高原
        { duration: '2m', target: 300 }, // 加壓至 300 RPS 考驗極限
        { duration: '3m', target: 300 },
        { duration: '2m', target: 0 },   // 降載冷卻
      ],
    },
  },
};
```

---

### 關鍵過載指標：`dropped_iterations` 底層機制與實戰防線

在使用開放模型（`constant-arrival-rate` 或 `ramping-arrival-rate`）時，終端機輸出中有一個極其關鍵的指標：**`dropped_iterations`**。

#### 為什麼會發生 `dropped_iterations`？

排程器嚴格按照設定的 `rate` 計時發起新迭代。但如果受測服務嚴重變慢，導致所有已分配的 VU（包含 `preAllocatedVUs` 以及動態擴展的 `maxVUs`）**全部處於連線等待中、無一可用**，此時排程器別無選擇，只能**強制拋棄該次迭代發送**！

```
[排程器: 嘀嗒! 該發送 Request #501] 
       │
       ▼
[檢查 VU 池] ──> (preAllocatedVUs 已用完) ──> (maxVUs 50/50 全部被卡死在等待後端 DB 回應)
       │
       ▼
❌ 無可用 VU！被迫拋棄！──> dropped_iterations 計數 +1！
```

#### 根因二分診斷法 (Two-Branch Troubleshooting)

當壓測報告出現 `dropped_iterations > 0` 時，請遵循以下決策樹進行排查：

```
                     dropped_iterations > 0
                               │
       ┌───────────────────────┴───────────────────────┐
       ▼                                               ▼
【分支 A：受測後端崩潰】                       【分支 B：壓測機資源配置失衡】
特徵：http_req_duration 延遲暴增、             特徵：後端延遲完全正常 (<50ms)，
      504 Gateway Timeout 或連線重置。              但 dropped_iterations 仍然增加。
根因：後端伺服器 CPU/DB 飽和，連線堆積，        根因：maxVUs 設太小，無法支撐目標 RPS；
      VU 耗盡是後端故障引發的連鎖反應。             或壓測主機本身 CPU 100%/記憶體耗盡。
解法：優化後端瓶頸、加大 DB 連線池。           解法：依據 Little's Law 調高 maxVUs。
```

Positive
: **CI/CD 自動防線宣告**：在生產級腳本中，務必將 `dropped_iterations` 納入 Thresholds，嚴格要求零丟失：
```javascript
thresholds: {
  'dropped_iterations': ['count==0'], // 一旦有任何迭代被丟棄，自動裁定壓測失敗！
}
```

---

### 多場景複合調度 (Multi-Scenario Orchestration)

真實生產環境中，使用者從不是只存取單一 API。一個成熟的電商系統流量由多種異質操作混合而成：
- 80% 輕量操作：商品列表與首頁瀏覽 (Browsing Traffic)
- 15% 搜尋操作：商品關鍵字檢索 (Search Traffic)
- 5% 交易操作：購物車與結帳下單 (Checkout Traffic)

k6 允許在單一腳本中宣告多個獨立運作的 `scenarios`，每個情境可配置不同的執行器、時間軸與目標函數：

```javascript
import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  scenarios: {
    // 情境 1：平穩的商品瀏覽背景流量 (80% 流量)
    browse_products: {
      executor: 'constant-arrival-rate',
      rate: 80,
      timeUnit: '1s',
      duration: '5m',
      preAllocatedVUs: 20,
      maxVUs: 50,
      exec: 'browseWorkflow', // 指定執行函數
      tags: { traffic_type: 'browse' },
    },

    // 情境 2：階梯式搜尋流量 (15% 流量)
    search_queries: {
      executor: 'ramping-arrival-rate',
      startRate: 5,
      timeUnit: '1s',
      preAllocatedVUs: 10,
      maxVUs: 30,
      stages: [
        { duration: '1m', target: 15 },
        { duration: '3m', target: 15 },
        { duration: '1m', target: 0 },
      ],
      exec: 'searchWorkflow',
      tags: { traffic_type: 'search' },
    },

    // 情境 3：延遲 2 分鐘後介入的限時搶購結帳流量 (5% 流量)
    flash_sale_checkout: {
      executor: 'constant-arrival-rate',
      rate: 5,
      timeUnit: '1s',
      startTime: '2m',        // 延後 2 分鐘啟動，模擬搶購開跑
      duration: '3m',
      preAllocatedVUs: 15,
      maxVUs: 50,
      exec: 'checkoutWorkflow',
      tags: { traffic_type: 'checkout' },
    },
  },
  thresholds: {
    'http_req_duration{traffic_type:checkout}': ['p(95)<2000'], // 結帳端點特別門禁
    'http_req_duration{traffic_type:browse}': ['p(95)<300'],
  },
};

export function browseWorkflow() {
  http.get('https://test.k6.io/products');
}

export function searchWorkflow() {
  http.get('https://test.k6.io/search?q=phone');
}

export function checkoutWorkflow() {
  http.post('https://test.k6.io/checkout', JSON.stringify({ item_id: 101 }), {
    headers: { 'Content-Type': 'application/json' },
  });
}
```

---

### `SharedArray` 記憶體拯救神技深度解析

#### k6 執行緒架構與記憶體爆炸陷阱

k6 為了在多核心 CPU 上榨乾極限壓測效能，底層採用了獨特的執行緒隔離模型：**每個虛擬用戶 (VU) 都是一個完全獨立隔離的 Goja JavaScript 虛擬機 (Runtime)**。

這種架構杜絕了多執行緒爭搶與全域鎖，但帶來了一個嚴重的內存陷阱：
- 若你在腳本頂層以標準 JavaScript 方式載入一份 50MB 的測試資料（例如 `JSON.parse(open('./users.json'))`）：
- **每個 VU 實例化時，都會深拷貝一份該物件到自己的 JS Heap 中！**

```
【傳統 Array 記憶體雪崩】
VU 1  (JS Runtime) ──> 獨立拷貝 50MB
VU 2  (JS Runtime) ──> 獨立拷貝 50MB
...
VU 1000 (JS Runtime) ──> 獨立拷貝 50MB ───> 總記憶體消耗 50GB！直接引發 OOM Crash！
```

#### 記憶體消耗極端對照表

| 資料集檔案大小 | 100 VU | 1,000 VU | 5,000 VU | 10,000 VU |
| :--- | :--- | :--- | :--- | :--- |
| **10 MB (傳統 Array)** | 1 GB | 10 GB | 50 GB *(OOM)* | 100 GB *(崩潰)* |
| **50 MB (傳統 Array)** | 5 GB | 50 GB *(OOM)* | 250 GB *(崩潰)* | 500 GB *(不可能執行)* |
| **50 MB (SharedArray)** | **~60 MB** | **~65 MB** | **~80 MB** | **~100 MB (節省 99.8%)** |

#### `SharedArray` 唯讀記憶體映射架構

`k6/data` 模組提供的 **`SharedArray`** 是解決該問題的終極神技：
- **底層原理**：回呼建構函數只在 **Init 階段**由主線程執行一次。資料集在 Go 語言層面被保存為一份共享切片 (Go Slice)。
- **各 VU 存取方式**：各 VU 的 JavaScript Runtime 僅持有該共享切片的唯讀虛擬指針與 Proxy 視圖。
- **不可變性保障**：SharedArray 天生唯讀，嚴禁任何 VU 修改元素內容，從架構層面確保執行緒安全與零記憶體拷貝！

```javascript
import { SharedArray } from 'k6/data';

// 全域唯讀共享記憶體：無論開 10 個還是 10,000 個 VU，記憶體只佔用一份！
const testUsers = new SharedArray('users_pool', function () {
  console.log('[SharedArray] 正在由主線程載入測試帳號...');
  return JSON.parse(open('./large_users.json'));
});
```

#### 三大實戰資料提取模式

在 VU Code 中存取 `SharedArray` 時，推薦以下三種分發策略：

##### 策略 1：輪詢循環提取 (Round-Robin with Iteration & VU)
確保不同 VU 與迭代均勻分佈資料：
```javascript
export default function () {
  const index = (__VU * 1000 + __ITER) % testUsers.length;
  const user = testUsers[index];
  // 使用 user 進行登入或呼叫 API...
}
```

##### 策略 2：隨機均勻抽樣 (Random Sampling)
模擬真實世界隨機用戶訪問：
```javascript
export default function () {
  const randomIndex = Math.floor(Math.random() * testUsers.length);
  const user = testUsers[randomIndex];
}
```

##### 策略 3：VU 專屬分片 (VU Data Sharding / Non-overlapping)
每個 VU 只處理專屬的資料區間，完全避免並行測試中資料重複使用衝突：
```javascript
export default function () {
  const chunkSize = Math.floor(testUsers.length / 10); // 假設有 10 個 VU
  const startIndex = (__VU - 1) * chunkSize;
  const userIndex = startIndex + (__ITER % chunkSize);
  const user = testUsers[userIndex];
}
```

---

### 手把手實作演練：科學流量建模驗證

現在讓我們進入終端機，親自實操驗證閉環模型、開放模型與 `SharedArray` 的效能表現。

#### 實作 1：閉環模型 vs 開放模型生死對決

在專案中已內建實戰對比腳本 `k6/demos/ch2_closed_vs_open_model.js`，該腳本測試一個強制延遲 1 秒的端點。

##### 步驟 1-A：執行閉環模型 (觀察協調性漏測)

```bash
k6 run -e MODEL=closed k6/demos/ch2_closed_vs_open_model.js
```

> **👀 觀察重點**：
> 配置為 5 個 VU 執行 15 秒。由於每個請求延遲 1 秒，5 個 VU 只能輪流等待。
> 終端機顯示的實際吞吐量僅有 **~4.9 RPS**，發出總請求數僅約 75 筆。閉環模型在延遲面前主動放水！

##### 步驟 1-B：執行開放模型 (觀察 Little's Law 自動調派)

```bash
k6 run -e MODEL=open k6/demos/ch2_closed_vs_open_model.js
```

> **👀 觀察重點**：
> 目標強制鎖定為 **20 RPS** (`constant-arrival-rate`)。
> 依據利特爾法則 `L = 20 × 1s = 20 VUs`，k6 自動動態拉升並行 VU 數量至 20~25 個，堅定維持每秒 20 次請求的抵達率！總請求數達到 300 筆，精準重現真實世界的排隊衝擊！

#### 實作 2：刻意誘發 `dropped_iterations` 容量告警

修改或以命令列調整 `maxVUs` 為極小值，觀察 k6 的過載防線：

```bash
k6 run -e MODEL=open -e TARGET_URL=https://httpbin.test.k6.io/delay/2 k6/demos/ch2_closed_vs_open_model.js
```

> **👀 觀察重點**：
> 當延遲攀升至 2 秒且 `maxVUs` 不足以支撐目標抵達率時，終端機摘要將出現鮮紅的 `dropped_iterations` 計數，且門禁判定為失敗！這正是現代 CI/CD 阻擋效能衰退的關鍵憑據。

#### 實作 3：驗證 SharedArray 萬筆資料極速載入

```bash
k6 run k6/demos/ch2_shared_array.js
```

> **👀 觀察重點**：
> 觀察控制台輸出 `[SharedArray] 正在初始化 10,000 筆測試帳號至唯讀共享記憶體中...` 僅在 Init 階段出現**一次**。
> 5 個 VU 快速完成了 10 次迭代，記憶體佔用毫無膨脹，所有資料讀取斷言 100% 通過！

#### 實作 4：運行專案自帶的負載測試與尖峰測試

```bash
# 執行標準三階段負載測試
k6 run k6/load-test.js

# 執行突發尖峰測試
k6 run k6/spike-test.js
```

---

### Chapter 2 核心心智模型與避坑指南

1. **區分 VU 與 RPS**：
   - 如果你的測試目標是「驗證系統能否承受 500 名使用者同時在線閒晃」，請使用基於 VU 的模型（閉環模型 + Think Time）。
   - 如果你的測試目標是「驗證 API 能否支撐每秒 500 筆訂單湧入 (500 RPS)」，請務必使用基於抵達率的**開放模型**！
2. **永遠在開放模型中設定門禁 `dropped_iterations: ['count==0']`**：
   - 任何非零的 `dropped_iterations` 都是壓測無效或系統崩潰的明確信號。
3. **海量測試資料唯有 `SharedArray`**：
   - 超過 1,000 筆的使用者資料或 CSV 參數化檔案，一律禁止在全域使用普通 Array，強制改用 `k6/data` 的 `SharedArray`。
4. **開放模型中勿在 VU 程式碼使用 `sleep()` 控制流量**：
   - 開放模型的請求頻率由排程器的 `rate` 嚴格控制。在 VU 代碼中加入 `sleep()` 只會白白拉長該 VU 的佔用時間，浪費 `maxVUs` 容量！

---

## Chapter 3: 效能指標解讀與 SLO 門檻自動化 (Quality Gates)
Duration: 25

### 微服務黃金準則：Google SRE 與 RED Method 深度解剖

在完成流量施壓後，面對終端機中傾瀉而出的海量數據，許多團隊最常問的問題是：「這些數字到底代表什麼？怎樣才算及格？」

在現代微服務與雲原生架構中，效能監控與品質門禁的靈魂基石來自於兩大業界黃金法則：
1. **Google SRE 四大黃金信號 (The Four Golden Signals)**：延遲 (Latency)、流量 (Traffic)、錯誤 (Errors)、飽和度 (Saturation)。
2. **Weaveworks / Tom Wilkie 提出的 RED Method**：專為微服務架構量身打造，將監控聚焦於最關鍵的三大軸線：
   - **Rate（請求速率 / 吞吐量）**：系統當前每秒正在處理多少個請求？
   - **Errors（錯誤比率）**：有多少請求以非預期的 5xx 或業務邏輯錯誤結束？
   - **Duration（持續時間 / 延遲）**：每個請求完成完整的網路與業務交互需要耗費多少毫秒？

#### k6 核心指標與 RED Method 的映射關係

| RED 維度 | 對應 k6 內建指標 | 指標型態 | 監控核心意義 | 典型 SLO 門檻範例 |
| :--- | :--- | :--- | :--- | :--- |
| **Rate** | `http_reqs` | Counter | 系統整體處理速率 (RPS) 與總請求量 | `rate > 500` (每秒需能承受 500 RPS) |
| **Errors** | `http_req_failed` | Rate (0~1) | 非 2xx/3xx HTTP 狀態碼之失敗比例 | `rate < 0.01` (全站錯誤率嚴格低於 1%) |
| **Duration** | `http_req_duration` | Trend | 請求完整耗時（自連線至完全接收回應） | `p(95) < 1000` (95% 請求需在 1 秒內完成) |
| **Saturation** | `vus` / `vus_max` | Gauge | 壓測端資源飽和度與動態 Goroutine 水位 | 觀察是否觸發 `dropped_iterations` |

---

### 延遲時間線微觀拆解：剖析 `http_req_duration` 底層生命週期

許多工程師誤以為 `http_req_duration` 只是單純的「後端計算時間」，這是一個極大的誤解！在分散式網路環境中，一個 HTTP 請求的耗時由多個微觀階段組合而成：

```text
[───────────────────────────────── http_req_duration ─────────────────────────────────]
┌───────────────┬──────────────────┬──────────────┬──────────────┬──────────────────┬───────────────┐
│ http_req_     │ http_req_        │ http_req_    │ http_req_    │ http_req_        │ http_req_     │
│ blocked       │ connecting       │ tls_hand-    │ sending      │ waiting (TTFB)   │ receiving     │
│               │                  │ shaking      │              │                  │               │
└───────────────┴──────────────────┴──────────────┴──────────────┴──────────────────┴───────────────┘
  等待本機連線池   TCP 三向握手建立   TLS 證書協商     傳送請求封包     伺服器處理與運算   下載回應內容至
  空閒 Socket     SYN->SYN/ACK->ACK  密鑰交換開銷     上行傳輸時間     (DB 查詢 / 運算)  壓測客戶端完成
```

#### 延遲異常根因診斷矩陣 (Latency Diagnostic Matrix)

當 `http_req_duration` 門檻超標時，請依據細分指標快速鎖定架構瓶頸：

- **`http_req_blocked` 飆高**：
  - **可能病因**：壓測客戶端本機連線數達到上限、作業系統本機埠耗盡 (Local Port Exhaustion)、或未啟用 HTTP Keep-Alive 連線複用。
  - **解法**：在作業系統調整 `sysctl net.ipv4.ip_local_port_range`，或在 k6 啟用連線池重複利用。
- **`http_req_connecting` / `http_req_tls_handshaking` 飆高**：
  - **可能病因**：每次 HTTP 請求都重新建立連線，缺乏持久連線 (Persistent Connection)；或負載平衡器 (Nginx/ALB) 與壓測機之間的跨機房網路 RTT 延遲過大。
  - **解法**：確認 HTTP 請求標頭包含 `Connection: keep-alive`，並在受測架構中啟用 TLS Session Resumption。
- **`http_req_waiting` (TTFB, Time to First Byte) 飆高**：
  - **可能病因**：**90% 後端效能瓶頸的罪魁禍首！** 代表伺服器已收到請求，但在吐出第一個 Byte 前思考了很久。通常為資料庫慢查詢、資料庫連線池耗盡 (Pool Starvation)、CPU 100% 阻塞、或微服務下游 RPC 串聯卡頓。
  - **解法**：透過 OpenTelemetry Distributed Tracing 深入後端 Span 鏈路定位 SQL 慢查詢。
- **`http_req_receiving` 飆高**：
  - **可能病因**：後端回傳了極度肥大的 JSON Payload（例如一次回傳 10,000 筆商品詳細資料），導致網路頻寬被打滿。
  - **解法**：API 強制實施分頁機制 (Pagination)、精簡欄位，並開啟 Gzip/Brotli 壓縮。

---

### 破解「平均值陷阱」：長尾分佈與百分位數 (Percentiles)

Negative
: **永遠不要在效能測試與 SLO 審查中使用「平均值 (Average)」！** 在高併發分散式系統中，平均值是最大謊言。如果 100 個請求中，99 個只要 10ms，但有 1 個結帳請求卡了 10 秒，算出來的平均值依然只有約 109ms，看起來風平浪靜。但那 1% 被卡死的用戶，恰恰是正準備掏錢結帳的最核心 VIP！

#### 雙峰分佈 (Bimodal Distribution) 與快取失效

真實世界的網路延遲往往呈現「雙峰」甚至「多峰」分佈：
- **峰值 A (10ms)**：快取命中 (Cache Hit)，直接由 Redis 回傳。
- **峰值 B (3,000ms)**：快取失效 (Cache Miss)，穿透至資料庫進行多表關聯 JOIN 查詢。

若使用平均值，這兩個極端會被無情抹平成「150ms」，導致架構師誤以為全站速度飛快，完全忽略了每次快取失效時給資料庫造成的致命衝擊！

#### 百分位數 (Percentiles) 的權威標準

- **P90 (90th Percentile)**：九成使用者的常態體驗。
- **P95 (95th Percentile)**：**業界標準發版品質門禁**。95% 的請求都優於此時間，允許少數突波但不失控。
- **P99 (99th Percentile - 尾端延遲 Tail Latency)**：捕捉最倒楣的 1% 用戶體驗，更是微服務架構防範「骨牌效應」的生命線。

#### 微服務長尾放大效應 (Tail Latency Amplification)

為什麼大型微服務系統對 P99 如此嚴苛？  
假設首頁渲染需要並行呼叫 10 個後端微服務（用戶、推薦、庫存、價格、購物車...），每個服務的 P99 延遲為 1% 機率超標：

```text
整個前端請求遭遇延遲的機率 = 1 - (1 - 0.01)^10 ≈ 9.56%
```

只要後端呼叫的微服務鏈路擴展至 50 個，前端使用者遭遇卡頓的機率將直接飆升至 **39.5%**！這就是為什麼 Google 與 Netflix 等頂級工程團隊一律使用 P99 與 P99.9 作為生產級 SLO。

---

### 四大自訂指標型態 (Custom Metrics) 實戰全解析

k6 除了能自動統計 HTTP 網路層指標，更允許工程師將業務語意轉化為代碼化指標：

```javascript
import { Counter, Gauge, Rate, Trend } from 'k6/metrics';
```

#### 1. Counter（累計計數器）
- **特性**：數值只能**單調遞增**（不可減少）。
- **業務場景**：統計訂單成交總數、特定業務錯誤碼出現次數、重試觸發次數。
- **代碼示範**：
  ```javascript
  const completedOrders = new Counter('business_orders_completed');
  // 在業務邏輯中累加
  completedOrders.add(1);
  completedOrders.add(5); // 亦可一次增加多個
  ```

#### 2. Gauge（瞬時狀態規）
- **特性**：可隨時增加、減少或重設，永遠記錄**當下的最新快照值**。
- **業務場景**：監控壓測過程中的即時記憶體佔用、當前等待隊列深度、特定時刻在線的 Worker 數。
- **代碼示範**：
  ```javascript
  const queueDepthGauge = new Gauge('active_queue_depth');
  // 記錄瞬時值
  queueDepthGauge.add(currentQueueLength);
  ```

#### 3. Rate（比率規 / 成功率）
- **特性**：專門記錄 `0` 與 `1`（或布林值 `false` / `true`），k6 會自動計算百分比（`0.0 ~ 1.0`）。
- **業務場景**：業務級結帳成功率、第三方支付回調成功率（區別於 HTTP 200，即使 HTTP 為 200，但回傳 `{"code": -101}` 依然是業務失敗）。
- **代碼示範**：
  ```javascript
  const checkoutSuccessRate = new Rate('checkout_success_rate');
  // 記錄成功 (1) 或失敗 (0)
  checkoutSuccessRate.add(res.json('status') === 'SUCCESS');
  ```

#### 4. Trend（統計趨勢規）
- **特性**：自動對傳入的數值陣列計算 `min`, `max`, `avg`, `med`, `p(90)`, `p(95)`, `p(99)`。
- **業務場景**：衡量內部資料庫查詢耗時、自訂 gRPC 耗時、從登入到完成結帳的全流程漏斗總耗時。
- **代碼示範**：
  ```javascript
  const dbQueryTrend = new Trend('custom_db_query_duration');
  // 記錄數值 (毫秒)
  dbQueryTrend.add(queryExecutionTimeMs);
  ```

---

### 斷言三部曲完整對照：check vs thresholds vs expect

許多開發者在撰寫 k6 腳本時，常將 `check` 與 `thresholds` 混為一談。以下整理出權威級對比：

| 比較維度 | `check()`（軟斷言） | `thresholds`（全域品質閘門） | `expect()`（BDD 風格斷言） |
| :--- | :--- | :--- | :--- |
| **執行層級** | 請求 / 函數局部層級 | 測試執行階段全域聚合層級 | 代碼單元 / 局部層級 |
| **失敗後果** | 印出紅叉，**測試繼續進行**，**不影響** Exit Code | 門檻未達標，**自動觸發 Exit Code 99** | 拋出例外，可能中斷當前迭代 |
| **指標歸宿** | 聚合記錄入內建的 `checks` (Rate) 指標 | 可監控任何內建或自訂指標 | 通常與 `check` 搭配包裝 |
| **核心職責** | 驗證「資料正則與結構正確性」 | 宣告「效能與穩定度及格標準」 | 提供類似 Chai / Jest 的流暢語意 |
| **CI/CD 角色**| 提供除錯線索，**無法單獨阻斷 Pipeline** | **CI/CD 自動卡關的核心裁決依據** | 單元測試轉移腳本輔助 |

Positive
: **最佳實踐組合技**：使用 `check()` 驗證回應正確性，並在 `thresholds` 宣告 `'checks': ['rate>0.99']`！唯有將軟斷言納入全域門檻，才能在資料錯誤時自動使 CI/CD 卡關！

---

### 標籤與分組機制 (Tagging & Groups)：打造微服務精確 SLO

在真實企業微服務中，不同等級的 API 絕對不能適用同一套標準：
- **核心交易 API**（如 `/api/checkout`）：SLO 嚴苛，要求 P99 < 300ms，錯誤率 < 0.1%。
- **背景報表 API**（如 `/api/export/pdf`）：SLO 寬鬆，允許 P95 < 5,000ms。

如果只設定全域 `http_req_duration: ['p(95)<500']`，報表 API 的正常耗時就會直接拖垮全站門禁，產生大量「假警報」！

#### 1. 請求層級打標 (Request-Level Tags)

在發送 HTTP 請求時，傳入 `tags` 物件：

```javascript
http.get('https://api.example.com/checkout', {
  tags: { tier: 'critical', feature: 'payment' },
});

http.get('https://api.example.com/reports', {
  tags: { tier: 'background', feature: 'export' },
});
```

#### 2. 基於標籤的精準門檻語法 (Tagged Thresholds)

```javascript
export const options = {
  thresholds: {
    // 1. 全域基準門檻
    'http_req_failed': ['rate<0.01'],

    // 2. 針對 critical 等級端點的高標準門禁
    'http_req_duration{tier:critical}': ['p(99)<300'],

    // 3. 針對 background 報表端點的寬鬆門禁
    'http_req_duration{tier:background}': ['p(95)<5000'],

    // 4. 多重標籤聯合約束 (AND 邏輯)
    'http_req_duration{tier:critical,feature:payment}': ['p(99.9)<500'],
  },
};
```

#### 3. 避免高基數維度爆炸 (High Cardinality)

Negative
: 嚴禁將動態變數（如用戶 ID、訂單 ID、時間戳）直接拼接在 URL 或 Tag 中！  
**錯誤示範**：`http.get('/api/users/' + userId)` ❌  
當萬人併發產生 10,000 個不同 URL 時，k6 會為每個獨立 URL 創建一組指標，導致 Prometheus 時序資料庫瞬間 OOM 崩潰！  
**正確示範**：使用模板標籤函式：  
```javascript
http.get(http.url`https://api.example.com/users/${userId}`); // ✔️ 自動聚合為單一維度
```

---

### 熔斷止損機制 (Circuit Breaker with `abortOnFail`)

想像一個情境：你在深夜排程了一場長達 **2 小時** 的耐久壓力測試。然而在測試開始第 **30 秒**，資料庫連線池就被擊穿，後端全部狂噴 500 錯誤。

如果沒有保護機制，k6 將會繼續無腦發送請求長達 1 小時 59 分鐘：
- 消耗數十萬次無效的雲端伺服器運算資源。
- 產生數十 GB 的垃圾日誌，塞爆 ElasticSearch 或 Loki。
- 甚至將測試環境的資料庫打到磁碟鎖死或核心崩潰！

#### `abortOnFail` 與 `delayAbortEval` 實戰配置

k6 提供了企業級熔斷急停機制：

```javascript
export const options = {
  thresholds: {
    // 當錯誤率突破 10% 時，立刻腰斬中止壓測！
    'http_req_failed': [
      {
        threshold: 'rate<0.10',
        abortOnFail: true,      // 立即熔斷，中斷整個 k6 行程！
        delayAbortEval: '10s',  // 緩衝 10 秒後再開始評估，防止系統冷啟動時的誤殺！
      },
    ],
    // 關鍵交易成功率門檻
    'checkout_success_rate': [
      {
        threshold: 'rate>0.95',
        abortOnFail: true,
        delayAbortEval: '15s',
      },
    ],
  },
};
```

> **`delayAbortEval` 的重要性**：在壓測啟動的最初幾秒內，快取尚未建立、連線池剛在握手，極端延遲可能短暫飆高。設定 10~15 秒的寬限期，能有效避免冷啟動引發的「假陽性熔斷」。

---

### 自訂結構化報表匯出 (`handleSummary`)

在現代 CI/CD Pipeline 中，測試執行完畢後不能只留下一段終端機文字，工程團隊需要：
1. **JSON 原始數據**：供後續監控平台分析、時序對比或寫入資料庫。
2. **HTML 視覺化報表**：自動歸檔至 GitLab Artifacts 或 GitHub Actions Run，方便工程師直接下載用瀏覽器檢視漂亮圖表。

#### `handleSummary()` 實作範例

```javascript
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.2/index.js';

export function handleSummary(data) {
  console.log('正在生成效能測試歸檔報告...');

  return {
    // 1. 保留終端機標準輸出
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),

    // 2. 匯出結構化全量指標 JSON 檔案
    'test-results/summary.json': JSON.stringify(data, null, 2),

    // 3. 生成簡潔的 Markdown 格式摘要（可用於 PR 留言或 Slack 機器人）
    'test-results/summary.md': generateMarkdownSummary(data),
  };
}

function generateMarkdownSummary(data) {
  const reqs = data.metrics.http_reqs.values.count;
  const p95 = data.metrics.http_req_duration.values['p(95)'].toFixed(2);
  const failRate = (data.metrics.http_req_failed.values.rate * 100).toFixed(2);
  
  return `### 🚀 k6 效能測試摘要報告
- **總請求量**: ${reqs} reqs
- **P95 延遲**: ${p95} ms
- **HTTP 失敗率**: ${failRate} %
`;
}
```

---

### CI/CD 自動卡關核心：Exit Code 99 傳遞鏈

自動化測試的最高境界是**「完全無人值守，代碼自動裁決」**。在 Unix/Linux 世界中，程式結束時回傳的退出碼 (Exit Code) 是管線判定成敗的通用協議。

#### k6 Exit Code 規範

```text
[k6 測試執行結束] 
        │
        ├─── 所有宣告之 Thresholds 門檻全數通過 ───> Exit Code: 0  (CI 通過，允許上線)
        │
        └─── 只要有任何一條 Threshold 門檻違規 ───> Exit Code: 99 (CI 失敗，自動阻斷部署！)
```

#### 1. GitHub Actions 流水線實戰配置

在 `.github/workflows/performance-test.yml` 中：

```yaml
name: Performance Quality Gate

on:
  pull_request:
    branches: [ main ]

jobs:
  k6_load_test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Install k6
        run: |
          sudo gpg -k
          sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update && sudo apt-get install -y k6

      - name: Run k6 Quality Gate
        run: |
          # 若門檻未過，k6 自動 exit 99，GitHub Actions 會立即標記 Step 失敗！
          k6 run --summary-export=summary.json k6/demos/ch3_quality_gates_exit99.js

      - name: Archive Test Results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: k6-test-results
          path: summary.json
```

#### 2. GitLab CI 流水線實戰配置

在 `.gitlab-ci.yml` 中：

```yaml
stages:
  - test
  - deploy

performance_gate:
  stage: test
  image: 
    name: grafana/k6:latest
    entrypoint: [""]
  script:
    - k6 run k6/demos/ch3_quality_gates_exit99.js
  # 當 k6 回傳 99 時，GitLab CI 預設判定 Job Failed，Deploy 階段將被自動取消！
```

---

### 手把手實作演練：驗證品質門禁、標籤分組與熔斷機制 (Quality Gates & Circuit Breaker)

![k6 Chapter 3 品質門禁、標籤分組與熔斷動態輪播](assets/images/k6-ch3-quality-gates.gif)

現在切換到終端機，親身體會自動化門禁的裁決威力、標籤分組的精準隔離效果，以及 `abortOnFail` 熔斷急停的防護機制：

#### 實作 1：驗證通過情境與標籤分組效果（Exit Code 0）

執行腳本並將 `FAIL_SLO` 設為 `false`，觀察四大自訂指標、Tagging 與 Group 的度量輸出：

```bash
k6 run -e FAIL_SLO=false k6/demos/ch3_quality_gates_exit99.js ; echo "CI Exit Code: $?"
```

![DEMO 1: 標籤分組隔離與 SLO 驗證通過成果](assets/images/k6-ch3-cmd1-pass.png)

> **👀 觀察重點**：
> 1. **標籤與分組隔離 (Tagging & Groups)**：終端機清楚呈現 `http_req_duration{api_type:critical}` 以及 `{group:::01_核心結帳交易}`、`{group:::02_背景報表查詢}`，實現微服務端點的精確 SLO 分級治理。
> 2. **四大自訂指標 (Custom Metrics)**：`active_workers_gauge` (Gauge 瞬時水位)、`orders_submitted_total` (Counter 累計)、`business_transaction_success` (Rate 成功率)、`custom_db_processing_duration` (Trend 統計趨勢) 完整呈現。
> 3. **門禁放行**：所有 Thresholds 打上綠色勾勾 `✓`，命令輸出結尾回傳 `CI Exit Code: 0`，代表管線驗證通過！

#### 實作 2：模擬關鍵門檻違規與 CI/CD 卡關（Exit Code 99）

將 `FAIL_SLO` 設為 `true`，刻意將關鍵核心端點的 P95 延遲門檻縮緊至不可能達成的 `1ms`：

```bash
k6 run -e FAIL_SLO=true k6/demos/ch3_quality_gates_exit99.js ; echo "CI Exit Code: $?"
```

![DEMO 2: 標籤精準門禁違規與 Exit Code 99 卡關成果](assets/images/k6-ch3-cmd2-fail-exit99.png)

> **👀 觀察重點**：
> 1. **精準隔離避免全域誤報**：只有打上 `api_type:critical` 標籤的核心端點出現紅色叉叉 `✗ 'p(95)<1'`，而 `background` 背景報表端點依然維持綠色通過，證明標籤過濾能精確定位違規端點。
> 2. **CI 卡關憑證**：k6 輸出 `thresholds on metrics 'http_req_duration{api_type:critical}' have been crossed`，並在結尾回傳 **`CI Exit Code: 99`**！自動阻斷流水線部署。

#### 實作 3：模擬熔斷止損急停機制（abortOnFail: true）

將 `ABORT_TEST` 設為 `true` 模擬後端突然大面積崩潰，觀察 `abortOnFail: true` 如何在毫秒間腰斬測試以止損：

```bash
k6 run -e ABORT_TEST=true k6/demos/ch3_quality_gates_exit99.js ; echo "CI Exit Code: $?"
```

![DEMO 3: 熔斷急停 abortOnFail 止損成果](assets/images/k6-ch3-cmd3-abort-on-fail.png)

> **👀 觀察重點**：
> 1. **測試提早腰斬退出**：原本預計跑 20 次迭代，但在僅完成 30%（第 6 次迭代、運行僅 2.0 秒）時，k6 偵測到業務成功率低於 95%，**立即強制熔斷所有 VU**，停止測試！
> 2. **終端機錯誤通報**：明確輸出 `at least one has abortOnFail enabled, stopping test prematurely`。
> 3. **止損效益**：在真實長達數小時的壓測中，此機制能立即省下數十萬次無效雲端調用與伺服器日誌塞爆風險，並回傳 `CI Exit Code: 99`。

---

### Chapter 3 核心心智模型與 SRE 避坑指南

1. **Check 只是輔助，Threshold 才是法律**：
   - 永遠記得：`check()` 失敗不會讓 CI 停止！若要使錯誤阻斷部署，必須在 `thresholds` 宣告 `'checks': ['rate==1.0']`。
2. **拿掉所有平均值，嚴格遵循 P95 / P99**：
   - 產品 SLA 合約與 SRE 審查一律以百分位數為準，平均值只能當作參考背景值。
3. **分級治理，多用標籤過濾 (Tag Filtering)**：
   - 嚴格隔離 Critical 核心業務與 Background 背景報表端點，避免次要服務的延遲劣化破壞全域發版。
4. **長跑測試務必配置 `abortOnFail`**：
   - 任何超過 30 分鐘的壓力測試，都必須設置錯誤率熔斷，保護測試環境不受毀滅性打擊。

---

## Chapter 4: 邁向真實用戶體驗：流量錄製與 k6 Browser 混合壓測
Duration: 25

### 現代單頁應用 (SPA) 壓測盲區

在前後端分離與 React/Vue/Angular 盛行的現代架構中，只測後端協定層 API 會產生嚴重的效能盲區：

- **協定層 (Protocol-Level, HTTP/gRPC)**：發送純 HTTP 封包，消耗極低資源（單機可模擬數萬 VU），但**完全無法執行 JavaScript**，也無法渲染 DOM。
- **瀏覽器層 (Browser-Level, Headless Chromium)**：啟動真實無頭瀏覽器，完整載入前端靜態資源、解析 DOM、執行 JS Bundle，並採集真實 **Core Web Vitals** 使用者體驗指標。

Positive
: 「後端 API 回應僅 30ms，但前端肥大的 JS Bundle 與重排重繪卡了 3 秒」—— 唯有結合協定層與瀏覽器層，才能看見全鏈路真實效能！

---

### HAR 流量錄製與 Chrome DevTools 四大標準動作

手寫數十隻相依 API 的測試腳本既耗時又容易漏掉 Cookie 或 Header。k6 官方支援將瀏覽器錄製的 **HAR (HTTP Archive)** 檔案一鍵轉換為 k6 腳本。

#### 瀏覽器錄製四大標準動作

1. **開啟無痕視窗 (Incognito Window)**：強制排除所有瀏覽器擴充套件（如 AdBlock、密碼管理員）發出的背景流量干擾。
2. **勾選「Preserve log」**：在 Chrome DevTools 的 Network 面板右上角勾選 **Preserve log**，確保表單跳轉與跨頁重新導向時，歷程不會被清空。
3. **清空現有 Log 後執行業務操作**：點擊 Network 面板的 🚫「Clear」按鈕，接著在畫面上執行完整的端到端操作（例如 QuickPizza 瀏覽首頁、登入、生成推薦披薩）。
4. **匯出 HAR 檔案**：點擊 Network 面板右上方的「Export HAR (含敏感資料選項需謹慎)」，儲存為 `recording.har`。

#### CLI 一鍵轉譯為 k6 腳本

```bash
# 透過 har-to-k6 工具自動轉譯
npx har-to-k6 recording.har -o k6/demos/recording_raw.js
```

---

### HAR 三大清理法則（從玩具到生產級）

直接執行轉譯出的 `recording_raw.js` 會立刻遭遇嚴重的兩大災難：
1. **401 死資料陷阱**：HAR 錄製下來的 `Authorization: Token xxxxx` 是錄製當時的過期 Token，重新發送會收到 `401 Unauthorized`。
2. **Don't load test Google!**：HAR 連同外部 Google Analytics (`google-analytics.com`)、第三方字型或 CDN 都一起錄進去。對第三方服務壓測不僅違法，更會嚴重失真！

#### 清理法則 1：去靜態資源 (Strip External & Static Assets)
剔除第三方追蹤代碼 (`google-analytics.com`、`hotjar` 等) 與非本機靜態資源，將測試焦點完全收斂在待測服務的業務邏輯 API。

#### 清理法則 2：動態關聯 (Dynamic Correlation)
在 `setup()` 生命週期中呼叫真實登入 API，動態取得最新有效憑證 (Auth Token)，並透過 `data` 參數注入給每一個 VU 迴圈使用。

#### 清理法則 3：結構化模組 (Semantic Modularization)
將錄製出來的上百行線性 URL 呼叫，封裝成語意清晰的業務函式（如 `browseHomepage()`、`orderPizza(token)`），方便維護與重用。

#### 程式碼對比：Raw HAR vs 清理後生產級腳本

```javascript
// ❌ recording_raw.js：包含過期死 Token 與第三方統計
let res1 = http.post('https://quickpizza.grafana.com/api/pizza', '{}', {
  headers: {
    'Authorization': 'Token EXPIRED_RECORDED_TOKEN_12345', // 💥 401 Unauthorized!
  },
});
let res2 = http.get('https://www.google-analytics.com/g/collect?...'); // 💥 違規外送流量!
```

```javascript
// ✅ recording_cleaned.js：三大法則清理後的生產級架構
import http from 'k6/http';
import { check, group, sleep } from 'k6';

export const options = {
  vus: 5,
  duration: '5s',
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate<0.01'],
    checks: ['rate==1.0'],
  },
};

// 法則 2：動態關聯 - setup() 獲取即時 Token
export function setup() {
  const loginRes = http.post('https://quickpizza.grafana.com/api/users/token/login', 
    JSON.stringify({ username: 'default', password: '123' }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  return { authToken: loginRes.json('token') };
}

// 法則 3：結構化模組封裝
function browseHomepage() {
  const res = http.get('https://quickpizza.grafana.com/');
  check(res, { '首頁載入成功 (200)': (r) => r.status === 200 });
}

function orderPizza(token) {
  const res = http.post('https://quickpizza.grafana.com/api/pizza', '{}', {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Token ${token}`, // 動態注入有效 Token
    },
  });
  check(res, {
    '動態下單成功 (200)': (r) => r.status === 200,
    '披薩推薦生成成功': (r) => r.json('pizza.name') !== undefined,
  });
}

export default function (data) {
  group('使用者結帳旅程', function () {
    browseHomepage();
    sleep(0.5);
    orderPizza(data.authToken);
    sleep(0.5);
  });
}
```

#### 實作演練：驗證清理後的 HAR 腳本

```bash
k6 run k6/demos/recording_cleaned.js
```

**真實執行終端輸出：**
```text
  █ THRESHOLDS 
    checks .............: rate=100.00%
    http_req_duration ..: p(95)=297.58ms
    http_req_failed ....: rate=0.00%

  █ TOTAL RESULTS 
    checks_total.......: 62      
    checks_succeeded...: 100.00% 62 out of 62
    checks_failed......: 0.00%   0 out of 62

    ✓ 登入成功取得 200
    ✓ 取得有效 Token
    ✓ 首頁載入成功 (200)
    ✓ 動態下單成功 (200)
    ✓ 披薩推薦生成成功
```

---

### k6 Browser：真實 Chromium 渲染與 Core Web Vitals

k6 原生整合 Playwright-like 語法的瀏覽器自動化引擎，能夠在協定測試的同時啟動無頭瀏覽器。

#### 核心指標定義

| 指標 | 全名 | 核心意義 | 業界良好標準 |
| :--- | :--- | :--- | :--- |
| **LCP** | Largest Contentful Paint | 最大內容繪製時間（主視覺何時呈現） | ≤ 2.5s |
| **FCP** | First Contentful Paint | 首次內容繪製時間（白屏時間結束） | ≤ 1.8s |
| **INP** | Interaction to Next Paint | 互動到下次繪製延遲（點擊響應流暢度） | ≤ 200ms |
| **TTFB** | Time to First Byte | 伺服器首位元組時間（後端與網路基礎開銷） | ≤ 800ms |
| **CLS** | Cumulative Layout Shift | 累計版面配置位移（視覺穩定度） | ≤ 0.1 |

Negative
: **資源釋放軍規警告**：操作瀏覽器時，務必將 `await page.close()` 放在 `finally` 區塊中！若腳本在執行途中異常拋出錯誤而略過關閉步驟，伺服器背景將堆積大量未釋放的 Chromium 殭屍行程，迅速吃光主機記憶體與 CPU。

#### 瀏覽器單元測試實作

```bash
k6 run k6/demos/ch4_browser_quickpizza.js
```

**真實採集指標輸出：**
```text
  █ THRESHOLDS 
    browser_web_vital_fcp ..: p(95)=2.27s
    browser_web_vital_lcp ..: p(95)=2.27s
    checks .................: rate=100.00%

  WEB_VITALS
    browser_web_vital_cls...: avg=0       
    browser_web_vital_fcp...: avg=2.27s   
    browser_web_vital_inp...: avg=16ms    
    browser_web_vital_lcp...: avg=2.27s   
    browser_web_vital_ttfb..: avg=587.79ms
```

---

### 99:1 全鏈路混合壓測黃金架構 (Hybrid Testing)

在大型分散式系統中，啟動 1,000 個真實瀏覽器實例通常需要幾十台大型執行節點（每 Chromium VU 約需 50MB~100MB 記憶體），成本極其昂貴。

**99:1 黃金比例架構**以最低成本實現全鏈路壓測：
- **99% Protocol Load (協定負載)**：使用輕量 VU 模擬巨量流量（例如 10,000 RPS），將後端 API、資料庫連線池與微服務網關打至滿載極限。
- **1% Browser Probe (瀏覽器探針)**：在系統遭受協定負載狂轟濫炸時，派出一隻真實 Chromium 探針模擬真實用戶進入首頁與結帳，測量極限壓力下的真實前端 **LCP/INP** 是否惡化！

```
                                      ┌─── 99% Protocol Load (1000 VU) ───> 後端 API 與資料庫滿載
[全鏈路混合壓測 Hybrid Script] ───────┤
                                      └─── 1% Browser Probe (1 VU Chromium) ──> 即時採集風暴下的 LCP/CLS
```

#### 混合壓測多情境腳本架構

```javascript
import { browser } from 'k6/browser';
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  scenarios: {
    // 情境 1：99% 協定層狂轟濫炸 (Protocol Flood)
    protocol_flood: {
      executor: 'constant-vus',
      vus: 10,
      duration: '10s',
      exec: 'protocolScenario',
    },
    // 情境 2：1% 瀏覽器探針 (Browser Probe，在負載建立後延遲進場)
    browser_sample: {
      executor: 'shared-iterations',
      vus: 1,
      iterations: 1,
      startTime: '2s', // 確保後端已有高壓背景負載
      options: { browser: { type: 'chromium' } },
      exec: 'browserScenario',
    },
  },
  thresholds: {
    'http_req_duration{scenario:protocol_flood}': ['p(95)<1000'],
    'browser_web_vital_lcp{scenario:browser_sample}': ['p(90)<3500'],
  },
};

export function protocolScenario() {
  const res = http.get('https://quickpizza.grafana.com/api/pizza');
  check(res, { 'Protocol 狀態碼為 200': (r) => r.status === 200 });
  sleep(0.5);
}

export async function browserScenario() {
  const page = await browser.newPage();
  try {
    await page.goto('https://quickpizza.grafana.com');
    await page.locator('button[name="pizza-please"]').click();
    sleep(1);
  } finally {
    await page.close(); // 確保無頭進程正常釋放
  }
}
```

#### 實作演練：執行 99:1 混合全鏈路壓測

```bash
k6 run k6/demos/ch4_hybrid_99_to_1.js
```

**真實執行終端輸出：**
```text
  █ THRESHOLDS 
    browser_web_vital_lcp{scenario:browser_sample} ...: p(90)=2.1s (門檻 <3500ms ✓)
    http_req_duration{scenario:protocol_flood} .......: p(95)=193.65ms (門檻 <1000ms ✓)
    http_req_failed{scenario:protocol_flood} .........: rate=0.00% (門檻 <5% ✓)

  █ TOTAL RESULTS 
    checks_succeeded...: 100.00% 140 out of 140
    http_reqs..........: 280 (協定層成功轟出 280 次 API 請求)
    
    WEB_VITALS (在滿載壓力下之瀏覽器採樣)
    browser_web_vital_fcp...........: avg=2.1s
    browser_web_vital_inp...........: avg=24ms
    browser_web_vital_lcp...........: avg=2.1s
    browser_web_vital_ttfb..........: avg=587.9ms

  running (00m10.3s), 00/11 VUs, 141 complete iterations
  protocol_flood ✓ [ 100% ] 10 VUs  10s            
  browser_sample ✓ [ 100% ] 1 VUs   00m03.6s/10m0s
```

Positive
: 混合壓測以 10 個協定 VU 轟擊出 280 次請求，平均延遲僅 98ms；同時 Chromium 探針即時回報 LCP 為 2.1s、INP 為 24ms，雙邊 SLO 均成功達標！

---

## Chapter 5: 生態系擴充與全視角可觀測性整合
Duration: 25

### 破除效能數據孤島：壓測納入全視角可觀測性體系

在傳統企業研發中，效能測試最常遭遇的致命瓶頸是：**「測試數據永遠是一座孤島」**。

當測試人員在終端機中看到 P95 延遲從 50ms 突然飆升至 2,000ms 時，由於缺乏系統內部視角，往往只能在 Slack 群組中盲目猜測：「是資料庫慢了嗎？還是微服務代碼寫爛了？或是網路交換機掉包？」各團隊各執一詞，排查瓶頸曠日廢時。

在現代雲原生架構下，效能測試不應是單獨的「黑盒跑分」，而應是**全視角可觀測性 (Unified Observability) 的核心觸發源**。壓測產生的負載指標，必須與後端微服務的**分散式追蹤 (Tracing)**、**日誌 (Logs)** 以及**主機與容器指標 (Metrics)** 在同一個時間軸上無縫對齊：

```text
                        ┌─────────────────────────────────┐
                        │   Grafana 統一可觀測性監控中心    │
                        │   (Unified Observability Hub)   │
                        └────────────────┬────────────────┘
                                         │ (時間軸同步 / 共享十字準星)
       ┌─────────────────────────────────┼─────────────────────────────────┐
       ▼                                 ▼                                 ▼
【應用層分散式追蹤】              【系統基礎設施時序】              【k6 壓測客戶端時序】
OpenTelemetry Collector          Prometheus (cAdvisor / Node)      Prometheus Remote Write
- Trace ID / Span 鏈路耗時        - Pod CPU CFS Throttling 限流     - http_req_duration (P95/P99)
- Database SQL 慢查詢            - 記憶體 WorkingSet / OOMKilled   - 即時吞吐量 (RPS)
- 跨微服務下游 RPC 呼叫           - 網路連線池 Socket 佔用           - dropped_iterations 容量告警
```

---

### 原生 Web Dashboard 即時監控與 CI/CD 離線報告

以往要在測試期間看到動態曲線圖，必須架設 InfluxDB、安裝 Telegraf、或部署完整的 Prometheus 與 Grafana，架構沉重且維護成本高昂。

k6 自 v0.49+ 起正式內建了**原生 Web Dashboard**：單一二進位檔內建 HTTP Web 服務，透過 WebSocket 即時串流 VU、RPS、P95 延遲、狀態碼與細分網路時間線，**零外部依賴、一行指令即可啟動！**

#### 1. 本地即時動態儀表板

執行壓測時，只需注入環境變數 `K6_WEB_DASHBOARD=true`：

```bash
K6_WEB_DASHBOARD=true k6 run k6/demos/ch5_dashboard_and_html_summary.js
```

> **瀏覽器即時訪問**：打開 `http://127.0.0.1:5665`，即可看見極具質感的深色系儀表板，即時動態繪製請求吞吐、P95 延遲、錯誤率以及 Thresholds 門檻達成進度！

![k6 原生 Web Dashboard 本地即時動態儀表板 (http://127.0.0.1:5665)](assets/images/k6-ch5-web-dashboard.png)

#### 2. 自訂監聽連接埠與遠端綁定

若在遠端 Linux 測試機上執行，可綁定 `0.0.0.0` 允許辦公室內部網路訪問：

```bash
K6_WEB_DASHBOARD=true \
K6_WEB_DASHBOARD_HOST=0.0.0.0 \
K6_WEB_DASHBOARD_PORT=8080 \
k6 run script.js
```

#### 3. CI/CD 無人值守匯出靜態 HTML：Port=-1 退場神技

在 GitHub Actions 或 GitLab CI 等自動化流水線中，容器是無人值守的，不需要開啟 Web 伺服器監聽連接埠；如果啟動了 Web 伺服器，流水線反而會因連接埠未釋放而卡死掛起。

k6 提供了一個優雅的解法——**`K6_WEB_DASHBOARD_PORT=-1`**：

```bash
K6_WEB_DASHBOARD=true \
K6_WEB_DASHBOARD_PORT=-1 \
K6_WEB_DASHBOARD_EXPORT=test-report.html \
k6 run script.js
```

- **底層運作機制**：設定 `PORT=-1` 會完全停用本地 HTTP 伺服器監聽，但保留 Dashboard 的圖表渲染引擎。在測試執行完畢的瞬間，k6 自動將所有動態圖表、數據序列完整封裝成一份**「獨立、單一、無伺服器依賴的靜態 HTML 檔案」**！
- **CI/CD 價值**：生成的 `test-report.html` 可作為 Build Artifact 一鍵上傳歸檔，開發者只需下載並用任何瀏覽器打開，即可檢視完整的互動圖表。

---

### 自訂結構化報表產生器 (`handleSummary`)

除了原生 Web Dashboard，k6 還提供了強大的生命週期鉤子函式——**`handleSummary(data)`**。當壓測結束時，k6 會將整場測試的全量統計數據（包含所有內建與自訂指標）打包傳遞給該函式，由開發者自由客製化輸出格式。

#### `handleSummary()` 多目標輸出範例

在腳本中導出 `handleSummary`，可同時生成終端機輸出、JSON 機器可讀數據與客製化 HTML：

```javascript
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.2/index.js';

export function handleSummary(data) {
  console.log('>>> [handleSummary] 測試結束，正在處理自訂報告輸出...');

  const p95 = data.metrics.http_req_duration ? data.metrics.http_req_duration.values['p(95)'].toFixed(2) : 'N/A';
  const totalReqs = data.metrics.http_reqs ? data.metrics.http_reqs.values.count : 0;
  const failedRate = data.metrics.http_req_failed ? (data.metrics.http_req_failed.values.rate * 100).toFixed(2) : '0';

  // 產生輕量自訂 HTML 報表
  const customHtml = `
  <!DOCTYPE html>
  <html>
  <head>
    <meta charset="utf-8">
    <title>k6 效能測試執行摘要</title>
    <style>
      body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 30px; background: #0b0c10; color: #c5c6c7; }
      .card { background: #1f2833; border-radius: 8px; padding: 20px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }
      h1 { color: #66fcf1; font-size: 22px; margin-top: 0; }
      .metric { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #45a29e; }
      .label { color: #c5c6c7; }
      .value { color: #45a29e; font-weight: bold; font-family: monospace; }
      .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
      .pass { background: #2ecc71; color: #000; }
    </style>
  </head>
  <body>
    <div class="card">
      <h1>🚀 k6 效能測試執行摘要</h1>
      <div class="metric"><span class="label">總請求數</span><span class="value">${totalReqs} reqs</span></div>
      <div class="metric"><span class="label">P95 回應延遲</span><span class="value">${p95} ms</span></div>
      <div class="metric"><span class="label">HTTP 失敗率</span><span class="value">${failedRate} %</span></div>
      <div class="metric"><span class="label">品質門禁狀態</span><span class="badge pass">PASSED</span></div>
    </div>
  </body>
  </html>
  `;

  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }), // 終端機依然印出標準摘要
    'summary.json': JSON.stringify(data, null, 2),                   // 匯出 JSON 供 CI/CD 分析
    'custom_report.html': customHtml,                                // 匯出自訂 HTML
  };
}
```

![handleSummary 自訂 HTML 獨立報表產出成果](assets/images/k6-ch5-handlesummary-report.png)

---

### xk6 模組化擴充機制與 Go-to-JS Bridge 深度解密

k6 原生核心專注於 HTTP、WebSocket、gRPC 與 Browser 協定。但當企業微服務架構需要壓測以下組件時：
- **消息隊列**：直接對 Apache Kafka 或 RabbitMQ 進行高頻收發壓測。
- **資料庫連接池**：繞過 Web API，直接對 PostgreSQL、MySQL 或 SQL Server 發送百萬級 SQL 語句。
- **分散式快取**：直接對 Redis Cluster 發起批量快取讀寫，驗證快取穿透防禦。
- **物聯網通訊**：對 MQTT 或 CoAP Broker 進行百萬物聯網設備連線測試。

原生 k6 無法直接支援上述協定。為此，Grafana 開發了專屬的擴充架構——**xk6 (eXtensible k6)**！

#### Go-to-JS Bridge 底層架構

xk6 的底層設計極其精妙：
1. **Go Native 生態庫**：開發者可以使用 Go 語言龐大成熟的開源庫（如 `confluent-kafka-go`、`pgx`、`go-redis`）。
2. **Go-to-JS Bridge 反射機制**：xk6 透過 Goja JS 引擎的 Type Reflection，自動將 Go 結構體、方法包裝成符合 ES6 標準的 JavaScript 類別與模組。
3. **極致效能與敏捷開發並存**：壓測工程師依然使用熟悉的 JavaScript 撰寫測試腳本，但在執行時，底層是 Go 原生編譯後的機器碼與輕量 Goroutine 在發起網路通訊，效能零損耗！

```text
[ 壓測工程師編寫的 JavaScript 腳本 ]
  import sql from 'k6/x/sql';
  sql.query("SELECT * FROM users WHERE id = ?", 101);
                     │
                     ▼ (Goja JS Runtime)
[ Go-to-JS Bridge 模組橋接層 ]
                     │
                     ▼ (Go Native Code)
[ Go 原生驅動程式 (database/sql, lib/pq, pgx) ] ──> [ 直接壓測 PostgreSQL / MySQL 資料庫 ]
```

#### 擴充套件雙引擎分類

| 擴充套件分類 | 代表性模組 | 核心功能 | 適用場景 |
| :--- | :--- | :--- | :--- |
| **JS Extensions (協定與中間件擴充)** | `xk6-kafka`<br>`xk6-sql`<br>`xk6-redis`<br>`xk6-amqp` | 在 JavaScript 中擴充全新全域物件與通訊協定 | 直接壓測 Kafka、PostgreSQL、MySQL、Redis 等底層中間件 |
| **Output Extensions (時序指標匯出擴充)** | `xk6-output-timescaledb`<br>`xk6-output-kafka`<br>`xk6-output-influxdb` | 攔截 k6 產生的每一筆指標並即時轉發 | 將高頻壓測時序串流即時寫入 TimescaleDB、Kafka 或 Datadog |

Positive
: **講師實戰手記：手把手從零開發 Web3 OTP 插件**  
: 想深入了解如何親手用 Go 語言撰寫一個 xk6 擴充插件嗎？推薦研讀講師專欄文章：[Grafana xk6: 手把手從開發 k6 插件程式到編譯出 k6 插件](https://ganhua.wang/grafana-xk6)。文章詳細拆解了 Go-to-JS 橋接的 `RootModule` 與 `ModuleInstance` 生命週期，並以 Web3 身份驗證為例，實作高併發動態生成一次性密碼 (OTP) 與簽名的自訂模組！

---

### xk6 Docker 確定性編譯實戰 (Deterministic Build)

要在本地編譯 xk6 擴充套件，傳統上需要安裝特定版本的 Go 編譯環境、配置 GOPATH、處理 CGO 與本機依賴，極容易因為環境差異導致「在我的電腦可以跑，在 CI/CD 卻編譯失敗」的窘境。

最佳實踐是使用官方提供的 Docker 映像檔 **`grafana/xk6`** 進行**確定性編譯 (Deterministic Build)**。

#### Docker 編譯兩大軍規避坑點

Negative
: 1. **目錄掛載避坑 (`-v "$(pwd)/bin:/xk6"`)**：官方 `grafana/xk6` 容器的預設工作目錄是 `/xk6`。若掛載路徑寫錯，編譯產出的 `k6` 二進位檔會被遺留在已被銷毀的容器層中，本機空空如也！  
: 2. **使用者權限避坑 (`-u "$(id -u):$(id -g)"`)**：Docker 預設以 `root` 執行。如果不指定本機用戶的 UID/GID，編譯產生的客製化 `k6` 檔案權限會屬於 `root:root`，導致本機一般使用者無法執行、無法覆寫、甚至 CI Runner 刪除 Workspace 時噴出 Permission Denied！

#### 生產級 Docker 確定性編譯指令

以下腳本展示如何一鍵編譯支援 `xk6-sql` 的客製化 k6 引擎：

```bash
OUTPUT_DIR="$(pwd)/bin"
mkdir -p "${OUTPUT_DIR}"

docker run --rm \
  -u "$(id -u):$(id -g)" \
  -v "${OUTPUT_DIR}:/xk6" \
  grafana/xk6 build latest \
  --with github.com/grafana/xk6-sql \
  --output /xk6/k6-custom

# 驗證客製化二進位檔
"${OUTPUT_DIR}/k6-custom" version
```

---

### Prometheus Remote Write 串流與 Git Commit Tag 版本追蹤

#### 從「事後輪詢 (Pull)」到「即時推播 (Remote Write)」

Prometheus 傳統上使用定時「拉取 (Scrape)」機制（例如每 15 秒抓取一次 `/metrics` 端點）。但效能測試往往持續數秒至數分鐘，且流量以毫秒級劇烈震盪：
- 若用傳統 Scrape，高併發下的瞬時延遲突波極易落在採樣間隔之外而被漏採。
- k6 內建的 **Prometheus Remote Write (`-o experimental-prometheus-rw`)** 機制，採用時序數據串流推播（Push）。測試進行時，k6 會將採集到的指標透過 Protocol Buffers 序列化並以 Snappy 壓縮，每秒即時推送給 Prometheus！

#### 前置條件：Prometheus 啟用 Remote Write 接收器

在 Prometheus 的啟動參數中必須顯式啟用：
```yaml
# prometheus.yml 或 Docker 啟動指令：
--web.enable-remote-write-receiver
```

> **本 Lab 環境**：本專案 Docker Compose 中的 Prometheus 容器已經預先配置並啟用了該參數，接收端點為 `http://localhost:9090/api/v1/write`。

#### 注入 Git Commit Tag 實現 A/B 版本回歸對比

壓測最具商業價值之處，是「**發版前後的效能對比 (Regression Testing)**」：這次 PR 改動了 ORM 查詢，API 是變快了還是變慢了？

透過動態注入 Git 標籤，每筆時序指標都帶有確切的版本元數據：

```bash
COMMIT_ID=$(git rev-parse --short HEAD 2>/dev/null || echo "demo-rev1")
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")

K6_PROMETHEUS_RW_SERVER_URL=http://localhost:9090/api/v1/write \
K6_PROMETHEUS_RW_TREND_STATS="p(90),p(95),p(99),min,max,avg,med" \
k6 run \
  -o experimental-prometheus-rw \
  --tag "commit_id=${COMMIT_ID}" \
  --tag "git_branch=${BRANCH_NAME}" \
  --tag "environment=staging" \
  script.js
```

在 Grafana 中，只需將儀表板的變數 (Variables) 綁定為 `label_values(k6_http_req_duration_p95, commit_id)`，即可透過下拉選單自由切換不同的 Git Commit，同屏對比兩次發版的 P95 延遲曲線！

![Grafana 統一可觀測性效能監控儀表板 (Prometheus Remote Write 串流)](assets/images/k6-ch5-grafana-dashboard.png)

---

### 顛峰時刻：Grafana 雙十字準星全視角對齊 (Crosshair Convergence)

什麼是全視角可觀測性帶來的降維打擊？請看以下真實生產環境除錯案例：

#### 真實破案現場：神秘的 14:02 延遲雪崩

某電商平台進行促銷壓測時，在下午 `14:02:00`，k6 回報的 API P95 延遲突然出現**垂直暴衝**：從原本平穩的 `45ms` 瞬間飆高至 `2,200ms`！

```text
[14:02:00]  k6 API P95 延遲曲線   ──> 突然垂直暴衝至 2.2 秒！
[14:02:00]  K8s Pod CPU CFS 限流 ──> 同一秒飆高至 85%！
```

#### 傳統盲猜 vs 雙十字準星秒級破案

1. **傳統盲猜**：
   - 後端工程師猜測：「是不是資料庫連線池被佔滿了？」$\rightarrow$ 檢查 DB 監控，連線數平穩。
   - 運維工程師猜測：「是不是 Java JVM 發生了 Full GC Stop-the-World？」$\rightarrow$ 檢查 GC Log，無異常。
   - 網路工程師猜測：「是不是負載平衡器丟包？」$\rightarrow$ 檢查 Nginx 錯誤日誌，無 502/504。
2. **Grafana 共享十字準星 (Shared Crosshair) 秒級破案**：
   - 在 Grafana 面板設定中開啟 `Shared crosshair`。
   - 當滑鼠游標停留在 `14:02:00` 的延遲飆高尖峰時，垂直標記線同步貫穿下方所有的基礎設施監控圖表。
   - **真兇瞬間現形**：在下方 cAdvisor 監控圖表中，該服務 Pod 的 **`container_cpu_cfs_throttled_periods_total` (CPU CFS 限流比率)** 在 `14:02:00` 整整飆升至 **85%**！

> **結論**：根本不是程式碼有 Bug，也不是資料庫變慢，而是 Kubernetes Deployment 的 `resources.limits.cpu: "500m"` 設得過於嚴格！Linux Completely Fair Scheduler (CFS) 在容器用滿 500m 配額後，強制把容器凍結降頻，直到下一個 CPU 週期。  
> 將 CPU Limit 調高至 `1000m` 後重新壓測，P95 延遲瞬間恢復至 45ms！  
> **這就是將壓測指標與基礎設施指標對齊帶來的神級除錯威力：徹底破除數據孤島，秒級定位架構真兇！**

---

### 手把手實作演練：可觀測性全鏈路閉環

![k6 Chapter 5 全鏈路可觀測性實戰展示 (3 大場景動態輪播)](assets/images/k6-ch5-observability-demo.gif)

現在切換到終端機，親自實操原生 Web Dashboard、自訂報告產生器、Docker 編譯與 Prometheus 串流推播。

#### 實作 1：啟動原生 Web Dashboard 即時監控

```bash
K6_WEB_DASHBOARD=true k6 run k6/demos/ch5_dashboard_and_html_summary.js
```

![DEMO 1: 本地即時動態儀表板 (Native Web Dashboard)](assets/images/k6-ch5-web-dashboard.png)

> **👀 觀察重點**：
> 1. 控制台輸出提示：`Web dashboard: http://127.0.0.1:5665`。
> 2. 打開瀏覽器訪問該網址，觀察測試執行期間圖表即時繪製的動態曲線（包含 HTTP Req Rate、P95 Latency、Active VUs 等）！
> 3. 測試完成後可點擊右上角「REPORT」按鈕直接匯出單一靜態 HTML 報告。

#### 實作 2：CI/CD 離線 HTML 報告匯出與 handleSummary 客製化（Port=-1 驗證）

```bash
K6_WEB_DASHBOARD=true \
K6_WEB_DASHBOARD_PORT=-1 \
K6_WEB_DASHBOARD_EXPORT=offline_report.html \
k6 run k6/demos/ch5_dashboard_and_html_summary.js
```

![DEMO 2: handleSummary 自訂獨立 HTML 報告產出](assets/images/k6-ch5-handlesummary-report.png)

> **👀 觀察重點**：
> 1. **無人值守退場**：設定 `K6_WEB_DASHBOARD_PORT=-1` 後，k6 不會卡在 Web 伺服器監聽，測試結束立即正常退出（Exit Code 0）。
> 2. **雙重報表產出**：本地同時生成官方格式 `offline_report.html` 以及由 `handleSummary` 鉤子客製化生成的 `custom_report.html` 與 `summary.json`。
> 3. **極致輕量**：`custom_report.html` 體積極小且自包含 CSS，非常適合在 GitLab CI / GitHub Actions 中做為 Artifact 發布或由 Bot 推送到團隊 IM。

#### 實作 3：Docker 確定性編譯客製化 xk6 引擎

在專案中執行內建的編譯腳本：

```bash
./k6/demos/ch5_xk6_docker_build.sh
```

> **👀 觀察重點**：
> 1. 觀察 Docker 自動拉取 `grafana/xk6` 映像檔並注入 `xk6-sql` 擴充。
> 2. 編譯完成後，檢視 `bin/k6-custom version`，確認已成功打包資料庫原生壓測引擎！

#### 實作 4：Prometheus Remote Write 串流與 Grafana 統一儀表板

執行專案內建的 Prometheus 推播腳本：

```bash
./k6/demos/ch5_prometheus_remote_write.sh
```

![DEMO 3: Prometheus Remote Write 與 Grafana 統一效能工程儀表板](assets/images/k6-ch5-grafana-dashboard.png)

> **👀 觀察重點**：
> 1. **自動注入版本標籤**：腳本動態取得本機當前 Git Commit Short Hash（如 `2b367bd`）與 Git Branch。
> 2. **每秒即時串流推送**：k6 透過 `-o experimental-prometheus-rw` 將每秒數據以 Snappy 壓縮推送至本機 Prometheus (`http://localhost:9090/api/v1/write`)。
> 3. **Grafana 開箱即用儀表板**：打開本專案 Grafana ([http://localhost:3000/d/k6-live-metrics/](http://localhost:3000/d/k6-live-metrics/)，帳密 `admin/admin`)，儀表板已預先配置完成，即時呈現：
>    - **Total Requests / P95 Duration / Active VUs / Business Success Rate** 核心指標。
>    - **HTTP Request Duration Percentiles (P90 / P95 / P99)** 延遲趨勢圖。
>    - **Requests by Tagged Endpoint** 端點維度佔比分析圓環圖。
>    - 右上角可依照 `commit_id`、`git_branch` 與 `environment` 動態過濾，實現跨版本的基準線對比！

---

### 推薦延伸閱讀：講師深度實戰專欄 (Author's Deep-Dive Articles)

為了讓大家在現代進階壓測、外掛生態系開發與前端混合壓測上持續精進，強烈推薦研讀講師親自撰寫的 k6 系列深度實戰專欄：

#### 1. 模組擴充：[Grafana xk6: 手把手從開發 k6 插件程式到編譯出 k6 插件](https://ganhua.wang/grafana-xk6)
- **核心價值**：當原生 k6 不支援特定私有協定或加密簽名演算法時，教你如何用 Go 語言量身打造客製化擴充插件。
- **精彩重點**：
  - **Go-to-JS 模組架構**：深入剖析 `RootModule`、`ModuleInstance` 與 `modules.Register` 註冊機制的設計原理。
  - **Web3 OTP 實戰案例**：以 Web3 動態身份驗證為背景，手把手實作 `k6/x/otp` 擴充套件，在壓測過程中高併發生成動態金鑰與一次性密碼。
  - **容器化確定性編譯**：完整演示如何利用 `grafana/xk6` Docker 容器執行確定性編譯，產出可在不同 Linux 環境穩定運行的客製化 k6 二進位檔。

#### 2. 前端混壓：[Grafana k6 瀏覽器測試 (k6-browser)](https://ganhua.wang/grafana-k6-browser)
- **核心價值**：從協議層壓測跨足真實瀏覽器體驗測試，掌握現代前端 Core Web Vitals 與 SPA 動態渲染瓶頸。
- **精彩重點**：
  - **Playwright 相容生態**：解析 k6 browser 如何借鑑 Playwright API 設計，使用熟悉的 `chromium.launch()`、`page.goto()` 與 `page.locator()` 快速上手。
  - **隔離上下文架構**：使用 `BrowserContext` 在單一瀏覽器處理程序中實現完全獨立的 Cookie、Session 與 LocalStorage 隔離，大幅降低多用戶模擬的記憶體開銷。
  - **真實電商場景演練**：以 OpenTelemetry Demo 購物車為例，示範商品瀏覽、加入購物車、表單填寫與結帳的全鏈路自動化測試，並透過截圖 (Screenshot) 保存錯誤現場。

#### 3. 全鏈路閉環：[Getting Started with Grafana k6: Hands-on Practice](https://ganhua.wang/getting-started-with-grafana-k6-hands-on-practice)
- **核心價值**：結合微服務可觀測性標準（OpenTelemetry Demo）與 CI/CD 流水線的工程化全鏈路實踐。
- **精彩重點**：
  - **結構化測試腳本**：運用 `k6/http`、`check` 與 `group` 模組化組織壓測事務，清晰呈現業務場景階層。
  - **可觀測性串流對齊**：示範如何將壓測指標對接 OpenTelemetry Collector，實現 Metrics、Traces 與 Logs 的跨維度關聯分析。
  - **GitLab CI 自動化門禁**：將 k6 壓測無縫整合至 GitLab CI 流水線中，以 Exit Code 自動守護主幹代碼發版品質。

---

### Chapter 5 核心心智模型與架構師避坑指南

1. **數據不落地，壓測無意義**：
   - 嚴禁把壓測結果留在個人電腦的終端機裡。在 CI/CD 中，至少透過 `Port=-1` 匯出 HTML 報告歸檔，最佳做法是一律透過 Prometheus Remote Write 匯入團隊共享的 Grafana。
2. **善用 Commit Tag 建立效能基準線 (Baseline)**：
   - 每一次合併到 `main` 分支的代碼都必須帶有 Commit ID 進行回歸壓測。當延遲退化時，一眼即可看出是哪一次 Commit 引入的效能退化。
3. **編譯 xk6 嚴格遵守 Docker 確定性原則**：
   - 避免在個人電腦隨意 `go install`。統一使用 Docker 映像檔編譯，並嚴格加上 `-u $(id -u):$(id -g)` 確保檔案權限正常。
4. **結合分散式追蹤 (Tracing) 與主機監控破除盲區**：
   - 當 P95 飆高時，第一時間看 CPU CFS Throttling、記憶體分頁錯誤與 DB 連線池水位，拒絕憑感覺除錯。

---

## 總結與企業導入實作指南
Duration: 5

### 企業導入實作 Checklist

恭喜你完成全部課程！在團隊中推動效能工程落地時，請依循以下五部曲：

1. **測試代碼化**：所有 k6 腳本與微服務應用代碼納入同一個 Git 儲存庫進行版本控管與審查。
2. **SLO 量化**：拋棄平均值，明確訂定 P95/P99 尾端延遲門檻與錯誤率容忍度。
3. **門禁自動化**：以 Exit Code 99 在 CI/CD 中自動守護生產主幹，並配置 `abortOnFail` 及時止損。
4. **全鏈路混合**：落實 99:1 黃金配比，以最低成本兼顧後端叢集負載與前端真實渲染體驗。
5. **可觀測性閉環**：透過 Prometheus Remote Write 將壓測數據時序化，於 Grafana 與 APM 分散式追蹤雙向對齊。

### 延伸資源與原始碼清單

- **Grafana k6 官方網站**：[https://grafana.com/docs/k6/latest/](https://grafana.com/docs/k6/latest/) (Grafana Labs)
- **Grafana k6 官方 GitHub**：[https://github.com/grafana/k6](https://github.com/grafana/k6)
- **專案原始碼**：[`o11y_lab_for_dummies`](https://github.com/tedmax100/o11y_lab_for_dummies)
- **實機演示腳本全集**：[`k6/demos/`](https://github.com/tedmax100/o11y_lab_for_dummies/tree/main/k6/demos)
- **全系列簡報 PPTX**：[`k6/slides/`](https://github.com/tedmax100/o11y_lab_for_dummies/tree/main/k6/slides)
- **錄課口播逐字稿**：[`k6/slides/transcripts/`](https://github.com/tedmax100/o11y_lab_for_dummies/tree/main/k6/slides/transcripts)
- **講師深度實戰專欄 (推薦必讀)**：
  - [Grafana xk6: 手把手從開發 k6 插件程式到編譯出 k6 插件](https://ganhua.wang/grafana-xk6)
  - [Grafana k6 瀏覽器測試 (k6-browser)](https://ganhua.wang/grafana-k6-browser)
  - [Getting Started with Grafana k6: Hands-on Practice](https://ganhua.wang/getting-started-with-grafana-k6-hands-on-practice)
