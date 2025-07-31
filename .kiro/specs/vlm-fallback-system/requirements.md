# VLM Fallback System - 功能需求規格

## 1. 功能概述

### 1.1 目標
當狀態追蹤系統無法有效處理用戶查詢時，自動切換到 VLM 直接回答模式，提供智能、靈活的用戶交互體驗。

### 1.2 核心價值
- **提升用戶體驗**：避免 "No active state" 的無用回應
- **增強系統靈活性**：支援各種類型的用戶查詢
- **保持系統穩定性**：不影響現有的狀態追蹤功能

## 2. 功能需求

### 2.1 智能觸發機制

#### 2.1.1 觸發條件
- **置信度過低**：當前狀態置信度 < 0.40
- **查詢類型未知**：QueryType.UNKNOWN
- **無有效狀態**：current_state 為空或 None
- **查詢與任務無關**：無法匹配到預定義的查詢模式

#### 2.1.2 觸發邏輯
```python
def should_use_vlm_direct(query: str, state_data: Optional[Dict]) -> bool:
    # 條件 1：無有效狀態
    if not state_data:
        return True
    
    # 條件 2：置信度過低
    confidence = state_data.get('confidence', 0.0)
    if confidence < 0.40:
        return True
    
    # 條件 3：查詢類型未知
    query_type = classify_query(query)
    if query_type == QueryType.UNKNOWN:
        return True
    
    return False
```

### 2.2 動態模式切換

#### 2.2.1 模式類型
- **Template Mode**：使用預定義模板回答（現有功能）
- **VLM Direct Mode**：使用 VLM 直接回答（新功能）

#### 2.2.2 切換流程
1. 保存當前 VLM 提示詞
2. 切換到直接回答提示詞
3. 發送 VLM 請求
4. 恢復原始提示詞

### 2.3 提示詞管理

#### 2.3.1 狀態追蹤提示詞
```python
STATE_TRACKING_PROMPT = """
You are an AI Manual Assistant with state tracking capabilities...
[現有的狀態追蹤提示詞]
"""
```

#### 2.3.2 直接回答提示詞
```python
DIRECT_ANSWER_PROMPT = """
You are a helpful AI assistant. The user is asking: "{query}"

Please provide a direct, helpful answer to their question. Focus on being:
- Accurate and informative
- Helpful and supportive
- Clear and concise
- Relevant to their specific question
"""
```

### 2.4 錯誤處理

#### 2.4.1 異常情況
- VLM 服務不可用
- 提示詞切換失敗
- 網路連接問題
- 超時錯誤

#### 2.4.2 恢復機制
- 自動恢復原始提示詞
- 回退到基本模板回答
- 記錄錯誤日誌
- 通知用戶系統狀態

## 3. 非功能需求

### 3.1 性能要求
- **響應時間**：VLM 直接回答 < 5 秒
- **並發處理**：支援多用戶同時查詢
- **資源使用**：不顯著增加系統負載

### 3.2 可靠性要求
- **可用性**：99.9% 的正常運行時間
- **數據一致性**：提示詞狀態的正確保存和恢復
- **故障恢復**：自動從錯誤狀態恢復

### 3.3 安全性要求
- **輸入驗證**：防止惡意查詢
- **權限控制**：確保只有授權用戶可以使用
- **日誌安全**：敏感信息不記錄到日誌

### 3.4 可維護性要求
- **模組化設計**：功能獨立，易於測試
- **配置管理**：可配置的觸發條件和提示詞
- **監控能力**：完整的性能和使用統計

## 4. 用戶體驗需求

### 4.1 響應質量
- **相關性**：回答與用戶問題高度相關
- **準確性**：提供準確、可靠的信息
- **完整性**：回答完整，不遺漏重要信息

### 4.2 交互體驗
- **無縫切換**：用戶感知不到模式切換
- **一致性**：回答風格保持一致
- **即時性**：快速響應用戶查詢

### 4.3 透明度
- **模式標識**：在回應中標識回答模式
- **狀態指示**：顯示系統當前狀態
- **錯誤提示**：友好的錯誤信息

## 5. 技術約束

### 5.1 系統兼容性
- 與現有的 Memory System 兼容
- 與現有的 Logging System 兼容
- 與現有的 Frontend System 兼容

### 5.2 技術限制
- 不修改現有的核心狀態追蹤邏輯
- 保持向後兼容性
- 遵循現有的代碼風格和架構

## 6. 驗收標準

### 6.1 功能驗收
- [ ] 智能觸發機制正常工作
- [ ] 動態模式切換無錯誤
- [ ] 提示詞管理正確
- [ ] 錯誤處理有效

### 6.2 性能驗收
- [ ] 響應時間符合要求
- [ ] 並發處理正常
- [ ] 資源使用合理

### 6.3 用戶體驗驗收
- [ ] 回答質量滿意
- [ ] 交互體驗流暢
- [ ] 錯誤處理友好 