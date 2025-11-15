import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.main import app
from app.models import Base
from app.deps import get_db

@pytest.fixture
async def get_test_db():
    """
    Возвращает тестовую БД.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True
    )

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    # Создание таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Создание сессии для тестов
    async with async_session() as session:
        yield session

    # Удаление таблиц после тестов
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def override_get_db(get_test_db: AsyncSession):
    """
    Подменяет зависимость get_db на get_test_db.
    """
    async def _override():
        yield get_test_db

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.clear()

@pytest.fixture
async def test_client():
    """
    Асинхронный клиент для тестов FastAPI через ASGITransport.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
