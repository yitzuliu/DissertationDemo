# 🤖 AI Manual Assistant

**The Universal Manual for Everything - An AI that sees, understands, and guides**

Transform any real-world task into a guided, step-by-step experience using computer vision and contextual AI with a revolutionary dual-loop memory system.

## 🌟 **The Vision**

Imagine never being stuck on a task again. Whether you're cooking your first meal, fixing a broken device, assembling furniture, or learning a new skill - you have an intelligent companion that:

- **👀 Sees everything** you're working with through your camera
- **🧠 Understands the context** of what you're trying to accomplish  
- **🗣️ Guides you step-by-step** through any process with personalized instructions
- **⚡ Adapts in real-time** as you progress, celebrating successes and preventing mistakes
- **🧠 Remembers your progress** with a sophisticated dual-loop memory system

## 🎯 **The Core Concept**

This isn't just another chatbot or simple object detection system. This is **contextual activity recognition with intelligent memory** - an AI that transforms your camera into an intelligent manual for any hands-on task.

**The breakthrough:** Instead of you describing what you see, the AI sees what you see and remembers your progress. Instead of generic instructions, you get guidance based on your actual setup, tools, and current step in the process.

**The result:** Like having an experienced mentor standing beside you, watching your work, understanding your progress, and providing exactly the guidance you need as your work unfolds.

> **🚀 Current Status:** Dual-loop memory system completed! System now features subconscious state tracking and instant query responses with 100% accuracy.

## 🏗️ **System Architecture**

### 📊 **Three-Layer Architecture with Dual-Loop Memory**

```
📱 Frontend Layer (Port 5500)
    ↓ HTTP Requests
🔄 Backend Layer (Port 8000) 
    ↓ Model API Calls
🧠 Model Server Layer (Port 8080)
    ↓ VLM Observations
🧠 Dual-Loop Memory System
    ├── 🔄 Subconscious Loop (Background State Tracking)
    └── ⚡ Instant Response Loop (User Queries)
```

#### **Layer 1: Frontend (Port 5500)**
- Real-time camera interface
- User interaction controls
- Responsive UI for AI guidance
- Cross-platform support
- Query interface for instant responses

#### **Layer 2: Backend (Port 8000)**
- Unified API gateway
- Image preprocessing pipeline
- Model selection and routing
- Configuration management
- **State Tracker integration**
- **RAG knowledge base**

#### **Layer 3: Model Server (Port 8080)**
- Vision-Language Models
- Real-time inference
- OpenAI-compatible API
- Resource management

#### **🧠 Dual-Loop Memory System**
- **Subconscious Loop**: Continuous VLM observation → State tracking → RAG matching → Sliding window memory
- **Instant Response Loop**: User queries → Direct state lookup → Immediate response (< 50ms)

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
- **[RAG & State Tracker Integration](./docs/RAG_STATE_TRACKER_INTEGRATION_APPROACHES.md)** - Three approaches for integrating RAG and State Tracker
- **[VLM Enhancement Guide](./docs/VLM_ENHANCEMENT_GUIDE.md)** - Optimization guide for vision models
- **[Test Results Summary](./TEST_RESULTS_SUMMARY.md)** - Latest VQA 2.0 performance results

### **Additional Resources**
- **[Troubleshooting Guide](./docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[FAQ](./docs/FAQ.md)** - Frequently asked questions

## ✨ **Key Features**

**🎯 Core Vision with Dual-Loop Memory:**
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

**🧠 Revolutionary Dual-Loop Memory System:**
- **🔄 Subconscious Loop** - Background state tracking that continuously monitors your progress
- **⚡ Instant Response Loop** - Immediate answers to queries like "What step am I on?" or "What tools do I need?"
- **🧠 RAG Knowledge Base** - Intelligent matching of VLM observations to task steps
- **📊 Sliding Window Memory** - Efficient memory management with automatic cleanup
- **🎯 Query Classification** - 100% accurate understanding of user intent

**🧪 Current Testing:**
- **Video Approach**: Continuous understanding with temporal reasoning (SmolVLM2-Video)
- **Image Approach**: High-frequency intelligent capture with context memory (SmolVLM)
- **Memory System**: Dual-loop coordination with 100% success rate

## 🎬 **Real-World Examples**

### 🍳 **Cooking Assistant**
```
AI sees [eggs, pan, stove, spatula, salt, butter]
AI recognizes "scrambled eggs preparation setup"
User asks "What step am I on?"

AI Response:
"You're currently on Step 1: Preparation. I can see you have all the necessary tools:
- Eggs, pan, stove, spatula, salt, butter
- Estimated time: 2-3 minutes
- Safety notes: Be careful with hot pan

Next: Crack 2-3 eggs into a bowl and whisk them..."
```

### 🔧 **Repair Assistant**
```
AI sees [laptop, screwdriver, replacement_part, manual]
AI recognizes "laptop repair/upgrade scenario"  
User asks "What tools do I need?"

AI Response:
"Based on your current repair task, you need:
- Phillips head screwdriver (you have this)
- Anti-static wrist strap (recommended)
- Small container for screws
- Estimated time: 15-20 minutes
- Safety notes: Ensure laptop is powered off and unplugged

I can see you're ready to start the repair process..."
```

### 🪑 **Assembly Assistant**
```
AI sees [furniture_parts, screws, allen_wrench, instruction_manual]
AI recognizes "furniture assembly in progress"
User asks "How much progress have I made?"

AI Response:
"You've completed 60% of the assembly! Current status:
- ✅ Base frame assembled correctly
- ✅ Side panels attached
- 🔄 Working on: Shelf installation
- Remaining: 2 steps (shelf alignment, final tightening)
- Estimated time remaining: 10-15 minutes

You're doing great! The next step is to align the shelf with the brackets..."
```

## 🛠️ **Tech Stack**

### **Frontend**
- HTML5, CSS3, JavaScript
- Real-time camera integration
- Responsive design with modern UI
- Query interface for instant responses

### **Backend**
- FastAPI (Python)
- Unified model server architecture
- Image preprocessing pipeline
- **State Tracker system**
- **RAG knowledge base integration**

### **AI Models**
- SmolVLM & SmolVLM2
- Moondream2
- Phi-3.5-Vision (MLX Optimized)
- LLaVA (MLX Optimized)
- YOLO8

### **Memory System**
- **Dual-loop architecture**
- **RAG vector search (ChromaDB)**
- **Sliding window memory management**
- **Query classification engine**

### **Infrastructure**
- Three-layer architecture (Frontend → Backend → Model Server)
- Configuration management system
- Comprehensive logging and monitoring
- **Service communication validation**

## 💡 **What Makes This Different**

### **🔍 Unlike YouTube Tutorials:**
- **No more rewinding** to see what tool they're using
- **No assumptions** about what you have or your skill level
- **No generic instructions** that don't match your specific situation
- **Continuous adaptation** to your actual progress as it happens
- **Instant progress tracking** - "You're 60% done, next step is..."

### **🤖 Unlike Other AI Assistants:**
- **Continuously watches your workspace** like human eyes, not relying on your descriptions
- **Understands ongoing activities** and temporal sequences, not just static objects
- **Provides flowing progress guidance**: "I can see you've completed step 1 and are moving to step 2..."
- **Prevents mistakes as they develop** in real-time: "I see you reaching for that tool - use the smaller one instead..."
- **Remembers your entire session** and can answer "What step am I on?" instantly

### **📚 Unlike Traditional Manuals:**
- **Continuously adaptive guidance** - responds to your ongoing activities in real-time
- **Natural dialogue** - ask questions while working, get immediate contextual answers
- **Temporal memory** - remembers your entire work session and progress flow
- **Real-time encouragement** - celebrates progress as it happens: "Perfect! You're doing great!"
- **Detailed tool lists** - "You need: screwdriver, wrench, safety glasses"

### **🎯 The Result:**
**Confidence instead of frustration. Flowing guidance instead of fragmented instructions. Natural mentoring instead of robotic responses. Intelligent memory that never forgets where you are.**

## 🌍 **Universal Application**

This system is designed to help with:
- **🍳 Cooking** - From basic meals to complex recipes
- **🔧 Repairs** - Electronics, appliances, vehicles
- **🪑 Assembly** - Furniture, electronics, DIY projects  
- **📚 Learning** - New skills, hobbies, techniques
- **🏠 Home improvement** - Installation, maintenance, decoration
- **🎨 Creative projects** - Art, crafts, building

## 📊 **Current Performance Metrics**

- **✅ Dual-Loop Memory System**: 100% success rate
- **✅ Query Classification**: 100% accuracy
- **✅ Service Communication**: All endpoints functional
- **✅ Response Time**: < 50ms for instant queries
- **✅ Memory Usage**: Optimized sliding window < 1MB
- **✅ Error Handling**: Robust fault tolerance
- **✅ System Stability**: 100% recovery rate

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

**Built with ❤️ for makers, learners, and anyone who wants to confidently tackle any hands-on task with intelligent AI assistance.** 