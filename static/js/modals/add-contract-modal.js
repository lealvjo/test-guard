function openAddContractModal(collectionId, collectionName) {
    document.getElementById('modalCollectionId').value = collectionId;
    document.getElementById('addModalCollectionName').textContent = collectionName;
    document.getElementById('contractNameInput').value = '';
    document.getElementById('contractVersionInput').value = '';
    document.getElementById('contractMethodInput').value = '';
    document.getElementById('contractEndpointInput').value = '';
    document.getElementById('contractSchemaInput').value = '';
    document.getElementById('addContractModal').style.display = 'block';
}

function closeAddContractModal() {
    document.getElementById('addContractModal').style.display = 'none';

    document.getElementById('contractNameInput').value = '';
    document.getElementById('contractVersionInput').value = '';
    document.getElementById('contractMethodInput').value = '';
    document.getElementById('contractEndpointInput').value = '';
    document.getElementById('contractSchemaInput').value = '';
}

function formatContractJson() {
    const textarea = document.getElementById('contractSchemaInput');
    try {
        const json = JSON.parse(textarea.value);
        textarea.value = JSON.stringify(json, null, 2);
        showNotification('JSON formatado com sucesso!', 'success');
    } catch (e) {
        showNotification(`JSON inválido: ${e.message}`, 'error');
    }
}

async function addContractToCollection() {
    const collectionId = document.getElementById('modalCollectionId').value;
    const contractName = document.getElementById('contractNameInput').value.trim();
    const contractVersion = document.getElementById('contractVersionInput').value.trim();
    const contractMethod = document.getElementById('contractMethodInput').value.trim();
    const contractEndpoint = document.getElementById('contractEndpointInput').value.trim();
    const schemaText = document.getElementById('contractSchemaInput').value.trim();

    if (!contractName || !contractVersion || !contractMethod || !contractEndpoint || !schemaText) {
        showNotification('Preencha todos os campos obrigatórios.', 'error');
        return;
    }

    const allowedMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'];
    if (!allowedMethods.includes(contractMethod)) {
        showNotification(`Método HTTP '${contractMethod}' não é válido. Métodos permitidos: ${allowedMethods.join(', ')}`, 'error');
        return;
    }

    if (!contractEndpoint.startsWith('/')) {
        showNotification("Endpoint deve começar com '/'. Exemplo: /api/users", 'error');
        return;
    }

    let schema;
    try {
        schema = JSON.parse(schemaText);
    } catch (e) {
        showNotification(`JSON inválido: ${e.message}`, 'error');
        return;
    }

    const payload = {
        action: 'add',
        schema: {
            contract: contractName,
            version: contractVersion,
            method: contractMethod,
            endpoint: contractEndpoint,
            expected: schema
        }
    };

    try {
        const response = await fetch(`/contracts/${collectionId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (response.ok) {
            showNotification('Contrato adicionado com sucesso!', 'success');
            closeAddContractModal();
            refreshContracts();
        } else {
            showNotification(`Erro: ${result.error || 'Erro desconhecido'}`, 'error');
        }
    } catch (error) {
        showNotification(`Erro na requisição: ${error.message}`, 'error');
    }
}

function showNotification(message, type = 'info') {
    const existingNotification = document.getElementById('toast-notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    const notification = document.createElement('div');
    notification.id = 'toast-notification';
    notification.className = `toast toast-${type}`;
    notification.innerHTML = `
        <div class="toast-content">
            <span class="toast-icon">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('toast-show');
    }, 100);

    setTimeout(() => {
        if (notification.parentElement) {
            notification.classList.remove('toast-show');
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }
    }, 4000);
}

document.addEventListener('click', function(event) {
    const modal = document.getElementById('addContractModal');
    if (modal && event.target === modal) {
        closeAddContractModal();
    }
});
