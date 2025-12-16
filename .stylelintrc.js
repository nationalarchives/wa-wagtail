const config = require('stylelint-config-torchbox');
module.exports = {
    // See https://github.com/torchbox/stylelint-config-torchbox for rules.
    extends: 'stylelint-config-torchbox',
    // remove when https://github.com/torchbox/stylelint-config-torchbox/pull/40 is merged.
    rules: {
        'scss/at-rule-no-unknown': [
            true,
            {
                ignoreAtRules: [
                    ...config.rules['scss/at-rule-no-unknown'][1].ignoreAtRules,
                    'layer',
                    'config',
                    'theme',
                    'custom-variant',
                    'plugin',
                    'source',
                    'variant',
                    'utility',
                    'reference',
                    'tailwind',
                ],
            },
        ],
    },
};
