// Modal de Histórico - Arquivo separado
// Este arquivo contém todas as funções relacionadas ao histórico de validações

// Funções da Modal de Histórico
async function showValidationHistory() {
    console.log('showValidationHistory chamada');
    
    const historyModal = document.getElementById('historyModal');
    if (!historyModal) {
        console.error('Modal de histórico não encontrada!');
        return;
    }
    
    const historyContent = document.getElementById('historyContent');
    if (!historyContent) {
        console.error('Conteúdo da modal de histórico não encontrado!');
        return;
    }
    
    historyContent.innerHTML = '<div class="schema-loading">⏳ Carregando histórico...</div>';
    historyModal.style.display = 'block';
    console.log('Modal de histórico aberta');
    
    try {
        const response = await fetch(`/contract-validation-history?collection_name=${encodeURIComponent(currentValidationData.collectionName)}&contract_name=${encodeURIComponent(currentValidationData.contractName)}&limit=5`);
        
        if (!response.ok) {
            throw new Error(`Erro ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Dados do histórico recebidos:', data);
        
        // Corrigido: verificar data.history diretamente
        if (data.history && data.history.length > 0) {
            displayHistoryItems(data.history);
        } else {
            historyContent.innerHTML = '<div class="schema-error">📭 Nenhuma execução encontrada para este contrato.</div>';
        }
    } catch (error) {
        console.error('Erro ao carregar histórico:', error);
        historyContent.innerHTML = `<div class="schema-error">⚠️ Erro ao carregar histórico: ${error.message}</div>`;
    }
}

function displayHistoryItems(history) {
    const historyContent = document.getElementById('historyContent');
    
    let html = '<div style="margin-bottom: 15px; color: #5e6c84; font-size: 14px;">💡 Clique em uma execução para reutilizar o body:</div>';
    
    history.forEach((item, index) => {
        const date = new Date(item.execution_date).toLocaleString('pt-BR');
        const statusClass = item.valid ? 'success' : 'error';
        const statusIcon = item.valid ? '✅' : '❌';
        const dataPreview = JSON.stringify(item.validated_data, null, 2).substring(0, 100) + '...';
        const parsedContractIds = parseContractIdentifier(item.contract_id);
        
        // Implementar preview para mensagens longas (mais de 100 caracteres)
        let messageDisplay = item.message;
        let detailsButton = '';
        
        if (!item.valid && item.message && item.message.length > 100) {
            const shortMessage = item.message.substring(0, 100) + '...';
            messageDisplay = shortMessage;
            detailsButton = `<div class="tooltip" style="margin-left: 10px;"><button onclick="event.stopPropagation(); showHistoryErrorDetails(${index})" style="background: #dc3545; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">🔍 Ver detalhes completos</button><span class="tooltiptext">Devido ao relatório do erro ficar muito grande, clique aqui para ver os detalhes completos</span></div>`;
        }
        
        html += `
            <div class="history-item ${statusClass}" onclick="useHistoryData(${index})">
                <div class="history-date">${statusIcon} ${date}</div>
                <div class="history-message">${messageDisplay}</div>
                <div class="history-details">
                    <span class="history-version">🔢 ${item.version || 'v1.0'}</span>
                    <span class="history-method">🌐 ${item.method || 'POST'}</span>
                    <span class="history-contract-id">📁 ID Coleção: ${parsedContractIds.collectionId}</span>
                    <span class="history-contract-id">🧩 ID Schema: ${parsedContractIds.schemaId}</span>
                    ${detailsButton}
                </div>
                <div class="history-data-preview">${dataPreview}</div>
            </div>
        `;
    });
    
    historyContent.innerHTML = html;
    
    // Armazenar histórico para uso posterior
    window.currentHistory = history;
}

function parseContractIdentifier(contractId) {
    if (!contractId || typeof contractId !== 'string') {
        return { collectionId: 'N/A', schemaId: 'N/A' };
    }

    const parts = contractId.split('-');
    if (parts.length >= 2) {
        return {
            collectionId: parts[0] || 'N/A',
            schemaId: parts.slice(1).join('-') || 'N/A'
        };
    }

    // Fallback para manter algum valor útil visível
    return { collectionId: contractId, schemaId: 'N/A' };
}

function showHistoryErrorDetails(index) {
    const historyItem = window.currentHistory[index];
    if (!historyItem) {
        alert('Item do histórico não encontrado');
        return;
    }
    
    const { message } = historyItem;
    
    // Criar modal de detalhes se não existir
    let detailsModal = document.getElementById('historyErrorDetailsModal');
    if (!detailsModal) {
        detailsModal = document.createElement('div');
        detailsModal.id = 'historyErrorDetailsModal';
        detailsModal.innerHTML = `
            <div class="modal" style="display: none; position: fixed; z-index: 10000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5);">
                <div class="modal-content" style="background-color: #fefefe; margin: 5% auto; padding: 20px; border: 1px solid #888; width: 80%; max-width: 800px; border-radius: 8px; max-height: 80vh; overflow-y: auto;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h3 style="margin: 0; color: #dc3545;">🔍 Detalhes Completos do Erro</h3>
                        <button onclick="closeHistoryErrorDetails()" style="background: #dc3545; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; font-size: 14px;">✕ Fechar</button>
                    </div>
                    <div id="historyErrorDetailsContent" style="background: #f8f9fa; padding: 15px; border-radius: 6px; font-family: 'Courier New', monospace; font-size: 12px; line-height: 1.5; white-space: pre-wrap; overflow-x: auto; max-height: 60vh; overflow-y: auto; border: 1px solid #dee2e6;"></div>
                </div>
            </div>
        `;
        document.body.appendChild(detailsModal);
    }
    
    const contentDiv = document.getElementById('historyErrorDetailsContent');
    if (contentDiv) {
        // Formatar a mensagem para melhor legibilidade
        let formattedMessage = message;
        
        // Se a mensagem contém JSON, tentar formatá-lo
        if (message.includes('[') && message.includes(']')) {
            try {
                // Extrair o JSON da mensagem
                const jsonMatch = message.match(/\[(.*?)\]/s);
                if (jsonMatch) {
                    const jsonString = '[' + jsonMatch[1] + ']';
                    const parsedJson = JSON.parse(jsonString);
                    const formattedJson = JSON.stringify(parsedJson, null, 2);
                    
                    // Substituir o JSON na mensagem
                    formattedMessage = message.replace(jsonString, formattedJson);
                }
            } catch (e) {
                console.log('Não foi possível formatar JSON:', e);
            }
        }
        
        contentDiv.textContent = formattedMessage;
    }
    
    // Mostrar modal
    detailsModal.style.display = 'block';
    const modalElement = detailsModal.querySelector('.modal');
    if (modalElement) {
        modalElement.style.display = 'block';
    }
}

function closeHistoryErrorDetails() {
    const detailsModal = document.getElementById('historyErrorDetailsModal');
    if (detailsModal) {
        detailsModal.style.display = 'none';
        const modalElement = detailsModal.querySelector('.modal');
        if (modalElement) {
            modalElement.style.display = 'none';
        }
    }
}

function useHistoryData(index) {
    const historyItem = window.currentHistory[index];
    if (historyItem && historyItem.validated_data) {
        // Preencher o campo de validação com os dados do histórico
        document.getElementById('validationBody').value = JSON.stringify(historyItem.validated_data, null, 2);
        
        // Fechar modal de histórico
        closeHistoryModal();
        
        // Mostrar mensagem de sucesso
        showValidationResult(`Body carregado do histórico (${new Date(historyItem.execution_date).toLocaleString('pt-BR')})`, true);
    }
}

function closeHistoryModal() {
    document.getElementById('historyModal').style.display = 'none';
    window.currentHistory = null;
}

// Função para atualizar histórico após validação
async function refreshHistoryAfterValidation() {
    // Só atualizar se a modal de histórico estiver aberta
    const historyModal = document.getElementById('historyModal');
    if (historyModal.style.display === 'block') {
        console.log('Atualizando histórico após validação...');
        await showValidationHistory();
    }
}

// Função para incluir a modal de histórico no DOM
function includeHistoryModal() {
    // Verificar se a modal já existe
    if (document.getElementById('historyModal')) {
        return;
    }
    
    // Criar elemento para incluir o conteúdo da modal
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = `
        <!-- Modal de Histórico -->
        <div id="historyModal" class="history-modal">
            <div class="history-modal-content">
                <div class="history-modal-header">
                    <h3 class="history-modal-title">📋 Histórico de Execuções</h3>
                    <span class="history-close" onclick="closeHistoryModal()">&times;</span>
                </div>
                <div id="historyContent">
                    <div class="schema-loading">⏳ Carregando histórico...</div>
                </div>
            </div>
        </div>
    `;
    
    // Adicionar ao body
    document.body.appendChild(modalContainer.firstElementChild);
    
    // Adicionar CSS se não existir
    if (!document.getElementById('history-modal-styles')) {
        const style = document.createElement('style');
        style.id = 'history-modal-styles';
        style.textContent = `
            /* Tooltips Bonitos */
            .tooltip {
                position: relative;
                display: inline-block;
            }
            
            .tooltip .tooltiptext {
                visibility: hidden;
                width: 280px;
                background-color: #172b4d;
                color: #ffffff;
                text-align: center;
                border-radius: 8px;
                padding: 12px 16px;
                position: absolute;
                z-index: 10001;
                bottom: 125%;
                left: 50%;
                margin-left: -140px;
                opacity: 0;
                transition: opacity 0.3s ease;
                font-size: 13px;
                line-height: 1.4;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                border: 1px solid #344563;
            }
            
            .tooltip .tooltiptext::after {
                content: "";
                position: absolute;
                top: 100%;
                left: 50%;
                margin-left: -5px;
                border-width: 5px;
                border-style: solid;
                border-color: #172b4d transparent transparent transparent;
            }
            
            .tooltip:hover .tooltiptext {
                visibility: visible;
                opacity: 1;
            }
            
            /* Modal de Histórico */
            .history-modal {
                display: none;
                position: fixed;
                z-index: 2000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                animation: fadeIn 0.3s ease;
            }

            .history-modal-content {
                background-color: #ffffff;
                margin: 5% auto;
                padding: 25px;
                border-radius: 8px;
                width: 80%;
                max-width: 600px;
                max-height: 80vh;
                overflow-y: auto;
                animation: slideIn 0.3s ease;
            }

            .history-modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 2px solid #ebecf0;
            }

            .history-modal-title {
                font-size: 20px;
                font-weight: 600;
                color: #172b4d;
                margin: 0;
            }

            .history-close {
                font-size: 28px;
                font-weight: bold;
                color: #5e6c84;
                cursor: pointer;
                transition: color 0.2s;
            }

            .history-close:hover {
                color: #172b4d;
            }

            .history-item {
                padding: 15px;
                border: 1px solid #ebecf0;
                border-radius: 6px;
                margin-bottom: 10px;
                cursor: pointer;
                transition: all 0.2s;
            }

            .history-item:hover {
                background-color: #f8f9fa;
                border-color: #0065ff;
            }

            .history-item.success {
                border-left: 4px solid #006644;
            }

            .history-item.error {
                border-left: 4px solid #bf2600;
            }

            .history-date {
                font-size: 12px;
                color: #5e6c84;
                margin-bottom: 5px;
            }

            .history-message {
                font-size: 14px;
                color: #172b4d;
                margin-bottom: 8px;
            }

            .history-details {
                display: flex;
                gap: 15px;
                margin-bottom: 8px;
                font-size: 12px;
                color: #5e6c84;
            }

            .history-details span {
                background-color: #f8f9fa;
                padding: 4px 8px;
                border-radius: 4px;
            }

            .history-data-preview {
                font-size: 12px;
                color: #5e6c84;
                font-family: monospace;
                background-color: #f8f9fa;
                padding: 8px;
                border-radius: 4px;
                max-height: 60px;
                overflow: hidden;
            }

            .schema-loading {
                text-align: center;
                padding: 20px;
                color: #5e6c84;
                font-size: 16px;
            }

            .schema-error {
                text-align: center;
                padding: 20px;
                color: #bf2600;
                font-size: 16px;
            }

            /* Animações */
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            @keyframes slideIn {
                from { transform: translateY(-50px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }

            /* Responsivo */
            @media (max-width: 768px) {
                .history-modal-content {
                    width: 95%;
                    margin: 5% auto;
                    max-width: none;
                }
                
                .history-details {
                    flex-direction: column;
                    gap: 8px;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// Event listener para fechar modal de detalhes ao clicar fora
document.addEventListener('click', function(event) {
    const historyModal = document.getElementById('historyModal');
    if (historyModal && event.target === historyModal) {
        closeHistoryModal();
    }

    const detailsModal = document.getElementById('historyErrorDetailsModal');
    if (detailsModal && event.target === detailsModal) {
        closeHistoryErrorDetails();
    }
});

// Incluir a modal quando o DOM estiver carregado
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', includeHistoryModal);
} else {
    includeHistoryModal();
}
