// Modal de Validação - Arquivo separado
// Este arquivo contém todas as funções relacionadas à validação de contratos

console.log('validation_modal.js carregado');

// Funções da Modal de Validação
let currentValidationData = {};

function openValidationModal(collectionName, contractName, version = 'v1.0', method = 'POST') {
    try {
        currentValidationData = {
            collectionName: collectionName,
            contractName: contractName,
            version: version,
            method: method
        };
        
        const modal = document.getElementById('validationModal');
        if (!modal) {
            console.error('Modal validationModal não encontrada!');
            return;
        }
        
        // Verificar se os elementos existem
        const collectionNameEl = document.getElementById('modalCollectionName');
        const contractNameEl = document.getElementById('modalContractName');
        const versionEl = document.getElementById('modalVersion');
        const methodEl = document.getElementById('modalMethod');
        
        if (collectionNameEl) collectionNameEl.textContent = collectionName;
        if (contractNameEl) contractNameEl.textContent = contractName;
        if (versionEl) versionEl.textContent = version;
        if (methodEl) methodEl.textContent = method;
        
        // Limpar campos
        const validationBody = document.getElementById('validationBody');
        if (validationBody) validationBody.value = '';
        
        const validationResult = document.getElementById('validationResult');
        if (validationResult) {
            validationResult.style.display = 'none';
            validationResult.textContent = '';
        }
        
        // Mostrar modal
        modal.style.display = 'block';
        
        // Carregar preview do schema
        loadSchemaPreview();
        
    } catch (error) {
        console.error('Erro ao abrir modal:', error);
    }
}

function closeModal() {
    const modal = document.getElementById('validationModal');
    if (modal) {
        modal.style.display = 'none';
    }
    currentValidationData = {};
}

async function loadSchemaPreview() {
    const previewDiv = document.getElementById('schemaPreview');
    previewDiv.innerHTML = '<div class="schema-loading">Carregando schema...</div>';
    
    try {
        const response = await fetch(`/contracts/search?name=${encodeURIComponent(currentValidationData.collectionName)}&contract=${encodeURIComponent(currentValidationData.contractName)}`);
        if (response.ok) {
            const result = await response.json();
            if (result.contracts && result.contracts.length > 0) {
                const contract = result.contracts[0];
                previewDiv.innerHTML = `<div class="schema-content">${JSON.stringify(contract, null, 2)}</div>`;
            } else {
                previewDiv.innerHTML = '<div class="schema-error">Contrato não encontrado</div>';
            }
        } else {
            previewDiv.innerHTML = '<div class="schema-error">Erro ao carregar schema</div>';
        }
    } catch (error) {
        previewDiv.innerHTML = '<div class="schema-error">Erro ao carregar schema</div>';
    }
}

function formatValidationJson() {
    const textarea = document.getElementById('validationBody');
    try {
        const json = JSON.parse(textarea.value);
        textarea.value = JSON.stringify(json, null, 2);
        showValidationResult(true, 'JSON formatado com sucesso!');
    } catch (error) {
        showValidationResult(false, 'JSON inválido! Verifique a sintaxe.');
    }
}

function showValidationResult(success, message, data = null) {
    const resultDiv = document.getElementById('validationResult');
    const icon = success ? '✅' : '❌';
    
    let content = `${icon} ${message}`;
    
    if (success && data) {
        // Mostrar dados adicionais se disponíveis
        if (data.validated_data) {
            content += `\n\n📋 Dados validados:\n${JSON.stringify(data.validated_data, null, 2)}`;
        }
        if (data.contract_id) {
            content += `\n\n🆔 ID do Contrato: ${data.contract_id}`;
        }
        if (data.execution_date) {
            content += `\n\n📅 Data de Execução: ${new Date(data.execution_date).toLocaleString('pt-BR')}`;
        }
    }
    
    resultDiv.textContent = content;
    resultDiv.className = success ? 'validation-result validation-success' : 'validation-result validation-error';
    resultDiv.style.display = 'block';
}

async function executeValidation() {
    const validationBody = document.getElementById('validationBody');
    const bodyText = validationBody.value.trim();
    
    if (!bodyText) {
        showValidationResult(false, 'Por favor, insira um JSON para validação');
        return;
    }
    
    try {
        JSON.parse(bodyText); // Validar JSON
    } catch (error) {
        showValidationResult(false, 'JSON inválido: ' + error.message);
        return;
    }
    
    try {
        const response = await fetch('/contracts/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                collection_name: currentValidationData.collectionName,
                contract_name: currentValidationData.contractName,
                version: currentValidationData.version,
                method: currentValidationData.method,
                body: JSON.parse(bodyText)
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showValidationResult(true, result.data.message || 'Validação bem-sucedida!', result.data);
        } else {
            showValidationResult(false, result.message || 'Erro na validação');
        }
    } catch (error) {
        showValidationResult(false, 'Erro na requisição: ' + error.message);
    }
}

// Função showValidationHistory está implementada em history_modal.js