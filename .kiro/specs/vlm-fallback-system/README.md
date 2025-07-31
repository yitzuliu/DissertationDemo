# VLM Fallback System

## 概述

VLM Fallback System 是一個智能查詢處理系統，當狀態追蹤系統的置信度過低或用戶查詢與當前任務流程不相關時，自動切換到 VLM 直接回答模式，提供更靈活和智能的用戶交互體驗。

## 核心概念

### 問題背景
- 當置信度 < 0.40 時，系統返回 "No active state"
- 用戶查詢與任務流程無關時，無法提供有用回應
- 系統缺乏靈活性，只能處理預定義的查詢類型

### 解決方案
- **智能回退機制**：自動判斷是否需要 VLM 直接回答
- **動態提示詞切換**：在狀態追蹤和直接回答間無縫切換
- **狀態保護**：確保原始狀態追蹤不受影響

## 功能特點

### 1. 智能觸發條件
- 置信度過低（< 0.40）
- 查詢類型為 UNKNOWN
- 無有效狀態數據

### 2. 動態模式切換
- **模板回答模式**：用於任務相關查詢
- **VLM 直接回答模式**：用於一般性問題

### 3. 完整狀態管理
- 提示詞保存和恢復
- 錯誤處理和回退
- 並發安全處理

## 系統架構

```
User Query → QueryProcessor → Decision Logic → Response Mode
                                    ↓
                            ┌─────────────┬─────────────┐
                            ↓             ↓             ↓
                    Template Mode   VLM Direct Mode   Error Fallback
                            ↓             ↓             ↓
                    State-based    Dynamic Prompt    Basic Response
                    Response       + VLM Call        + Recovery
```

## 文件結構

- `requirements.md` - 功能需求規格
- `design.md` - 系統設計文檔
- `implementation.md` - 實現計劃
- `tasks.md` - 開發任務清單
- `testing.md` - 測試計劃
- `discussion-record.md` - 討論記錄

## 相關系統

- **Memory System** - 狀態追蹤和 RAG 知識庫
- **Logging System** - 完整的日誌追蹤
- **Frontend System** - 用戶界面和交互

## 狀態

🟡 **規劃階段** - 功能設計和文檔準備中 