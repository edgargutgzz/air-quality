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
from datetime import datetime

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
# Air Quality Map

# Upload data.
sensors = pd.read_csv("assets/sensores.csv")

# Mapbox token
token = os.environ['DB_PWD_TER']

# Map Layout
map_layout = dict(
    mapbox={
        'accesstoken': token,
        'style': "light",
        'zoom': 11,
        'center': dict(lat=25.685387622008598, lon=-100.31385813323436)
    },
    height = 450,
    showlegend=False,
    margin={'l': 0, 'r': 0, 'b': 0, 't': 0},
    modebar=dict(remove=["zoom", "toimage", "pan", "select", "lasso", "zoomin", "zoomout", "autoscale", "reset",
                         "resetscale", "resetview"]),
    hoverlabel_bgcolor="#000000"
)

sensors = px.scatter_mapbox(sensors, lat="lat", lon="lon", custom_data=["nombre", "municipio", "sensor_id"])

sensors.update_traces(
    marker=dict(size=12),  # Increase size as needed
    opacity = .8,
    hovertemplate="<br>".join([
        "%{customdata[0]}",
        "Municipio: %{customdata[1]}",
        "Sensor ID: %{customdata[2]}"
    ])
)

sensors.update_layout(map_layout)

#----------
# Air Quality Table
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
# Air Quality Scatter Plot

# Create a copy of the DataFrame for the scatter plot and sort it by 'municipio'
scatter_dataframe = dataframe.copy()
scatter_dataframe.sort_values(by='municipio', ascending=False, inplace=True)

# Define the assign_color_label function
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

# Assign color labels
scatter_dataframe['Calidad del Aire'] = scatter_dataframe['avg_pm25'].apply(assign_color_label)

# Colors with transparency
color_map = {
    "Buena": "rgba(105,214,179,0.8)",    # green
    "Aceptable": "rgba(238,238,0,0.8)",    # yellow
    "Mala": "rgba(255,126,0,0.8)",    # orange
    "Muy Mala": "rgba(255,2,0,0.8)",    # red
    "Extremadamente Mala": "rgba(91,50,176,0.8)",    # purple
}

scatter_dataframe['sensor_count'] = range(1, len(scatter_dataframe) + 1)
scatter_dataframe['municipio_order'] = scatter_dataframe.groupby('municipio').ngroup()

scatter_dataframe.rename(columns={"avg_pm25": "PM2.5", "municipio": "Municipio"}, inplace=True)

scatter_fig = px.scatter(
    scatter_dataframe,
    x="PM2.5",
    y='Municipio',
    title=None,
    hover_name='nombre',
    custom_data=["nombre", "Calidad del Aire"],  # Add 'nombre' to the custom data
)

scatter_fig.update_traces(
    hovertemplate="<br>".join([
        "<b>%{customdata[0]}</b>",  # Display the sensor name in bold
        "Calidad del Aire = %{customdata[1]}",  # Adjust the index for 'Calidad del Aire' to 1
        "PM2.5 = %{x:.0f}",  # Use .0f to round to nearest whole number
        "Municipio = %{y}",
    ]),
    hoverinfo="none",  # Prevent Plotly from automatically adding data to the hover labels
    #opacity = .9,
    marker=dict(
        size=15,  # Adjust the size here
        line=dict(
            width=1,  # Modify the width of the border here
            color='white'  # Set the color of the border
        ),
        color=scatter_dataframe['Calidad del Aire'].map(color_map)  # Use the color map here
    )
)

scatter_fig.update_layout(
    xaxis_title=None,
    yaxis_title=None,
    showlegend=False,
)

scatter_fig.update_layout(
    height=450, 
    margin=dict(l=20, r=20, t=20, b=20),
    plot_bgcolor='rgb(232,242,255)',  # light grey
    yaxis=dict(  
        tickmode="array",
        tickvals=scatter_dataframe["Municipio"],
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
layout = html.Div([

    # Filtros y Visualizaciones - Desktop
    dbc.Row([

        # Sidebar   
        dbc.Col([
            # Data Comun
            dbc.Row(
                dbc.Col(
                    html.A(
                        dbc.Row(
                            dbc.Col(
                                html.Img(src="../assets/logo_datacomun.png", height="34px"),
                                style={"color": "black"}
                            )
                        ),
                        href="/", 
                        style={"text-decoration": "none"}
                    )
                ),
                className = "pb-4 px-3 pt-2"
            ),
            # Fuente de datos
            dbc.Row(
                dbc.Col([
                    html.P("🏭 Fuente de datos", style={"font-weight": "bold"}),
                    dcc.Dropdown(
                        id='municipio-dropdown-d',
                        options=[
                            {"label": "Sensores de Purple Air", "value": "Sensores de Purple Air"},
                            {"label": "Sensores del Estado de Nuevo León", "value": "Sensores del Estado de Nuevo León", "disabled": True}
                        ],
                        value='Sensores de Purple Air',
                        clearable=False,
                        style={'backgroundColor': '#F8F9FA'}
                    )
                ]),
                className = "pt-4 px-3"
            ),
            # Indicador
            dbc.Row(
                dbc.Col([
                    html.P("📊 Indicador", style={"font-weight": "bold"}),
                    dcc.Dropdown(
                        id='mes-dropdown-d',
                        options=[
                            {"label": "PM2.5", "value": "PM2.5"},
                            {"label": "PM10.0", "value": "PM10.0", "disabled": True},
                            {"label": "Temperatura", "value": "Temperatura", "disabled": True}
                        ],
                        value='PM2.5',
                        clearable=False,
                        style={'backgroundColor': '#F8F9FA'}
                    )
                ]),
                className = "pt-4 px-3"
            ),
            # Municipio
            dbc.Row(
                dbc.Col([
                    html.P("📍 Municipio", style={"font-weight": "bold"}),
                    dcc.Dropdown(
                        id='mes-dropdown-d',
                        options=[
                            {"label": "Todos", "value": "Todos"},
                            {"label": "Abasolo", "value": "Abasolo", "disabled": True},
                            {"label": "El Carmen", "value": "El Carmen", "disabled": True},
                            {"label": "Escobedo", "value": "Escobedo", "disabled": True},
                            {"label": "García", "value": "García", "disabled": True},
                            {"label": "Juárez", "value": "Juárez", "disabled": True},
                            {"label": "Allende", "value": "Allende", "disabled": True},
                            {"label": "Apodaca", "value": "Apodaca", "disabled": True},
                            {"label": "Cadereyta Jimenez", "value": "Cadereyta Jimenez", "disabled": True},
                            {"label": "Cienega de Flores", "value": "Cienega de Flores", "disabled": True},
                            {"label": "Guadalupe", "value": "Guadalupe", "disabled": True},
                            {"label": "Monterrey", "value": "Monterrey", "disabled": True},
                            {"label": "Salinas Victoria", "value": "Salinas Victoria", "disabled": True},
                            {"label": "San Nicolás de los Garza", "value": "San Nicolás de los Garza", "disabled": True},
                            {"label": "San Pedro Garza García", "value": "San Pedro Garza García", "disabled": True},
                            {"label": "Santa Catarina", "value": "Santa Catarina", "disabled": True},
                            {"label": "Santiago", "value": "Santiago", "disabled": True}
                        ],
                        value='Todos',
                        clearable=False,
                        style={'backgroundColor': '#F8F9FA'}
                    )
                ]),
                className = "pt-4 px-3"
            ),
            # Fecha
            dbc.Row(
                dbc.Col([
                    html.P("📅 Fecha", style={"font-weight": "bold"}),
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        start_date_placeholder_text="Start Period",
                        end_date_placeholder_text="End Period",
                        start_date=datetime(2023, 5, 8),
                        end_date=datetime(2023, 5, 30),
                        min_date_allowed=datetime(2023, 5, 30),
                        max_date_allowed=datetime(2023, 5, 8),
                        display_format="DD/MM/YYYY"
                    )
                ]),
                className = "pt-4 px-3"
            ),
            dbc.Row(
                dbc.Col(
                    html.Hr()
                ),
                className = "px-3 mt-auto"
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Button(
                        "Conoce más",
                        color = "secondary",
                        outline = True
                    )
                ),
                className = "px-3 pb-4 pt-2"
            )
        ],
        className='pt-4 d-flex flex-column',
        width=3,
        style = {
            "position": "fixed", 
            "top": 0,
            "height": "100vh",
            "border-right": "1px solid #DBDBDB",
        }
        ),

        # Visualizaciones
        dbc.Col([

            # Texto introductorio
            dbc.Row(
                dbc.Col(
                    dbc.Alert(
                        "Utiliza los filtros de la izquierda para explorar los datos de calidad del aire en Monterrey.",
                        color = "primary",
                        dismissable = True,
                        duration = 10000
                    )
                ),
                className = "pt-4"
            ),
            # Mapa
            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Sensores de Purple Air", style={"font-weight": "bold"}),
                        dbc.CardBody(
                            dcc.Graph(
                                figure=sensors,
                                config={'displaylogo': False},
                                id="mapa-mobile"
                            )
                        )
                    ])
                ),
                className = "pt-2 pb-5"
            ),
            # Tabla
            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Sensores de Purple Air", style={"font-weight": "bold"}),
                        dbc.CardBody(
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
                    ])
                ),
                className = "pb-5"
            ),
            # Scatter Plot
            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Sensores de Purple Air por Volumen Promedio de PM2.5", style={"font-weight": "bold"}),
                        dbc.CardBody(
                            dcc.Graph(
                                id='scatter_plot',
                                figure=scatter_fig,
                                config={'displayModeBar': False}
                            )
                        )            
                    ])
                ),
                className = "pb-5"
            )
        ],
        width=9,
        className = "px-5",
        style = {
            "margin-left": "25%"
        }
        )

    ],
    className="m-0"
    )

])

