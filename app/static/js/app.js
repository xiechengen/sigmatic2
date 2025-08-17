// Sigmatic - Main JavaScript Application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    loadUploadedFiles();
    updateSessionStatus();
    
    // Event listeners
    document.getElementById('uploadForm').addEventListener('submit', handleFileUpload);
    document.getElementById('clearSession').addEventListener('click', clearSession);
    document.getElementById('queryForm').addEventListener('submit', handleQuery);
    document.getElementById('clearDashboard').addEventListener('click', clearDashboard);
    
    // Load dashboard on page load
    loadDashboard();
    
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
        
        // Update session status after loading files
        updateSessionStatus();
        
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
            updateSessionStatus();
            
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



// Add chat message
function addChatMessage(type, content, isTemporary = false) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    const messageId = isTemporary ? 'temp-' + Date.now() : null;
    
    if (messageId) {
        messageDiv.id = messageId;
    }
    
    messageDiv.className = `chat-message ${type}`;
    messageDiv.innerHTML = `<div class="message-content">${content}</div>`;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageId;
}

// Remove chat message by ID
function removeChatMessage(messageId) {
    const message = document.getElementById(messageId);
    if (message) {
        message.remove();
    }
}

// Add query response with results
function addQueryResponse(result) {
    const chatMessages = document.getElementById('chatMessages');
    const responseDiv = document.createElement('div');
    responseDiv.className = 'chat-message assistant';
    
    let content = '';
    
    // Add report
    if (result.report) {
        content += `
            <div class="query-report">
                <h6><i class="fas fa-chart-bar me-2"></i>Analysis Report</h6>
                <p>${result.report}</p>
            </div>
        `;
    }
    
    // Add results based on type
    if (result.result) {
        if (result.result.type === 'dataframe') {
            content += `
                <div class="query-result">
                    <div class="query-result-header">
                        <i class="fas fa-table me-2"></i>Results (${result.result.total_rows} rows)
                    </div>
                    <div class="query-result-content">
                        ${createDataTable(result.result.data, result.result.columns)}
                    </div>
                </div>
            `;
        } else if (result.result.type === 'scalar') {
            content += `
                <div class="query-result">
                    <div class="query-result-header">
                        <i class="fas fa-calculator me-2"></i>Result
                    </div>
                    <div class="query-result-content">
                        <h4 class="text-primary">${result.result.value}</h4>
                    </div>
                </div>
            `;
        } else if (result.result.type === 'series') {
            content += `
                <div class="query-result">
                    <div class="query-result-header">
                        <i class="fas fa-list me-2"></i>Results
                    </div>
                    <div class="query-result-content">
                        ${createSeriesDisplay(result.result.data)}
                    </div>
                </div>
            `;
        }
    }
    
    // Add pandas code (collapsible)
    if (result.pandas_code) {
        content += `
            <details class="query-code">
                <summary class="query-code-header">
                    <i class="fas fa-code me-2"></i>Generated Pandas Code
                </summary>
                <pre><code>${escapeHtml(result.pandas_code)}</code></pre>
            </details>
        `;
    }
    
    responseDiv.innerHTML = `<div class="message-content">${content}</div>`;
    chatMessages.appendChild(responseDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Create data table for results
function createDataTable(data, columns) {
    if (!data || data.length === 0) {
        return '<p class="text-muted">No data to display</p>';
    }
    
    let tableHTML = `
        <div class="table-responsive">
            <table class="table table-sm table-hover">
                <thead>
                    <tr>
                        ${columns.map(col => `<th>${escapeHtml(col)}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
    `;
    
    data.forEach(row => {
        tableHTML += '<tr>';
        columns.forEach(col => {
            const value = row[col] !== null && row[col] !== undefined ? row[col] : '';
            tableHTML += `<td>${escapeHtml(String(value))}</td>`;
        });
        tableHTML += '</tr>';
    });
    
    tableHTML += `
                </tbody>
            </table>
        </div>
    `;
    
    return tableHTML;
}

// Create series display
function createSeriesDisplay(data) {
    let html = '<div class="row">';
    
    Object.entries(data).forEach(([key, value]) => {
        html += `
            <div class="col-md-6 mb-2">
                <div class="card">
                    <div class="card-body p-2">
                        <small class="text-muted">${escapeHtml(key)}</small>
                        <div class="fw-bold">${escapeHtml(String(value))}</div>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    return html;
}

// Update session status indicator
function updateSessionStatus() {
    const sessionStatus = document.getElementById('sessionStatus');
    const filesList = document.querySelector('#filesList');
    
    if (filesList && filesList.children.length > 0) {
        const fileCount = filesList.children.length;
        sessionStatus.innerHTML = `
            <i class="fas fa-check-circle me-1 text-success"></i>
            ${fileCount} file${fileCount > 1 ? 's' : ''} loaded - Ready to query
        `;
        sessionStatus.className = 'text-success';
    } else {
        sessionStatus.innerHTML = `
            <i class="fas fa-info-circle me-1"></i>
            Upload CSV files to start querying
        `;
        sessionStatus.className = 'text-muted';
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Dashboard functions
async function clearDashboard() {
    if (confirm('Are you sure you want to clear all charts from the dashboard?')) {
        const dashboardCharts = document.getElementById('dashboardCharts');
        dashboardCharts.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="fas fa-chart-bar fa-3x mb-3"></i>
                <p>No charts pinned to dashboard yet.</p>
                <p>Create visualizations and pin them here for easy access!</p>
            </div>
        `;
    }
}

async function loadDashboard() {
    try {
        const response = await fetch('/dashboard');
        const result = await response.json();
        
        if (result.success && result.charts.length > 0) {
            displayDashboardCharts(result.charts);
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function displayDashboardCharts(charts) {
    const dashboardCharts = document.getElementById('dashboardCharts');
    
    if (charts.length === 0) {
        dashboardCharts.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="fas fa-chart-bar fa-3x mb-3"></i>
                <p>No charts pinned to dashboard yet.</p>
                <p>Create visualizations and pin them here for easy access!</p>
            </div>
        `;
        return;
    }
    
    dashboardCharts.innerHTML = charts.map(chart => createChartHTML(chart)).join('');
    
    // Render charts
    charts.forEach(chart => {
        if (chart.chart && chart.chart.data) {
            const chartDiv = document.getElementById(`chart-${chart.id}`);
            if (chartDiv) {
                Plotly.newPlot(chartDiv, chart.chart.data.data, chart.chart.layout);
            }
        }
    });
}

function createChartHTML(chart) {
    return `
        <div class="chart-container">
            <div class="chart-header">
                <h6 class="chart-title">${escapeHtml(chart.title)}</h6>
                <div class="chart-actions">
                    <span class="chart-type-badge">${chart.chart.type || 'chart'}</span>
                    <button class="btn btn-outline-danger btn-sm" onclick="removeChartFromDashboard('${chart.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <div class="chart-content">
                <div id="chart-${chart.id}"></div>
            </div>
        </div>
    `;
}

async function removeChartFromDashboard(chartId) {
    try {
        const response = await fetch(`/dashboard/remove/${chartId}`, {
            method: 'DELETE'
        });
        const result = await response.json();
        
        if (result.success) {
            loadDashboard(); // Reload dashboard
        }
    } catch (error) {
        console.error('Error removing chart:', error);
    }
}

async function pinChartToDashboard(chartData, title) {
    try {
        const response = await fetch('/dashboard/pin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                chart: chartData,
                title: title
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Update the pin button to show it's pinned
            const pinBtn = document.querySelector('.pin-chart-btn[data-chart-id]');
            if (pinBtn) {
                pinBtn.classList.add('pinned');
                pinBtn.innerHTML = '<i class="fas fa-thumbtack"></i> Pinned';
                pinBtn.disabled = true;
            }
            
            // Reload dashboard
            loadDashboard();
        }
    } catch (error) {
        console.error('Error pinning chart:', error);
    }
}

// Enhanced query handler to detect visualization requests
async function handleQuery(event) {
    event.preventDefault();

    const queryInput = document.getElementById('queryInput');
    const query = queryInput.value.trim();

    if (!query) {
        return;
    }

    // Check if there are uploaded files
    const filesList = document.querySelector('#filesList');
    if (!filesList || filesList.children.length === 0) {
        addChatMessage('assistant', '❌ No data uploaded. Please upload CSV files first before asking questions.\n\n💡 Tip: Make sure you see the green "1 file loaded" indicator above before querying.');
        return;
    }

    // Add user message to chat
    addChatMessage('user', query);
    queryInput.value = '';

    // Add loading message
    const loadingId = addChatMessage('assistant', 'Analyzing your query<span class="loading-dots"></span>', true);

    try {
        // Check if this is a visualization request
        const isVisualization = isVisualizationQuery(query);
        
        let response;
        if (isVisualization) {
            response = await fetch('/visualize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });
        } else {
            response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });
        }

        const result = await response.json();

        // Remove loading message
        removeChatMessage(loadingId);

        if (result.success) {
            if (isVisualization) {
                addVisualizationResponse(result);
            } else {
                addQueryResponse(result);
            }
        } else {
            // Provide more helpful error messages
            let errorMessage = result.error;
            if (result.error.includes('No data uploaded')) {
                errorMessage = '❌ No data uploaded. Please upload CSV files first before asking questions.\n\n💡 Tip: Make sure you see the green "1 file loaded" indicator above before querying.';
            } else if (result.error.includes('Error executing pandas code')) {
                // Extract the generated code from the error message for debugging
                const errorParts = result.error.split('\n\nGenerated code:\n');
                if (errorParts.length > 1) {
                    const generatedCode = errorParts[1].split('\n\nOriginal OpenAI response:')[0];
                    errorMessage = `❌ Query processing error: ${errorParts[0].replace('Error executing pandas code: ', '')}\n\n🔍 Generated code:\n\`\`\`python\n${generatedCode}\n\`\`\``;
                } else {
                    errorMessage = `❌ Query processing error: ${result.error.replace('Error executing pandas code: ', '')}`;
                }
            } else {
                errorMessage = `❌ Error: ${result.error}`;
            }
            addChatMessage('assistant', errorMessage);
        }
    } catch (error) {
        console.error('Query error:', error);
        removeChatMessage(loadingId);
        addChatMessage('assistant', '❌ An error occurred while processing your query. Please try again.');
    }
}

function isVisualizationQuery(query) {
    const visualizationKeywords = [
        'plot', 'chart', 'graph', 'visualize', 'scatter', 'line', 'bar', 'histogram',
        'box', 'pie', 'heatmap', 'correlation', 'trend', 'distribution'
    ];
    
    const queryLower = query.toLowerCase();
    return visualizationKeywords.some(keyword => queryLower.includes(keyword));
}

function addVisualizationResponse(result) {
    const chatMessages = document.getElementById('chatMessages');
    const responseDiv = document.createElement('div');
    responseDiv.className = 'chat-message assistant';

    // Generate unique chart ID
    const chartId = 'chart-' + Math.random().toString(36).substr(2, 9);

    let content = '';

    // Add chart type and title
    const chartType = result.chart_type || 'chart';
    const chartTitle = result.chart.layout?.title?.text || 'Visualization';
    
    content += `
        <div class="visualization-result">
            <div class="visualization-header">
                <div>
                    <h6 class="visualization-title">
                        <i class="fas fa-chart-bar me-2"></i>${escapeHtml(chartTitle)}
                    </h6>
                    <span class="chart-type-badge">${chartType}</span>
                </div>
                <div class="visualization-actions">
                    <button class="btn btn-sm pin-chart-btn" onclick="pinChartToDashboard(${JSON.stringify(result.chart)}, '${escapeHtml(chartTitle)}')">
                        <i class="fas fa-thumbtack"></i> Pin to Dashboard
                    </button>
                </div>
            </div>
            <div class="chart-content">
                <div id="${chartId}"></div>
            </div>
    `;

    // Add data summary if available
    if (result.data_summary) {
        content += createDataSummaryHTML(result.data_summary);
    }

    content += '</div>';

    responseDiv.innerHTML = `<div class="message-content">${content}</div>`;
    chatMessages.appendChild(responseDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Render the chart
    const chartDiv = document.getElementById(chartId);
    if (chartDiv && result.chart && result.chart.data) {
        // The chart.data is already the full Plotly figure JSON
        const plotlyData = result.chart.data;
        Plotly.newPlot(chartDiv, plotlyData.data, plotlyData.layout);
    }
}

function createDataSummaryHTML(summary) {
    let html = '<div class="chart-summary"><h6>Data Summary</h6>';
    
    html += `<div class="summary-item">
        <span class="summary-label">Total Records:</span>
        <span class="summary-value">${summary.total_records}</span>
    </div>`;
    
    if (summary.x_column) {
        html += `<div class="summary-item">
            <span class="summary-label">X-Axis (${summary.x_column.name}):</span>
            <span class="summary-value">${summary.x_column.type} - ${summary.x_column.unique_values} unique values</span>
        </div>`;
        
        if (summary.x_column.mean !== undefined) {
            html += `<div class="summary-item">
                <span class="summary-label">Mean:</span>
                <span class="summary-value">${summary.x_column.mean.toFixed(2)}</span>
            </div>`;
        }
    }
    
    if (summary.y_column) {
        html += `<div class="summary-item">
            <span class="summary-label">Y-Axis (${summary.y_column.name}):</span>
            <span class="summary-value">${summary.y_column.type} - ${summary.y_column.unique_values} unique values</span>
        </div>`;
        
        if (summary.y_column.mean !== undefined) {
            html += `<div class="summary-item">
                <span class="summary-label">Mean:</span>
                <span class="summary-value">${summary.y_column.mean.toFixed(2)}</span>
            </div>`;
        }
    }
    
    html += '</div>';
    return html;
} 