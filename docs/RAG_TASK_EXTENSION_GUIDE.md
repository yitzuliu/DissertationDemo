# RAG 系統任務擴展指南

## 📋 概述

本指南說明如何在 Vision Intelligence Hub 的 RAG (Retrieval-Augmented Generation) 系統中添加新的任務知識，**無需修改任何系統代碼**。

## 🎯 核心特性

### **即插即用設計**
- ✅ 自動掃描 `data/tasks` 目錄
- ✅ 自動載入所有 YAML 任務文件
- ✅ 自動生成向量嵌入
- ✅ 自動整合到搜索系統
- ✅ 無需重啟系統（支持熱重載）

### **零代碼修改**
- 不需要修改 RAG 系統源代碼
- 不需要重新編譯或部署
- 只需要添加 YAML 文件即可

## 📁 文件結構

```
data/tasks/
├── coffee_brewing.yaml      # 咖啡沖泡任務（示例）
├── daily_journaling.yaml    # 日記撰寫任務（示例）
├── cooking_pasta.yaml       # 煮義大利麵任務
├── meditation.yaml          # 冥想練習任務
└── [your_task].yaml         # 您的自定義任務
```

## 📝 YAML 任務文件格式

### **基本結構**

```yaml
# 任務基本信息
task_name: "your_task_name"
display_name: "顯示名稱"
description: "任務描述"
estimated_total_duration: "預計總時間"
difficulty_level: "難度等級"

# 任務元數據
metadata:
  category: "任務類別"
  tags: ["標籤1", "標籤2"]
  prerequisites: ["前置條件"]
  safety_level: "安全等級"

# 步驟定義
steps:
  - step_id: 1
    title: "步驟標題"
    task_description: "步驟描述"
    tools_needed: ["工具1", "工具2"]
    completion_indicators: ["完成指標1", "完成指標2"]
    visual_cues: ["視覺線索1", "視覺線索2"]
    estimated_duration: "預計時間"
    safety_notes: ["安全注意事項"]

# 全局安全注意事項
global_safety_notes:
  - "全局安全注意事項1"
  - "全局安全注意事項2"

# 任務完成指標
task_completion_indicators:
  - "任務完成指標1"
  - "任務完成指標2"
```

### **字段說明**

| 字段 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `task_name` | string | ✅ | 任務唯一標識符（英文，小寫，下劃線） |
| `display_name` | string | ✅ | 用戶友好的顯示名稱 |
| `description` | string | ✅ | 任務的詳細描述 |
| `estimated_total_duration` | string | ❌ | 預計總時間（如："15-30 minutes"） |
| `difficulty_level` | string | ❌ | 難度等級（如："beginner", "intermediate", "advanced"） |
| `metadata` | object | ❌ | 任務元數據 |
| `steps` | array | ✅ | 任務步驟列表 |
| `global_safety_notes` | array | ❌ | 全局安全注意事項 |
| `task_completion_indicators` | array | ❌ | 任務完成指標 |

### **步驟字段說明**

| 字段 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `step_id` | integer | ✅ | 步驟編號（從1開始） |
| `title` | string | ✅ | 步驟標題 |
| `task_description` | string | ✅ | 步驟詳細描述 |
| `tools_needed` | array | ✅ | 需要的工具列表 |
| `completion_indicators` | array | ✅ | 完成指標列表 |
| `visual_cues` | array | ✅ | 視覺線索列表 |
| `estimated_duration` | string | ❌ | 預計時間 |
| `safety_notes` | array | ❌ | 安全注意事項 |

## 🔧 創建新任務的步驟

### **步驟 1：準備任務信息**
1. 確定任務名稱和描述
2. 分解任務為具體步驟
3. 識別每個步驟的工具需求
4. 定義完成指標和視覺線索
5. 考慮安全注意事項

### **步驟 2：創建 YAML 文件**
1. 在 `data/tasks/` 目錄創建新的 `.yaml` 文件
2. 使用 `task_name` 作為文件名（不含擴展名）
3. 按照上述格式編寫任務內容

### **步驟 3：驗證文件格式**
```bash
# 檢查 YAML 語法
python -c "import yaml; yaml.safe_load(open('data/tasks/your_task.yaml'))"
```

### **步驟 4：測試任務載入**
```python
from src.memory.rag.task_loader import TaskKnowledgeLoader

# 創建任務載入器
loader = TaskKnowledgeLoader()

# 載入新任務
task = loader.load_task("your_task_name")
print(f"Task loaded: {task.display_name}")
print(f"Steps: {task.get_total_steps()}")
```

## 📊 示例：日記撰寫任務

### **文件：`data/tasks/daily_journaling.yaml`**

```yaml
task_name: "daily_journaling"
display_name: "Writing a Daily Journal Entry"
description: "Complete process of writing a meaningful daily journal entry"
estimated_total_duration: "15-30 minutes"
difficulty_level: "beginner"

metadata:
  category: "personal_development"
  tags: ["journaling", "reflection", "planning"]
  prerequisites: ["basic_writing_skills"]
  safety_level: "no_risk"

steps:
  - step_id: 1
    title: "Prepare Journaling Environment"
    task_description: "Create a comfortable environment for journaling"
    tools_needed: ["journal_notebook", "pen_or_pencil", "quiet_space"]
    completion_indicators: ["journal_and_pen_ready", "comfortable_seating_arranged"]
    visual_cues: ["journal_notebook", "writing_pen", "comfortable_chair"]
    estimated_duration: "2-3 minutes"
    safety_notes: ["ensure_comfortable_posture"]

  - step_id: 2
    title: "Set Intention and Date"
    task_description: "Write the date and set your intention"
    tools_needed: ["journal_notebook", "pen_or_pencil"]
    completion_indicators: ["current_date_written", "session_intention_set"]
    visual_cues: ["date_written_in_journal", "intention_statement"]
    estimated_duration: "1-2 minutes"

# ... 更多步驟

global_safety_notes:
  - "journaling_is_a_safe_space_for_self_expression"
  - "be_honest_and_authentic_with_yourself"

task_completion_indicators:
  - "complete_journal_entry_written"
  - "emotional_state_processed"
  - "insights_gained"
```

## 🔍 系統自動化機制

### **自動掃描**
```python
# 系統啟動時自動執行
yaml_files = list(self.tasks_directory.glob("*.yaml")) + list(self.tasks_directory.glob("*.yml"))
for file_path in yaml_files:
    task_name = file_path.stem  # 自動提取文件名
    task_knowledge = self.load_task(task_name, file_path)
```

### **自動向量化**
```python
# 自動添加到向量搜索引擎
for task_name, task in self.loaded_tasks.items():
    self.vector_engine.add_task_knowledge(task)
```

### **自動搜索整合**
- 系統會自動在所有任務中搜索匹配的步驟
- 支持跨任務的語義搜索
- 自動提供相關的任務建議

## 🧪 測試和驗證

### **驗證任務載入**
```python
from src.memory.rag.knowledge_base import RAGKnowledgeBase

# 初始化知識庫
kb = RAGKnowledgeBase()
kb.initialize()

# 檢查載入的任務
tasks = kb.get_all_tasks()
print(f"Loaded tasks: {tasks}")

# 檢查特定任務
if "your_task_name" in tasks:
    summary = kb.get_task_summary("your_task_name")
    print(f"Task summary: {summary}")
```

### **測試任務搜索**
```python
# 測試視覺線索匹配
result = kb.find_matching_step("我看到一本日記本")
print(f"Matched task: {result.task_name}")
print(f"Matched step: {result.step_id}")
print(f"Similarity: {result.similarity}")
```

### **測試步驟查詢**
```python
# 獲取步驟詳情
step_details = kb.get_step_details("your_task_name", 1)
print(f"Step details: {step_details}")

# 獲取下一個步驟
next_step = kb.get_next_step_info("your_task_name", 1)
print(f"Next step: {next_step}")
```

## 🚀 最佳實踐

### **任務設計原則**
1. **清晰性**：每個步驟的描述要清晰明確
2. **完整性**：涵蓋所有必要的工具和指標
3. **安全性**：包含適當的安全注意事項
4. **視覺性**：提供豐富的視覺線索
5. **實用性**：確保步驟在實際中可執行

### **命名規範**
- `task_name`：使用英文，小寫，下劃線分隔
- `display_name`：使用用戶友好的名稱
- `visual_cues`：使用具體的視覺描述
- `tools_needed`：使用標準化的工具名稱

### **文件組織**
- 每個任務一個 YAML 文件
- 文件名與 `task_name` 一致
- 保持文件結構的一致性
- 添加適當的註釋

## 🔧 故障排除

### **常見問題**

#### **1. 任務未載入**
- 檢查 YAML 語法是否正確
- 確認文件在 `data/tasks/` 目錄中
- 檢查 `task_name` 是否唯一

#### **2. 搜索結果不準確**
- 檢查 `visual_cues` 是否具體
- 確保 `completion_indicators` 明確
- 驗證步驟描述是否清晰

#### **3. 系統性能問題**
- 檢查任務步驟數量（建議 < 20 步）
- 優化 `visual_cues` 數量
- 考慮使用向量優化器

### **調試工具**
```python
# 獲取系統統計信息
stats = kb.get_system_stats()
print(f"System stats: {stats}")

# 健康檢查
health = kb.health_check()
print(f"Health check: {health}")

# 清除緩存（如果需要）
kb.clear_all_caches()
```

## 📈 性能考慮

### **優化建議**
1. **步驟數量**：每個任務建議 5-15 個步驟
2. **視覺線索**：每個步驟 3-8 個視覺線索
3. **文件大小**：單個 YAML 文件 < 50KB
4. **任務總數**：系統支持數百個任務

### **監控指標**
- 任務載入時間
- 搜索響應時間
- 向量匹配準確率
- 記憶體使用量

## 🔮 未來擴展

### **計劃中的功能**
- 動態任務重載
- 任務版本管理
- 任務依賴關係
- 用戶自定義任務
- 任務性能分析

### **API 擴展**
- RESTful 任務管理 API
- 任務模板系統
- 批量任務導入
- 任務導出功能

## 📚 參考資源

- [YAML 語法指南](https://yaml.org/spec/)
- [RAG 系統架構文檔](./PROJECT_STRUCTURE.md)
- [任務驗證工具](../src/memory/rag/validation.py)
- [性能測試套件](../src/memory/rag/performance_tester.py)

---

**注意**：本指南基於當前系統版本。如有更新，請參考最新的系統文檔。 