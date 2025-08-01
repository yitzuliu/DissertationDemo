# VLM Fallback System

## 概述

VLM Fallback System 是 AI Manual Assistant 的增強功能，當狀態追蹤系統的信心值過低或無法匹配到合適的步驟時，自動將用戶查詢轉發給VLM進行直接回答。

## 核心概念

```
用戶查詢 → 狀態追蹤 → 信心值檢查
                           ↓
                    信心值 < 0.40?
                           ↓
                    是 → VLM Fallback → VLM直接回答
                    否 → Template Response → 預定義回應
```

## 主要特性

- **智能觸發**：基於信心值自動決定是否使用VLM fallback
- **無縫集成**：與現有系統完全兼容，不破壞原有功能
- **錯誤恢復**：VLM不可用時提供友好的降級回應
- **透明顯示**：用戶可以了解回應來源（template vs VLM fallback）

## 觸發條件

1. **信心值過低**：當前狀態信心值 < 0.40
2. **無狀態數據**：state_data 為 None 或空
3. **查詢類型未知**：QueryType.UNKNOWN
4. **無匹配步驟**：無法找到對應的任務步驟

## 系統架構

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   VLM Service   │
│                 │    │                 │    │                 │
│ - Query Input   │───▶│ - Query Router  │───▶│ - Model Server  │
│ - Response UI   │    │ - State Tracker │    │ - Direct Query  │
│ - Status Display│◀───│ - VLM Fallback  │◀───│ - Response Gen  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 文件結構

```
.kiro/specs/vlm-fallback-system/
├── README.md           # 本文件
├── design.md          # 詳細系統設計
├── requirements.md    # 功能需求規格
├── tasks.md          # 開發任務清單
└── discussion-record.md # 討論記錄
```

## 快速開始

### 1. 查看需求
閱讀 [requirements.md](requirements.md) 了解詳細的功能需求。

### 2. 了解設計
查看 [design.md](design.md) 了解系統架構和技術實現。

### 3. 開發任務
參考 [tasks.md](tasks.md) 了解具體的開發任務和時間安排。

## 實現概要

### 核心組件

1. **DecisionEngine** - 決定是否使用VLM fallback
2. **VLMClient** - 處理與VLM服務的通信
3. **VLMFallbackProcessor** - 協調整個fallback流程
4. **VLMFallbackConfig** - 管理配置參數

### 集成點

- `src/state_tracker/query_processor.py` - 查詢處理器
- `src/backend/main.py` - 後端API端點
- `src/frontend/js/query.js` - 前端顯示

## 配置示例

```json
{
  "vlm_fallback": {
    "decision_engine": {
      "confidence_threshold": 0.40
    },
    "vlm_client": {
      "model_server_url": "http://localhost:8080",
      "timeout": 30,
      "max_retries": 2
    }
  }
}
```

## 使用示例

### 高信心值場景（使用Template）
```
用戶: "我在哪一步？"
系統: 信心值 0.85 → Template Response
回應: "您目前在咖啡沖泡任務的第3步：磨咖啡豆..."
```

### 低信心值場景（使用VLM Fallback）
```
用戶: "今天天氣怎麼樣？"
系統: 信心值 0.20 → VLM Fallback
回應: "我無法獲取實時天氣信息，建議您查看天氣應用或網站..."
```

## 開發狀態

- **設計階段**: ✅ 完成
- **需求分析**: ✅ 完成
- **任務規劃**: ✅ 完成
- **實現階段**: 🟡 待開始
- **測試階段**: ⏳ 待開始
- **部署階段**: ⏳ 待開始

## 貢獻指南

1. 閱讀所有設計文檔
2. 了解現有系統架構
3. 按照tasks.md中的任務順序開發
4. 確保向後兼容性
5. 編寫完整的測試用例

## 聯繫信息

如有問題或建議，請參考 [discussion-record.md](discussion-record.md) 或聯繫開發團隊。