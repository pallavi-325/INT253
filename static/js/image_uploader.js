/**
 * CareNest Medical Image Previewer & Validator
 */

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('id_image');
    const previewContainer = document.getElementById('image-preview-container');
    const previewImage = document.getElementById('image-preview');
    const previewInfo = document.getElementById('image-preview-info');

    if (!fileInput || !previewContainer || !previewImage) return;

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) {
            previewContainer.classList.add('hidden');
            return;
        }

        // Validate client size limit (10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert('Selected file is too large! Maximum image size is 10MB.');
            fileInput.value = '';
            previewContainer.classList.add('hidden');
            return;
        }

        const reader = new FileReader();
        reader.onload = (event) => {
            previewImage.src = event.target.result;
            
            const tempImg = new Image();
            tempImg.src = event.target.result;
            tempImg.onload = () => {
                const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
                if (previewInfo) {
                    previewInfo.textContent = `Dimensions: ${tempImg.width} x ${tempImg.height}px · File size: ${sizeMB} MB`;
                }
                if (tempImg.width < 400 || tempImg.height < 400) {
                    alert('Warning: Image resolution is lower than recommended (400x400px). The doctor may ask for a clearer photo.');
                }
            };
            
            previewContainer.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    });
});

