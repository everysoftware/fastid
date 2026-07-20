# ADR 0002: Provide Tiered Standalone Webhook Receiver Examples

- Status: Accepted
- Date: 2026-07-20

## Context

A minimal webhook receiver is useful for first success but omits production concerns. Adding storage abstractions and
database setup to that same file would obscure the authentication flow. Making examples import shared implementation
code would reduce duplication but make each example harder to copy into another service.

## Decision

FastID will provide three standalone FastAPI receiver applications:

- a quick-start authentication example;
- an advanced in-memory Webhook-ID idempotency reference;
- an advanced SQLAlchemy Webhook-ID idempotency reference.

Each application will independently implement Standard Webhooks verification using Python's standard library. Advanced
examples will share the same conceptual claim, complete, and release lifecycle but will not import each other.
The SQLAlchemy example will use SQLAlchemy's async APIs with `aiosqlite` supplied by an optional Poetry `examples`
dependency group.

## Consequences

- New users can reach a working receiver without database setup.
- Experienced users can compare volatile and durable idempotency boundaries.
- Each file can be copied independently.
- Signature-verification code is intentionally duplicated and must be changed consistently if the protocol evolves.
- The in-memory example is not production-durable and must say so prominently.
- The SQLAlchemy example introduces database concepts only in its dedicated file.
