/**
 * Bolbash Beauty Spot - Navigation & Mobile Drawer Manager
 * Pure Vanilla JavaScript implementation with strict Body Scroll Locking & Accessibility (ARIA)
 */

document.addEventListener('DOMContentLoaded', () => {
    const menuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const menuBackdrop = document.getElementById('mobile-menu-backdrop');
    const iconHamburger = document.getElementById('icon-hamburger');
    const iconClose = document.getElementById('icon-close');

    if (!menuButton || !mobileMenu || !menuBackdrop) {
        return;
    }

    let isMenuOpen = false;

    function openMenu() {
        isMenuOpen = true;
        
        // Show backdrop with opacity transition
        menuBackdrop.classList.remove('hidden');
        setTimeout(() => {
            menuBackdrop.classList.remove('opacity-0');
            menuBackdrop.classList.add('opacity-100');
        }, 10);

        // Slide in menu
        mobileMenu.classList.remove('invisible', 'pointer-events-none');
        mobileMenu.classList.remove('translate-x-full');
        mobileMenu.classList.add('translate-x-0');
        mobileMenu.setAttribute('aria-hidden', 'false');

        // Update toggle icons
        if (iconHamburger && iconClose) {
            iconHamburger.classList.add('hidden');
            iconClose.classList.remove('hidden');
        }

        // Update ARIA
        menuButton.setAttribute('aria-expanded', 'true');

        // Strict body and html scroll locking across desktop & mobile touch devices
        document.documentElement.style.overflow = 'hidden';
        document.body.style.overflow = 'hidden';
        document.documentElement.classList.add('overflow-hidden');
        document.body.classList.add('overflow-hidden');
    }

    function closeMenu() {
        isMenuOpen = false;

        // Hide backdrop
        menuBackdrop.classList.remove('opacity-100');
        menuBackdrop.classList.add('opacity-0');
        setTimeout(() => {
            menuBackdrop.classList.add('hidden');
        }, 300);

        // Slide out menu
        mobileMenu.classList.remove('translate-x-0');
        mobileMenu.classList.add('translate-x-full');
        mobileMenu.setAttribute('aria-hidden', 'true');
        setTimeout(() => {
            if (!isMenuOpen) {
                mobileMenu.classList.add('invisible', 'pointer-events-none');
            }
        }, 300);

        // Update toggle icons
        if (iconHamburger && iconClose) {
            iconHamburger.classList.remove('hidden');
            iconClose.classList.add('hidden');
        }

        // Update ARIA
        menuButton.setAttribute('aria-expanded', 'false');

        // Restore body and html scrolling
        document.documentElement.style.overflow = '';
        document.body.style.overflow = '';
        document.documentElement.classList.remove('overflow-hidden');
        document.body.classList.remove('overflow-hidden');
    }

    function toggleMenu() {
        if (isMenuOpen) {
            closeMenu();
        } else {
            openMenu();
        }
    }

    // Event Listeners
    menuButton.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleMenu();
    });

    menuBackdrop.addEventListener('click', () => {
        if (isMenuOpen) {
            closeMenu();
        }
    });

    // Prevent background touch scrolling on mobile backdrop
    menuBackdrop.addEventListener('touchmove', (e) => {
        if (isMenuOpen) {
            e.preventDefault();
        }
    }, { passive: false });

    // Close mobile menu on Escape key press
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isMenuOpen) {
            closeMenu();
        }
    });

    // Close menu when clicking on any navigation link inside mobile drawer
    const mobileLinks = mobileMenu.querySelectorAll('a');
    mobileLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (isMenuOpen) {
                closeMenu();
            }
        });
    });

    // Dynamic Sticky Navbar Scroll Elevation Shadow
    const siteHeader = document.getElementById('site-header');
    if (siteHeader) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 20) {
                siteHeader.classList.add('shadow-md', 'bg-white/98');
                siteHeader.classList.remove('shadow-sm', 'bg-white/95');
            } else {
                siteHeader.classList.remove('shadow-md', 'bg-white/98');
                siteHeader.classList.add('shadow-sm', 'bg-white/95');
            }
        }, { passive: true });
    }
});
