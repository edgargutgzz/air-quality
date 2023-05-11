import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
import dash_ag_grid as dag
import pandas as pd
import os
import psycopg2
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_table

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
)
SELECT sensor_id, nombre, municipio, ROUND(AVG(pm25)) as avg_pm25
FROM numbered_rows
WHERE row_num > 714
GROUP BY sensor_id, nombre, municipio
ORDER BY MIN(date);
"""

dataframe = pd.read_sql(query, conn)
dataframe.sort_values(by='avg_pm25', ascending=False, inplace=True) 

# Close the connection
conn.close()

#----------

# Air Quality - Table
max_value = dataframe['avg_pm25'].max()

columnDefs = [
    {"headerName": "ID", "field": "sensor_id", "flex": 1},
    {"headerName": "Sensor", "field": "nombre", "flex": 3},
    {"headerName": "Municipio", "field": "municipio", "flex": 2},
    {"headerName": "PM2.5", "field": "avg_pm25", "flex": 2},
    {"headerName": "Calidad del Aire", "field": "color_label", "flex": 2}
]

def assign_color_label(value):
    if value <= 25:
        return "Buena"
    elif 26 <= value <= 45:
        return "Aceptable"
    elif 46 <= value <= 79:
        return "Mala"
    elif 80 <= value <= 147:
        return "Muy Mala"
    else:
        return "Extremadamente Mala"

# Assign 'color_label' to the original dataframe
dataframe['color_label'] = dataframe['avg_pm25'].apply(assign_color_label)


# Air Quality - Scatter Plot

# Create a copy of the DataFrame for the scatter plot and sort it by 'municipio'
scatter_dataframe = dataframe.copy()
scatter_dataframe.sort_values(by='municipio', ascending=False, inplace=True)

scatter_dataframe['color_label'] = scatter_dataframe['avg_pm25'].apply(assign_color_label)
scatter_dataframe['sensor_count'] = range(1, len(scatter_dataframe) + 1)
scatter_dataframe['municipio_order'] = scatter_dataframe.groupby('municipio').ngroup()

# Update the column names
scatter_dataframe.rename(columns={"color_label": "Calidad del Aire", "avg_pm25": "PM2.5", "municipio": "Municipio"}, inplace=True)


scatter_fig = px.scatter(
    scatter_dataframe,
    x="PM2.5",
    y='Municipio',
    color="Calidad del Aire",
    color_discrete_sequence=["#00FF00", "#0000FF", "#FFFF00", "#FFA500", "#FF0000"],
    title=None,
    hover_name='nombre'
)

scatter_fig.update_traces(
    marker=dict(
        line=dict(
            width=1,  # Modify the width of the border here
            color='grey'  # Set the color of the border
        )
    )
)


scatter_fig.update_layout(
    xaxis_title=None,
    yaxis_title=None,
    showlegend=False,
)

scatter_fig.update_layout(
    height=600, 
    margin=dict(l=20, r=20, t=20, b=20),
    yaxis=dict(  
        tickmode="array",
        tickvals=scatter_dataframe["Municipio"],
        ticktext=["   " + label + "   " for label in scatter_dataframe["Municipio"]],
        tickfont=dict(size=14),
        tickangle=0,
        ticklen=10,
        tickcolor='white'
    ),
    xaxis=dict(  
        tickmode="auto",
        tickfont=dict(size=14),
        tickangle=0,
        ticklen=10,
        tickcolor='white',
        ticklabelmode="period",
        ticklabelposition="outside",
        ticksuffix="   ",
        tickvals=scatter_dataframe["PM2.5"],
        ticktext=["   " + str(label) + "   " for label in scatter_dataframe["PM2.5"]],
        dtick=1 # add this dtick value to adjust tick spacing
    )
)

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
                    dbc.NavItem(
                        dbc.DropdownMenu([
                            dbc.DropdownMenuItem("OCCAMM", href="/occamm"),
                            dbc.DropdownMenuItem("Purple Air", href="/purpleair")
                        ],
                            label="Mapas",
                            toggle_style={
                                "background": "#F8F9FA",
                                "color": "#7A7B7B",
                                "border": "none"
                            },
                            nav=True
                        )
                    ),
                    dbc.NavItem(dbc.NavLink("Conoce más", href="/conocemas")),
                    dbc.NavItem(dbc.NavLink("Datos", href="/datos"))
                ], className="ms-auto", navbar=True),
                id="navbar-collapse", navbar=True,
            ),

        ]),
        color="light", dark=False
    ),

    # Air Quality - Table
    dbc.Row(
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Sensores de Purple Air del Área Metropolitana de Monterrey", style={"font-weight": "bold"}),
                dbc.CardBody(
                    html.Div(
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
                    )
                )
            ])
        ),
        className="pt-4"
    ),

    # Air Quality - Scatter Plot
    dbc.Row(
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Sensores de Purple Air por Volumen de PM2.5", style={"font-weight": "bold"}),
                dbc.CardBody(
                    dcc.Graph(
                        id='scatter_plot',
                        figure=scatter_fig,
                        config={'displayModeBar': False}
                    )
                )            
            ])
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

