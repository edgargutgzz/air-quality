import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
import dash_ag_grid as dag
import pandas as pd


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

# Sample data
data = {
    'name': ['Estación de Monitoreo de Calidad del Aire Comité Municipal PAN Abasolo', 'Estación de Monitoreo de Calidad del Aire Comité Municipal PAN Allende', 'La Gozacion', 'Estación de Monitoreo de Calidad del Aire Comité Municipal PAN Allende'],
    'sensor_index': [143390, 50571, 132661, 143346],
    'municipio': ['Abasolo', 'Allende', 'Allende', 'Allende'],
    'estado': ['Nuevo Leon'] * 4,
    'lat': [25.947264, 25.215078, 25.317438, 25.282354],
    'lon': [-100.399025, -99.9597, -100.04217, -100.0235]
}

df = pd.DataFrame(data)


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

    dbc.Row(
        dbc.Col(
            html.Div(
                dag.AgGrid(
                    id='my_ag_grid',
                    rowData=df.to_dict('records'),
                    columnDefs=[{"headerName": col, "field": col} for col in df.columns],
                    defaultColDef={
                        'editable': False,
                        'sortable': True,
                        'filter': 'agTextColumnFilter',
                        'resizable': True
                    }
                )
            )
        )
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

