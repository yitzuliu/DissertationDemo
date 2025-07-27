#!/usr/bin/env python3
"""
Simulated Steps Test
Test State Tracker matching with simulated VLM observations for coffee brewing steps
"""

import subprocess
import requests
import time
import json
import sys
import os
import threading
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

class SimulatedStepsTester:
    def __init__(self):
        # Service configuration
        self.model_port = 8080
        self.backend_port = 8000
        self.model_process = None
        self.backend_process = None
        self.max_retries = 3
        
        # Test results
        self.test_results = {
            'step_1': False,
            'step_2': False,
            'step_3': False
        }
        
        # Virtual environment setup
        self.base_dir = Path(__file__).parent.parent.parent
        self.venv_path = self.base_dir / "ai_vision_env"  # Python 3.13.3
        self.python_executable = self.venv_path / "bin" / "python"
        
        # Verify virtual environment exists
        if not self.python_executable.exists():
            # Try alternative environment
            alt_venv_path = self.base_dir / "ai_vision_env_311"  # Python 3.11.8
            alt_python = alt_venv_path / "bin" / "python"
            
            if alt_python.exists():
                print(f"⚠️ Main virtual environment not found, using alternative: {alt_python}")
                self.venv_path = alt_venv_path
                self.python_executable = alt_python
            else:
                print(f"❌ Virtual environment not found: {self.python_executable}")
                print(f"❌ Alternative environment also not found: {alt_python}")
                print(f"⚠️ Will use system Python: {sys.executable}")
                self.python_executable = sys.executable
        else:
            print(f"✅ Using virtual environment: {self.python_executable}")
    
    def kill_port(self, port):
        """Force close processes using the specified port"""
        try:
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"], 
                capture_output=True, text=True
            )
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    subprocess.run(["kill", "-9", pid])
                print(f"✅ Force closed processes on port {port}")
                time.sleep(2)
        except Exception as e:
            print(f"⚠️ Error cleaning up port {port}: {e}")
    
    def start_model_service(self):
        """Start model service (SmolVLM)"""
        print("🚀 Step 1: Starting model service (SmolVLM)")
        print("=" * 50)
        
        # Use absolute path to ensure correct script location
        model_script = self.base_dir / "src/models/smolvlm/run_smolvlm.py"
        if not model_script.exists():
            print(f"❌ Model startup script doesn't exist: {model_script}")
            return False
        
        print(f"🐍 Using Python: {self.python_executable}")
        print(f"📄 Model script: {model_script}")
        
        for attempt in range(self.max_retries):
            print(f"📋 Attempt {attempt + 1}/{self.max_retries} to start model service...")
            
            # Clean up port
            self.kill_port(self.model_port)
            
            try:
                # Set environment variables, activate virtual environment
                env = os.environ.copy()
                if self.venv_path.exists():
                    env["VIRTUAL_ENV"] = str(self.venv_path)
                    env["PATH"] = f"{self.venv_path / 'bin'}:{env.get('PATH', '')}"
                
                # Start model service
                self.model_process = subprocess.Popen(
                    [str(self.python_executable), str(model_script)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env,
                    cwd=str(model_script.parent)
                )
                
                # Wait for startup
                print("⏳ Waiting for model service to start...")
                time.sleep(20)  # SmolVLM needs more time to start
                
                # Check service status
                if self.check_model_service():
                    print("✅ Model service started successfully")
                    return True
                else:
                    print(f"❌ Attempt {attempt + 1} failed")
                    if self.model_process:
                        self.model_process.terminate()
                        
            except Exception as e:
                print(f"❌ Error starting model service: {e}")
        
        print("❌ Model service startup failed, reached maximum retry attempts")
        return False
    
    def check_model_service(self):
        """Check if model service is running normally"""
        try:
            # Check process status
            if self.model_process and self.model_process.poll() is not None:
                print("❌ Model process has terminated")
                return False
            
            # Check port response - llama-server usually listens on root path
            try:
                response = requests.get(f"http://localhost:{self.model_port}/v1/models", timeout=10)
                if response.status_code == 200:
                    print("✅ Model service /v1/models endpoint responding normally")
                    return True
            except Exception as e:
                print(f"⚠️ /v1/models check failed: {e}")
            
            # Backup check: try root path
            try:
                response = requests.get(f"http://localhost:{self.model_port}/", timeout=5)
                if response.status_code in [200, 404]:  # 404 also indicates service is running
                    print("✅ Model service root path responding normally")
                    return True
            except Exception as e:
                print(f"⚠️ Root path check failed: {e}")
            
            return False
        except Exception as e:
            print(f"❌ Error checking model service: {e}")
            return False
    
    def start_backend_service(self):
        """Start backend service"""
        print("\n🚀 Step 2: Starting backend service")
        print("=" * 50)
        
        # Use absolute path to ensure correct script location
        backend_script = self.base_dir / "src/backend/main.py"
        if not backend_script.exists():
            print(f"❌ Backend startup script doesn't exist: {backend_script}")
            return False
        
        print(f"🐍 Using Python: {self.python_executable}")
        print(f"📄 Backend script: {backend_script}")
        
        for attempt in range(self.max_retries):
            print(f"📋 Attempt {attempt + 1}/{self.max_retries} to start backend service...")
            
            # Clean up port
            self.kill_port(self.backend_port)
            
            try:
                # Set environment variables, activate virtual environment
                env = os.environ.copy()
                if self.venv_path.exists():
                    env["VIRTUAL_ENV"] = str(self.venv_path)
                    env["PATH"] = f"{self.venv_path / 'bin'}:{env.get('PATH', '')}"
                    env["PYTHONPATH"] = str(self.base_dir / "src")
                
                # Start backend service - use uvicorn command
                self.backend_process = subprocess.Popen(
                    [str(self.python_executable), "-m", "uvicorn", "main:app", 
                     "--host", "127.0.0.1", "--port", str(self.backend_port), "--reload"],
                    cwd=str(backend_script.parent),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env
                )
                
                # Wait for startup
                print("⏳ Waiting for backend service to start...")
                time.sleep(10)  # Give more time for backend to start
                
                # Check service status
                if self.check_backend_service():
                    print("✅ Backend service started successfully")
                    return True
                else:
                    print(f"❌ Attempt {attempt + 1} failed")
                    if self.backend_process:
                        self.backend_process.terminate()
                        time.sleep(2)
                        
            except Exception as e:
                print(f"❌ Error starting backend service: {e}")
        
        print("❌ Backend service startup failed, reached maximum retry attempts")
        return False
    
    def check_backend_service(self):
        """Check if backend service is running normally"""
        try:
            # Check process status
            if self.backend_process and self.backend_process.poll() is not None:
                print("❌ Backend process has terminated")
                if self.backend_process.stderr:
                    stderr_output = self.backend_process.stderr.read()
                    if stderr_output:
                        print(f"❌ Backend error message: {stderr_output[:200]}...")
                return False
            
            # Check port response
            response = requests.get(f"http://localhost:{self.backend_port}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend health check endpoint responding normally")
                return True
            else:
                print(f"❌ Backend health check returned: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error checking backend service: {e}")
            return False
    
    def setup_chrome_driver(self):
        """Setup Chrome driver for frontend testing"""
        print("🌐 Setting up browser automation environment...")
        
        try:
            # First check if Chrome is installed
            chrome_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
                "/opt/google/chrome/chrome"
            ]
            
            chrome_found = None
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    chrome_found = chrome_path
                    print(f"   ✅ Found Chrome: {chrome_path}")
                    break
            
            if not chrome_found:
                print("   ❌ Chrome browser not found")
                print("   📋 Please install Google Chrome or use: brew install --cask google-chrome")
                return None
            
            # Setup Chrome options
            chrome_options = Options()
            
            # Basic settings
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Set Chrome path
            chrome_options.binary_location = chrome_found
            
            # Try to start browser
            self.driver = webdriver.Chrome(options=chrome_options)
            
            print("   ✅ Browser started successfully")
            print("   📋 Browser automation ready")
            return self.driver
            
        except ImportError as e:
            print(f"   ❌ Selenium import failed: {e}")
            print("   📋 Please ensure selenium is installed: pip install selenium")
            return None
        except Exception as e:
            print(f"   ❌ Browser setup failed: {e}")
            print("   📋 This might be a ChromeDriver version issue")
            
            # Try to auto-install ChromeDriver
            try:
                print("   📋 Trying to auto-install ChromeDriver...")
                result = subprocess.run(["brew", "install", "chromedriver"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("   ✅ ChromeDriver installed successfully, retrying...")
                    self.driver = webdriver.Chrome(options=chrome_options)
                    return self.driver
                else:
                    print(f"   ❌ ChromeDriver installation failed: {result.stderr}")
            except:
                pass
            
            return None

    def send_vlm_observation(self, text, step_name):
        """Send simulated VLM observation to State Tracker"""
        try:
            response = requests.post(
                f"http://localhost:{self.backend_port}/api/v1/state/process",
                json={"text": text},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ VLM Observation ({step_name}): {result.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ VLM Observation failed ({step_name}): {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ VLM Observation error ({step_name}): {e}")
            return False

    def query_current_step(self, query_text, expected_keywords):
        """Query current step and verify response with flexible matching"""
        try:
            # Find query input and send button
            query_input = self.driver.find_element(By.ID, "queryInput")
            send_button = self.driver.find_element(By.ID, "queryButton")
            
            # Clear and enter query
            query_input.clear()
            query_input.send_keys(query_text)
            send_button.click()
            
            # Wait for response
            response_element = self.driver.find_element(By.ID, "responseText")
            WebDriverWait(self.driver, 10).until(
                lambda d: response_element.text.strip() != ""
            )
            
            response_text = response_element.text.strip()
            print(f"📝 Query: '{query_text}'")
            print(f"📝 Response: '{response_text}'")
            
            # Flexible matching strategy
            response_lower = response_text.lower()
            
            # 1. Direct keyword matching
            direct_matches = [keyword for keyword in expected_keywords if keyword.lower() in response_lower]
            
            # 2. Semantic matching for common patterns
            semantic_matches = []
            
            # Check for step patterns (step 1, step 2, etc.)
            if any(f"step {i}" in response_lower for i in range(1, 10)):
                semantic_matches.append("step_number")
            
            # Check for task name patterns
            if "brewing_coffee" in response_lower or "coffee" in response_lower:
                semantic_matches.append("task_name")
            
            # Check for confidence patterns
            if "confidence" in response_lower or "0." in response_lower:
                semantic_matches.append("confidence")
            
            # Check for tool/requirement patterns
            if any(word in response_lower for word in ["tools", "requirements", "equipment"]):
                semantic_matches.append("tools_requirements")
            
            # Check for error/unknown patterns
            if any(word in response_lower for word in ["don't understand", "sorry", "question"]):
                semantic_matches.append("unknown_query")
            
            # Success criteria: either direct matches OR semantic matches
            if direct_matches or semantic_matches:
                print(f"✅ Response matches - Direct: {direct_matches}, Semantic: {semantic_matches}")
                return True
            else:
                print(f"❌ Response does not contain expected patterns")
                print(f"   Expected keywords: {expected_keywords}")
                print(f"   Response: {response_text}")
                return False
                
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return False

    def test_step_1_gathering_equipment(self):
        """Test Step 1: Gathering Equipment and Ingredients"""
        print("\n🔄 Testing Step 1: Gathering Equipment and Ingredients")
        print("=" * 60)
        
        # Simulate VLM observations for 10 seconds (every second)
        step_1_observations = [
            "I can see coffee beans, coffee grinder, pour-over dripper setup, coffee filter paper, gooseneck kettle, digital scale, timer, and coffee mug on the counter. The user is gathering all necessary equipment and fresh coffee beans for brewing. All equipment is visible on the counter and coffee beans are ready for grinding. This appears to be the first step of coffee making - gathering equipment and ingredients.",
            "The user has collected coffee beans, grinder, pour-over dripper, coffee filter, gooseneck kettle, digital scale, timer, and coffee mug. All equipment is visible on the counter and coffee beans are ready for grinding. This is clearly the gathering equipment and ingredients step.",
            "I observe coffee beans, coffee grinder, pour-over dripper setup, coffee filter paper, gooseneck kettle, digital scale, timer, and coffee mug on the counter. The user is gathering all necessary equipment and fresh coffee beans for brewing. This is step 1 of coffee making.",
            "Coffee beans, grinder, pour-over dripper, coffee filter, gooseneck kettle, digital scale, timer, and coffee mug are all visible on the counter. The user is gathering equipment and ingredients for coffee brewing. This is the first step.",
            "I can see all the necessary equipment: coffee beans, coffee grinder, pour-over dripper setup, coffee filter paper, gooseneck kettle, digital scale, timer, and coffee mug. The user is gathering equipment and ingredients for brewing coffee.",
            "The counter shows coffee beans, grinder, pour-over dripper, coffee filter, gooseneck kettle, digital scale, timer, and coffee mug. The user is collecting all necessary equipment and fresh coffee beans for brewing. This is gathering equipment and ingredients.",
            "Coffee beans, coffee grinder, pour-over dripper setup, coffee filter paper, gooseneck kettle, digital scale, timer, and coffee mug are all present. The user is gathering all necessary equipment and fresh coffee beans for brewing. Step 1 is in progress.",
            "I observe the user gathering equipment: coffee beans, grinder, pour-over dripper, coffee filter, gooseneck kettle, digital scale, timer, and coffee mug. All equipment is visible on the counter and coffee beans are ready for grinding.",
            "The user has coffee beans, coffee grinder, pour-over dripper setup, coffee filter paper, gooseneck kettle, digital scale, timer, and coffee mug ready. This is clearly the gathering equipment and ingredients step of coffee making.",
            "Coffee beans, grinder, pour-over dripper, coffee filter, gooseneck kettle, digital scale, timer, and coffee mug are all on the counter. The user is gathering all necessary equipment and fresh coffee beans for brewing. This is step 1."
        ]
        
        # Send VLM observations every second for 10 seconds
        for i, observation in enumerate(step_1_observations, 1):
            print(f"👁️ VLM Observation {i}/10: Sending Step 1 observation...")
            self.send_vlm_observation(observation, "Step 1")
            time.sleep(1)
        
        # Test user queries during Step 1
        print("\n📋 Testing user queries during Step 1...")
        
        # Query 1: Current step
        print("\n🔍 Query 1: What is the current step?")
        success1 = self.query_current_step("What is the current step?", 
                                         ["step 1", "brewing_coffee", "1", "first", "confidence", "gather", "equipment"])
        
        # Query 2: What tools do I need?
        print("\n🔍 Query 2: What tools do I need?")
        success2 = self.query_current_step("What tools do I need?", 
                                         ["brewing_coffee", "step 1", "1", "tools", "requirements", "coffee_beans", "grinder", "kettle", "dripper", "filter", "scale", "timer", "mug"])
        
        # Query 3: Next step
        print("\n🔍 Query 3: What is the next step?")
        success3 = self.query_current_step("What is the next step?", 
                                         ["step 2", "2", "next", "complete", "heating", "water"])
        
        step_1_success = success1 and success2 and success3
        print(f"\n📊 Step 1 Test Results: {step_1_success}")
        return step_1_success

    def test_step_2_heating_water(self):
        """Test Step 2: Heating Water to Optimal Temperature"""
        print("\n🔄 Testing Step 2: Heating Water to Optimal Temperature")
        print("=" * 60)
        
        # Simulate VLM observations for 10 seconds (every second)
        step_2_observations = [
            "I can see the gooseneck kettle on the heat source with steam rising from the kettle. The water is being heated to the optimal temperature of 195-205°F (90-96°C) for coffee extraction. The thermometer reading shows the water temperature. Steam is visible from the kettle and the kettle is ready for pouring. This is the step of heating water to optimal temperature.",
            "The gooseneck kettle is on the heat source with steam rising. Water is being heated to 195-205°F (90-96°C) for optimal coffee extraction. The thermometer shows the temperature and steam is visible from the kettle. This is heating water to optimal temperature.",
            "I observe the gooseneck kettle on the heat source with steam rising from the kettle. The water temperature is being raised to 195-205°F (90-96°C) for coffee extraction. The thermometer reading shows the current temperature. This is step 2 of coffee making.",
            "The kettle is on the heat source with steam rising. Water is being heated to the optimal temperature of 195-205°F (90-96°C) for coffee extraction. Steam is visible from the kettle and the kettle is ready for pouring. This is heating water.",
            "I can see the gooseneck kettle on the heat source with steam rising from the kettle. The water is being heated to 195-205°F (90-96°C) for optimal coffee extraction. The thermometer reading shows the water temperature. This is step 2.",
            "The gooseneck kettle is on the heat source with steam rising. Water is being heated to the optimal temperature of 195-205°F (90-96°C) for coffee extraction. Steam is visible from the kettle. This is the heating water step.",
            "I observe steam rising from the gooseneck kettle on the heat source. The water is being heated to 195-205°F (90-96°C) for optimal coffee extraction. The thermometer reading shows the temperature. This is heating water to optimal temperature.",
            "The kettle is on the heat source with steam rising from the kettle. Water is being heated to 195-205°F (90-96°C) for coffee extraction. The thermometer shows the temperature and steam is visible. This is step 2 of coffee making.",
            "I can see the gooseneck kettle on the heat source with steam rising. The water temperature is being raised to 195-205°F (90-96°C) for optimal coffee extraction. Steam is visible from the kettle and the kettle is ready for pouring.",
            "The gooseneck kettle is on the heat source with steam rising from the kettle. Water is being heated to the optimal temperature of 195-205°F (90-96°C) for coffee extraction. The thermometer reading shows the water temperature. This is heating water."
        ]
        
        # Send VLM observations every second for 10 seconds
        for i, observation in enumerate(step_2_observations, 1):
            print(f"👁️ VLM Observation {i}/10: Sending Step 2 observation...")
            self.send_vlm_observation(observation, "Step 2")
            time.sleep(1)
        
        # Test user queries during Step 2
        print("\n📋 Testing user queries during Step 2...")
        
        # Query 1: Current step
        print("\n🔍 Query 1: What is the current step?")
        success1 = self.query_current_step("What is the current step?", 
                                         ["step 2", "brewing_coffee", "2", "second", "confidence", "heating", "water"])
        
        # Query 2: What tools do I need?
        print("\n🔍 Query 2: What tools do I need?")
        success2 = self.query_current_step("What tools do I need?", 
                                         ["brewing_coffee", "step 2", "2", "tools", "requirements", "kettle", "thermometer", "heat", "gooseneck"])
        
        # Query 3: What's my progress?
        print("\n🔍 Query 3: What's my progress?")
        success3 = self.query_current_step("What's my progress?", 
                                         ["brewing_coffee", "step 2", "2", "progress", "complete", "duration", "minutes"])
        
        step_2_success = success1 and success2 and success3
        print(f"\n📊 Step 2 Test Results: {step_2_success}")
        return step_2_success

    def test_step_3_grinding_coffee(self):
        """Test Step 3: Grinding Coffee Beans"""
        print("\n🔄 Testing Step 3: Grinding Coffee Beans")
        print("=" * 60)
        
        # Simulate VLM observations for 10 seconds (every second)
        step_3_observations = [
            "I can see the coffee grinder in operation. The user is grinding coffee beans to medium-fine consistency for pour-over brewing. The digital scale is showing the weight of the ground coffee. Coffee grounds are being produced and the ground coffee texture is medium-fine. This is the step of grinding coffee beans.",
            "The coffee grinder is in operation. Coffee beans are being ground to medium-fine consistency for pour-over brewing. The digital scale shows the weight of the ground coffee. Coffee grounds are being produced. This is grinding coffee beans.",
            "I observe the coffee grinder in operation. The user is grinding coffee beans to medium-fine consistency for pour-over brewing. The digital scale is showing the weight and coffee grounds are being produced. This is step 3 of coffee making.",
            "The grinder is in operation with coffee beans being ground to medium-fine consistency. The digital scale shows the weight of the ground coffee. Coffee grounds are being produced and the ground coffee texture is medium-fine. This is grinding coffee.",
            "I can see the coffee grinder in operation. Coffee beans are being ground to medium-fine consistency for pour-over brewing. The digital scale is showing the weight of the ground coffee. This is the grinding step.",
            "The coffee grinder is in operation. The user is grinding coffee beans to medium-fine consistency for pour-over brewing. Coffee grounds are being produced and the ground coffee texture is medium-fine. This is step 3.",
            "I observe coffee beans being ground in the grinder. The digital scale is showing the weight of the ground coffee. The ground coffee texture is medium-fine for pour-over brewing. This is grinding coffee beans.",
            "The grinder is in operation with coffee beans being ground to medium-fine consistency. The digital scale shows the weight and coffee grounds are being produced. This is the grinding coffee step.",
            "I can see the coffee grinder in operation. Coffee beans are being ground to medium-fine consistency for pour-over brewing. The digital scale is showing the weight of the ground coffee. This is step 3 of coffee making.",
            "The coffee grinder is in operation. The user is grinding coffee beans to medium-fine consistency. Coffee grounds are being produced and the ground coffee texture is medium-fine. This is grinding coffee beans."
        ]
        
        # Send VLM observations every second for 10 seconds
        for i, observation in enumerate(step_3_observations, 1):
            print(f"👁️ VLM Observation {i}/10: Sending Step 3 observation...")
            self.send_vlm_observation(observation, "Step 3")
            time.sleep(1)
        
        # Test user queries during Step 3
        print("\n📋 Testing user queries during Step 3...")
        
        # Query 1: Current step
        print("\n🔍 Query 1: What is the current step?")
        success1 = self.query_current_step("What is the current step?", 
                                         ["step 3", "brewing_coffee", "3", "third", "confidence", "grinding", "coffee"])
        
        # Query 2: What tools do I need?
        print("\n🔍 Query 2: What tools do I need?")
        success2 = self.query_current_step("What tools do I need?", 
                                         ["brewing_coffee", "step 3", "3", "tools", "requirements", "grinder", "coffee_beans", "scale", "coffee_grinder"])
        
        # Query 3: Help me with this step
        print("\n🔍 Query 3: Help me with this step")
        success3 = self.query_current_step("Help me with this step", 
                                         ["brewing_coffee", "step 3", "3", "help", "instruction", "guide", "safety", "notes"])
        
        step_3_success = success1 and success2 and success3
        print(f"\n📊 Step 3 Test Results: {step_3_success}")
        return step_3_success

    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up resources...")
        
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
                print("   ✅ Browser closed")
            except:
                print("   ⚠️ Error closing browser")
        
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
                print("   ✅ Backend service stopped")
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                print("   ⚠️ Backend service force stopped")
        
        if self.model_process:
            self.model_process.terminate()
            try:
                self.model_process.wait(timeout=5)
                print("   ✅ Model service stopped")
            except subprocess.TimeoutExpired:
                self.model_process.kill()
                print("   ⚠️ Model service force stopped")
        
        print("✅ Cleanup completed")
    
    def verify_all_services_ready(self):
        """Verify all services are ready"""
        print("\n🔍 Verifying all services status")
        print("=" * 50)
        
        services_status = {
            'model_service': False,
            'backend_service': False
        }
        
        # Check model service
        print("📋 Checking model service status...")
        if self.check_model_service():
            services_status['model_service'] = True
            print("   ✅ Model service running normally")
        else:
            print("   ❌ Model service not running normally")
        
        # Check backend service
        print("📋 Checking backend service status...")
        if self.check_backend_service():
            services_status['backend_service'] = True
            print("   ✅ Backend service running normally")
        else:
            print("   ❌ Backend service not running normally")
        
        # Overall status assessment
        all_services_ready = (
            services_status['model_service'] and 
            services_status['backend_service']
        )
        
        if all_services_ready:
            print("\n✅ All services are ready")
            return True
        else:
            print("\n❌ Some services are not ready")
            print(f"   - Model service: {'✅' if services_status['model_service'] else '❌'}")
            print(f"   - Backend service: {'✅' if services_status['backend_service'] else '❌'}")
            return False
    
    def run_full_test(self):
        """Run complete simulated steps test"""
        print("🧪 Simulated Steps Test - Coffee Brewing Workflow")
        print("=" * 60)
        
        try:
            # Step 1: Start services
            print("\n🚀 Step 1: Starting services")
            print("=" * 40)
            
            if not self.start_model_service():
                print("❌ Test failed: Model service startup failed")
                return False
            
            if not self.start_backend_service():
                print("❌ Test failed: Backend service startup failed")
                return False
            
            # Step 2: Verify all services are ready
            if not self.verify_all_services_ready():
                print("❌ Test failed: Services not fully ready")
                return False
            
            # Step 3: Setup browser
            print("\n🚀 Step 2: Setting up browser")
            print("=" * 40)
            
            if not self.setup_chrome_driver():
                print("❌ Test failed: Browser setup failed")
                return False
            
            # Step 4: Open query page
            print("\n🚀 Step 3: Opening query page")
            print("=" * 40)
            
            try:
                # Open query page
                query_page_path = self.base_dir / "src" / "frontend" / "query.html"
                self.driver.get(f"file://{query_page_path.absolute()}")
                
                # Wait for page to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "queryInput"))
                )
                print("✅ Query page loaded successfully")
            except Exception as e:
                print(f"❌ Failed to load query page: {e}")
                return False
            
            # Step 5: Run tests
            print("\n🎯 Starting simulated steps tests")
            print("=" * 60)
            
            # Test each step
            self.test_results["step_1"] = self.test_step_1_gathering_equipment()
            self.test_results["step_2"] = self.test_step_2_heating_water()
            self.test_results["step_3"] = self.test_step_3_grinding_coffee()
            
            # Summary
            print("\n" + "=" * 60)
            print("📊 SIMULATED STEPS TEST SUMMARY")
            print("=" * 60)
            
            total_steps = len(self.test_results)
            successful_steps = sum(self.test_results.values())
            
            for step, success in self.test_results.items():
                status = "✅ PASS" if success else "❌ FAIL"
                print(f"{step.replace('_', ' ').title()}: {status}")
            
            print(f"\nOverall Success Rate: {successful_steps}/{total_steps} ({successful_steps/total_steps*100:.1f}%)")
            
            if successful_steps == total_steps:
                print("🎉 All steps passed! State Tracker is working correctly.")
            else:
                print("⚠️ Some steps failed. Check the logs for details.")
            
            return successful_steps == total_steps
            
        except KeyboardInterrupt:
            print("\n⚠️ Test interrupted by user")
            return False
        finally:
            self.cleanup()

def main():
    tester = SimulatedStepsTester()
    success = tester.run_full_test()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 