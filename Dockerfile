FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# cache-friendly: primero deps
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# luego el código
COPY . .

RUN chmod +x scripts/start.sh

EXPOSE 8000
ENTRYPOINT ["sh", "scripts/start.sh"]
