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
    if (!file.type.startsWith('image/')) {
        showNotification('Erro de Validação', 'Por favor, selecione apenas arquivos de imagem.', 'error');
        document.getElementById('image').value = '';
        return;
    }

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

    const uploadLabel = document.getElementById('uploadLabel');
    uploadLabel.innerHTML = `
        <div class="file-upload-icon">📁</div>
        <div class="file-upload-text">Clique para selecionar uma imagem</div>
        <div class="file-upload-hint">ou arraste e solte aqui</div>
    `;
}

function setupDragAndDrop() {
    const uploadLabel = document.getElementById('uploadLabel');
    if (!uploadLabel) return;

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
    `;

    container.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 100);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (container.contains(toast)) {
                container.removeChild(toast);
            }
        }, 300);
    }, 5000);
}

async function submitAutomation(event) {
    event.preventDefault();

    const cucumberInput = document.querySelector('input[name="cucumber"]:checked');
    const payload = {
        name: document.getElementById('name').value.trim(),
        squad: document.getElementById('squad').value.trim(),
        type: document.getElementById('type').value,
        description: document.getElementById('description').value.trim(),
        language: document.getElementById('language').value.trim(),
        cucumber: cucumberInput ? cucumberInput.value : '',
        launch_date: document.getElementById('launch_date').value,
        git: document.getElementById('git').value.trim(),
        image_base64: selectedImageBase64
    };

    const required = ['name', 'squad', 'type', 'description', 'language', 'cucumber', 'launch_date', 'git'];
    for (const key of required) {
        if (!payload[key]) {
            showNotification('Erro de Validação', 'Preencha todos os campos obrigatórios.', 'error');
            return;
        }
    }

    const allowedTypes = ['Frontend', 'Backend', 'Mobile'];
    if (!allowedTypes.includes(payload.type)) {
        showNotification('Erro de Validação', `Tipo '${payload.type}' não é válido. Tipos permitidos: ${allowedTypes.join(', ')}`, 'error');
        return;
    }

    try {
        const resp = await fetch('/register-automation', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });

        const result = await resp.json();

        if (!resp.ok) {
            throw new Error(result.error || 'Falha ao salvar automação');
        }

        showNotification('Sucesso!', 'Automação cadastrada com sucesso!', 'success');
        document.getElementById('automationForm').reset();
        removeImage();
    } catch (e) {
        showNotification('Erro de Validação', e.message, 'error');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    setupDragAndDrop();
});
