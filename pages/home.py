import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
import dash_ag_grid as dag
import pandas as pd
import os
import psycopg2
from dash.dependencies import Input, Output, State
import plotly.express as px


dash.register_page(__name__, path="/")


# Footer
correo = html.Div(
    "📩 contacto@observatoriodelaire.com",
    style={"font-size": "16px"}
)
telefono = html.Div(
    "📞 81 2314 3857",
    style={"font-size": "16px", "margin-left": "30px"}
)

#----------

# Air Quality data
# Connect to database.
DATABASE_URL = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)

# Execute the query and fetch data
query = """
WITH numbered_rows AS (
    SELECT a.sensor_id, a.pm25, s.nombre, s.municipio, TO_TIMESTAMP(a.date, 'YYYY/MM/DD HH24:MI') as date, ROW_NUMBER() OVER (ORDER BY TO_TIMESTAMP(a.date, 'YYYY/MM/DD HH24:MI')) as row_num
    FROM air_quality a
    JOIN sensors s ON a.sensor_id = s.sensor_id
    WHERE a.pm25 > 0
)
SELECT sensor_id, nombre, municipio, ROUND(AVG(pm25)) as avg_pm25
FROM numbered_rows
WHERE row_num > 714
GROUP BY sensor_id, nombre, municipio
HAVING ROUND(AVG(pm25)) > 0
ORDER BY MIN(date);
"""

dataframe = pd.read_sql(query, conn)

# Close the connection
conn.close()

#----------

# Air Quality Spark Line

max_value = dataframe['avg_pm25'].max()
dataframe['sparkline'] = (dataframe['avg_pm25'] / max_value) * 100

columnDefs = [
    {"headerName": col, "field": col} if col != "sparkline" else {
        "headerName": "Sparkline",
        "field": "sparkline",
        "cellRenderer": (
            'function(params) {'
                'var eDiv = document.createElement("div");'
                'eDiv.style.width = params.value + "%";'
                'eDiv.style.height = "100%";'
                'eDiv.style.backgroundColor = "rgba(58, 71, 80, 0.6)";'
                'return eDiv;'
            '}'
        )
    } for col in dataframe.columns
]


#----------

# Page layout
layout = dbc.Container([

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

    # Air Quality - Table
    dbc.Row(
        dbc.Col(
            html.Div(
                dag.AgGrid(
                    id='my_ag_grid',
                    rowData=dataframe.to_dict('records'),
                    columnDefs=columnDefs,
                    defaultColDef={
                        'editable': False,
                        'sortable': True,
                        'filter': 'agTextColumnFilter',
                        'resizable': True
                    }
                )
            )
        ),
        className="pt-4"
    ),

    # Footer - Mobile
    dbc.Row(
        dbc.Col([
            html.B(
                "Comunícate con nosotros",
                style = {"font-size": "22px"}
            ),
            html.P(
                "📩 contacto@observatoriodelaire.com",
                className = "pt-3",
                style = {"font-size": "16px"}
            ),
            html.P(
                "📞 81 2314 3857",
                className="pt-1",
                style = {"font-size": "16px"}
            ),
            html.P(
                "📍 Blvd. Antonio L. Rodriguez #2100, Colonia Santa María, Monterrey, Nuevo León.",
                className="pt-1",
                style = {"font-size": "16px"}
            ),
            html.Br(),
            html.Div(
                [
                    html.A(
                        href="https://twitter.com/observatoriomty",
                        target="_blank",
                        children=html.Img(
                            src="assets/twitter.png",
                            alt="Twitter",
                            height="34",
                            style={"margin-right": "25px"}
                        ),
                    ),
                    html.A(
                        href="https://www.instagram.com/observatoriomty/",
                        target="_blank",
                        children=html.Img(
                            src="assets/instagram.png",
                            alt="Instagram",
                            height="32",
                            style={"margin-right": "25px"}
                        ),
                    ),
                    html.A(
                        href="https://www.facebook.com/observatoriomty",
                        target="_blank",
                        children=html.Img(
                            src="assets/facebook.png",
                            alt="Facebook",
                            height="30"
                        ),
                    )
                ],
                style={"display": "flex"},
            ),
            html.P(
                "© Observatorio Ciudadano de la Calidad del Aire del Área Metropolitana de Monterrey (2023)",
                className = "pt-4",
                style = {"font-size": "12px"}
            )
        ],
            style={
                "background-color": "#F7F7F7",
            },
            className = "pt-3 pb-1"
        ),
        className="pt-4 d-lg-none"
    ),

    # Footer - Desktop
    dbc.Row(
        dbc.Col([
            html.B(
                "Comunícate con nosotros",
                style={"font-size": "22px"}
            ),
            html.P([
                correo,
                telefono
            ],  style={'display': 'flex', 'justify-content': 'center'}, className = "pt-3"
            ),
            html.P(
                "📍 Blvd. Antonio L. Rodriguez #2100, Colonia Santa María, Monterrey, Nuevo León.",
                className="pt-1",
                style={"font-size": "16px"}
            ),
            html.Br(),
            html.Div(
                [
                    html.A(
                        href="https://twitter.com/observatoriomty",
                        target="_blank",
                        children=html.Img(
                            src="assets/twitter.png",
                            alt="Twitter",
                            height="34",
                            style={"margin-right": "25px"}
                        ),
                    ),
                    html.A(
                        href="https://www.instagram.com/observatoriomty/",
                        target="_blank",
                        children=html.Img(
                            src="assets/instagram.png",
                            alt="Instagram",
                            height="32",
                            style={"margin-right": "25px"}
                        ),
                    ),
                    html.A(
                        href="https://www.facebook.com/observatoriomty",
                        target="_blank",
                        children=html.Img(
                            src="assets/facebook.png",
                            alt="Facebook",
                            height="30"
                        ),
                    )
                ],
                style={"display": "flex", "align-items": "center", "justify-content": "center"},
            ),
            html.P(
                "© Observatorio Ciudadano de la Calidad del Aire del Área Metropolitana de Monterrey (2023)",
                className="pt-4",
                style={"font-size": "12px"}
            )
        ],
            style={
                "background-color": "#F7F7F7",
                "text-align": "center"
            },
            className="pt-3 pb-1"
        ),
        className="pt-4 d-none d-lg-block", style = {"text-align": "center"}
    )


])

