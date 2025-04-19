# syntax=docker/dockerfile:1.4

# Build stage for dependencies
FROM python:3.11-slim as builder

WORKDIR /build
COPY requirements.txt .

# Simplified layer caching
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y \
    build-essential \
    imagemagick \
    ffmpeg \
    libsm6 \
    libxext6

# Configure ImageMagick
RUN sed -i \
    -e 's/<policy domain="path" rights="none" pattern="@\*"/<policy domain="path" rights="read|write" pattern="@*"/g' \
    -e 's/<policy domain="resource" name="memory" value="256MiB"/<policy domain="resource" name="memory" value="1GiB"/g' \
    -e 's/<policy domain="resource" name="disk" value="1GiB"/<policy domain="resource" name="disk" value="8GiB"/g' \
    -e 's/<policy domain="resource" name="width" value="16KP"/<policy domain="resource" name="width" value="64KP"/g' \
    -e 's/<policy domain="resource" name="height" value="16KP"/<policy domain="resource" name="height" value="64KP"/g' \
    /etc/ImageMagick-6/policy.xml || true

# Use pip cache
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user -r requirements.txt

# Development stage
FROM builder AS dev

# Create directory structure in dev stage
RUN mkdir -p /app/exports/logs/gpt_logs \
             /app/exports/logs/pexel_logs \
             /app/exports/logs/ffmpeg \
             /app/exports/photos \
             /app/exports/audio \
             /app/exports/videos \
             /app/exports/captions \
             /app/temp/pexels_cache \
             /app/temp/pexels_cache/videos \
             /app/temp/pexels_cache/metadata \
             /app/temp/theme_cache \
             /app/temp/content_cache \
             /tmp/.buildx-cache && \
    chmod -R 755 /app/exports /app/temp && \
    chmod 777 /tmp/.buildx-cache

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Add the app directory to Python path
ENV PYTHONPATH=/app

# Copy only necessary files
COPY app/ /app/app/
COPY web/streamlit_app.py /app/web/streamlit_app.py
COPY config/ /app/config/
COPY app.py /app/app.py

# Set environment variables
ENV IMAGEMAGICK_BINARY=/usr/bin/convert
ENV OPENAI_API_KEY="" \
    PEXELS_API_KEY=""

EXPOSE 7701

# Use the same command as in docker-compose
CMD ["streamlit", "run", "web/streamlit_app.py", "--server.port=7701", "--server.address=0.0.0.0"]

# Use dev stage by default
FROM dev AS final