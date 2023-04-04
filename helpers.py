import os
import pandas as pd
import numpy as np
import pytz
import time
from datetime import datetime
import plotly.graph_objects as go
from csv import DictReader
import codecs
import urllib


token = os.environ.get("MAPBOX_TOKEN")
stations_url = "https://uhslc.soest.hawaii.edu/komar/stations.csv"
stations_general = pd.read_csv(stations_url)


def get_longitude(id=""):
    return stations_general.X if not id else stations_general[stations_general.id == id].X.values[0]


def get_latitude(id=""):
    return stations_general.Y if not id else stations_general[stations_general.id == id].Y.values[0]


def get_locations_name():
    return stations_general.name


def get_stations_table_data(column_names):
    stations_table = stations_general[column_names]
    table_data = stations_table.to_dict("records")

    return table_data


def get_stations_dropdown_options():
    data = stations_general.to_dict('records')
    options = [(f'{record["id"]} {record["dlnrid"]} {record["name"]}',
                record["id"]) for record in data]
    return [{"label": opt[0], "value": opt[1]} for opt in options]


def get_on_off_alert(station_id):
    return {"off": stations_general[stations_general.id == station_id].level_alert_off.values[0],
            "on": stations_general[stations_general.id == station_id].level_alert_on.values[0]}


def draw_map(id="", selected_point=[]):
    lat = get_latitude(id) if id else 21
    lon = get_longitude(id) if id else -158
    fig = go.Figure(go.Scattermapbox(
        lat=get_latitude(),
        lon=get_longitude(),
        mode="markers",
        marker={"size": 9, "color": "green", "opacity": 1},
        selected=go.scattermapbox.Selected(
            marker={
                "color": "skyblue",
                "size": 18,
            }
        ),
        selectedpoints=selected_point,
        text=get_locations_name(),
        customdata=stations_general["id"]
    ))

    fig.update_layout(
        autosize=True,
        hovermode="closest",
        clickmode="event+select",
        mapbox_style="carto-positron",
        mapbox=dict(
            accesstoken=token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=lat,
                lon=lon
            ),
            pitch=0,
            zoom=6 if not selected_point else 8,
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    return fig


def populate_data(row, date, time, battery, water_level):
    time.append(date)
    battery.append(float(row["bv"]))
    row_data = int(row["data"])
    if row_data > -10000 and row_data < 99999:
        water_level.append(row_data / 100)
    else:
        water_level.append(np.nan)

    return time, battery, water_level


def convert_to_hst(str_date):
    date = datetime.strptime(str_date, "%Y-%m-%dT%H:%M:%SZ")
    date = date.astimezone(pytz.timezone("Pacific/Honolulu"))
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


def _get_water_level_graph(station_id, is_gmt, station_id_stored, data_stored):
    if station_id != station_id_stored:
        t1 = time.time()
        res = urllib.request.urlopen(f"https://uhslc.soest.hawaii.edu/reservoir/{station_id}.csv")
        data = list(DictReader(codecs.iterdecode(res, encoding="utf-8"), delimiter=","))
        t2 = time.time()
        print("read ", t2-t1)
    else:
        data = data_stored

    all_values = []
    time1, battery1, water_level1 = [], [], []
    time6, battery6, water_level6 = [], [], []

    t1 = time.time()
    for row in data:
        row_data = int(row["data"])
        if row_data > -10000 and row_data < 99999 and int(row["txtype"]) != "q":
            all_values.append(row_data)
    t2 = time.time()
    print("loop 1 ", t2-t1)

    stdev = np.std(all_values) if len(all_values) else np.nan
    mean = np.mean(all_values) if len(all_values) else np.nan

    maxarr = sorted(all_values)
    minval = maxarr[1]/100
    maxval = maxarr[len(maxarr) - 10]/100
    if (maxval > (mean + 6*stdev)/100):
        maxval = (mean + 6*stdev)/100

    water_alerts = get_on_off_alert(station_id)

    t1 = time.time()
    for row in data:
        mydate = row["date"] if is_gmt else convert_to_hst(row["date"])

        if int(row["txtype"]) == 1:
            time1, battery1, water_level1 = populate_data(
                row, mydate, time1, battery1, water_level1)

        elif int(row["txtype"]) == 6:
            time6, battery6, water_level6 = populate_data(
                row, mydate, time6, battery6, water_level6)
    t2 = time.time()
    print("loop 1 ", t2-t1)
    return time1, water_level1, time6, water_level6, battery1, battery6, water_alerts, minval, maxval, station_id_stored, data


def draw_graphs(station_id, is_gmt, station_id_stored, data_stored):

    time1, water_level1, time6, water_level6, battery1, battery6, water_alerts, minval, maxval, station_id, data = _get_water_level_graph(
        station_id, is_gmt, station_id_stored, data_stored)

    today = np.datetime64("today", "D")
    yesterday = np.datetime64("today", "D") - np.timedelta64(1, "D")

    ### Water Level ###
    fig_water_level = go.Figure()
    fig_water_level.add_trace(
        go.Scatter(
            x=time1,
            y=water_level1,
            name="Scheduled",
            mode="lines",
        )
    )
    fig_water_level.add_trace(
        go.Scatter(
            x=time6,
            y=water_level6,
            name="Alert",
            mode="markers",
            marker=dict(symbol="circle", size=10)
        )
    )
    fig_water_level.add_trace(
        go.Scatter(
            x=[time1[0], time1[len(time1)-1]],
            y=[water_alerts["on"], water_alerts["on"]],
            name=f"Alert on {int(water_alerts['on'])}",
            mode="lines",
            line=dict(color="red", dash="dash")
        )
    )
    fig_water_level.add_trace(
        go.Scatter(
            x=[time1[0], time1[len(time1)-1]],
            y=[water_alerts["off"], water_alerts["off"]],
            name=f"Alert off {int(water_alerts['off'])}",
            mode="lines",
            line=dict(color="green", dash="dash")
        )
    )

    fig_water_level.update_layout(
        title="Water Level",
        title_font={"size": 21},
        title_x=0.5,
        autosize=True,
        xaxis={"title": "Time/Date (GMT)" if is_gmt else "Time/Date (Pacific/Honolulu)",
               "range": [yesterday, today], "type": "date",
               "rangeslider_visible": True,
               "rangeselector": {
                   "buttons": [
                       {
                           "count": 2,
                           "label": "2d",
                           "step": "day",
                           "stepmode": "backward"
                       },
                       {
                           "count": 7,
                           "label": "1w",
                           "step": "day",
                           "stepmode": "backward"
                       },
                       {
                           "count": 42,
                           "label": "6w",
                           "step": "day",
                           "stepmode": "backward"
                       }
                   ],
                   "x": 0,
                   "y": 1.1
               }},
        yaxis={"title": "Feet", "range": [
            minval-1, max(water_alerts["on"]+1, maxval+2)]},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        modebar_remove=[
            "select2d", "lasso2d", "autoScale2d", "hoverClosestCartesian",
            "hoverCompareCartesian", "zoom3d", "pan3d",
            "resetCameraDefault3d", "resetCameraLastSave3d", "hoverClosest3d",
            "orbitRotation", "tableRotation", "zoomInGeo", "zoomOutGeo",
            "hoverClosestGeo", "toImage", "sendDataToCloud", "hoverClosestGl2d",
            "hoverClosestPie", "toggleHover", "toggleSpikelines", "resetViewMapbox",
        ],
        height=600
    )
    fig_water_level.update_xaxes(gridcolor="lightgrey")
    fig_water_level.update_yaxes(gridcolor="lightgrey")

    ### Battery Voltage ###
    fig_bat_voltage = go.Figure()
    fig_bat_voltage.add_trace(
        go.Scatter(
            x=time1,
            y=battery1,
            name="Scheduled",
            mode="lines",
        )
    )
    fig_bat_voltage.add_trace(
        go.Scatter(
            x=time6,
            y=battery6,
            name="Alert",
            mode="markers",
            marker=dict(symbol="circle", size=10)
        )
    )

    fig_bat_voltage.update_layout(
        title="Battery Voltage",
        title_font={"size": 21},
        title_x=0.5,
        autosize=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"title": "Time/Date (GMT)" if is_gmt else "Time/Date (Pacific/Honolulu)",
               "range": [yesterday, today], "type": "date",
               "rangeslider_visible": True,
               "rangeselector": {
                   "buttons": [
                       {
                           "count": 2,
                           "label": "2d",
                           "step": "day",
                           "stepmode": "backward"
                       },
                       {
                           "count": 7,
                           "label": "1w",
                           "step": "day",
                           "stepmode": "backward"
                       },
                       {
                           "count": 42,
                           "label": "6w",
                           "step": "day",
                           "stepmode": "backward"
                       }
                   ],
                   "x": 0,
                   "y": 1.1
               }, },
        modebar_remove=[
            "select2d", "lasso2d", "autoScale2d", "hoverClosestCartesian",
            "hoverCompareCartesian", "zoom3d", "pan3d",
            "resetCameraDefault3d", "resetCameraLastSave3d", "hoverClosest3d",
            "orbitRotation", "tableRotation", "zoomInGeo", "zoomOutGeo",
            "hoverClosestGeo", "toImage", "sendDataToCloud", "hoverClosestGl2d",
            "hoverClosestPie", "toggleHover", "toggleSpikelines", "resetViewMapbox",
        ],
        height=600
    )
    fig_bat_voltage.update_xaxes(gridcolor="lightgrey")
    fig_bat_voltage.update_yaxes(gridcolor="lightgrey")

    return fig_water_level, fig_bat_voltage, station_id, data
