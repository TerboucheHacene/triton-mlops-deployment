"""
Locust Load Testing for Triton Inference Server
================================================
This file defines load testing scenarios for various Triton models.

Run with:
    locust -f tests/locustfile.py --host=http://localhost:8000

Web UI:
    http://localhost:8089
"""

import json
import random
import numpy as np
from locust import HttpUser, task, between, events
import base64


class TritonUser(HttpUser):
    """
    Simulates a user making inference requests to Triton server.
    
    Configuration:
    - wait_time: 1-3 seconds between requests (adjustable)
    - host: Triton server URL (default: http://localhost:8000)
    """
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a simulated user starts"""
        # Check if server is ready
        response = self.client.get("/v2/health/ready")
        if response.status_code != 200:
            print("⚠️  WARNING: Triton server not ready!")
    
    @task(5)  # Weight: 5 (runs 5x more than others)
    def linear_regression_inference(self):
        """Test linear regression model (lightweight, fast)"""
        payload = {
            "inputs": [{
                "name": "INPUT__0",
                "shape": [1, 1],
                "datatype": "FP32",
                "data": [random.uniform(0, 10)]
            }]
        }
        
        with self.client.post(
            "/v2/models/linear_regression_model/infer",
            json=payload,
            catch_response=True,
            name="Linear Regression"
        ) as response:
            if response.status_code == 200:
                result = response.json()
                if "outputs" in result:
                    response.success()
                else:
                    response.failure("No outputs in response")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(3)  # Weight: 3
    def sentiment_inference(self):
        """Test sentiment analysis model (Python backend)"""
        texts = [
            "This product is amazing!",
            "Terrible experience, very disappointed.",
            "It's okay, nothing special.",
            "Absolutely loved it! Highly recommend!",
            "Not worth the money."
        ]
        
        payload = {
            "inputs": [{
                "name": "text",
                "shape": [1],
                "datatype": "BYTES",
                "data": [random.choice(texts)]
            }]
        }
        
        with self.client.post(
            "/v2/models/sentiment/infer",
            json=payload,
            catch_response=True,
            name="Sentiment Analysis"
        ) as response:
            if response.status_code == 200:
                result = response.json()
                if "outputs" in result and len(result["outputs"]) == 2:
                    response.success()
                else:
                    response.failure("Invalid output format")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)  # Weight: 2
    def resnet_ensemble_inference(self):
        """Test ResNet ensemble pipeline (heavier workload)"""
        # Generate random image data (224x224x3)
        # In real scenario, this would be actual image bytes
        image_data = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        payload = {
            "inputs": [{
                "name": "INPUT__0",
                "shape": list(image_data.shape),
                "datatype": "UINT8",
                "data": image_data.flatten().tolist()
            }]
        }
        
        with self.client.post(
            "/v2/models/resnet_ensemble/infer",
            json=payload,
            catch_response=True,
            name="ResNet Ensemble"
        ) as response:
            if response.status_code == 200:
                result = response.json()
                if "outputs" in result:
                    response.success()
                else:
                    response.failure("No outputs in response")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)  # Weight: 1 (least frequent)
    def multiple_requests(self):
        """Test sending multiple sequential requests"""
        for _ in range(3):
            input_val = random.uniform(0, 10)
            payload = {
                "inputs": [{
                    "name": "INPUT__0",
                    "shape": [1, 1],
                    "datatype": "FP32",
                    "data": [input_val]
                }]
            }
            
            with self.client.post(
                "/v2/models/linear_regression_model/infer",
                json=payload,
                catch_response=True,
                name="Multiple Sequential Requests"
            ) as response:
                if response.status_code == 200:
                    result = response.json()
                    if "outputs" in result:
                        response.success()
                    else:
                        response.failure("No outputs in response")
                else:
                    response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def health_check(self):
        """Test health endpoints (minimal load)"""
        with self.client.get(
            "/v2/health/ready",
            catch_response=True,
            name="Health Check"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def list_models(self):
        """Test model repository listing"""
        with self.client.post(
            "/v2/repository/index",
            catch_response=True,
            name="List Models"
        ) as response:
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    response.success()
                else:
                    response.failure("Empty or invalid model list")
            else:
                response.failure(f"Status code: {response.status_code}")


class HeavyLoadUser(HttpUser):
    """
    Simulates heavy load with complex models and larger batches.
    Use this for stress testing.
    
    Run with:
        locust -f tests/locustfile.py --host=http://localhost:8000 HeavyLoadUser
    """
    
    wait_time = between(0.5, 1.5)  # Faster requests
    
    @task
    def rapid_requests(self):
        """Test with rapid sequential requests"""
        num_requests = random.randint(5, 10)
        
        for _ in range(num_requests):
            input_val = random.uniform(0, 10)
            payload = {
                "inputs": [{
                    "name": "INPUT__0",
                    "shape": [1, 1],
                    "datatype": "FP32",
                    "data": [input_val]
                }]
            }
            
            with self.client.post(
                "/v2/models/linear_regression_model/infer",
                json=payload,
                catch_response=True,
                name=f"Heavy Load (n={num_requests})"
            ) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Status code: {response.status_code}")


class RealisticScenario(HttpUser):
    """
    Simulates realistic user behavior with mixed workloads.
    
    Run with:
        locust -f tests/locustfile.py --host=http://localhost:8000 RealisticScenario
    """
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """User session start"""
        # Check server health (like a client would)
        self.client.get("/v2/health/ready")
        # List available models
        self.client.post("/v2/repository/index")
    
    @task(10)
    def typical_inference(self):
        """Most common use case: single inference"""
        models = [
            ("linear_regression_model", "Linear"),
            ("sentiment", "Sentiment")
        ]
        model_name, label = random.choice(models)
        
        if model_name == "linear_regression_model":
            payload = {
                "inputs": [{
                    "name": "INPUT__0",
                    "shape": [1, 1],
                    "datatype": "FP32",
                    "data": [random.uniform(0, 10)]
                }]
            }
        else:  # sentiment
            texts = [
                "Great product!",
                "Not satisfied.",
                "Average quality."
            ]
            payload = {
                "inputs": [{
                    "name": "text",
                    "shape": [1],
                    "datatype": "BYTES",
                    "data": [random.choice(texts)]
                }]
            }
        
        self.client.post(
            f"/v2/models/{model_name}/infer",
            json=payload,
            name=f"Typical: {label}"
        )
    
    @task(2)
    def occasional_stress(self):
        """Occasional stress testing with multiple requests"""
        num_requests = random.randint(3, 5)
        
        for _ in range(num_requests):
            input_val = random.uniform(0, 10)
            payload = {
                "inputs": [{
                    "name": "INPUT__0",
                    "shape": [1, 1],
                    "datatype": "FP32",
                    "data": [input_val]
                }]
            }
            
            self.client.post(
                "/v2/models/linear_regression_model/infer",
                json=payload,
                name="Occasional Stress"
            )


# Custom event handlers for detailed logging
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts"""
    print("=" * 60)
    print("🚀 Starting Triton Load Test")
    print("=" * 60)
    print(f"Target: {environment.host}")
    print(f"Users: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops"""
    print("\n" + "=" * 60)
    print("🏁 Load Test Complete")
    print("=" * 60)
    
    stats = environment.stats
    print(f"Total Requests: {stats.total.num_requests}")
    print(f"Total Failures: {stats.total.num_failures}")
    print(f"Average Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"Requests/sec: {stats.total.total_rps:.2f}")
    print("=" * 60)
