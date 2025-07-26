# 階段3.1：服務間通信驗證與啟動測試

## 📋 測試概述

階段3.1專注於驗證分離式服務架構中三個獨立服務間的通信和啟動能力：

### 🎯 測試目標

1. **驗證模型服務 → 後端服務的數據傳輸通道**
   - VLM觀察間隔控制功能
   - VLM文字傳輸到State Tracker

2. **驗證後端服務 → 前端服務的查詢響應通道**
   - State Tracker + RAG處理結果
   - API端點響應能力

3. **驗證前端服務 → 後端服務的用戶查詢傳輸通道**
   - 用戶查詢傳輸
   - 即時響應機制

4. **測試各服務的獨立啟動**
   - 後端服務獨立啟動
   - 前端服務獨立可用
   - 服務間不需要整合為單一系統

5. **確認端口通信正常**
   - 後端服務端口8000
   - 各API端點可訪問性

6. **驗證基礎數據流**
   - 端到端數據流：VLM文字 → State Tracker → 前端顯示

## 🚀 執行方式

### 方式一：執行完整測試套件（推薦）

```bash
# 進入測試目錄
cd tests/stage_3_1

# 執行完整的階段3.1測試
python run_stage_3_1_tests.py
```

### 方式二：分別執行各項測試

```bash
# 1. 執行服務啟動測試
python test_service_startup.py

# 2. 執行服務通信測試
python test_service_communication.py
```

## 📋 前置條件

### 1. 後端服務準備
確保後端服務可以正常啟動：

```bash
# 進入後端目錄
cd src/backend

# 安裝依賴（如果需要）
pip install -r requirements.txt

# 啟動後端服務
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 前端文件檢查
確保前端文件存在：
- `src/frontend/index.html`
- `src/frontend/query.html`

### 3. Python依賴
測試腳本需要以下依賴：
```bash
pip install aiohttp requests psutil
```

## 📊 測試內容詳解

### 服務啟動測試 (`test_service_startup.py`)

| 測試項目 | 描述 | 驗證內容 |
|---------|------|---------|
| 後端服務獨立啟動 | 測試後端服務可以獨立啟動 | uvicorn啟動、健康檢查、狀態端點 |
| 前端服務可用性 | 測試前端文件完整性 | HTML文件存在、關鍵功能元素 |
| 服務端口配置 | 測試端口配置正確性 | 各API端點可訪問性 |
| 服務獨立性 | 驗證服務不需要整合 | 獨立功能運行測試 |

### 服務通信測試 (`test_service_communication.py`)

| 測試項目 | 描述 | 驗證內容 |
|---------|------|---------|
| 後端服務健康檢查 | 基本連通性測試 | `/health`端點響應 |
| 後端狀態端點 | 狀態查詢功能 | `/status`端點數據 |
| State Tracker端點 | 狀態追蹤功能 | `/api/v1/state/*`端點群 |
| VLM→State Tracker數據流 | VLM文字處理流程 | 文字處理、狀態更新 |
| 用戶查詢數據流 | 查詢響應流程 | 查詢處理、即時回應 |
| 端到端數據流 | 完整工作流程 | VLM→處理→查詢→回應 |
| 服務獨立性 | 獨立運行驗證 | 無依賴運行測試 |

## 📈 測試報告

### 報告文件
測試完成後會生成以下報告文件：

1. **綜合報告**: `STAGE_3_1_COMPREHENSIVE_REPORT_YYYYMMDD_HHMMSS.json`
2. **啟動測試報告**: `stage_3_1_startup_report_YYYYMMDD_HHMMSS.json`
3. **通信測試報告**: `stage_3_1_test_report_YYYYMMDD_HHMMSS.json`
4. **完成標記**: `../../STAGE_3_1_COMPLETE.md`（測試全部通過時）

### 報告內容
- 測試執行摘要
- 各項測試詳細結果
- 性能指標（響應時間等）
- 發現的問題和建議
- 下一步行動計劃

## ✅ 成功標準

階段3.1被視為成功完成需要滿足：

1. **所有啟動測試通過** (100%)
   - 後端服務可以獨立啟動
   - 前端服務文件完整可用
   - 端口配置正確
   - 服務獨立性驗證通過

2. **所有通信測試通過** (100%)
   - 所有API端點正常響應
   - VLM文字處理流程正常
   - 用戶查詢流程正常
   - 端到端數據流正常

3. **性能指標達標**
   - API響應時間 < 5秒
   - 端到端處理時間 < 10秒

## 🔧 故障排除

### 常見問題

1. **後端服務啟動失敗**
   ```bash
   # 檢查端口是否被占用
   lsof -i :8000
   
   # 檢查依賴是否安裝
   pip list | grep fastapi
   ```

2. **API端點無響應**
   ```bash
   # 手動測試端點
   curl http://localhost:8000/health
   curl http://localhost:8000/status
   ```

3. **前端文件缺失**
   ```bash
   # 檢查文件是否存在
   ls -la src/frontend/index.html
   ls -la src/frontend/query.html
   ```

### 調試模式
如需詳細調試信息，可以設置環境變量：

```bash
export PYTHONPATH=$PWD
export LOG_LEVEL=DEBUG
python run_stage_3_1_tests.py
```

## 🎯 下一步

階段3.1完成後，可以進入：
- **階段3.2**: 雙循環跨服務協調與穩定性
- **階段3.3**: 跨服務基礎功能測試

## 📞 支援

如果測試過程中遇到問題，請檢查：
1. 測試報告中的錯誤信息
2. 後端服務日誌
3. 網絡連接狀態
4. Python依賴版本

---

**執行日期**: 2024年7月26日  
**測試版本**: Stage 3.1  
**架構**: 分離式服務雙循環記憶系統