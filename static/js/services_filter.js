/**
 * Bolbash Beauty Spot — Services Category Filter Controller
 * Vanilla JS client-side filtering for service category cards.
 */

document.addEventListener('DOMContentLoaded', () => {
    const filterButtons = document.querySelectorAll('[data-filter]');
    const serviceCards = document.querySelectorAll('[data-category-slug]');

    if (!filterButtons.length || !serviceCards.length) return;

    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            const filterValue = button.getAttribute('data-filter');

            // Update active state on buttons
            filterButtons.forEach(btn => {
                btn.classList.remove('bg-brand-pink', 'text-white', 'shadow-md');
                btn.classList.add('bg-white', 'text-brand-neutral-700', 'hover:bg-brand-neutral-100');
                btn.setAttribute('aria-selected', 'false');
            });

            button.classList.remove('bg-white', 'text-brand-neutral-700', 'hover:bg-brand-neutral-100');
            button.classList.add('bg-brand-pink', 'text-white', 'shadow-md');
            button.setAttribute('aria-selected', 'true');

            // Filter service cards
            serviceCards.forEach(card => {
                const cardCategory = card.getAttribute('data-category-slug');
                if (filterValue === 'all' || cardCategory === filterValue) {
                    card.style.display = 'flex';
                    card.classList.add('animate-fadeIn');
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
});
