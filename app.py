from dash import Dash
from layout import app_layout
from callbacks import register_callbacks

# Especifica la hoja de estilos externa
external_stylesheets = ['/assets/styles.css']

# Pasa la configuración al crear la instancia de Dash
app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = app_layout()

register_callbacks(app)  # Registra los callbacks

if __name__ == '__main__':
    app.run_server(debug=True)
