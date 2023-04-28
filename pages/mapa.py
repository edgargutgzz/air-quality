import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
import plotly.express as px
import os
import pandas as pd

dash.register_page(__name__, path="/mapa")

# Map
# Upload data.
sensors = pd.read_csv("assets/sensores.csv")

# Mapbox token
token = os.environ['DB_PWD_TER']

# Map Layout
map_layout = dict(
    mapbox={
        'accesstoken': token,
        'style': "light",
        'zoom': 12,
        'center': dict(lat=25.65409262897884, lon=-100.37682059704264)
    },
    showlegend=False,
    margin={'l': 0, 'r': 0, 'b': 0, 't': 0},
    modebar=dict(remove=["zoom", "toimage", "pan", "select", "lasso", "zoomin", "zoomout", "autoscale", "reset",
                         "resetscale", "resetview"]),
    hoverlabel_bgcolor="#000000"
)

sensors = px.scatter_mapbox(sensors, lat="lat", lon="lon", custom_data=["name", "sensor_index", "municipio"])

sensors.update_traces(hovertemplate="<br>".join([
    "Name: %{customdata[0]}",
    "Sensor Index: %{customdata[1]}",
    "Municipio: %{customdata[2]}"
    ])
)

sensors.update_layout(map_layout)

# Page layout
layout = html.Div([

    # Navbar - Mobile and Desktop
    dbc.Navbar(
        dbc.Container([

            html.A(
                dbc.Row(
                    dbc.Col(
                        html.Img(src="../assets/logo_occamm.png", height="34px"),
                        style={"color": "black"}
                    ),
                    align="center", className="g-0"
                ),
                href="/", style={"text-decoration": "none"}
            ),

            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),

            dbc.Collapse(
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Mapa", href="/mapa")),
                    dbc.NavItem(dbc.NavLink("Datos", href="/datos")),
                    dbc.NavItem(dbc.NavLink("Conoce más", href="/conocemas"))
                ], className="ms-auto", navbar=True),
                id="navbar-collapse", navbar=True,
            ),

        ]),
        color="light", dark=False
    ),

    # Mapa - Mobile y Desktop
    dbc.Row(
        dcc.Graph(
            figure=sensors,
            config={'displaylogo': False},
            style={"height": "100vh", "width": "100%"},
        )
    )

])

