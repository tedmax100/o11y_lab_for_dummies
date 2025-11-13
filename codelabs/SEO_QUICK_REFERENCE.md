# 🚀 SEO 快速參考

## ✅ 已完成的設定

| 項目 | 狀態 | 位置 |
|------|------|------|
| Meta Tags | ✅ | `generated/index.html` |
| Open Graph | ✅ | `generated/index.html` |
| Twitter Card | ✅ | `generated/index.html` |
| Structured Data | ✅ | `generated/index.html` (底部) |
| robots.txt | ✅ | `generated/robots.txt` |
| sitemap.xml | ✅ | `generated/sitemap.xml` |
| Semantic HTML | ✅ | `generated/index.html` |

## 📋 待辦事項

### 🎨 1. 建立 OG Image（重要！）

```bash
# 方法 1: 使用 HTML 生成器
cd codelabs
open generate-og-image.html  # 在瀏覽器中開啟
# 然後截圖並儲存為 generated/og-image.png
```

**尺寸**: 1200 x 630 px
**位置**: `codelabs/generated/og-image.png`

### 🎯 2. 建立 Favicon

使用 [Favicon Generator](https://realfavicongenerator.net/):
1. 上傳 Logo
2. 下載所有尺寸
3. 放到 `codelabs/generated/`

需要的檔案:
- `favicon-32x32.png`
- `favicon-16x16.png`
- `apple-touch-icon.png`

### 📤 3. 提交 Sitemap

#### Google Search Console
```
URL: https://search.google.com/search-console
Sitemap: https://tedmax100.github.io/o11y_lab_for_dummies/sitemap.xml
```

#### Bing Webmaster
```
URL: https://www.bing.com/webmasters
Sitemap: https://tedmax100.github.io/o11y_lab_for_dummies/sitemap.xml
```

---

## 🛠️ 常用工具和指令

### 更新 Sitemap
```bash
cd codelabs
./generate-sitemap.sh
```

### 測試 SEO

**PageSpeed Insights**:
```
https://pagespeed.web.dev/?url=https://tedmax100.github.io/o11y_lab_for_dummies/
```

**Facebook Debugger**:
```
https://developers.facebook.com/tools/debug/
輸入: https://tedmax100.github.io/o11y_lab_for_dummies/
```

**Twitter Card Validator**:
```
https://cards-dev.twitter.com/validator
輸入: https://tedmax100.github.io/o11y_lab_for_dummies/
```

**Rich Results Test**:
```
https://search.google.com/test/rich-results
輸入: https://tedmax100.github.io/o11y_lab_for_dummies/
```

---

## 📊 關鍵 Meta Tags 總覽

### 核心 Tags
```html
<title>OpenTelemetry 可觀測性實驗室 - 互動式實作教學</title>
<meta name="description" content="完整的 OpenTelemetry 可觀測性實驗室...">
<meta name="keywords" content="OpenTelemetry, 可觀測性, Grafana...">
```

### Open Graph (社群媒體)
```html
<meta property="og:title" content="...">
<meta property="og:description" content="...">
<meta property="og:image" content="https://tedmax100.github.io/o11y_lab_for_dummies/og-image.png">
<meta property="og:url" content="https://tedmax100.github.io/o11y_lab_for_dummies/">
```

### Structured Data
```json
{
  "@context": "https://schema.org",
  "@type": "Course",
  "name": "OpenTelemetry 可觀測性實驗室",
  "educationalLevel": "Intermediate",
  "courseWorkload": "PT2H"
}
```

---

## 🎯 目標關鍵字

### 主要關鍵字
- OpenTelemetry 教學
- 可觀測性實驗室
- Grafana 教學
- 分散式追蹤
- OpenTelemetry 中文

### 長尾關鍵字
- OpenTelemetry Python 教學
- OpenTelemetry Go 手動埋點
- Grafana Loki Tempo 整合
- 可觀測性三大支柱
- OpenTelemetry 自動埋點

---

## 📈 效能目標

| 指標 | 目標 | 當前 |
|------|------|------|
| PageSpeed (Mobile) | > 90 | 待測試 |
| PageSpeed (Desktop) | > 95 | 待測試 |
| First Contentful Paint | < 1.8s | 待測試 |
| Time to Interactive | < 3.8s | 待測試 |
| Cumulative Layout Shift | < 0.1 | 待測試 |

---

## 🔍 檢查清單

部署前檢查:

- [x] Title tag (< 60 字元)
- [x] Meta description (< 160 字元)
- [x] Keywords
- [x] Open Graph tags
- [x] Twitter Card tags
- [x] Canonical URL
- [x] robots.txt
- [x] sitemap.xml
- [x] Structured Data
- [x] lang 屬性
- [ ] **OG Image** ⚠️ 需要建立
- [ ] **Favicon** ⚠️ 需要建立
- [ ] Google Search Console 驗證
- [ ] Sitemap 提交
- [ ] 行動裝置測試
- [ ] PageSpeed 測試

---

## 📞 需要協助？

查看完整文件: [SEO_GUIDE.md](./SEO_GUIDE.md)

---

最後更新: 2025-01-08
