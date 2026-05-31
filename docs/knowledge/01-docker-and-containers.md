# Docker

## 为什么需要 Docker

正常开发要在自己电脑上装 PostgreSQL、Redis。装完还要配置端口、设置密码、处理版本冲突。换一台电脑又装一遍。

Docker 的做法：写一个 `docker-compose.yml` 文件描述你需要什么服务，一条命令全启动。别人的电脑只需要装 Docker，不需要单独装 PostgreSQL 和 Redis。

## 三个核心概念

**镜像（image）** = 安装包。`postgres:16-alpine` 就是 PostgreSQL 16 的安装包。

**容器（container）** = 运行中的程序。一个镜像可以启动多个容器。

**数据卷（volume）** = 外接硬盘。容器删了数据就没了，volume 把数据存在容器外面。

## docker-compose.yml 里每行什么意思

```yaml
services:
  postgres:
    image: postgres:16-alpine           # 用这个安装包
    container_name: ai-reading-postgres # 容器名字
    ports:
      - "5432:5432"                     # 你的电脑:容器内部
    volumes:
      - postgres_data:/var/lib/...      # 数据存在外面
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"] # 怎么检查它活着
      interval: 5s                      # 多久检查一次
```

端口映射 `"5432:5432"`：你在代码里写 `localhost:5432`，Docker 把这个请求转发到容器里的 5432 端口。

Redis 端口改成了 6380：因为你电脑的 6379 端口已经被别的程序占了。改的是你电脑这边的端口，容器内部还是 6379。

## 常用命令

```bash
docker compose up -d          # 启动（-d 后台运行）
docker compose ps             # 看状态
docker compose down           # 停掉
docker compose logs postgres  # 看日志
```
