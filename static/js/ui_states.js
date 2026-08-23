/**
 * Bolbash Beauty Spot — Global UI States & Interactivity Controller
 * Provides reusable loading states, button spinners, toast alerts, and form error management.
 */

window.BolbashUI = {
    /**
     * Puts a button into a loading state.
     * Prevents double submission and shows a subtle brand spinner.
     * @param {HTMLElement} button 
     * @param {string} [loadingText] 
     */
    showButtonLoading: function (button, loadingText) {
        if (!button) return;
        if (button.dataset.isLoading === "true") return;

        // Store original content if not already stored
        if (!button.dataset.originalHtml) {
            button.dataset.originalHtml = button.innerHTML;
        }

        button.dataset.isLoading = "true";
        button.disabled = true;
        button.classList.add("opacity-80", "pointer-events-none", "cursor-not-allowed");

        const text = loadingText || button.getAttribute("data-loading-text") || "Processing...";
        
        button.innerHTML = `
            <span class="inline-flex items-center justify-center space-x-2">
                <svg class="animate-spin w-4 h-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>${text}</span>
            </span>
        `;
    },

    /**
     * Restores a button to its original state.
     * @param {HTMLElement} button 
     */
    resetButton: function (button) {
        if (!button) return;
        if (button.dataset.originalHtml) {
            button.innerHTML = button.dataset.originalHtml;
            delete button.dataset.originalHtml;
        }
        button.dataset.isLoading = "false";
        button.disabled = false;
        button.classList.remove("opacity-80", "pointer-events-none", "cursor-not-allowed");
    },

    /**
     * Shows a dynamic toast notification.
     * @param {string} message 
     * @param {'success' | 'error' | 'warning' | 'info'} [type='info'] 
     * @param {number} [duration=4000] 
     */
    showToast: function (message, type = 'info', duration = 4000) {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'fixed bottom-5 right-5 z-50 flex flex-col space-y-3 max-w-sm w-full px-4 pointer-events-none';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = 'pointer-events-auto p-4 rounded-2xl border text-xs sm:text-sm font-medium shadow-xl flex items-center justify-between transition-all duration-300 transform translate-y-4 opacity-0';

        let bgClasses = 'bg-slate-900 border-slate-800 text-white';
        let icon = '✨';

        if (type === 'success') {
            bgClasses = 'bg-emerald-950 border-emerald-800 text-emerald-100';
            icon = '✅';
        } else if (type === 'error') {
            bgClasses = 'bg-rose-950 border-rose-800 text-rose-100';
            icon = '⚠️';
        } else if (type === 'warning') {
            bgClasses = 'bg-amber-950 border-amber-800 text-amber-100';
            icon = '🔔';
        } else if (type === 'info') {
            bgClasses = 'bg-slate-900 border-pink-500/30 text-white';
            icon = 'ℹ️';
        }

        toast.className += ' ' + bgClasses;
        toast.innerHTML = `
            <div class="flex items-center space-x-3">
                <span class="text-base">${icon}</span>
                <span>${message}</span>
            </div>
            <button type="button" onclick="this.parentElement.remove()" class="text-xs uppercase font-bold tracking-wider opacity-70 hover:opacity-100 pl-3">
                ✕
            </button>
        `;

        container.appendChild(toast);

        // Animate in
        requestAnimationFrame(() => {
            toast.classList.remove('translate-y-4', 'opacity-0');
        });

        // Auto dismiss
        setTimeout(() => {
            toast.classList.add('translate-y-4', 'opacity-0');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, duration);
    },

    /**
     * Highlights an input with a field validation error.
     * @param {HTMLElement} inputElement 
     * @param {string} errorMessage 
     */
    showFormError: function (inputElement, errorMessage) {
        if (!inputElement) return;
        inputElement.classList.add('border-rose-500', 'focus:ring-rose-500');

        let errorEl = inputElement.parentElement.querySelector('.js-field-error');
        if (!errorEl) {
            errorEl = document.createElement('p');
            errorEl.className = 'js-field-error mt-1 text-xs font-semibold text-rose-600 flex items-center space-x-1';
            inputElement.parentElement.appendChild(errorEl);
        }
        errorEl.innerHTML = `<span>⚠️</span><span>${errorMessage}</span>`;
    },

    /**
     * Clears all field errors in a form.
     * @param {HTMLFormElement} form 
     */
    clearFormErrors: function (form) {
        if (!form) return;
        form.querySelectorAll('.border-rose-500').forEach(el => {
            el.classList.remove('border-rose-500', 'focus:ring-rose-500');
        });
        form.querySelectorAll('.js-field-error').forEach(el => el.remove());
    }
};

// Auto-bind form loading states on submit
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function (e) {
            // Find submit button inside form
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn && !submitBtn.hasAttribute('data-no-auto-loading')) {
                const customText = form.getAttribute('data-loading-text') || submitBtn.getAttribute('data-loading-text');
                window.BolbashUI.showButtonLoading(submitBtn, customText);
            }
        });
    });
});
