from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import mne
from mne import EpochsArray
import numpy as np
from utils import decode_contents
from mne.time_frequency import psd_array_multitaper

def compute_psd_multitaper(raw, sfreq, t_ftimwin, tapsmofrq):
    signal_data, _ = raw[:, :]  # Aquí extraemos los datos del objeto RawArray
    result = psd_array_multitaper(signal_data[0], sfreq, fmin=0.0, fmax=50.0, bandwidth=tapsmofrq, adaptive=False)
    print("Resultado de psd_array_multitaper:", result)  # Línea de depuración
    psd, freqs = result  # Cambiamos esta línea para desempacar el resultado
    return psd, freqs





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

    @app.callback(
        [Output('psd-graph', 'figure'), Output('psd-db-graph', 'figure')],
        [Input('psd-button', 'n_clicks')],
        [State('upload-data', 'contents'),
        State('column-dropdown', 'value'),
        State('freq-input', 'value'),
        State('mtm-timwin-input', 'value'),
        State('mtm-tapsmofrq-input', 'value'),
        State('wavelet-freq-min', 'value'),
        State('wavelet-freq-max', 'value'),
        State('unit-input', 'value')]
    )
    def update_psd_graph(n_clicks, contents, selected_column, freq_ms, mtm_timwin, mtm_tapsmofrq, freq_min, freq_max, unit):
        if contents and selected_column:
            decoded = decode_contents(contents)
            signal_data = decoded[selected_column].values
            signal_data = signal_data.reshape(1, -1)  # Reshape data to (1, n_samples)

            # Create MNE Info object
            info = mne.create_info(ch_names=['signal'], sfreq=freq_ms * 1000, ch_types=['eeg'])

            # Create RawArray object
            raw = mne.io.RawArray(signal_data, info)

            # Compute PSD
            freqs = np.arange(freq_min, freq_max, 1)
            psd, freqs_psd = compute_psd_multitaper(raw, freq_ms * 1000, mtm_timwin, mtm_tapsmofrq)

            
            # Ajuste de unidades y título
            y_label = f'Potencia ({unit}^2/Hz)'
            psd_db = 10 * np.log10(psd)

            # Gráfico de PSD en potencia
            fig_power = go.Figure(data=go.Scatter(x=freqs_psd, y=psd, mode='lines'))
            fig_power.update_layout(title='Espectro de Potencia',
                                    xaxis_title='Frecuencia (Hz)',
                                    yaxis_title=f'Potencia ({unit}^2/Hz)',
                                    template="plotly_white")

            # Gráfico de PSD en decibeles
            fig_db = go.Figure(data=go.Scatter(x=freqs_psd, y=psd_db, mode='lines'))
            fig_db.update_layout(title='Espectro de Potencia (Decibeles)',
                                xaxis_title='Frecuencia (Hz)',
                                yaxis_title='Decibeles (dB)',
                                template="plotly_white")

            return fig_power, fig_db

        else:
            return go.Figure(), go.Figure()