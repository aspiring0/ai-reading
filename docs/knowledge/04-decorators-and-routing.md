# 装饰器和路由

## 为什么 @app.get("/health") 这样写

`@app.get("/health")` 是一个 Python 装饰器。把它理解成一个"注册标签"。

```python
@app.get("/health")
async def health():
    return {"status": "ok"}
```

这行代码的意思是：**把这个函数注册到 app 上，当有人访问 /health 路径时，调用这个函数**。

拆开看：
- `app` — 就是我们创建的 FastAPI 实例（`app = FastAPI()`）
- `.get` — HTTP GET 方法（还有 `.post`、`.put`、`.delete` 等）
- `"/health"` — URL 路径

所以：
- `@app.get("/articles")` → 用 GET 方法访问 /articles 时触发
- `@app.post("/articles")` → 用 POST 方法访问 /articles 时触发
- `@app.delete("/articles/123")` → 用 DELETE 方法访问 /articles/123 时触发

GET/POST 的区别：GET 是"给我数据"（浏览器打开网页就是 GET），POST 是"我给你数据"（提交表单就是 POST）。

## 为什么叫 "装饰器"

因为它"装饰"了函数——在函数外面包装了一层额外功能。这里的额外功能是：把这个函数注册为一个 API 端点。

不写装饰器的话，等价于：
```python
async def health():
    return {"status": "ok"}

app.add_api_route("/health", health, methods=["GET"])
```

装饰器只是更简洁的写法。
