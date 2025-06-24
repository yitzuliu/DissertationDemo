#!/usr/bin/env python3
"""
Model Configuration Validator and Standardizer

This script validates all model configuration files against the template.json
and provides warnings for missing or non-standard fields.
"""

import json
import os
from pathlib import Path
import sys
import argparse

def load_json(filepath):
    """Load JSON file into a dictionary"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {filepath}: {str(e)}")
        return None

def save_json(filepath, data):
    """Save dictionary as JSON file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving {filepath}: {str(e)}")
        return False

def validate_config(config, template, model_name):
    """Validate model configuration against template"""
    issues = []
    missing_fields = []
    
    # Check for missing required top-level fields
    required_fields = [
        "model_name", "model_path", "server", "image_processing", 
        "api", "ui", "version"
    ]
    for field in required_fields:
        if field not in config:
            missing_fields.append(field)
            issues.append(f"Missing required field: {field}")
    
    # Check for nested required fields
    if "server" in config:
        for field in ["command", "args", "port"]:
            if field not in config["server"]:
                missing_fields.append(f"server.{field}")
                issues.append(f"Missing required field: server.{field}")
    
    if "image_processing" in config:
        for field in ["size", "format"]:
            if field not in config["image_processing"]:
                missing_fields.append(f"image_processing.{field}")
                issues.append(f"Missing required field: image_processing.{field}")
    
    # Check for non-standard fields (present in config but not in template)
    def check_nonstandard_fields(config_dict, template_dict, prefix=""):
        for key in config_dict:
            full_key = f"{prefix}.{key}" if prefix else key
            if key not in template_dict:
                issues.append(f"Non-standard field: {full_key}")
            elif isinstance(config_dict[key], dict) and isinstance(template_dict[key], dict):
                check_nonstandard_fields(config_dict[key], template_dict[key], full_key)
    
    check_nonstandard_fields(config, template)
    
    # Output validation results
    if not issues:
        print(f"✅ {model_name}: Valid configuration")
        return True, {}
    else:
        print(f"⚠️ {model_name}: Found {len(issues)} issue(s):")
        for issue in issues:
            print(f"  - {issue}")
        return False, {"missing": missing_fields, "issues": issues}

def standardize_config(config, template, missing_fields):
    """Add missing fields from template to config"""
    result = config.copy()
    
    # Helper function to add missing fields
    def add_missing_fields(result_dict, template_dict, prefix=""):
        for key, value in template_dict.items():
            if key not in result_dict:
                if prefix in missing_fields or f"{prefix}.{key}" in missing_fields or not prefix:
                    result_dict[key] = value
                    print(f"  + Added missing field: {prefix + '.' if prefix else ''}{key}")
            elif isinstance(value, dict) and isinstance(result_dict[key], dict):
                add_missing_fields(result_dict[key], value, f"{prefix}.{key}" if prefix else key)
    
    add_missing_fields(result, template)
    return result

def main():
    parser = argparse.ArgumentParser(description='Validate and standardize model config files')
    parser.add_argument('--fix', action='store_true', help='Fix issues by adding missing fields')
    parser.add_argument('--check', action='store_true', help='Only check for issues without output')
    args = parser.parse_args()
    
    config_dir = Path(__file__).parent.parent / "config" / "model_configs"
    if not config_dir.exists():
        print(f"Error: Config directory not found: {config_dir}")
        sys.exit(1)
    
    template_path = config_dir / "template.json"
    template = load_json(template_path)
    if not template:
        print("Error: Template file not found or invalid")
        sys.exit(1)
    
    all_valid = True
    models_with_issues = []
    
    # Process each model config file
    for config_file in config_dir.glob("*.json"):
        if config_file.name == "template.json":
            continue
        
        model_name = config_file.stem
        config = load_json(config_file)
        if not config:
            continue
        
        valid, issues = validate_config(config, template, model_name)
        all_valid = all_valid and valid
        
        if not valid:
            models_with_issues.append(model_name)
            if args.fix:
                print(f"Fixing {model_name} configuration...")
                fixed_config = standardize_config(config, template, issues.get("missing", []))
                if save_json(config_file, fixed_config):
                    print(f"✅ Updated {model_name} configuration")
    
    # Print summary
    print("\nValidation Summary:")
    if all_valid:
        print("✅ All model configurations are valid")
    else:
        print(f"⚠️ {len(models_with_issues)} model(s) have issues:")
        for model in models_with_issues:
            print(f"  - {model}")
        if args.fix:
            print("\nFixed the issues by adding missing fields from the template")
        else:
            print("\nRun with --fix to automatically add missing fields")
    
    return 0 if all_valid else 1

if __name__ == "__main__":
    sys.exit(main())
