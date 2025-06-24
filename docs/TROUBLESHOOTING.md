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
python src/models/smolvlm/start_server.py
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
# Use fastest model
python src/models/smolvlm/start_server.py

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

### 5. Network Connectivity

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

## Advanced Troubleshooting

### Debug Mode

Enable detailed logging:

```bash
# Backend debug mode
export LOG_LEVEL=DEBUG
python src/backend/main.py

# Model server debug mode
export MODEL_DEBUG=1
python src/models/smolvlm/start_server.py --debug
```

### Log Analysis

Check log files for errors:

```bash
# Backend logs
tail -f logs/app.log | grep ERROR

# System logs (macOS)
log show --predicate 'process == "Python"' --last 1h

# Browser console logs
# Open Developer Tools > Console tab
```

### Memory Debugging

Monitor memory usage:

```bash
# Python memory profiler
pip install memory-profiler
python -m memory_profiler src/backend/main.py

# System memory monitoring
watch -n 1 free -h  # Linux
while true; do vm_stat; sleep 1; done  # macOS
```

## Model-Specific Issues

### SmolVLM Issues

**Slow responses:**
- Check image preprocessing settings
- Ensure proper quantization
- Monitor memory usage

```bash
# Optimize SmolVLM
python src/models/smolvlm/start_server.py --quantize int8
```

### Phi-3 Vision Issues

**High memory usage:**
- Use quantized version
- Reduce context window
- Monitor GPU memory

```bash
# Phi-3 with optimization
PHI3_QUANTIZE=true python src/models/phi3_vision/start_server.py
```

### YOLO8 Issues

**Detection accuracy:**
- Check lighting conditions
- Verify object categories
- Adjust confidence threshold

```bash
# YOLO8 with custom threshold
python src/models/yolo8/start_server.py --confidence 0.5
```

## Environment-Specific Issues

### macOS Specific

**Apple Silicon Optimization:**
```bash
# Install Apple Silicon optimized packages
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Enable Metal Performance Shaders
export PYTORCH_ENABLE_MPS_FALLBACK=1
```

**Security Restrictions:**
```bash
# Allow unsigned packages
sudo spctl --master-disable

# Reset application permissions
tccutil reset Camera
```

### Linux Specific

**GPU Issues:**
```bash
# Check CUDA installation
nvidia-smi
nvcc --version

# Install CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Audio/Video Permissions:**
```bash
# Add user to video group
sudo usermod -a -G video $USER

# Install video codecs
sudo apt install ubuntu-restricted-extras
```

## Recovery Procedures

### Complete System Reset

If all else fails:

```bash
# 1. Stop all services
pkill -f "python.*start_server"
pkill -f "python.*main.py"

# 2. Clean cache and temporary files
rm -rf ~/.cache/torch/
rm -rf ~/.cache/huggingface/
rm -rf logs/*

# 3. Reset virtual environment
deactivate
rm -rf ai_vision_env
python3 -m venv ai_vision_env
source ai_vision_env/bin/activate

# 4. Fresh installation
pip install --upgrade pip
pip install -r requirements.txt

# 5. Restart services in order
python src/models/smolvlm/start_server.py &
sleep 10
python src/backend/main.py &
sleep 5
cd src/frontend && python -m http.server 5500
```

### Backup and Restore

**Create system backup:**
```bash
# Backup configuration
cp -r src/config/ config_backup_$(date +%Y%m%d)/

# Backup logs
cp -r logs/ logs_backup_$(date +%Y%m%d)/
```

**Restore from backup:**
```bash
# Restore configuration
cp -r config_backup_YYYYMMDD/* src/config/
```

## Getting Help

### Collect Diagnostic Information

Before seeking help, gather this information:

```bash
# System information
uname -a
python --version
pip list > installed_packages.txt

# Service status
ps aux | grep python > running_processes.txt

# Log files
cp logs/app.log debug_logs.txt

# Configuration
cp src/config/app_config.json config_info.txt
```

### Report Issues

When reporting issues, include:
1. System information (OS, Python version)
2. Steps to reproduce the problem
3. Error messages and log files
4. Screenshots if applicable

### Community Support

- **GitHub Issues**: [Create an issue](https://github.com/yitzuliu/DissertationDemo/issues)
- **Documentation**: Check [docs directory](../)
- **FAQ**: See [FAQ.md](./FAQ.md)

## Prevention Tips

### Regular Maintenance

```bash
# Weekly maintenance script
#!/bin/bash
# clean_system.sh

# Clear logs older than 7 days
find logs/ -name "*.log" -mtime +7 -delete

# Update packages
pip list --outdated
# pip install --upgrade <package_name>

# Check disk space
df -h

# Restart services
./restart_services.sh
```

### Monitoring

Set up basic monitoring:

```bash
# Create monitoring script
#!/bin/bash
# monitor.sh

while true; do
    echo "$(date): Checking services..."
    curl -s http://localhost:8000/status || echo "Backend down"
    curl -s http://localhost:8080/v1/models || echo "Model server down"
    curl -s http://localhost:5500 || echo "Frontend down"
    sleep 60
done
```

### Best Practices

1. **Regular Updates**: Keep dependencies updated
2. **Clean Shutdowns**: Always stop services properly
3. **Resource Monitoring**: Watch memory and CPU usage
4. **Log Rotation**: Prevent log files from growing too large
5. **Backup Configurations**: Save working configurations

---

**Need more help?** Check our [FAQ](./FAQ.md) or create an issue on [GitHub](https://github.com/yitzuliu/DissertationDemo/issues). 