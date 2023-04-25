FROM python:3.11

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-root

COPY . .

EXPOSE 8080

# Start the application
CMD ["python", "cli.py"]
