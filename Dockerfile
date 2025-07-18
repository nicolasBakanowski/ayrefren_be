FROM python:3.11-slim

WORKDIR /app

RUN pip install --upgrade pip

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x scripts/start.sh

EXPOSE 8000

ENTRYPOINT ["sh", "scripts/start.sh"]
CMD []
