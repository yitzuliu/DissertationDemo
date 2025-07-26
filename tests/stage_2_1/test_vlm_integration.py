#!/usr/bin/env python3
"""
Test VLM Integration with Backend

This script tests the actual VLM response format and State Tracker integration
to ensure we're correctly processing the model output.
"""

import asyncio
import httpx
import json
import base64
import io
from PIL import Image, ImageDraw

def create_test_image():
    """Create a simple test image of coffee brewing"""
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple coffee cup
    draw.rectangle([150, 150, 250, 250], outline='black', width=3)
    draw.text((160, 120), "Coffee Cup", fill='black')
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    img_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return f"data:image/jpeg;base64,{img_data}"

async def test_vlm_response_format():
    """Test actual VLM response format from backend"""
    print("🧪 Testing VLM Response Format...")
    
    # Create test image
    test_image = create_test_image()
    print("✅ Test image created")
    
    # Prepare request
    request_data = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Describe what you see in this image. Focus on coffee-related activities."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": test_image
                        }
                    }
                ]
            }
        ],
        "max_tokens": 150
    }
    
    try:
        # Send request to backend
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("📡 Sending request to backend...")
            response = await client.post(
                "http://localhost:8000/v1/chat/completions",
                json=request_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Backend response received")
                
                # Analyze response structure
                print("\n📋 Response Structure Analysis:")
                print(f"Response keys: {list(result.keys())}")
                
                if 'choices' in result:
                    print(f"Number of choices: {len(result['choices'])}")
                    
                    for i, choice in enumerate(result['choices']):
                        print(f"\nChoice {i}:")
                        print(f"  Keys: {list(choice.keys())}")
                        
                        if 'message' in choice:
                            message = choice['message']
                            print(f"  Message keys: {list(message.keys())}")
                            
                            if 'content' in message:
                                content = message['content']
                                print(f"  Content type: {type(content)}")
                                
                                if isinstance(content, str):
                                    print(f"  Content (first 100 chars): {content[:100]}...")
                                    print(f"  Content length: {len(content)}")
                                    
                                    # Test State Tracker processing
                                    print("\n🔄 Testing State Tracker Processing:")
                                    state_response = await client.post(
                                        "http://localhost:8000/api/v1/state/process",
                                        json={"text": content}
                                    )
                                    
                                    if state_response.status_code == 200:
                                        state_result = state_response.json()
                                        print("✅ State Tracker processed successfully")
                                        print(f"  Updated: {state_result.get('updated')}")
                                        
                                        current_state = state_result.get('current_state')
                                        if current_state:
                                            print(f"  Task: {current_state.get('task_id')}")
                                            print(f"  Step: {current_state.get('step_index')}")
                                            print(f"  Confidence: {current_state.get('confidence', 0):.2f}")
                                    else:
                                        print(f"❌ State Tracker failed: {state_response.status_code}")
                                        print(f"  Error: {state_response.text}")
                                
                                elif isinstance(content, list):
                                    print(f"  Content is list with {len(content)} items")
                                    for j, item in enumerate(content):
                                        print(f"    Item {j}: {type(item)} - {str(item)[:50]}...")
                                
                                else:
                                    print(f"  Unexpected content format: {content}")
                
                # Check current state
                print("\n📊 Current State Check:")
                state_response = await client.get("http://localhost:8000/api/v1/state")
                if state_response.status_code == 200:
                    state_data = state_response.json()
                    print(f"  Has current state: {state_data.get('summary', {}).get('has_current_state')}")
                    print(f"  History size: {state_data.get('summary', {}).get('history_size')}")
                
            else:
                print(f"❌ Backend request failed: {response.status_code}")
                print(f"Error: {response.text}")
                
    except httpx.ConnectError:
        print("❌ Cannot connect to backend. Is the server running on localhost:8000?")
        print("Start backend with: cd src/backend && python main.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_vlm_response_format())