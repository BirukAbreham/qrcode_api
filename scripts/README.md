# Development Scripts

- `scripts/install` - Install dependencies in a virtual environment.
- `scripts/run_dev` - Runs development environment

> Example for running the scripts

```bash
chmod +x scripts/*
./scripts/install # To install the dependencies
./scripts/run_dev # To run the dev environment
```

## To generate `requirement.txt` from `pyproject.toml`
```bash
poetry export --without-hashes --format=requirements.txt > requirements.txt
```
