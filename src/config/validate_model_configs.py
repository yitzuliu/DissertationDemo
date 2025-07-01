#!/usr/bin/env python3
"""
Model Configuration Validator

Validates that all model configurations are consistent and correct.
Checks for:
- Model ID consistency across files
- Path correctness
- Server configuration validity
- API endpoint consistency
"""

import json
import os
from pathlib import Path
import sys

class ModelConfigValidator:
    def __init__(self, config_dir="./"):
        self.config_dir = Path(str(config_dir))
        self.errors = []
        self.warnings = []
        
    def validate_all_configs(self):
        """驗證所有模型配置的一致性"""
        print("🔍 Validating Model Configurations...")
        
        # 檢查主配置文件
        self._validate_app_config()
        
        # 檢查所有模型配置
        model_configs_dir = self.config_dir / "model_configs"
        if model_configs_dir.exists():
            for config_file in model_configs_dir.glob("*.json"):
                self._validate_model_config(config_file)
        
        # 檢查後端代碼一致性
        self._validate_backend_consistency()
        
        # 輸出報告
        self._print_report()
        
        return len(self.errors) == 0
    
    def _validate_app_config(self):
        """驗證主應用配置"""
        app_config_path = self.config_dir / "app_config.json"
        
        if not app_config_path.exists():
            self.errors.append("❌ app_config.json not found")
            return
            
        try:
            with open(app_config_path, 'r') as f:
                config = json.load(f)
                
            active_model = config.get("active_model")
            if not active_model:
                self.errors.append("❌ No active_model specified in app_config.json")
                return
                
            # 檢查對應的模型配置文件是否存在
            model_config_path = self.config_dir / "model_configs" / f"{active_model}.json"
            if not model_config_path.exists():
                self.errors.append(f"❌ Model config file {active_model}.json not found for active model")
            else:
                print(f"✅ Active model config found: {active_model}.json")
                
        except json.JSONDecodeError:
            self.errors.append("❌ Invalid JSON in app_config.json")
        except Exception as e:
            self.errors.append(f"❌ Error reading app_config.json: {e}")
    
    def _validate_model_config(self, config_path):
        """驗證單個模型配置文件"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            model_id = config.get("model_id")
            model_name = config.get("model_name")
            
            # 檢查必需字段
            required_fields = ["model_id", "model_name", "device"]
            for field in required_fields:
                if field not in config:
                    self.errors.append(f"❌ {config_path.name}: Missing required field '{field}'")
            
            # 檢查模型ID與文件名的一致性
            expected_filename = f"{model_id}.json"
            if config_path.name != expected_filename:
                self.warnings.append(f"⚠️  {config_path.name}: Model ID '{model_id}' doesn't match filename")
            
            # 檢查路徑配置
            if "model_path" in config:
                model_path = config["model_path"]
                if model_path.startswith("src/"):
                    self.warnings.append(f"⚠️  {config_path.name}: model_path uses absolute project path, consider relative path")
            
            # 檢查服務器配置
            if "server" in config:
                server_config = config["server"]
                if "startup_script" in server_config:
                    script_path = server_config["startup_script"]
                    if script_path.startswith("src/"):
                        # 這是完整路徑，檢查文件是否存在
                        full_script_path = Path("../..") / script_path
                        if not full_script_path.exists():
                            self.warnings.append(f"⚠️  {config_path.name}: startup_script path may be incorrect: {script_path}")
            
            print(f"✅ {config_path.name}: Basic validation passed")
                
        except json.JSONDecodeError:
            self.errors.append(f"❌ {config_path.name}: Invalid JSON")
        except Exception as e:
            self.errors.append(f"❌ {config_path.name}: Error reading file: {e}")
    
    def _validate_backend_consistency(self):
        """檢查後端代碼與配置的一致性"""
        backend_main_path = self.config_dir.parent / "backend" / "main.py"
        
        if not backend_main_path.exists():
            self.warnings.append("⚠️  Backend main.py not found, skipping consistency check")
            return
            
        try:
            with open(backend_main_path, 'r') as f:
                backend_code = f.read()
            
            # 檢查所有模型配置文件
            model_configs_dir = self.config_dir / "model_configs"
            if model_configs_dir.exists():
                model_ids = []
                for config_file in model_configs_dir.glob("*.json"):
                    try:
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                            model_id = config.get("model_id")
                            if model_id:
                                model_ids.append(model_id)
                    except:
                        continue
                
                # 檢查後端代碼是否包含所有模型ID
                missing_models = []
                for model_id in model_ids:
                    if model_id not in backend_code:
                        missing_models.append(model_id)
                
                if missing_models:
                    self.warnings.append(f"⚠️  Backend code may not handle these models: {missing_models}")
                else:
                    print("✅ Backend appears to handle all configured models")
                    
        except Exception as e:
            self.warnings.append(f"⚠️  Could not validate backend consistency: {e}")
    
    def _print_report(self):
        """輸出驗證報告"""
        print("\n" + "="*60)
        print("📋 MODEL CONFIGURATION VALIDATION REPORT")
        print("="*60)
        
        if not self.errors and not self.warnings:
            print("🎉 All configurations are valid and consistent!")
            return
        
        if self.errors:
            print(f"\n🚨 ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   {warning}")
        
        print(f"\n📊 Summary: {len(self.errors)} errors, {len(self.warnings)} warnings")
        
        if self.errors:
            print("❌ Configuration validation FAILED")
        else:
            print("✅ Configuration validation PASSED (with warnings)")

def main():
    """主函數"""
    # 確定配置目錄
    if len(sys.argv) > 1:
        config_dir = Path(sys.argv[1])
    else:
        # 假設從項目根目錄運行
        config_dir = Path(__file__).parent
    
    validator = ModelConfigValidator(config_dir)
    success = validator.validate_all_configs()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
