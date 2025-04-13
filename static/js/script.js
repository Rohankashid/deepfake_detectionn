const MAX_FILE_SIZE = 100 * 1024 * 1024;
const analyzeBtn = document.getElementById('analyzeBtn');
const loaderContainer = document.querySelector('.loader-container');
const resultContainer = document.getElementById('result-container');

function handleVideoSubmit(event) {
    event.preventDefault();
    const videoInput = document.getElementById('videoFile');
    const errorMessage = document.getElementById('error-message');
    const file = videoInput.files[0];

    if (file && file.size > MAX_FILE_SIZE) {
        errorMessage.style.display = 'block';
        videoInput.value = '';
        return;
    }

    errorMessage.style.display = 'none';
    
    if(file) {
        // Show loading states
        loaderContainer.style.display = 'flex';
        analyzeBtn.classList.add('is-loading');
        analyzeBtn.disabled = true;
        
        uploadVideo(file);
    }
}

function uploadVideo(file) {
    const formData = new FormData();
    formData.append('video', file);

    fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Hide loader
        loaderContainer.style.display = 'none';
        analyzeBtn.classList.remove('is-loading');
        analyzeBtn.disabled = false;

        if (data.status === 'success') {
            resultContainer.innerHTML = `<p>Analysis Complete: <strong>${data.prediction}</strong></p>`;
            resultContainer.style.display = 'block';
        } else {
            resultContainer.innerHTML = `<p style="color: red;">Error: ${data.message}</p>`;
            resultContainer.style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        loaderContainer.style.display = 'none';
        analyzeBtn.classList.remove('is-loading');
        analyzeBtn.disabled = false;
        resultContainer.innerHTML = `<p style="color: red;">Analysis failed. Please try again.</p>`;
        resultContainer.style.display = 'block';
    });
}
