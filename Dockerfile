FROM python:3.11-slim

# Avoid Python writing .pyc files and buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies (if any) and project requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Create unprivileged user
RUN useradd -m appuser || true

# Copy project
COPY . /app
RUN chown -R appuser:appuser /app
USER appuser

# Streamlit default port
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
