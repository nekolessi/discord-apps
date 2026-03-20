// @ts-check
import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";
import eslintConfigPrettier from "eslint-config-prettier";

export default [
  { ignores: ["dist/**", "node_modules/**", "**/*.d.ts"] },
  {
    files: ["**/*.{js,cjs,mjs}", "eslint.config.*"],
    ...js.configs.recommended,
    languageOptions: {
      globals: { ...globals.node },
    },
  },
  ...tseslint.configs.recommended,
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
  },
  eslintConfigPrettier,
];
