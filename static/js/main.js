/**
 * Bolbash Beauty Spot - Global JavaScript
 * Vanilla JavaScript framework foundation & UI enhancements
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log('Bolbash Beauty Spot platform initialized.');
    initScrollReveal();
});

/**
 * Initialize IntersectionObserver to handle smooth section scroll transitions
 */
function initScrollReveal() {
    const selector = '.reveal-on-scroll, .reveal-fade-up, .reveal-fade-in, .reveal-slide-left, .reveal-slide-right, .reveal-scale, section:not([data-no-reveal])';
    const targetElements = document.querySelectorAll(selector);

    if (!targetElements.length) return;

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        targetElements.forEach(el => el.classList.add('is-revealed'));
        return;
    }

    const observerOptions = {
        root: null,
        rootMargin: '0px 0px -40px 0px',
        threshold: 0.08
    };

    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-revealed');
                obs.unobserve(entry.target);
            }
        });
    }, observerOptions);

    targetElements.forEach(el => {
        if (!el.classList.contains('reveal-fade-up') &&
            !el.classList.contains('reveal-fade-in') &&
            !el.classList.contains('reveal-slide-left') &&
            !el.classList.contains('reveal-slide-right') &&
            !el.classList.contains('reveal-scale') &&
            !el.classList.contains('reveal-on-scroll')) {
            el.classList.add('reveal-fade-up');
        }
        observer.observe(el);
    });
}