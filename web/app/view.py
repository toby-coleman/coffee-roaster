import plotly.plotly as py
import plotly.graph_objs as go
from plotly import tools

import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd

import control


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
                                        html.H5('Controls'),
                                    ],
                                    className='card-header'
                                ),
                                html.Div(
                                    [
                                        html.H6('Set heater output'),
                                        dcc.Slider(min=0, max=100, step=1, value=-3, id='heat-slider'),
                                        html.Span('', className='badge badge-pill badge-primary text-center', id='heat-badge'),
                                    ],
                                    className='card-body'
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
                                dcc.Graph(id='main-chart'),
                                # For live updates to chart
                                dcc.Interval(
                                    id='interval-component',
                                    interval=2*1000, # in milliseconds
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


def set_heat(value):
    control.publish('set.heat', value)
    return '{0}%'.format(value)
