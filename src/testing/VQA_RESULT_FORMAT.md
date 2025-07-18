# 🎯 VQA測試結果格式說明

## 📊 結果文件結構

### 🔍 **問題和圖像對照信息**

每個VQA測試結果現在包含完整的問題-圖像對照信息，直接在問題結果中：

```json
{
  "test_metadata": {
    "image_reference_note": "每個問題的 image_id 對應 image_filename，圖像文件位於 testing_material/vqa2/images/val2014_sample/ 目錄"
  },
  "results": {
    "moondream2": {
      "question_results": [
        {
          "question_id": 100187002,
          "image_id": 100187,
          "image_filename": "COCO_val2014_000000100187.jpg",
          "question": "Is it daytime?",
          "model_answer": "Yes",
          "ground_truth": "no"
        }
      ]
    }
  }
}
```

## 🔗 **對照關係說明**

### **Question ID → Image ID → 文件名**
```
Question ID: 100187002  （VQA問題唯一標識符）
     ↓
Image ID: 100187       （COCO圖像標識符）
     ↓
文件名: COCO_val2014_000000100187.jpg  （實際圖像文件）
```

### **查找對應圖像的方法**

1. **通過問題ID查找：**
   - 在 `question_results` 中找到 `question_id`
   - 查看對應的 `image_id` 和 `image_filename`

2. **直接查看圖像：**
   ```bash
   # 圖像文件位置
   testing_material/vqa2/images/val2014_sample/COCO_val2014_000000100187.jpg
   ```

## 📋 **詳細字段說明**

### **問題結果字段**
- `question_id`: VQA數據集中的問題唯一ID
- `image_id`: 對應的COCO圖像ID  
- `image_filename`: 圖像文件名
- `question`: 問題文本
- `model_answer`: 模型回答
- `ground_truth`: 標準答案
- `is_correct`: 是否回答正確
- `vqa_accuracy`: VQA官方評估準確度
- `inference_time`: 推理時間（秒）

### **圖像文件路徑**
所有圖像文件統一存放在：
- `testing_material/vqa2/images/val2014_sample/` 目錄
- 文件名格式：`COCO_val2014_000000100187.jpg`（12位數字補零）

## 🎯 **使用示例**

### **查找特定問題的圖像：**
```python
# 假設要查找問題ID 100187002的對應圖像
question_id = 100187002

# 在結果中找到這個問題
for result in results['moondream2']['question_results']:
    if result['question_id'] == question_id:
        image_file = result['image_filename']
        print(f"問題 {question_id} 對應圖像: {image_file}")
        break
```

### **驗證圖像文件存在：**
```bash
ls testing_material/vqa2/images/val2014_sample/COCO_val2014_000000100187.jpg
```

## ✅ **新版本優勢**

1. **完整對照信息**：每個問題都有明確的圖像ID和文件名
2. **快速查找**：圖像對照表提供集中的圖像信息
3. **路徑透明**：明確顯示圖像文件的存放位置
4. **調試友好**：便於檢查和驗證測試結果

---
**版本信息**：framework_version "unified_v1.1" 開始支持完整圖像對照信息
