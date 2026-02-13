# iOS App Icon Generator

AI-powered CLI and web API for generating iOS app icons, web favicons, and Instagram posts using image generation models via [Replicate](https://replicate.com/).

Give it a text prompt, pick a style, and get back production-ready assets — all iOS icon sizes (1024 → 20px), favicon bundles (`.ico`, `.png`, webmanifest), or Instagram-optimized images with optional text overlays.

## Features

- **Multiple AI models** — SDXL, Flux Schnell, Flux Dev, Flux Pro
- **iOS icon pipeline** — generates every required App Store size, applies rounded-corner masks, optional background removal via `rembg`
- **Favicon generation** — standalone TypeScript scripts produce `.ico`, apple-touch-icon, android-chrome PNGs, and `site.webmanifest`
- **Instagram posts** — square, portrait, landscape, and story aspect ratios with text overlay and card layout options
- **Web API + React frontend** — FastAPI backend with auth, job queue, and a React UI (optional)
- **Custom prompts** — use preset styles (ios, flat, vector) or pass any prompt you want

## Quick Start

```bash
# 1. Clone & setup
git clone https://github.com/CodyBontecou/ios-app-icons.git
cd ios-app-icons
./setup.sh          # creates venv, installs deps

# 2. Add your Replicate API token
cp .env.example .env
# edit .env → REPLICATE_API_TOKEN=r8_...

# 3. Generate icons
source venv/bin/activate
icon-gen generate --subject "happy cat"
```

Output lands in `output/<subject>-<timestamp>/` with `originals/`, `processed/`, and `metadata.json`.

## CLI Usage

### Generate iOS app icons

```bash
icon-gen generate --subject "mountain logo"
icon-gen generate --subject "coffee cup" --style flat --color blue
icon-gen generate --subject "rocket" --style vector --variations 8
icon-gen generate --subject "my concept" --style custom --custom-style "watercolor botanical illustration, soft edges"
```

### Choose a model

```bash
icon-gen generate --subject "cat" --model flux-dev   # better quality, good text
icon-gen generate --subject "cat" --model flux-pro   # best quality
icon-gen generate --subject "cat" --model sdxl       # default, most flexible
```

### Generate Instagram posts

```bash
icon-gen instagram --subject "product shot" --aspect-ratio portrait \
  --text "NEW DROP" --text-style brutalist --text-color white
```

### Skip processing steps

```bash
icon-gen generate --subject "cat" --no-process      # originals only
icon-gen generate --subject "cat" --no-remove-bg    # keep backgrounds
icon-gen generate --subject "cat" --no-mask         # skip rounded corners
```

### Show config

```bash
icon-gen info
```

## Favicon Scripts (TypeScript)

Standalone scripts that generate full favicon bundles using Replicate + Sharp:

```bash
npm install

# Generic AI favicon from a text prompt
npx tsx favicon-generator.ts "minimalist rocket logo" --style modern

# Project-specific generators
npx tsx generate-smartskin-icon.ts
npx tsx generate-cc-favicon.ts
```

## Web API (Optional)

A FastAPI backend with user auth (OAuth + JWT), a background job queue, and a React frontend.

```bash
# Start Postgres
docker compose up -d

# Run migrations
alembic upgrade head

# Start the API
source venv/bin/activate
uvicorn icon_generator.api.main:app --reload

# Start the frontend
cd frontend && npm install && npm run dev
```

## Output Structure

```
output/<subject>-<timestamp>/
├── originals/           # AI-generated source images
│   ├── variant-1.png
│   └── ...
├── processed/           # Resized + masked icons
│   ├── variant-1/
│   │   ├── AppIcon-1024.png
│   │   ├── AppIcon-180.png
│   │   └── ...
│   └── ...
├── metadata.json        # Prompt, model, parameters
└── prompt.txt           # Raw prompt used
```

## iOS Icon Sizes

| Size | Usage |
|------|-------|
| 1024 | App Store |
| 180 | iPhone @3x |
| 167 | iPad Pro @2x |
| 152 | iPad @2x |
| 120 | iPhone @2x |
| 76 | iPad @1x |
| 60 | Spotlight |
| 40 | Spotlight @2x |
| 29 | Settings |
| 20 | Notification |

## Project Structure

```
src/icon_generator/
├── cli.py            # Click CLI (icon-gen command)
├── config.py         # Model configs, sizes, env loading
├── generator.py      # Replicate API integration
├── processor.py      # Resize, mask, bg removal, text overlay
├── prompts.py        # Prompt templates per style
├── api/              # FastAPI web backend
├── auth/             # OAuth + JWT auth
└── db/               # Async SQLAlchemy + Postgres
frontend/             # React + Vite UI
migrations/           # Alembic DB migrations
favicon-generator.ts  # Standalone TS favicon tool
```

## Requirements

- Python 3.13+
- A [Replicate API token](https://replicate.com/account/api-tokens) (~$0.01–0.05 per generation)
- Node.js 18+ (only for TypeScript favicon scripts or frontend)
- Docker (only for web API's Postgres database)

## License

MIT
