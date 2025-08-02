# VLM Fallback System - 開發任務清單

## 項目概述

**目標**：實現VLM fallback系統，當狀態追蹤系統信心值過低或無法匹配時，自動將查詢轉發給VLM進行直接回答。

**核心概念**：信心值過低 → VLM直接查詢 → 返回VLM回應給用戶

**時間線**：預計 1-2 週完成
**優先級**：高
**狀態**：✅ 完成

## 階段 1：核心功能實現 (Week 1)

### 1.1 基礎架構搭建

#### Task 1.1.1: 創建 VLM Fallback 模組結構
- **文件**: `src/vlm_fallback/`
- **子任務**:
  - [x] 創建 `__init__.py`
  - [x] 創建 `decision_engine.py`
  - [x] 創建 `vlm_client.py`
  - [x] 創建 `fallback_processor.py`
  - [x] 創建 `config.py`
- **估計時間**: 1 小時
- **依賴**: 無
- **狀態**: ✅ 完成

#### Task 1.1.2: 實現決策引擎 (DecisionEngine)
- **文件**: `src/vlm_fallback/decision_engine.py`
- **子任務**:
  - [x] 實現 `should_use_vlm_fallback()` 方法
  - [x] 實現信心值閾值檢查
  - [x] 實現狀態數據驗證
  - [x] 添加決策日誌記錄
- **估計時間**: 3 小時
- **依賴**: Task 1.1.1
- **狀態**: ✅ 完成

#### Task 1.1.3: 實現提示詞管理器 (PromptManager)
- **文件**: `src/vlm_fallback/prompt_manager.py`
- **子任務**:
  - [x] 實現 `save_current_prompt()` 方法
  - [x] 實現 `switch_to_fallback_prompt()` 方法
  - [x] 實現 `restore_original_prompt()` 方法（關鍵！）
  - [x] 實現 `execute_fallback_with_prompt_switch()` 完整流程
  - [x] 添加錯誤情況下的提示詞恢復保證
- **估計時間**: 5 小時
- **依賴**: Task 1.1.1
- **狀態**: ✅ 完成

#### Task 1.1.4: 實現 VLM 客戶端 (VLMClient)
- **文件**: `src/vlm_fallback/vlm_client.py`
- **子任務**:
  - [x] 實現 `send_query()` 方法
  - [x] 實現VLM響應處理
  - [x] 添加超時和重試機制
  - [x] 與PromptManager集成
- **估計時間**: 3 小時
- **依賴**: Task 1.1.3
- **狀態**: ✅ 完成

### 1.2 核心處理器實現

#### Task 1.2.1: 實現 Fallback 處理器
- **文件**: `src/vlm_fallback/fallback_processor.py`
- **子任務**:
  - [x] 實現 `VLMFallbackProcessor` 類
  - [x] 實現 `process_query_with_fallback()` 方法
  - [x] 實現 `_vlm_fallback_response()` 方法
  - [x] 集成決策引擎、提示詞管理器和VLM客戶端
  - [x] 實現響應格式化
  - [x] 確保提示詞恢復的錯誤處理
- **估計時間**: 4 小時
- **依賴**: Task 1.1.2, Task 1.1.3, Task 1.1.4
- **狀態**: ✅ 完成

#### Task 1.2.2: 實現配置管理
- **文件**: `src/vlm_fallback/config.py`
- **子任務**:
  - [x] 定義 `VLMFallbackConfig` 類
  - [x] 實現配置文件讀取
  - [x] 實現默認配置
  - [x] 添加配置驗證
- **估計時間**: 2 小時
- **依賴**: Task 1.1.1
- **狀態**: ✅ 完成

### 1.3 系統集成

#### Task 1.3.1: 修改 QueryProcessor
- **文件**: `src/state_tracker/query_processor.py`
- **子任務**:
  - [x] 添加 VLM Fallback 導入
  - [x] 修改 `process_instant_query()` 方法集成fallback
  - [x] **確保回應格式與template完全一致**
  - [x] **實現用戶無感知的響應模式偽裝**
  - [x] 保持向後兼容性
- **估計時間**: 4 小時
- **依賴**: Task 1.2.1
- **狀態**: ✅ 完成

#### Task 1.3.2: 修改後端 API
- **文件**: `src/backend/main.py`
- **子任務**:
  - [x] 修改 `/api/v1/state/query` 端點
  - [x] 集成 VLM Fallback 處理器
  - [x] **確保不暴露fallback模式標識**
  - [x] **統一回應格式，用戶無法區分來源**
  - [x] 更新錯誤處理
- **估計時間**: 3 小時
- **依賴**: Task 1.3.1
- **狀態**: ✅ 完成

## 階段 2：測試和優化 (Week 2)

### 2.1 單元測試

#### Task 2.1.1: 決策引擎測試
- **文件**: `tests/test_vlm_fallback_integration.py`
- **子任務**:
  - [x] 測試信心值閾值判斷
  - [x] 測試無狀態數據情況
  - [x] 測試查詢類型未知情況
  - [x] 測試邊界條件
- **估計時間**: 2 小時
- **依賴**: Task 1.1.2
- **狀態**: ✅ 完成

#### Task 2.1.2: 提示詞管理器測試
- **文件**: `tests/test_vlm_fallback_integration.py`
- **子任務**:
  - [x] 測試提示詞保存功能
  - [x] 測試提示詞切換功能
  - [x] 測試提示詞恢復功能（關鍵測試！）
  - [x] 測試錯誤情況下的提示詞恢復
  - [x] 測試完整的切換流程
- **估計時間**: 4 小時
- **依賴**: Task 1.1.3
- **狀態**: ✅ 完成

#### Task 2.1.3: VLM客戶端測試
- **文件**: `tests/test_vlm_fallback_integration.py`
- **子任務**:
  - [x] 測試VLM請求發送
  - [x] 測試響應處理
  - [x] 測試錯誤處理和重試
  - [x] 測試超時機制
- **估計時間**: 2 小時
- **依賴**: Task 1.1.4
- **狀態**: ✅ 完成

#### Task 2.1.4: Fallback處理器測試
- **文件**: `tests/test_vlm_fallback_e2e.py`
- **子任務**:
  - [x] 測試完整fallback流程（包含提示詞切換）
  - [x] 測試響應格式化
  - [x] 測試錯誤情況下的提示詞恢復
  - [x] 測試性能指標
  - [x] 測試提示詞狀態一致性
- **估計時間**: 3 小時
- **依賴**: Task 1.2.1
- **狀態**: ✅ 完成

### 2.2 集成測試

#### Task 2.2.1: 端到端測試
- **文件**: `tests/test_complete_system_e2e.py`
- **子任務**:
  - [x] 測試完整查詢流程（包含提示詞切換和恢復）
  - [x] 測試與現有系統集成
  - [x] 測試不同信心值場景
  - [x] 測試VLM狀態追蹤功能在fallback後是否正常
  - [x] 測試錯誤恢復和提示詞一致性
- **估計時間**: 5 小時
- **依賴**: Task 2.1.1, Task 2.1.2, Task 2.1.3, Task 2.1.4
- **狀態**: ✅ 完成

#### Task 2.2.2: 性能測試
- **文件**: `tests/test_full_system_automated.py`
- **子任務**:
  - [x] 測試決策時間
  - [x] 測試VLM響應時間
  - [x] 測試並發處理
  - [x] 測試資源使用
- **估計時間**: 2 小時
- **依賴**: Task 2.2.1
- **狀態**: ✅ 完成

### 2.3 配置和文檔

#### Task 2.3.1: 配置文件
- **文件**: `src/config/vlm_fallback_config.json`
- **子任務**:
  - [x] 創建默認配置文件
  - [x] 定義信心值閾值配置
  - [x] 定義VLM客戶端配置
  - [x] 添加配置說明
- **估計時間**: 1 小時
- **依賴**: Task 1.2.2
- **狀態**: ✅ 完成

#### Task 2.3.2: 前端顯示更新
- **文件**: `src/frontend/js/query.js`
- **子任務**:
  - [x] 添加響應模式顯示 - 無需修改（透明設計）
  - [x] 添加信心值顯示 - 無需修改（透明設計）
  - [x] 更新響應處理邏輯 - 無需修改（透明設計）
  - [x] 添加fallback指示器 - 無需修改（透明設計）
- **估計時間**: 2 小時
- **依賴**: Task 1.3.2
- **狀態**: ✅ 完成（透明設計，無需前端修改）

#### Task 2.3.3: 用戶文檔
- **文件**: `docs/vlm_fallback_user_guide.md`
- **子任務**:
  - [x] 編寫功能說明
  - [x] 添加使用示例
  - [x] 添加配置說明
  - [x] 添加故障排除指南
- **估計時間**: 2 小時
- **依賴**: Task 2.2.2
- **狀態**: ✅ 完成

## 風險和緩解措施

### 高風險項目

#### Risk 1: VLM 服務不可用
- **風險**: VLM 服務宕機，導致fallback功能完全失效
- **緩解**: 實現降級回應機制，VLM不可用時提供友好錯誤訊息

#### Risk 2: 響應時間過長
- **風險**: VLM推理時間過長，影響用戶體驗
- **緩解**: 設置合理超時時間，實現超時處理機制

#### Risk 3: 系統集成問題
- **風險**: 與現有系統集成時破壞原有功能
- **緩解**: 保持最小侵入性，充分測試向後兼容性

### 中風險項目

#### Risk 4: 信心值閾值設置不當
- **風險**: 閾值過高或過低導致fallback觸發不當
- **緩解**: 提供可配置的閾值，支持動態調整

#### Risk 5: VLM回應質量問題
- **風險**: VLM回應不相關或質量差
- **緩解**: 優化提示詞模板，添加回應質量檢查

## 驗收標準

### 功能驗收
- [x] 信心值過低時自動觸發VLM fallback
- [x] VLM請求和響應處理正確
- [x] 錯誤情況下降級處理有效
- [x] 不影響現有狀態追蹤功能
- [x] 向後兼容性保持

### 性能驗收
- [x] fallback決策時間 < 10ms
- [x] VLM響應時間 < 10秒
- [x] 系統整體性能不受影響
- [x] 並發處理正常
- [x] 錯誤率 < 5%

### 集成驗收
- [x] 與現有系統無縫集成
- [x] API接口保持兼容
- [x] 日誌記錄完整
- [x] 配置管理正常

### 用戶體驗驗收
- [x] 低信心值時提供有意義回應
- [x] 回應質量滿足用戶需求
- [x] **用戶完全無感知fallback的存在**
- [x] **前端始終顯示綠色"State Query"回應**
- [x] **無論template還是VLM fallback都是相同的UI樣式**
- [x] 錯誤處理友好且透明

## 里程碑

### Milestone 1: 核心功能完成 (Week 1 結束)
- 決策引擎實現
- VLM客戶端實現
- Fallback處理器實現
- 基本系統集成完成

### Milestone 2: 完整系統完成 (Week 2 結束)
- 完整測試通過
- 前端顯示更新
- 配置和文檔完成
- 生產部署準備就緒

## 實現優先級

### 高優先級 (必須完成)
- 決策引擎實現
- VLM客戶端實現
- 基本系統集成
- 核心功能測試

### 中優先級 (重要)
- 錯誤處理優化
- 性能測試
- 配置管理
- 前端顯示更新

### 低優先級 (可選)
- 高級配置選項
- 詳細用戶文檔
- 性能優化
- 監控指標

## 影響檔案清單

### 🆕 新增檔案
```
src/vlm_fallback/
├── __init__.py                    # 模組初始化
├── decision_engine.py             # 決策引擎
├── prompt_manager.py              # 提示詞管理器
├── vlm_client.py                  # VLM客戶端
├── fallback_processor.py          # 核心處理器
└── config.py                      # 配置管理

src/config/
└── vlm_fallback_config.json       # 配置文件

tests/vlm_fallback/
├── test_decision_engine.py        # 決策引擎測試
├── test_prompt_manager.py         # 提示詞管理器測試
├── test_vlm_client.py             # VLM客戶端測試
├── test_fallback_processor.py     # 處理器測試
├── test_integration.py            # 集成測試
└── test_performance.py            # 性能測試

docs/
└── vlm_fallback_user_guide.md     # 用戶文檔
```

### 🔄 修改檔案
```
src/state_tracker/
├── query_processor.py             # 集成fallback邏輯
└── state_tracker.py               # 添加fallback支持

src/backend/
└── main.py                        # 修改查詢API端點

src/frontend/
├── index.html                     # 確保UI一致性（已確認無需修改）
└── js/query.js                    # 可能需要微調（可選）
```

### 📋 配置檔案
```
src/config/
├── app_config.json                # 可能需要添加fallback配置
└── models_config.json             # 可能需要VLM配置調整
```

### 🧪 測試相關
```
tests/
├── test_backend_api.py            # 可能需要更新API測試
└── integration/                   # 可能需要更新集成測試
```

## 關鍵用戶體驗要求

### 🎯 核心原則
1. **完全透明**：用戶絕對無法感知fallback的存在
2. **統一顯示**：所有回應都顯示為綠色"State Query"
3. **一致格式**：template和VLM fallback回應格式完全相同
4. **無標識暴露**：不暴露任何fallback相關的標識

### 🔍 前端確認要點
- ✅ **顏色**：綠色 (`query-response` 類別)
- ✅ **圖標**：`fas fa-chart-line`
- ✅ **標題**：始終顯示 "State Query"
- ✅ **樣式**：`linear-gradient(135deg, #d1fae5, #ecfdf5)`
- ✅ **邊框**：`3px solid #10b981`

## 技術債務

### 需要注意的技術債務
- 確保不破壞現有的雙循環記憶系統
- 保持與現有日誌系統的兼容性
- 維護API接口的向後兼容性
- 確保配置管理的一致性
- **確保VLM提示詞恢復機制的可靠性**
- **維護用戶體驗的完全透明性** 