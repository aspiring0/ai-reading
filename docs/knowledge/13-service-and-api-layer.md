# 13 - Service 层和 API 层：为什么要分三层

## 一句话说清楚

API 层是"前台"，Service 层是"经理"，Repository 层是"仓库"。前台接客，经理安排活，仓库搬东西。

## 为什么不能直接在 API 里写逻辑？

你可能会想：API 端点里直接操作数据库不就行了吗？为什么要绕一圈？

```
❌ 不分层的写法（很乱）：
  API 端点里：
    1. 接收参数
    2. 校验参数
    3. 计算字数
    4. 写 SQL 插入
    5. 查询结果
    6. 转换格式
    7. 返回响应
  → 一个函数干了七件事，改一处要改全部

✅ 分三层的写法（清晰）：
  API 层 (articles.py)：
    接收参数 → 调用 Service → 返回响应   （只管接客和送客）

  Service 层 (article_service.py)：
    计算字数 → 调用 Repository → 转换格式  （只管业务规则）

  Repository 层 (article_repo.py)：
    写 SQL → 返回数据库对象              （只管搬数据）
```

## 真实例子：创建文章

用户请求 → 后端做了什么：

```
API 层 (admin.py create_article)
  │  接收 JSON → 转成 ArticleCreate 对象
  │  检查 X-Admin-Key 是否正确
  │  调用 service.create_article(data)
  │  把返回值转成 JSON 响应
  ↓
Service 层 (article_service.py create_article)
  │  计算字数 word_count
  │  创建 Article ORM 对象
  │  调用 repo.create(article) 存入数据库
  │  如果有 segments 也一起存
  │  用 ArticleResponse 转换格式返回
  ↓
Repository 层 (article_repo.py create)
  │  session.add(article) → 写入数据库
  │  session.flush() → 确认写入
  │  session.refresh() → 读回最新数据
  │  返回 Article 对象
```

## 关键概念

### API 层的 Depends(get_db)
```python
async def list_articles(db: AsyncSession = Depends(get_db)):
```
意思是："每个请求给我一个新的数据库连接，用完自动关"。FastAPI 的依赖注入系统自动管理。

### Service 层的 model_validate
```python
ArticleResponse.model_validate(article)
```
把数据库对象（ORM）转成 API 响应格式（Pydantic）。因为数据库对象有很多内部属性，不能直接返回给用户。

### Admin Key 认证
```python
async def verify_admin_key(x_admin_key: str = Header(...)):
```
从请求头读 `X-Admin-Key`，和配置里的密钥比对。只有通过验证才能调管理端点。

## 测试是怎么工作的

```
API 测试不用启动服务器！
  用 httpx.AsyncClient + ASGITransport
  直接调用 FastAPI 代码，跳过网络层

测试流程：
  1. 创建测试数据库连接
  2. 覆盖 get_db 依赖 → 用测试连接
  3. 发请求 → 验证响应
  4. 回滚数据库 → 不留痕迹
```
