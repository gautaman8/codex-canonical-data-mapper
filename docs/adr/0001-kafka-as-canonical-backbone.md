# ADR-0001: Kafka as canonical event backbone

- Status: Accepted
- Date: 2026-02-15
- Owners: Middleware Architecture

## Context
The platform requires asynchronous, replayable, independently deployable integration services with strict decoupling from core systems.

## Decision
Kafka is the mandatory internal event backbone for canonical and adapter event flows. Pub/Sub may be used only for edge fan-out or external async notifications.

## Consequences
- Services publish and consume through topics, not direct synchronous coupling to core.
- Topic governance and schema evolution become mandatory.
- Operational ownership includes lag monitoring, DLQ handling, and replay strategy.

## Alternatives Considered
- Pub/Sub-only backbone: rejected due to weaker partition-control and replay requirements for canonical internal streams.
- Direct API chaining: rejected due to coupling, scalability, and resilience risks.
