# Tests 重新整理計劃

## 🎯 目標
重新整理測試結構，使其更清晰、更易維護，並符合專案的實際架構。

## 📁 新結構

### Core 核心功能測試
- `test_backend_api.py` ← 保留現有
- `test_vector_optimization.py` ← 重命名 `test_stage_1_3.py`
- `test_state_tracker.py` ← 從 `stage_2_integrated_tests.py` 提取
- `test_query_processor.py` ← 新建，整合查詢處理測試

### Memory System 記憶系統測試
- `test_task_knowledge.py` ← 保留現有
- `test_memory_consistency.py` ← 重命名 `stage_2_4/test_task_knowledge_enhanced.py`
- `test_rag_system.py` ← 新建，整合 RAG 相關測試

### VLM Fallback 測試
- `test_fallback_triggers.py` ← 整合現有 VLM fallback 測試
- `test_fallback_integration.py` ← 重命名 `test_vlm_fallback_integration.py`
- `test_image_processing.py` ← 新建，專門測試圖片處理

### Integration 整合測試
- `test_dual_loop_coordination.py` ← 移動 `stage_3_2/test_dual_loop_coordination.py`
- `test_cross_service.py` ← 重命名 `stage_3_3/test_stage_3_3_final.py`
- `test_end_to_end.py` ← 整合現有端到端測試

### System 系統級測試
- `test_service_startup.py` ← 整合 `stage_3_1/` 測試
- `test_logging_system.py` ← 整合 `logging_system_tests/`
- `test_performance.py` ← 新建，整合性能相關測試

### Scenarios 場景測試
- `test_coffee_brewing.py` ← 新建，專門測試咖啡沖泡場景
- `test_task_scenarios.py` ← 新建，其他任務場景

## 🗂️ 歸檔檔案

### 移至 archive/tests/deprecated/
- `test_backend_only.py` - 功能重複
- `test_integration_only.py` - 功能重複
- `quick_test.py` - 已整合到其他測試
- `stage_2_integrated_results.json` - 舊結果檔案

### 移至 archive/tests/old_structure/
- `stage_3_1/` - 整個資料夾
- `stage_3_2/` - 整個資料夾  
- `stage_3_3/` - 整個資料夾
- `logging_system_tests/` - 整個資料夾

### 移至 archive/tests/experimental/
- `test_vlm_fallback_e2e.py` - 實驗性測試
- `test_full_system_automated.py` - 實驗性測試
- `test_complete_system_e2e.py` - 實驗性測試

## ✅ 執行步驟

1. 創建新的資料夾結構
2. 移動和重命名檔案
3. 更新檔案內的導入路徑
4. 創建新的 README.md
5. 測試所有重新整理後的檔案
6. 歸檔舊檔案

## 📊 預期效果

- 更清晰的測試分類
- 更容易找到相關測試
- 減少重複測試
- 更好的維護性
- 符合專案架構的組織方式