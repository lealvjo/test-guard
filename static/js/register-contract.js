// ===== REGISTER CONTRACT - JavaScript específico =====

function backToHome() { 
    window.location.href = '/'; 
}

function showFormAlert(message, isError) {
    const alertBox = document.getElementById('formAlert');
    alertBox.textContent = message;
    alertBox.style.display = 'block';
    alertBox.className = 'alert ' + (isError ? 'alert-error' : 'alert-success');
}

function clearFormAlert() {
    const alertBox = document.getElementById('formAlert');
    alertBox.style.display = 'none';
    alertBox.textContent = '';
}

function addSchema() {
    const schemasContainer = document.getElementById('schemasContainer');
    const schemaIndex = schemasContainer.children.length;
    
    const schemaItem = document.createElement('div');
    schemaItem.className = 'schema-item';
    schemaItem.innerHTML = `
        <h4>Schema ${schemaIndex + 1}</h4>
        <div class="form-grid">
            <div>
                <label for="contract_${schemaIndex}">📄 Nome do Contrato</label>
                <input type="text" id="contract_${schemaIndex}" placeholder="Ex: contrato de validação de login" />
            </div>
            <div>
                <label for="version_${schemaIndex}">🏷️ Versão</label>
                <input type="text" id="version_${schemaIndex}" placeholder="Ex: v1, v2, v1.1" required />
                <small style="color: #5e6c84; font-size: 12px; margin-top: 4px; display: block;">
                    Versão deste contrato específico.
                </small>
            </div>
            <div>
                <label for="method_${schemaIndex}">🌐 Método HTTP</label>
                <select id="method_${schemaIndex}" required>
                    <option value="" disabled selected>Selecione...</option>
                    <option value="GET">GET</option>
                    <option value="POST">POST</option>
                    <option value="PUT">PUT</option>
                    <option value="DELETE">DELETE</option>
                    <option value="PATCH">PATCH</option>
                    <option value="HEAD">HEAD</option>
                    <option value="OPTIONS">OPTIONS</option>
                </select>
            </div>
            <div class="full">
                <label for="schema_${schemaIndex}">📋 Schema JSON</label>
                <textarea id="schema_${schemaIndex}" rows="8" placeholder='{
  "type": "object",
  "properties": {
    "email": {
      "type": "string",
      "format": "email"
    },
    "password": {
      "type": "string",
      "minLength": 6
    }
  },
  "required": ["email", "password"]
}'></textarea>
                <small style="color: #5e6c84; font-size: 12px; margin-top: 4px; display: block;">
                    Defina o schema JSON que será usado para validar este contrato.
                </small>
            </div>
        </div>
        <div style="margin-top: 16px; display: flex; gap: 8px;">
            <button type="button" class="btn btn-secondary" onclick="removeSchema(this)">🗑️ Remover Schema</button>
        </div>
    `;
    
    schemasContainer.appendChild(schemaItem);
    clearFormAlert();
}

function removeSchema(button) {
    const schemaItem = button.closest('.schema-item');
    schemaItem.remove();
    clearFormAlert();
}

function validateForm() {
    const collectionName = document.getElementById('collectionName').value.trim();
    const description = document.getElementById('description').value.trim();
    const schemasContainer = document.getElementById('schemasContainer');
    
    // Limpar alertas anteriores
    clearFormAlert();
    
    // Validar nome da coleção
    if (!collectionName) {
        showFormAlert('❌ Por favor, informe o nome da coleção.', true);
        return false;
    }
    
    // Validar se há pelo menos um schema
    if (schemasContainer.children.length === 0) {
        showFormAlert('❌ Por favor, adicione pelo menos um schema.', true);
        return false;
    }
    
    // Validar cada schema
    for (let i = 0; i < schemasContainer.children.length; i++) {
        const schemaItem = schemasContainer.children[i];
        const contractName = schemaItem.querySelector(`input[id^="contract_"]`).value.trim();
        const version = schemaItem.querySelector(`input[id^="version_"]`).value.trim();
        const method = schemaItem.querySelector(`select[id^="method_"]`).value;
        const schema = schemaItem.querySelector(`textarea[id^="schema_"]`).value.trim();
        
        if (!contractName) {
            showFormAlert(`❌ Schema ${i + 1}: Nome do contrato é obrigatório.`, true);
            return false;
        }
        
        if (!version) {
            showFormAlert(`❌ Schema ${i + 1}: Versão é obrigatória.`, true);
            return false;
        }
        
        if (!method) {
            showFormAlert(`❌ Schema ${i + 1}: Método HTTP é obrigatório.`, true);
            return false;
        }
        
        if (!schema) {
            showFormAlert(`❌ Schema ${i + 1}: Schema JSON é obrigatório.`, true);
            return false;
        }
        
        // Validar se o schema é um JSON válido
        try {
            JSON.parse(schema);
        } catch (error) {
            showFormAlert(`❌ Schema ${i + 1}: JSON inválido. Verifique a sintaxe.`, true);
            return false;
        }
    }
    
    return true;
}

function submitForm() {
    if (!validateForm()) {
        return false;
    }
    
    const collectionName = document.getElementById('collectionName').value.trim();
    const description = document.getElementById('description').value.trim();
    const schemasContainer = document.getElementById('schemasContainer');
    
    // Coletar dados dos schemas
    const schemas = [];
    for (let i = 0; i < schemasContainer.children.length; i++) {
        const schemaItem = schemasContainer.children[i];
        const contractName = schemaItem.querySelector(`input[id^="contract_"]`).value.trim();
        const version = schemaItem.querySelector(`input[id^="version_"]`).value.trim();
        const method = schemaItem.querySelector(`select[id^="method_"]`).value;
        const schema = schemaItem.querySelector(`textarea[id^="schema_"]`).value.trim();
        
        schemas.push({
            contract_name: contractName,
            version: version,
            method: method,
            schema: JSON.parse(schema)
        });
    }
    
    // Criar payload
    const payload = {
        collection_name: collectionName,
        description: description,
        schemas: schemas
    };
    
    // Enviar para o servidor
    fetch('/register-contract', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showFormAlert('✅ Coleção cadastrada com sucesso!', false);
            // Limpar formulário após sucesso
            setTimeout(() => {
                document.getElementById('collectionName').value = '';
                document.getElementById('description').value = '';
                schemasContainer.innerHTML = '';
                clearFormAlert();
            }, 2000);
        } else {
            showFormAlert('❌ Erro ao cadastrar: ' + (data.message || 'Erro desconhecido'), true);
        }
    })
    .catch(error => {
        showFormAlert('❌ Erro na requisição: ' + error.message, true);
    });
    
    return false; // Prevenir submit padrão do formulário
}

