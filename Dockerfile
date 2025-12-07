FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

RUN useradd -m appuser || true

COPY . /app
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8502

CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8502", "--server.address", "127.0.0.1"]
