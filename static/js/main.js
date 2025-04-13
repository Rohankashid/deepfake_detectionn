// Video preview functionality
function previewVideo(input) {
    const preview = document.getElementById('video-preview');
    const previewContainer = document.querySelector('.video-preview-container');
    const file = input.files[0];
    
    if (file) {
        const url = URL.createObjectURL(file);
        preview.src = url;
        previewContainer.style.display = 'block';
        preview.style.display = 'block';
        
        // Add event listeners for video loading
        preview.onloadedmetadata = function() {
            preview.play();
        };
        
        preview.onerror = function() {
            console.error('Error loading video');
            previewContainer.style.display = 'none';
        };
    }
}

// Upload and analyze video
async function uploadVideo() {
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    const resultDiv = document.getElementById('result');
    const loader = document.getElementById('loader');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    
    if (!file) {
        resultDiv.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-circle"></i>
                <p>Please select a video file first.</p>
            </div>
        `;
        return;
    }
    
    // Show loading state
    loader.style.display = 'block';
    progressContainer.style.display = 'block';
    resultDiv.innerHTML = '';
    
    // Simulate progress
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 5;
        if (progress <= 90) {
            progressBar.style.width = `${progress}%`;
        }
    }, 300);
    
    const formData = new FormData();
    formData.append('video', file);
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        // Complete progress bar
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        
        // Hide loader and progress bar after a short delay
        setTimeout(() => {
            loader.style.display = 'none';
            progressContainer.style.display = 'none';
            
            if (data.error) {
                resultDiv.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-circle"></i>
                        <p>${data.error}</p>
                    </div>
                `;
            } else {
                displayAnalysisResults(data);
            }
        }, 500);
    } catch (error) {
        clearInterval(progressInterval);
        loader.style.display = 'none';
        progressContainer.style.display = 'none';
        resultDiv.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-circle"></i>
                <p>Error uploading file. Please try again.</p>
            </div>
        `;
    }
}

// Display analysis results
function displayAnalysisResults(data) {
    const resultDiv = document.getElementById('result');
    
    // Create the analysis results HTML
    const analysisHTML = `
        <div class="analysis-results">
            <div class="analysis-header">
                <h3>Analysis Results</h3>
                <div class="analysis-score ${data.is_deepfake ? 'deepfake' : 'authentic'}">
                    ${data.is_deepfake ? 'Deepfake Detected' : 'Authentic Video'}
                </div>
            </div>
            
            <div class="confidence-section">
                <h4>Confidence Score</h4>
                <div class="confidence-meter">
                    <div class="confidence-bar" style="width: ${data.confidence_score * 100}%"></div>
                </div>
                <div class="confidence-value">${(data.confidence_score * 100).toFixed(2)}%</div>
            </div>

            <div class="analysis-details">
                <div class="detail-card">
                    <h4>Video Metadata</h4>
                    <div class="detail-value">
                        <p>Duration: ${data.metadata.duration.toFixed(2)}s</p>
                        <p>Resolution: ${data.metadata.width}x${data.metadata.height}</p>
                        <p>FPS: ${data.metadata.fps}</p>
                    </div>
                </div>
                
                <div class="detail-card">
                    <h4>Analysis Summary</h4>
                    <div class="detail-value">
                        <p>Lighting Consistency: ${(data.analysis_summary.lighting_consistency * 100).toFixed(2)}%</p>
                        <p>Motion Consistency: ${(data.analysis_summary.motion_consistency * 100).toFixed(2)}%</p>
                        <p>Face Detection Stability: ${(data.analysis_summary.face_detection_stability * 100).toFixed(2)}%</p>
                    </div>
                </div>

                <div class="detail-card">
                    <h4>Processing Details</h4>
                    <div class="detail-value">
                        <p>Processing Time: ${data.processing_time.toFixed(2)}s</p>
                        <p>Frames Analyzed: ${data.frame_analysis.length}</p>
                        <p>Processing Efficiency: ${data.analysis_summary.processing_efficiency.toFixed(2)} fps</p>
                    </div>
                </div>
            </div>

            <div class="visualization-section">
                <h4>Analysis Visualization</h4>
                <img src="data:image/png;base64,${data.visualization}" alt="Analysis Visualization" class="analysis-chart">
            </div>

            <button class="detailed-report-btn" onclick="showDetailedReport(${JSON.stringify(data)})">
                View Detailed Report
            </button>
        </div>
    `;

    resultDiv.innerHTML = analysisHTML;
}

// Show detailed report
function showDetailedReport(data) {
    const resultDiv = document.getElementById('result');
    const currentContent = resultDiv.innerHTML;
    
    const detailedReportHTML = `
        <div class="detailed-report">
            <div class="report-header">
                <h3>Detailed Analysis Report</h3>
                <button class="back-btn" onclick="document.getElementById('result').innerHTML = \`${currentContent}\`">
                    Back to Summary
                </button>
            </div>
            
            <div class="report-section">
                <h4>Analysis Conclusion</h4>
                <div class="conclusion-text">
                    ${generateConclusionText(data)}
                </div>
            </div>

            <div class="report-section">
                <h4>Parameter Analysis</h4>
                <div class="parameter-analysis">
                    ${generateParameterAnalysis(data)}
                </div>
            </div>

            <div class="report-section">
                <h4>Frame-by-Frame Analysis</h4>
                <div class="frame-grid">
                    ${data.frame_analysis.map(frame => `
                        <div class="frame-card">
                            <div class="frame-header">Frame ${frame.frame_idx}</div>
                            <div class="frame-details">
                                <p>Time: ${frame.timestamp.toFixed(2)}s</p>
                                <p>Faces: ${frame.face_count}</p>
                                <p>Lighting: ${(frame.lighting_score * 100).toFixed(2)}%</p>
                                <p>Motion: ${(frame.motion_score * 100).toFixed(2)}%</p>
                                <p>Consistency: ${(frame.consistency_score * 100).toFixed(2)}%</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;

    resultDiv.innerHTML = detailedReportHTML;
}

// Generate conclusion text
function generateConclusionText(data) {
    const isDeepfake = data.is_deepfake;
    const confidence = data.confidence_score * 100;
    const lighting = data.analysis_summary.lighting_consistency * 100;
    const motion = data.analysis_summary.motion_consistency * 100;
    const faceStability = data.analysis_summary.face_detection_stability * 100;

    let conclusion = `
        <p class="conclusion-main">
            This video has been determined to be <strong>${isDeepfake ? 'a deepfake' : 'authentic'}</strong> 
            with ${confidence.toFixed(2)}% confidence.
        </p>
    `;

    if (isDeepfake) {
        conclusion += `
            <p class="conclusion-details">
                The analysis indicates several inconsistencies that suggest this is a deepfake:
                ${lighting < 80 ? `<br>- Lighting inconsistencies (${lighting.toFixed(2)}% consistency)` : ''}
                ${motion < 80 ? `<br>- Unnatural motion patterns (${motion.toFixed(2)}% consistency)` : ''}
                ${faceStability < 80 ? `<br>- Unstable face detection (${faceStability.toFixed(2)}% stability)` : ''}
            </p>
        `;
    } else {
        conclusion += `
            <p class="conclusion-details">
                The analysis shows consistent patterns typical of authentic videos:
                ${lighting > 80 ? `<br>- Natural lighting patterns (${lighting.toFixed(2)}% consistency)` : ''}
                ${motion > 80 ? `<br>- Natural motion flow (${motion.toFixed(2)}% consistency)` : ''}
                ${faceStability > 80 ? `<br>- Stable face detection (${faceStability.toFixed(2)}% stability)` : ''}
            </p>
        `;
    }

    return conclusion;
}

// Generate parameter analysis
function generateParameterAnalysis(data) {
    const parameters = [
        {
            name: 'Lighting Consistency',
            value: data.analysis_summary.lighting_consistency * 100,
            threshold: 80,
            description: 'Measures the consistency of lighting across frames'
        },
        {
            name: 'Motion Consistency',
            value: data.analysis_summary.motion_consistency * 100,
            threshold: 80,
            description: 'Analyzes the natural flow of motion between frames'
        },
        {
            name: 'Face Detection Stability',
            value: data.analysis_summary.face_detection_stability * 100,
            threshold: 80,
            description: 'Evaluates the stability of face detection across frames'
        }
    ];

    return `
        <div class="parameter-grid">
            ${parameters.map(param => `
                <div class="parameter-card ${param.value >= param.threshold ? 'good' : 'warning'}">
                    <h5>${param.name}</h5>
                    <div class="parameter-value">${param.value.toFixed(2)}%</div>
                    <div class="parameter-description">${param.description}</div>
                    <div class="parameter-status">
                        ${param.value >= param.threshold ? '✓ Within normal range' : '⚠ Below expected range'}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// Add drag and drop functionality
document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.querySelector('.upload-area');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults (e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        uploadArea.classList.add('highlight');
    }

    function unhighlight(e) {
        uploadArea.classList.remove('highlight');
    }

    uploadArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        const fileInput = document.getElementById('file-input');
        fileInput.files = files;
        previewVideo(fileInput);
    }
}); 