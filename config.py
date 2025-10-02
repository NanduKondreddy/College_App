# config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Database URI: use managed DATABASE_URL or fallback to SQLite file
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(basedir, 'data.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask secret
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

    # JWT config
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # seconds
