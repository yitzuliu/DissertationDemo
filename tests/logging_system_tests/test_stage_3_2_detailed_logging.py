#!/usr/bin/env python3
"""
Stage 3.2: 後端查詢處理日誌整合測試

測試內容：
1. 詳細查詢分類過程日誌
2. 詳細查詢處理過程日誌
3. 狀態查找過程日誌
4. 回應生成過程日誌
5. 向後兼容性測試
"""

import requests
import time
import json
import sys
import os
from pathlib import Path

class Stage32DetailedLoggingTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.test_results = {
            'detailed_classify_logging': False,
            'detailed_process_logging': False,
            'state_lookup_logging': False,
            'response_generate_logging': False,
            'backward_compatibility': False
        }
        
    def test_detailed_classify_logging(self):
        """測試詳細查詢分類過程日誌"""
        print("🧪 測試詳細查詢分類過程日誌...")
        
        try:
            # 測試查詢分類過程
            query_data = {
                'query': 'Where am I?',
                'query_id': f"stage32_classify_{int(time.time() * 1000)}"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/state/query",
                json=query_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    print(f"✅ 查詢處理成功: {result['query_type']}")
                    self.test_results['detailed_classify_logging'] = True
                    return True
                else:
                    print(f"❌ 查詢處理失敗: {result}")
                    return False
            else:
                print(f"❌ 查詢端點錯誤: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 詳細分類日誌測試失敗: {e}")
            return False
    
    def test_detailed_process_logging(self):
        """測試詳細查詢處理過程日誌"""
        print("\n🧪 測試詳細查詢處理過程日誌...")
        
        try:
            # 測試不同類型的查詢
            test_queries = [
                "What tools do I need?",
                "What's next?",
                "What's my progress?",
                "Help me with this step"
            ]
            
            successful_queries = 0
            for query in test_queries:
                query_data = {
                    'query': query,
                    'query_id': f"stage32_process_{int(time.time() * 1000)}"
                }
                
                response = requests.post(
                    f"{self.backend_url}/api/v1/state/query",
                    json=query_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'success':
                        successful_queries += 1
                        print(f"  ✅ '{query}' -> {result['query_type']}")
                    else:
                        print(f"  ❌ '{query}' -> 失敗")
                else:
                    print(f"  ❌ '{query}' -> 錯誤 {response.status_code}")
            
            success_rate = successful_queries / len(test_queries)
            if success_rate >= 0.8:  # 80% 成功率
                print(f"✅ 詳細處理日誌測試成功: {successful_queries}/{len(test_queries)}")
                self.test_results['detailed_process_logging'] = True
                return True
            else:
                print(f"❌ 詳細處理日誌測試失敗: {successful_queries}/{len(test_queries)}")
                return False
                
        except Exception as e:
            print(f"❌ 詳細處理日誌測試失敗: {e}")
            return False
    
    def test_state_lookup_logging(self):
        """測試狀態查找過程日誌"""
        print("\n🧪 測試狀態查找過程日誌...")
        
        try:
            # 測試狀態查找（目前應該沒有活動狀態）
            query_data = {
                'query': 'What is the current step?',
                'query_id': f"stage32_state_{int(time.time() * 1000)}"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/state/query",
                json=query_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    # 檢查回應是否包含 "No active state"
                    if "No active state" in result.get('response', ''):
                        print("✅ 狀態查找日誌測試成功（無活動狀態）")
                        self.test_results['state_lookup_logging'] = True
                        return True
                    else:
                        print("⚠️ 狀態查找日誌測試（有活動狀態）")
                        self.test_results['state_lookup_logging'] = True
                        return True
                else:
                    print(f"❌ 狀態查找測試失敗: {result}")
                    return False
            else:
                print(f"❌ 狀態查找端點錯誤: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 狀態查找日誌測試失敗: {e}")
            return False
    
    def test_response_generate_logging(self):
        """測試回應生成過程日誌"""
        print("\n🧪 測試回應生成過程日誌...")
        
        try:
            # 測試回應生成
            query_data = {
                'query': 'Give me an overview',
                'query_id': f"stage32_response_{int(time.time() * 1000)}"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/state/query",
                json=query_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    response_text = result.get('response', '')
                    response_length = len(response_text)
                    
                    print(f"✅ 回應生成測試成功: 長度 {response_length} 字符")
                    print(f"  回應類型: {result.get('query_type', 'unknown')}")
                    print(f"  處理時間: {result.get('processing_time_ms', 0):.1f}ms")
                    
                    self.test_results['response_generate_logging'] = True
                    return True
                else:
                    print(f"❌ 回應生成測試失敗: {result}")
                    return False
            else:
                print(f"❌ 回應生成端點錯誤: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 回應生成日誌測試失敗: {e}")
            return False
    
    def test_backward_compatibility(self):
        """測試向後兼容性"""
        print("\n🧪 測試向後兼容性...")
        
        try:
            # 測試不帶 query_id 的查詢（舊格式）
            query_data = {
                'query': 'What equipment is required?'
                # 不包含 query_id
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/state/query",
                json=query_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success' and 'response' in result:
                    print(f"✅ 向後兼容性測試成功: {result['query_type']}")
                    self.test_results['backward_compatibility'] = True
                    return True
                else:
                    print(f"❌ 向後兼容性測試失敗: {result}")
                    return False
            else:
                print(f"❌ 向後兼容性端點錯誤: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 向後兼容性測試失敗: {e}")
            return False
    
    def check_log_files(self):
        """檢查日誌文件中的詳細記錄"""
        print("\n🔍 檢查日誌文件中的詳細記錄...")
        
        try:
            # 查找今天的日誌文件
            today = time.strftime('%Y%m%d')
            log_file = f"logs/user_{today}.log"
            
            if not os.path.exists(log_file):
                print(f"⚠️ 日誌文件不存在: {log_file}")
                return False
            
            # 讀取最新的日誌記錄
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 查找 Stage 3.2 的新日誌類型
            new_log_types = [
                'QUERY_CLASSIFY_START',
                'QUERY_PATTERN_CHECK',
                'QUERY_PATTERN_MATCH',
                'QUERY_CLASSIFY_RESULT',
                'QUERY_PROCESS_START',
                'QUERY_STATE_LOOKUP',
                'QUERY_RESPONSE_GENERATE',
                'QUERY_PROCESS_COMPLETE',
                'QUERY_RECEIVED'
            ]
            
            found_types = []
            for line in lines[-50:]:  # 檢查最後50行
                for log_type in new_log_types:
                    if log_type in line:
                        found_types.append(log_type)
            
            print(f"📊 找到的新日誌類型: {len(found_types)}/{len(new_log_types)}")
            for log_type in new_log_types:
                status = "✅" if log_type in found_types else "❌"
                print(f"  {status} {log_type}")
            
            # 如果找到大部分新日誌類型，認為測試成功
            if len(found_types) >= len(new_log_types) * 0.7:  # 70% 覆蓋率
                print("✅ 日誌文件檢查成功")
                return True
            else:
                print("❌ 日誌文件檢查失敗")
                return False
                
        except Exception as e:
            print(f"❌ 日誌文件檢查失敗: {e}")
            return False
    
    def run_all_tests(self):
        """運行所有測試"""
        print("🚀 Stage 3.2: 後端查詢處理日誌整合測試")
        print("=" * 60)
        
        # 檢查後端服務是否運行
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code != 200:
                print("❌ 後端服務未運行，請先啟動後端服務")
                return False
            print("✅ 後端服務運行正常")
        except Exception as e:
            print(f"❌ 無法連接到後端服務: {e}")
            return False
        
        # 運行測試
        tests = [
            self.test_detailed_classify_logging,
            self.test_detailed_process_logging,
            self.test_state_lookup_logging,
            self.test_response_generate_logging,
            self.test_backward_compatibility
        ]
        
        passed_tests = 0
        for test in tests:
            if test():
                passed_tests += 1
        
        # 檢查日誌文件
        log_check_result = self.check_log_files()
        
        # 輸出結果
        print("\n📊 測試結果摘要:")
        print("=" * 40)
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
        
        print(f"\n總計: {passed_tests}/{len(tests)} 測試通過")
        print(f"日誌文件檢查: {'✅ PASS' if log_check_result else '❌ FAIL'}")
        
        if passed_tests == len(tests) and log_check_result:
            print("🎉 所有測試通過！Stage 3.2 實作成功")
            return True
        else:
            print("⚠️ 部分測試失敗，請檢查實作")
            return False

def main():
    tester = Stage32DetailedLoggingTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 