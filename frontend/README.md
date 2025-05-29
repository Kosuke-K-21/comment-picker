# Comment Picker Frontend

A React TypeScript frontend application that communicates with the FastAPI backend.

## Features

- TypeScript + React application
- Webpack bundling
- Docker containerization with Nginx
- CORS-enabled communication with backend
- Responsive design

## Development

### Prerequisites

- Node.js 18+
- npm

### Local Development

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm start
```

The application will be available at `http://localhost:3000`.

### Building for Production

```bash
npm run build
```

## Docker

### Build Docker Image

```bash
docker build -t comment-picker-frontend .
```

### Run Docker Container

```bash
docker run -p 3000:80 comment-picker-frontend
```

## Environment Variables

- `REACT_APP_API_URL`: Backend API URL (defaults to `http://localhost:8000` for development)

## Project Structure

```
frontend/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── App.tsx            # Main React component
│   ├── App.css            # Styles
│   └── index.tsx          # Application entry point
├── Dockerfile             # Docker configuration
├── nginx.conf             # Nginx configuration for production
├── package.json           # Dependencies and scripts
├── tsconfig.json          # TypeScript configuration
└── webpack.config.js      # Webpack bundling configuration
