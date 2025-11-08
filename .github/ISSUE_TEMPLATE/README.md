# Issue Templates 說明

本專案提供以下 Issue Templates：

## 📝 可用的 Templates

### 1. Codelabs 回饋
**檔案**: `codelabs-feedback.md`
**用途**: 報告 Codelabs 教學中的錯誤或提供建議
**Labels**: `codelabs`, `documentation`
**直接連結**: [建立 Codelabs 回饋](https://github.com/tedmax100/o11y_lab_for_dummies/issues/new?template=codelabs-feedback.md&labels=codelabs,documentation)

### 2. Bug 報告
**檔案**: `bug_report.md`
**用途**: 報告專案中的錯誤或問題
**Labels**: `bug`
**直接連結**: [報告 Bug](https://github.com/tedmax100/o11y_lab_for_dummies/issues/new?template=bug_report.md&labels=bug)

### 3. 功能建議
**檔案**: `feature_request.md`
**用途**: 建議新功能或改進
**Labels**: `enhancement`
**直接連結**: [提出功能建議](https://github.com/tedmax100/o11y_lab_for_dummies/issues/new?template=feature_request.md&labels=enhancement)

## 🔗 URL 參數說明

GitHub 支援透過 URL 參數來預填 Issue：

### 基本語法
```
https://github.com/USER/REPO/issues/new?parameter1=value1&parameter2=value2
```

### 可用參數

| 參數 | 說明 | 範例 |
|------|------|------|
| `template` | 指定 template 檔案名稱 | `template=codelabs-feedback.md` |
| `labels` | 設定 labels（逗號分隔） | `labels=bug,urgent` |
| `title` | 預設標題 | `title=[Bug]%20Something%20broken` |
| `body` | 預設內容 | `body=Please%20describe...` |
| `assignees` | 指定負責人（逗號分隔） | `assignees=username1,username2` |
| `milestone` | 指定 milestone | `milestone=1` |

### 範例 URLs

#### 1. 使用 Template + Labels
```
https://github.com/tedmax100/o11y_lab_for_dummies/issues/new?template=codelabs-feedback.md&labels=codelabs,documentation
```

#### 2. 自訂標題 + Labels
```
https://github.com/tedmax100/o11y_lab_for_dummies/issues/new?labels=bug,urgent&title=[Bug]%20Critical%20Error
```

#### 3. 完整範例
```
https://github.com/tedmax100/o11y_lab_for_dummies/issues/new?template=bug_report.md&labels=bug,urgent&title=[Bug]%20Docker%20compose%20failed&assignees=tedmax100
```

## 📌 注意事項

1. **URL Encoding**:
   - 空格使用 `%20`
   - 中文需要 URL encode

2. **Labels**:
   - 必須是 repo 中已存在的 label
   - 多個 labels 用逗號分隔，不要有空格
   - 範例：`labels=bug,urgent` ✅
   - 錯誤：`labels=bug, urgent` ❌

3. **Template 檔案名稱**:
   - 必須包含 `.md` 副檔名
   - 大小寫敏感
   - 必須存在於 `.github/ISSUE_TEMPLATE/` 目錄

## 🎯 在 Codelabs 中使用

在 Codelabs Markdown 的 metadata 中設定：

```markdown
---
feedback link: https://github.com/tedmax100/o11y_lab_for_dummies/issues/new?template=codelabs-feedback.md&labels=codelabs,documentation
---
```

這樣使用者點擊 "Report a mistake" 時，就會：
1. 自動開啟建立 Issue 頁面
2. 套用 `codelabs-feedback.md` template
3. 自動加上 `codelabs` 和 `documentation` labels

## 🔧 自訂 Template

要建立新的 template：

1. 在 `.github/ISSUE_TEMPLATE/` 建立 `.md` 檔案
2. 使用 YAML front matter 定義 template metadata：

```markdown
---
name: Template 名稱
about: Template 描述
title: '[Prefix] '
labels: 'label1, label2'
assignees: ''
---

## 標題
內容...
```

3. 使用新的 URL：
```
https://github.com/USER/REPO/issues/new?template=你的檔案.md
```

## 📚 參考資料

- [GitHub Issue Templates 官方文件](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository)
- [URL 參數說明](https://docs.github.com/en/issues/tracking-your-work-with-issues/creating-an-issue#creating-an-issue-from-a-url-query)
