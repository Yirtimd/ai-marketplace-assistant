# Desktop App (Stage 10)

Electron + React desktop client for AI Marketplace Assistant.

## Requirements

- Node.js 18+
- Running backend API (`http://localhost:8000/api/v1`)

## Install

```bash
cd desktop-app
npm install
```

## Development

```bash
npm run dev
```

This starts:

- Vite renderer on `http://localhost:5173`
- Electron main process

## Build renderer

```bash
npm run build:web
```

## Available sections

- Dashboard
- Products
- Reviews
- Content AI
- Inventory
- Settings

## API base URL

Default value:

`http://localhost:8000/api/v1`

You can change it from **Settings** screen in the desktop app.
