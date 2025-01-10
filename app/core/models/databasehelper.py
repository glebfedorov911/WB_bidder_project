from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_scoped_session, async_sessionmaker

from ..settings import settings


class DataBaseHelper:
    def __init__(self, url, echo):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
            pool_size=300,
            max_overflow=200,
            pool_timeout=10,
            pool_recycle=1500,
        )

        self.async_session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False 
        )

    async def async_session_depends(self) -> AsyncSession:
        async with self.async_session_factory() as async_session:
            yield async_session


database_helper = DataBaseHelper(
    url=settings.db_settings.url,
    echo=settings.db_settings.echo,
)