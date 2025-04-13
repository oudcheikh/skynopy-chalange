FROM python:3.10-slim
WORKDIR /app
ENV PYTHONPATH=/app
COPY . .
RUN pip install --cache-dir /tmp/pip_cache -r requirements.txt
CMD ["python", "main.py"]
