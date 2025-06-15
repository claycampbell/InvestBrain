/**
 * Standalone Simulation System - No External Dependencies
 */

class ThesisSimulation {
    constructor(thesisId) {
        this.thesisId = thesisId;
        this.isRunning = false;
        this.results = null;
    }

    async runSimulation(params) {
        if (this.isRunning) {
            console.log('Simulation already running');
            return;
        }

        this.isRunning = true;
        this.showProgress();

        try {
            const response = await fetch(`/api/thesis/${this.thesisId}/simulate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    time_horizon: params.timeHorizon || 1,
                    scenario: params.scenario || 'base',
                    volatility: params.volatility || 'medium',
                    include_events: true,
                    simulation_type: 'forecast'
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            this.results = data;
            this.displayResults();

        } catch (error) {
            console.error('Simulation error:', error);
            this.showError('Simulation failed. Please try again.');
        } finally {
            this.isRunning = false;
            this.hideProgress();
        }
    }

    showProgress() {
        const modal = document.getElementById('simulationModal');
        if (modal) {
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
            
            // Animate progress
            const progressBar = modal.querySelector('.progress-bar');
            if (progressBar) {
                let progress = 0;
                const interval = setInterval(() => {
                    progress += Math.random() * 15;
                    if (progress > 90) progress = 90;
                    progressBar.style.width = progress + '%';
                    
                    if (!this.isRunning) {
                        progressBar.style.width = '100%';
                        clearInterval(interval);
                        setTimeout(() => bootstrapModal.hide(), 500);
                    }
                }, 300);
            }
        }
    }

    hideProgress() {
        // Progress is hidden automatically in showProgress
    }

    displayResults() {
        if (!this.results) return;

        const container = document.getElementById('simulationResults');
        if (!container) return;

        // Generate safe HTML content
        const html = this.generateResultsHTML();
        container.innerHTML = html;
        container.style.display = 'block';
        container.scrollIntoView({ behavior: 'smooth' });

        // Render chart if data exists
        this.renderChart();
    }

    generateResultsHTML() {
        const events = this.results.events || [];
        const scenario = this.results.scenario_analysis || {};

        return `
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0">Simulation Results</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Generated Events (${events.length})</h6>
                            <div class="event-list">
                                ${events.map((event, index) => `
                                    <div class="event-item mb-2 p-2 border rounded">
                                        <strong>Event ${index + 1}:</strong> ${this.safeText(event.title)}<br>
                                        <small class="text-muted">${this.safeText(event.description)}</small>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                        <div class="col-md-6">
                            <h6>Scenario Analysis</h6>
                            <div class="scenario-analysis">
                                <div class="mb-2">
                                    <strong>Bull Case:</strong> ${this.safeText(scenario.bull_case?.description || 'Optimistic scenario')}
                                </div>
                                <div class="mb-2">
                                    <strong>Base Case:</strong> ${this.safeText(scenario.base_case?.description || 'Expected scenario')}
                                </div>
                                <div class="mb-2">
                                    <strong>Bear Case:</strong> ${this.safeText(scenario.bear_case?.description || 'Pessimistic scenario')}
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="mt-3">
                        <div id="performanceChart"></div>
                    </div>
                </div>
            </div>
        `;
    }

    safeText(text) {
        if (!text) return 'N/A';
        return String(text).substring(0, 200) + (String(text).length > 200 ? '...' : '');
    }

    renderChart() {
        const chartData = this.results.chart_data;
        const events = this.results.events || [];
        
        if (!chartData || !chartData.performance_data) {
            document.getElementById('performanceChart').innerHTML = 
                '<div class="text-center text-muted">Chart data unavailable</div>';
            return;
        }

        try {
            const options = {
                chart: {
                    type: 'line',
                    height: 400,
                    toolbar: { show: false }
                },
                series: [
                    {
                        name: 'Market Performance',
                        data: chartData.performance_data.market_performance || []
                    },
                    {
                        name: 'Thesis Performance',
                        data: chartData.performance_data.thesis_performance || []
                    }
                ],
                xaxis: {
                    categories: chartData.timeline || [],
                    title: { text: 'Timeline' }
                },
                yaxis: {
                    title: { text: 'Performance (%)' }
                },
                annotations: {
                    points: events.map((event, index) => ({
                        x: index * 2,
                        y: 100,
                        marker: {
                            size: 6,
                            fillColor: '#28a745',
                            strokeColor: '#fff'
                        },
                        label: {
                            text: `Event ${index + 1}`,
                            style: { background: '#28a745', color: '#fff' }
                        }
                    }))
                },
                stroke: { width: 2 },
                colors: ['#6c757d', '#007bff']
            };

            const chart = new ApexCharts(document.getElementById('performanceChart'), options);
            chart.render();

        } catch (error) {
            console.error('Chart rendering failed:', error);
            document.getElementById('performanceChart').innerHTML = 
                '<div class="text-center text-warning">Chart rendering error</div>';
        }
    }

    showError(message) {
        const container = document.getElementById('simulationResults');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Error:</strong> ${message}
                </div>
            `;
            container.style.display = 'block';
        }
    }
}

// Initialize simulation when page loads
document.addEventListener('DOMContentLoaded', function() {
    const thesisId = window.location.pathname.split('/').pop();
    const simulation = new ThesisSimulation(thesisId);

    // Forecast simulation form
    const forecastForm = document.getElementById('forecastForm');
    if (forecastForm) {
        forecastForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const timeHorizon = document.getElementById('timeHorizon')?.value || 1;
            const scenarioType = document.getElementById('scenarioType')?.value || 'base';
            
            simulation.runSimulation({
                timeHorizon: parseInt(timeHorizon),
                scenario: scenarioType,
                volatility: 'medium'
            });
        });
    }

    // Event simulation form
    const eventForm = document.getElementById('eventForm');
    if (eventForm) {
        eventForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            simulation.runSimulation({
                timeHorizon: 1,
                scenario: 'base',
                volatility: 'medium'
            });
        });
    }
});