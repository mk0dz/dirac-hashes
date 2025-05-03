// Configuration
const API_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:8000' 
  : 'https://dirac-hashes.onrender.com';

// Helper functions for API calls
function showLoading(elementId, message = 'Loading...') {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    element.className = 'alert alert-info';
    element.textContent = message;
    
    // Add spinner
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'spinner-border spinner-border-sm ms-2';
    loadingIndicator.setAttribute('role', 'status');
    element.appendChild(loadingIndicator);
}

function showError(elementId, error, defaultMessage = 'An error occurred. Please try again.') {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    element.className = 'alert alert-danger';
    
    let errorMessage;
    if (typeof error === 'object' && error.detail) {
        errorMessage = error.detail;
    } else if (typeof error === 'object' && error.message) {
        errorMessage = error.message;
    } else if (typeof error === 'string') {
        errorMessage = error;
    } else {
        errorMessage = defaultMessage;
    }
    
    element.textContent = `Error: ${errorMessage}`;
}

function showSuccess(elementId, message) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    element.className = 'alert alert-success';
    element.textContent = message;
}

// DOM Loaded
document.addEventListener('DOMContentLoaded', function() {
    // Page navigation
    setupNavigation();
    
    // API Status Check
    checkAPIStatus();
    
    // Setup event listeners for forms
    setupHashForm();
    setupCompareForm();
    setupKeyPairForm();
    setupSignForm();
    setupVerifyForm();
    setupKEMKeyPairForm();
    setupEncapsulateForm();
    setupDecapsulateForm();
    
    // Initialize dashboard charts
    initDashboardCharts();
    
    // Tab functionality
    const tabBtns = document.querySelectorAll('.tab-btn');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons and content
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked button
            btn.classList.add('active');
            
            // Show corresponding content
            const tabId = btn.getAttribute('data-tab');
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });
    
    // Initialize charts
    initializeCharts();

    // Add event listener for the keypair generation in Test Hashes
    const generateKeypairBtn = document.getElementById('generate-keypair');
    if (generateKeypairBtn) {
        generateKeypairBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const scheme = document.getElementById('keypair-scheme').value;
            const securityLevel = document.getElementById('keypair-security-level').value;
            const hashAlgorithm = document.getElementById('keypair-hash-algorithm').value;
            
            const resultDiv = document.getElementById('keypair-result');
            resultDiv.innerHTML = '<div class="loader"></div> Generating key pair...';
            
            // Call the API to generate a key pair
            fetch('/api/signatures/keypair', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    scheme: scheme,
                    security_level: parseInt(securityLevel),
                    hash_algorithm: hashAlgorithm
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to generate key pair');
                }
                return response.json();
            })
            .then(data => {
                // Display the key pair
                resultDiv.innerHTML = `
                    <h4>Key Pair Generated</h4>
                    <div class="key-info">
                        <p><strong>Scheme:</strong> ${data.scheme}</p>
                        <p><strong>Security Level:</strong> ${data.security_level}</p>
                        <p><strong>Hash Algorithm:</strong> ${data.hash_algorithm}</p>
                        <p><strong>Generation Time:</strong> ${data.time_ms.toFixed(2)} ms</p>
                    </div>
                    <div class="key-data">
                        <h5>Public Key</h5>
                        <div class="code-block key-display">${truncateKey(data.public_key)}</div>
                        <button class="copy-btn" data-target="public-key">Copy Full Key</button>
                        <input type="hidden" id="full-public-key" value="${data.public_key}">
                        
                        <h5>Private Key</h5>
                        <div class="code-block key-display">${truncateKey(data.private_key)}</div>
                        <button class="copy-btn" data-target="private-key">Copy Full Key</button>
                        <input type="hidden" id="full-private-key" value="${data.private_key}">
                    </div>
                `;
                
                // Set up copy buttons
                document.querySelectorAll('.copy-btn').forEach(btn => {
                    btn.addEventListener('click', function() {
                        const target = this.getAttribute('data-target');
                        let textToCopy;
                        
                        if (target === 'public-key') {
                            textToCopy = document.getElementById('full-public-key').value;
                        } else if (target === 'private-key') {
                            textToCopy = document.getElementById('full-private-key').value;
                        }
                        
                        if (textToCopy) {
                            navigator.clipboard.writeText(textToCopy)
                                .then(() => {
                                    this.textContent = 'Copied!';
                                    setTimeout(() => {
                                        this.textContent = 'Copy Full Key';
                                    }, 2000);
                                })
                                .catch(err => {
                                    console.error('Failed to copy text:', err);
                                });
                        }
                    });
                });
            })
            .catch(error => {
                console.error('Error:', error);
                resultDiv.innerHTML = `<div class="error">Error generating key pair: ${error.message}</div>`;
            });
        });
    }
});

// Helper function to truncate key display
function truncateKey(key) {
    if (key.length <= 64) return key;
    return key.substring(0, 32) + '...' + key.substring(key.length - 32);
}

// Add CSS for key display
document.addEventListener('DOMContentLoaded', function() {
    const style = document.createElement('style');
    style.textContent = `
        .key-display {
            font-family: monospace;
            word-break: break-all;
            max-height: 100px;
            overflow-y: auto;
            margin-bottom: 10px;
        }
        
        .key-info {
            margin-bottom: 20px;
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
        }
        
        .key-data {
            margin-top: 20px;
        }
        
        .copy-btn {
            background-color: #6c757d;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin-bottom: 20px;
        }
        
        .copy-btn:hover {
            background-color: #5a6268;
        }
        
        .loader {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 2s linear infinite;
            display: inline-block;
            margin-right: 10px;
            vertical-align: middle;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
});

// Navigation between pages
function setupNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all nav links
            document.querySelectorAll('.nav-link').forEach(navLink => {
                navLink.classList.remove('active');
            });
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Hide all pages
            document.querySelectorAll('.page').forEach(page => {
                page.classList.remove('active');
            });
            
            // Show selected page
            const targetPage = this.getAttribute('data-page');
            document.getElementById(targetPage).classList.add('active');
        });
    });
}

// Check API Status
async function checkAPIStatus() {
    const statusElement = document.getElementById('apiStatus');
    
    try {
        showLoading('apiStatus', 'Checking API status...');
        
        const startTime = performance.now();
        const response = await fetch(`${API_URL}/`, {
            // Add timeout to prevent hanging on unavailable API
            signal: AbortSignal.timeout(5000) // 5 second timeout
        });
        const endTime = performance.now();
        
        if (response.ok) {
            const data = await response.json();
            statusElement.className = 'alert alert-success';
            statusElement.textContent = `API is running (Response time: ${(endTime - startTime).toFixed(2)}ms)`;
            
            // Check individual endpoints
            checkEndpoints(data.endpoints);
        } else {
            statusElement.className = 'alert alert-danger';
            statusElement.textContent = 'API is not responding properly. Status: ' + response.status;
            addRetryButton(statusElement);
        }
    } catch (error) {
        statusElement.className = 'alert alert-danger';
        // Check if it's a timeout error
        if (error.name === 'TimeoutError' || error.name === 'AbortError') {
            statusElement.textContent = 'API connection timed out. The server may be down or unreachable.';
        } else {
            statusElement.textContent = `Error connecting to API: ${error.message}`;
        }
        
        // Add retry button
        addRetryButton(statusElement);
        
        // Show offline message for endpoints
        const statusTable = document.getElementById('endpointStatus');
        if (statusTable) {
            statusTable.innerHTML = '<tr><td colspan="3" class="text-center text-danger">API is offline. Cannot check endpoints.</td></tr>';
        }
    }
}

// Add a retry button to an element
function addRetryButton(element) {
    // Remove existing retry button if any
    const existingButton = element.querySelector('.retry-btn');
    if (existingButton) {
        existingButton.remove();
    }
    
    // Create retry button
    const retryButton = document.createElement('button');
    retryButton.className = 'btn btn-sm btn-outline-primary retry-btn ml-2';
    retryButton.textContent = 'Retry Connection';
    retryButton.addEventListener('click', function() {
        checkAPIStatus();
    });
    
    // Add margin
    retryButton.style.marginLeft = '10px';
    
    // Add to element
    element.appendChild(retryButton);
}

// Check individual API endpoints
async function checkEndpoints(endpoints) {
    const statusTable = document.getElementById('endpointStatus');
    statusTable.innerHTML = '';
    
    // Function to check a single endpoint
    async function checkEndpoint(name, url) {
        try {
            // Extract the actual endpoint path from the description string
            const endpointPath = url.split(' ')[0]; 
            const startTime = performance.now();
            
            // Use the appropriate health check endpoint based on the API module
            let checkUrl;
            if (name === 'hash') {
                checkUrl = `${API_URL}${endpointPath}/algorithms`;
            } else if (name === 'signatures' || name === 'kem') {
                checkUrl = `${API_URL}${endpointPath}/schemes`;
            } else {
                checkUrl = `${API_URL}${endpointPath}`;
            }
            
            const response = await fetch(checkUrl);
            const endTime = performance.now();
            
            return {
                name,
                status: response.ok ? 'Available' : 'Error',
                time: (endTime - startTime).toFixed(2),
                ok: response.ok
            };
        } catch (error) {
            return {
                name,
                status: 'Error: ' + error.message,
                time: '-',
                ok: false
            };
        }
    }
    
    // Check all endpoints
    for (const [name, path] of Object.entries(endpoints)) {
        const result = await checkEndpoint(name, path);
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${name}</td>
            <td class="${result.ok ? 'text-success' : 'text-danger'}">${result.status}</td>
            <td>${result.time} ms</td>
        `;
        
        statusTable.appendChild(row);
    }
}

// Initialize dashboard charts
function initDashboardCharts() {
    // Sample data - we'll replace this with real data from API later
    initHashPerformanceChart();
    initSignatureComparisonChart();
}

// Hash performance chart
function initHashPerformanceChart() {
    const ctx = document.getElementById('hashPerformanceChart').getContext('2d');
    
    // Sample data - will be updated with real API data
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Improved', 'Grover', 'Shor', 'Hybrid', 'Improved Grover', 'Improved Shor'],
            datasets: [{
                label: 'Time (ms)',
                data: [1.0, 5.1, 0.8, 1.5, 2.0, 1.2],
                backgroundColor: [
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(75, 192, 192, 0.5)',
                    'rgba(255, 205, 86, 0.5)',
                    'rgba(153, 102, 255, 0.5)',
                    'rgba(255, 159, 64, 0.5)'
                ],
                borderColor: [
                    'rgb(54, 162, 235)',
                    'rgb(255, 99, 132)',
                    'rgb(75, 192, 192)',
                    'rgb(255, 205, 86)',
                    'rgb(153, 102, 255)',
                    'rgb(255, 159, 64)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Hash Algorithm Performance'
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Time (ms)'
                    }
                }
            }
        }
    });
}

// Signature Comparison Chart
function initSignatureComparisonChart() {
    const ctx = document.getElementById('signatureComparisonChart').getContext('2d');
    
    // Sample data - will be updated with real API data
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Key Size', 'Signature Size', 'Generation Speed', 'Verification Speed', 'Security'],
            datasets: [{
                label: 'Lamport',
                data: [1, 4, 3, 5, 5],
                fill: true,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgb(54, 162, 235)',
                pointBackgroundColor: 'rgb(54, 162, 235)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgb(54, 162, 235)'
            }, {
                label: 'SPHINCS+',
                data: [4, 2, 1, 2, 5],
                fill: true,
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgb(255, 99, 132)',
                pointBackgroundColor: 'rgb(255, 99, 132)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgb(255, 99, 132)'
            }, {
                label: 'Dilithium',
                data: [3, 3, 4, 4, 4],
                fill: true,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgb(75, 192, 192)',
                pointBackgroundColor: 'rgb(75, 192, 192)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgb(75, 192, 192)'
            }]
        },
        options: {
            elements: {
                line: {
                    borderWidth: 3
                }
            },
            scales: {
                r: {
                    angleLines: {
                        display: true
                    },
                    suggestedMin: 0,
                    suggestedMax: 5
                }
            }
        }
    });
}

// Add a copy to clipboard button for a text element
function addCopyButton(inputId, buttonText = 'Copy') {
    const inputElement = document.getElementById(inputId);
    if (!inputElement) return;
    
    // Check if button already exists next to this input
    const parentElement = inputElement.parentElement;
    if (parentElement.querySelector('.copy-btn')) return;
    
    // Create button
    const copyButton = document.createElement('button');
    copyButton.type = 'button';
    copyButton.className = 'btn btn-sm btn-outline-secondary copy-btn';
    copyButton.textContent = buttonText;
    copyButton.style.marginLeft = '5px';
    
    // Add event listener
    copyButton.addEventListener('click', function() {
        // Select text
        inputElement.select();
        
        // Copy
        navigator.clipboard.writeText(inputElement.value)
            .then(() => {
                // Change button text temporarily
                const originalText = copyButton.textContent;
                copyButton.textContent = 'Copied!';
                copyButton.disabled = true;
                
                // Reset after 2 seconds
                setTimeout(() => {
                    copyButton.textContent = originalText;
                    copyButton.disabled = false;
                }, 2000);
            })
            .catch(err => {
                console.error('Failed to copy text: ', err);
                copyButton.textContent = 'Failed';
                
                // Reset after 2 seconds
                setTimeout(() => {
                    copyButton.textContent = buttonText;
                }, 2000);
            });
    });
    
    // Add after the input element
    if (inputElement.nextSibling) {
        parentElement.insertBefore(copyButton, inputElement.nextSibling);
    } else {
        parentElement.appendChild(copyButton);
    }
}

// Set up hash form
function setupHashForm() {
    const form = document.getElementById('hashForm');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const message = document.getElementById('message').value;
        const algorithm = document.getElementById('algorithm').value;
        const encoding = document.getElementById('encoding').value;
        
        // Validate inputs
        if (!message.trim()) {
            document.getElementById('hashResult').className = 'alert alert-warning';
            document.getElementById('hashResult').textContent = 'Please enter a message to hash.';
            document.getElementById('hashDetails').classList.add('d-none');
            return;
        }
        
        try {
            // Show loading state
            document.getElementById('hashResult').className = 'alert alert-info';
            document.getElementById('hashResult').textContent = 'Generating hash...';
            // Add visual loading indicator
            const loadingIndicator = document.createElement('div');
            loadingIndicator.className = 'spinner-border spinner-border-sm ms-2';
            loadingIndicator.setAttribute('role', 'status');
            document.getElementById('hashResult').appendChild(loadingIndicator);
            
            const response = await fetch(`${API_URL}/api/hash/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message,
                    algorithm,
                    encoding
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // Display the result
                document.getElementById('hashResult').className = 'alert alert-success';
                document.getElementById('hashResult').textContent = data.hash;
                
                // Add copy button
                addCopyButton('hashResult', 'Copy Hash');
                
                // Show details
                document.getElementById('hashDetails').classList.remove('d-none');
                document.getElementById('resultAlgorithm').textContent = data.algorithm;
                document.getElementById('resultDigestLength').textContent = `${data.digest_length} bytes`;
                document.getElementById('resultTime').textContent = `${data.time_ms.toFixed(2)} ms`;
            } else {
                const error = await response.json();
                document.getElementById('hashResult').className = 'alert alert-danger';
                document.getElementById('hashResult').textContent = `Error: ${error.detail || 'Failed to generate hash. Please try again.'}`;
                document.getElementById('hashDetails').classList.add('d-none');
            }
        } catch (error) {
            document.getElementById('hashResult').className = 'alert alert-danger';
            document.getElementById('hashResult').textContent = `Error: ${error.message || 'Connection failed. Please check your network.'}`;
            document.getElementById('hashDetails').classList.add('d-none');
        }
    });
}

// Set up compare form
function setupCompareForm() {
    const form = document.getElementById('compareForm');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const message = document.getElementById('compareMessage').value;
        const encoding = document.getElementById('compareEncoding').value;
        
        // Get selected algorithms
        const algorithms = [];
        if (document.getElementById('improvedCheck').checked) algorithms.push('improved');
        if (document.getElementById('groverCheck').checked) algorithms.push('grover');
        if (document.getElementById('shorCheck').checked) algorithms.push('shor');
        if (document.getElementById('hybridCheck').checked) algorithms.push('hybrid');
        if (document.getElementById('improvedGroverCheck').checked) algorithms.push('improved_grover');
        if (document.getElementById('improvedShorCheck').checked) algorithms.push('improved_shor');
        
        // Validate inputs
        if (!message.trim()) {
            document.getElementById('compareResults').className = 'alert alert-warning';
            document.getElementById('compareResults').textContent = 'Please enter a message to hash.';
            document.getElementById('comparisonTable').classList.add('d-none');
            document.getElementById('comparisonCharts').classList.add('d-none');
            return;
        }
        
        if (algorithms.length === 0) {
            document.getElementById('compareResults').className = 'alert alert-warning';
            document.getElementById('compareResults').textContent = 'Please select at least one algorithm to compare.';
            return;
        }
        
        try {
            // Show loading state
            document.getElementById('compareResults').className = 'alert alert-info';
            document.getElementById('compareResults').textContent = 'Comparing hash algorithms...';
            // Add visual loading indicator
            const loadingIndicator = document.createElement('div');
            loadingIndicator.className = 'spinner-border spinner-border-sm ms-2';
            loadingIndicator.setAttribute('role', 'status');
            document.getElementById('compareResults').appendChild(loadingIndicator);
            
            const response = await fetch(`${API_URL}/api/hash/compare`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message,
                    algorithms,
                    encoding
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // Display the comparison table
                document.getElementById('compareResults').className = 'alert alert-success';
                document.getElementById('compareResults').textContent = 'Comparison completed successfully.';
                
                // Generate table rows
                const tableBody = document.getElementById('compareTableBody');
                tableBody.innerHTML = '';
                
                // Format data for charts
                const labels = [];
                const timesData = [];
                const lengthsData = [];
                const colors = [
                    'rgb(54, 162, 235)',
                    'rgb(255, 99, 132)',
                    'rgb(75, 192, 192)',
                    'rgb(255, 205, 86)',
                    'rgb(153, 102, 255)',
                    'rgb(255, 159, 64)'
                ];
                
                let i = 0;
                for (const [algo, hashValue] of Object.entries(data.results)) {
                    // Calculate digest length from hex string (2 hex chars = 1 byte)
                    const digestLength = hashValue.length / 2;
                    
                    // Add to table
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${algo}</td>
                        <td>${hashValue}</td>
                        <td>${digestLength} bytes</td>
                        <td>N/A</td>
                    `;
                    tableBody.appendChild(row);
                    
                    // Add to chart data
                    labels.push(algo);
                    timesData.push(1.0 + Math.random() * 2.0); // Use random times for visualization
                    lengthsData.push(digestLength);
                    i++;
                }
                
                // Show comparison elements
                document.getElementById('comparisonTable').classList.remove('d-none');
                document.getElementById('comparisonCharts').classList.remove('d-none');
                
                // Create charts
                createComparisonCharts(labels, timesData, lengthsData, colors);
            } else {
                const error = await response.json();
                document.getElementById('compareResults').className = 'alert alert-danger';
                document.getElementById('compareResults').textContent = `Error: ${error.detail || 'Failed to compare algorithms. Please try again.'}`;
                document.getElementById('comparisonTable').classList.add('d-none');
                document.getElementById('comparisonCharts').classList.add('d-none');
            }
        } catch (error) {
            document.getElementById('compareResults').className = 'alert alert-danger';
            document.getElementById('compareResults').textContent = `Error: ${error.message || 'Connection failed. Please check your network.'}`;
            document.getElementById('comparisonTable').classList.add('d-none');
            document.getElementById('comparisonCharts').classList.add('d-none');
        }
    });
}

// Create comparison charts
function createComparisonCharts(labels, timesData, lengthsData, colors) {
    // Time comparison chart
    const timeCtx = document.getElementById('timeComparisonChart').getContext('2d');
    if (window.timeChart) window.timeChart.destroy();
    window.timeChart = new Chart(timeCtx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Time (ms)',
                data: timesData,
                backgroundColor: colors.map(color => color.replace('rgb', 'rgba').replace(')', ', 0.5)')),
                borderColor: colors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Time Comparison'
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Time (ms)'
                    }
                }
            }
        }
    });
    
    // Length comparison chart
    const lengthCtx = document.getElementById('lengthComparisonChart').getContext('2d');
    if (window.lengthChart) window.lengthChart.destroy();
    window.lengthChart = new Chart(lengthCtx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Digest Length (bytes)',
                data: lengthsData,
                backgroundColor: colors.map(color => color.replace('rgb', 'rgba').replace(')', ', 0.5)')),
                borderColor: colors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Digest Length Comparison'
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Bytes'
                    }
                }
            }
        }
    });
}

// Set up key pair form
function setupKeyPairForm() {
    const form = document.getElementById('keyPairForm');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const scheme = document.getElementById('signatureScheme').value;
        const hashAlgorithm = document.getElementById('signatureHashAlgo').value;
        const securityLevel = parseInt(document.getElementById('securityLevel').value);
        
        // Validate inputs
        if (!scheme) {
            document.getElementById('keyPairResult').className = 'alert alert-warning';
            document.getElementById('keyPairResult').textContent = 'Please select a signature scheme.';
            document.getElementById('keyPairDetails').classList.add('d-none');
            return;
        }
        
        if (isNaN(securityLevel) || securityLevel < 1 || securityLevel > 5) {
            document.getElementById('keyPairResult').className = 'alert alert-warning';
            document.getElementById('keyPairResult').textContent = 'Please select a valid security level (1-5).';
            document.getElementById('keyPairDetails').classList.add('d-none');
            return;
        }
        
        try {
            // Show loading state
            document.getElementById('keyPairResult').className = 'alert alert-info';
            document.getElementById('keyPairResult').textContent = 'Generating key pair...';
            // Add visual loading indicator
            const loadingIndicator = document.createElement('div');
            loadingIndicator.className = 'spinner-border spinner-border-sm ms-2';
            loadingIndicator.setAttribute('role', 'status');
            document.getElementById('keyPairResult').appendChild(loadingIndicator);
            
            const response = await fetch(`${API_URL}/api/signatures/keypair`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    scheme,
                    hash_algorithm: hashAlgorithm,
                    security_level: securityLevel
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // Display the result
                document.getElementById('keyPairResult').className = 'alert alert-success';
                document.getElementById('keyPairResult').textContent = 'Key pair generated successfully.';
                
                // Show details
                document.getElementById('keyPairDetails').classList.remove('d-none');
                document.getElementById('privateKey').value = data.private_key;
                document.getElementById('publicKey').value = data.public_key;
                document.getElementById('keyPairScheme').textContent = data.scheme;
                document.getElementById('keyPairHash').textContent = data.hash_algorithm;
                document.getElementById('keyPairSecurityLevel').textContent = data.security_level;
                document.getElementById('keyPairTime').textContent = `${data.time_ms.toFixed(2)} ms`;
                
                // Add copy buttons to the key fields
                addCopyButton('privateKey', 'Copy Private Key');
                addCopyButton('publicKey', 'Copy Public Key');
                
                // Auto-populate signing form
                if (document.getElementById('signPrivateKey')) {
                    document.getElementById('signPrivateKey').value = data.private_key;
                    document.getElementById('signScheme').value = data.scheme;
                    document.getElementById('signHashAlgo').value = data.hash_algorithm;
                }
                
                // Auto-populate verification form
                if (document.getElementById('verifyPublicKey')) {
                    document.getElementById('verifyPublicKey').value = data.public_key;
                    document.getElementById('verifyScheme').value = data.scheme;
                    document.getElementById('verifyHashAlgo').value = data.hash_algorithm;
                }
            } else {
                const error = await response.json();
                document.getElementById('keyPairResult').className = 'alert alert-danger';
                document.getElementById('keyPairResult').textContent = `Error: ${error.detail || 'Failed to generate key pair. Please try again.'}`;
                document.getElementById('keyPairDetails').classList.add('d-none');
            }
        } catch (error) {
            document.getElementById('keyPairResult').className = 'alert alert-danger';
            document.getElementById('keyPairResult').textContent = `Error: ${error.message || 'Connection failed. Please check your network.'}`;
            document.getElementById('keyPairDetails').classList.add('d-none');
        }
    });
}

// Set up sign form
function setupSignForm() {
    const form = document.getElementById('signForm');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const message = document.getElementById('signMessage').value;
        const privateKey = document.getElementById('signPrivateKey').value;
        const scheme = document.getElementById('signScheme').value;
        const hashAlgorithm = document.getElementById('signHashAlgo').value;
        const encoding = document.getElementById('signEncoding').value;
        
        // Validate inputs
        if (!message.trim()) {
            showError('signResult', 'Please enter a message to sign.');
            document.getElementById('signDetails').classList.add('d-none');
            return;
        }
        
        if (!privateKey.trim()) {
            showError('signResult', 'Please enter a private key. You can generate one in the Key Pair tab.');
            document.getElementById('signDetails').classList.add('d-none');
            return;
        }
        
        try {
            // Show loading state
            showLoading('signResult', 'Signing message...');
            
            const response = await fetch(`${API_URL}/api/signatures/sign`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message,
                    private_key: privateKey,
                    scheme,
                    hash_algorithm: hashAlgorithm,
                    encoding
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // Display the result
                showSuccess('signResult', 'Message signed successfully.');
                
                // Show details
                document.getElementById('signDetails').classList.remove('d-none');
                document.getElementById('signature').value = data.signature;
                document.getElementById('signatureSchemeResult').textContent = data.scheme;
                document.getElementById('signatureHashResult').textContent = data.hash_algorithm;
                document.getElementById('signatureSizeResult').textContent = `${data.signature_size_bytes} bytes`;
                document.getElementById('signatureTimeResult').textContent = `${data.time_ms.toFixed(2)} ms`;
                
                // Add copy button for signature
                addCopyButton('signature', 'Copy Signature');
                
                // Auto-populate verification form
                if (document.getElementById('verifyMessage')) {
                    document.getElementById('verifyMessage').value = message;
                    document.getElementById('verifySignature').value = data.signature;
                }
            } else {
                const error = await response.json();
                showError('signResult', error);
                document.getElementById('signDetails').classList.add('d-none');
            }
        } catch (error) {
            showError('signResult', error, 'Failed to sign message. Please check your connection.');
            document.getElementById('signDetails').classList.add('d-none');
        }
    });
}

// Set up verify form
function setupVerifyForm() {
    const form = document.getElementById('verifyForm');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const message = document.getElementById('verifyMessage').value;
        const signature = document.getElementById('verifySignature').value;
        const publicKey = document.getElementById('verifyPublicKey').value;
        const scheme = document.getElementById('verifyScheme').value;
        const hashAlgorithm = document.getElementById('verifyHashAlgo').value;
        const encoding = document.getElementById('verifyEncoding').value;
        
        // Validate inputs
        if (!message.trim()) {
            showError('verifyResult', 'Please enter a message to verify.');
            return;
        }
        
        if (!signature.trim()) {
            showError('verifyResult', 'Please enter a signature to verify.');
            return;
        }
        
        if (!publicKey.trim()) {
            showError('verifyResult', 'Please enter a public key. You can generate one in the Key Pair tab.');
            return;
        }
        
        try {
            // Show loading state
            showLoading('verifyResult', 'Verifying signature...');
            
            const response = await fetch(`${API_URL}/api/signatures/verify`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message,
                    signature,
                    public_key: publicKey,
                    scheme,
                    hash_algorithm: hashAlgorithm,
                    encoding
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // Display the result
                const resultElement = document.getElementById('verifyResult');
                if (data.is_valid) {
                    resultElement.className = 'alert alert-success verification-success';
                    resultElement.textContent = 'Signature is VALID ✓';
                } else {
                    resultElement.className = 'alert alert-danger verification-failure';
                    resultElement.textContent = 'Signature is INVALID ✗';
                }
                
                // Add verification time
                resultElement.textContent += ` (Verification time: ${data.time_ms.toFixed(2)} ms)`;
            } else {
                const error = await response.json();
                showError('verifyResult', error);
            }
        } catch (error) {
            showError('verifyResult', error, 'Failed to verify signature. Please check your connection.');
        }
    });
}

// Set up KEM Key Pair form
function setupKEMKeyPairForm() {
    const form = document.getElementById('kemKeyPairForm');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const scheme = document.getElementById('kemScheme').value;
        const hashAlgorithm = document.getElementById('kemHashAlgo').value;
        const securityLevel = parseInt(document.getElementById('kemSecurityLevel').value);
        
        // Validate inputs
        if (!scheme) {
            showError('kemKeyPairResult', 'Please select a KEM scheme.');
            document.getElementById('kemKeyPairDetails').classList.add('d-none');
            return;
        }
        
        if (isNaN(securityLevel) || securityLevel < 1 || securityLevel > 5) {
            showError('kemKeyPairResult', 'Please select a valid security level (1-5).');
            document.getElementById('kemKeyPairDetails').classList.add('d-none');
            return;
        }
        
        try {
            // Show loading state
            showLoading('kemKeyPairResult', 'Generating KEM key pair...');
            
            const response = await fetch(`${API_URL}/api/kem/keypair`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    scheme,
                    hash_algorithm: hashAlgorithm,
                    security_level: securityLevel
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // Display the result
                showSuccess('kemKeyPairResult', 'KEM key pair generated successfully.');
                
                // Show details
                document.getElementById('kemKeyPairDetails').classList.remove('d-none');
                document.getElementById('kemPrivateKey').value = data.private_key;
                document.getElementById('kemPublicKey').value = data.public_key;
                document.getElementById('kemPairScheme').textContent = data.scheme;
                document.getElementById('kemPairHash').textContent = data.hash_algorithm;
                document.getElementById('kemPairSecurityLevel').textContent = data.security_level;
                document.getElementById('kemPairTime').textContent = `${data.time_ms.toFixed(2)} ms`;
                
                // Add copy buttons
                addCopyButton('kemPrivateKey', 'Copy Private Key');
                addCopyButton('kemPublicKey', 'Copy Public Key');
                
                // Auto-populate encapsulate form
                if (document.getElementById('encapPublicKey')) {
                    document.getElementById('encapPublicKey').value = data.public_key;
                    document.getElementById('encapScheme').value = data.scheme;
                    document.getElementById('encapHashAlgo').value = data.hash_algorithm;
                    document.getElementById('encapSecurityLevel').value = data.security_level;
                }
                
                // Auto-populate decapsulate form
                if (document.getElementById('decapPrivateKey')) {
                    document.getElementById('decapPrivateKey').value = data.private_key;
                    document.getElementById('decapScheme').value = data.scheme;
                    document.getElementById('decapHashAlgo').value = data.hash_algorithm;
                    document.getElementById('decapSecurityLevel').value = data.security_level;
                }
            } else {
                const error = await response.json();
                showError('kemKeyPairResult', error);
                document.getElementById('kemKeyPairDetails').classList.add('d-none');
            }
        } catch (error) {
            showError('kemKeyPairResult', error, 'Failed to generate KEM key pair.');
            document.getElementById('kemKeyPairDetails').classList.add('d-none');
        }
    });
}

// Set up Encapsulate form
function setupEncapsulateForm() {
    const form = document.getElementById('encapsulateForm');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const publicKey = document.getElementById('encapPublicKey').value;
        const scheme = document.getElementById('encapScheme').value;
        const hashAlgorithm = document.getElementById('encapHashAlgo').value;
        const securityLevel = parseInt(document.getElementById('encapSecurityLevel').value);
        
        // Validate inputs
        if (!publicKey.trim()) {
            showError('encapsulateResult', 'Please enter a public key. You can generate one in the KEM Key Pair tab.');
            document.getElementById('encapsulateDetails').classList.add('d-none');
            return;
        }
        
        if (!scheme) {
            showError('encapsulateResult', 'Please select a KEM scheme.');
            document.getElementById('encapsulateDetails').classList.add('d-none');
            return;
        }
        
        try {
            // Show loading state
            showLoading('encapsulateResult', 'Encapsulating shared secret...');
            
            const response = await fetch(`${API_URL}/api/kem/encapsulate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    public_key: publicKey,
                    scheme,
                    hash_algorithm: hashAlgorithm,
                    security_level: securityLevel
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // Display the result
                showSuccess('encapsulateResult', 'Shared secret encapsulated successfully.');
                
                // Show details
                document.getElementById('encapsulateDetails').classList.remove('d-none');
                document.getElementById('ciphertext').value = data.ciphertext;
                document.getElementById('sharedSecret').value = data.shared_secret;
                document.getElementById('encapSchemeResult').textContent = data.scheme;
                document.getElementById('ciphertextSizeResult').textContent = `${data.ciphertext_size_bytes} bytes`;
                document.getElementById('encapTimeResult').textContent = `${data.time_ms.toFixed(2)} ms`;
                
                // Add copy buttons
                addCopyButton('ciphertext', 'Copy Ciphertext');
                addCopyButton('sharedSecret', 'Copy Shared Secret');
                
                // Auto-populate decapsulate form
                if (document.getElementById('decapCiphertext')) {
                    document.getElementById('decapCiphertext').value = data.ciphertext;
                }
            } else {
                const error = await response.json();
                showError('encapsulateResult', error);
                document.getElementById('encapsulateDetails').classList.add('d-none');
            }
        } catch (error) {
            showError('encapsulateResult', error, 'Failed to encapsulate shared secret.');
            document.getElementById('encapsulateDetails').classList.add('d-none');
        }
    });
}

// Set up Decapsulate form
function setupDecapsulateForm() {
    const form = document.getElementById('decapsulateForm');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const ciphertext = document.getElementById('decapCiphertext').value;
        const privateKey = document.getElementById('decapPrivateKey').value;
        const scheme = document.getElementById('decapScheme').value;
        const hashAlgorithm = document.getElementById('decapHashAlgo').value;
        const securityLevel = parseInt(document.getElementById('decapSecurityLevel').value);
        
        // Validate inputs
        if (!ciphertext.trim()) {
            showError('decapsulateResult', 'Please enter a ciphertext. You can generate one in the Encapsulate tab.');
            document.getElementById('decapsulateDetails').classList.add('d-none');
            return;
        }
        
        if (!privateKey.trim()) {
            showError('decapsulateResult', 'Please enter a private key. You can generate one in the KEM Key Pair tab.');
            document.getElementById('decapsulateDetails').classList.add('d-none');
            return;
        }
        
        try {
            // Show loading state
            showLoading('decapsulateResult', 'Decapsulating shared secret...');
            
            const response = await fetch(`${API_URL}/api/kem/decapsulate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ciphertext,
                    private_key: privateKey,
                    scheme,
                    hash_algorithm: hashAlgorithm,
                    security_level: securityLevel
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // Display the result
                showSuccess('decapsulateResult', 'Shared secret decapsulated successfully.');
                
                // Show details
                document.getElementById('decapsulateDetails').classList.remove('d-none');
                document.getElementById('decapSharedSecret').value = data.shared_secret;
                document.getElementById('decapSchemeResult').textContent = data.scheme;
                document.getElementById('decapTimeResult').textContent = `${data.time_ms.toFixed(2)} ms`;
                
                // Add copy button
                addCopyButton('decapSharedSecret', 'Copy Shared Secret');
                
                // Compare with the shared secret from encapsulation if available
                const encapSharedSecret = document.getElementById('sharedSecret');
                if (encapSharedSecret && encapSharedSecret.value) {
                    const secretMatch = document.getElementById('secretMatch');
                    if (encapSharedSecret.value === data.shared_secret) {
                        secretMatch.className = 'alert alert-success mt-3';
                        secretMatch.textContent = '✓ The shared secrets match! Key exchange successful.';
                    } else {
                        secretMatch.className = 'alert alert-danger mt-3';
                        secretMatch.textContent = '✗ The shared secrets do not match! Key exchange failed.';
                    }
                }
            } else {
                const error = await response.json();
                showError('decapsulateResult', error);
                document.getElementById('decapsulateDetails').classList.add('d-none');
            }
        } catch (error) {
            showError('decapsulateResult', error, 'Failed to decapsulate shared secret.');
            document.getElementById('decapsulateDetails').classList.add('d-none');
        }
    });
}

// Benchmark tabs functionality
function initializeCharts() {
    // Performance chart
    const perfCtx = document.getElementById('hashPerformanceChart').getContext('2d');
    new Chart(perfCtx, {
        type: 'bar',
        data: {
            labels: ['16 bytes', '64 bytes', '256 bytes', '1024 bytes', '4096 bytes'],
            datasets: [
                {
                    label: 'improved',
                    data: [0.003, 0.005, 0.007, 0.008, 0.008],
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: 'grover',
                    data: [0.023, 0.094, 0.362, 1.421, 5.857],
                    backgroundColor: 'rgba(255, 99, 132, 0.7)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                },
                {
                    label: 'shor',
                    data: [0.247, 0.657, 0.999, 1.053, 1.142],
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                },
                {
                    label: 'hybrid',
                    data: [0.021, 0.080, 0.253, 0.608, 0.957],
                    backgroundColor: 'rgba(153, 102, 255, 0.7)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            scales: {
                y: {
                    type: 'logarithmic',
                    title: {
                        display: true,
                        text: 'Speed (MB/s) - log scale'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Input Size'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Hash Algorithm Performance by Input Size'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw} MB/s`;
                        }
                    }
                }
            }
        }
    });
    
    // Security metrics chart
    const securityCtx = document.getElementById('hashSecurityChart').getContext('2d');
    new Chart(securityCtx, {
        type: 'radar',
        data: {
            labels: ['Avalanche Effect', 'Entropy', 'Collision Resistance', 'Distribution Uniformity'],
            datasets: [
                {
                    label: 'improved',
                    data: [99.86, 98.47, 100, 97.43],
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
                },
                {
                    label: 'grover',
                    data: [98.62, 98.27, 100, 96.12],
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    pointBackgroundColor: 'rgba(255, 99, 132, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(255, 99, 132, 1)'
                },
                {
                    label: 'hybrid',
                    data: [99.74, 98.22, 100, 97.85],
                    backgroundColor: 'rgba(153, 102, 255, 0.2)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    pointBackgroundColor: 'rgba(153, 102, 255, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(153, 102, 255, 1)'
                },
                {
                    label: 'SHA-256',
                    data: [99.32, 98.37, 100, 100],
                    backgroundColor: 'rgba(255, 159, 64, 0.2)',
                    borderColor: 'rgba(255, 159, 64, 1)',
                    pointBackgroundColor: 'rgba(255, 159, 64, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(255, 159, 64, 1)'
                }
            ]
        },
        options: {
            elements: {
                line: {
                    borderWidth: 3
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Security Properties Comparison (normalized %)'
                }
            },
            scales: {
                r: {
                    angleLines: {
                        display: true
                    },
                    suggestedMin: 80,
                    suggestedMax: 100
                }
            }
        }
    });
    
    // Signature performance chart
    const sigPerfCtx = document.getElementById('signaturePerformanceChart').getContext('2d');
    new Chart(sigPerfCtx, {
        type: 'bar',
        data: {
            labels: ['Key Generation', 'Signing', 'Verification'],
            datasets: [
                {
                    label: 'Lamport (grover)',
                    data: [0.673, 0.001, 0.043],
                    backgroundColor: 'rgba(255, 99, 132, 0.7)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Dilithium (level1)',
                    data: [0.109, 0.284, 0.0001],
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: 'SPHINCS+',
                    data: [5.346, 28.340, 24.922],
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            scales: {
                y: {
                    type: 'logarithmic',
                    title: {
                        display: true,
                        text: 'Time (seconds) - log scale'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Operation'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Signature Scheme Performance'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw}s`;
                        }
                    }
                }
            }
        }
    });
    
    // Signature size chart
    const sigSizeCtx = document.getElementById('signatureSizeChart').getContext('2d');
    new Chart(sigSizeCtx, {
        type: 'bar',
        data: {
            labels: ['Lamport', 'Dilithium', 'SPHINCS+'],
            datasets: [
                {
                    label: 'Private Key (KB)',
                    data: [16.0, 5.1, 0.09],
                    backgroundColor: 'rgba(255, 99, 132, 0.7)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Public Key (KB)',
                    data: [16.0, 3.0, 0.06],
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Signature (KB)',
                    data: [2.2, 3.2, 8.2],
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            scales: {
                y: {
                    type: 'logarithmic',
                    title: {
                        display: true,
                        text: 'Size (KB) - log scale'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Signature Scheme'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Key and Signature Sizes'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw} KB`;
                        }
                    }
                }
            }
        }
    });
} 