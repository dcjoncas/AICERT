FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r /app/backend/requirements.txt
WORKDIR /app/backend
EXPOSE 8000
CMD ["python","run.py"]
