from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/job_finder"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    seed_default_user: bool = True
    default_user_name: str = "Chris Carl"
    default_user_email: str = "chris77carl@gmail.com"
    default_user_password: str = "default"

    cors_origins: str = Field(default="http://localhost:3000")
    profile_storage_dir: str = "storage/profiles"
    openai_api_key: str | None = None
    openai_profile_agent_model: str = "gpt-4.1-mini"
    openai_resume_builder_resume_import_model: str = "gpt-4.1-mini"
    openai_resume_builder_jd_model: str = "gpt-4.1-mini"
    openai_resume_builder_assessment_model: str = "gpt-4.1-mini"
    openai_resume_builder_docx_model: str = "gpt-4.1-mini"


settings = Settings()
