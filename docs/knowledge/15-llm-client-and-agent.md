# 15 - LLM Client 和 Agent：怎么让代码调用 AI

## 一句话说清楚

LLM Client 是"电话"，Agent 是"拿着电话办事的人"。Client 负责打通电话，Agent 负责说什么话、怎么理解回答。

## 为什么不能直接用 OpenAI SDK

```
❌ 每个地方直接写：
    client = AsyncOpenAI(...)
    response = await client.chat.completions.create(...)
    # 每次都要处理：重试、超时、日志、JSON 解析...

✅ 封装后：
    client = LLMClient()
    result = await client.chat_json("system", "user")
    # 重试、日志、JSON 全自动处理
```

好处：换 AI 模型只改一处，测试时 mock 一个类就行。

## LLMClient 做了什么

```
你的代码调用 chat()
    ↓
1. 构造请求（model、messages、temperature）
    ↓
2. 调用 OpenAI SDK
    ↓ 成功 → 返回文本
    ↓ 失败 → 等待 1s → 重试
    ↓       再失败 → 等待 2s → 重试
    ↓       还失败 → 等待 4s → 重试
    ↓ 全失败 → 抛 ExternalServiceException
    ↓
3. 记录日志（token 用量、耗时、成功/失败）
```

**指数退避**：每次失败等的时间翻倍。为什么？AI 服务短暂过载时，同时重试只会更慢，错开时间更有效。

## BaseAgent 做了什么

```
子类（比如 ContentGenerator）设置 system_prompt
    ↓
调用 call_llm_json(user_prompt, result_type=GenerationResult)
    ↓
1. 调用 LLMClient.chat_json() 拿到 AI 回复
    ↓
2. json.loads() 解析 JSON
    ↓
3. GenerationResult.model_validate() 校验字段
    ↓ 成功 → 返回 Pydantic 对象
    ↓ JSON 格式错 → 在 prompt 里加上错误提示 → 重试
    ↓ 字段缺失   → 同上重试
    ↓ 全失败     → 抛 ExternalServiceException
```

**关键设计：重试时把错误信息告诉 AI**

```
第一次 AI 返回：{"title": "xxx"}  ← 缺了 score 字段
第二次 prompt 里加上：
  "上次返回的 JSON 格式有误：score field required
   请确保返回合法 JSON。"
AI 就知道哪里错了，能纠正。
```

## 为什么用 Pydantic 而不是直接用 dict

```python
# dict：运行时不检查，字段名拼错了也不知道
data = json.loads(raw)  # {"titel": "xxx"}  ← 拼错了，不报错

# Pydantic：立即报错，强制字段完整
result = GenerationResult.model_validate(data)  # → ValidationError!
```

## 文件对应关系

| 文件 | 角色 |
|---|---|
| `utils/llm_client.py` | 电话：打通 AI、重试、日志 |
| `agents/base.py` | 基类：通用的"拿电话办事"流程 |
| `agents/content_generator.py`（下步） | 写手：让 AI 写文章 |
| `agents/content_judge.py`（下步） | 评委：让 AI 评文章 |
