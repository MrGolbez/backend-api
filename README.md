# Backend API

This folder contains the Azure Functions backend for the Cloud Resume Challenge. It provides a small HTTP API that updates and returns the website visitor count using Azure Table Storage semantics through Cosmos DB Table API.

## Project Overview

The backend is intentionally simple:

- Azure Functions with Python
- One HTTP-triggered endpoint
- Cosmos DB Table API access through `azure-data-tables`
- Configuration supplied through environment variables

Its current purpose is to support the resume website visitor counter while keeping the backend logic easy to understand and extend.

## API

### `GET /api/GetResumeCounter`

Returns the incremented visitor count as JSON.

Example response:

```json
{
  "count": 42
}
```

Current flow:

1. Receive an HTTP `GET` request
2. Read the current row from the configured table
3. Increment the `Count` value
4. Upsert the updated entity
5. Return the new value as JSON

The function also supports `OPTIONS` requests for CORS preflight handling.

## Configuration

The Function uses these environment variables:

- `STORAGE_CONNECTION_STRING`
- `TABLE_NAME`

For local development, those values are read from `local.settings.json`.

For Azure deployments, they should be set in the Function App application settings.

## Files

- `function_app.py`: Azure Function definition and visitor counter logic
- `requirements.txt`: Python dependencies
- `host.json`: Function host configuration
- `local.settings.json`: Local-only development settings placeholder

## Local Run

Start the Function locally from this folder:

```powershell
cd c:\Users\mcrane\Documents\Cloud_Resume_Challenge\backend-api
func start
```

Test the API:

```powershell
Invoke-RestMethod http://localhost:7071/api/GetResumeCounter
```

## Infrastructure as Code Roadmap

Infrastructure as Code has not been added yet, but this backend is being structured with that next step in mind.

Planned IaC additions include:

- Azure Function App deployment configuration
- Hosting plan definition
- Application settings and environment variable wiring
- Cosmos DB account and Table API table provisioning
- Storage resources required by the Function App
- Deployment automation to make the backend reproducible across environments

The goal is for this backend to evolve from a manually configured project into a repeatable deployment managed through templates and source control.
