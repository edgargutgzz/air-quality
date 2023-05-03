import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
import plotly.express as px
import os
import pandas as pd

dash.register_page(__name__, path="/purpleair")

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
                            dbc.DropdownMenuItem("Purple Air", href="/purpleair")
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

    # Purple Air
    dbc. Row(
        dbc.Col(
            html.Iframe(
                src="https://map.purpleair.com/1/mAQI/a10/p604800/cC0#8.5/25.5545/-100.2867",
                style={"width": "100%", "height": "100vh", "border": "0"}
            )
        )
    )

])

