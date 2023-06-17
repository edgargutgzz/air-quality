import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
import dash_ag_grid as dag
import pandas as pd
import os
import psycopg2
from dash.dependencies import Input, Output, State
import plotly.express as px
from datetime import datetime, date
import plotly.graph_objects as go
import numpy as np
import pytz

#----------
dash.register_page(__name__, path="/")

#----------
# Data

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
# Tabla

columnDefs = [
    {"headerName": "Sensor", "field": "nombre", "flex": 2},
    {"headerName": "Municipio", "field": "municipio", "flex": 2},
    {"headerName": "PM2.5", "field": "avg_pm25", "flex": 1, 'headerTooltip': 'Promedio global de acuerdo a las mediciones realizadas cada hora.'},
    {"headerName": "Calidad del Aire", "field": "color_label", "flex": 2}
]

def assign_color_label(value):
    if value <= 25:
        return "🟢 Buena"
    elif 26 <= value <= 45:
        return "🟡 Aceptable"
    elif 46 <= value <= 79:
        return "🟠 Mala"
    elif 80 <= value <= 147:
        return "🔴 Muy Mala"
    else:
        return "🟣 Extremadamente Mala"

# Assign 'color_label' to the original dataframe
dataframe['color_label'] = dataframe['avg_pm25'].apply(assign_color_label)

#----------
# Scatter Plot

# Create a copy of the DataFrame for the scatter plot and sort it by 'municipio'
scatter_dataframe = dataframe.copy()
scatter_dataframe.sort_values(by='municipio', ascending=False, inplace=True)

# Add Calidad del Aire column
def calidad_aire(value):
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

scatter_dataframe['calidad_aire'] = scatter_dataframe['avg_pm25'].apply(calidad_aire)

# Colors with transparency
color_map = {
    "Buena": "rgba(0,205,0,0.8)",    # green
    "Aceptable": "rgba(255,215,0,0.8)",    # yellow
    "Mala": "rgba(250,135,0,0.8)",    # orange
    "Muy Mala": "rgba(235,0,0,0.8)",    # red
    "Extremadamente Mala": "rgba(188,23,255,0.8)",    # purple
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
    custom_data=["nombre", "calidad_aire"], 
)

scatter_fig.update_traces(
    hovertemplate="<br>".join([
        "Sensor: %{customdata[0]}",
        "Municipio: %{y}",
        "PM2.5: %{x:.0f}",
        "Calidad del Aire: %{customdata[1]}"
    ]),
    hoverinfo="none", 
    marker=dict(
        size=14, 
        line=dict(
            width=1,  
            color='white' 
        ),
        color=scatter_dataframe['calidad_aire'].map(color_map)  
    )
)

scatter_fig.update_layout(
    xaxis_title= "",
    yaxis_title=None,
    showlegend=False,
    height=500, 
    margin=dict(l=20, r=20, t=20, b=0),
    plot_bgcolor='rgb(240,240,239)', 
    yaxis=dict(  
        tickmode="array",
        tickvals=scatter_dataframe["Municipio"],
        ticktext=[str(label) + "   " for label in scatter_dataframe["Municipio"]],
        tickfont=dict(size=14),
        tickangle=0,
        ticklen=10,
        tickcolor='white',
        automargin = True
    ),
    xaxis=dict(  
        tickmode="auto",
        side = "bottom",
        tickfont=dict(size=14),
        tickangle=0,
        ticklen=10,
        tickcolor='white',
        ticklabelmode="period",
        ticklabelposition="outside",
        ticksuffix="   ",
        tickvals=scatter_dataframe["PM2.5"],
        ticktext=["   " + str(label) + "   " for label in scatter_dataframe["PM2.5"]],
        dtick=1 
    ),
    annotations=[
        dict(
            x=0, 
            y=-0.105,  
            showarrow=False,
            text="<b>PM2.5</b>",
            xref="paper",
            yref="paper",
            font=dict(size=14),
        )
    ]
)

#----------
# Mapa

# Upload data.
sensors_df = pd.read_csv("assets/sensores.csv")

# Merge the dataframes on 'sensor_id'
merged_df = sensors_df.merge(scatter_dataframe[['sensor_id', 'PM2.5', 'calidad_aire']], on='sensor_id', how='left')

# Mapbox token
token = os.environ['DB_PWD_TER']

# Create a separate trace for each "Calidad del Aire" category
traces = []
for calidad in merged_df['calidad_aire'].unique():
    df_sub = merged_df[merged_df['calidad_aire'] == calidad]
    traces.append(
        go.Scattermapbox(
            lat=df_sub["lat"],
            lon=df_sub["lon"],
            customdata=np.stack((df_sub["nombre"], df_sub["municipio"], df_sub["PM2.5"]), axis=-1),
            mode='markers',
            marker=dict(
                size=14,
                opacity = .8,
                color=color_map[calidad]
            ),
            hovertemplate="Sensor: %{customdata[0]}<br>Municipio: %{customdata[1]}<br>PM2.5: %{customdata[2]}",
            name=calidad
        )
    )

# Convert your dataframe into the Graph Objects format
sensors_go = go.Figure(data=traces)

# Update layout
sensors_go.update_layout(
    mapbox=dict(
        accesstoken=token,
        style="light",
        zoom=10,
        center=dict(lat=25.685387622008598, lon=-100.31385813323436)
    ),
    height=500,
    margin={'l': 0, 'r': 0, 'b': 0, 't': 0},
    modebar=dict(remove=["zoom", "toimage", "pan", "select", "lasso", "zoomin", "zoomout", "autoscale", "reset", "resetscale", "resetview"]),
    showlegend=True,
    legend=dict(
        x=.98,
        y=.98,
        traceorder="normal",
        font=dict(
            family="sans-serif",
            size=14,
            color="black"
        ),
        xanchor='right', 
        yanchor='top' 
    )
)

#----------
# Calendar date

# Create a timezone object for Mexico City
mexico_tz = pytz.timezone('America/Mexico_City')

# Get the current date in Mexico City timezone
now_mexico = datetime.now(mexico_tz)


#----------
# Page layout
layout = html.Div([

    # Sidebar y Visualizaciones - Desktop
    dbc.Row([

        # Sidebar   
        dbc.Col([
            # Website's logo
            dbc.Row(
                dbc.Col(
                    dbc.Row(
                        dbc.Col(
                            html.Img(src="../assets/logo_datacomun.png", height="24px"),
                            style={"color": "black"}
                        )
                    )
                ),
                className = "pt-2 px-3 pb-4"
            ),
            # Fuente de datos
            dbc.Row(
                dbc.Col([
                    html.Div([
                        html.Img(src="assets/sensor.png", height="22px", style={'margin-right': '6px'}),
                        html.Span(
                            "Fuente de Datos", style = {"font-weight": "bold"}, id="fuente-tooltip-target"
                        ), 
                        dbc.Tooltip(
                            "Solo una fuente de datos disponible por el momento.",
                            target="fuente-tooltip-target",
                            placement = "top"
                        )              
                    ],
                        style={'display': 'flex', 'align-items': 'center'}
                    ),
                    dcc.Dropdown(
                        id='municipio-dropdown-d',
                        options=[
                            {"label": "Sensores de Purple Air", "value": "Sensores de Purple Air"},
                            {"label": "🔒🔜 Sensores del Estado de N.L.", "value": "Sensores del Estado de Nuevo León", "disabled": True}
                        ],
                        value='Sensores de Purple Air',
                        clearable=False,
                        style={'backgroundColor': '#FFFFFF'},
                        className = "pt-3"
                    )
                ]),
                className = "pt-4 px-3"
            ),
            # Indicador
            dbc.Row(
                dbc.Col([
                    html.Div([
                        html.Img(src="assets/indicador.png", height="20px", style={'margin-right': '8px'}),
                        html.Span(
                            "Indicador", style = {"font-weight": "bold"}, id="indicador-tooltip-target"
                        ), 
                        dbc.Tooltip(
                            "Solo un indicador disponible por el momento.",
                            target="indicador-tooltip-target",
                            placement = "top"
                        )              
                    ],
                        style={'display': 'flex', 'align-items': 'center'}
                    ),
                    dcc.Dropdown(
                        id='mes-dropdown-d',
                        options=[
                            {"label": "PM2.5", "value": "PM2.5"},
                            {"label": "🔒🔜 PM10.0", "value": "PM10.0", "disabled": True},
                            {"label": "🔒🔜 Temperatura", "value": "Temperatura", "disabled": True}
                        ],
                        value='PM2.5',
                        clearable=False,
                        style={'backgroundColor': '#FFFFFF'},
                        className = "pt-3"
                    )
                ]),
                className = "pt-4 px-3"
            ),
            # Municipio
            dbc.Row(
                dbc.Col([
                    html.Div([
                        html.Img(src="assets/location.png", height="20px", style={'margin-right': '8px'}),
                        html.Span(
                            "Municipio", style = {"font-weight": "bold"}, id="municipio-tooltip-target"
                        ), 
                        dbc.Tooltip(
                            "Solo una opción disponible por el momento.",
                            target="municipio-tooltip-target",
                            placement = "top"
                        )              
                    ],
                        style={'display': 'flex', 'align-items': 'center'}
                    ),
                    dcc.Dropdown(
                        id='mes-dropdown-d',
                        options=[
                            {"label": "Zona Metropolitana", "value": "Zona Metropolitana"},
                            {"label": "🔒🔜 Abasolo", "value": "Abasolo", "disabled": True},
                            {"label": "🔒🔜 El Carmen", "value": "El Carmen", "disabled": True},
                            {"label": "🔒🔜 Escobedo", "value": "Escobedo", "disabled": True},
                            {"label": "🔒🔜 García", "value": "García", "disabled": True},
                            {"label": "🔒🔜 Juárez", "value": "Juárez", "disabled": True},
                            {"label": "🔒🔜 Allende", "value": "Allende", "disabled": True},
                            {"label": "🔒🔜 Apodaca", "value": "Apodaca", "disabled": True},
                            {"label": "🔒🔜 Cadereyta Jimenez", "value": "Cadereyta Jimenez", "disabled": True},
                            {"label": "🔒🔜 Cienega de Flores", "value": "Cienega de Flores", "disabled": True},
                            {"label": "🔒🔜 Guadalupe", "value": "Guadalupe", "disabled": True},
                            {"label": "🔒🔜 Monterrey", "value": "Monterrey", "disabled": True},
                            {"label": "🔒🔜 Salinas Victoria", "value": "Salinas Victoria", "disabled": True},
                            {"label": "🔒🔜 San Nicolás de los Garza", "value": "San Nicolás de los Garza", "disabled": True},
                            {"label": "🔒🔜 San Pedro Garza García", "value": "San Pedro Garza García", "disabled": True},
                            {"label": "🔒🔜 Santa Catarina", "value": "Santa Catarina", "disabled": True},
                            {"label": "🔒🔜 Santiago", "value": "Santiago", "disabled": True}
                        ],
                        value='Zona Metropolitana',
                        clearable=False,
                        style={'backgroundColor': '#FFFFFF'},
                        className = "pt-3"
                    )
                ]),
                className = "pt-4 px-3"
            ),
            # Fecha
            dbc.Row(
                dbc.Col([
                    html.Div([
                        html.Img(src="assets/calendar.png", height="18px", style={'margin-right': '10px'}),
                        html.Span(
                            "Fecha", style = {"font-weight": "bold"}, id="fecha-tooltip-target"
                        ), 
                        dbc.Tooltip(
                            "El rango de fecha se actualiza diariamente. No se puede seleccionar un rango menor por el momento.",
                            target="fecha-tooltip-target",
                            placement = "top"
                        )              
                    ],
                        style={'display': 'flex', 'align-items': 'center'}
                    ),
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        start_date_placeholder_text="Start Period",
                        end_date_placeholder_text="End Period",
                        start_date=datetime(2023, 5, 8),
                        end_date= now_mexico,
                        min_date_allowed=datetime(2023, 5, 31),
                        max_date_allowed=datetime(2023, 5, 8),
                        display_format="DD/MM/YYYY",
                        className = "pt-3 smaller-font"
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
            # Conoce más y descargar
            dbc.Row([
                # Conoce más
                dbc.Col(
                    html.Div([
                        dbc.Button(
                            "Conoce más",
                            color = "secondary",
                            outline = True,
                            id = "open_conocemas",
                            n_clicks = 0,
                            style={'border-color': '#CCCCCC', "font-size": "14px"}
                        ),
                        dbc.Modal([
                            dbc.ModalHeader(
                                dbc.ModalTitle("Conoce más")
                            ),
                            dbc.ModalBody([
                                html.P([
                                    "Desarrollamos esta plataforma para fortalecer a la ciudadanía en la lucha por crear una ciudad "
                                    "con mejor calidad de aire para todas y todos. El sistema actual recolecta cada " 
                                    "hora datos de los más de 100 sensores de ",
                                    html.A("Purple Air",
                                           href="https://www2.purpleair.com/",
                                           target="_blank",
                                           style={"text-decoration": "none"}),
                                    " en el área metropolitana de Monterrey."
                                ]),
                                html.P([
                                    "Si tienes dudas sobre el proyecto o te gustaría colaborar para fortalecer la plataforma "
                                    "nos puedes enviar un correo a hola@datacomun.org o visitar nuestra página en ",
                                    html.A(
                                        "datacomun.org",
                                        href="https://www.datacomun.org/",
                                        target="_blank",
                                        style={"text-decoration": "none"}
                                    )
                                ])
                            ])
                        ],
                        id = "modal_conocemas",
                        is_open = False
                        )
                    ]),
                    className = "pb-4 pt-2 d-flex align-items-center justify-content-center"
                ),
                # Descargar
                dbc.Col(
                    html.Div([
                        dbc.Button(
                            html.Span("Descargar", style={"padding": "5px"}),
                            id="open_descargar", 
                            color="secondary",
                            outline=True,
                            style={'border-color': '#CCCCCC', "font-size": "14px"}
                        ),
                        dbc.Modal([
                            dbc.ModalHeader(
                                dbc.ModalTitle("Descarga los datos")
                            ),
                            dbc.ModalBody(
                                html.P(
                                    "Los datos se descargan de acuerdo a los filtros previamente seleccionados en formato CSV que puedes abrir " 
                                    "en varias plataformas, incluyendo Excel."
                                )
                            ),
                            dbc.ModalFooter([
                                dbc.Button(
                                    "Descargar",
                                    id="boton_descargar", 
                                    color="secondary",
                                    outline=True,
                                    style={'border-color': '#CCCCCC'}
                                ),
                                dcc.Download(id = "datos")
                            ])
                        ],
                        id = "modal_descargar",
                        is_open = False
                        )
                    ]),
                    className = "pb-4 pt-2 d-flex align-items-center justify-content-center"
                )
            ])
        ],
            className='pt-4 d-flex flex-column',
            width=3,
            style = {
                "position": "fixed", 
                "top": 0,
                "height": "100vh",
                "border-right": "1px solid #DBDBDB",
                "overflow": "auto"
            }
        ),

        # Visualizaciones
        dbc.Col([

            # Mapa
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(
                                figure=sensors_go,
                                config={'displaylogo': False},
                                id="mapa-mobile"
                            )
                        )
                    )
                ),
                className = "pt-4"
            ),
            # Tabla
            dbc.Row(
                dbc.Col(
                    dbc.Card(
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
                    )
                ),
                className = "pt-4"
            ),
            # Scatter Plot
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(
                                id='scatter_plot',
                                figure=scatter_fig,
                                config={'displayModeBar': False}
                            )
                        )            
                    )
                ),
                className = "pt-4 pb-4"
            )
        ],
        width=9,
        className = "px-5",
        style = {
            "margin-left": "25%"
        }
        )

    ],
        className="m-0 d-none d-xl-block"
    ),

    # Sidebar y Visualizaciones - Mobile
    dbc.Row(
        dbc.Col([
            # Webbsite's logo
            dbc.Row(
                dbc.Col(
                    dbc.Row(
                        dbc.Col(
                            html.Img(src="../assets/logo_datacomun.png", height="30px"),
                            style={"color": "black"}
                        )
                    )
                ),
                className = "pt-4 pb-4",
                style={"text-align": "center"}
            ),
            # Mapa
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(
                                figure=sensors_go,
                                config={'displaylogo': False},
                                id="mapa-mobile"
                            )
                        )
                    )
                ),
                className = "pt-2 pb-4"
            ),
            # Tabla
            dbc.Row(
                dbc.Col(
                    dbc.Card(
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
                    )
                ),
                className = "pt-2 pb-4"
            ),
            # Scatter Plot
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(
                                id='scatter_plot',
                                figure=scatter_fig,
                                config={'displayModeBar': False}
                            )
                        )            
                    )
                ),
                className = "pt-2 pb-5"
            ),
            # NavBar
            dbc.Row([
                # Filtros
                dbc.Col(
                    html.Div([
                        html.Button(
                            html.Img(src="assets/filtro.png", height="26px"), 
                            id="open_offcanvas",
                            n_clicks=0,
                            style={
                                "background": "none",
                                "border": "none",
                                "cursor": "pointer",
                            }
                        ),
                        dbc.Offcanvas([
                            # Fuente de datos
                            dbc.Row(
                                dbc.Col([
                                    html.Div([
                                        html.Img(src="assets/sensor.png", height="22px", style={'margin-right': '6px'}),
                                        html.Span(
                                            "Fuente de Datos", style = {"font-weight": "bold"}, id="fuente-tooltip-target"
                                        ), 
                                        dbc.Tooltip(
                                            "Solo una fuente de datos disponible por el momento.",
                                            target="fuente-tooltip-target",
                                            placement = "top"
                                        )              
                                    ],
                                        style={'display': 'flex', 'align-items': 'center'}
                                    ),
                                    dcc.Dropdown(
                                        id='municipio-dropdown-d',
                                        options=[
                                            {"label": "Sensores de Purple Air", "value": "Sensores de Purple Air"},
                                            {"label": "🔒🔜 Sensores del Estado de N.L.", "value": "Sensores del Estado de Nuevo León",
                                            "disabled": True}
                                        ],
                                        value='Sensores de Purple Air',
                                        clearable=False,
                                        style={'backgroundColor': '#FFFFFF'},
                                        className = "pt-3"
                                    )
                                ]),
                                className = "pt-4 px-3"
                            ),
                            # Indicador
                            dbc.Row(
                                dbc.Col([
                                    html.Div([
                                        html.Img(src="assets/indicador.png", height="20px", style={'margin-right': '8px'}),
                                        html.Span(
                                            "Indicador", style = {"font-weight": "bold"}, id="indicador-tooltip-target"
                                        ), 
                                        dbc.Tooltip(
                                            "Solo un indicador disponible por el momento.",
                                            target="indicador-tooltip-target",
                                            placement = "top"
                                        )              
                                    ],
                                        style={'display': 'flex', 'align-items': 'center'}
                                    ),
                                    dcc.Dropdown(
                                        id='mes-dropdown-d',
                                        options=[
                                            {"label": "PM2.5", "value": "PM2.5"},
                                            {"label": "🔒🔜 PM10.0", "value": "PM10.0", "disabled": True},
                                            {"label": "🔒🔜 Temperatura", "value": "Temperatura", "disabled": True}
                                        ],
                                        value='PM2.5',
                                        clearable=False,
                                        style={'backgroundColor': '#FFFFFF'},
                                        className = "pt-3"
                                    )
                                ]),
                                className = "pt-4 px-3"
                            ),
                            # Municipio
                            dbc.Row(
                                dbc.Col([
                                    html.Div([
                                        html.Img(src="assets/location.png", height="20px", style={'margin-right': '8px'}),
                                        html.Span(
                                            "Municipio", style = {"font-weight": "bold"}, id="municipio-tooltip-target"
                                        ), 
                                        dbc.Tooltip(
                                            "Solo una opción disponible por el momento.",
                                            target="municipio-tooltip-target",
                                            placement = "top"
                                        )              
                                    ],
                                        style={'display': 'flex', 'align-items': 'center'}
                                    ),
                                    dcc.Dropdown(
                                        id='mes-dropdown-m',
                                        options=[
                                            {"label": "Zona Metropolitana", "value": "Zona Metropolitana"},
                                            {"label": "🔒🔜 Abasolo", "value": "Abasolo", "disabled": True},
                                            {"label": "🔒🔜 El Carmen", "value": "El Carmen", "disabled": True},
                                            {"label": "🔒🔜 Escobedo", "value": "Escobedo", "disabled": True},
                                            {"label": "🔒🔜 García", "value": "García", "disabled": True},
                                            {"label": "🔒🔜 Juárez", "value": "Juárez", "disabled": True},
                                            {"label": "🔒🔜 Allende", "value": "Allende", "disabled": True},
                                            {"label": "🔒🔜 Apodaca", "value": "Apodaca", "disabled": True},
                                            {"label": "🔒🔜 Cadereyta Jimenez", "value": "Cadereyta Jimenez", "disabled": True},
                                            {"label": "🔒🔜 Cienega de Flores", "value": "Cienega de Flores", "disabled": True},
                                            {"label": "🔒🔜 Guadalupe", "value": "Guadalupe", "disabled": True},
                                            {"label": "🔒🔜 Monterrey", "value": "Monterrey", "disabled": True},
                                            {"label": "🔒🔜 Salinas Victoria", "value": "Salinas Victoria", "disabled": True},
                                            {"label": "🔒🔜 San Nicolás de los Garza", "value": "San Nicolás de los Garza", "disabled": True},
                                            {"label": "🔒🔜 San Pedro Garza García", "value": "San Pedro Garza García", "disabled": True},
                                            {"label": "🔒🔜 Santa Catarina", "value": "Santa Catarina", "disabled": True},
                                            {"label": "🔒🔜 Santiago", "value": "Santiago", "disabled": True}
                                        ],
                                        value='Zona Metropolitana',
                                        clearable=False,
                                        style={'backgroundColor': '#FFFFFF'},
                                        className = "pt-3"
                                    )
                                ]),
                                className = "pt-4 px-3"
                            ),
                            # Fecha
                            dbc.Row(
                                dbc.Col([
                                    html.Div([
                                        html.Img(src="assets/calendar.png", height="18px", style={'margin-right': '10px'}),
                                        html.Span(
                                            "Fecha", style = {"font-weight": "bold"}, id="fecha-tooltip-target"
                                        ), 
                                        dbc.Tooltip(
                                            "El rango de fecha se actualiza diariamente. No se puede seleccionar un rango menor por el momento.",
                                            target="fecha-tooltip-target",
                                            placement = "top"
                                        )              
                                    ],
                                        style={'display': 'flex', 'align-items': 'center'}
                                    ),
                                    dcc.DatePickerRange(
                                        id='date-picker-range',
                                        start_date_placeholder_text="Start Period",
                                        end_date_placeholder_text="End Period",
                                        start_date=datetime(2023, 5, 8),
                                        end_date= now_mexico,
                                        min_date_allowed=datetime(2023, 5, 31),
                                        max_date_allowed=datetime(2023, 5, 8),
                                        display_format="DD/MM/YYYY",
                                        className = "smaller-font pt-3"
                                    )
                                ]),
                                className = "pt-4 px-3"
                            )
                        ],
                            id = "offcanvas",
                            is_open = False,
                            placement = "start",
                            style = {"z-index": "9999"}
                        )
                    ]),
                    className = "d-flex align-items-center justify-content-center"
                ),
                # Descargar datos
                dbc.Col(
                    html.Div([
                        html.Button(
                            "⬇️", 
                            id="open_descargar_m",
                            n_clicks=0,
                            style={
                                "background": "none",
                                "border": "none",
                                "font-size": "26px",
                                "cursor": "pointer",
                            }
                        ),
                        dbc.Modal([
                            dbc.ModalHeader(
                                dbc.ModalTitle("Descarga los datos")
                            ),
                            dbc.ModalBody(
                                html.P(
                                    "Los datos se descargan de acuerdo a los filtros previamente seleccionados en formato CSV que puedes abrir " 
                                    "en varias plataformas, incluyendo Excel."
                                )
                            ),
                            dbc.ModalFooter([
                                dbc.Button(
                                    "⬇️ Descargar",
                                    id="boton_descargar_m", 
                                    color="secondary",
                                    outline=True,
                                    style={'border-color': '#CCCCCC'}
                                ),
                                dcc.Download(id = "datos_m")
                            ])
                        ],
                        id = "modal_descargar_m",
                        is_open = False
                        )
                    ]),
                    className = "d-flex align-items-center justify-content-center"
                ),
                # Conoce más
                dbc.Col(
                    html.Div([
                        html.Button(
                            "ℹ️", 
                            id="open_conocemas_m",
                            n_clicks=0,
                            style={
                                "background": "none",
                                "border": "none",
                                "font-size": "26px",
                                "cursor": "pointer",
                            }
                        ),
                        dbc.Modal([
                            dbc.ModalHeader(
                                dbc.ModalTitle(
                                    dbc.Col(
                                        html.Img(src="../assets/logo_datacomun.png", height="30px"),
                                        style={"color": "black"}
                                    )
                                )
                            ),
                            dbc.ModalBody([
                                html.P([
                                    "Desarrollamos esta plataforma para fortalecer a la ciudadanía en la lucha por crear una ciudad "
                                    "con mejor calidad de aire para todas y todos. El sistema actual recolecta cada " 
                                    "hora datos de los más de 100 sensores de ",
                                    html.A("Purple Air",
                                           href="https://www2.purpleair.com/",
                                           target="_blank",
                                           style={"text-decoration": "none"}),
                                    " en el área metropolitana de Monterrey."
                                ]),
                                html.P([
                                    "Si tienes dudas sobre el proyecto o te gustaría colaborar para fortalecer la plataforma "
                                    "nos puedes enviar un correo a hola@datacomun.org o visitar nuestra página en ",
                                    html.A(
                                        "datacomun.org",
                                        href="https://www.datacomun.org/",
                                        target="_blank",
                                        style={"text-decoration": "none"}
                                    )
                                ])
                            ])
                        ],
                        id = "modal_conocemas_m",
                        is_open = False
                        )
                    ]),
                    className = "d-flex align-items-center justify-content-center"
                )
            ],  
                className = "pb-2 pt-2 position-fixed w-100",
                style = {"bottom": "0", "background-color": "rgba(255,255,255,0.9)", "z-index": "9998"}
            )
        ]),
        className = "m-0 d-xl-none"
    )

])

