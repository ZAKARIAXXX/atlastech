# ADR-002: Next.js 15 as Frontend Framework

## Status

Accepted

## Context

AtlasTech needs a production-grade web dashboard for IT technicians to view fleet health, manage incidents, launch diagnostics, and eventually interact with AI-assisted triage. The frontend must support real-time updates (WebSocket/SSE), complex data visualization, and role-based access.

## Decision

We chose **Next.js 15** with the App Router, TypeScript, Tailwind CSS v4, and shadcn/ui.

- App Router for server components and streaming
- TypeScript for full-stack type alignment
- Tailwind CSS v4 for utility-first styling
- shadcn/ui for accessible, customizable component primitives
- Recharts for telemetry visualization

## Alternatives Considered

| Framework | Pros | Cons |
|-----------|------|------|
| **Remix** | Excellent loaders/actions | Smaller ecosystem, less community momentum |
| **SvelteKit** | Lightweight, fast | Smaller talent pool, fewer enterprise integrations |
| **Vue/Nuxt** | Great DX | Team preference leans toward React |

## Consequences

- The web app runs as a standalone Next.js build inside a Docker container.
- API communication is handled via server-side fetch in API routes or direct client-side fetch to the FastAPI backend.
- The monorepo contains both Python and TypeScript projects, requiring separate CI jobs.
