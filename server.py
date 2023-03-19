import dash

app = dash.Dash(
    "UHSLC",
    assets_folder = 'assets'
)

server = app.server
app.config.suppress_callback_exceptions = False
app.title = "UHSLC"
app.description = ""