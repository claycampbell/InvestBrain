/**
 * Signal Renderer - Handles real-time signal monitoring and visualization
 * for the Investment Thesis Intelligence System
 */

class SignalRenderer {
    constructor() {
        this.signalContainer = document.getElementById('signals-container');
        this.chartContainer = document.getElementById('signal-charts');
        this.refreshInterval = 30000; // 30 seconds
        this.charts = new Map();
        
        this.initializeRenderer();
        this.startAutoRefresh();
    }
    
    initializeRenderer() {
        // Initialize Chart.js defaults for dark theme
        if (typeof Chart !== 'undefined') {
            Chart.defaults.color = '#ffffff';
            Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
            Chart.defaults.backgroundColor = 'rgba(255, 255, 255, 0.05)';
        }
        
        this.loadSignals();
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Manual refresh button
        const refreshButton = document.getElementById('refresh-signals');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => this.refreshSignals());
        }
        
        // Signal threshold update buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('update-threshold')) {
                this.handleThresholdUpdate(e);
            }
            if (e.target.classList.contains('toggle-signal')) {
                this.handleSignalToggle(e);
            }
        });
    }
    
    async loadSignals() {
        try {
            const response = await fetch('/api/signals/status');
            if (response.ok) {
                const signals = await response.json();
                this.renderSignals(signals);
            } else {
                this.showError('Failed to load signals');
            }
        } catch (error) {
            console.error('Error loading signals:', error);
            this.showError('Error loading signals: ' + error.message);
        }
    }
    
    async refreshSignals() {
        const refreshButton = document.getElementById('refresh-signals');
        if (refreshButton) {
            refreshButton.disabled = true;
            refreshButton.innerHTML = '<span class="loading-spinner"></span> Refreshing...';
        }
        
        try {
            // Trigger signal check
            const checkResponse = await fetch('/api/signals/check', {
                method: 'POST'
            });
            
            if (checkResponse.ok) {
                // Reload signals after check
                await this.loadSignals();
                this.showSuccess('Signals refreshed successfully');
            } else {
                this.showError('Failed to refresh signals');
            }
        } catch (error) {
            console.error('Error refreshing signals:', error);
            this.showError('Error refreshing signals: ' + error.message);
        } finally {
            if (refreshButton) {
                refreshButton.disabled = false;
                refreshButton.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
            }
        }
    }
    
    renderSignals(signals) {
        if (!this.signalContainer) return;
        
        if (!signals || signals.length === 0) {
            this.signalContainer.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i>
                    No active signals found. Create a thesis analysis to start monitoring signals.
                </div>
            `;
            return;
        }
        
        const signalsHtml = signals.map(signal => this.renderSignalCard(signal)).join('');
        this.signalContainer.innerHTML = signalsHtml;
        
        // Render charts for signals with historical data
        this.renderSignalCharts(signals);
    }
    
    renderSignalCard(signal) {
        const statusClass = this.getStatusClass(signal.status);
        const statusIcon = this.getStatusIcon(signal.status);
        const lastChecked = signal.last_checked ? 
            new Date(signal.last_checked).toLocaleString() : 'Never';
        
        return `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card signal-card h-100" data-signal-id="${signal.id}">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">
                            <span class="signal-status ${signal.status}"></span>
                            ${signal.signal_name}
                        </h6>
                        <span class="badge ${statusClass}">
                            <i class="fas ${statusIcon}"></i> ${signal.status}
                        </span>
                    </div>
                    <div class="card-body">
                        <div class="row mb-2">
                            <div class="col-6">
                                <small class="text-muted">Current Value</small>
                                <div class="metric-value">
                                    ${this.formatValue(signal.current_value, signal.signal_type)}
                                </div>
                            </div>
                            <div class="col-6">
                                <small class="text-muted">Threshold</small>
                                <div class="threshold-value">
                                    ${this.formatThreshold(signal.threshold_value, signal.threshold_type)}
                                </div>
                            </div>
                        </div>
                        
                        <div class="signal-type-badge mb-2">
                            <span class="badge bg-secondary">${signal.signal_type}</span>
                        </div>
                        
                        <div class="signal-actions">
                            <button class="btn btn-sm btn-outline-primary update-threshold" 
                                    data-signal-id="${signal.id}">
                                <i class="fas fa-edit"></i> Update
                            </button>
                            <button class="btn btn-sm btn-outline-secondary toggle-signal" 
                                    data-signal-id="${signal.id}" 
                                    data-action="${signal.status === 'active' ? 'deactivate' : 'activate'}">
                                <i class="fas ${signal.status === 'active' ? 'fa-pause' : 'fa-play'}"></i>
                                ${signal.status === 'active' ? 'Pause' : 'Resume'}
                            </button>
                        </div>
                    </div>
                    <div class="card-footer">
                        <small class="text-muted">
                            <i class="fas fa-clock"></i> Last checked: ${lastChecked}
                        </small>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderSignalCharts(signals) {
        if (!this.chartContainer) return;
        
        // Clear existing charts
        this.charts.forEach(chart => chart.destroy());
        this.charts.clear();
        
        const activeSignals = signals.filter(signal => 
            signal.status === 'active' && signal.current_value !== null
        );
        
        if (activeSignals.length === 0) {
            this.chartContainer.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-chart-line"></i>
                    No active signals with data to display
                </div>
            `;
            return;
        }
        
        // Create overview chart
        this.renderOverviewChart(activeSignals);
        
        // Create individual signal trend charts
        activeSignals.forEach(signal => {
            this.renderSignalTrendChart(signal);
        });
    }
    
    renderOverviewChart(signals) {
        const chartContainer = document.createElement('div');
        chartContainer.className = 'col-12 mb-4';
        chartContainer.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">
                        <i class="fas fa-chart-bar"></i> Signal Overview
                    </h5>
                </div>
                <div class="card-body">
                    <div class="chart-container">
                        <canvas id="overview-chart"></canvas>
                    </div>
                </div>
            </div>
        `;
        
        this.chartContainer.appendChild(chartContainer);
        
        const ctx = document.getElementById('overview-chart');
        if (ctx && typeof Chart !== 'undefined') {
            const chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: signals.map(s => s.signal_name),
                    datasets: [{
                        label: 'Current Values',
                        data: signals.map(s => s.current_value || 0),
                        backgroundColor: signals.map(s => this.getSignalColor(s.status)),
                        borderColor: signals.map(s => this.getSignalColor(s.status)),
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: (context) => {
                                    const signal = signals[context.dataIndex];
                                    return [
                                        `Current: ${this.formatValue(context.parsed.y, signal.signal_type)}`,
                                        `Threshold: ${this.formatThreshold(signal.threshold_value, signal.threshold_type)}`,
                                        `Status: ${signal.status}`
                                    ];
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
            
            this.charts.set('overview', chart);
        }
    }
    
    renderSignalTrendChart(signal) {
        // This would typically show historical data
        // For now, we'll create a placeholder that shows the current value vs threshold
        const chartContainer = document.createElement('div');
        chartContainer.className = 'col-md-6 mb-4';
        chartContainer.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h6 class="mb-0">${signal.signal_name} Trend</h6>
                </div>
                <div class="card-body">
                    <div class="chart-container" style="height: 200px;">
                        <canvas id="trend-chart-${signal.id}"></canvas>
                    </div>
                </div>
            </div>
        `;
        
        this.chartContainer.appendChild(chartContainer);
        
        const ctx = document.getElementById(`trend-chart-${signal.id}`);
        if (ctx && typeof Chart !== 'undefined') {
            // Generate sample trend data (in real implementation, this would come from historical data)
            const trendData = this.generateTrendData(signal);
            
            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: trendData.labels,
                    datasets: [{
                        label: 'Value',
                        data: trendData.values,
                        borderColor: this.getSignalColor(signal.status),
                        backgroundColor: this.getSignalColor(signal.status, 0.1),
                        tension: 0.1,
                        fill: true
                    }, {
                        label: 'Threshold',
                        data: trendData.thresholds,
                        borderColor: '#ffc107',
                        backgroundColor: 'transparent',
                        borderDash: [5, 5],
                        pointRadius: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
            
            this.charts.set(`trend-${signal.id}`, chart);
        }
    }
    
    generateTrendData(signal) {
        // Generate mock trend data for visualization
        // In real implementation, this would fetch historical data
        const now = new Date();
        const labels = [];
        const values = [];
        const thresholds = [];
        
        for (let i = 23; i >= 0; i--) {
            const time = new Date(now.getTime() - i * 60 * 60 * 1000);
            labels.push(time.getHours().toString().padStart(2, '0') + ':00');
            
            // Generate values around the current value with some variation
            const baseValue = signal.current_value || 100;
            const variation = baseValue * 0.1 * (Math.random() - 0.5);
            values.push(Math.max(0, baseValue + variation));
            thresholds.push(signal.threshold_value);
        }
        
        return { labels, values, thresholds };
    }
    
    getStatusClass(status) {
        switch (status) {
            case 'active': return 'bg-success';
            case 'triggered': return 'bg-danger';
            case 'inactive': return 'bg-secondary';
            default: return 'bg-secondary';
        }
    }
    
    getStatusIcon(status) {
        switch (status) {
            case 'active': return 'fa-play';
            case 'triggered': return 'fa-exclamation-triangle';
            case 'inactive': return 'fa-pause';
            default: return 'fa-question';
        }
    }
    
    getSignalColor(status, alpha = 1) {
        const colors = {
            'active': `rgba(40, 167, 69, ${alpha})`,
            'triggered': `rgba(220, 53, 69, ${alpha})`,
            'inactive': `rgba(108, 117, 125, ${alpha})`
        };
        return colors[status] || colors.inactive;
    }
    
    formatValue(value, type) {
        if (value === null || value === undefined) return 'N/A';
        
        switch (type) {
            case 'price':
                return '$' + parseFloat(value).toFixed(2);
            case 'volume':
                return parseInt(value).toLocaleString();
            case 'sentiment':
                return parseFloat(value).toFixed(1);
            default:
                return parseFloat(value).toFixed(2);
        }
    }
    
    formatThreshold(value, type) {
        if (value === null || value === undefined) return 'N/A';
        
        switch (type) {
            case 'change_percent':
                return parseFloat(value).toFixed(1) + '%';
            case 'above':
                return '> ' + parseFloat(value).toFixed(2);
            case 'below':
                return '< ' + parseFloat(value).toFixed(2);
            default:
                return parseFloat(value).toFixed(2);
        }
    }
    
    async handleThresholdUpdate(event) {
        const signalId = event.target.dataset.signalId;
        const currentThreshold = event.target.closest('.card').querySelector('.threshold-value').textContent;
        
        const newThreshold = prompt('Enter new threshold value:', currentThreshold.replace(/[^\d.-]/g, ''));
        if (newThreshold === null || newThreshold === '') return;
        
        const threshold = parseFloat(newThreshold);
        if (isNaN(threshold)) {
            this.showError('Invalid threshold value');
            return;
        }
        
        try {
            const response = await fetch(`/api/signals/${signalId}/threshold`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ threshold: threshold })
            });
            
            if (response.ok) {
                this.showSuccess('Threshold updated successfully');
                this.loadSignals(); // Refresh the display
            } else {
                this.showError('Failed to update threshold');
            }
        } catch (error) {
            console.error('Error updating threshold:', error);
            this.showError('Error updating threshold: ' + error.message);
        }
    }
    
    async handleSignalToggle(event) {
        const signalId = event.target.dataset.signalId;
        const action = event.target.dataset.action;
        
        try {
            const response = await fetch(`/api/signals/${signalId}/${action}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showSuccess(`Signal ${action}d successfully`);
                this.loadSignals(); // Refresh the display
            } else {
                this.showError(`Failed to ${action} signal`);
            }
        } catch (error) {
            console.error(`Error ${action}ing signal:`, error);
            this.showError(`Error ${action}ing signal: ` + error.message);
        }
    }
    
    startAutoRefresh() {
        setInterval(() => {
            this.loadSignals();
        }, this.refreshInterval);
    }
    
    showError(message) {
        this.showAlert(message, 'danger');
    }
    
    showSuccess(message) {
        this.showAlert(message, 'success');
    }
    
    showAlert(message, type) {
        const alertContainer = document.getElementById('alert-container') || this.createAlertContainer();
        
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="fas ${type === 'danger' ? 'fa-exclamation-circle' : 'fa-check-circle'}"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        alertContainer.innerHTML = alertHtml;
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = alertContainer.querySelector('.alert');
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }
    
    createAlertContainer() {
        const container = document.createElement('div');
        container.id = 'alert-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1050';
        
        document.body.appendChild(container);
        return container;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SignalRenderer();
});
