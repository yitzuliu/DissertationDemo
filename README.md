# 🤖 AI Manual Assistant

**智能手動助手 - 基於視覺語言模型的任務指導系統**

一個集成多個先進視覺語言模型的智能任務指導系統，具備革命性的雙循環記憶架構，能夠實時理解用戶的任務進度並提供精準指導。

## 🌟 **系統特色**

這是一個完整的視覺智能系統，能夠：

- **👀 多模型視覺理解** - 集成 5+ 個先進 VLM 模型，包括 Moondream2、SmolVLM2、Phi-3.5-Vision 等
- **🧠 雙循環記憶系統** - 潛意識狀態追蹤 + 即時查詢響應，毫秒級回應速度
- **🎯 智能任務匹配** - RAG 知識庫結合語義搜索，精準識別任務步驟
- **⚡ 實時狀態管理** - 持續監控任務進度，提供個性化指導
- **🔄 容錯機制** - 完善的異常處理和服務恢復能力

## 🎯 **核心創新**

本系統的突破在於**雙循環記憶架構**：

**潛意識循環（持續運行）**：VLM 觀察 → 智能匹配 → 狀態更新 → 記憶存儲

**即時響應循環（按需觸發）**：用戶查詢 → 直接讀取 → 即時回應

**技術成果**：實現了 0.2ms 平均查詢響應時間，記憶體使用僅 0.004MB，系統穩定性達到 100%。

> **🚀 開發狀態：** 系統已完成三個主要開發階段，包括 RAG 知識庫、雙循環記憶系統和跨服務整合，所有測試均達到 100% 通過率。

## 🏗️ **系統架構**

### 📊 **三層架構 + 雙循環記憶系統**

```
📱 前端層 (Port 5500)
    ↓ HTTP 請求
🔄 後端層 (Port 8000) 
    ↓ 模型 API 調用
🧠 模型服務層 (Port 8080)
    ↓ VLM 觀察
🧠 雙循環記憶系統
    ├── 🔄 潛意識循環 (背景狀態追蹤)
    └── ⚡ 即時響應循環 (用戶查詢)
```

#### **第一層：前端界面 (Port 5500)**
- **多界面支持**：主應用 (`index.html`)、統一界面 (`unified.html`)、查詢界面 (`query.html`)
- **實時攝像頭整合**：支持多攝像頭切換和實時預覽
- **響應式設計**：適配桌面和移動設備
- **狀態監控**：實時後端連接狀態顯示
- **查詢系統**：支持自然語言查詢和示例觸發

#### **第二層：後端服務 (Port 8000)**
- **FastAPI 服務器**：統一 API 網關，兼容 OpenAI 格式
- **狀態追蹤器**：雙循環記憶系統核心，持續監控任務進度
- **RAG 知識庫**：ChromaDB 向量搜索，語義匹配任務步驟
- **圖像處理**：針對不同 VLM 模型的預處理優化
- **配置管理**：動態模型切換和參數調整
- **查詢分類器**：91.7% 準確率的意圖識別系統
- **記憶體管理**：滑動窗口機制，使用量 < 1MB

#### **第三層：模型服務 (Port 8080)**
- **多 VLM 支持**：Moondream2、SmolVLM2、SmolVLM、Phi-3.5-Vision、LLaVA-MLX
- **Apple Silicon 優化**：MLX 和 MPS 加速，針對 M 系列芯片優化
- **OpenAI 兼容 API**：標準聊天完成接口
- **資源管理**：自動清理和記憶體優化
- **性能監控**：健康檢查和負載平衡

#### **🧠 雙循環記憶系統**
- **🔄 潛意識循環**：VLM 觀察 → 狀態追蹤 → RAG 匹配 → 記憶更新（持續後台運行）
- **⚡ 即時響應循環**：用戶查詢 → 直接記憶查找 → <1ms 響應
- **🎯 查詢分類**：意圖識別準確率 91.7%
- **📊 滑動窗口**：高效記憶管理，自動清理機制
- **🔍 語義匹配**：ChromaDB 向量搜索，上下文理解

## 🎯 **支持的模型與最新性能**

系統集成多個先進的視覺語言模型，經過全面的 VQA 2.0 測試驗證。**最新測試結果 (2025-07-29 13:12:58)：**

### **🏆 性能排名 (VQA 2.0 - 20 題測試)**

| 模型 | VQA 準確率 | 簡單準確率 | 平均推理時間 | 記憶體使用 | 狀態 |
|------|:----------:|:----------:|:------------:|:----------:|:----:|
| **🥇 Moondream2** | **62.5%** | **65.0%** | 8.35s | 0.10GB | ✅ **最佳整體** |
| **🥈 SmolVLM2-MLX** | **52.5%** | **55.0%** | 8.41s | 2.08GB | ✅ **平衡型** |
| **⚡ SmolVLM-GGUF** | **36.0%** | **35.0%** | **0.39s** | 1.58GB | ✅ **最快速** |
| **🥉 Phi-3.5-MLX** | **35.0%** | **35.0%** | 5.29s | 1.53GB | ✅ **快速型** |
| **⚠️ LLaVA-MLX** | **21.0%** | **20.0%** | 24.15s | 1.16GB | 🚫 **有問題** |

### **🚨 關鍵發現：上下文理解限制**
**所有模型的上下文理解能力均為 0%** - 無法維持對話記憶或回憶先前圖像信息。多輪對話需要外部記憶系統（我們的雙循環架構解決了這個問題）。

### **📊 模型推薦**
- **🎯 生產環境 VQA**：Moondream2（最高準確率：65.0%）
- **⚡ 實時應用**：SmolVLM-GGUF（最快推理：0.39s）
- **🔄 平衡使用**：SmolVLM2-MLX（良好的速度/準確率平衡）
- **🚫 避免使用**：LLaVA-MLX（嚴重性能問題：24.15s 推理時間）

### **🔧 技術特點**
- **Apple Silicon 優化**：所有模型均針對 M 系列芯片進行 MLX/MPS 優化
- **統一接口**：所有模型使用相同的 OpenAI 兼容 API
- **熱切換**：支持運行時模型切換，無需重啟系統
- **資源管理**：智能記憶體管理和自動清理機制

> **⚠️ 單模型運行**：由於記憶體限制，建議一次只運行一個模型服務器。詳細比較請參見 [模型性能指南](src/testing/reports/model_performance_guide.md)。

## 🚀 **快速開始**

### **環境準備**
```bash
# 克隆項目
git clone https://github.com/yitzuliu/DissertationDemo.git
cd DissertationDemo

# 激活虛擬環境
source ai_vision_env/bin/activate

# 安裝依賴
pip install -r requirements.txt

# Apple Silicon 用戶安裝 MLX 支持
pip install mlx-vlm
```

### **系統啟動（三層架構）**
需要在三個不同的終端會話中運行三個組件：

#### **1. 啟動模型服務器（選擇一個）**
```bash
# 推薦：Moondream2（最佳整體性能）
cd src/models/moondream2
python run_moondream2_optimized.py

# 或者：SmolVLM2（平衡性能）
cd src/models/smolvlm2
python run_smolvlm2_500m_video_optimized.py

# 或者：SmolVLM（最快速度）
cd src/models/smolvlm
python run_smolvlm.py
```

#### **2. 啟動後端服務器（新終端）**
```bash
cd src/backend
python main.py
```

#### **3. 啟動前端服務器（新終端）**
```bash
cd src/frontend
python -m http.server 5500
```

### **訪問系統**
在瀏覽器中打開以下任一界面：

- **主應用**：`http://localhost:5500/index.html` - 攝像頭 + AI 分析
- **統一界面**：`http://localhost:5500/unified.html` - 視覺分析 + 狀態查詢
- **查詢界面**：`http://localhost:5500/query.html` - 專用狀態查詢

### **系統驗證**
```bash
# 檢查服務狀態
curl http://localhost:8080/health  # 模型服務
curl http://localhost:8000/health  # 後端服務

# 測試 API
curl -X POST http://localhost:8000/api/v1/state/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What step am I on?"}'
```

## 📖 **文檔與指南**

### **🚀 系統組件文檔**
- **[後端服務指南](src/backend/README.md)** - FastAPI 服務器和 API 端點
- **[前端界面指南](src/frontend/README.md)** - 三種界面的使用說明
- **[模型系統指南](src/models/README.md)** - VLM 模型實現和性能比較
- **[測試框架指南](tests/README.md)** - 完整的測試套件和驗證

### **📊 最新測試結果與分析**
- **[測試結果總結](TEST_RESULTS_SUMMARY.md)** - 最新 VQA 2.0 性能結果 (2025-07-29)
- **[VQA 分析報告](src/testing/reports/vqa_analysis.md)** - 詳細的 VQA 2.0 性能分析
- **[模型性能指南](src/testing/reports/model_performance_guide.md)** - 生產環境推薦
- **[上下文理解分析](src/testing/reports/context_understanding_analysis.md)** - 關鍵上下文能力評估

### **🧪 測試框架**
- **[測試概覽](src/testing/README.md)** - 綜合測試框架
- **[VQA 測試](src/testing/vqa/README.md)** - VQA 2.0 評估框架
- **[VLM 測試](src/testing/vlm/README.md)** - 視覺語言模型測試套件
- **[測試報告](src/testing/reports/README.md)** - 所有分析報告

### **🏗️ 系統架構文檔**
- **[RAG 系統運作指南](docs/RAG_SYSTEM_OPERATION_GUIDE.md)** - RAG 知識庫技術文檔
- **[狀態追蹤器使用指南](docs/STATE_TRACKER_USER_GUIDE.md)** - 雙循環記憶系統
- **[VLM 系統完整指南](docs/VLM_SYSTEM_GUIDE.md)** - 視覺語言模型系統
- **[後端前端接口指南](docs/BACKEND_FRONTEND_INTERFACE_GUIDE.md)** - API 接口文檔

### **📋 開發進度文檔**
- **[階段完成報告](STAGE_*_COMPLETE.md)** - 開發進度文檔
- **[階段 2 最終驗證](STAGE_2_FINAL_VALIDATION.md)** - 雙循環系統驗證
- **[階段 3.3 完成](STAGE_3_3_COMPLETE.md)** - 跨服務功能測試

## ✨ **核心功能特色**

### **🎯 多模型視覺理解系統**
- **👁️ 智能視覺分析** - 集成 5+ 個先進 VLM 模型，支持實時圖像和視頻理解
  - **🔄 實時處理** - 持續場景理解和對象識別
  - **🎯 上下文感知** - 理解活動和工作流程，不僅僅是對象識別
  - **💡 自適應指導** - 根據用戶偏好調整指導風格
  - **⚡ 本地處理** - 離線工作，無需昂貴的雲端依賴
- **🔧 模型熱切換** - 支持運行時切換不同 VLM 模型
- **📊 性能監控** - 實時監控推理時間、準確率和資源使用
- **🛡️ 容錯機制** - 完善的異常處理和服務恢復能力

### **🧠 革命性雙循環記憶系統**
- **� 潛意識t循環** - 背景狀態追蹤，持續監控任務進度
  - VLM 觀察 → 智能匹配 → 狀態更新 → 記憶存儲
  - 平均處理時間：16ms（比目標快 6 倍）
  - 匹配準確率：91.7%
- **⚡ 即時響應循環** - 毫秒級查詢響應，無需 VLM 調用
  - 用戶查詢 → 直接記憶查找 → 即時回應
  - 平均響應時間：0.2ms（比目標快 100 倍）
  - 系統吞吐量：334,207 查詢/秒
- **🧠 RAG 知識庫** - ChromaDB 向量搜索，智能匹配任務步驟
- **📊 滑動窗口記憶** - 高效記憶管理，使用量 < 1MB
- **🎯 查詢分類** - 91.7% 準確率的意圖識別

### **🔧 系統架構優勢**
- **三層分離架構** - 前端、後端、模型服務獨立運行
- **統一 API 接口** - OpenAI 兼容的標準接口
- **配置管理** - 動態配置更新和模型切換
- **日誌系統** - 完整的系統監控和錯誤追蹤
- **測試框架** - 全面的 VQA 2.0 測試和性能驗證

### **🧪 已驗證功能**
- **視覺理解**：多模型支持，準確率達 65%（Moondream2）
- **記憶系統**：雙循環協調，100% 成功率
- **狀態追蹤**：實時任務進度監控
- **查詢響應**：支持自然語言查詢，6 種查詢類型
- **容錯恢復**：100% 服務恢復率

## 🎬 **實際應用示例**

### 🍳 **咖啡沖泡助手**
```
VLM 觀察：[咖啡豆, 磨豆機, 濾紙, 手沖壺, 電子秤]
系統識別："咖啡沖泡任務 - 步驟 3：研磨咖啡豆"
用戶查詢："我現在在哪一步？"

系統回應：
"您目前在咖啡沖泡任務的第 3 步：研磨咖啡豆
- 所需工具：咖啡豆、磨豆機、電子秤
- 預估時間：2-3 分鐘
- 完成指標：研磨至中等細度，22 克咖啡粉
- 安全提示：注意磨豆機刀片安全

下一步：將濾紙放入手沖壺並用熱水沖洗..."
```

### 🔧 **系統狀態查詢**
```
用戶查詢："我需要什麼工具？"
系統響應時間：0.2ms

系統回應：
"根據當前任務步驟，您需要以下工具：
✅ 已識別：咖啡豆、磨豆機、電子秤
🔄 即將需要：手沖壺、濾紙、計時器
📊 任務進度：37.5% (步驟 3/8)
🎯 置信度：85%

建議：準備好手沖壺和濾紙，下一步會用到。"
```

### 🧠 **記憶系統展示**
```
潛意識循環（持續運行）：
VLM 觀察 → "用戶正在使用磨豆機" → RAG 匹配 → 更新狀態

即時響應循環（用戶觸發）：
用戶："整體進度如何？" → 直接記憶查找 → 0.2ms 回應

系統回應：
"咖啡沖泡任務整體進度：
✅ 已完成：收集器具 (步驟 1)
✅ 已完成：加熱水溫 (步驟 2)  
🔄 進行中：研磨咖啡豆 (步驟 3)
⏳ 待完成：5 個步驟
📊 完成度：37.5%
⏱️ 預估剩餘時間：8-10 分鐘"
```

## 🛠️ **技術棧**

### **前端技術**
- **HTML5, CSS3, JavaScript** - 現代 Web 技術
- **多界面支持** - 主應用、統一界面、查詢界面
- **實時攝像頭整合** - 支持多攝像頭切換
- **響應式設計** - 適配桌面和移動設備
- **WebSocket 通信** - 實時狀態更新

### **後端技術**
- **FastAPI (Python)** - 高性能 Web 框架
- **OpenAI 兼容 API** - 標準聊天完成接口
- **圖像預處理管道** - 針對不同 VLM 模型優化
- **狀態追蹤系統** - 雙循環記憶架構
- **配置管理** - 動態配置更新和模型切換

### **AI 模型**
- **Moondream2** - 最佳整體性能 (65.0% 準確率)
- **SmolVLM2-500M-Video** - 視頻理解能力
- **SmolVLM-500M-Instruct** - 最快推理 (0.39s)
- **Phi-3.5-Vision (MLX)** - Apple Silicon 優化
- **LLaVA (MLX)** - 高精度分析
- **統一接口** - BaseVisionModel 抽象基類

### **記憶系統**
- **雙循環架構** - 潛意識循環 + 即時響應循環
- **RAG 向量搜索** - ChromaDB 語義匹配
- **滑動窗口記憶** - 高效記憶管理 (<1MB)
- **查詢分類引擎** - 91.7% 意圖識別準確率

### **基礎設施**
- **三層分離架構** - 前端 → 後端 → 模型服務
- **Apple Silicon 優化** - MLX 和 MPS 加速
- **配置管理系統** - JSON 配置文件
- **全面日誌監控** - 系統、用戶、視覺日誌
- **服務通信驗證** - 健康檢查和負載平衡

### **開發與測試**
- **VQA 2.0 測試框架** - 標準化性能評估
- **綜合測試套件** - 單元測試、集成測試、性能測試
- **持續集成** - 自動化測試和驗證
- **性能監控** - 實時指標收集和分析

## 💡 **系統優勢**

### **🔍 相比傳統教學視頻：**
- **無需重複播放** - 系統實時理解您的操作進度
- **無假設前提** - 不假設您的技能水平或可用工具
- **個性化指導** - 根據您的實際情況提供針對性指導
- **持續適應** - 隨著您的進度實時調整指導內容
- **即時進度追蹤** - "您已完成 60%，下一步是..."

### **🤖 相比其他 AI 助手：**
- **持續視覺監控** - 像人眼一樣持續觀察工作空間
- **理解活動序列** - 理解正在進行的活動和時間順序
- **流暢進度指導** - "我看到您已完成步驟 1，正在進行步驟 2..."
- **實時錯誤預防** - "我看到您要拿那個工具，建議使用較小的那個..."
- **完整會話記憶** - 能夠即時回答"我在哪一步？"

### **📚 相比傳統手冊：**
- **持續自適應指導** - 實時響應您的操作活動
- **自然對話** - 工作時提問，立即獲得上下文相關答案
- **時間記憶** - 記住整個工作會話和進度流程
- **實時鼓勵** - 慶祝進度："完美！您做得很好！"
- **詳細工具清單** - "您需要：螺絲刀、扳手、安全眼鏡"

### **🎯 技術突破：**

#### **雙循環記憶架構**
- **潛意識循環**：持續背景監控，無需用戶干預
- **即時響應循環**：毫秒級查詢響應，無需重新分析

#### **多模型整合**
- **5+ VLM 模型**：根據需求選擇最佳模型
- **統一接口**：無縫切換不同模型
- **性能優化**：Apple Silicon 專門優化

#### **智能記憶管理**
- **滑動窗口**：高效記憶使用 (<1MB)
- **語義搜索**：ChromaDB 向量匹配
- **自動清理**：智能記憶管理

### **🏆 最終結果：**
**信心取代挫折感。流暢指導取代碎片化指令。自然導師取代機械回應。永不遺忘您位置的智能記憶。**

## 🌍 **應用場景**

### **🍳 烹飪指導**
- **咖啡沖泡** - 完整的 8 步驟指導系統（已實現）
- **基礎烹飪** - 從簡單料理到複雜食譜
- **烘焙指導** - 精確時間和溫度控制
- **食材識別** - 智能識別食材和工具

### **🔧 維修助手**
- **電子設備** - 筆記本電腦、手機、家電維修
- **汽車保養** - 基礎維護和故障排除
- **家具修復** - 木工、金屬加工指導
- **工具識別** - 自動識別所需工具和材料

### **🪑 組裝指導**
- **家具組裝** - IKEA 家具、DIY 項目
- **電子產品** - 電腦組裝、設備安裝
- **模型製作** - 精密組裝指導
- **進度追蹤** - 實時組裝進度監控

### **📚 學習輔助**
- **技能學習** - 新技能的步驟化學習
- **實驗指導** - 科學實驗和操作指導
- **藝術創作** - 繪畫、手工藝指導
- **運動訓練** - 動作分解和糾正

### **🏠 家居改善**
- **裝修指導** - 牆面處理、地板安裝
- **園藝指導** - 植物護理、景觀設計
- **清潔保養** - 深度清潔和維護
- **安全檢查** - 家居安全評估

### **🎨 創意項目**
- **藝術創作** - 繪畫、雕塑、手工藝
- **DIY 項目** - 創意製作和改造
- **攝影指導** - 拍攝技巧和後期處理
- **音樂學習** - 樂器演奏指導

## 📊 **Current System Performance**

### **🧠 Dual-Loop Memory System**
- **✅ System Success Rate**: 100% (all tests passed)
- **✅ Query Classification**: 100% accuracy (intent recognition)
- **✅ Response Time**: <50ms for instant queries
- **✅ Memory Usage**: <1MB sliding window optimization
- **✅ Service Recovery**: 100% fault tolerance

### **🎯 VLM Performance (Latest VQA 2.0 Results)**
- **🥇 Best Accuracy**: Moondream2 (65.0% simple, 62.5% VQA)
- **⚡ Fastest Inference**: SmolVLM-GGUF (0.39s average)
- **🔄 Best Balance**: SmolVLM2-MLX (55.0% accuracy, 8.41s)
- **🚫 Critical Issue**: LLaVA-MLX (24.15s inference, 20.0% accuracy)

### **⚠️ Known Limitations**
- **Context Understanding**: 0% capability across all VLMs
- **Text Reading**: Poor performance on text within images
- **Counting Tasks**: Challenges with numerical reasoning
- **Multi-turn Conversations**: Require external memory (our dual-loop system)

## 🤝 **Contributing**

We welcome contributions! Please see our documentation for detailed instructions on:
- **[Getting Started](GETTING_STARTED.md)** - Development environment setup
- **[Testing Framework](src/testing/README.md)** - Comprehensive testing procedures
- **[Project Structure](PROJECT_STRUCTURE.md)** - System architecture and components
- **[Latest Results](TEST_RESULTS_SUMMARY.md)** - Current performance benchmarks

## 📄 **License**

This project is licensed under the [MIT License](./LICENSE).

## 🔗 **Links**

- **GitHub Repository**: [AI Manual Assistant](https://github.com/yitzuliu/DissertationDemo)
- **Documentation**: See [docs](./docs/) directory
- **Issues**: [GitHub Issues](https://github.com/yitzuliu/DissertationDemo/issues)

---

**Built with ❤️ for makers, learners, and anyone who wants to confidently tackle any hands-on task with intelligent AI assistance.** 