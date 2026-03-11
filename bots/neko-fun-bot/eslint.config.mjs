// @ts-check
import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";
import eslintConfigPrettier from "eslint-config-prettier";

export default [
  // ignore build artifacts
  { ignores: ["dist/**", "node_modules/**", "**/*.d.ts"] },

  // JS files (including this config)
  {
    files: ["**/*.{js,cjs,mjs}", "eslint.config.*"],
    ...js.configs.recommended,
    languageOptions: {
      globals: { ...globals.node },
    },
  },

  // Base TS rules (non type-aware)
  ...tseslint.configs.recommended,

  // Type-aware TS rules scoped to TS only
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
      // practical defaults for discord.js handlers
      "@typescript-eslint/no-misused-promises": [
        "error",
        { checksVoidReturn: { attributes: false } }
      ],
      "@typescript-eslint/consistent-type-imports": "warn",
      // enable if/when you're ready to tighten payload types
      // "@typescript-eslint/no-unsafe-assignment": "error",
    },
  },

  // turn off stylistic rules that clash with Prettier
  eslintConfigPrettier,
];
