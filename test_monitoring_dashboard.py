#!/usr/bin/env python3
"""
Test script to demonstrate the local monitoring dashboard functionality.
This script simulates orchestrator workflows and shows real-time monitoring.
"""

import os
import sys
import time
import threading
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from orchestrator.monitoring import (
    get_monitor, 
    monitor_node, 
    monitor_workflow,
    LocalMonitoringDashboard
)
from orchestrator.monitoring.web_dashboard import run_dashboard

def simulate_content_fetcher(workflow_id: str, content_type: str):
    """Simulate ContentFetcher node execution."""
    print(f"  📥 ContentFetcher processing {content_type}...")
    
    # Simulate different processing times
    processing_time = 2.0 if content_type == "youtube" else 1.5
    time.sleep(processing_time)
    
    # Simulate some failures (10% chance)
    import random
    if random.random() < 0.1:
        raise Exception(f"Failed to fetch {content_type} content")
    
    return {"content": f"Sample {content_type} content", "metadata": {"source": content_type}}

def simulate_summarizer(workflow_id: str, content: dict):
    """Simulate SummarizerNode execution.""" 
    print(f"  🤖 Summarizer processing content...")
    
    # Simulate DeepSeek API call time
    time.sleep(3.0)
    
    # Simulate occasional failures (5% chance)
    import random
    if random.random() < 0.05:
        raise Exception("DeepSeek API rate limit exceeded")
    
    return {"summary": "AI-generated summary", "tokens_used": 1200}

def simulate_embedding(workflow_id: str, content: dict):
    """Simulate EmbeddingNode execution."""
    print(f"  🔢 Embedding generating vectors...")
    
    # Simulate OpenAI embedding API call
    time.sleep(1.5)
    
    return {"embedding": [0.1, 0.2, 0.3] * 512, "tokens_used": 300}  # 1536 dimensions

def simulate_storage(workflow_id: str, data: dict):
    """Simulate StorageNode execution."""
    print(f"  💾 Storage saving to database...")
    
    # Simulate database operation
    time.sleep(0.8)
    
    # Simulate occasional DB connection issues (3% chance)
    import random
    if random.random() < 0.03:
        raise Exception("Database connection timeout")
    
    return {"stored_id": f"content_{int(time.time())}", "status": "saved"}

# Apply monitoring decorators
simulate_content_fetcher = monitor_node("content_fetcher")(simulate_content_fetcher)
simulate_summarizer = monitor_node("summarizer")(simulate_summarizer)
simulate_embedding = monitor_node("embedding")(simulate_embedding)
simulate_storage = monitor_node("storage")(simulate_storage)

@monitor_workflow("youtube")
def simulate_youtube_workflow(workflow_id: str = None):
    """Simulate a complete YouTube processing workflow."""
    print("🎥 Starting YouTube workflow...")
    
    try:
        # ContentFetcher
        content = simulate_content_fetcher(workflow_id, "youtube")
        
        # Parallel processing: Summarizer and Embedding
        summary = simulate_summarizer(workflow_id, content)
        embedding = simulate_embedding(workflow_id, content)
        
        # Storage
        result = simulate_storage(workflow_id, {
            "content": content,
            "summary": summary,
            "embedding": embedding
        })
        
        print("✅ YouTube workflow completed successfully!")
        return result
        
    except Exception as e:
        print(f"❌ YouTube workflow failed: {e}")
        raise

@monitor_workflow("reddit")
def simulate_reddit_workflow(workflow_id: str = None):
    """Simulate a complete Reddit processing workflow."""
    print("📝 Starting Reddit workflow...")
    
    try:
        # ContentFetcher  
        content = simulate_content_fetcher(workflow_id, "reddit")
        
        # Parallel processing: Summarizer and Embedding
        summary = simulate_summarizer(workflow_id, content)
        embedding = simulate_embedding(workflow_id, content)
        
        # Storage
        result = simulate_storage(workflow_id, {
            "content": content,
            "summary": summary,
            "embedding": embedding
        })
        
        print("✅ Reddit workflow completed successfully!")
        return result
        
    except Exception as e:
        print(f"❌ Reddit workflow failed: {e}")
        raise

def run_continuous_simulation():
    """Run continuous workflow simulation for testing."""
    print("🚀 Starting continuous workflow simulation...")
    
    import random
    workflow_count = 0
    
    while True:
        try:
            workflow_count += 1
            print(f"\n--- Workflow #{workflow_count} ---")
            
            # Randomly choose workflow type
            if random.random() < 0.6:  # 60% YouTube, 40% Reddit
                simulate_youtube_workflow()
            else:
                simulate_reddit_workflow()
            
            # Wait between workflows (1-5 seconds)
            wait_time = random.uniform(1, 5)
            time.sleep(wait_time)
            
        except Exception as e:
            print(f"Workflow #{workflow_count} failed: {e}")
            continue

def print_dashboard_summary():
    """Print a summary of monitoring data."""
    monitor = get_monitor()
    data = monitor.get_dashboard_data()
    
    print("\n" + "="*60)
    print("📊 MONITORING DASHBOARD SUMMARY")
    print("="*60)
    
    # Overview
    overview = data["overview"]
    print(f"Total Workflows: {overview['total_workflows']}")
    print(f"Success Rate: {overview['success_rate']*100:.1f}%")
    print(f"Active Workflows: {overview['active_workflows']}")
    print(f"Active Nodes: {overview['active_nodes']}")
    
    # 24h Performance
    recent = data["recent_performance"]
    print(f"\n24h Performance:")
    print(f"  Workflows: {recent['workflows_24h']}")
    print(f"  Avg Duration: {recent['avg_duration_24h']:.1f}s")
    print(f"  Error Rate: {recent['error_rate_24h']*100:.1f}%")
    
    # Node Performance
    print(f"\nNode Performance:")
    for node_name, stats in data["node_performance"].items():
        print(f"  {node_name}:")
        print(f"    Executions: {stats['total_executions']}")
        print(f"    Success Rate: {stats['success_rate']*100:.1f}%")
        print(f"    Avg Duration: {stats['avg_duration']:.1f}s")
    
    # Recent Workflows
    print(f"\nRecent Workflows:")
    for workflow in data["recent_workflows"]:
        status_icon = "✅" if workflow["status"] == "success" else "❌"
        print(f"  {status_icon} {workflow['id']} ({workflow['content_type']}) - {workflow['duration']:.1f}s")
    
    # Alerts
    alerts = monitor.get_alerts()
    if alerts:
        print(f"\n🚨 Alerts:")
        for alert in alerts:
            level_icon = "🔴" if alert["level"] == "error" else "🟡" if alert["level"] == "warning" else "🔵"
            print(f"  {level_icon} {alert['message']}")
    else:
        print(f"\n✅ No alerts")
    
    print("="*60)

def main():
    """Main test function."""
    print("🎯 InsightHub Monitoring Dashboard Test")
    print("="*50)
    
    # Initialize monitoring
    monitor = get_monitor()
    print("✅ Monitoring system initialized")
    
    # Run some test workflows
    print("\n1. Running sample workflows...")
    
    try:
        simulate_youtube_workflow()
        time.sleep(1)
        simulate_reddit_workflow()
        time.sleep(1)
        simulate_youtube_workflow()
    except Exception as e:
        print(f"Test workflow error: {e}")
    
    # Print initial summary
    print_dashboard_summary()
    
    # Ask user what to do next
    print("\n🎯 Choose what to do next:")
    print("1. Run web dashboard (http://localhost:8080)")
    print("2. Run continuous simulation (generates test data)")
    print("3. Print current dashboard data")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🌐 Starting web dashboard...")
        print("Visit http://localhost:8080 to view the dashboard")
        print("Press Ctrl+C to stop")
        try:
            run_dashboard(debug=True)
        except KeyboardInterrupt:
            print("\n👋 Dashboard stopped")
            
    elif choice == "2":
        print("\n🔄 Starting continuous simulation...")
        print("This will generate test workflows every 1-5 seconds")
        print("Press Ctrl+C to stop")
        try:
            run_continuous_simulation()
        except KeyboardInterrupt:
            print("\n👋 Simulation stopped")
            print_dashboard_summary()
            
    elif choice == "3":
        print_dashboard_summary()
        
    elif choice == "4":
        print("👋 Goodbye!")
        
    else:
        print("Invalid choice. Exiting...")

if __name__ == "__main__":
    main() 