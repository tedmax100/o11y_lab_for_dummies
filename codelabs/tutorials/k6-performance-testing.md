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
: 本專案的所有配套演示腳本均已收錄於專案的 `k6/demos/` 目錄中，並通過本機環境完整實測！

---

## Chapter 1: k6 核心哲學與腳本基礎手把手
Duration: 15

### 傳統壓測痛點 vs Testing as Code

在過去十年間，Apache JMeter 是效能測試的代名詞。然而在現代 DevOps 與 GitOps 體系下，傳統工具帶來了三大致命痛點：

1. **配置維護地獄**：肥大且巢狀的 XML 格式無法進行有意義的 Git Diff 與 Code Review，團隊多人協作必定發生 Merge Conflict。
2. **開發體驗斷層**：後端與 SRE 工程師日常使用現代 IDE 與程式語言，卻被迫切換到老舊的 Java GUI 介面點擊拉節點，腳本淪為無人維護的技術債。
3. **CI/CD 自動化整合成本極高**：啟動耗時、資源沉重，難以在輕量 CI Runner 容器中快速執行與退出。

**Grafana k6** 的核心哲學是 **Testing as Code**：以純粹的 JavaScript/ES6 撰寫測試，享有現代模組化、Linter、自動補全與版本控制優勢。

### 底層架構優勢：Goroutine vs 傳統執行緒

k6 雖然腳本寫的是 JavaScript，但其底層執行引擎完全由 **Go 語言** 編寫（內建 Goja JS Runtime）：

| 評估維度 | 傳統 JVM 工具 (JMeter) | Grafana k6 (Go 引擎) |
| :--- | :--- | :--- |
| **併發模型** | One OS Thread per Virtual User (VU) | Go Goroutine 輕量級協程 |
| **單 VU 記憶體開銷** | 1MB ~ 2MB (Thread Stack) | **僅約 2KB ~ 4KB** |
| **Context Switch 開銷** | 高 (由作業系統核心頻繁排程) | 極低 (由 Go Runtime 在使用者空間高效調度) |
| **單機併發能力** | 約 1,000 ~ 2,000 VUs 即達硬體瓶頸 | **單台普通機器可輕鬆驅動 30,000+ VUs** |

### k6 全平台安裝指南 (Installing k6)

k6 為單一獨立二進位檔（Single Binary），不依賴外部執行環境（無須預裝 Node.js 或 Go）。依據您的作業系統選擇合適的安裝方式：

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

### 軟斷言 check() 與避免高基數爆炸

- **check() 是軟斷言**：與單元測試中斷執行的 `assert` 不同，k6 的 `check()` 失敗時**不會停止測試**，而是記錄成功率。這確保了在大規模壓測中能精確統計出 99.9% 成功率，而非因偶發錯誤中途夭折。
- **避免高基數維度爆炸 (High Cardinality)**：嚴禁寫出 `http.get('/api/users/' + userId)`。當萬人併發產生數萬個不同 URL 時，Prometheus/Grafana 會因時序暴增而 OOM 崩潰！正確寫法是使用模板標籤函式：``http.url`https://api.example.com/users/${userId}` ``，指標將自動聚合在同一名稱下。

### 實作演練：執行第一支生命週期測試

打開終端機，執行專案準備好的演示腳本：

```bash
k6 run k6/demos/ch1_lifecycle_and_checks.js
```

Positive
: 觀察終端機輸出，確認 Init、Setup、VU Code 與 Teardown 的執行順序！

---

## Chapter 2: 科學化流量建模與協調性漏測破解
Duration: 20

### 五大經典壓測模式

在盲目加壓前，必須先依據業務場景科學化定義流量波形：

1. **Smoke Test (冒煙測試)**：1~2 VU，極短時間（1m），驗證 API 路由、鑑權與腳本邏輯通暢。
2. **Load Test (常規負載測試)**：平緩爬升 (Ramp-up) $\rightarrow$ 尖峰高原期 (Plateau) $\rightarrow$ 平緩降速 (Ramp-down)，驗證日常峰值下的 SLA/SLO。
3. **Stress Test (壓力極限測試)**：階梯式持續加壓衝破安全水位，尋找系統崩潰點 (Breaking Point)。
4. **Spike Test (突發尖峰測試)**：流量在數十秒內暴衝數十倍，考驗 Kubernetes HPA 自動擴展與自癒彈性。
5. **Soak Test (浸泡耐久測試)**：在基準負載下長跑數小時，揪出緩慢發生的 Memory Leak 與連線池枯竭。

### 協調性漏測 (Coordinated Omission) 致命盲點

由效能專家 Gil Tene 提出的 **Coordinated Omission** 是傳統壓測最大的數據謊言：

Negative
: **閉環模型 (Closed Loop Model - vus: 10)**：虛擬用戶必須等待前一個請求回應才能發送下一個。當後端資料庫卡頓 5 秒時，10 個 VU 全部被卡住，5 秒內發出的請求數暴跌至個位數！測試工具誤以為「平均延遲不高」，卻完全忽略了外部真實使用者在此時正在瘋狂排隊等待的慘劇！

### 開放模型實戰與利特爾法則 (Little's Law)

**開放模型 (Open Model)** 將抵達率 (Arrival Rate) 與 VU 解耦，強制維持每秒發出既定數量的請求：

```javascript
export const options = {
  scenarios: {
    open_model_traffic: {
      executor: 'constant-arrival-rate',
      rate: 100,             // 每秒鎖定 100 次迭代 (100 RPS)
      timeUnit: '1s',
      duration: '5m',
      preAllocatedVUs: 20,   // 依據利特爾法則精算的基準並發
      maxVUs: 150,           // 面對延遲突波時的動態緩衝池
    },
  },
};
```

#### 利特爾法則精算公式

$$L = \lambda \times W$$

- $L$：系統內並行量 (所需 VU 數)
- $\lambda$：請求抵達率 (目標 RPS)
- $W$：平均回應時間 (Latency，秒)

**精算範例**：目標 200 RPS，預期回應時間 100ms (0.1s)：  
$$L = 200 \times 0.1 = 20\text{ VUs}$$  
若極端延遲飆高至 1s，則需要 $200 \times 1 = 200\text{ VUs}$。因此設定 `preAllocatedVUs: 20`，`maxVUs: 250`。

### SharedArray 記憶體拯救神技

在萬人併發測試中，若在全域使用普通 JS 陣列載入 50MB 測試資料，k6 為每個獨立的 VU 虛擬機都會複製一份，1,000 個 VU 會消耗 50GB 記憶體，直接引發 OOM Crash！

```javascript
import { SharedArray } from 'k6/data';

// 唯讀共享記憶體：10,000 筆資料在記憶體中永遠只有一份！
const users = new SharedArray('users_dataset', function () {
  return JSON.parse(open('./large_users.json'));
});
```

### 實作演練：驗證開放模型與 SharedArray

```bash
# 1. 執行閉環模型 (延遲拖垮 RPS)
k6 run -e MODEL=closed k6/demos/ch2_closed_vs_open_model.js

# 2. 執行開放模型 (自動調派 VU 守住目標 RPS)
k6 run -e MODEL=open k6/demos/ch2_closed_vs_open_model.js

# 3. 驗證 SharedArray 極速低記憶體載入
k6 run k6/demos/ch2_shared_array.js
```

---

## Chapter 3: 效能指標解讀與 SLO 門檻自動化 (Quality Gates)
Duration: 20

### 微服務黃金準則：RED Method

解讀 k6 測試摘要時，請緊扣微服務監控的黃金準則：

- **Rate（吞吐速率）**：對應 k6 的 `http_reqs` (每秒請求總量)。
- **Errors（錯誤比率）**：對應 k6 的 `http_req_failed` (非預期狀態碼比例)。
- **Duration（回應延遲）**：對應 k6 的 `http_req_duration` (完整網路交互時間)。

### 破解平均值陷阱：尾端延遲 (Tail Latency)

Negative
: 永遠不要看平均值 (Average)！在 100 個請求中，99 個 10ms，1 個結帳請求卡了 10 秒，算出來的平均值依然只有約 109ms，看似一切正常。但那個最關鍵的買單用戶已經流失！

在定義 SLO 時，一律採用百分位數：
- **P95**：95% 請求優於此時間，為日常及格標準。
- **P99（尾端延遲，Tail Latency）**：精準捕捉體驗最差的 1% 用戶，防範微服務鏈路中的骨牌效應。

### 四大自訂指標型態 (Custom Metrics)

```javascript
import { Counter, Gauge, Rate, Trend } from 'k6/metrics';

const orderCount = new Counter('orders_total');              // 累計計數器
const activeWorkers = new Gauge('active_workers');           // 瞬時狀態規
const businessSuccess = new Rate('checkout_success_rate');   // 業務成功率 (0~1)
const dbLatency = new Trend('db_query_duration');            // 統計趨勢 (自動計算 p90/p95/avg)
```

### CI/CD 自動卡關關鍵：Exit Code 99

```
[k6 測試執行完畢] ──> 所有 Thresholds 及格 ──> Exit Code 0  ──> CI/CD 綠燈發布
                  └── 任何一項門檻違規 ──> Exit Code 99 ──> CI/CD 紅燈中斷阻斷！
```

在腳本中設定門檻，並搭配標籤精確控制各 API 的 SLO：

```javascript
export const options = {
  thresholds: {
    'http_req_failed': ['rate<0.01'], // 錯誤率 < 1%
    'http_req_duration{api:checkout}': ['p(99)<500'], // 關鍵 API P99 < 500ms
    'checkout_success_rate': [
      {
        threshold: 'rate>0.99',
        abortOnFail: true,      // 熔斷機制：一旦嚴重失敗立即腰斬測試，止損 CI 運算資源！
        delayAbortEval: '5s',   // 緩衝 5 秒再開始評估熔斷，避免冷啟動誤判
      },
    ],
  },
};
```

### 實作演練：親手觸發 Exit Code 99 阻斷

```bash
# 模擬門檻超標，驗證 Linux Shell 捕獲代碼 99
k6 run -e FAIL_SLO=true k6/demos/ch3_quality_gates_exit99.js ; echo "CI Exit Code: $?"
```

Positive
: 終端機最後一行印出 `CI Exit Code: 99`，證明自動化效能門禁成功阻斷！

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
| **LCP** | Largest Contentful Paint | 最大內容繪製時間（主視覺何時呈現） | $\le 2.5\text{s}$ |
| **FCP** | First Contentful Paint | 首次內容繪製時間（白屏時間結束） | $\le 1.8\text{s}$ |
| **INP** | Interaction to Next Paint | 互動到下次繪製延遲（點擊響應流暢度） | $\le 200\text{ms}$ |
| **TTFB** | Time to First Byte | 伺服器首位元組時間（後端與網路基礎開銷） | $\le 800\text{ms}$ |
| **CLS** | Cumulative Layout Shift | 累計版面配置位移（視覺穩定度） | $\le 0.1$ |

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
Duration: 20

### 破除數據孤島：原生 Web Dashboard

無需額外安裝任何資料庫或 Grafana，一行環境變數直接啟動原生動態儀表板：

```bash
K6_WEB_DASHBOARD=true k6 run script.js
# 開啟瀏覽器訪問：http://127.0.0.1:5665
```

#### CI/CD 匯出靜態 HTML 報告：Port=-1 退場神技

在 CI/CD 中，為避免 Web 伺服器一直佔據連接埠導致流水線無法結束，使用以下參數：

```bash
K6_WEB_DASHBOARD=true \
K6_WEB_DASHBOARD_PORT=-1 \
K6_WEB_DASHBOARD_EXPORT=report.html \
k6 run script.js
```

### xk6 擴充機制與 Docker 確定性編譯

當需要測試 Kafka、PostgreSQL/MySQL SQL 或 Redis 時，使用官方 Docker 映像檔進行確定性編譯：

```bash
docker run --rm \
  -u "$(id -u):$(id -g)" \
  -v "$(pwd):/xk6" \
  grafana/xk6 build latest \
  --with github.com/grafana/xk6-sql \
  --output /xk6/k6-custom
```

Positive
: 注意 `-v "$(pwd):/xk6"` 掛載點，確保編譯完成的二進位檔直接輸出至本機目錄！

### Prometheus Remote Write 與 Commit Tag 綁定

本 Lab 的 Prometheus 已啟用 `--web.enable-remote-write-receiver`，直接以時序串流推送指標，並綁定當前 Git 版本：

```bash
K6_PROMETHEUS_RW_SERVER_URL=http://localhost:9090/api/v1/write \
k6 run \
  -o experimental-prometheus-rw \
  --tag "commit_id=$(git rev-parse --short HEAD)" \
  script.js
```

### 顛峰時刻：Grafana 雙時間軸對齊除錯

在 Grafana 啟用 **Shared Crosshair（共享十字準星）**：

```
[14:02:00]  k6 API P95 Latency 曲線   ──> 突然垂直暴衝至 2.2 秒！
[14:02:00]  K8s Pod CPU CFS Throttling ──> 同一秒飆高至 85%！
```

**結論**：秒級破案！不是程式碼有 Bug，而是 Kubernetes Pod 的 CPU Limit 設得太緊，容器被 Linux 核心強迫降頻卡頓。將壓測與系統基礎設施指標對齊，徹底破除數據孤島！

### 實作演練：執行 Prometheus 推播演示

```bash
./k6/demos/ch5_prometheus_remote_write.sh
```

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

- **專案原始碼**：[`o11y_lab_for_dummies`](https://github.com/tedmax100/o11y_lab_for_dummies)
- **實機演示腳本全集**：[`k6/demos/`](https://github.com/tedmax100/o11y_lab_for_dummies/tree/main/k6/demos)
- **全系列簡報 PPTX**：[`k6/slides/`](https://github.com/tedmax100/o11y_lab_for_dummies/tree/main/k6/slides)
- **錄課口播逐字稿**：[`k6/slides/transcripts/`](https://github.com/tedmax100/o11y_lab_for_dummies/tree/main/k6/slides/transcripts)
