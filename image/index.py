import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps.BioDiversity import BioDiversity
from apps.Carbon import Carbon
from apps.Experiential import Experiential
from apps.Hydrology import Hydrology
from apps.ImplementationCost import ImplementationCost
from apps.Infrastructure import Infrastructure
from apps.PeopleHouses import PeopleHouses
from apps.Recreational import Recreational
from apps.RegionalEconomy import RegionalEconomy


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Label('Seasons:'),
    dcc.RadioItems(
        id='crossfilter-season',
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
        id='crossfilter-pb-level',
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
        id='crossfilter-batch-range',
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
        id='crossfilter-time-slider',
        marks={
            10 * i: '{}'.format(10 * i) for i in range(1, 5)},
        count=1,
        min=1,
        max=50,
        step=1,
        allowCross=False,
        value=[1, 50]
    ),
    html.Div(id='page-content')
])

index_page = html.Div([
    html.P('Index')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname'),
               Input('crossfilter-time-slider', 'value'),
               Input('crossfilter-pb-level', 'value'),
               Input('crossfilter-batch-range', 'value'),
               Input('crossfilter-season', 'value')])
def display_page(pathname, time_range, pb_level, batches, season):
    if pathname == '/home' or pathname == '/':
        return index_page
    elif pathname == '/BioDiversity':
        return BioDiversity.layout
    elif pathname == '/Carbon':
        return Carbon.layout
    elif pathname == '/Experiential':
        return Experiential.layout
    elif pathname == '/Hydrology':
        return Hydrology.layout
    elif pathname == '/ImplementationCost':
        return ImplementationCost.layout
    elif pathname == '/Infrastructure':
        return Infrastructure.layout
    elif pathname == '/PeopleHouses':
        print(season)
        return PeopleHouses.layout
    elif pathname == '/Recreational':
        return Recreational.layout
    elif pathname == '/RegionalEconomy':
        return RegionalEconomy.layout
    else:
        return html.Div(
            children=[
                html.Div(
                    className='ui header',
                    children=['404']
                ),
                html.P('File not found.')
            ])


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=False, port=8050)
