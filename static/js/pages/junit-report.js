(function () {
    const rows = Array.from(document.querySelectorAll('tbody tr'));
    const perPage = 10;
    if (!rows.length) return;

    const paginationMeta = document.querySelector('.pagination-meta');
    const serverPaginationVisible = !!paginationMeta && paginationMeta.textContent.includes('Exibindo');
    if (serverPaginationVisible && rows.length <= perPage) return;

    const container = document.getElementById('clientPagination');
    const meta = document.getElementById('clientPaginationMeta');
    const pagesContainer = document.getElementById('clientPages');
    const prevBtn = document.getElementById('clientPrev');
    const nextBtn = document.getElementById('clientNext');
    if (!container || !meta || !pagesContainer || !prevBtn || !nextBtn) return;

    container.style.display = 'flex';

    let currentPage = 1;
    const total = rows.length;
    const totalPages = Math.max(1, Math.ceil(total / perPage));

    function render() {
        const start = (currentPage - 1) * perPage;
        const end = start + perPage;

        rows.forEach((row, idx) => {
            row.style.display = (idx >= start && idx < end) ? '' : 'none';
        });

        meta.textContent = `Exibindo ${start + 1}-${Math.min(end, total)} de ${total} testcases | Página ${currentPage} de ${totalPages}`;

        pagesContainer.innerHTML = '';
        for (let p = 1; p <= totalPages; p++) {
            const link = document.createElement('a');
            link.href = '#';
            link.className = 'btn btn-page' + (p === currentPage ? ' disabled' : '');
            link.textContent = String(p);
            link.onclick = (e) => {
                e.preventDefault();
                if (p !== currentPage) {
                    currentPage = p;
                    render();
                }
            };
            pagesContainer.appendChild(link);
        }

        prevBtn.classList.toggle('disabled', currentPage === 1);
        nextBtn.classList.toggle('disabled', currentPage === totalPages);
    }

    prevBtn.onclick = (e) => {
        e.preventDefault();
        if (currentPage > 1) {
            currentPage -= 1;
            render();
        }
    };

    nextBtn.onclick = (e) => {
        e.preventDefault();
        if (currentPage < totalPages) {
            currentPage += 1;
            render();
        }
    };

    render();
})();
