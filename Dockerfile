# 使用官方 Python 3.9 镜像，基于 Debian Bookworm
FROM python:3.9-slim-bookworm

# 设置非交互模式 (沿用自 Debian 基础)
ENV DEBIAN_FRONTEND=noninteractive

# 替换国内源并安装依赖
# 注意：pip已经存在，这里只需要安装 openjdk-17-jdk 和 build-essential
RUN echo "deb http://mirrors.aliyun.com/debian bookworm main contrib non-free" > /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list && \
    apt-get -o Acquire::ForceIPv4=true -o Acquire::Retries=5 -o Acquire::http::Timeout=60 update && \
    # 修复依赖问题
    apt-get -o Acquire::ForceIPv4=true -o Acquire::Retries=5 -o Acquire::http::Timeout=60 install -y --fix-broken && \
    # 安装 openjdk 和 build-essential
    apt-get -o Acquire::ForceIPv4=true -o Acquire::Retries=5 -o Acquire::http::Timeout=60 install -y \
    openjdk-17-jdk \
    build-essential \
    binutils-dev \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 安装 Python 依赖
COPY requirements.txt .
# 使用清华源加速 pip 安装 (这里的 pip 已经是 Python 3.9 对应的 pip)
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir -r requirements.txt

# 复制所有应用源代码
COPY . /app

# 授予必要的执行权限
RUN chmod -R 777 /app

# 暴露应用端口
EXPOSE 5000

# 使用 Gunicorn 启动应用
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]

# docker builder prune
# export HTTP_PROXY="http://127.0.0.1:7890"
# export HTTPS_PROXY="http://127.0.0.1:7890"
# docker buildx build --platform linux/amd64,linux/arm64 -t hx062312/unitrans:v2.1 . --push
