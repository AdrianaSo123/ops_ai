# Badges

[![Build Status](https://github.com/your-org/opsai/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/opsai/actions)
[![Coverage Status](https://coveralls.io/repos/github/your-org/opsai/badge.svg?branch=main)](https://coveralls.io/github/your-org/opsai?branch=main)

# Architecture Diagram

![OpsAI Architecture](docs/architecture.png)

---

# API Example

```bash
curl -X POST http://localhost:8000/api/orchestrate \
  -H 'Content-Type: application/json' \
  -d '{"input": "Onboard new client Acme Corp"}'
```

# OpenAPI Docs

Once running, access interactive docs at: http://localhost:8000/docs

---

# Error Response Format

All errors return JSON in the format:

```
{
  "error": {
    "type": "ValidationError",
    "message": "Detailed error message"
  }
}
```

---

# Test Coverage

To run tests with coverage:

```bash
pytest --cov=opsai --cov-report=term-missing
```
