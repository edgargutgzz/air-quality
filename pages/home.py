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

#----------

# Air Quality - Map

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

#----------

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
                        html.Img(src="../assets/logo_datacomun.png", height="34px"),
                        style={"color": "black"}
                    ),
                    align="center", className="g-0"
                ),
                href="/", style={"text-decoration": "none"}
            ),

            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0)

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

    # Air Quality - Map
    dbc.Row(
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Sensores de Purple Air por Volumen de PM2.5", style={"font-weight": "bold"}),
                dbc.CardBody(
                    dcc.Graph(
                        figure=sensors,
                        config={'displaylogo': False},
                        style={"height": "100vh", "width": "100%"},
                        id="mapa-mobile"
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
    )


])

