import pytest
from sqlmodel.ext.asyncio.session import AsyncSession
from models import Item


@pytest.fixture()
async def items(db):
    items = []

    async with AsyncSession(db) as session:
        for i in range(3):
            item = Item(
                name=f"Item #{i}",
            )
            items.append(item)
            session.add(item)
        await session.commit()
        [await session.refresh(item) for item in items]

    yield items
