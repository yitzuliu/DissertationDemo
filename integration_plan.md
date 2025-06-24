# AI Manual Assistant Integration Framework

**Note:** Model selection (YOLO vs. VLM) is still under evaluation. Both architectures are supported; the final choice will be based on reliability and testing. The system is designed for end-to-end, automated detection and guidance, and this document is intended to be compatible with either approach.

---

## Glossary
- **YOLO**: You Only Look Once, a fast object detection model.
- **VLM**: Vision-Language Model, a model that understands both images and text.
- **End-to-End**: Fully automated pipeline from camera input to user guidance.
- **Majority Voting**: Aggregating multiple model outputs for stability.
- **Quantization**: Reducing model size/precision for efficiency.

---

## System Data Flow
```
Camera Input
   ↓
[YOLO and/or VLM Processing]
   ↓
Context Understanding
   ↓
Guidance Generation
   ↓
User Receives Step-by-Step Instructions
```

---

## Model Selection Criteria
- **Accuracy** (object and state recognition)
- **Latency** (response time)
- **Resource Usage** (memory, compute)
- **Extensibility** (ease of adding new tasks/models)
- **Edge Device Compatibility**
- **Reliability in real-world scenarios**

## Current Situation Analysis

The project currently contains two main components:
1. **YOLO8 Basic Object Detection System**
   - Strengths: Fast, accurate identification of predefined object categories
   - Limitations: Limited to about 80 predefined categories, unable to understand object states, contextual relationships, and activities

2. **SmolVLM Vision-Language System**
   - Strengths: Understands image content and context, can generate natural language descriptions and guidance
   - Areas for improvement: Response consistency and accuracy need enhancement

## Framework Adjustment Plan

**Note:** The choice of primary model (YOLO or VLM) for this project is still under consideration. We are actively evaluating which model is more reliable for our use case. Both architectures are valid options, and the final decision will be based on further testing and reliability assessment.

### 1. Core Architecture: Model Selection Options

#### Option A: VLM-based Visual Understanding System
- Use a powerful VLM (e.g., Qwen2-VL-2B, MiniCPM-Llama3-V-2.5, Phi-3-vision-4B, LLaVA-1.5-3B) as the primary recognition engine
- Advantages: Deep understanding of object states, spatial relationships, context, and activities; generates personalized, context-relevant guidance
- YOLO can serve as an auxiliary system for quick screening or verification

#### Option B: YOLO-based Primary Detection with VLM Contextualization
- Use YOLO as the main object detector for speed and deterministic results
- Pass detected regions or the full frame to a VLM for contextual understanding and guidance
- Advantages: Fast initial detection, resource efficiency, and the ability to leverage VLM for higher-level reasoning when needed

**Integration method example:**
```python
# Pseudocode for flexible integration
# Option A: VLM primary, YOLO auxiliary
# Option B: YOLO primary, VLM auxiliary

def process_frame(frame):
    if primary_model == 'YOLO':
        yolo_results = yolo_model(frame)
        vlm_response = vlm_model(frame, prompt, yolo_results)
        return vlm_response
    else:
        vlm_response = vlm_model(frame, prompt)
        if needs_verification(vlm_response):
            yolo_results = yolo_model(frame)
            verified_response = verify_with_yolo(vlm_response, yolo_results)
            return verified_response
        return vlm_response
```

## Edge Device Performance Considerations

For scenarios where deployment may be on laptops, iPhones or similar devices, we've specifically considered the resource requirements of models:

### Edge Device Compatibility Comparison

| Model | Parameters | Memory Requirement | MacBook M3 | iPhone | Recommended Use Case |
|------|-------|---------|-----------|--------|------------|
| SmolVLM (current) | 2B | ~4GB | ✅ Good | ⚠️ Limited | Extremely resource-constrained scenarios |
| Qwen2-VL-2B | 2B | ~5GB | ✅✅ Excellent | ✅ Viable | Best edge device option |
| MiniCPM-Llama3-V-1.5 | ~2.5B | ~5GB | ✅✅ Excellent | ✅ Good | Apple devices specialized |
| LLaVA-1.5-3B | 3B | ~6GB | ✅ Good | ⚠️ Requires newer models | When stronger comprehension needed |

### Optimization Strategies

To ensure smooth experience on edge devices, the following optimization measures are recommended:

1. **Model Quantization**
   - INT8 quantization reduces memory requirements by 50%
   - 4-bit quantization further reduces by 75%
   - Recommended to use GGUF format for quantization

2. **Inference Optimization**
   - Small batch processing (batch size=1)
   - Optimize context window size (default set to 2048)
   - Leverage Apple Neural Engine acceleration

3. **Adaptive Processing**
   - Dynamically adjust image resolution based on device performance
   - Adjust processing frequency based on battery status
   - Implement processing level selection (high quality/balanced/performance priority)

## Implementation Priorities

1. **Immediate Priorities**
   - Implement majority voting system (improve accuracy)
   - Activate scene memory system (enhance contextual understanding)
   - Upgrade to recommended VLM model

2. **Short-term Goals (2-4 weeks)**
   - Optimize image processing pipeline
   - Complete parameter testing and optimization
   - Implement advanced prompt engineering

3. **Long-term Goals (1-3 months)**
   - Implement selective integration of VLM and YOLO
   - Develop task-specific expert systems (cooking, repair, assembly)
   - Build adaptive processing system

## Performance Evaluation Metrics

| Metric | Target Value | Measurement Method |
|------|--------|---------|
| Object Recognition Accuracy | >90% | Comparison with manual annotation |
| State Understanding Accuracy | >85% | User feedback rating |
| Guidance Relevance | >85% | Task completion rate and user rating |
| Response Time | <2 seconds | System log analysis |
| Guidance Effectiveness | >80% | Task success rate improvement |

**Note:** Metrics will be measured using a combination of annotated test datasets, user studies, and system logs.

## Conclusion

**Current Status:** Model selection is ongoing. Based on the analysis of YOLO and VLM capabilities, we are evaluating both as potential core components of the system. The final architecture will fully leverage VLM's contextual understanding and/or YOLO's fast detection advantages as appropriate, to create a comprehensive and intelligent AI manual assistant system. Both models may be selectively integrated depending on scenario and reliability.
