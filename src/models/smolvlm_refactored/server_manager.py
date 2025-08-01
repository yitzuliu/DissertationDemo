#!/usr/bin/env python3
"""
Unified SmolVLM Server Manager

This module provides a unified server management interface for SmolVLM,
combining the best features from both run_smolvlm.py and smolvlm_model.py.
"""

import subprocess
import sys
import time
import signal
import os
import threading
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class SmolVLMServerManager:
    """
    Unified SmolVLM server manager with enhanced functionality.
    """
    
    def __init__(self, model_name: str = "ggml-org/SmolVLM-500M-Instruct-GGUF", 
                 port: int = 8080, 
                 timeout: int = 60):
        """
        Initialize the server manager.
        
        Args:
            model_name: The model name/path
            port: Server port
            timeout: Request timeout
        """
        self.model_name = model_name
        self.port = port
        self.timeout = timeout
        self.server_url = f"http://localhost:{self.port}/v1/chat/completions"
        self.health_url = f"http://localhost:{self.port}/health"
        
        # Server process management
        self.process = None
        self.server_ready = False
        self.output_thread = None
        
        # Signal handling
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info("Received stop signal, shutting down server...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def start(self, verbose: bool = False) -> bool:
        """
        Start SmolVLM server.
        
        Args:
            verbose: Whether to print output to console
            
        Returns:
            True if server started successfully, False otherwise
        """
        if self.is_running():
            logger.info("SmolVLM server already running")
            if verbose:
                print("✅ SmolVLM server already running")
            return True
        
        cmd = [
            "llama-server",
            "-hf", self.model_name,
            "-ngl", "99",
            "--port", str(self.port)
        ]
        
        logger.info(f"Starting SmolVLM server with model: {self.model_name} on port: {self.port}")
        if verbose:
            print("🚀 Starting SmolVLM server...")
            print(f"📦 Model: {self.model_name}")
            print(f"🌐 Port: {self.port}")
            print(f"💻 Command: {' '.join(cmd)}")
            print("-" * 50)
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Start a thread to monitor server output
            def monitor_output():
                if self.process and self.process.stdout:
                    for line in iter(self.process.stdout.readline, ''):
                        line = line.rstrip()
                        logger.debug(f"SmolVLM server: {line}")
                        
                        if verbose:
                            print(line)
                        
                        if "HTTP server listening" in line or "Server listening" in line:
                            logger.info(f"SmolVLM server running at http://localhost:{self.port}")
                            self.server_ready = True
                            if verbose:
                                print(f"\n✅ SmolVLM server running at http://localhost:{self.port}")
                                print("📡 API endpoint: /v1/chat/completions")
                                print("🛑 Press Ctrl+C to stop server")
            
            self.output_thread = threading.Thread(target=monitor_output)
            self.output_thread.daemon = True
            self.output_thread.start()
            
            # Wait for server to become ready
            start_time = time.time()
            while time.time() - start_time < 30:  # Wait up to 30 seconds
                if self.server_ready:
                    return True
                if self.process.poll() is not None:
                    logger.error("SmolVLM server failed to start")
                    if verbose:
                        print("❌ SmolVLM server failed to start")
                    return False
                time.sleep(0.5)
                
            logger.warning("Timed out waiting for SmolVLM server to start")
            if verbose:
                print("⏰ Timed out waiting for SmolVLM server to start")
            return self.is_running()
            
        except FileNotFoundError:
            logger.error("Error: 'llama-server' command not found")
            if verbose:
                print("❌ Error: 'llama-server' command not found")
                print("Please ensure llama.cpp is properly installed and added to PATH")
            return False
        except Exception as e:
            logger.error(f"Error starting SmolVLM server: {str(e)}")
            if verbose:
                print(f"❌ Startup failed: {e}")
            return False
    
    def stop(self) -> bool:
        """
        Stop SmolVLM server.
        
        Returns:
            True if server stopped successfully, False otherwise
        """
        if not self.process:
            return True
            
        logger.info("Stopping SmolVLM server...")
        print("🔄 Stopping SmolVLM server...")
        
        try:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
                logger.info("SmolVLM server stopped")
                print("✅ SmolVLM server stopped")
                return True
            except subprocess.TimeoutExpired:
                logger.warning("Force stopping server...")
                print("⚠️ Force stopping server...")
                self.process.kill()
                self.process.wait()
                logger.info("SmolVLM server force stopped")
                print("✅ SmolVLM server force stopped")
                return True
        except Exception as e:
            logger.error(f"Error stopping SmolVLM server: {str(e)}")
            print(f"❌ Error stopping server: {e}")
            return False
        finally:
            self.process = None
            self.server_ready = False
    
    def is_running(self) -> bool:
        """
        Check if server is running by testing the health endpoint.
        
        Returns:
            True if server is running, False otherwise
        """
        try:
            response = requests.get(self.health_url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        Get server information.
        
        Returns:
            Dictionary containing server information
        """
        try:
            response = requests.get(self.health_url, timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Health check failed: HTTP {response.status_code}"}
        except Exception as e:
            return {"error": f"Failed to get server info: {str(e)}"}
    
    def wait_for_server(self, timeout: int = 30) -> bool:
        """
        Wait for server to become ready.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if server became ready, False if timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_running():
                return True
            time.sleep(1)
        return False 