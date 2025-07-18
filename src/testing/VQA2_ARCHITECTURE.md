## 🎯 VQA 2.0 測試架構整理總結

### 📁 **核心文件結構**
```
src/testing/
├── vqa_framework.py      # VQA 2.0 核心框架（完整功能）
├── vqa_test.py          # VQA 測試啟動器（命令行界面）
├── example_vqa2_results.py  # 結果格式說明文檔
└── run_vqa2.py          # 簡化啟動器（可選）
```

### 🚀 **快速使用方法**

#### **使用 vqa_test.py（統一使用COCO真實數據）**
```bash
# COCO真實數據測試（默認模式）
python vqa_test.py --questions 20

# 測試特定模型
python vqa_test.py --models moondream2 --questions 10

# 測試多個模型
python vqa_test.py --models moondream2 smolvlm_instruct --questions 15

# 快速測試（使用--quick參數，效果相同）
python vqa_test.py --quick --questions 20
```

#### **方法2：使用 run_vqa2.py（簡化版）**
```bash
# 快速演示
python run_vqa2.py --demo

# 快速測試
python run_vqa2.py --quick

# 查看結果格式說明
python run_vqa2.py --explain
```

### 🖼️ **COCO 圖像使用說明**

框架會自動使用這20張真實COCO val2014圖像：
```
圖像ID: 139, 285, 632, 724, 776, 785, 802, 872, 885, 1000,
       1268, 1296, 1353, 1584, 1818, 2006, 2149, 2153, 2157, 2261

文件格式: COCO_val2014_000000000139.jpg (etc.)
存放路徑: testing_material/vqa2/images/val2014_sample/
```

### 🤖 **支持的模型**
- `moondream2` - 最快，輕量級（推薦測試）
- `smolvlm_instruct` - 500M參數，平衡性能
- `smolvlm_v2_instruct` - 視頻優化版本
- `llava_mlx` - 7B模型，較大但性能好
- `phi35_vision` - Microsoft模型

### 📊 **測試流程**
1. **自動下載數據**：框架會自動下載VQA 2.0數據集和COCO圖像
2. **模型載入**：按需載入指定的VLM模型
3. **問答測試**：對每張圖像提出VQA問題
4. **結果評估**：計算準確度和VQA準確度
5. **結果保存**：保存到 `results/` 目錄

### 🎯 **測試結果**
- **簡單準確度**：基本的正確/錯誤統計
- **VQA準確度**：官方VQA評估方法（考慮多標註者一致性）
- **推理時間**：每個問題的平均處理時間
- **詳細結果**：每個問題的具體回答和評分

### 📁 **輸出文件**
```
results/
├── vqa2_results_coco_20250718_123456.json    # 完整測試結果
└── （結果文件以時間戳命名）
```

### 🔧 **故障排除**
1. **網絡問題**：首次運行需要下載數據，確保網絡連接
2. **記憶體不足**：建議使用較小模型（moondream2）
3. **模型載入失敗**：檢查模型ID和網絡連接
4. **圖像下載失敗**：框架會創建佔位符圖像繼續測試

### ✨ **特色功能**
- **自動化程度高**：一鍵運行完整測試
- **真實數據**：使用官方VQA 2.0數據集和COCO圖像
- **多模型支持**：可同時測試多個VLM模型
- **詳細分析**：提供完整的性能分析和錯誤統計
- **記憶體優化**：自動清理模型記憶體，避免溢出

### 📈 **預期表現**
根據之前的測試結果：
- **Moondream2**: ~60-80% VQA準確度，推理速度最快
- **SmolVLM**: ~60-70% VQA準確度，平衡性能
- **LLaVA**: ~50-70% VQA準確度，較大模型但性能穩定

---
**使用建議**：統一使用COCO真實數據，推薦運行 `python vqa_test.py --questions 5` 進行快速驗證。
