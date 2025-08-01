# RAG 系統運作技術文檔

## 📋 概述

本文檔詳細說明 Vision Intelligence Hub 中 RAG (Retrieval-Augmented Generation) 系統的完整運作機制，包括系統架構、工作流程、匹配策略和回應生成。

## 🏗️ 系統架構

### **核心組件**

```
RAG 系統架構
├── 📁 數據層 (Data Layer)
│   ├── data/tasks/          # 任務知識文件
│   ├── cache/embeddings/    # 向量緩存
│   └── cache/embeddings_optimizer/  # 優化緩存
│
├── 🔧 處理層 (Processing Layer)
│   ├── TaskKnowledgeLoader  # 任務載入器
│   ├── ChromaVectorSearchEngine  # 向量搜索引擎
│   ├── VectorOptimizer      # 向量優化器
│   └── Validation          # 數據驗證
│
├── 🎯 邏輯層 (Logic Layer)
│   ├── RAGKnowledgeBase    # 知識庫核心
│   ├── MatchResult         # 匹配結果
│   └── SearchStrategy      # 搜索策略
│
└── 🌐 接口層 (Interface Layer)
    ├── State Tracker       # 狀態追蹤器
    ├── VLM Integration     # VLM 集成
    └── Response Generator  # 回應生成器
```

### **數據流圖**

```
用戶觀察 → VLM 處理 → RAG 匹配 → 回應生成
    ↓           ↓          ↓          ↓
視覺輸入   文本描述   向量搜索   智能回應
    ↓           ↓          ↓          ↓
圖像數據   觀察文本   相似度計算   指導內容
```

## 🔄 完整工作流程

### **階段 1：系統初始化**

#### **1.1 任務載入**
```python
# 自動掃描 data/tasks/ 目錄
yaml_files = list(self.tasks_directory.glob("*.yaml")) + list(self.tasks_directory.glob("*.yml"))

for file_path in yaml_files:
    task_name = file_path.stem  # 提取文件名（不含擴展名）
    task_knowledge = self.load_task(task_name, file_path)
    self.loaded_tasks[task_name] = task_knowledge
```

#### **1.2 向量化處理**
```python
# 為每個任務步驟生成向量嵌入
for task_name, task in self.loaded_tasks.items():
    for step in task.steps:
        # 組合步驟信息
        step_text = f"{step.title} {step.task_description} {' '.join(step.visual_cues)}"
        
        # 生成向量嵌入
        embedding = self.vector_engine.encode_text(step_text)
        
        # 存儲到向量數據庫
        self.vector_engine.add_document(
            task_name=task_name,
            step_id=step.step_id,
            text=step_text,
            embedding=embedding
        )
```

#### **1.3 緩存優化**
```python
# 預計算所有嵌入並緩存
if precompute_embeddings:
    self.vector_optimizer.precompute_all_embeddings(self.loaded_tasks)
```

### **階段 2：觀察處理**

#### **2.1 VLM 視覺分析**
```python
# VLM 處理視覺輸入
def process_visual_observation(image_data):
    # 1. 圖像預處理
    processed_image = preprocess_image(image_data)
    
    # 2. VLM 分析
    observation_text = vlm_model.analyze(processed_image)
    
    # 3. 文本清理和標準化
    cleaned_observation = clean_and_normalize_text(observation_text)
    
    return cleaned_observation
```

#### **2.2 觀察文本生成**
```python
# 生成結構化的觀察描述
observation_data = {
    "raw_text": observation_text,
    "visual_elements": extract_visual_elements(observation_text),
    "actions": extract_actions(observation_text),
    "objects": extract_objects(observation_text),
    "context": extract_context(observation_text)
}
```

### **階段 3：RAG 匹配**

#### **3.1 多層次匹配策略**

##### **優先級 1：精確視覺線索匹配**
```python
def exact_visual_cue_matching(observation, visual_cues):
    """精確視覺線索匹配"""
    matched_cues = []
    for cue in visual_cues:
        if cue.lower() in observation.lower():
            matched_cues.append(cue)
    return matched_cues

# 視覺線索映射表
visual_cue_mapping = {
    "coffee_brewing": {
        "coffee_beans": {"step_id": 1, "confidence": 0.95},
        "grinder": {"step_id": 3, "confidence": 0.90},
        "kettle": {"step_id": 2, "confidence": 0.85},
        "filter_paper": {"step_id": 4, "confidence": 0.88}
    },
    "daily_journaling": {
        "journal_notebook": {"step_id": 1, "confidence": 0.92},
        "writing_pen": {"step_id": 2, "confidence": 0.89},
        "reflective_expression": {"step_id": 3, "confidence": 0.87}
    }
}
```

##### **優先級 2：語義相似度匹配**
```python
def semantic_similarity_matching(observation, task_steps):
    """語義相似度匹配"""
    similarities = []
    
    for task_name, steps in task_steps.items():
        for step in steps:
            # 組合步驟文本
            step_text = f"{step.title} {step.task_description} {' '.join(step.visual_cues)}"
            
            # 計算語義相似度
            similarity = calculate_semantic_similarity(observation, step_text)
            
            similarities.append({
                "task_name": task_name,
                "step_id": step.step_id,
                "similarity": similarity,
                "step_text": step_text
            })
    
    # 按相似度排序
    similarities.sort(key=lambda x: x["similarity"], reverse=True)
    return similarities
```

##### **優先級 3：標籤和類別匹配**
```python
def tag_and_category_matching(observation, task_metadata):
    """標籤和類別匹配"""
    matches = []
    
    for task_name, metadata in task_metadata.items():
        # 檢查標籤匹配
        tag_matches = []
        for tag in metadata.get("tags", []):
            if tag.lower() in observation.lower():
                tag_matches.append(tag)
        
        # 檢查類別匹配
        category = metadata.get("category", "")
        category_match = category.lower() in observation.lower()
        
        if tag_matches or category_match:
            matches.append({
                "task_name": task_name,
                "tag_matches": tag_matches,
                "category_match": category_match,
                "confidence": len(tag_matches) * 0.3 + (1 if category_match else 0) * 0.2
            })
    
    return matches
```

#### **3.2 綜合匹配算法**
```python
def comprehensive_matching(observation, knowledge_base):
    """綜合匹配算法"""
    results = []
    
    # 1. 精確視覺線索匹配
    exact_matches = exact_visual_cue_matching(observation, knowledge_base.visual_cues)
    
    # 2. 語義相似度匹配
    semantic_matches = semantic_similarity_matching(observation, knowledge_base.task_steps)
    
    # 3. 標籤和類別匹配
    tag_matches = tag_and_category_matching(observation, knowledge_base.task_metadata)
    
    # 4. 綜合評分
    for semantic_match in semantic_matches:
        score = semantic_match["similarity"]
        
        # 如果有精確視覺線索匹配，提升分數
        if any(cue in observation for cue in exact_matches):
            score *= 1.5
        
        # 如果有標籤匹配，提升分數
        for tag_match in tag_matches:
            if tag_match["task_name"] == semantic_match["task_name"]:
                score += tag_match["confidence"] * 0.3
        
        results.append({
            **semantic_match,
            "final_score": score
        })
    
    # 按最終分數排序
    results.sort(key=lambda x: x["final_score"], reverse=True)
    return results
```

### **階段 4：回應生成**

#### **4.1 置信度評估**
```python
def evaluate_confidence(match_result):
    """評估匹配置信度"""
    similarity = match_result.similarity
    
    if similarity > 0.8:
        return "high", "🟢 高置信度"
    elif similarity > 0.6:
        return "medium", "🟡 中等置信度"
    elif similarity > 0.4:
        return "low", "🟠 低置信度"
    else:
        return "very_low", "🔴 極低置信度"
```

#### **4.2 回應策略選擇**
```python
def select_response_strategy(confidence_level, match_result):
    """選擇回應策略"""
    
    if confidence_level == "high":
        return generate_detailed_guidance(match_result)
    elif confidence_level == "medium":
        return generate_general_guidance(match_result)
    elif confidence_level == "low":
        return generate_suggestive_guidance(match_result)
    else:
        return generate_inquiry_response(match_result)

def generate_detailed_guidance(match_result):
    """生成詳細指導"""
    step_details = get_step_details(match_result.task_name, match_result.step_id)
    
    return {
        "type": "detailed_guidance",
        "content": {
            "step_title": step_details["title"],
            "description": step_details["task_description"],
            "tools_needed": step_details["tools_needed"],
            "completion_indicators": step_details["completion_indicators"],
            "safety_notes": step_details["safety_notes"],
            "estimated_duration": step_details["estimated_duration"]
        },
        "confidence": match_result.similarity,
        "next_steps": get_next_step_suggestions(match_result)
    }

def generate_general_guidance(match_result):
    """生成一般指導"""
    return {
        "type": "general_guidance",
        "content": {
            "suggested_task": match_result.task_name,
            "suggested_step": match_result.step_id,
            "general_advice": get_general_advice(match_result),
            "alternative_suggestions": get_alternative_suggestions(match_result)
        },
        "confidence": match_result.similarity
    }

def generate_suggestive_guidance(match_result):
    """生成建議性指導"""
    return {
        "type": "suggestive_guidance",
        "content": {
            "possible_tasks": get_possible_tasks(match_result),
            "clarification_questions": generate_clarification_questions(match_result),
            "general_tips": get_general_tips()
        },
        "confidence": match_result.similarity
    }

def generate_inquiry_response(match_result):
    """生成詢問回應"""
    return {
        "type": "inquiry",
        "content": {
            "message": "我需要更多信息來提供準確的指導",
            "questions": [
                "您正在進行什麼類型的活動？",
                "您看到了哪些具體的工具或設備？",
                "您的目標是什麼？"
            ],
            "available_tasks": list_available_tasks()
        },
        "confidence": match_result.similarity
    }
```

## 🎯 匹配機制詳解

### **多層次匹配策略**

#### **層次 1：視覺線索匹配（最高優先級）**
```python
# 視覺線索權重配置
visual_cue_weights = {
    "exact_match": 1.0,      # 精確匹配
    "partial_match": 0.7,    # 部分匹配
    "semantic_match": 0.5,   # 語義匹配
    "category_match": 0.3    # 類別匹配
}

def calculate_visual_cue_score(observation, visual_cues):
    """計算視覺線索匹配分數"""
    score = 0.0
    
    for cue in visual_cues:
        if cue.lower() in observation.lower():
            score += visual_cue_weights["exact_match"]
        elif any(word in observation.lower() for word in cue.lower().split()):
            score += visual_cue_weights["partial_match"]
    
    return min(score, 1.0)  # 限制最大分數為 1.0
```

#### **層次 2：語義相似度匹配**
```python
def calculate_semantic_similarity(text1, text2):
    """計算語義相似度"""
    # 使用預訓練的句子嵌入模型
    embeddings = sentence_transformer.encode([text1, text2])
    
    # 計算餘弦相似度
    similarity = cosine_similarity(
        embeddings[0].reshape(1, -1), 
        embeddings[1].reshape(1, -1)
    )[0][0]
    
    return float(similarity)
```

#### **層次 3：上下文匹配**
```python
def calculate_context_score(observation, task_context):
    """計算上下文匹配分數"""
    context_keywords = {
        "coffee_brewing": ["coffee", "brewing", "drink", "morning", "kitchen"],
        "daily_journaling": ["journal", "writing", "reflection", "personal", "thoughts"]
    }
    
    task_keywords = context_keywords.get(task_context, [])
    matched_keywords = sum(1 for keyword in task_keywords if keyword in observation.lower())
    
    return matched_keywords / len(task_keywords) if task_keywords else 0.0
```

### **綜合評分算法**
```python
def calculate_final_score(observation, match_result):
    """計算最終匹配分數"""
    
    # 基礎語義相似度
    base_similarity = match_result.similarity
    
    # 視覺線索加分
    visual_cue_score = calculate_visual_cue_score(
        observation, 
        get_step_visual_cues(match_result.task_name, match_result.step_id)
    )
    
    # 上下文加分
    context_score = calculate_context_score(
        observation, 
        get_task_category(match_result.task_name)
    )
    
    # 綜合計算
    final_score = (
        base_similarity * 0.6 +      # 語義相似度權重 60%
        visual_cue_score * 0.3 +     # 視覺線索權重 30%
        context_score * 0.1          # 上下文權重 10%
    )
    
    return min(final_score, 1.0)  # 限制最大分數為 1.0
```

## 📊 性能優化

### **向量緩存策略**
```python
class VectorCache:
    def __init__(self, cache_dir):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings_cache = {}
        self.metadata_cache = {}
    
    def get_cached_embedding(self, text_hash):
        """獲取緩存的向量嵌入"""
        cache_file = self.cache_dir / f"{text_hash}.npy"
        if cache_file.exists():
            return np.load(cache_file)
        return None
    
    def cache_embedding(self, text_hash, embedding):
        """緩存向量嵌入"""
        cache_file = self.cache_dir / f"{text_hash}.npy"
        np.save(cache_file, embedding)
        self.embeddings_cache[text_hash] = embedding
```

### **搜索優化**
```python
class OptimizedSearchEngine:
    def __init__(self):
        self.index = None
        self.embeddings = []
        self.metadata = []
    
    def build_index(self, embeddings):
        """構建搜索索引"""
        self.embeddings = np.array(embeddings)
        self.index = faiss.IndexFlatIP(self.embeddings.shape[1])
        self.index.add(self.embeddings.astype('float32'))
    
    def search(self, query_embedding, top_k=5):
        """快速搜索"""
        query_vector = query_embedding.reshape(1, -1).astype('float32')
        similarities, indices = self.index.search(query_vector, top_k)
        
        return [
            {
                "index": int(idx),
                "similarity": float(sim),
                "metadata": self.metadata[idx]
            }
            for idx, sim in zip(indices[0], similarities[0])
        ]
```

## 🔧 配置和調優

### **系統配置參數**
```python
RAG_CONFIG = {
    # 相似度閾值
    "similarity_thresholds": {
        "high_confidence": 0.7,
        "medium_confidence": 0.5,
        "low_confidence": 0.35,
        "minimum_confidence": 0.2
    },
    
    # 搜索參數
    "search_params": {
        "top_k": 5,
        "max_search_time_ms": 100,
        "enable_caching": True,
        "cache_ttl_seconds": 3600
    },
    
    # 向量模型配置
    "vector_model": {
        "name": "all-MiniLM-L6-v2",
        "max_length": 512,
        "normalize_embeddings": True
    },
    
    # 性能配置
    "performance": {
        "precompute_embeddings": True,
        "enable_optimization": True,
        "max_concurrent_searches": 10
    }
}
```

### **性能監控**
```python
class RAGPerformanceMonitor:
    def __init__(self):
        self.metrics = {
            "total_searches": 0,
            "average_search_time": 0.0,
            "cache_hit_rate": 0.0,
            "accuracy_metrics": {}
        }
    
    def record_search(self, search_time, cache_hit, accuracy):
        """記錄搜索性能"""
        self.metrics["total_searches"] += 1
        self.metrics["average_search_time"] = (
            (self.metrics["average_search_time"] * (self.metrics["total_searches"] - 1) + search_time) /
            self.metrics["total_searches"]
        )
        
        # 更新緩存命中率
        if cache_hit:
            self.metrics["cache_hit_rate"] = (
                (self.metrics["cache_hit_rate"] * (self.metrics["total_searches"] - 1) + 1) /
                self.metrics["total_searches"]
            )
    
    def get_performance_report(self):
        """獲取性能報告"""
        return {
            "total_searches": self.metrics["total_searches"],
            "average_search_time_ms": self.metrics["average_search_time"] * 1000,
            "cache_hit_rate_percent": self.metrics["cache_hit_rate"] * 100,
            "performance_grade": self.calculate_performance_grade()
        }
```

## 🧪 測試和驗證

### **單元測試**
```python
def test_rag_matching():
    """測試 RAG 匹配功能"""
    kb = RAGKnowledgeBase()
    kb.initialize()
    
    # 測試用例
    test_cases = [
        {
            "observation": "我看到咖啡豆和磨豆機",
            "expected_task": "coffee_brewing",
            "expected_step": 1,
            "min_confidence": 0.6
        },
        {
            "observation": "用戶拿著日記本準備寫作",
            "expected_task": "daily_journaling",
            "expected_step": 1,
            "min_confidence": 0.6
        }
    ]
    
    for test_case in test_cases:
        result = kb.find_matching_step(test_case["observation"])
        
        assert result.task_name == test_case["expected_task"], \
            f"Expected {test_case['expected_task']}, got {result.task_name}"
        
        assert result.step_id == test_case["expected_step"], \
            f"Expected step {test_case['expected_step']}, got {result.step_id}"
        
        assert result.similarity >= test_case["min_confidence"], \
            f"Confidence {result.similarity} below threshold {test_case['min_confidence']}"
```

### **性能測試**
```python
def test_rag_performance():
    """測試 RAG 性能"""
    kb = RAGKnowledgeBase()
    kb.initialize()
    
    # 性能基準
    performance_targets = {
        "search_time_ms": 100,
        "accuracy_rate": 0.8,
        "memory_usage_mb": 50
    }
    
    # 執行性能測試
    start_time = time.time()
    for _ in range(100):
        result = kb.find_matching_step("測試觀察")
    
    total_time = (time.time() - start_time) * 1000
    avg_time = total_time / 100
    
    assert avg_time <= performance_targets["search_time_ms"], \
        f"Average search time {avg_time}ms exceeds target {performance_targets['search_time_ms']}ms"
```

## 📈 監控和維護

### **健康檢查**
```python
def rag_health_check():
    """RAG 系統健康檢查"""
    health_status = {
        "status": "healthy",
        "issues": [],
        "warnings": [],
        "metrics": {}
    }
    
    try:
        kb = RAGKnowledgeBase()
        kb.initialize()
        
        # 檢查基本功能
        result = kb.find_matching_step("測試觀察")
        if not result:
            health_status["issues"].append("Basic search functionality failed")
        
        # 檢查性能指標
        stats = kb.get_system_stats()
        if stats["vector_engine"]["avg_search_time_ms"] > 100:
            health_status["warnings"].append("Search performance below target")
        
        # 檢查緩存狀態
        if stats["vector_optimizer"]["cache_hits"] == 0:
            health_status["warnings"].append("No cache hits detected")
        
        health_status["metrics"] = stats
        
    except Exception as e:
        health_status["status"] = "error"
        health_status["issues"].append(f"System error: {str(e)}")
    
    return health_status
```

### **日誌記錄**
```python
def log_rag_operation(operation_type, details, performance_metrics):
    """記錄 RAG 操作"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation_type": operation_type,
        "details": details,
        "performance": performance_metrics,
        "system_version": RAG_SYSTEM_VERSION
    }
    
    # 寫入日誌文件
    with open("logs/rag_operations.log", "a") as f:
        json.dump(log_entry, f)
        f.write("\n")
```

## 🔮 未來擴展

### **計劃中的功能**
1. **動態學習**：根據用戶反饋調整匹配策略
2. **多模態支持**：支持音頻、視頻等多種輸入
3. **個性化適配**：根據用戶偏好調整回應風格
4. **實時更新**：支持任務知識的動態更新

### **API 擴展**
```python
# RESTful API 設計
@app.post("/api/v1/rag/search")
async def rag_search(request: RAGSearchRequest):
    """RAG 搜索 API"""
    pass

@app.get("/api/v1/rag/tasks")
async def get_available_tasks():
    """獲取可用任務列表"""
    pass

@app.post("/api/v1/rag/feedback")
async def submit_feedback(request: RAGFeedbackRequest):
    """提交用戶反饋"""
    pass
```

---

**版本**：1.0.0  
**最後更新**：2025-08-01  
**維護者**：Vision Intelligence Hub 開發團隊 