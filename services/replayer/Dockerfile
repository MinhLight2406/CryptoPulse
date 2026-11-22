FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app/libs
RUN useradd --create-home appuser
COPY libs/ ./libs/
COPY services/replayer/src/ ./src/
USER appuser
CMD ["python", "src/main.py"]
