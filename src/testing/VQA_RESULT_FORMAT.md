# 🎯 VQA Test Result Format Documentation

## 📊 Result File Structure

### 🔍 **Question and Image Reference Information**

Each VQA test result now contains complete question-image reference information directly in the question results:

```json
{
  "test_metadata": {
    "image_reference_note": "Each question's image_id corresponds to image_filename, image files are located in testing_material/vqa2/images/val2014_sample/ directory"
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

## 🔗 **Reference Relationship**

### **Question ID → Image ID → Filename**
```
Question ID: 100187002  (VQA question unique identifier)
     ↓
Image ID: 100187       (COCO image identifier)
     ↓
Filename: COCO_val2014_000000100187.jpg  (Actual image file)
```

### **Methods to Find Corresponding Images**

1. **Search by Question ID:**
   - Find `question_id` in `question_results`
   - Check corresponding `image_id` and `image_filename`

2. **Direct image access:**
   ```bash
   # Image file location
   testing_material/vqa2/images/val2014_sample/COCO_val2014_000000100187.jpg
   ```

## 📋 **Detailed Field Description**

### **Question Result Fields**
- `question_id`: Unique question ID in VQA dataset
- `image_id`: Corresponding COCO image ID  
- `image_filename`: Image filename
- `question`: Question text
- `model_answer`: Model response
- `ground_truth`: Ground truth answer
- `is_correct`: Whether the answer is correct
- `vqa_accuracy`: Official VQA evaluation accuracy
- `inference_time`: Inference time (seconds)

### **Image File Path**
All image files are stored in:
- `testing_material/vqa2/images/val2014_sample/` directory
- Filename format: `COCO_val2014_000000100187.jpg` (12-digit zero-padded)

## 🎯 **Usage Examples**

### **Find image for specific question:**
```python
# Find corresponding image for question ID 100187002
question_id = 100187002

# Find this question in results
for result in results['moondream2']['question_results']:
    if result['question_id'] == question_id:
        image_file = result['image_filename']
        print(f"Question {question_id} corresponds to image: {image_file}")
        break
```

### **Verify image file exists:**
```bash
ls testing_material/vqa2/images/val2014_sample/COCO_val2014_000000100187.jpg
```

## ✅ **New Version Advantages**

1. **Complete reference information**: Each question has clear image ID and filename
2. **Quick lookup**: Direct access to image information in question results
3. **Path transparency**: Clear indication of image file storage location
4. **Debug friendly**: Easy to check and verify test results

---
**Version Info**: framework_version "unified_v1.1" supports complete image reference information
