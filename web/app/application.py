import dash
import dash_core_components as dcc
import dash_html_components as html

import view


stylesheets = [
    'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
]

app = dash.Dash(
    __name__,
    external_stylesheets=stylesheets
)
app.config['suppress_callback_exceptions'] = True
app.title = 'Raspberry Pi'
application = app.server


app.layout = html.Div(children=[
    html.Div(
        children=[
            html.H5(
                'Raspberry Pi',
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


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', threaded=True, debug=True, port=80)
