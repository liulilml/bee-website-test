FROM python:3.10-slim-bookworm

LABEL maintainer="openclaw-backup"
LABEL description="Agent-Reach - Multi-platform content reader"

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 克隆并安装 Agent-Reach
RUN git clone https://github.com/Panniantong/agent-reach.git . \
    && pip install --no-cache-dir -e .

# 数据输出目录
RUN mkdir -p /app/output

VOLUME ["/app/output"]

ENTRYPOINT ["python3", "-m", "agent_reach"]
CMD ["--help"]
