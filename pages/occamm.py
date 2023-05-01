import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
import plotly.express as px
import os
import pandas as pd

dash.register_page(__name__, path="/occamm")

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

sensors = px.scatter_mapbox(sensors, lat="lat", lon="lon", custom_data=["nombre", "municipio", "sensor_id"])

sensors.update_traces(hovertemplate="<br>".join([
    "%{customdata[0]}",
    "Municipio: %{customdata[1]}",
    "Sensor ID: %{customdata[2]}"
    ])
)

sensors.update_layout(map_layout)

# Map's title
info_icon = html.I(className = "fas fa-info-circle", style = dict(display = "inline-block"))

btn_text = html.Div("OCCAMM", style = dict(paddingRight = "1vw", display = "inline-block"))

map_title = html.Span([btn_text, info_icon])

# Map switches - Mobile
switches_mobile = html.Div([
    dbc.Label(
        "🔍 Explora el mapa "
    ),
    dbc.Checklist(
        options=[
            {"label": "🔵 Sensores de Purple Air con Recolección de Datos Activo", "value": 1}
        ],
        value=[1],
        id="switches-input-mobile",
        switch=True,
        inline = True,
        input_checked_style = {"backgroundColor": "#5C6369", "borderColor": "#5C6369"}
    )
])

# Map switches - Desktop
switches_desktop = html.Div([
    dbc.Label(
        "🔍 Explora el mapa "
    ),
    dbc.Checklist(
        options=[
            {"label": "🔵 Sensores de Purple Air con Recolección de Datos Activo", "value": 1}
        ],
        value=[1],
        id="switches-input-desktop",
        switch=True,
        inline = True,
        input_checked_style = {"backgroundColor": "#5C6369", "borderColor": "#5C6369"}
    )
])


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
                    dbc.NavItem(dbc.NavLink("Conoce más", href="/conocemas")),
                    dbc.NavItem(dbc.NavLink("Datos", href="/datos")),
                    dbc.NavItem(
                        dbc.DropdownMenu([
                            dbc.DropdownMenuItem("OCCAMM", href="/occamm"),
                            dbc.DropdownMenuItem("Purple Air", href="/purple_air")
                        ],
                            label="Mapa",
                            toggle_style={
                                "background": "#F8F9FA",
                                "color": "#7A7B7B",
                                "border": "none"
                            },
                            nav=True
                        )
                    )
                ], className="ms-auto", navbar=True),
                id="navbar-collapse", navbar=True,
            ),

        ]),
        color="light", dark=False
    ),

    # Mapa - Mobile
    dbc.Row(

        # Sidebar and Map
        dbc.Col([
            # Map
            dcc.Graph(
                figure={},
                config={'displaylogo': False},
                style={"height": "100vh", "width": "100%"},
                id="mapa-mobile"
            ),
            # Title
            dbc.Button(
                map_title,
                id="open-offcanvas",
                n_clicks=0,
                style={"position": "absolute", "top": "5%", "left": "50%",
                       "transform": "translate(-50%, -50%)"},
                outline=False,
                color="secondary",
                class_name="mx-auto"
            ),
            # Sidebar
            dbc.Offcanvas(
                [
                    html.P(
                        "El mapa del Observatorio del Aire de Monterrey está desarrollado como una herramienta para " 
                        "promover información sobre el estado, causas y efectos de la contaminación del Aire en la "
                        "Zona Metropolitana.",
                    ),
                    html.P(
                        html.Hr(),
                        className="px-4"
                    ),
                    html.Div(
                        switches_mobile,
                        id="radioitems-checklist-output"
                    )
                ],
                id="offcanvas",
                title="OCCAMM",
                is_open=False,
                placement="start"
            )
        ],
            style={"position": "relative"},
            className="d-lg-none"
        )
    ),

    # Mapa - Desktop
    dbc.Row([

        # Sidebar
        dbc.Col([
            html.H4("OCCAMM", className="px-4 pt-3"),
            html.P(
                "El mapa del Observatorio del Aire de Monterrey está desarrollado como una herramienta para promover "
                "información sobre el estado, causas y efectos de la contaminación del Aire en la Zona Metropolitana.",
                className="px-4"
            ),
            html.P(
                html.Hr(),
                className="px-4"
            ),
            html.Div(
                switches_desktop,
                id="radioitems-checklist-output",
                className="px-4"
            )
        ],
            lg=3,
            xl=3,
            className="d-none d-lg-block"
        ),

        # Map
        dbc.Col([
            dcc.Graph(
                figure={},
                config={'displaylogo': False},
                style={"height": "100vh", "width": "100%"},
                id="mapa-desktop"
            ),
        ],
            lg=9,
            xl=9,
            className="d-none d-lg-block"
        )

    ])



])

