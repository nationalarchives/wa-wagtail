import { initAll } from '@nationalarchives/frontend/nationalarchives/all';

import Header from './components/header';
import SkipLink from './components/skip-link';

import '../sass/main.scss';

function initComponent(ComponentClass) {
    const items = document.querySelectorAll(ComponentClass.selector());
    items.forEach((item) => new ComponentClass(item));
}

document.addEventListener('DOMContentLoaded', () => {
    initComponent(SkipLink);

    // Initialise custom header with extended mobile breakpoint
    // Must be initialised before initAll() to prevent TNA's default header from taking over
    initComponent(Header);

    // Initialise TNA Frontend components
    initAll();
});
