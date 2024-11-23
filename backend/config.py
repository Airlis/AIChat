import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'defualt-openai-key')
    OPENAI_CONTENT_MODEL = os.getenv('OPENAI_CONTENT_MODEL', 'gpt-4o-2024-11-20')
    OPENAI_QUESTION_MODEL = os.getenv('OPENAI_QUESTION_MODEL', 'gpt-4o-2024-11-20')
    OPENAI_CLASSIFICATION_MODEL = os.getenv('OPENAI_CLASSIFICATION_MODEL', 'gpt-4o-2024-11-20')

    AWS_REGION = os.getenv('AWS_REGION', 'ca-central-1')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    DYNAMODB_SCRAPED_CONTENT_TABLE = os.getenv('DYNAMODB_SCRAPED_CONTENT_TABLE', 'default-table-name')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'PSQL_DATABASE_URL',
        'postgresql://username:password@localhost/your_database_name'
    )
    

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'PSQL_DATABASE_URL',
        'postgresql://username:password@localhost/your_database_name'
    )

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
