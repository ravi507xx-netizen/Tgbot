#!/usr/bin/env python3
"""
Keep-alive service for 24/7 operation of the Flask application
This script runs in the background to keep the application alive
"""

import os
import time
import requests
import threading
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('keep_alive.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class KeepAliveService:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.environ.get('RENDER_URL', 'http://localhost:5000')
        self.health_endpoint = f"{self.base_url}/health"
        self.cleanup_endpoint = f"{self.base_url}/cleanup"
        self.ping_interval = 300  # 5 minutes
        self.cleanup_interval = 1800  # 30 minutes
        self.running = False
        
    def health_check(self):
        """Perform health check on the application"""
        try:
            response = requests.get(self.health_endpoint, timeout=30)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Health check passed: {data}")
                return True
            else:
                logger.warning(f"Health check failed with status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check error: {e}")
            return False
    
    def cleanup_expired_links(self):
        """Clean up expired links"""
        try:
            response = requests.get(self.cleanup_endpoint, timeout=30)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Cleanup completed: {data}")
            else:
                logger.warning(f"Cleanup failed with status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Cleanup error: {e}")
    
    def ping_worker(self):
        """Background worker for health checks"""
        logger.info("Starting ping worker...")
        while self.running:
            try:
                success = self.health_check()
                if not success:
                    logger.warning("Health check failed, will retry in next interval")
                time.sleep(self.ping_interval)
            except Exception as e:
                logger.error(f"Error in ping worker: {e}")
                time.sleep(60)  # Wait 1 minute before retry
    
    def cleanup_worker(self):
        """Background worker for cleanup tasks"""
        logger.info("Starting cleanup worker...")
        while self.running:
            try:
                self.cleanup_expired_links()
                time.sleep(self.cleanup_interval)
            except Exception as e:
                logger.error(f"Error in cleanup worker: {e}")
                time.sleep(600)  # Wait 10 minutes before retry
    
    def start(self):
        """Start the keep-alive service"""
        if self.running:
            logger.warning("Keep-alive service is already running")
            return
        
        self.running = True
        logger.info(f"Starting keep-alive service for {self.base_url}")
        
        # Start health check worker
        ping_thread = threading.Thread(target=self.ping_worker, daemon=True)
        ping_thread.start()
        logger.info("Health check worker started")
        
        # Start cleanup worker
        cleanup_thread = threading.Thread(target=self.cleanup_worker, daemon=True)
        cleanup_thread.start()
        logger.info("Cleanup worker started")
        
        # Initial health check
        if self.health_check():
            logger.info("Initial health check passed")
        else:
            logger.warning("Initial health check failed")
    
    def stop(self):
        """Stop the keep-alive service"""
        logger.info("Stopping keep-alive service...")
        self.running = False
    
    def run_forever(self):
        """Run the service indefinitely"""
        self.start()
        try:
            while self.running:
                time.sleep(10)  # Main thread sleep
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping service...")
        finally:
            self.stop()

def main():
    """Main function for keep-alive service"""
    # Get the URL from environment or use default
    render_url = os.environ.get('RENDER_URL')
    
    if render_url:
        logger.info(f"Using RENDER_URL: {render_url}")
        service = KeepAliveService(render_url)
    else:
        # Try to detect the URL from common environment variables
        service_name = os.environ.get('SERVICE_NAME', 'telegram-link-generator')
        region = os.environ.get('RENDER_REGION', 'us-west1')
        
        # Common Render URL patterns
        possible_urls = [
            f"https://{service_name}.onrender.com",
            f"https://{service_name}-{os.environ.get('SERVICE_ID', 'default')}.onrender.com",
            f"https://{service_name}.{region}.onrender.com"
        ]
        
        logger.info("RENDER_URL not found, trying to detect URL...")
        service = KeepAliveService()
        
        # Test each possible URL
        for url in possible_urls:
            try:
                test_service = KeepAliveService(url)
                if test_service.health_check():
                    logger.info(f"Found working URL: {url}")
                    service = test_service
                    break
            except Exception:
                continue
    
    service.run_forever()

if __name__ == '__main__':
    # Check if this is running in production environment
    if os.environ.get('RENDER'):
        # Production mode
        logger.info("Running in production mode on Render")
        main()
    else:
        # Development mode
        logger.info("Running in development mode")
        
        # For development, we can also create a simple standalone version
        import signal
        import sys
        
        service = KeepAliveService()
        
        def signal_handler(signum, frame):
            logger.info("Received shutdown signal, stopping service...")
            service.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        service.run_forever()