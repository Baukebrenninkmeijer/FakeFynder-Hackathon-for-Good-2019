import configparser
from sqlalchemy import create_engine
import pandas as pd
import logging

config = configparser.ConfigParser()
config.read('config.ini')

logger = logging.getLogger(__name__)


class DatabaseIO:
    def __init__(self):
        db_config = config['RDS']
        url = db_config['url']
        db = db_config['db']
        username = db_config['username']
        password = db_config['password']
        self.engine = create_engine(
            f"mysql+pymysql://{username}:{password}@{url}/{db}")

    def write_data(self, df, table):
        logger.info(f'Writing to {table}...')
        copy = df.copy()
        copy.to_sql(table, self.engine, if_exists='replace', chunksize=1000, index=False)
        logger.info('Done.')

    def read_data(self, table, parse_dates=None):
        logger.info(f'Reading data from {table}...')
        res = pd.read_sql(table, self.engine, parse_dates=parse_dates)
        logger.info('Done.')
        return res

    def read_history(self):
        return self.read_data('history')

    def write_history(self, df):
        return self.write_data(df, 'history')
