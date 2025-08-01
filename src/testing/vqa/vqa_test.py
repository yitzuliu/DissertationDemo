#!/usr/bin/env python3
"""
VQA 2.0 Testing Framework - COCO Real Data Version
Integrates all VQA 2.0 testing functionality, supports multiple VLM models

Usage:
    python vqa_test.py                    # Basic test (20 questions, all models)
    python vqa_test.py --questions 10     # Test with 10 questions
    python vqa_test.py --models moondream2  # Test specific model
    python vqa_test.py --help             # View all options

Author: AI Manual Assistant Team
Date: 2025-01-27
"""

import sys
import time
import argparse
import json
from pathlib import Path

# Ensure parent directory is in sys.path for direct execution
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    parser = argparse.ArgumentParser(description="VQA 2.0 Testing Tool")
    
    # Test parameters
    parser.add_argument('--questions', type=int, default=20,
                       help='Number of test questions (default: 20, max 20)')
    parser.add_argument('--models', nargs='+', 
                       default=['phi35_vision', 'llava_mlx', 'smolvlm_v2_instruct', 'smolvlm_instruct', 'moondream2'],
                       choices=['phi35_vision', 'llava_mlx', 'smolvlm_v2_instruct', 'smolvlm_instruct', 'moondream2'],
                       help='Models to test (default: all models in optimized order)')
    
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
        # Use robust relative path for data_dir
        data_dir = Path(__file__).parent.parent / 'materials' / 'vqa2'
        framework = VQAFramework(data_dir=str(data_dir))
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
        # Load COCO real data
        print(f"\n⚡ Loading COCO real data...")
        questions, annotations = framework.load_sample_data(min(args.questions, 20))
        print(f"✅ Loaded {len(questions)} questions")
        
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
            
            # Show question details in verbose mode
            if args.verbose and "question_results" in results:
                print(f"   📋 Question details:")
                for i, q_result in enumerate(results["question_results"][:5], 1):
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
                # Always save results, whether single model or complete test
                if len(args.models) == 1:
                    # Single model test - use consistent naming format
                    suffix = f"single_{args.models[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    results_file = framework.save_results(all_results, "coco", args.questions, suffix)
                else:
                    # Complete test - use timestamp
                    results_file = framework.save_results(all_results, "coco", args.questions)
                print(f"\n💾 Results saved to: {results_file}")
            except Exception as e:
                print(f"\n⚠️ Failed to save results: {e}")
        
        total_time = time.time() - start_time
        print(f"\n⏱️ Total test time: {total_time:.1f}s")
        print(f"\n✅ VQA 2.0 testing completed successfully!")
        
        # Cleanup before exit
        try:
            framework.cleanup()
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️ Testing interrupted by user")
        # Cleanup on interrupt
        try:
            framework.cleanup()
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
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
        
        # Cleanup on error
        try:
            framework.cleanup()
        except Exception as cleanup_error:
            print(f"⚠️ Cleanup warning: {cleanup_error}")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
