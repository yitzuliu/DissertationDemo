# AI Manual Assistant - Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the AI Manual Assistant system.

## Quick Diagnostics

### System Health Check
Run these commands to check system status:

```bash
# Check if all services are running
lsof -i :5500  # Frontend
lsof -i :8000  # Backend
lsof -i :8080  # Model Server

# Check system resources
htop
nvidia-smi  # If using GPU

# Check log files
tail -f logs/app.log
```

## Common Issues

### 1. Camera Not Working

#### Symptoms:
- Black screen in camera preview
- "Camera access denied" errors
- Camera feed freezes

#### Solutions:

**On macOS:**
```bash
# Check camera permissions
system_profiler SPCameraDataType

# Reset camera permissions
sudo killall VDCAssistant
```

**In Browser:**
1. Check browser permissions (Camera icon in address bar)
2. Try different browsers (Chrome, Firefox, Safari)
3. Restart browser with fresh profile

**System Level:**
```bash
# Check if camera is in use
lsof | grep AppleCamera
sudo killall corecameraid
```

### 2. Model Server Issues

#### Symptoms:
- "Model server not responding" errors
- Slow or no AI responses
- High memory usage

#### Solutions:

**Memory Issues:**
```bash
# Check memory usage
ps aux | grep python | head -10
free -h  # Linux
vm_stat  # macOS

# Clear model cache
rm -rf ~/.cache/torch/hub/
rm -rf ~/.cache/huggingface/

# Restart with lower memory model
python src/models/moondream2/run_moondream2_optimized.py  # Only 0.10GB memory
```

**Connection Issues:**
```bash
# Test model server directly
curl http://localhost:8080/v1/models

# Check network configuration
netstat -an | grep 8080
```

### 3. Installation Problems

#### Symptoms:
- Package installation failures
- Module import errors
- Permission errors

#### Solutions:

**Python Environment:**
```bash
# Recreate virtual environment
rm -rf ai_vision_env
python3 -m venv ai_vision_env
source ai_vision_env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Permission Issues (macOS):**
```bash
# Fix Homebrew permissions
sudo chown -R $(whoami) /opt/homebrew/
```

**Package Conflicts:**
```bash
# Clean install
pip freeze > installed_packages.txt
pip uninstall -r installed_packages.txt -y
pip install -r requirements.txt
```

### 4. Performance Issues

#### Symptoms:
- Slow AI responses (>5 seconds)
- High CPU/GPU usage
- System lag or freezing

#### Solutions:

**Optimize Model Settings:**
```bash
# Use fastest model (Moondream2)
python src/models/moondream2/run_moondream2_optimized.py

# Use best balance model (SmolVLM2)
python src/models/smolvlm2/run_smolvlm2.py

# Reduce image quality
# Edit frontend/index.html, change capture quality to 0.7
```

**System Optimization:**
```bash
# Close unnecessary applications
# Increase virtual memory (if needed)
# Monitor resource usage
top -o cpu
```

### 5. LLaVA-MLX Performance Issues

#### Symptoms:
- Very slow responses (17+ seconds)
- Low accuracy (34% VQA accuracy)
- Model reloading messages in logs

#### Root Cause:
LLaVA-MLX requires model reloading for each image due to state management issues, causing significant performance degradation.

#### Solutions:

**Immediate Fix:**
```bash
# Switch to better performing model
# Stop LLaVA-MLX (Ctrl+C)
# Start SmolVLM2 instead
python src/models/smolvlm2/run_smolvlm2.py
```

**Performance Comparison:**
- **LLaVA-MLX**: 34.0% VQA accuracy, 17.86s average
- **SmolVLM2**: 66.0% VQA accuracy, 6.61s average
- **Moondream2**: 56.0% VQA accuracy, 4.06s average

**Recommendation:** Avoid LLaVA-MLX until the reloading issue is resolved.

### 6. Network Connectivity

#### Symptoms:
- Frontend can't connect to backend
- API timeouts
- CORS errors in browser console

#### Solutions:

**Port Conflicts:**
```bash
# Find processes using ports
lsof -i :5500 -i :8000 -i :8080

# Kill conflicting processes
kill -9 <PID>
```

**Firewall Issues:**
```bash
# macOS: Allow ports in firewall
sudo pfctl -f /etc/pf.conf

# Linux: Configure iptables
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
```

## Model-Specific Issues

### SmolVLM2-500M-Video-Instruct Issues

#### Symptoms:
- Model loading failures
- Memory errors

#### Solutions:
```bash
# Ensure sufficient memory (2.08GB required)
free -h  # Check available memory

# Clear cache and restart
rm -rf ~/.cache/huggingface/
python src/models/smolvlm2/run_smolvlm2.py
```

### Moondream2 Issues

#### Symptoms:
- Fast but inaccurate responses
- Low VQA accuracy

#### Solutions:
```bash
# This is expected - Moondream2 prioritizes speed over accuracy
# For better accuracy, switch to SmolVLM2
python src/models/smolvlm2/run_smolvlm2.py
```

### Phi-3.5-Vision Issues

#### Symptoms:
- Very slow responses (19+ seconds)
- MLX-related errors

#### Solutions:
```bash
# Ensure MLX is properly installed
pip install mlx-vlm

# Check Apple Silicon compatibility
uname -m  # Should show arm64

# For faster responses, switch to SmolVLM2
python src/models/smolvlm2/run_smolvlm2.py
```

## Performance Optimization

### Model Selection Guide

#### For Best Overall Performance:
```bash
python src/models/smolvlm2/run_smolvlm2.py
# VQA Accuracy: 66.0%, Time: 6.61s, Memory: 2.08GB
```

#### For Speed-Critical Applications:
```bash
python src/models/moondream2/run_moondream2_optimized.py
# VQA Accuracy: 56.0%, Time: 4.06s, Memory: 0.10GB
```

#### For Resource-Constrained Environments:
```bash
python src/models/moondream2/run_moondream2_optimized.py
# Lowest memory usage: 0.10GB
```

#### ⚠️ Avoid This Model:
```bash
python src/models/llava_mlx/run_llava_mlx.py
# Poor performance: 34.0% VQA accuracy, 17.86s average
```

### Testing Model Performance

Use the built-in VQA testing framework:

```bash
# Quick performance test (10 questions)
python src/testing/vqa_test.py --questions 10 --models smolvlm_v2_instruct

# Compare multiple models
python src/testing/vqa_test.py --questions 10 --models smolvlm_v2_instruct moondream2

# Comprehensive test (20 questions)
python src/testing/vqa_test.py --questions 20 --models smolvlm_v2_instruct
```

## Advanced Troubleshooting

### Debug Mode

Enable detailed logging:

```bash
# Backend debug mode
export LOG_LEVEL=DEBUG
python src/backend/main.py

# Model server debug mode
export MODEL_DEBUG=1
python src/models/smolvlm2/run_smolvlm2.py --debug
```

### Log Analysis

Check log files for errors:

```bash
# Backend logs
tail -f logs/app.log | grep ERROR

# System logs (macOS)
log show --predicate 'process == "Python"' --last 1h
```

### Performance Monitoring

Monitor real-time performance:

```bash
# Check model server response time
curl -w "@-" -o /dev/null -s "http://localhost:8080/health" <<'EOF'
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n
EOF

# Monitor memory usage
watch -n 1 'ps aux | grep python | grep -v grep'
```

## Common Error Messages

### "Model server not responding"
- Check if model server is running on port 8080
- Restart the model server
- Try a different model

### "Out of memory"
- Close other applications
- Switch to Moondream2 (lowest memory usage)
- Restart the system

### "LLaVA model reloading"
- This is expected behavior for LLaVA-MLX
- Consider switching to SmolVLM2 for better performance

### "MLX not found"
- Install MLX for Apple Silicon: `pip install mlx-vlm`
- Ensure you're on Apple Silicon Mac

## Performance Benchmarks

### Latest VQA 2.0 Test Results (July 19, 2025)

**10 Questions Test:**
- SmolVLM2: ~66s, 66.0% accuracy
- SmolVLM: ~60s, 64.0% accuracy
- Moondream2: ~41s, 56.0% accuracy
- Phi-3.5: ~190s, 60.0% accuracy
- LLaVA-MLX: ~179s, 34.0% accuracy

**15 Questions Test:**
- SmolVLM2: ~98s, 58-66% accuracy
- SmolVLM: ~90s, 49-64% accuracy
- Moondream2: ~55s, 56-60% accuracy
- Phi-3.5: ~201s, 56-60% accuracy
- LLaVA-MLX: ~260s, 24-34% accuracy

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Run the VQA test** to verify model performance
3. **Check system resources** (memory, CPU)
4. **Try a different model** if one is underperforming

### When Reporting Issues

Include the following information:
- **System**: macOS/Linux version, hardware specs
- **Model**: Which model you're using
- **Error**: Exact error message
- **Steps**: How to reproduce the issue
- **Performance**: VQA test results if applicable

### Additional Resources

- **Model Comparison**: `docs/MODEL_COMPARISON.md`
- **API Documentation**: `docs/API.md`
- **Developer Setup**: `docs/DEVELOPER_SETUP.md`
- **FAQ**: `docs/FAQ.md`
- **Test Results**: `src/testing/vqa_test_result.md`

---

**Last Updated**: July 19, 2025  
**Test Framework**: VQA 2.0 Standard Evaluation  
**Hardware**: MacBook Air M3, 16GB RAM 