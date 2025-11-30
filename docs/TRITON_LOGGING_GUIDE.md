# Triton Server Logging Guide

This guide explains how to view and monitor logs from your Triton Inference Server running in Docker.

## Quick Reference

| Command | Purpose |
|---------|---------|
| `docker logs triton_server --tail 100` | View last 100 log lines |
| `docker logs triton_server --follow` | Live stream logs (Ctrl+C to stop) |
| `docker logs triton_server --timestamps` | Show logs with timestamps |
| `docker logs triton_server 2>&1 \| grep "ERROR"` | Filter for errors only |
| `curl -X POST http://localhost:8000/v2/repository/index` | List all models |
| `curl http://localhost:8000/v2/models/MODEL_NAME` | Check specific model status |

---

## 1. View Recent Logs

### Last 100 Lines
```bash
docker logs triton_server --tail 100
```

### Last 50 Lines
```bash
docker logs triton_server --tail 50
```

### All Logs (Warning: Can be very long)
```bash
docker logs triton_server
```

### With Timestamps
```bash
docker logs triton_server --timestamps --tail 100
```

---

## 2. Real-Time Log Monitoring

### Follow All New Logs
```bash
# Press Ctrl+C to stop
docker logs triton_server --follow
```

### Follow with Tail (Show last 20 lines, then stream)
```bash
docker logs triton_server --tail 20 --follow
```

### Follow with Timestamps
```bash
docker logs triton_server --follow --timestamps
```

---

## 3. Filter and Search Logs

### Show Only Errors
```bash
docker logs triton_server 2>&1 | grep -i error
```

### Show Python Model Logs
```bash
# Your logging.info() statements appear as "INFO:root"
docker logs triton_server 2>&1 | grep "INFO:root"
```

### Show Logs for Specific Model
```bash
# Example: sentiment model
docker logs triton_server 2>&1 | grep sentiment

# Example: linear_regression_model
docker logs triton_server 2>&1 | grep linear_regression
```

### Show Model Loading Logs
```bash
docker logs triton_server 2>&1 | grep "loading:"
```

### Show HTTP Requests
```bash
docker logs triton_server 2>&1 | grep "HTTP request"
```

### Combine Filters (Show errors for specific model)
```bash
docker logs triton_server 2>&1 | grep sentiment | grep -i error
```

---

## 4. Save Logs to File

### Save All Logs
```bash
docker logs triton_server > triton_logs.txt 2>&1
```

### Save Recent Logs
```bash
docker logs triton_server --tail 500 > triton_recent.txt 2>&1
```

### Save Logs with Timestamps
```bash
docker logs triton_server --timestamps > triton_logs_timestamped.txt 2>&1
```

### Save Filtered Logs (Errors Only)
```bash
docker logs triton_server 2>&1 | grep -i error > triton_errors.txt
```

---

## 5. Understanding Log Levels

Triton uses different log prefixes:

| Prefix | Meaning | Example |
|--------|---------|---------|
| `I` | Info | `I1130 09:27:24.676713 1 http_server.cc:3452] HTTP request` |
| `W` | Warning | `W1130 10:15:32.123456 1 model.cc:123] Warning message` |
| `E` | Error | `E1130 10:20:45.654321 1 model.cc:456] Error message` |
| `INFO:root` | Python logging.info() | `INFO:root:Processing 1 requests` |
| `WARNING:root` | Python logging.warning() | `WARNING:root:Low confidence detected` |
| `ERROR:root` | Python logging.error() | `ERROR:root:Failed to process request` |

---

## 6. Common Log Patterns

### Model Loading
```bash
docker logs triton_server 2>&1 | grep "loading:"
```
Example output:
```
I1129 20:48:04.629783 1 model_lifecycle.cc:462] loading: sentiment:1
```

### Model Execution
```bash
docker logs triton_server 2>&1 | grep "executing"
```
Example output:
```
I1130 09:27:24.681792 1 python_be.cc:1270] model sentiment, instance sentiment_0_0, executing 1 requests
```

### Inference Requests
```bash
docker logs triton_server 2>&1 | grep "infer"
```

### Response Outputs
```bash
docker logs triton_server 2>&1 | grep "response output"
```

---

## 7. Python Model Logging

### Current Logging in sentiment/1/model.py

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In initialize():
logging.info("Model initialized successfully")

# In execute():
logging.info(f"Processing {len(requests)} requests")
logging.info("Processing a request")
```

### Enhanced Logging Example

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# In initialize():
logger.info("Sentiment model initialized successfully")
logger.info(f"Model: nlptown/bert-base-multilingual-uncased-sentiment")

# In execute():
logger.info(f"Received batch of {len(requests)} requests")

for i, request in enumerate(requests):
    decoded_str = inpData[0].decode('utf-8')
    logger.debug(f"Request {i}: Processing text: '{decoded_str[:50]}...'")
    
    sentiment = self.model(decoded_str)
    label = sentiment[0]['label']
    score = sentiment[0]['score']
    
    logger.info(f"Request {i}: Predicted '{label}' with confidence {score:.3f}")
    
    if score < 0.6:
        logger.warning(f"Request {i}: Low confidence prediction: {score:.3f}")
```

### View Enhanced Logs
```bash
# All Python logs
docker logs triton_server 2>&1 | grep -E "(INFO|WARNING|ERROR):root"

# Only warnings and errors
docker logs triton_server 2>&1 | grep -E "(WARNING|ERROR):root"
```

---

## 8. Troubleshooting

### Model Not Loading
```bash
docker logs triton_server 2>&1 | grep -i "failed to load"
```

### Shared Memory Issues
```bash
docker logs triton_server 2>&1 | grep -i "shared memory"
```

### Configuration Errors
```bash
docker logs triton_server 2>&1 | grep -i "config"
```

### GPU Issues
```bash
docker logs triton_server 2>&1 | grep -i "cuda\|gpu"
```

---

## 9. Log Rotation and Management

### Check Log Size
```bash
docker logs triton_server 2>&1 | wc -l  # Count lines
```

### Clear Docker Logs (Use with caution!)
```bash
# Stop container
docker-compose down

# Remove container (logs are deleted)
docker rm triton_server

# Restart
docker-compose up -d
```

### Configure Docker Logging Driver (docker-compose.yaml)
```yaml
services:
  triton:
    image: triton-python-backend:latest
    container_name: triton_server
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 10. Quick Troubleshooting Commands

### Check if Server is Running
```bash
docker ps | grep triton_server
```

### Check Server Health
```bash
curl http://localhost:8000/v2/health/ready
```

### List All Models (Repository Index)
```bash
# List all models in the repository (requires POST method)
curl -X POST http://localhost:8000/v2/repository/index

# With verbose output
curl -X POST -v http://localhost:8000/v2/repository/index

# Pretty formatted
curl -X POST -s http://localhost:8000/v2/repository/index | python -m json.tool
```

### Check Specific Model Status
```bash
# Check sentiment model
curl http://localhost:8000/v2/models/sentiment

# Check linear regression model
curl http://localhost:8000/v2/models/linear_regression_model

# Check ensemble model
curl http://localhost:8000/v2/models/text_ensemble
```

### Check Model Status with Pretty JSON
```bash
# Format JSON output for better readability
curl -s http://localhost:8000/v2/models/sentiment | python -m json.tool

# Wait for server to start, then check (useful after restart)
sleep 10 && curl -s http://localhost:8000/v2/models/sentiment | python -m json.tool
```

**Important:** Remove angle brackets when copying URLs from documentation!
```bash
# ❌ WRONG - Don't include angle brackets (they're just placeholders in docs)
# curl <http://localhost:8000/v2/models/sentiment>
# This will cause: "zsh: no such file or directory"

# ✅ CORRECT - Just the URL without angle brackets
curl http://localhost:8000/v2/models/sentiment
```

Angle brackets `< >` are shell redirection operators and will cause errors like:
```
zsh: no such file or directory: http://localhost:8000/v2/models>
```

### Server Metadata
```bash
curl http://localhost:8000/v2

# Pretty formatted
curl -s http://localhost:8000/v2 | python -m json.tool
```

---

## 11. Common Pitfalls

### 1. Angle Brackets in URLs
**Problem:** Copying URLs with angle brackets from documentation
```bash
# ❌ This will fail - angle brackets are shell redirection operators
# curl <http://localhost:8000/api>
```

**Error:**
```
zsh: no such file or directory: http://localhost:8000/api>
```

**Why:** Shells interpret `<` and `>` as input/output redirection operators.

**Solution:** Always remove angle brackets from URLs
```bash
# ✅ Correct - no angle brackets
curl http://localhost:8000/api
```

### 2. Missing `-s` Flag with JSON Formatting
**Problem:** Progress bar interferes with JSON parsing
```bash
# ❌ May show progress info
curl http://localhost:8000/v2 | python -m json.tool
```

**Solution:** Use `-s` (silent) flag
```bash
# ✅ Clean output
curl -s http://localhost:8000/v2 | python -m json.tool
```

### 3. Forgetting `2>&1` When Grepping Docker Logs
**Problem:** Docker sends some logs to stderr, not stdout
```bash
# ❌ May miss error logs
docker logs triton_server | grep error
```

**Solution:** Redirect stderr to stdout
```bash
# ✅ Captures all logs
docker logs triton_server 2>&1 | grep error
```

---

## 12. Best Practices

1. **Use `--follow` for debugging** - Watch logs in real-time while testing
2. **Use `--tail` to limit output** - Prevents overwhelming output
3. **Add timestamps** - Helpful for performance analysis
4. **Filter aggressively** - Use grep to find what you need
5. **Save important logs** - Keep logs when diagnosing issues
6. **Add meaningful logging** - Use descriptive messages in your Python models
7. **Use appropriate log levels** - INFO for normal flow, WARNING for issues, ERROR for failures
8. **Monitor regularly** - Check logs periodically in production

---

## 13. Example Workflow

### During Development
```bash
# Terminal 1: Monitor logs
docker logs triton_server --follow --tail 20

# Terminal 2: Run your tests/requests
python test_inference.py
```

### Debugging an Issue
```bash
# 1. Check recent errors
docker logs triton_server 2>&1 | grep -i error | tail -20

# 2. Check model loading
docker logs triton_server 2>&1 | grep "sentiment" | grep "loading"

# 3. Save full context
docker logs triton_server > debug_logs.txt 2>&1

# 4. Analyze the file
less debug_logs.txt
```

### Production Monitoring
```bash
# Check for errors in last hour (approximate)
docker logs triton_server --since 1h 2>&1 | grep -i error

# Check model performance logs
docker logs triton_server --since 1h 2>&1 | grep "INFO:root" | grep -i "confidence\|score"
```

---

## Additional Resources

- [Triton Server Documentation](https://docs.nvidia.com/deeplearning/triton-inference-server/)
- [Docker Logs Documentation](https://docs.docker.com/engine/reference/commandline/logs/)
- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)

---

## Summary

**Most Commonly Used Commands:**

```bash
# Quick check
docker logs triton_server --tail 50

# Real-time monitoring
docker logs triton_server --follow --tail 20

# Find errors
docker logs triton_server 2>&1 | grep -i error

# Your Python model logs
docker logs triton_server 2>&1 | grep "INFO:root"

# Save for analysis
docker logs triton_server > logs.txt 2>&1
```

Press `Ctrl+C` to stop any following/streaming command.
