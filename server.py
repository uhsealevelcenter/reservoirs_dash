import dash
import dash_bootstrap_components as dbc

app = dash.Dash(
    "UHSLC",
    # assets_folder = 'app/assets',
    # external_stylesheets=[dbc.themes.BOOTSTRAP]
)

server = app.server
app.config.suppress_callback_exceptions = False
app.title = "UHSLC"
app.description = ""