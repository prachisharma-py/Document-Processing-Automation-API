# Document Processing Automation API

A backend API built with Django REST Framework that allows authenticated users to upload PDF documents and process them asynchronously using Celery, Redis, and PyMuPDF.

The project demonstrates REST API development, JWT authentication, document validation, background task processing, automated testing, and Docker-based development.

---

🔗 **Live Demo**

🚀 **Live API:** https://document-processing-automation-api.onrender.com/api/doc/

---

## Features

- **JWT Authentication** — user registration, login, token refresh, and authenticated user endpoints.
- **Document Management** — upload, list, retrieve, and delete PDF documents.
- **Document Validation** — validate PDF uploads and enforce file-size limits.
- **User Data Isolation** — users can access and manage only their own documents.
- **Asynchronous Processing** — process documents in the background using Celery and Redis.
- **PDF Text Extraction** — extract text from PDF files using PyMuPDF.
- **Extracted Text Retrieval** — retrieve extracted PDF text through a dedicated endpoint without including large text payloads in regular document responses.
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
       |       Users, document metadata, processing status
       |
       +------ AWS S3
       |       Private PDF document storage
       |
       +------ Redis
       |       Celery message broker and result backend
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

The API stores document metadata in PostgreSQL and PDF files in the configured storage backend. Local development uses Django filesystem storage, while production uses a private AWS S3 bucket.

After an upload, the API schedules asynchronous processing through Celery and Redis. The Celery worker retrieves the PDF, extracts its text using PyMuPDF, and updates the document's processing status and extracted text in PostgreSQL.

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
| GET | `/api/v1/documents/<id>/text/` | Retrieve extracted text after successful processing |
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
- AWS S3 bucket name and region for production document storage.
- AWS credentials supplied securely through the deployment environment or an IAM role.

For local development, leave `AWS_STORAGE_BUCKET_NAME` unset to use filesystem storage. For production, configure the AWS S3 bucket and region, along with appropriate AWS credentials or IAM permissions. Never commit real credentials or secret keys.

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

## **Current Status**

The core API and production deployment are implemented.

- JWT authentication and user-specific document access.
- PDF upload, validation, listing, retrieval, and deletion.
- Private AWS S3 storage for production documents.
- Asynchronous PDF processing using Celery and Redis.
- PDF text extraction using PyMuPDF.
- Document processing status tracking, retries, and duplicate-processing protection.
- Dedicated endpoint for retrieving extracted text.
- Docker-based local development environment.
- Automated test suite.
- Production deployment on Render with PostgreSQL, Redis, Gunicorn, and Supervisor.

The production API supports the complete document-processing workflow, from PDF upload to extracted-text retrieval.

## **Live Production API**

The API is deployed and accessible through Render.

| Resource | URL |
|---|---|
| Swagger UI | https://document-processing-automation-api.onrender.com/api/doc/ |
| OpenAPI Schema | https://document-processing-automation-api.onrender.com/api/schema/ |
| ReDoc | https://document-processing-automation-api.onrender.com/api/redoc/ |

### **Try the Live API**

1. Open the Swagger UI.
2. Register a new user using the registration endpoint.
3. Log in to obtain JWT access and refresh tokens.
4. Click **Authorize** and enter your access token.
5. Test the authenticated document endpoints.

**Note:** The Render free web service may take some time to respond after a period of inactivity. Background processing runs alongside the web application, so queued tasks may be delayed while the service is inactive.

## **Future Improvements**

- Add CI/CD automation for testing and deployment.
- Improve application monitoring and production observability.
- Add document processing metrics and performance monitoring.
- Add support for additional document formats.
- Improve API rate limiting and abuse protection.

## **Contributing**

Contributions, suggestions, and improvements are welcome.

To contribute:

1. Fork the repository.
2. Clone your fork:

   ```bash
   git clone https://github.com/<your-username>/document-processing-automation-api.git
   ```

3. Create a feature branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```

4. Install dependencies and configure your local environment using `.env.example`.
5. Make your changes and add appropriate tests.
6. Run the automated test suite:

   ```bash
   docker compose exec web pytest
   ```

7. Commit and push your changes:

   ```bash
   git add .
   git commit -m "Describe your changes"
   git push origin feature/your-feature-name
   ```

8. Open a Pull Request describing your changes.

Please ensure that tests pass and that no credentials, secret keys, or environment-specific configuration files are committed.
