FROM python:3.11-slim

WORKDIR /app

# системные зависимости (нужны иногда для aiohttp)
RUN apt-get update && apt-get install -y gcc

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
