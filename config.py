import os

database_url = os.environ.get("DATABASE_URL", "sqlite:///cipher.db")

if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://", "postgresql://", 1
    )


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "project_cipher_secret")
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False