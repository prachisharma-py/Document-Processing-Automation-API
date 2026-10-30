# Document Processing Automation API

A backend API built with Django REST Framework that allows authenticated users to upload PDF documents and process them asynchronously using Celery, Redis, and PyMuPDF.

The project demonstrates REST API development, JWT authentication, document validation, background task processing, automated testing, and Docker-based development.

## Features

- **JWT Authentication** — user registration, login, token refresh, and authenticated user endpoints.
- **Document Management** — upload, list, retrieve, and delete PDF documents.
- **Document Validation** — validate PDF uploads and enforce file-size limits.
- **User Data Isolation** — users can access and manage only their own documents.
- **Asynchronous Processing** — process documents in the background using Celery and Redis.
- **PDF Text Extraction** — extract text from PDF files using PyMuPDF.
- **Processing Status Tracking** — track documents through uploaded, pending, processing, completed, and failed states.
- **Task Reliability** — retry failed processing tasks and prevent duplicate processing.
- **Automated Tests** — test authentication, document management, validation, and processing behavior.
- **Docker Support** — run the API, PostgreSQL, Redis, and Celery worker using Docker Compose.
- **Production-oriented Configuration** — Gunicorn, WhiteNoise, environment-based settings, and security checks.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Web framework |
| Django REST Framework | REST API development |
| PostgreSQL | Relational database |
| Redis | Celery message broker and result backend |
| Celery | Background task processing |
| PyMuPDF | PDF text extraction |
| JWT | API authentication |
| pytest | Automated testing |
| Docker Compose | Local service orchestration |
| Gunicorn | WSGI application server |
| WhiteNoise | Static file serving |

## Architecture

```text
Client / API Consumer
       |
       v
Django REST Framework API
       |
       +------ PostgreSQL
       |       Users, documents, status
       |
       +------ Redis
       |       Celery message broker
       |
       v
Celery Worker
       |
       v
PyMuPDF
       |
       v
Extract PDF text and update status
```

The API accepts document uploads and schedules background processing. The Celery worker extracts text from each PDF and updates its processing status in the database.

## API Endpoints

All endpoints use the `/api/v1/` prefix.

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register/` | Register a new user |
| POST | `/api/v1/auth/login/` | Obtain JWT access and refresh tokens |
| POST | `/api/v1/auth/refresh/` | Refresh an access token |
| GET | `/api/v1/auth/me/` | Retrieve the authenticated user's profile |

### Documents

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/documents/` | Upload a PDF document |
| GET | `/api/v1/documents/` | List the authenticated user's documents |
| GET | `/api/v1/documents/<id>/` | Retrieve a document |
| DELETE | `/api/v1/documents/<id>/delete/` | Delete a document and its stored file |

**Authentication:** Document endpoints require a valid JWT access token. Include it in the request header:

```http
Authorization: Bearer <access_token>
```

Users can access and manage only their own documents. PDF uploads are validated before processing, and document text extraction runs asynchronously through Celery.

## Interactive API Documentation

The API documentation is generated using `drf-spectacular` and the OpenAPI specification.

When running the application locally with Docker, the documentation is available at:

| Resource | URL | Purpose |
|---|---|---|
| Swagger UI | `http://localhost:8000/api/doc/` | Explore endpoints and execute API requests |
| OpenAPI Schema | `http://localhost:8000/api/schema/` | View or retrieve the API specification |
| ReDoc | `http://localhost:8000/api/redoc/` | Browse API documentation in ReDoc |

### Using Swagger UI

1. Start the application using Docker Compose.
2. Open the Swagger UI URL in your browser.
3. Expand an endpoint to inspect its request parameters, request body, and responses.
4. Use **Try it out** to execute requests.
5. Register a user or log in to obtain JWT tokens.
6. Click **Authorize** and provide your access token using the format `Bearer <access_token>`.
7. Test authenticated endpoints, including document uploads and document retrieval.

For PDF uploads, select `multipart/form-data` and use the file picker to choose a PDF file.

The API accepts PDF files up to 10 MB. Uploaded documents are processed asynchronously by the Celery worker.

## Document Processing Lifecycle

Documents move through the following statuses:

- `UPLOADED` — the document has been uploaded.
- `PENDING` — processing has been scheduled.
- `PROCESSING` — a worker is processing the document.
- `COMPLETED` — processing finished successfully.
- `FAILED` — processing failed after an error.

PDF text extraction runs asynchronously, allowing the API to respond without waiting for the entire processing task to finish. Failed tasks can be retried, and completed or already-processing documents are protected against duplicate processing.

## Run Locally with Docker

### Prerequisites

- Docker Desktop
- Git

### 1. Clone the repository

```bash
git clone https://github.com/prachisharma-py/document-processing-automation-api.git
cd document-processing-automation-api
```

### 2. Configure environment variables

Create your local `.env` file from the example:

```bash
cp .env.example .env
```

Update the values in `.env`, especially the Django secret key and database password. Keep `.env` private and never commit real secrets.

### 3. Start the services

```bash
docker compose up --build -d
```

Check service status:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs -f web
```

View Celery worker logs:

```bash
docker compose logs -f celery
```

### 4. Run database migrations

```bash
docker compose exec web python manage.py migrate
```

### 5. Create an administrator (optional)

```bash
docker compose exec web python manage.py createsuperuser
```

The API will be available at:

`http://localhost:8000/`

## Run Tests

Run the automated test suite inside the Dockerized application:

```bash
docker compose exec web pytest
```

Run Django's configuration check:

```bash
docker compose exec web python manage.py check
```

## Configuration

The `.env.example` file documents the environment variables required by the application, including:

- Django secret key, debug mode, and allowed hosts.
- PostgreSQL database name, username, password, host, and port.
- Redis connection URL.
- Celery broker and result backend URLs.

Use development settings locally and configure secure secrets, allowed hosts, and HTTPS-related settings before production deployment.

## Project Structure

```text
document_processing_automation_api/
├── apps/
│   ├── users/
│   └── documents/
├── config/
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── manage.py
├── pytest.ini
└── requirements.txt
```

## Current Status

The core API, JWT authentication, PDF document management, asynchronous processing, Docker setup, and automated tests are implemented.

Production deployment and final documentation verification remain planned.

## Production API

**Production deployment is planned.** A public production API URL will be added after deployment and verification.

Once deployed, the production endpoints will follow this structure:

| Resource | Production URL |
|---|---|
| API base URL | `https://your-deployed-domain` |
| Swagger UI | `https://your-deployed-domain/api/doc/` |
| OpenAPI Schema | `https://your-deployed-domain/api/schema/` |
| ReDoc | `https://your-deployed-domain/api/redoc/` |

These are URL templates, not currently live endpoints. Replace `your-deployed-domain` with the actual deployment hostname after deployment.

The production API and documentation URLs will be verified before being published as live links.

## Future Improvements

- Deploy the API and worker to a hosting provider.
- Add CI checks for the complete Dockerized workflow.
- Improve monitoring and production observability.
