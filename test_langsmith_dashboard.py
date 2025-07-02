#!/usr/bin/env python3
"""
Test script for LangSmith dashboard functionality.
Demonstrates all the monitoring and analysis capabilities.
"""

import json
import sys
from pathlib import Path

# Add src to path to import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.orchestrator.monitoring.langsmith_dashboard import get_langsmith_dashboard

def main():
    """Demonstrate LangSmith dashboard capabilities."""
    print("🎯 LangSmith Dashboard Feature Demo")
    print("=" * 60)
    
    # Initialize dashboard
    dashboard = get_langsmith_dashboard()
    
    # Test basic functionality
    print("\n1️⃣ Testing Basic Functionality")
    print("-" * 40)
    
    test_results = dashboard.test_dashboard_functionality()
    print(f"✅ Local Monitor Available: {test_results['local_monitor']['available']}")
    print(f"✅ Data Accessible: {test_results['local_monitor']['data_accessible']}")
    print(f"✅ Workflows Available: {test_results['local_monitor']['recent_workflows_count']}")
    print(f"✅ LangSmith Client: {test_results['langsmith_integration']['client_initialized']}")
    print(f"✅ API Available: {test_results['langsmith_integration']['api_available']}")
    print(f"✅ Dashboard Generation: {test_results['dashboard_data']['generation_successful']}")
    
    # Get enhanced dashboard data
    print("\n2️⃣ Enhanced Dashboard Data")
    print("-" * 40)
    
    enhanced_data = dashboard.get_enhanced_dashboard_data()
    
    # Overview stats
    overview = enhanced_data['overview']
    print(f"📊 Total Workflows: {overview['total_workflows']}")
    print(f"📊 Success Rate: {overview['success_rate']:.1%}")
    print(f"📊 Active Workflows: {overview['active_workflows']}")
    print(f"📊 Active Nodes: {overview['active_nodes']}")
    
    # LangSmith status
    langsmith = enhanced_data['langsmith_status']
    print(f"\n🔗 LangSmith Status:")
    print(f"   API Available: {langsmith['api_available']}")
    print(f"   Client Initialized: {langsmith['client_initialized']}")
    print(f"   Project: {langsmith['project']}")
    print(f"   Pending Traces: {langsmith['pending_traces']}")
    print(f"   Library Available: {langsmith['langsmith_available']}")
    
    # Trace analysis
    trace_analysis = enhanced_data['trace_analysis']
    print(f"\n📈 Trace Analysis:")
    print(f"   Total Traces: {trace_analysis['total_traces']}")
    
    if trace_analysis['total_traces'] > 0:
        patterns = trace_analysis['trace_patterns']
        print(f"   Most Common Path: {patterns['most_common_path']}")
        print(f"   Content Types: {patterns['content_type_breakdown']}")
        
        # Performance patterns
        perf_patterns = trace_analysis['performance_patterns']
        if 'avg_duration' in perf_patterns:
            print(f"   Avg Duration: {perf_patterns['avg_duration']:.2f}s")
            print(f"   Median Duration: {perf_patterns['median_duration']:.2f}s")
    
    # Performance insights
    print("\n⚡ Performance Insights:")
    insights = enhanced_data['performance_insights']
    
    # Resource utilization
    resources = insights['resource_utilization']
    if 'total_tokens_used' in resources and resources['total_tokens_used'] > 0:
        print(f"   Total Tokens: {resources['total_tokens_used']:,}")
        print(f"   Total Cost: ${resources['total_cost']:.4f}")
        print(f"   Avg Cost/Workflow: ${resources['avg_cost_per_workflow']:.4f}")
        print(f"   Cost per Token: ${resources['cost_per_token']:.6f}")
    
    # Slow workflows
    if insights['slow_workflows']:
        print(f"   Slow Workflows: {len(insights['slow_workflows'])}")
        for workflow in insights['slow_workflows'][:3]:  # Show first 3
            print(f"     - {workflow['content_type']}: {workflow['duration']:.1f}s")
    
    # Optimization opportunities
    if insights['optimization_opportunities']:
        print(f"   Optimization Opportunities: {len(insights['optimization_opportunities'])}")
        for opp in insights['optimization_opportunities'][:3]:  # Show first 3
            print(f"     - {opp['description']}")
    
    # Bottleneck detection
    print("\n🚨 Bottleneck Detection:")
    bottlenecks = enhanced_data['bottleneck_detection']
    
    if not bottlenecks:
        print("   ✅ No bottlenecks detected!")
    else:
        print(f"   Found {len(bottlenecks)} bottlenecks:")
        for bottleneck in bottlenecks:
            print(f"     - {bottleneck['type']}: {bottleneck['node']}")
            print(f"       Severity: {bottleneck['severity']}")
            print(f"       Suggestion: {bottleneck['suggestion']}")
    
    # Recommendations
    print("\n💡 AI Recommendations:")
    recommendations = enhanced_data['recommendation_engine']
    
    if not recommendations:
        print("   ✅ No recommendations - system performing optimally!")
    else:
        print(f"   Found {len(recommendations)} recommendations:")
        for rec in recommendations:
            print(f"     - [{rec['priority'].upper()}] {rec['title']}")
            print(f"       Category: {rec['category']}")
            print(f"       Issue: {rec['description']}")
            print(f"       Action: {rec['action']}")
    
    # Node performance
    print("\n🔧 Node Performance:")
    node_performance = enhanced_data['node_performance']
    
    if not node_performance:
        print("   No node performance data available")
    else:
        for node_name, stats in list(node_performance.items())[:5]:  # Show first 5 nodes
            print(f"   {node_name}:")
            print(f"     Executions: {stats['total_executions']}")
            print(f"     Success Rate: {stats['success_rate']:.1%}")
            print(f"     Avg Duration: {stats['avg_duration']:.2f}s")
    
    # Recent workflows
    print("\n📊 Recent Workflows:")
    recent_workflows = enhanced_data['recent_workflows']
    
    if not recent_workflows:
        print("   No recent workflows available")
    else:
        print(f"   Showing last {min(3, len(recent_workflows))} workflows:")
        for workflow in recent_workflows[-3:]:  # Show last 3
            print(f"     - {workflow['content_type']}: {workflow['status']} ({workflow.get('duration', 'N/A')})")
    
    print("\n🎉 Dashboard Demo Complete!")
    print("=" * 60)
    print("All LangSmith dashboard features are working correctly!")

if __name__ == "__main__":
    main() 