"""Define all callback functions."""

from collections import defaultdict
import datetime
import pickle

from dash.dependencies import Input, Output, State
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import twstock

import applications
import constants
import utils

app = applications.app


def accumulate_shares(data, stockid):
    """Accumulate the share based on selected stock index."""
    stock_shares = defaultdict(list)
    for sid, d, s in zip(data['Id'], data['Date'], data['Share']):
        if sid == stockid:
            s = 0 if s == '' else s
            stock_shares[d].append(s)
    dates = []
    accu_shares = []
    total_shares = 0
    for dt, values in stock_shares.items():
        shares = int(np.array(values).astype(np.int32).sum())
        if shares !=0:
            total_shares += shares
            dates.append(dt)
            accu_shares.append(total_shares)
    return dates, accu_shares

def acuumulate_cash_flow(data, stockid):
    paid = defaultdict(list)
    receive = defaultdict(list)
    for sid, d, p, r in zip(data['Id'], data['Date'], data['Paid'], data['Receive']):
        if sid == stockid:
            p = 0 if p == '' else p
            r = 0 if r == '' else r
            paid[d].append(p)
            receive[d].append(r)

    return paid, receive

def load_history(stockid):
    cache_dir = constants.CACHE / str(stockid)
    dates = []
    prices = []
    files = []
    for file_path in cache_dir.glob('*'):
        year, month = np.array(file_path.stem.split('-')).astype(np.int32).tolist()
        files.append(datetime.date(year, month, 1))
    for f in sorted(files):
        file_path = cache_dir / f'{f.year}-{f.month}.pickle'
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
            prices.extend([d['close'] for d in data])
            dates.extend([d['date'].date() for d in data])
    return dates, prices

def load_latest_price(stockid):
    cache_dir = constants.CACHE / str(stockid)
    files = []
    for file_path in cache_dir.glob('*'):
        year, month = np.array(file_path.stem.split('-')).astype(np.int32).tolist()
        files.append(datetime.date(year, month, 1))
    if files == []:
        return 0.0
    date = sorted(files)[-1]
    file_path = cache_dir / f'{date.year}-{date.month}.pickle'
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
        return [d['close'] for d in data][-1]


@app.callback(
    Output('ShareGraph', 'figure'),
    [Input('StockID', 'value')]
)
def update_shares_graph(stockid):
    """Plot the graph to display shares based on selected stock index."""
    data = utils.load_data(constants.CSVPATH)
    dates, accu_shares = accumulate_shares(data, stockid)
    paid, receive = acuumulate_cash_flow(data, stockid)
    all_dates, prices = load_history(stockid)
    shares = np.zeros((len(prices))).astype(np.int32)

    roi_d = []
    roi = np.zeros((len(prices))).astype(np.float32)

    for i, start_date in enumerate(dates[:-1]):
        end_date = dates[i + 1]

        start = all_dates.index(start_date)
        end = all_dates.index(end_date)
        shares[start:end] = accu_shares[i]
    start = all_dates.index(dates[-1])
    shares[start:] = accu_shares[-1]
    #fig = make_subplots(specs=[[{"secondary_y": True}]])

    for i, dt in enumerate(all_dates):
        p, r = 0, 0
        for d, val in paid.items():
            if d > dt:
                break
            p += np.array(val).astype(np.float32).sum()
        for d, val in receive.items():
            if d > dt:
                break
            r += np.array(val).astype(np.float32).sum()
        if p == 0 and r == 0 and len(roi_d) == 0:
            roi[i] = 0
        else:
            roi_d.append(dt)
            roi[i] = (prices[i] * shares[i] + r) / p
    roi = roi[-len(roi_d):]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=all_dates, y=shares, name='shares', marker_color='lightgray'))
    fig.add_trace(go.Scatter(x=all_dates, y=prices, yaxis='y2', name='prices', marker_color='red'))
    fig.add_trace(go.Scatter(x=roi_d, y=roi, name='return', yaxis='y3', marker_color='blue'))
    fig.layout = go.Layout(
        yaxis=dict(
            title='shares',
            range=[0, int(max(accu_shares) * 1.1)],
            side="left",
            position=0.0
        ),
        yaxis2=dict(
            title='price',
            titlefont=dict(color="darkred"),
            tickfont=dict(color="darkred"),
            overlaying="y",
            side="left",
            position=0.06
        ),
        yaxis3=dict(
            title='return',
            titlefont=dict(color='blue'),
            tickfont=dict(color='blue'),
            overlaying="y",
            side="right",
            position=1.0
        ),
        xaxis={'type': 'category'}
    )
    return fig


@app.callback(
    [Output('Table', 'columns'),
     Output('Table', 'data')
    ],
    [Input('StockID', 'value'),
     Input('Table', 'data_timestamp')],
    [State('Table', 'data')]
)
def gen_table(value, data_timestamp, data_rows):
    columns = []
    for key in ['id', 'share', 'receive', 'paid', 'price', 'return']:
        if key == 'return':
            name = 'return (%)'
        else:
            name = key
        columns.append({'name': name, 'id': key})

    rows = {}

    data = utils.load_data(constants.CSVPATH)
    STOCK_ID = sorted(list(set(data['Id'])))

    if data_timestamp is None and data_rows is None:
        for sid in STOCK_ID:
            p = load_latest_price(sid)
            try:
                name = f'{twstock.codes[sid].name} ({sid})'
            except:
                name = sid
            rows[sid] = {'id': name, 'share': 0, 'receive': 0, 'paid': 0, 'price': p, 'return':0}

        for sid, d, s, p, r in zip(data['Id'], data['Date'], data['Share'], data['Paid'], data['Receive']):
            s = 0 if s == '' else s
            rows[sid]['share'] += int(s)
            r = 0 if r == '' else r
            p = 0 if p == '' else p
            rows[sid]['receive'] += int(r)
            rows[sid]['paid'] += int(p)
        table_data = []
        for r, d in rows.items():
            table_data.append(d)
        for row in table_data:
            row['return'] = '{:.2f}'.format(
                (float(row['price'] * row['share'] + row['receive']) / row['paid'] - 1.0) * 100.
            )
        total_paid = 0
        total_receive = 0
        total_value = 0
        for row in table_data:
            total_paid += row['paid']
            total_receive += row['receive']
            total_value += float(row['price']) * row['share']
        roi = total_value + total_receive - total_paid
        row = {'id': 'Total', 'receive': total_receive, 'paid': total_paid, 'return': roi}
        table_data.append(row)
    else:
        total_paid = 0
        total_receive = 0
        total_value = 0
        for row in data_rows[:-1]:
            row['return'] = '{:.2f}'.format(
                ((float(row['price']) * row['share'] + row['receive']) / row['paid'] - 1.0) * 100.
            )
            total_paid += row['paid']
            total_receive += row['receive']
            total_value += float(row['price']) * row['share']
        roi = total_value + total_receive - total_paid
        row = {'id': 'Total', 'receive': total_receive, 'paid': total_paid, 'return': roi}
        table_data = data_rows
        table_data[-1] = {'id': 'Total', 'receive': total_receive, 'paid': total_paid, 'return': roi}

    return columns, table_data
