// ===== AUTOMATIONS LIST - JavaScript específico =====

let currentPage = 1;
let currentSearch = '';
let totalPages = 1;

/**
 * Carrega as automações em formato de cards
 * @param {number} page - Página atual
 * @param {string} search - Termo de busca
 */
async function loadAutomationsCards(page = 1, search = '') {
    showLoading();
    hideAlert();
    hideEmptyState();
    
    try {
        let url = `/automations/paginated?page=${page}&per_page=10`;
        if (search) {
            url += `&search=${encodeURIComponent(search)}`;
        }
        
        const data = await safeFetch(url);
        
        if (data.automations && data.automations.length > 0) {
            displayAutomations(data.automations);
            createPagination('pagination', data.current_page, data.total_pages, loadAutomationsCards);
            currentPage = data.current_page;
            totalPages = data.total_pages;
        } else {
            showEmptyState();
        }
        
    } catch (error) {
        showAlert(`Erro ao carregar automações: ${error.message}`, true);
        showEmptyState();
    } finally {
        hideLoading();
    }
}

/**
 * Exibe as automações em formato de cards
 * @param {Array} automations - Array de automações
 */
function displayAutomations(automations) {
    const container = document.getElementById('automationsList');
    container.innerHTML = '';
    
    hideEmptyState();
    container.style.display = 'grid';
    
    automations.forEach(automation => {
        const cardDiv = document.createElement('div');
        cardDiv.className = 'card';
        
        const launchDate = automation.launch_date ? 
            new Date(automation.launch_date).toLocaleDateString('pt-BR') : 
            'Não informado';
        const description = automation.description || 'Nenhuma descrição disponível';
        
        // Criação da imagem ou placeholder
        const imageHtml = automation.image_base64 ? 
            `<div style="margin-bottom: 12px; text-align: center;">
                <img src="${automation.image_base64}" 
                     alt="${automation.name}" 
                     class="automation-image"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
                <div class="automation-placeholder" style="display: none;">
                    <div class="automation-placeholder-icon">🤖</div>
                    <div class="automation-placeholder-text">AUTOMAÇÃO</div>
                </div>
            </div>` : 
            `<div style="margin-bottom: 12px; text-align: center;">
                <div class="automation-placeholder">
                    <div class="automation-placeholder-icon">🤖</div>
                    <div class="automation-placeholder-text">AUTOMAÇÃO</div>
                </div>
            </div>`;

        cardDiv.innerHTML = `
            ${imageHtml}
            <div class="card-title">📝 ${automation.name}</div>
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
                <strong>💻 Linguagem:</strong> ${automation.language || 'Não informado'}
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
                ${automation.git ? 
                    `<a href="${automation.git}" class="btn-repo" target="_blank">🔗 Abrir Repositório</a>` : 
                    '<span style="color: #5e6c84; font-size: 12px;">🔗 Sem repositório</span>'
                }
            </div>
        `;
        
        container.appendChild(cardDiv);
    });
}

/**
 * Filtra automações por termo de busca
 */
function filterAutomations() {
    const searchTerm = document.getElementById('automationSearch').value.trim();
    currentSearch = searchTerm;
    loadAutomationsCards(1, searchTerm);
}

/**
 * Limpa a busca
 */
function clearSearch() {
    document.getElementById('automationSearch').value = '';
    currentSearch = '';
    loadAutomationsCards(1, '');
}

/**
 * Atualiza a lista de automações
 */
function refreshAutomations() {
    loadAutomationsCards(currentPage, currentSearch);
}

// ===== INICIALIZAÇÃO =====

/**
 * Inicializa a página de automações
 */
function initializeAutomationsPage() {
    // Carregar automações ao inicializar
    loadAutomationsCards();
    
    // Permitir busca com Enter
    const searchInput = document.getElementById('automationSearch');
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                filterAutomations();
            }
        });
        
        // Busca com debounce para melhor performance
        const debouncedSearch = debounce(filterAutomations, 500);
        searchInput.addEventListener('input', debouncedSearch);
    }
}

// Executa inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', initializeAutomationsPage);
