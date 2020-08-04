"""Define all callback functions."""

from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

import applications
import constants
import utils

app = applications.app


@app.callback(
    Output('ShareGraph', 'figure'),
    [Input('StockID', 'value')]
)
def share_accumulate(stockid):
    """Accumulate the share based on selected stock index."""
    date = []
    acc_share = []
    share = 0
    data = utils.load_data(constants.CSVPATH)
    for sid, d, s in zip(data['Id'], data['Date'], data['Share']):
        s = 0 if s == '' else s
        if sid == stockid:
            date.append(d)
            share += int(s)
            acc_share.append(share)
    return {
        'data': [
            go.Scatter(x=date, y=acc_share)
        ],
        'layout': go.Layout(
            yaxis={'range': [0, int(max(acc_share) * 1.1)]}
        )
    }


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
        columns.append({'name': key, 'id': key})

    rows = {}
    if data_timestamp is None and data_rows is None:
        data = utils.load_data(constants.CSVPATH)
        STOCK_ID = sorted(list(set(data['Id'])))

        for sid in STOCK_ID:
            rows[sid] = {'id': sid, 'share': 0, 'receive': 0, 'paid': 0, 'price': 0, 'return':0}

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
            row['return'] = float(row['price'] * row['share'] + row['receive']) / row['paid']
    else:
        for row in data_rows:
            row['return'] = float(int(row['price']) * row['share'] + row['receive']) / row['paid']
        table_data = data_rows
    return columns, table_data
