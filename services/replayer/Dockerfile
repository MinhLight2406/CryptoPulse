FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app/libs
COPY services/replayer/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd --create-home appuser
COPY libs/ ./libs/
COPY services/replayer/src/ ./src/
USER appuser
CMD ["python", "src/main.py"]
