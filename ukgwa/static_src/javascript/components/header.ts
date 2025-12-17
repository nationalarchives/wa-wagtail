/**
 * Custom Header component that extends TNA Frontend's Header
 * with a configurable mobile breakpoint.
 *
 * Default TNA breakpoint is 48em (768px), but this can be overridden
 * via the `data-mobile-breakpoint` attribute on the header element.
 */

const DEFAULT_BREAKPOINT = '64em'; // 1024px - adjust as needed

export default class Header {
    private $module: HTMLElement;
    private $toggleButton: HTMLButtonElement | null;
    private $navigation: HTMLElement | null;
    private $links: NodeListOf<HTMLElement> | null;
    private menuOpened: boolean;
    private mql: MediaQueryList;

    static selector(): string {
        return '[data-module="tna-header"]';
    }

    constructor($module: HTMLElement) {
        this.$module = $module;
        this.$toggleButton = $module?.querySelector(
            '.tna-header__navigation-button',
        );
        this.$navigation = $module?.querySelector('.tna-header__navigation');
        this.$links =
            this.$navigation?.querySelectorAll('[tabindex="0"]') || null;
        this.menuOpened = false;

        // Get custom breakpoint from data attribute, or use default
        const breakpoint =
            $module?.dataset.mobileBreakpoint || DEFAULT_BREAKPOINT;
        this.mql = window.matchMedia(`(max-width: ${breakpoint})`);

        if (!this.$module || !this.$toggleButton || !this.$navigation) {
            return;
        }

        this.$toggleButton.removeAttribute('hidden');
        this.syncState();
        this.$toggleButton.addEventListener('click', () =>
            this.handleToggleNavigation(),
        );

        if ('addEventListener' in this.mql) {
            this.mql.addEventListener('change', () => this.syncState());
        } else {
            // Legacy fallback for older browsers
            this.mql.addListener(() => this.syncState());
        }

        this.$module.addEventListener('keyup', (e: KeyboardEvent) => {
            if (e.code === 'Escape') {
                if (this.menuOpened && this.mql.matches) {
                    this.menuOpened = false;
                    this.syncState();
                    this.$toggleButton?.focus();
                }
            }
        });
    }

    private handleToggleNavigation(): void {
        this.menuOpened = !this.menuOpened;
        this.syncState();
    }

    private syncState(): void {
        if (this.mql.matches) {
            if (this.menuOpened) {
                this.show();
            } else {
                this.hide();
            }
        } else {
            this.show();
        }
    }

    private show(): void {
        if (!this.$navigation || !this.$toggleButton) return;

        this.$navigation.classList.add('tna-header__navigation--open');
        this.$navigation.removeAttribute('hidden');
        this.$navigation.setAttribute('aria-hidden', 'false');
        this.$toggleButton.setAttribute('aria-expanded', 'true');
        this.$toggleButton.setAttribute('title', 'Close menu');
        this.$toggleButton.classList.add(
            'tna-header__navigation-button--opened',
        );

        if (this.$links) {
            for (let i = 0; i < this.$links.length; i++) {
                this.$links[i].setAttribute('tabindex', '0');
            }
        }
    }

    private hide(): void {
        if (!this.$navigation || !this.$toggleButton) return;

        this.$navigation.classList.remove('tna-header__navigation--open');
        this.$navigation.hidden = true;
        this.$navigation.setAttribute('aria-hidden', 'true');
        this.$toggleButton.setAttribute('aria-expanded', 'false');
        this.$toggleButton.setAttribute('title', 'Open menu');
        this.$toggleButton.classList.remove(
            'tna-header__navigation-button--opened',
        );

        if (this.$links) {
            for (let i = 0; i < this.$links.length; i++) {
                this.$links[i].setAttribute('tabindex', '-1');
            }
        }
    }
}

