from pydantic import Field, computed_field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuration settings for the application."""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

    Host: str = Field(default='localhost', env='HOST', description='Database host')
    PORT: int = Field(default=5432, env='PORT', description='Database port')
    DB_USER: str = Field(default='postgres', env='DB_USER', description='Database user')
    DB_PASSWORD: str = Field(default='Mromi88123', env='DB_PASSWORD', description='Database password')
    DB_NAME: str = Field(default='AI_Resume_DB', env='DB_NAME', description='Database name')

    #Session setting
    Max_Connection: int = Field(default=10, env='MAX_CONNECTION', description='Maximum number of database connections')
    Max_Overflow: int = Field(default=20, env='MAX_OVERFLOW', description='Maximum number of overflow connections')
    timeout: int = Field(default=30, env='TIMEOUT', description='Database connection timeout in seconds')

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """Construct the database URL from the settings."""
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.Host}:{self.PORT}/{self.DB_NAME}"

    def DATABASE_ASYNC_URL(self) -> str:
        """Construct the asynchronous database URL from the settings."""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.Host}:{self.PORT}/{self.DB_NAME}"

    
#Instatinate the object of the settings class to use in session.py and main.py
settings = Settings()