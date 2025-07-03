# LangSmith Operational Procedures

## Overview

This document outlines operational procedures for maintaining LangSmith monitoring infrastructure, handling incidents, backup/recovery, and system maintenance for the InsightHub orchestrator.

## Table of Contents

1. [Monitoring and Alerting Setup](#monitoring-and-alerting-setup)
2. [Incident Response Procedures](#incident-response-procedures)
3. [Backup and Recovery Procedures](#backup-and-recovery-procedures)
4. [Maintenance and Update Procedures](#maintenance-and-update-procedures)
5. [Security and Compliance](#security-and-compliance)

## Monitoring and Alerting Setup

### Alert Configuration

```python
# config/alert_config.py
ALERT_THRESHOLDS = {
    "error_rate": {
        "warning": 0.05,    # 5% error rate
        "critical": 0.15    # 15% error rate
    },
    "response_time": {
        "warning": 30,      # 30 seconds
        "critical": 60      # 60 seconds
    },
    "api_quota": {
        "warning": 0.80,    # 80% of quota
        "critical": 0.95    # 95% of quota
    },
    "cost_per_hour": {
        "warning": 10.0,    # $10/hour
        "critical": 25.0    # $25/hour
    },
    "total_tokens_per_hour": {
        "warning": 100000,  # 100k tokens/hour
        "critical": 500000  # 500k tokens/hour
    }
}

NOTIFICATION_CHANNELS = {
    "critical": [
        "slack://team-alerts",
        "email://on-call@insighthub.com",
        "sms://+1234567890"
    ],
    "warning": [
        "slack://monitoring",
        "email://team-leads@insighthub.com"
    ]
}
```

### Monitoring Setup Script

```python
# scripts/setup_monitoring.py
from src.orchestrator.monitoring.dashboard import get_monitor
import json

def setup_monitoring():
    """Initialize monitoring infrastructure."""
    monitor = get_monitor()
    
    # Create monitoring directories
    directories = [
        ".monitoring",
        "logs/monitoring",
        "health_reports",
        "incidents"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Initialize alert system
    alert_config = {
        "enabled": True,
        "check_interval": 300,  # 5 minutes
        "thresholds": ALERT_THRESHOLDS,
        "channels": NOTIFICATION_CHANNELS
    }
    
    with open(".monitoring/alert_config.json", "w") as f:
        json.dump(alert_config, f, indent=2)
    
    print("✅ Monitoring infrastructure initialized")

def start_alert_monitor():
    """Start the alert monitoring service."""
    import schedule
    import time
    
    def check_alerts():
        monitor = get_monitor()
        dashboard_data = monitor.get_dashboard_data()
        
        # Check error rate
        error_rate = 1 - dashboard_data['overview']['success_rate']
        if error_rate > ALERT_THRESHOLDS['error_rate']['critical']:
            send_alert("critical", f"Error rate critical: {error_rate:.1%}")
        elif error_rate > ALERT_THRESHOLDS['error_rate']['warning']:
            send_alert("warning", f"Error rate elevated: {error_rate:.1%}")
        
        # Check response time
        avg_duration = dashboard_data.get('avg_duration', 0)
        if avg_duration > ALERT_THRESHOLDS['response_time']['critical']:
            send_alert("critical", f"Response time critical: {avg_duration:.1f}s")
        elif avg_duration > ALERT_THRESHOLDS['response_time']['warning']:
            send_alert("warning", f"Response time elevated: {avg_duration:.1f}s")
    
    # Schedule alert checks every 5 minutes
    schedule.every(5).minutes.do(check_alerts)
    
    print("🔔 Alert monitoring started")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    setup_monitoring()
    start_alert_monitor()
```

## Incident Response Procedures

### Incident Classification

**Severity Levels:**

1. **Critical (P1)**
   - System completely down
   - >25% error rate
   - Security breach
   - Response: Immediate (5 minutes)

2. **High (P2)**
   - Significant performance degradation
   - 15-25% error rate
   - API quota exceeded
   - Response: Within 30 minutes

3. **Medium (P3)**
   - Minor performance issues
   - 5-15% error rate
   - Non-critical feature failures
   - Response: Within 2 hours

4. **Low (P4)**
   - Cosmetic issues
   - <5% error rate
   - Documentation updates
   - Response: Next business day

### Incident Response Runbook

```python
# scripts/incident_runbook.py
from datetime import datetime
import json

class IncidentRunbook:
    def __init__(self):
        self.incident_id = None
        self.start_time = None
        self.severity = None
        
    def start_incident(self, severity: str, description: str):
        """Start incident response process."""
        self.incident_id = f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.start_time = datetime.now()
        self.severity = severity
        
        print(f"🚨 INCIDENT STARTED: {self.incident_id}")
        print(f"Severity: {severity}")
        print(f"Description: {description}")
        
        # Execute severity-specific response
        if severity == "critical":
            self.critical_response()
        elif severity == "high":
            self.high_response()
        elif severity == "medium":
            self.medium_response()
        else:
            self.low_response()
        
        # Log incident
        self.log_incident(description)
    
    def critical_response(self):
        """Response for critical incidents."""
        print("🔥 CRITICAL INCIDENT RESPONSE")
        print("1. Page on-call engineer immediately")
        print("2. Start incident bridge/war room")
        print("3. Notify leadership team")
        print("4. Begin system triage")
        
        # Immediate actions
        self.check_system_health()
        self.enable_emergency_mode()
        self.gather_diagnostics()
    
    def high_response(self):
        """Response for high severity incidents."""
        print("⚠️ HIGH SEVERITY INCIDENT RESPONSE")
        print("1. Notify primary on-call")
        print("2. Start investigation")
        print("3. Prepare status updates")
        
        self.check_system_health()
        self.apply_quick_fixes()
    
    def check_system_health(self):
        """Quick system health check."""
        from src.orchestrator.monitoring.dashboard import get_monitor
        
        monitor = get_monitor()
        data = monitor.get_dashboard_data()
        
        print("📊 System Health Check:")
        print(f"  Success Rate: {data['overview']['success_rate']:.1%}")
        print(f"  Active Workflows: {data['overview']['active_workflows']}")
        print(f"  Recent Errors: {len(data.get('alerts', []))}")
    
    def enable_emergency_mode(self):
        """Enable emergency fallback mode."""
        print("🚨 Enabling Emergency Mode:")
        print("  - Activating local monitoring fallback")
        print("  - Enabling aggressive caching")
        print("  - Reducing processing complexity")
        print("  - Implementing circuit breakers")
    
    def gather_diagnostics(self):
        """Gather diagnostic information."""
        print("🔍 Gathering Diagnostics:")
        
        # System metrics
        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "incident_id": self.incident_id,
            "system_metrics": self.get_system_metrics(),
            "recent_logs": self.get_recent_logs(),
            "trace_analysis": self.get_trace_analysis()
        }
        
        # Save diagnostics
        filename = f"incidents/{self.incident_id}_diagnostics.json"
        with open(filename, "w") as f:
            json.dump(diagnostics, f, indent=2)
        
        print(f"  Diagnostics saved: {filename}")
    
    def log_incident(self, description: str):
        """Log incident details."""
        incident_log = {
            "incident_id": self.incident_id,
            "start_time": self.start_time.isoformat(),
            "severity": self.severity,
            "description": description,
            "status": "active",
            "timeline": [],
            "resolution": None
        }
        
        filename = f"incidents/{self.incident_id}.json"
        with open(filename, "w") as f:
            json.dump(incident_log, f, indent=2)
```

### Post-Incident Review

```python
# scripts/post_incident_review.py
def conduct_post_incident_review(incident_id: str):
    """Conduct post-incident review and create action items."""
    
    # Load incident data
    with open(f"incidents/{incident_id}.json", "r") as f:
        incident_data = json.load(f)
    
    print(f"📋 Post-Incident Review: {incident_id}")
    print(f"Duration: {incident_data.get('duration', 'Unknown')}")
    print(f"Impact: {incident_data.get('impact', 'Under analysis')}")
    
    # Review checklist
    review_questions = [
        "What was the root cause?",
        "How could detection have been faster?",
        "What preventive measures can be implemented?",
        "Were response procedures effective?",
        "What documentation needs updating?"
    ]
    
    action_items = []
    for question in review_questions:
        print(f"\n❓ {question}")
        response = input("Response: ")
        if response.strip():
            action_items.append({
                "question": question,
                "response": response,
                "priority": "medium",
                "assignee": "team"
            })
    
    # Save review results
    review_data = {
        "incident_id": incident_id,
        "review_date": datetime.now().isoformat(),
        "action_items": action_items,
        "lessons_learned": [],
        "prevention_measures": []
    }
    
    filename = f"incidents/{incident_id}_review.json"
    with open(filename, "w") as f:
        json.dump(review_data, f, indent=2)
    
    print(f"✅ Post-incident review saved: {filename}")
```

## Backup and Recovery Procedures

### Data Backup Strategy

```python
# scripts/backup_system.py
import shutil
from datetime import datetime
from pathlib import Path

class BackupManager:
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_full_backup(self):
        """Create full system backup."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"full_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        print(f"📦 Creating full backup: {backup_name}")
        
        # Backup monitoring data
        self.backup_monitoring_data(backup_path)
        
        # Backup configuration
        self.backup_configuration(backup_path)
        
        # Backup logs
        self.backup_logs(backup_path)
        
        # Create backup manifest
        self.create_manifest(backup_path)
        
        print(f"✅ Full backup completed: {backup_path}")
        return backup_path
    
    def backup_monitoring_data(self, backup_path):
        """Backup monitoring data."""
        monitoring_backup = backup_path / "monitoring"
        monitoring_backup.mkdir(parents=True, exist_ok=True)
        
        # Copy monitoring files
        source_dir = Path(".monitoring")
        if source_dir.exists():
            shutil.copytree(source_dir, monitoring_backup / "data")
        
        print("  📊 Monitoring data backed up")
    
    def backup_configuration(self, backup_path):
        """Backup configuration files."""
        config_backup = backup_path / "config"
        config_backup.mkdir(parents=True, exist_ok=True)
        
        # Configuration files to backup
        config_files = [
            ".env",
            "config/",
            "pyproject.toml"
        ]
        
        for config_file in config_files:
            source = Path(config_file)
            if source.exists():
                if source.is_file():
                    shutil.copy2(source, config_backup)
                else:
                    shutil.copytree(source, config_backup / source.name)
        
        print("  ⚙️ Configuration backed up")
    
    def restore_from_backup(self, backup_path: Path):
        """Restore system from backup."""
        print(f"🔄 Restoring from backup: {backup_path}")
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")
        
        # Restore monitoring data
        monitoring_backup = backup_path / "monitoring" / "data"
        if monitoring_backup.exists():
            shutil.rmtree(".monitoring", ignore_errors=True)
            shutil.copytree(monitoring_backup, ".monitoring")
            print("  📊 Monitoring data restored")
        
        # Restore configuration
        config_backup = backup_path / "config"
        if config_backup.exists():
            for item in config_backup.iterdir():
                if item.is_file():
                    shutil.copy2(item, ".")
                else:
                    target = Path(item.name)
                    if target.exists():
                        shutil.rmtree(target)
                    shutil.copytree(item, target)
            print("  ⚙️ Configuration restored")
        
        print("✅ System restored from backup")

# Automated backup schedule
def schedule_backups():
    """Schedule automated backups."""
    import schedule
    import time
    
    backup_manager = BackupManager()
    
    # Daily backup at 2 AM
    schedule.every().day.at("02:00").do(backup_manager.create_full_backup)
    
    # Weekly cleanup (keep last 30 days)
    schedule.every().week.do(backup_manager.cleanup_old_backups, days=30)
    
    print("📅 Backup schedule initialized")
    while True:
        schedule.run_pending()
        time.sleep(3600)  # Check every hour
```

### Disaster Recovery Plan

```python
# scripts/disaster_recovery.py
class DisasterRecovery:
    def __init__(self):
        self.recovery_steps = [
            "assess_damage",
            "restore_infrastructure",
            "restore_data",
            "verify_functionality",
            "resume_operations"
        ]
    
    def execute_recovery_plan(self):
        """Execute disaster recovery plan."""
        print("🆘 EXECUTING DISASTER RECOVERY PLAN")
        
        for step in self.recovery_steps:
            print(f"\n📋 Step: {step.replace('_', ' ').title()}")
            
            if step == "assess_damage":
                self.assess_damage()
            elif step == "restore_infrastructure":
                self.restore_infrastructure()
            elif step == "restore_data":
                self.restore_data()
            elif step == "verify_functionality":
                self.verify_functionality()
            elif step == "resume_operations":
                self.resume_operations()
            
            input("Press Enter to continue to next step...")
    
    def assess_damage(self):
        """Assess system damage."""
        print("  🔍 Assessing system damage...")
        print("  - Check file system integrity")
        print("  - Verify database accessibility")
        print("  - Test network connectivity")
        print("  - Identify missing components")
    
    def restore_infrastructure(self):
        """Restore infrastructure components."""
        print("  🏗️ Restoring infrastructure...")
        print("  - Reinstall system dependencies")
        print("  - Restore configuration files")
        print("  - Setup monitoring infrastructure")
        print("  - Configure network settings")
    
    def restore_data(self):
        """Restore data from backups."""
        print("  💾 Restoring data...")
        backup_manager = BackupManager()
        
        # Find latest backup
        latest_backup = self.find_latest_backup()
        if latest_backup:
            backup_manager.restore_from_backup(latest_backup)
        else:
            print("  ⚠️ No backups found - manual data recovery required")
    
    def verify_functionality(self):
        """Verify system functionality."""
        print("  ✅ Verifying functionality...")
        print("  - Test monitoring dashboard")
        print("  - Verify trace collection")
        print("  - Check alert system")
        print("  - Run integration tests")
```

## Maintenance and Update Procedures

### Scheduled Maintenance

```python
# scripts/maintenance.py
def weekly_maintenance():
    """Perform weekly maintenance tasks."""
    print("🔧 Weekly Maintenance - {}".format(datetime.now().strftime("%Y-%m-%d")))
    
    # Clean up old logs
    cleanup_logs(days=7)
    
    # Optimize monitoring database
    optimize_monitoring_db()
    
    # Update dependencies
    check_dependency_updates()
    
    # Verify backup integrity
    verify_backups()
    
    # Generate health report
    generate_weekly_health_report()

def cleanup_logs(days=7):
    """Clean up old log files."""
    cutoff_date = datetime.now() - timedelta(days=days)
    log_dir = Path("logs")
    
    if log_dir.exists():
        for log_file in log_dir.rglob("*.log"):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                log_file.unlink()
                print(f"  🗑️ Removed old log: {log_file}")

def check_dependency_updates():
    """Check for dependency updates."""
    print("  📦 Checking dependency updates...")
    
    # Check Python packages
    import subprocess
    result = subprocess.run(["pip", "list", "--outdated"], capture_output=True, text=True)
    
    if result.stdout:
        print("  📋 Outdated packages found:")
        print(result.stdout)
    else:
        print("  ✅ All packages up to date")
```

## Security and Compliance

### Optimization & Cache Configuration (Task 38.5)

> **Status:** Introduced in July 2025 – enabled when `ENABLE_OPTIMIZATIONS=true`.

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `ENABLE_OPTIMIZATIONS` | `false` | Master switch – routes `Orchestrator.process_content()` through the new `OptimizedOrchestrator` pipeline. |
| `IH_CACHE_MAX_AGE_HOURS` | `24` | TTL for a single ContentCache entry. |
| `IH_CACHE_MAX_ITEMS` | `1000` | Maximum number of cached items before LRU eviction begins. |
| `METRICS_TUNE_INTERVAL_MIN` | `30` | Minimum minutes between automatic metric-driven tuning cycles. |
| `RETRY_TIMEOUT_SEC` | `30` | Per-attempt timeout enforced by `SmartRetryManager`. |

These values are surfaced via a centralized dataclass:

```python
from src.config import OPTIMIZATION_SETTINGS

print(OPTIMIZATION_SETTINGS.enable_optimizations)
```

### Metrics-Driven Tuning

The **OptimizerMetricsTuner** aggregates recent `WorkflowMetrics` objects and periodically calls

* `AdaptiveModelSelector.update_from_metrics()` – adjusts model choices based on p95 node duration.
* `SmartRetryManager.tune_from_metrics()` – recalibrates retry base delays from error frequencies.

Together with new cache hit/miss counters (`ContentCache.stats`) this creates a feedback loop that slowly
optimises runtime without manual intervention.  Tuning frequency is controlled by
`METRICS_TUNE_INTERVAL_MIN` to avoid thrashing.

### Operational Impact

* **Enablement**: set `ENABLE_OPTIMIZATIONS=true` in production `.env` and redeploy.
* **Monitoring**: dashboard surfaces cache hit ratio, timeout occurrences and model latency before/after tuning.
* **Rollback**: unset the env flag; OptimizedOrchestrator path is bypassed.

## Quick-Start: LangSmith Web Dashboard (Task 38.4)

After ensuring you have Python dependencies installed (`flask`, `langsmith>=0.0.14`), you can launch the live monitoring UI with:

```bash
python -m src.orchestrator.monitoring.langsmith_web_dashboard  # default http://localhost:8081
# or explicitly
python - <<'PY'
from src.orchestrator.monitoring.langsmith_web_dashboard import run_enhanced_dashboard
run_enhanced_dashboard(host="0.0.0.0", port=8081, debug=False)
PY
```

Environment variables (at minimum):

```
LANGSMITH_API_KEY=<your_api_key>       # optional for local-only mode
LANGSMITH_PROJECT=InsightHub           # optional (default as shown)
```

Health-check endpoints:

| URL | Description |
|------|-------------|
| `GET /api/test` | Returns `{"status":"ok"}` JSON – confirms server up |
| `GET /api/enhanced-dashboard` | Returns the full dashboard JSON payload |
| `GET /api/langsmith-status` | Quick LangSmith connection / permission check |

> **Tip:** Add `ENABLE_OPTIMIZATIONS=true` to observe cache hit/miss counters and adaptive tuning metrics live.

---

This operational procedures documentation provides comprehensive guidance for maintaining LangSmith infrastructure, handling incidents, and ensuring system reliability. 