import dash
from dash import Dash, html
import plotly_express as px
import os

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

# Map
# Mapbox token
token = os.environ['DB_PWD_TER']
px.set_mapbox_access_token(token)


if __name__ == '__main__':
    app.run_server(debug=True)