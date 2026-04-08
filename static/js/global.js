// ===== UTILITÁRIOS GLOBAIS =====

/**
 * Mostra um alerta/toast na tela
 * @param {string} message - Mensagem a ser exibida
 * @param {boolean} isError - Se é erro (true) ou sucesso (false)
 * @param {number} duration - Duração em ms (padrão: 5000)
 */
function showAlert(message, isError = false, duration = 5000) {
    const alertBox = document.getElementById('alertBox');
    if (!alertBox) {
        console.warn('Elemento alertBox não encontrado');
        return;
    }
    
    const icon = isError ? '❌' : '✅';
    alertBox.innerHTML = `${icon} ${message}`;
    alertBox.className = 'alert ' + (isError ? 'alert-error' : 'alert-success');
    alertBox.style.display = 'block';
    
    // Auto-hide após duration
    if (duration > 0) {
        setTimeout(() => {
            alertBox.style.display = 'none';
        }, duration);
    }
}

/**
 * Esconde o alerta atual
 */
function hideAlert() {
    const alertBox = document.getElementById('alertBox');
    if (alertBox) {
        alertBox.style.display = 'none';
    }
}

/**
 * Mostra estado de loading
 * @param {string} elementId - ID do elemento a ser mostrado
 */
function showLoading(elementId = 'loadingMessage') {
    const loadingElement = document.getElementById(elementId);
    if (loadingElement) {
        loadingElement.style.display = 'block';
    }
}

/**
 * Esconde estado de loading
 * @param {string} elementId - ID do elemento a ser escondido
 */
function hideLoading(elementId = 'loadingMessage') {
    const loadingElement = document.getElementById(elementId);
    if (loadingElement) {
        loadingElement.style.display = 'none';
    }
}

/**
 * Mostra estado vazio
 * @param {string} elementId - ID do elemento a ser mostrado
 */
function showEmptyState(elementId = 'emptyState') {
    const emptyElement = document.getElementById(elementId);
    if (emptyElement) {
        emptyElement.style.display = 'block';
    }
}

/**
 * Esconde estado vazio
 * @param {string} elementId - ID do elemento a ser escondido
 */
function hideEmptyState(elementId = 'emptyState') {
    const emptyElement = document.getElementById(elementId);
    if (emptyElement) {
        emptyElement.style.display = 'none';
    }
}

// ===== UTILITÁRIOS DE FORMATAÇÃO =====

/**
 * Tenta fazer parse de JSON
 * @param {string} text - Texto para fazer parse
 * @returns {object|null} - Objeto parseado ou null se inválido
 */
function tryParseJSON(text) {
    try {
        return JSON.parse(text);
    } catch (e) {
        return null;
    }
}

/**
 * Formata JSON com indentação
 * @param {object} obj - Objeto para formatar
 * @param {number} spaces - Número de espaços para indentação
 * @returns {string} - JSON formatado
 */
function formatJSON(obj, spaces = 2) {
    return JSON.stringify(obj, null, spaces);
}

/**
 * Remove comentários de JSON
 * @param {string} jsonText - Texto JSON com comentários
 * @returns {string} - JSON limpo
 */
function cleanJsonFromComments(jsonText) {
    return jsonText
        .replace(/\/\/.*$/gm, '') // Remove comentários de linha
        .replace(/\/\*[\s\S]*?\*\//g, '') // Remove comentários de bloco
        .trim();
}

// ===== UTILITÁRIOS DE MODAL =====

/**
 * Abre uma modal
 * @param {string} modalId - ID da modal
 */
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Previne scroll do body
    }
}

/**
 * Fecha uma modal
 * @param {string} modalId - ID da modal
 */
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto'; // Restaura scroll do body
    }
}

/**
 * Fecha modal ao clicar fora dela
 */
function setupModalCloseOnClickOutside() {
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    });
}

// ===== UTILITÁRIOS DE FORMULÁRIO =====

/**
 * Valida se um campo está preenchido
 * @param {string} fieldId - ID do campo
 * @param {string} errorMessage - Mensagem de erro
 * @returns {boolean} - Se o campo é válido
 */
function validateRequired(fieldId, errorMessage = 'Este campo é obrigatório') {
    const field = document.getElementById(fieldId);
    if (!field || !field.value.trim()) {
        showAlert(errorMessage, true);
        if (field) field.focus();
        return false;
    }
    return true;
}

/**
 * Valida formato de email
 * @param {string} email - Email para validar
 * @returns {boolean} - Se o email é válido
 */
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Valida formato de URL
 * @param {string} url - URL para validar
 * @returns {boolean} - Se a URL é válida
 */
function validateURL(url) {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}

// ===== UTILITÁRIOS DE REQUISIÇÃO =====

/**
 * Faz uma requisição fetch com tratamento de erro
 * @param {string} url - URL da requisição
 * @param {object} options - Opções da requisição
 * @returns {Promise} - Promise da requisição
 */
async function safeFetch(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`Erro ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Erro na requisição:', error);
        throw error;
    }
}

// ===== UTILITÁRIOS DE PAGINAÇÃO =====

/**
 * Cria botões de paginação
 * @param {string} containerId - ID do container
 * @param {number} currentPage - Página atual
 * @param {number} totalPages - Total de páginas
 * @param {function} onPageChange - Callback para mudança de página
 */
function createPagination(containerId, currentPage, totalPages, onPageChange) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '';
    
    if (totalPages <= 1) return;
    
    // Botão anterior
    const prevButton = document.createElement('button');
    prevButton.textContent = '← Anterior';
    prevButton.disabled = currentPage === 1;
    prevButton.onclick = () => onPageChange(currentPage - 1);
    container.appendChild(prevButton);
    
    // Números das páginas
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        const pageButton = document.createElement('button');
        pageButton.textContent = i;
        pageButton.className = i === currentPage ? 'active' : '';
        pageButton.onclick = () => onPageChange(i);
        container.appendChild(pageButton);
    }
    
    // Botão próximo
    const nextButton = document.createElement('button');
    nextButton.textContent = 'Próximo →';
    nextButton.disabled = currentPage === totalPages;
    nextButton.onclick = () => onPageChange(currentPage + 1);
    container.appendChild(nextButton);
}

// ===== UTILITÁRIOS DE BUSCA =====

/**
 * Debounce para busca
 * @param {function} func - Função a ser executada
 * @param {number} wait - Tempo de espera em ms
 * @returns {function} - Função com debounce
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ===== INICIALIZAÇÃO =====

/**
 * Inicializa funcionalidades globais
 */
function initializeGlobalFeatures() {
    // Setup modal close on click outside
    setupModalCloseOnClickOutside();
    
    // Setup tooltips
    const tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', function() {
            const tooltipText = this.querySelector('.tooltiptext');
            if (tooltipText) {
                tooltipText.style.visibility = 'visible';
                tooltipText.style.opacity = '1';
            }
        });
        
        tooltip.addEventListener('mouseleave', function() {
            const tooltipText = this.querySelector('.tooltiptext');
            if (tooltipText) {
                tooltipText.style.visibility = 'hidden';
                tooltipText.style.opacity = '0';
            }
        });
    });
}

// Executa inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', initializeGlobalFeatures);

// ===== EXPORTS PARA MÓDULOS =====
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showAlert,
        hideAlert,
        showLoading,
        hideLoading,
        showEmptyState,
        hideEmptyState,
        tryParseJSON,
        formatJSON,
        cleanJsonFromComments,
        openModal,
        closeModal,
        validateRequired,
        validateEmail,
        validateURL,
        safeFetch,
        createPagination,
        debounce
    };
}
