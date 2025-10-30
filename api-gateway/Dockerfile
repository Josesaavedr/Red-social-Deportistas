FROM python:3.11-slim
WORKDIR /app
COPY api_gateway_fastapi.py ./
RUN pip install --no-cache-dir fastapi uvicorn[standard] httpx PyJWT
EXPOSE 8000
CMD ["uvicorn", "api_gateway_fastapi:app", "--host", "0.0.0.0", "--port", "8000"]