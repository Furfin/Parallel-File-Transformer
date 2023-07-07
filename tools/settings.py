from pydantic import BaseSettings


class Settings(BaseSettings):
    db: str
    db_name: str
    db_password: str
    db_host: str
    db_login: str
    
    s3_host: str
    s3_ak: str
    s3_sk: str
    
    rabbitmq_host: str
    rabbitmq_ak: str
    rabbitmq_sk: str
    
    
    class Config:
        env_file = ".env"

settings = Settings()