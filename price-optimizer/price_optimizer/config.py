import os
import logging
from pathlib import Path
from dotenv import load_dotenv

_project_root = Path(__file__).parent.parent
load_dotenv(_project_root / '.env')


class Config:
    DB_PATH = os.getenv('BOOK_DATA_DB', '~/.book-data/books.db')
    EXPERIMENTS_PATH = os.getenv('EXPERIMENTS_PATH', '~/.book-data/experiments.json')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    @classmethod
    def get_db_path(cls, override=None):
        raw = override or cls.DB_PATH
        path = Path(raw).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)

    @classmethod
    def get_experiments_path(cls, override=None):
        raw = override or cls.EXPERIMENTS_PATH
        path = Path(raw).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)

    @classmethod
    def setup_logging(cls):
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL.upper(), logging.INFO),
            format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        )

    @classmethod
    def as_dict(cls):
        return {
            'DB_PATH': cls.DB_PATH,
            'EXPERIMENTS_PATH': cls.EXPERIMENTS_PATH,
            'LOG_LEVEL': cls.LOG_LEVEL,
        }
