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

## ✨ **Key Features**

**🎯 Core Vision with Dual-Loop Memory:**
- **👁️ Intelligent Vision** - AI understands your work context, either through continuous video or smart image analysis
   - **🔄 Real-time Processing** - Continuous scene understanding and object recognition
   - **🎯 Context-Aware** - Understands activities and workflows, not just objects  
   - **💡 Adaptive Guidance** - Learns your preferences and adjusts instruction style
   - **⚡ Local Processing** - Works offline with optimized performance
- **🧠 Context Understanding** - Tracks your progress and provides relevant guidance
- **⚡ Real-time Guidance** - Provides contextual help as you work
- **🎯 Activity Recognition** - Understands what you're doing, not just what objects are present
- **💡 Adaptive Mentoring** - Learns your pace and provides encouragement and corrections
- **📱 Flexible Input** - Currently testing both continuous video and intelligent image capture
- **💰 Cost-Effective** - Efficient local processing without expensive cloud dependencies

**🧠 Revolutionary Dual-Loop Memory System:**
- **🔄 Subconscious Loop** - Background state tracking that continuously monitors your progress
- **⚡ Instant Response Loop** - Immediate answers to queries like "What step am I on?" or "What tools do I need?"
- **🧠 RAG Knowledge Base** - Intelligent matching of VLM observations to task steps
- **📊 Sliding Window Memory** - Efficient memory management with automatic cleanup
- **🎯 Query Classification** - 100% accurate understanding of user intent

**🧪 Current Testing:**
- **Video Approach**: Continuous understanding with temporal reasoning (SmolVLM2-Video)
- **Image Approach**: High-frequency intelligent capture with context memory (SmolVLM)
- **Memory System**: Dual-loop coordination with 100% success rate

## 🎬 **Real-World Examples**

### 🍳 **Cooking Assistant**
```
AI sees [eggs, pan, stove, spatula, salt, butter]
AI recognizes "scrambled eggs preparation setup"
User asks "What step am I on?"

AI Response:
"You're currently on Step 1: Preparation. I can see you have all the necessary tools:
- Eggs, pan, stove, spatula, salt, butter
- Estimated time: 2-3 minutes
- Safety notes: Be careful with hot pan

Next: Crack 2-3 eggs into a bowl and whisk them..."
```

### 🔧 **Repair Assistant**
```
AI sees [laptop, screwdriver, replacement_part, manual]
AI recognizes "laptop repair/upgrade scenario"  
User asks "What tools do I need?"

AI Response:
"Based on your current repair task, you need:
- Phillips head screwdriver (you have this)
- Anti-static wrist strap (recommended)
- Small container for screws
- Estimated time: 15-20 minutes
- Safety notes: Ensure laptop is powered off and unplugged

I can see you're ready to start the repair process..."
```

### 🪑 **Assembly Assistant**
```
AI sees [furniture_parts, screws, allen_wrench, instruction_manual]
AI recognizes "furniture assembly in progress"
User asks "How much progress have I made?"

AI Response:
"You've completed 60% of the assembly! Current status:
- ✅ Base frame assembled correctly
- ✅ Side panels attached
- 🔄 Working on: Shelf installation
- Remaining: 2 steps (shelf alignment, final tightening)
- Estimated time remaining: 10-15 minutes

You're doing great! The next step is to align the shelf with the brackets..."
```

## 🛠️ **Tech Stack**

### **Frontend**
- HTML5, CSS3, JavaScript
- Real-time camera integration
- Responsive design with modern UI
- Query interface for instant responses

### **Backend**
- FastAPI (Python)
- Unified model server architecture
- Image preprocessing pipeline
- **State Tracker system**
- **RAG knowledge base integration**

### **AI Models**
- SmolVLM & SmolVLM2
- Moondream2
- Phi-3.5-Vision (MLX Optimized)
- LLaVA (MLX Optimized)
- YOLO8

### **Memory System**
- **Dual-loop architecture**
- **RAG vector search (ChromaDB)**
- **Sliding window memory management**
- **Query classification engine**

### **Infrastructure**
- Three-layer architecture (Frontend → Backend → Model Server)
- Configuration management system
- Comprehensive logging and monitoring
- **Service communication validation**

## 💡 **What Makes This Different**

### **🔍 Unlike YouTube Tutorials:**
- **No more rewinding** to see what tool they're using
- **No assumptions** about what you have or your skill level
- **No generic instructions** that don't match your specific situation
- **Continuous adaptation** to your actual progress as it happens
- **Instant progress tracking** - "You're 60% done, next step is..."

### **🤖 Unlike Other AI Assistants:**
- **Continuously watches your workspace** like human eyes, not relying on your descriptions
- **Understands ongoing activities** and temporal sequences, not just static objects
- **Provides flowing progress guidance**: "I can see you've completed step 1 and are moving to step 2..."
- **Prevents mistakes as they develop** in real-time: "I see you reaching for that tool - use the smaller one instead..."
- **Remembers your entire session** and can answer "What step am I on?" instantly

### **📚 Unlike Traditional Manuals:**
- **Continuously adaptive guidance** - responds to your ongoing activities in real-time
- **Natural dialogue** - ask questions while working, get immediate contextual answers
- **Temporal memory** - remembers your entire work session and progress flow
- **Real-time encouragement** - celebrates progress as it happens: "Perfect! You're doing great!"
- **Detailed tool lists** - "You need: screwdriver, wrench, safety glasses"

### **🎯 The Result:**
**Confidence instead of frustration. Flowing guidance instead of fragmented instructions. Natural mentoring instead of robotic responses. Intelligent memory that never forgets where you are.**

## 🌍 **Universal Application**

This system is designed to help with:
- **🍳 Cooking** - From basic meals to complex recipes
- **🔧 Repairs** - Electronics, appliances, vehicles
- **🪑 Assembly** - Furniture, electronics, DIY projects  
- **📚 Learning** - New skills, hobbies, techniques
- **🏠 Home improvement** - Installation, maintenance, decoration
- **🎨 Creative projects** - Art, crafts, building

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