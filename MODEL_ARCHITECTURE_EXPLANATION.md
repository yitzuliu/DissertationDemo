# 🏗️ 模型架構說明：Launcher vs Server

## 📊 架構對比

```
用戶命令
    ↓
model_launcher.py (啟動器)
    ↓
unified_model_server.py (服務器)
    ↓
實際的AI模型 (SmolVLM2, Moondream2, etc.)
```

## 🔍 詳細對比

| 特性 | model_launcher.py | unified_model_server.py |
|------|-------------------|-------------------------|
| **角色** | 🚀 **啟動器/管理器** | 🖥️ **實際服務器** |
| **功能** | 選擇、配置、啟動模型 | 載入模型、處理請求 |
| **運行時間** | 短暫運行後退出 | 持續運行直到停止 |
| **用戶交互** | 命令行介面 | HTTP API 介面 |
| **主要任務** | 模型管理和啟動 | 模型推理和服務 |

## 🎯 具體功能分工

### model_launcher.py (啟動器)
```bash
# 這些都是 launcher 的功能
python src/models/model_launcher.py --list          # 列出模型
python src/models/model_launcher.py --status xxx   # 檢查狀態  
python src/models/model_launcher.py --model xxx    # 啟動模型
python src/models/model_launcher.py                # 智能預設
```

**主要職責:**
- 🔍 **模型發現**: 列出所有可用模型
- 🧠 **智能選擇**: 根據記憶體自動選擇預設模型
- ✅ **依賴檢查**: 確認模型所需依賴是否安裝
- 📊 **狀態監控**: 檢查模型配置和腳本狀態
- 🚀 **啟動管理**: 啟動對應的模型服務器
- ⚙️ **配置管理**: 處理端口、主機等參數

### unified_model_server.py (服務器)
```bash
# 這是 server 被 launcher 調用時的實際命令
python src/models/unified_model_server.py --model moondream2_optimized --port 8080
```

**主要職責:**
- 🤖 **模型載入**: 實際載入AI模型到記憶體
- 🌐 **HTTP服務**: 提供REST API端點
- 🔄 **請求處理**: 處理圖像分析請求
- 📡 **API兼容**: 提供OpenAI兼容的API格式
- 💾 **記憶體管理**: 管理模型在記憶體中的狀態
- 📊 **健康檢查**: 提供服務器狀態監控

## 🔄 完整工作流程

### 1. 用戶啟動模型
```bash
python src/models/model_launcher.py --model moondream2_optimized
```

### 2. Launcher 的工作
```
1. 檢查模型是否存在 ✅
2. 驗證依賴是否安裝 ✅  
3. 讀取模型配置 ✅
4. 準備啟動參數 ✅
5. 調用 unified_model_server.py
```

### 3. Server 的工作
```
1. 接收啟動參數 ✅
2. 載入指定的AI模型 ✅
3. 啟動Flask HTTP服務器 ✅
4. 等待API請求 ✅
5. 處理圖像分析請求 ✅
```

### 4. 用戶使用API
```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [...]}'
```

## 🎯 為什麼需要兩個文件？

### 🚀 **分離關注點**
- **Launcher**: 專注於模型管理和啟動邏輯
- **Server**: 專注於模型推理和API服務

### 🔧 **靈活性**
- 可以直接調用 `unified_model_server.py` 進行開發測試
- 可以通過 `model_launcher.py` 進行生產環境管理

### 📊 **可維護性**
- 啟動邏輯和服務邏輯分開，更容易維護
- 可以獨立測試和調試每個組件

## 💡 使用建議

### 🎯 **日常使用** (推薦)
```bash
# 智能預設啟動
python src/models/model_launcher.py

# 指定模型啟動
python src/models/model_launcher.py --model moondream2_optimized
```

### 🔧 **開發調試**
```bash
# 直接啟動服務器 (跳過launcher)
python src/models/unified_model_server.py --model moondream2_optimized

# 檢查模型狀態
python src/models/model_launcher.py --status moondream2_optimized
```

### 🚀 **快速切換**
```bash
# 使用切換腳本
python switch_model.py --quick    # 最快模型
python switch_model.py --best     # 最佳模型
```

## 🎉 智能預設模型邏輯

### 記憶體檢測
- **< 4GB**: 選擇 `moondream2_optimized` (最省記憶體)
- **4-8GB**: 選擇 `moondream2_optimized` (平衡選擇)  
- **> 8GB**: 選擇 `smolvlm2_500m_video_optimized` (最佳性能)

### 備用策略
如果無法檢測記憶體，按優先級選擇：
1. `moondream2_optimized` (最穩定)
2. `smolvlm2_500m_video_optimized` (最佳性能)
3. `phi3_vision_optimized` (詳細分析)
4. 其他可用模型

---

**總結**: 現在你有了一個智能、統一、易用的模型管理系統！🚀