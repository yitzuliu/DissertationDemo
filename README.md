# 🤖 AI Manual Assistant

**The Universal Manual for Everything - An AI that sees, understands, and guides**

Transform any real-world task into a guided, step-by-step experience using computer vision and contextual AI.

## 🌟 **The Vision**

Imagine never being stuck on a task again. Whether you're cooking your first meal, fixing a broken device, assembling furniture, or learning a new skill - you have an intelligent companion that:

- **👀 Sees everything** you're working with through your camera
- **🧠 Understands the context** of what you're trying to accomplish  
- **🗣️ Guides you step-by-step** through any process with personalized instructions
- **⚡ Adapts in real-time** as you progress, celebrating successes and preventing mistakes

## 🎯 **The Core Concept**

This isn't just another chatbot or simple object detection system. This is **contextual activity recognition** - an AI that transforms your camera into an intelligent manual for any hands-on task.

**The breakthrough:** Instead of you describing what you see, the AI sees what you see - whether through continuous video understanding or intelligent image analysis. Instead of generic instructions, you get guidance based on your actual setup, tools, and progress.

**The result:** Like having an experienced mentor standing beside you, watching your work and understanding your progress, providing exactly the guidance you need as your work unfolds.

> **🧪 Current Development:** Testing both continuous video processing and intelligent image capture to determine the most reliable approach for real-time guidance.

## 🏗️ **System Architecture**

### 📊 **Three-Layer Architecture**

```
📱 Frontend Layer (Port 5500)
    ↓ HTTP Requests
🔄 Backend Layer (Port 8000) 
    ↓ Model API Calls
🧠 Model Server Layer (Port 8080)
```

#### **Layer 1: Frontend (Port 5500)**
- Real-time camera interface
- User interaction controls
- Responsive UI for AI guidance
- Cross-platform support

#### **Layer 2: Backend (Port 8000)**
- Unified API gateway
- Image preprocessing pipeline
- Model selection and routing
- Configuration management

#### **Layer 3: Model Server (Port 8080)**
- Vision-Language Models
- Real-time inference
- OpenAI-compatible API
- Resource management

## 🎯 **Supported Models**

Our system is designed to be model-agnostic, allowing for the integration of various Vision-Language Models. Each model runs in its own dedicated server process.

**✅ Actively Supported & Tested Models:**
- **Moondream2**: A lightweight and very fast model, great for quick analysis.
- **SmolVLM / SmolVLM2**: Efficient models designed for a balance of performance and capability.
- **Phi-3.5-Vision (MLX)**: A powerful model from Microsoft, optimized for Apple Silicon via MLX for top-tier performance.
- **LLaVA-v1.6 (MLX)**: An excellent conversational model, optimized for Apple Silicon. Note: It excels with photographic images but consistently fails on certain synthetic images (e.g., simple geometric shapes on a flat background) due to an underlying `mlx-vlm` library issue.
- **YOLOv8**: A specialized, high-speed object detection model.

> **⚠️ One Model at a Time:** Due to memory constraints on typical development machines, only one model server should be run at a time. To switch models, stop the current server and start a different one.

## 🚀 **Quick Start**

1.  **Clone and Setup Environment**:
   ```bash
   git clone https://github.com/yitzuliu/DissertationDemo.git
   cd destination_code
    # Activate your python virtual environment
   source ai_vision_env/bin/activate
   ```

2.  **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
    # Install MLX for Apple Silicon if you plan to use MLX models
    pip install mlx-vlm
   ```

3.  **Run the System (3-Layer Architecture)**:
    You need to run three separate components in three different terminal sessions.

    **a. Start a Model Server (Choose one):**
   ```bash
    # Example: Start the LLaVA MLX server
    python src/models/llava_mlx/run_llava_mlx.py
    
    # Or, start the Phi-3.5 Vision MLX server
    # python "src/models/Phi_3.5_Vision MLX/run_phi3_vision_optimized.py"
    ```

    **b. Start the Backend Server (New Terminal):**
    ```bash
   python src/backend/main.py
    ```
   
    **c. Start the Frontend Server (New Terminal):**
    ```bash
   cd src/frontend && python -m http.server 5500
   ```

4.  **Open the Assistant**:
    Open your web browser and navigate to `http://localhost:5500`.

For more detailed instructions, see the [Developer Setup Guide](./docs/DEVELOPER_SETUP.md).

## 📖 **Documentation**

### **Complete Documentation**
- **[System Architecture](./docs/ARCHITECTURE.md)** - Complete system design and component overview
- **[Developer Setup Guide](./docs/DEVELOPER_SETUP.md)** - Step-by-step development environment setup
- **[Model Comparison Guide](./docs/MODEL_COMPARISON.md)** - Detailed comparison of all supported models
- **[API Documentation](./docs/API.md)** - Complete API reference and examples

### **Project Guides**
- **[Integration Plan](./integration_plan.md)** - Project roadmap and implementation strategy
- **[VLM Enhancement Guide](./VLM_Enhancement_Guide.md)** - Optimization guide for vision models
- **[TODO List](./TODO_LIST.md)** - Current development tasks and priorities

## ✨ **Key Features**

**🎯 Core Vision (Testing Multiple Approaches):**
- **👁️ Intelligent Vision** - AI understands your work context, either through continuous video or smart image analysis
   - **🔄 Real-time Processing** - Continuous scene understanding and object recognition
   - **🎯 Context-Aware** - Understands activities and workflows, not just objects  
   - **💡 Adaptive Guidance** - Learns your preferences and adjusts instruction style
   - **⚡ Local Processing** - Works offline with optimized performance
- **🧠 Context Understanding** - Tracks your progress and provides relevant guidance
- **⚡ Real-time Guidance** - Provides contextual help as you work
- **🎯 Activity Recognition** - Understands what you're doing, not just what objects are present
- **💡 Adaptive Mentoring** - Learns your pace and provides encouragement and corrections
- **📱 Flexible Input** - Currently testing both continuous video and intelligent image capture
- **💰 Cost-Effective** - Efficient local processing without expensive cloud dependencies

**🧪 Current Testing:**
- **Video Approach**: Continuous understanding with temporal reasoning (SmolVLM2-Video)
- **Image Approach**: High-frequency intelligent capture with context memory (SmolVLM)

## 🎬 **Real-World Examples**

### 🍳 **Cooking Assistant**
```
AI sees [eggs, pan, stove, spatula, salt, butter]
AI recognizes "scrambled eggs preparation setup"
User asks "How do I make scrambled eggs?"

AI Response:
"Perfect! I can see you have everything needed for scrambled eggs.
1. First, crack 2-3 eggs into a bowl
2. Heat your pan on medium heat with a bit of butter
3. I'll watch and tell you when it's ready..."
```

### 🔧 **Repair Assistant**
```
AI sees [laptop, screwdriver, replacement_part, manual]
AI recognizes "laptop repair/upgrade scenario"  
User asks "How do I replace this part?"

AI Response:
"I can see you're working on a laptop repair. Based on the part you're holding:
1. First, ensure the laptop is powered off and unplugged
2. I notice you have the right screwdriver - remove the back panel screws
3. I'll guide you to the correct component location..."
```

### 🪑 **Assembly Assistant**
```
AI sees [furniture_parts, screws, allen_wrench, instruction_manual]
AI recognizes "furniture assembly in progress"
User asks "I'm lost, what's next?"

AI Response:
"I can see your progress! You've completed the base frame correctly.
Next steps:
1. Take the long shelf piece (I can see it to your left)
2. Align it with the middle brackets
3. Use the 40mm screws - I'll confirm when you have the right ones..."
```

## 🛠️ **Tech Stack**

### **Frontend**
- HTML5, CSS3, JavaScript
- Real-time camera integration
- Responsive design with modern UI

### **Backend**
- FastAPI (Python)
- Unified model server architecture
- Image preprocessing pipeline

### **AI Models**
- SmolVLM & SmolVLM2
- Moondream2
- Phi-3.5-Vision (MLX Optimized)
- LLaVA (MLX Optimized)
- YOLO8

### **Infrastructure**
- Three-layer architecture (Frontend → Backend → Model Server)
- Configuration management system
- Comprehensive logging and monitoring

## 💡 **What Makes This Different**

### **🔍 Unlike YouTube Tutorials:**
- **No more rewinding** to see what tool they're using
- **No assumptions** about what you have or your skill level
- **No generic instructions** that don't match your specific situation
- **Continuous adaptation** to your actual progress as it happens

### **🤖 Unlike Other AI Assistants:**
- **Continuously watches your workspace** like human eyes, not relying on your descriptions
- **Understands ongoing activities** and temporal sequences, not just static objects
- **Provides flowing progress guidance**: "I can see you've completed step 1 and are moving to step 2..."
- **Prevents mistakes as they develop** in real-time: "I see you reaching for that tool - use the smaller one instead..."

### **📚 Unlike Traditional Manuals:**
- **Continuously adaptive guidance** - responds to your ongoing activities in real-time
- **Natural dialogue** - ask questions while working, get immediate contextual answers
- **Temporal memory** - remembers your entire work session and progress flow
- **Real-time encouragement** - celebrates progress as it happens: "Perfect! You're doing great!"

### **🎯 The Result:**
**Confidence instead of frustration. Flowing guidance instead of fragmented instructions. Natural mentoring instead of robotic responses.**

## 🌍 **Universal Application**

This system is designed to help with:
- **🍳 Cooking** - From basic meals to complex recipes
- **🔧 Repairs** - Electronics, appliances, vehicles
- **🪑 Assembly** - Furniture, electronics, DIY projects  
- **📚 Learning** - New skills, hobbies, techniques
- **🏠 Home improvement** - Installation, maintenance, decoration
- **🎨 Creative projects** - Art, crafts, building

## 🤝 **Contributing**

We welcome contributions! Please see our [Developer Setup Guide](./docs/DEVELOPER_SETUP.md) for detailed instructions on:
- Setting up the development environment
- Code style guidelines
- Testing procedures
- Submitting pull requests

## 📄 **License**

This project is licensed under the [MIT License](./LICENSE).

## 🔗 **Links**

- **GitHub Repository**: [AI Manual Assistant](https://github.com/yitzuliu/DissertationDemo)
- **Documentation**: See [docs](./docs/) directory
- **Issues**: [GitHub Issues](https://github.com/yitzuliu/DissertationDemo/issues)

---

**Built with ❤️ for makers, learners, and anyone who wants to confidently tackle any hands-on task.** 