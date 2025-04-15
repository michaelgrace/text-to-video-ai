# syntax=docker/dockerfile:1.4

FROM python:3.11-slim

# Create necessary directories
RUN python create_directories.py

# Install ImageMagick and other necessary dependencies
RUN apt-get update && apt-get install -y \
    imagemagick \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Fix ImageMagick policy to allow proper video processing
RUN sed -i 's/<policy domain="path" rights="none" pattern="@\*"/<policy domain="path" rights="read|write" pattern="@*"/g' /etc/ImageMagick-6/policy.xml || true
# Add these more comprehensive policy updates for video processing
RUN sed -i 's/<policy domain="resource" name="memory" value="256MiB"/<policy domain="resource" name="memory" value="1GiB"/g' /etc/ImageMagick-6/policy.xml || true
RUN sed -i 's/<policy domain="resource" name="disk" value="1GiB"/<policy domain="resource" name="disk" value="8GiB"/g' /etc/ImageMagick-6/policy.xml || true
RUN sed -i 's/<policy domain="resource" name="width" value="16KP"/<policy domain="resource" name="width" value="64KP"/g' /etc/ImageMagick-6/policy.xml || true
RUN sed -i 's/<policy domain="resource" name="height" value="16KP"/<policy domain="resource" name="height" value="64KP"/g' /etc/ImageMagick-6/policy.xml || true

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt streamlit

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/output /app/temp && \
    chmod -R 755 /app/output /app/temp

# Set ImageMagick binary path
ENV IMAGEMAGICK_BINARY=/usr/bin/convert

# Set environment variables as placeholders
ENV OPENAI_API_KEY=""
ENV PEXELS_API_KEY=""

EXPOSE 7701

# Use the same command as in docker-compose
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=7701", "--server.address=0.0.0.0"]

# DO NOT REMOVE 
# Command to run the application
# ENTRYPOINT ["python", "app.py"]
# CMD ["Text To Video AI Demo"]