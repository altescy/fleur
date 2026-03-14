# Fleur Runtime (TypeScript)

This project contains the browser runtime for Fleur.

## Build

```bash
cd runtime
bun install
bun run build
```

The build output is written to:

- `../src/fleur/assets/fleur.js`

`bun run build` emits a minified bundle. Use `bun run build:dev` for a sourcemap-enabled development build.

## Notes

- Output format is IIFE for direct `<script>` usage.
- Runtime APIs are exposed on `globalThis.__fleur` (`h`, `lazy`, `Cmd`, `Sub`, `Html`, `program`).
