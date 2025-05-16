from sqlalchemy import and_, delete, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

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
    async def find_by_id(cls, model_id: int):
        async with async_session_maker() as session:  # Создаем экземпляр сессии
            query = select(cls.model).filter_by(
                id=model_id
            )  # Используем модель для выборки
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(
                **filter_by
            )  # Используем модель для выборки
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def delete_item(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(
                **filter_by
            )  # Используем модель для выборки
            result = await session.execute(query)
            instance = result.scalar_one_or_none()
            return await session.execute(
                delete(cls.model).where(cls.model.region == instance.region)
            )

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
        async with async_session_maker() as session:
            # Создаем экземпляр сессии
            query = insert(cls.model).values(**data)  # Используем модель для выборки
            await session.execute(query)
            await session.commit()

    @classmethod
    async def update_data(cls, well_number_id, **data):
        async with async_session_maker() as session:
            # Создаем экземпляр сессии
            query = (
                update(cls.model)
                .where(cls.model.id == well_number_id)  # Условие для поиска записи
                .values(**data)
            )
            await session.execute(query)
            await session.commit()

    @classmethod
    async def add_data_all(cls, data_list):
        async with async_session_maker() as session:  # Создаем экземпляр сессии
            query = insert(cls.model)  # Используем модель для выборки
            await session.execute(query, data_list)
            await session.commit()
