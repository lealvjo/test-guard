let currentValidationData = {};
let currentApiDocLanguage = 'python';

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

        const collectionNameEl = document.getElementById('modalCollectionName');
        const contractNameEl = document.getElementById('modalContractName');
        const versionEl = document.getElementById('modalVersion');
        const methodEl = document.getElementById('modalMethod');

        if (collectionNameEl) collectionNameEl.textContent = collectionName;
        if (contractNameEl) contractNameEl.textContent = contractName;
        if (versionEl) versionEl.textContent = version;
        if (methodEl) methodEl.textContent = method;

        const validationBody = document.getElementById('validationBody');
        if (validationBody) validationBody.value = '';

        const validationResult = document.getElementById('validationResult');
        if (validationResult) {
            validationResult.style.display = 'none';
            validationResult.textContent = '';
        }

        modal.style.display = 'block';

        loadSchemaPreview();
        refreshApiDocsIfVisible();
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
        refreshApiDocsIfVisible();
    } catch (error) {
        showValidationResult(false, 'JSON inválido! Verifique a sintaxe.');
    }
}

function openApiDocsModal() {
    const modal = document.getElementById('apiDocsModal');
    if (!modal) return;

    const collectionEl = document.getElementById('apiDocsCollectionName');
    const contractEl = document.getElementById('apiDocsContractName');
    const versionEl = document.getElementById('apiDocsVersion');
    const methodEl = document.getElementById('apiDocsMethod');

    if (collectionEl) collectionEl.textContent = currentValidationData.collectionName || '-';
    if (contractEl) contractEl.textContent = currentValidationData.contractName || '-';
    if (versionEl) versionEl.textContent = currentValidationData.version || 'v1.0';
    if (methodEl) methodEl.textContent = currentValidationData.method || 'POST';

    modal.style.display = 'block';
    renderApiDocExample(currentApiDocLanguage);
}

function closeApiDocsModal() {
    const modal = document.getElementById('apiDocsModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function refreshApiDocsIfVisible() {
    const modal = document.getElementById('apiDocsModal');
    if (modal && modal.style.display === 'block') {
        renderApiDocExample(currentApiDocLanguage);
    }
}

function cleanJsonFromComments(jsonText) {
    return jsonText
        .replace(/\/\/.*$/gm, '')
        .replace(/\/\*[\s\S]*?\*\//g, '')
        .trim();
}

function renderApiDocExample(language) {
    currentApiDocLanguage = language;
    const collectionName = currentValidationData.collectionName || 'nome-da-colecao';
    const contractName = currentValidationData.contractName || 'nome-do-contrato';
    const version = currentValidationData.version || 'v1.0';
    const method = currentValidationData.method || 'POST';
    let code = '';

    if (language === 'python') {
        code = `import requests

url = "http://localhost:5000/contract-validate"
payload = {
    "collection_name": "${collectionName}",
    "contract_name": "${contractName}",
    "version": "${version}",
    "method": "${method}",
    "body_to_validate": {
        # Aqui você deve colocar o payload JSON
        # que será comparado com o contrato.
    }
}

response = requests.post(url, json=payload, timeout=30)
print(response.status_code)
print(response.json())`;
    } else if (language === 'javascript') {
        code = `const url = "http://localhost:5000/contract-validate";
const payload = {
  collection_name: "${collectionName}",
  contract_name: "${contractName}",
  version: "${version}",
  method: "${method}",
  body_to_validate: {
    // Aqui você deve colocar o payload JSON
    // que será comparado com o contrato.
  }
};

const response = await fetch(url, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload)
});

const result = await response.json();
console.log(response.status, result);`;
    } else if (language === 'typescript') {
        code = `type ValidationPayload = {
  collection_name: string;
  contract_name: string;
  version: string;
  method: string;
  body_to_validate: Record<string, unknown>;
};

const url = "http://localhost:5000/contract-validate";
const payload: ValidationPayload = {
  collection_name: "${collectionName}",
  contract_name: "${contractName}",
  version: "${version}",
  method: "${method}",
  body_to_validate: {
    // Aqui você deve colocar o payload JSON
    // que será comparado com o contrato.
  }
};

const response = await fetch(url, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload)
});

const result = await response.json();
console.log(response.status, result);`;
    } else if (language === 'java') {
        code = `import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class ContractValidationExample {
    public static void main(String[] args) throws Exception {
        // Em body_to_validate, coloque o payload JSON
        // que será comparado com o contrato.
        String json = """
{
  "collection_name": "${collectionName}",
  "contract_name": "${contractName}",
  "version": "${version}",
  "method": "${method}",
  "body_to_validate": {}
}
""";

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("http://localhost:5000/contract-validate"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(json))
                .build();

        HttpClient client = HttpClient.newHttpClient();
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

        System.out.println(response.statusCode());
        System.out.println(response.body());
    }
}`;
    } else if (language === 'dotnet') {
        code = `using System.Net.Http;
using System.Text;
using System.Text.Json;

var client = new HttpClient();
var url = "http://localhost:5000/contract-validate";

var payload = new
{
    collection_name = "${collectionName}",
    contract_name = "${contractName}",
    version = "${version}",
    method = "${method}",
    body_to_validate = new
    {
        // Aqui você deve colocar o payload JSON
        // que será comparado com o contrato.
    }
};

var json = JsonSerializer.Serialize(payload);
var content = new StringContent(json, Encoding.UTF8, "application/json");

var response = await client.PostAsync(url, content);
var body = await response.Content.ReadAsStringAsync();

Console.WriteLine((int)response.StatusCode);
Console.WriteLine(body);`;
    } else if (language === 'curl') {
        code = `curl -X POST "http://localhost:5000/contract-validate" \\
  -H "Content-Type: application/json" \\
  -d '{
    "collection_name": "${collectionName}",
    "contract_name": "${contractName}",
    "version": "${version}",
    "method": "${method}",
    "body_to_validate": {
      // Aqui você deve colocar o payload JSON
      // que será comparado com o contrato.
    }
  }'`;
    }

    const codeEl = document.getElementById('apiDocCode');
    if (codeEl) {
        codeEl.textContent = code;
    }

    ['python', 'js', 'ts', 'java', 'dotnet', 'curl'].forEach((langKey) => {
        const btn = document.getElementById(`api-doc-lang-${langKey}`);
        if (!btn) return;

        const selectedKeyMap = {
            javascript: 'js',
            typescript: 'ts',
            dotnet: 'dotnet',
            curl: 'curl',
            python: 'python',
            java: 'java'
        };
        const selectedKey = selectedKeyMap[language] || language;
        btn.classList.toggle('active', langKey === selectedKey);
    });
}

async function copyApiDocExample() {
    const codeEl = document.getElementById('apiDocCode');
    if (!codeEl || !codeEl.textContent) {
        showValidationResult(false, 'Não há exemplo para copiar no momento.');
        return;
    }

    try {
        await navigator.clipboard.writeText(codeEl.textContent);
        showValidationResult(true, 'Exemplo copiado para a área de transferência.');
    } catch (error) {
        showValidationResult(false, 'Não foi possível copiar automaticamente. Copie manualmente o conteúdo da documentação.');
    }
}

function showValidationResult(success, message, data = null) {
    const resultDiv = document.getElementById('validationResult');

    if (typeof success === 'string') {
        const icon = message ? '✅' : '❌';
        const content = `${icon} ${success}`;
        resultDiv.textContent = content;
        resultDiv.className = message ? 'validation-result validation-success' : 'validation-result validation-error';
        resultDiv.style.display = 'block';
        return;
    }

    let content = message;
    if (!message.startsWith('✅') && !message.startsWith('❌')) {
        const icon = success ? '✅' : '❌';
        content = `${icon} ${message}`;
    }

    resultDiv.textContent = content;
    resultDiv.className = success ? 'validation-result validation-success' : 'validation-result validation-error';
    resultDiv.style.display = 'block';
}

async function executeValidation() {
    const validationBody = document.getElementById('validationBody');
    const bodyText = validationBody.value.trim();

    const validationResult = document.getElementById('validationResult');
    if (validationResult) {
        validationResult.style.display = 'none';
        validationResult.textContent = '';
    }

    const existingDetailsButton = document.querySelector('[onclick="showErrorDetails()"]');
    if (existingDetailsButton) {
        existingDetailsButton.remove();
    }

    if (!bodyText) {
        showValidationResult(false, 'Por favor, insira um JSON para validação');
        return;
    }

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
            let errorMessage = result.message || 'Erro na validação';

            if (result.validation_error && result.validation_error.path) {
                const pathValue = Array.isArray(result.validation_error.path)
                    ? result.validation_error.path.join('.')
                    : result.validation_error.path;

                if (pathValue && pathValue.trim() !== '') {
                    errorMessage += `\n\n📍 Path: ${pathValue}`;
                }
            }

            if (errorMessage.length > 100) {
                const preview = errorMessage.substring(0, 100) + '...';
                showValidationResult(false, preview);

                setTimeout(() => {
                    const resultDiv = document.getElementById('validationResult');
                    if (resultDiv) {
                        const detailsButton = document.createElement('div');
                        detailsButton.style.marginTop = '10px';
                        detailsButton.innerHTML = `<button onclick="showErrorDetails()" style="background: #dc3545; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; font-size: 13px;">🔍 Ver detalhes completos</button>`;
                        resultDiv.parentNode.insertBefore(detailsButton, resultDiv.nextSibling);

                        window.currentErrorDetails = {
                            message: errorMessage,
                            result: result
                        };

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

    if (window.currentErrorDetails) {
        errorData = window.currentErrorDetails;
    } else if (window.errorHistory && window.errorHistory.length > 0) {
        errorData = window.errorHistory[window.errorHistory.length - 1];
    }

    if (!errorData) {
        alert('Nenhum erro encontrado para exibir detalhes');
        return;
    }

    const {message} = errorData;
    let detailsModal = document.getElementById('errorDetailsModal');

    if (!detailsModal) {
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

    const contentDiv = document.getElementById('errorDetailsContent');

    if (contentDiv) {
        let formattedMessage = message;

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

document.addEventListener('click', function(event) {
    const validationModal = document.getElementById('validationModal');
    if (validationModal && event.target === validationModal) {
        closeModal();
    }

    const detailsModal = document.getElementById('errorDetailsModal');
    if (detailsModal && event.target === detailsModal) {
        closeErrorDetails();
    }

    const apiDocsModal = document.getElementById('apiDocsModal');
    if (apiDocsModal && event.target === apiDocsModal) {
        closeApiDocsModal();
    }
});
