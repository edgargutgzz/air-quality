import dash
from dash import Dash, html, dcc, Input, Output, State
import plotly_express as px
import os
import pandas as pd
import psycopg2

# Bootstrap
external_stylesheets = [{'href': 'https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css',
     'rel': 'stylesheet', 'integrity': 'sha384-Zenh87qX5JnK2Jl0vWa8Ck2rdkQ2Bzep5IDxbcnCeuOxjzrPF/et3URy9Bv1WTRi',
     'crossorigin': 'anonymous'}]

# Initialize app
app = Dash(__name__, title= "Aire Limpio - OCCAMM",
           use_pages=True,
           external_stylesheets=external_stylesheets,
           )

server = app.server

# Page layout
app.layout = html.Div(
    dash.page_container
)

#----------

# Navbar - Mobile and Desktop
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)(toggle_navbar_collapse)

#----------

if __name__ == '__main__':
    app.run_server(debug=True)