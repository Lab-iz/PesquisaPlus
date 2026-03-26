import os

from sqlalchemy.pool import StaticPool


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///pesquisa_plus.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_NAME = "PESQUISA+"
    INSTITUTION_NAME = os.getenv("INSTITUTION_NAME", "Instituicao Academica")
    CONTENT_PREVIEW_WORDS = 55


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }
    WTF_CSRF_ENABLED = False
