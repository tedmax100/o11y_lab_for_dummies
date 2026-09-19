#!/bin/bash

# 自動生成 sitemap.xml
# 使用方式: ./generate-sitemap.sh

SITE_URL="https://tedmax100.github.io/o11y_lab_for_dummies"
OUTPUT_FILE="generated/sitemap.xml"
CURRENT_DATE=$(date +%Y-%m-%d)

echo "🔄 生成 sitemap.xml..."

cat > "$OUTPUT_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">

    <!-- Homepage -->
    <url>
        <loc>${SITE_URL}/</loc>
        <lastmod>${CURRENT_DATE}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>

    <!-- Main Tutorial -->
    <url>
        <loc>${SITE_URL}/o11y-lab-tutorial/</loc>
        <lastmod>${CURRENT_DATE}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.9</priority>
    </url>

    <!-- GitHub Repository -->
    <url>
        <loc>https://github.com/tedmax100/o11y_lab_for_dummies</loc>
        <lastmod>${CURRENT_DATE}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>

EOF

# 自動偵測 generated 目錄下的所有 HTML 檔案（排除 index.html）
echo "📂 掃描教學頁面..."

if [ -d "generated/o11y-lab-tutorial" ]; then
    find generated/o11y-lab-tutorial -name "index.html" -o -name "*.html" | while read -r file; do
        relative_path="${file#generated/}"
        url="${SITE_URL}/${relative_path}"

        echo "    <url>" >> "$OUTPUT_FILE"
        echo "        <loc>${url}</loc>" >> "$OUTPUT_FILE"
        echo "        <lastmod>${CURRENT_DATE}</lastmod>" >> "$OUTPUT_FILE"
        echo "        <changefreq>monthly</changefreq>" >> "$OUTPUT_FILE"
        echo "        <priority>0.7</priority>" >> "$OUTPUT_FILE"
        echo "    </url>" >> "$OUTPUT_FILE"
        echo ""  >> "$OUTPUT_FILE"
    done
fi

if [ -d "generated/k6-performance-testing" ]; then
    find generated/k6-performance-testing -name "index.html" -o -name "*.html" | while read -r file; do
        relative_path="${file#generated/}"
        url="${SITE_URL}/${relative_path}"

        echo "    <url>" >> "$OUTPUT_FILE"
        echo "        <loc>${url}</loc>" >> "$OUTPUT_FILE"
        echo "        <lastmod>${CURRENT_DATE}</lastmod>" >> "$OUTPUT_FILE"
        echo "        <changefreq>monthly</changefreq>" >> "$OUTPUT_FILE"
        echo "        <priority>0.9</priority>" >> "$OUTPUT_FILE"
        echo "    </url>" >> "$OUTPUT_FILE"
        echo ""  >> "$OUTPUT_FILE"
    done
fi

# 結束 XML
echo "</urlset>" >> "$OUTPUT_FILE"

echo "✅ Sitemap 已生成: $OUTPUT_FILE"
echo "📊 包含 URL 數量: $(grep -c "<loc>" "$OUTPUT_FILE")"

# 驗證 XML 格式（如果安裝了 xmllint）
if command -v xmllint &> /dev/null; then
    echo "🔍 驗證 XML 格式..."
    if xmllint --noout "$OUTPUT_FILE" 2>&1; then
        echo "✅ XML 格式正確"
    else
        echo "❌ XML 格式錯誤"
        exit 1
    fi
else
    echo "💡 提示: 安裝 xmllint 可自動驗證 XML 格式"
    echo "   Ubuntu/Debian: sudo apt install libxml2-utils"
    echo "   macOS: brew install libxml2"
fi

echo ""
echo "📤 下一步:"
echo "1. 檢查生成的 sitemap.xml"
echo "2. 提交到 Google Search Console"
echo "3. URL: https://search.google.com/search-console"
