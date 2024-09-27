# Transx api build with fastapi

How to run 
```bash
cd transx-api
poetry install
poetry run uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

How to run tests
```bash
poetry run pytest tests
```

How to run tests with coverage
```bash
pytest tests --cov=api
```