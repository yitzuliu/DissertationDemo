#!/usr/bin/env python3
"""
VQA 2.0 Testing Framework - COCO Real Data Version
Integrates all VQA 2.0 testing functionality, supports multiple VLM models, unified use of COCO real data

Usage:
    python vqa_test.py --questions 20           # COCO real data test (default)
    python vqa_test.py --quick --questions 20   # Same as above (explicitly specify quick mode)
    python vqa_test.py --models moondream2 --questions 10  # Test specific model
    python vqa_test.py --help                   # View all options

Author: AI Manual Assistant Team
Date: 2025-01-27
"""

import sys
import time
import argparse
import json
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    parser = argparse.ArgumentParser(description="VQA 2.0 Testing Tool")
    
    # Test mode (only keep quick mode, using COCO real data)
    parser.add_argument('--quick', action='store_true', default=True,
                       help='Use 20 COCO real images for testing (default mode)')
    
    # Test parameters
    parser.add_argument('--questions', type=int, default=20,
                       help='Number of test questions (default: 20, max 20 COCO images)')
    parser.add_argument('--models', nargs='+', 
                       default=['smolvlm_instruct', 'smolvlm_v2_instruct', 'moondream2', 'llava_mlx', 'phi35_vision'],
                       choices=['smolvlm_instruct', 'smolvlm_v2_instruct', 'moondream2', 'llava_mlx', 'phi35_vision'],
                       help='List of models to test (default: test all models)')
    
    # Advanced options
    parser.add_argument('--verbose', action='store_true',
                       help='Show detailed output')
    parser.add_argument('--save-results', action='store_true', default=True,
                       help='Save test results')
    
    args = parser.parse_args()
    
    print("🎯 VQA 2.0 Testing Framework")
    print("=" * 60)
    
    try:
        from vqa_framework import VQAFramework
        print("✅ Successfully imported VQA framework")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("Please ensure vqa_framework.py file exists")
        return 1
    
    # Initialize framework
    try:
        framework = VQAFramework()
        print("✅ VQA framework initialized successfully")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return 1
    
    # Show test configuration
    print(f"\n📊 Test Configuration:")
    print(f"   📝 Number of questions: {args.questions}")
    print(f"   🤖 Test models: {', '.join(args.models)}")
    print(f"   🎯 Test mode: COCO real data test")
    
    start_time = time.time()
    
    try:
        # Use COCO real data for testing
        print(f"\n⚡ Running COCO real data test...")
        print("📝 Using 20 COCO images and real VQA data")
        # Limit to max 20 questions (corresponding to 20 COCO images)
        questions, annotations = framework.load_sample_data(min(args.questions, 20))
        print(f"✅ Using up to 20 COCO images: {len(questions)} questions")
        
        # Check image availability
        print(f"\n🖼️ Checking image availability...")
        image_stats = framework.check_image_availability(questions)
        print(f"📈 Image availability: {image_stats['available']}/{image_stats['total']} ({image_stats['rate']:.1%})")
        
        # Run evaluation
        print(f"\n🤖 Starting model evaluation...")
        all_results = {}
        
        for i, model_name in enumerate(args.models, 1):
            print(f"\n[{i}/{len(args.models)}] Evaluating model: {model_name}")
            
            results = framework.evaluate_model(
                model_name=model_name,
                questions=questions,
                annotations=annotations,
                max_questions=args.questions,
                verbose=args.verbose
            )
            
            all_results[model_name] = results
        
        # Show result summary
        print("\n" + "="*60)
        print("📈 Testing Complete! Result Summary:")
        print("="*60)
        
        best_model = None
        best_vqa_accuracy = 0
        
        for model_name, results in all_results.items():
            if "error" in results:
                print(f"\n❌ {model_name}: Evaluation failed - {results['error']}")
                continue
                
            accuracy = results.get("accuracy", 0)
            vqa_accuracy = results.get("vqa_accuracy", 0)
            correct = results.get("correct", 0)
            total = results.get("total", 0)
            avg_time = results.get("avg_time", 0)
                
            if vqa_accuracy > best_vqa_accuracy:
                best_vqa_accuracy = vqa_accuracy
                best_model = model_name
            
            print(f"\n🤖 {model_name}:")
            print(f"   ✅ Correct answers: {correct}/{total}")
            print(f"   📊 Simple accuracy: {accuracy:.1%}")
            print(f"   🎯 VQA accuracy: {vqa_accuracy:.1%}")
            print(f"   ⏱️ Average inference time: {avg_time:.2f}s")
            
            # Show question and image mapping information
            if args.verbose and "question_results" in results:
                print(f"   📋 Question details:")
                for i, q_result in enumerate(results["question_results"][:5], 1):  # Only show first 5
                    q_id = q_result.get('question_id', 'N/A')
                    img_id = q_result.get('image_id', 'N/A')
                    img_file = q_result.get('image_filename', 'N/A')
                    is_correct = q_result.get('is_correct', False)
                    status = "✅" if is_correct else "❌"
                    print(f"      {i}. {status} Q{q_id} → Image{img_id} ({img_file})")
                if len(results["question_results"]) > 5:
                    print(f"      ... and {len(results['question_results'])-5} more questions")
            
            # Performance assessment
            if vqa_accuracy >= 0.6:
                assessment = "🏆 Excellent performance"
            elif vqa_accuracy >= 0.4:
                assessment = "🎯 Average performance"
            else:
                assessment = "🔧 Needs improvement"
            print(f"   {assessment}")
        
        if best_model:
            print(f"\n🏆 Best model: {best_model} (VQA accuracy: {best_vqa_accuracy:.1%})")
        
        # Save results
        if args.save_results and all_results:
            try:
                results_file = framework.save_results(all_results, "coco", args.questions)
                print(f"\n💾 Results saved to: {results_file}")
            except Exception as e:
                print(f"\n⚠️ Failed to save results: {e}")
        
        total_time = time.time() - start_time
        print(f"\n⏱️ Total test time: {total_time:.1f}s")
        print(f"\n✅ VQA 2.0 testing completed successfully!")
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️ Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Testing failed: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        print(f"\n🔧 Troubleshooting suggestions:")
        print("1. Check network connection")
        print("2. Verify model file integrity")
        print("3. Check data directory permissions")
        print("4. Use --verbose to see detailed error information")
        return 1

if __name__ == "__main__":
    sys.exit(main())
