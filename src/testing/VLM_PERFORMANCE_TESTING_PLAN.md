# VLM 模型測試計劃
## 📋 測試目標

對 5 個視覺語言模型進行簡單測試，記錄基本性能指標和回應結果。使用 MacBook Air M3 (16GB) 環境，每個模型測試 10-20 張圖片。

## 🎯 測試模型列表

1. **SmolVLM2-500M-Video-Instruct** → `HuggingFaceTB/SmolVLM2-500M-Video-Instruct`
2. **SmolVLM-500M-Instruct** → `HuggingFaceTB/SmolVLM-500M-Instruct`
3. **Moondream2** → `vikhyatk/moondream2`
4. **llava-hf/llava-1.5-7b-hf** → `llava-hf/llava-1.5-7b-hf`
5. **Phi-3.5-Vision-Instruct** → `microsoft/Phi-3.5-vision-instruct`

> 載入方式請參考 `active_model.md`

## 📊 記錄的測試指標

### ⏱️ **時間指標**
- **模型載入時間**: 載入模型需要多長時間
- **推理時間**: 每張圖片處理時間
- **總測試時間**: 完整測試所需時間

### 💾 **記憶體指標**  
- **載入前記憶體**: 載入模型前的記憶體使用
- **載入後記憶體**: 載入模型後的記憶體使用
- **記憶體差值**: 模型佔用的記憶體大小

### 📝 **結果記錄**
- **模型回應**: 對每張圖片的完整回應文字
- **圖片資訊**: 圖片檔名、大小、解析度
- **錯誤記錄**: 如果出現錯誤的詳細資訊

## 📸 測試設定

### **📏 統一測試條件** ✨
為確保公平比較，所有模型使用統一的測試條件：

- **🖼️ 圖像預處理**: 統一縮放至最大 1024 像素，保持長寬比
- **💬 提示詞**: 所有模型使用相同提示詞
- **⚙️ 生成參數**: `max_new_tokens: 100, do_sample: false`
- **🏷️ 圖像格式**: 本地圖像使用 `{"type": "image", "image": image}` 格式

### **測試圖像**
- 圖像放置位置：`src/testing/testing_material/images/`
- 數量：根據可用圖像數量
- 格式：支援 JPG、PNG 等常見格式
- 處理：自動縮放至統一尺寸

### **測試提示詞**
使用統一的提示詞對所有圖像進行測試：
```
"Describe what you see in this image in detail."
```

## 🛠️ 實施檔案

### 📁 **簡單檔案結構**
```
src/testing/
├── VLM_PERFORMANCE_TESTING_PLAN.md     # 測試規劃
├── vlm_tester.py                        # 主要測試程式
├── testing_material/
│   └── images/                          # 測試圖片 (您提供)
└── results/
    └── test_results.json                # 測試結果記錄
```

### 🔧 **主程式功能**
`vlm_tester.py` 將包含：
- **逐一載入模型**（避免記憶體溢出）
- **完整測試後釋放模型記憶體**
- 讀取測試圖片
- 記錄時間和記憶體使用
- 儲存所有結果到 JSON 檔案

### ⚠️ **記憶體管理策略** ✨
由於 M3 MacBook Air 16GB 記憶體限制：
1. **逐一載入**: 一次只載入一個模型
2. **完整測試**: 完成該模型的所有圖片測試
3. **記憶體清理**: `del model, gc.collect(), torch.mps.empty_cache()`
4. **載入下一個**: 清理後載入下一個模型

### ⏱️ **超時機制** ✨
針對不同模型的技術特性設置合理超時：
- **小模型** (SmolVLM 系列, Moondream2): 60秒
- **中型模型** (Phi-3.5-Vision): 120秒  
- **大模型** (LLaVA-v1.5-7B): 180秒

### 🔧 **已知限制** ✨
- **LLaVA-v1.5-7B**: 在 CPU 上推理速度極慢，可能超時
- **Phi-3.5-Vision**: 載入時間較長，推理可能超時
- **Moondream2**: 使用特殊 API，無法完全統一參數控制

## 📋 實施步驟

1. **建立測試程式** - 寫一個 `vlm_tester.py`
2. **測試模型載入** - 確認所有 5 個模型都能正常載入
3. **執行測試** - 對所有圖片進行測試
4. **記錄結果** - 所有資料儲存到 JSON 檔案

## 📊 結果格式 ✨

測試結果將以 JSON 格式儲存，包含統一測試標記：

```json
{
  "test_timestamp": "2025-01-XX XX:XX:XX",
  "system_info": {
    "device": "MacBook Air M3",
    "memory": "16GB",
    "mps_available": true
  },
  "models": {
    "model_name": {
      "model_id": "actual/model/path",
      "load_time": 10.5,
      "memory_before": 8.2,
      "memory_after": 12.8,
      "memory_diff": 4.6,
      "memory_after_cleanup": 8.5,
      "successful_inferences": 3,
      "failed_inferences": 0,
      "avg_inference_time": 6.2,
      "images": {
        "image1.jpg": {
          "inference_time": 2.1,
          "response": "詳細回應文字...",
          "image_info": {
            "original_size": [1920, 1080],
            "processed_size": [1024, 576],
            "mode": "RGB",
            "file_size": 245760
          },
          "error": null,
          "unified_test": true,
          "generation_params": {
            "max_new_tokens": 100,
            "do_sample": false
          },
          "timeout_used": 60
        }
      }
    }
  }
}
```

## 🏆 實際測試結果 ✨

### ✅ **成功的模型 (3/5)**
| 排名 | 模型 | 載入時間 | 推理時間 | 成功率 |
|------|------|----------|----------|--------|
| 🥇 | **Moondream2** | 5.39s | **5.94s** | 100% |
| 🥈 | **SmolVLM-500M-Instruct** | 3.86s | **11.86s** | 100% |
| 🥉 | **SmolVLM2-500M-Video** | 2.53s | **15.36s** | 100% |

### ❌ **超時的模型 (2/5)**
- **LLaVA-v1.5-7B**: CPU 推理超時（180秒）
- **Phi-3.5-Vision**: 推理複雜度高，超時（120秒）

### 📝 **關鍵發現**
1. **小模型優勢明顯**: 500M 參數的模型在 M3 上表現最佳
2. **Moondream2 領先**: 推理速度和載入速度平衡最好
3. **大模型限制**: 7B+ 參數模型需要 GPU 加速
4. **統一測試成功**: 實現了公平的比較條件

## ✅ 使用方法

1. **單模型測試**: `python vlm_tester.py "模型名稱"`
2. **全部測試**: `python vlm_tester.py`
3. **查看結果**: 檢查 `results/` 目錄中的 JSON 文件 