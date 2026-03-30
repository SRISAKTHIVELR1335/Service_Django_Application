document.addEventListener('DOMContentLoaded', function() {
    initLogFilters();
    initLogModals();
});

function initLogFilters() {
    const filterForm = document.getElementById('logFilterForm');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            const inputs = filterForm.querySelectorAll('input, select');
            inputs.forEach(function(input) {
                if (!input.value) {
                    input.disabled = true;
                }
            });
        });
    }
}

function initLogModals() {
    const logModals = document.querySelectorAll('[id^="logModal"]');
    logModals.forEach(function(modal) {
        modal.addEventListener('shown.bs.modal', function() {
            const pre = modal.querySelector('pre');
            if (pre) {
                pre.scrollTop = pre.scrollHeight;
            }
        });
    });
}

function exportLogs(format) {
    const params = new URLSearchParams(window.location.search);
    params.append('format', format);
    
    window.location.href = '/api/logs/export?' + params.toString();
}

function copyLogText(logId) {
    const pre = document.querySelector('#logModal' + logId + ' pre');
    if (pre) {
        navigator.clipboard.writeText(pre.textContent).then(function() {
            showToast('Log copied to clipboard', 'success');
        }).catch(function(err) {
            console.error('Failed to copy:', err);
            showToast('Failed to copy log', 'danger');
        });
    }
}
