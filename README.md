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

## 🧠 **How It Works: The Intelligence Pipeline**

+--------------------------------+
|      FRONTEND (Your App)       |
|  (e.g., iPhone App, Web App)   |
+--------------------------------+
| - Captures video/image         |
| - Displays guidance to user    |
+--------------------------------+
             |
             | (Sends image data over the network via HTTP/API call)
             ▼
+--------------------------------+
|        BACKEND (Server)        |
|  (e.g., Python FastAPI Server) |
+--------------------------------+
| 1. Receives image data         |
| 2. Image Enhancement Module    | <--- Your new, smart idea!
|    - Denoise, sharpen, etc.    |
| 3. VLM Perception Engine       |
|    - (Phi-3, LLaVA, Moondream) |
|    - Analyzes enhanced image   |
| 4. Returns structured JSON     |
+--------------------------------+
             |
             | (Sends JSON response back over the network)
             ▼
+--------------------------------+
|      FRONTEND (Your App)       |
+--------------------------------+
| - Receives JSON                |
| - Presents guidance (TTS, text)|
+--------------------------------+


**Note:** The choice of primary model (YOLO or VLM) is still undecided. With modern Vision-Language Models (VLMs), object detection and context understanding can often occur simultaneously, rather than as strictly separate stages. The architecture is flexible and may use either a sequential or parallel approach depending on the chosen models.

**Importantly, the system is designed for end-to-end detection and understanding:**
- The pipeline aims to process raw camera input all the way to actionable, context-aware guidance for the user, without manual intervention at any stage.
- This end-to-end approach ensures that detection, context recognition, and instruction are seamlessly integrated, providing a smooth and intelligent user experience.

### Stage 1 & 2: 👁️ **Object Detection & Context Understanding**
```
📷 Camera Input
    ↓
[Detection + Understanding]
    ↓
💬 AI Assistant (What should you do next?)
    ↓
🗣️ Step-by-step guidance
```
- Real-time detection and contextual understanding of all objects in view
- Analyzes object relationships, spatial arrangements, and activity patterns
- Maintains memory of previous actions and progress

### Stage 3: 💬 **Interactive Guidance & Instruction**
```
Context + User Question → AI Assistant → "Place onion on cutting board, slice downward in 1/4 inch intervals"
```
- Generates specific, actionable instructions
- Provides real-time feedback and error prevention
- Adapts guidance based on user skill level and progress

## ✨ **Why This Matters**

### **🚀 Revolutionary Approach to Learning**
- **No more frustrating tutorials** that don't match your exact situation
- **No more pausing videos** to figure out what tool they're using
- **No more guessing** if you're doing it right

### **🎯 Personalized & Contextual**
- **Sees your actual setup** - knows what tools and materials you have
- **Adapts to your pace** - never rushes, never leaves you behind  
- **Prevents mistakes** - catches errors before they become problems
- **Celebrates progress** - acknowledges each step you complete successfully

### **🌍 Universal Application**
This isn't limited to one domain. It's designed to help with:
- **🍳 Cooking** - From basic meals to complex recipes
- **🔧 Repairs** - Electronics, appliances, vehicles
- **🪑 Assembly** - Furniture, electronics, DIY projects  
- **📚 Learning** - New skills, hobbies, techniques
- **🏠 Home improvement** - Installation, maintenance, decoration
- **🎨 Creative projects** - Art, crafts, building

## ✨ **Key Features**

- **🔄 Real-time Processing** - Continuous scene understanding and object recognition
- **🎯 Context-Aware** - Understands activities and workflows, not just objects  
- **💡 Adaptive Guidance** - Learns your preferences and adjusts instruction style
- **⚡ Local Processing** - Works offline with optimized performance
- **📱 Multi-Platform** - Supports various camera inputs and devices
- **💰 Cost-Effective** - Efficient processing without expensive cloud dependencies

## 🏗️ **System Architecture**

### 📊 **Three-Layer Fixed Port Architecture**

The AI Manual Assistant follows a robust three-layer architecture with fixed ports for reliable communication:

```
📱 Frontend Layer (Port 5500)
    ↓ HTTP Requests
🔄 Backend Layer (Port 8000) 
    ↓ Model API Calls
🧠 Model Server Layer (Port 8080)
```

#### **Layer 1: Frontend (Port 5500)**
- **Real-time Camera Interface** - Live video stream processing
- **User Interaction Controls** - Start/stop, instruction input, settings
- **Responsive UI** - Displays AI guidance and system status
- **Cross-platform Support** - Works on desktop and mobile browsers

#### **Layer 2: Backend (Port 8000)**
- **Unified API Gateway** - Single endpoint for all model interactions
- **Image Preprocessing** - Optimized for each model (SmolVLM: 640x480, Phi-3: 336x336)
- **Request Routing** - Intelligent forwarding to active model server
- **Configuration Management** - Dynamic model switching and parameter tuning

#### **Layer 3: Model Server (Port 8080)**
- **Vision-Language Models** - Currently supports SmolVLM, Phi-3 Vision, and SmolVLM2
- **Real-time Inference** - Optimized for Apple Silicon with MPS acceleration
- **OpenAI-Compatible API** - Standard `/v1/chat/completions` endpoint
- **Resource Management** - Efficient memory usage and model loading

### 🔄 **Data Flow**
```
Camera → Frontend → Backend → Model Server → AI Response → Frontend → User
```

### 🎯 **Model Support**
- ✅ **SmolVLM** - Lightweight, fast responses, optimized for real-time interaction
- ✅ **SmolVLM2** - MLX-optimized for Apple Silicon with video understanding
- ✅ **Phi-3 Vision** - Microsoft's advanced model, higher accuracy
- 🚀 **Future Models** - Qwen2-VL, MiniCPM-Llama3-V (planned)

## 🎬 **Real-World Examples**

### 🍳 **Cooking Assistant**
```
Stage 1: AI sees [eggs, pan, stove, spatula, salt, butter]
Stage 2: AI recognizes "scrambled eggs preparation setup"
Stage 3: User asks "How do I make scrambled eggs?"

AI Response:
"Perfect! I can see you have everything needed for scrambled eggs.
1. First, crack 2-3 eggs into a bowl
2. Heat your pan on medium heat with a bit of butter
3. I'll watch and tell you when it's ready..."

[User cracks eggs]
AI: "Great! I see the eggs are cracked. Now whisk them until smooth..."
```

### 🔧 **Repair Assistant**
```
Stage 1: AI sees [laptop, screwdriver, replacement_part, manual]
Stage 2: AI recognizes "laptop repair/upgrade scenario"  
Stage 3: User asks "How do I replace this part?"

AI Response:
"I can see you're working on a laptop repair. Based on the part you're holding:
1. First, ensure the laptop is powered off and unplugged
2. I notice you have the right screwdriver - remove the back panel screws
3. I'll guide you to the correct component location..."
```

### 🪑 **Assembly Assistant**
```
Stage 1: AI sees [furniture_parts, screws, allen_wrench, instruction_manual]
Stage 2: AI recognizes "furniture assembly in progress"
Stage 3: User asks "I'm lost, what's next?"

AI Response:
"I can see your progress! You've completed the base frame correctly.
Next steps:
1. Take the long shelf piece (I can see it to your left)
2. Align it with the middle brackets
3. Use the 40mm screws - I'll confirm when you have the right ones..."
```

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

3. **Choose your AI model**:
   ```bash
   # SmolVLM2 (MLX-optimized for Apple Silicon)
   python src/models/smolvlm2/start_server.py --model video
   
   # SmolVLM (Original, lightweight)
   python src/models/smolvlm/start_server.py
   
   # Phi-3 Vision (Advanced understanding)
   python src/models/phi3_vision/start_server.py --model phi3.5
   ```

4. **Start the assistant**:
   ```bash
   # Start model server (use active model)
   python model_switcher.py status  # Check current model
   
   # For SmolVLM
   python src/models/smolvlm/start_server.py
   
   # For Phi-3 Vision (with flexible options)
   python src/models/phi3_vision/start_server.py --model phi3    # 128K version
   python src/models/phi3_vision/start_server.py --model phi3.5  # Enhanced version
   
   # Start backend
   python src/backend/main.py
   
   # Start frontend (new terminal)
   cd src/frontend && python -m http.server 5500
   ```

5. **Quick model switching with environment variables**:
   ```bash
   # Switch Phi-3 variants easily
   PHI3_MODEL=phi3.5 python src/models/phi3_vision/start_server.py
   PHI3_PORT=8081 python src/models/phi3_vision/start_server.py
   ```


4. **Point camera at any task** and ask for help!

## 📋 **Real-World Impact Stories**

### 🍳 **"Finally, I can cook without calling my mom every 5 minutes"**
**The Challenge:** Sarah, a college student, wants to cook healthy meals but gets overwhelmed by recipe videos that move too fast and use different ingredients.

**With AI Manual Assistant:**
1. **Adaptive Recognition:** Camera sees her small dorm kitchen setup and suggests modifications for limited space
2. **Real-time Guidance:** "I can see your pan is getting too hot - turn it down to medium"
3. **Ingredient Substitution:** "No heavy cream? I see you have milk and butter - here's how to make a substitute"
4. **Success Tracking:** "Perfect! Your onions are translucent now - time for the next step"

### 🔧 **"I saved $200 by fixing my laptop myself"**
**The Challenge:** Mark's laptop won't start, and repair shops quote $200+ for diagnostics alone.

**With AI Manual Assistant:**
1. **Problem Diagnosis:** Camera analyzes the laptop behavior and LED patterns
2. **Tool Verification:** "I can see you have the right screwdriver set for this model"
3. **Step-by-step Repair:** Guides through opening the case, checking connections, and identifying the faulty RAM
4. **Safety Monitoring:** "Wait - make sure you're grounded before touching that component"

### 🪑 **"IKEA furniture instructions finally make sense"**
**The Challenge:** Lisa struggles with assembly instructions that seem designed for engineers, not regular people.

**With AI Manual Assistant:**
1. **Visual Clarity:** "You're holding the right piece, but it's upside down - flip it over"
2. **Progress Tracking:** "Great! You've completed step 3 of 12. The frame is looking solid"
3. **Error Prevention:** "Stop! Those are 25mm screws, but this step needs 15mm - see the bag labeled 'B'?"
4. **Completion Confidence:** "All done! Your bookshelf is properly assembled and stable"

### 📚 **"Learning guitar has never been easier"**
**The Challenge:** Tom wants to learn guitar but online tutorials can't see his hand position or correct his mistakes.

**With AI Manual Assistant:**
1. **Posture Correction:** "I can see your fretting hand - try curving your fingers more"
2. **Real-time Feedback:** "Your chord shape looks correct! Now try the strumming pattern"
3. **Progress Recognition:** "You've been practicing for 20 minutes - your finger placement has improved significantly"
4. **Encouraging Guidance:** "Don't worry about that buzz - it's normal. Here's how to adjust your finger pressure"

### 🏠 **"Home repairs don't intimidate me anymore"**
**The Challenge:** Jennifer's bathroom faucet leaks, but she's never done plumbing work and fears making it worse.

**With AI Manual Assistant:**
1. **Problem Assessment:** Camera analyzes the leak location and suggests the most likely cause
2. **Tool Preparation:** "You'll need an adjustable wrench and plumber's tape - I can see you have both"
3. **Safety First:** "Perfect! You turned off the water supply - that's the most important step"
4. **Confidence Building:** "The leak has stopped! You've successfully replaced the O-ring yourself"

## 🛠️ **Tech Stack**



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

3. **Choose your AI model**:
   ```bash
   # SmolVLM2 (MLX-optimized for Apple Silicon)
   python src/models/smolvlm2/start_server.py --model video
   
   # SmolVLM (Original, lightweight)
   python src/models/smolvlm/start_server.py
   
   # Phi-3 Vision (Advanced understanding)
   python src/models/phi3_vision/start_server.py --model phi3.5
   ```

4. **Start the assistant**:
   ```bash
   # Start model server (use active model)
   python model_switcher.py status  # Check current model
   
   # For SmolVLM
   python src/models/smolvlm/start_server.py
   
   # For Phi-3 Vision (with flexible options)
   python src/models/phi3_vision/start_server.py --model phi3    # 128K version
   python src/models/phi3_vision/start_server.py --model phi3.5  # Enhanced version
   
   # Start backend
   python src/backend/main.py
   
   # Start frontend (new terminal)
   cd src/frontend && python -m http.server 5500
   ```

5. **Quick model switching with environment variables**:
   ```bash
   # Switch Phi-3 variants easily
   PHI3_MODEL=phi3.5 python src/models/phi3_vision/start_server.py
   PHI3_PORT=8081 python src/models/phi3_vision/start_server.py
   ```


4. **Point camera at any task** and ask for help!

## 📋 **Real-World Impact Stories**

### 🍳 **"Finally, I can cook without calling my mom every 5 minutes"**
**The Challenge:** Sarah, a college student, wants to cook healthy meals but gets overwhelmed by recipe videos that move too fast and use different ingredients.

**With AI Manual Assistant:**
1. **Adaptive Recognition:** Camera sees her small dorm kitchen setup and suggests modifications for limited space
2. **Real-time Guidance:** "I can see your pan is getting too hot - turn it down to medium"
3. **Ingredient Substitution:** "No heavy cream? I see you have milk and butter - here's how to make a substitute"
4. **Success Tracking:** "Perfect! Your onions are translucent now - time for the next step"

### 🔧 **"I saved $200 by fixing my laptop myself"**
**The Challenge:** Mark's laptop won't start, and repair shops quote $200+ for diagnostics alone.

**With AI Manual Assistant:**
1. **Problem Diagnosis:** Camera analyzes the laptop behavior and LED patterns
2. **Tool Verification:** "I can see you have the right screwdriver set for this model"
3. **Step-by-step Repair:** Guides through opening the case, checking connections, and identifying the faulty RAM
4. **Safety Monitoring:** "Wait - make sure you're grounded before touching that component"

### 🪑 **"IKEA furniture instructions finally make sense"**
**The Challenge:** Lisa struggles with assembly instructions that seem designed for engineers, not regular people.

**With AI Manual Assistant:**
1. **Visual Clarity:** "You're holding the right piece, but it's upside down - flip it over"
2. **Progress Tracking:** "Great! You've completed step 3 of 12. The frame is looking solid"
3. **Error Prevention:** "Stop! Those are 25mm screws, but this step needs 15mm - see the bag labeled 'B'?"
4. **Completion Confidence:** "All done! Your bookshelf is properly assembled and stable"

### 📚 **"Learning guitar has never been easier"**
**The Challenge:** Tom wants to learn guitar but online tutorials can't see his hand position or correct his mistakes.

**With AI Manual Assistant:**
1. **Posture Correction:** "I can see your fretting hand - try curving your fingers more"
2. **Real-time Feedback:** "Your chord shape looks correct! Now try the strumming pattern"
3. **Progress Recognition:** "You've been practicing for 20 minutes - your finger placement has improved significantly"
4. **Encouraging Guidance:** "Don't worry about that buzz - it's normal. Here's how to adjust your finger pressure"

### 🏠 **"Home repairs don't intimidate me anymore"**
**The Challenge:** Jennifer's bathroom faucet leaks, but she's never done plumbing work and fears making it worse.

**With AI Manual Assistant:**
1. **Problem Assessment:** Camera analyzes the leak location and suggests the most likely cause
2. **Tool Preparation:** "You'll need an adjustable wrench and plumber's tape - I can see you have both"
3. **Safety First:** "Perfect! You turned off the water supply - that's the most important step"
4. **Confidence Building:** "The leak has stopped! You've successfully replaced the O-ring yourself"

## 🛠️ **Tech Stack**



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
**With AI Manual Assistant:**
1. **Posture Correction:** "I can see your fretting hand - try curving your fingers more"
2. **Real-time Feedback:** "Your chord shape looks correct! Now try the strumming pattern"
3. **Progress Recognition:** "You've been practicing for 20 minutes - your finger placement has improved significantly"
4. **Encouraging Guidance:** "Don't worry about that buzz - it's normal. Here's how to adjust your finger pressure"

### 🏠 **"Home repairs don't intimidate me anymore"**
**The Challenge:** Jennifer's bathroom faucet leaks, but she's never done plumbing work and fears making it worse.

**With AI Manual Assistant:**
1. **Problem Assessment:** Camera analyzes the leak location and suggests the most likely cause
2. **Tool Preparation:** "You'll need an adjustable wrench and plumber's tape - I can see you have both"
3. **Safety First:** "Perfect! You turned off the water supply - that's the most important step"
4. **Confidence Building:** "The leak has stopped! You've successfully replaced the O-ring yourself"

## 🛠️ **Tech Stack**



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

3. **Choose your AI model**:
   ```bash
   # SmolVLM2 (MLX-optimized for Apple Silicon)
   python src/models/smolvlm2/start_server.py --model video
   
   # SmolVLM (Original, lightweight)
   python src/models/smolvlm/start_server.py
   
   # Phi-3 Vision (Advanced understanding)
   python src/models/phi3_vision/start_server.py --model phi3.5
   ```

4. **Start the assistant**:
   ```bash
   # Start model server (use active model)
   python model_switcher.py status  # Check current model
   
   # For SmolVLM
   python src/models/smolvlm/start_server.py
   
   # For Phi-3 Vision (with flexible options)
   python src/models/phi3_vision/start_server.py --model phi3    # 128K version
   python src/models/phi3_vision/start_server.py --model phi3.5  # Enhanced version
   
   # Start backend
   python src/backend/main.py
   
   # Start frontend (new terminal)
   cd src/frontend && python -m http.server 5500
   ```

5. **Quick model switching with environment variables**:
   ```bash
   # Switch Phi-3 variants easily
   PHI3_MODEL=phi3.5 python src/models/phi3_vision/start_server.py
   PHI3_PORT=8081 python src/models/phi3_vision/start_server.py
   ```


4. **Point camera at any task** and ask for help!

## 📋 **Real-World Impact Stories**

### 🍳 **"Finally, I can cook without calling my mom every 5 minutes"**
**The Challenge:** Sarah, a college student, wants to cook healthy meals but gets overwhelmed by recipe videos that move too fast and use different ingredients.

**With AI Manual Assistant:**
1. **Adaptive Recognition:** Camera sees her small dorm kitchen setup and suggests modifications for limited space
2. **Real-time Guidance:** "I can see your pan is getting too hot - turn it down to medium"
3. **Ingredient Substitution:** "No heavy cream? I see you have milk and butter - here's how to make a substitute"
4. **Success Tracking:** "Perfect! Your onions are translucent now - time for the next step"

### 🔧 **"I saved $200 by fixing my laptop myself"**
**The Challenge:** Mark's laptop won't start, and repair shops quote $200+ for diagnostics alone.

**With AI Manual Assistant:**
1. **Problem Diagnosis:** Camera analyzes the laptop behavior and LED patterns
2. **Tool Verification:** "I can see you have the right screwdriver set for this model"
3. **Step-by-step Repair:** Guides through opening the case, checking connections, and identifying the faulty RAM
4. **Safety Monitoring:** "Wait - make sure you're grounded before touching that component"

### 🪑 **"IKEA furniture instructions finally make sense"**
**The Challenge:** Lisa struggles with assembly instructions that seem designed for engineers, not regular people.

**With AI Manual Assistant:**
1. **Visual Clarity:** "You're holding the right piece, but it's upside down - flip it over"
2. **Progress Tracking:** "Great! You've completed step 3 of 12. The frame is looking solid"
3. **Error Prevention:** "Stop! Those are 25mm screws, but this step needs 15mm - see the bag labeled 'B'?"
4. **Completion Confidence:** "All done! Your bookshelf is properly assembled and stable"

### 📚 **"Learning guitar has never been easier"**
**The Challenge:** Tom wants to learn guitar but online tutorials can't see his hand position or correct his mistakes.

**With AI Manual Assistant:**
1. **Posture Correction:** "I can see your fretting hand - try curving your fingers more"
2. **Real-time Feedback:** "Your chord shape looks correct! Now try the strumming pattern"
3. **Progress Recognition:** "You've been practicing for 20 minutes - your finger placement has improved significantly"
4. **Encouraging Guidance:** "Don't worry about that buzz - it's normal. Here's how to adjust your finger pressure"

### 🏠 **"Home repairs don't intimidate me anymore"**
**The Challenge:** Jennifer's bathroom faucet leaks, but she's never done plumbing work and fears making it worse.

**With AI Manual Assistant:**
1. **Problem Assessment:** Camera analyzes the leak location and suggests the most likely cause
2. **Tool Preparation:** "You'll need an adjustable wrench and plumber's tape - I can see you have both"
3. **Safety First:** "Perfect! You turned off the water supply - that's the most important step"
4. **Confidence Building:** "The leak has stopped! You've successfully replaced the O-ring yourself"

## 🛠️ **Tech Stack**



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

3. **Choose your AI model**:
   ```bash
   # SmolVLM2 (MLX-optimized for Apple Silicon)
   python src/models/smolvlm2/start_server.py --model video
   
   # SmolVLM (Original, lightweight)
   python src/models/smolvlm/start_server.py
   
   # Phi-3 Vision (Advanced understanding)
   python src/models/phi3_vision/start_server.py --model phi3.5
   ```

4. **Start the assistant**:
   ```bash
   # Start model server (use active model)
   python model_switcher.py status  # Check current model
   
   # For SmolVLM
   python src/models/smolvlm/start_server.py
   
   # For Phi-3 Vision (with flexible options)
   python src/models/phi3_vision/start_server.py --model phi3    # 128K version
   python src/models/phi3_vision/start_server.py --model phi3.5  # Enhanced version
   
   # Start backend
   python src/backend/main.py
   
   # Start frontend (new terminal)
   cd src/frontend && python -m http.server 5500
   ```

5. **Quick model switching with environment variables**:
   ```bash
   # Switch Phi-3 variants easily
   PHI3_MODEL=phi3.5 python src/models/phi3_vision/start_server.py
   PHI3_PORT=8081 python src/models/phi3_vision/start_server.py
   ```


4. **Point camera at any task** and ask for help!

## 📋 **Real-World Impact Stories**

### 🍳 **"Finally, I can cook without calling my mom every 5 minutes"**
**The Challenge:** Sarah, a college student, wants to cook healthy meals but gets overwhelmed by recipe videos that move too fast and use different ingredients.

**With AI Manual Assistant:**
1. **Adaptive Recognition:** Camera sees her small dorm kitchen setup and suggests modifications for limited space
2. **Real-time Guidance:** "I can see your pan is getting too hot - turn it down to medium"
3. **Ingredient Substitution:** "No heavy cream? I see you have milk and butter - here's how to make a substitute"
4. **Success Tracking:** "Perfect! Your onions are translucent now - time for the next step"

### 🔧 **"I saved $200 by fixing my laptop myself"**
**The Challenge:** Mark's laptop won't start, and repair shops quote $200+ for diagnostics alone.

**With AI Manual Assistant:**
1. **Problem Diagnosis:** Camera analyzes the laptop behavior and LED patterns
2. **Tool Verification:** "I can see you have the right screwdriver set for this model"
3. **Step-by-step Repair:** Guides through opening the case, checking connections, and identifying the faulty RAM
4. **Safety Monitoring:** "Wait - make sure you're grounded before touching that component"

### 🪑 **"IKEA furniture instructions finally make sense"**
**The Challenge:** Lisa struggles with assembly instructions that seem designed for engineers, not regular people.

**With AI Manual Assistant:**
1. **Visual Clarity:** "You're holding the right piece, but it's upside down - flip it over"
2. **Progress Tracking:** "Great! You've completed step 3 of 12. The frame is looking solid"
3. **Error Prevention:** "Stop! Those are 25mm screws, but this step needs 15mm - see the bag labeled 'B'?"
4. **Completion Confidence:** "All done! Your bookshelf is properly assembled and stable"

### 📚 **"Learning guitar has never been easier"**
**The Challenge:** Tom wants to learn guitar but online tutorials can't see his hand position or correct his mistakes.

**With AI Manual Assistant:**
1. **Posture Correction:** "I can see your fretting hand - try curving your fingers more"
2. **Real-time Feedback:** "Your chord shape looks correct! Now try the strumming pattern"
3. **Progress Recognition:** "You've been practicing for 20 minutes - your finger placement has improved significantly"
4. **Encouraging Guidance:** "Don't worry about that buzz - it's normal. Here's how to adjust your finger pressure"

### 🏠 **"Home repairs don't intimidate me anymore"**
**The Challenge:** Jennifer's bathroom faucet leaks, but she's never done plumbing work and fears making it worse.

**With AI Manual Assistant:**
1. **Problem Assessment:** Camera analyzes the leak location and suggests the most likely cause
2. **Tool Preparation:** "You'll need an adjustable wrench and plumber's tape - I can see you have both"
3. **Safety First:** "Perfect! You turned off the water supply - that's the most important step"
4. **Confidence Building:** "The leak has stopped! You've successfully replaced the O-ring yourself"

## 🛠️ **Tech Stack**



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

3. **Choose your AI model**:
   ```bash
   # SmolVLM2 (MLX-optimized for Apple Silicon)
   python src/models/smolvlm2/start_server.py --model video
   
   # SmolVLM (Original, lightweight)
   python src/models/smolvlm/start_server.py
   
   # Phi-3 Vision (Advanced understanding)
   python src/models/phi3_vision/start_server.py --model phi3.5
   ```

4. **Start the assistant**:
   ```bash
   # Start model server (use active model)
   python model_switcher.py status  # Check current model
   
   # For SmolVLM
   python src/models/smolvlm/start_server.py
   
   # For Phi-3 Vision (with flexible options)
   python src/models/phi3_vision/start_server.py --model phi3    # 128K version
   python src/models/phi3_vision/start_server.py --model phi3.5  # Enhanced version
   
   # Start backend
   python src/backend/main.py
   
   # Start frontend (new terminal)
   cd src/frontend && python -m http.server 5500
   ```

5. **Quick model switching with environment variables**:
   ```bash
   # Switch Phi-3 variants easily
   PHI3_MODEL=phi3.5 python src/models/phi3_vision/start_server.py
   PHI3_PORT=8081 python src/models/phi3_vision/start_server.py
   ```


4. **Point camera at any task** and ask for help!

## 📋 **Real-World Impact Stories**

### 🍳 **"Finally, I can cook without calling my mom every 5 minutes"**
**The Challenge:** Sarah, a college student, wants to cook healthy meals but gets overwhelmed by recipe videos that move too fast and use different ingredients.

**With AI Manual Assistant:**
1. **Adaptive Recognition:** Camera sees her small dorm kitchen setup and suggests modifications for limited space
2. **Real-time Guidance:** "I can see your pan is getting too hot - turn it down to medium"
3. **Ingredient Substitution:** "No heavy cream? I see you have milk and butter - here's how to make a substitute"
4. **Success Tracking:** "Perfect! Your onions are translucent now - time for the next step"

### 🔧 **"I saved $200 by fixing my laptop myself"**
**The Challenge:** Mark's laptop won't start, and repair shops quote $200+ for diagnostics alone.

**With AI Manual Assistant:**
1. **Problem Diagnosis:** Camera analyzes the laptop behavior and LED patterns
2. **Tool Verification:** "I can see you have the right screwdriver set for this model"
3. **Step-by-step Repair:** Guides through opening the case, checking connections, and identifying the faulty RAM
4. **Safety Monitoring:** "Wait - make sure you're grounded before touching that component"

### 🪑 **"IKEA furniture instructions finally make sense"**
**The Challenge:** Lisa struggles with assembly instructions that seem designed for engineers, not regular people.

**With AI Manual Assistant:**
1. **Visual Clarity:** "You're holding the right piece, but it's upside down - flip it over"
2. **Progress Tracking:** "Great! You've completed step 3 of 12. The frame is looking solid"
3. **Error Prevention:** "Stop! Those are 25mm screws, but this step needs 15mm - see the bag labeled 'B'?"
4. **Completion Confidence:** "All done! Your bookshelf is properly assembled and stable"

### 📚 **"Learning guitar has never been easier"**
**The Challenge:** Tom wants to learn guitar but online tutorials can't see his hand position or correct his mistakes.

**With AI Manual Assistant:**
1. **Posture Correction:** "I can see your fretting hand - try curving your fingers more"
2. **Real-time Feedback:** "Your chord shape looks correct! Now try the strumming pattern"
3. **Progress Recognition:** "You've been practicing for 20 minutes - your finger placement has improved significantly"
4. **Encouraging Guidance:** "Don't worry about that buzz - it's normal. Here's how to adjust your finger pressure"

### 🏠 **"Home repairs don't intimidate me anymore"**
**The Challenge:** Jennifer's bathroom faucet leaks, but she's never done plumbing work and fears making it worse.

**With AI Manual Assistant:**
1. **Problem Assessment:** Camera analyzes the leak location and suggests the most likely cause
2. **Tool Preparation:** "You'll need an adjustable wrench and plumber's tape - I can see you have both"
3. **Safety First:** "Perfect! You turned off the water supply - that's the most important step"
4. **Confidence Building:** "The leak has stopped! You've successfully replaced the O-ring yourself"

## 🛠️ **Tech Stack**



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
**Confidence instead of frustration. Success instead of giving up. Learning