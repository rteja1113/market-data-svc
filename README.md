# Market-Data-Service
# TODO
- [X] Add pre-commit hooks
- [X] Descriptive README
- [X] Add tests
- [X] Add CI/CD
- [X] Add Dockerfile
- [X] Build DB and ORM
- [X] Add API


## Description
This is a FastAPI application that provides an API for Indian Energy Exchange Data. It scrapes the IEX website for prices and exposes them via APIs.


## Pre-commit Hooks
This project uses pre-commit hooks to ensure code quality and consistency. The hooks include:
- `trailing-whitespace` and `end-of-file-fixer` for removing unnecessary whitespace.
- `check-json` and `check-yaml` for checking the syntax of JSON and YAML files.
- `pretty-format-json` and `pretty-format-yaml` for automatically formatting JSON and YAML files.
- `isort` for sorting Python imports.
- `black` for automatic Python code formatting.
- `flake8` for checking Python code against PEP8 style guide.

## Setup
1. Clone the repository.
2. Install the dependencies using Poetry: `poetry install`
3. Install the pre-commit hooks: `pre-commit install`

## Usage
Run the dockerfile using `docker build .`

## Contributing
Provide instructions on how to contribute to your project.
