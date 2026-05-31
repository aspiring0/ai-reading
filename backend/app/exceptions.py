"""
自定义异常层级

所有业务异常继承 AppException，在 FastAPI exception_handlers 中统一注册。
Service 层抛异常，API 层不需要 try/except，错误响应自动格式化。

统一错误响应格式：
    {
        "detail": "人类可读消息",
        "error_code": "ARTICLE_NOT_FOUND",
        "errors": [{"field": "email", "message": "格式无效"}]
    }
"""

from fastapi import HTTPException


class AppException(HTTPException):
    """基础业务异常，所有自定义异常的父类。"""

    def __init__(
        self,
        status_code: int = 500,
        detail: str = "Internal server error",
        error_code: str = "INTERNAL_ERROR",
        errors: list[dict] | None = None,
    ) -> None:
        self.error_code = error_code
        self.errors = errors or []
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(AppException):
    """资源未找到 — 当查询的数据不存在时抛出。"""

    def __init__(self, detail: str = "Resource not found", error_code: str = "NOT_FOUND") -> None:
        super().__init__(status_code=404, detail=detail, error_code=error_code)


class ValidationException(AppException):
    """业务校验失败 — 请求数据不符合业务规则时抛出。"""

    def __init__(
        self,
        detail: str = "Validation error",
        error_code: str = "VALIDATION_ERROR",
        errors: list[dict] | None = None,
    ) -> None:
        super().__init__(status_code=422, detail=detail, error_code=error_code, errors=errors)


class UnauthorizedException(AppException):
    """认证失败 — token 无效/过期或凭据错误。"""

    def __init__(self, detail: str = "Unauthorized", error_code: str = "UNAUTHORIZED") -> None:
        super().__init__(status_code=401, detail=detail, error_code=error_code)


class ForbiddenException(AppException):
    """权限不足 — 已认证但无权访问。"""

    def __init__(self, detail: str = "Forbidden", error_code: str = "FORBIDDEN") -> None:
        super().__init__(status_code=403, detail=detail, error_code=error_code)


class ExternalServiceException(AppException):
    """外部服务异常 — LLM 调用失败、第三方 API 超时等。"""

    def __init__(
        self,
        detail: str = "External service unavailable",
        error_code: str = "EXTERNAL_SERVICE_ERROR",
    ) -> None:
        super().__init__(status_code=503, detail=detail, error_code=error_code)
