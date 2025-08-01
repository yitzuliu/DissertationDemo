#!/usr/bin/env python3
"""
Migration Script for SmolVLM Refactored Implementation

This script helps migrate from the original SmolVLM implementation
to the refactored version by backing up original files and copying
the refactored versions.
"""

import os
import shutil
import sys
from pathlib import Path
from datetime import datetime

def backup_original_files():
    """Backup original files before migration."""
    print("📦 Creating backups of original files...")
    
    # Define paths
    current_dir = Path(__file__).parent
    target_dir = current_dir.parent / "smolvlm"
    backup_dir = target_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create backup directory
    backup_dir.mkdir(exist_ok=True)
    
    # Files to backup
    files_to_backup = [
        "run_smolvlm.py",
        "smolvlm_model.py"
    ]
    
    backed_up_files = []
    
    for file_name in files_to_backup:
        original_path = target_dir / file_name
        backup_path = backup_dir / file_name
        
        if original_path.exists():
            shutil.copy2(original_path, backup_path)
            backed_up_files.append(file_name)
            print(f"  ✅ Backed up: {file_name}")
        else:
            print(f"  ⚠️ File not found: {file_name}")
    
    return backup_dir, backed_up_files

def copy_refactored_files():
    """Copy refactored files to target directory."""
    print("\n🔄 Copying refactored files...")
    
    # Define paths
    current_dir = Path(__file__).parent
    target_dir = current_dir.parent / "smolvlm"
    
    # Files to copy
    files_to_copy = [
        ("server_manager.py", "server_manager.py"),
        ("run_smolvlm.py", "run_smolvlm.py"),
        ("smolvlm_model.py", "smolvlm_model.py")
    ]
    
    copied_files = []
    
    for src_file, dst_file in files_to_copy:
        src_path = current_dir / src_file
        dst_path = target_dir / dst_file
        
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            copied_files.append(dst_file)
            print(f"  ✅ Copied: {dst_file}")
        else:
            print(f"  ❌ Source file not found: {src_file}")
    
    return copied_files

def verify_migration():
    """Verify that the migration was successful."""
    print("\n🔍 Verifying migration...")
    
    # Define paths
    current_dir = Path(__file__).parent
    target_dir = current_dir.parent / "smolvlm"
    
    # Files to verify
    files_to_verify = [
        "server_manager.py",
        "run_smolvlm.py",
        "smolvlm_model.py"
    ]
    
    verification_results = []
    
    for file_name in files_to_verify:
        file_path = target_dir / file_name
        if file_path.exists():
            # Check if file is readable
            try:
                with open(file_path, 'r') as f:
                    content = f.read(100)  # Read first 100 characters
                verification_results.append((file_name, True, "File exists and readable"))
                print(f"  ✅ Verified: {file_name}")
            except Exception as e:
                verification_results.append((file_name, False, f"File exists but not readable: {e}"))
                print(f"  ❌ Verification failed: {file_name} - {e}")
        else:
            verification_results.append((file_name, False, "File does not exist"))
            print(f"  ❌ File missing: {file_name}")
    
    return verification_results

def run_test():
    """Run the test to ensure everything works."""
    print("\n🧪 Running test to verify functionality...")
    
    try:
        # Change to target directory
        target_dir = Path(__file__).parent.parent / "smolvlm"
        original_cwd = os.getcwd()
        os.chdir(target_dir)
        
        # Import and test
        sys.path.insert(0, str(target_dir))
        
        from server_manager import SmolVLMServerManager
        from smolvlm_model import SmolVLMModel
        
        # Test server manager
        manager = SmolVLMServerManager()
        is_running = manager.is_running()
        
        # Test model initialization
        config = {
            "smolvlm_version": "ggml-org/SmolVLM-500M-Instruct-GGUF",
            "port": 8080,
            "timeout": 60,
            "manage_server": False
        }
        model = SmolVLMModel("smolvlm", config)
        
        print("  ✅ All imports successful")
        print(f"  ✅ Server manager working (server running: {is_running})")
        print("  ✅ Model initialization successful")
        
        # Restore original working directory
        os.chdir(original_cwd)
        
        return True
        
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        # Restore original working directory
        os.chdir(original_cwd)
        return False

def main():
    """Main migration function."""
    print("🚀 SmolVLM Refactored Implementation Migration")
    print("=" * 60)
    
    # Check if we're in the right directory
    current_dir = Path(__file__).parent
    if current_dir.name != "smolvlm_refactored":
        print("❌ Error: This script must be run from the smolvlm_refactored directory")
        sys.exit(1)
    
    # Check if target directory exists
    target_dir = current_dir.parent / "smolvlm"
    if not target_dir.exists():
        print(f"❌ Error: Target directory {target_dir} does not exist")
        sys.exit(1)
    
    print(f"📁 Source directory: {current_dir}")
    print(f"📁 Target directory: {target_dir}")
    print()
    
    # Confirm migration
    response = input("Do you want to proceed with the migration? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("Migration cancelled.")
        sys.exit(0)
    
    try:
        # Step 1: Backup original files
        backup_dir, backed_up_files = backup_original_files()
        
        # Step 2: Copy refactored files
        copied_files = copy_refactored_files()
        
        # Step 3: Verify migration
        verification_results = verify_migration()
        
        # Step 4: Run test
        test_success = run_test()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Migration Summary:")
        print("=" * 60)
        
        print(f"📦 Backup directory: {backup_dir}")
        print(f"📦 Files backed up: {len(backed_up_files)}")
        for file_name in backed_up_files:
            print(f"  - {file_name}")
        
        print(f"\n🔄 Files copied: {len(copied_files)}")
        for file_name in copied_files:
            print(f"  - {file_name}")
        
        print(f"\n🔍 Verification results:")
        all_verified = True
        for file_name, success, message in verification_results:
            status = "✅" if success else "❌"
            print(f"  {status} {file_name}: {message}")
            if not success:
                all_verified = False
        
        print(f"\n🧪 Test result: {'✅ PASS' if test_success else '❌ FAIL'}")
        
        if all_verified and test_success:
            print("\n🎉 Migration completed successfully!")
            print("\n📝 Next steps:")
            print("1. Test your application with the refactored implementation")
            print("2. If everything works correctly, you can delete the backup directory")
            print("3. If issues arise, restore from backup:")
            print(f"   cp {backup_dir}/* {target_dir}/")
        else:
            print("\n⚠️ Migration completed with issues.")
            print("Please check the verification results and test output above.")
            print("You can restore from backup if needed:")
            print(f"   cp {backup_dir}/* {target_dir}/")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("Please check the error and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main() 