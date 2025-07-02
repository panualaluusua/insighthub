#!/usr/bin/env python3
"""
Enhanced web dashboard with LangSmith monitoring integration.
Provides visual monitoring for orchestrator performance with LangSmith insights.
"""

import json
from flask import Flask, render_template_string, jsonify
from datetime import datetime
from .langsmith_dashboard import get_langsmith_dashboard

app = Flask(__name__)

# Enhanced HTML template with LangSmith features
ENHANCED_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 InsightHub LangSmith Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { color: white; text-align: center; margin-bottom: 30px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header-status { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 20px; backdrop-filter: blur(10px); }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .status-item { color: white; text-align: center; }
        .status-value { font-size: 1.5em; font-weight: bold; }
        .status-label { font-size: 0.9em; opacity: 0.8; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); transition: transform 0.3s ease; }
        .stat-card:hover { transform: translateY(-5px); box-shadow: 0 12px 35px rgba(0,0,0,0.15); }
        .stat-value { font-size: 2.5em; font-weight: bold; color: #667eea; margin-bottom: 5px; }
        .stat-label { color: #6b7280; font-size: 0.95em; }
        .section { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); margin-bottom: 25px; }
        .section h2 { margin-top: 0; color: #333; display: flex; align-items: center; gap: 10px; }
        .section h2::before { content: "📊"; }
        .langsmith-section h2::before { content: "🔗"; }
        .performance-section h2::before { content: "⚡"; }
        .errors-section h2::before { content: "🚨"; }
        .insights-section h2::before { content: "💡"; }
        .node-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        .node-card { background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); padding: 20px; border-radius: 12px; border-left: 5px solid #10b981; }
        .node-card h4 { margin: 0 0 15px 0; color: #1f2937; }
        .node-metric { display: flex; justify-content: space-between; margin: 8px 0; }
        .metric-label { color: #6b7280; }
        .metric-value { font-weight: bold; color: #1f2937; }
        .workflows-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        .workflows-table th, .workflows-table td { padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }
        .workflows-table th { background-color: #f9fafb; font-weight: 600; }
        .workflows-table tr:hover { background-color: #f9fafb; }
        .status-success { color: #10b981; font-weight: bold; }
        .status-error { color: #ef4444; font-weight: bold; }
        .status-running { color: #f59e0b; font-weight: bold; }
        .alert { padding: 15px; margin: 15px 0; border-radius: 10px; border-left: 4px solid; }
        .alert-error { background-color: #fee2e2; color: #dc2626; border-left-color: #dc2626; }
        .alert-warning { background-color: #fef3c7; color: #d97706; border-left-color: #d97706; }
        .alert-info { background-color: #dbeafe; color: #2563eb; border-left-color: #2563eb; }
        .alert-success { background-color: #d1fae5; color: #065f46; border-left-color: #10b981; }
        .recommendations { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }
        .recommendation { background: linear-gradient(135deg, #fff7ed 0%, #fed7aa 100%); padding: 20px; border-radius: 10px; border-left: 4px solid #f59e0b; }
        .recommendation h4 { margin: 0 0 10px 0; color: #92400e; }
        .recommendation .priority { font-size: 0.8em; font-weight: bold; text-transform: uppercase; }
        .priority-high { color: #dc2626; }
        .priority-medium { color: #d97706; }
        .priority-low { color: #059669; }
        .refresh-btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 12px 25px; border-radius: 8px; cursor: pointer; font-weight: bold; transition: all 0.3s ease; }
        .refresh-btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }
        .last-updated { color: rgba(255,255,255,0.8); font-size: 0.9em; text-align: center; margin-top: 30px; }
        .langsmith-status { display: flex; align-items: center; gap: 10px; padding: 10px; border-radius: 8px; margin: 10px 0; }
        .status-connected { background-color: #d1fae5; color: #065f46; }
        .status-pending { background-color: #fef3c7; color: #92400e; }
        .status-error { background-color: #fee2e2; color: #dc2626; }
        .performance-insight { background: linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 100%); padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #0284c7; }
        .insight-title { font-weight: bold; color: #0c4a6e; margin-bottom: 8px; }
        .insight-details { color: #0369a1; }
        .bottleneck { background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%); padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #dc2626; }
        .bottleneck-title { font-weight: bold; color: #991b1b; margin-bottom: 8px; }
        .bottleneck-suggestion { color: #b91c1c; font-style: italic; }
        .trace-analysis { background: linear-gradient(135deg, #f0f9ff 0%, #dbeafe 100%); padding: 20px; border-radius: 12px; margin: 15px 0; }
    </style>
    <script>
        function refreshData() {
            fetch('/api/enhanced-dashboard')
                .then(response => response.json())
                .then(data => {
                    updateDashboard(data);
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                    showAlert('Failed to fetch dashboard data', 'error');
                });
        }
        
        function updateDashboard(data) {
            // Update LangSmith status
            updateLangSmithStatus(data.langsmith_status);
            
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
            
            // Update LangSmith-specific sections
            updateTraceAnalysis(data.trace_analysis);
            updatePerformanceInsights(data.performance_insights);
            updateBottlenecks(data.bottleneck_detection);
            updateRecommendations(data.recommendation_engine);
        }
        
        function updateLangSmithStatus(status) {
            const container = document.getElementById('langsmith-status');
            const statusClass = status.api_available ? 'status-connected' : 
                               (status.client_initialized ? 'status-pending' : 'status-error');
            
            const statusText = status.api_available ? 'Connected' : 
                              (status.client_initialized ? 'API Permissions Pending' : 'Not Available');
            
            container.className = 'langsmith-status ' + statusClass;
            container.innerHTML = `
                <strong>LangSmith:</strong> ${statusText} | 
                Project: ${status.project} | 
                Pending Traces: ${status.pending_traces}
            `;
        }
        
        function updateNodePerformance(nodeStats) {
            const container = document.getElementById('node-performance');
            container.innerHTML = '';
            
            Object.entries(nodeStats).forEach(([nodeName, stats]) => {
                const nodeCard = document.createElement('div');
                nodeCard.className = 'node-card';
                nodeCard.innerHTML = `
                    <h4>${nodeName}</h4>
                    <div class="node-metric">
                        <span class="metric-label">Executions:</span>
                        <span class="metric-value">${stats.total_executions}</span>
                    </div>
                    <div class="node-metric">
                        <span class="metric-label">Success Rate:</span>
                        <span class="metric-value">${(stats.success_rate * 100).toFixed(1)}%</span>
                    </div>
                    <div class="node-metric">
                        <span class="metric-label">Avg Duration:</span>
                        <span class="metric-value">${stats.avg_duration.toFixed(1)}s</span>
                    </div>
                `;
                container.appendChild(nodeCard);
            });
        }
        
        function updateRecentWorkflows(workflows) {
            const tbody = document.getElementById('recent-workflows-tbody');
            tbody.innerHTML = '';
            
            workflows.forEach(workflow => {
                const row = document.createElement('tr');
                const statusClass = workflow.status === 'success' ? 'status-success' : 
                                   workflow.status === 'error' ? 'status-error' : 'status-running';
                row.innerHTML = `
                    <td>${workflow.id.substring(0, 8)}...</td>
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
        
        function updateTraceAnalysis(analysis) {
            const container = document.getElementById('trace-analysis');
            if (analysis.total_traces === 0) {
                container.innerHTML = '<div class="alert alert-info">No traces available for analysis</div>';
                return;
            }
            
            container.innerHTML = `
                <h3>📈 Trace Analysis</h3>
                <div class="performance-insight">
                    <div class="insight-title">Total Traces: ${analysis.total_traces}</div>
                    <div class="insight-details">
                        Most Common Path: ${analysis.trace_patterns.most_common_path}<br>
                        Content Types: ${Object.entries(analysis.trace_patterns.content_type_breakdown).map(([type, count]) => `${type}: ${count}`).join(', ')}
                    </div>
                </div>
            `;
        }
        
        function updatePerformanceInsights(insights) {
            const container = document.getElementById('performance-insights');
            container.innerHTML = '<h3>⚡ Performance Insights</h3>';
            
            if (insights.slow_workflows.length > 0) {
                const slowWorkflowsHtml = insights.slow_workflows.map(w => 
                    `<li>${w.content_type}: ${w.duration.toFixed(1)}s (${w.threshold_exceeded.toFixed(1)}s over threshold)</li>`
                ).join('');
                container.innerHTML += `
                    <div class="performance-insight">
                        <div class="insight-title">Slow Workflows (${insights.slow_workflows.length})</div>
                        <ul class="insight-details">${slowWorkflowsHtml}</ul>
                    </div>
                `;
            }
            
            if (insights.optimization_opportunities.length > 0) {
                const opportunitiesHtml = insights.optimization_opportunities.map(opp => 
                    `<li>${opp.description}</li>`
                ).join('');
                container.innerHTML += `
                    <div class="performance-insight">
                        <div class="insight-title">Optimization Opportunities</div>
                        <ul class="insight-details">${opportunitiesHtml}</ul>
                    </div>
                `;
            }
            
            // Resource utilization
            const resources = insights.resource_utilization;
            if (resources.total_tokens_used > 0) {
                container.innerHTML += `
                    <div class="performance-insight">
                        <div class="insight-title">Resource Utilization</div>
                        <div class="insight-details">
                            Tokens Used: ${resources.total_tokens_used.toLocaleString()}<br>
                            Total Cost: $${resources.total_cost.toFixed(4)}<br>
                            Avg Cost/Workflow: $${resources.avg_cost_per_workflow.toFixed(4)}<br>
                            Cost per Token: $${resources.cost_per_token.toFixed(6)}
                        </div>
                    </div>
                `;
            }
        }
        
        function updateBottlenecks(bottlenecks) {
            const container = document.getElementById('bottlenecks');
            container.innerHTML = '<h3>🚨 Bottleneck Detection</h3>';
            
            if (bottlenecks.length === 0) {
                container.innerHTML += '<div class="alert alert-success">No bottlenecks detected! 🎉</div>';
                return;
            }
            
            bottlenecks.forEach(bottleneck => {
                const severityClass = bottleneck.severity === 'high' ? 'bottleneck' : 'performance-insight';
                container.innerHTML += `
                    <div class="${severityClass}">
                        <div class="bottleneck-title">${bottleneck.type.replace('_', ' ').toUpperCase()}: ${bottleneck.node}</div>
                        <div class="bottleneck-suggestion">${bottleneck.suggestion}</div>
                    </div>
                `;
            });
        }
        
        function updateRecommendations(recommendations) {
            const container = document.getElementById('recommendations');
            container.innerHTML = '';
            
            if (recommendations.length === 0) {
                container.innerHTML = '<div class="alert alert-success">No recommendations - system performing optimally! ✨</div>';
                return;
            }
            
            recommendations.forEach(rec => {
                const recommendation = document.createElement('div');
                recommendation.className = 'recommendation';
                recommendation.innerHTML = `
                    <div class="priority priority-${rec.priority}">[${rec.priority.toUpperCase()}]</div>
                    <h4>${rec.title}</h4>
                    <div><strong>Category:</strong> ${rec.category}</div>
                    <div><strong>Issue:</strong> ${rec.description}</div>
                    <div><strong>Action:</strong> ${rec.action}</div>
                `;
                container.appendChild(recommendation);
            });
        }
        
        function showAlert(message, type) {
            const alertHtml = `<div class="alert alert-${type}">${message}</div>`;
            document.body.insertAdjacentHTML('afterbegin', alertHtml);
            setTimeout(() => {
                document.querySelector('.alert').remove();
            }, 5000);
        }
        
        // Auto-refresh every 30 seconds
        setInterval(refreshData, 30000);
        
        // Initial load
        window.addEventListener('load', refreshData);
    </script>
</head>
<body>
    <div class="container">
        <h1>🎯 InsightHub LangSmith Monitoring Dashboard</h1>
        
        <div class="header-status">
            <div class="status-grid">
                <div class="status-item">
                    <div class="status-value" id="total-workflows">-</div>
                    <div class="status-label">Total Workflows</div>
                </div>
                <div class="status-item">
                    <div class="status-value" id="success-rate">-</div>
                    <div class="status-label">Success Rate</div>
                </div>
                <div class="status-item">
                    <div class="status-value" id="active-workflows">-</div>
                    <div class="status-label">Active Workflows</div>
                </div>
                <div class="status-item">
                    <div class="status-value" id="active-nodes">-</div>
                    <div class="status-label">Active Nodes</div>
                </div>
            </div>
            <div id="langsmith-status" class="langsmith-status">
                Loading LangSmith status...
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
                <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Data</button>
            </div>
        </div>
        
        <div class="section langsmith-section">
            <h2>LangSmith Integration Status</h2>
            <div id="trace-analysis" class="trace-analysis">
                Loading trace analysis...
            </div>
        </div>
        
        <div class="section performance-section">
            <h2>Performance Insights</h2>
            <div id="performance-insights">
                Loading performance insights...
            </div>
        </div>
        
        <div class="section errors-section">
            <h2>Bottleneck Detection</h2>
            <div id="bottlenecks">
                Loading bottleneck analysis...
            </div>
        </div>
        
        <div class="section insights-section">
            <h2>AI Recommendations</h2>
            <div id="recommendations" class="recommendations">
                Loading recommendations...
            </div>
        </div>
        
        <div class="section">
            <h2>Node Performance</h2>
            <div class="node-stats" id="node-performance">
                <!-- Node stats will be populated by JavaScript -->
            </div>
        </div>
        
        <div class="section">
            <h2>Recent Workflows</h2>
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
        
        <div class="last-updated" id="last-updated">
            Loading...
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def enhanced_dashboard():
    """Serve the enhanced dashboard with LangSmith integration."""
    return render_template_string(ENHANCED_DASHBOARD_HTML)

@app.route('/api/enhanced-dashboard')
def api_enhanced_dashboard():
    """API endpoint for enhanced dashboard data with LangSmith integration."""
    try:
        dashboard = get_langsmith_dashboard()
        data = dashboard.get_enhanced_dashboard_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/langsmith-status')
def api_langsmith_status():
    """API endpoint for LangSmith connection status."""
    try:
        dashboard = get_langsmith_dashboard()
        test_results = dashboard.test_dashboard_functionality()
        return jsonify(test_results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/test')
def api_test():
    """Test API endpoint."""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "message": "Enhanced LangSmith Dashboard API is working"
    })

def run_enhanced_dashboard(host='localhost', port=8081, debug=False):
    """Run the enhanced dashboard server."""
    print(f"🎯 Starting Enhanced LangSmith Dashboard on http://{host}:{port}")
    print("Features: LangSmith integration, performance insights, bottleneck detection")
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    run_enhanced_dashboard(debug=True) 