import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

DATABASE_URL = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
    dbuser=os.getenv('AZURE_POSTGRESQL_USER'),
    dbpass=os.getenv('AZURE_POSTGRESQL_PASSWORD'),
    dbhost=os.getenv('AZURE_POSTGRESQL_HOST'),
    dbname=os.getenv('AZURE_POSTGRESQL_NAME')
)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or "sqlite:///" + os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "app.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
