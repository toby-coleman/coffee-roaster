import plotly.plotly as py
import plotly.graph_objs as go
from plotly import tools

import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd

import control

UPDATE_INTERVAL = 2


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
                                        # For live updates to data table
                                        dcc.Interval(
                                            id='data-interval-component',
                                            interval=UPDATE_INTERVAL * 1000, # in milliseconds
                                            n_intervals=0
                                        ),
                                    ],
                                    className='card-body'
                                ),
                                html.Div(
                                    [
                                        html.A("Download data", href="/download"),
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
                                dcc.Graph(id='main-chart', config={'displayModeBar': False}),
                                # For live updates to chart
                                dcc.Interval(
                                    id='interval-component',
                                    interval=15 * 1000, # in milliseconds
                                    n_intervals=0
                                ),
                            ],
                            className='card'
                        )
                    ], className='col-lg-8'),

            ], className='row ml-4 mr-4 pt-4'
        ),
    ]
)


def chart():
    fig = tools.make_subplots(
        rows=3, cols=1,
        shared_xaxes=True, specs=[[{'rowspan': 2}], [None], [{}]],
        print_grid=False
    )

    temperature = control.data('log.temperature')
    heat = control.data('log.heat')
    # Temperature trace
    fig.append_trace(
        go.Scatter(
            x=temperature.index,
            y=temperature.value,
            name='Temperature', line={'color': '#1f77b4', 'shape': 'hv', 'width': 1}, mode='lines'
        ),
        row=1, col=1
    )
    # Heater trace
    fig.append_trace(
        go.Scatter(
            x=heat.index,
            y=heat.value,
            name='Heater output', line={'color': '#d62728', 'shape': 'hv', 'width': 1}, mode='lines'
        ),
        row=3, col=1
    )
    # Axis range
    dfinish = pd.Timestamp.utcnow().value // 10 ** 6
    dstart = dfinish - 30 * 60 * 1000 # 30 minutes
    fig['layout'].update(
        xaxis={
            'title':'Time', 'range': [dstart, dfinish]
        },
        yaxis={'title': 'Temperature, °C'},
        yaxis2={'title': 'Heater state, %', 'range': [-10, 110]},
        margin={'l': 60, 'r': 25, 't': 25, 'b': 60},
        height=460,
        showlegend=False,
    )
    
    return fig


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
