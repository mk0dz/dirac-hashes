// Configuration
const API_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:8000' 
  : 'https://dirac-hashes.onrender.com';

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
    try {
        const startTime = performance.now();
        const response = await fetch(`${API_URL}/`);
        const endTime = performance.now();
        
        if (response.ok) {
            const data = await response.json();
            document.getElementById('apiStatus').className = 'alert alert-success';
            document.getElementById('apiStatus').textContent = `API is running (Response time: ${(endTime - startTime).toFixed(2)}ms)`;
            
            // Check individual endpoints
            checkEndpoints(data.endpoints);
        } else {
            document.getElementById('apiStatus').className = 'alert alert-danger';
            document.getElementById('apiStatus').textContent = 'API is not responding properly';
        }
    } catch (error) {
        document.getElementById('apiStatus').className = 'alert alert-danger';
        document.getElementById('apiStatus').textContent = `Error connecting to API: ${error.message}`;
    }
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

// Set up hash form
function setupHashForm() {
    const form = document.getElementById('hashForm');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const message = document.getElementById('message').value;
        const algorithm = document.getElementById('algorithm').value;
        const encoding = document.getElementById('encoding').value;
        
        try {
            // Show loading state
            document.getElementById('hashResult').className = 'alert alert-info';
            document.getElementById('hashResult').textContent = 'Generating hash...';
            
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
                
                // Show details
                document.getElementById('hashDetails').classList.remove('d-none');
                document.getElementById('resultAlgorithm').textContent = data.algorithm;
                document.getElementById('resultDigestLength').textContent = `${data.digest_length} bytes`;
                document.getElementById('resultTime').textContent = `${data.time_ms.toFixed(2)} ms`;
            } else {
                const error = await response.json();
                document.getElementById('hashResult').className = 'alert alert-danger';
                document.getElementById('hashResult').textContent = `Error: ${error.detail}`;
                document.getElementById('hashDetails').classList.add('d-none');
            }
        } catch (error) {
            document.getElementById('hashResult').className = 'alert alert-danger';
            document.getElementById('hashResult').textContent = `Error: ${error.message}`;
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
        
        if (algorithms.length === 0) {
            document.getElementById('compareResults').className = 'alert alert-warning';
            document.getElementById('compareResults').textContent = 'Please select at least one algorithm to compare.';
            return;
        }
        
        try {
            // Show loading state
            document.getElementById('compareResults').className = 'alert alert-info';
            document.getElementById('compareResults').textContent = 'Comparing hash algorithms...';
            
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
                for (const [algo, result] of Object.entries(data.results)) {
                    // Add to table
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${algo}</td>
                        <td>${result.hash}</td>
                        <td>${result.digest_length} bytes</td>
                        <td>${result.time_ms.toFixed(2)} ms</td>
                    `;
                    tableBody.appendChild(row);
                    
                    // Add to chart data
                    labels.push(algo);
                    timesData.push(result.time_ms);
                    lengthsData.push(result.digest_length);
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
                document.getElementById('compareResults').textContent = `Error: ${error.detail}`;
                document.getElementById('comparisonTable').classList.add('d-none');
                document.getElementById('comparisonCharts').classList.add('d-none');
            }
        } catch (error) {
            document.getElementById('compareResults').className = 'alert alert-danger';
            document.getElementById('compareResults').textContent = `Error: ${error.message}`;
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
        
        try {
            // Show loading state
            document.getElementById('keyPairResult').className = 'alert alert-info';
            document.getElementById('keyPairResult').textContent = 'Generating key pair...';
            
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
                document.getElementById('keyPairResult').textContent = `Error: ${error.detail}`;
                document.getElementById('keyPairDetails').classList.add('d-none');
            }
        } catch (error) {
            document.getElementById('keyPairResult').className = 'alert alert-danger';
            document.getElementById('keyPairResult').textContent = `Error: ${error.message}`;
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
        
        try {
            // Show loading state
            document.getElementById('signResult').className = 'alert alert-info';
            document.getElementById('signResult').textContent = 'Signing message...';
            
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
                document.getElementById('signResult').className = 'alert alert-success';
                document.getElementById('signResult').textContent = 'Message signed successfully.';
                
                // Show details
                document.getElementById('signDetails').classList.remove('d-none');
                document.getElementById('signature').value = data.signature;
                document.getElementById('signatureSchemeResult').textContent = data.scheme;
                document.getElementById('signatureHashResult').textContent = data.hash_algorithm;
                document.getElementById('signatureSizeResult').textContent = `${data.signature_size_bytes} bytes`;
                document.getElementById('signatureTimeResult').textContent = `${data.time_ms.toFixed(2)} ms`;
                
                // Auto-populate verification form
                if (document.getElementById('verifyMessage')) {
                    document.getElementById('verifyMessage').value = message;
                    document.getElementById('verifySignature').value = data.signature;
                }
            } else {
                const error = await response.json();
                document.getElementById('signResult').className = 'alert alert-danger';
                document.getElementById('signResult').textContent = `Error: ${error.detail}`;
                document.getElementById('signDetails').classList.add('d-none');
            }
        } catch (error) {
            document.getElementById('signResult').className = 'alert alert-danger';
            document.getElementById('signResult').textContent = `Error: ${error.message}`;
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
        
        try {
            // Show loading state
            document.getElementById('verifyResult').className = 'alert alert-info';
            document.getElementById('verifyResult').textContent = 'Verifying signature...';
            
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
                if (data.is_valid) {
                    document.getElementById('verifyResult').className = 'alert alert-success verification-success';
                    document.getElementById('verifyResult').textContent = 'Signature is VALID ✓';
                } else {
                    document.getElementById('verifyResult').className = 'alert alert-danger verification-failure';
                    document.getElementById('verifyResult').textContent = 'Signature is INVALID ✗';
                }
                
                // Add verification time
                document.getElementById('verifyResult').textContent += ` (Verification time: ${data.time_ms.toFixed(2)} ms)`;
            } else {
                const error = await response.json();
                document.getElementById('verifyResult').className = 'alert alert-danger';
                document.getElementById('verifyResult').textContent = `Error: ${error.detail}`;
            }
        } catch (error) {
            document.getElementById('verifyResult').className = 'alert alert-danger';
            document.getElementById('verifyResult').textContent = `Error: ${error.message}`;
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
        
        try {
            // Show loading state
            document.getElementById('kemKeyPairResult').className = 'alert alert-info';
            document.getElementById('kemKeyPairResult').textContent = 'Generating KEM key pair...';
            
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
                document.getElementById('kemKeyPairResult').className = 'alert alert-success';
                document.getElementById('kemKeyPairResult').textContent = 'KEM key pair generated successfully.';
                
                // Show details
                document.getElementById('kemKeyPairDetails').classList.remove('d-none');
                document.getElementById('kemPrivateKey').value = data.private_key;
                document.getElementById('kemPublicKey').value = data.public_key;
                document.getElementById('kemPairScheme').textContent = data.scheme;
                document.getElementById('kemPairHash').textContent = data.hash_algorithm;
                document.getElementById('kemPairSecurityLevel').textContent = data.security_level;
                document.getElementById('kemPairTime').textContent = `${data.time_ms.toFixed(2)} ms`;
                
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
                document.getElementById('kemKeyPairResult').className = 'alert alert-danger';
                document.getElementById('kemKeyPairResult').textContent = `Error: ${error.detail}`;
                document.getElementById('kemKeyPairDetails').classList.add('d-none');
            }
        } catch (error) {
            document.getElementById('kemKeyPairResult').className = 'alert alert-danger';
            document.getElementById('kemKeyPairResult').textContent = `Error: ${error.message}`;
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
        
        try {
            // Show loading state
            document.getElementById('encapsulateResult').className = 'alert alert-info';
            document.getElementById('encapsulateResult').textContent = 'Encapsulating shared secret...';
            
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
                document.getElementById('encapsulateResult').className = 'alert alert-success';
                document.getElementById('encapsulateResult').textContent = 'Shared secret encapsulated successfully.';
                
                // Show details
                document.getElementById('encapsulateDetails').classList.remove('d-none');
                document.getElementById('ciphertext').value = data.ciphertext;
                document.getElementById('sharedSecret').value = data.shared_secret;
                document.getElementById('encapSchemeResult').textContent = data.scheme;
                document.getElementById('ciphertextSizeResult').textContent = `${data.ciphertext_size_bytes} bytes`;
                document.getElementById('encapTimeResult').textContent = `${data.time_ms.toFixed(2)} ms`;
                
                // Auto-populate decapsulate form
                if (document.getElementById('decapCiphertext')) {
                    document.getElementById('decapCiphertext').value = data.ciphertext;
                }
            } else {
                const error = await response.json();
                document.getElementById('encapsulateResult').className = 'alert alert-danger';
                document.getElementById('encapsulateResult').textContent = `Error: ${error.detail}`;
                document.getElementById('encapsulateDetails').classList.add('d-none');
            }
        } catch (error) {
            document.getElementById('encapsulateResult').className = 'alert alert-danger';
            document.getElementById('encapsulateResult').textContent = `Error: ${error.message}`;
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
        
        try {
            // Show loading state
            document.getElementById('decapsulateResult').className = 'alert alert-info';
            document.getElementById('decapsulateResult').textContent = 'Decapsulating shared secret...';
            
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
                document.getElementById('decapsulateResult').className = 'alert alert-success';
                document.getElementById('decapsulateResult').textContent = 'Shared secret decapsulated successfully.';
                
                // Show details
                document.getElementById('decapsulateDetails').classList.remove('d-none');
                document.getElementById('decapSharedSecret').value = data.shared_secret;
                document.getElementById('decapSchemeResult').textContent = data.scheme;
                document.getElementById('decapTimeResult').textContent = `${data.time_ms.toFixed(2)} ms`;
                
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
                document.getElementById('decapsulateResult').className = 'alert alert-danger';
                document.getElementById('decapsulateResult').textContent = `Error: ${error.detail}`;
                document.getElementById('decapsulateDetails').classList.add('d-none');
            }
        } catch (error) {
            document.getElementById('decapsulateResult').className = 'alert alert-danger';
            document.getElementById('decapsulateResult').textContent = `Error: ${error.message}`;
            document.getElementById('decapsulateDetails').classList.add('d-none');
        }
    });
} 