import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash import Output, Input

from server import app
from callbacks import *
from helpers import draw_map

raw_columns = ["id", "dlnrid", "name",  "Y", "X"]
stations_table_data = get_stations_table_data(raw_columns)
stations_table_columns = ["stnid", "dlnrid", "name", "lat", "lon"]


app.layout = html.Div([
    dcc.ConfirmDialog(
        id="cookie-accept",
        message="DISCLAIMER. Do you accept?",
        submit_n_clicks=0,
        cancel_n_clicks=0
    ),
    dcc.Store(id="cookie-store", storage_type="local"),
    html.Div(id="page-content")
])

page_content = html.Div(className="container", children=[
    html.Div(className="container", children=[
        dcc.Graph(id="fig_map", figure=draw_map())
    ]),
    dcc.Store(id="loaded_data"),
    dcc.Store(id="station_id", data={"station_id": ""}),
    html.Br(),
    html.Div(
        className="container",
        children=[
            html.Div(
                className="one-half column",
                children=[
                    html.H6("Stations:"),
                    dcc.Dropdown(
                        id="stations_dropdown",
                        options=get_stations_dropdown_options(),
                        placeholder="Select a station"
                    ),
                    html.Br(),
                    html.Div([
                        html.Button("GMT",
                                    id="gmt-button",
                                    style={"border-right": "0",
                                           "width": "50%",
                                           "border-radius": "0%"}),
                        html.Button("HST",
                                    id="hst-button",
                                    style={"border-left": "0",
                                           "width": "50%",
                                           "border-radius": "0%"})
                    ], style={"width": "100%"})
                ]),
            html.Div(
                className="one-half column",
                children=[
                    dash_table.DataTable(
                        id="stations_table",
                        columns=[{"name": i, "id": j}
                                 for i, j in zip(stations_table_columns, raw_columns)],
                        data=stations_table_data,
                        style_data={
                            "color": "black",
                            "backgroundColor": "white",
                            "border": "none",
                            "fontSize": "14px"
                        },
                        style_data_conditional=[
                            {
                                "if": {"row_index": "odd"},
                                "backgroundColor": "rgb(240, 240, 240)",
                            },
                            {
                                "if": {"column_id": "id"},
                                "cursor": "pointer",
                                "textAlign": "right",
                                "color": "blue",
                            }
                        ],
                        style_header={
                            "backgroundColor": "rgb(210, 210, 210)",
                            "color": "black",
                            "fontWeight": "bold",
                            "fontSize": "14px"
                        },
                        style_table={
                            "overflowY": "auto",
                            "height": "300px",
                        },
                        fixed_rows={"headers": True},
                    ),
                ])
        ]
    ),
    html.Div(
        html.H2(id="station-title",
                style={"text-align": "center", "font-weight": "bold"}
                )),
        dcc.Loading([
        dcc.Graph(
            id="fig_water_level"
        ),
        html.Br(),
        dcc.Graph(id="fig_bat_voltage")])
    ])


@app.callback(Output("cookie-accept", "displayed"),
    Input("cookie-store", "data"),
)
def show_cookie_prompt(data):
    if data is not None and data.get("persisted"):
        return False
    return True

@app.callback(
    Output("cookie-store", "data"),
    Output("page-content", "children"),
    [Input("cookie-accept", "submit_n_clicks")],
    [State("cookie-store", "data")]
)
def store_cookie(n_clicks, data):
    try:
        if data["persisted"]:
            return data, page_content
    except:
        if n_clicks:
            data = {"persisted": True, "timestamp": datetime.now().isoformat()}
            return data, page_content
        return data, []


if __name__ == "__main__":
   app.run_server(debug=False)
