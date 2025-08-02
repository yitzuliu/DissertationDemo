# 🏗️ AI Manual Assistant - 項目結構

## 📁 整理後的目錄結構

```
destination_code/
├── 📁 src/                          # 源代碼
│   ├── 📁 backend/                  # 後端服務
│   │   └── main.py                  # FastAPI 後端主程序
│   ├── 📁 frontend/                 # 前端界面
│   │   └── index.html               # 統一前端界面
│   ├── 📁 models/                   # VLM 模型服務
│   │   └── smolvlm/                 # SmolVLM 模型
│   │       └── run_smolvlm.py       # VLM 服務啟動器
│   ├── 📁 state_tracker/            # 狀態追蹤系統
│   │   └── query_processor.py       # 查詢處理器（已集成 VLM Fallback）
│   ├── 📁 vlm_fallback/             # VLM Fallback 系統 ⭐ 新增
│   │   ├── __init__.py              # 模組初始化
│   │   ├── decision_engine.py       # 決策引擎
│   │   ├── prompt_manager.py        # 提示詞管理器
│   │   ├── vlm_client.py           # VLM 客戶端
│   │   ├── fallback_processor.py   # 核心處理器
│   │   └── config.py               # 配置管理
│   ├── 📁 config/                   # 配置文件
│   │   └── vlm_fallback_config.json # VLM Fallback 配置 ⭐ 新增
│   └── 📁 logging/                  # 日誌系統
│
├── 📁 tests/                        # 測試文件
│   ├── test_complete_system_e2e.py  # 完整端到端測試
│   ├── test_core_components.py      # 核心組件測試
│   ├── test_vlm_fallback_*.py       # VLM Fallback 測試
│   ├── test_backend_only.py         # 後端專用測試
│   ├── test_integration_only.py     # 集成測試
│   └── quick_test.py               # 快速驗證測試
│
├── 📁 docs/                         # 文檔
│   ├── vlm_fallback_user_guide.md   # VLM Fallback 用戶指南 ⭐ 新增
│   ├── VLM_FALLBACK_INTEGRATION_COMPLETE.md # 集成完成報告 ⭐ 新增
│   ├── FINAL_TEST_GUIDE.md          # 最終測試指南 ⭐ 新增
│   ├── TESTING_GUIDE.md             # 測試指南 ⭐ 新增
│   ├── development_stages/          # 開發階段文檔
│   │   ├── STAGE_*.md               # 各階段完成報告
│   │   └── TEST_RESULTS_SUMMARY.md  # 測試結果總結
│   └── [其他現有文檔]
│
├── 📁 .kiro/                        # Kiro IDE 配置
│   └── specs/vlm-fallback-system/   # VLM Fallback 系統規格
│       ├── README.md                # 系統概述
│       ├── design.md                # 設計文檔
│       ├── tasks.md                 # 任務清單
│       └── development-checklist.md # 開發檢查清單
│
├── start_system.py                  # 系統啟動腳本 ⭐ 新增
├── requirements.txt                 # Python 依賴
└── README.md                        # 項目說明
```

## 🎯 核心組件

### 1. VLM Fallback System ⭐ 新增功能
- **位置**: `src/vlm_fallback/`
- **功能**: 智能 VLM 回退系統
- **特點**: 用戶透明、自動觸發、錯誤恢復

### 2. 後端服務
- **位置**: `src/backend/main.py`
- **功能**: FastAPI 後端，已集成 VLM Fallback
- **端口**: http://localhost:8000

### 3. VLM 服務
- **位置**: `src/models/smolvlm/run_smolvlm.py`
- **功能**: SmolVLM 視覺語言模型服務
- **端口**: http://localhost:8080

### 4. 前端界面
- **位置**: `src/frontend/index.html`
- **功能**: 統一的視覺分析和查詢界面
- **特點**: 支持 VLM Fallback（用戶無感知）

## 🧪 測試系統

### 完整測試套件
- **`tests/test_complete_system_e2e.py`** - 端到端測試（✅ 17/17 通過）
- **`tests/test_core_components.py`** - 核心組件測試
- **`tests/quick_test.py`** - 快速驗證測試

### 專項測試
- **`tests/test_vlm_fallback_*.py`** - VLM Fallback 專項測試
- **`tests/test_integration_only.py`** - 集成測試（無需服務器）
- **`tests/test_backend_only.py`** - 後端專用測試

## 📚 文檔系統

### 用戶文檔
- **`docs/vlm_fallback_user_guide.md`** - VLM Fallback 用戶指南
- **`docs/FINAL_TEST_GUIDE.md`** - 最終測試指南
- **`docs/TESTING_GUIDE.md`** - 詳細測試指南

### 開發文檔
- **`docs/VLM_FALLBACK_INTEGRATION_COMPLETE.md`** - 集成完成報告
- **`docs/development_stages/`** - 開發階段文檔
- **`.kiro/specs/vlm-fallback-system/`** - 系統規格文檔

## 🚀 快速啟動

### 方法 1：一鍵啟動
```bash
python start_system.py --all
```

### 方法 2：手動啟動
```bash
# 終端 1：後端
cd src/backend && python main.py

# 終端 2：VLM 服務
cd src/models/smolvlm && python run_smolvlm.py

# 終端 3：測試
python tests/quick_test.py
```

### 方法 3：只測試集成
```bash
python tests/test_integration_only.py
```

## ✅ 系統狀態

### 開發完成度
- **Stage 1**: 核心功能實現 ✅ 100%
- **Stage 2**: 系統集成 ✅ 100%
- **Stage 3**: 測試驗證 ✅ 100%

### 測試結果
- **端到端測試**: ✅ 17/17 通過
- **集成測試**: ✅ 5/5 通過
- **功能測試**: ✅ 全部通過

### 核心特性
- ✅ 透明 VLM Fallback
- ✅ 智能決策引擎
- ✅ 強健錯誤處理
- ✅ 統一用戶體驗
- ✅ 完整前端集成

## 🎯 使用指南

1. **啟動系統**: 使用 `start_system.py --all`
2. **打開前端**: 訪問 `src/frontend/index.html`
3. **測試功能**: 
   - 狀態查詢：「Where am I?」
   - VLM Fallback：「What is the meaning of life?」
   - 視覺分析：上傳圖片並提問
4. **監控日誌**: 查看終端輸出

## 📞 支持

- **測試問題**: 查看 `docs/FINAL_TEST_GUIDE.md`
- **使用問題**: 查看 `docs/vlm_fallback_user_guide.md`
- **開發問題**: 查看 `.kiro/specs/vlm-fallback-system/`

---

**🎉 VLM Fallback System 已完全集成並可投入使用！**