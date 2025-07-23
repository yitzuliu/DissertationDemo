# 🚀 AI Manual Assistant - 模型快速啟動指南

## 📋 系統狀態

✅ **後端系統**: 已修復並準備就緒  
✅ **配置系統**: 已統一並驗證通過  
✅ **模型啟動器**: 已創建統一啟動介面  
✅ **依賴檢查**: 自動檢查所有必需依賴  

## 🎯 推薦模型

### 🏆 生產環境推薦
```bash
# 最佳整體性能 (66.0% VQA準確率)
python src/models/model_launcher.py --model smolvlm2_500m_video_optimized

# 最快推理速度 (4.06秒平均響應)
python src/models/model_launcher.py --model moondream2_optimized
```

### 🧪 開發測試推薦
```bash
# 詳細分析能力
python src/models/model_launcher.py --model phi3_vision_optimized

# 輕量級測試
python src/models/model_launcher.py --model moondream2
```

## 🛠️ 使用方式

### 1. 查看所有可用模型
```bash
python src/models/model_launcher.py --list
```

### 2. 檢查模型狀態
```bash
python src/models/model_launcher.py --status smolvlm2_500m_video_optimized
```

### 3. 啟動模型服務器
```bash
# 使用默認端口 8080
python src/models/model_launcher.py --model smolvlm2_500m_video_optimized

# 使用自定義端口
python src/models/model_launcher.py --model moondream2_optimized --port 8081

# 跳過依賴檢查 (加快啟動)
python src/models/model_launcher.py --model smolvlm2_500m_video_optimized --no-deps-check
```

## 🔧 完整系統啟動流程

### 步驟 1: 啟動模型服務器
```bash
# 終端 1: 啟動推薦的模型
python src/models/model_launcher.py --model smolvlm2_500m_video_optimized
```

### 步驟 2: 啟動後端服務器
```bash
# 終端 2: 啟動後端
python src/backend/main.py
```

### 步驟 3: 啟動前端服務器
```bash
# 終端 3: 啟動前端
cd src/frontend && python -m http.server 5500
```

### 步驟 4: 訪問應用
```
瀏覽器訪問: http://localhost:5500
```

## 📊 模型性能對比

| 模型 | VQA準確率 | 推理時間 | 記憶體使用 | 推薦場景 |
|------|-----------|----------|------------|----------|
| **SmolVLM2-Optimized** | 🏆 66.0% | 6.61s | 2.08GB | 生產環境 |
| **SmolVLM** | 64.0% | 5.98s | 1.58GB | 通用使用 |
| **Moondream2-Optimized** | 56.0% | 🏆 4.06s | 🏆 0.10GB | 快速響應 |
| **Phi3-Vision-Optimized** | 60.0% | 13.61s | 1.53GB | 詳細分析 |
| **LLaVA-MLX** | ⚠️ 34.0% | 17.86s | 1.16GB | 不推薦 |

## 🔍 故障排除

### 常見問題

#### 1. 模型啟動失敗
```bash
# 檢查依賴
python src/models/model_launcher.py --status [model_name]

# 檢查配置
python src/config/validate_model_configs.py
```

#### 2. 端口衝突
```bash
# 使用不同端口
python src/models/model_launcher.py --model [model_name] --port 8081
```

#### 3. 記憶體不足
```bash
# 使用輕量級模型
python src/models/model_launcher.py --model moondream2_optimized
```

#### 4. 依賴缺失
```bash
# 安裝依賴
pip install -r requirements.txt

# MLX 依賴 (Apple Silicon)
pip install mlx-vlm
```

### 日誌檢查
```bash
# 檢查應用日誌
tail -f logs/app_*.log

# 檢查模型日誌
tail -f logs/model_*.log
```

## 🎯 測試驗證

### 1. 快速功能測試
```bash
# VQA 快速測試 (10題)
python src/testing/vqa/vqa_test.py --questions 10 --models smolvlm2

# 性能測試
python src/testing/vlm/vlm_tester.py smolvlm2_500m_video_optimized
```

### 2. API 測試
```bash
# 健康檢查
curl http://localhost:8080/health

# 後端狀態
curl http://localhost:8000/status
```

## 📈 性能優化建議

### Apple Silicon 用戶
- 優先使用 MLX 優化版本 (phi3_vision_optimized, llava_mlx)
- 啟用 MPS 加速

### 記憶體受限環境
- 使用 moondream2_optimized (僅需 0.10GB)
- 啟用 half_precision 模式

### 速度優先場景
- 使用 moondream2_optimized (4.06秒響應)
- 跳過圖像預處理

### 準確率優先場景
- 使用 smolvlm2_500m_video_optimized (66.0% VQA準確率)
- 啟用圖像增強處理

## 🔄 模型切換

### 熱切換 (無需重啟後端)
1. 停止當前模型服務器 (Ctrl+C)
2. 啟動新模型服務器
3. 後端會自動連接到新模型

### 配置切換
```bash
# 更新活躍模型配置
# 編輯 src/config/app_config.json
{
  "active_model": "moondream2_optimized"
}
```

## 📚 進階使用

### 自定義配置
```bash
# 複製模板配置
cp src/config/model_configs/template.json src/config/model_configs/my_model.json

# 編輯配置文件
# 添加到 model_launcher.py 的 model_runners 字典
```

### 批量測試
```bash
# 測試所有模型
python src/testing/vqa/vqa_test.py --questions 5 --models smolvlm2 moondream2 phi3_vision
```

### 性能監控
```bash
# 實時監控
watch -n 1 'curl -s http://localhost:8080/health | jq'
```

---

## 🎉 總結

現在你有了一個完全統一和系統化的模型啟動系統：

✅ **統一啟動器**: 一個命令啟動任何模型  
✅ **配置驗證**: 自動檢查配置一致性  
✅ **依賴管理**: 自動檢查和提示缺失依賴  
✅ **狀態監控**: 實時檢查模型和服務狀態  
✅ **錯誤處理**: 完善的錯誤提示和恢復機制  

**立即開始使用:**
```bash
python src/models/model_launcher.py --model smolvlm2_500m_video_optimized
```

享受統一、高效的AI視覺助手開發體驗！ 🚀