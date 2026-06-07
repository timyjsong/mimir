# Ticket 0-1 — greet(): tiny greeting module + tests

## Story

A tiny utility module so the project has something real to build, test, and lint.

## Acceptance Criteria

- AC1.1: `src/greet.js` exports a function `greet(name)` (ESM named export) returning the string `Hello, <name>!`.
- AC1.2: `greet()` with no argument returns `Hello, world!`.
- AC1.3: `greet` trims surrounding whitespace from `name` — `greet("  Ada ")` returns `Hello, Ada!`.
- AC1.4: `test/greet.test.js` covers AC1.1–AC1.3 using `node:test` + `node:assert/strict`, and `npm test` passes.
- AC1.5: `npm run lint` passes.

## Dev Notes

- ESM project (`"type": "module"` is already set in package.json).
- Node built-ins only; no dependencies.
- Read `docs/api-notes.md` for naming/format conventions before implementing.

## What this story IS NOT

- Do NOT create or touch `src/slug.js` or its tests — ticket 0-2 owns them.
