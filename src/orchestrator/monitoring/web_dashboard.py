#!/usr/bin/env python3
"""
Simple web dashboard for real-time monitoring visualization.
"""

import json
from flask import Flask, render_template_string, jsonify
from datetime import datetime
from .dashboard import get_monitor

app = Flask(__name__)

# HTML template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InsightHub Orchestrator Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-value { font-size: 2em; font-weight: bold; color: #2563eb; }
        .stat-label { color: #6b7280; font-size: 0.9em; }
        .section { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .section h2 { margin-top: 0; color: #333; }
        .node-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .node-card { background: #f8fafc; padding: 15px; border-radius: 6px; border-left: 4px solid #10b981; }
        .workflows-table { width: 100%; border-collapse: collapse; }
        .workflows-table th, .workflows-table td { padding: 10px; text-align: left; border-bottom: 1px solid #e5e7eb; }
        .workflows-table th { background-color: #f9fafb; font-weight: 600; }
        .status-success { color: #10b981; font-weight: bold; }
        .status-error { color: #ef4444; font-weight: bold; }
        .alert { padding: 12px; margin: 10px 0; border-radius: 6px; }
        .alert-error { background-color: #fee2e2; color: #dc2626; border-left: 4px solid #dc2626; }
        .alert-warning { background-color: #fef3c7; color: #d97706; border-left: 4px solid #d97706; }
        .alert-info { background-color: #dbeafe; color: #2563eb; border-left: 4px solid #2563eb; }
        .refresh-btn { background: #2563eb; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; }
        .refresh-btn:hover { background: #1d4ed8; }
        .last-updated { color: #6b7280; font-size: 0.8em; text-align: center; margin-top: 20px; }
    </style>
    <script>
        function refreshData() {
            fetch('/api/dashboard')
                .then(response => response.json())
                .then(data => {
                    updateDashboard(data);
                })
                .catch(error => console.error('Error fetching data:', error));
        }
        
        function updateDashboard(data) {
            // Update overview stats
            document.getElementById('total-workflows').textContent = data.overview.total_workflows;
            document.getElementById('success-rate').textContent = (data.overview.success_rate * 100).toFixed(1) + '%';
            document.getElementById('active-workflows').textContent = data.overview.active_workflows;
            document.getElementById('active-nodes').textContent = data.overview.active_nodes;
            
            // Update 24h stats
            document.getElementById('workflows-24h').textContent = data.recent_performance.workflows_24h;
            document.getElementById('avg-duration-24h').textContent = data.recent_performance.avg_duration_24h.toFixed(1) + 's';
            document.getElementById('error-rate-24h').textContent = (data.recent_performance.error_rate_24h * 100).toFixed(1) + '%';
            
            // Update last updated time
            document.getElementById('last-updated').textContent = 'Last updated: ' + new Date(data.timestamp).toLocaleString();
            
            // Update node performance
            updateNodePerformance(data.node_performance);
            
            // Update recent workflows
            updateRecentWorkflows(data.recent_workflows);
        }
        
        function updateNodePerformance(nodeStats) {
            const container = document.getElementById('node-performance');
            container.innerHTML = '';
            
            Object.entries(nodeStats).forEach(([nodeName, stats]) => {
                const nodeCard = document.createElement('div');
                nodeCard.className = 'node-card';
                nodeCard.innerHTML = `
                    <h4>${nodeName}</h4>
                    <div>Executions: ${stats.total_executions}</div>
                    <div>Success Rate: ${(stats.success_rate * 100).toFixed(1)}%</div>
                    <div>Avg Duration: ${stats.avg_duration.toFixed(1)}s</div>
                `;
                container.appendChild(nodeCard);
            });
        }
        
        function updateRecentWorkflows(workflows) {
            const tbody = document.getElementById('recent-workflows-tbody');
            tbody.innerHTML = '';
            
            workflows.forEach(workflow => {
                const row = document.createElement('tr');
                const statusClass = workflow.status === 'success' ? 'status-success' : 'status-error';
                row.innerHTML = `
                    <td>${workflow.id}</td>
                    <td>${workflow.content_type}</td>
                    <td>${workflow.duration ? workflow.duration.toFixed(1) + 's' : 'N/A'}</td>
                    <td class="${statusClass}">${workflow.status}</td>
                    <td>${new Date(workflow.start_time).toLocaleString()}</td>
                    <td>${workflow.total_tokens}</td>
                    <td>$${workflow.total_cost.toFixed(4)}</td>
                `;
                tbody.appendChild(row);
            });
        }
        
        // Auto-refresh every 30 seconds
        setInterval(refreshData, 30000);
        
        // Initial load
        window.addEventListener('load', refreshData);
    </script>
</head>
<body>
    <div class="container">
        <h1>🎯 InsightHub Orchestrator Dashboard</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="total-workflows">-</div>
                <div class="stat-label">Total Workflows</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="success-rate">-</div>
                <div class="stat-label">Success Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="active-workflows">-</div>
                <div class="stat-label">Active Workflows</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="active-nodes">-</div>
                <div class="stat-label">Active Nodes</div>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="workflows-24h">-</div>
                <div class="stat-label">Workflows (24h)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="avg-duration-24h">-</div>
                <div class="stat-label">Avg Duration (24h)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="error-rate-24h">-</div>
                <div class="stat-label">Error Rate (24h)</div>
            </div>
            <div class="stat-card">
                <button class="refresh-btn" onclick="refreshData()">🔄 Refresh</button>
            </div>
        </div>
        
        <div class="section">
            <h2>🔧 Node Performance</h2>
            <div class="node-stats" id="node-performance">
                <!-- Node stats will be populated by JavaScript -->
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Recent Workflows</h2>
            <table class="workflows-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Content Type</th>
                        <th>Duration</th>
                        <th>Status</th>
                        <th>Start Time</th>
                        <th>Tokens</th>
                        <th>Cost</th>
                    </tr>
                </thead>
                <tbody id="recent-workflows-tbody">
                    <!-- Workflow data will be populated by JavaScript -->
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>🚨 Alerts</h2>
            <div id="alerts-container">
                <!-- Alerts will be populated by JavaScript -->
            </div>
        </div>
        
        <div class="last-updated" id="last-updated">
            Loading...
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Serve the main dashboard page."""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/dashboard')
def api_dashboard():
    """API endpoint for dashboard data."""
    monitor = get_monitor()
    data = monitor.get_dashboard_data()
    return jsonify(data)

@app.route('/api/alerts')
def api_alerts():
    """API endpoint for alerts."""
    monitor = get_monitor()
    alerts = monitor.get_alerts()
    return jsonify(alerts)

@app.route('/api/status')
def api_status():
    """API endpoint for system status."""
    monitor = get_monitor()
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "active_workflows": len(monitor.active_workflows),
        "active_nodes": len(monitor.active_nodes)
    })

def run_dashboard(host='localhost', port=8080, debug=False):
    """Run the dashboard web server."""
    print(f"🎯 Starting InsightHub Orchestrator Dashboard at http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    run_dashboard(debug=True) 