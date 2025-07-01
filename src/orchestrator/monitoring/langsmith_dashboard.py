#!/usr/bin/env python3
"""
LangSmith monitoring dashboard integration for InsightHub orchestrator.
Provides LangSmith-aware monitoring that works with both local collection and API uploads.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import statistics
import logging
from collections import defaultdict

try:
    from langsmith import Client
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("LangSmith not available, running in local-only mode")

from .dashboard import LocalMonitoringDashboard, get_monitor
from .metrics import NodeMetrics, WorkflowMetrics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LangSmithDashboard:
    """
    Enhanced monitoring dashboard with LangSmith integration.
    Provides hybrid local/cloud monitoring capabilities.
    """
    
    def __init__(self, local_monitor: Optional[LocalMonitoringDashboard] = None):
        self.local_monitor = local_monitor or get_monitor()
        self.langsmith_client = None
        self.api_available = False
        
        # Try to initialize LangSmith client if available
        if LANGSMITH_AVAILABLE:
            self._init_langsmith_client()
        
        # Trace data for LangSmith integration
        self.pending_traces: List[Dict] = []
        self.trace_cache_file = Path(".monitoring/langsmith_traces.json")
        
        # Load cached traces
        self._load_trace_cache()
    
    def _init_langsmith_client(self):
        """Initialize LangSmith client and test API availability."""
        try:
            api_key = os.getenv("LANGSMITH_API_KEY")
            project = os.getenv("LANGSMITH_PROJECT", "InsightHub")
            
            if not api_key:
                logger.warning("LANGSMITH_API_KEY not found. Running in local-only mode.")
                return
            
            self.langsmith_client = Client()
            
            # Test API connectivity (simple call that doesn't require write permissions)
            try:
                # This is a read-only operation that should work even with limited permissions
                self.langsmith_client.list_runs(project_name=project, limit=1)
                self.api_available = True
                logger.info("LangSmith API connection established successfully")
            except Exception as e:
                if "403" in str(e):
                    logger.info("LangSmith API key authenticated but write permissions pending. Using local mode.")
                    self.api_available = False
                else:
                    logger.warning(f"LangSmith API connection failed: {e}. Using local mode.")
                    self.api_available = False
                    
        except Exception as e:
            logger.warning(f"Failed to initialize LangSmith client: {e}. Using local mode.")
            self.langsmith_client = None
            self.api_available = False
    
    def _load_trace_cache(self):
        """Load cached traces from disk."""
        try:
            if self.trace_cache_file.exists():
                with open(self.trace_cache_file, 'r') as f:
                    self.pending_traces = json.load(f)
                logger.info(f"Loaded {len(self.pending_traces)} cached traces")
        except Exception as e:
            logger.error(f"Failed to load trace cache: {e}")
            self.pending_traces = []
    
    def _save_trace_cache(self):
        """Save pending traces to disk."""
        try:
            self.trace_cache_file.parent.mkdir(exist_ok=True)
            with open(self.trace_cache_file, 'w') as f:
                json.dump(self.pending_traces, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save trace cache: {e}")
    
    def get_enhanced_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data with LangSmith enhancements."""
        
        # Get base dashboard data from local monitor
        base_data = self.local_monitor.get_dashboard_data()
        
        # Add LangSmith-specific data
        langsmith_data = {
            "langsmith_status": {
                "api_available": self.api_available,
                "pending_traces": len(self.pending_traces),
                "client_initialized": self.langsmith_client is not None,
                "project": os.getenv("LANGSMITH_PROJECT", "InsightHub"),
                "langsmith_available": LANGSMITH_AVAILABLE
            },
            "trace_analysis": self._analyze_traces(),
            "performance_insights": self._get_performance_insights(),
            "bottleneck_detection": self._detect_bottlenecks(),
            "recommendation_engine": self._generate_recommendations()
        }
        
        # Merge data
        enhanced_data = {**base_data, **langsmith_data}
        
        return enhanced_data
    
    def _analyze_traces(self) -> Dict[str, Any]:
        """Analyze trace data for insights."""
        workflows = list(self.local_monitor.recent_workflows)
        
        if not workflows:
            return {"total_traces": 0, "analysis": "No traces available"}
        
        # Analyze trace patterns
        analysis = {
            "total_traces": len(workflows),
            "trace_patterns": self._analyze_trace_patterns(workflows),
            "error_patterns": self._analyze_error_patterns(workflows),
            "performance_patterns": self._analyze_performance_patterns(workflows)
        }
        
        return analysis
    
    def _analyze_trace_patterns(self, workflows: List[WorkflowMetrics]) -> Dict[str, Any]:
        """Analyze patterns in trace execution."""
        patterns = {
            "most_common_path": self._find_most_common_execution_path(workflows),
            "node_sequence_analysis": self._analyze_node_sequences(workflows),
            "content_type_breakdown": self._analyze_content_type_patterns(workflows)
        }
        return patterns
    
    def _analyze_error_patterns(self, workflows: List[WorkflowMetrics]) -> Dict[str, Any]:
        """Analyze error patterns in traces."""
        failed_workflows = [w for w in workflows if w.status != "success"]
        
        if not failed_workflows:
            return {"error_count": 0, "patterns": []}
        
        error_analysis = {
            "error_count": len(failed_workflows),
            "error_rate": len(failed_workflows) / len(workflows),
            "common_errors": self._group_common_errors(failed_workflows),
            "failure_points": self._analyze_failure_points(failed_workflows),
            "recovery_suggestions": self._suggest_error_recovery(failed_workflows)
        }
        
        return error_analysis
    
    def _analyze_performance_patterns(self, workflows: List[WorkflowMetrics]) -> Dict[str, Any]:
        """Analyze performance patterns."""
        successful_workflows = [w for w in workflows if w.status == "success" and w.duration]
        
        if not successful_workflows:
            return {"analysis": "No successful workflows to analyze"}
        
        durations = [w.duration for w in successful_workflows]
        
        performance_analysis = {
            "avg_duration": statistics.mean(durations),
            "median_duration": statistics.median(durations),
            "std_deviation": statistics.stdev(durations) if len(durations) > 1 else 0,
            "percentiles": {
                "p95": self._percentile(durations, 95),
                "p99": self._percentile(durations, 99)
            },
            "node_performance": self._analyze_node_performance(successful_workflows)
        }
        
        return performance_analysis
    
    def _get_performance_insights(self) -> Dict[str, Any]:
        """Generate performance insights."""
        workflows = list(self.local_monitor.recent_workflows)
        
        insights = {
            "slow_workflows": self._identify_slow_workflows(workflows),
            "fast_workflows": self._identify_fast_workflows(workflows),
            "optimization_opportunities": self._identify_optimization_opportunities(workflows),
            "resource_utilization": self._analyze_resource_utilization(workflows)
        }
        
        return insights
    
    def _detect_bottlenecks(self) -> List[Dict[str, Any]]:
        """Detect performance bottlenecks."""
        bottlenecks = []
        
        # Analyze node performance for bottlenecks
        node_stats = self.local_monitor.node_stats
        
        for node_name, stats in node_stats.items():
            if stats["total_executions"] < 3:  # Skip nodes with insufficient data
                continue
            
            # Detect slow nodes
            if stats["avg_duration"] > 30:  # More than 30 seconds average
                bottlenecks.append({
                    "type": "slow_node",
                    "node": node_name,
                    "avg_duration": stats["avg_duration"],
                    "severity": "high" if stats["avg_duration"] > 60 else "medium",
                    "suggestion": f"Consider optimizing {node_name} - average execution time is {stats['avg_duration']:.1f}s"
                })
            
            # Detect error-prone nodes
            if stats["success_rate"] < 0.9 and stats["total_executions"] > 5:
                bottlenecks.append({
                    "type": "error_prone_node",
                    "node": node_name,
                    "success_rate": stats["success_rate"],
                    "severity": "high" if stats["success_rate"] < 0.7 else "medium",
                    "suggestion": f"Investigate reliability issues in {node_name} - success rate is {stats['success_rate']*100:.1f}%"
                })
        
        return bottlenecks
    
    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # API status recommendations
        if not self.api_available and self.langsmith_client:
            recommendations.append({
                "category": "infrastructure",
                "priority": "medium",
                "title": "LangSmith API Permissions Pending",
                "description": "API key authenticated but write permissions are still activating. Traces are being cached locally.",
                "action": "Wait 24-72 hours for full API permissions, or contact LangSmith support if issues persist."
            })
        
        # Performance recommendations
        workflows = list(self.local_monitor.recent_workflows)
        if workflows:
            successful_workflows = [w for w in workflows if w.status == "success" and w.duration]
            if successful_workflows:
                avg_duration = statistics.mean([w.duration for w in successful_workflows])
                if avg_duration > 45:
                    recommendations.append({
                        "category": "performance",
                        "priority": "high",
                        "title": "High Average Workflow Duration",
                        "description": f"Average workflow duration is {avg_duration:.1f}s",
                        "action": "Consider implementing parallel processing or optimizing slow nodes."
                    })
        
        # Error rate recommendations
        if len(workflows) >= 20:
            recent_errors = len([w for w in workflows[-20:] if w.status != "success"])
            if recent_errors > 5:
                recommendations.append({
                    "category": "reliability",
                    "priority": "high",
                    "title": "High Recent Error Rate",
                    "description": f"{recent_errors} errors in last 20 workflows",
                    "action": "Review error logs and implement better error handling or retry logic."
                })
        
        return recommendations
    
    def test_dashboard_functionality(self) -> Dict[str, Any]:
        """Test all dashboard components and return status."""
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "local_monitor": {
                "available": self.local_monitor is not None,
                "data_accessible": False,
                "recent_workflows_count": 0
            },
            "langsmith_integration": {
                "client_initialized": self.langsmith_client is not None,
                "api_available": self.api_available,
                "cached_traces": len(self.pending_traces),
                "langsmith_library_available": LANGSMITH_AVAILABLE
            },
            "dashboard_data": {
                "generation_successful": False,
                "data_size": 0
            }
        }
        
        # Test local monitor
        try:
            dashboard_data = self.local_monitor.get_dashboard_data()
            test_results["local_monitor"]["data_accessible"] = True
            test_results["local_monitor"]["recent_workflows_count"] = len(self.local_monitor.recent_workflows)
        except Exception as e:
            test_results["local_monitor"]["error"] = str(e)
        
        # Test enhanced dashboard data generation
        try:
            enhanced_data = self.get_enhanced_dashboard_data()
            test_results["dashboard_data"]["generation_successful"] = True
            test_results["dashboard_data"]["data_size"] = len(json.dumps(enhanced_data))
        except Exception as e:
            test_results["dashboard_data"]["error"] = str(e)
        
        return test_results
    
    # Helper methods
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index == int(index):
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _find_most_common_execution_path(self, workflows: List[WorkflowMetrics]) -> str:
        """Find the most common execution path through nodes."""
        paths = defaultdict(int)
        for workflow in workflows:
            path = " -> ".join([node.node_name for node in workflow.nodes])
            paths[path] += 1
        return max(paths.items(), key=lambda x: x[1])[0] if paths else "No paths found"
    
    def _analyze_node_sequences(self, workflows: List[WorkflowMetrics]) -> Dict[str, int]:
        """Analyze common node sequences."""
        sequences = defaultdict(int)
        for workflow in workflows:
            for i in range(len(workflow.nodes) - 1):
                sequence = f"{workflow.nodes[i].node_name} -> {workflow.nodes[i+1].node_name}"
                sequences[sequence] += 1
        return dict(sequences)
    
    def _analyze_content_type_patterns(self, workflows: List[WorkflowMetrics]) -> Dict[str, int]:
        """Analyze patterns by content type."""
        patterns = defaultdict(int)
        for workflow in workflows:
            patterns[workflow.content_type] += 1
        return dict(patterns)
    
    def _group_common_errors(self, failed_workflows: List[WorkflowMetrics]) -> Dict[str, int]:
        """Group common error messages."""
        errors = defaultdict(int)
        for workflow in failed_workflows:
            error_msg = workflow.error_message or "Unknown error"
            # Simplify error message for grouping
            simplified_error = error_msg.split(':')[0] if ':' in error_msg else error_msg
            errors[simplified_error] += 1
        return dict(errors)
    
    def _analyze_failure_points(self, failed_workflows: List[WorkflowMetrics]) -> Dict[str, int]:
        """Analyze which nodes fail most often."""
        failure_points = defaultdict(int)
        for workflow in failed_workflows:
            for node in workflow.nodes:
                if node.status != "success":
                    failure_points[node.node_name] += 1
        return dict(failure_points)
    
    def _suggest_error_recovery(self, failed_workflows: List[WorkflowMetrics]) -> List[str]:
        """Suggest error recovery strategies."""
        suggestions = []
        
        failure_points = self._analyze_failure_points(failed_workflows)
        if failure_points:
            most_failing_node = max(failure_points.items(), key=lambda x: x[1])[0]
            suggestions.append(f"Consider adding retry logic to {most_failing_node}")
            suggestions.append(f"Implement better error handling in {most_failing_node}")
        
        return suggestions
    
    def _identify_slow_workflows(self, workflows: List[WorkflowMetrics]) -> List[Dict[str, Any]]:
        """Identify unusually slow workflows."""
        successful_workflows = [w for w in workflows if w.status == "success" and w.duration]
        if len(successful_workflows) < 3:
            return []
        
        durations = [w.duration for w in successful_workflows]
        avg_duration = statistics.mean(durations)
        std_duration = statistics.stdev(durations) if len(durations) > 1 else 0
        threshold = avg_duration + 2 * std_duration
        
        slow_workflows = [
            {
                "workflow_id": w.workflow_id,
                "duration": w.duration,
                "content_type": w.content_type,
                "threshold_exceeded": w.duration - threshold
            }
            for w in successful_workflows 
            if w.duration > threshold
        ]
        
        return slow_workflows
    
    def _identify_fast_workflows(self, workflows: List[WorkflowMetrics]) -> List[Dict[str, Any]]:
        """Identify unusually fast workflows."""
        successful_workflows = [w for w in workflows if w.status == "success" and w.duration]
        if len(successful_workflows) < 3:
            return []
        
        durations = [w.duration for w in successful_workflows]
        avg_duration = statistics.mean(durations)
        std_duration = statistics.stdev(durations) if len(durations) > 1 else 0
        threshold = avg_duration - std_duration
        
        fast_workflows = [
            {
                "workflow_id": w.workflow_id,
                "duration": w.duration,
                "content_type": w.content_type,
                "time_saved": threshold - w.duration
            }
            for w in successful_workflows 
            if w.duration < threshold and threshold > 0
        ]
        
        return fast_workflows
    
    def _identify_optimization_opportunities(self, workflows: List[WorkflowMetrics]) -> List[Dict[str, str]]:
        """Identify optimization opportunities."""
        opportunities = []
        
        # Node-level optimization opportunities
        node_stats = self.local_monitor.node_stats
        for node_name, stats in node_stats.items():
            if stats["avg_duration"] > 20 and stats["total_executions"] > 3:
                opportunities.append({
                    "type": "node_optimization",
                    "target": node_name,
                    "description": f"{node_name} averages {stats['avg_duration']:.1f}s - consider caching or parallel processing"
                })
        
        return opportunities
    
    def _analyze_resource_utilization(self, workflows: List[WorkflowMetrics]) -> Dict[str, Any]:
        """Analyze resource utilization patterns."""
        if not workflows:
            return {"analysis": "No workflows to analyze"}
        
        total_tokens = sum(w.total_tokens for w in workflows if w.total_tokens)
        total_cost = sum(w.total_cost for w in workflows if w.total_cost)
        total_duration = sum(w.duration for w in workflows if w.duration)
        
        return {
            "total_tokens_used": total_tokens,
            "total_cost": total_cost,
            "total_processing_time": total_duration,
            "avg_tokens_per_workflow": total_tokens / len(workflows) if workflows else 0,
            "avg_cost_per_workflow": total_cost / len(workflows) if workflows else 0,
            "cost_per_token": total_cost / total_tokens if total_tokens > 0 else 0
        }
    
    def _analyze_node_performance(self, workflows: List[WorkflowMetrics]) -> Dict[str, Dict[str, float]]:
        """Analyze performance by node type."""
        node_performance = defaultdict(lambda: {"durations": [], "count": 0})
        
        for workflow in workflows:
            for node in workflow.nodes:
                if node.duration:
                    node_performance[node.node_name]["durations"].append(node.duration)
                    node_performance[node.node_name]["count"] += 1
        
        # Calculate statistics for each node
        performance_stats = {}
        for node_name, data in node_performance.items():
            durations = data["durations"]
            if durations:
                performance_stats[node_name] = {
                    "avg_duration": statistics.mean(durations),
                    "median_duration": statistics.median(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "execution_count": data["count"]
                }
        
        return performance_stats


def get_langsmith_dashboard() -> LangSmithDashboard:
    """Get or create the global LangSmith dashboard instance."""
    if not hasattr(get_langsmith_dashboard, '_instance'):
        get_langsmith_dashboard._instance = LangSmithDashboard()
    return get_langsmith_dashboard._instance


def main():
    """Test the LangSmith dashboard functionality."""
    dashboard = get_langsmith_dashboard()
    
    print("🎯 LangSmith Dashboard Test")
    print("=" * 50)
    
    # Test functionality
    test_results = dashboard.test_dashboard_functionality()
    print(json.dumps(test_results, indent=2))
    
    print("\n📊 Enhanced Dashboard Data")
    print("=" * 50)
    
    # Get enhanced data
    enhanced_data = dashboard.get_enhanced_dashboard_data()
    
    # Print key metrics
    print(f"Total workflows: {enhanced_data['overview']['total_workflows']}")
    print(f"Success rate: {enhanced_data['overview']['success_rate']:.1%}")
    print(f"LangSmith API available: {enhanced_data['langsmith_status']['api_available']}")
    print(f"Pending traces: {enhanced_data['langsmith_status']['pending_traces']}")
    
    # Print recommendations
    recommendations = enhanced_data['recommendation_engine']
    if recommendations:
        print(f"\n💡 Recommendations ({len(recommendations)}):")
        for rec in recommendations:
            print(f"- [{rec['priority'].upper()}] {rec['title']}: {rec['description']}")
    else:
        print("\n✅ No recommendations - system performing well!")


if __name__ == "__main__":
    main() 