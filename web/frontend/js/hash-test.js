// DOM Elements
const algorithmSelector = document.getElementById('algorithmSelector');
const algorithmOptions = document.querySelectorAll('.algorithm-option');
const inputText = document.getElementById('inputText');
const encodingSelect = document.getElementById('encodingSelect');
const generateButton = document.getElementById('generateButton');
const hashOutput = document.getElementById('hashOutput');
const copyButton = document.getElementById('copyButton');
const saveButton = document.getElementById('saveButton');
const performanceTable = document.getElementById('performanceTable').querySelector('tbody');

// State variables
let selectedAlgorithm = null;
let lastGeneratedHash = null;
const performanceData = {};

// API URL
const API_URL = 'https://dirac-hashes.onrender.com';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Available hash algorithms
    const algorithms = [
        { id: 'improved', name: 'Dirac-Improved', description: 'Default quantum-resistant hash (256-bit)' },
        { id: 'grover', name: 'Dirac-Grover', description: 'Grover-inspired quantum-resistant hash' },
        { id: 'shor', name: 'Dirac-Shor', description: 'Shor-inspired quantum-resistant hash' },
        { id: 'dirac-256', name: 'Dirac-256', description: 'Original Dirac hash (256-bit)' },
        { id: 'sha256', name: 'SHA-256', description: 'Standard SHA-256 for comparison' }
    ];

    // DOM elements
    const algorithmOptions = document.getElementById('algorithm-options');
    const inputText = document.getElementById('input-text');
    const encodingSelect = document.getElementById('encoding-select');
    const generateButton = document.getElementById('generate-button');
    const resultCard = document.getElementById('result-card');
    const hashResult = document.getElementById('hash-result');
    const copyButton = document.getElementById('copy-button');
    const saveButton = document.getElementById('save-button');
    const performanceData = document.getElementById('performance-data');
    const notificationContainer = document.getElementById('notification-container');

    let selectedAlgorithm = null;
    let performanceResults = getPerformanceResultsFromStorage() || [];

    // Populate algorithm options
    algorithms.forEach(algo => {
        const algoEl = document.createElement('div');
        algoEl.className = 'algorithm-option';
        algoEl.dataset.algorithmId = algo.id;
        
        algoEl.innerHTML = `
            <div class="algorithm-name">${algo.name}</div>
            <div class="algorithm-description">${algo.description}</div>
        `;
        
        algoEl.addEventListener('click', () => {
            document.querySelectorAll('.algorithm-option').forEach(el => {
                el.classList.remove('selected');
            });
            algoEl.classList.add('selected');
            selectedAlgorithm = algo;
            updateGenerateButtonState();
        });
        
        algorithmOptions.appendChild(algoEl);
    });

    // Event listeners
    inputText.addEventListener('input', updateGenerateButtonState);
    
    generateButton.addEventListener('click', async () => {
        if (!selectedAlgorithm || !inputText.value.trim()) {
            return;
        }
        
        try {
            showLoading();
            const result = await generateHash();
            displayResult(result);
            savePerformanceResult(result);
            updatePerformanceTable();
            showNotification('Hash generated successfully', 'success');
        } catch (error) {
            console.error('Hash generation error:', error);
            showNotification('Error generating hash: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    });
    
    copyButton.addEventListener('click', () => {
        copyToClipboard();
    });
    
    saveButton.addEventListener('click', () => {
        saveHashAsFile();
    });
    
    // Functions
    function updateGenerateButtonState() {
        generateButton.disabled = !selectedAlgorithm || !inputText.value.trim();
    }
    
    async function generateHash() {
        const startTime = performance.now();
        
        const inputData = inputText.value;
        const encoding = encodingSelect.value;
        const algorithm = selectedAlgorithm.id;
        
        // Call the actual API
        const response = await fetch(`${API_URL}/api/hash/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: inputData,
                algorithm: algorithm,
                encoding: encoding
            })
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        const endTime = performance.now();
        const duration = endTime - startTime;
        
        return {
            algorithm: selectedAlgorithm.name,
            algorithmId: selectedAlgorithm.id,
            inputLength: new TextEncoder().encode(inputData).length,
            encoding,
            hashValue: data.hash,
            hashSize: data.hash.length * 4, // Approximate bit size from hex chars
            duration,
            date: new Date().toISOString()
        };
    }
    
    function displayResult(result) {
        resultCard.style.display = 'block';
        
        hashResult.innerHTML = `
            <div class="hash-info">
                <div class="hash-info-item">
                    <div class="hash-info-label">Algorithm</div>
                    <div class="hash-info-value">${result.algorithm}</div>
                </div>
                <div class="hash-info-item">
                    <div class="hash-info-label">Size</div>
                    <div class="hash-info-value">${result.hashSize} bits</div>
                </div>
                <div class="hash-info-item">
                    <div class="hash-info-label">Input Size</div>
                    <div class="hash-info-value">${result.inputLength} bytes</div>
                </div>
                <div class="hash-info-item">
                    <div class="hash-info-label">Encoding</div>
                    <div class="hash-info-value">${result.encoding}</div>
                </div>
                <div class="hash-info-item">
                    <div class="hash-info-label">Speed</div>
                    <div class="hash-info-value">${result.duration.toFixed(2)} ms</div>
                </div>
            </div>
            <div class="hash-value-container">
                <div class="hash-value-label">Hash Value (Hex):</div>
                <div class="hash-value" id="hash-value">${formatHashValue(result.hashValue)}</div>
            </div>
        `;
        
        // Scroll to result
        resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    function formatHashValue(hash) {
        // Format the hash value with spaces every 8 characters for readability
        return hash.match(/.{1,8}/g).join(' ');
    }
    
    function savePerformanceResult(result) {
        // Add to the beginning of the array
        performanceResults.unshift({
            algorithm: result.algorithm,
            algorithmId: result.algorithmId,
            hashSize: result.hashSize,
            duration: result.duration,
            date: result.date
        });
        
        // Keep only the last 20 results
        if (performanceResults.length > 20) {
            performanceResults.pop();
        }
        
        // Save to local storage
        localStorage.setItem('hashPerformanceResults', JSON.stringify(performanceResults));
    }
    
    function getPerformanceResultsFromStorage() {
        const stored = localStorage.getItem('hashPerformanceResults');
        return stored ? JSON.parse(stored) : null;
    }
    
    function updatePerformanceTable() {
        performanceData.innerHTML = '';
        
        performanceResults.forEach(result => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${result.algorithm}</td>
                <td>${result.hashSize} bits</td>
                <td>${result.duration.toFixed(2)} ms</td>
                <td>${new Date(result.date).toLocaleString()}</td>
            `;
            
            performanceData.appendChild(row);
        });
        
        if (performanceResults.length === 0) {
            const emptyRow = document.createElement('tr');
            emptyRow.innerHTML = '<td colspan="4" class="empty-table">No performance data yet</td>';
            performanceData.appendChild(emptyRow);
        }
    }
    
    function copyToClipboard() {
        const hashValue = document.getElementById('hash-value');
        if (!hashValue) return;
        
        const textToCopy = hashValue.textContent.replace(/\s/g, ''); // Remove spaces
        
        navigator.clipboard.writeText(textToCopy).then(() => {
            showNotification('Hash copied to clipboard', 'success');
        }).catch(err => {
            console.error('Error copying to clipboard:', err);
            showNotification('Failed to copy to clipboard', 'error');
        });
    }
    
    function saveHashAsFile() {
        const hashValue = document.getElementById('hash-value');
        if (!hashValue) return;
        
        const textToSave = hashValue.textContent.replace(/\s/g, '');
        const algorithm = selectedAlgorithm.name;
        const timestamp = new Date().toISOString().replace(/[:\.]/g, '-');
        const filename = `${algorithm}-hash-${timestamp}.txt`;
        
        const blob = new Blob([textToSave], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 0);
        
        showNotification('Hash saved to file', 'success');
    }
    
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        notificationContainer.appendChild(notification);
        
        // Trigger animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            notification.addEventListener('transitionend', () => {
                notificationContainer.removeChild(notification);
            });
        }, 3000);
    }
    
    function showLoading() {
        // Create loading element if it doesn't exist
        if (!document.getElementById('loading-spinner')) {
            const loading = document.createElement('div');
            loading.id = 'loading-spinner';
            loading.className = 'loading-spinner';
            loading.innerHTML = '<div class="spinner"></div>';
            document.body.appendChild(loading);
        }
        
        document.getElementById('loading-spinner').classList.add('show');
    }
    
    function hideLoading() {
        const loading = document.getElementById('loading-spinner');
        if (loading) {
            loading.classList.remove('show');
        }
    }
    
    // Initialize performance table
    updatePerformanceTable();
}); 