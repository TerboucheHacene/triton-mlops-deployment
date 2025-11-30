#!/usr/bin/env python3
"""
Script to verify Triton Server is performing dynamic batching on resnet_model.

This script monitors Triton metrics to show:
1. Batch size distribution (how many requests per batch)
2. Inference execution count vs request count (batching efficiency)
3. Queue times (indicates batching delay)
"""

import requests
import time
import sys


def get_metrics():
    """Fetch metrics from Triton server."""
    try:
        response = requests.get("http://localhost:8002/metrics")
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ Error fetching metrics: {e}")
        sys.exit(1)


def parse_metric(metrics_text, metric_name, model="resnet_model"):
    """Parse a specific metric value for a model."""
    for line in metrics_text.split('\n'):
        if metric_name in line and f'model="{model}"' in line:
            # Extract value (last part after space)
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    return float(parts[-1])
                except ValueError:
                    continue
    return 0


def check_batching():
    """Check if dynamic batching is working."""
    print("🔍 Checking Triton Dynamic Batching Status...\n")
    
    metrics = get_metrics()
    
    # Key metrics for resnet_model
    model = "resnet_model"
    
    # Total requests received
    requests_success = parse_metric(metrics, "nv_inference_request_success", model)
    
    # Total inference executions (batched calls)
    exec_count = parse_metric(metrics, "nv_inference_exec_count", model)
    
    # Queue duration (time spent waiting for batching)
    queue_duration_us = parse_metric(metrics, "nv_inference_queue_duration_us", model)
    
    # Compute duration
    compute_duration_us = parse_metric(metrics, "nv_inference_compute_infer_duration_us", model)
    
    print(f"📊 Metrics for '{model}':")
    print(f"{'='*60}")
    print(f"✓ Total Requests:        {int(requests_success)}")
    print(f"✓ Inference Executions:  {int(exec_count)}")
    print(f"✓ Queue Time (total):    {queue_duration_us/1e6:.2f}s")
    print(f"✓ Compute Time (total):  {compute_duration_us/1e6:.2f}s")
    print(f"{'='*60}\n")
    
    # Calculate batching efficiency
    if exec_count > 0:
        avg_batch_size = requests_success / exec_count
        batching_efficiency = (1 - exec_count / requests_success) * 100
        avg_queue_per_request_ms = (queue_duration_us / requests_success) / 1000
        avg_compute_per_execution_ms = (compute_duration_us / exec_count) / 1000
        
        print(f"🎯 Batching Analysis:")
        print(f"{'='*60}")
        print(f"Average Batch Size:      {avg_batch_size:.2f} requests/batch")
        print(f"Batching Efficiency:     {batching_efficiency:.1f}% GPU call reduction")
        print(f"Avg Queue Time/Request:  {avg_queue_per_request_ms:.2f}ms")
        print(f"Avg Compute/Execution:   {avg_compute_per_execution_ms:.2f}ms")
        print(f"{'='*60}\n")
        
        # Interpretation
        print(f"💡 Interpretation:")
        if avg_batch_size > 1.5:
            print(f"✅ BATCHING IS WORKING! Average {avg_batch_size:.1f} requests combined per GPU call.")
            print(f"   {int(requests_success)} requests executed in only {int(exec_count)} GPU calls.")
            print(f"   GPU utilization improved by {batching_efficiency:.1f}%!")
        elif avg_batch_size > 1.1:
            print(f"⚠️  PARTIAL BATCHING: Average {avg_batch_size:.1f} requests/batch.")
            print(f"   Consider increasing load or max_queue_delay for better batching.")
        else:
            print(f"❌ NO BATCHING: Each request executed separately.")
            print(f"   Check dynamic_batching configuration or increase concurrent load.")
        
        if avg_queue_per_request_ms > 5:
            print(f"\n⏱️  High queue times ({avg_queue_per_request_ms:.1f}ms) - batching delay working as expected.")
        else:
            print(f"\n⏱️  Low queue times ({avg_queue_per_request_ms:.1f}ms) - requests processed quickly.")
            
    else:
        print("⚠️  No inference executions recorded yet. Send some requests first!")
    
    # Check configuration
    print(f"\n📋 Dynamic Batching Configuration:")
    print(f"{'='*60}")
    print(f"Model: resnet_model")
    print(f"Max Batch Size: 32")
    print(f"Preferred Batch Sizes: [4, 8, 16]")
    print(f"Max Queue Delay: 1000 microseconds (1ms)")
    print(f"{'='*60}")


def monitor_batching(interval=5, duration=30):
    """Monitor batching in real-time."""
    print(f"📡 Monitoring batching for {duration} seconds (refresh every {interval}s)...\n")
    
    start_time = time.time()
    prev_requests = 0
    prev_executions = 0
    
    while time.time() - start_time < duration:
        metrics = get_metrics()
        
        requests = parse_metric(metrics, "nv_inference_request_success", "resnet_model")
        executions = parse_metric(metrics, "nv_inference_exec_count", "resnet_model")
        
        new_requests = requests - prev_requests
        new_executions = executions - prev_executions
        
        if new_executions > 0:
            batch_size = new_requests / new_executions
            print(f"⏱️  [{time.strftime('%H:%M:%S')}] "
                  f"+{int(new_requests)} requests in +{int(new_executions)} executions "
                  f"→ avg batch: {batch_size:.1f}")
        elif new_requests > 0:
            print(f"⏱️  [{time.strftime('%H:%M:%S')}] "
                  f"+{int(new_requests)} requests (waiting to batch...)")
        else:
            print(f"⏱️  [{time.strftime('%H:%M:%S')}] No new requests")
        
        prev_requests = requests
        prev_executions = executions
        
        time.sleep(interval)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Check Triton dynamic batching status")
    parser.add_argument("--monitor", action="store_true", 
                       help="Monitor batching in real-time")
    parser.add_argument("--interval", type=int, default=5,
                       help="Monitoring interval in seconds (default: 5)")
    parser.add_argument("--duration", type=int, default=30,
                       help="Monitoring duration in seconds (default: 30)")
    
    args = parser.parse_args()
    
    if args.monitor:
        monitor_batching(args.interval, args.duration)
    else:
        check_batching()
