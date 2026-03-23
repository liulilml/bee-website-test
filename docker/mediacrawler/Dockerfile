FROM python:3.10-slim-bookworm

LABEL maintainer="openclaw-backup"
LABEL description="MediaCrawler - Chinese social media crawler"

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    wget \
    curl \
    gnupg \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 克隆 MediaCrawler
RUN git clone https://github.com/NanmiCoder/MediaCrawler.git . \
    && pip install --no-cache-dir -r requirements.txt \
    && playwright install chromium --with-deps

# 数据输出目录
RUN mkdir -p /app/data /app/browser_data

VOLUME ["/app/data", "/app/browser_data"]

ENTRYPOINT ["python3", "main.py"]
CMD ["--help"]
