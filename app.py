import os
import plotly.graph_objects as go
import pandas as pd

from dash import Dash

token = os.environ.get('MAPBOX_TOKEN')

stations_csv = 'https://uhslc.soest.hawaii.edu/komar/stations.csv'
df = pd.read_csv(stations_csv)

site_lon = df.X
site_lat = df.Y
locations_name = df.name

fig = go.Figure(go.Scattermapbox(
    lat=site_lat,
    lon=site_lon,
    mode='markers',
    marker=go.scattermapbox.Marker(
        size=9
    ),
    text=locations_name,
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
)

fig.show()

app = Dash(__name__)
