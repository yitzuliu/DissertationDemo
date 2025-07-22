# AI Manual Assistant - Frequently Asked Questions

## General Questions

### Q: What is the AI Manual Assistant?
A: The AI Manual Assistant is a real-time visual guidance system that uses Vision-Language Models (VLMs) to provide contextual assistance for hands-on tasks. It acts like an intelligent mentor that watches your work through your camera and provides step-by-step guidance.

### Q: What makes this different from other AI assistants?
A: Unlike traditional AI assistants that rely on text descriptions, our system continuously watches your workspace through your camera, understands ongoing activities, and provides real-time guidance based on what it actually sees happening.

### Q: What types of tasks can it help with?
A: The system is designed to help with various hands-on activities including:
- 🍳 Cooking (recipes, techniques, timing)
- 🔧 Repairs (electronics, appliances, vehicles)
- 🪑 Assembly (furniture, electronics, DIY projects)
- 📚 Learning (new skills, hobbies, techniques)
- 🏠 Home improvement (installation, maintenance)
- 🎨 Creative projects (art, crafts, building)

## Technical Questions

### Q: What are the system requirements?
A: **Minimum Requirements:**
- macOS (Apple Silicon M1/M2/M3 recommended) or Linux
- Python 3.9+
- 16GB RAM minimum (32GB recommended)
- 50GB free disk space
- Webcam or camera access

### Q: Which model should I use?
A: **For most users, we recommend:**
1. **SmolVLM2-500M-Video-Instruct** - Best overall performance (66.0% VQA accuracy)
2. **SmolVLM-500M-Instruct** - Excellent alternative (64.0% VQA accuracy)
3. **Moondream2** - Fastest inference (4.06s, good for speed-critical applications)

See our [Model Comparison Guide](./MODEL_COMPARISON.md) for detailed analysis.

### Q: Can I run multiple models at the same time?
A: No, due to memory constraints on typical development machines, only one model server should be run at a time. To switch models, stop the current server and start a different one.

### Q: Do I need an internet connection?
A: No! The system works completely offline once set up. All AI processing happens locally on your machine, ensuring privacy and eliminating dependency on cloud services.

### Q: Is my data private?
A: Yes, absolutely. All processing happens locally on your device. No images or data are sent to external servers or cloud services.

## Setup and Installation

### Q: How do I install the system?
A: Follow these steps:
1. Clone the repository
2. Create a Python virtual environment
3. Install dependencies from `requirements.txt`
4. For Apple Silicon: Install `mlx-vlm` for optimized models
5. Start the three-layer system (Model Server, Backend, Frontend)

See our [Developer Setup Guide](./DEVELOPER_SETUP.md) for detailed instructions.

### Q: I'm getting "ModuleNotFoundError" errors. What should I do?
A: This usually means:
1. Your virtual environment is not activated - run `source ai_vision_env/bin/activate`
2. You're running scripts from the wrong directory - ensure you're in the project root
3. Dependencies aren't installed - run `pip install -r requirements.txt`

### Q: The camera isn't working. How do I fix it?
A: **Common solutions:**
1. **Browser permissions**: Check camera permissions in your browser
2. **System permissions**: On macOS, check System Preferences > Security & Privacy > Camera
3. **Camera in use**: Close other applications using the camera
4. **Try different browsers**: Chrome, Firefox, Safari may behave differently

See our [Troubleshooting Guide](./TROUBLESHOOTING.md) for more camera issues.

### Q: Which ports does the system use?
A: The system uses three ports:
- **Port 5500**: Frontend (web interface)
- **Port 8000**: Backend (API gateway)
- **Port 8080**: Model Server (AI inference)

If you get port conflicts, you may need to stop other applications or modify the port settings.

## Performance and Optimization

### Q: The system is running slowly. How can I improve performance?
A: **Performance optimization tips:**
1. **Use faster models**: Moondream2 is the fastest (4.06s inference)
2. **Apple Silicon users**: Use MLX-optimized models for better performance
3. **Reduce image quality**: Lower the capture quality in frontend settings
4. **Close other applications**: Free up system memory
5. **Check system resources**: Ensure you have enough RAM available

### Q: How accurate are the AI responses?
A: **Based on VQA 2.0 testing:**
- SmolVLM2-500M-Video-Instruct: 66.0% accuracy (best)
- SmolVLM-500M-Instruct: 64.0% accuracy
- Moondream2: 56.0% accuracy
- Phi-3.5-Vision (MLX): 60.0% accuracy

See [Test Results Summary](../TEST_RESULTS_SUMMARY.md) for detailed performance data.

### Q: Can I improve the AI's accuracy?
A: **Yes, several ways:**
1. **Better lighting**: Ensure good lighting in your workspace
2. **Clear camera view**: Keep the camera clean and unobstructed
3. **Stable positioning**: Minimize camera shake and movement
4. **Specific prompts**: Ask clear, specific questions
5. **Model selection**: Use higher-accuracy models for important tasks

## Development and Customization

### Q: Can I add new models to the system?
A: Yes! The system is designed to be model-agnostic. To add a new model:
1. Create a new model directory in `src/models/`
2. Implement the model following the existing patterns
3. Add a configuration file in `src/config/model_configs/`
4. Create a run script for the model server

### Q: How do I modify the system for my specific use case?
A: **Customization options:**
1. **Prompts**: Modify default prompts in model configurations
2. **Image processing**: Adjust preprocessing parameters in the backend
3. **UI**: Customize the frontend interface
4. **Models**: Train or fine-tune models for specific domains

### Q: Is there an API I can use?
A: Yes! The system exposes OpenAI-compatible APIs:
- **Backend API**: `http://localhost:8000/v1/chat/completions`
- **Model Server API**: `http://localhost:8080/v1/chat/completions`

See our [API Documentation](./API.md) for complete reference.

### Q: Can I integrate this with other applications?
A: Absolutely! The system provides standard REST APIs that can be integrated with other applications. The OpenAI-compatible format makes it easy to integrate with existing tools and workflows.

## Future Development

### Q: What new features are planned?
A: **Upcoming enhancements:**
1. **RAG & State Tracker Integration**: Advanced context management and memory
2. **Mobile Support**: Smartphone and tablet compatibility
3. **Offline Mode Improvements**: Better offline capabilities
4. **Performance Optimizations**: Faster inference and lower resource usage

See [RAG & State Tracker Integration Approaches](./RAG_STATE_TRACKER_INTEGRATION_APPROACHES.md) for detailed planning.

### Q: How can I contribute to the project?
A: We welcome contributions! You can:
1. **Report issues**: Submit bug reports and feature requests
2. **Improve documentation**: Help improve guides and documentation
3. **Add models**: Integrate new Vision-Language Models
4. **Optimize performance**: Contribute performance improvements
5. **Test and feedback**: Test the system and provide feedback

See our [Developer Setup Guide](./DEVELOPER_SETUP.md) for contribution guidelines.

### Q: Is there a roadmap for the project?
A: Yes! The project follows a structured development approach:
1. **Current Phase**: Model optimization and testing framework
2. **Next Phase**: RAG and State Tracker integration
3. **Future Phases**: Mobile support, advanced features, and scaling

## Troubleshooting

### Q: The model server won't start. What should I check?
A: **Common issues:**
1. **Memory**: Ensure you have enough RAM (16GB minimum)
2. **Dependencies**: Check all required packages are installed
3. **Python version**: Ensure Python 3.9+ is being used
4. **Virtual environment**: Make sure it's activated
5. **Port conflicts**: Check if port 8080 is already in use

### Q: I'm getting connection errors between components. How do I fix this?
A: **Connection troubleshooting:**
1. **Check all services are running**: Frontend, Backend, Model Server
2. **Verify ports**: Ensure 5500, 8000, 8080 are available
3. **Check firewall**: Ensure local connections are allowed
4. **Restart services**: Try restarting all components in order

### Q: The AI responses don't make sense. What's wrong?
A: **Response quality issues:**
1. **Model selection**: Try a different model (SmolVLM2 recommended)
2. **Image quality**: Ensure good lighting and clear camera view
3. **Prompt clarity**: Ask more specific, clear questions
4. **Model state**: Restart the model server to clear any state issues

For more detailed troubleshooting, see our [Troubleshooting Guide](./TROUBLESHOOTING.md).

---

**Need more help?** 
- Check our [Getting Started Guide](../GETTING_STARTED.md)
- Review the [Troubleshooting Guide](./TROUBLESHOOTING.md)
- See the [Developer Setup Guide](./DEVELOPER_SETUP.md)

**Last Updated**: January 2025