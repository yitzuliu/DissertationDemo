# AI Manual Assistant - Frequently Asked Questions (FAQ)

## General Questions

### Q: What is the AI Manual Assistant?
**A:** The AI Manual Assistant is a real-time vision-guided system that uses advanced AI to provide step-by-step assistance for hands-on tasks. It sees what you see through your camera and provides contextual guidance for cooking, repairs, assembly, and more.

**🧪 Current Development:** The system is testing two approaches - enhanced image analysis and continuous video understanding - to determine the optimal solution for real-time guidance.

### Q: What makes this different from other AI assistants?
**A:** Unlike text-based AI assistants, our system actually sees your workspace through your camera. It understands the context of what you're doing and provides visual confirmation of your progress, preventing mistakes in real-time. We're currently testing both image-based and video-based approaches to find the most reliable solution.

### Q: Does it work offline?
**A:** Yes! The system is designed for local processing with edge-optimized models. Once set up, it works without internet connectivity for basic functionality.

## Technical Questions

### Q: What are the system requirements?
**A:** 
- macOS (M1/M2/M3 recommended) or Linux
- Python 3.8+ (3.10 recommended)
- 16GB RAM minimum (32GB recommended)
- 50GB free disk space
- Camera (built-in or external)

### Q: Which AI models are supported?
**A:** We support multiple vision-language models for testing different approaches:

**🏆 Best Performance Models (VQA 2.0 Tested):**
- **SmolVLM2-500M-Video-Instruct** - Best overall (66.0% VQA accuracy, 6.61s)
- **SmolVLM-500M-Instruct** - Excellent alternative (64.0% VQA accuracy, 5.98s)
- **Moondream2** - Fastest inference (56.0% VQA accuracy, 4.06s)

**Additional Models:**
- **Phi-3.5-Vision (MLX)** - High-accuracy analysis (60.0% VQA accuracy, 13.61s)
- **LLaVA-MLX** - Conversational (34.0% VQA accuracy, 17.86s) ⚠️ Underperforming
- **YOLO8** - Real-time object detection

### Q: Can I switch between models?
**A:** Yes! The system supports dynamic model switching. You can change models through the configuration or by restarting with a different model server.

### Q: What ports does the system use?
**A:** The system uses a three-layer architecture:
- Frontend: Port 5500
- Backend: Port 8000
- Model Server: Port 8080

## Setup and Installation

### Q: How do I install the system?
**A:** Follow these steps:
1. Clone the repository
2. Create a virtual environment
3. Install dependencies
4. Start the services

See our [Developer Setup Guide](./DEVELOPER_SETUP.md) for detailed instructions.

### Q: The installation is taking a long time. Is this normal?
**A:** Yes, the first installation downloads large AI models (~8GB). This is normal and only happens once.

### Q: I'm getting permission errors on macOS. What should I do?
**A:** Grant camera permissions when prompted. You may also need to allow the application in System Preferences > Security & Privacy.

## Usage Questions

### Q: How accurate is the object recognition?
**A:** Accuracy varies by model and approach, based on our latest VQA 2.0 testing:

**🏆 Best Performing Models:**
- **SmolVLM2-500M-Video-Instruct**: 66.0% VQA accuracy, 6.61s average
- **SmolVLM-500M-Instruct**: 64.0% VQA accuracy, 5.98s average
- **Moondream2**: 56.0% VQA accuracy, 4.06s average (fastest)

**Other Models:**
- **Phi-3.5-Vision (MLX)**: 60.0% VQA accuracy, 13.61s average
- **LLaVA-MLX**: 34.0% VQA accuracy, 17.86s average ⚠️ Underperforming

See our [Model Comparison Guide](./MODEL_COMPARISON.md) for detailed benchmarks and testing status.

### Q: Can it help with any type of task?
**A:** The system is designed for hands-on tasks including:
- Cooking and food preparation
- Electronics and appliance repair
- Furniture assembly
- Home improvement projects
- Learning new skills
- Creative projects

### Q: How do I get better results?
**A:** For optimal performance:
- Ensure good lighting
- Keep objects clearly visible
- Speak clearly when asking questions
- Provide context about what you're trying to accomplish
- Use the recommended models (SmolVLM2 or SmolVLM for best results)

### Q: Why does the LLaVA model have performance issues?
**A:** The LLaVA-MLX model has shown significant performance degradation in recent tests:
- **Previous Performance**: 56% VQA accuracy
- **Current Performance**: 34% VQA accuracy
- **Root Cause**: Model reloading for each image causes overhead and state management issues
- **Recommendation**: Use SmolVLM2 or SmolVLM instead for better performance

### Q: Which model should I use for my specific needs?
**A:** Based on our VQA 2.0 testing:

**For Production Use:**
- **Best Overall**: SmolVLM2-500M-Video-Instruct (66.0% accuracy, good speed)
- **Fastest**: Moondream2 (4.06s average, 56.0% accuracy)
- **Most Reliable**: SmolVLM-500M-Instruct (64.0% accuracy, stable performance)

**For Different Scenarios:**
- **Quick Testing (10 questions)**: Moondream2 (~41 seconds)
- **Standard Testing (15 questions)**: SmolVLM2 (~98 seconds)
- **Comprehensive Testing (20 questions)**: SmolVLM2 (~130 seconds)

## Troubleshooting

### Q: The camera feed is not working. What should I check?
**A:** 
1. Check camera permissions
2. Ensure no other apps are using the camera
3. Restart the frontend service
4. Check browser console for errors

### Q: The AI responses are slow or inaccurate. How can I fix this?
**A:**
1. Check system resources (CPU/Memory usage)
2. Try switching to a faster model (Moondream2 for speed, SmolVLM2 for balance)
3. Improve lighting conditions
4. Restart the model server
5. Avoid using LLaVA-MLX due to performance issues

### Q: I'm getting "Model server not responding" errors. What should I do?
**A:**
1. Check if the model server is running (port 8080)
2. Restart the model server
3. Check log files for error messages
4. Ensure sufficient system memory
5. Try a different model if one is failing

### Q: The system is using too much memory. How can I reduce usage?
**A:**
1. Switch to Moondream2 (uses only 0.10GB memory)
2. Use SmolVLM-500M-Instruct (uses 1.58GB)
3. Close other applications
4. Restart the system to clear memory
5. Consider quantized models for lower memory usage

## Performance and Optimization

### Q: How can I improve response time?
**A:**
- Use Moondream2 for fastest responses (4.06s average)
- Use SmolVLM2 for best balance (6.61s average)
- Ensure good hardware (Apple Silicon recommended)
- Close unnecessary applications
- Use lower image quality settings if needed

### Q: Can I run multiple models simultaneously?
**A:** No, the system is designed to run only one model at a time due to memory considerations. This ensures optimal performance and prevents memory issues. To use a different model, stop the current one and start the desired model.

### Q: How do I optimize for my specific hardware?
**A:** See our [VLM Enhancement Guide](../VLM_Enhancement_Guide.md) for hardware-specific optimization tips and guidance on testing both image and video approaches on your hardware.

### Q: What are the time estimates for different test scenarios?
**A:** Based on our VQA 2.0 testing:

**10 Questions Test:**
- Moondream2: ~41 seconds
- SmolVLM2: ~66 seconds
- SmolVLM: ~60 seconds
- Phi-3.5: ~136 seconds
- LLaVA-MLX: ~179 seconds

**15 Questions Test:**
- Moondream2: ~55 seconds
- SmolVLM2: ~98 seconds
- SmolVLM: ~90 seconds
- Phi-3.5: ~204 seconds
- LLaVA-MLX: ~260 seconds

**20 Questions Test:**
- Moondream2: ~74 seconds
- SmolVLM2: ~130 seconds
- SmolVLM: ~120 seconds
- Phi-3.5: ~272 seconds
- LLaVA-MLX: ~346 seconds

## Development and Customization

### Q: Can I add support for new models?
**A:** Yes! The system is designed to be extensible. See our [Developer Setup Guide](./DEVELOPER_SETUP.md) for information on adding new models.

### Q: How do I customize the prompts?
**A:** You can modify prompts in the model configuration files located in `src/config/model_configs/`. Each model has its own configuration file.

### Q: Can I contribute to the project?
**A:** Absolutely! We welcome contributions. Please see our [Developer Setup Guide](./DEVELOPER_SETUP.md) for contribution guidelines.

## Advanced Features

### Q: Does the system support video analysis?
**A:** Yes, we're currently testing SmolVLM2-Video for continuous video understanding. This approach is being evaluated against our current image analysis approach to determine which provides better real-time guidance. The video model can process 5-10 second segments for temporal understanding and activity recognition.

### Q: Can I use the system programmatically?
**A:** Yes! We provide a complete REST API. See our [API Documentation](./API.md) for endpoint details and examples.

### Q: Is there a mobile app?
**A:** Currently, the system runs as a web application that works on mobile browsers. Native mobile apps are planned for future releases.

## Testing and Evaluation

### Q: How do you evaluate model performance?
**A:** We use the VQA 2.0 (Visual Question Answering) benchmark with real COCO dataset questions and images. Our testing framework evaluates:
- **Simple Accuracy**: Binary correct/incorrect answers
- **VQA Accuracy**: Standard VQA 2.0 evaluation with partial credit
- **Inference Time**: Average response time per question
- **Memory Usage**: Resource consumption tracking

### Q: Where can I find detailed test results?
**A:** See `src/testing/vqa_test_result.md` for comprehensive test results, time analysis, and performance comparisons.

### Q: How often do you update model performance data?
**A:** We regularly test and update model performance data. The latest results are from July 19, 2025, using VQA 2.0 testing framework.

## Support and Community

### Q: Where can I get help?
**A:** 
- Check this FAQ first
- Read our documentation in the [docs](../) directory
- Create an issue on GitHub
- Contact the development team

### Q: How do I report bugs?
**A:** Please create a detailed issue on our GitHub repository including:
- System information
- Steps to reproduce
- Error messages
- Log files if available

### Q: Is there a community forum?
**A:** We primarily use GitHub Issues for community support and discussions.

## Future Development

### Q: What features are planned for future releases?
**A:** See our [TODO List](../TODO_LIST.md) for current development priorities and planned features.

### Q: When will the next version be released?
**A:** We follow an iterative development approach. Check our GitHub repository for the latest releases and roadmap updates.

### Q: Will there be commercial licensing options?
**A:** Currently, the project is open source under the MIT License. Commercial licensing options may be considered in the future.

---

**Last Updated**: July 19, 2025  
**Test Framework**: VQA 2.0 Standard Evaluation  
**Hardware**: MacBook Air M3, 16GB RAM 