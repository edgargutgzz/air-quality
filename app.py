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

# Map

# Mapbox token
token = os.environ['DB_PWD_TER']
px.set_mapbox_access_token(token)

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

# Map's Callback - Mobile
def map_mobile(switches_value):

    sensors = pd.read_csv("assets/sensores.csv")

    if switches_value == [1]:

        sensors = px.scatter_mapbox(sensors, lat="lat", lon="lon", custom_data=["nombre", "municipio", "sensor_id"])

        sensors.update_traces(hovertemplate="<br>".join([
            "%{customdata[0]}",
            "Municipio: %{customdata[1]}",
            "Sensor ID: %{customdata[2]}"
        ])
        )

        sensors.update_layout(map_layout)

        return sensors

    else:

        placeholder = px.scatter_mapbox(
            sensors,
            lat="lat", lon="lon", custom_data=["nombre", "municipio", "sensor_id"]
        )

        placeholder.update_traces(
            marker={'size': 0, 'opacity': .5, 'color': '#E2474B'},
            hoverinfo="none"
        )

        placeholder.update_layout(map_layout)

        return placeholder

app.callback(
    Output("mapa-mobile", "figure"),
    Input("switches-input-mobile", "value")
)(map_mobile)

# Map's Sidebar Callback - Mobile
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

app.callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)(toggle_offcanvas)

# Callback - Desktop
def map_desktop(switches_value):

    sensors = pd.read_csv("assets/sensores.csv")

    if switches_value == [1]:

        sensors = px.scatter_mapbox(sensors, lat="lat", lon="lon", custom_data=["nombre", "municipio", "sensor_id"])

        sensors.update_traces(hovertemplate="<br>".join([
            "%{customdata[0]}",
            "Municipio: %{customdata[1]}",
            "Sensor ID: %{customdata[2]}"
        ])
        )

        sensors.update_layout(map_layout)

        return sensors

    else:

        placeholder = px.scatter_mapbox(
            sensors,
            lat="lat", lon="lon", custom_data=["nombre", "municipio", "sensor_id"]
        )

        placeholder.update_traces(
            marker={'size': 0, 'opacity': .5, 'color': '#E2474B'},
            hoverinfo="none"
        )

        placeholder.update_layout(map_layout)

        return placeholder

app.callback(
    Output("mapa-desktop", "figure"),
    Input("switches-input-desktop", "value")
)(map_desktop)

#----------

if __name__ == '__main__':
    app.run_server(debug=True)