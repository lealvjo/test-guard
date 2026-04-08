// ===== REGISTER AUTOMATION - JavaScript específico =====

function backToHome() { 
    window.location.href = '/'; 
}

let selectedImageBase64 = null;

function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    processImageFile(file);
}

function processImageFile(file) {
    // Validar tipo de arquivo
    if (!file.type.startsWith('image/')) {
        showNotification('Erro de Validação', 'Por favor, selecione apenas arquivos de imagem.', 'error');
        document.getElementById('image').value = '';
        return;
    }

    // Validar tamanho (máximo 2MB)
    if (file.size > 2 * 1024 * 1024) {
        showNotification('Erro de Validação', 'A imagem deve ter no máximo 2MB.', 'error');
        document.getElementById('image').value = '';
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        selectedImageBase64 = e.target.result;
        document.getElementById('previewImg').src = e.target.result;
        document.getElementById('imagePreview').classList.add('show');
        
        // Atualizar o label para mostrar que foi selecionado
        const uploadLabel = document.getElementById('uploadLabel');
        uploadLabel.innerHTML = `
            <div class="file-upload-icon">✅</div>
            <div class="file-upload-text">Imagem selecionada!</div>
            <div class="file-upload-hint">Clique para trocar</div>
        `;
    };
    reader.readAsDataURL(file);
}

function removeImage() {
    selectedImageBase64 = null;
    document.getElementById('image').value = '';
    document.getElementById('imagePreview').classList.remove('show');
    
    // Restaurar o label original
    const uploadLabel = document.getElementById('uploadLabel');
    uploadLabel.innerHTML = `
        <div class="file-upload-icon">📁</div>
        <div class="file-upload-text">Clique para selecionar uma imagem</div>
        <div class="file-upload-hint">ou arraste e solte aqui</div>
    `;
}

function showNotification(title, message, type = 'success') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? '✅' : '❌';
    
    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    container.appendChild(toast);
    
    // Auto remove após 5 segundos
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}

// Drag & Drop functionality
document.addEventListener('DOMContentLoaded', function() {
    const uploadLabel = document.getElementById('uploadLabel');
    
    if (uploadLabel) {
        uploadLabel.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadLabel.classList.add('dragover');
        });
        
        uploadLabel.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadLabel.classList.remove('dragover');
        });
        
        uploadLabel.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadLabel.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                processImageFile(files[0]);
            }
        });
    }
});

