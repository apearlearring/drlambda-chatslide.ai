let currentCommand = '';
let isProcessing = false;

// Add loading state management
function setLoadingState(loading, message = 'Processing your request...') {
    isProcessing = loading;
    const overlay = document.querySelector('.loading-overlay');
    
    // Add null checks for all DOM elements
    const loadingText = overlay ? overlay.querySelector('.loading-text') : null;
    const uploadBtn = document.getElementById('uploadBtn');
    const sendBtn = document.getElementById('sendBtn');
    const fileInput = document.getElementById('fileInput');
    const commandInput = document.getElementById('commandInput');
    const leftPanel = document.querySelector('.left-panel');
    const rightPanel = document.querySelector('.right-panel');
    
    // Update loading message based on current command
    if (message === 'Generating chart...') {
        message = currentCommand ? 'Updating chart...' : 'Generating chart...';
    }
    
    if (loading) {
        // Show loading overlay with updated message
        if (overlay && loadingText) {
            loadingText.textContent = message;
            overlay.classList.add('active');
        }
        
        // Disable all interactive elements
        if (uploadBtn) uploadBtn.disabled = true;
        if (sendBtn) sendBtn.disabled = true;
        if (fileInput) fileInput.disabled = true;
        if (commandInput) commandInput.disabled = true;
        
        // Add disabled class to containers
        if (leftPanel) leftPanel.classList.add('disabled');
        if (rightPanel) rightPanel.classList.add('disabled');
        
        // Change cursor
        document.body.style.cursor = 'wait';
    } else {
        // Hide loading overlay
        if (overlay) overlay.classList.remove('active');
        
        // Enable all interactive elements
        if (uploadBtn) uploadBtn.disabled = false;
        if (sendBtn) sendBtn.disabled = false;
        if (fileInput) fileInput.disabled = false;
        if (commandInput) commandInput.disabled = false;
        
        // Remove disabled class
        if (leftPanel) leftPanel.classList.remove('disabled');
        if (rightPanel) rightPanel.classList.remove('disabled');
        
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
        alert('Please select a file');
        return;
    }
    
    try {
        setLoadingState(true, 'Uploading file...');
        showProgress(50);
        
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showProgress(100);
            displayDataPreview(data.preview);
            // Clear any previous candidate questions
            document.getElementById('candidateQuestionsContainer').innerHTML = '';
            // Reset current command since we're starting with new data
            currentCommand = '';
        } else {
            throw new Error(data.detail);
        }
    } catch (error) {
        console.error('Error uploading file:', error);
        alert('Error uploading file: ' + error.message);
    } finally {
        setLoadingState(false);
        hideProgress();
    }
});

// Function to display candidate questions
function displayCandidateQuestions(questions) {
    console.log('Displaying candidate questions:', questions);
    
    const container = document.getElementById('candidateQuestionsContainer');
    
    // Clear previous questions
    container.innerHTML = '';
    
    if (!questions || questions.length === 0) {
        console.log('No candidate questions to display');
        return;
    }
    
    // Add a heading
    const heading = document.createElement('h5');
    heading.textContent = 'Follow-up Questions:';
    heading.className = 'mt-3 mb-2';
    container.appendChild(heading);
    
    // Create a div for each question
    questions.forEach(question => {
        console.log('Adding question:', question);
        const questionDiv = document.createElement('div');
        questionDiv.className = 'candidate-question';
        questionDiv.textContent = question;
        
        // Add click event to send this question to the server
        questionDiv.addEventListener('click', () => {
            // Set the question in the input field
            const commandInput = document.getElementById('commandInput');
            commandInput.value = question;
            
            // Send the command
            sendCommand(question);
        });
        
        container.appendChild(questionDiv);
    });
}

// Command Handler
document.getElementById('sendBtn').addEventListener('click', async () => {
    if (isProcessing) return;
    
    const commandInput = document.getElementById('commandInput');
    const command = commandInput.value.trim();
    
    if (!command) {
        alert('Please enter a command');
        return;
    }
    
    await sendCommand(command);
});

// Function to send command to the server
async function sendCommand(command) {
    if (isProcessing) return;

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
            document.getElementById('commandInput').value = ''; // Clear input after success
            
            console.log('candidate questions:', data.candidate_questions);

            // Display candidate questions if available
            if (data.candidate_questions && data.candidate_questions.length > 0) {
                displayCandidateQuestions(data.candidate_questions);
            } else {
                // Clear candidate questions if none are returned
                document.getElementById('candidateQuestionsContainer').innerHTML = '';
            }
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
}

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
    
    // Log for debugging
    console.log('Setting chart path:', chartPath);
    
    // Make sure the path is absolute
    const absolutePath = chartPath.startsWith('/') ? chartPath : '/' + chartPath;
    chartFrame.src = absolutePath;
    
    // Add output path display
    const chartContainer = document.querySelector('.chart-container');
    let pathDisplay = chartContainer.querySelector('.output-path');
    
    if (!pathDisplay) {
        pathDisplay = document.createElement('div');
        pathDisplay.className = 'output-path';
        chartContainer.appendChild(pathDisplay);
    }
    
    pathDisplay.textContent = `Output Path: ${outputPath}`;
    
    // Log when the iframe loads
    chartFrame.onload = () => {
        console.log('Chart iframe loaded');
    };
} 