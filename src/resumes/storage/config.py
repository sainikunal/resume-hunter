import psycopg2
from typing import NamedTuple

import os
from dotenv import load_dotenv

# Load environment variables
loaded_env = load_dotenv(".env")
if not loaded_env:
    exit("The .env file was not found!")

# Define settings structure
class Settings(NamedTuple):
    database: str
    user: str
    password: str
    host: str
    port: str

# Initialize settings from environment variables
settings = Settings(
    database=os.getenv("RESUME_POSTGRES_DB"),
    user=os.getenv("RESUME_POSTGRES_USER"),
    password=os.getenv("RESUME_POSTGRES_PASSWORD"),
    host=os.getenv("RESUME_POSTGRES_HOST"),
    port=os.getenv("RESUME_POSTGRES_PORT"),
)

# Table names
TABLE_CITY = "city"
TABLE_RESUME = "resume"
TABLE_EDUCATION = "education"
TABLE_ADDITIONAL = "additional"
TABLE_POSITION = "position"
TABLE_EXPERIENCE_STEP = "experience_step"

# Connect to the database
def connect() -> psycopg2.extensions.connection:
    try:
        db = psycopg2.connect(
            database=settings.database,
            user=settings.user,
            password=settings.password,
            host=settings.host,
            port=int(settings.port),
        )
        return db
    except BaseException as err:
        exit(f"Failed to connect to the database: {err}")