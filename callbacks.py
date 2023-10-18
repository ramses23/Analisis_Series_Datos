from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import mne
from mne import EpochsArray
import numpy as np
from utils import decode_contents

def register_callbacks(app):

    @app.callback(
        [Output('column-dropdown', 'options'),
         Output('upload-success-message', 'children')],
        Input('upload-data', 'contents'),
        State('upload-data', 'filename')
    )
    def update_dropdown(contents, filename):
        if contents is not None:
            decoded = decode_contents(contents)
            return [{'label': col, 'value': col} for col in decoded.columns], f"¡El Archivo {filename} fue cargado con éxito!"
        return [], ''

    @app.callback(
        Output('data-graph', 'figure'),
        [Input('analyze-button', 'n_clicks')],
        [State('upload-data', 'contents'),
        State('column-dropdown', 'value'),
        State('freq-input', 'value'),
        State('unit-input', 'value'),
        State('time-start-input', 'value'),
        State('time-end-input', 'value'),
        State('highpass-input', 'value'),
        State('lowpass-input', 'value')]
    )
    def update_graph(n_clicks, contents, selected_column, freq_ms, unit, time_start_sec, time_end_sec, highpass_freq, lowpass_freq):
        if contents and selected_column and freq_ms:
            decoded = decode_contents(contents)
            signal_data = decoded[selected_column].values
            signal_data = signal_data.reshape(1, -1)  # Reshape data to (1, n_samples)

            # Create MNE Info object
            info = mne.create_info(ch_names=['signal'], sfreq=freq_ms * 1000, ch_types=['eeg'])

            # Create RawArray object
            raw = mne.io.RawArray(signal_data, info)

            # Filter the signal
            raw.filter(l_freq=highpass_freq, h_freq=lowpass_freq)

            # Select the time range
            raw.crop(tmin=time_start_sec, tmax=time_end_sec)

            # Get the data and times for plotting
            data, times = raw[:, :]

            fig = go.Figure()
            fig.add_trace(go.Scatter(y=data[0], x=times, mode='lines', name=selected_column))
            fig.update_layout(title=f"Señal {selected_column} entre {time_start_sec} y {time_end_sec} segundos",
                            xaxis_title="Tiempo (s)",
                            yaxis_title=unit,
                            template="plotly_white")
            return fig

        return {}


    @app.callback(
        Output('wavelet-graph', 'figure'),
        Input('wavelet-button', 'n_clicks'),
        State('upload-data', 'contents'),
        State('column-dropdown', 'value'),
        State('freq-input', 'value'),
        State('time-start-input', 'value'),
        State('time-end-input', 'value'),
        State('highpass-input', 'value'),
        State('lowpass-input', 'value'),
        State('wavelet-freq-min', 'value'),
        State('wavelet-freq-max', 'value')
    )

    def update_wavelet_graph(n_clicks, contents, selected_column, freq_ms, time_start_sec, time_end_sec, highpass_freq, lowpass_freq, wavelet_freq_min, wavelet_freq_max):
    
        if contents and selected_column:
            decoded = decode_contents(contents)
            signal_data = decoded[selected_column].values
            signal_data = signal_data.reshape(1, -1)  # Reshape data to (1, n_samples)

            # Create MNE Info object
            info = mne.create_info(ch_names=['signal'], sfreq=freq_ms * 1000, ch_types=['eeg'])

            # Create RawArray object
            raw = mne.io.RawArray(signal_data, info)

            # Filter the signal
            raw.filter(l_freq=highpass_freq, h_freq=lowpass_freq)

            # Create an Epochs object from the Raw data
            events = np.array([[raw.first_samp, 0, 1]])  # Single event at the beginning
            epochs = EpochsArray(signal_data[None], info, events=events, tmin=raw.times[0])

            # Compute TFR
            frequencies = np.arange(wavelet_freq_min, wavelet_freq_max, 1)
            power = mne.time_frequency.tfr_multitaper(epochs, freqs=frequencies, n_cycles=6, use_fft=True, return_itc=False)

            # Extract data for visualization
            data = power.data[0]
            times = power.times
            freqs = power.freqs

            # Create figure for the scalogram
            fig = go.Figure(data=go.Heatmap(z=data,
                                            x=times,
                                            y=freqs,
                                            colorscale='Viridis',
                                            zsmooth='best'))
            fig.update_layout(title='Escalograma (Wavelet Power Spectrum)',
                            xaxis_title='Tiempo (s)',
                            yaxis_title='Frecuencia (Hz)',
                            template="plotly_white")
            return fig

        return {}