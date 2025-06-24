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

**The breakthrough:** Instead of you describing what you see, the AI sees what you see. Instead of generic instructions, you get guidance based on your actual setup, tools, and progress.

**The result:** Like having an experienced mentor standing beside you, watching your work, and providing exactly the guidance you need, exactly when you need it.

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

- ✅ **SmolVLM** - Lightweight, fast responses, optimized for real-time interaction
- ✅ **Phi-3 Vision** - Microsoft's advanced model with higher accuracy
- ✅ **LLaVA** - Excellent for multi-turn conversations
- ✅ **YOLO8** - Real-time object detection
- ✅ **Moondream2** - Efficient specialized processing

## 🚀 **Quick Start**

1. **Clone and setup**:
   ```bash
   git clone https://github.com/yitzuliu/DissertationDemo.git
   cd destination_code
   source ai_vision_env/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the assistant**:
   ```bash
   # Start model server
   python src/models/smolvlm/start_server.py
   
   # Start backend (new terminal)
   python src/backend/main.py
   
   # Start frontend (new terminal)
   cd src/frontend && python -m http.server 5500
   ```

4. **Point camera at any task** and ask for help!

For detailed setup instructions, see the [Developer Setup Guide](./docs/DEVELOPER_SETUP.md).

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

- **🔄 Real-time Processing** - Continuous scene understanding and object recognition
- **🎯 Context-Aware** - Understands activities and workflows, not just objects  
- **💡 Adaptive Guidance** - Learns your preferences and adjusts instruction style
- **⚡ Local Processing** - Works offline with optimized performance
- **📱 Multi-Platform** - Supports various camera inputs and devices
- **💰 Cost-Effective** - Efficient processing without expensive cloud dependencies

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
- SmolVLM - Primary lightweight model
- Phi-3 Vision - High-accuracy model
- LLaVA - Multi-turn conversations
- YOLO8 - Real-time object detection

### **Infrastructure**
- Three-layer architecture (Frontend → Backend → Model Server)
- Configuration management system
- Comprehensive logging and monitoring

## 💡 **What Makes This Different**

### **🔍 Unlike YouTube Tutorials:**
- **No more rewinding** to see what tool they're using
- **No assumptions** about what you have or your skill level
- **No generic instructions** that don't match your specific situation
- **Real-time adaptation** to your actual progress and setup

### **🤖 Unlike Other AI Assistants:**
- **Actually sees your workspace** instead of relying on your descriptions
- **Understands context** beyond just identifying objects
- **Provides visual confirmation** of your progress: "I can see you've done step 1..."
- **Prevents mistakes in real-time** before they happen: "Wait! That's the wrong screw..."

### **📚 Unlike Traditional Manuals:**
- **Adaptive guidance** - responds to what you're actually doing
- **Interactive dialogue** - ask questions and get immediate answers
- **Context memory** - remembers your progress and previous choices
- **Encouragement** - celebrates your successes along the way

### **🎯 The Result:**
**Confidence instead of frustration. Success instead of giving up. Learning instead of just following.**

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