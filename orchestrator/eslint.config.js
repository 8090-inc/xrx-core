const eslint = require('@eslint/js');
const tseslint = require('typescript-eslint');

const ignores = [
  '**/*.js',
];

module.exports = tseslint.config(
  {
    ...eslint.configs.recommended,
    ignores,
  },
  ...tseslint.configs.recommended.map((config) => ({
    ...config,
    ignores,
  })),
);
