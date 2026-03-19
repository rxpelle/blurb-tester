import os
import logging
from pathlib import Path
from dotenv import load_dotenv

_project_root = Path(__file__).parent.parent
load_dotenv(_project_root / '.env')


class Config:
    DB_PATH = os.getenv('BOOK_DATA_DB', '~/.book-data/books.db')
    KU_PAGE_RATE = float(os.getenv('KU_PAGE_RATE', '0.0045'))
    READ_WINDOW_DAYS = int(os.getenv('READ_WINDOW_DAYS', '60'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    @classmethod
    def get_db_path(cls, override=None):
        raw = override or cls.DB_PATH
        path = Path(raw).expanduser().resolve()
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
            'KU_PAGE_RATE': cls.KU_PAGE_RATE,
            'READ_WINDOW_DAYS': cls.READ_WINDOW_DAYS,
            'LOG_LEVEL': cls.LOG_LEVEL,
        }
