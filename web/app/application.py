import dash
import dash_core_components as dcc
import dash_html_components as html

from flask import Flask, send_file
from datetime import datetime

import view


stylesheets = [
    'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
]
application = Flask(__name__)
app = dash.Dash(
    server=application,
    external_stylesheets=stylesheets
)
app.config['suppress_callback_exceptions'] = True
app.title = 'Coffee Roast Controller'


app.layout = html.Div(children=[
    html.Div(
        children=[
            html.H5(
                'Coffee Roaster',
                className='my-0 mr-md-auto text-light font-weight-bold',
            ),
            html.Nav(
                children=[
                    # Button/status go here
                ], className='my-2 my-md-0 mr-md-3',
            )
        ], className='d-flex flex-column flex-md-row align-items-center p-3 px-md-4 mb-3 bg-dark border-bottom shadow-sm gradient-nav',
    ),

    # URL bar (not visible)
    dcc.Location(id='url', refresh=False),

    # Page content
    html.Div(id='page-content', className='px-md4')

])


@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    return view.layout


# Callback to update chart
@app.callback(dash.dependencies.Output('main-chart', 'figure'),
              [dash.dependencies.Input('interval-component', 'n_intervals')])
def update_chart(n):
    return view.chart()


# Callback to set heater level
@app.callback(dash.dependencies.Output('heat-badge', 'children'),
              [dash.dependencies.Input('heat-slider', 'value')])
def update_scatter_chart(value):
    return view.set_heat(value)


# Callback to set temperature ROR on PID control
@app.callback(dash.dependencies.Output('ror-badge', 'children'),
              [dash.dependencies.Input('ror-slider', 'value'),
               dash.dependencies.Input('data-interval-component', 'n_intervals')])
def update_scatter_chart(value, n):
    return view.update_pid(value)


# Callback to update heat-badge colour
@app.callback(dash.dependencies.Output('heat-badge', 'className'),
              [dash.dependencies.Input('data-interval-component', 'n_intervals')])
def update_heat_badge(n):
    return view.badge_auto(True)


# Callback to update ror-badge colour
@app.callback(dash.dependencies.Output('ror-badge', 'className'),
              [dash.dependencies.Input('data-interval-component', 'n_intervals')])
def update_ror_badge(n):
    return view.badge_auto(False)


# Callback to update latest value table
@app.callback(dash.dependencies.Output('latest-table', 'children'),
              [dash.dependencies.Input('data-interval-component', 'n_intervals')])
def update_table(n):
    return view.table()


# Data download handler
@app.server.route('/download')
def download():
    df = view.data_summary(['log.temperature', 'log.heat', 'log.auto_mode'])
    return send_file(
        df.to_csv(),
        mimetype='text/csv',
        as_attachment=True,
        attachment_filename='profile_{0:%Y%m%d}.csv'.format(datetime.now())
    )


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', threaded=True, debug=True, port=8080)
