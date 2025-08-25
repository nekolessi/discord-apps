module.exports = {
root: true,
env: { es2022: true, node: true },
extends: [
'eslint:recommended',
'plugin:import/recommended',
'prettier'
],
parserOptions: { ecmaVersion: 'latest', sourceType: 'module' },
rules: {
'import/order': [
'warn',
{
'newlines-between': 'always',
alphabetize: { order: 'asc', caseInsensitive: true }
}
]
}
}