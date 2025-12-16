import { initAll } from '@nationalarchives/frontend/nationalarchives/all';

import SkipLink from './components/skip-link';

import '../sass/main.scss';

function initComponent(ComponentClass) {
    const items = document.querySelectorAll(ComponentClass.selector());
    items.forEach((item) => new ComponentClass(item));
}

document.addEventListener('DOMContentLoaded', () => {
    initComponent(SkipLink);

    // Initialise TNA Frontend components
    initAll();
});
