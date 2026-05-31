# Docker 与容器化

## Docker 是什么

Docker 是一种**打包和运行软件**的方式。正常情况下，你在电脑上装 PostgreSQL、Redis，需要各自安装、配置、设置开机启动。Docker 把这些软件连同它们的运行环境打包成一个"容器"，一条命令就能启动。

类比：Docker 就像集装箱。不管里面装的是什么货物，码头（服务器）只需要处理标准集装箱，不用关心内部。

## Docker Compose 是什么

我们项目里用了 `docker-compose.yml`，它是一个"编排工具"——定义一组容器怎么启动、怎么连接。

看看我们项目中的配置：

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16-alpine       # 用 postgres 16 的精简版镜像
    container_name: ai-reading-postgres
    ports:
      - "5432:5432"                 # 宿主机端口:容器端口
    volumes:
      - postgres_data:/var/lib/postgresql/data  # 数据持久化
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U aireading"]
      interval: 5s                  # 每 5 秒检查一次
      timeout: 5s
      retries: 5                    # 连续失败 5 次才标记为 unhealthy
```

### 关键概念

**image（镜像）**：软件的安装包。`postgres:16-alpine` 就是 PostgreSQL 16 的精简版。

**container（容器）**：镜像运行起来的实例。一个镜像可以启动多个容器。

**ports（端口映射）**：`"5432:5432"` 意思是把你电脑的 5432 端口映射到容器的 5432 端口。这样你在电脑上访问 `localhost:5432` 就等于访问容器里的 PostgreSQL。

为什么 Redis 改成了 6380？因为本地 6379 端口已经被占用了：
```yaml
ports:
  - "${REDIS_PORT:-6379}:6379"    # 宿主机用 6380，容器内部仍然是 6379
```
注意：容器内部端口没变，变的只是你电脑上的端口。

**volumes（数据卷）**：容器是临时的——删掉容器数据就没了。volume 把数据存在容器外面，这样删掉重建容器数据还在。

**healthcheck（健康检查）**：Docker 定期执行一个命令来判断服务是否正常。`pg_isready` 是 PostgreSQL 自带的检查命令。

## 常用命令

```bash
docker compose up -d              # 后台启动所有服务（-d = detached）
docker compose up -d postgres     # 只启动 postgres
docker compose ps                 # 查看容器状态
docker compose down               # 停止并删除容器（数据卷保留）
docker compose down -v            # 停止并删除容器和数据卷（慎用，数据会丢）
docker compose logs postgres      # 查看 postgres 日志
docker compose logs -f redis      # 实时跟踪 redis 日志（-f = follow）
```
