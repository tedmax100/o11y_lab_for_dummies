# Grafana k6 影音課程全章節錄課逐字稿全集 (Course Lecture Transcripts)

本目錄包含全套 5 大章節、48 頁簡報的**廣播級口播逐字稿（Verbatim Lecture Scripts）**。專為錄製高品質線上影音教學課程打造，每一頁均提供**畫面焦點**、**時間標記**、**完整 spoken-word 逐字台詞**、**螢幕動作切換指引**與**實機 Live Demo 銜接點**。

---

## 📑 章節逐字稿導航與時間規劃

| 章節編號與主題 | 投影片頁數 | 預估錄製時長 | 專屬逐字稿檔案連結 | 實機 Live Demo 配套 |
| :--- | :---: | :---: | :--- | :--- |
| **Chapter 1**<br>Modern Performance Testing with k6 | 8 頁 | 12 ~ 15 分鐘 | [Ch1 逐字稿](file:///home/nathan/Project/o11y_lab_for_dummies/k6/slides/transcripts/Ch1_逐字稿_Modern_Performance_Testing_with_k6.md) | `k6/demos/ch1_lifecycle_and_checks.js` |
| **Chapter 2**<br>Scientific k6 Traffic Modeling | 10 頁 | 18 ~ 22 分鐘 | [Ch2 逐字稿](file:///home/nathan/Project/o11y_lab_for_dummies/k6/slides/transcripts/Ch2_逐字稿_Scientific_k6_Traffic_Modeling.md) | `k6/demos/ch2_closed_vs_open_model.js`<br>`k6/demos/ch2_shared_array.js` |
| **Chapter 3**<br>k6 Quality Gates | 10 頁 | 18 ~ 20 分鐘 | [Ch3 逐字稿](file:///home/nathan/Project/o11y_lab_for_dummies/k6/slides/transcripts/Ch3_逐字稿_k6_Quality_Gates.md) | `k6/demos/ch3_quality_gates_exit99.js` |
| **Chapter 4**<br>Precision k6 Hybrid Testing | 10 頁 | 18 ~ 22 分鐘 | [Ch4 逐字稿](file:///home/nathan/Project/o11y_lab_for_dummies/k6/slides/transcripts/Ch4_逐字稿_Precision_k6_Hybrid_Testing.md) | `k6/demos/ch4_browser_quickpizza.js`<br>`k6/demos/ch4_hybrid_99_to_1.js` |
| **Chapter 5**<br>k6 Observability and Modular Architecture | 10 頁 | 15 ~ 20 分鐘 | [Ch5 逐字稿](file:///home/nathan/Project/o11y_lab_for_dummies/k6/slides/transcripts/Ch5_逐字稿_k6_Observability_and_Modular_Architecture.md) | `k6/demos/ch5_dashboard_and_html_summary.js`<br>`k6/demos/ch5_prometheus_remote_write.sh`<br>`k6/demos/ch5_xk6_docker_build.sh` |

---

## 🎙️ 講師錄音錄影雙螢幕佈局推薦

1. **主螢幕 (Primary Display - 1920x1080)**：
   - 全螢幕播放 PPTX（使用 [`k6/slides/`](file:///home/nathan/Project/o11y_lab_for_dummies/k6/slides) 目錄下的 5 份最新簡報）。
   - 錄製軟體（OBS / Camtasia）擷取此螢幕。
2. **副螢幕 (Secondary Display - 提詞機)**：
   - 開啟本目錄下的對應章節逐字稿。
   - 字體調大至舒適大小，跟著逐字稿內的【動作指引】切換終端機或 VS Code。
3. **終端機分割視窗**：
   - 上半部：執行 k6 指令。
   - 下半部：即時觀察日誌、Exit Code 或 Grafana 畫面。
