FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY gifbot.py ./
COPY arial.ttf ./
COPY comic.ttf ./
COPY impact.ttf ./
COPY temp/.gitkeep ./temp/.gitkeep

RUN useradd --create-home botuser && chown -R botuser:botuser /app
USER botuser

CMD ["python", "gifbot.py"]