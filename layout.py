from dash import dcc, html  

def app_layout():
    return html.Div([
        html.H1("Análisis de series temporales", id='title-text'),

        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Arrastra y suelta o ',
                html.A('selecciona un archivo CSV')
            ]),
            className='centered-text',
            multiple=False
        ),

        html.Div(id='upload-success-message', children='', className='success-message centered-text'),

        html.Label("Selecciona el registro (columna) que deseas analizar:"),
        dcc.Dropdown(id='column-dropdown'),

        html.Label("Ingresa la frecuencia de adquisición de la señal (datos por milisegundo):"),
        dcc.Input(id='freq-input', type='number', min=0.001, step=0.001, value=1),

        html.Label("Ingresa las unidades de la señal (ej. 'mV' para milivolts):"),
        dcc.Input(id='unit-input', type='text', value='mV'),

        html.Label("Inicio de ventana de tiempo (segundos):"),
        dcc.Input(id='time-start-input', type='number', min=0, step=0.1, value=0),

        html.Label("Final de ventana de tiempo (segundos):"),
        dcc.Input(id='time-end-input', type='number', min=0, step=0.1, value=10),

        html.Label("Frecuencia de corte para filtro pasa altas (Hz):"),
        dcc.Input(id='highpass-input', type='number', min=0, step=0.1, value=0),

        html.Label("Frecuencia de corte para filtro pasabajas (Hz):"),
        dcc.Input(id='lowpass-input', type='number', min=0, step=0.1, value=100),

        # campos para especificar las frecuencias para el análisis wavelet
        html.Label("Frecuencia mínima para wavelet (Hz):"),
        dcc.Input(id='wavelet-freq-min', type='number', min=0, step=0.1, value=1),

        html.Label("Frecuencia máxima para wavelet (Hz):"),
        dcc.Input(id='wavelet-freq-max', type='number', min=0, step=0.1, value=50),

                # entradas para el cálculo del espectro de potencia
        html.Label("Tiempo de ventana multitaper (t_ftimwin, será dividido por cada frecuencia de interés):"),
        dcc.Input(id='mtm-timwin-input', type='number', min=0.001, step=0.001, value=5),

        html.Label("Banda de frecuencia de suavizado multitaper (tapsmofrq en Hz):"),
        dcc.Input(id='mtm-tapsmofrq-input', type='number', min=0, step=0.1, value=0.4),

        html.Button('Analizar', id='analyze-button', className='primary-button'),
        html.Button('Generar Escalograma', id='wavelet-button', className='primary-button'),

        # Nuevo botón para calcular el espectro de potencia
        html.Button('Calcular Espectro de Potencia', id='psd-button', className='primary-button'),

        dcc.Graph(id='wavelet-graph', className='graph-style'),
        dcc.Graph(id='data-graph', className='graph-style'),

        # Nuevo gráfico para el espectro de potencia
        dcc.Graph(id='psd-graph', className='graph-style'),
        dcc.Graph(id='psd-db-graph', className='graph-style'),
    ])






