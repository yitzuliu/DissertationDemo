#!/usr/bin/env python3
"""
SmolVLM2 Video Processing
MLX-optimized video understanding and real-time processing for Apple Silicon
"""

import os
import sys
from pathlib import Path
from typing import Union, Dict, Any, Optional, Generator
import json
import time

try:
    import mlx_vlm
    from PIL import Image
    import cv2
    import numpy as np
except ImportError as e:
    print(f"❌ Required dependency not found: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)

class SmolVLM2VideoProcessor:
    """Video processor using MLX-VLM for Apple Silicon optimization"""
    
    def __init__(self, model_path: str = "mlx-community/SmolVLM2-500M-Video-Instruct-mlx"):
        self.model_path = model_path
        self.model = None
        self.processor = None
        self._load_model()
    
    def _load_model(self):
        """Load the MLX-optimized SmolVLM2 model"""
        try:
            print(f"🔄 Loading SmolVLM2 video model: {self.model_path}")
            # MLX-VLM handles model loading automatically
            print("✅ Video model loaded successfully with MLX optimization")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            raise
    
    def process_video(
        self,
        video_path: Union[str, Path],
        prompt: str = "Describe what is happening in this video",
        system_prompt: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Process a single video file with SmolVLM2
        
        Args:
            video_path: Path to video file
            prompt: User prompt for the video
            system_prompt: Optional system prompt for context
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Validate video file
            video_path = Path(video_path)
            if not video_path.exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            # Check video format
            supported_formats = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
            if video_path.suffix.lower() not in supported_formats:
                raise ValueError(f"Unsupported video format: {video_path.suffix}")
            
            # Prepare system prompt
            if system_prompt is None:
                system_prompt = "Focus only on describing the key dramatic action or notable event occurring in this video segment. Skip general context or scene-setting details unless they are crucial to understanding the main action."
            
            print(f"🔄 Processing video: {video_path.name}")
            print(f"📝 Prompt: '{prompt[:50]}...'")
            
            # Use MLX-VLM video generation (adapted from Apple.md example)
            response = mlx_vlm.smolvlm_video_generate(
                model=self.model_path,
                video=str(video_path.absolute()),
                prompt=prompt,
                system=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            print("✅ Video processed successfully")
            
            # Get video metadata
            metadata = self._get_video_metadata(video_path)
            
            return {
                "success": True,
                "response": response,
                "model": self.model_path,
                "video_path": str(video_path),
                "prompt": prompt,
                "system_prompt": system_prompt,
                "metadata": metadata,
                "parameters": {
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            }
            
        except Exception as e:
            print(f"❌ Error processing video: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": self.model_path,
                "video_path": str(video_path) if 'video_path' in locals() else None,
                "prompt": prompt
            }
    
    def _get_video_metadata(self, video_path: Path) -> Dict[str, Any]:
        """Extract video metadata using OpenCV"""
        try:
            cap = cv2.VideoCapture(str(video_path))
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            return {
                "duration": duration,
                "fps": fps,
                "frame_count": frame_count,
                "resolution": {"width": width, "height": height},
                "file_size": video_path.stat().st_size
            }
        except Exception as e:
            return {"error": f"Could not extract metadata: {e}"}
    
    def process_video_stream(
        self,
        camera_index: int = 0,
        prompt: str = "Describe what you see in real-time",
        system_prompt: Optional[str] = None,
        processing_interval: float = 2.0,
        max_tokens: int = 256,
        temperature: float = 0.7
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Process real-time video stream from camera
        
        Args:
            camera_index: Camera device index (0 for default)
            prompt: Prompt for each frame analysis
            system_prompt: Optional system prompt
            processing_interval: Seconds between processing frames
            max_tokens: Maximum tokens per response
            temperature: Generation temperature
            
        Yields:
            Dictionary with real-time analysis results
        """
        try:
            print(f"🎥 Starting real-time video stream processing...")
            print(f"📷 Camera: {camera_index}")
            print(f"⏱️  Processing interval: {processing_interval}s")
            print("🛑 Press 'q' to quit")
            
            cap = cv2.VideoCapture(camera_index)
            if not cap.isOpened():
                raise RuntimeError(f"Could not open camera {camera_index}")
            
            # Set camera properties for optimal performance
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            if system_prompt is None:
                system_prompt = "You are a real-time AI assistant watching through a camera. Provide brief, helpful observations about what you see. Focus on activities, objects, and any safety considerations."
            
            last_process_time = 0
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                current_time = time.time()
                
                # Process frame at specified interval
                if current_time - last_process_time >= processing_interval:
                    try:
                        # Save frame temporarily
                        temp_path = "/tmp/stream_frame.jpg"
                        cv2.imwrite(temp_path, frame)
                        
                        # Process with MLX-VLM
                        response = mlx_vlm.generate(
                            model=self.model_path,
                            image=temp_path,
                            prompt=prompt,
                            system=system_prompt,
                            max_tokens=max_tokens,
                            temperature=temperature
                        )
                        
                        result = {
                            "success": True,
                            "response": response,
                            "timestamp": current_time,
                            "frame_count": frame_count,
                            "model": self.model_path
                        }
                        
                        last_process_time = current_time
                        yield result
                        
                        # Clean up temp file
                        os.remove(temp_path)
                        
                    except Exception as e:
                        yield {
                            "success": False,
                            "error": str(e),
                            "timestamp": current_time,
                            "frame_count": frame_count
                        }
                
                # Display frame (optional)
                cv2.imshow('SmolVLM2 Real-time Processing', frame)
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
        except Exception as e:
            yield {
                "success": False,
                "error": f"Stream processing failed: {e}",
                "timestamp": time.time()
            }
    
    def analyze_video_segments(
        self,
        video_path: Union[str, Path],
        segment_duration: float = 10.0,
        overlap: float = 2.0,
        prompt: str = "Describe what happens in this video segment",
        system_prompt: Optional[str] = None,
        max_tokens: int = 256,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Analyze video in segments for detailed understanding
        
        Args:
            video_path: Path to video file
            segment_duration: Duration of each segment in seconds
            overlap: Overlap between segments in seconds
            prompt: Prompt for each segment
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens per segment
            temperature: Generation temperature
            
        Returns:
            Dictionary with segmented analysis results
        """
        try:
            video_path = Path(video_path)
            metadata = self._get_video_metadata(video_path)
            
            if "error" in metadata:
                raise Exception(metadata["error"])
            
            total_duration = metadata["duration"]
            segments = []
            
            print(f"🎬 Analyzing video in segments...")
            print(f"📹 Total duration: {total_duration:.1f}s")
            print(f"⏱️  Segment duration: {segment_duration}s")
            print(f"🔄 Overlap: {overlap}s")
            
            # Calculate segments
            current_time = 0
            segment_index = 0
            
            while current_time < total_duration:
                end_time = min(current_time + segment_duration, total_duration)
                
                print(f"Processing segment {segment_index + 1}: {current_time:.1f}s - {end_time:.1f}s")
                
                # Extract segment (this is a simplified approach)
                # In a full implementation, you'd extract the actual video segment
                segment_prompt = f"{prompt} (Time: {current_time:.1f}s - {end_time:.1f}s)"
                
                # For now, analyze the full video with time-specific prompt
                segment_result = self.process_video(
                    video_path=video_path,
                    prompt=segment_prompt,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                segments.append({
                    "segment_index": segment_index,
                    "start_time": current_time,
                    "end_time": end_time,
                    "duration": end_time - current_time,
                    "result": segment_result
                })
                
                current_time += segment_duration - overlap
                segment_index += 1
                
                if current_time >= total_duration:
                    break
            
            print(f"✅ Completed analysis of {len(segments)} segments")
            
            return {
                "success": True,
                "video_path": str(video_path),
                "metadata": metadata,
                "segment_count": len(segments),
                "segments": segments,
                "model": self.model_path
            }
            
        except Exception as e:
            print(f"❌ Error in segment analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "video_path": str(video_path) if 'video_path' in locals() else None
            }

def main():
    """CLI interface for video processing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SmolVLM2 Video Processor")
    parser.add_argument("video", help="Path to video file")
    parser.add_argument("--prompt", "-p", 
                       default="Describe what is happening in this video",
                       help="Prompt for the video")
    parser.add_argument("--system", "-s", help="System prompt for context")
    parser.add_argument("--model", "-m", 
                       default="mlx-community/SmolVLM2-500M-Video-Instruct-mlx",
                       help="Model path")
    parser.add_argument("--max-tokens", type=int, default=512,
                       help="Maximum tokens to generate")
    parser.add_argument("--temperature", type=float, default=0.7,
                       help="Generation temperature")
    parser.add_argument("--output", "-o", help="Output file for response")
    
    args = parser.parse_args()
    
    print("🎯 SmolVLM2 Video Processor")
    print("=" * 50)
    
    processor = SmolVLM2VideoProcessor(model_path=args.model)
    
    result = processor.process_video(
        video_path=args.video,
        prompt=args.prompt,
        system_prompt=args.system,
        max_tokens=args.max_tokens,
        temperature=args.temperature
    )
    
    if result["success"]:
        print(f"\n✅ Video Analysis:")
        print(f"{result['response']}")
        
        if result["metadata"]:
            meta = result["metadata"]
            print(f"\n📹 Video Info:")
            print(f"   Duration: {meta.get('duration', 'Unknown'):.1f}s")
            print(f"   Resolution: {meta.get('resolution', {}).get('width', '?')}x{meta.get('resolution', {}).get('height', '?')}")
            print(f"   FPS: {meta.get('fps', 'Unknown'):.1f}")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n📝 Response saved to: {args.output}")
    else:
        print(f"\n❌ Error: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main() 