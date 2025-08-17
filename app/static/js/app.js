// Sigmatic - Main JavaScript Application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    loadUploadedFiles();
    
    // Event listeners
    document.getElementById('uploadForm').addEventListener('submit', handleFileUpload);
    document.getElementById('clearSession').addEventListener('click', clearSession);
    
    // File input change event
    document.getElementById('fileInput').addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            console.log('File selected:', file.name);
        }
    });
});

// Handle file upload
async function handleFileUpload(event) {
    event.preventDefault();
    
    const formData = new FormData();
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        showAlert('Please select a file to upload.', 'danger');
        return;
    }
    
    formData.append('file', file);
    
    // Show loading
    showLoading(true);
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            fileInput.value = ''; // Clear the input
            loadUploadedFiles(); // Refresh the file list
        } else {
            showAlert(result.error, 'danger');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showAlert('An error occurred during upload.', 'danger');
    } finally {
        showLoading(false);
    }
}

// Load uploaded files
async function loadUploadedFiles() {
    try {
        const response = await fetch('/files');
        const result = await response.json();
        
        const filesList = document.getElementById('filesList');
        
        if (result.files.length === 0) {
            filesList.innerHTML = '<p class="text-muted">No files uploaded yet.</p>';
            return;
        }
        
        filesList.innerHTML = result.files.map(file => `
            <div class="file-item">
                <h6><i class="fas fa-file-csv me-2"></i>${file.filename}</h6>
                <div class="file-stats">
                    <span class="badge bg-primary me-2">${file.rows} rows</span>
                    <span class="badge bg-secondary me-2">${file.columns} columns</span>
                </div>
                <div class="file-actions">
                    <button class="btn btn-sm btn-outline-primary me-2" onclick="previewFile('${file.filename}')">
                        <i class="fas fa-eye me-1"></i>Preview
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="removeFile('${file.filename}')">
                        <i class="fas fa-trash me-1"></i>Remove
                    </button>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading files:', error);
        showAlert('Error loading uploaded files.', 'danger');
    }
}

// Preview file data
async function previewFile(filename) {
    showLoading(true);
    
    try {
        const response = await fetch(`/preview/${filename}`);
        const result = await response.json();
        
        if (result.success) {
            displayDataPreview(result.data, result.columns, filename);
        } else {
            showAlert(result.error, 'danger');
        }
    } catch (error) {
        console.error('Preview error:', error);
        showAlert('Error previewing file.', 'danger');
    } finally {
        showLoading(false);
    }
}

// Display data preview
function displayDataPreview(data, columns, filename) {
    const previewContainer = document.getElementById('dataPreview');
    
    if (data.length === 0) {
        previewContainer.innerHTML = `
            <div class="text-center text-muted">
                <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
                <p>No data to display</p>
            </div>
        `;
        return;
    }
    
    // Create table header
    let tableHTML = `
        <div class="preview-table">
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            ${columns.map(col => `<th>${col}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
    `;
    
    // Create table rows
    data.forEach(row => {
        tableHTML += '<tr>';
        columns.forEach(col => {
            const value = row[col] !== null && row[col] !== undefined ? row[col] : '';
            tableHTML += `<td>${value}</td>`;
        });
        tableHTML += '</tr>';
    });
    
    tableHTML += `
                    </tbody>
                </table>
            </div>
        </div>
        <div class="mt-3">
            <small class="text-muted">
                Showing first 10 rows of ${filename} (${data.length} total rows)
            </small>
        </div>
    `;
    
    previewContainer.innerHTML = tableHTML;
}

// Remove file
async function removeFile(filename) {
    if (!confirm(`Are you sure you want to remove ${filename}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/remove-file/${filename}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            loadUploadedFiles();
            
            // Clear preview if this was the displayed file
            const previewContainer = document.getElementById('dataPreview');
            if (previewContainer.innerHTML.includes(filename)) {
                previewContainer.innerHTML = `
                    <div class="text-center text-muted">
                        <i class="fas fa-upload fa-3x mb-3"></i>
                        <p>Upload a CSV file to preview your data</p>
                    </div>
                `;
            }
        } else {
            showAlert(result.error, 'danger');
        }
    } catch (error) {
        console.error('Remove error:', error);
        showAlert('Error removing file.', 'danger');
    }
}

// Clear session
async function clearSession() {
    if (!confirm('Are you sure you want to clear all uploaded files? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch('/clear-session', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            loadUploadedFiles();
            
            // Clear preview
            document.getElementById('dataPreview').innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-upload fa-3x mb-3"></i>
                    <p>Upload a CSV file to preview your data</p>
                </div>
            `;
        } else {
            showAlert('Error clearing session.', 'danger');
        }
    } catch (error) {
        console.error('Clear session error:', error);
        showAlert('Error clearing session.', 'danger');
    }
}

// Show alert message
function showAlert(message, type) {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the container
    const container = document.querySelector('.container-fluid');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Show/hide loading modal
function showLoading(show) {
    const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
    if (show) {
        modal.show();
    } else {
        modal.hide();
    }
} 