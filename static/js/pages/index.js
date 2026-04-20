let currentPage = 1;
let currentSearch = '';
let currentStatus = '';
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
    document.getElementById('reportsList').style.display = 'none';
    document.getElementById('emptyState').style.display = 'none';
}

function hideLoading() {
    document.getElementById('loadingMessage').style.display = 'none';
}

function showEmptyState() {
    document.getElementById('emptyState').style.display = 'block';
    document.getElementById('reportsList').style.display = 'none';
    document.getElementById('reportsList').innerHTML = '';
}

function hideEmptyState() {
    document.getElementById('emptyState').style.display = 'none';
}

function toggleReportDetails(reportId) {
    const details = document.getElementById(`details-${reportId}`);
    const icon = document.getElementById(`icon-${reportId}`);

    if (details.classList.contains('expanded')) {
        details.classList.remove('expanded');
        icon.classList.remove('expanded');
    } else {
        details.classList.add('expanded');
        icon.classList.add('expanded');
    }
}

function formatDate(dateStr) {
    const options = {year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric'};
    return new Date(dateStr).toLocaleDateString('pt-BR', options);
}

function getStatusClass(status) {
    switch (status.toLowerCase()) {
        case 'completed':
            return 'status-completed';
        case 'pending':
            return 'status-pending';
        case 'failed':
            return 'status-failed';
        default:
            return 'status-pending';
    }
}

async function loadReports(page = 1, search = '', status = '') {
    showLoading();
    hideError();
    hideEmptyState();

    try {
        let url = `/reports/paginated?page=${page}&per_page=10`;
        if (search) {
            url += `&search=${encodeURIComponent(search)}`;
        }

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Erro ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        if (data.reports && data.reports.length > 0) {
            let filteredReports = data.reports;
            if (status) {
                filteredReports = data.reports.filter(report =>
                    report.status.toLowerCase() === status.toLowerCase()
                );
            }

            if (filteredReports.length > 0) {
                displayReports(filteredReports);
                updatePagination(data.current_page, data.total_pages);
                currentPage = data.current_page;
                totalPages = data.total_pages;
            } else {
                showEmptyState();
            }
        } else {
            showEmptyState();
        }

    } catch (error) {
        showError(`Erro ao carregar relatórios: ${error.message}`);
        showEmptyState();
    } finally {
        hideLoading();
    }
}

function displayReports(reports) {
    const container = document.getElementById('reportsList');
    container.innerHTML = '';

    hideEmptyState();
    container.style.display = 'block';

    reports.forEach(report => {
        const reportDiv = document.createElement('div');
        reportDiv.className = 'report-item';

        const reportDate = formatDate(report.report_date);
        const statusClass = getStatusClass(report.status);

        reportDiv.innerHTML = `
            <div class="report-header">
                <div onclick="toggleReportDetails(${report.id_report})" style="flex: 1; cursor: pointer;">
                    <h3 class="report-title">📊 ${report.name}</h3>
                    <p class="report-meta">
                        🆔 ID: ${report.id_report} | 
                        👥 Squad: ${report.squad} | 
                        🎯 Tipo: ${report.type || 'Não informado'} | 
                        📅 Data: ${reportDate}
                    </p>
                </div>
                <div class="report-actions">
                    <span class="status-badge ${statusClass}">${report.status}</span>
                    <span id="icon-${report.id_report}" class="expand-icon" onclick="toggleReportDetails(${report.id_report})">▶</span>
                </div>
            </div>
            <div id="details-${report.id_report}" class="report-details">
                <div class="report-info">
                    <div class="report-info-title">📋 Detalhes do Relatório</div>
                    <div class="report-info-content">
🆔 ID do Relatório: ${report.id_report}
📊 Nome da Automação: ${report.name}
👥 Squad: ${report.squad}
🎯 Tipo: ${report.type || 'Não informado'}
📈 Status: ${report.status}
📅 Data do Relatório: ${reportDate}
                    </div>
                </div>
                <div style="text-align: center; margin-top: 16px;">
                    <a href="${report.url_report}" class="btn-report" target="_blank">🔗 Abrir Relatório</a>
                    ${report.junit ? `<a href="/reports/${report.id_report}/junit" class="btn-report btn-junit" target="_blank">🧪 Abrir Relatório JUnit</a>` : ''}
                </div>
            </div>
        `;

        container.appendChild(reportDiv);
    });
}

function updatePagination(currentPageValue, totalPagesValue) {
    const container = document.getElementById('pagination');
    container.innerHTML = '';

    if (totalPagesValue <= 1) return;

    const prevButton = document.createElement('button');
    prevButton.textContent = '← Anterior';
    prevButton.disabled = currentPageValue === 1;
    prevButton.onclick = () => loadReports(currentPageValue - 1, currentSearch, currentStatus);
    container.appendChild(prevButton);

    const startPage = Math.max(1, currentPageValue - 2);
    const endPage = Math.min(totalPagesValue, currentPageValue + 2);

    for (let i = startPage; i <= endPage; i++) {
        const pageButton = document.createElement('button');
        pageButton.textContent = i;
        pageButton.className = i === currentPageValue ? 'active' : '';
        pageButton.onclick = () => loadReports(i, currentSearch, currentStatus);
        container.appendChild(pageButton);
    }

    const nextButton = document.createElement('button');
    nextButton.textContent = 'Próximo →';
    nextButton.disabled = currentPageValue === totalPagesValue;
    nextButton.onclick = () => loadReports(currentPageValue + 1, currentSearch, currentStatus);
    container.appendChild(nextButton);
}

function searchReports() {
    const searchTerm = document.getElementById('searchInput').value.trim();
    const statusFilter = document.getElementById('statusFilter').value;
    currentSearch = searchTerm;
    currentStatus = statusFilter;
    loadReports(1, searchTerm, statusFilter);
}

function filterByStatus() {
    const statusFilter = document.getElementById('statusFilter').value;
    currentSearch = '';
    currentStatus = statusFilter;
    document.getElementById('searchInput').value = '';
    loadReports(1, '', statusFilter);
}

function clearSearch() {
    document.getElementById('searchInput').value = '';
    document.getElementById('statusFilter').value = '';
    currentSearch = '';
    currentStatus = '';
    loadReports(1, '', '');
}

function refreshReports() {
    loadReports(currentPage, currentSearch, currentStatus);
}

window.onload = () => {
    loadReports();
};

document.getElementById('searchInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        searchReports();
    }
});
