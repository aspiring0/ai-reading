# 全流程：从你在浏览器输入 URL 到看到结果

## 一个完整的请求链路

假设你在浏览器打开 `http://localhost:8000/health`，背后发生了这些事：

```
你在浏览器输入 URL
    ↓
① 浏览器发请求给 Uvicorn（Python 的 Web 服务器）
    ↓
② Uvicorn 把请求交给 FastAPI（我们的代码框架）
    ↓
③ FastAPI 看请求路径是 /health，找到对应的函数
    ↓
④ 执行 health() 函数里的代码：
    ├── 连接 PostgreSQL，执行 SELECT 1 看数据库在不在
    └── 连接 Redis，执行 PING 看缓存在不在
    ↓
⑤ 把结果组装成 JSON 字符串返回
    ↓
⑥ 浏览器显示 {"status":"ok","database":"connected","redis":"connected"}
```

## 每个环节对应项目中的什么

| 环节 | 对应的文件 | 作用 |
|---|---|---|
| Web 服务器 | uvicorn（第三方库） | 接收 HTTP 请求，转交给我们的代码 |
| 框架 | `app/main.py` 里的 `app = FastAPI(...)` | 决定请求该由哪个函数处理 |
| 路由匹配 | `@app.get("/health")` | 把 URL 和函数绑定在一起 |
| 数据库连接 | `app/database.py` | 和 PostgreSQL 通信 |
| Redis 连接 | `app/main.py` 的 lifespan | 和 Redis 通信 |
| 配置读取 | `app/config.py` | 从 .env 文件读取数据库地址、密码等 |
| 容器运行 | `docker-compose.yml` | 把 PostgreSQL 和 Redis 跑在 Docker 里 |

## 它们是怎么启动的

```
你在终端输入: cd backend && uvicorn app.main:app --reload

1. Uvicorn 启动
2. 加载 app.main 这个模块
3. 执行 main.py 里的代码：
   ├── 读取 config.py → 从 .env 加载配置（数据库地址、Redis 地址等）
   ├── 创建数据库引擎（database.py 里的 engine）
   ├── 注册 CORS 中间件（允许前端跨域访问）
   ├── 注册路由（/health、/api/v1/...）
   └── 执行 lifespan 的启动部分 → 连接 Redis，存到 app.state.redis
4. Uvicorn 开始监听 8000 端口，等待请求
5. 请求进来 → 按上面的链路处理
```

## 一句话总结每个文件是干嘛的

- **config.py** → 读配置（数据库在哪、密码是啥）
- **database.py** → 连数据库
- **main.py** → 把所有东西组装起来，是整个应用的入口
- **dependencies.py** → 提供公用工具（给数据库连接、给 Redis 连接）
- **exceptions.py** → 定义错误类型（404、401 等）
- **docker-compose.yml** → 让 PostgreSQL 和 Redis 在容器里跑
- **.env** → 存密码和密钥（不提交到 git）
