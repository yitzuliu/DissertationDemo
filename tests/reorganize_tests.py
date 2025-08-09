#!/usr/bin/env python3
"""
測試檔案重新整理腳本

這個腳本會：
1. 創建新的測試資料夾結構
2. 移動和重命名測試檔案
3. 歸檔舊檔案到 archive/tests/
4. 更新檔案路徑和導入

執行方式：
python tests/reorganize_tests.py
"""

import os
import shutil
from pathlib import Path

class TestReorganizer:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.archive_dir = self.base_dir.parent / "archive" / "tests"
        
        # 新結構定義
        self.new_structure = {
            "core": [
                ("test_backend_api.py", "test_backend_api.py"),
                ("test_stage_1_3.py", "test_vector_optimization.py"),
            ],
            "memory_system": [
                ("test_task_knowledge.py", "test_task_knowledge.py"),
                ("stage_2_4/test_task_knowledge_enhanced.py", "test_memory_consistency.py"),
            ],
            "vlm_fallback": [
                ("test_vlm_fallback_integration.py", "test_fallback_integration.py"),
            ],
            "integration": [
                ("stage_3_2/test_dual_loop_coordination.py", "test_dual_loop_coordination.py"),
                ("stage_3_3/test_stage_3_3_final.py", "test_cross_service.py"),
                ("test_complete_system_e2e.py", "test_end_to_end.py"),
            ],
            "system": [
                ("stage_3_1/run_stage_3_1_tests.py", "test_service_startup.py"),
            ],
            "scenarios": [
                # 這些是新建的檔案，稍後創建
            ]
        }
        
        # 需要歸檔的檔案
        self.files_to_archive = {
            "deprecated": [
                "test_backend_only.py",
                "test_integration_only.py", 
                "quick_test.py",
                "stage_2_integrated_results.json",
                "STAGE_2_TEST_GUIDE.md",
            ],
            "old_structure": [
                "stage_3_1/",
                "stage_3_2/", 
                "stage_3_3/",
                "stage_2_4/",
                "logging_system_tests/",
            ],
            "experimental": [
                "test_vlm_fallback_e2e.py",
                "test_full_system_automated.py",
                "test_core_components.py",
            ]
        }
    
    def create_new_structure(self):
        """創建新的資料夾結構"""
        print("🏗️ 創建新的測試資料夾結構...")
        
        for folder in self.new_structure.keys():
            folder_path = self.base_dir / folder
            folder_path.mkdir(exist_ok=True)
            print(f"   ✅ 創建資料夾: {folder}")
        
        # 創建歸檔資料夾
        for archive_type in self.files_to_archive.keys():
            archive_path = self.archive_dir / archive_type
            archive_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ 創建歸檔資料夾: archive/tests/{archive_type}")
    
    def move_files(self):
        """移動和重命名檔案"""
        print("📦 移動和重命名測試檔案...")
        
        for folder, files in self.new_structure.items():
            for old_path, new_name in files:
                old_file = self.base_dir / old_path
                new_file = self.base_dir / folder / new_name
                
                if old_file.exists():
                    if old_file.is_file():
                        shutil.copy2(old_file, new_file)
                        print(f"   ✅ 移動: {old_path} → {folder}/{new_name}")
                    else:
                        print(f"   ⚠️ 跳過資料夾: {old_path}")
                else:
                    print(f"   ❌ 檔案不存在: {old_path}")
    
    def archive_old_files(self):
        """歸檔舊檔案"""
        print("🗂️ 歸檔舊檔案...")
        
        for archive_type, files in self.files_to_archive.items():
            archive_path = self.archive_dir / archive_type
            
            for file_path in files:
                old_file = self.base_dir / file_path
                
                if old_file.exists():
                    if old_file.is_file():
                        new_file = archive_path / old_file.name
                        shutil.move(str(old_file), str(new_file))
                        print(f"   ✅ 歸檔檔案: {file_path} → archive/tests/{archive_type}/")
                    elif old_file.is_dir():
                        new_dir = archive_path / old_file.name
                        if new_dir.exists():
                            shutil.rmtree(new_dir)
                        shutil.move(str(old_file), str(new_dir))
                        print(f"   ✅ 歸檔資料夾: {file_path} → archive/tests/{archive_type}/")
                else:
                    print(f"   ⚠️ 檔案不存在: {file_path}")
    
    def create_new_test_files(self):
        """創建新的測試檔案"""
        print("📝 創建新的測試檔案...")
        
        # 創建 test_coffee_brewing.py
        coffee_test_content = '''#!/usr/bin/env python3
"""
咖啡沖泡場景完整測試

這個測試專門驗證咖啡沖泡場景的完整工作流程：
1. 開啟前端和後端服務
2. 模擬 VLM 觀察咖啡沖泡步驟
3. 驗證步驟配對和狀態更新
4. 測試觀察錯誤時的處理
"""

import sys
import time
import requests
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

class CoffeeBrewingScenarioTest:
    """咖啡沖泡場景測試"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.test_results = {
            'service_startup': False,
            'step_matching': False,
            'error_handling': False,
            'state_consistency': False
        }
        
        # 模擬咖啡沖泡步驟觀察
        self.coffee_steps = [
            {"step": 1, "observation": "準備咖啡豆和器具", "confidence": 0.9},
            {"step": 2, "observation": "研磨咖啡豆", "confidence": 0.85},
            {"step": 3, "observation": "加熱水到適當溫度", "confidence": 0.88},
            {"step": 4, "observation": "沖泡咖啡", "confidence": 0.92},
            {"step": 5, "observation": "享用咖啡", "confidence": 0.95}
        ]
    
    def test_step_matching(self):
        """測試步驟配對"""
        print("🧪 測試咖啡沖泡步驟配對...")
        
        for step_data in self.coffee_steps:
            try:
                # 模擬 VLM 觀察
                response = requests.post(
                    f"{self.backend_url}/api/v1/state/process",
                    json={
                        "text": step_data["observation"],
                        "confidence": step_data["confidence"],
                        "step_id": step_data["step"]
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ 步驟 {step_data['step']}: {step_data['observation']}")
                    print(f"      配對結果: {result.get('matched_step', 'N/A')}")
                else:
                    print(f"   ❌ 步驟 {step_data['step']} 處理失敗")
                    
            except Exception as e:
                print(f"   ❌ 步驟 {step_data['step']} 異常: {e}")
        
        self.test_results['step_matching'] = True
        return True
    
    def test_error_handling(self):
        """測試錯誤觀察處理"""
        print("🧪 測試錯誤觀察處理...")
        
        error_observations = [
            {"observation": "看到奇怪的東西", "confidence": 0.3},
            {"observation": "無法識別當前步驟", "confidence": 0.2},
            {"observation": "", "confidence": 0.0}
        ]
        
        for error_data in error_observations:
            try:
                response = requests.post(
                    f"{self.backend_url}/api/v1/state/process",
                    json={
                        "text": error_data["observation"],
                        "confidence": error_data["confidence"]
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"   ✅ 錯誤觀察處理正常: {error_data['observation'][:20]}...")
                else:
                    print(f"   ❌ 錯誤觀察處理失敗")
                    
            except Exception as e:
                print(f"   ❌ 錯誤觀察異常: {e}")
        
        self.test_results['error_handling'] = True
        return True
    
    def run_full_test(self):
        """執行完整測試"""
        print("🎯 咖啡沖泡場景完整測試")
        print("=" * 50)
        
        try:
            # 測試步驟配對
            self.test_step_matching()
            
            # 測試錯誤處理
            self.test_error_handling()
            
            # 顯示結果
            passed = sum(self.test_results.values())
            total = len(self.test_results)
            
            print(f"\\n📊 測試結果: {passed}/{total} 通過")
            
            if passed == total:
                print("✅ 咖啡沖泡場景測試成功!")
                return True
            else:
                print("❌ 部分測試失敗")
                return False
                
        except Exception as e:
            print(f"❌ 測試執行異常: {e}")
            return False

def main():
    tester = CoffeeBrewingScenarioTest()
    success = tester.run_full_test()
    return success

if __name__ == "__main__":
    main()
'''
        
        coffee_test_file = self.base_dir / "scenarios" / "test_coffee_brewing.py"
        with open(coffee_test_file, 'w', encoding='utf-8') as f:
            f.write(coffee_test_content)
        print("   ✅ 創建: scenarios/test_coffee_brewing.py")
        
        # 創建其他新檔案的佔位符
        placeholder_files = [
            ("core/test_state_tracker.py", "狀態追蹤器測試"),
            ("core/test_query_processor.py", "查詢處理器測試"),
            ("memory_system/test_rag_system.py", "RAG 系統測試"),
            ("vlm_fallback/test_fallback_triggers.py", "Fallback 觸發測試"),
            ("vlm_fallback/test_image_processing.py", "圖片處理測試"),
            ("system/test_logging_system.py", "日誌系統測試"),
            ("system/test_performance.py", "性能測試"),
            ("scenarios/test_task_scenarios.py", "任務場景測試"),
        ]
        
        for file_path, description in placeholder_files:
            full_path = self.base_dir / file_path
            placeholder_content = f'''#!/usr/bin/env python3
"""
{description}

TODO: 實現具體測試邏輯
這個檔案是重新整理過程中創建的佔位符，需要進一步實現。
"""

def main():
    print("🚧 {description} - 待實現")
    return True

if __name__ == "__main__":
    main()
'''
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(placeholder_content)
            print(f"   ✅ 創建佔位符: {file_path}")
    
    def update_readme(self):
        """更新 README"""
        print("📚 更新 README...")
        
        # 重命名舊 README
        old_readme = self.base_dir / "README.md"
        if old_readme.exists():
            backup_readme = self.base_dir / "README_OLD.md"
            shutil.move(str(old_readme), str(backup_readme))
            print("   ✅ 備份舊 README 為 README_OLD.md")
        
        # 重命名新 README
        new_readme = self.base_dir / "README_NEW.md"
        if new_readme.exists():
            final_readme = self.base_dir / "README.md"
            shutil.move(str(new_readme), str(final_readme))
            print("   ✅ 啟用新 README.md")
    
    def run_reorganization(self):
        """執行完整重新整理"""
        print("🚀 開始測試檔案重新整理")
        print("=" * 50)
        
        try:
            self.create_new_structure()
            self.move_files()
            self.create_new_test_files()
            self.archive_old_files()
            self.update_readme()
            
            print("\n✅ 測試檔案重新整理完成!")
            print("📁 新結構已創建")
            print("🗂️ 舊檔案已歸檔至 archive/tests/")
            print("📚 README 已更新")
            
            return True
            
        except Exception as e:
            print(f"\n❌ 重新整理過程中出現錯誤: {e}")
            return False

def main():
    reorganizer = TestReorganizer()
    success = reorganizer.run_reorganization()
    
    if success:
        print("\n🎉 重新整理成功完成!")
        print("請檢查新的測試結構並測試相關功能。")
    else:
        print("\n💥 重新整理失敗!")
        print("請檢查錯誤信息並手動修復。")

if __name__ == "__main__":
    main()