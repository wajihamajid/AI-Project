import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# 1. Define your Settings Schema
class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., validation_alias="DATABASE_URL")
    Max_Connection: int = Field(5, validation_alias="Max_Connection")
    Max_Overflow: int = Field(10, validation_alias="Max_Overflow")
    timeout: int = Field(30, validation_alias="timeout")

    # This replaces the old 'class Config' format in Pydantic v2
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Prevents errors if your .env has other variables
    )

# 2. Instantiate the settings object (This actually reads the .env file)
settings = Settings()

# 3. Create your usable variables for the rest of your app
DATABASE_URL = settings.DATABASE_URL
MAX_CONNECTION = settings.Max_Connection
MAX_OVERFLOW = settings.Max_Overflow
TIMEOUT = settings.timeout

# Quick test print to make sure it loads
# print(f"Successfully loaded Database URL: {DATABASE_URL}")
# print(f"Max Connections: {MAX_CONNECTION}")