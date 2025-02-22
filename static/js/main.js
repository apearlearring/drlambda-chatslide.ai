let currentCommand = '';
let isProcessing = false;

// Add loading state management
function setLoadingState(loading, message = 'Processing your request...') {
    isProcessing = loading;
    const overlay = document.querySelector('.loading-overlay');
    const loadingText = overlay.querySelector('.loading-text');
    const uploadBtn = document.getElementById('uploadBtn');
    const sendBtn = document.getElementById('sendBtn');
    const fileInput = document.getElementById('fileInput');
    const commandInput = document.getElementById('commandInput');
    
    // Update loading message based on current command
    if (message === 'Generating chart...') {
        message = currentCommand ? 'Updating chart...' : 'Generating chart...';
    }
    
    if (loading) {
        // Show loading overlay with updated message
        loadingText.textContent = message;
        overlay.classList.add('active');
        
        // Disable all interactive elements
        uploadBtn.disabled = true;
        sendBtn.disabled = true;
        fileInput.disabled = true;
        commandInput.disabled = true;
        
        // Add disabled class to containers
        document.querySelector('.left-panel').classList.add('disabled');
        document.querySelector('.right-panel').classList.add('disabled');
        
        // Change cursor
        document.body.style.cursor = 'wait';
    } else {
        // Hide loading overlay
        overlay.classList.remove('active');
        
        // Enable all interactive elements
        uploadBtn.disabled = false;
        sendBtn.disabled = false;
        fileInput.disabled = false;
        commandInput.disabled = false;
        
        // Remove disabled class
        document.querySelector('.left-panel').classList.remove('disabled');
        document.querySelector('.right-panel').classList.remove('disabled');
        
        // Restore cursor
        document.body.style.cursor = 'default';
    }
}

// File Upload Handler
document.getElementById('uploadBtn').addEventListener('click', async () => {
    if (isProcessing) return;
    
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a file first');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Add file content logging
    const reader = new FileReader();
    reader.onload = function(e) {
        console.log('File content:', e.target.result);
    };
    reader.readAsText(file);
    
    console.log('File object:', file);

    try {
        setLoadingState(true, 'Uploading file...');
        showProgress(30);
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        console.log(data)
        if (data.status === 'success') {
            showProgress(100);
            displayDataPreview(data.preview);
        } else {
            throw new Error(data.detail);
        }
    } catch (error) {
        alert('Error uploading file: ' + error.message);
    } finally {
        setLoadingState(false);
        hideProgress();
    }
});

// Command Handler
document.getElementById('sendBtn').addEventListener('click', async () => {
    if (isProcessing) return;
    
    const commandInput = document.getElementById('commandInput');
    const command = commandInput.value.trim();
    
    if (!command) {
        alert('Please enter a command');
        return;
    }
    
    try {
        setLoadingState(true, 'Generating chart...');
        showProgress(30);
        const endpoint = currentCommand ? '/update' : '/process';
        
        console.log('Sending command to:', endpoint);
        console.log('Command:', command);

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `command=${encodeURIComponent(command)}`
        });
        
        const data = await response.json();
        console.log('Response:', data);
        
        if (data.status === 'success') {
            showProgress(100);
            displayChart(data.chart_path, data.output_path);
            currentCommand = command;
            commandInput.value = ''; // Clear input after success
        } else {
            throw new Error(data.detail);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error processing command: ' + error.message);
    } finally {
        setLoadingState(false);
        hideProgress();
    }
});

// Add keyboard event listener for command input
document.getElementById('commandInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !isProcessing) {
        document.getElementById('sendBtn').click();
    }
});

// Helper Functions
function showProgress(percent) {
    const progressBar = document.getElementById('progressBar');
    progressBar.classList.remove('d-none');
    progressBar.querySelector('.progress-bar').style.width = `${percent}%`;
}

function hideProgress() {
    const progressBar = document.getElementById('progressBar');
    progressBar.classList.add('d-none');
}

function displayDataPreview(preview) {
    const previewElement = document.getElementById('dataPreview');
    previewElement.innerHTML = `<pre>${JSON.stringify(preview, null, 2)}</pre>`;
}

function displayChart(chartPath, outputPath) {
    const chartFrame = document.getElementById('chartFrame');
    chartFrame.src = chartPath;
    
    // Add output path display
    const chartContainer = document.querySelector('.chart-container');
    let pathDisplay = chartContainer.querySelector('.output-path');
    
    if (!pathDisplay) {
        pathDisplay = document.createElement('div');
        pathDisplay.className = 'output-path';
        chartContainer.appendChild(pathDisplay);
    }
    
    pathDisplay.textContent = `Output Path: ${outputPath}`;
} 