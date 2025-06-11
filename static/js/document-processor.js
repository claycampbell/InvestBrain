/**
 * Document Processor Frontend Logic
 * Handles document upload, processing, and file management
 */

class DocumentProcessor {
    constructor() {
        this.uploadArea = document.getElementById('upload-area');
        this.fileInput = document.getElementById('file-input');
        this.uploadForm = document.getElementById('upload-form');
        this.progressBar = document.getElementById('upload-progress');
        this.fileList = document.getElementById('file-list');
        
        this.supportedFormats = ['pdf', 'xlsx', 'xls', 'csv'];
        this.maxFileSize = 16 * 1024 * 1024; // 16MB
        
        this.initializeEventListeners();
        this.loadFileList();
    }
    
    initializeEventListeners() {
        // Drag and drop functionality
        if (this.uploadArea) {
            this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
            this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
            this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
            this.uploadArea.addEventListener('click', () => this.fileInput?.click());
        }
        
        // File input change
        if (this.fileInput) {
            this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }
        
        // Form submission
        if (this.uploadForm) {
            this.uploadForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
    }
    
    handleDragOver(event) {
        event.preventDefault();
        this.uploadArea.classList.add('dragover');
    }
    
    handleDragLeave(event) {
        event.preventDefault();
        this.uploadArea.classList.remove('dragover');
    }
    
    handleDrop(event) {
        event.preventDefault();
        this.uploadArea.classList.remove('dragover');
        
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            this.handleFiles(files);
        }
    }
    
    handleFileSelect(event) {
        const files = event.target.files;
        if (files.length > 0) {
            this.handleFiles(files);
        }
    }
    
    handleFiles(files) {
        for (let file of files) {
            if (this.validateFile(file)) {
                this.displayFilePreview(file);
            }
        }
    }
    
    validateFile(file) {
        // Check file size
        if (file.size > this.maxFileSize) {
            this.showError(`File "${file.name}" is too large. Maximum size is 16MB.`);
            return false;
        }
        
        // Check file type
        const extension = file.name.split('.').pop().toLowerCase();
        if (!this.supportedFormats.includes(extension)) {
            this.showError(`File type ".${extension}" is not supported. Supported formats: ${this.supportedFormats.join(', ')}`);
            return false;
        }
        
        return true;
    }
    
    displayFilePreview(file) {
        const previewContainer = document.getElementById('file-preview') || this.createFilePreviewContainer();
        
        const fileItem = document.createElement('div');
        fileItem.className = 'file-preview-item border rounded p-3 mb-2';
        fileItem.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <i class="fas ${this.getFileIcon(file.name)} me-2"></i>
                    <strong>${file.name}</strong>
                    <small class="text-muted ms-2">(${this.formatFileSize(file.size)})</small>
                </div>
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="mt-2">
                <small class="text-muted">Ready to upload</small>
            </div>
        `;
        
        previewContainer.appendChild(fileItem);
    }
    
    createFilePreviewContainer() {
        const container = document.createElement('div');
        container.id = 'file-preview';
        container.className = 'mt-3';
        
        const uploadArea = document.getElementById('upload-area');
        if (uploadArea) {
            uploadArea.parentNode.insertBefore(container, uploadArea.nextSibling);
        }
        
        return container;
    }
    
    getFileIcon(filename) {
        const extension = filename.split('.').pop().toLowerCase();
        switch (extension) {
            case 'pdf':
                return 'fa-file-pdf text-danger';
            case 'xlsx':
            case 'xls':
                return 'fa-file-excel text-success';
            case 'csv':
                return 'fa-file-csv text-info';
            default:
                return 'fa-file text-secondary';
        }
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    async handleFormSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(this.uploadForm);
        const file = this.fileInput.files[0];
        
        if (!file) {
            this.showError('Please select a file to upload.');
            return;
        }
        
        if (!this.validateFile(file)) {
            return;
        }
        
        this.showProgress(true);
        
        try {
            const response = await this.uploadFile(formData);
            
            if (response.ok) {
                this.showSuccess('Document uploaded and processed successfully!');
                this.clearForm();
                this.loadFileList();
                
                // Redirect if successful
                if (response.redirected) {
                    setTimeout(() => {
                        window.location.href = response.url;
                    }, 1500);
                }
            } else {
                const errorText = await response.text();
                this.showError('Upload failed. Please try again.');
                console.error('Upload error:', errorText);
            }
        } catch (error) {
            console.error('Network error:', error);
            this.showError('Network error. Please check your connection and try again.');
        } finally {
            this.showProgress(false);
        }
    }
    
    async uploadFile(formData) {
        return fetch('/documents/upload', {
            method: 'POST',
            body: formData
        });
    }
    
    showProgress(show) {
        if (this.progressBar) {
            this.progressBar.style.display = show ? 'block' : 'none';
            if (show) {
                this.progressBar.innerHTML = `
                    <div class="progress">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" 
                             role="progressbar" style="width: 100%">
                            Processing...
                        </div>
                    </div>
                `;
            }
        }
        
        const submitButton = this.uploadForm?.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = show;
            submitButton.innerHTML = show ? 
                '<span class="loading-spinner"></span> Processing...' : 
                '<i class="fas fa-upload"></i> Upload Document';
        }
    }
    
    async loadFileList() {
        if (!this.fileList) return;
        
        try {
            const response = await fetch('/documents');
            if (response.ok) {
                const html = await response.text();
                // Extract the file list section from the response
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const fileListSection = doc.getElementById('file-list');
                
                if (fileListSection) {
                    this.fileList.innerHTML = fileListSection.innerHTML;
                    this.initializeFileListInteractions();
                }
            }
        } catch (error) {
            console.error('Error loading file list:', error);
        }
    }
    
    initializeFileListInteractions() {
        // Add event listeners for file list interactions
        const fileItems = this.fileList?.querySelectorAll('.file-item');
        fileItems?.forEach(item => {
            const deleteButton = item.querySelector('.delete-file');
            if (deleteButton) {
                deleteButton.addEventListener('click', (e) => this.handleFileDelete(e));
            }
            
            const viewButton = item.querySelector('.view-file');
            if (viewButton) {
                viewButton.addEventListener('click', (e) => this.handleFileView(e));
            }
        });
    }
    
    async handleFileDelete(event) {
        event.preventDefault();
        
        const fileId = event.target.dataset.fileId;
        const fileName = event.target.dataset.fileName;
        
        if (!confirm(`Are you sure you want to delete "${fileName}"?`)) {
            return;
        }
        
        try {
            const response = await fetch(`/documents/${fileId}/delete`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showSuccess('File deleted successfully.');
                this.loadFileList();
            } else {
                this.showError('Failed to delete file.');
            }
        } catch (error) {
            console.error('Error deleting file:', error);
            this.showError('Network error while deleting file.');
        }
    }
    
    handleFileView(event) {
        event.preventDefault();
        
        const fileId = event.target.dataset.fileId;
        const fileName = event.target.dataset.fileName;
        
        // Open file details in modal or new page
        this.showFileDetails(fileId, fileName);
    }
    
    async showFileDetails(fileId, fileName) {
        try {
            const response = await fetch(`/api/documents/${fileId}`);
            if (response.ok) {
                const fileData = await response.json();
                this.displayFileModal(fileData);
            } else {
                this.showError('Failed to load file details.');
            }
        } catch (error) {
            console.error('Error loading file details:', error);
            this.showError('Error loading file details.');
        }
    }
    
    displayFileModal(fileData) {
        const modalHtml = `
            <div class="modal fade" id="fileModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas ${this.getFileIcon(fileData.filename)} me-2"></i>
                                ${fileData.filename}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>File Information</h6>
                                    <ul class="list-unstyled">
                                        <li><strong>Type:</strong> ${fileData.file_type}</li>
                                        <li><strong>Size:</strong> ${this.formatFileSize(fileData.file_size)}</li>
                                        <li><strong>Uploaded:</strong> ${new Date(fileData.created_at).toLocaleString()}</li>
                                    </ul>
                                </div>
                                <div class="col-md-6">
                                    <h6>Processing Status</h6>
                                    <div class="alert alert-success">
                                        <i class="fas fa-check-circle"></i> Successfully processed
                                    </div>
                                </div>
                            </div>
                            
                            ${this.generateProcessedDataPreview(fileData.processed_data)}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal
        const existingModal = document.getElementById('fileModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add new modal
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('fileModal'));
        modal.show();
    }
    
    generateProcessedDataPreview(processedData) {
        if (!processedData) {
            return '<p class="text-muted">No processed data available</p>';
        }
        
        let preview = '<h6>Processed Data Preview</h6>';
        
        if (processedData.summary) {
            preview += `
                <div class="alert alert-info">
                    <h6>Summary</h6>
                    <p class="mb-0">${JSON.stringify(processedData.summary, null, 2)}</p>
                </div>
            `;
        }
        
        if (processedData.key_metrics) {
            preview += `
                <div class="mt-3">
                    <h6>Key Metrics</h6>
                    <div class="row">
                        ${this.generateMetricsPreview(processedData.key_metrics)}
                    </div>
                </div>
            `;
        }
        
        if (processedData.tables && processedData.tables.length > 0) {
            preview += `
                <div class="mt-3">
                    <h6>Tables Found</h6>
                    <p>Found ${processedData.tables.length} table(s) in the document</p>
                </div>
            `;
        }
        
        return preview;
    }
    
    generateMetricsPreview(metrics) {
        if (!metrics || Object.keys(metrics).length === 0) {
            return '<div class="col-12"><p class="text-muted">No metrics extracted</p></div>';
        }
        
        return Object.entries(metrics).slice(0, 6).map(([key, value]) => `
            <div class="col-md-4 mb-2">
                <div class="bg-light p-2 rounded">
                    <small class="text-muted">${key}</small><br>
                    <strong>${typeof value === 'number' ? value.toLocaleString() : value}</strong>
                </div>
            </div>
        `).join('');
    }
    
    clearForm() {
        if (this.uploadForm) {
            this.uploadForm.reset();
        }
        
        const filePreview = document.getElementById('file-preview');
        if (filePreview) {
            filePreview.innerHTML = '';
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
        
        const uploadArea = document.getElementById('upload-area');
        if (uploadArea) {
            uploadArea.parentNode.insertBefore(container, uploadArea);
        }
        
        return container;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DocumentProcessor();
});
