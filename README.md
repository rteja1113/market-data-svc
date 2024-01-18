# [WIP] IEX-APP
# TODO
- [X] Add pre-commit hooks
- [ ] Descriptive README
- [ ] Add tests
- [ ] Add CI/CD
- [ ] Add Dockerfile
- [ ] Build DB and ORM
- [ ] Add API


## Description
This is a Python application that provides an API for Indian Energy Exchange Data. It uses web scraping techniques to gather data and pandas for data manipulation.


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
Provide instructions on how to use your application.

## Contributing
Provide instructions on how to contribute to your project.
