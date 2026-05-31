"""
泛型异步 Repository 基类。

提供通用的 CRUD 操作，所有具体 Repository 继承此类获得基础能力。
使用泛型 [T] 让子类自动获得正确的类型提示。

为什么用 Repository 模式：
    把所有 SQL 查询集中在一个地方，Service 层不直接写查询。
    好处：换数据库只改 Repository，测试时 mock Repository 即可。
"""

from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """泛型异步 Repository — 子类只需指定模型类即可获得完整 CRUD。"""

    def __init__(self, model: type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: object) -> T | None:
        """按主键查一条记录，找不到返回 None。"""
        return await self.session.get(self.model, id)

    async def get_multi(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> list[T]:
        """查多条记录，支持分页。"""
        stmt = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, obj: T) -> T:
        """创建一条记录并 flush（由 get_db 统一 commit）。"""
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj: T, data: dict) -> T:
        """更新记录的字段值。data 是 {字段名: 新值} 的字典。"""
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: T) -> None:
        """删除一条记录。"""
        await self.session.delete(obj)
        await self.session.flush()

    async def count(self) -> int:
        """统计总记录数。"""
        stmt = select(func.count()).select_from(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one()
