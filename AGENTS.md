# AGENTS

## Type Policy

- Keep type definitions strict and explicit.
- Do not remove type annotations to silence errors.
- Do not loosen types to `Any` or broad unions unless there is a clear, documented design reason.
- Fix type errors by improving API/type design first (generic constraints, variance, overloads, helper types).
- Maintain `pyright` clean status after changes.
- When a trade-off is unavoidable, document why and keep the narrowest possible type surface.
