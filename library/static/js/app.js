/**
 * Digital Library & E-Book Circulation Portal
 * Interactive Frontend Utilities (Instant Search, Due Date & Fine Calculations)
 */

document.addEventListener('DOMContentLoaded', () => {
    initInstantSearch();
    initIssueDateCalculator();
    initReturnFineCalculator();
    initStandaloneCalculator();
    initToastDismiss();
    initGlobalShortcuts();
});

/**
 * Instant Client-Side Search & Genre Filter for Book Catalog
 */
function initInstantSearch() {
    const searchInput = document.getElementById('catalogInstantSearch');
    const bookCards = document.querySelectorAll('.book-card-item');
    const noResultsEl = document.getElementById('noResultsMessage');
    const resultCountEl = document.getElementById('resultCount');
    const genrePills = document.querySelectorAll('.genre-filter-pill');
    const availabilityFilter = document.getElementById('availabilityQuickFilter');

    if (!searchInput && !genrePills.length && !availabilityFilter) return;

    let activeGenre = 'all';
    let activeAvailability = 'all';

    function filterBooks() {
        const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
        let visibleCount = 0;

        bookCards.forEach(card => {
            const title = card.getAttribute('data-title') || '';
            const author = card.getAttribute('data-author') || '';
            const isbn = card.getAttribute('data-isbn') || '';
            const genre = card.getAttribute('data-genre') || '';
            const isAvailable = card.getAttribute('data-available') === 'true';

            const matchesQuery = !query || 
                title.includes(query) || 
                author.includes(query) || 
                isbn.includes(query) || 
                genre.toLowerCase().includes(query);

            const matchesGenre = (activeGenre === 'all') || (genre.toLowerCase() === activeGenre.toLowerCase());
            
            let matchesAvailability = true;
            if (activeAvailability === 'available') {
                matchesAvailability = isAvailable;
            } else if (activeAvailability === 'unavailable') {
                matchesAvailability = !isAvailable;
            }

            if (matchesQuery && matchesGenre && matchesAvailability) {
                card.style.display = '';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        if (resultCountEl) {
            resultCountEl.textContent = visibleCount;
        }

        if (noResultsEl) {
            noResultsEl.style.display = (visibleCount === 0) ? 'block' : 'none';
        }
    }

    if (searchInput) {
        searchInput.addEventListener('input', filterBooks);
    }

    genrePills.forEach(pill => {
        pill.addEventListener('click', (e) => {
            // Check if link navigation is desired or client side toggle
            if (pill.getAttribute('data-genre')) {
                e.preventDefault();
                genrePills.forEach(p => p.classList.remove('active'));
                pill.classList.add('active');
                activeGenre = pill.getAttribute('data-genre');
                filterBooks();
            }
        });
    });

    if (availabilityFilter) {
        availabilityFilter.addEventListener('change', (e) => {
            activeAvailability = e.target.value;
            filterBooks();
        });
    }
}

/**
 * Interactive Due Date Calculator during Book Issue Workflow
 */
function initIssueDateCalculator() {
    const issueDateInput = document.getElementById('issueDateInput');
    const dueDateInput = document.getElementById('dueDateInput');
    const calculatedDueText = document.getElementById('calculatedDuePreview');
    const loanDays = 14;

    if (!issueDateInput || !dueDateInput) return;

    function updateDueDate() {
        if (!issueDateInput.value) return;
        const issueDate = new Date(issueDateInput.value + 'T00:00:00');
        if (isNaN(issueDate.getTime())) return;

        const calculatedDue = new Date(issueDate);
        calculatedDue.setDate(calculatedDue.getDate() + loanDays);

        const yyyy = calculatedDue.getFullYear();
        const mm = String(calculatedDue.getMonth() + 1).padStart(2, '0');
        const dd = String(calculatedDue.getDate()).padStart(2, '0');
        const formattedDate = `${yyyy}-${mm}-${dd}`;

        dueDateInput.value = formattedDate;

        if (calculatedDueText) {
            const options = { year: 'numeric', month: 'short', day: 'numeric', weekday: 'short' };
            calculatedDueText.textContent = calculatedDue.toLocaleDateString(undefined, options);
        }
    }

    issueDateInput.addEventListener('change', updateDueDate);
    // Initial run if value is present
    if (issueDateInput.value && !dueDateInput.value) {
        updateDueDate();
    }
}

/**
 * Return Workflow Live Fine Calculator
 */
function initReturnFineCalculator() {
    const returnDateInput = document.getElementById('returnDateInput');
    const dueDateStr = document.getElementById('recordDueDateVal')?.value;
    const fineRateEl = document.getElementById('fineRateVal');
    const daysOverdueDisplay = document.getElementById('calcDaysOverdueDisplay');
    const fineAmountDisplay = document.getElementById('calcFineAmountDisplay');
    const fineStatusBadge = document.getElementById('fineStatusBadge');

    if (!returnDateInput || !dueDateStr) return;

    const rate = fineRateEl ? parseFloat(fineRateEl.value) : 1.0;
    const dueDate = new Date(dueDateStr + 'T00:00:00');

    function calculateReturnFine() {
        if (!returnDateInput.value) return;
        const returnDate = new Date(returnDateInput.value + 'T00:00:00');
        if (isNaN(returnDate.getTime())) return;

        const diffTime = returnDate.getTime() - dueDate.getTime();
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        const overdueDays = Math.max(0, diffDays);
        const totalFine = (overdueDays * rate).toFixed(2);

        if (daysOverdueDisplay) daysOverdueDisplay.textContent = overdueDays;
        if (fineAmountDisplay) fineAmountDisplay.textContent = `$${totalFine}`;

        if (fineStatusBadge) {
            if (overdueDays > 0) {
                fineStatusBadge.className = 'badge bg-danger p-2';
                fineStatusBadge.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-1"></i> Overdue by ${overdueDays} day(s)`;
            } else {
                fineStatusBadge.className = 'badge bg-success p-2';
                fineStatusBadge.innerHTML = `<i class="bi bi-check-circle-fill me-1"></i> Returned On-Time (No Fine)`;
            }
        }
    }

    returnDateInput.addEventListener('change', calculateReturnFine);
    calculateReturnFine();
}

/**
 * Standalone Interactive Due-Date & Fine Calculator Tool
 */
function initStandaloneCalculator() {
    const toolIssueDate = document.getElementById('toolIssueDate');
    const toolLoanDuration = document.getElementById('toolLoanDuration');
    const toolReturnDate = document.getElementById('toolReturnDate');
    const toolDailyRate = document.getElementById('toolDailyRate');

    const resultDueDate = document.getElementById('toolResultDueDate');
    const resultOverdueDays = document.getElementById('toolResultOverdueDays');
    const resultFine = document.getElementById('toolResultFine');
    const resultStatus = document.getElementById('toolResultStatus');

    if (!toolIssueDate || !toolReturnDate) return;

    function runCalculator() {
        if (!toolIssueDate.value) return;

        const issueDate = new Date(toolIssueDate.value + 'T00:00:00');
        const duration = toolLoanDuration ? parseInt(toolLoanDuration.value, 10) || 14 : 14;
        const rate = toolDailyRate ? parseFloat(toolDailyRate.value) || 1.0 : 1.0;

        const calculatedDue = new Date(issueDate);
        calculatedDue.setDate(calculatedDue.getDate() + duration);

        const yyyy = calculatedDue.getFullYear();
        const mm = String(calculatedDue.getMonth() + 1).padStart(2, '0');
        const dd = String(calculatedDue.getDate()).padStart(2, '0');
        const dueDateString = `${yyyy}-${mm}-${dd}`;

        if (resultDueDate) {
            const options = { year: 'numeric', month: 'short', day: 'numeric', weekday: 'short' };
            resultDueDate.textContent = calculatedDue.toLocaleDateString(undefined, options);
        }

        if (toolReturnDate.value) {
            const returnDate = new Date(toolReturnDate.value + 'T00:00:00');
            const diffTime = returnDate.getTime() - calculatedDue.getTime();
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            const overdueDays = Math.max(0, diffDays);
            const fine = (overdueDays * rate).toFixed(2);

            if (resultOverdueDays) resultOverdueDays.textContent = `${overdueDays} day(s)`;
            if (resultFine) resultFine.textContent = `$${fine}`;

            if (resultStatus) {
                if (overdueDays > 0) {
                    resultStatus.innerHTML = `<span class="badge bg-danger fs-6 py-2 px-3"><i class="bi bi-clock-history me-1"></i> Overdue ($${fine} fine)</span>`;
                } else {
                    resultStatus.innerHTML = `<span class="badge bg-success fs-6 py-2 px-3"><i class="bi bi-check-circle me-1"></i> On Time ($0.00 fine)</span>`;
                }
            }
        }
    }

    [toolIssueDate, toolLoanDuration, toolReturnDate, toolDailyRate].forEach(input => {
        if (input) input.addEventListener('input', runCalculator);
    });

    runCalculator();
}

/**
 * Toast Notifications Auto-Dismiss
 */
function initToastDismiss() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            } else {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 500);
            }
        }, 6000);
    });
}

/**
 * Keyboard shortcut: press '/' to focus search input anywhere
 */
function initGlobalShortcuts() {
    document.addEventListener('keydown', (e) => {
        if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
            const searchInput = document.getElementById('catalogInstantSearch');
            if (searchInput) {
                e.preventDefault();
                searchInput.focus();
                searchInput.select();
            }
        }
    });
}
