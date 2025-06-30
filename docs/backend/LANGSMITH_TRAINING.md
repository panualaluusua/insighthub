# LangSmith Training Materials

## Overview

This document provides comprehensive training materials for team members to effectively use LangSmith monitoring and debugging capabilities within the InsightHub orchestrator system.

## Table of Contents

1. [Getting Started Tutorial](#getting-started-tutorial)
2. [Team Training Materials](#team-training-materials)
3. [Quick Reference Guides](#quick-reference-guides)
4. [Advanced Usage Patterns](#advanced-usage-patterns)
5. [Hands-On Exercises](#hands-on-exercises)

## Getting Started Tutorial

### Tutorial 1: Setting Up Your First Trace

**Objective**: Learn to add basic tracing to a function

**Duration**: 15 minutes

**Steps**:

1. **Install Dependencies**
   ```bash
   pip install langsmith
   ```

2. **Set Environment Variables**
   ```bash
   export LANGCHAIN_TRACING_V2=true
   export LANGCHAIN_API_KEY="your_api_key"
   export LANGCHAIN_PROJECT="InsightHub"
   ```

3. **Create Your First Traced Function**
   ```python
   # tutorial_1_basic_tracing.py
   from langsmith import traceable
   import time
   import random
   
   @traceable(name="my_first_trace")
   def process_text(text: str) -> str:
       """A simple function to demonstrate tracing."""
       # Simulate processing time
       time.sleep(random.uniform(0.5, 2.0))
       
       # Simple text processing
       word_count = len(text.split())
       processed_text = text.upper()
       
       return {
           "original_text": text,
           "processed_text": processed_text,
           "word_count": word_count,
           "status": "success"
       }
   
   if __name__ == "__main__":
       # Test the function
       sample_text = "Hello world, this is my first LangSmith trace!"
       result = process_text(sample_text)
       print(f"Result: {result}")
   ```

4. **Run and View Trace**
   ```bash
   python tutorial_1_basic_tracing.py
   ```
   
   Then visit https://smith.langchain.com/project/InsightHub to view your trace.

**Expected Outcome**: You should see your trace in the LangSmith dashboard with input/output data and execution time.

### Tutorial 2: Error Handling and Debugging

**Objective**: Learn to trace errors and debug issues

**Duration**: 20 minutes

**Steps**:

1. **Create Function with Error Scenarios**
   ```python
   # tutorial_2_error_handling.py
   from langsmith import traceable
   import random
   
   @traceable(name="error_prone_function")
   def risky_operation(input_value: int) -> dict:
       """Function that might fail to demonstrate error tracing."""
       
       if input_value < 0:
           raise ValueError("Input cannot be negative")
       
       if input_value > 100:
           raise ValueError("Input too large (max 100)")
       
       # Random failure simulation
       if random.random() < 0.3:  # 30% chance of failure
           raise RuntimeError("Random processing error occurred")
       
       # Success case
       result = input_value * 2
       return {
           "input": input_value,
           "output": result,
           "status": "success"
       }
   
   @traceable(name="safe_wrapper")
   def safe_operation(input_value: int) -> dict:
       """Wrapper with error handling."""
       try:
           return risky_operation(input_value)
       except ValueError as e:
           return {
               "input": input_value,
               "error": str(e),
               "error_type": "validation_error",
               "status": "failed"
           }
       except RuntimeError as e:
           return {
               "input": input_value,
               "error": str(e),
               "error_type": "processing_error",
               "status": "failed"
           }
   
   if __name__ == "__main__":
       # Test with various inputs
       test_values = [-5, 150, 50, 25, 75]
       
       for value in test_values:
           print(f"\nTesting with value: {value}")
           result = safe_operation(value)
           print(f"Result: {result}")
   ```

2. **Analyze Error Traces**
   - Run the script multiple times
   - Check LangSmith dashboard for error traces
   - Examine error details and stack traces
   - Practice filtering by success/error status

### Tutorial 3: Performance Monitoring

**Objective**: Learn to monitor and optimize performance

**Duration**: 25 minutes

**Steps**:

1. **Create Performance Test Functions**
   ```python
   # tutorial_3_performance.py
   from langsmith import traceable
   import time
   import random
   
   @traceable(name="fast_operation")
   def fast_function(data: str) -> str:
       """Simulates a fast operation."""
       time.sleep(0.1)  # 100ms
       return f"Fast: {data[:10]}..."
   
   @traceable(name="slow_operation")
   def slow_function(data: str) -> str:
       """Simulates a slow operation."""
       time.sleep(2.0)  # 2 seconds
       return f"Slow: {data[:10]}..."
   
   @traceable(name="variable_operation")
   def variable_function(data: str) -> str:
       """Simulates variable performance."""
       duration = random.uniform(0.5, 3.0)
       time.sleep(duration)
       return f"Variable ({duration:.1f}s): {data[:10]}..."
   
   @traceable(name="performance_comparison")
   def run_performance_test():
       """Run performance comparison."""
       test_data = "This is test data for performance monitoring"
       
       results = {}
       
       # Test each function
       start_time = time.time()
       results["fast"] = fast_function(test_data)
       results["fast_time"] = time.time() - start_time
       
       start_time = time.time()
       results["slow"] = slow_function(test_data)
       results["slow_time"] = time.time() - start_time
       
       start_time = time.time()
       results["variable"] = variable_function(test_data)
       results["variable_time"] = time.time() - start_time
       
       return results
   
   if __name__ == "__main__":
       for i in range(5):
           print(f"Run {i+1}:")
           results = run_performance_test()
           print(f"  Fast: {results['fast_time']:.2f}s")
           print(f"  Slow: {results['slow_time']:.2f}s")
           print(f"  Variable: {results['variable_time']:.2f}s")
   ```

2. **Analyze Performance Data**
   - View traces in LangSmith dashboard
   - Compare execution times
   - Identify performance patterns
   - Use filtering to find slow operations

## Team Training Materials

### Training Module 1: LangSmith Fundamentals (2 hours)

**Learning Objectives**:
- Understand LangSmith purpose and benefits
- Learn basic tracing concepts
- Practice adding traces to existing code
- Navigate LangSmith dashboard

**Agenda**:
1. **Introduction (20 min)**
   - What is LangSmith?
   - Why monitoring matters
   - InsightHub integration overview

2. **Hands-on Setup (30 min)**
   - Environment configuration
   - API key setup
   - First trace creation

3. **Dashboard Navigation (40 min)**
   - Project overview
   - Trace explorer
   - Filtering and searching
   - Performance metrics

4. **Practical Exercise (30 min)**
   - Add tracing to provided code samples
   - Debug a failing workflow
   - Share findings with team

**Materials Provided**:
- Setup checklist
- Code samples for practice
- Common error scenarios
- Dashboard navigation guide

### Training Module 2: Advanced Monitoring (1.5 hours)

**Learning Objectives**:
- Implement comprehensive error handling
- Design performance monitoring strategies
- Create custom metrics and alerts
- Collaborate effectively using traces

**Agenda**:
1. **Error Handling Patterns (30 min)**
   - Best practices for error tracing
   - Common error scenarios in InsightHub
   - Recovery strategies

2. **Performance Optimization (30 min)**
   - Identifying bottlenecks
   - Using optimization framework
   - A/B testing setup

3. **Team Collaboration (30 min)**
   - Sharing traces with team members
   - Incident response procedures
   - Code review practices

### Training Module 3: Production Operations (1 hour)

**Learning Objectives**:
- Monitor production systems
- Respond to incidents effectively
- Maintain monitoring infrastructure
- Generate reports and insights

**Agenda**:
1. **Production Monitoring (20 min)**
   - Alert configuration
   - Dashboard interpretation
   - Escalation procedures

2. **Incident Response (20 min)**
   - Response procedures
   - Communication protocols
   - Post-incident reviews

3. **Maintenance Tasks (20 min)**
   - Regular health checks
   - Backup procedures
   - System updates

## Quick Reference Guides

### Cheat Sheet: Common Tracing Patterns

```python
# Basic tracing
@traceable(name="function_name")
def my_function(param):
    return result

# With metadata
@traceable(name="function_name", metadata={"version": "1.0"})
def my_function(param):
    return result

# Error handling
@traceable(name="safe_function")
def safe_function(param):
    try:
        return process(param)
    except Exception as e:
        # Error automatically captured
        return {"error": str(e), "status": "failed"}

# Performance monitoring
@traceable(name="timed_function")
def timed_function(param):
    start_time = time.time()
    result = process(param)
    duration = time.time() - start_time
    return {"result": result, "duration": duration}
```

### Dashboard Quick Reference

**Essential Filters**:
- Status: `status:error` or `status:success`
- Time: `start_time:>2024-01-01` 
- Duration: `total_time:>10s`
- Project: `project_name:InsightHub`

**Common Views**:
- All errors: Filter by `status:error`
- Slow operations: Sort by duration (descending)
- Recent activity: Sort by start time (descending)
- Node performance: Group by trace name

**Keyboard Shortcuts**:
- `Ctrl+F`: Search traces
- `Ctrl+R`: Refresh view
- `Esc`: Clear filters
- `Enter`: Apply search

### Troubleshooting Guide

**Common Issues**:

1. **No traces appearing**
   ```bash
   # Check environment
   echo $LANGCHAIN_TRACING_V2
   echo $LANGCHAIN_API_KEY
   echo $LANGCHAIN_PROJECT
   ```

2. **403 Forbidden errors**
   - Wait for API key activation (24-72 hours)
   - Verify API key permissions
   - Check project access

3. **Slow dashboard loading**
   - Reduce time range filter
   - Use more specific filters
   - Clear browser cache

4. **Missing trace data**
   - Verify `@traceable` decorators
   - Check for exceptions in code
   - Confirm network connectivity

## Advanced Usage Patterns

### Pattern 1: Custom Metrics Integration

```python
# advanced_metrics.py
from langsmith import traceable
from src.orchestrator.monitoring.dashboard import get_monitor
import time

monitor = get_monitor()

@traceable(name="monitored_operation")
def operation_with_custom_metrics(data):
    """Function with both LangSmith and local monitoring."""
    
    # Start local monitoring
    execution_id = monitor.start_node(
        workflow_id="custom_workflow",
        node_name="advanced_operation",
        input_size=len(str(data))
    )
    
    try:
        # Simulate processing
        start_time = time.time()
        result = process_data(data)
        duration = time.time() - start_time
        
        # Complete local monitoring
        monitor.complete_node(
            execution_id=execution_id,
            status="success",
            output_size=len(str(result)),
            metadata={"custom_metric": duration},
            total_tokens=100, # Example value, replace with actual token count
            total_cost=0.001 # Example value, replace with actual cost
        )
        
        # Return with LangSmith metadata
        return {
            "result": result,
            "processing_time": duration,
            "custom_metrics": {
                "efficiency_score": len(str(result)) / duration,
                "data_compression": len(str(result)) / len(str(data))
            }
        }
        
    except Exception as e:
        monitor.complete_node(
            execution_id=execution_id,
            status="error",
            error_message=str(e)
        )
        raise
```

### Pattern 2: Conditional Tracing

```python
# conditional_tracing.py
import os
from langsmith import traceable

# Enable tracing based on environment
ENABLE_DETAILED_TRACING = os.getenv("DETAILED_TRACING", "false").lower() == "true"

def conditional_trace(name: str, detailed: bool = False):
    """Decorator for conditional tracing."""
    def decorator(func):
        if detailed and ENABLE_DETAILED_TRACING:
            return traceable(name=f"{name}_detailed")(func)
        elif not detailed:
            return traceable(name=name)(func)
        else:
            return func  # No tracing
    return decorator

@conditional_trace("content_processor", detailed=True)
def detailed_processing(content):
    """Function with detailed tracing only when enabled."""
    return process_content_with_details(content)

@conditional_trace("quick_processor")
def quick_processing(content):
    """Function with standard tracing."""
    return process_content_quickly(content)
```

### Pattern 3: Trace Sampling

```python
# trace_sampling.py
import random
from langsmith import traceable

def sampled_trace(name: str, sample_rate: float = 0.1):
    """Decorator for sampled tracing."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if random.random() < sample_rate:
                # Apply tracing
                traced_func = traceable(name=name)(func)
                return traced_func(*args, **kwargs)
            else:
                # Execute without tracing
                return func(*args, **kwargs)
        return wrapper
    return decorator

@sampled_trace("high_volume_operation", sample_rate=0.05)  # 5% sampling
def high_volume_function(data):
    """Function called frequently, traced only 5% of the time."""
    return process_high_volume_data(data)
```

## Hands-On Exercises

### Exercise 1: Debug a Failing Workflow

**Scenario**: A YouTube content processing workflow is failing intermittently.

**Task**: Use LangSmith traces to identify and fix the issue.

**Steps**:
1. Run the provided failing code
2. Examine error traces in LangSmith
3. Identify the root cause
4. Implement a fix
5. Verify the fix with new traces

**Code**:
```python
# exercise_1_debug.py
from langsmith import traceable
import random

@traceable(name="youtube_processor")
def process_youtube_content(url: str) -> dict:
    """Process YouTube content - has hidden bugs."""
    
    # Bug 1: URL validation issue
    if not url.startswith("https://youtube.com"):
        raise ValueError("Invalid YouTube URL")
    
    # Bug 2: Random network failures not handled
    if random.random() < 0.3:
        raise ConnectionError("Network timeout")
    
    # Bug 3: Content length not validated
    content = fetch_content(url)  # Returns variable length content
    
    if len(content) > 100000:  # Hidden limit
        raise ValueError("Content too long")
    
    return {"url": url, "content": content[:100], "status": "success"}

def fetch_content(url: str) -> str:
    """Simulate content fetching."""
    # Returns random length content
    length = random.randint(50, 150000)
    return "Sample content " * (length // 15)

# Test the function
if __name__ == "__main__":
    test_urls = [
        "https://youtube.com/watch?v=test1",
        "https://youtube.com/watch?v=test2",
        "http://youtube.com/watch?v=test3",  # Wrong protocol
        "https://youtube.com/watch?v=test4",
    ]
    
    for url in test_urls:
        try:
            result = process_youtube_content(url)
            print(f"✅ Success: {url}")
        except Exception as e:
            print(f"❌ Failed: {url} - {e}")
```

**Solution Hints**:
- Look for patterns in error messages
- Check input validation logic
- Implement retry mechanisms for network errors
- Add content length limits

### Exercise 2: Performance Optimization

**Scenario**: The content summarization process is running slower than expected.

**Task**: Use LangSmith performance data to optimize the workflow.

**Steps**:
1. Run the performance test suite
2. Analyze timing data in LangSmith
3. Identify bottlenecks
4. Apply optimizations from the framework
5. Compare before/after performance

**Code**:
```python
# exercise_2_performance.py
from langsmith import traceable
import time
import random

@traceable(name="slow_summarizer")
def summarize_content(content: str) -> str:
    """Slow summarization function to optimize."""
    
    # Inefficient preprocessing
    for i in range(100):
        content = content.replace(f"word{i}", f"optimized{i}")
    
    # Simulated API call with variable timing
    api_delay = random.uniform(2.0, 8.0)
    time.sleep(api_delay)
    
    # Inefficient post-processing
    words = content.split()
    summary_words = []
    for word in words:
        if len(word) > 3:  # Simple filter
            summary_words.append(word)
    
    return " ".join(summary_words[:50])  # First 50 words

@traceable(name="content_workflow")
def process_content_workflow(content: str) -> dict:
    """Full content processing workflow."""
    
    # Step 1: Validation (always slow)
    time.sleep(1.0)
    
    # Step 2: Summarization (very slow)
    summary = summarize_content(content)
    
    # Step 3: Quality check (moderately slow)
    time.sleep(0.5)
    quality_score = len(summary) / len(content)
    
    return {
        "summary": summary,
        "quality_score": quality_score,
        "original_length": len(content),
        "summary_length": len(summary)
    }

# Performance test
if __name__ == "__main__":
    test_content = "Sample content " * 1000  # Large content
    
    print("Running performance test...")
    for i in range(3):
        start_time = time.time()
        result = process_content_workflow(test_content)
        duration = time.time() - start_time
        print(f"Run {i+1}: {duration:.2f}s")
```

**Optimization Hints**:
- Use the caching framework for repeated content
- Apply parallel processing where possible
- Implement smart retry for API calls
- Consider model optimization strategies

### Exercise 3: Create Custom Dashboard

**Scenario**: Create a custom monitoring dashboard for your team.

**Task**: Build a dashboard showing key metrics for your assigned component.

**Requirements**:
- Show real-time success rate
- Display performance trends
- Alert on error thresholds
- Include custom business metrics

This training material provides comprehensive guidance for team members to become proficient with LangSmith monitoring and debugging capabilities. 