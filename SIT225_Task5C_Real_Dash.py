"""SIT225 Task 5C — smooth playback of REAL recorded Arduino Cloud data.

Reads SIT225_Task5C_Real_Accelerometer_Data.csv (499 real synchronized
X/Y/Z samples). This is historical CSV playback, NOT a live cloud connection.
Keep this script and the CSV together in your Downloads folder.
"""
from collections import deque
from pathlib import Path
from threading import Lock
import pandas as pd
from dash import Dash, dcc, html, Input, Output
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

CSV_NAME = 'SIT225_Task5C_Real_Accelerometer_Data.csv'
CSV_PATH = Path(__file__).resolve().parent / CSV_NAME
if not CSV_PATH.is_file():
    raise SystemExit(f'Missing CSV: {CSV_PATH}\nDownload the supplied CSV into the SAME folder as this script.')

df = pd.read_csv(CSV_PATH)
needed = {'time', 'X', 'Y', 'Z'}
if not needed.issubset(df.columns):
    raise SystemExit(f'CSV columns must include {sorted(needed)}. Found: {list(df.columns)}')
df['time'] = pd.to_datetime(df['time'], utc=True, errors='coerce')
for col in ('X', 'Y', 'Z'):
    df[col] = pd.to_numeric(df[col], errors='coerce')
df = df.dropna(subset=['time', 'X', 'Y', 'Z']).sort_values('time').drop_duplicates('time')
if df.empty:
    raise SystemExit('No valid records in CSV.')
records = list(df[['time', 'X', 'Y', 'Z']].itertuples(index=False, name=None))

class SmoothStream:
    def __init__(self, max_points=500):
        self.max_points = max_points
        self._pending = deque()
        self._lock = Lock()

    def append(self, timestamp, x, y, z):
        stamp = timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + ' UTC'
        with self._lock:
            self._pending.append((stamp, float(x), float(y), float(z)))
            while len(self._pending) > self.max_points:
                self._pending.popleft()

    def drain(self):
        with self._lock:
            if not self._pending:
                return None
            batch = list(self._pending)
            self._pending.clear()
        stamps = [p[0] for p in batch]
        return ({'x': [stamps, stamps, stamps],
                 'y': [[p[1] for p in batch], [p[2] for p in batch], [p[3] for p in batch]]},
                [0, 1, 2], self.max_points)

stream = SmoothStream(max_points=max(500, len(records)))
app = Dash(__name__)
fig = go.Figure()
for axis in ('X', 'Y', 'Z'):
    fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name=axis, line={'width': 2}))
fig.update_layout(template='plotly_dark',
                  title='iPhone accelerometer — REAL Arduino Cloud CSV (recorded playback)',
                  xaxis_title='Recorded time (UTC)', yaxis_title='Accelerometer reading',
                  uirevision='keep', margin={'l': 60, 'r': 25, 't': 65, 'b': 75})
app.layout = html.Div([
    html.H2('SIT225 Task 5C — Smooth Recorded-Data Plot'),
    html.P('REAL phone sensor readings exported from Arduino Cloud. '
           'Historical CSV playback, NOT a live cloud/API connection.',
           style={'color': '#a7f3d0'}),
    html.Div(id='status', children=f'Loaded {len(records)} real samples. Playing back...'),
    dcc.Graph(id='live-graph', figure=fig, style={'height': '72vh'}),
    dcc.Interval(id='clock', interval=200, n_intervals=0),
], style={'maxWidth': '1250px', 'margin': 'auto', 'padding': '16px',
          'fontFamily': 'Arial', 'background': '#111827', 'color': 'white',
          'minHeight': '100vh'})

# Replay 3 real historical readings every 200 ms. This does NOT claim real-time acquisition.
SAMPLES_PER_TICK = 3

@app.callback(Output('live-graph', 'extendData'),
              Output('status', 'children'),
              Output('clock', 'disabled'),
              Input('clock', 'n_intervals'))
def update(n):
    start = n * SAMPLES_PER_TICK
    if start >= len(records):
        return None, f'Completed: {len(records)} real recorded samples plotted.', True
    end = min(start + SAMPLES_PER_TICK, len(records))
    for stamp, x, y, z in records[start:end]:
        stream.append(stamp, x, y, z)
    result = stream.drain()
    finished = end >= len(records)
    status = f'Plotted {end} / {len(records)} real recorded samples' + (' — completed.' if finished else ' — playing back...')
    return result, status, finished

if __name__ == '__main__':
    print(f'Loaded {len(records)} REAL records from {CSV_PATH}')
    print('RECORDED CSV PLAYBACK — NOT a live Arduino Cloud connection.')
    print('Open http://127.0.0.1:8050')
    app.run(debug=False, host='127.0.0.1', port=8050)
