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

本教學為全系列 **6 大章節線上課程**的完整互動式實作指引，帶領你從零打造現代化、代碼化（Testing as Code）的企業級效能防線。

![課程路線圖：Chapter 1 核心哲學 → Chapter 2 流量建模 → Chapter 3 品質門禁 → Chapter 4 混合壓測 → Chapter 5 可觀測性閉環 → Chapter 6 AI Agent 工程，以及各章重點](assets/images/k6-diagram-course-roadmap.png)

### 你將學到什麼

- **Testing as Code**：告別 XML 點擊操作，使用標準 ES6 JavaScript 撰寫高維護性的測試腳本。
- **Go 語言並發威力**：理解 Goroutine 如何在單機上以遠低於傳統執行緒模型的資源驅動數萬並發用戶。
- **科學化流量建模**：破解「協調性漏測 (Coordinated Omission)」盲點，運用利特爾法則（Little's Law）配置開放模型。
- **看懂測試結果**：用 5 步驟 SOP 判讀 k6 結尾摘要，從儀表板的 8 種曲線型態找出系統飽和的「拐點」，並判讀 Soak 長跑的洩漏訊號。
- **精準品質門禁 (Quality Gates)**：依 SLO 推導 P95/P99 尾端延遲門檻，以 **Exit Code 99** 在 CI/CD 中自動阻斷不良發布。
- **全鏈路混合壓測 (Hybrid Testing)**：打造 **99:1 黃金配比**，兼顧後端高壓與前端 Core Web Vitals (LCP/INP/CLS) 真實渲染體驗。
- **可觀測性閉環**：接入 Prometheus Remote Write 與 Grafana，實現 API 延遲突波與 Kubernetes CPU CFS Throttling 雙時間軸對齊除錯。

### 實驗環境要求

- **作業系統**：Linux、macOS 或 Windows (WSL2)
- **硬體建議**：至少 4 核心 CPU、8GB RAM
- **必要工具**：
  - `k6` CLI v2.x（本課程以 v2.2.0 錄製與實測）
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
| **單 VU 記憶體開銷** | 數 MB（Thread Stack + JVM 物件） | **簡單腳本約 1MB ~ 5MB**（每個 VU 含一個獨立 Goja JS Runtime） |
| **Context Switch 開銷** | 高 (由作業系統核心頻繁排程) | 極低 (由 Go Runtime 在使用者空間高效調度) |
| **單機併發能力** | 約 1,000 ~ 2,000 VUs 即達硬體瓶頸 | **單台高規格機器可達 30,000 ~ 40,000 VUs** |

Negative
: **常見誤解**：Goroutine 本身的初始堆疊只有約 2KB~4KB，但一個 k6 VU **不等於**一個 Goroutine——每個 VU 都有自己的 JS Runtime、模組與資料。官方文件（Running large tests）給的估算是**簡單腳本每 VU 約 1~5MB**（1,000 VUs ≈ 1~5GB），瀏覽器 VU 更高。規劃壓測機前，建議先用 100 VUs 實測記憶體再等比例放大。

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

輸出範例：`k6 v2.2.0 (commit/00a9a1b7f5, go1.26.5, linux/amd64)`，確認出現版本資訊即代表安裝成功！

---

### k6 CLI x AI 現代化工作流 (Configure AI Assistant & MCP)

隨著生成式 AI 技術成熟，現代效能工程不僅走向代碼化（Testing as Code），更邁入 **AI 智慧賦能時代**。Grafana k6 官方正式推出基於 **Model Context Protocol (MCP)** 的整合方案，將 k6 CLI 與現代 AI 助手（Cursor、Claude Desktop、VS Code Copilot、Antigravity 等）無縫串接。

#### 1. 什麼是 k6 MCP Server？

Model Context Protocol (MCP) 是一項開放協議，允許大語言模型安全地存取本地工具與上下文。在新版 k6（本課程使用 v2.2.0）中，MCP 伺服器直接以**子命令 `k6 x mcp`** 形式提供（透過 Automatic Extension Resolution 按需下載，無須 Node.js/npm），讓 AI 助手具備以下能力：
- 取得官方最新 k6 API 與最佳實踐文檔。
- 在代碼編輯器中自動語法靜態檢驗。
- 直接驅動 k6 執行壓測並即時解析測試指標。

#### 2. 快速設定 k6 MCP Server

在支援 MCP 的工具（如 Claude Code、Cursor 或 VS Code Copilot）的設定檔中，註冊本機 k6 子命令即可：

```json
{
  "mcpServers": {
    "k6": {
      "command": "k6",
      "args": ["x", "mcp"]
    }
  }
}
```

> 不想手動改設定檔？Chapter 6 介紹的 `k6 x agent init <editor>` 會自動幫你寫好這份設定，並一併安裝 k6 AI 技能包。

#### 3. MCP 工具庫 (Tools)、提示詞 (Prompts) 與資源 (Resources)

k6 MCP Server 為 AI 助手賦予了三類關鍵能力：

- **工具 (Tools)**（共 6 個，Chapter 6 有完整實作）：
  - `validate_script`：在正式壓測前，以 1 VU / 1 次迭代實際執行腳本，提早揪出語法錯誤、模組引用錯誤或端點無法連線等問題。
  - `run_script`：允許 AI 助手直接在本機以指定 VU 與 duration 驅動 k6 執行測試，並回傳 RPS、P95 延遲、錯誤率等指標。
  - `get_documentation` / `list_sections`：檢索與瀏覽 k6 官方文件（如 `k6/browser`、thresholds 語法），降低 AI 產出過時 API 的機率。
  - `info`：取得本機 k6 版本與 Grafana Cloud 登入狀態。
  - `search_terraform`：搜尋 Grafana Terraform Provider 中的 k6 Cloud 資源。
- **提示詞模板 (Prompts)**：提供撰寫複雜 k6 腳本的起手式模板。
- **資源 (Resources)**：提供官方腳本撰寫最佳實踐 (Best Practices) 等參考資料。

#### 4. 使用 AI Agent 自主逆向生成完整測試套件 (Bootstrap with k6 x Agent)

以往為一套複雜的後端系統撰寫效能測試需要耗費數天：開發者必須逐一閱讀 API 文件、手寫身分驗證邏輯、設計隨機資料池並校驗斷言。

利用 **Bootstrap with k6 x Agent** 工作流，AI 代理能自主完成全套工程交付：

![Bootstrap with k6 x Agent 工作流：專案代碼/OpenAPI/HAR 規格 → AI Agent 自主解析 → 生成全情境壓測腳本 → validate_script（1 VU 冒煙）＋ run_script → 自動自癒微調 → 生產就緒測試套件](assets/images/k6-diagram-agent-workflow.png)

1. **資產自動探索 (Asset Discovery)**：Agent 讀取專案中的 `openapi.yaml` 或前端網路請求錄製檔（`.har`）。
2. **情境自主建模 (Autonomous Modeling)**：自動拆解出 Smoke、Load、Stress 測試情境，並配置合理的 P95 閾值門禁。
3. **閉環驗證與自癒 (Self-Healing Loop)**：Agent 自動調用 `validate_script` 以 1 個 VU 驗證語法與真實 API 通訊；一旦遇到 401 Unauthorized 或 422 Unprocessable Entity，Agent 自行修正請求標頭與 Body 格式，再以 `run_script` 執行，直到全數 Pass！

Positive
: 透過 k6 CLI 與 AI 助手的深度融合，效能測試從「少數效能專家的專屬重擔」，變成了「每位開發者在 IDE 內隨手即可生成的日常防線」！在後續的 **Chapter 6** 中，我們將專章深入探索 `k6 x agent` 如何以原生雙引擎一鍵配置 11 個 AI 技能包與原生 MCP 伺服器！

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
  const res = http.get('https://quickpizza.grafana.com', {
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

![Options 設定優先順序由高至低：CLI Flags → Environment Variables → In-script options → Default Values](assets/images/k6-diagram-options-precedence.png)

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

##### B. 品質門禁 (Quality Gates & Thresholds)

| Option 屬性 | CLI 旗標 | 型態 / 範例 | 說明與典型場景 |
| :--- | :--- | :--- | :--- |
| `thresholds` | *(無單一旗標)* | 物件 | **宣告式效能門檻**（從 SLO 推導而來，但不等於 SLO，見 Chapter 3）。例如 `http_req_duration: ['p(95)<200']`（95% 請求需在 200ms 內完成）。若失敗則 k6 退出碼非 0，直接熔斷 CI/CD。 |

##### C. 網路協定與連線行為 (Network & Protocols)

| Option 屬性 | CLI 旗標 | 型態 / 範例 | 說明與典型場景 |
| :--- | :--- | :--- | :--- |
| `noConnectionReuse` | `--no-connection-reuse` | 布林（預設 `false`） | **停用 HTTP 連線複用 (Keep-Alive)**。每次請求強制建立全新 TCP/TLS 握手，考驗伺服器高頻建連能力。 |
| `insecureSkipTLSVerify` | `--insecure-skip-tls-verify` | 布林（預設 `false`） | **跳過 SSL 憑證檢查**。在開發或 Staging 環境遇到自簽憑證或無效 HTTPS 時必備。 |
| `rps` | `--rps` | 數值（如 `500`） | **每秒最大請求數上限**（⚠️ 官方不建議使用：它只是粗略節流且不計入重導向等細節）。需要控制 RPS 時，請改用 Chapter 2 的 `constant-arrival-rate` / `ramping-arrival-rate` 開放模型執行器。 |
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

### 用 group() 分段說故事：模擬一趟使用者旅程

真實使用者做的是**「一趟旅程」，而不是「一個請求」**。在 QuickPizza 上，一趟典型的旅程是：逛首頁、要一份披薩推薦、登入後送出評分。只看整體的 `http_req_duration`，你只會知道「系統有點慢」；用 `group()` 把旅程分段，k6 就會**依段落分開統計**，讓你知道「是哪一段慢、慢多少」。

| 段落 | 使用者在做什麼 | 停頓（think time） | 為什麼停這麼久 |
| :-- | :-- | :-- | :-- |
| 瀏覽首頁 | 打開 QuickPizza 首頁 | 1～3 秒 | 掃一眼頁面就往下走 |
| 取得推薦 | 請系統推薦一份披薩 | 3～8 秒 | 看推薦內容、猶豫要不要換一份 |
| 送出評分 | 登入後給這份披薩打分數 | 2～5 秒 | 給分前想一想 |

每一段的停頓時間不同，是因為真實使用者在不同頁面停留的時間本來就不同。如果每一步都固定 `sleep(1)`，送出的流量節奏就不像真人。

旅程的骨架長這樣（完整腳本：`k6/demos/ch1_group_journey.js`）：

```javascript
import http from 'k6/http';
import { group, check, sleep } from 'k6';

export default function () {
  group('瀏覽首頁', function () {
    const res = http.get(`${BASE}/`);
    check(res, { '首頁 200': (r) => r.status === 200 });
    sleep(Math.random() * 2 + 1);   // 掃一眼：1～3 秒
  });

  group('取得推薦', function () {
    const res = http.post(`${BASE}/api/pizza`, '{}', { headers: demoHeaders });
    check(res, { '推薦 200': (r) => r.status === 200 });
    sleep(Math.random() * 5 + 3);   // 挑選猶豫：3～8 秒
  });

  group('送出評分', function () {
    const res = http.post(`${BASE}/api/ratings`, JSON.stringify({ stars: 5, pizza_id: 1 }),
                          { headers: userHeaders });   // 帶登入後的 token
    check(res, { '評分 201': (r) => r.status === 201 });
    sleep(Math.random() * 3 + 2);   // 給分前想一想：2～5 秒
  });
}
```

執行時加上 `--summary-mode=full`：

```bash
k6 run --summary-mode=full k6/demos/ch1_group_journey.js
```

摘要最後會多出每一段自己的區塊（k6 v2.2 對 QuickPizza 實測，節錄）：

```text
  █ GROUP: 瀏覽首頁
    ✓ 首頁 200
    http_req_duration..........: avg=201.1ms  med=201.13ms p(90)=201.56ms p(95)=201.63ms

  █ GROUP: 取得推薦
    ✓ 推薦 200
    http_req_duration..........: avg=266ms    med=266.47ms p(90)=300.72ms p(95)=312.12ms

  █ GROUP: 送出評分
    ✓ 評分 201
    http_req_duration..........: avg=225.3ms  med=224.09ms p(90)=230.5ms  p(95)=233.3ms
```

一眼就看得出來：**「取得推薦」的 p95 比首頁多了 50% 以上，而且波動最大**（med 266ms、p95 312ms）。回報時說「取得推薦那一段的 p95 是 312ms，比首頁慢 50%」，遠比「整體有點慢」有用得多——這正是 Chapter 3 判讀摘要、Chapter 5 找拐點的基礎。

Negative
: **預設摘要看不到分段統計**：k6 v1 起預設為精簡模式，只顯示整體數字。要看到上面的 `█ GROUP` 區塊，請加 `--summary-mode=full`；或是在 thresholds 為某一段設門檻，例如 `'http_req_duration{group:::送出評分}': ['p(95)<1500']`，那一段就會出現在摘要的 THRESHOLDS 區（Chapter 3 會再深入）。

Negative
: **比較各段快慢時，看請求延遲，不要看整段時間**：請比較各 group 的 `http_req_duration`，不要用 `group_duration`。`group_duration` 量的是整段 group 的經過時間，連 `sleep()` 的停頓也**一起算進去**。實測中「瀏覽首頁」的請求只花約 200ms，但 `group_duration` 會超過 1 秒，因為停頓也被算進去了。

Positive
: **group 名稱要固定**：group 名稱會變成指標的標籤，跟 `http.url` 同樣的道理，**不要把使用者 ID、訂單編號這類動態值放進 group 名稱**，否則每個不同的名稱都會產生一組新的指標。

Positive
: **為什麼範例要每個 VU 自己登入？** 公開的 QuickPizza 位於負載平衡器後方，靠 cookie 把同一個使用者固定在同一台機器上。如果只在 `setup()` 登入一次再讓所有 VU 共用 token，其他 VU 的請求可能被分到另一台不認得這個 token 的機器，評分就會隨機失敗（401）。所以範例讓每個 VU 第一次迭代時自己註冊並登入，並設定 `noCookiesReset: true` 保留 cookie。

### 實作演練：執行第一支生命週期測試與 CLI Options 實戰

![k6 CLI 終端實機執行展示 (3 大情境動態輪播)](assets/images/k6-ch1-cli-options.gif)

打開終端機，依序執行專案為您準備好的 3 組實戰指令，親身體驗生命週期、CLI 覆蓋與通訊除錯：

Negative
: **前置條件**：`ch1_lifecycle_and_checks.js` 預設打向 Grafana 公開的 QuickPizza（`https://quickpizza.grafana.com`，使用 `/healthz` 與 `/api/pizza/{id}` 端點），不需啟動本機環境，但需要能連外網。若所有 check 與 thresholds 都失敗，請先檢查網路。

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

加上 `--http-debug` 旗標透視底層 HTTP Request（包含 `Authorization` token）與 200 OK Response 封包細節：

```bash
k6 run --vus 1 --iterations 1 --http-debug k6/demos/ch1_lifecycle_and_checks.js
```

![DEMO 3: HTTP 除錯封包透視成果](assets/images/k6-ch1-cmd3-httpdebug.png)

#### 步驟 4：用 group 跑一趟使用者旅程，看分段統計

對 QuickPizza 跑一趟「瀏覽首頁 → 取得推薦 → 送出評分」的旅程（5 個 VU、1 分鐘，不需要啟動本機實驗環境）：

```bash
k6 run --summary-mode=full k6/demos/ch1_group_journey.js
```

> **👀 觀察重點**：
> 1. 摘要最後有 `█ GROUP: 瀏覽首頁`、`█ GROUP: 取得推薦`、`█ GROUP: 送出評分` 三個區塊，各自有 check 結果與 `http_req_duration`。
> 2. 比較三段的 p95，找出最慢的一段，試著用一句話回報：「哪一段的 p95 是多少、比最快的一段慢多少」。
> 3. 拿掉 `--summary-mode=full` 再跑一次，確認預設摘要只剩整體數字，以及 THRESHOLDS 區裡 `{group:::送出評分}` 那一條門檻。

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

![Smoke Test 流量波形：從第一秒起固定 1 個 VU，持續 1 分鐘](assets/images/k6-ch2-smoke-pattern.png)

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

- **業務目標**：評估系統在預期的日常峰值流量下的吞吐量、平均延遲與 P95/P99 表現，驗證是否達到由 SLO 推導出的效能門檻。
- **流量波形**：經典三段式波形：
  1. **預熱緩升 (Ramp-up)**：讓快取預熱、連線池逐步建立，避免冷啟動擊穿。
  2. **尖峰高原期 (Plateau / Steady State)**：維持高負載持續觀察系統資源是否穩定。
  3. **平緩降速 (Ramp-down)**：驗證連線資源、GC、執行緒池是否能優雅釋放與回收。

![Load Test 流量波形：3 分鐘爬升至 50 VUs，維持 10 分鐘高原穩態，3 分鐘降載至 0](assets/images/k6-ch2-load-pattern.png)

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

![Stress Test 流量波形：每階 2 分鐘爬升加 3 分鐘維持，50、100、200、300 VUs 階梯加壓後冷卻](assets/images/k6-ch2-stress-pattern.png)

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

![Spike Test 流量波形：基準 10 VUs，10 秒內暴增至 200 VUs 維持 1 分鐘，急降後觀察 2 分鐘自癒](assets/images/k6-ch2-spike-pattern.png)

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

- **業務目標**：在系統安全水位（約 60%~80% 負載，見下方設計原則）下長跑數小時至數十小時，專門揪出短時間壓測看不出來的「**四大隱形殺手**」：
  1. **記憶體洩漏 (Memory Leak)**：底層全域變數、快取未設置 TTL 或 Event Listener 未解綁，長時間運行導致 JVM/V8 堆疊溢位 (OOM)。
  2. **連線池洩漏 (Connection Pool Exhaustion)**：資料庫 Query 或 HTTP Client 連線未顯式關閉，累積數小時後池化連線耗盡。
  3. **日誌與磁碟爆滿 (Disk Full)**：無上限日誌堆積填滿 Pod 磁碟空間引發 Evicted。
  4. **認證憑證失效 (Token Expiration)**：JWT/OAuth Token 長期運行未刷新，引發大面積 401 故障。

![Soak Test 流量波形：5 分鐘預熱至 40 VUs，固定維持 4 小時，5 分鐘收尾](assets/images/k6-ch2-soak-pattern.png)

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

- **Soak 設計三原則**：
  1. **負載取「確定撐得住」的六到八成**：通常是 Load Test 通過門檻時的 VU 數 × 0.6～0.8。目的是讓**時間成為唯一的變數**——如果一開始就把系統壓在邊緣，流量造成的劣化和時間造成的劣化會混在一起，無法分辨。
  2. **時長要蓋過一個完整的自然週期**：例如每小時的排程、每天的批次、快取過期時間，並且長到趨勢能和雜訊分開。練習環境 30～60 分鐘即可看出方法；實務上 2～4 小時是常見起點，先短跑一次確認一切正常再拉長。
  3. **窗口內禁止部署、重啟與批次**：通知相關團隊明確的時段與禁止事項，事後確認沒人動過——這三件事任何一件發生，Soak 的數據就得作廢。
- **收尾段不只是降速**：保留至少 5 分鐘觀察負載歸零後系統**是否恢復**，結束後再跑一次 Smoke Test 與基準比較。判讀方法見 Chapter 5 的「Soak 判讀：趨勢比門檻重要」。

#### 五大模式決策矩陣 (Traffic Pattern Decision Matrix)

| 模式名稱 | 併發量級 (VU) | 測試時長 | 核心測試目標 | CI/CD 觸發時機 | 典型失敗徵兆 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Smoke (冒煙)** | 1 ~ 2 VU | 30s ~ 1m | 腳本與 API 路由連通性 | 每次 Git Push / PR 構建 | 404/401、斷言失效率 > 0% |
| **Load (常規負載)** | 預估尖峰 100% | 15m ~ 30m | 驗證常態峰值是否達到效能門檻 | 每週 Release / 發版前審核 | P95 延遲超標、Thread 阻塞 |
| **Stress (極限壓力)** | 預估尖峰 150%~300% | 20m ~ 45m | 探尋崩潰拐點與防禦降級 | 重大版本升級 / 季度容量評估 | RPS 倒退、500 Internal Error |
| **Spike (突發尖峰)** | 瞬間暴衝 5x~20x | 3m ~ 5m | 檢驗 HPA 彈性擴展與快取抗震 | 促銷活動前夕 / 大促架構演練 | HPA 擴展滯後、快取擊穿崩潰 |
| **Soak (浸泡耐久)** | 安全水位 60%~80% | 2h ~ 24h | 揪出記憶體洩漏與連線池枯竭 | 週末排程 / 上線前最後耐久驗證 | 記憶體階梯上升、DB Connection Timeout |

---

### 徹底破解「協調性漏測 (Coordinated Omission)」致命數據謊言

由 Azul Systems 創辦人兼著名效能大師 **Gil Tene** 提出的 **Coordinated Omission（協調性漏測）**，被公認為效能工程歷史上最致命、最普遍的數據盲點！

#### 什麼是協調性漏測？

Negative
: 當受測系統發生延遲或卡頓時，測試工具「**無意中與受測系統同謀協調**」，自動延遲發送後續請求，導致測試報告中統計到的延遲數據「看似平穩正常」，實際上卻完全掩蓋了使用者端真實發生的災難性排隊延遲！

#### 收費站車禍心智模型 (The Tollbooth Analogy)

想像一座高速公路收費站，平時**每秒通行 1 輛車**，平均耗時 1 秒（平均延遲 1s、RPS = 1）。突然，收費閘道當機**卡死整整 100 秒**：

![收費站卡死 100 秒：閉環模型只送出 1 個請求、延遲 100 秒；開放模型 100 個請求全部受害，等待 100 秒到 1 秒不等](assets/images/k6-diagram-tollbooth.png)

閉環模型的報表只記錄到「1 筆請求、延遲 100 秒」，看起來只有一個人受影響；真實世界（開放模型）裡，後續車輛仍以固定頻率抵達，**100 個人全被堵在路上**，總等待 5,050 秒、平均延遲 50.5 秒。

#### 閉環模型 (Closed Loop Model) 的數學缺陷

在傳統壓測工具（包括 k6 使用 `vus: 10` 或 JMeter 預設 Thread Group）中，虛擬用戶的執行邏輯本質是閉環的：

![閉環模型吞吐量 RPS = VUs ÷（回應時間 + sleep）：10 個 VU 時，回應 50ms 可打出 200 RPS，回應 5s 只剩 2 RPS](assets/images/k6-diagram-closed-loop-rps.png)

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

### Open Model 不是萬用解：何時仍該用閉環模型

協調性漏測之所以是「謊言」，有一個前提：**真實世界的流量本來就是 open 的**。公開網站的使用者不會因為你變慢就停手。但如果被測系統在現實中本來就是 closed 的，硬用開放模型，反而是把流量模擬錯了。

選模型只要問一題：**後端變慢時，真實的 client 會不會跟著少送？**

| 答案 | 模型 | 執行器 | 典型場景 |
| :-- | :-- | :-- | :-- |
| 不會：使用者照樣湧入 | 開放模型 | `constant-arrival-rate`、`ramping-arrival-rate` | 公開網站、公開 API、活動搶購 |
| 會：client 等回應才送下一筆 | 閉環模型 | `constant-vus`、`ramping-vus`、`per-vu-iterations` | 下表 5 種情境 |

以下 5 種情境，閉環模型仍然是正確的選擇：

| # | 情境 | 為什麼用閉環 | 建議執行器 |
| :-: | :-- | :-- | :-- |
| 1 | 固定數量的 client，等回應才送下一筆 | batch worker、MQ consumer、固定 50 位客服、IoT 輪詢——後端變慢時本來就會少送，RPS 下降是真實行為，不是漏測 | `constant-vus` |
| 2 | 要驗的是同時在線數／連線數 | 「撐得住 1 萬條 WebSocket 嗎？」、session 上限、connection pool——arrival rate 控制的是每秒開始幾個 iteration，管不到同時掛著幾條連線 | `ramping-vus` |
| 3 | Browser 測試（Chapter 4） | 每個 VU 都是一個 Chromium；開放模型一遇到變慢就加開瀏覽器，先垮的是壓測機。後端壓力交給 protocol 腳本，browser 只用少量 VU 量體驗 | `constant-vus` |
| 4 | 測試資料只能用固定次數 | 每個 VU 綁一組帳號、每筆訂單資料只能用一次——要的是精確的次數，不是速率 | `per-vu-iterations` |
| 5 | Smoke 與共用環境初探 | 1～2 個 VU 確認腳本能跑；變慢時自動降速，不會把大家共用的 staging 打爆 | `vus: 1` |

Negative
: **用閉環模型時記得**：協調性漏測依然存在，量到的延遲會偏樂觀。它適合上面這些本身就是 closed 的情境，但不要拿它來驗證公開服務的 SLO。

---

### 關鍵過載指標：`dropped_iterations` 底層機制與實戰防線

在使用開放模型（`constant-arrival-rate` 或 `ramping-arrival-rate`）時，終端機輸出中有一個極其關鍵的指標：**`dropped_iterations`**。

#### 為什麼會發生 `dropped_iterations`？

排程器嚴格按照設定的 `rate` 計時發起新迭代。但如果受測服務嚴重變慢，導致所有已分配的 VU（包含 `preAllocatedVUs` 以及動態擴展的 `maxVUs`）**全部處於連線等待中、無一可用**，此時排程器別無選擇，只能**強制拋棄該次迭代發送**！

![dropped_iterations 發生機制：排程器時間到要發送第 501 個迭代 → 檢查 VU 池，preAllocatedVUs 用完、maxVUs 50/50 全部卡在等待後端 → 沒有可用 VU，丟棄迭代，dropped_iterations +1](assets/images/k6-diagram-dropped-iterations-mechanism.png)

#### 根因二分診斷法 (Two-Branch Troubleshooting)

當壓測報告出現 `dropped_iterations > 0` 時，請遵循以下決策樹進行排查：

![dropped_iterations > 0 的二分診斷：分支 A 受測後端崩潰（延遲暴增，優化後端、加大連線池）；分支 B 壓測機資源配置失衡（延遲正常，依 Little's Law 調高 maxVUs）](assets/images/k6-diagram-dropped-iterations-diagnosis.png)

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
  http.get('https://api.example.com/products');
}

export function searchWorkflow() {
  http.get('https://api.example.com/search?q=phone');
}

export function checkoutWorkflow() {
  http.post('https://api.example.com/checkout', JSON.stringify({ item_id: 101 }), {
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

![載入 50 MB 測試資料時的總記憶體：傳統 Array 為 50 MB × VU 數（1,000 VU 即 50 GB），SharedArray 全部 VU 共用一份（約 60～100 MB）](assets/images/k6-diagram-sharedarray-memory.png)

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
> 配置為 5 個 VU 執行 15 秒，目標端點為 QuickPizza 的 `/api/delay/1`（伺服器固定延遲 1 秒，含網路往返實測約 1.2 秒）。5 個 VU 只能輪流等待。
> 終端機顯示的實際吞吐量僅有 **~4 RPS**，發出總請求數僅約 65 筆（v2.2.0 實測）。閉環模型在延遲面前主動放水！

##### 步驟 1-B：執行開放模型 (觀察 Little's Law 自動調派)

```bash
k6 run -e MODEL=open k6/demos/ch2_closed_vs_open_model.js
```

> **👀 觀察重點**：
> 目標強制鎖定為 **20 RPS** (`constant-arrival-rate`)。
> 依據利特爾法則 `L = 20 × 1.2s ≈ 24 VUs`，腳本預先配置 `preAllocatedVUs: 40`（多留的緩衝用來吸收冷啟動 TLS 握手拉長的首輪延遲），堅定維持每秒 20 次請求的抵達率！總請求數達到約 300 筆、`dropped_iterations` 為 0，精準重現真實世界的排隊衝擊！
>
> 💡 **加碼實驗**：把 `preAllocatedVUs` 改回 10 再跑一次，會看到 k6 在測試途中臨時擴充 VU 來不及，出現少量 `dropped_iterations`——這就是 Little's Law 精算預配置的價值。

#### 實作 2：刻意誘發 `dropped_iterations` 容量告警

修改或以命令列調整 `maxVUs` 為極小值，觀察 k6 的過載防線：

```bash
k6 run -e MODEL=open -e TARGET_URL=https://quickpizza.grafana.com/api/delay/3 k6/demos/ch2_closed_vs_open_model.js
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
   - 判斷口訣：後端變慢時，真實 client 會不會跟著少送？不會就用開放模型，會就用閉環模型（見〈Open Model 不是萬用解〉的 5 種情境）。
2. **永遠在開放模型中設定門禁 `dropped_iterations: ['count==0']`**：
   - 任何非零的 `dropped_iterations` 都是壓測無效或系統崩潰的明確信號。
3. **海量測試資料唯有 `SharedArray`**：
   - 超過 1,000 筆的使用者資料或 CSV 參數化檔案，一律禁止在全域使用普通 Array，強制改用 `k6/data` 的 `SharedArray`。
4. **開放模型中勿在 VU 程式碼使用 `sleep()` 控制流量**：
   - 開放模型的請求頻率由排程器的 `rate` 嚴格控制。在 VU 代碼中加入 `sleep()` 只會白白拉長該 VU 的佔用時間，浪費 `maxVUs` 容量！

---

## Chapter 3: 效能指標解讀與 SLO 門檻自動化 (Quality Gates)
Duration: 30

### 微服務黃金準則：Google SRE 與 RED Method 深度解剖

在完成流量施壓後，面對終端機中傾瀉而出的海量數據，許多團隊最常問的問題是：「這些數字到底代表什麼？怎樣才算及格？」

在現代微服務與雲原生架構中，效能監控與品質門禁的靈魂基石來自於兩大業界黃金法則：
1. **Google SRE 四大黃金信號 (The Four Golden Signals)**：延遲 (Latency)、流量 (Traffic)、錯誤 (Errors)、飽和度 (Saturation)。
2. **Weaveworks / Tom Wilkie 提出的 RED Method**：專為微服務架構量身打造，將監控聚焦於最關鍵的三大軸線：
   - **Rate（請求速率 / 吞吐量）**：系統當前每秒正在處理多少個請求？
   - **Errors（錯誤比率）**：有多少請求以非預期的 5xx 或業務邏輯錯誤結束？
   - **Duration（持續時間 / 延遲）**：每個請求完成完整的網路與業務交互需要耗費多少毫秒？

#### k6 核心指標與 RED Method 的映射關係

| RED 維度 | 對應 k6 內建指標 | 指標型態 | 監控核心意義 | 典型 threshold 範例 |
| :--- | :--- | :--- | :--- | :--- |
| **Rate** | `http_reqs` | Counter | 系統整體處理速率 (RPS) 與總請求量 | `rate > 500` (每秒需能承受 500 RPS) |
| **Errors** | `http_req_failed` | Rate (0~1) | 非 2xx/3xx HTTP 狀態碼之失敗比例 | `rate < 0.01` (全站錯誤率嚴格低於 1%) |
| **Duration** | `http_req_duration` | Trend | 送出請求到收完回應的耗時（不含連線建立，見下一節） | `p(95) < 1000` (95% 請求需在 1 秒內完成) |
| **Saturation** | `vus` / `vus_max` | Gauge | 壓測端資源飽和度與動態 Goroutine 水位 | 觀察是否觸發 `dropped_iterations` |

#### SLI、SLO、SLA 與 k6 Thresholds

| 名詞 | 是什麼 | 例子 |
| :--- | :--- | :--- |
| **SLI**（Service Level Indicator，服務水準指標） | 衡量服務好壞的量測值 | 請求延遲、錯誤率——對應 k6 的 `http_req_duration`、`http_req_failed` |
| **SLO**（Service Level Objective，服務水準目標） | 團隊對 SLI 訂的內部目標，搭配一段時間窗口 | 「過去 28 天內，99% 的結帳請求在 500ms 內完成」 |
| **SLA**（Service Level Agreement，服務水準協議） | 對客戶的合約承諾，違反要賠償；通常比 SLO 寬鬆 | 「月可用率低於 99.9% 時退還部分費用」 |

Negative
: **k6 threshold 不等於 SLO。** SLO 是對「真實流量、一段時間窗口」的目標；k6 threshold 是「發版前、單次測試」的門檻，是從 SLO 推導出來的替代指標。兩者的流量組成、時間長度、執行環境都不同，所以 threshold 通常要訂得**比 SLO 更嚴格**，留下安全邊際——例如 SLO 是「99% 請求在 500ms 內」，壓測門檻可設 `p(99)<400`。**跑一次壓測通過 threshold，只代表這個版本在這次測試條件下沒有明顯退化，不代表上線後就會符合 SLO**；是否真的達標，要看監控系統對真實流量的長期量測。

---

### 延遲時間線微觀拆解：剖析 `http_req_duration` 底層生命週期

許多工程師誤以為 `http_req_duration` 只是單純的「後端計算時間」，也有人以為它包含了「從建立連線到收完回應」的全部時間——**兩者都不對！** k6 把一次 HTTP 請求拆成 6 個細分指標，但 `http_req_duration` 只涵蓋其中**後 3 段**：

![一次 HTTP 請求的 6 個細分指標：blocked、connecting、tls_handshaking 屬於連線準備，不計入 http_req_duration；http_req_duration 等於 sending + waiting + receiving](assets/images/k6-ch3-latency-timeline.png)

Positive
: **官方定義**：`http_req_duration = http_req_sending + http_req_waiting + http_req_receiving`。`blocked`、`connecting`、`tls_handshaking` 是**額外**發生在請求送出之前的時間，它們會拉長 `iteration_duration`（以及真實使用者的體感），卻**不會**反映在 `http_req_duration` 上。親手驗證：執行 `k6 run --summary-mode=full script.js`，把 sending + waiting + receiving 三個 avg 加起來，會剛好等於 `http_req_duration` 的 avg。

#### 延遲異常根因診斷矩陣 (Latency Diagnostic Matrix)

當延遲門檻超標、或 `iteration_duration` 莫名變長時，先用 `--summary-mode=full`（或 Web Dashboard 的 **Timings** 分頁）看到全部 6 個細分指標，再依據以下矩陣快速鎖定架構瓶頸。注意前兩項**不會**讓 `http_req_duration` 變高，只會讓 `iteration_duration` 變長——如果你只盯著 `http_req_duration`，連線層的問題會完全隱形：

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

### 看懂 k6 結尾摘要：5 步驟判讀 SOP (Reading the End-of-Test Summary)

每次 `k6 run` 結束，終端機都會吐出一大段摘要。新手最常犯的錯是「從第一行讀到最後一行」，或只瞄一眼綠色勾勾就收工。資深工程師會**依固定順序、帶著問題**去讀。以下是一份 k6 v1+/v2 格式的真實摘要（開放模型 `constant-arrival-rate`，目標 50 RPS 持續 60 秒，`maxVUs: 60`）：

```text
  █ THRESHOLDS

    http_req_duration
    ✗ 'p(95)<500' p(95)=812.4ms                              ◀ ① 判決：門檻違規

    http_req_failed
    ✓ 'rate<0.01' rate=0.84%


  █ TOTAL RESULTS

    checks_total.......: 5920    98.7/s
    checks_succeeded...: 99.58%  5895 out of 5920            ◀ ② 功能正確性
    checks_failed......: 0.42%   25 out of 5920

    ✗ status is 200
      ↳  99% — ✓ 2935 / ✗ 25
    ✓ body has items

    HTTP
    http_req_duration..............: avg=231.5ms min=12.1ms med=98.3ms max=4.21s p(90)=640.2ms p(95)=812.4ms
      { expected_response:true }...: avg=226.9ms min=12.1ms med=97.9ms max=3.87s p(90)=631.7ms p(95)=801.0ms
    http_req_failed................: 0.84%  25 out of 2960        ◀ ③ 延遲分佈形狀 + 錯誤率
    http_reqs......................: 2960   49.3/s

    EXECUTION
    dropped_iterations.............: 37     0.62/s               ◀ ④ 壓測本身有沒有效
    iteration_duration.............: avg=1.24s   min=1.01s  med=1.10s  max=5.22s p(90)=1.65s p(95)=1.82s
    iterations.....................: 2960   49.3/s
    vus............................: 7      min=1       max=60
    vus_max........................: 60     min=60      max=60

    NETWORK
    data_received..................: 38 MB  630 kB/s             ◀ ⑤ 頻寬與 Payload
    data_sent......................: 312 kB 5.2 kB/s
```

#### 步驟 ①：先看 `█ THRESHOLDS`——判決書

- 這區只回答一個問題：**這次測試過關了沒？** `✓` 通過、`✗` 違規。只要有一個 `✗`，k6 就會以 **Exit Code 99** 結束（下一節 CI/CD 卡關的基礎）。
- 看到 `✗` 時，記下是**哪個指標、哪個統計量**違規（本例是 `http_req_duration` 的 `p(95)`），接下來的步驟都是在找「為什麼」。

#### 步驟 ②：看 `checks`——功能到底對不對

- `checks_succeeded` 不是 100% 時，往下看每條 check 的 `↳ 99% — ✓ 2935 / ✗ 25`，找出是哪條斷言在失敗。
- **陷阱**：`check()` 是軟斷言，**失敗不會讓 k6 回傳非 0**！若要讓 check 失敗能卡關，必須另外加門檻 `checks: ['rate>0.99']`。

#### 步驟 ③：看 `HTTP` 群組——讀出延遲分佈的「形狀」

不要只看單一數字，而是把一整行當作分佈來讀：

| 比較 | 判讀法則 | 本例 |
| :-- | :-- | :-- |
| `med` vs `p(95)` | 比值 > 3 倍 → 明顯**長尾**，少數請求很慘 | 98ms vs 812ms ≈ 8 倍 → 嚴重長尾 |
| `avg` vs `med` | `avg` 遠大於 `med` → 分佈右偏，被極端值拉高 | 231ms vs 98ms → 右偏 |
| `max` | 出現整數秒（如 `60s`）通常是**逾時**，不是真的處理那麼久 | 4.21s，未觸及逾時 |
| 整體 vs `{ expected_response:true }` | 後者只算成功回應。若**整體明顯比成功的還快**，代表錯誤回應「快速失敗」把延遲拉低了 | 兩者接近，錯誤不是快速失敗 |
| `http_reqs` 的速率 | 系統實際吞吐 (RPS)，要跟你設計的目標流量比對 | 49.3/s，略低於目標 50/s，差額就是被丟掉的迭代 |

#### 步驟 ④：看 `EXECUTION` 群組——這次壓測本身「有效」嗎？

- **`dropped_iterations` > 0**：k6 沒有空閒 VU 可以啟動新迭代，**你設定的流量根本沒打出去**（見 Chapter 2）。本例丟了 37 次。
- **`vus` 的 `max` 等於 `vus_max`**：VU 池被用光了。這跟 `dropped_iterations` 通常一起出現，根因多半是**後端變慢**，VU 被長尾請求卡住回不來。
- **`iteration_duration` 遠大於 `http_req_duration`**：差距來自 `sleep()`、多個請求串接、客戶端處理，以及 `blocked`/`connecting`/`tls` 這些**不計入** `http_req_duration` 的連線時間。差距異常大時，用 `--summary-mode=full` 檢查 6 個細分指標。

#### 步驟 ⑤：看 `NETWORK` 群組——頻寬與 Payload 合理嗎？

- `data_received ÷ http_reqs` = 平均每筆回應大小。本例 38 MB ÷ 2960 ≈ **13 KB/筆**，若某支 API 突然變成數百 KB，要懷疑沒分頁或少了壓縮。
- `data_received` 的速率接近壓測機網卡上限時（例如 100 Mbps ≈ 12.5 MB/s），**瓶頸可能在壓測機，而不是受測系統**。

Positive
: **本例結論**：P95 違規（①），而延遲分佈呈現 8 倍長尾（③）。目標 50 RPS 只打出 49.3、丟了 37 次迭代、VU 池用光（④）——**後端在接近 50 RPS 時已飽和，長尾請求佔住 VU，壓測端也因此補不上流量**。下一步：用 Chapter 5 的儀表板找出飽和的「拐點」時間，再對齊後端指標找根因。

#### 常見誤判對照表

| 看到的現象 | ❌ 常見誤判 | ✅ 正確解讀 |
| :-- | :-- | :-- |
| `avg` 很低 | 「系統很快，沒問題」 | 平均值會掩蓋長尾，一律以 `p(95)`/`p(99)` 為準 |
| 錯誤率高，但延遲超漂亮 | 「只是有點錯，速度很好」 | 錯誤回應通常**快速失敗**（如 503 立刻返回），拉低了延遲。改看 `{ expected_response:true }` |
| 所有門檻 ✓，但有 `dropped_iterations` | 「測試通過」 | 目標流量沒打滿，**結果無效**，應加門檻 `dropped_iterations: ['count==0']` |
| check 有 ✗，但 Exit Code 是 0 | 「CI 沒擋，應該沒事」 | check 是軟斷言，需加 `checks: ['rate>0.99']` 門檻 |
| `http_req_duration` 正常，但使用者說慢 | 「後端很快，是使用者網路的問題」 | 看 `http_req_blocked`/`connecting`/`tls_handshaking`（不計入 duration），或改用 k6 Browser 量測前端渲染 |

Negative
: **預設摘要會隱藏細分指標**：k6 v1 起預設為精簡模式 (`compact`)，`http_req_blocked`、`http_req_waiting` 等 6 個細分指標不會列出。除錯時請加上 `--summary-mode=full`，它還會依 `group` 與 `scenario` 分別列出指標。

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
  // 第二個參數 true：告訴 k6 這是「時間」，摘要才會顯示成 123.4ms
  const dbQueryTrend = new Trend('custom_db_query_duration', true);
  // 記錄數值 (毫秒)
  dbQueryTrend.add(queryExecutionTimeMs);
  ```

#### 自訂指標的 5 個規則

四種型態會用了，接下來是「定義與使用」時最容易踩的坑。下面這支腳本把 5 個規則一次示範，不需要連線任何服務就能直接跑（`k6/demos/ch3_custom_metric_rules.js`）：

```javascript
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
```

```bash
k6 run k6/demos/ch3_custom_metric_rules.js
```

跑完後，自訂指標會出現在摘要的 `CUSTOM` 區塊（規則 5，k6 v2.2 實測輸出）：

```text
  █ THRESHOLDS
    checkout_success
    ✓ 'rate>0.9' rate=100.00%
    db_query_time{endpoint:checkout}
    ✓ 'p(95)<200' p(95)=138ms

  █ TOTAL RESULTS
    CUSTOM
    checkout_success..........: 100.00% 5 out of 5
    db_query_time.............: avg=120ms min=100ms med=120ms max=140ms p(90)=136ms p(95)=138ms
      { endpoint:checkout }...: avg=120ms min=100ms med=120ms max=140ms p(90)=136ms p(95)=138ms
    orders_completed..........: 5       0.999145/s
    queue_depth...............: 4       min=0      max=4
```

| 規則 | 怎麼做 | 做錯會怎樣 |
| :-- | :-- | :-- |
| **1. 在最上層宣告** | `new Trend(...)` 寫在 `default function` 外面 | 寫在 `default function` 裡，k6 直接報錯：`metrics must be declared in the init context` |
| **2. 時間型 Trend 加 `true`** | `new Trend('db_query_time', true)` | 沒加的話摘要只顯示 `123.4`，看不出是毫秒還是次數 |
| **3. 名稱只用英數與底線** | `checkout_duration`，以字母或底線開頭，最長 128 字元 | 用中文命名（如「結帳耗時」）會報錯：`Invalid metric name` |
| **4. 用 tags 細分並設門檻** | `.add(值, { endpoint: 'checkout' })` 搭配 `'db_query_time{endpoint:checkout}'` 門檻 | 不帶 tags 就只能對整體設門檻，分不出是哪個端點慢 |
| **5. 知道去哪裡看** | 終端機：摘要的 `CUSTOM` 區塊；Prometheus：名稱加上 `k6_` 前綴，Rate 再加 `_rate`、Counter 再加 `_total` | 在 Grafana 查 `k6_checkout_success` 會查不到，要查 `k6_checkout_success_rate` |

Negative
: **tag 的值不要放動態資料**：跟 `http.url` 與 group 名稱同樣的道理，`{ endpoint: 'checkout' }` 這種固定分類可以，放使用者 ID 或訂單編號會讓指標數量爆炸。

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

#### 3. 以 group 為單位設門檻 (Group Thresholds)

Chapter 1 用 `group()` 把一趟使用者旅程切成幾段。k6 會自動幫 group 內送出的每個指標（`http_req_*`、`checks`、自訂指標）打上 `group` 標籤，所以不必逐一幫請求加 tags，就能直接對「旅程中的某一段」設門檻：

```javascript
export const options = {
  thresholds: {
    'http_req_duration{group:::01_核心結帳交易}': ['p(95)<1000'],
    'http_req_duration{group:::02_背景報表查詢}': ['p(95)<3000'],
  },
};

export default function () {
  group('01_核心結帳交易', () => { /* ... */ });
  group('02_背景報表查詢', () => { /* ... */ });
}
```

**為什麼是三個冒號？** 標籤名稱是 `group`，後面接一個 `:`；k6 存的標籤值會在 group 名稱前加上 `::`，變成 `::01_核心結帳交易`。兩段接在一起就成了 `group:::01_核心結帳交易`。巢狀 group 則用 `::` 串接各層名稱，例如 `group('結帳', () => group('付款', ...))` 要寫成 `{group:::結帳::付款}`。

**tag 與 group 怎麼選？** 兩者都能拿來篩選門檻，差別在於你想用什麼方式分類：

| | `group` | 請求層級 `tags` |
| :-- | :-- | :-- |
| 回答的問題 | 旅程中的**哪一段**慢？ | **哪一類** API 慢？ |
| 打標方式 | 包在 `group()` 裡自動套用 | 每個請求手動傳 `tags` |
| 典型用法 | 「結帳這一段 p95 < 1s」 | 「所有 critical API p99 < 300ms」，不管出現在哪一段 |

同一個端點如果會在不同段落被呼叫，想「不分段落，統一管這一類 API」就用 tags；想知道「這一段旅程整體表現如何」就用 group。`ch3_quality_gates_exit99.js` 兩種都用了：`{api_type:critical}` 管端點等級，`{group:::01_核心結帳交易}` 管旅程段落。

Negative
: **group 門檻的三個陷阱**（k6 v2.2 實測）：  
① **名稱打錯不會報錯，而且會顯示通過**：門檻對不到任何請求時，摘要會顯示 `p(95)=0` 並打上 `✓`。修改 group 名稱時，記得同步修改門檻，並確認摘要中的數值不是 0。  
② **外層 group 不含內層的數據**：`{group:::結帳}` 只統計直接寫在「結帳」裡的請求；巢狀在「付款」裡的請求只屬於 `{group:::結帳::付款}`，要另外設門檻。  
③ **延遲門檻不要用 group_duration**：它會把 `sleep()` 的停頓一起算進去，請改用 `http_req_duration`（見 Chapter 1）。

#### 4. 避免高基數維度爆炸 (High Cardinality)

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

![k6 Exit Code 規範：所有 Thresholds 通過回傳 Exit Code 0（CI 通過）；任一 Threshold 違規回傳 Exit Code 99（CI 失敗，阻斷部署）](assets/images/k6-diagram-exit-code-chain.png)

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
> 4. **套用 5 步驟判讀**：即使全部通過，也請照「看懂 k6 結尾摘要」的順序走一遍：`med` 與 `p(95)` 差幾倍？`vus` 的 max 有沒有碰到 `vus_max`？再加上 `--summary-mode=full` 重跑一次，找出 6 個細分延遲裡最大的是哪一段。

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
3. **讀摘要要有順序：判決 → 正確性 → 分佈形狀 → 壓測有效性 → 頻寬**：
   - 門檻全綠不代表結果可信。只要出現 `dropped_iterations` 或 VU 池見底，這次壓測就沒打出目標流量，結論必須作廢重測。
4. **分級治理，多用標籤過濾 (Tag Filtering)**：
   - 嚴格隔離 Critical 核心業務與 Background 背景報表端點，避免次要服務的延遲劣化破壞全域發版。
5. **長跑測試務必配置 `abortOnFail`**：
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

![99:1 混合壓測架構：Hybrid Script 把約 99% 的流量交給輕量 Protocol VU 把後端打到滿載，約 1% 的流量交給 1 個 Chromium 探針採集風暴下的 LCP/CLS](assets/images/k6-diagram-hybrid-99-1.png)

Negative
: **99:1 指的是流量比例，不是 VU 數**。本章 Demo 用 10 個 protocol VU 在 10 秒內打出約 280 次 API 請求，而瀏覽器探針只跑 1 次完整的使用者旅程——以流量計算大約就是 99:1。實際要配置多少 protocol VU，取決於你的目標負載（可用 Chapter 2 的利特爾法則推算）與壓測機資源；Demo 打的是公開共用的 QuickPizza，所以刻意維持小規模。

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
    await page.waitForTimeout(1000); // 瀏覽器 async 函式中勿用 sleep()，它會阻塞 event loop
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
Duration: 30

### 破除效能數據孤島：壓測納入全視角可觀測性體系

在傳統企業研發中，效能測試最常遭遇的致命瓶頸是：**「測試數據永遠是一座孤島」**。

當測試人員在終端機中看到 P95 延遲從 50ms 突然飆升至 2,000ms 時，由於缺乏系統內部視角，往往只能在 Slack 群組中盲目猜測：「是資料庫慢了嗎？還是微服務代碼寫爛了？或是網路交換機掉包？」各團隊各執一詞，排查瓶頸曠日廢時。

在現代雲原生架構下，效能測試不應是單獨的「黑盒跑分」，而應是**全視角可觀測性 (Unified Observability) 的核心觸發源**。壓測產生的負載指標，必須與後端微服務的**分散式追蹤 (Tracing)**、**日誌 (Logs)** 以及**主機與容器指標 (Metrics)** 在同一個時間軸上無縫對齊：

![Grafana 統一可觀測性監控中心以共享時間軸串起三類數據：OpenTelemetry 分散式追蹤、Prometheus 基礎設施時序、k6 Prometheus Remote Write 壓測時序](assets/images/k6-diagram-grafana-unified-hub.png)

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

![xk6 Go-to-JS Bridge 架構：JavaScript 腳本經 Goja JS Runtime 呼叫 Go-to-JS Bridge，再由 Go 原生驅動程式直接壓測 PostgreSQL / MySQL](assets/images/k6-diagram-xk6-bridge.png)

#### 擴充套件雙引擎分類

| 擴充套件分類 | 代表性模組 | 核心功能 | 適用場景 |
| :--- | :--- | :--- | :--- |
| **JS Extensions (協定與中間件擴充)** | `xk6-kafka`<br>`xk6-sql`<br>`xk6-redis`<br>`xk6-amqp` | 在 JavaScript 中擴充全新全域物件與通訊協定 | 直接壓測 Kafka、PostgreSQL、MySQL、Redis 等底層中間件 |
| **Output Extensions (時序指標匯出擴充)** | `xk6-output-timescaledb`<br>`xk6-output-kafka`<br>`xk6-output-influxdb` | 攔截 k6 產生的每一筆指標並即時轉發 | 將高頻壓測時序串流即時寫入 TimescaleDB、Kafka 或 Datadog |

Positive
: **講師實戰手記：手把手從零開發 Web3 OTP 插件**——想深入了解如何親手用 Go 語言撰寫一個 xk6 擴充插件嗎？推薦研讀講師專欄文章：[Grafana xk6: 手把手從開發 k6 插件程式到編譯出 k6 插件](https://ganhua.wang/grafana-xk6)。文章詳細拆解了 Go-to-JS 橋接的 `RootModule` 與 `ModuleInstance` 生命週期，並以 Web3 身份驗證為例，實作高併發動態生成一次性密碼 (OTP) 與簽名的自訂模組！

---

### xk6 Docker 確定性編譯實戰 (Deterministic Build)

要在本地編譯 xk6 擴充套件，傳統上需要安裝特定版本的 Go 編譯環境、配置 GOPATH、處理 CGO 與本機依賴，極容易因為環境差異導致「在我的電腦可以跑，在 CI/CD 卻編譯失敗」的窘境。

最佳實踐是使用官方提供的 Docker 映像檔 **`grafana/xk6`** 進行**確定性編譯 (Deterministic Build)**。

#### Docker 編譯兩大軍規避坑點

Negative
: **目錄掛載**：務必用 `-v "$(pwd)/bin:/xk6"` 把本機目錄掛到容器內。官方 `grafana/xk6` 容器的預設工作目錄是 `/xk6`。若掛載路徑寫錯，編譯產出的 `k6` 二進位檔會被遺留在已被銷毀的容器層中，本機空空如也！  

Negative
: **使用者權限**：務必加上 `-u "$(id -u):$(id -g)"`。Docker 預設以 `root` 執行。如果不指定本機用戶的 UID/GID，編譯產生的客製化 `k6` 檔案權限會屬於 `root:root`，導致本機一般使用者無法執行、無法覆寫、甚至 CI Runner 刪除 Workspace 時噴出 Permission Denied！

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
# Prometheus 啟動參數：
--web.enable-remote-write-receiver          # 接收 k6 推送的 Remote Write
--enable-feature=native-histograms          # 接收 native histogram（缺少時 k6 推送會收到 HTTP 500）
```

> **本 Lab 環境**：本專案 Docker Compose 中的 Prometheus 容器已經預先啟用上述兩個參數，接收端點為 `http://localhost:9090/api/v1/write`。

#### Trend 指標的兩種轉換方式：為什麼選 Native Histogram

k6 的 Trend 指標（如 `http_req_duration`）推到 Prometheus 時有兩種轉換方式：

| 方式 | 設定 | Prometheus 端的指標 | 問題 |
| :-- | :-- | :-- | :-- |
| **Trend Stats**（預設） | `K6_PROMETHEUS_RW_TREND_STATS="p(95),p(99)"` | 每個統計量各一條 Gauge，如 `k6_http_req_duration_p95` | k6 端已經算好百分位數，**Prometheus 無法再正確合併**：把多條序列（不同端點、不同時間）的 P95 取平均，得到的不是真正的 P95 |
| **Native Histogram**（本課程採用） | `K6_FEATURES=native-histograms` | 一條直方圖 `k6_http_req_duration_seconds`（單位：秒） | 無：保留完整分佈，任意過濾、合併後再用 `histogram_quantile()` 算出真正的百分位數 |

Negative
: **k6 v2 的新寫法**：舊版文件中的 `K6_PROMETHEUS_RW_TREND_AS_NATIVE_HISTOGRAM=true` 在 k6 v2.2 已被標為舊寫法，執行時會出現 `Legacy env var detected` 警告。請改用 Feature Flag：環境變數 `K6_FEATURES=native-histograms`，或 CLI 參數 `k6 run --features native-histograms`。可用 `k6 features` 列出目前版本支援的 Flag。

查詢範例（Grafana / PromQL）：

```promql
# 每個時間點的 P95（毫秒），用於趨勢圖
histogram_quantile(0.95, sum(rate(k6_http_req_duration_seconds[$__rate_interval]))) * 1000

# 整段儀表板時間範圍的 P95（毫秒），用於單一數字卡（Instant 查詢）
histogram_quantile(0.95, sum(increase(k6_http_req_duration_seconds[$__range]))) * 1000

# 依端點標籤拆開看 P95
histogram_quantile(0.95, sum by (api_type) (rate(k6_http_req_duration_seconds[$__rate_interval]))) * 1000
```

#### 注入 Git Commit Tag 實現 A/B 版本回歸對比

壓測最具商業價值之處，是「**發版前後的效能對比 (Regression Testing)**」：這次 PR 改動了 ORM 查詢，API 是變快了還是變慢了？

透過動態注入 Git 標籤，每筆時序指標都帶有確切的版本元數據：

```bash
COMMIT_ID=$(git rev-parse --short HEAD 2>/dev/null || echo "demo-rev1")
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")

K6_PROMETHEUS_RW_SERVER_URL=http://localhost:9090/api/v1/write \
K6_FEATURES=native-histograms \
k6 run \
  -o experimental-prometheus-rw \
  --tag "commit_id=${COMMIT_ID}" \
  --tag "git_branch=${BRANCH_NAME}" \
  --tag "environment=staging" \
  script.js
```

在 Grafana 中，只需將儀表板的變數 (Variables) 綁定為 `label_values(k6_http_reqs_total, commit_id)`，並在查詢中加上 `{commit_id=~"$commit_id"}` 過濾，即可透過下拉選單自由切換不同的 Git Commit，同屏對比兩次發版的 P95 延遲曲線！本專案的 `k6-live-metrics` 儀表板已內建 `commit_id`、`git_branch`、`environment` 三個變數。

![Grafana 統一可觀測性效能監控儀表板 (Prometheus Remote Write 串流)](assets/images/k6-ch5-grafana-dashboard.png)

---

### 看懂儀表板：從曲線型態判讀系統狀態 (Reading the Dashboard)

Chapter 3 教你讀「一次測試結束後的總結數字」；儀表板則讓你看到**數字隨時間怎麼變化**。總結只告訴你「P95 = 812ms」，曲線才會告訴你「P95 在第 35 秒、負載來到 45 RPS 時開始抬頭」——這個**拐點**才是容量規劃真正需要的答案。

#### 1. Web Dashboard 三大分頁地圖

| 分頁 | 內容 | 回答什麼問題 |
| :-- | :-- | :-- |
| **Overview** | 上排 6 個數字卡（Iteration Rate、HTTP Request Rate、HTTP Request Duration、HTTP Request Failed、Received/Sent Rate）；**HTTP Performance overview**（請求速率 + P95 延遲 + 失敗率疊在同一張圖）；VUs、Transfer Rate、HTTP Request Duration、Iteration Duration 四張趨勢圖 | 系統在什麼負載下開始變慢或出錯？ |
| **Timings** | `http_req_duration` 的 6 個細分指標各一張圖（Waiting、Blocked、Connecting、TLS handshaking、Sending、Receiving），另有 Browser、WebSocket、gRPC 區塊 | 變慢的是哪一段？後端運算還是連線層？ |
| **Summary** | 所有 Trend / Counter / Rate / Gauge 指標的結尾統計表 | 等同終端機摘要，可用 Chapter 3 的 5 步驟判讀 |

Negative
: **Overview 數字卡陷阱**：上排的 `HTTP Request Duration` 大數字顯示的是**平均值 (avg)**，不是 P95！判讀延遲請看下方 **HTTP Performance overview** 圖中的 P95 曲線，或 **HTTP Request Duration** 圖中的 P90/P95/P99 線。

#### 2. 判讀核心心法：永遠把「負載軸」和「反應軸」疊在一起看

單看延遲曲線沒有意義：延遲上升可能只是因為負載變大了。判讀時一定要同時看兩組線：

- **負載軸（你施加了多少壓力）**：`vus`、請求速率 (`http_reqs` rate)
- **反應軸（系統怎麼回應）**：P95/P99 延遲、失敗率 (`http_req_failed`)

Web Dashboard 的 **HTTP Performance overview** 和 **VUs**（VU 數與請求速率疊圖）就是為此設計的。背後的數學是 Chapter 2 的利特爾法則：在閉環模型下，`RPS ≈ VUs ÷ (回應時間 + sleep)`。當 VU 增加但 RPS 不再增加時，**一定**是回應時間變長了。

#### 3. 八種經典曲線型態

![儀表板的 8 種經典曲線型態：① 健康線性、② 飽和平台、③ 崩潰懸崖、④ 尾巴張開、⑤ 緩慢爬坡、⑥ 週期鋸齒、⑦ 錯誤率階梯、⑧ 吞吐下滑・連線層](assets/images/k6-ch5-curve-patterns.png)

⑤⑦⑧ 三種型態只會在**負載固定、長時間執行**的 Soak 測試中清楚浮現：負載不變時，時間是唯一的變數，所以曲線的任何移動都指向「隨時間累積」的問題。

| 型態 | 你看到的 | 代表什麼 | 下一步 |
| :-- | :-- | :-- | :-- |
| **① 健康線性** | VUs ↑、RPS 同比例 ↑、P95 平穩 | 系統仍有餘裕 | 繼續加壓，找出上限 |
| **② 飽和平台** | VUs 持續 ↑，但 **RPS 走平**；同一時間 P95 開始爬升 | 達到容量上限，請求開始排隊。**拐點當下的 RPS 就是系統容量** | 記下拐點時間，到 Timings 分頁確認是 Waiting 在漲 |
| **③ 崩潰懸崖** | P95 垂直暴衝、**錯誤率同時竄升**、RPS 反而下降 | 佇列溢出、逾時、連線池或執行緒池耗盡 | 找「錯誤率第一次 > 0」的時間點，對齊後端日誌 |
| **④ 尾巴張開** | P90/P95 平穩，**P99 越拉越開** | 只有少數請求受害：GC 停頓、鎖競爭、快取失效、某個慢節點 | 用 Tags 拆端點找出元兇；對齊 GC 與 DB 鎖指標 |
| **⑤ 緩慢爬坡** | **負載不變**，延遲隨時間緩慢上升，沒有尖刺、沒有階梯 | 記憶體壓力（洩漏導致 GC 越來越頻繁），或資料越積越多讓查詢變慢 | **看 P50 有沒有一起爬**：P50 與 P95 一起變厚 → 全面性的記憶體／GC 壓力；只有特定端點變慢 → 資料累積，用 Tags 拆端點確認 |
| **⑥ 週期鋸齒** | 固定間隔出現尖峰 | 排程任務、GC 週期、快取 TTL 同時到期、自動擴縮容 | 量出尖峰間隔，比對 cron、TTL 與 HPA 設定 |
| **⑦ 錯誤率階梯** | **負載不變**，錯誤率在某一刻跳上一階、維持一段時間後再跳一階 | 某種**有限資源正在被用完**：DB 連線池借出不還、檔案描述符 (open files)、執行緒池。每一階代表又少了一批 | 依 `status` 與錯誤訊息分類，看哪類端點先出錯（需要 DB 的端點先逾時 → 連線池；寫入類先失敗 → 磁碟） |
| **⑧ 吞吐下滑・連線層** | VUs 固定，**RPS 逐步下滑**，但 P95 **持平**；同時 `http_req_blocked` / `connecting` 上升 | 問題在**連線建立層**：伺服器或負載平衡器的連線數上限，或**壓測機自己的連線用完**。還記得嗎？這兩段不計入 `http_req_duration`，所以 P95 看起來沒事 | **先排除壓測機**（`top`、`ss -s` 看本機連線與埠數），再往伺服器與 LB 的連線數查 |

Positive
: **別忘了檢查壓測機自己**：若 RPS 走平，但後端 CPU 很閒、延遲也沒漲，瓶頸可能在**壓測機**（CPU 滿載、網卡頻寬用光）或 `dropped_iterations` 已經出現。Web Dashboard 看不到壓測機資源，請同時開 `top` 觀察 k6 行程。

#### 4. 本專案 Grafana 儀表板 (`k6-live-metrics`) 逐面板判讀

| 面板 | 回答什麼問題 | 判讀注意事項 |
| :-- | :-- | :-- |
| 🚀 **Total Requests** | 這次總共打了多少請求？ | 是累積數，只能確認「有沒有打出去」，不代表效能 |
| ⚡ **P95 Request Duration** | 整段時間範圍的延遲水位？ | 以 native histogram 對**整段儀表板時間範圍**計算真正的 P95（`increase(...[$__range])`）。縮放時間範圍，數字會跟著重算；要看某次測試，請先把時間範圍對準那次測試 |
| 👥 **Active VUs** | 施加了多少壓力？ | 與延遲面板對照，找出拐點 |
| 🎯 **Business Transaction Success Rate** | 業務流程真的成功了嗎？ | 來自自訂 `Rate` 指標。**HTTP 200 不代表業務成功**，若它下降但 `http_req_failed` 正常，代表 API 回了 200 但內容錯誤 |
| 📈 **Duration Percentiles (P90/P95/P99)** | 延遲分佈隨時間怎麼變？ | 每個點是該時間視窗內的百分位數，直接套用上面的型態 ②④⑤⑥⑦ |
| 🏷️ **Requests by Tagged Endpoint** | 流量配比是否符合設計？ | 若配比與腳本預期不符（例如結帳佔比過低），這次壓測結果就不具代表性 |

#### 5. 儀表板判讀 4 步驟 SOP

1. **確認壓力真的打出去了**：VUs 與 RPS 是否符合腳本設計？有沒有 `dropped_iterations`？流量配比對不對？
2. **找出拐點時間**：在延遲或錯誤率曲線上，找到第一個偏離平穩的時間點，並記下當下的 VUs 與 RPS。
3. **定位是哪一段變慢**：切到 Timings 分頁。Waiting 漲是後端運算，Blocked/Connecting 漲是連線層，Receiving 漲是 Payload 過大。
4. **對齊後端指標找根因**：把拐點時間帶進 Grafana，用共享十字準星對齊基礎設施指標——這就是下一節的「破案現場」。

#### 6. Soak 判讀：趨勢比門檻重要

Soak 測試有一個反直覺的特性：**全程綠燈也可能是失敗的 Soak**。假設門檻是 `p(95)<800`，而 P95 在一小時內從 300ms 一路爬到 700ms——門檻沒破，但這條趨勢線在告訴你：第八小時就會紅燈。Soak 的門檻仍然是裁判，但真正要看的是**斜率**。

**(1) 把趨勢量化，而不是用眼睛估**：只取「固定負載」那一段（排除暖身與收尾），每 5 分鐘分一桶，算出每桶的 P50、P95、錯誤率、RPS 與 `http_req_blocked` P95，再對每條線做線性趨勢，判斷它是「持平」「緩慢爬升（⑤）」「階梯（⑦）」還是「下滑（⑧）」。在本專案中，Grafana 的 P90/P95/P99 趨勢圖已經是分桶後的結果；若要離線分析，可用 `--out json=raw.json` 輸出原始數據（兩小時的 Soak 可能產生數百 MB，長跑時優先用 Prometheus Remote Write）。

**(2) 一定要看「恢復」**：負載歸零之後，系統有沒有回到基準？正常的系統在流量歸零後幾分鐘內就恢復；**有洩漏的系統不會**，因為被佔住的資源不會自己還回來。做法是在 Soak 結束幾分鐘後，再跑一次 Smoke Test，和測試前的基準比較。「Soak 結束 10 分鐘後，Smoke 的 P95 仍是 650ms（基準 300ms）」是你**不需要任何伺服器端數據**就能拿出的硬證據。

**(3) k6 端是「果」，後端監控是「因」**：k6 只能告訴你症狀，確認根因需要把同一段時間的後端曲線對齊來看。下表列出每個訊號該對照哪條後端曲線，以及本 Lab 環境要去哪裡看：

| k6 端訊號 | 對照的後端數據 | 本 Lab 去哪看 / 替代方案 |
| :-- | :-- | :-- |
| ⑤ P95 緩慢爬升 | 應用程式記憶體（heap）、GC 次數與暫停時間 | 本 Lab 未收集 runtime 指標，用 `docker stats` 定時記錄各服務容器的記憶體 |
| ⑤ 特定端點變慢 | 資料庫查詢延遲 | Grafana **4 Golden Signals** 儀表板的 *Database Query Latency*；Tempo 追蹤找慢 Span |
| ⑦ 錯誤率階梯 | DB 連線池使用中／上限；DB 端當前連線數 | `docker exec postgres psql -U postgres -c "select count(*) from pg_stat_activity"` 定時記錄 |
| ⑦ 錯誤率階梯（其他候選） | open files、執行緒數、錯誤日誌 | `docker exec service-a sh -c 'ls /proc/1/fd \| wc -l'`；Grafana *Recent Error Logs*（Loki） |
| ⑧ 吞吐下滑・連線層 | 伺服器／LB 連線數與逾時計數；**壓測機本身**的連線 | 壓測機執行 `ss -s`；服務端看 4 Golden Signals 的 *Request Rate by Service* 是否同步下滑 |
| 所有訊號 | 部署、重啟、排程工作的時間紀錄 | 確認 Soak 期間沒有人動過系統——「不是洩漏，是有人動了它」 |

Negative
: **Soak 期間，除了受測系統，還有兩樣東西也要撐得住**：(1) **壓測機**——長時間執行時定時記錄 k6 所在主機的 CPU 與記憶體，壓測機自己洩漏會被誤判成系統問題；(2) **測試資料**——參數化帳號會不會被鎖、測試資料會不會把資料庫塞爆（這本身就是你製造的「洩漏」，會讓 ⑤ 看起來像資料累積）。

---

### 顛峰時刻：Grafana 雙十字準星全視角對齊 (Crosshair Convergence)

什麼是全視角可觀測性帶來的降維打擊？請看以下真實生產環境除錯案例：

#### 真實破案現場：神秘的 14:02 延遲雪崩

某電商平台進行促銷壓測時，在下午 `14:02:00`，k6 回報的 API P95 延遲突然出現**垂直暴衝**：從原本平穩的 `45ms` 瞬間飆高至 `2,200ms`！

![共享十字準星示意：14:02:00 同一秒，k6 API P95 從 45ms 暴衝到 2,200ms，Pod CPU CFS Throttling 飆到 85%](assets/images/k6-diagram-crosshair-1402.png)

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
> 4. **練習判讀**：在 **Overview** 分頁比對 VUs 與請求速率兩條線是否同步上升（型態 ① 健康線性），再切到 **Timings** 分頁，找出 6 個細分延遲中哪一段最大。記得：上排數字卡的 Duration 是 avg，不是 P95。

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
> 4. **練習判讀**：對照「本專案 Grafana 儀表板逐面板判讀」表格，確認 Active VUs 上升時 P95 是否跟著抬頭、P99 是否與 P95 越拉越開（型態 ④），以及 Requests by Tagged Endpoint 的配比是否符合腳本設計。

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

#### 社群推薦閱讀：[Day 24｜Soak Test：從 k6 端數據推測伺服器在漏什麼](https://ithelp.ithome.com.tw/articles/10413194)
- **出處**：iThome 鐵人賽系列〈不會寫程式，我照樣做效能測試 - Claude Code × k6 的 30 天〉。本章「Soak 判讀：趨勢比門檻重要」與型態 ⑦⑧ 的判讀思路參考自該文。
- **推薦理由**：完整示範只靠 k6 端數據（P95、錯誤率、RPS 三條趨勢線）推測伺服器端洩漏類型的方法，並附上 Soak 設計、窗口告知、向 RD 索取監控數據的清單與實作練習，非常適合 QA 與非開發背景的讀者。

---

### Chapter 5 核心心智模型與架構師避坑指南

1. **數據不落地，壓測無意義**：
   - 嚴禁把壓測結果留在個人電腦的終端機裡。在 CI/CD 中，至少透過 `Port=-1` 匯出 HTML 報告歸檔，最佳做法是一律透過 Prometheus Remote Write 匯入團隊共享的 Grafana。
2. **善用 Commit Tag 建立效能基準線 (Baseline)**：
   - 每一次合併到 `main` 分支的代碼都必須帶有 Commit ID 進行回歸壓測。當延遲退化時，一眼即可看出是哪一次 Commit 引入的效能退化。
3. **編譯 xk6 嚴格遵守 Docker 確定性原則**：
   - 避免在個人電腦隨意 `go install`。統一使用 Docker 映像檔編譯，並嚴格加上 `-u $(id -u):$(id -g)` 確保檔案權限正常。
4. **看儀表板要找「拐點」，不是看最終數字**：
   - 永遠把負載軸（VUs / RPS）與反應軸（P95/P99 / 錯誤率）疊在一起看。RPS 走平而延遲開始爬升的那一刻，就是系統容量。
   - Soak 測試看**斜率**不看紅綠燈：全程綠燈但 P95 持續爬升的 Soak 是失敗的 Soak；負載歸零後不恢復，是最硬的洩漏證據。
5. **結合分散式追蹤 (Tracing) 與主機監控破除盲區**：
   - 當 P95 飆高時，第一時間看 CPU CFS Throttling、記憶體分頁錯誤與 DB 連線池水位，拒絕憑感覺除錯。

---

## Chapter 6: k6 x agent ── AI 驅動的效能測試新紀元
Duration: 20

### 效能壓測新紀元：從 Test as Code 躍升至 AI Agent 自主工程

![Module 6: k6 x agent ── AI 驅動的效能測試新紀元](assets/images/k6-ch6-slide-1.png)

進入 2025、2026 年，軟體開發的範式正在經歷一場波瀾壯闊的革命——那就是 **AI Agent（智慧體）與 AI 代碼編輯器的全面普及**！

過去手動配置 AI 壓測工作流需要繁複設定 MCP JSON、手寫 Prompt Rules、配置 Node.js 依賴，且 AI 常因缺乏上下文產生過期語法或造成記憶體洩漏的動態 URL。

`k6 x agent` 是 Grafana k6 官方原生內建的 AI 子命令擴充套件（Subcommand Extension，開源專案 [xk6-subcommand-agent](https://github.com/grafana/xk6-subcommand-agent)），專為一鍵配置 AI 編輯器與 Agent 壓測工作流而設計。只需在專案根目錄執行一次命令，它就會自動完成 **「安裝 11 個 AI 技能包」** 與 **「註冊原生 k6 MCP 伺服器」** 兩大設定！

- 🌐 **Grafana 官方配置指南**：[Bootstrap with k6 x agent (Grafana Docs)](https://grafana.com/docs/k6/latest/set-up/configure-ai-assistant/bootstrap-with-k6-x-agent/)
- 🐙 **GitHub 官方開源儲存庫**：[https://github.com/grafana/xk6-subcommand-agent](https://github.com/grafana/xk6-subcommand-agent)

---

### 自動化雙引擎解密：技能包注入與原生 MCP 註冊

![自動化雙引擎解密：技能包注入與原生 MCP 註冊](assets/images/k6-ch6-slide-2.png)

`k6 x agent` 幫你自動處理兩大核心任務：

#### 1. 自動化引擎 1：自動安裝內建 AI 技能 (Bundled Skills)
- **標準規格目錄寫入**：將標準 `SKILL.md` 或 Cursor 的 `.mdc` Rules 自動寫入專屬目錄（如 `.cursor/rules`），讓 AI 即刻掌握 k6 專業規範。
- **自然語言意圖觸發**：在 AI 聊天視窗輸入 *"write a smoke test"* 或 *"convert Playwright"*，AI 自動觸發對應技能，按規範產出代碼。
- **最佳實踐預設注入**：內建 Grafana 團隊嚴選的最佳實踐，避免 AI 產生過期語法或動態字串拼接引發 High Cardinality 記憶體洩漏代碼。
- **團隊水準高度一致**：團隊成員只需執行一次 `init` 命令，即可在不同開發機間擁有完全統一的 AI 壓測提示詞與自動化腳本生成水準。

#### 2. 自動化引擎 2：自動註冊 k6 MCP 伺服器 (Auto-Register MCP)
- **一鍵配置原生協議**：自動將 `k6 x mcp` 寫入編輯器設定檔（如 `.mcp.json`、`.cursor/mcp.json` 或 `.vscode/mcp.json`），免除手動翻找設定。
- **零外部執行環境依賴**：直接呼叫 k6 原生子命令執行檔，完全無需預裝 Node.js、npm 或全域套件，環境乾淨且效能極高。
- **1 VU 冒煙預檢 (`validate_script`)**：賦予 AI 預檢能力：以 1 VU、1 次迭代實際執行腳本，回報語法錯誤、執行期例外與可行的修正建議，杜絕低階錯誤。
- **本機閉環自癒 (`run_script`)**：賦予 AI 執行能力：直接在聊天室驅動本地壓測，即時結構化解析 RPS、P95 延遲與 HTTP 狀態碼自癒修正。

---

### 安全防護與冪等性機制：企業級配置守門員

![安全防護與冪等性：企業級配置守門員](assets/images/k6-ch6-slide-3.png)

非破壞性寫入、智慧辨識自訂規則，確保多次重複執行絕不毀損既有專案代碼：

#### 四大安全機制
1. **擁有者標籤保護 (Owner Tag)**：
   產生的檔案均附帶 `<!-- generated by k6 x agent -->` 識別標記。重複執行 `init` 時，系統自動比對標籤，精準區隔系統自動產生與工程師客製內容，安全無虞。
2. **寫入前安全預覽 (`--dry-run`)**：
   支援在真正寫入磁碟前加上 `--dry-run` 旗標。終端機會清晰預覽列印出所有將新增、修改或保留的檔案清單與完整路徑，完全零副作用。
3. **客製保護與智慧略過 (Custom Guard)**：
   偵測到使用者已手動修改過的檔案時，系統會自動跳過保護，絕不覆蓋你的客製規則；唯有在需要官方版本升級時，才需在命令後加上 `--force` 顯式同步。
4. **零全域污染與 Git 友善 (Git Friendly)**：
   所有產出檔案均收斂於專案本地工作區目錄內（如 `.cursor/rules` 與 `.mcp.json`），不污染全域環境，變更乾淨無雜訊，非常適合團隊納入 Pull Request 進行版本審計。

---

### 常用 CLI 指令速查與 6 大編輯器環境適配

![常用 CLI 指令速查與 6 大編輯器環境適配](assets/images/k6-ch6-slide-4.png)

在專案根目錄終端機執行直覺的子命令，一鍵適配主流 AI 代碼編輯器與自主 Agent 環境：

#### 常用 CLI 指令速查
```bash
# 1. 為指定編輯器進行初始化 (例如 Cursor 或 Claude Code)
k6 x agent init cursor
k6 x agent init claude-code

# 2. 一鍵初始化所有支援的編輯器（團隊協作最佳實踐）
k6 x agent init --all

# 3. 預覽將產生的檔案與路徑（安全檢查，不安裝）
k6 x agent init --dry-run cursor

# 4. 強制覆蓋重置所有技能與 MCP 設定（版本升級專用）
k6 x agent init --force cursor

# 5. 檢查當前專案的 AI 技能與 MCP 伺服器連線狀態
k6 x agent status

# 6. 查看內建的所有 AI 技能清單與詳細描述
k6 x agent skills list
```

#### 原生支援 6 大編輯器矩陣
* **Cursor** (`cursor`)：寫入 `.cursor/rules/*.mdc` 與 `.cursor/mcp.json`，自然語言無縫調度 k6 工具。
* **Claude Code** (`claude-code`)：Anthropic 官方終端 Agent CLI，完美支援 skills 技能包與本地工具鏈。
* **GitHub Copilot** (`vscode-copilot`)：微軟 VS Code 原生工作區，自動配置 `.vscode/mcp.json`，IDE 體驗極致流暢。
* **OpenAI Codex CLI** (`codex-cli`)：OpenAI 原生終端工作流，支援命令行環境下的全自動逆向生成與壓測驗證。
* **OpenCode** (`opencode`)：開源終端 AI 助手環境，提供完全開源自主可控的 Agent 壓測配置方案。
* **Cline** (`cline`)：VS Code 開源自主 Agent 插件，支援檔案讀寫、終端執行與 MCP 閉環反饋。

---

### 內建 11 大專業 AI 技能庫深度剖析

![內建 11 個 AI 技能，精講 5 個核心工作流](assets/images/k6-ch6-slide-5.png)

執行 `init` 後，`k6 x agent` 會自動將 11 個專業壓測技能寫入編輯器的 Rules 目錄（如 `.cursor/rules/*.mdc` 或 `.claude/skills/*/SKILL.md`）。這些技能並非一般的簡短提示詞，而是 Grafana 官方效能工程團隊將數十年的壓測經驗、最佳實踐、AST 語法規範與自癒修復邏輯固化而成的**專家系統知識庫**。

#### 實戰操練系統目標 (System Under Test, SUT)

為了讓讀者深刻體會 AI 技能在生產環境中的威力，本章所有實戰案例與演練均統一採用 Grafana 官方維護的微服務旗艦電商示範應用 ── **Astronomy Shop (OpenTelemetry Demo)**：

* 🌐 **旗艦測試網站**：[`https://appenvdev.field-eng-demo.grafana.net/`](https://appenvdev.field-eng-demo.grafana.net/)
* 🔭 **系統核心特徵**：由 10+ 個雲原生微服務組成（Next.js 前端、Product Catalog、Cart Service、Recommendation、Checkout 等），支援端到端分散式追蹤與 Prometheus 可觀測性監控。
* 🎯 **三大關鍵業務路徑**：
  1. **全館商品目錄查詢**：`GET /api/products`（取得天文望遠鏡、濾鏡、配件列表）
  2. **單一商品規格詳情**：`GET /api/products/{id}`（例如 `OLJCESPC7Z` 探索型折射望遠鏡）
  3. **購物車寫入操作**：`POST /api/cart`（傳送 JSON payload 模擬加入購物車）
  4. **前端真實 SSR 頁面渲染**：`GET /product/66VCHSJNUP`（Starsense 望遠鏡頁面，量測真實 Core Web Vitals）

---

### 11 個技能精講 5 個：專家級壓測核心工作流

在 11 大技能庫中，以下 5 大技能涵蓋了從「需求規劃」、「冒煙快篩」、「生產級負載」、「前端體驗」到「E2E 測試轉譯」的日常核心研發工作流。讓我們透過具體對話 Prompt、AI 推理思考與可執行的生產級腳本，一步步深度拆解：

---

#### 技能 1：`k6-test-planner` (壓測策略規劃師)

* **核心定位**：擔任資深效能架構師。專門接收產品經理或開發團隊模糊的自然語言需求，自動分析端點特徵、計算並發 VU 與爬坡階段，並設計合理的 SLO 品質門禁規範。
* **常見觸發詞**：`"plan tests for order service"`, `"design a test strategy"`, `"recommend VU and RPS"`, `"針對天文商城設計壓測計畫"`

##### 實戰演示：為 Astronomy Shop 電商下單鏈路規劃促銷壓測策略

> **💬 使用者對話 Prompt**：
> 「我們即將針對 Astronomy Shop (`https://appenvdev.field-eng-demo.grafana.net`) 進行促銷檔期壓測。主要業務旅程為：瀏覽商品目錄 (`/api/products`)、查詢個別望遠鏡規格 (`/api/products/{id}`)，並將商品加入購物車 (`POST /api/cart`)。平日流量約 30 RPS，預期大促高峰將達到 150 RPS。請為我們規劃專業的壓測策略，包含利特爾法則並發 VU 計算、測試階段規劃與 SLO 門檻設計。」

##### AI Agent 內部推理與規劃流程 (Behind the Scenes)
1. **呼叫 MCP 工具預檢**：調用 `mcp_k6_info` 確認當前安裝的 k6 版本與可用擴充。
2. **端點架構特徵解構**：
   * `/api/products`：讀取密集型端點，預期回應體較大（~11KB JSON），易受網路頻寬與 JSON 序列化瓶頸影響。
   * `/api/products/{id}`：高頻讀取端點，具備快取潛力。
   * `/api/cart`：狀態寫入端點，涉及 Redis/資料庫狀態變更與分散式鎖，最容易在高併發下產生競爭與延遲劣化。
3. **運用利特爾法則 (Little's Law) 進行並發推導**：
   $$N = X \times (R + Z)$$
   * 目標峰值吞吐量 $X = 150 \text{ req/sec}$。
   * 預期平均系統延遲 $R \approx 0.2 \text{s}$ (200ms)。
   * 人類真實思考時間 (Think Time) $Z \approx 1.5 \text{s}$。
   * 單一虛擬用戶每次完整迭代耗時 $= 0.2\text{s} + 1.5\text{s} = 1.7\text{s}$。
   * 所需高峰並發虛擬用戶數 $N = 150 \times 1.7 = 255 \text{ VUs}$。

##### AI 輸出的結構化壓測計畫 (Markdown Plan)

```markdown
# Astronomy Shop 促銷檔期效能壓測計畫書

## 1. 系統全貌與關鍵路徑
- **目標系統**：Astronomy Shop (OpenTelemetry Demo e-commerce)
- **測試基底網址**：https://appenvdev.field-eng-demo.grafana.net
- **核心路徑**：Catalog (`/api/products`) -> Detail (`/api/products/{id}`) -> Cart (`/api/cart`)

## 2. 測試矩陣 (Test Matrix)
| 階段 | 測試類型 | 執行器 (Executor) | 並發規模 (VUs / RPS) | 持續時間 | 目標驗證重點 | 推薦調用技能 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Phase 1** | 冒煙測試 (Smoke) | `constant-vus` | 1 VU | 30s | 驗證 200 OK 與資料結構正確性 | `k6-smoke-test` |
| **Phase 2** | 常規負載 (Average) | `ramping-vus` | 0 -> 50 VUs | 10m | 檢驗平日 30 RPS 負載下的穩態表現 | `k6-load-test` |
| **Phase 3** | 大促尖峰 (Stress) | `ramping-vus` | 0 -> 255 VUs | 15m | 階梯式爬坡檢驗 150 RPS 負載極限 | `k6-load-test` |
| **Phase 4** | 前端混合體驗 (Hybrid) | 99 Protocol : 1 Browser | 99 VUs + 1 Browser VU | 5m | 測量後端高壓下前端 Core Web Vitals | `k6-browser-test` |

## 3. 建議 SLO 品質門禁規範 (Thresholds)
- **全域可用性**：`http_req_failed: ['rate<0.005']` (錯誤率低於 0.5%)
- **全域 P95 延遲**：`http_req_duration: ['p(95)<500', 'p(99)<1000']`
- **關鍵寫入端點 (Cart)**：`http_req_duration{name:AddToCart}: ['p(95)<400']`
- **斷言成功率**：`checks: ['rate>0.99']`
```

---

#### 技能 2：`k6-smoke-test` (極速冒煙檢驗)

* **核心定位**：CI/CD Pipeline 的第一道極速防線。以極少資源（1 個 VU）在 5 秒內快速發送請求，驗證端點連線狀態、HTTP 狀態碼與資料有效性，在尚未發起高壓測試前先行攔截低階錯誤。
* **常見觸發詞**：`"write a smoke test"`, `"quick sanity check"`, `"verify health check endpoint"`

##### 實戰演示：Astronomy Shop 5 秒極速冒煙先驗

> **💬 使用者對話 Prompt**：
> 「請幫我針對 Astronomy Shop (`https://appenvdev.field-eng-demo.grafana.net`) 寫一個 1 個 VU 的極速冒煙測試腳本。必須檢查：1. 首頁 HTML 正常回應且包含 OTel demo 標題；2. 商品目錄 API (`/api/products`) 回傳有效商品陣列；3. 望遠鏡詳情 API (`/api/products/OLJCESPC7Z`) 正確回傳 Explorascope 商品。請設定嚴格門禁：錯誤率必須為 0%，P95 < 600ms，並且一定要遵循 tags 防高基數標籤規範！」

##### AI 自動生成的生產級冒煙腳本

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 1,
  duration: '5s',
  thresholds: {
    // 冒煙測試零容忍標準：不可有任何請求失敗，check 100% 成功
    http_req_failed: ['rate==0.00'],
    checks: ['rate==1.00'],
    http_req_duration: ['p(95)<600'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://appenvdev.field-eng-demo.grafana.net';

export default function () {
  // 1. 探測商城首頁 HTML
  const homeRes = http.get(BASE_URL, { tags: { name: 'GetHomePage' } });
  check(homeRes, {
    '首頁回應 200 OK': (r) => r.status === 200,
    '首頁標題包含 OTel demo': (r) => r.body && r.body.includes('OTel demo'),
  });

  // 2. 探測商品目錄 API (/api/products)
  const productsRes = http.get(`${BASE_URL}/api/products`, {
    tags: { name: 'GetProducts' },
  });
  check(productsRes, {
    '商品目錄回應 200 OK': (r) => r.status === 200,
    '回傳陣列包含有效商品': (r) => {
      try {
        const data = r.json();
        return Array.isArray(data) && data.length > 0;
      } catch (e) {
        return false;
      }
    },
  });

  // 3. 探測特定商品詳情 API (/api/products/OLJCESPC7Z)
  // 注意：使用 tags 標籤統一聚合，防止不同商品 ID 造成時序高基數爆炸
  const detailRes = http.get(`${BASE_URL}/api/products/OLJCESPC7Z`, {
    tags: { name: 'GetProductDetail' },
  });
  check(detailRes, {
    '商品詳情回應 200 OK': (r) => r.status === 200,
    '商品包含 Explorascope 望遠鏡': (r) => {
      try {
        const item = r.json();
        return item.id === 'OLJCESPC7Z';
      } catch (e) {
        return false;
      }
    },
  });

  sleep(1);
}
```

##### 終端真實執行輸出與成果解析

```text
  █ THRESHOLDS 
    checks..............: ✓ 'rate==1.00' rate=100.00%
    http_req_duration...: ✓ 'p(95)<600'  p(95)=171.2ms
    http_req_failed.....: ✓ 'rate==0.00' rate=0.00%

  █ TOTAL RESULTS 
    checks_succeeded...: 100.00% 18 out of 18
    ✓ 首頁回應 200 OK
    ✓ 首頁標題包含 OTel demo
    ✓ 商品目錄回應 200 OK
    ✓ 回傳陣列包含有效商品
    ✓ 商品詳情回應 200 OK
    ✓ 商品包含 Explorascope 望遠鏡

    HTTP
    http_req_duration...: avg=169.61ms min=167.74ms med=169.66ms max=171.36ms p(95)=171.2ms
    http_req_failed.....: 0.00% 0 out of 9
    iterations..........: 3
```

> [!TIP]
> **AI 專家守護原則**：在執行任何大規模並發壓測（例如 500 VU）之前，AI 技能庫強制要求先跑一次 1 VU 冒煙先驗。若 1 VU 下 API 就出現 500 錯誤或路徑不存在，壓測應立即終止，避免無效流量衝擊測試環境並浪費 CI Runner 資源！

---

#### 技能 3：`k6-load-test` (生產級負載壓測)

* **核心定位**：自動生成符合生產規格的高併發負載測試腳本。原生支援階梯爬坡（Ramping VUs）、開放式到達率模型（Arrival Rate）、動態數據關聯，並嚴格遵循 `SharedArray` 跨 VU 記憶體共享最佳實踐。
* **常見觸發詞**：`"write a load test"`, `"stress test this endpoint"`, `"soak test with 500 RPS"`

##### 實戰演示：Astronomy Shop 階梯式購物車下單負載壓測

> **💬 使用者對話 Prompt**：
> 「請為 Astronomy Shop (`https://appenvdev.field-eng-demo.grafana.net`) 撰寫一份生產級負載壓測腳本：
> 1. 模擬使用者購買流程：瀏覽目錄 -> 點擊望遠鏡商品規格 -> 加入購物車 (`POST /api/cart`)。
> 2. 負載模型：使用 `ramping-vus` 階梯爬坡（3s 爬升至 3 VU、維持 5s、2s 降坡冷卻）。
> 3. 測試資料：使用 `SharedArray` 跨 VU 唯讀共享 5 款熱門望遠鏡 ID（`OLJCESPC7Z`, `66VCHSJNUP`, `1YMWWN1N4O` 等），各 VU 隨機挑選商品進行購物車加入操作。
> 4. 防高基數：針對商品詳情與購物車加入加入標準化 `tags: { name: '...' }` 標籤。
> 5. 門禁：全域 P95 < 800ms，且針對 AddToCart 單獨配置 P95 < 600ms SLO。」

##### AI 自動生成的生產級負載腳本

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';

// 1. 跨 VU 唯讀共享測試商品清單 (SharedArray 最佳實踐，杜絕記憶體洩漏)
const TARGET_PRODUCTS = new SharedArray('Astronomy Products', function () {
  return [
    { id: 'OLJCESPC7Z', name: 'Explorascope Refractor' },
    { id: '66VCHSJNUP', name: 'Starsense Explorer' },
    { id: '1YMWWN1N4O', name: 'Eclipsmart Solar Scope' },
    { id: '2ZYFJ3GM2N', name: 'Roof Binoculars' },
    { id: '0PUK6V6EV0', name: 'Solar System Color Imager' },
  ];
});

// 2. 階梯爬坡與精確 Tagged Thresholds 門禁
export const options = {
  scenarios: {
    astronomy_shop_flow: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '3s', target: 3 },  // 快速階梯爬坡
        { duration: '5s', target: 3 },  // 穩態負載測試
        { duration: '2s', target: 0 },  // 降坡冷卻釋放
      ],
      gracefulRampDown: '2s',
    },
  },
  thresholds: {
    // 全域門禁
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<800'],
    checks: ['rate==1.00'],

    // 端點級細緻門禁 (利用 tags 標籤精準過濾，單獨監控關鍵寫入瓶頸)
    'http_req_duration{name:GetProductCatalog}': ['p(95)<500'],
    'http_req_duration{name:GetProductDetail}': ['p(95)<400'],
    'http_req_duration{name:AddToCart}': ['p(95)<600'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://appenvdev.field-eng-demo.grafana.net';

export default function () {
  // 從 SharedArray 隨機選取一件天文儀器
  const product = TARGET_PRODUCTS[Math.floor(Math.random() * TARGET_PRODUCTS.length)];
  const userId = `k6-user-${__VU}`;

  // 步驟 1：瀏覽全館目錄 (GET /api/products)
  const catalogRes = http.get(`${BASE_URL}/api/products`, {
    tags: { name: 'GetProductCatalog' },
  });
  check(catalogRes, {
    '商品目錄回應 200 OK': (r) => r.status === 200,
    '商品目錄包含商品': (r) => r.json().length > 0,
  });

  // 步驟 2：點選特定望遠鏡商品詳情 (GET /api/products/{id})
  const detailRes = http.get(`${BASE_URL}/api/products/${product.id}`, {
    tags: { name: 'GetProductDetail' },
  });
  check(detailRes, {
    '商品詳情回應 200 OK': (r) => r.status === 200,
    '商品 ID 符合預期': (r) => r.json().id === product.id,
  });

  // 步驟 3：加入購物車 (POST /api/cart)
  const cartPayload = JSON.stringify({
    userId: userId,
    item: { productId: product.id, quantity: 1 },
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
        return data.items && data.items.some(i => i.productId === product.id);
      } catch (e) {
        return false;
      }
    },
  });

  // 破除協調性漏測：注入 1~2 秒動態隨機思考時間 (Think Time)
  sleep(1 + Math.random() * 1);
}
```

##### 終端真實執行輸出與指標深度解析

```text
  █ THRESHOLDS 
    checks..........................................: ✓ 'rate==1.00' rate=100.00%
    http_req_duration...............................: ✓ 'p(95)<800'  p(95)=209.9ms
      {name:AddToCart}..............................: ✓ 'p(95)<600'  p(95)=176.31ms
      {name:GetProductCatalog}......................: ✓ 'p(95)<500'  p(95)=307.12ms
      {name:GetProductDetail}.......................: ✓ 'p(95)<400'  p(95)=164.6ms
    http_req_failed.................................: ✓ 'rate<0.01'  rate=0.00%

  █ TOTAL RESULTS 
    checks_succeeded...: 100.00% 72 out of 72
    http_reqs..........: 36     3.385477/s
    iterations.........: 12
```

> [!NOTE]
> **指標剖析**：透過 Tagged Thresholds 可以清晰看出：
> 1. `GetProductCatalog` 由於需回傳完整的商品 JSON 陣列，P95 為 **307.12ms**，是三者中延遲最高者。
> 2. `AddToCart` 為狀態寫入，P95 為 **176.31ms**，遠低於 600ms 警戒線。
> 3. 全部 72 個 check 100% 成功，展現了微服務後端在併發下的健全度。

---

#### 技能 4：`k6-browser-test` (前端真實渲染與 Web Vitals)

* **核心定位**：透過 `k6/browser` 驅動真實無頭 Chromium，完整加載 CSS、JavaScript、圖片與字體資源，量測 Google Core Web Vitals（LCP 最大內容繪製、CLS 累計版面位移、INP 互動延遲）真實前端體驗指標。
* **常見觸發詞**：`"browser test for login UI"`, `"measure Web Vitals"`, `"hybrid 99:1 test"`

##### 實戰演示：Astronomy Shop 望遠鏡詳情頁 Core Web Vitals 採樣

> **💬 使用者對話 Prompt**：
> 「請幫我為 Astronomy Shop 的 Starsense 望遠鏡商品頁面 (`https://appenvdev.field-eng-demo.grafana.net/product/66VCHSJNUP`) 寫一個 k6/browser 瀏覽器渲染壓測腳本。
> 要求：
> 1. 使用 chromium 瀏覽器渲染真實前端與 CSS/JS/圖片資源。
> 2. 驗證商品頁標題包含 'Starsense Explorer Refractor Telescope'。
> 3. 採樣 Core Web Vitals，並訂定門禁：LCP < 2.5s、CLS < 0.1。
> 4. 嚴格落實 `try ... finally { await page.close() }` 清理機制，防範瀏覽器記憶體洩漏！」

##### AI 自動生成的生產級瀏覽器壓測腳本

```javascript
import { browser } from 'k6/browser';
import { check } from 'k6';

export const options = {
  scenarios: {
    astronomy_browser_ui: {
      executor: 'shared-iterations',
      iterations: 1,
      options: {
        browser: {
          type: 'chromium',
        },
      },
    },
  },
  thresholds: {
    // 嚴格 Core Web Vitals 前端指標門禁 (Google 官方良好體驗門檻)
    browser_web_vital_lcp: ['p(95)<2500'], // Largest Contentful Paint < 2.5s
    browser_web_vital_cls: ['p(95)<0.1'],  // Cumulative Layout Shift < 0.1
    checks: ['rate==1.00'],
  },
};

const PRODUCT_URL = __ENV.TARGET_URL || 'https://appenvdev.field-eng-demo.grafana.net/product/66VCHSJNUP';

export default async function () {
  // 建立全新隔離的無頭瀏覽器頁面
  const page = await browser.newPage();

  try {
    // 導航至望遠鏡商品頁，等待網路閒置以確保 Next.js 完成 Hydration
    await page.goto(PRODUCT_URL, { waitUntil: 'networkidle' });

    // 檢查瀏覽器頁面標題
    const title = await page.title();
    check(title, {
      '頁面標題包含 OTel demo': (t) => t.includes('OTel demo'),
    });

    // 驗證商品主要標題 h2 是否正確渲染
    const heading = await page.locator('h2').textContent();
    check(heading, {
      '商品名稱正確渲染': (h) => h && h.includes('Starsense Explorer'),
    });
  } finally {
    // 軍規級防護：無論測試成功或丟出例外，保證關閉頁面，杜絕 Chromium 殭屍進程！
    await page.close();
  }
}
```

##### 終端真實執行輸出與 Web Vitals 解析

```text
  █ TOTAL RESULTS 
    checks_succeeded...: 100.00% 2 out of 2
    ✓ 頁面標題包含 OTel demo
    ✓ 商品名稱正確渲染

    BROWSER
    browser_data_received.......: 1.4 MB 714 kB/s
    browser_data_sent...........: 108 kB 56 kB/s
    browser_http_req_duration...: avg=416.54ms min=31.84ms med=353.03ms max=702.98ms
    browser_http_req_failed.....: 0.00%  0 out of 30

    WEB_VITALS
    browser_web_vital_cls.......: avg=0.000646 min=0.000646 med=0.000646 max=0.000646
    browser_web_vital_fcp.......: avg=980ms    min=980ms    med=980ms    max=980ms
    browser_web_vital_lcp.......: avg=980ms    min=980ms    med=980ms    max=980ms
    browser_web_vital_ttfb......: avg=654ms    min=654ms    med=654ms    max=654ms
```

> [!IMPORTANT]
> **瀏覽器測試三大關鍵洞察**：
> 1. **真實資源開銷**：純 HTTP 測試只下載了 50KB 的 HTML，但真實瀏覽器測試加載了 **30 個靜態資產**（Next.js chunks、字型、高解析望遠鏡圖片），共計 **1.4MB**，真實暴露前端 CDN 與客戶端頻寬瓶頸！
> 2. **LCP 為 980ms**：遠優於 2.5 秒的 Google 綠色良好標準。
> 3. **CLS 僅 0.000646**：表明 Next.js 在渲染商品詳情與圖片時版面極為穩定，完全沒有畫面突兀跳動的劣質體驗。

---

#### 技能 5：`k6-playwright-converter` (Playwright 測試無痛轉譯)

* **核心定位**：讀取團隊現有的 Playwright 或 Puppeteer E2E 功能測試代碼，精準提取選擇器與業務流程，無痛轉譯為相容 k6 高併發架構與 Web Vitals 採樣的混合壓測腳本。
* **常見觸發詞**：`"convert Playwright script"`, `"migrate E2E test to k6"`, `"transform ui test"`

##### 實戰演示：將現有 Playwright E2E 功能測試升級為 k6 混合壓測

一般 QA 團隊通常擁有如下撰寫的標準 Playwright 功能測試：

```typescript
// 原生 Playwright E2E 測試 (tests/astronomy.spec.ts)
import { test, expect } from '@playwright/test';

test('使用者應能瀏覽望遠鏡商品並檢視詳情', async ({ page }) => {
  await page.goto('https://appenvdev.field-eng-demo.grafana.net');
  await expect(page).toHaveTitle(/OTel demo/);

  // 點擊第一個望遠鏡商品卡片
  await page.locator('a[href^="/product/"]').first().click();
  await expect(page.locator('h2')).toBeVisible();

  // 驗證包含加入購物車按鈕
  const addToCartBtn = page.locator('button', { hasText: /Add To Cart/i });
  await expect(addToCartBtn).toBeEnabled();
});
```

> **💬 使用者對話 Prompt**：
> 「我們手邊有一段 Playwright 測試，驗證從首頁進入 Astronomy Shop (`https://appenvdev.field-eng-demo.grafana.net`) 並點選望遠鏡商品查看購物車按鈕。請使用 `k6-playwright-converter` 幫我無痛轉譯為相容 k6 高併發架構的 `k6/browser` 腳本，加入 think time 模擬真實使用者，並升級加入 Core Web Vitals 效能監控門檻！」

##### 轉譯後生成的生產級 k6/browser 腳本

```javascript
import { browser } from 'k6/browser';
import { check } from 'k6';

export const options = {
  scenarios: {
    astronomy_e2e_journey: {
      executor: 'shared-iterations',
      iterations: 1,
      options: {
        browser: {
          type: 'chromium',
        },
      },
    },
  },
  thresholds: {
    // 轉譯時自動注入性能門禁
    browser_web_vital_lcp: ['p(95)<2500'],
    browser_web_vital_cls: ['p(95)<0.1'],
    checks: ['rate==1.00'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://appenvdev.field-eng-demo.grafana.net';

export default async function () {
  const page = await browser.newPage();

  try {
    // 1. 導航至首頁 (等同 page.goto)
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    const title = await page.title();
    check(title, {
      '首頁標題符合預期': (t) => t.includes('OTel demo'),
    });

    // 模擬使用者閱覽首頁商品 (1 秒 Think Time；async 瀏覽器流程中用 waitForTimeout 取代 sleep)
    await page.waitForTimeout(1000);

    // 2. 點選望遠鏡商品卡片 (等同 page.locator('...').first().click())
    const productLink = page.locator('a[href^="/product/"]').first();
    await productLink.click();
    await page.waitForLoadState('networkidle');

    // 3. 解決非同步 Check 陷阱：先 await 取出文字再進行 check 斷言
    const headingText = await page.locator('h2').textContent();
    check(headingText, {
      '商品名稱標題正常顯示': (text) => text && text.trim().length > 0,
    });

    // 4. 驗證加入購物車按鈕存在且可用
    const addToCartBtn = page.locator('button');
    const btnText = await addToCartBtn.textContent();
    check(btnText, {
      '加入購物車按鈕已呈現': (text) => text && text.includes('Add To Cart'),
    });
  } finally {
    // 自動補全軍規資源清理
    await page.close();
  }
}
```

##### 四大轉譯關鍵架構剖析

| 轉譯維度 | 原始 Playwright 測試 | 轉譯後 k6/browser 壓測 | 轉譯價值與避坑要點 |
| :--- | :--- | :--- | :--- |
| **執行架構** | `test('...', async ({ page }) => ...)` 單一功能斷言 | `options.scenarios` 宣告式模型 + `export default async` | 賦予其與 10,000 個 Protocol VU 同時併發執行的能力 |
| **非同步斷言陷阱** | `await expect(locator).toHaveText(...)` 鏈式語法 | 先 `await locator.textContent()` 取值再 `check(val, ...)` | **致命坑點**：k6 原生 `check()` 不支援 Promise；若直接傳 Promise 物件進去會永遠判定為真（假通過），AI 自動重構為正確的兩段式求值 |
| **資源清理** | 由 Playwright Runner 在測試後全域回收 | 強制注入 `try { ... } finally { await page.close() }` | 壓測高併發下若拋出例外，未關閉的 Chromium 進程會迅速耗盡伺服器 RAM 導致 OOM Crash |
| **體驗維度升級** | 僅驗證「功能對與錯」(Functional Correctness) | 升級納入 `browser_web_vital_lcp` / `cls` 時延監控 | 讓功能測試無縫升級為兼具體驗品質的效能指標守門員 |

---

### 完整 11 大 AI 擴充技能庫全覽矩陣與進階維護指南

除了上述 5 大核心工作流技能外，`k6 x agent` 還打包了 6 款進階的維護、診斷與雲端治理工具，構成完整的效能工程工具鏈：

| 技能名稱 | 核心職責 | 典型觸發指令 / Prompt | 適用場景與技術亮點 |
| :--- | :--- | :--- | :--- |
| **`k6-docs`** | 官方知識庫權威檢索 | `"lookup thresholds syntax"`, `"k6 x docs javascript-api"` | 調用 `k6 x docs` 直接檢索二進位檔內建的最新官方文件，AI 絕不胡編濫造 |
| **`k6-test-maintenance`** | 既有腳本審計與重構 | `"tighten thresholds"`, `"fix deprecated APIs"`, `"audit script"` | 分類 Class A (宣告式門檻收緊) vs Class B (執行期邏輯微調)，支援 AST `k6 inspect` 靜態預檢 |
| **`k6-perf-test-website`** | 全站效能分析與混合工程 | `"performance test website"`, `"record HAR and convert"` | 提供 HAR 錄製過濾、`har-to-k6` 轉譯、99:1 混合架構組裝與 LG Monitor 本機 CPU 防自殘監控 |
| **`k6-cloud-investigate-test`** | 雲端壓測記錄與日誌排查 | `"investigate test run 12345"`, `"why did cloud test fail"` | 透過 `gcx api` 調取 Loki `{test_run_id}` 日誌，破解「Zero Observation Trap」零觀測樣本假通過盲點 |
| **`k6-manage`** | 雲端測試資產安全治理 | `"list cloud test runs"`, `"update cloud script safely"` | 實踐安全編輯黃金迴圈（GET -> Backup -> Edit -> Validate -> PUT -> SHA256 驗證） |
| **`k6-trend-analysis`** | 多版本趨勢與效能退化偵測 | `"compare last 5 runs"`, `"detect latency regression"` | 橫跨多版本比對 P95/P99 延遲與錯誤率，自動定位效能退化是應用代碼、資料庫還是網路問題 |

#### 6 大進階維護工具深度實戰指南

##### 1. `k6-docs`：官方知識庫權威檢索（杜絕 AI 幻覺）
AI 在生成代碼時常因訓練資料過期而拼錯 Threshold 語法或在 browser 內調用不支援的 API。`k6-docs` 賦予 AI 直接調用 `k6 x docs` 子命令的能力：
```bash
# 終端機可直接查詢任意 k6 主題
k6 x docs using-k6 thresholds
k6 x docs javascript-api k6-http
k6 x docs search "sharedarray"
```
AI 在生成腳本前會主動發起 MCP 查詢（例如 `get_documentation("best_practices")`），確保產出的每一行代碼完全符合當前安裝的 k6 版本規範！

##### 2. `k6-test-maintenance`：腳本健康維護與門檻收緊
在生產維運中，既有腳本往往隨著服務迭代而逐漸失修（例如端點更名、Thresholds 設定過於寬鬆）。該技能提供精準的變更分類控制：
* **Class A（宣告式配置變更）**：例如將 `p(95)<1000` 根據歷史真實表現收緊為 `p(95)<250`。此類變更不影響執行期邏輯，AI 會自動計算 SHA-256 並執行 `k6 inspect` 預檢，無需啟動雲端耗費測試配額。
* **Class B（執行期邏輯異動）**：例如更換請求 URL、修改 check 條件。AI 會強制要求使用者確認 Diff，並執行本地 1-VU 冒煙驗證後才允許發布。

##### 3. `k6-perf-test-website`：網站全站效能分析與 99:1 混合工作流
專門用於對全新外部網站進行端到端效能摸底。引導工程師依序執行：
1. **HAR 錄製**：使用 Playwright 錄製使用者真實操作，並以 Regex 過濾掉 Google Analytics 等第三方雜訊。
2. **轉譯清洗**：使用 `har-to-k6` 轉譯後，自動移除寫死的 Session Token，並將端點替換為 `__ENV.BASE_URL`。
3. **本機防自殘監控 (LG Monitor)**：透過背景腳本 `run-with-monitor.sh` 即時監控本機 CPU 與記憶體，若 Idle < 10% 則自動警告使用者「本機負載機已成為瓶頸」，避免誤把自己的電腦卡死當成後端伺服器崩潰！

##### 4. `k6-cloud-investigate-test`：Grafana Cloud 壓測排查與避坑
排查雲端壓測記錄時，AI 會透過 `gcx api` 提取 Grafana Cloud 上的 Loki 結構化日誌。更重要的是，該技能內建了 **「Zero Observation Trap（零觀測樣本假通過）」** 陷阱防護：
> 在 k6 中，如果一個 Threshold 對應的 Metric 完全沒有任何觀測值（例如腳本在執行到 check 之前就發生例外崩潰中斷），k6 預設會顯示 `✓ pass`！該技能會主動審計腳本，引導在 `catch` 區塊強制補上 `check(null, { "completed": false })`，徹底根除漏報風險。

##### 5. `k6-manage`：Grafana Cloud 測試資產安全治理
管理企業在 Grafana Cloud k6 (GCk6) 上託管的數百個壓測專案。嚴格遵循「安全編輯黃金迴圈」：
$$\text{GET (下載原檔)} \longrightarrow \text{Backup (時間戳備份)} \longrightarrow \text{Edit (AI 局部重構)} \longrightarrow \text{k6 inspect (語法校驗)} \longrightarrow \text{PUT (推播更新)} \longrightarrow \text{SHA-256 (雜湊比對)}$$
杜絕多人協作時手滑覆蓋他人腳本的嚴重生產事故。

##### 6. `k6-trend-analysis`：多版本趨勢洞悉與效能回歸偵測
在 CI/CD 中多次執行壓測後，該技能會自 Grafana Cloud 抓取最近 10 次執行的時間序列數據，自動輸出跨版本比較表格：
```text
| Commit  | Build Date | P95 Duration | Error Rate | 判定結果 |
|---------|------------|--------------|------------|----------|
| 3a89e1  | 2026-09-20 | 185ms        | 0.00%      | Baseline |
| 4f12b8  | 2026-09-21 | 192ms        | 0.00%      | Pass     |
| 9d78c3  | 2026-09-22 | 480ms (+150%)| 1.20%      | REGRESSION DETECTED! |
```
AI 會自動分析退化發生的端點，交叉比對資料庫連線池與 GC 延遲，為開發團隊產出第一手的效能回歸診斷摘要。

###### 延伸應用：讓 AI 分析「單次 Soak 內」的趨勢

`k6-trend-analysis` 比較的是**多次執行之間**的趨勢（依賴 Grafana Cloud）。若要分析**單次 Soak 測試內部**的洩漏訊號，可直接把本機輸出的原始數據（`k6 run --out json=raw.json soak.js`）交給 AI 編輯器，並把 Chapter 5「Soak 判讀」的邏輯寫進 Prompt：

```text
請讀取 raw.json（60 分鐘 Soak：5 分鐘暖身、50 分鐘固定 20 VU、5 分鐘收尾）。
1. 以 5 分鐘為一桶，算出每桶的 p50、p95、錯誤率、rps、http_req_blocked p95。
2. 只看 50 分鐘固定負載那一段：對 p95、錯誤率、rps 各做線性趨勢，給出斜率與方向，
   並判斷是「持平」「緩慢爬升」「階梯狀」還是「下滑」。
3. 依端點（tags.name）拆開，指出趨勢最明顯的前三個端點。
4. 收尾段負載歸零後，最後一桶與第一桶的 p95 相比如何？系統有沒有恢復？
5. 對照「緩慢爬升＝記憶體/GC 壓力、階梯狀錯誤＝有限資源耗盡、rps 下滑＋blocked 上升＝連線層」，
   給出你的推測。每一條推測都標註〔推論〕，並說明還需要哪一項後端數據才能確認。
```

Positive
: **為什麼要求 AI 標註〔推論〕？** k6 端只看得到「果」。AI 能從曲線形狀推測可能的洩漏類型，但沒有後端監控數據對照前，任何根因都只是推論。要求 AI 明確標示推論，並列出需要補的後端數據，才不會把猜測寫進給開發團隊的報告裡。（此 Prompt 改寫自 iThome 鐵人賽〈[Day 24｜Soak Test：從 k6 端數據推測伺服器在漏什麼](https://ithelp.ithome.com.tw/articles/10413194)〉）

---

### 企業導入實作 Checklist：AI 壓測工程化最佳實踐

![企業導入實作 Checklist：AI 壓測工程化最佳實踐](assets/images/k6-ch6-slide-6.png)

將 AI Agent 融入團隊研發管線、建立腳本審計、記憶體防護與閉環自癒機制：

| 維度 | 關鍵檢核點 (Action Items) | 預期工程效益 |
| :--- | :--- | :--- |
| **1. 配置治理與團隊協作** | • 將 `.cursor/rules` 納入 Git 版本控管<br>• 敏感 API Token 透過環境變數注入<br>• CI Pipeline 執行 `k6 x agent status` 檢驗環境 | 全團隊共享統一的 AI 壓測提示詞標準，杜絕配置漂移 |
| **2. AI 閉環自癒工程** | • 生成腳本後 AI 必調用 `validate_script` 預檢<br>• 嚴格落實「大併發前先跑 1 VU 冒煙先驗」<br>• AI 解析 k6 終端日誌自動修正報錯代碼 | 將傳統 30 分鐘手動除錯縮短為秒級自主自癒 |
| **3. 高基數記憶體防護** | • AI 技能規則嚴格強制使用 `http.url` 標籤<br>• 嚴禁以模板字串拼接動態 ID (`/users/${id}`)<br>• 大量測試資料強制由 `SharedArray` 載入 | 從根本杜絕 Prometheus 時間序列爆炸與 OOM 崩潰 |
| **4. 官方生態系資源** | • 關注 GitHub `grafana/xk6-subcommand-agent`<br>• 定期執行 `k6 x agent init --force` 同步技能包<br>• 搭配 Prometheus Remote Write 達成全鏈路可觀測 | 讓團隊壓測能力隨 Grafana 官方最新演進持續升級 |

---

### 手把手實作演練：k6 x agent 現代化 AI 壓測工程實戰

![Chapter 6 AI Agent Engineering Demo](assets/images/k6-ch6-agent-workflow.gif)

#### 實作 1：檢查本機工作區 AI 狀態與 MCP 原生支援（k6 x agent status）

在專案根目錄執行狀態檢查命令，觀察 k6 的 **Automatic Extension Resolution（自動擴充解析機制）** 與編輯器適配狀態：

![k6 x agent status 狀態檢核](assets/images/k6-ch6-agent-status.png)

```bash
# 檢查當前專案工作區的 AI 編輯器與 MCP 連線狀態
k6 x agent status
```

**終端真實執行輸出**：
```text
nathan@o11y-lab:~/Project/o11y_lab_for_dummies$ k6 x agent status
INFO[0000] Automatic extension resolution is enabled. The current k6 binary doesn't satisfy all dependencies, it's required to provision a custom binary.  deps="subcommand:agent"
INFO[0000] Using cached k6 binary                        artifact_id=976b21276989fad3b6480294c0662247e292396f deps="map[k6:v2.2.0 subcommand:agent:v0.2.1]" path=/home/nathan/.cache/k6/builds/976b21276989fad3b6480294c0662247e292396f/k6
Agent installation status

[+] Claude Code
   - .mcp.json detected

[-] Cline
   - Not detected in this workspace
   - Hint: k6 x agent init cline

[-] OpenAI Codex CLI
   - Missing: .codex/mcp.json
   - Hint: k6 x agent init codex-cli

[+] Cursor
   - .cursor/mcp.json detected

[-] OpenCode
   - Missing: opencode.json
   - Hint: k6 x agent init opencode

[-] VSCode/GitHub Copilot
   - Missing: .vscode/mcp.json
   - Hint: k6 x agent init vscode-copilot

[+] k6 MCP support
   - Found at /usr/bin/k6
```

**終端執行輸出深度解析**：
* **`Automatic extension resolution`**：`k6 v2.2+` 內建自動依賴解析機制，當呼叫 `x agent` 或 `x mcp` 時，k6 會動態從官方二進位庫按需下載擴充套件（如 `subcommand:agent:v0.2.1` 與 `subcommand:mcp:v0.6.1`），存於 `~/.cache/k6/builds/`，完全免除本機預裝 Go 或 npm 的負擔。
* **`[+] Claude Code` 與 `[+] Cursor`**：當我們為 Cursor 與 Claude Code 執行 `init` 後，狀態會從 `[-]` 變成綠色 `[+]`，標記 `.mcp.json` 與相關技能規則已正確就位。
* **`[+] k6 MCP support`**：系統在 `/usr/bin/k6` 偵測到原生 MCP 支援，代表 AI 助手可透過 Model Context Protocol 直接呼叫 k6 執行腳本驗證。

---

#### 實作 2：探索 11 大內建技能庫與 Prompt 規則檢索（skills list & skills show）

透過 `k6 x agent skills` 系列指令，你可以隨時查看二進位檔內建的所有技能，甚至直接印出官方 Prompt 規範：

![k6 x agent skills list 技能清單與檢索](assets/images/k6-ch6-agent-skills-list.png)

```bash
# 1. 列出二進位檔內建的所有 AI 技能清單
k6 x agent skills list

# 2. 查看特定技能的完整 Prompt 規則（以 k6-smoke-test 為例）
k6 x agent skills show k6-smoke-test
```

**`skills list` 終端真實輸出**：
```text
NAME                       DESCRIPTION
k6-browser-test            Use this skill when the user wants to write a k6 browser test that in...
k6-cloud-investigate-test  Investigate a Grafana Cloud k6 test — describe the script, list run...
k6-docs                    Look up official k6 documentation with `k6 x docs` when writing, debu...
k6-load-test               Use this skill when the user says "write a k6 script", "generate a k6...
k6-manage                  Interact with Grafana Cloud k6 (GCk6) — manage load tests, test run...
k6-perf-test-website       Use when the user wants to performance-test, load-test, or stress-tes...
k6-playwright-converter    Use this skill when a user provides a Playwright script and needs a f...
k6-smoke-test              Use this skill when the user wants a quick k6 smoke test to verify ba...
k6-test-maintenance        Maintain and improve existing k6 test scripts. Covers threshold tight...
k6-test-planner            Use this skill to plan k6 test suites from natural-language requireme...
k6-trend-analysis          Analyze Grafana Cloud test trends and detect regressions...
```

**`skills show k6-smoke-test` 核心規則解析**：
執行 `skills show` 會直接將編譯在 k6 內部的 Markdown Prompt 印到終端：
```markdown
You are a senior k6 performance engineer. You create lightweight smoke tests that verify an application's basic functionality under minimal load — the first line of defence before heavier performance testing.

## Workflow
1. Scope & Inputs: A smoke test should cover the happy path only — no stress, no edge cases.
2. Design & Development:
   - Use 1–5 VUs with a short duration (30s–2m).
   - Prefer constant-vus executor for simplicity.
   - Include check() calls for every critical assertion.
   - Set strict thresholds: http_req_failed: ['rate==0'], http_req_duration: ['p(95)<500'].
   - Parameterise base URL via environment variable (__ENV.BASE_URL).
```
這意味著團隊可以**零時差檢驗官方提示詞工程標準**，無需到處翻找檔案即可知悉 AI 的決策邏輯！

---

#### 實作 3：安全預覽安裝檔案與路徑（--dry-run 零副作用檢核）

在正式修改磁碟前，利用 `--dry-run` 旗標預覽即將產生的規則與設定檔：

![k6 x agent init cursor --dry-run 安全預覽](assets/images/k6-ch6-agent-init-dryrun.png)

```bash
# 針對 Cursor 編輯器進行乾跑預覽
k6 x agent init cursor --dry-run

# 針對 Claude Code 進行乾跑預覽
k6 x agent init claude-code --dry-run
```

**預覽檢核要點**：
* **Cursor 格式**：產生 11 個 `.cursor/rules/*.mdc` 規則檔案，並智慧合併（`[merge]`）`.cursor/mcp.json`。
* **Claude Code 格式**：產生 `.claude/skills/*/SKILL.md` 目錄結構，並合併根目錄的 `.mcp.json` 與 `.claude/settings.local.json`。
* 乾跑模式下完全零磁碟寫入，避免誤更動專案檔案。

---

#### 實作 4：一鍵初始化 AI 編輯器與檢核配置（.cursor/mcp.json 與 11 大技能包）

確認無誤後，正式執行初始化命令：

![k6 x agent init cursor 初始化完成](assets/images/k6-ch6-agent-init-cursor.png)

```bash
# 1. 初始化 Cursor 編輯器環境
k6 x agent init cursor

# 2. 或初始化 Claude Code 終端環境
k6 x agent init claude-code

# 檢視自動產生的 MCP 設定檔
cat .cursor/mcp.json  # Cursor 專屬配置
cat .mcp.json         # Claude Code 專屬配置

# 檢視自動產生的 AI 技能規則檔案頭部
head -n 7 .cursor/rules/k6-smoke-test.mdc
```

**產出檔案檢驗**：
* `.cursor/mcp.json` 或 `.mcp.json` 內容如下，註冊了本地的原生 k6 MCP 伺服器：
  ```json
  {
    "mcpServers": {
      "k6": {
        "command": "k6",
        "args": ["x", "mcp"]
      }
    }
  }
  ```
* 規則檔案首部包含 `<!-- generated by k6 x agent -->` 擁有者防護標籤，防止未來的更新覆蓋手動修改的客製化規則。

---

#### 實作 5：AI 閉環驗證與自癒：調用 validate_script 與 run_script

當 AI 編輯器連線至 `k6 x mcp` 後，AI 助手即可自動調用原生 MCP 工具：

![k6 x mcp validate_script 閉環驗證](assets/images/k6-ch6-mcp-validation.png)

```bash
# k6 x mcp 伺服器原生提供 6 大標準工具：
# 1. validate_script: 以 1 VU、1 次迭代實際執行腳本，偵測語法、執行期與網路問題
# 2. run_script: 以指定的 VU 與 duration 執行測試，回傳 stdout 與 metrics（上限 50 VUs / 5 分鐘）
# 3. get_documentation: 精準擷取 k6 官方 Markdown 文件內容
# 4. list_sections: 樹狀瀏覽 k6 文件章節結構
# 5. info: 取得 local k6 binary 與 Grafana Cloud 登入狀態
# 6. search_terraform: 搜尋 Grafana Terraform 壓測資源
```

當你在 AI 聊天視窗要求生成腳本時，AI 會在背後發送 JSON-RPC 請求給 `validate_script`：
```json
{
  "valid": true,
  "summary": { "status": "success", "issue_count": 0, "ready_to_run": true },
  "stdout": "checks_succeeded: 100.00% (7/7) | http_req_duration: p(95)=194.4ms",
  "recommendations": ["✓ Validation passed! Your script is ready for load testing"]
}
```
若有語法錯誤或端點無法連線，AI 會接收到結構化報錯，自動修正代碼後再次驗證，形成自主閉環自癒！

#### 實作 6：實戰執行 AI 逆向生成之 QuickPizza 冒煙測試腳本

專案中自帶了 AI 遵循最佳實踐規範生成的示範冒煙腳本 `k6/demos/ch6_quickpizza_smoke_agent.js`：

```bash
# 執行 AI 逆向生成並通過 MCP 驗證的 QuickPizza 冒煙測試
k6 run k6/demos/ch6_quickpizza_smoke_agent.js
```

腳本完整原始碼一覽：
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 1,
  duration: '3s',
  thresholds: {
    // 冒煙品質門禁：不可有任何請求失敗，且 100% check 成功
    http_req_failed: ['rate==0.00'],
    http_req_duration: ['p(95)<1000'],
    checks: ['rate==1.00'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://quickpizza.grafana.com';

export default function () {
  // 1. 探測首頁 HTML
  const homeRes = http.get(BASE_URL, { tags: { name: 'GetHomePage' } });
  check(homeRes, {
    '首頁回應 200 OK': (r) => r.status === 200,
    '首頁包含 QuickPizza 標題': (r) => r.body && r.body.includes('QuickPizza'),
  });

  // 2. 探測系統組態 API (/api/config)
  const configRes = http.get(`${BASE_URL}/api/config`, { tags: { name: 'GetConfig' } });
  check(configRes, {
    'Config API 回應 200 OK': (r) => r.status === 200,
    'Config 回傳 JSON 格式': (r) => r.headers['Content-Type'] && r.headers['Content-Type'].includes('application/json'),
  });

  // 3. 查詢名言佳句 API (/api/quotes)
  const quotesRes = http.get(`${BASE_URL}/api/quotes`, { tags: { name: 'GetQuotes' } });
  check(quotesRes, {
    'Quotes API 回應 200 OK': (r) => r.status === 200,
    'Quotes 回傳陣列資料': (r) => {
      try {
        const data = r.json();
        return data && Array.isArray(data.quotes) && data.quotes.length > 0;
      } catch (e) {
        return false;
      }
    },
  });

  sleep(1);
}
```

執行後終端呈現：
* `checks_succeeded: 100.00% 14 out of 14`
* `http_req_failed: 0.00%`
* `p(95) = 193.26ms < 1000ms`
* Exit code 為 `0`，驗證全數通過！

---

#### 實作 7：實戰壓測真實旗艦網站 ── Astronomy Shop (OpenTelemetry Demo)

除了 QuickPizza 外，專案更收錄了一份針對 Grafana 官方旗艦電商示範應用 ── **Astronomy Shop** (`https://appenvdev.field-eng-demo.grafana.net`) 的完整實戰演示腳本 [`k6/demos/ch6_otel_astronomy_shop.js`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/demos/ch6_otel_astronomy_shop.js)：

```bash
# 執行 AI 規範生成的 Astronomy Shop 階梯負載與購物車壓測腳本
k6 run k6/demos/ch6_otel_astronomy_shop.js
```

**核心實踐特色**：
1. **`SharedArray` 記憶體最佳化**：跨 VU 唯讀映射 5 款熱門望遠鏡（Explorascope、Starsense、Eclipsmart 等），零冗餘拷貝。
2. **完整電商核心旅程**：模擬「商品目錄瀏覽 (`GetProductCatalog`) $\to$ 單一規格查詢 (`GetProductDetail`) $\to$ 購物車寫入 (`AddToCart`)」全鏈路。
3. **精準 Tagged Thresholds 門禁**：針對各端點單獨訂定 P95 門檻，第一時間揪出是目錄查詢慢還是購物車寫入慢。
4. **隨機思考時間 (Think Time)**：以 `sleep(1 + Math.random() * 1)` 模擬真實人類操作間隔，徹底破解協調性漏測盲點。

**終端真實執行輸出**：
```text
  █ THRESHOLDS 
    checks..........................................: ✓ 'rate==1.00' rate=100.00%
    http_req_duration...............................: ✓ 'p(95)<800'  p(95)=209.9ms
      {name:AddToCart}..............................: ✓ 'p(95)<600'  p(95)=176.31ms
      {name:GetProductCatalog}......................: ✓ 'p(95)<500'  p(95)=307.12ms
      {name:GetProductDetail}.......................: ✓ 'p(95)<400'  p(95)=164.6ms
    http_req_failed.................................: ✓ 'rate<0.01'  rate=0.00%

  █ TOTAL RESULTS 
    checks_succeeded...: 100.00% 72 out of 72
    http_reqs..........: 36     3.385477/s
    iterations.........: 12
```

如果你想進一步量測 Astronomy Shop 前端頁面的真實渲染體驗，可直接在終端機執行下列命令，啟動無頭 Chromium 採集 Core Web Vitals：
```bash
# 使用真實無頭 Chromium 採集 Astronomy Shop 望遠鏡頁面的 Core Web Vitals
k6 run - << 'EOF'
import { browser } from 'k6/browser';
import { check } from 'k6';

export const options = {
  scenarios: {
    ui: { executor: 'shared-iterations', iterations: 1, options: { browser: { type: 'chromium' } } },
  },
  thresholds: {
    browser_web_vital_lcp: ['p(95)<2500'],
    browser_web_vital_cls: ['p(95)<0.1'],
  },
};

export default async function () {
  const page = await browser.newPage();
  try {
    await page.goto('https://appenvdev.field-eng-demo.grafana.net/product/66VCHSJNUP', { waitUntil: 'networkidle' });
    const title = await page.title();
    check(title, { 'Title OK': (t) => t.includes('OTel demo') });
  } finally {
    await page.close();
  }
}
EOF
```
終端將即時印出 `browser_web_vital_lcp`（~980ms）與 `browser_web_vital_cls`（~0.0006），體驗極致流暢！

---

### 隨堂實作練習指引：AI 輔助壓測三部曲

![隨堂實作練習指引：AI 輔助壓測三部曲](assets/images/k6-ch6-slide-7.png)

請依序完成三大實戰任務，親身體驗 `k6 x agent` 的一鍵配置與 AI 輔助壓測閉環：

#### 任務一：一鍵初始化本地 AI 編輯器與狀態檢核
- **任務目標**：為你的主力編輯器（例如 Cursor 或 Claude Code）配置 k6 技能與 MCP 伺服器，並驗證連線健康度。
- **實作指令**：
  ```bash
  k6 x agent init cursor       # 若使用 Claude Code，改為 k6 x agent init claude-code
  k6 x agent status            # 檢查 MCP 與 11 大技能連線狀態
  ```
- **驗證標準**：`.cursor/rules/` 目錄下產生 11 個 `.mdc` 規則檔案，且 `.cursor/mcp.json` 正確註冊 `k6 x mcp`。

#### 任務二：AI 逆向生成冒煙測試並閉環自癒 (QuickPizza 或 Astronomy Shop)
- **任務目標**：利用內建 `k6-smoke-test` 技能與 MCP 工具，逆向生成冒煙測試並由 AI 本機跑通 1 VU 冒煙。
- **實作 Prompt (可擇一實作)**：
  * **選項 A (QuickPizza)**：
    > "針對 QuickPizza 的 `/api/quotes` 與 `/api/config` 端點撰寫 1 VU 冒煙測試腳本，包含 check 斷言與 `http.url` 標籤，並請使用 `validate_script` 驗證腳本合法性。"
  * **選項 B (Astronomy Shop 旗艦商城)**：
    > "針對 Astronomy Shop (`https://appenvdev.field-eng-demo.grafana.net`) 的商品目錄 `/api/products` 與詳情 `/api/products/OLJCESPC7Z` 端點撰寫 1 VU 冒煙測試腳本，要求零錯誤率門檻與 tags 標籤防高基數，並調用 `validate_script` 完成自癒預檢。"
- **驗證標準**：AI 產生合規腳本並調用 `validate_script` 驗證通過，無語法錯誤與動態 URL 拼接。

#### 任務三：Playwright 測試無痛轉譯為 k6 混合壓測與 Web Vitals 量測
- **任務目標**：利用 `k6-playwright-converter` 技能將 E2E 測試升級為具備真實瀏覽器性能量測的混合壓測腳本。
- **實作 Prompt**：
  > "請將 Astronomy Shop 的 Playwright 商品瀏覽測試（訪問首頁並點擊望遠鏡卡片）轉譯為 k6 browser 腳本，加入 `finally { await page.close() }` 軍規保護，並設定 LCP < 2500ms 與 CLS < 0.1 體驗門檻。"
- **驗證標準**：產出標準 `k6/browser` 語法，加入 `try...finally` 關閉瀏覽器，並具備 Core Web Vitals 採樣與驗證。

---

### Chapter 6 核心心智模型與 AI 壓測避坑指南

<aside class="positive">
<b>💡 心智模型轉移：從「人肉腳本工人」躍升為「AI 壓測架構師」</b><br>
過去效能工程師花費 80% 時間在繁瑣的 API 抓包、語法除錯、動態參數關聯與設定檔配置。藉助 <code>k6 x agent</code> 與 MCP 原生閉環能力，工程師將轉型為高階壓測架構師：專注於商業 SLO 定義、流量模型規劃與瓶頸根因分析，而將機械性的腳本生成、語法預檢與冒煙驗證交由 AI Agent 自動完成！
</aside>

<aside class="negative">
<b>⚠️ 企業級 AI 壓測三大紅線</b><br>
1. <b>嚴禁動態字串拼接 URL</b>：要求 AI 產出代碼時，必須遵循 <code>tags: { name: '...' }</code> 或 <code>http.url</code> 規範，防止時間序列爆炸癱瘓監控系統。<br>
2. <b>大併發前必先 1 VU 冒煙</b>：不可在未經 <code>validate_script</code> 驗證下直接調度 1,000 VU，避免大量無效流量衝擊測試環境。<br>
3. <b>大數據集必用 SharedArray</b>：要求 AI 載入萬筆以上測試帳號時，必須採用 <code>SharedArray</code> 進行唯讀記憶體映射，防止記憶體洩漏引發 OOM Crash。
</aside>

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
