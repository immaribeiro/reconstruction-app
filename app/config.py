from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://reconstruction_user:my_secure_pg_password_here@localhost:5432/reconstruction_db" # Updated for PostgreSQL
    api_key: str = "your_super_secret_api_key" # Placeholder, should be loaded from env var

    class Config:
        env_file = ".env"

settings = Settings()