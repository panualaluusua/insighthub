#!/usr/bin/env python3
"""
Local monitoring dashboard for the InsightHub orchestrator.
Provides performance tracking, error monitoring, and dashboard functionality
that works independently of LangSmith API permissions.
"""

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from collections import defaultdict, deque
import statistics
import uuid
import logging

from .metrics import NodeMetrics, WorkflowMetrics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalMonitoringDashboard:
    """
    Local monitoring dashboard for the orchestrator.
    Collects and analyzes performance metrics without requiring external services.
    """
    
    def __init__(self, data_dir: str = ".monitoring"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # In-memory storage for recent metrics (last 1000 workflows)
        self.recent_workflows: deque = deque(maxlen=1000)
        self.active_workflows: Dict[str, WorkflowMetrics] = {}
        self.active_nodes: Dict[str, NodeMetrics] = {}
        
        # Performance aggregations
        self.node_stats: Dict[str, Dict] = defaultdict(lambda: {
            "total_executions": 0,
            "total_duration": 0,
            "error_count": 0,
            "success_count": 0,
            "avg_duration": 0,
            "success_rate": 0
        })
        
        # Load existing data
        self._load_data()
        
        # Auto-save thread
        self._start_auto_save()
    
    def _load_data(self):
        """Load existing monitoring data from disk."""
        try:
            workflows_file = self.data_dir / "workflows.json"
            if workflows_file.exists():
                with open(workflows_file, 'r') as f:
                    data = json.load(f)
                    for workflow_data in data[-1000:]:  # Load last 1000
                        try:
                            workflow = WorkflowMetrics.from_dict(workflow_data)
                            self.recent_workflows.append(workflow)
                            self._update_node_stats(workflow)
                        except Exception as e:
                            logger.warning(f"Failed to load workflow data: {e}")
            
            logger.info(f"Loaded {len(self.recent_workflows)} workflow records")
            
        except Exception as e:
            logger.error(f"Failed to load monitoring data: {e}")
    
    def _save_data(self):
        """Save monitoring data to disk."""
        try:
            workflows_file = self.data_dir / "workflows.json"
            
            # Convert workflows to serializable format
            serializable_workflows = [workflow.to_dict() for workflow in self.recent_workflows]
            
            with open(workflows_file, 'w') as f:
                json.dump(serializable_workflows, f, indent=2)
            
            # Save aggregated stats
            stats_file = self.data_dir / "node_stats.json"
            with open(stats_file, 'w') as f:
                json.dump(dict(self.node_stats), f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save monitoring data: {e}")
    
    def _start_auto_save(self):
        """Start background thread for auto-saving data."""
        def save_periodically():
            while True:
                time.sleep(60)  # Save every minute
                self._save_data()
        
        save_thread = threading.Thread(target=save_periodically, daemon=True)
        save_thread.start()
    
    def start_workflow(self, content_type: str = "unknown") -> str:
        """Start monitoring a new workflow."""
        workflow_id = str(uuid.uuid4())
        workflow = WorkflowMetrics(
            workflow_id=workflow_id,
            start_time=datetime.now(),
            content_type=content_type
        )
        self.active_workflows[workflow_id] = workflow
        logger.info(f"Started monitoring workflow {workflow_id} ({content_type})")
        return workflow_id
    
    def start_node(self, workflow_id: str, node_name: str, input_size: Optional[int] = None) -> str:
        """Start monitoring a node execution."""
        execution_id = str(uuid.uuid4())
        node_metrics = NodeMetrics(
            node_name=node_name,
            execution_id=execution_id,
            start_time=datetime.now(),
            input_size=input_size
        )
        self.active_nodes[execution_id] = node_metrics
        
        # Add to workflow if it exists
        if workflow_id in self.active_workflows:
            self.active_workflows[workflow_id].add_node(node_metrics)
        
        logger.debug(f"Started monitoring node {node_name} (execution: {execution_id})")
        return execution_id
    
    def complete_node(self, execution_id: str, status: str = "success", 
                     output_size: Optional[int] = None, error_message: Optional[str] = None,
                     metadata: Dict[str, Any] = None):
        """Complete monitoring of a node execution."""
        if execution_id in self.active_nodes:
            node = self.active_nodes[execution_id]
            node.complete(status=status, error_message=error_message, metadata=metadata)
            if output_size:
                node.output_size = output_size
            
            logger.debug(f"Completed monitoring node {node.node_name} ({execution_id}): {status} in {node.duration:.2f}s")
            del self.active_nodes[execution_id]
    
    def complete_workflow(self, workflow_id: str, status: str = "success", 
                         error_message: Optional[str] = None, 
                         total_tokens: int = 0, total_cost: float = 0.0):
        """Complete monitoring of a workflow."""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow.complete(status=status, error_message=error_message)
            workflow.total_tokens = total_tokens
            workflow.total_cost = total_cost
            
            # Move to recent workflows
            self.recent_workflows.append(workflow)
            self._update_node_stats(workflow)
            
            logger.info(f"Completed monitoring workflow {workflow_id}: {status} in {workflow.duration:.2f}s")
            del self.active_workflows[workflow_id]
    
    def _update_node_stats(self, workflow: WorkflowMetrics):
        """Update aggregated node statistics."""
        for node in workflow.nodes:
            stats = self.node_stats[node.node_name]
            stats["total_executions"] += 1
            
            if node.duration:
                stats["total_duration"] += node.duration
                stats["avg_duration"] = stats["total_duration"] / stats["total_executions"]
            
            if node.status == "success":
                stats["success_count"] += 1
            else:
                stats["error_count"] += 1
            
            stats["success_rate"] = stats["success_count"] / stats["total_executions"] if stats["total_executions"] > 0 else 0
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        now = datetime.now()
        
        # Recent performance (last 24 hours)
        recent_workflows = [w for w in self.recent_workflows 
                          if w.start_time > now - timedelta(hours=24)]
        
        # Overall stats
        total_workflows = len(self.recent_workflows)
        successful_workflows = len([w for w in self.recent_workflows if w.status == "success"])
        
        dashboard_data = {
            "timestamp": now.isoformat(),
            "overview": {
                "total_workflows": total_workflows,
                "successful_workflows": successful_workflows,
                "success_rate": successful_workflows / total_workflows if total_workflows > 0 else 0,
                "active_workflows": len(self.active_workflows),
                "active_nodes": len(self.active_nodes)
            },
            "recent_performance": {
                "workflows_24h": len(recent_workflows),
                "avg_duration_24h": statistics.mean([w.duration for w in recent_workflows if w.duration]) if recent_workflows else 0,
                "error_rate_24h": len([w for w in recent_workflows if w.status != "success"]) / len(recent_workflows) if recent_workflows else 0
            },
            "node_performance": dict(self.node_stats),
            "recent_workflows": [
                {
                    "id": w.workflow_id[:8],
                    "content_type": w.content_type,
                    "duration": w.duration,
                    "status": w.status,
                    "start_time": w.start_time.isoformat(),
                    "total_tokens": w.total_tokens,
                    "total_cost": w.total_cost
                }
                for w in list(self.recent_workflows)[-10:]  # Last 10 workflows
            ],
            "content_type_stats": self._get_content_type_stats()
        }
        
        return dashboard_data
    
    def _get_content_type_stats(self) -> Dict[str, Dict]:
        """Get statistics by content type."""
        stats = defaultdict(lambda: {"count": 0, "avg_duration": 0, "success_rate": 0})
        
        for workflow in self.recent_workflows:
            content_stats = stats[workflow.content_type]
            content_stats["count"] += 1
            
            if workflow.duration:
                current_total = content_stats["avg_duration"] * (content_stats["count"] - 1)
                content_stats["avg_duration"] = (current_total + workflow.duration) / content_stats["count"]
            
            if workflow.status == "success":
                content_stats["success_rate"] = (content_stats["success_rate"] * (content_stats["count"] - 1) + 1) / content_stats["count"]
            else:
                content_stats["success_rate"] = content_stats["success_rate"] * (content_stats["count"] - 1) / content_stats["count"]
        
        return dict(stats)
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get current alerts based on performance thresholds."""
        alerts = []
        
        # Check error rates
        for node_name, stats in self.node_stats.items():
            if stats["total_executions"] >= 10 and stats["success_rate"] < 0.9:
                alerts.append({
                    "level": "warning",
                    "type": "high_error_rate",
                    "message": f"High error rate in {node_name}: {(1-stats['success_rate'])*100:.1f}%",
                    "node": node_name,
                    "value": 1 - stats["success_rate"]
                })
        
        # Check slow nodes
        for node_name, stats in self.node_stats.items():
            if stats["avg_duration"] > 30:  # More than 30 seconds
                alerts.append({
                    "level": "info", 
                    "type": "slow_performance",
                    "message": f"Slow performance in {node_name}: {stats['avg_duration']:.1f}s average",
                    "node": node_name,
                    "value": stats["avg_duration"]
                })
        
        # Check recent failures
        recent_failures = [w for w in list(self.recent_workflows)[-20:] if w.status != "success"]
        if len(recent_failures) >= 3:
            alerts.append({
                "level": "error",
                "type": "recent_failures", 
                "message": f"{len(recent_failures)} failures in last 20 workflows",
                "value": len(recent_failures)
            })
        
        return alerts

# Global monitoring instance
_monitor = None

def get_monitor() -> LocalMonitoringDashboard:
    """Get the global monitoring instance."""
    global _monitor
    if _monitor is None:
        _monitor = LocalMonitoringDashboard()
    return _monitor

def monitor_node(node_name: str):
    """Decorator to monitor node execution."""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            monitor = get_monitor()
            workflow_id = kwargs.get('workflow_id', 'unknown')
            
            # Start monitoring
            execution_id = monitor.start_node(workflow_id, node_name)
            
            try:
                # Execute function
                start_time = time.time()
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Complete monitoring
                metadata = {"duration": duration}
                if hasattr(result, '__len__'):
                    metadata["output_size"] = len(str(result))
                
                monitor.complete_node(execution_id, status="success", metadata=metadata)
                return result
                
            except Exception as e:
                # Record error
                monitor.complete_node(execution_id, status="error", error_message=str(e))
                raise
        
        return wrapper
    return decorator

def monitor_workflow(content_type: str = "unknown"):
    """Decorator to monitor entire workflow execution."""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            monitor = get_monitor()
            
            # Start workflow monitoring
            workflow_id = monitor.start_workflow(content_type)
            kwargs['workflow_id'] = workflow_id  # Pass to node functions
            
            try:
                # Execute workflow
                result = func(*args, **kwargs)
                
                # Complete monitoring
                monitor.complete_workflow(workflow_id, status="success")
                return result
                
            except Exception as e:
                # Record error
                monitor.complete_workflow(workflow_id, status="error", error_message=str(e))
                raise
        
        return wrapper
    return decorator 