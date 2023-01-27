from dash import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table

from helpers import *
from server import app

raw_columns = ['id', 'dlnrid', 'name',  'Y', 'X']
stations_table_data = get_stations_table_data(raw_columns)
stations_table_columns = ["stnid", "dlnrid", "name", "lat", "lon"]

fig_map = draw_map()
fig_water_level, fig_bat_voltage = draw_graphs("EDD024F8", True)

app.layout = html.Div(className="container", children=[
    html.Div(className="container", children=[
        dcc.Graph(figure=fig_map)
    ]),
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
                    ], style={"width": '100%'})
                ]),
            html.Div(
                className="one-half column",
                children=[
                    dash_table.DataTable(
                        id='stations_table',
                        columns=[{"name": i, "id": j}  # , "presentation": "markdown"} if j=="id" else {"name": i, "id": j}
                                 for i, j in zip(stations_table_columns, raw_columns)],
                        data=stations_table_data,
                        style_data={
                            'color': 'black',
                            'backgroundColor': 'white',
                            'border': 'none',
                            'fontSize': '14px'
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(240, 240, 240)',
                            },
                            {
                                'if': {'column_id': 'id'},
                                'cursor': 'pointer',
                                'textAlign': 'right',
                                'color': 'blue',
                                # 'textDecoration': 'underline'
                            }
                        ],
                        style_header={
                            'backgroundColor': 'rgb(210, 210, 210)',
                            'color': 'black',
                            'fontWeight': 'bold',
                            'fontSize': '14px'
                        },
                        style_table={
                            'overflowY': 'auto',
                            'height': '300px',
                        },
                        fixed_rows={'headers': True},
                    ),
                    html.P(id="table_selected", children="AAAa")
                ])
        ]
    ),
    html.Div(
        html.H2("Naslov", id="station-title",
                style={"text-align": "center", "font-weight": "bold"}
                )),
        dcc.Graph(
            figure=fig_water_level
        ),
        html.Br(),
        dcc.Graph(figure=fig_bat_voltage)
    ])


@app.callback(
    Output('table_selected', 'children'),
    Input('stations_table', 'active_cell'))
def update_graphs(active_cell):
    return str(active_cell) if active_cell else "Click the table"


@app.callback(
    Output("hst-button", "className"),
    Output('gmt-button', "className"),
    Input("hst-button", "n_clicks"),
    Input("gmt-button", "n_clicks")
)
def update_button_style(hst_n_clicks, gmt_n_clicks):
    if str(gmt_n_clicks) == 'None':
        gmt_n_clicks = 0
    if str(hst_n_clicks) == 'None':
        hst_n_clicks = 0
    return ["button-active", "button-inactive"] if hst_n_clicks > gmt_n_clicks else ["button-inactive", "button-active"]


if __name__ == '__main__':
   app.run_server(debug=False)
