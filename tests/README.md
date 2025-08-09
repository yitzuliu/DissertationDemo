# AI Manual Assistant - 測試套件 (重新整理版)

## 🎯 **測試架構概述**

本測試套件按照系統架構和功能模組重新整理，提供清晰的測試分類和執行指南。

## 📁 **測試結構**

```
tests/
├── core/                              # 核心功能測試
├── memory_system/                     # 記憶系統測試
├── vlm_fallback/                      # VLM Fallback 測試
├── integration/                       # 整合測試
├── system/                           # 系統級測試
└── scenarios/                        # 場景測試
```

## 🧪 **測試分類詳解**

### **Core 核心功能測試**
專注於系統核心組件的單元測試和基礎功能驗證。

- **`test_backend_api.py`** - 後端 API 端點測試
- **`test_vector_optimization.py`** - 向量優化和預計算測試
- **`test_state_tracker.py`** - 狀態追蹤器測試
- **`test_query_processor.py`** - 查詢處理器測試

### **Memory System 記憶系統測試**
驗證記憶系統、任務知識管理和 RAG 功能。

- **`test_task_knowledge.py`** - 任務知識載入和驗證
- **`test_memory_consistency.py`** - 記憶一致性和信心指數測試
- **`test_rag_system.py`** - RAG 系統功能測試

### **VLM Fallback 測試**
測試 VLM 備用響應機制的各種觸發場景。

- **`test_fallback_triggers.py`** - Fallback 觸發條件測試
- **`test_fallback_integration.py`** - Fallback 系統整合測試
- **`test_image_processing.py`** - 圖片處理和視覺分析測試

### **Integration 整合測試**
驗證多個服務間的協調和整合功能。

- **`test_dual_loop_coordination.py`** - 雙循環協調測試
- **`test_cross_service.py`** - 跨服務功能測試
- **`test_end_to_end.py`** - 端到端工作流程測試

### **System 系統級測試**
測試系統啟動、日誌、性能等系統級功能。

- **`test_service_startup.py`** - 服務啟動和通信測試
- **`test_logging_system.py`** - 日誌系統測試
- **`test_performance.py`** - 性能基準測試

### **Scenarios 場景測試**
基於實際使用場景的綜合測試。

- **`test_coffee_brewing.py`** - 咖啡沖泡場景完整測試
- **`test_task_scenarios.py`** - 其他任務場景測試

## 🚀 **執行測試**

### **按類別執行**
```bash
# 核心功能測試
python -m pytest tests/core/ -v

# 記憶系統測試
python -m pytest tests/memory_system/ -v

# VLM Fallback 測試
python -m pytest tests/vlm_fallback/ -v

# 整合測試
python -m pytest tests/integration/ -v

# 系統級測試
python -m pytest tests/system/ -v

# 場景測試
python -m pytest tests/scenarios/ -v
```

### **執行特定測試**
```bash
# 後端 API 測試
python tests/core/test_backend_api.py

# 咖啡沖泡場景測試
python tests/scenarios/test_coffee_brewing.py

# 雙循環協調測試
python tests/integration/test_dual_loop_coordination.py
```

### **執行所有測試**
```bash
# 使用 pytest
python -m pytest tests/ -v

# 或使用自定義腳本
python tests/run_all_tests.py
```

## 📊 **測試覆蓋範圍**

### **功能覆蓋**
- ✅ VLM 視覺處理
- ✅ 後端 API 服務
- ✅ 狀態追蹤和管理
- ✅ 記憶系統和 RAG
- ✅ VLM Fallback 機制
- ✅ 跨服務協調
- ✅ 日誌和監控
- ✅ 端到端工作流程

### **測試類型**
- **單元測試** - 個別組件功能
- **整合測試** - 組件間協作
- **系統測試** - 完整系統功能
- **場景測試** - 實際使用情境
- **性能測試** - 響應時間和資源使用

## 🔧 **測試環境設置**

### **前置條件**
```bash
# 激活虛擬環境
source ai_vision_env/bin/activate

# 設置 Python 路徑
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# 安裝測試依賴
pip install pytest pytest-asyncio requests pillow
```

### **測試資料**
- 任務資料: `data/tasks/coffee_brewing.yaml`
- 測試圖片: `data/test_images/`
- 日誌檔案: `logs/`

## 📈 **性能基準**

### **響應時間目標**
- API 端點: < 100ms
- 狀態更新: < 50ms
- 跨服務通信: < 200ms
- VLM Fallback: < 5000ms

### **記憶體使用目標**
- 滑動視窗: < 1MB
- 向量快取: 高效預計算
- 服務記憶體: 穩定使用

## 🚨 **故障排除**

### **常見問題**
1. **導入錯誤**: 確保 PYTHONPATH 設置正確
2. **服務未啟動**: 檢查必要服務是否運行
3. **測試資料缺失**: 確認測試資料檔案存在
4. **端口衝突**: 檢查端口 8000 和 8080 是否可用

### **調試模式**
```bash
# 啟用詳細日誌
export LOG_LEVEL=DEBUG

# 執行單一測試並顯示輸出
python tests/core/test_backend_api.py -v
```

## 📋 **維護指南**

### **添加新測試**
1. 選擇適當的分類資料夾
2. 遵循命名慣例: `test_*.py`
3. 包含完整的文檔字串
4. 更新相關 README

### **更新現有測試**
- 保持測試與代碼同步
- 更新預期結果
- 維護向後兼容性

## 🔄 **重新整理歷史**

### **2025年1月 - 測試結構重新整理**
- ✅ 按功能模組重新分類
- ✅ 移除重複和過時測試
- ✅ 改善測試組織和可維護性
- ✅ 創建清晰的執行指南

### **歸檔檔案**
舊的測試結構已移至 `archive/tests/`，包括：
- 舊的 stage 結構
- 重複的測試檔案
- 實驗性測試

---

**最後更新**: 2025年1月  
**狀態**: ✅ **重新整理完成**  
**維護者**: 開發團隊