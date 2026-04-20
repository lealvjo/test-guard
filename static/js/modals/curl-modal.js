// Modal de Curl - Arquivo separado
// Este arquivo contém todas as funções relacionadas à validação automática com curl

// Funções da Modal de Curl
function showCurlModal() {
    // Verificar se a modal já existe
    if (!document.getElementById('curlModal')) {
        // Mostrar indicador de carregamento
        const loadingIndicator = document.createElement('div');
        loadingIndicator.id = 'curlLoadingIndicator';
        loadingIndicator.style.cssText = `
            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: rgba(0,0,0,0.8); color: white; padding: 20px;
            border-radius: 8px; z-index: 10000; font-size: 16px;
        `;
        loadingIndicator.innerHTML = '🚀 Carregando Validação Automática...';
        document.body.appendChild(loadingIndicator);
        
        loadCurlModal().then(() => {
            // Remover indicador de carregamento
            const indicator = document.getElementById('curlLoadingIndicator');
            if (indicator) indicator.remove();
            
            // Aguardar um pouco para garantir que o DOM foi atualizado
            setTimeout(() => {
                document.getElementById('curlModal').style.display = 'block';
            }, 50);
        });
    } else {
        document.getElementById('curlModal').style.display = 'block';
    }
    
    // Aguardar um pouco para garantir que os elementos existem
    setTimeout(() => {
        if (document.getElementById('curlModalCollectionName')) {
            document.getElementById('curlModalCollectionName').textContent = currentValidationData.collectionName;
        }
        if (document.getElementById('curlModalContractName')) {
            document.getElementById('curlModalContractName').textContent = currentValidationData.contractName;
        }
        if (document.getElementById('curlCommand')) {
            document.getElementById('curlCommand').value = '';
        }
        if (document.getElementById('curlResult')) {
            document.getElementById('curlResult').style.display = 'none';
        }
    }, 100);
}

async function loadCurlModal() {
    try {
        const response = await fetch('/static/curl_modal.html');
        const html = await response.text();
        
        // Criar container para a modal
        const modalContainer = document.createElement('div');
        modalContainer.innerHTML = html;
        
        // Adicionar ao body
        document.body.appendChild(modalContainer.firstElementChild);
        
        // Adicionar CSS se não existir
        if (!document.getElementById('curl-modal-styles')) {
            const style = document.createElement('style');
            style.id = 'curl-modal-styles';
            style.textContent = `
                /* Modal de Curl */
                .curl-input { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 13px; height: 150px; width: 100%; padding: 12px; border: 1px solid #dfe1e6; border-radius: 6px; background-color: #fafbfc; resize: vertical; }
                .curl-result { margin-top: 20px; padding: 15px; border-radius: 6px; font-size: 14px; line-height: 1.5; white-space: pre-wrap; }
                .curl-success { background-color: #e3fcef; color: #006644; border: 1px solid #b7ebc6; }
                .curl-error { background-color: #ffebe6; color: #bf2600; border: 1px solid #ffbdad; }
                   .security-notice { margin-bottom: 20px; padding: 15px; background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 6px; display: flex; align-items: flex-start; gap: 10px; }
                   .security-icon { font-size: 20px; }
                   .security-text { flex: 1; font-size: 14px; color: #856404; }
                   
                   /* Efeito visual para campo carregado automaticamente */
                   .auto-loaded { 
                       border: 2px solid #28a745 !important; 
                       background-color: #f8fff9 !important; 
                       box-shadow: 0 0 10px rgba(40, 167, 69, 0.3) !important;
                       animation: pulse-green 2s ease-in-out;
                   }
                   
                   @keyframes pulse-green {
                       0% { box-shadow: 0 0 5px rgba(40, 167, 69, 0.3); }
                       50% { box-shadow: 0 0 20px rgba(40, 167, 69, 0.6); }
                       100% { box-shadow: 0 0 5px rgba(40, 167, 69, 0.3); }
                   }
            `;
            document.head.appendChild(style);
        }
    } catch (error) {
        console.error('Erro ao carregar modal de curl:', error);
    }
}

function closeCurlModal() {
    document.getElementById('curlModal').style.display = 'none';
}

document.addEventListener('click', function(event) {
    const curlModal = document.getElementById('curlModal');
    if (curlModal && event.target === curlModal) {
        closeCurlModal();
    }
});

function showCurlResult(message, isSuccess) {
    const resultDiv = document.getElementById('curlResult');
    
    // Verificar se a mensagem já tem ícone para evitar duplicação
    let content = message;
    if (!message.startsWith('✅') && !message.startsWith('❌')) {
        const icon = isSuccess ? '✅' : '❌';
        content = `${icon} ${message}`;
    }
    
    resultDiv.textContent = content;
    resultDiv.className = `curl-result ${isSuccess ? 'curl-success' : 'curl-error'}`;
    resultDiv.style.display = 'block';
}

async function executeCurl() {
    const curlCommand = document.getElementById('curlCommand').value.trim();
    
    if (!curlCommand) {
        showCurlResult('Por favor, insira um comando curl.', false);
        return;
    }

    try {
        const response = await fetch('/execute-curl', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                curl_command: curlCommand
            })
        });

        const result = await response.json();
        console.log('Resultado do curl:', result);

        if (result.response_body) {
            // Preencher o campo de validação com o response body
            const validationBody = document.getElementById('validationBody');
            const jsonBody = JSON.stringify(result.response_body, null, 2);
            
            // Adicionar comentário indicando que foi carregado automaticamente
            const autoLoadedComment = `// 🚀 Body carregado automaticamente via Validação Automática (cURL)\n// Data/Hora: ${new Date().toLocaleString('pt-BR')}\n\n${jsonBody}`;
            validationBody.value = autoLoadedComment;
            
            // Adicionar classe visual para indicar que foi carregado automaticamente
            validationBody.classList.add('auto-loaded');
            
            // Remover a classe após 5 segundos
            setTimeout(() => {
                validationBody.classList.remove('auto-loaded');
            }, 5000);
            
            showCurlResult(`Curl executado com sucesso! Response body preenchido automaticamente no campo de validação.`, true);
            
            // Fechar modal de curl após 2 segundos
            setTimeout(() => {
                closeCurlModal();
            }, 2000);
        } else {
            showCurlResult(`Erro ao executar curl: ${result.message || 'Resposta inválida'}`, false);
        }
        
    } catch (error) {
        showCurlResult(`Erro na requisição: ${error.message}`, false);
    }
}
