// Upload Zone functionality
const uploadZone = document.getElementById('upload-zone');
const fileInput = document.getElementById('file-input');
const uploadProgress = document.getElementById('upload-progress');
const fileList = document.getElementById('file-list');
const cancelUpload = document.getElementById('cancel-upload');
const browseFilesBtn = document.getElementById('browse-files-btn');


// Add event listener for the Browse Files button
browseFilesBtn.addEventListener('click', (event) => {
    event.stopPropagation(); // Prevent the event from bubbling up to the upload zone
    fileInput.click();
});

// Prevent default drag behaviors
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    uploadZone.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
});

// Highlight drop zone when item is dragged over it
['dragenter', 'dragover'].forEach(eventName => {
    uploadZone.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    uploadZone.addEventListener(eventName, unhighlight, false);
});

// Handle dropped files
uploadZone.addEventListener('drop', handleDrop, false);
uploadZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFiles);

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight(e) {
    uploadZone.classList.add('dragover');
}

function unhighlight(e) {
    uploadZone.classList.remove('dragover');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles({target: {files}});
}

function handleFiles(e) {
    const files = [...e.target.files];
    if (files.length === 0) return;

    uploadProgress.classList.remove('hidden');
    files.forEach(file => createProgressItem(file)); // Show progress for each file
    uploadFiles(files); // Upload all files

    // Reset file input
    fileInput.value = '';
}

function createProgressItem(file) {
    // Create progress item
    const item = document.createElement('div');
    item.className = 'flex items-center space-x-4';
    item.innerHTML = `
        <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
            </svg>
        </div>
        <div class="flex-1">
            <div class="flex justify-between items-center mb-1">
                <span class="font-medium">${file.name}</span>
                <span class="text-sm text-gray-500 progress-text">0%</span>
            </div>
            <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div class="progress-bar h-full bg-blue-600 transition-all duration-300" style="width: 0%"></div>
            </div>
        </div>
    `;

    fileList.appendChild(item);

    // Simulate upload progress (for now)
    let progress = 0;
    const progressBar = item.querySelector('.progress-bar');
    const progressText = item.querySelector('.progress-text');

    const interval = setInterval(() => {
        progress += Math.random() * 10;
        if (progress > 100) progress = 100;

        progressBar.style.width = `${progress}%`;
        progressText.textContent = `${Math.round(progress)}%`;

        if (progress === 100) {
            clearInterval(interval);
            setTimeout(() => {
                gsap.to(item, {
                    opacity: 0,
                    y: -20,
                    duration: 0.5,
                    onComplete: () => {
                        item.remove();
                        if (!fileList.children.length) {
                            uploadProgress.classList.add('hidden');
                        }
                    }
                });
            }, 1000);
        }
    }, 200);
}

async function uploadFiles(files) {
    const formData = new FormData();
    files.forEach(file => {
        formData.append('files', file); // Use 'files' as the key to match backend
    });

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            // Show success message
            const successMessage = document.getElementById('success-message');
            successMessage.textContent = result.message;
            successMessage.classList.remove('hidden');

            // Optionally, hide success message after 5 seconds
            setTimeout(() => {
                successMessage.classList.add('hidden');
            }, 5000);
        } else {
            alert('Upload failed: ' + result.message);
        }
    } catch (error) {
        alert('Error uploading files: ' + error.message);
    }
}

// Cancel upload
cancelUpload.addEventListener('click', () => {
    gsap.to(uploadProgress, {
        opacity: 0,
        y: -20,
        duration: 0.5,
        onComplete: () => {
            uploadProgress.classList.add('hidden');
            uploadProgress.style.opacity = 1;
            uploadProgress.style.transform = 'none';
            fileList.innerHTML = '';
        }
    });
});

// GSAP Animations
gsap.from('#upload-zone', {
    y: 40,
    opacity: 0,
    duration: 1,
    ease: 'power3.out'
});

// Remove uploadImage function since we no longer need it