# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import sqlalchemy
import geoalchemy2
import xarray as xr
import pandas as pd
import numpy as np

import plotly.plotly as py
import plotly.graph_objs as go
from datetime import datetime

# from metrics import metrics

import yaml
import json

import flask

ph_path = '/nfs/pyromancer/SharedData/regsimout/centralhigh22nov2018/PeopleHouses/'


df2 = pd.read_csv(
    'https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')


assets_external_path = 'https://dssh.cloud.bushfirebehaviour.net.au/'

external_stylesheets = [
    # Dash CSS
    # 'https://codepen.io/chriddyp/pen/bWLwgP.css',
    # Loading screen CSS
    # 'https://codepen.io/chriddyp/pen/brPBPO.css',
    # Semantic UI
    'https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.4.1/semantic.css'
]

# external JavaScript files
external_scripts = [
    'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.4.1/jquery.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.4.1/semantic.min.js'
]


# For Testing purposes only...
df = pd.DataFrame(np.random.rand(100, 6) * 100, columns=[
                  'PB 0', 'PB 1', 'PB 2', 'PB 3', 'PB 5', 'PB 10'])


data = []

pb_colours = ["#fde725",
              "#90d743",
              "#35b779",
              "#21918c",
              "#31688e",
              "#443983",
              "#440154"
              ]
colour_index = 0
for col in df.columns:
    data.append(
        go.Box(
            y=df[col],
            name=col,
            marker=dict(color=pb_colours[colour_index]),
            boxmean=True,
            showlegend=True
        )
    )
    colour_index = colour_index + 1

app = dash.Dash(__name__,
                external_scripts=external_scripts,
                external_stylesheets=external_stylesheets,
                assets_external_path=assets_external_path)

app.scripts.config.serve_locally = False

app.title = "Test"

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        <div class="ui container">
            <div class="ui fixed borderless inverted main menu">
                <a href="/home" class="item">Home</a>
                <a href="/metrics" class="item">Metrics</a>
                <a href="/plots" class="item">Plots</a>
            </div>
        </div>
        <div class="ui main text container">
            <div class="ui header">
                DSS Metrics Analysis Dashboard'
            </div>
            
            {%app_entry%}
        </div>
        <div class="ui inverted vertical footer segment">
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        </div>
    </body>
</html>
'''

app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

plot_layout = html.Div(
    id='page-content',
    children=[])

metric_layout = html.Div(
    id='page-content',
    children=[])

index_page = html.Div(
    id='page-content',
    children=[
        html.Div(
            className='ui text container',
            children=[
                html.Div(
                    children=[
                        html.Label('Seasons:'),
                        dcc.RadioItems(
                            id='season',
                            options=[
                                {'label': 'Prescribed Burning',
                                 'value': 'burn'},
                                {'label': 'Wildfires',
                                 'value': 'wild'}
                            ],
                            value='wild'
                        ),
                        html.Label(
                            'Levels of Prescribed Burning:'
                        ),
                        dcc.Dropdown(
                            id='pb',
                            options=[
                                {'label': 'PB 0', 'value': '0'},
                                {'label': 'PB 1', 'value': '1'},
                                {'label': 'PB 2', 'value': '2'},
                                {'label': 'PB 3', 'value': '3'},
                                {'label': 'PB 5', 'value': '5'},
                                {'label': 'PB 10', 'value': '10'}
                            ],
                            multi=True,
                            value="0"
                        ),
                        html.Label('Batches'),
                        dcc.RangeSlider(
                            marks={
                                10 * i: '{}'.format(10 * i) for i in range(1, 10)},
                            count=1,
                            min=1,
                            max=100,
                            step=1,
                            allowCross=False,
                            value=[1, 100]
                        ),
                        html.Label('Time'),
                        dcc.RangeSlider(
                            marks={
                                10 * i: '{}'.format(10 * i) for i in range(1, 5)},
                            count=1,
                            min=1,
                            max=50,
                            step=1,
                            allowCross=False,
                            value=[1, 50]
                        )
                    ])
            ]
        ),
        html.Div(
            className='ui text container',
            children=[
                dcc.Graph(
                    id='example-graph',
                    figure={
                        'data': data,
                        'layout': {
                            'title': 'Sample'
                        }
                    }
                )
            ]
        ),
        html.Div(
            className='ui text container',
            children=[
                html.Div(id='console')
            ]
        )
    ])
# ], style={'columnCount': 2})


# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/plots':
        return plot_layout
    elif pathname == '/metrics':
        return metric_layout
    else:
        return index_page
    # You could also return a 404 "URL not found" page here


@app.callback(
    Output(component_id='console', component_property='children'),
    [Input(component_id='pb', component_property='value')]
)
def update_output_div(input_value):
    return 'You\'ve entered "{}"'.format(input_value)


def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])]

        + # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=False, port=8050)
