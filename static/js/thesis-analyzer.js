/**
 * Thesis Analyzer Frontend Logic
 * Handles thesis analysis form submission and results display
 */

class ThesisAnalyzer {
    constructor() {
        this.analysisForm = document.getElementById('thesis-form');
        this.resultsContainer = document.getElementById('analysis-results');
        this.loadingSpinner = document.getElementById('loading-spinner');
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        if (this.analysisForm) {
            this.analysisForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
        
        // Auto-save functionality
        const thesisTextarea = document.getElementById('thesis_text');
        if (thesisTextarea) {
            thesisTextarea.addEventListener('input', () => this.autoSave());
        }
        
        // Real-time word count
        if (thesisTextarea) {
            thesisTextarea.addEventListener('input', () => this.updateWordCount());
        }
    }
    
    handleFormSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(this.analysisForm);
        const title = formData.get('title');
        const thesisText = formData.get('thesis_text');
        
        if (!title || !thesisText) {
            this.showError('Please provide both a title and thesis text.');
            return;
        }
        
        this.showLoading(true);
        this.submitAnalysis(formData);
    }
    
    async submitAnalysis(formData) {
        try {
            const response = await fetch('/thesis/new', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                // Check if we're being redirected to view the thesis
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    // Handle success without redirect
                    this.showSuccess('Thesis analysis completed successfully!');
                    this.clearForm();
                }
            } else {
                try {
                    const errorData = await response.json();
                    
                    // Handle specific error types
                    if (errorData.error_type === 'network_timeout') {
                        this.showError('Analysis service temporarily unavailable due to network issues. Please try again in a moment.');
                        if (errorData.retry_suggested) {
                            setTimeout(() => {
                                this.showRetryButton();
                            }, 3000);
                        }
                    } else if (errorData.error_type === 'content_filter') {
                        this.showError('Content was filtered by AI safety policies. Please revise your thesis text.');
                    } else {
                        this.showError(errorData.error || 'Analysis failed. Please try again.');
                    }
                } catch (parseError) {
                    // Fallback for non-JSON error responses
                    const errorText = await response.text();
                    this.showError('Analysis failed. Please try again.');
                    console.error('Analysis error:', errorText);
                }
            }
        } catch (error) {
            console.error('Network error:', error);
            this.showError('Network error. Please check your connection and try again.');
        } finally {
            this.showLoading(false);
        }
    }
    
    showRetryButton() {
        const alertContainer = document.getElementById('alert-container');
        if (alertContainer) {
            const retryButton = document.createElement('button');
            retryButton.className = 'btn btn-outline-primary btn-sm mt-2';
            retryButton.innerHTML = '<i class="fas fa-redo"></i> Retry Analysis';
            retryButton.onclick = () => {
                alertContainer.innerHTML = '';
                const formData = new FormData(this.analysisForm);
                this.showLoading(true);
                this.submitAnalysis(formData);
            };
            alertContainer.querySelector('.alert').appendChild(retryButton);
        }
    }
    
    showLoading(show) {
        if (this.loadingSpinner) {
            this.loadingSpinner.style.display = show ? 'block' : 'none';
        }
        
        const submitButton = this.analysisForm?.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = show;
            submitButton.innerHTML = show ? 
                '<span class="loading-spinner"></span> Analyzing...' : 
                'Analyze Thesis';
        }
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
        container.className = 'mb-3';
        
        const form = document.getElementById('thesis-form');
        if (form) {
            form.parentNode.insertBefore(container, form);
        }
        
        return container;
    }
    
    updateWordCount() {
        const textarea = document.getElementById('thesis_text');
        const counter = document.getElementById('word-count');
        
        if (textarea && counter) {
            const words = textarea.value.trim().split(/\s+/).filter(word => word.length > 0);
            counter.textContent = `${words.length} words`;
            
            // Color coding based on length
            if (words.length < 50) {
                counter.className = 'text-warning small';
            } else if (words.length > 500) {
                counter.className = 'text-info small';
            } else {
                counter.className = 'text-muted small';
            }
        }
    }
    
    autoSave() {
        const textarea = document.getElementById('thesis_text');
        const title = document.getElementById('title');
        
        if (textarea && title) {
            const data = {
                title: title.value,
                thesis_text: textarea.value,
                timestamp: new Date().toISOString()
            };
            
            // Save to localStorage
            localStorage.setItem('thesis_draft', JSON.stringify(data));
            
            // Show save indicator
            this.showSaveIndicator();
        }
    }
    
    showSaveIndicator() {
        let indicator = document.getElementById('save-indicator');
        if (!indicator) {
            indicator = document.createElement('small');
            indicator.id = 'save-indicator';
            indicator.className = 'text-muted ms-2';
            
            const textarea = document.getElementById('thesis_text');
            if (textarea) {
                textarea.parentNode.appendChild(indicator);
            }
        }
        
        indicator.textContent = 'Draft saved';
        indicator.style.opacity = '1';
        
        setTimeout(() => {
            indicator.style.opacity = '0.5';
        }, 2000);
    }
    
    loadDraft() {
        const draft = localStorage.getItem('thesis_draft');
        if (draft) {
            try {
                const data = JSON.parse(draft);
                const titleInput = document.getElementById('title');
                const textareaInput = document.getElementById('thesis_text');
                
                if (titleInput && !titleInput.value) {
                    titleInput.value = data.title || '';
                }
                
                if (textareaInput && !textareaInput.value) {
                    textareaInput.value = data.thesis_text || '';
                    this.updateWordCount();
                }
                
                // Show restoration indicator
                if (data.title || data.thesis_text) {
                    this.showAlert('Draft restored from previous session', 'info');
                }
            } catch (error) {
                console.error('Error loading draft:', error);
            }
        }
    }
    
    clearForm() {
        if (this.analysisForm) {
            this.analysisForm.reset();
            this.updateWordCount();
            localStorage.removeItem('thesis_draft');
        }
    }
    
    // Method to display analysis results if we're on the view page
    displayAnalysisResults(analysisData) {
        if (!this.resultsContainer || !analysisData) return;
        
        const resultsHtml = this.generateResultsHtml(analysisData);
        this.resultsContainer.innerHTML = resultsHtml;
        
        // Initialize interactive elements
        this.initializeResultsInteractions();
    }
    
    generateResultsHtml(data) {
        return `
            <div class="row">
                <div class="col-md-6">
                    <div class="analysis-section">
                        <h4><i class="fas fa-bullseye"></i> Core Claim</h4>
                        <p class="lead">${data.core_claim || 'Not identified'}</p>
                    </div>
                    
                    <div class="analysis-section">
                        <h4><i class="fas fa-link"></i> Causal Chain</h4>
                        <div class="causal-chain">
                            ${this.generateCausalChainHtml(data.causal_chain)}
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="analysis-section">
                        <h4><i class="fas fa-brain"></i> Mental Model</h4>
                        <span class="badge bg-primary">${data.mental_model || 'Unknown'}</span>
                    </div>
                    
                    <div class="analysis-section">
                        <h4><i class="fas fa-exclamation-triangle"></i> Key Assumptions</h4>
                        <ul class="list-unstyled">
                            ${this.generateAssumptionsHtml(data.assumptions)}
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="mt-4">
                <div class="analysis-section">
                    <h4><i class="fas fa-chart-line"></i> Metrics to Track</h4>
                    <div class="row">
                        ${this.generateMetricsHtml(data.metrics_to_track)}
                    </div>
                </div>
            </div>
            
            <div class="mt-4">
                <div class="analysis-section">
                    <h4><i class="fas fa-shield-alt"></i> Counter-Thesis</h4>
                    <div class="alert alert-warning">
                        ${this.generateCounterThesisHtml(data.counter_thesis)}
                    </div>
                </div>
            </div>
        `;
    }
    
    generateCausalChainHtml(causalChain) {
        if (!Array.isArray(causalChain) || causalChain.length === 0) {
            return '<p class="text-muted">No causal chain identified</p>';
        }
        
        return causalChain.map(step => `
            <div class="causal-step">
                <strong>${step}</strong>
            </div>
        `).join('');
    }
    
    generateAssumptionsHtml(assumptions) {
        if (!Array.isArray(assumptions) || assumptions.length === 0) {
            return '<li class="text-muted">No assumptions identified</li>';
        }
        
        return assumptions.map(assumption => `
            <li><i class="fas fa-arrow-right text-warning me-2"></i>${assumption}</li>
        `).join('');
    }
    
    generateMetricsHtml(metrics) {
        if (!Array.isArray(metrics) || metrics.length === 0) {
            return '<div class="col-12"><p class="text-muted">No metrics identified</p></div>';
        }
        
        return metrics.map(metric => `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="metric-card">
                    <h6 class="fw-bold">${metric.name || 'Unknown Metric'}</h6>
                    <p class="mb-1"><small class="text-muted">${metric.description || ''}</small></p>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="badge bg-secondary">${metric.type || 'unknown'}</span>
                        <small class="text-muted">${metric.frequency || 'unknown'}</small>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    generateCounterThesisHtml(counterThesis) {
        if (!Array.isArray(counterThesis) || counterThesis.length === 0) {
            return '<p>No counter-arguments identified</p>';
        }
        
        return `
            <ul class="mb-0">
                ${counterThesis.map(point => `<li>${point}</li>`).join('')}
            </ul>
        `;
    }
    
    initializeResultsInteractions() {
        // Add any interactive elements for the results
        const metricCards = document.querySelectorAll('.metric-card');
        metricCards.forEach(card => {
            card.addEventListener('click', () => {
                card.classList.toggle('border-primary');
            });
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const analyzer = new ThesisAnalyzer();
    
    // Load draft if we're on the new thesis page
    if (document.getElementById('thesis-form')) {
        analyzer.loadDraft();
    }
    
    // If we're on a view page and have analysis data, display it
    const analysisDataElement = document.getElementById('analysis-data');
    if (analysisDataElement) {
        try {
            const analysisData = JSON.parse(analysisDataElement.textContent);
            analyzer.displayAnalysisResults(analysisData);
        } catch (error) {
            console.error('Error parsing analysis data:', error);
        }
    }
});
