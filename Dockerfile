FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN groupadd --system --gid 10001 appuser \
    && useradd --system --uid 10001 --gid appuser --home-dir /app appuser

COPY --chown=appuser:appuser . .

COPY --chown=appuser:appuser supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir -p /app/media \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && exec supervisord -c /etc/supervisor/conf.d/supervisord.conf"]
