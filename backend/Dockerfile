# 阶段1：安装依赖
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 阶段2：运行应用（更小的镜像）
FROM python:3.12-slim

WORKDIR /app

# 从 builder 阶段复制已安装的包
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
