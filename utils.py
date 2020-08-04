"""Define the helper function."""

import csv
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import dash_table


import datetime

COLUMNS = ['Date', 'Id', 'Share', 'Price', 'Paid', 'Receive', 'Note']


def _is_empty_row(row):
    return set(row) == set([''])


def load_data(csvpath):
    """Load the csv file."""
    data = {key:[] for key in COLUMNS}
    with open(csvpath, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        read_header = False
        for row in reader:
            if not read_header:  # First line is header.
                header = row[0].split(',')
                read_header = True
            else:
                row = row[0].split(',')
                if not _is_empty_row(row):  # Skip Empty Line.
                    for i, num in enumerate(row):
                        data[header[i]].append(num)

    # Translate the date.
    for i, date in enumerate(data['Date']):
        year, month, day = date.split('/')
        data['Date'][i] = datetime.date(int(year), int(month), int(day))

    return data
