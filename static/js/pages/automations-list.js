let currentPage = 1;
let currentSearch = '';
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
    document.getElementById('automationsList').style.display = 'none';
    document.getElementById('emptyState').style.display = 'none';
}

function hideLoading() {
    document.getElementById('loadingMessage').style.display = 'none';
}

function showEmptyState() {
    document.getElementById('emptyState').style.display = 'block';
    document.getElementById('automationsList').style.display = 'none';
    document.getElementById('automationsList').innerHTML = '';
}

function hideEmptyState() {
    document.getElementById('emptyState').style.display = 'none';
}

async function loadAutomationsCards(page = 1, search = '') {
    showLoading();
    hideError();
    hideEmptyState();

    try {
        let url = `/automations/paginated?page=${page}&per_page=12`;
        if (search) {
            url += `&search=${encodeURIComponent(search)}`;
        }

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Erro ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        if (data.automations && data.automations.length > 0) {
            displayAutomations(data.automations);
            updatePagination(data.current_page, data.total_pages);
            currentPage = data.current_page;
            totalPages = data.total_pages;
        } else {
            showEmptyState();
        }

    } catch (error) {
        showError(`Erro ao carregar automações: ${error.message}`);
        showEmptyState();
    } finally {
        hideLoading();
    }
}

function displayAutomations(automations) {
    const container = document.getElementById('automationsList');
    container.innerHTML = '';

    hideEmptyState();
    container.style.display = 'grid';

    automations.forEach(automation => {
        const cardDiv = document.createElement('div');
        cardDiv.className = 'card';

        const launchDate = automation.launch_date ? new Date(automation.launch_date).toLocaleDateString('pt-BR') : 'Não informado';
        const description = automation.description || 'Nenhuma descrição disponível';

        const imageHtml = automation.image_base64 ?
            `<div style="margin-bottom: 12px; text-align: center;">
                <img src="${automation.image_base64}" alt="${automation.name}" 
                     style="width: 80%; height: 100px; border-radius: 6px; border: 1px solid #dfe1e6; object-fit: cover;" />
            </div>` :
            `<div style="margin-bottom: 12px; text-align: center;">
                <div style="width: 80%; height: 100px; background: linear-gradient(135deg, #0065ff 0%, #0047cc 100%); border-radius: 6px; border: 1px solid #dfe1e6; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; margin: 0 auto;">
                    <div style="font-size: 28px; margin-bottom: 3px;">🤖</div>
                    <div style="font-size: 9px; font-weight: 600; opacity: 0.9;">AUTOMAÇÃO</div>
                </div>
            </div>`;

        cardDiv.innerHTML = `
            ${imageHtml}
            <div class="card-title-row">
                <div class="card-title">📝 ${automation.name}</div>
                <button class="btn-doc-api-mini" title="Gerar relatórios para esta automação" aria-label="Gerar relatórios para esta automação">📘</button>
            </div>
            <div class="card-meta">
                <strong>🆔 ID:</strong> ${automation.id}
            </div>
            <div class="card-meta">
                <strong>👥 Squad:</strong> ${automation.squad || 'Não informado'}
            </div>
            <div class="card-meta">
                <strong>🎯 Tipo:</strong> ${automation.type || 'Não informado'}
            </div>
            <div class="card-meta">
                <strong>💻 Linguagem:</strong> ${automation.language}
            </div>
            <div class="card-meta">
                <strong>🥒 Cucumber:</strong> ${automation.cucumber || 'Não informado'}
            </div>
            <div class="card-meta">
                <strong>📅 Lançamento:</strong> ${launchDate}
            </div>
            <div class="card-description" title="${description}">
                📄 ${description}
            </div>
            <div class="card-actions">
                ${automation.git ? `<a href="${automation.git}" class="btn-repo" target="_blank">🔗 Abrir Repositório</a>` : '<span style="color: #5e6c84; font-size: 12px;">🔗 Sem repositório</span>'}
            </div>
        `;

        const docsButton = cardDiv.querySelector('.btn-doc-api-mini');
        if (docsButton) {
            docsButton.addEventListener('click', () => openAutomationApiDocsModal(automation));
        }

        container.appendChild(cardDiv);
    });
}

function updatePagination(currentPageValue, totalPagesValue) {
    const container = document.getElementById('pagination');
    container.innerHTML = '';

    if (totalPagesValue <= 1) return;

    const prevButton = document.createElement('button');
    prevButton.textContent = '← Anterior';
    prevButton.disabled = currentPageValue === 1;
    prevButton.onclick = () => loadAutomationsCards(currentPageValue - 1, currentSearch);
    container.appendChild(prevButton);

    const startPage = Math.max(1, currentPageValue - 2);
    const endPage = Math.min(totalPagesValue, currentPageValue + 2);

    for (let i = startPage; i <= endPage; i++) {
        const pageButton = document.createElement('button');
        pageButton.textContent = i;
        pageButton.className = i === currentPageValue ? 'active' : '';
        pageButton.onclick = () => loadAutomationsCards(i, currentSearch);
        container.appendChild(pageButton);
    }

    const nextButton = document.createElement('button');
    nextButton.textContent = 'Próximo →';
    nextButton.disabled = currentPageValue === totalPagesValue;
    nextButton.onclick = () => loadAutomationsCards(currentPageValue + 1, currentSearch);
    container.appendChild(nextButton);
}

function filterAutomations() {
    const searchTerm = document.getElementById('automationSearch').value.trim();
    currentSearch = searchTerm;
    loadAutomationsCards(1, searchTerm);
}

function clearSearch() {
    document.getElementById('automationSearch').value = '';
    currentSearch = '';
    loadAutomationsCards(1, '');
}

function refreshAutomations() {
    loadAutomationsCards(currentPage, currentSearch);
}

window.onload = () => {
    loadAutomationsCards();
};

document.getElementById('automationSearch').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        filterAutomations();
    }
});
