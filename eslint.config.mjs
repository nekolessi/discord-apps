// @ts-check
import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";
import eslintConfigPrettier from "eslint-config-prettier";


export default [
// Ignore build artifacts
{ ignores: ["dist/**", "node_modules/**", "**/*.d.ts"] },


// Base JS rules for JS files only (includes the config file itself)
{
files: ["**/*.{js,cjs,mjs}", "eslint.config.*"],
...js.configs.recommended,
languageOptions: {
globals: { ...globals.node },
},
},


// Base TS rules (non type-aware)
...tseslint.configs.recommended,


// Type-aware TS rules *scoped to TS only*
{
files: ["**/*.{ts,tsx}"],
languageOptions: {
parserOptions: {
project: "./tsconfig.json",
tsconfigRootDir: import.meta.dirname,
sourceType: "module",
},
globals: { ...globals.node },
},
rules: {
// Practical discord.js defaults
"@typescript-eslint/no-misused-promises": [
"error",
{ checksVoidReturn: { attributes: false } }
],
"@typescript-eslint/consistent-type-imports": "warn",
// Relax this if your handlers use `any` from discord.js payloads
"@typescript-eslint/no-unsafe-assignment": "off",
},
},


// Disable stylistic clashes with Prettier
eslintConfigPrettier,
];