import os
import logging


class Config:
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Scoring weights
    WEIGHT_CONTENT = 0.30
    WEIGHT_STRUCTURED_DATA = 0.25
    WEIGHT_CITATIONS = 0.20
    WEIGHT_LANDING_PAGE = 0.25

    @classmethod
    def setup_logging(cls):
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL.upper(), logging.INFO),
            format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        )

    @classmethod
    def as_dict(cls):
        return {
            'LOG_LEVEL': cls.LOG_LEVEL,
            'WEIGHT_CONTENT': cls.WEIGHT_CONTENT,
            'WEIGHT_STRUCTURED_DATA': cls.WEIGHT_STRUCTURED_DATA,
            'WEIGHT_CITATIONS': cls.WEIGHT_CITATIONS,
            'WEIGHT_LANDING_PAGE': cls.WEIGHT_LANDING_PAGE,
        }
