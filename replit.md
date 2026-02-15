# Itinero - Personalized Travel Planner

## Overview

Itinero is an AI-powered travel planning application that generates personalized itineraries based on user preferences including destination, dates, number of travelers, and budget. The app features a landing page with a trip planning form and a dashboard that displays generated itineraries with day-by-day plans, hotel recommendations, transport options, and budget breakdowns.

Currently the app uses mock data to simulate AI-generated itineraries. The backend is minimal with placeholder routes, and the storage layer uses in-memory storage rather than the database.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend
- **Framework**: React 18 with TypeScript, bundled by Vite
- **Routing**: Wouter (lightweight client-side router) with two main routes: `/` (home/landing) and `/plan` (dashboard)
- **State Management**: TanStack React Query for server state; local React state for UI
- **UI Components**: shadcn/ui component library (new-york style) built on Radix UI primitives
- **Styling**: Tailwind CSS v4 with CSS variables for theming, using a "Clean Travel Theme" with teal & sand color palette
- **Fonts**: Inter (sans-serif) and Playfair Display (serif) loaded from Google Fonts
- **Animations**: Framer Motion for page transitions and loading states
- **Path aliases**: `@/` maps to `client/src/`, `@shared/` maps to `shared/`

### Backend
- **Runtime**: Node.js with Express 5
- **Language**: TypeScript, executed via tsx in development
- **API Pattern**: All API routes should be prefixed with `/api`
- **Dev Server**: Vite dev server runs as middleware in Express during development with HMR support
- **Production**: Client is built to `dist/public`, server is bundled with esbuild to `dist/index.cjs`
- **Build Script**: Custom `script/build.ts` handles both Vite client build and esbuild server bundling

### Data Layer
- **ORM**: Drizzle ORM configured for PostgreSQL
- **Schema Location**: `shared/schema.ts` — shared between client and server
- **Current Schema**: Single `users` table with `id` (UUID), `username`, and `password`
- **Validation**: Zod schemas generated from Drizzle schemas via `drizzle-zod`
- **Storage Interface**: `IStorage` interface in `server/storage.ts` abstracts data access. Currently uses `MemStorage` (in-memory Map). Should be swapped to a database-backed implementation when connecting to PostgreSQL.
- **Database Migrations**: Drizzle Kit configured with `drizzle-kit push` command, migrations output to `./migrations`
- **Database URL**: Requires `DATABASE_URL` environment variable for PostgreSQL connection

### Key Design Decisions
1. **Shared schema between client and server** — Types defined once in `shared/schema.ts` are used on both sides, ensuring type safety across the stack
2. **Storage abstraction** — The `IStorage` interface allows swapping between in-memory and database-backed storage without changing route handlers
3. **Mock data pattern** — `client/src/lib/mockData.ts` defines data interfaces and mock generators, indicating the app is designed to eventually replace these with real API calls
4. **Single HTTP server** — Express and Vite share the same HTTP server instance, enabling WebSocket HMR without port conflicts

## External Dependencies

### Database
- **PostgreSQL** — Required via `DATABASE_URL` environment variable. Drizzle ORM handles schema management and queries. Session storage uses `connect-pg-simple`.

### Key NPM Packages
- **express** v5 — HTTP server
- **drizzle-orm** / **drizzle-kit** — Database ORM and migration tooling
- **@tanstack/react-query** — Client-side data fetching and caching
- **framer-motion** — Animation library used on the frontend
- **react-day-picker** — Calendar date picker component
- **date-fns** — Date utility library
- **zod** — Runtime schema validation
- **wouter** — Lightweight React router
- **recharts** — Charting library (chart UI components present)
- **embla-carousel-react** — Carousel component
- **vaul** — Drawer component

### Replit-specific
- **@replit/vite-plugin-runtime-error-modal** — Shows runtime errors in dev
- **@replit/vite-plugin-cartographer** — Dev tooling (dev only)
- **@replit/vite-plugin-dev-banner** — Dev banner (dev only)
- **vite-plugin-meta-images** — Custom plugin for OpenGraph meta tag generation using Replit deployment URLs