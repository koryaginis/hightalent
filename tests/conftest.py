# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.models import Base
from app.deps import get_db

# ---- Любыеio backend для async тестов ----
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

# ---- Тестовая БД ----
@pytest.fixture
async def test_db_session():
    """
    Создаём in-memory SQLite для тестов.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True
    )

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    # создаём все таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # создаём сессию для тестов
    async with async_session() as session:
        yield session

    # удаляем таблицы после тестов
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# ---- Подмена зависимости get_db ----
@pytest.fixture
async def override_get_db(test_db_session: AsyncSession):
    """
    Подменяем get_db на тестовую сессию.
    """
    async def _override():
        yield test_db_session

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.clear()

# ---- Async клиент FastAPI ----
@pytest.fixture
async def test_client():
    """
    Асинхронный клиент для тестов FastAPI через ASGITransport.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
