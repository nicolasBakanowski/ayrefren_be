FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip

# 1) Copiá primero requirements para aprovechar la cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Recién ahora copiá el resto del código
COPY . .

RUN chmod +x scripts/start.sh

EXPOSE 8000
ENTRYPOINT ["sh", "scripts/start.sh"]
