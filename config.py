import os

class Config:
    SECRET_KEY = "project_cipher_secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///cipher.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False