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
            <div>
                <label for="endpoint_${schemaIndex}">🔗 Endpoint</label>
                <input type="text" id="endpoint_${schemaIndex}" placeholder="Ex: /api/users/login" required />
                <small style="color: #5e6c84; font-size: 12px; margin-top: 4px; display: block;">
                    Caminho da API (ex: /api/users, /auth/login)
                </small>
            </div>
            <div class="full">
                <label for="expected_${schemaIndex}">📋 JSON Schema</label>
                <textarea id="expected_${schemaIndex}" class="json-editor" placeholder='{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "message": {
      "type": "string"
    },
    "status": {
      "type": "string"
    }
  },
  "required": ["message"]
}' style="height: 350px; min-height: 350px;"></textarea>
            </div>
        </div>
        <div class="schema-actions">
            <button type="button" class="btn btn-small btn-danger" onclick="removeSchema(this)">🗑️ Remover Schema</button>
            <button type="button" class="btn btn-small" onclick="formatJson(${schemaIndex})">✨ Formatar JSON</button>
        </div>
    `;

    schemasContainer.appendChild(schemaItem);
}

function removeSchema(button) {
    button.closest('.schema-item').remove();
    updateSchemaNumbers();
}

function updateSchemaNumbers() {
    const schemas = document.querySelectorAll('.schema-item h4');
    schemas.forEach((header, index) => {
        header.textContent = `Schema ${index + 1}`;
    });
}

function formatJson(schemaIndex) {
    const textarea = document.getElementById(`expected_${schemaIndex}`);
    try {
        const json = JSON.parse(textarea.value);
        textarea.value = JSON.stringify(json, null, 2);
    } catch (e) {
        showFormAlert('JSON inválido para formatação', true);
    }
}

async function submitContract(event) {
    event.preventDefault();
    clearFormAlert();

    const payload = {
        name: document.getElementById('name').value.trim(),
        squad: document.getElementById('squad').value.trim(),
        repository_url: document.getElementById('repositoryUrl').value.trim(),
        schemas: []
    };

    if (!payload.name) {
        return showFormAlert('Nome da coleção é obrigatório.', true);
    }
    if (!payload.squad) {
        return showFormAlert('Squad é obrigatório.', true);
    }

    try {
        const checkResponse = await fetch('/contracts/check-name', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name: payload.name})
        });

        if (checkResponse.ok) {
            const checkResult = await checkResponse.json();
            if (!checkResult.available) {
                return showFormAlert(`Já existe uma coleção com o nome "${payload.name}". Escolha um nome diferente.`, true);
            }
        }
    } catch (e) {
        console.warn('Verificação de nome falhou, continuando com validação no backend:', e);
    }

    const schemaItems = document.querySelectorAll('.schema-item');
    if (schemaItems.length === 0) {
        return showFormAlert('Adicione pelo menos um schema.', true);
    }

    const contractVersions = new Set();
    for (let i = 0; i < schemaItems.length; i++) {
        const contractName = document.getElementById(`contract_${i}`).value.trim();
        const contractVersion = document.getElementById(`version_${i}`).value.trim();

        if (contractName && contractVersion) {
            const contractKey = `${contractName.toLowerCase()}_${contractVersion}`;
            if (contractVersions.has(contractKey)) {
                return showFormAlert(`Já existe um contrato com o nome "${contractName}" na versão "${contractVersion}" na mesma coleção.`, true);
            }
            contractVersions.add(contractKey);
        }
    }

    for (let i = 0; i < schemaItems.length; i++) {
        const contractName = document.getElementById(`contract_${i}`).value.trim();
        const contractVersion = document.getElementById(`version_${i}`).value.trim();
        const httpMethod = document.getElementById(`method_${i}`).value.trim();
        const endpoint = document.getElementById(`endpoint_${i}`).value.trim();
        const expectedJson = document.getElementById(`expected_${i}`).value.trim();

        if (!contractName) {
            return showFormAlert(`Nome do contrato é obrigatório no Schema ${i + 1}.`, true);
        }
        if (!contractVersion) {
            return showFormAlert(`Versão é obrigatória no Schema ${i + 1}.`, true);
        }
        if (!httpMethod) {
            return showFormAlert(`Método HTTP é obrigatório no Schema ${i + 1}.`, true);
        }
        if (!endpoint) {
            return showFormAlert(`Endpoint é obrigatório no Schema ${i + 1}.`, true);
        }
        if (!expectedJson) {
            return showFormAlert(`JSON Schema é obrigatório no Schema ${i + 1}.`, true);
        }

        const allowedMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'];
        if (!allowedMethods.includes(httpMethod)) {
            return showFormAlert(`Método HTTP '${httpMethod}' não é válido no Schema ${i + 1}. Métodos permitidos: ${allowedMethods.join(', ')}`, true);
        }

        if (!endpoint.startsWith('/')) {
            return showFormAlert(`Endpoint deve começar com '/' no Schema ${i + 1}. Exemplo: /api/users`, true);
        }

        try {
            const expected = JSON.parse(expectedJson);
            payload.schemas.push({
                contract: contractName,
                version: contractVersion,
                method: httpMethod,
                endpoint: endpoint,
                expected: expected
            });
        } catch (e) {
            return showFormAlert(`JSON inválido no Schema ${i + 1}: ${e.message}`, true);
        }
    }

    try {
        const resp = await fetch('/contract', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });

        const result = await resp.json();

        if (!resp.ok) {
            throw new Error(result.error || 'Falha ao salvar coleção de contratos');
        }

        showFormAlert('Coleção de contratos cadastrada com sucesso!', false);
        document.getElementById('contractForm').reset();
        document.getElementById('schemasContainer').innerHTML = '';
    } catch (e) {
        showFormAlert(e.message, true);
    }
}

window.onload = function() {
    addSchema();
};
