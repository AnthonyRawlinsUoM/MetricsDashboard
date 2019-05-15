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

external_stylesheets = [
    # Dash CSS
    # 'https://codepen.io/chriddyp/pen/bWLwgP.css',
    # Loading screen CSS
    # 'https://codepen.io/chriddyp/pen/brPBPO.css',
    # Semantic UI
    'https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.4.1/semantic.css',
    '/assets/css/sticky.css'
]

# external JavaScript files
external_scripts = [
    'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.4.1/jquery.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.4.1/semantic.min.js'
]
assets_external_path = 'https://dssh.cloud.bushfirebehaviour.net.au/assets/'

app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets,
                external_scripts=external_scripts,
                assets_external_path=assets_external_path)

app.scripts.config.serve_locally = False
app.title = "DSS Metrics Analysis"
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
                <a class="header item" href="/home" >
                <img class="logo" src="/assets/images/unimelb_logo.png">
                DSS Metrics</a>
                <div class="ui simple dropdown item">
                Metrics <i class="dropdown icon"></i>
                <div class="menu">
                  <a class="item" href="/BioDiversity">BioDiversity</a>
                  <a class="item" href="/Carbon">Carbon</a>
                  <a class="item" href="/Experiential">Experiential</a>
                  <a class="item" href="/Hydrology">Hydrology</a>
                  <a class="item" href="/ImplementationCost">Implementation Cost</a>
                  <a class="item" href="/Infrastructure">Infrastructure</a>
                  <a class="item" href="/PeopleHouses">People &amp; Houses</a>
                  <a class="item" href="/Recreational">Recreational</a>
                  <a class="item" href="/RegionalEconomy">RegionalEconomy</a>
                </div>
              </div>
            </div>
        </div>
        <div class="ui main text container">
            <div class="ui header">
                DSS Metrics Analysis Dashboard
            </div>
            {%app_entry%}
        </div>
        
        <div class="ui inverted vertical footer segment">
            <div class="ui container">
              <div class="ui stackable inverted divided grid">
                <div class="three wide column">
                  <h4 class="ui inverted header">Group 1</h4>
                  <div class="ui inverted link list">
                    <a href="#" class="item">Link One</a>
                    <a href="#" class="item">Link Two</a>
                    <a href="#" class="item">Link Three</a>
                    <a href="#" class="item">Link Four</a>
                  </div>
                </div>
                <div class="three wide column">
                  <h4 class="ui inverted header">Group 2</h4>
                  <div class="ui inverted link list">
                    <a href="#" class="item">Link One</a>
                    <a href="#" class="item">Link Two</a>
                    <a href="#" class="item">Link Three</a>
                    <a href="#" class="item">Link Four</a>
                  </div>
                </div>
                <div class="three wide column">
                  <h4 class="ui inverted header">Group 3</h4>
                  <div class="ui inverted link list">
                    <a href="#" class="item">Link One</a>
                    <a href="#" class="item">Link Two</a>
                    <a href="#" class="item">Link Three</a>
                    <a href="#" class="item">Link Four</a>
                  </div>
                </div>
                <div class="seven wide column">
                  <h4 class="ui inverted header">Footer Header</h4>
                  <p>Extra space for a call to action inside the footer that could help re-engage users.</p>
                </div>
              </div>
              <div class="ui inverted section divider"></div>
              <img src="/assets/images/unimelb_logo.png" class="ui centered small image">
              <div class="ui horizontal inverted small divided link list">
                <a class="item" href="#">Site Map</a>
                <a class="item" href="#">Contact Us</a>
                <a class="item" href="#">Terms and Conditions</a>
                <a class="item" href="#">Privacy Policy</a>
              </div>
            </div>
          </div>
        
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        
        
    </body>
</html>
'''

server = app.server
app.config.suppress_callback_exceptions = True
