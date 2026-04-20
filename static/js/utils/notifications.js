function showToastNotification(firstArg, secondArg = 'info', thirdArg = null) {
    let title = '';
    let message = '';
    let type = 'info';

    if (thirdArg !== null) {
        title = firstArg || '';
        message = secondArg || '';
        type = thirdArg || 'info';
    } else {
        message = firstArg || '';
        type = secondArg || 'info';
    }

    const container = document.getElementById('toastContainer');
    if (container) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const icon = type === 'success' ? '✅' : '❌';
        const resolvedTitle = title || (type === 'success' ? 'Sucesso!' : type === 'error' ? 'Erro' : 'Informação');

        toast.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-content">
                <div class="toast-title">${resolvedTitle}</div>
                <div class="toast-message">${message}</div>
            </div>
        `;

        container.appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 100);

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (container.contains(toast)) {
                    container.removeChild(toast);
                }
            }, 300);
        }, 5000);

        return;
    }

    const existingNotification = document.getElementById('toast-notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    const notification = document.createElement('div');
    notification.id = 'toast-notification';
    notification.className = `toast toast-${type}`;
    notification.innerHTML = `
        <div class="toast-content">
            <span class="toast-icon">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('toast-show');
    }, 100);

    setTimeout(() => {
        if (notification.parentElement) {
            notification.classList.remove('toast-show');
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }
    }, 4000);
}
