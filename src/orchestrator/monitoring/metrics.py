#!/usr/bin/env python3
"""
Metrics data structures for monitoring orchestrator performance.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Any, Optional

@dataclass
class NodeMetrics:
    """Metrics for a single node execution."""
    node_name: str
    execution_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    status: str = "running"  # running, success, error
    input_size: Optional[int] = None
    output_size: Optional[int] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def complete(self, status: str = "success", error_message: Optional[str] = None, metadata: Dict[str, Any] = None):
        """Mark the node execution as complete."""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.status = status
        if error_message:
            self.error_message = error_message
        if metadata:
            self.metadata.update(metadata)

@dataclass 
class WorkflowMetrics:
    """Metrics for a complete workflow execution."""
    workflow_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    status: str = "running"
    content_type: str = "unknown"  # youtube, reddit
    nodes: List[NodeMetrics] = None
    total_tokens: int = 0
    total_cost: float = 0.0
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.nodes is None:
            self.nodes = []
    
    def add_node(self, node_metrics: NodeMetrics):
        """Add node metrics to the workflow."""
        self.nodes.append(node_metrics)
    
    def complete(self, status: str = "success", error_message: Optional[str] = None):
        """Mark the workflow as complete."""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.status = status
        if error_message:
            self.error_message = error_message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with ISO formatted dates."""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        
        # Convert node datetime objects
        for node_dict in data['nodes']:
            if isinstance(node_dict['start_time'], datetime):
                node_dict['start_time'] = node_dict['start_time'].isoformat()
            if node_dict.get('end_time') and isinstance(node_dict['end_time'], datetime):
                node_dict['end_time'] = node_dict['end_time'].isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowMetrics':
        """Create from dictionary with ISO formatted dates."""
        # Convert ISO strings back to datetime objects
        workflow = cls(**data)
        workflow.start_time = datetime.fromisoformat(data['start_time'])
        if data.get('end_time'):
            workflow.end_time = datetime.fromisoformat(data['end_time'])
        
        # Convert node datetime objects
        workflow.nodes = []
        for node_data in data.get('nodes', []):
            node = NodeMetrics(**node_data)
            node.start_time = datetime.fromisoformat(node_data['start_time'])
            if node_data.get('end_time'):
                node.end_time = datetime.fromisoformat(node_data['end_time'])
            workflow.nodes.append(node)
        
        return workflow 

# ---------------------------------------------------------------------------
# Task 38.5 – Aggregation Helpers
# ---------------------------------------------------------------------------

def aggregate_workflow_metrics(workflows: List["WorkflowMetrics"]) -> Dict[str, Dict[str, Any]]:
    """Aggregate a list of ``WorkflowMetrics`` instances into node-level stats.

    Returns a mapping ``node_name → {count, error_count, durations, p95_duration, error_rate}``.
    """
    from statistics import mean, quantiles

    node_stats: Dict[str, Dict[str, Any]] = {}

    for wf in workflows:
        for node in wf.nodes:
            stats = node_stats.setdefault(node.node_name, {
                "durations": [],
                "error_count": 0,
                "count": 0,
            })

            if node.duration is not None:
                stats["durations"].append(node.duration)
            if node.status != "success":
                stats["error_count"] += 1
            stats["count"] += 1

    # Post-process metrics
    for node_name, stats in node_stats.items():
        durations = stats["durations"] or [0]
        stats["p95_duration"] = quantiles(durations, n=100)[94] if len(durations) > 1 else durations[0]
        stats["avg_duration"] = mean(durations)
        stats["error_rate"] = stats["error_count"] / stats["count"] if stats["count"] else 0.0

    return node_stats 