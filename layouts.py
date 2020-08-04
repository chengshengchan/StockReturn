"""Define the layout of dashboard."""

import csv
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import dash_table
import utils
import constants

def main_page():
    """Define the layout of main page."""
    data = utils.load_data(constants.CSVPATH)
    options = []
    for idx in sorted(list(set(data['Id']))):
        options.append({'label': idx, 'value': idx})

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
            editable=True
        ),
        dcc.Dropdown(id='StockID', options=options, value=options[0]['value']),
        dcc.Graph(id='ShareGraph'),
    ])
