# 🎯 VQA Test Result Format Documentation

## 📊 **Result Structure Overview**

### **Question-Image Reference System**
Each VQA test result contains complete question-image reference information:

```json
{
  "test_metadata": {
    "test_date": "2025-07-18 22:21:26",
    "test_mode": "coco",
    "num_questions": 20,
    "framework_version": "unified_v1.1"
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
          "ground_truth": "no",
          "is_correct": false,
          "vqa_accuracy": 0.0,
          "inference_time": 4.23
        }
      ]
    }
  }
}
```

## 🔗 **Reference Relationship**

### **Question ID → Image ID → Filename**
```
Question ID: 100187002  (VQA question unique identifier)
     ↓
Image ID: 100187       (COCO image identifier)
     ↓
Filename: COCO_val2014_000000100187.jpg  (Actual image file)
```

### **Image File Location**
- **Path**: `testing_material/vqa2/images/val2014_sample/`
- **Format**: `COCO_val2014_000000100187.jpg` (12-digit zero-padded)

## 📋 **Field Descriptions**

### **Question Result Fields**
| Field | Type | Description |
|-------|------|-------------|
| `question_id` | int | Unique question ID in VQA dataset |
| `image_id` | int | Corresponding COCO image ID |
| `image_filename` | str | Image filename |
| `question` | str | Question text |
| `model_answer` | str | Model response |
| `ground_truth` | str | Ground truth answer |
| `is_correct` | bool | Whether answer is correct |
| `vqa_accuracy` | float | Official VQA evaluation accuracy |
| `inference_time` | float | Inference time (seconds) |

### **Model Result Fields**
| Field | Type | Description |
|-------|------|-------------|
| `accuracy` | float | Simple accuracy (correct/total) |
| `vqa_accuracy` | float | Average VQA accuracy |
| `correct` | int | Number of correct answers |
| `total` | int | Total number of questions |
| `avg_time` | float | Average inference time |

## 🎯 **Usage Examples**

### **Find Image for Specific Question**
```python
# Find corresponding image for question ID 100187002
question_id = 100187002

for result in results['moondream2']['question_results']:
    if result['question_id'] == question_id:
        image_file = result['image_filename']
        print(f"Question {question_id} → {image_file}")
        break
```

### **Verify Image File Exists**
```bash
ls testing_material/vqa2/images/val2014_sample/COCO_val2014_000000100187.jpg
```

### **Calculate Model Performance**
```python
# Get model performance metrics
model_results = results['moondream2']
accuracy = model_results['accuracy']
vqa_accuracy = model_results['vqa_accuracy']
avg_time = model_results['avg_time']

print(f"Accuracy: {accuracy:.1%}")
print(f"VQA Accuracy: {vqa_accuracy:.1%}")
print(f"Avg Time: {avg_time:.2f}s")
```

## ✅ **Key Features**

1. **Complete Reference**: Each question has clear image ID and filename
2. **Quick Lookup**: Direct access to image information
3. **Path Transparency**: Clear image file storage location
4. **Debug Friendly**: Easy to verify test results
5. **Performance Metrics**: Comprehensive accuracy and timing data

---

**Version**: unified_v1.1  
**Last Updated**: July 18, 2025
