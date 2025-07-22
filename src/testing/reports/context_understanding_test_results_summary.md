# VLM Context Understanding Capability Test Results Summary

**Test Date:** July 22, 2025 13:01:28  
**Test Duration:** 260.31 seconds (4.34 minutes)  
**Test Environment:** MacBook Air M3 (16GB RAM)  
**Test Framework:** Custom VLM Context Understanding Tester  

## Executive Summary

This comprehensive test evaluated the context understanding capabilities of 5 state-of-the-art Vision-Language Models (VLMs) using a forensic-level testing methodology. The results confirm that while some models can answer context questions, most answers are generic or hallucinated, and true context retention remains a challenge.

## Test Methodology

### Test Flow
1. **Image Description Phase:** Present image with detailed forensic prompt
2. **Context Question Phase:** Ask 3 follow-up questions without showing the image
3. **Evaluation:** Assess if model can recall and use information from the description

### Test Images
- **IMG_0119.JPG:** Shiba Inu dog on tiled floor
- **IMG_2053.JPG:** Person holding passport with "FKONs" shirt
- **test_image.jpg:** Geometric diagram with blue square and red circle

### Context Questions
1. "What were the most prominent colors in the image?"
2. "Were there any people visible in the image?"
3. "Summarize the main subject or scene of the image in one sentence."

## Results Summary

### **Overall Performance Rankings**

| **Model** | **Context Q Success Rate** | **Context Accuracy** | **Avg Inference (s)** | **Notes** |
|-----------|---------------------------|---------------------|-----------------------|-----------|
| SmolVLM-500M-Instruct | 100% | Answers present, but often generic or hallucinated | ~3.4 | Best context retention, but not always accurate |
| SmolVLM2-500M-Video-Instruct | 100% | Answers present, but often generic or hallucinated | ~6.2 | Consistent, but context answers are generic |
| Moondream2 | 0% | Model cannot answer context questions without image | ~5.9 | Vision-only, no context retention |
| LLaVA-v1.6-Mistral-7B-MLX | ~66% | Some answers missing or empty | ~6.7 | Incomplete context answers |
| Phi-3.5-Vision-Instruct | ~66% | Some answers missing or empty | ~10.1 | Incomplete context answers |

*Note: For exact context accuracy, manual review of answers is required. Moondream2 always replies it cannot answer without the image.*

### **Key Findings**
- All models can answer the initial image description.
- Only SmolVLM and SmolVLM2 consistently provide answers to context questions, but many are generic or hallucinated.
- Moondream2 cannot answer context questions without the image (always returns fallback message).
- LLaVA and Phi-3.5 sometimes skip context questions or provide empty answers.
- No model demonstrates reliable, detailed context retention across all images and questions.

## Recommendations
- For context-dependent applications, SmolVLM-500M-Instruct and SmolVLM2-500M-Video-Instruct provide the most consistent (if generic) answers.
- For vision-only tasks, Moondream2 is fast but cannot handle context.
- LLaVA and Phi-3.5 may require further tuning for context retention.
- Developers should not rely on current VLMs for multi-turn context understanding without external memory or prompt engineering.

---

**Test Framework:** Custom VLM Context Understanding Tester  
**Evaluation Method:** Forensic-level detail testing with follow-up questions  
**Data Source:** Real-world images with complex visual elements  
**Last Updated:** 2025-07-22 13:01:28 