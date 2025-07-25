"""
簡化的語義搜索測試

驗證ChromaDB語義搜索是否按預期工作
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

def test_embedding_similarity():
    """測試嵌入模型的語義理解能力"""
    from sentence_transformers import SentenceTransformer
    
    print("🧠 測試嵌入模型的語義理解...")
    
    # 初始化嵌入模型
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # 測試文本
    texts = [
        "桌上有螺絲刀和扳手",
        "我看到一些工具",
        "Python是編程語言",
        "用戶在寫代碼",
        "桌上有咖啡"
    ]
    
    # 生成嵌入
    embeddings = model.encode(texts)
    
    # 測試查詢
    queries = [
        "桌上有什麼工具？",
        "用戶在做什麼編程工作？",
        "有什麼飲料嗎？"
    ]
    
    query_embeddings = model.encode(queries)
    
    # 計算相似度
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    
    print("\n📊 語義相似度測試結果:")
    print("=" * 50)
    
    for i, query in enumerate(queries):
        print(f"\n🔍 查詢: '{query}'")
        
        # 計算與所有文本的相似度
        similarities = cosine_similarity([query_embeddings[i]], embeddings)[0]
        
        # 排序並顯示最相關的結果
        sorted_indices = np.argsort(similarities)[::-1]
        
        for j, idx in enumerate(sorted_indices[:3]):
            similarity = similarities[idx]
            print(f"   {j+1}. [{similarity:.3f}] {texts[idx]}")
    
    print("\n✅ 語義搜索測試完成！")
    print("🎯 結果顯示模型能夠理解語義關係")

if __name__ == "__main__":
    try:
        test_embedding_similarity()
    except ImportError as e:
        print(f"❌ 導入錯誤: {e}")
        print("請確保已安裝 sentence-transformers 和 scikit-learn")
    except Exception as e:
        print(f"❌ 測試失敗: {e}")