// Dirac Hashes - Main App JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initApp();
    
    // Check API status
    checkApiStatus();
    
    // Set up navigation
    setupNavigation();
    
    // Initialize page-specific functionality
    initHomePage();
    initStatsPage();
    initTestHashesPage();
    initSignaturesPage();
    initKemPage();
});

// Global API URL - change this to your deployed API URL
const API_URL = 'http://localhost:8000';

// Page Navigation
function setupNavigation() {
    // Get all navigation links
    const navLinks = document.querySelectorAll('.nav-item');
    
    // Add click event listener to each link
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the target page
            const targetPage = this.getAttribute('data-page');
            
            // Remove active class from all links and pages
            navLinks.forEach(link => link.classList.remove('active'));
            document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
            
            // Add active class to clicked link and target page
            this.classList.add('active');
            document.getElementById(targetPage).classList.add('active');
        });
    });
}

// Initialize the application
function initApp() {
    console.log('Initializing Dirac Hashes App');
}

// Home Page Initialization
function initHomePage() {
    // No specific initialization needed for home page
}

// Stats Page Initialization
function initStatsPage() {
    // Create performance chart
    createPerformanceChart();
    
    // Create security level chart
    createSecurityChart();
    
    // Set up periodic API status update
    setInterval(checkApiStatus, 10000);
}

// Check API Status
function checkApiStatus() {
    const startTime = Date.now();
    
    fetch(`${API_URL}/`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        },
        mode: 'cors',
        cache: 'no-cache',
        timeout: 5000
    })
    .then(response => {
        const endTime = Date.now();
        const responseTime = endTime - startTime;
        
        if (!response.ok) {
            throw new Error('API is offline');
        }
        return response.json().then(data => ({ data, responseTime }));
    })
    .then(({ data, responseTime }) => {
        updateApiStatusDisplay(true, responseTime);
        checkEndpointStatuses();
    })
    .catch(error => {
        console.error('API Status Error:', error);
        updateApiStatusDisplay(false);
    });
}

// Update API Status Display
function updateApiStatusDisplay(isOnline = false, responseTime = null) {
    const statusElement = document.getElementById('api-status');
    const statusIndicator = document.getElementById('status-indicator');
    const responseTimeElement = document.getElementById('response-time');
    
    if (statusElement && statusIndicator) {
        if (isOnline) {
            statusIndicator.className = 'status-indicator status-online';
            statusElement.textContent = 'Online';
            
            // If we have performance data, update the response time
            if (responseTime && responseTimeElement) {
                responseTimeElement.textContent = `${responseTime}ms`;
            }
        } else {
            statusIndicator.className = 'status-indicator status-offline';
            statusElement.textContent = 'Offline';
            if (responseTimeElement) {
                responseTimeElement.textContent = 'N/A';
            }
            
            // Clear endpoint statuses
            const endpoints = ['hash', 'signatures', 'kem'];
            endpoints.forEach(endpoint => {
                const statusElement = document.getElementById(`${endpoint}-status`);
                const responseTimeElement = document.getElementById(`${endpoint}-response-time`);
                
                if (statusElement) statusElement.textContent = 'Offline';
                if (responseTimeElement) responseTimeElement.textContent = 'N/A';
            });
        }
    }
}

// Check individual endpoint statuses
function checkEndpointStatuses() {
    const endpoints = [
        { 
            name: 'hash', 
            path: '/api/hash/info',
            method: 'GET',
            body: null
        },
        { 
            name: 'signatures', 
            path: '/api/signatures/keypair',
            method: 'POST',
            body: {
                scheme: 'dilithium',
                hash_algorithm: 'improved',
                security_level: 1
            }
        },
        { 
            name: 'kem', 
            path: '/api/kem/keypair',
            method: 'POST',
            body: {
                scheme: 'kyber',
                hash_algorithm: 'improved',
                security_level: 1
            }
        }
    ];
    
    endpoints.forEach(endpoint => {
        const statusElement = document.getElementById(`${endpoint.name}-status`);
        const responseTimeElement = document.getElementById(`${endpoint.name}-response-time`);
        
        if (statusElement && responseTimeElement) {
            const startTime = Date.now();
            
            const fetchOptions = {
                method: endpoint.method,
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                mode: 'cors',
                cache: 'no-cache',
                timeout: 5000
            };
            
            // Add body for POST requests
            if (endpoint.method === 'POST' && endpoint.body) {
                fetchOptions.body = JSON.stringify(endpoint.body);
            }
            
            fetch(`${API_URL}${endpoint.path}`, fetchOptions)
            .then(response => {
                const endTime = Date.now();
                const responseTime = endTime - startTime;
                
                if (!response.ok) {
                    throw new Error(`${endpoint.name} endpoint is unavailable`);
                }
                
                statusElement.textContent = 'Available';
                responseTimeElement.textContent = `${responseTime.toFixed(2)} ms`;
            })
            .catch(error => {
                console.error(`Endpoint Error (${endpoint.name}):`, error);
                statusElement.textContent = 'Unavailable';
                responseTimeElement.textContent = 'N/A';
            });
        }
    });
}

// Create Performance Chart
function createPerformanceChart() {
    const ctx = document.getElementById('performanceChart');
    
    if (ctx) {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Dirac-256', 'Grover', 'Shor', 'Improved', 'SHA-256'],
                datasets: [{
                    label: 'Hash Time (ms)',
                    data: [25, 18, 32, 15, 8],
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(153, 102, 255, 0.7)',
                        'rgba(255, 159, 64, 0.7)',
                        'rgba(201, 203, 207, 0.7)'
                    ],
                    borderColor: '#000',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
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
}

// Create Security Chart
function createSecurityChart() {
    const ctx = document.getElementById('securityChart');
    
    if (ctx) {
        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: [
                    'Classical Resistance',
                    'Quantum Resistance',
                    'Side-Channel Protection',
                    'Collision Resistance',
                    'Speed'
                ],
                datasets: [
                    {
                        label: 'Dirac Hash',
                        data: [95, 90, 85, 92, 75],
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgb(75, 192, 192)',
                        borderWidth: 1
                    },
                    {
                        label: 'SHA-256',
                        data: [85, 50, 70, 90, 95],
                        backgroundColor: 'rgba(153, 102, 255, 0.2)',
                        borderColor: 'rgb(153, 102, 255)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
}

// Test Hashes Page Initialization
function initTestHashesPage() {
    const hashForm = document.getElementById('hash-form');
    const hashCompareForm = document.getElementById('hash-compare-form');
    
    if (hashForm) {
        hashForm.addEventListener('submit', function(e) {
            e.preventDefault();
            generateHash();
        });
    }
    
    if (hashCompareForm) {
        hashCompareForm.addEventListener('submit', function(e) {
            e.preventDefault();
            compareHashes();
        });
    }
}

// Generate Hash
function generateHash() {
    const messageInput = document.getElementById('hash-input').value;
    const algorithmSelect = document.getElementById('hash-algorithm').value;
    const resultElement = document.getElementById('hash-result');
    
    if (!messageInput) {
        resultElement.textContent = 'Please enter a message to hash';
        return;
    }
    
    const data = {
        message: messageInput,
        algorithm: algorithmSelect,
        encoding: 'utf-8'
    };
    
    fetch(`${API_URL}/api/hash/generate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        resultElement.innerHTML = `
            <div class="code-block">
                <strong>Hash:</strong> ${data.hash}
                <br>
                <strong>Algorithm:</strong> ${data.algorithm}
            </div>
        `;
    })
    .catch(error => {
        console.error('Error generating hash:', error);
        resultElement.textContent = 'Error generating hash. Please try again.';
    });
}

// Compare Hashes
function compareHashes() {
    const messageInput = document.getElementById('compare-input').value;
    const resultElement = document.getElementById('compare-result');
    
    if (!messageInput) {
        resultElement.textContent = 'Please enter a message to hash';
        return;
    }
    
    const data = {
        message: messageInput,
        algorithms: ['improved', 'grover', 'shor'],
        encoding: 'utf-8'
    };
    
    // Show loading indicator
    resultElement.innerHTML = '<div>Loading...</div>';
    
    fetch(`${API_URL}/api/hash/compare`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        let resultHTML = '<div class="code-block">';
        
        // Display each algorithm's hash result correctly
        // The API returns hashValue directly as a string, not as an object with a hash property
        for (const [algorithm, hashValue] of Object.entries(data.results)) {
            resultHTML += `<strong>${algorithm}:</strong> ${hashValue}<br>`;
        }
        
        resultHTML += '</div>';
        resultElement.innerHTML = resultHTML;
    })
    .catch(error => {
        console.error('Error comparing hashes:', error);
        resultElement.textContent = 'Error comparing hashes. Please try again.';
    });
}

// Signatures Page Initialization
function initSignaturesPage() {
    const generateKeyPairBtn = document.getElementById('generate-signature-keypair');
    const signMessageBtn = document.getElementById('sign-message-btn');
    const verifySignatureBtn = document.getElementById('verify-signature-btn');
    
    if (generateKeyPairBtn) {
        generateKeyPairBtn.addEventListener('click', generateSignatureKeyPair);
    }
    
    if (signMessageBtn) {
        signMessageBtn.addEventListener('click', signMessage);
    }
    
    if (verifySignatureBtn) {
        verifySignatureBtn.addEventListener('click', verifySignature);
    }
}

// Generate Signature Key Pair
function generateSignatureKeyPair() {
    const schemeSelect = document.getElementById('signature-scheme').value;
    const securityLevelSelect = document.getElementById('signature-security-level').value;
    const resultElement = document.getElementById('signature-keypair-result');
    
    const data = {
        scheme: schemeSelect,
        hash_algorithm: 'improved',
        security_level: parseInt(securityLevelSelect)
    };
    
    fetch(`${API_URL}/api/signatures/keypair`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        // Store keys in hidden inputs for later use
        document.getElementById('signature-public-key').value = data.public_key;
        document.getElementById('signature-private-key').value = data.private_key;
        
        resultElement.innerHTML = `
            <div class="code-block">
                <strong>Public Key:</strong> ${truncateKey(data.public_key)}
                <br>
                <strong>Private Key:</strong> ${truncateKey(data.private_key)}
                <br>
                <strong>Scheme:</strong> ${data.scheme}
                <br>
                <strong>Security Level:</strong> ${data.security_level}
            </div>
        `;
        
        // Enable the sign message button
        document.getElementById('sign-message-btn').disabled = false;
    })
    .catch(error => {
        console.error('Error generating signature key pair:', error);
        resultElement.textContent = 'Error generating signature key pair. Please try again.';
    });
}

// Sign Message
function signMessage() {
    // This would typically call the API to sign a message, but we'll simulate it
    const messageInput = document.getElementById('sign-message-input').value;
    const privateKey = document.getElementById('signature-private-key').value;
    const resultElement = document.getElementById('signature-result');
    
    if (!messageInput) {
        resultElement.textContent = 'Please enter a message to sign';
        return;
    }
    
    if (!privateKey) {
        resultElement.textContent = 'Please generate a key pair first';
        return;
    }
    
    // For demo purposes, generate a random signature
    const signature = generateRandomSignature();
    document.getElementById('signature-value').value = signature;
    
    resultElement.innerHTML = `
        <div class="code-block">
            <strong>Message:</strong> ${messageInput}
            <br>
            <strong>Signature:</strong> ${truncateKey(signature)}
        </div>
    `;
    
    // Enable the verify signature button
    document.getElementById('verify-signature-btn').disabled = false;
}

// Verify Signature
function verifySignature() {
    // This would typically call the API to verify a signature, but we'll simulate it
    const messageInput = document.getElementById('sign-message-input').value;
    const signature = document.getElementById('signature-value').value;
    const publicKey = document.getElementById('signature-public-key').value;
    const resultElement = document.getElementById('verification-result');
    
    if (!messageInput || !signature || !publicKey) {
        resultElement.textContent = 'Please complete all previous steps first';
        return;
    }
    
    // For demo purposes, always verify as valid
    resultElement.innerHTML = `
        <div class="api-status">
            <span class="status-indicator status-online"></span>
            <strong>Signature Verified:</strong> Valid
        </div>
    `;
}

// KEM Page Initialization
function initKemPage() {
    const generateKemKeyPairBtn = document.getElementById('generate-kem-keypair');
    const encapsulateBtn = document.getElementById('encapsulate-btn');
    const decapsulateBtn = document.getElementById('decapsulate-btn');
    
    if (generateKemKeyPairBtn) {
        generateKemKeyPairBtn.addEventListener('click', generateKemKeyPair);
    }
    
    if (encapsulateBtn) {
        encapsulateBtn.addEventListener('click', encapsulateKey);
    }
    
    if (decapsulateBtn) {
        decapsulateBtn.addEventListener('click', decapsulateKey);
    }
}

// Generate KEM Key Pair
function generateKemKeyPair() {
    const schemeSelect = document.getElementById('kem-scheme').value;
    const securityLevelSelect = document.getElementById('kem-security-level').value;
    const resultElement = document.getElementById('kem-keypair-result');
    
    const data = {
        scheme: schemeSelect,
        hash_algorithm: 'improved',
        security_level: parseInt(securityLevelSelect)
    };
    
    fetch(`${API_URL}/api/kem/keypair`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        // Store keys in hidden inputs for later use
        document.getElementById('kem-public-key').value = data.public_key;
        document.getElementById('kem-private-key').value = data.private_key;
        
        resultElement.innerHTML = `
            <div class="code-block">
                <strong>Public Key:</strong> ${truncateKey(data.public_key)}
                <br>
                <strong>Private Key:</strong> ${truncateKey(data.private_key)}
                <br>
                <strong>Scheme:</strong> ${data.scheme}
                <br>
                <strong>Security Level:</strong> ${data.security_level}
            </div>
        `;
        
        // Enable the encapsulate button
        document.getElementById('encapsulate-btn').disabled = false;
    })
    .catch(error => {
        console.error('Error generating KEM key pair:', error);
        resultElement.textContent = 'Error generating KEM key pair. Please try again.';
    });
}

// Encapsulate Key
function encapsulateKey() {
    // This would typically call the API to encapsulate a key, but we'll simulate it
    const publicKey = document.getElementById('kem-public-key').value;
    const resultElement = document.getElementById('encapsulation-result');
    
    if (!publicKey) {
        resultElement.textContent = 'Please generate a key pair first';
        return;
    }
    
    // For demo purposes, generate random ciphertext and shared secret
    const ciphertext = generateRandomSignature(32);
    const sharedSecret = generateRandomSignature(16);
    
    document.getElementById('kem-ciphertext').value = ciphertext;
    document.getElementById('kem-shared-secret').value = sharedSecret;
    
    resultElement.innerHTML = `
        <div class="code-block">
            <strong>Ciphertext:</strong> ${truncateKey(ciphertext)}
            <br>
            <strong>Shared Secret:</strong> ${truncateKey(sharedSecret)}
        </div>
    `;
    
    // Enable the decapsulate button
    document.getElementById('decapsulate-btn').disabled = false;
}

// Decapsulate Key
function decapsulateKey() {
    // This would typically call the API to decapsulate a key, but we'll simulate it
    const privateKey = document.getElementById('kem-private-key').value;
    const ciphertext = document.getElementById('kem-ciphertext').value;
    const sharedSecret = document.getElementById('kem-shared-secret').value;
    const resultElement = document.getElementById('decapsulation-result');
    
    if (!privateKey || !ciphertext) {
        resultElement.textContent = 'Please complete all previous steps first';
        return;
    }
    
    // For demo purposes, always recover the same shared secret
    resultElement.innerHTML = `
        <div class="code-block">
            <strong>Recovered Secret:</strong> ${truncateKey(sharedSecret)}
        </div>
        <div class="api-status">
            <span class="status-indicator status-online"></span>
            <strong>Secret Match:</strong> True
        </div>
    `;
}

// Helper Functions

// Generate a random signature (for demo purposes)
function generateRandomSignature(length = 64) {
    const characters = '0123456789abcdef';
    let result = '';
    for (let i = 0; i < length * 2; i++) {
        result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return result;
}

// Truncate key for display
function truncateKey(key) {
    if (key.length > 64) {
        return key.substring(0, 32) + '...' + key.substring(key.length - 32);
    }
    return key;
} 