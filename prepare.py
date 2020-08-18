"""Based on given csv, prepare the data for dashboard."""

from collections import defaultdict, namedtuple
from dateutil.relativedelta import *
import datetime
import pickle
import time

import twstock

import constants
import utils

PAUSE = 8

def _translate(prices):
    fields = ['date', 'capacity', 'turnover', 'open', 'high', 'low', 'close', 'change', 'transaction']

    new_format = []

    for price in prices:
        _to_dict = {key: getattr(price, key) for key in fields}
        new_format.append(_to_dict)
    return new_format


def extract_date(data):
    """Extract date."""
    stocks = defaultdict(dict)
    for sid, date in zip(data['Id'], data['Date']):
        if sid not in stocks:
            stocks[sid]['start'] = stocks[sid]['end'] = date
        else:
            if date > stocks[sid]['end']:
                stocks[sid]['end'] = date
            if date < stocks[sid]['start']:
                stocks[sid]['start'] = date
    return stocks


if __name__ == '__main__':
    # Create Cache
    constants.CACHE.mkdir(exist_ok=True)

    print('Loading data from csv ...')
    data = utils.load_data(constants.CSVPATH)
    stock_date = extract_date(data)
    for stockid, date_range in stock_date.items():
        if stockid not in twstock.codes:
            time.sleep(PAUSE)
            continue

        query_date = date_range['start']
        today = datetime.date.today()
        stock_dir = constants.CACHE / stockid
        stock_dir.mkdir(exist_ok=True)
        print(f'Getting {stockid} ...')

        stock = twstock.Stock(stockid)
        time.sleep(PAUSE)

        while True:
            if query_date.year > today.year:
                break
            elif query_date.year == today.year and query_date.month == today.month:
                break
            prices_path = stock_dir / f'{query_date.year}-{query_date.month}.pickle'
            if prices_path.is_file():
                print(f'Skip {stockid} ... {query_date.year}-{query_date.month}.')
                query_date += relativedelta(months=1)
                continue
            else:
                prices = stock.fetch(query_date.year, query_date.month)
                prices = _translate(prices)
                with open(prices_path, 'wb') as f:
                    pickle.dump(prices, f)
                print(f'Getting {stockid} ... {query_date.year}-{query_date.month}.')
                time.sleep(PAUSE)
            query_date += relativedelta(months=1)

        prices_path = stock_dir / f'{query_date.year}-{query_date.month}.pickle'
        prices = stock.fetch(query_date.year, query_date.month)
        prices = _translate(prices)
        with open(prices_path, 'wb') as f:
            pickle.dump(prices, f)
        print(f'Getting {stockid} ... {query_date.year}-{query_date.month}.')
        time.sleep(PAUSE*2)
