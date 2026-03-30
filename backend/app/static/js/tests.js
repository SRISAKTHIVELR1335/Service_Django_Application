document.addEventListener('DOMContentLoaded', function() {
    initTestFilters();
});

function initTestFilters() {
    const vehicleSelect = document.getElementById('vehicleSelect');
    const typeSelect = document.getElementById('typeSelect');
    const searchInput = document.getElementById('testSearch');
    
    if (vehicleSelect) {
        vehicleSelect.addEventListener('change', filterTests);
    }
    
    if (typeSelect) {
        typeSelect.addEventListener('change', filterTests);
    }
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterTests, 300));
    }
}

function filterTests() {
    const vehicleId = document.getElementById('vehicleSelect')?.value || '';
    const testType = document.getElementById('typeSelect')?.value || '';
    const search = document.getElementById('testSearch')?.value || '';
    
    const params = new URLSearchParams();
    if (vehicleId) params.append('vehicle_id', vehicleId);
    if (testType) params.append('type', testType);
    if (search) params.append('search', search);
    
    window.location.href = '/tests?' + params.toString();
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction() {
        const context = this;
        const args = arguments;
        const later = function() {
            timeout = null;
            func.apply(context, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
