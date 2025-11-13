# 🔍 SEO 設定指南

本文件說明此專案的 SEO（搜尋引擎最佳化）設定。

## ✅ 已完成的 SEO 設定

### 1. HTML Meta Tags

**位置**: `codelabs/generated/index.html`

#### Primary Meta Tags
```html
<title>OpenTelemetry 可觀測性實驗室 - 互動式實作教學</title>
<meta name="title" content="...">
<meta name="description" content="...">
<meta name="keywords" content="OpenTelemetry, 可觀測性, ...">
<meta name="author" content="tedmax100">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://tedmax100.github.io/o11y_lab_for_dummies/">
```

#### Open Graph Tags (Facebook, LinkedIn)
```html
<meta property="og:type" content="website">
<meta property="og:url" content="...">
<meta property="og:title" content="...">
<meta property="og:description" content="...">
<meta property="og:image" content="...">
<meta property="og:locale" content="zh_TW">
```

#### Twitter Card Tags
```html
<meta property="twitter:card" content="summary_large_image">
<meta property="twitter:title" content="...">
<meta property="twitter:description" content="...">
<meta property="twitter:image" content="...">
```

### 2. Structured Data (JSON-LD)

**位置**: `codelabs/generated/index.html` (底部)

#### Course Schema
```json
{
  "@context": "https://schema.org",
  "@type": "Course",
  "name": "OpenTelemetry 可觀測性實驗室",
  "educationalLevel": "Intermediate",
  "courseWorkload": "PT2H"
}
```

#### WebSite Schema
```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "OpenTelemetry 可觀測性實驗室"
}
```

### 3. robots.txt

**位置**: `codelabs/generated/robots.txt`

```
User-agent: *
Allow: /
Sitemap: https://tedmax100.github.io/o11y_lab_for_dummies/sitemap.xml
```

### 4. sitemap.xml

**位置**: `codelabs/generated/sitemap.xml`

包含主要頁面：
- 首頁 (priority: 1.0)
- 教學頁面 (priority: 0.9)
- GitHub Repository (priority: 0.8)

### 5. Semantic HTML

- ✅ 正確使用 `<header>`, `<footer>`, `<h1>-<h6>`
- ✅ `lang="zh-TW"` 屬性設定
- ✅ 語意化的 class 命名

---

## 📋 待完成的 SEO 任務

### 1. 建立 OG Image (Open Graph Image)

**需要建立**: `codelabs/generated/og-image.png`

**建議規格**:
- **尺寸**: 1200x630 px (Facebook/LinkedIn 標準)
- **格式**: PNG 或 JPG
- **檔案大小**: < 1MB
- **內容建議**:
  - 專案標題：OpenTelemetry 可觀測性實驗室
  - 關鍵視覺元素：OpenTelemetry logo、Grafana、Prometheus 等
  - 背景：漸層色 (#667eea to #764ba2)

**建立方式**:

#### 選項 1: 使用 Canva
1. 訪問 [Canva](https://www.canva.com/)
2. 選擇「自訂尺寸」→ 1200 x 630 px
3. 設計包含：
   - 標題文字
   - Logo/圖示
   - 背景色彩
4. 下載為 PNG

#### 選項 2: 使用 Figma
1. 建立 1200x630 畫布
2. 設計視覺元素
3. Export 為 PNG

#### 選項 3: 使用 HTML/CSS 生成
```bash
# 可以用 puppeteer 或 playwright 截圖
npm install puppeteer
node generate-og-image.js
```

### 2. 建立 Favicon

**需要建立**:
- `favicon-32x32.png`
- `favicon-16x16.png`
- `apple-touch-icon.png` (180x180)

**工具推薦**:
- [Favicon Generator](https://realfavicongenerator.net/)
- [Favicon.io](https://favicon.io/)

**步驟**:
1. 準備一個正方形 Logo (至少 512x512 px)
2. 上傳到 Favicon Generator
3. 下載生成的所有尺寸
4. 放到 `codelabs/generated/` 目錄

### 3. 提交 Sitemap 到搜尋引擎

#### Google Search Console
1. 訪問 [Google Search Console](https://search.google.com/search-console)
2. 驗證網站所有權
3. 提交 sitemap: `https://tedmax100.github.io/o11y_lab_for_dummies/sitemap.xml`

#### Bing Webmaster Tools
1. 訪問 [Bing Webmaster](https://www.bing.com/webmasters)
2. 驗證網站
3. 提交 sitemap

### 4. Google Analytics (選用)

如果要追蹤流量，可以設定 Google Analytics：

1. **建立 GA4 Property**:
   - 訪問 [Google Analytics](https://analytics.google.com/)
   - 建立新的 Property
   - 取得 Measurement ID (格式: G-XXXXXXXXXX)

2. **在 HTML 中加入追蹤碼**:

在 `index.html` 的 `<head>` 中加入：

```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

3. **在 Codelabs metadata 中更新**:

```markdown
analytics account: G-XXXXXXXXXX
```

### 5. 更新 sitemap.xml

**目前需要手動更新**。當有新頁面時：

1. 編輯 `codelabs/generated/sitemap.xml`
2. 加入新的 `<url>` 區塊
3. 更新 `<lastmod>` 日期

**建議**: 建立自動化腳本

```bash
# 可以建立一個腳本來自動生成 sitemap
# 例如: scripts/generate-sitemap.sh
```

### 6. 性能最佳化

#### 圖片最佳化
```bash
# 壓縮 PNG
optipng -o7 og-image.png

# 或使用 ImageMagick
convert og-image.png -quality 85 -strip og-image-optimized.png
```

#### 啟用 Cache
在 GitHub Pages 無法直接設定，但可以：
- 使用 CDN (如 Cloudflare)
- 最小化 CSS/JS

#### Lazy Loading
對於未來的圖片，可以加入：
```html
<img src="image.png" loading="lazy" alt="描述">
```

---

## 🧪 SEO 測試工具

### 1. Google 工具

- **[PageSpeed Insights](https://pagespeed.web.dev/)**
  - 測試網站速度
  - 目標：行動裝置 > 90 分

- **[Mobile-Friendly Test](https://search.google.com/test/mobile-friendly)**
  - 測試行動裝置友善度

- **[Rich Results Test](https://search.google.com/test/rich-results)**
  - 測試 Structured Data 是否正確

### 2. 社群媒體預覽測試

- **[Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/)**
  - 測試 Open Graph tags
  - 清除 Facebook 快取

- **[Twitter Card Validator](https://cards-dev.twitter.com/validator)**
  - 測試 Twitter Cards

- **[LinkedIn Post Inspector](https://www.linkedin.com/post-inspector/)**
  - 測試 LinkedIn 預覽

### 3. 其他工具

- **[Schema.org Validator](https://validator.schema.org/)**
  - 驗證 JSON-LD structured data

- **[XML Sitemap Validator](https://www.xml-sitemaps.com/validate-xml-sitemap.html)**
  - 驗證 sitemap.xml

---

## 📊 監控 SEO 表現

### 定期檢查項目

1. **搜尋排名**:
   - 關鍵字: "OpenTelemetry 教學"
   - 關鍵字: "可觀測性 實驗室"
   - 使用 Google Search Console 追蹤

2. **流量來源**:
   - Google Analytics
   - GitHub Insights

3. **連結品質**:
   - 檢查 backlinks
   - 使用 Google Search Console

---

## ✅ SEO Checklist

部署前檢查清單：

- [x] Meta description (< 160 字元)
- [x] Meta keywords
- [x] Open Graph tags
- [x] Twitter Card tags
- [x] Canonical URL
- [x] robots.txt
- [x] sitemap.xml
- [x] Structured Data (JSON-LD)
- [x] Semantic HTML
- [x] 語言設定 (lang="zh-TW")
- [ ] OG Image (1200x630)
- [ ] Favicon (多尺寸)
- [ ] Google Search Console 驗證
- [ ] Sitemap 提交
- [ ] Google Analytics (選用)
- [ ] 行動裝置測試通過
- [ ] PageSpeed > 90 分

---

## 🔗 參考資源

- [Google SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
- [Schema.org Documentation](https://schema.org/docs/documents.html)
- [Open Graph Protocol](https://ogp.me/)
- [Twitter Cards Documentation](https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/abouts-cards)
- [Sitemap Protocol](https://www.sitemaps.org/protocol.html)

---

## 📝 維護建議

1. **定期更新** (每月):
   - 檢查斷連結
   - 更新 sitemap 的 lastmod 日期
   - 檢查 Google Search Console 錯誤

2. **內容更新**:
   - 新增教學時更新 sitemap
   - 更新 meta description 保持相關性

3. **效能監控**:
   - PageSpeed Insights 分數
   - Core Web Vitals
   - 載入時間

祝 SEO 優化順利！🚀
