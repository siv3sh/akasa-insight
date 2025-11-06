# Akasa Air – Data Engineering Console

Production-grade web frontend for data operations, analytics, and monitoring.

## Overview

A comprehensive data engineering console providing real-time insights into four authoritative KPIs:
1. **Repeat Customers** (>1 order)
2. **Monthly Order Trends**
3. **Regional Revenue**
4. **Top Customers by Spend** (last 30 days)

Plus operational features: ingestion monitoring, data quality reports, and settings.

## Tech Stack

- **Frontend**: React 18 + TypeScript + Vite
- **UI**: Tailwind CSS + shadcn/ui components
- **Routing**: React Router v6
- **Data**: TanStack Query (React Query) for fetching + caching
- **Charts**: Recharts
- **Validation**: Zod
- **Testing**: Vitest + Testing Library (Playwright scaffold included)

## Features

### Core Analytics
- **Dashboard** (`/`): KPI cards, charts (monthly orders, regional revenue), top spenders table
- **Customers** (`/customers`): Searchable table with pagination, repeat customer badges
- **Orders Trends** (`/orders-trends`): Time-series line chart (daily/weekly/monthly)
- **Regional Revenue** (`/regional-revenue`): Bar chart + drill-down table
- **Top Spenders** (`/top-spenders`): Ranked table with adjustable time window

### Operations
- **Data Quality** (`/data-quality`): Validation expectations, duplicates, null anomalies
- **Ingestion Runs** (`/ingestion-runs`): Pipeline execution history with status, duration, logs
- **Settings** (`/settings`): Theme toggle, cache management, environment info (no secrets exposed)

### Global Features
- **Responsive Design**: Mobile-first layout with collapsible sidebar
- **Light/Dark Theme**: Automatic theme switching via `next-themes`
- **Error Boundaries**: Graceful error handling with retry
- **Loading States**: Skeleton loaders and empty states
- **URL Sync**: Filters synced with search params
- **Accessibility**: WAI-ARIA compliant, keyboard navigation, focus management

## Project Structure

```
src/
├── api/
│   ├── types.ts          # TypeScript interfaces for all API responses
│   ├── mocks.ts          # Mock data generators
│   └── client.ts         # API client with mock/real adapter
├── components/
│   ├── layout/
│   │   ├── AppLayout.tsx
│   │   └── AppSidebar.tsx
│   ├── shared/
│   │   ├── KpiCard.tsx
│   │   ├── StatusBadge.tsx
│   │   ├── ErrorBoundary.tsx
│   │   └── EmptyState.tsx
│   └── ui/               # shadcn/ui components
├── features/
│   ├── dashboard/
│   ├── customers/
│   ├── orders-trends/
│   ├── regional-revenue/
│   ├── top-spenders/
│   ├── data-quality/
│   ├── ingestion/
│   └── settings/
├── lib/
│   ├── utils.ts
│   └── format.ts         # Currency, date, number formatters
└── App.tsx
```

## Setup

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
# Clone the repository
git clone <YOUR_GIT_URL>
cd akasa-air-console

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:8080`.

## Environment Variables

Create a `.env` file in the root:

```env
# API Mode
VITE_USE_MOCKS=true          # Use mock data (set to "false" for real API)

# Real API (when VITE_USE_MOCKS=false)
VITE_API_BASE_URL=https://api.akasaair.com
```

**Security Note**: Never commit real credentials or API keys to version control.

## Development

### Running Tests

```bash
# Unit tests
npm run test

# E2E tests (Playwright)
npm run test:e2e
```

### Building for Production

```bash
npm run build

# Preview production build
npm run preview
```

### Code Quality

```bash
# Lint
npm run lint

# Format
npm run format
```

## Architecture Highlights

### API Layer
- **Mock/Real Adapter**: Toggle between mock data (default) and real API without changing UI code
- **Fully Typed**: All API responses use Zod-validated TypeScript interfaces
- **Abort Support**: Query cancellation via AbortController

### State Management
- **TanStack Query**: Automatic caching, background refetch, optimistic updates
- **Query Keys**: Organized per route for efficient invalidation

### Performance
- **Code Splitting**: Routes lazy-loaded
- **Memoization**: Expensive selectors memoized
- **Skeleton Loaders**: Instant visual feedback during data fetch

### Accessibility
- Semantic HTML (`<header>`, `<main>`, `<nav>`)
- ARIA labels and roles
- Keyboard navigation (Tab, Enter, Escape)
- Focus management
- Skip-to-content links

## Security

- **No Secrets Exposed**: Credentials, connection strings, and API keys are never logged or displayed in the UI
- **Client-Side Validation**: Zod schemas validate all user inputs
- **HTTPS Only**: Production builds enforce secure connections

## KPI Definitions

1. **Repeat Customers**: Count of customers with `total_orders > 1`
2. **Monthly Order Trends**: Time-series of order counts by month (Jan–Nov 2024)
3. **Regional Revenue**: Sum of revenue grouped by region (North, South, East, West, Central)
4. **Top Customers by Spend**: Ranked by `lifetime_spend` in the last 30 days

## Deployment

### Build

```bash
npm run build
```

Output: `dist/` directory ready for static hosting.

### Deploy Options

- **Lovable**: Click "Publish" in the Lovable dashboard
- **Vercel/Netlify**: Connect GitHub repo for auto-deploys
- **Custom**: Serve `dist/` via Nginx, Apache, or CDN

### Environment Variables in Production

Set `VITE_USE_MOCKS=false` and provide `VITE_API_BASE_URL` in your hosting platform's environment settings.

## Acceptance Criteria

✅ All four KPIs rendered and filterable by date/region  
✅ No secrets displayed; credentials never logged  
✅ Dashboard achieves ≥90 Lighthouse performance and accessibility (mock data)  
✅ Error boundaries catch failures; user can retry without reload  
✅ Responsive design (mobile, tablet, desktop)  
✅ Background refetch with visual indicators  
✅ Time-zone awareness with UTC toggle  

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Proprietary - Akasa Air

## Support

For questions or issues, contact the Data Engineering team.

---

**Built with ❤️ for Akasa Air**
