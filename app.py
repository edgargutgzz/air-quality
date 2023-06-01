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
app = Dash(__name__, title= "Calidad del Aire - Data Comun",
           use_pages=True,
           external_stylesheets=external_stylesheets,
           )


# Google Analytics
app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-MFWLPXZ29K"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
        
          gtag('config', 'G-MFWLPXZ29K');
        </script>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""


server = app.server

# Page layout
app.layout = html.Div(
    dash.page_container
)

#----------
# Air Quality Data
# Connect to database.
DATABASE_URL = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)

# Execute the query and fetch data
query = """
WITH numbered_rows AS (
    SELECT a.pollution_id, a.sensor_id, a.pm25, s.nombre, s.municipio,
           (TO_TIMESTAMP(a.date, 'YYYY/MM/DD HH24:MI') - INTERVAL '6 hours') as date
    FROM air_quality a
    JOIN sensors s ON a.sensor_id = s.sensor_id
)
SELECT pollution_id, TO_CHAR(date, 'YYYY/MM/DD HH24:MI') as date, nombre, municipio, sensor_id, pm25
FROM numbered_rows
WHERE date >= TIMESTAMP '2023-05-08 00:00:00'
ORDER BY date;
"""

dataframe = pd.read_sql(query, conn)

dataframe.rename(columns={"nombre": "sensor", "date": "fecha"}, inplace=True)

# Close the connection
conn.close()

#----------
# Conoce más - Desktop
def conocemas(n, is_open):
    if n:
        return not is_open
    return is_open

app.callback(
    Output("modal_conocemas", "is_open"),
    [Input("open_conocemas", "n_clicks")],
    [State("modal_conocemas", "is_open")],
)(conocemas)

# Conoce más - Mobile
def conocemas_m(n, is_open):
    if n:
        return not is_open
    return is_open

app.callback(
    Output("modal_conocemas_m", "is_open"),
    [Input("open_conocemas_m", "n_clicks")],
    [State("modal_conocemas_m", "is_open")],
)(conocemas_m)

#----------
# Descargar - Desktop
def descargar(n, is_open):
    if n:
        return not is_open
    return is_open

app.callback(
    Output("modal_descargar", "is_open"),
    [Input("open_descargar", "n_clicks")],
    [State("modal_descargar", "is_open")],
)(descargar)

# Descargar - Mobile
def descargar_m(n, is_open):
    if n:
        return not is_open
    return is_open

app.callback(
    Output("modal_descargar_m", "is_open"),
    [Input("open_descargar_m", "n_clicks")],
    [State("modal_descargar_m", "is_open")],
)(descargar_m)

#----------
# Download button - Desktop
def descargar_modal(n_clicks):
    return dcc.send_data_frame(dataframe.to_csv, "calidadaire.csv", index = False)

app.callback(
    Output("datos", "data"),
    Input("boton_descargar", "n_clicks"),
    prevent_initial_call=True,
)(descargar_modal)

# Download button - Mobile
def descargar_modal_m(n_clicks):
    return dcc.send_data_frame(dataframe.to_csv, "calidadaire.csv", index = False)

app.callback(
    Output("datos_m", "data"),
    Input("boton_descargar_m", "n_clicks"),
    prevent_initial_call=True,
)(descargar_modal_m)

#----------
# Offcanvas - Mobile
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

app.callback(
    Output("offcanvas", "is_open"),
    Input("open_offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)(toggle_offcanvas)








#----------
if __name__ == '__main__':
    app.run_server(debug=True)