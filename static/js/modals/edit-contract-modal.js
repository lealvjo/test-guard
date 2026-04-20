let currentEditData = {};
let hasUnsavedChanges = false;

function openEditContractModal(collectionName, contractName, contractVersion) {
    currentEditData = {
        collectionName: collectionName,
        contractName: contractName,
        contractVersion: contractVersion
    };

    hasUnsavedChanges = false;

    document.getElementById('editModalCollectionName').textContent = collectionName;
    document.getElementById('editModalContractName').textContent = contractName;
    document.getElementById('editModalContractVersion').textContent = contractVersion;

    document.getElementById('editContractName').value = contractName;
    document.getElementById('editContractVersion').value = contractVersion;

    loadCurrentSchema(collectionName, contractName, contractVersion);
    document.getElementById('editContractModal').style.display = 'block';
}

function closeEditModal() {
    document.getElementById('editContractModal').style.display = 'none';

    if (hasUnsavedChanges) {
        refreshContracts();
    }

    currentEditData = {};
    hasUnsavedChanges = false;

    document.getElementById('editContractName').value = '';
    document.getElementById('editContractVersion').value = '';
    document.getElementById('editContractMethod').value = '';
    document.getElementById('editContractEndpoint').value = '';
    document.getElementById('editContractSchema').value = '';
    document.getElementById('editValidationResult').style.display = 'none';
}

async function loadCurrentSchema(collectionName, contractName, contractVersion) {
    try {
        const response = await fetch(`/contracts/paginated?page=1&per_page=100&search=${encodeURIComponent(collectionName)}`);

        if (!response.ok) {
            throw new Error(`Erro ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        if (data.contracts && data.contracts.length > 0) {
            let targetContract = null;
            for (const contract of data.contracts) {
                if (contract.name === collectionName) {
                    targetContract = contract;
                    break;
                }
            }

            if (targetContract) {
                const schemas = targetContract.schemas;
                let targetSchema = null;
                let foundSchema = null;

                for (const schema of schemas) {
                    if (schema.contract === contractName) {
                        const schemaVersion = schema.version || 'v1';
                        if (schemaVersion === contractVersion) {
                            targetSchema = schema.expected;
                            foundSchema = schema;
                            break;
                        }
                    }
                }

                if (targetSchema) {
                    document.getElementById('editContractSchema').value = JSON.stringify(targetSchema, null, 2);

                    if (foundSchema && foundSchema.method) {
                        document.getElementById('editContractMethod').value = foundSchema.method;
                    }
                    if (foundSchema && foundSchema.endpoint) {
                        document.getElementById('editContractEndpoint').value = foundSchema.endpoint;
                    }
                } else {
                    showEditValidationResult('🔍 Schema não encontrado para este contrato.', false);
                }
            } else {
                showEditValidationResult('📁 Coleção não encontrada.', false);
            }
        } else {
            showEditValidationResult('📁 Coleção não encontrada.', false);
        }
    } catch (error) {
        showEditValidationResult(`⚠️ Erro ao carregar schema: ${error.message}`, false);
    }
}

function formatEditJson() {
    const textarea = document.getElementById('editContractSchema');
    try {
        const json = JSON.parse(textarea.value);
        textarea.value = JSON.stringify(json, null, 2);
        showEditValidationResult('JSON formatado com sucesso!', true);
    } catch (e) {
        showEditValidationResult(`JSON inválido: ${e.message}`, false);
    }
}

function showEditValidationResult(message, isSuccess) {
    const resultDiv = document.getElementById('editValidationResult');
    const icon = isSuccess ? '✅' : '❌';
    resultDiv.textContent = `${icon} ${message}`;
    resultDiv.className = `validation-result ${isSuccess ? 'validation-success' : 'validation-error'}`;
    resultDiv.style.display = 'block';
}

async function saveContractEdit() {
    const newContractName = document.getElementById('editContractName').value.trim();
    const newContractVersion = document.getElementById('editContractVersion').value.trim();
    const newContractMethod = document.getElementById('editContractMethod').value.trim();
    const newContractEndpoint = document.getElementById('editContractEndpoint').value.trim();
    const schemaText = document.getElementById('editContractSchema').value.trim();

    if (!newContractName || !newContractVersion || !newContractMethod || !newContractEndpoint || !schemaText) {
        showEditValidationResult('Todos os campos são obrigatórios.', false);
        return;
    }

    const allowedMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'];
    if (!allowedMethods.includes(newContractMethod)) {
        showEditValidationResult(`Método HTTP '${newContractMethod}' não é válido. Métodos permitidos: ${allowedMethods.join(', ')}`, false);
        return;
    }

    if (!newContractEndpoint.startsWith('/')) {
        showEditValidationResult("Endpoint deve começar com '/'. Exemplo: /api/users", false);
        return;
    }

    try {
        const schema = JSON.parse(schemaText);
        const collectionResponse = await fetch(`/contracts/paginated?page=1&per_page=100&search=${encodeURIComponent(currentEditData.collectionName)}`);
        const collectionData = await collectionResponse.json();

        if (!collectionData.contracts || collectionData.contracts.length === 0) {
            showEditValidationResult('Coleção não encontrada.', false);
            return;
        }

        let targetCollection = null;
        for (const contract of collectionData.contracts) {
            if (contract.name === currentEditData.collectionName) {
                targetCollection = contract;
                break;
            }
        }

        if (!targetCollection) {
            showEditValidationResult('Coleção não encontrada.', false);
            return;
        }

        const updateData = {
            action: 'update',
            contract_name: currentEditData.contractName,
            schema: {
                contract: newContractName,
                version: newContractVersion,
                method: newContractMethod,
                endpoint: newContractEndpoint,
                expected: schema
            }
        };

        const response = await fetch(`/contracts/${targetCollection.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updateData)
        });

        const result = await response.json();

        if (response.ok) {
            showEditValidationResult('Contrato atualizado com sucesso!', true);
            hasUnsavedChanges = true;
        } else {
            showEditValidationResult(`Erro ao atualizar contrato: ${result.error || 'Erro desconhecido'}`, false);
        }
    } catch (error) {
        if (error instanceof SyntaxError) {
            showEditValidationResult('JSON Schema inválido. Verifique a sintaxe.', false);
        } else {
            showEditValidationResult(`Erro ao salvar: ${error.message}`, false);
        }
    }
}

document.addEventListener('click', function(event) {
    const editModal = document.getElementById('editContractModal');
    if (editModal && event.target === editModal) {
        closeEditModal();
    }
});
