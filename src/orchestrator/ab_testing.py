"""A/B Testing Framework for workflow optimizations.

This module implements experiment management for testing different
orchestration strategies and measuring their performance impact.
"""

import json
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Callable, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import logging

from .state import ContentState
from .monitoring import get_monitor

logger = logging.getLogger(__name__)


class ExperimentStatus(Enum):
    """Status of an A/B test experiment."""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    TERMINATED = "terminated"


@dataclass
class ExperimentConfig:
    """Configuration for an A/B test experiment."""
    experiment_id: str
    name: str
    description: str
    status: ExperimentStatus
    
    # Experiment parameters
    control_strategy: str
    treatment_strategies: List[str]
    traffic_allocation: Dict[str, float]  # Strategy -> percentage (0.0-1.0)
    
    # Success metrics
    primary_metric: str  # e.g., "duration", "success_rate", "cost"
    secondary_metrics: List[str]
    
    # Experiment lifecycle
    start_date: str
    end_date: Optional[str]
    min_sample_size: int
    max_duration_days: int
    
    # Statistical parameters
    significance_level: float = 0.05
    power: float = 0.8
    minimum_effect_size: float = 0.1  # 10% improvement
    
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = datetime.now(timezone.utc).isoformat()


@dataclass
class ExperimentResult:
    """Results from an experiment execution."""
    experiment_id: str
    strategy: str
    execution_id: str
    
    # Performance metrics
    duration: float
    success: bool
    error_message: Optional[str]
    
    # Content metrics
    content_type: str
    content_length: Optional[int]
    
    # Resource metrics
    tokens_used: int = 0
    api_cost: float = 0.0
    
    # Metadata
    timestamp: str = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if self.metadata is None:
            self.metadata = {}


class ABTestManager:
    """Manages A/B testing experiments for workflow optimizations."""
    
    def __init__(self, experiments_dir: str = ".experiments"):
        self.experiments_dir = Path(experiments_dir)
        self.experiments_dir.mkdir(exist_ok=True)
        
        # In-memory cache for active experiments
        self.active_experiments: Dict[str, ExperimentConfig] = {}
        self.experiment_results: Dict[str, List[ExperimentResult]] = {}
        
        # Load existing experiments
        self._load_experiments()
    
    def _load_experiments(self):
        """Load experiments from disk."""
        try:
            for exp_file in self.experiments_dir.glob("experiment_*.json"):
                with open(exp_file, 'r') as f:
                    data = json.load(f)
                    config = ExperimentConfig(**data['config'])
                    if config.status in [ExperimentStatus.RUNNING, ExperimentStatus.PAUSED]:
                        self.active_experiments[config.experiment_id] = config
                    
                    # Load results
                    if 'results' in data:
                        self.experiment_results[config.experiment_id] = [
                            ExperimentResult(**result) for result in data['results']
                        ]
            
            logger.info(f"Loaded {len(self.active_experiments)} active experiments")
            
        except Exception as e:
            logger.error(f"Failed to load experiments: {e}")
    
    def _save_experiment(self, experiment: ExperimentConfig):
        """Save experiment configuration and results to disk."""
        try:
            exp_file = self.experiments_dir / f"experiment_{experiment.experiment_id}.json"
            
            data = {
                'config': asdict(experiment),
                'results': [asdict(result) for result in self.experiment_results.get(experiment.experiment_id, [])]
            }
            
            with open(exp_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save experiment {experiment.experiment_id}: {e}")
    
    def create_experiment(
        self,
        name: str,
        description: str,
        control_strategy: str,
        treatment_strategies: List[str],
        traffic_allocation: Dict[str, float],
        primary_metric: str = "duration",
        secondary_metrics: List[str] = None,
        min_sample_size: int = 100,
        max_duration_days: int = 30
    ) -> str:
        """Create a new A/B test experiment."""
        
        experiment_id = f"exp_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Validate traffic allocation
        total_allocation = sum(traffic_allocation.values())
        if abs(total_allocation - 1.0) > 0.01:
            raise ValueError(f"Traffic allocation must sum to 1.0, got {total_allocation}")
        
        experiment = ExperimentConfig(
            experiment_id=experiment_id,
            name=name,
            description=description,
            status=ExperimentStatus.DRAFT,
            control_strategy=control_strategy,
            treatment_strategies=treatment_strategies,
            traffic_allocation=traffic_allocation,
            primary_metric=primary_metric,
            secondary_metrics=secondary_metrics or [],
            start_date=datetime.now(timezone.utc).isoformat(),
            end_date=None,
            min_sample_size=min_sample_size,
            max_duration_days=max_duration_days
        )
        
        self.active_experiments[experiment_id] = experiment
        self.experiment_results[experiment_id] = []
        self._save_experiment(experiment)
        
        logger.info(f"Created experiment {experiment_id}: {name}")
        return experiment_id
    
    def start_experiment(self, experiment_id: str):
        """Start running an experiment."""
        if experiment_id not in self.active_experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        experiment = self.active_experiments[experiment_id]
        experiment.status = ExperimentStatus.RUNNING
        experiment.start_date = datetime.now(timezone.utc).isoformat()
        
        self._save_experiment(experiment)
        logger.info(f"Started experiment {experiment_id}")
    
    def select_strategy(self, experiment_id: str) -> str:
        """Select a strategy for this execution based on traffic allocation."""
        if experiment_id not in self.active_experiments:
            return "default"  # Fallback to default strategy
        
        experiment = self.active_experiments[experiment_id]
        if experiment.status != ExperimentStatus.RUNNING:
            return experiment.control_strategy
        
        # Weighted random selection based on traffic allocation
        rand_val = random.random()
        cumulative = 0.0
        
        for strategy, allocation in experiment.traffic_allocation.items():
            cumulative += allocation
            if rand_val <= cumulative:
                return strategy
        
        # Fallback to control
        return experiment.control_strategy
    
    def record_result(
        self,
        experiment_id: str,
        strategy: str,
        execution_id: str,
        duration: float,
        success: bool,
        content_type: str,
        content_length: Optional[int] = None,
        error_message: Optional[str] = None,
        tokens_used: int = 0,
        api_cost: float = 0.0,
        metadata: Dict[str, Any] = None
    ):
        """Record the result of an experiment execution."""
        
        result = ExperimentResult(
            experiment_id=experiment_id,
            strategy=strategy,
            execution_id=execution_id,
            duration=duration,
            success=success,
            error_message=error_message,
            content_type=content_type,
            content_length=content_length,
            tokens_used=tokens_used,
            api_cost=api_cost,
            metadata=metadata or {}
        )
        
        if experiment_id not in self.experiment_results:
            self.experiment_results[experiment_id] = []
        
        self.experiment_results[experiment_id].append(result)
        
        # Save periodically (every 10 results)
        if len(self.experiment_results[experiment_id]) % 10 == 0:
            if experiment_id in self.active_experiments:
                self._save_experiment(self.active_experiments[experiment_id])
    
    def analyze_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Analyze experiment results and determine statistical significance."""
        if experiment_id not in self.experiment_results:
            return {"error": "No results found for experiment"}
        
        results = self.experiment_results[experiment_id]
        if not results:
            return {"error": "No results to analyze"}
        
        # Group results by strategy
        strategy_results = {}
        for result in results:
            if result.strategy not in strategy_results:
                strategy_results[result.strategy] = []
            strategy_results[result.strategy].append(result)
        
        # Calculate metrics for each strategy
        strategy_metrics = {}
        for strategy, strategy_results_list in strategy_results.items():
            successful_results = [r for r in strategy_results_list if r.success]
            
            metrics = {
                "sample_size": len(strategy_results_list),
                "success_count": len(successful_results),
                "success_rate": len(successful_results) / len(strategy_results_list) if strategy_results_list else 0,
                "avg_duration": statistics.mean([r.duration for r in successful_results]) if successful_results else 0,
                "median_duration": statistics.median([r.duration for r in successful_results]) if successful_results else 0,
                "total_tokens": sum([r.tokens_used for r in strategy_results_list]),
                "total_cost": sum([r.api_cost for r in strategy_results_list]),
                "avg_cost_per_execution": statistics.mean([r.api_cost for r in strategy_results_list]) if strategy_results_list else 0
            }
            
            if len(successful_results) > 1:
                metrics["duration_std"] = statistics.stdev([r.duration for r in successful_results])
            
            strategy_metrics[strategy] = metrics
        
        return {
            "experiment_id": experiment_id,
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_executions": len(results),
            "strategy_metrics": strategy_metrics
        }


# Global A/B test manager instance
_ab_manager = None

def get_ab_manager() -> ABTestManager:
    """Get global A/B test manager instance."""
    global _ab_manager
    if _ab_manager is None:
        _ab_manager = ABTestManager()
    return _ab_manager