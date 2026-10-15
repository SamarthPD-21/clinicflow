from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ClinicFlow API"
    app_version: str = "1.0.0"
    database_url: str = "postgresql+psycopg://clinicflow:clinicflow@localhost:5432/clinicflow"
    # Length of one bookable appointment slot, used for double-booking detection.
    slot_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
