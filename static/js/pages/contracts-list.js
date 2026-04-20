let currentPage = 1;
let currentSearch = '';
let currentSquad = '';
let totalPages = 1;

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function hideError() {
    document.getElementById('errorMessage').style.display = 'none';
}

function showLoading() {
    document.getElementById('loadingMessage').style.display = 'block';
    document.getElementById('contractsList').style.display = 'none';
    document.getElementById('emptyState').style.display = 'none';
}

function hideLoading() {
    document.getElementById('loadingMessage').style.display = 'none';
}

function showEmptyState() {
    document.getElementById('emptyState').style.display = 'block';
    document.getElementById('contractsList').style.display = 'none';
    document.getElementById('contractsList').innerHTML = '';
}

function hideEmptyState() {
    document.getElementById('emptyState').style.display = 'none';
}

function toggleContractDetails(contractId) {
    const details = document.getElementById(`details-${contractId}`);
    const icon = document.getElementById(`icon-${contractId}`);

    if (details.classList.contains('expanded')) {
        details.classList.remove('expanded');
        icon.classList.remove('expanded');
    } else {
        details.classList.add('expanded');
        icon.classList.add('expanded');
    }
}

async function loadContracts(page = 1, search = '', squad = '') {
    showLoading();
    hideError();
    hideEmptyState();

    try {
        let url = `/contracts/paginated?page=${page}&per_page=10`;
        if (search) {
            url += `&search=${encodeURIComponent(search)}`;
        }
        if (squad) {
            url += `&squad=${encodeURIComponent(squad)}`;
        }

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Erro ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        if (data.contracts && data.contracts.length > 0) {
            displayContracts(data.contracts);
            updatePagination(data.current_page, data.total_pages);
            currentPage = data.current_page;
            totalPages = data.total_pages;
        } else {
            showEmptyState();
        }

    } catch (error) {
        showError(`Erro ao carregar coleções: ${error.message}`);
        showEmptyState();
    } finally {
        hideLoading();
    }
}

function displayContracts(contracts) {
    const container = document.getElementById('contractsList');
    container.innerHTML = '';
    hideEmptyState();
    container.style.display = 'block';

    contracts.forEach(contract => {
        const contractDiv = document.createElement('div');
        contractDiv.className = 'contract-item';

        const schemasCount = contract.schemas ? contract.schemas.length : 0;
        const createdDateTime = new Date(contract.created_at).toLocaleString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        contractDiv.innerHTML = `
            <div class="contract-header">
                <div onclick="toggleContractDetails(${contract.id})" style="flex: 1; cursor: pointer;">
                    <h3 class="contract-title">📁 ${contract.name}</h3>
                    <p class="contract-meta">
                        👥 Squad: ${contract.squad} | 
                        📋 Contratos: ${schemasCount} | 
                        📅 Criado em: ${createdDateTime}
                        ${contract.repository_url ? ` | 🔗 <a href="${contract.repository_url}" target="_blank" class="repository-link" style="color: #0065ff; text-decoration: none;" data-tooltip="Abrir repositório do projeto que está sendo testado por esta coleção de contratos">Repositório</a>` : ''}
                    </p>
                </div>
                <div class="contract-actions">
                    <button class="btn-add-contract" data-collection-id="${contract.id}" data-collection-name="${contract.name}" title="Adicionar contrato">➕</button>
                    <span id="icon-${contract.id}" class="expand-icon" onclick="toggleContractDetails(${contract.id})">▶</span>
                </div>
            </div>
            <div id="details-${contract.id}" class="contract-details">
                ${contract.schemas ? contract.schemas.map((schema, index) => {
            const schemaTitle = schema.contract || schema.title || `Contrato ${index + 1}`;
            const schemaVersion = schema.version || 'v1';
            const schemaMethod = schema.method || 'N/A';
            const schemaEndpoint = schema.endpoint || 'N/A';

            const methodIcons = {
                'GET': '📥',
                'POST': '📤',
                'PUT': '🔄',
                'DELETE': '🗑️',
                'PATCH': '🔧',
                'HEAD': '👁️',
                'OPTIONS': '⚙️',
                'N/A': '❓'
            };

            const getEndpointIcon = (endpoint) => {
                if (endpoint === 'N/A') return '❓';
                if (endpoint.includes('/auth') || endpoint.includes('/login')) return '🔐';
                if (endpoint.includes('/user')) return '👤';
                if (endpoint.includes('/api')) return '🔌';
                if (endpoint.includes('/admin')) return '⚡';
                if (endpoint.includes('/mobile')) return '📱';
                if (endpoint.includes('/web')) return '🌐';
                return '🔗';
            };

            return `
                        <div class="contract-schema">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div class="contract-schema-title">${schemaTitle}</div>
                                    <small style="color: #5e6c84; font-size: 12px;">
                                        🏷️ Versão: ${schemaVersion} | 
                                        ${methodIcons[schemaMethod]} Método: <span style="color: #0065ff; font-weight: 600;">${schemaMethod}</span> | 
                                        ${getEndpointIcon(schemaEndpoint)} Endpoint: <span style="color: #006644; font-weight: 600;">${schemaEndpoint}</span>
                                    </small>
                                </div>
                                <div style="display: flex; gap: 8px;">
                                    <button class="btn btn-primary btn-small" onclick="openValidationModal('${contract.name}', '${schemaTitle}', '${schemaVersion}', '${schemaMethod}')">▶️ Executar</button>
                                    <button class="btn btn-secondary btn-small" onclick="openEditContractModal('${contract.name}', '${schemaTitle}', '${schemaVersion}')">✏️ Editar</button>
                                </div>
                            </div>
                        </div>
                    `;
        }).join('') : '<p>📭 Nenhum contrato encontrado nesta coleção.</p>'}
            </div>
        `;

        container.appendChild(contractDiv);
    });

    container.querySelectorAll('.btn-add-contract').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const collectionId = this.getAttribute('data-collection-id');
            const collectionName = this.getAttribute('data-collection-name');
            openAddContractModal(collectionId, collectionName);
        });
    });
}

function updatePagination(currentPageValue, totalPagesValue) {
    const container = document.getElementById('pagination');
    container.innerHTML = '';

    if (totalPagesValue <= 1) return;

    const prevButton = document.createElement('button');
    prevButton.textContent = '← Anterior';
    prevButton.disabled = currentPageValue === 1;
    prevButton.onclick = () => loadContracts(currentPageValue - 1, currentSearch, currentSquad);
    container.appendChild(prevButton);

    const startPage = Math.max(1, currentPageValue - 2);
    const endPage = Math.min(totalPagesValue, currentPageValue + 2);

    for (let i = startPage; i <= endPage; i++) {
        const pageButton = document.createElement('button');
        pageButton.textContent = i;
        pageButton.className = i === currentPageValue ? 'active' : '';
        pageButton.onclick = () => loadContracts(i, currentSearch, currentSquad);
        container.appendChild(pageButton);
    }

    const nextButton = document.createElement('button');
    nextButton.textContent = 'Próximo →';
    nextButton.disabled = currentPageValue === totalPagesValue;
    nextButton.onclick = () => loadContracts(currentPageValue + 1, currentSearch, currentSquad);
    container.appendChild(nextButton);
}

function searchContracts() {
    const searchTerm = document.getElementById('searchInput').value.trim();
    const squadFilter = document.getElementById('squadFilter').value;
    currentSearch = searchTerm;
    currentSquad = squadFilter;
    loadContracts(1, searchTerm, squadFilter);
}

function filterBySquad() {
    const squadFilter = document.getElementById('squadFilter').value;
    currentSearch = '';
    currentSquad = squadFilter;
    document.getElementById('searchInput').value = '';
    loadContracts(1, '', squadFilter);
}

function clearSearch() {
    document.getElementById('searchInput').value = '';
    document.getElementById('squadFilter').value = '';
    currentSearch = '';
    currentSquad = '';
    loadContracts(1, '', '');
}

function refreshContracts() {
    loadContracts(currentPage, currentSearch, currentSquad);
}

window.onload = () => {
    loadContracts();
};

document.getElementById('searchInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        searchContracts();
    }
});
