from dash import Dash, Input, Output, callback, dash_table
import pandas as pd
from dash import Input, Output, State, ctx
from server import app
from helpers import *


@app.callback(
    Output('station-title', 'children'),
    Output('fig_water_level', 'figure'),
    Output('fig_bat_voltage', 'figure'),
    # Output('fig_map', 'figure'),
    Output('stations_dropdown', 'value'),
    Output('stations_table', 'active_cell'),
    Output('stations_table', 'selected_cells'),
    Input('stations_table', 'active_cell'),
    Input('stations_dropdown', 'value'),
    Input("hst-button", "n_clicks_timestamp"),
    Input("gmt-button", "n_clicks_timestamp"),
    Input("fig_map", "clickData"),
    State('stations_table', 'selected_cells'),
    State('stations_table', 'data'),
    State('fig_map', 'figure'))
def update_graphs(active_cell, station_dropdown, hst_button, gmt_button, map_data, selected_cells, stations_table, map):
    trigger = ctx.triggered_id
    hst_button = 0 if not hst_button else hst_button
    gmt_button = 0 if not gmt_button else gmt_button
    is_gmt = True if gmt_button >= hst_button else False
    
    if trigger == 'stations_table' or active_cell:
        station_id = active_cell["row_id"]
        dd_value = None
        table_cell = active_cell
        fig_water_level, fig_bat_voltage = draw_graphs(station_id, is_gmt)
        return station_id, fig_water_level, fig_bat_voltage, dd_value, table_cell, selected_cells
    elif trigger == 'stations_dropdown' or station_dropdown:
        station_id = station_dropdown
        dd_value = station_dropdown
        table_cell = None
        fig_water_level, fig_bat_voltage = draw_graphs(station_id, is_gmt)
        return station_id, fig_water_level, fig_bat_voltage, dd_value, table_cell, []
    elif trigger == 'fig_map':
        # print(map)
        table_cell = {}#[station for station in stations_table if station['X']==lon and station['Y']==lat][0]
        station_id = dd_value = map_data['points'][0]['customdata']
        fig_water_level, fig_bat_voltage = draw_graphs(station_id, is_gmt)
        return station_id, fig_water_level, fig_bat_voltage, None, None, []


    return "Station", go.Figure(), go.Figure(), None, None, []


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

# @app.callback(
#     Output("test", "children"),
#     Input("mapbox_fig", "clickData")
# )
# def test(click_data):
#     return click_data
