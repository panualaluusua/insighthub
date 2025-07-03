# LangSmith Integration Documentation

## Overview

This document provides comprehensive guidance for integrating, configuring, and maintaining LangSmith monitoring and debugging capabilities within the InsightHub orchestrator system.

## Table of Contents

1. [Setup and Configuration](#setup-and-configuration)
2. [Troubleshooting Guide](#troubleshooting-guide)
3. [API Key Management and Security](#api-key-management-and-security)
4. [Trace Instrumentation Patterns](#trace-instrumentation-patterns)
5. [Configuration Reference](#configuration-reference)

## Setup and Configuration

### Prerequisites

- Python 3.8 or higher
- LangSmith account with API access
- Project workspace with orchestrator components

### Installation Steps

1. **Install LangSmith SDK**
   ```bash
   pip install langsmith
   ```

2. **Set up Environment Variables**
   ```bash
   # Required for LangSmith integration
   export LANGCHAIN_TRACING_V2=true
   export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
   export LANGCHAIN_API_KEY="your_langsmith_api_key"
   export LANGCHAIN_PROJECT="InsightHub"
   ```

3. **Initialize LangSmith Project**
   ```python
   from langsmith import Client
   
   client = Client()
   
   # Create project if it doesn't exist
   try:
       project = client.create_project(
           project_name="InsightHub",
           description="Content orchestrator monitoring and debugging"
       )
   except Exception as e:
       print(f"Project may already exist: {e}")
   ```

4. **Verify Integration**
   ```bash
   python test_langsmith_dashboard.py
   ```

### Configuration Files

#### `.env` Configuration
```bash
# LangSmith Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=ls_your_api_key_here
LANGCHAIN_PROJECT=InsightHub

# Additional API Keys for traced components
DEEPSEEK_API_KEY=your_deepseek_key
OPENAI_API_KEY=your_openai_key
```

#### Project Configuration
```python
# config/langsmith_config.py
LANGSMITH_CONFIG = {
    "project_name": "InsightHub",
    "tracing_enabled": True,
    "debug_mode": False,
    "batch_size": 100,
    "timeout": 30,
    "retry_attempts": 3
}
```

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. API Key Authentication Errors

**Error**: `Authentication failed`
```
langsmith.utils.LangSmithAuthError: Authentication failed
```

**Solutions**:
- Verify API key is correct and active
- Check environment variable spelling: `LANGCHAIN_API_KEY`
- Ensure API key has proper permissions
- Test with: `python -c "from langsmith import Client; print(Client().info)"`

#### 2. Project Access Issues

**Error**: `Project not found`
```
langsmith.utils.LangSmithError: Project 'InsightHub' not found
```

**Solutions**:
- Create project manually in LangSmith dashboard
- Run project setup script: `python setup_langsmith_project.py`
- Verify project name matches exactly (case-sensitive)

#### 3. Tracing Not Appearing

**Symptoms**: Code runs but no traces appear in LangSmith dashboard

**Solutions**:
- Verify `LANGCHAIN_TRACING_V2=true` is set
- Check network connectivity to LangSmith endpoint
- Ensure `@traceable` decorators are properly applied
- Check for errors in application logs

#### 4. Performance Issues

**Symptoms**: Slow response times with tracing enabled

**Solutions**:
- Enable async tracing for non-blocking operations
- Reduce trace payload size by filtering sensitive data
- Use trace sampling for high-volume operations
- Consider local monitoring fallback

#### 5. Quota Limits

**Error**: `Rate limit exceeded`
```
langsmith.utils.LangSmithError: Rate limit exceeded
```

**Solutions**:
- Implement exponential backoff retry logic
- Use trace sampling to reduce volume
- Upgrade LangSmith plan if needed
- Implement local caching for development

### Debugging Steps

1. **Check Environment Setup**
   ```bash
   python -c "
   import os
   print('LANGCHAIN_TRACING_V2:', os.getenv('LANGCHAIN_TRACING_V2'))
   print('LANGCHAIN_API_KEY:', os.getenv('LANGCHAIN_API_KEY')[:8] + '...' if os.getenv('LANGCHAIN_API_KEY') else 'Not set')
   print('LANGCHAIN_PROJECT:', os.getenv('LANGCHAIN_PROJECT'))
   "
   ```

2. **Test API Connection**
   ```python
   from langsmith import Client
   
   try:
       client = Client()
       print("✅ Client initialized")
       print("📊 Client info:", client.info)
   except Exception as e:
       print("❌ Client setup failed:", e)
   ```

3. **Verify Project Access**
   ```python
   try:
       project = client.read_project(project_name="InsightHub")
       print("✅ Project accessible")
   except Exception as e:
       print("❌ Project access failed:", e)
   ```

4. **Test Trace Creation**
   ```python
   from langsmith import traceable
   
   @traceable
   def test_function():
       return {"test": "success"}
   
   result = test_function()
   print("Trace test result:", result)
   ```

## API Key Management and Security

### Security Best Practices

1. **Environment Variables Only**
   - Never commit API keys to version control
   - Use `.env` files for local development
   - Use secure secrets management in production

2. **Key Rotation**
   ```bash
   # Generate new API key in LangSmith dashboard
   # Update environment variables
   export LANGCHAIN_API_KEY="new_api_key"
   # Restart services
   ```

3. **Access Control**
   - Use least-privilege principle
   - Create separate keys for different environments
   - Monitor API key usage in LangSmith dashboard

4. **Production Security**
   ```bash
   # Use environment-specific secrets
   # Production
   kubectl create secret generic langsmith-secrets \
     --from-literal=api-key="prod_api_key"
   
   # Staging
   kubectl create secret generic langsmith-secrets-staging \
     --from-literal=api-key="staging_api_key"
   ```

### Key Management Script

```python
# scripts/manage_langsmith_keys.py
import os
from langsmith import Client

def validate_api_key(api_key: str) -> bool:
    """Validate API key functionality."""
    try:
        client = Client(api_key=api_key)
        client.info
        return True
    except Exception:
        return False

def rotate_api_key():
    """Guide for API key rotation."""
    print("API Key Rotation Steps:")
    print("1. Generate new key in LangSmith dashboard")
    print("2. Update environment variables")
    print("3. Test new key with validate_api_key()")
    print("4. Update production secrets")
    print("5. Restart services")

if __name__ == "__main__":
    current_key = os.getenv("LANGCHAIN_API_KEY")
    if current_key:
        is_valid = validate_api_key(current_key)
        print(f"Current API key status: {'✅ Valid' if is_valid else '❌ Invalid'}")
    else:
        print("❌ No API key found in environment")
```

## Trace Instrumentation Patterns

### Basic Tracing Pattern

```python
from langsmith import traceable

@traceable(name="node_name")
def process_content(input_data):
    """Basic tracing pattern for orchestrator nodes."""
    try:
        result = perform_processing(input_data)
        return result
    except Exception as e:
        # Error will be automatically captured in trace
        raise
```

### Advanced Tracing with Metadata

```python
from langsmith import traceable
from typing import Dict, Any

@traceable(
    name="content_summarizer",
    metadata={"model": "deepseek-chat", "temperature": 0.3}
)
def summarize_content(content: str, model_config: Dict[str, Any]) -> str:
    """Advanced tracing with custom metadata."""
    # Custom tags for filtering
    tags = [
        f"model:{model_config.get('model', 'unknown')}",
        f"content_length:{len(content)}",
        "node:summarizer"
    ]
    
    # Add custom inputs/outputs for better debugging
    trace_inputs = {
        "content_preview": content[:200] + "..." if len(content) > 200 else content,
        "content_length": len(content),
        "model_config": model_config
    }
    
    result = process_with_model(content, model_config)
    
    trace_outputs = {
        "summary": result,
        "summary_length": len(result),
        "compression_ratio": len(result) / len(content)
    }
    
    return result
```

### Error Handling Pattern

```python
from langsmith import traceable
import logging

logger = logging.getLogger(__name__)

@traceable(name="error_handling_example")
def robust_processing(data):
    """Error handling pattern with tracing."""
    try:
        # Main processing logic
        result = process_data(data)
        
        # Add success metadata
        return {
            "status": "success",
            "result": result,
            "metadata": {"processing_time": "2.5s"}
        }
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        # Error automatically captured in trace
        return {
            "status": "validation_error",
            "error": str(e),
            "recovery_action": "skip_invalid_data"
        }
        
    except APIError as e:
        logger.error(f"API error: {e}")
        # Implement retry logic
        return {
            "status": "api_error",
            "error": str(e),
            "recovery_action": "retry_with_backoff"
        }
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        # Capture unexpected errors
        return {
            "status": "unexpected_error",
            "error": str(e),
            "recovery_action": "manual_review_required"
        }
```

### Workflow-Level Tracing

```python
from langsmith import traceable
from datetime import datetime

@traceable(name="content_orchestrator_workflow")
def orchestrate_content_processing(content_url: str):
    """Complete workflow tracing pattern."""
    workflow_start = datetime.now()
    
    # Initialize workflow state
    state = {
        "content_url": content_url,
        "start_time": workflow_start.isoformat(),
        "steps_completed": [],
        "errors": []
    }
    
    try:
        # Step 1: Content Fetching
        content = fetch_content(content_url)
        state["steps_completed"].append("fetch")
        
        # Step 2: Summarization
        summary = summarize_content(content)
        state["steps_completed"].append("summarize")
        
        # Step 3: Embedding Generation
        embedding = generate_embedding(summary)
        state["steps_completed"].append("embed")
        
        # Step 4: Storage
        storage_result = store_content(summary, embedding)
        state["steps_completed"].append("store")
        
        # Final state
        state["status"] = "success"
        state["duration"] = (datetime.now() - workflow_start).total_seconds()
        
        return state
        
    except Exception as e:
        state["status"] = "error"
        state["error"] = str(e)
        state["duration"] = (datetime.now() - workflow_start).total_seconds()
        raise
```

### Custom Metrics Integration

```python
from langsmith import traceable
from src.orchestrator.monitoring.dashboard import get_monitor

monitor = get_monitor()

@traceable(name="monitored_node")
def process_with_monitoring(data):
    """Integration pattern with local monitoring."""
    # Start local monitoring
    execution_id = monitor.start_node(
        workflow_id="current_workflow",
        node_name="custom_processor",
        input_size=len(str(data))
    )
    
    try:
        result = perform_processing(data)
        
        # Complete monitoring with success
        monitor.complete_node(
            execution_id=execution_id,
            status="success",
            output_size=len(str(result))
        )
        
        return result
        
    except Exception as e:
        # Complete monitoring with error
        monitor.complete_node(
            execution_id=execution_id,
            status="error",
            error_message=str(e)
        )
        raise
```

## Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LANGCHAIN_TRACING_V2` | Yes | `false` | Enable LangSmith tracing |
| `LANGCHAIN_ENDPOINT` | Yes | - | LangSmith API endpoint |
| `LANGCHAIN_API_KEY` | Yes | - | LangSmith API key |
| `LANGCHAIN_PROJECT` | Yes | - | Project name in LangSmith |
| `LANGSMITH_BATCH_SIZE` | No | `100` | Batch size for trace uploads |
| `LANGSMITH_TIMEOUT` | No | `30` | API timeout in seconds |

### Tracing Configuration

```python
# config/tracing_config.py
TRACING_CONFIG = {
    # Global tracing settings
    "enabled": True,
    "project_name": "InsightHub",
    "environment": "production",  # or "development", "staging"
    
    # Performance settings
    "batch_size": 100,
    "upload_interval": 5,  # seconds
    "max_retries": 3,
    "timeout": 30,
    
    # Filtering settings
    "sample_rate": 1.0,  # 0.0 to 1.0
    "exclude_patterns": [
        "health_check",
        "metrics_collection"
    ],
    
    # Security settings
    "mask_inputs": False,
    "mask_outputs": False,
    "exclude_sensitive_keys": [
        "api_key",
        "password",
        "token"
    ]
}
```

### Performance Optimization

```python
# For high-volume applications
PERFORMANCE_CONFIG = {
    # Async tracing (non-blocking)
    "async_mode": True,
    
    # Sampling for high-volume operations
    "sampling": {
        "content_fetch": 1.0,      # Trace all
        "summarization": 0.1,      # Trace 10%
        "embedding": 0.05,         # Trace 5%
        "storage": 1.0             # Trace all
    },
    
    # Local buffering
    "buffer_size": 1000,
    "flush_interval": 10,
    
    # Fallback to local monitoring
    "fallback_enabled": True,
    "fallback_threshold": 5  # seconds
}
```

## Workflow Visualization & Adaptive Metrics (Tasks 38.4 & 38.5)

InsightHubin LangSmith-dashboard antaa reaaliaikaiset näkymät workflow-polkuihin ja optimointimittareihin.

### Dashboard-polut

* **Most Common Path** näyttää solmuketjun, jota käytetään useimmin (ks. `/api/enhanced-dashboard → trace_analysis.most_common_path`).
* **Node Performance** ‑kortit kuvaavat suorituskertoja, onnistumis­prosenttia ja keskimääräistä kestoa.

### Adaptive Metrics

| Metric | Lähde | Käyttötarkoitus |
|--------|-------|-----------------|
| `cache_hits` / `cache_misses` | `ContentCache.stats` | Cache-strategian tehokkuus |
| `avg_duration` & `p95_duration` | `WorkflowMetrics` | AdaptiveModelSelectorin mallivalinta |
| `error_stats` | SmartRetryManager.tune_from_metrics | Retry-viiveen kalibrointi |

OptimizerMetricsTuner kerää nämä 30 min välein (env `METRICS_TUNE_INTERVAL_MIN`) ja säätää:

1. **AdaptiveModelSelector** → mallin prioriteettikynnys per solmu
2. **SmartRetryManager** → `base_delay` virhetyyppikohtaisesti

### Quick-Start

Katso **Quick-Start: LangSmith Web Dashboard** ‑osio [LANGSMITH_OPERATIONS.md](LANGSMITH_OPERATIONS.md#quick-start-langsmith-web-dashboard) – sisältää käynnistys­komennot ja API-pisteet.

### Optimointi-asetukset

Optimointi + välimuistiin liittyvät ENV-muuttujat on koottu taulukkoon [Optimization & Cache Configuration](LANGSMITH_OPERATIONS.md#optimization--cache-configuration-task-385).

This documentation provides comprehensive coverage of LangSmith integration setup, configuration, and troubleshooting. The next sections will cover workflow documentation, operational procedures, and training materials. 