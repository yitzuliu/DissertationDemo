# VLM Fallback System - 功能需求規格

## 1. 功能概述

### 1.1 目標
當狀態追蹤系統的信心值過低或無法匹配到合適的步驟時，自動將用戶查詢轉發給VLM進行直接回答，提供智能、靈活的用戶交互體驗。

### 1.2 核心價值
- **解決低信心值問題**：當信心值 < 0.40 時，提供有意義的回應
- **處理未知查詢**：支援系統無法識別的查詢類型
- **保持系統完整性**：不破壞現有的狀態追蹤和雙循環記憶功能
- **提升用戶滿意度**：避免無用的錯誤回應，提供實際幫助

## 2. 功能需求

### 2.1 VLM Fallback 觸發機制

#### 2.1.1 主要觸發條件
- **信心值過低**：當前狀態信心值 < 0.40
- **無狀態數據**：state_data 為 None 或空
- **查詢類型未知**：QueryType.UNKNOWN
- **無匹配步驟**：無法找到對應的任務步驟

#### 2.1.2 觸發邏輯實現
```python
def should_use_vlm_fallback(query: str, state_data: Optional[Dict]) -> bool:
    """
    決定是否使用VLM fallback的核心邏輯
    """
    # 條件 1：無狀態數據
    if not state_data:
        return True
    
    # 條件 2：信心值過低
    confidence = state_data.get('confidence', 0.0)
    if confidence < 0.40:
        return True
    
    # 條件 3：查詢類型未知
    query_type = state_data.get('query_type', 'UNKNOWN')
    if query_type == 'UNKNOWN':
        return True
    
    # 條件 4：無當前步驟
    if not state_data.get('current_step'):
        return True
    
    return False
```

### 2.2 響應模式

#### 2.2.1 模式類型
- **Template Mode**：使用預定義模板回答（現有功能，高信心值時使用）
- **VLM Fallback Mode**：直接向VLM發送查詢（新功能，低信心值時使用）

#### 2.2.2 VLM Fallback 流程
1. 檢測到需要使用fallback（信心值過低等）
2. **保存當前VLM的狀態追蹤提示詞**
3. **切換VLM到fallback提示詞**
4. 發送用戶查詢到VLM服務（http://localhost:8080）
5. 獲取VLM響應
6. **恢復原本的狀態追蹤提示詞**（關鍵步驟！）
7. 返回響應給用戶並記錄使用情況

**重要**：步驟6是關鍵，因為VLM是系統的"雙眼睛"，需要持續監控用戶操作狀態。

### 2.3 提示詞管理需求

#### 2.3.1 提示詞切換需求
```python
class PromptManager:
    async def save_current_prompt(self) -> bool:
        """
        保存當前VLM的狀態追蹤提示詞
        - 必須確保完整保存
        - 支援錯誤恢復
        """
        pass
    
    async def switch_to_fallback_prompt(self, query: str) -> bool:
        """
        切換到fallback專用提示詞
        - 格式化用戶查詢
        - 設置適當的回應風格
        """
        pass
    
    async def restore_original_prompt(self) -> bool:
        """
        恢復原本的狀態追蹤提示詞
        - 這是關鍵步驟！
        - 確保VLM繼續執行狀態監控功能
        - 必須在任何情況下都能成功恢復
        """
        pass
```

#### 2.3.2 提示詞模板需求
```python
# 需要保存和恢復的原始提示詞
ORIGINAL_STATE_TRACKING_PROMPT = """
[現有的完整狀態追蹤提示詞]
"""

# 臨時使用的fallback提示詞
FALLBACK_PROMPT_TEMPLATE = """
You are a helpful AI assistant. Please answer the user's question directly and helpfully.

User Question: {query}

Please provide a clear, accurate, and helpful response.
"""
```

### 2.4 錯誤處理

#### 2.4.1 異常情況
- VLM 服務不可用（連接失敗）
- VLM 請求超時
- VLM 響應格式錯誤
- 網路連接問題

#### 2.4.2 錯誤恢復策略
- **重試機制**：VLM請求失敗時自動重試（最多2次）
- **提示詞恢復保證**：無論任何錯誤情況，都必須恢復原始提示詞
- **降級回應**：VLM完全不可用時提供友好的錯誤訊息
- **狀態保護**：確保原有狀態追蹤功能不受影響
- **錯誤日誌**：記錄所有fallback相關錯誤

**關鍵要求**：即使在異常情況下，也必須確保VLM的狀態追蹤提示詞得到恢復，因為VLM需要繼續監控用戶操作。

## 3. 非功能需求

### 3.1 性能要求
- **響應時間**：VLM fallback 回應 < 10 秒（考慮VLM推理時間）
- **決策時間**：fallback決策 < 10ms
- **並發支持**：支援多用戶同時使用fallback功能
- **資源控制**：不影響現有系統性能

### 3.2 可靠性要求
- **高可用性**：VLM服務不可用時系統仍能正常運行
- **狀態一致性**：fallback不影響原有狀態追蹤功能
- **錯誤恢復**：VLM請求失敗時自動降級處理

### 3.3 兼容性要求
- **向後兼容**：不破壞現有API接口
- **系統集成**：與現有logging、state tracker無縫集成
- **配置靈活**：可以動態啟用/禁用fallback功能

### 3.4 可維護性要求
- **模組化設計**：fallback功能獨立模組，易於測試和維護
- **配置管理**：可配置信心值閾值、VLM參數等
- **監控支持**：提供fallback使用統計和性能指標
- **日誌記錄**：完整記錄fallback決策和執行過程

## 4. 用戶體驗需求

### 4.1 響應質量
- **相關性**：VLM回答與用戶問題高度相關
- **實用性**：提供實際有用的信息，避免無意義回應
- **準確性**：利用VLM的知識能力提供準確信息
- **友好性**：保持友好、支持性的回應語調

### 4.2 交互體驗
- **完全透明**：用戶完全無法感知是template還是VLM fallback
- **統一體驗**：所有回應都顯示為"State Query"回應
- **一致性**：fallback回應與template回應格式完全一致
- **及時性**：在合理時間內提供回應

### 4.3 用戶感知管理
- **無模式標識**：絕不顯示使用了VLM fallback
- **統一信心值**：即使使用fallback也顯示合理的信心值
- **一致的查詢類型**：根據查詢內容推測合理的查詢類型
- **錯誤處理透明**：VLM錯誤時回退到友好的state回應

## 5. 技術約束

### 5.1 系統兼容性
- 與現有的雙循環記憶系統完全兼容
- 與現有的VLM服務（port 8080）集成
- 與現有的後端API（port 8000）集成
- 與現有的日誌系統兼容

### 5.2 技術限制
- **最小侵入性**：不修改現有核心狀態追蹤邏輯
- **向後兼容**：保持現有API接口格式不變
- **架構一致性**：遵循現有的三層架構設計
- **代碼風格**：遵循現有的Python代碼規範

### 5.3 依賴約束
- 依賴現有的VLM服務正常運行
- 使用現有的配置管理系統
- 集成現有的錯誤處理機制

## 6. 驗收標準

### 6.1 功能驗收
- [ ] 信心值過低時自動觸發VLM fallback
- [ ] VLM請求和響應處理正確
- [ ] 錯誤情況下的降級處理有效
- [ ] 不影響現有狀態追蹤功能

### 6.2 性能驗收
- [ ] fallback決策時間 < 10ms
- [ ] VLM響應時間 < 10秒
- [ ] 系統整體性能不受影響
- [ ] 並發處理正常

### 6.3 集成驗收
- [ ] 與現有系統無縫集成
- [ ] API接口保持兼容
- [ ] 日誌記錄完整
- [ ] 配置管理正常

### 6.4 用戶體驗驗收
- [ ] 低信心值時提供有意義的回應
- [ ] 回應質量滿足用戶需求
- [ ] 用戶完全無法感知fallback的存在
- [ ] 所有回應都顯示為"State Query"類型
- [ ] 前端UI保持完全一致
- [ ] 錯誤處理友好且透明 