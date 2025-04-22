from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from ..core.config import settings
from contextlib import asynccontextmanager

class PostgresConnection(object): 
    def __init__(self, db_url: str=None):
        if db_url is None:
            db_url = settings.TARGET_DATABASE_URL
            if db_url.startswith('postgresql://'):
                db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://')
        
        self._db_url = db_url
        
    def __repr__(self) -> str:
        return f"Config Postgres url: {self._db_url}"
    
    async def connect_db(self):
        """
        Connect to PostgreSQL database asynchronously.
        """
        engine = create_async_engine(
            self._db_url, 
            pool_size=10, 
            max_overflow=20, 
            pool_timeout=30, 
            pool_recycle=1800
        )
        self.session = async_sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=engine, 
            class_=AsyncSession
        )
        
    async def close_db(self):
        """
        Close the database connection.
        """
        if hasattr(self, 'session'):
            # Trong SQLAlchemy async không cần đóng session_maker
            # nhưng có thể đóng engine nếu cần
            pass
        else:
            print("No session to close.")
    
    @asynccontextmanager
    async def get_session(self):
        """
        Get a session to the database.
        """
        async_session = self.session()
        try:
            yield async_session
        finally:
            await async_session.close()
    
        

