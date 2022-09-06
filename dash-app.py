
# import dash
# import dash_html_components as html
import plotly.graph_objects as go
# import dash_core_components as dcc
from dash import Dash, html, dcc
import plotly.express as px
from dash.dependencies import Input, Output, State
from dash_table import DataTable
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import qualitative
from datetime import date


# external JavaScript files
external_scripts = [
    'https://www.google-analytics.com/analytics.js',
    {'src': 'https://cdn.polyfill.io/v2/polyfill.min.js'},
    {
        'src': 'https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.10/lodash.core.js',
        'integrity': 'sha256-Qqd/EfdABZUcAxjOkMi8eGEivtdTkh3b65xCZL4qAQA=',
        'crossorigin': 'anonymous'
    }
]

# external CSS stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

# Set up Dashboard and create layout
app = Dash(__name__,
                external_scripts=external_scripts,
                external_stylesheets=external_stylesheets)

app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})


# Create two pieces of text horizontally just under the navbar
# the title of the application and the day it was last updated
today = date.today()
last_update_text = today.strftime("%B %d, %Y")

app.layout = html.Div([

    # Page Header
    html.Div([
        html.H6("Data Feature Store Dashboard", id="info-title"),
        html.H6(f"Data updated through {last_update_text}", id="data-update"),
    ]),


    # Page Header
    html.Div([
        html.H1('Data Feature Store')
    ]),

    # Dropdown Grid
    html.Div([
        html.Div([
            # Select Data Source Dropdown
            html.Div([
                html.Div('Data Sources', className='three columns'),
                html.Div(dcc.Dropdown(id='data_sorce-selector',
                                      options=[{'label':'ATMS', 'value':'ATMS' },
                                      {'label': 'SRMS', 'value':'SRMS'},
                                      {'label': 'TomTom', 'value':'TTOM'}
                                      ]),
                         className='nine columns')
            ]),

            # Select Location Dropdown
            html.Div([
                html.Div('Locations', className='three columns'),
                html.Div(dcc.Dropdown(id='location-selector',
                                      options=[{'label':'A', 'value':'A' },
                                      {'label': 'B', 'value':'B'},
                                      {'label': 'C', 'value':'C'}
                                      ]),
                         className='nine columns')
            ]),

            # Select Data Feature Dropdown
            html.Div([
                html.Div('Data Feature', className='three columns'),
                html.Div(dcc.Dropdown(id='data_feature-selector',
                                      options=[{'label':'Week', 'value':'WEEK' },
                                      {'label': 'Holiday', 'value':'HOLY'},
                                      {'label': 'Rain', 'value':'RAIN'}
                                      ]),
                         className='nine columns')
            ]),
        ], className='six columns'),

        # Empty
        html.Div(className='six columns'),
    ], className='twleve columns'),

    # Results Grid
    html.Div([

        # Match Results Table
        html.Div(
            html.Table(id='results'),
            className='six columns'
        ),

        # Season Summary Table and Graph
        html.Div([
            # summary table
            dcc.Graph(id='Data-summary'),

            # graph
            dcc.Graph(id='Data-graph')
            # style={},

        ], className='six columns')
    ]),
])



@app.callback(Output(component_id='bar_plot', component_property= 'figure'),
              [Input(component_id='dropdown', component_property= 'value')])
def graph_update(dropdown_value):
    print(dropdown_value)
    fig = go.Figure([go.Scatter(x = df['date'], y = df['{}'.format(dropdown_value)],\
                     line = dict(color = 'firebrick', width = 4))
                     ])
    
    fig.update_layout(title = 'Data over time',
                      xaxis_title = 'Dates',
                      yaxis_title = 'Prices'
                      )
    return fig  



if __name__ == '__main__': 
    app.run_server()