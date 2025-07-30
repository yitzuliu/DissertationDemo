# AI 手動助手日誌系統設計規格

## 概述
本文件定義了 AI 手動助手系統的統一日誌和數據追蹤標準。確保所有關鍵的系統、視覺和使用者互動都以結構化、一致且可追蹤的方式記錄。此設計支援除錯、監控、分析和未來開發。

---

## 1. 日誌分類與檔案

- **系統技術日誌**: `logs/system_technical_YYYYMMDD.log`
- **視覺觀察日誌**: `logs/visual_YYYYMMDD.log`
- **使用者查詢日誌**: `logs/user_YYYYMMDD.log`
- **統一流程追蹤日誌**: `logs/flow_tracking_YYYYMMDD.log`

每個日誌檔案按日輪換，使用一致的時間戳格式。

---

## 2. 事件驅動唯一ID與可追蹤性

- **observation_id**: 每次 VLM（視覺）觀察事件的唯一標識（由後端在每次圖像捕獲/分析週期生成）。
- **state_update_id**: 每次狀態更新事件的唯一標識（由 state_tracker 在狀態變更時生成）。
- **query_id**: 每次使用者查詢事件的唯一標識（由後端或 state_tracker 在每次使用者查詢時生成）。
- **request_id**: 每次 API 請求的唯一標識（由後端為每次 HTTP/API 呼叫生成）。
- **flow_id**: 用於分組相關事件（例如，使用者查詢和基於的觀察）。

**可追蹤性原則:**
- 每個事件日誌包含自己的唯一ID。
- 日誌引用相關ID（例如，使用者查詢日誌包含基於的 observation_id）。
- 這使得異步、事件驅動的流程具有完全可追蹤性。

---

## 3. 日誌類型、欄位和範例格式

### 3.1 系統技術日誌
**目的:** 記錄所有系統級事件、資源使用、端點互動和連線狀態。  
**負責模組:** backend (main.py), infrastructure/ops scripts

**關鍵事件:**
- 系統啟動/關閉
- 配置載入
- 記憶體/CPU 使用
- 端點/API 呼叫
- 連線狀態（前端、模型伺服器、資料庫）
- 錯誤處理和恢復

**範例:**
```
2025-07-30 09:00:00,000 [SYSTEM_START] system_id=sys_001, host=localhost, port=8000, model=smolvlm
2025-07-30 09:00:00,010 [MEMORY] system_id=sys_001, startup_memory=22.1MB
2025-07-30 09:01:12,345 [ENDPOINT] request_id=req_1753873272345, method=POST, path=/v1/chat/completions, status=200, duration=2.31s
2025-07-30 09:30:00,000 [SYSTEM_SHUTDOWN] system_id=sys_001, final_memory=22.5MB, uptime=30min
```

---

### 3.2 視覺觀察日誌
**目的:** 追蹤所有視覺數據流，包括圖像捕獲、提示詞使用、後端傳輸、RAG 匹配和狀態追蹤。  
**負責模組:** frontend (圖像捕獲, 提示詞), backend (main.py, 圖像處理), rag, state_tracker

**關鍵事件:**
- 圖像捕獲（時間戳、設備、解析度、品質、格式、大小）
- 使用的視覺提示詞（內容、長度、類型）
- 發送到後端的數據（問題、圖像元數據、token 數量）
- 後端接收（完整訊息結構）
- RAG 匹配過程（VLM 觀察、候選步驟、相似度分數）
- RAG 匹配結果（選定步驟、標題、相似度）
- 狀態追蹤器決策（信心度、動作、更新狀態）
- 所有事件應包含 observation_id 和 request_id 以實現可追蹤性

**範例:**
```
2025-07-30 09:01:10,000 [EYES_CAPTURE] observation_id=obs_123, request_id=req_1753873272345, device=MacBook FaceTime HD, resolution=1920x1080, quality=0.9, format=JPEG, size=1.2MB
2025-07-30 09:01:10,001 [EYES_PROMPT] observation_id=obs_123, prompt="描述製作咖啡的步驟...", length=48 chars
2025-07-30 09:01:10,002 [EYES_TRANSFER] observation_id=obs_123, sent_to_backend={question: "如何製作咖啡?", image: [base64], tokens: 100}
2025-07-30 09:01:10,200 [RAG_MATCHING] observation_id=obs_123, vlm_observation="桌上有咖啡濾紙和滴濾器。", candidate_steps=[step1, step2, step3, step4], similarities=[0.82, 0.65, 0.12, 0.05]
2025-07-30 09:01:10,230 [RAG_RESULT] observation_id=obs_123, selected=step2, title="沖洗濾紙", similarity=0.82
2025-07-30 09:01:10,240 [STATE_TRACKER] observation_id=obs_123, state_update_id=state_456, confidence=0.82, action=UPDATE, state={task:brewing_coffee, step:2}
```

---

### 3.3 使用者查詢日誌
**目的:** 記錄所有使用者查詢、分類、處理和回應，以實現可追蹤性和分析。  
**負責模組:** frontend (使用者輸入), backend (main.py), state_tracker

**關鍵事件:**
- 接收使用者查詢（query_id, request_id, 內容, 語言）
- 查詢分類（類型, 信心度）
- 查詢處理（當前狀態, 步驟, 任務）
- 查詢回應（內容, 處理時間）
- 所有事件應包含 query_id, request_id 和用於回應的 observation_id

**範例:**
```
2025-07-30 09:01:15,000 [USER_QUERY] query_id=query_789, request_id=req_1753873275000, question="我需要什麼工具?", language=zh, used_observation_id=obs_123
2025-07-30 09:01:15,001 [QUERY_CLASSIFY] query_id=query_789, type=required_tools, confidence=0.95
2025-07-30 09:01:15,002 [QUERY_PROCESS] query_id=query_789, state={task:brewing_coffee, step:2}
2025-07-30 09:01:15,003 [QUERY_RESPONSE] query_id=query_789, response="您需要: 濾紙、滴濾器、熱水、杯子。", duration=1.2ms
```

---

### 3.4 統一流程追蹤日誌
**目的:** 為每個使用者/系統流程提供端到端可追蹤性，通過唯一的 flow_id 連結所有相關事件。  
**負責模組:** backend (main.py), orchestrator, ops/monitoring

**關鍵事件:**
- 流程開始（flow_id, 類型, 開始時間）
- 每個主要步驟（步驟名稱, 時間戳, 相關ID）
- 流程結束（狀態, 總持續時間, 結果）

**範例:**
```
2025-07-30 09:01:10,000 [FLOW_START] flow_id=flow_1753873272345, type=EYES_OBSERVATION, started
2025-07-30 09:01:10,250 [FLOW_STEP] flow_id=flow_1753873272345, step=image_capture, observation_id=obs_123
2025-07-30 09:01:10,300 [FLOW_STEP] flow_id=flow_1753873272345, step=backend_transfer, request_id=req_1753873272345
2025-07-30 09:01:10,400 [FLOW_STEP] flow_id=flow_1753873272345, step=rag_matching, observation_id=obs_123
2025-07-30 09:01:10,500 [FLOW_STEP] flow_id=flow_1753873272345, step=state_update, state_update_id=state_456
2025-07-30 09:01:15,003 [FLOW_STEP] flow_id=flow_1753873272345, step=user_query, query_id=query_789
2025-07-30 09:01:15,004 [FLOW_END] flow_id=flow_1753873272345, status=SUCCESS, total_duration=5.0s
```

---

## 4. 日誌管理、輪換和儲存

- **目錄結構:**
  - `logs/system_YYYYMMDD.log`      # 系統日誌
  - `logs/visual_YYYYMMDD.log`      # 視覺日誌
  - `logs/user_YYYYMMDD.log`        # 使用者日誌
  - `logs/flow_tracking_YYYYMMDD.log` # 流程日誌
  - `logs/archive/`                 # 按月歸檔的日誌
- **輪換:**
  - 每日日誌輪換
  - 7天後壓縮日誌
  - 保留30天，然後按月歸檔
- **效能/儲存:**
  - 預估: 系統 (10-20MB/天), 視覺 (50-100MB/天), 使用者 (5-10MB/天)
  - 總計: 典型 65-130MB/天

---

## 5. 查詢和分析

- **基於時間戳的關聯:**
  - 使用時間戳和唯一ID將使用者查詢與最近的觀察/狀態更新關聯。
- **範例分析命令:**
```bash
# 在特定時間查找使用者查詢
grep "09:01:15" logs/user_20250730.log
# 查找該時間之前最近的狀態更新
grep -B5 -A5 "09:01:10" logs/visual_20250730.log
```
- **錯誤/效能診斷:**
```bash
# 檢查失敗的 VLM 處理
grep "action=FAIL" logs/visual_20250730.log
# 檢查失敗的使用者查詢分類
grep "confidence<0.5" logs/user_20250730.log
# 檢查系統記憶體使用
grep "MEMORY" logs/system_20250730.log
```

---

## 6. 實作階段與模組責任

### 第一階段: 核心 LogManager 與系統日誌 (第1週)
- 實作 LogManager 類別 (backend)
- 系統啟動/關閉、端點和錯誤日誌
- 每日輪換和歸檔

### 第二階段: 視覺流程日誌 (第2週)
- 前端: 圖像捕獲、提示詞和傳輸日誌
- 後端: 圖像接收、VLM 處理、RAG 匹配日誌
- 狀態追蹤器: 狀態更新日誌

### 第三階段: 使用者查詢日誌 (第3週)
- 前端: 使用者輸入日誌
- 後端: 查詢接收、分類、回應日誌
- 狀態追蹤器: 查詢處理日誌

### 第四階段: 統一流程追蹤與分析工具 (第4週)
- 在所有日誌中實作 flow_id 關聯
- 開發日誌分析腳本和儀表板
- 與監控/警報系統整合

---

## 7. 日誌事件到模組責任對應表

| 日誌事件類型         | 範例日誌標籤      | 負責模組         |
|-----------------------|---------------------|------------------------------|
| 系統啟動        | SYSTEM_START        | backend (main.py), ops       |
| 記憶體使用          | MEMORY              | backend, ops                 |
| 端點呼叫         | ENDPOINT            | backend (main.py)            |
| 圖像捕獲         | EYES_CAPTURE        | frontend                     |
| 視覺提示詞         | EYES_PROMPT         | frontend                     |
| 後端傳輸      | EYES_TRANSFER       | frontend, backend            |
| VLM 處理        | RAG_MATCHING        | backend, rag                 |
| RAG 匹配結果      | RAG_RESULT          | rag                          |
| 狀態更新          | STATE_TRACKER       | state_tracker                |
| 使用者查詢            | USER_QUERY          | frontend, backend            |
| 查詢分類  | QUERY_CLASSIFY      | backend, state_tracker       |
| 查詢處理      | QUERY_PROCESS       | state_tracker                |
| 查詢回應        | QUERY_RESPONSE      | backend, state_tracker       |
| 流程開始/步驟/結束   | FLOW_START/STEP/END | backend, orchestrator, ops   |

---

## 8. 日誌最佳實踐

- 始終包含唯一ID（observation_id, query_id, request_id, state_update_id, flow_id）以實現可追蹤性。
- 使用一致的時間戳格式: `YYYY-MM-DD HH:MM:SS,mmm`
- 記錄所有關鍵數據欄位（內容、類型、信心度、狀態等）
- 按類別分離日誌以便於分析和監控。
- 避免記錄敏感數據（例如，原始圖像 base64）除非除錯需要。
- 每日輪換日誌並按需歸檔。
- 日誌結構和欄位名稱應在所有模組中保持一致。
- 日誌記錄器應按模組初始化，並具有適當的檔案處理器。
- 未來擴展（例如，指標、警報）應遵循相同的結構。

---

## 9. 變更歷史
- 2025-07-30: 為工程和運營起草初始統一版本。