from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "integration-service"
    kafka_bootstrap_servers: str = "localhost:9092"
    postgres_dsn: str = "postgresql+psycopg2://integration:integration@localhost:5432/integration"


settings = Settings()
