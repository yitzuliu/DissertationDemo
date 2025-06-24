# AI Manual Assistant - Frequently Asked Questions (FAQ)

## General Questions

### Q: What is the AI Manual Assistant?
**A:** The AI Manual Assistant is a real-time vision-guided system that uses advanced AI to provide step-by-step assistance for hands-on tasks. It sees what you see through your camera and provides contextual guidance for cooking, repairs, assembly, and more.

### Q: What makes this different from other AI assistants?
**A:** Unlike text-based AI assistants, our system actually sees your workspace through your camera. It understands the context of what you're doing and provides visual confirmation of your progress, preventing mistakes in real-time.

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
**A:** We support multiple vision-language models:
- **SmolVLM** - Primary lightweight model for real-time interaction
- **Phi-3 Vision** - High-accuracy model for complex tasks
- **LLaVA** - Excellent for multi-turn conversations
- **YOLO8** - Real-time object detection
- **Moondream2** - Efficient specialized processing

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
**A:** Accuracy varies by model:
- SmolVLM: ~77% overall accuracy
- Phi-3 Vision: ~88% overall accuracy
- LLaVA: ~86% overall accuracy

See our [Model Comparison Guide](./MODEL_COMPARISON.md) for detailed benchmarks.

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
2. Try switching to a faster model (SmolVLM for speed)
3. Improve lighting conditions
4. Restart the model server

### Q: I'm getting "Model server not responding" errors. What should I do?
**A:**
1. Check if the model server is running (port 8080)
2. Restart the model server
3. Check log files for error messages
4. Ensure sufficient system memory

### Q: The system is using too much memory. How can I reduce usage?
**A:**
1. Switch to SmolVLM (uses less memory)
2. Close other applications
3. Restart the system to clear memory
4. Consider quantized models for lower memory usage

## Performance and Optimization

### Q: How can I improve response time?
**A:**
- Use SmolVLM for fastest responses
- Ensure good hardware (Apple Silicon recommended)
- Close unnecessary applications
- Use lower image quality settings if needed

### Q: Can I run multiple models simultaneously?
**A:** Running multiple models requires significant system resources. It's recommended to use one model at a time for optimal performance.

### Q: How do I optimize for my specific hardware?
**A:** See our [VLM Enhancement Guide](../VLM_Enhancement_Guide.md) for hardware-specific optimization tips.

## Development and Customization

### Q: Can I add support for new models?
**A:** Yes! The system is designed to be extensible. See our [Developer Setup Guide](./DEVELOPER_SETUP.md) for information on adding new models.

### Q: How do I customize the prompts?
**A:** You can modify prompts in the model configuration files located in `src/config/model_configs/`. Each model has its own configuration file.

### Q: Can I contribute to the project?
**A:** Absolutely! We welcome contributions. Please see our [Developer Setup Guide](./DEVELOPER_SETUP.md) for contribution guidelines.

## Advanced Features

### Q: Does the system support video analysis?
**A:** Yes, SmolVLM2 includes video understanding capabilities. Use the video model variant for enhanced temporal analysis.

### Q: Can I use the system programmatically?
**A:** Yes! We provide a complete REST API. See our [API Documentation](./API.md) for endpoint details and examples.

### Q: Is there a mobile app?
**A:** Currently, the system runs as a web application that works on mobile browsers. Native mobile apps are planned for future releases.

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

**Still have questions?** Create an issue on our [GitHub repository](https://github.com/yitzuliu/DissertationDemo/issues) or contact the development team. 