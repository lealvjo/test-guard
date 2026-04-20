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
    const result = formatJsonText(textarea.value);
    if (result.ok) {
        textarea.value = result.text;
        showToastNotification('JSON formatado com sucesso!', 'success');
    } else {
        showToastNotification(`JSON inválido: ${result.error.message}`, 'error');
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
        showToastNotification('Preencha todos os campos obrigatórios.', 'error');
        return;
    }

    const allowedMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'];
    if (!allowedMethods.includes(contractMethod)) {
        showToastNotification(`Método HTTP '${contractMethod}' não é válido. Métodos permitidos: ${allowedMethods.join(', ')}`, 'error');
        return;
    }

    if (!contractEndpoint.startsWith('/')) {
        showToastNotification("Endpoint deve começar com '/'. Exemplo: /api/users", 'error');
        return;
    }

    const parsedSchema = parseJsonText(schemaText);
    if (!parsedSchema.ok) {
        showToastNotification(`JSON inválido: ${parsedSchema.error.message}`, 'error');
        return;
    }
    const schema = parsedSchema.data;

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
            showToastNotification('Contrato adicionado com sucesso!', 'success');
            closeAddContractModal();
            refreshContracts();
        } else {
            showToastNotification(`Erro: ${result.error || 'Erro desconhecido'}`, 'error');
        }
    } catch (error) {
        showToastNotification(`Erro na requisição: ${error.message}`, 'error');
    }
}

document.addEventListener('click', function(event) {
    const modal = document.getElementById('addContractModal');
    if (modal && event.target === modal) {
        closeAddContractModal();
    }
});
