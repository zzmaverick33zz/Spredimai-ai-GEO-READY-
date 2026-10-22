import { defineConfig } from 'vite';
// `vite build --mode single` makes one self-contained chunk (used by scripts/make_single_html.py)
export default defineConfig(({ mode }) => ({
  build: { target: 'es2020', ...(mode === 'single' ? { outDir: 'dist-single', emptyOutDir: true, rollupOptions: { output: { inlineDynamicImports: true } } } : {}) }
}));
