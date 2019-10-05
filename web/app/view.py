import plotly.graph_objs as go
from plotly import subplots

import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import time

import control

# Colours: https://coolors.co/3e92cc-1d2d44-fffaff-d8315b-f0ebd8
UPDATE_INTERVAL = 1


def axis_limits():
    return [
        (pd.Timestamp.utcnow().floor('10min') - pd.Timedelta('20min')).to_pydatetime(),
        (pd.Timestamp.utcnow() + pd.Timedelta('5min')).ceil('10min').to_pydatetime()
    ]


def empty_figure(text='No data'):
    return {
    'layout': {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'showlegend': False,
        'xaxis': {
            'range': [0, 1],
            'showgrid': False,
            'zeroline': False,
            'showline': False,
            'ticks': '',
            'showticklabels': False
        },
        'yaxis': {
            'range': [0, 1],
            'showgrid': False,
            'zeroline': False,
            'showline': False,
            'ticks': '',
            'showticklabels': False
        },
        'annotations': [
            {
                'x': 0.5,
                'y': 0.5,
                'xref': 'x',
                'yref': 'y',
                'text': text,
                'font': {'color': 'white'},
                'showarrow': False,
            }
        ],
    },
}


def initialise_chart():
    fig = subplots.make_subplots(
        rows=3, cols=1,
        shared_xaxes=True, specs=[[{'rowspan': 2}], [None], [{}]],
        print_grid=False
    )
    
    fig.add_trace(
        # Temperature trace
        go.Scatter(
            x=[],
            y=[],
            name='Temperature', line={'color': '#1D2D44', 'shape': 'hv', 'width': 1}, mode='lines'
        ),
        row=1, col=1
    )
    fig.add_trace(
        # Heater trace
        go.Scatter(
            x=[],
            y=[],
            name='Heater output', line={'color': '#D8315B', 'shape': 'hv', 'width': 1}, mode='lines'
        ),
        row=3, col=1
    )
    fig.add_trace(
        # Stopwatch resets (vertical lines)
        go.Scatter(
            x=[],
            y=[],
            name='Stopwatch reset', marker={'color': '#3E92CC', 'symbol': 'star', 'size': 10}, mode='markers'
        ),
        row=3, col=1
    )
    # Layout
    fig['layout'].update(
        xaxis2={
            'range': axis_limits(),
            'autorange': False
        },
        yaxis={
            'title': 'Temperature, °C',
            'range': [0, 250],
            'autorange': False
        },
        yaxis2={'title': 'Heater state, %', 'range': [-10, 110]},
        margin={'l': 60, 'r': 25, 't': 25, 'b': 60},
        height=360,
        showlegend=False,
        plot_bgcolor='#F0EBD8'
    )
    
    return fig.to_dict()


layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H6('Set heater output:'),
                                        dcc.Slider(min=0, max=100, step=1, value=0, id='heat-slider'),
                                        html.Span('', className='badge badge-pill badge-success', id='heat-badge'),
                                        html.Br(),
                                        html.Br(),
                                        html.H6('Set temperature rise rate:'),
                                        dcc.Slider(min=0, max=20, step=0.5, value=0, id='ror-slider'),
                                        html.Span('', className='badge badge-pill badge-secondary', id='ror-badge'),
                                        html.Br(),
                                        html.Br(),
                                        html.H6('Latest data:'),
                                        html.Table(
                                            html.Tbody([], id='latest-table'),
                                            className='table table-striped table-sm'
                                        ),
                                        # For live updates to data table and chart
                                        dcc.Interval(
                                            id='data-interval-component',
                                            interval=10 * 1000, # in milliseconds (initial delay)
                                            n_intervals=0
                                        ),
                                    ],
                                    className='card-body',
                                ),
                                html.Div(
                                    [
                                        html.A(
                                            'Download data', href='/download',
                                            className='btn btn-sm btn-primary'
                                        ),
                                    ],
                                    className='card-footer text-center'
                                ),
                            ],
                            className='card',
                            style={'width': '100%', 'height': '460px'}
                        )
                    ], className='col-lg-4'),

                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        dcc.Graph(figure=empty_figure('Loading...'), id='main-chart', config={'displayModeBar': False}),
                                        # Slow updates to chart formatting
                                        dcc.Interval(
                                            id='interval-component',
                                            interval=5 * 60 * 1000, # in milliseconds
                                            n_intervals=0
                                        ),
                                    ],
                                    className='card-body'
                                ),
                                html.Div(
                                    [
                                        html.Button(
                                            'Stopwatch', id='stopwatch-button',
                                            className='btn btn-sm btn-success'
                                        )
                                    ],
                                    className='card-footer text-center'
                                ),
                            ],
                            className='card'
                        )
                    ], className='col-lg-8'),

            ], className='row ml-4 mr-4 pt-4'
        ),
        html.Div(
            id='hidden-div', style={'display': 'none'}
        )
    ]
)


def update_chart(fig): 
    # Find last updated timestamp and filter
    if fig['data'][0]['x']:
        temperature = control.data('log.temperature', max_points=25)
        temperature = temperature[temperature.index > fig['data'][0]['x'][-1]]
    else:
        # First update
        temperature = control.data('log.temperature')
    if fig['data'][1]['x']:
        heat = control.data('log.heat', max_points=25)
        heat = heat[heat.index > fig['data'][1]['x'][-1]]
    else:
        # First update
        heat = control.data('log.heat')
    # Prepare vertical lines for stopwatch resets
    stopwatch = control.data('log.stopwatch', extend=False)
    if fig['data'][2]['x']:
        stopwatch = stopwatch[stopwatch.index > fig['data'][2]['x'][-1]]
    stopwatch = stopwatch.assign(value=100)
    return {
        'x': [temperature.index, heat.index, stopwatch.index],
        'y': [temperature.value, heat.value, stopwatch.value]
    },
    [0, 1, 2]


def table():
    data = control.latest(['log.temperature', 'log.temperature_roc', 'log.heat', 'log.setpoint'])
    return [
        html.Tr([html.Td(key.replace('log.', '')), html.Td('{0:.1f}'.format(value))])
        for key, value in data.items()
    ]


def set_heat(value):
    control.publish('set.heat', value)
    return '{0} %'.format(value)


def badge_auto(invert=False):
    # Use this to change icon colours when in manual/PID mode
    auto = control.latest('log.auto_mode')
    class_name = 'badge badge-pill badge-'
    if auto:
        return class_name + ('secondary' if invert else 'success')
    else:
        return class_name + ('success' if invert else 'secondary')


def start_pid(value):
    auto = control.latest('log.auto_mode')
    if not auto:
        # Start PID by changing setpoint to current temperature
        setpoint = control.latest('log.temperature')
        control.publish('set.setpoint', setpoint)
    return '{0} °C/minute'.format(value)


def update_pid(value):
    auto = control.latest('log.auto_mode')
    if auto:
        # Already running PID, so increment setpoint by given degC/minute
        setpoint = control.latest('log.setpoint') + value * UPDATE_INTERVAL / 60
        control.publish('set.setpoint', setpoint)
    return '{0} °C/minute'.format(value)


def data_summary(topics):
    # Prepare dataframe containing last 30 mins of history
    data = {
        t: control.data(t) for t in topics
    }
    dstart = pd.Timestamp.now() - pd.Timedelta(minutes=30)
    return pd.concat(
        [
            d[d.index >= dstart].resample('1s').ffill().rename(columns={'value': t})
            for t, d in data.items()
        ],
        axis=1
    )


def stopwatch():
    # Get last stopwatch reset
    reset_time = control.latest('log.stopwatch')
    elapsed = time.time() - reset_time if reset_time else 0
    # Return stopwatch value
    return 'Stopwatch: {minutes:02d}:{seconds:02d}'.format(
        minutes=int(elapsed / 60), seconds=int(elapsed % 60)
    )


def reset_stopwatch():
    control.log('log.stopwatch', time.time())
