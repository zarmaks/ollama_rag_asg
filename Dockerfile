FROM python:3.11-slim
WORKDIR /app

# Install uv - the fast Python package installer
RUN pip install --no-cache-dir uv

COPY requirements.txt .
RUN uv pip install --no-cache --system -r requirements.txt

COPY ./src ./src
COPY ./data ./data
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
