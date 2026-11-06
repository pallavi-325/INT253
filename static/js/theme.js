/**
 * CareNest Pediatric Teledermatology - Theme Switcher
 * Manages Tailwind dark mode toggle and syncs with localStorage & OS preference.
 */

document.addEventListener('DOMContentLoaded', () => {
    const themeToggleDarkIcon = document.getElementById('theme-toggle-dark-icon');
    const themeToggleLightIcon = document.getElementById('theme-toggle-light-icon');
    const themeToggleBtn = document.getElementById('theme-toggle');

    if (!themeToggleBtn) return;

    // Synchronize initial icon state
    function updateIcon() {
        if (document.documentElement.classList.contains('dark')) {
            themeToggleLightIcon.classList.remove('hidden');
            themeToggleDarkIcon.classList.add('hidden');
        } else {
            themeToggleLightIcon.classList.add('hidden');
            themeToggleDarkIcon.classList.remove('hidden');
        }
    }

    updateIcon();

    themeToggleBtn.addEventListener('click', () => {
        // Toggle theme
        if (document.documentElement.classList.contains('dark')) {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('color-theme', 'light');
        } else {
            document.documentElement.classList.add('dark');
            localStorage.setItem('color-theme', 'dark');
        }
        updateIcon();

        // Dispatch custom theme change event for charts and interactive widgets
        window.dispatchEvent(new CustomEvent('themeChanged', {
            detail: {
                isDark: document.documentElement.classList.contains('dark')
            }
        }));
    });
});

