// ===== VALIDATION MODAL - JavaScript específico =====

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
    
    // Verificar se o primeiro parâmetro é uma string (formato antigo)
    if (typeof success === 'string') {
        // Formato antigo: showValidationResult(message, isSuccess)
        const icon = message ? '✅' : '❌';
        const content = `${icon} ${success}`;
        resultDiv.textContent = content;
        resultDiv.className = message ? 'validation-result validation-success' : 'validation-result validation-error';
        resultDiv.style.display = 'block';
        return;
    }
    
    // Formato novo: showValidationResult(success, message, data)
    // Verificar se a mensagem já tem ícone para evitar duplicação
    let content = message;
    if (!message.startsWith('✅') && !message.startsWith('❌')) {
        const icon = success ? '✅' : '❌';
        content = `${icon} ${message}`;
    }
    
    resultDiv.textContent = content;
    resultDiv.className = success ? 'validation-result validation-success' : 'validation-result validation-error';
    resultDiv.style.display = 'block';
}

function cleanJsonFromComments(jsonText) {
    // Remove comentários de linha (// ...) e comentários de bloco (/* ... */)
    return jsonText
        .replace(/\/\/.*$/gm, '') // Remove comentários de linha
        .replace(/\/\*[\s\S]*?\*\//g, '') // Remove comentários de bloco
        .trim();
}

async function executeValidation() {
    const validationBody = document.getElementById('validationBody');
    const bodyText = validationBody.value.trim();
    
    // Limpar resultado anterior
    const validationResult = document.getElementById('validationResult');
    if (validationResult) {
        validationResult.style.display = 'none';
        validationResult.textContent = '';
    }
    
    // Limpar botão de detalhes anterior se existir
    const existingDetailsButton = document.querySelector('[onclick="showErrorDetails()"]');
    if (existingDetailsButton) {
        existingDetailsButton.remove();
    }
    
    if (!bodyText) {
        showValidationResult(false, 'Por favor, insira um JSON para validação');
        return;
    }
    
    // Limpar comentários do JSON
    const cleanJsonText = cleanJsonFromComments(bodyText);
    
    try {
        JSON.parse(cleanJsonText);
    } catch (error) {
        showValidationResult(false, 'JSON inválido: ' + error.message);
        return;
    }
    
    try {
        const response = await fetch('/contract-validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                collection_name: currentValidationData.collectionName,
                contract_name: currentValidationData.contractName,
                version: currentValidationData.version,
                method: currentValidationData.method,
                body_to_validate: JSON.parse(cleanJsonText)
            })
        });
        
        const result = await response.json();
        
        if (result.valid) {
            showValidationResult(true, result.message || 'Validação bem-sucedida!', result);
        } else {
            // Mostrar exatamente a mensagem que vem da API
            let errorMessage = result.message || 'Erro na validação';
            
            // Adicionar path se disponível e não vazio
            if (result.validation_error && result.validation_error.path) {
                const pathValue = Array.isArray(result.validation_error.path) 
                    ? result.validation_error.path.join('.') 
                    : result.validation_error.path;
                
                if (pathValue && pathValue.trim() !== '') {
                    errorMessage += `\n\n📍 Path: ${pathValue}`;
                }
            }
            
            // Se a mensagem for muito longa, mostrar preview + botão "Ver detalhes"
            if (errorMessage.length > 100) {
                const preview = errorMessage.substring(0, 100) + '...';
                showValidationResult(false, preview);
                
                // Adicionar botão de detalhes separadamente
                setTimeout(() => {
                    const resultDiv = document.getElementById('validationResult');
                    if (resultDiv) {
                        const detailsButton = document.createElement('div');
                        detailsButton.style.marginTop = '10px';
                        detailsButton.innerHTML = `<button onclick="showErrorDetails()" style="background: #dc3545; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; font-size: 13px;">🔍 Ver detalhes completos</button>`;
                        resultDiv.parentNode.insertBefore(detailsButton, resultDiv.nextSibling);
                        
                        // Armazenar dados globalmente para a função showErrorDetails
                        window.currentErrorDetails = {
                            message: errorMessage,
                            result: result
                        };
                        
                        // Também armazenar no histórico para backup
                        if (!window.errorHistory) {
                            window.errorHistory = [];
                        }
                        window.errorHistory.push({
                            message: errorMessage,
                            result: result,
                            timestamp: new Date().toISOString()
                        });
                    }
                }, 100);
            } else {
                showValidationResult(false, errorMessage);
            }
        }
        
    } catch (error) {
        showValidationResult(false, 'Erro na requisição: ' + error.message);
    }
}

function showErrorDetails() {
    let errorData = null;
    
    // Tentar pegar dos dados globais primeiro
    if (window.currentErrorDetails) {
        errorData = window.currentErrorDetails;
    } else if (window.errorHistory && window.errorHistory.length > 0) {
        // Fallback para o histórico
        errorData = window.errorHistory[window.errorHistory.length - 1];
    }
    
    if (!errorData) {
        alert('Nenhum erro encontrado para exibir detalhes');
        return;
    }
    
    const { message, result } = errorData;
    
    // Verificar se o modal já existe
    let detailsModal = document.getElementById('errorDetailsModal');
    if (!detailsModal) {
        // Criar o modal se não existir
        detailsModal = document.createElement('div');
        detailsModal.id = 'errorDetailsModal';
        detailsModal.innerHTML = `
            <div class="modal" style="display: none; position: fixed; z-index: 10000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5);">
                <div class="modal-content" style="background-color: #fefefe; margin: 5% auto; padding: 20px; border: 1px solid #888; width: 80%; max-width: 800px; border-radius: 8px; max-height: 80vh; overflow-y: auto;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h3 style="margin: 0; color: #dc3545;">🔍 Detalhes Completos do Erro</h3>
                        <button onclick="closeErrorDetails()" style="background: #dc3545; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; font-size: 14px;">✕ Fechar</button>
                    </div>
                    <div id="errorDetailsContent" style="background: #f8f9fa; padding: 15px; border-radius: 6px; font-family: 'Courier New', monospace; font-size: 12px; line-height: 1.5; white-space: pre-wrap; overflow-x: auto; max-height: 60vh; overflow-y: auto; border: 1px solid #dee2e6;"></div>
                </div>
            </div>
        `;
        document.body.appendChild(detailsModal);
    }
    
    // Preencher o conteúdo
    const contentDiv = document.getElementById('errorDetailsContent');
    if (contentDiv) {
        let formattedMessage = message;
        
        // Tentar formatar JSON se detectado na mensagem
        if (message.includes('[') && message.includes(']')) {
            try {
                const jsonMatch = message.match(/\[(.*?)\]/s);
                if (jsonMatch) {
                    const jsonString = '[' + jsonMatch[1] + ']';
                    const parsedJson = JSON.parse(jsonString);
                    const formattedJson = JSON.stringify(parsedJson, null, 2);
                    formattedMessage = message.replace(jsonString, formattedJson);
                }
            } catch (e) {
                console.log('Não foi possível formatar JSON:', e);
            }
        }
        
        contentDiv.textContent = formattedMessage;
    }
    
    // Mostrar o modal
    detailsModal.style.display = 'block';
    const modalElement = detailsModal.querySelector('.modal');
    if (modalElement) {
        modalElement.style.display = 'block';
    }
}

function closeErrorDetails() {
    const detailsModal = document.getElementById('errorDetailsModal');
    if (detailsModal) {
        detailsModal.style.display = 'none';
        const modalElement = detailsModal.querySelector('.modal');
        if (modalElement) {
            modalElement.style.display = 'none';
        }
    }
}

// Event listener para fechar modal ao clicar fora
document.addEventListener('click', function(event) {
    const detailsModal = document.getElementById('errorDetailsModal');
    if (detailsModal && event.target === detailsModal) {
        closeErrorDetails();
    }
});

