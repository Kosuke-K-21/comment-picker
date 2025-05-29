# Comment Picker

A full-stack application with a FastAPI backend and React TypeScript frontend, both containerized with Docker.

## Architecture

- **Backend**: FastAPI (Python) - `/backend`
- **Frontend**: React + TypeScript - `/frontend`
- **Containerization**: Docker + Docker Compose

## Quick Start

### Prerequisites

- Docker
- Docker Compose

### Running the Application

1. Clone the repository and navigate to the project root
2. Build and start both services:

```bash
docker-compose up --build
```

This will:
- Build the FastAPI backend and expose it on `http://localhost:8000`
- Build the React frontend and expose it on `http://localhost:3000`
- Set up networking between the services

### Accessing the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Backend API Documentation**: http://localhost:8000/docs

## Development

### Backend Development

Navigate to the `backend` directory:

```bash
cd backend
```

See `backend/README.md` for detailed backend development instructions.

### Frontend Development

Navigate to the `frontend` directory:

```bash
cd frontend
```

See `frontend/README.md` for detailed frontend development instructions.

## Project Structure

```
comment-picker/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   └── main.py         # FastAPI application
│   ├── Dockerfile          # Backend Docker configuration
│   └── pyproject.toml      # Python dependencies
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── App.tsx         # Main React component
│   │   └── index.tsx       # Application entry point
│   ├── public/
│   │   └── index.html      # HTML template
│   ├── Dockerfile          # Frontend Docker configuration
│   └── package.json        # Node.js dependencies
├── docker-compose.yml      # Multi-service orchestration
└── README.md              # This file
```

## Features

- **Backend**:
  - FastAPI with automatic API documentation
  - CORS enabled for frontend communication
  - Docker containerization

- **Frontend**:
  - React with TypeScript
  - Webpack bundling
  - Nginx serving in production
  - Environment-based API URL configuration
  - Docker containerization

## Stopping the Application

```bash
docker-compose down
```

## Rebuilding After Changes

```bash
docker-compose up --build
```

## Troubleshooting

### Port Conflicts

If ports 3000 or 8000 are already in use, you can modify the port mappings in `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8001:80"  # Change 8000 to 8001
  frontend:
    ports:
      - "3001:80"  # Change 3000 to 3001
```

### Network Issues

If the frontend cannot connect to the backend, ensure both services are running and check the Docker network configuration.
