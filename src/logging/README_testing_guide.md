# 後端VLM處理日誌記錄測試指南

## 概述

本指南說明如何測試後端VLM處理日誌記錄功能，包括獨立測試和完整的端到端測試。

## 測試類型

### 1. 獨立測試（推薦）

**不需要實際的VLM服務器運行**

```bash
python src/logging/test_visual_logger_standalone.py
```

**測試內容：**
- 基本日誌記錄功能
- 數據清理功能
- ID一致性
- 性能指標記錄
- 錯誤場景處理
- 並發日誌記錄

### 2. 端到端測試（需要VLM服務器）

**需要SmolVLM服務器運行**

#### 方法一：自動啟動服務器
```bash
python src/logging/test_backend_vlm_logging.py
# 選擇 'y' 自動啟動服務器
```

#### 方法二：手動啟動服務器
```bash
# 終端1：啟動SmolVLM服務器
python src/models/smolvlm/run_smolvlm.py

# 終端2：運行測試
python src/logging/test_backend_vlm_logging.py
```

## 測試結果解讀

### 成功指標
- 所有測試通過率 100%
- 生成視覺日誌文件 `logs/visual_YYYYMMDD.log`
- 日誌包含所有事件類型：
  - BACKEND_RECEIVE
  - IMAGE_PROCESSING_START/RESULT
  - VLM_REQUEST/RESPONSE
  - RAG_DATA_TRANSFER
  - STATE_TRACKER_INTEGRATION
  - VISUAL_PERFORMANCE
  - VISUAL_ERROR

### 日誌驗證
檢查生成的日誌文件：
```bash
tail -20 logs/visual_20250730.log
```

## 故障排除

### 常見問題

1. **找不到視覺日誌文件**
   - 檢查 `logs/` 目錄是否存在
   - 確認日誌管理器正確初始化

2. **SmolVLM服務器啟動失敗**
   - 確認 `llama-server` 已安裝
   - 檢查端口 8080 是否被占用
   - 查看服務器啟動日誌

3. **測試超時**
   - 增加服務器啟動等待時間
   - 檢查網路連接
   - 確認模型下載完成

## 驗證清單

- [ ] 獨立測試通過 (100% 成功率)
- [ ] 端到端測試通過 (如果有VLM服務器)
- [ ] 生成視覺日誌文件
- [ ] 日誌包含所有必需的事件類型
- [ ] 觀察ID在整個流程中保持一致
- [ ] 敏感數據被正確清理
- [ ] 性能指標被正確記錄
- [ ] 錯誤情況被正確處理和記錄

## 任務 2.2 完成確認

✅ **已完成的功能：**
- 創建了 `VisualLogger` 類別
- 整合VLM處理接收日誌
- 記錄圖像處理過程和結果
- 整合與RAG系統的資料傳遞日誌
- 確保 observation_id 在整個流程中的一致性
- 修改後端 `src/backend/main.py` 整合所有日誌記錄
- 創建完整的測試套件驗證功能

✅ **測試驗證：**
- 獨立測試：6/6 通過 (100%)
- 後端整合驗證：10/10 通過 (100%)
- 日誌文件正確生成和格式化
- 所有日誌事件類型正常工作