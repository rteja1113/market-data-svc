# Use an official Python runtime as a base image
FROM python:3.10

# Install Poetry
RUN pip install poetry

# Set the working directory in the container
WORKDIR /app

# Copy the poetry configuration files into the container
COPY pyproject.toml poetry.lock* /app/

# Configure Poetry
# - Do not create a virtual environment inside the container;
#   dependencies will be installed system-wide
RUN poetry config virtualenvs.create false

# Install dependencies using Poetry
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy the rest of your application code
COPY . /app
