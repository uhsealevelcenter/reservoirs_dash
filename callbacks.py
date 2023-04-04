from dash import Input, Output, State, ctx
from server import app
from helpers import *


@app.callback(
    Output("station-title", "children"),
    Output("fig_water_level", "figure"),
    Output("fig_bat_voltage", "figure"),
    Output("stations_dropdown", "value"),
    Output("stations_table", "active_cell"),
    Output("stations_table", "selected_cells"),
    Output("station_id", "data"),
    Output("loaded_data", "data"),
    Input("stations_table", "active_cell"),
    Input("stations_dropdown", "value"),
    Input("hst-button", "n_clicks_timestamp"),
    Input("gmt-button", "n_clicks_timestamp"),
    Input("fig_map", "clickData"),
    State("stations_table", "selected_cells"),
    State("stations_dropdown", "value"),
    State("station_id", "data"),
    State("loaded_data", "data"),
    pervent_initial_callback=True
    )
def update_graphs(active_cell, station_dropdown, hst_button, gmt_button, map_data, selected_cells, station_dropdown_state,
                  station_id_stored, data_stored):
    trigger = ctx.triggered_id
    hst_button = 0 if not hst_button else hst_button
    gmt_button = 0 if not gmt_button else gmt_button
    is_gmt = True if gmt_button >= hst_button else False

    if trigger is None:
        station_id = dd_value = "EDD00CC6"
        table_cell, selected_cell = None, []
    elif trigger == "gmt-button" or trigger == "hst-button":
        station_id = dd_value = station_dropdown_state
        table_cell = active_cell
        selected_cell = selected_cells    
    elif trigger == "stations_table":
        station_id = dd_value = active_cell["row_id"]
        table_cell = active_cell
        selected_cell = selected_cells
    elif trigger == "stations_dropdown":
        station_id = dd_value = station_dropdown
        table_cell, selected_cell = None, []
    elif trigger == "fig_map":
        station_id = dd_value = map_data["points"][0]["customdata"]
        table_cell, selected_cell = None, []
    
    fig_water_level, fig_bat_voltage, station_id_to_store, data_to_store = draw_graphs(station_id, is_gmt, station_id_stored["station_id"], data_stored)
    return station_id, fig_water_level, fig_bat_voltage, dd_value, table_cell, selected_cell, {"station_id": station_id_to_store}, {"data": data_to_store}


@app.callback(
    Output("fig_map", "figure"),
    Input("stations_dropdown", "value"),
    Input("stations_table", "active_cell"),
    State("stations_table", "data"),
)
def update_map_figure(dropdown, active_cell, stations_table):
    if not dropdown and not active_cell:
        return draw_map()
    point_number = [stations_table.index(row) for row in stations_table if row["id"]==dropdown]
    if dropdown:
        return draw_map(dropdown, selected_point=point_number)
    if active_cell:
        return draw_map(active_cell["row_id"], selected_point=point_number)


@app.callback(
    Output("hst-button", "className"),
    Output("gmt-button", "className"),
    Input("hst-button", "n_clicks"),
    Input("gmt-button", "n_clicks")
)
def update_button_style(hst_n_clicks, gmt_n_clicks):
    if str(gmt_n_clicks) == "None":
        gmt_n_clicks = 0
    if str(hst_n_clicks) == "None":
        hst_n_clicks = 0
    return ["button-active", "button-inactive"] if hst_n_clicks > gmt_n_clicks else ["button-inactive", "button-active"]

