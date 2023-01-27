import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go


stations_csv = 'https://uhslc.soest.hawaii.edu/komar/stations.csv'
df = pd.read_csv(stations_csv)
token = os.environ.get('MAPBOX_TOKEN')


def get_longitude():
    return df.X

def get_latitude():
    return df.Y

def get_locations_name():
    return df.name

def get_stations_table_data(column_names):
    stations_table = df[column_names]
    table_data = stations_table.to_dict('records')
    
    return table_data

def get_stations_dropdown_options():
    data = df.to_dict('records')
    options = [f'{record["id"]} {record["dlnrid"]} {record["name"]}' for record in data]
    return [{'label': opt, 'value': opt} for opt in options]

def get_on_off_alert(station_id):
    return {"off": df[df.id==station_id].level_alert_off.values[0], 
            "on": df[df.id==station_id].level_alert_on.values[0]}

def draw_map():
    fig = go.Figure(go.Scattermapbox(
        lat=get_latitude(),
        lon=get_longitude(),
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=9
        ),
        text=get_locations_name(),
    ))

    fig.update_layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=token,
            bearing=0,
            center=dict(
                lat=21,
                lon=-158
            ),
            pitch=0,
            zoom=6
        ),
        margin = dict(l=0, r=0, t=0, b=0)
    )
    return fig

def populate_data(row, date, time, battery, water_level):
    time.append(date)
    battery.append(row['bv'])
    if row['data'] > -10000 and row['data'] < 99999:
        water_level.append(row['data'] / 100)
    else:
        water_level.append(np.nan)
    
    return time, battery, water_level


def _get_water_level_graph(station_id, is_gmt):
    df = pd.read_csv("data.csv")
    all_values = []
    time1, battery1, water_level1 = [], [], []
    time6, battery6, water_level6 = [], [], []

    for i in range(len(df)):
        if df.at[i, "data"] > -10000 and df.at[i, "data"] < 99999 and df.at[i, "txtype"] != "q":
            all_values.append(df.at[i, "data"])

    stdev = np.std(all_values) if len(all_values) else np.nan
    mean = np.mean(all_values) if len(all_values) else np.nan

    maxarr = sorted(all_values)
    minval = maxarr[1]/100
    maxval = maxarr[len(maxarr) - 10]/100
    if (maxval > (mean + 6*stdev)/100):
        maxval = (mean + 6*stdev)/100

    water_alerts = get_on_off_alert(station_id)

    for i in range(len(df)):
        row = df.loc[i]
        mydate = row['date']
        #TODO add timezone conversion for mydate

        if row['txtype'] == 1:
            time1, battery1, water_level1 = populate_data(row, mydate, time1, battery1, water_level1)

        elif row['txtype'] == 6:
            time6, battery6, water_level6 = populate_data(row, mydate, time6, battery6, water_level6)

    return time1, water_level1, time6, water_level6, battery1, battery6, water_alerts, minval, maxval

def draw_graphs(station_id, is_gmt):

    time1, water_level1, time6, water_level6, battery1, battery6, water_alerts, minval, maxval = _get_water_level_graph(station_id, is_gmt)

    today = np.datetime64('today', 'D')
    yesterday = np.datetime64('today', 'D') - np.timedelta64(1, 'D')

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
        "range": [yesterday, today], "type": 'date',
        "rangeslider_visible": True,
        "rangeselector": {
            "buttons": [
            {
                "count": 2,
                "label": '2d',
                "step": 'day',
                "stepmode": 'backward'
            },
            {
                "count": 7,
                "label": '1w',
                "step": 'day',
                "stepmode": 'backward'
            },
            {
                "count": 42,
                "label": '6w',
                "step": 'day',
                "stepmode": 'backward'
            }
            ],
            "x": 0,
            "y": 1.1
        }},
        yaxis={"title": "Feet", "range":[minval-1, max(water_alerts["on"]+1, maxval+2)]},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        modebar_remove=[
        "select2d",
        "lasso2d",
        "autoScale2d",
        "hoverClosestCartesian",
        "hoverCompareCartesian",
        "zoom3d",
        "pan3d",
        "resetCameraDefault3d",
        "resetCameraLastSave3d",
        "hoverClosest3d",
        "orbitRotation",
        "tableRotation",
        "zoomInGeo",
        "zoomOutGeo",
        "hoverClosestGeo",
        "toImage",
        "sendDataToCloud",
        "hoverClosestGl2d",
        "hoverClosestPie",
        "toggleHover",
        "toggleSpikelines",
        "resetViewMapbox",
        ],    
        height=600
    )
    fig_water_level.update_xaxes(gridcolor='lightgrey')
    fig_water_level.update_yaxes(gridcolor='lightgrey')

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
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis={"title": "Time/Date (GMT)" if is_gmt else "Time/Date (Pacific/Honolulu)",
        "range": [yesterday, today], "type": 'date',
        "rangeslider_visible": True,
        "rangeselector": {
            "buttons": [
            {
                "count": 2,
                "label": '2d',
                "step": 'day',
                "stepmode": 'backward'
            },
            {
                "count": 7,
                "label": '1w',
                "step": 'day',
                "stepmode": 'backward'
            },
            {
                "count": 42,
                "label": '6w',
                "step": 'day',
                "stepmode": 'backward'
            }
            ],
            "x": 0,
            "y": 1.1
        },},
        modebar_remove=[
        "select2d",
        "lasso2d",
        "autoScale2d",
        "hoverClosestCartesian",
        "hoverCompareCartesian",
        "zoom3d",
        "pan3d",
        "resetCameraDefault3d",
        "resetCameraLastSave3d",
        "hoverClosest3d",
        "orbitRotation",
        "tableRotation",
        "zoomInGeo",
        "zoomOutGeo",
        "hoverClosestGeo",
        "toImage",
        "sendDataToCloud",
        "hoverClosestGl2d",
        "hoverClosestPie",
        "toggleHover",
        "toggleSpikelines",
        "resetViewMapbox",
        ],    
        height=600
    )
    fig_bat_voltage.update_xaxes(gridcolor='lightgrey')
    fig_bat_voltage.update_yaxes(gridcolor='lightgrey')

    return fig_water_level, fig_bat_voltage