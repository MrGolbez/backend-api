# Cloud Resume Backend API

Azure Functions backend for my Azure Cloud Resume Challenge portfolio project.

This repo contains the Python HTTP API that powers the live visitor counter on `https://martycrane.com`.

## What This Demonstrates

- Python Azure Functions
- HTTP-triggered serverless API design
- Cosmos DB Table API integration through `azure-data-tables`
- Environment-based configuration
- CORS handling for browser requests
- Pytest coverage for backend behavior
- GitHub Actions CI/CD for testing and deployment
- Production app settings kept out of source control

## API

### `GET /api/GetResumeCounter`

Returns the incremented visitor count as JSON.

Example response:

```json
{
  "count": 42
}
```

Request flow:

1. Receive an HTTP `GET` request
2. Read the current visitor counter row from Cosmos DB Table API
3. Increment the `Count` value
4. Upsert the updated entity
5. Return the new count as JSON

The function also supports `OPTIONS` requests for CORS preflight handling.

## Configuration

The Function uses these environment variables:

- `STORAGE_CONNECTION_STRING`
- `TABLE_NAME`

For local development, those values are read from `local.settings.json`.

For Azure deployments, they are configured as Function App application settings.

Do not commit real connection strings or local secrets.

## Files

- `function_app.py`: Azure Function definition and visitor counter logic
- `requirements.txt`: Python dependencies
- `host.json`: Function host configuration
- `pytest.ini`: Pytest configuration
- `tests/test_function_app.py`: Backend tests
- `.github/workflows/`: Backend CI/CD workflow

## Local Run

Start the Function locally from this folder:

```powershell
cd C:\Users\mcrane\Documents\Cloud_Resume_Challenge\backend-api
func start
```

Test the API:

```powershell
Invoke-RestMethod http://localhost:7071/api/GetResumeCounter
```

## Tests

Run tests locally:

```powershell
pytest
```

The GitHub Actions workflow runs backend tests automatically before deployment.

## Deployment

The backend deploys to Azure Functions through GitHub Actions.

Production resources:

- Azure Function App: `martycrane-resume-api`
- Cosmos DB Table API account: `martycrane-resume-db`
- Counter table: `Counter`

The frontend calls this API from the static site and displays the returned count on page load.

## Infrastructure As Code

The Azure infrastructure is modeled in the project-level `infra/` folder using Bicep.

The current Bicep modules include:

- Function App Flex Consumption plan
- Linux Python Function App
- Function runtime/deployment storage
- Cosmos DB Table API account
- Counter table
- App settings generated during deployment

The Bicep currently matches the existing manually deployed production resources and has been validated with `az bicep build`. The next IaC step is reviewing detailed Azure `what-if` output before applying the template to production.

## Notes

- The current visitor counter update is intentionally simple and not fully atomic under high concurrency.
- For this portfolio use case, that tradeoff is acceptable and documented.
- A future hardening step could use managed identity and RBAC instead of connection-string based access.
