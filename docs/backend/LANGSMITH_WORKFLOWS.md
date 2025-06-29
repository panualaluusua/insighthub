# LangSmith Workflow Documentation

## Overview

This document outlines the operational workflows for using LangSmith monitoring and debugging capabilities in the InsightHub orchestrator system.

## Table of Contents

1. [Debugging Procedures](#debugging-procedures)
2. [Performance Analysis](#performance-analysis)
3. [Dashboard Usage](#dashboard-usage)
4. [Team Collaboration](#team-collaboration)

## Debugging Procedures

### Standard Debugging Workflow

1. **Identify the Issue**
   ```bash
   # Check recent errors in local dashboard
   python -c "
   from src.orchestrator.monitoring.dashboard import get_monitor
   monitor = get_monitor()
   data = monitor.get_dashboard_data()
   print('Recent errors:', len(data.get('alerts', [])))
   "
   ```

2. **Locate Relevant Traces**
   - Access LangSmith dashboard at https://smith.langchain.com
   - Filter by project: "InsightHub"
   - Search by error status or timeframe
   - Use tags to narrow down to specific nodes

3. **Analyze Trace Details**
   - Examine input/output data
   - Check execution timing
   - Review error messages and stack traces
   - Identify bottlenecks in the workflow

### Error Pattern Analysis

**Common Error Patterns:**

1. **API Rate Limiting** (429 errors)
   ```python
   # Solution: Use SmartRetryManager
   from src.orchestrator.optimization import SmartRetryManager
   retry_manager = SmartRetryManager()
   result = retry_manager.execute_with_retry(api_call, *args)
   ```

2. **Content Processing Failures**
   ```python
   # Solution: Content validation and chunking
   def process_content_safely(content):
       if len(content) > 50000:
           chunks = chunk_content(content, max_size=10000)
           return [process_chunk(chunk) for chunk in chunks]
       return process_content(content)
   ```

3. **Embedding Token Limits**
   ```python
   # Solution: Text truncation
   def generate_embedding_safely(text):
       max_tokens = 8000
       if estimate_tokens(text) > max_tokens:
           text = truncate_text(text, max_tokens)
       return generate_embedding(text)
   ```

### Interactive Debugging

```python
# scripts/debug_console.py
from langsmith import Client

def debug_workflow(workflow_id: str):
    """Interactive debugging session."""
    client = Client()
    
    # Get workflow traces
    traces = client.list_runs(
        project_name="InsightHub",
        filter=f"workflow_id:{workflow_id}"
    )
    
    for trace in traces:
        print(f"Trace: {trace.name} - Status: {trace.status}")
        if trace.error:
            print(f"Error: {trace.error}")
        
        # Interactive inspection
        response = input("Investigate this trace? (y/n): ")
        if response.lower() == 'y':
            print(f"Inputs: {trace.inputs}")
            print(f"Outputs: {trace.outputs}")
```

## Performance Analysis

### Key Performance Indicators

```python
# scripts/performance_analyzer.py
class PerformanceAnalyzer:
    def collect_metrics(self, hours_back=24):
        """Collect performance metrics."""
        metrics = {
            "avg_duration": 0,
            "success_rate": 0,
            "p95_duration": 0,
            "node_performance": {},
            "bottlenecks": []
        }
        
        # Analyze runs and calculate metrics
        runs = self.get_recent_runs(hours_back)
        metrics["success_rate"] = self.calculate_success_rate(runs)
        metrics["avg_duration"] = self.calculate_avg_duration(runs)
        metrics["bottlenecks"] = self.identify_bottlenecks(runs)
        
        return metrics
    
    def identify_bottlenecks(self, runs):
        """Identify performance bottlenecks."""
        bottlenecks = []
        
        # Group by node type
        node_times = {}
        for run in runs:
            node_name = run.name
            if node_name not in node_times:
                node_times[node_name] = []
            if run.total_time:
                node_times[node_name].append(run.total_time)
        
        # Find slow nodes (>50% of average workflow time)
        total_avg = sum(
            sum(times)/len(times) for times in node_times.values()
        )
        
        for node, times in node_times.items():
            avg_time = sum(times) / len(times)
            if avg_time > total_avg * 0.5:
                bottlenecks.append({
                    "node": node,
                    "avg_duration": avg_time,
                    "recommendation": self.get_recommendation(node, avg_time)
                })
        
        return bottlenecks
    
    def get_recommendation(self, node_name, duration):
        """Get optimization recommendations."""
        if "summariz" in node_name.lower() and duration > 10:
            return "Consider faster model or content chunking"
        elif "embed" in node_name.lower() and duration > 5:
            return "Use smaller embedding model or batch processing"
        elif "fetch" in node_name.lower() and duration > 8:
            return "Check network or implement parallel fetching"
        return "Review implementation for optimization"
```

### Optimization Workflow

1. **Run Analysis**
   ```bash
   python scripts/performance_analyzer.py
   ```

2. **Apply Optimizations**
   ```python
   from src.orchestrator.optimization import OptimizedOrchestrator
   orchestrator = OptimizedOrchestrator()
   result = orchestrator.process_content(content_url)
   ```

3. **A/B Test Results**
   ```python
   from src.orchestrator.ab_testing import ABTestManager
   ab_manager = ABTestManager()
   
   # Create performance experiment
   experiment = ab_manager.create_experiment(
       name="optimization_test",
       control_strategy="standard",
       test_strategy="optimized",
       traffic_allocation=0.5
   )
   ```

## Dashboard Usage

### LangSmith Dashboard Navigation

**Key Sections:**
- **Project Overview**: Total runs, success rate, cost tracking
- **Trace Explorer**: Filter, search, and analyze individual traces
- **Performance Analytics**: Duration charts, success trends
- **Error Analysis**: Error frequency and categorization

**Trace Status Indicators:**
- ✅ Success: Completed without errors
- ❌ Error: Failed with exception  
- ⏸️ Pending: Still in progress
- ⚠️ Warning: Completed with warnings

### Local Dashboard Access

```python
# View local monitoring dashboard
from src.orchestrator.monitoring.dashboard import get_monitor

def display_dashboard():
    monitor = get_monitor()
    data = monitor.get_dashboard_data()
    
    print("=== InsightHub Monitoring Dashboard ===")
    print(f"Total Workflows: {data['overview']['total_workflows']}")
    print(f"Success Rate: {data['overview']['success_rate']:.1%}")
    print(f"Active Workflows: {data['overview']['active_workflows']}")
    
    # Node performance
    for node, stats in data.get('node_performance', {}).items():
        print(f"\n{node}:")
        print(f"  Avg Duration: {stats['avg_duration']:.2f}s")
        print(f"  Success Rate: {stats['success_rate']:.1%}")
```

### Web Dashboard

```python
# Start web-based dashboard
from src.orchestrator.monitoring.web_dashboard import create_app

app = create_app()
app.run(host="0.0.0.0", port=8080)
# Access at http://localhost:8080
```

## Team Collaboration

### Monitoring Standards

**Daily Checklist:**
- [ ] Review overnight error alerts
- [ ] Check performance metrics vs. targets
- [ ] Identify blocked workflows
- [ ] Review cost trends

**Weekly Reviews:**
- [ ] Performance trend analysis  
- [ ] Error pattern analysis
- [ ] A/B test results
- [ ] Cost optimization review

### Code Review Standards

**Tracing Requirements:**
- [ ] All public functions have `@traceable` decorators
- [ ] Trace names are descriptive and consistent
- [ ] Error handling includes trace context
- [ ] Sensitive data excluded from traces
- [ ] Performance impact measured

### Incident Response

```python
# scripts/incident_response.py
class IncidentResponse:
    def handle_alert(self, alert):
        """Handle critical system alerts."""
        print(f"🚨 ALERT: {alert['message']}")
        
        # Assess impact
        self.assess_impact(alert)
        
        # Gather diagnostics
        diagnostics = self.gather_diagnostics(alert)
        
        # Apply immediate fixes
        self.apply_fixes(alert, diagnostics)
        
        # Monitor resolution
        self.monitor_resolution(alert)
    
    def assess_impact(self, alert):
        """Check system health and cascade failures."""
        dashboard_data = self.monitor.get_dashboard_data()
        
        print("📊 Impact Assessment:")
        print(f"  Success Rate: {dashboard_data['overview']['success_rate']:.1%}")
        print(f"  Active Workflows: {dashboard_data['overview']['active_workflows']}")
        
        recent_errors = len([
            a for a in dashboard_data.get('alerts', [])
            if self.is_recent(a['timestamp'], minutes=30)
        ])
        
        if recent_errors > 5:
            print("⚠️ Potential cascade failure detected")
```

### Automation

**Daily Health Check:**
```python
import schedule

def daily_health_check():
    """Automated daily system health check."""
    analyzer = PerformanceAnalyzer()
    metrics = analyzer.collect_metrics(hours_back=24)
    
    # Calculate health score
    health_score = calculate_health_score(metrics)
    
    if health_score < 80:
        send_alert(f"System health: {health_score}/100")
    
    # Generate report
    report = generate_health_report(metrics)
    save_report(report)

# Schedule daily at 9 AM
schedule.every().day.at("09:00").do(daily_health_check)
```

This workflow documentation provides practical guidance for debugging, performance analysis, dashboard usage, and team collaboration with LangSmith integration. 