"""
V1 路由聚合 — 把所有 v1 端点的子路由汇总到一起。

main.py 通过 app.include_router(v1_router, prefix="/api/v1")
把所有端点挂在 /api/v1/ 下。

新增模块时只需要在这里 add_router，不用改 main.py。
"""

from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.articles import router as articles_router

router = APIRouter()

router.include_router(articles_router)
router.include_router(admin_router)
