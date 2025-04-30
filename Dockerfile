# Enable BuildKit features
# syntax=docker/dockerfile:1.4

# Layer 1: Base Image
FROM python:3.11-slim AS dev

# Layer 2: Set Working Directory
WORKDIR /app

# Layer 3: System Dependencies and Configuration (Combined for cache efficiency)
RUN apt-get update && apt-get install -y \
    # Intel GPU Support - Basic set that's available
    i965-va-driver \
    va-driver-all \
    vainfo \
    # Core Dependencies
    imagemagick \
    ffmpeg \
    libsm6 \
    libxext6 \
    libva-drm2 \
    libva2 \
    # Cleanup and ImageMagick Configuration (same layer to reduce size)
    && rm -rf /var/lib/apt/lists/* \
    && sed -i 's/<policy domain="path" rights="none" pattern="@\*"/<policy domain="path" rights="read|write" pattern="@*"/g' /etc/ImageMagick-6/policy.xml \
    && sed -i 's/<policy domain="resource" name="memory" value="256MiB"/<policy domain="resource" name="memory" value="1GiB"/g' /etc/ImageMagick-6/policy.xml \
    && sed -i 's/<policy domain="resource" name="disk" value="1GiB"/<policy domain="resource" name="disk" value="8GiB"/g' /etc/ImageMagick-6/policy.xml \
    && sed -i 's/<policy domain="resource" name="width" value="16KP"/<policy domain="resource" name="width" value="64KP"/g' /etc/ImageMagick-6/policy.xml \
    && sed -i 's/<policy domain="resource" name="height" value="16KP"/<policy domain="resource" name="height" value="64KP"/g' /etc/ImageMagick-6/policy.xml

# Test GPU access during build (modified to handle missing packages)
RUN vainfo || echo "GPU support will be verified at runtime"

# Layer 4: Python Dependencies (Using cached pip)
COPY requirements.txt .
RUN pip install --upgrade pip
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copy custom fonts for MoviePy/PIL (ensure this path matches your repo)
COPY assets/fonts /app/assets/fonts

# Download NLTK data needed for stemming/fuzzy matching
RUN python -m nltk.downloader punkt

# Layer 5: Application Directory Setup
RUN mkdir -p /app/exports /app/temp && \
    chmod -R 755 /app/exports /app/temp

# Layer 6: Environment Configuration
ENV IMAGEMAGICK_BINARY=/usr/bin/convert

# DO NOT REMOVE PLACEHOLDERS
# ENV OPENAI_API_KEY=""
# ENV PEXELS_API_KEY=""

EXPOSE 7701

# Layer 8: Runtime Command
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=7701", "--server.address=0.0.0.0"]