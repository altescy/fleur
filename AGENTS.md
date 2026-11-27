# AGENTS

This guide is for coding agents working in this repository.
Follow it as the default development contract.

## Repository Overview

- `src/fleur/`: Python DSL/compiler/runtime bridge.
- `runtime/`: TypeScript browser runtime (built with Bun).
- `tests/unit/`: Python unit tests, mirrored by domain (`core/`, `builtins/`, `js/`).
- `tests/integration/`: end-to-end style Python tests across multiple layers.

## Rule Sources

- Checked for Cursor rules: none found (`.cursor/rules/`, `.cursorrules`).
- Checked for Copilot rules: none found (`.github/copilot-instructions.md`).
- Therefore this file and existing repo conventions are the authoritative agent rules.

## Build, Lint, and Test Commands

### Preferred aggregate commands (repo root)

- `make format` — sort imports and format Python (`ruff`).
- `make lint` — run `ruff check` + `pyright`.
- `make test` — run Python tests and TypeScript runtime tests.
- `make build` — build runtime bundle into `src/fleur/assets/fleur.js`.

### Python commands

- Full test run: `PYTHONPATH=$(pwd) uv run pytest`
- Single file: `PYTHONPATH=$(pwd) uv run pytest tests/unit/core/test_msg.py`
- Single test: `PYTHONPATH=$(pwd) uv run pytest tests/unit/core/test_msg.py::test_grouped_msg_compiles_to_message_builder_function`
- Type check: `PYTHONPATH=$(pwd) uv run pyright`
- Public API type completeness: `PYTHONPATH=$(pwd) uv run pyright --verifytypes fleur --ignoreexternal` (keep at 100%)
- Lint: `PYTHONPATH=$(pwd) uv run ruff check`
- Format: `PYTHONPATH=$(pwd) uv run ruff format`
- Import sort fix only: `PYTHONPATH=$(pwd) uv run ruff check --select I --fix`

### TypeScript runtime commands

- Type check runtime: `bun run --cwd runtime check`
- Test runtime: `bun run --cwd runtime test`
- Single runtime test file: `bun test runtime/test/diff.test.ts`
- Filter runtime test by name: `bun test runtime/test/diff.test.ts -t "creates TEXT patch"`
- Build runtime (minified): `bun run --cwd runtime build`
- Build runtime (dev/sourcemap): `bun run --cwd runtime build:dev`

### Agent workflow expectation

- After meaningful changes, run at least:
  - `uv run pyright`
  - `uv run ruff check src tests work/demo.py`
  - `uv run pytest -q`
- If `runtime/src` changed, also run:
  - `bun run --cwd runtime check`
  - `bun run --cwd runtime test`

## Code Style and Conventions

### Python formatting and structure

- Python version target is 3.11+ (`pyproject.toml`, pyright).
- Line length: 120.
- Use `ruff` as formatter/linter authority; do not hand-format against it.
- Prefer explicit imports; avoid star imports.
- Keep imports grouped: stdlib, third-party, local.
- Keep functions small and composable; extract helpers rather than deep nesting.

### Type policy (strict)

- Keep type definitions strict and explicit.
- Do not remove type annotations to silence errors.
- Do not loosen types to `Any` or broad unions unless there is a clear, documented design reason.
- Fix type errors by improving API/type design first (generic constraints, variance, overloads, helper types).
- Maintain `pyright` clean status after changes.
- When a trade-off is unavoidable, document why and keep the narrowest possible type surface.

### Typing conventions

- Prefer `TypeVar`-based generic modeling over `Any`.
- Use `Protocol` for behavior contracts when needed.
- Keep DSL-facing types separate from implementation-only helper types.
- Keep internal/private helpers private (leading underscore) if not part of DSL API.
- Avoid leaking implementation protocols into public API signatures unless intentional.

### Naming conventions

- Python modules/functions/variables: `snake_case`.
- Python classes: `PascalCase`.
- Constants: `UPPER_SNAKE_CASE`.
- Prefix non-public helpers with `_`.
- Use names that reflect layer responsibility (`core` concept vs `js` combinator vs `builtins` API).

### Error handling

- Fail fast on impossible states (`raise ValueError`/`TypeError` with clear messages).
- Preserve type safety when handling errors; avoid catch-all broad suppression.
- In runtime TS, prefer explicit guards and safe fallbacks for DOM node lookups.

### Testing conventions

- Keep unit tests close to source structure:
  - `src/fleur/core/*` -> `tests/unit/core/*`
  - `src/fleur/builtins/*` -> `tests/unit/builtins/*`
  - `src/fleur/js/*` -> `tests/unit/js/*`
- Put cross-layer behavior tests in `tests/integration/*`.
- For runtime TS, add `bun:test` files under `runtime/test/`.
- Prefer focused assertions on generated output (compile/emit), not brittle full snapshots.

## Architecture Guidance

### Layer boundaries

- `core`: framework concepts and DSL contracts (`Model`, `Msg`, `Update`, `Cmd`, `TaskLike`).
- `builtins`: higher-level user-facing capabilities (e.g., `Http`).
- `js`: ESTree-level representation/building/combinators.

### Dependency direction

- Allowed: `core -> js` (compile to JS AST), `builtins -> core/js`.
- Avoid: `js -> core` unless there is a compelling, reviewed reason.
- Keep public DSL APIs independent from low-level implementation details.

### Runtime TS organization

- Keep runtime split by concern:
  - `types.ts` shared runtime types
  - `vdom.ts` vnode constructors and wrapping
  - `dom.ts` DOM instantiation and prop operations
  - `diff.ts` patch planning
  - `patch.ts` patch application
  - `effects.ts` Cmd/Sub/Html helpers
  - `program.ts` app loop and subscription lifecycle

## Change Management for Agents

- Do not make unrelated refactors while fixing a focused issue.
- Do not silently rename public API identifiers without updating docs/tests.
- When moving files/modules, update imports and tests in the same change.
- If behavior changes, add or update tests to describe the new behavior.
- Prefer incremental, reviewable commits worth of changes even when not committing.

## Quick Pre-PR Checklist

- `make format`
- `make lint`
- `make test`
- If runtime changed, verify bundle build: `make build-runtime-dev`
- Confirm no accidental public API leakage from internal modules.
