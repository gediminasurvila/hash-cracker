class HashDetector {
    constructor() {
        this.hashInput = document.getElementById('hashInput');
        this.detectButton = document.getElementById('detectButton');
        this.crackButton = document.getElementById('crackButton');
        this.clearButton = document.getElementById('clearButton');
        this.startCrackButton = document.getElementById('startCrackButton');
        this.crackOptions = document.getElementById('crackOptions');
        this.wordlistFile = document.getElementById('wordlistFile');
        this.fileInfo = document.getElementById('fileInfo');
        this.hashFormat = document.getElementById('hashFormat');
        this.resultSection = document.getElementById('resultSection');
        this.resultText = document.getElementById('resultText');
        
        this.init();
    }
    
    init() {
        this.detectButton.addEventListener('click', () => this.detectHash());
        this.crackButton.addEventListener('click', () => this.toggleCrackOptions());
        this.clearButton.addEventListener('click', () => this.clearAll());
        this.startCrackButton.addEventListener('click', () => this.crackHash());
        this.wordlistFile.addEventListener('change', (e) => this.handleFileSelect(e));
        
        this.hashInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                this.detectHash();
            }
        });
        
        // Add keyboard shortcut for clear (Escape key)
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.clearAll();
            }
        });
        
        // Auto-focus on hash input when page loads
        this.hashInput.focus();
    }
    
    toggleCrackOptions() {
        this.crackOptions.classList.toggle('hidden');
    }
    
    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            const size = (file.size / 1024 / 1024).toFixed(2);
            this.fileInfo.textContent = `Selected: ${file.name} (${size} MB)`;
        } else {
            this.fileInfo.textContent = '';
        }
    }
    
    async detectHash() {
        const hash = this.hashInput.value.trim();
        
        if (!hash) {
            this.showError('Please enter a hash to analyze');
            return;
        }
        
        this.setLoading('detect', true);
        this.hideResult();
        
        try {
            const response = await fetch('/api/detect-hash', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ hash: hash })
            });
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            
            const result = await response.json();
            this.displayDetectionResult(result);
            
        } catch (error) {
            console.error('Error:', error);
            this.showError('Failed to analyze hash. Please check your connection and try again.');
        } finally {
            this.setLoading('detect', false);
        }
    }
    
    async crackHash() {
        const hash = this.hashInput.value.trim();
        const file = this.wordlistFile.files[0];
        const format = this.hashFormat.value;
        
        if (!hash) {
            this.showError('Please enter a hash to crack');
            return;
        }
        
        if (!file) {
            this.showError('Please select a wordlist file');
            return;
        }
        
        this.setLoading('crack', true);
        this.hideResult();
        
        try {
            const formData = new FormData();
            formData.append('hash', hash);
            formData.append('wordlist', file);
            if (format) {
                formData.append('format', format);
            }
            
            const response = await fetch('/api/crack-hash', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            
            const result = await response.json();
            this.displayCrackResult(result);
            
        } catch (error) {
            console.error('Error:', error);
            this.showError('Failed to crack hash. Please check your connection and try again.');
        } finally {
            this.setLoading('crack', false);
        }
    }
    
    setLoading(buttonType, loading) {
        const buttons = {
            'detect': this.detectButton,
            'crack': this.startCrackButton
        };
        
        const button = buttons[buttonType];
        if (!button) return;
        
        const btnText = button.querySelector('.btn-text');
        const spinner = button.querySelector('.spinner');
        
        button.disabled = loading;
        this.hashInput.disabled = loading;
        
        if (loading) {
            btnText.classList.add('hidden');
            spinner.classList.remove('hidden');
        } else {
            btnText.classList.remove('hidden');
            spinner.classList.add('hidden');
        }
    }
    
    displayDetectionResult(result) {
        if (result.error) {
            this.showError(result.error);
            return;
        }
        
        let html = '<h3>Hash Type Detection</h3>';
        
        if (result.possible_types && result.possible_types.length > 0) {
            if (result.possible_types.length === 1) {
                const type = result.possible_types[0];
                html += `
                    <div class="hash-info">
                        <div class="hash-type">${type.algorithm}</div>
                        <div class="hash-details">
                            <strong>Length:</strong> ${type.length} characters<br>
                            <strong>Confidence:</strong> ${type.confidence}<br>
                            ${type.description ? `<strong>Description:</strong> ${type.description}` : ''}
                        </div>
                    </div>
                `;
            } else {
                html += '<div class="multiple-results">';
                result.possible_types.forEach(type => {
                    html += `
                        <div class="hash-option">
                            <div class="hash-type">${type.algorithm}</div>
                            <div class="hash-details">
                                Length: ${type.length} chars | Confidence: ${type.confidence}
                                ${type.description ? `<br>${type.description}` : ''}
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
            }
        } else {
            html += '<div class="error">Unable to determine hash type. The input may not be a valid hash.</div>';
        }
        
        this.resultText.innerHTML = html;
        this.showResult();
    }
    
    displayCrackResult(result) {
        if (result.error) {
            this.showError(result.error);
            return;
        }
        
        let html = '<h3>Hash Cracking Result</h3>';
        
        if (result.cracked) {
            html += `
                <div class="hash-info" style="border-left-color: #48bb78;">
                    <div class="hash-type" style="color: #48bb78;">✓ Hash Cracked Successfully!</div>
                    <div class="hash-details">
                        <strong>Original Hash:</strong> ${result.hash}<br>
                        <strong>Cracked Password:</strong> <code style="background: #e6fffa; padding: 4px 8px; border-radius: 4px; color: #2d3748;">${result.password}</code><br>
                        <strong>Hash Type:</strong> ${result.hash_type || 'Auto-detected'}<br>
                        <strong>Time Taken:</strong> ${result.time_taken || 'N/A'}<br>
                        <strong>Attempts:</strong> ${result.attempts || 'N/A'}
                    </div>
                </div>
            `;
        } else {
            html += `
                <div class="hash-info" style="border-left-color: #f56565;">
                    <div class="hash-type" style="color: #f56565;">✗ Hash Not Cracked</div>
                    <div class="hash-details">
                        <strong>Status:</strong> ${result.message || 'Password not found in wordlist'}<br>
                        <strong>Hash Type:</strong> ${result.hash_type || 'Auto-detected'}<br>
                        <strong>Time Taken:</strong> ${result.time_taken || 'N/A'}<br>
                        <strong>Attempts:</strong> ${result.attempts || 'N/A'}
                    </div>
                </div>
            `;
        }
        
        this.resultText.innerHTML = html;
        this.showResult();
    }
    
    showError(message) {
        this.resultText.innerHTML = `<div class="error">${message}</div>`;
        this.showResult();
    }
    
    showResult() {
        this.resultSection.classList.remove('hidden');
    }
    
    hideResult() {
        this.resultSection.classList.add('hidden');
    }
    
    clearAll() {
        // Clear hash input
        this.hashInput.value = '';
        
        // Hide crack options
        this.crackOptions.classList.add('hidden');
        
        // Clear wordlist file selection
        this.wordlistFile.value = '';
        this.fileInfo.textContent = '';
        
        // Reset hash format selection
        this.hashFormat.value = '';
        
        // Hide results
        this.hideResult();
        
        // Clear result content
        this.resultText.innerHTML = '';
        
        // Re-enable all inputs
        this.hashInput.disabled = false;
        this.detectButton.disabled = false;
        this.crackButton.disabled = false;
        this.startCrackButton.disabled = false;
        
        // Hide any loading spinners
        const spinners = document.querySelectorAll('.spinner');
        const btnTexts = document.querySelectorAll('.btn-text');
        
        spinners.forEach(spinner => spinner.classList.add('hidden'));
        btnTexts.forEach(btnText => btnText.classList.remove('hidden'));
        
        // Focus back on hash input
        this.hashInput.focus();
        
        // Show a brief success message
        this.showTemporaryMessage('✓ Cleared! Ready for another hash.', 'success');
    }
    
    showTemporaryMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `temp-message ${type}`;
        messageDiv.textContent = message;
        messageDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
            background: ${type === 'success' ? '#48bb78' : '#667eea'};
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        `;
        
        // Add animation keyframes if not already present
        if (!document.querySelector('#temp-message-styles')) {
            const style = document.createElement('style');
            style.id = 'temp-message-styles';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOut {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(messageDiv);
        
        // Remove message after 3 seconds
        setTimeout(() => {
            messageDiv.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.parentNode.removeChild(messageDiv);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new HashDetector();
});