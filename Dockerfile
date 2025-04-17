# syntax=docker/dockerfile:1.4

# Build stage for dependencies
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements.txt .
RUN pip install --user -r requirements.txt streamlit

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    imagemagick \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/* \
    && sed -i \
    -e 's/<policy domain="path" rights="none" pattern="@\*"/<policy domain="path" rights="read|write" pattern="@*"/g' \
    -e 's/<policy domain="resource" name="memory" value="256MiB"/<policy domain="resource" name="memory" value="1GiB"/g' \
    -e 's/<policy domain="resource" name="disk" value="1GiB"/<policy domain="resource" name="disk" value="8GiB"/g' \
    -e 's/<policy domain="resource" name="width" value="16KP"/<policy domain="resource" name="width" value="64KP"/g' \
    -e 's/<policy domain="resource" name="height" value="16KP"/<policy domain="resource" name="height" value="64KP"/g' \
    /etc/ImageMagick-6/policy.xml || true

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy only necessary files
COPY utility/ /app/utility/
COPY app.py streamlit_app.py /app/

# Create directories with permissions
# RUN python /app/utility/directories/create_directories.py \
#     && chmod -R 755 /app/output /app/temp

# Set environment variables
ENV IMAGEMAGICK_BINARY=/usr/bin/convert \
    OPENAI_API_KEY="" \
    PEXELS_API_KEY=""

EXPOSE 7701

# Use the same command as in docker-compose
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=7701", "--server.address=0.0.0.0"]

# DO NOT REMOVE 
# Command to run the application
# ENTRYPOINT ["python", "app.py"]
# CMD ["Text To Video AI Demo"]