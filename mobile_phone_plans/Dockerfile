# Use uv's official Python image as base
# https://github.com/astral-sh/uv/pkgs/container/uv/579620319?tag=python3.13-bookworm
FROM ghcr.io/astral-sh/uv:python3.13-bookworm

# set labels
ARG BUILD_DATE
LABEL org.opencontainers.image.created=$BUILD_DATE
LABEL org.opencontainers.image.description="A scraper ETL pipeline for French mobile phone plans."
LABEL org.opencontainers.image.licenses="tagny"
LABEL org.opencontainers.image.source="https://github.com/tagny/quechoisir-comparator-scrapers/mobile_phone_plans"
LABEL org.opencontainers.image.title="quechoisir-mobile-phone-plans-etl"
LABEL org.opencontainers.image.url="https://github.com/tagny/quechoisir-comparator-scrapers/mobile_phone_plans/Dockerfile"
LABEL org.opencontainers.image.version="0.1.0"
LABEL org.opencontainers.image.vendor="tagny"
LABEL org.opencontainers.image.authors="tagny https://github.com/tagny"

# Set working directory
WORKDIR /app

# install the chrome web driiver
RUN apt-get update -y
RUN apt upgrade -y
RUN mkdir -p /var/lib/apt/lists/partial
RUN apt install -y libsm6 libxext6 ffmpeg libfontconfig1 libxrender1 libgl1-mesa-glx
RUN apt -y --force-yes install libu2f-udev fonts-liberation libasound2  libatk-bridge2.0-0 libatk1.0-0  libatspi2.0-0  libcairo2 libcups2 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libx11-6 libxcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxkbcommon0 libxrandr2 xdg-utils
RUN apt -y --force-yes install wget
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb
RUN apt install -f

# Copy application code
COPY etl ./etl

# Copy pyproject.toml and README.md for dependency resolution
COPY pyproject.toml README.md ./

# Copy configuration files
COPY config ./config

# Install project dependencies (including dev deps)
RUN uv sync

# Set default environment variables for MCP server
ARG PROJECT_ID
ARG BUCKET_NAME
ARG RAW_BASE_DIR
ARG BASE_URL

ENV PROJECT_ID=${PROJECT_ID}
ENV BUCKET_NAME=${BUCKET_NAME}
ENV RAW_BASE_DIR=${RAW_BASE_DIR}
ENV BASE_URL=${BASE_URL}

# Run the server with customizable args from env vars
CMD ["sh", "-c", "uv run -m etl extract -c config/extract_action_sequence.yml"]
