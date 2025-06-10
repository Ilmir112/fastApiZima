from sqlalchemy import and_, delete, insert, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from zimaApp.logger import logger
from zimaApp.database import async_session_maker


class BaseDAO:
    model = None

    @classmethod
    async def find_all(cls, limit=None, **filter_by):
        async with async_session_maker() as session:  # Создаем экземпляр сессии
            query = select(cls.model).filter_by(
                **filter_by
            )  # Используем модель для выборки
            if limit is not None:
                query = query.limit(limit)  # Добавляем лимит, если он задан
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_first(cls, **filter_by):
        async with async_session_maker() as session:  # Создаем экземпляр сессии
            query = select(cls.model).filter_by(
                **filter_by
            )  # Используем модель для выборки
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def find_by_id(cls, model_id: int):
        async with async_session_maker() as session:  # Создаем экземпляр сессии
            query = select(cls.model).filter_by(
                id=model_id
            )  # Используем модель для выборки
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        try:
            async with async_session_maker() as session:
                query = select(cls.model.__table__.columns).filter_by(**filter_by)
                result = await session.execute(query)
                if result:
                    return result.mappings().one_or_none()
        except Exception as e:
            logger.error(e)

    @classmethod
    async def delete_item_all_by_filter(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            instances = result.scalars().all()  # Получить все совпадающие записи

            if not instances:
                return None  # Или что-то другое, если записей не найдено

            # Удаляем все найденные записи
            for instance in instances:
                await session.execute(
                    delete(cls.model).where(cls.model.id == instance.id)
                )
            await session.commit()
            return {"deleted": len(instances)}

    @classmethod
    async def add_data(cls, **data):
        try:
            query = (
                insert(cls.model).values(**data).returning(*cls.model.__table__.columns)
            )
            async with async_session_maker() as session:
                result = await session.execute(query)
                await session.commit()
                return result.mappings().first()

        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot insert data into table"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot insert data into table"

            logger.error(msg, extra={"table": cls.model.__tablename__}, exc_info=True)
            return None

    @classmethod
    async def update_data(cls, datas, **data):
        async with async_session_maker() as session:
            query = (
                update(cls.model)
                .where(cls.model.id == datas)
                .values(**data)
                .returning(*cls.model.__table__.columns)
            )
            result = await session.execute(query)
            await session.commit()
            return result.mappings().first()

