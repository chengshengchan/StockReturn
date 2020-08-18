"""The index page."""

import dash_core_components as dcc
import dash_html_components as html
import dash_table
import twstock

import applications
from callbacks import *
import constants
import layouts
import utils


import socket

def select_stock():
    """Return a dropdown to select the stock id."""
    data = utils.load_data(constants.CSVPATH)
    options = []
    for idx in sorted(list(set(data['Id']))):
        try:
            name = f'{twstock.codes[idx].name} ({idx})'
        except:
            name = idx
        options.append({'label': name, 'value': idx})
    return dcc.Dropdown(id='StockID', options=options, value=options[0]['value'])



def main_page():
    """Define the layout of main page."""

    return html.Div([
        html.H2(children='Return of Investement on TW Stock.'),
        dcc.DatePickerRange(
            id='my-date-picker-range',
            #min_date_allowed=min(data['Date']),
            #max_date_allowed=max(data['Date']),
            #initial_visible_month=max(data['Date']),
            #end_date=max(data['Date'])
        ),
        dash_table.DataTable(
            id='Table',
            editable=True,
            style_data_conditional=[
                {
                    'if': {
                        'filter_query': '{return} > 0',
                        'column_id': 'return'
                    },
                    'color': 'red'
                },
                {
                    'if': {
                        'filter_query': '{return} <= 0',
                        'column_id': 'return'
                    },
                    'color': 'green'
                }

            ]
        ),
        select_stock(),
        dcc.Graph(id='ShareGraph'),
    ])

app = applications.app
app.layout = main_page

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8888, debug=True)
