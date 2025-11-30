"""
Simple Locust load test for ResNet Ensemble model with dynamic batching.

This test sends individual images from multiple concurrent users.
Triton server will automatically batch them at the resnet_model level.

Usage:
    # Basic test with 10 users (tests dynamic batching)
    locust -f tests/locustfile_resnet.py --host=http://localhost:8000 --users 10 --spawn-rate 2 --run-time 30s

    # Web UI mode
    locust -f tests/locustfile_resnet.py --host=http://localhost:8000

    # Headless with HTML report
    locust -f tests/locustfile_resnet.py --host=http://localhost:8000 --users 20 --spawn-rate 5 --run-time 60s --headless --html resnet-report.html
"""

from locust import HttpUser, task, between, events
import tritonclient.http as httpclient
import numpy as np
import random
import time


class ResNetLoadTest(HttpUser):
    """
    Load test for ResNet Ensemble model with dynamic batching.
    Each user sends single images - Triton batches them automatically at the model level.
    """
    
    wait_time = between(0.1, 0.5)  # Short wait to create concurrent requests
    
    def on_start(self):
        """Called when a user starts - initialize tritonclient"""
        # Extract host without protocol for tritonclient
        host = self.host.replace('http://', '').replace('https://', '')
        self.triton_client = httpclient.InferenceServerClient(url=host, verbose=False)
    
    @task(5)  # Weight: 5 - Standard 224x224 images
    def inference_standard_size(self):
        """Test with standard 224x224 images"""
        self._single_image_inference(224, 224, "Standard 224x224")
    
    @task(3)  # Weight: 3 - Small images
    def inference_small_size(self):
        """Test with small images (will be resized by preprocessor)"""
        size = random.choice([128, 160, 192])
        self._single_image_inference(size, size, f"Small {size}x{size}")
    
    @task(2)  # Weight: 2 - Large images
    def inference_large_size(self):
        """Test with large images (will be resized by preprocessor)"""
        size = random.choice([256, 320, 384])
        self._single_image_inference(size, size, f"Large {size}x{size}")
    
    @task(1)  # Weight: 1 - Variable rectangular images
    def inference_variable_size(self):
        """Test with variable rectangular images"""
        heights = [200, 224, 256, 300]
        widths = [200, 224, 256, 300]
        h = random.choice(heights)
        w = random.choice(widths)
        self._single_image_inference(h, w, f"Variable {h}x{w}")
    
    def _single_image_inference(self, height, width, name_suffix):
        """Helper method to perform single image inference"""
        start_time = time.time()
        
        try:
            # Generate random image (H, W, C) - NO batch dimension
            image = np.random.randint(0, 255, size=(height, width, 3), dtype=np.uint8)
            
            # Create input (Triton will handle batching internally)
            inputs = [httpclient.InferInput('INPUT__0', image.shape, 'UINT8')]
            inputs[0].set_data_from_numpy(image)
            
            # Create output request
            outputs = [httpclient.InferRequestedOutput('LABELS')]
            
            # Perform inference
            response = self.triton_client.infer('resnet_ensemble', inputs, outputs=outputs)
            
            # Get result
            labels = response.as_numpy('LABELS')
            
            # Report success
            total_time = int((time.time() - start_time) * 1000)
            self.environment.events.request.fire(
                request_type="TRITON",
                name=name_suffix,
                response_time=total_time,
                response_length=len(labels),
                exception=None,
                context={}
            )
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            self.environment.events.request.fire(
                request_type="TRITON",
                name=name_suffix,
                response_time=total_time,
                response_length=0,
                exception=e,
                context={}
            )


# Event handlers for better logging
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when the test starts"""
    print("\n" + "=" * 70)
    print("🚀 Starting ResNet Ensemble Load Test with Dynamic Batching")
    print("=" * 70)
    print(f"Target: {environment.host}")
    if hasattr(environment.parsed_options, 'num_users'):
        print(f"Users: {environment.parsed_options.num_users}")
    print("\n💡 Each user sends single images")
    print("💡 Triton automatically batches them at the model level")
    print("=" * 70 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when the test stops"""
    stats = environment.stats
    print("\n" + "=" * 70)
    print("🏁 ResNet Ensemble Load Test Complete")
    print("=" * 70)
    print(f"Total Requests: {stats.total.num_requests}")
    print(f"Total Failures: {stats.total.num_failures}")
    print(f"Average Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"Requests/sec: {stats.total.total_rps:.2f}")
    if stats.total.num_requests > 0:
        success_rate = ((stats.total.num_requests - stats.total.num_failures) / stats.total.num_requests * 100)
        print(f"Success Rate: {success_rate:.2f}%")
    print("\n💡 Dynamic batching combines concurrent requests automatically")
    print("=" * 70 + "\n")
