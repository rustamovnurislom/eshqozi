# Python bazasi digest bilan mahkamlangan; yangilashda testlarni qayta bajaring.
ARG DEPS_STAGE=dependencies-online
FROM python:3.12-slim@sha256:05cda9777409a9c3ffddd94a4c476b79f0769a0b4857f0c7ed9226b6800b0d6f AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.lock ./
FROM base AS dependencies-online
# Cloud proksining CA to‘plami kerak bo‘lsa, --secret id=ca_bundle,src=... bering.
# Bu TLS tekshiruvini saqlaydi; sertifikat kalit emas va tasvirga ko‘chirilmaydi.
RUN --mount=type=secret,id=ca_bundle \
    if [ -f /run/secrets/ca_bundle ]; then \
      PIP_CERT=/run/secrets/ca_bundle pip install --require-hashes --no-cache-dir -r requirements.lock; \
    else pip install --require-hashes --no-cache-dir -r requirements.lock; fi
FROM base AS dependencies-offline
RUN --mount=from=wheels,source=/,target=/wheels \
    pip install --require-hashes --no-index --find-links=/wheels --no-cache-dir -r requirements.lock
FROM ${DEPS_STAGE} AS application
RUN groupadd --gid 10001 app && useradd --uid 10001 --gid app --create-home app \
    && mkdir -p /app/var && chown app:app /app/var
COPY --chown=10001:10001 eshqozi ./eshqozi
COPY --chown=10001:10001 data ./data
USER 10001:10001
ENV ESHQOZI_HOST=0.0.0.0 ESHQOZI_DB=/app/var/eshqozi.sqlite3
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/readyz',timeout=3)"
CMD ["python", "-m", "eshqozi", "serve"]
