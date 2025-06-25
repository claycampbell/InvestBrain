// Eagle API Integration
class EagleAPIHandler {
    constructor() {
        this.resultContainer = document.getElementById('eagle-api-results');
    }

    async fetchMetrics(companyName, thesisText = '', metricsToTrack = []) {
        try {
            this.showLoading();
            const response = await fetch('/api/eagle-metrics', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    company_name: companyName,
                    thesis_text: thesisText,
                    metrics_to_track: metricsToTrack
                })
            });
            const data = await response.json();

            if (data.success) {
                this.displayResults(data);
            } else {
                this.showError(data.error || 'Failed to fetch Eagle API metrics');
            }
        } catch (error) {
            console.error('Eagle API error:', error);
            this.showError('Failed to fetch Eagle API metrics');
        }
    }

    async fetchMetricsFromThesis(thesisText, metricsToTrack = []) {
        try {
            this.showLoading();
            const response = await fetch('/api/eagle-metrics', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    thesis_text: thesisText,
                    metrics_to_track: metricsToTrack
                })
            });
            const data = await response.json();

            if (data.success) {
                this.displayResults(data);
            } else {
                this.showError(data.error || 'Failed to fetch Eagle API metrics');
            }
        } catch (error) {
            console.error('Eagle API error:', error);
            this.showError('Failed to fetch Eagle API metrics');
        }
    }

    showLoading() {
        if (this.resultContainer) {
            this.resultContainer.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-success" role="status">
                        <span class="visually-hidden">Loading Eagle API data...</span>
                    </div>
                    <p class="text-muted mt-2">Fetching real-time financial metrics...</p>
                </div>
            `;
        }
    }

    displayResults(eagleData) {
        if (!this.resultContainer) return;

        const companyName = eagleData.company_name || 'Unknown Company';
        const sedolId = eagleData.sedol_id || 'N/A';
        const source = eagleData.source || 'Eagle API';
        const isMockData = eagleData.mock_data || false;

        let html = `
            <div class="card mb-3">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h6 class="mb-0">
                        <i class="fas fa-chart-line text-success me-2"></i>
                        Eagle API Results: ${companyName}
                    </h6>
                    <div>
                        <span class="badge bg-success me-2">Eagle API</span>
                        <span class="badge bg-warning">SEDOL: ${sedolId}</span>
                        ${isMockData ? '<span class="badge bg-info ms-2">Mock Data</span>' : ''}
                    </div>
                </div>
                <div class="card-body">
                    <div class="row g-3">
        `;

        // Extract financial metrics
        const financialMetrics = eagleData.data?.financialMetrics || [];
        if (financialMetrics.length > 0) {
            const metrics = financialMetrics[0].metrics || [];
            
            for (const metric of metrics) {
                const formattedValue = this.formatMetricValue(metric.value);
                const trend = this.determineTrend(metric.value);
                const description = metric.description || metric.name;

                html += `
                    <div class="col-md-6">
                        <div class="card h-100 border-light">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-center">
                                    <h6 class="card-title mb-0 text-muted">
                                        ${this.formatMetricName(description)}
                                    </h6>
                                    <span class="badge bg-${trend.color}">${trend.icon}</span>
                                </div>
                                <p class="display-6 mb-0 mt-2">${formattedValue}</p>
                                <small class="text-muted">
                                    ${metric.unit || ''} | ${metric.period || 'LTM'}
                                </small>
                            </div>
                        </div>
                    </div>
                `;
            }
        } else {
            html += `
                <div class="col-12">
                    <div class="alert alert-info mb-0">
                        <i class="fas fa-info-circle me-2"></i>
                        No financial metrics available for ${companyName}
                    </div>
                </div>
            `;
        }

        html += `
                    </div>
                </div>
            </div>
        `;

        this.resultContainer.innerHTML = html;
    }

    showError(message) {
        if (this.resultContainer) {
            this.resultContainer.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    ${message}
                </div>
            `;
        }
    }

    formatMetricName(name) {
        return name
            .replace(/_/g, ' ')
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    formatMetricValue(value) {
        if (typeof value === 'number') {
            if (Math.abs(value) >= 1000000000) {
                return `${(value / 1000000000).toFixed(2)}B`;
            } else if (Math.abs(value) >= 1000000) {
                return `${(value / 1000000).toFixed(2)}M`;
            } else if (Math.abs(value) >= 1000) {
                return `${(value / 1000).toFixed(2)}K`;
            }

            // Check if it's a percentage metric
            if (value < 100 && value > -100) {
                return `${value.toFixed(2)}%`;
            }

            return value.toFixed(2);
        }
        return value;
    }

    determineTrend(value) {
        if (typeof value !== 'number') {
            return { color: 'secondary', icon: '—' };
        }

        if (value > 0) {
            return { color: 'success', icon: '↑' };
        } else if (value < 0) {
            return { color: 'danger', icon: '↓' };
        }
        return { color: 'secondary', icon: '—' };
    }
}

// Initialize Eagle API handler
document.addEventListener('DOMContentLoaded', function() {
    const eagleAPI = new EagleAPIHandler();

    // Hook into thesis analysis results
    window.eagleAPI = eagleAPI;
    
    // Function to be called after analysis completes
    window.loadEagleAPIResults = function(thesisText, metricsToTrack = []) {
        if (thesisText) {
            eagleAPI.fetchMetricsFromThesis(thesisText, metricsToTrack);
        }
    };

    // Auto-load Eagle API results if thesis text is available
    const thesisTextArea = document.querySelector('textarea[name="thesis_text"]');
    if (thesisTextArea && thesisTextArea.value.trim()) {
        window.loadEagleAPIResults(thesisTextArea.value.trim());
    }
});