from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

from setting import DB_FILE

engine = create_engine(f"sqlite://{DB_FILE}", echo=False)

Base = declarative_base()
