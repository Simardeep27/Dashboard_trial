import pandas as pd
import numpy as np
import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input,Output
import plotly.express as px
import equadratures.plot as Plot
import equadratures.poly as Poly
import base64
import io
import dash_table
import seaborn as sns
import plotly.tools
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css',dbc.themes.BOOTSTRAP]

app=dash.Dash(__name__,external_stylesheets=external_stylesheets,meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=0.8, maximum-scale=1.2,minimum-scale=0.5'}])

TOP_STYLE={
    "position":"fixed",
    "top":0,
    "left":0,
    "bottom":60,
    "width":"160rem",
    "padding":"2 rem 1 rem",
    "background-color":"#f8f9fa",
}

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 60,
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}
Aerofoil=pd.read_csv('airfoil_self_noise (2).csv', sep="\t", names = ['Freq','AOA','ChordLength','FSV','Suction','SPL'])



topbar=html.Div([
    html.P("Dataset")
], style=TOP_STYLE
)

sidebar= html.Div(
    [


    html.P("Enter the parameters",className="Para-txt"),

    html.Div(
        className="Options",
        children=[
            html.P("Select parameter X",className='txt'),
            dcc.Dropdown(
                            id='param_x',
                            # options=[
                            #     {"label":param_1,"value":param_1}
                            #     for param_1 in np.sort(Aerofoil.columns.unique())
                            # ],
                            # value="Freq",
                            # clearable=False,
                            # className="dropdown",
                        ),
            html.P("Select parameter Y",className='txt'),
            dcc.Dropdown(
                            id='param_y',
                            # options=[
                            #     {"label":param_2,"value":param_2}
                            #     for param_2 in np.sort(Aerofoil.columns.unique())
                            # ],
                            # value="Freq",
                            # clearable=False,
                            # className="dropdown",
                        ),

        ]
    ),
dcc.Upload(id='upload-data',
           children=html.A('Upload Files'),style={"margin-top":"30px"},multiple=True),
html.P("Parameter properties:"),
html.Div(className="Sliders",
    children=[
        html.P('Enter the lower range of Parameter'),
        dcc.Slider(
            id="lowerrange",
            min=0,
            max=2000,
            step=250,
            value=1000,
            marks={
                0:'0',
                500:'500',
                1000:'1000',
                1500:'1500',
                2000:'2000'
            }
        ),
html.P('Enter the upper range of Parameter'),
dcc.Slider(
            id="upperrange",
            min=0,
            max=2000,
            step=250,
            value=1000,
            marks={
                0:'0',
                500:'500',
                1000:'1000',
                1500:'1500',
                2000:'2000'
            }
        )
    ]
)
        ],
    style=SIDEBAR_STYLE,
)

content = html.Div(
     [

html.Div( className="Column-2",
                    children=[

html.Div(
        children=[
        html.H1(children=["Dataset Analysis"],className='header-title'),
        ],
),
                        html.Div( className="custom-plots",
                        children=[dcc.Graph(
                            id='plots', config={'displayModeBar':False},
                        ),
                        dcc.Graph(
                            id='pdf_x', config={'displayModeBar':False},
                        )
                        ]
                                  ),
                                  ]
          ),

html.Div(id='output-data'),
         html.Div(id='pdf'),
] ,style=CONTENT_STYLE

    )




app.layout=html.Div([
    topbar,
    sidebar,
    content
]
)

def parse_data(contents,filename):
    content_type, content_string=contents.split(',')
    decoded=base64.b64decode(content_string)
    if 'csv' in filename:
        df=pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    elif 'xls' in filename:
        df=pd.read_excel(io.BytesIO(decoded))
    else:
        pass
    return df


@app.callback(Output("output-data","children"),
    [Input("upload-data","contents"),
     Input("upload-data","filename")]
)
def update_table(contents, filename):
    table = html.Div()
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        table = html.Div([
        html.H5(filename),
        dash_table.DataTable(
            style_cell={
                'overflow':"hidden",
                'textOverflow':"ellipses",
                'maxWidth':"0",
            },
            page_size=20,
            style_table={'width':'500px','height': '300px', 'overflowY': 'auto'},
            tooltip_data=[
                {
                    column: {'value': str(value), 'type': 'markdown'}
                    for column, value in row.items()
                } for row in df.to_dict('records')
            ],tooltip_duration=None,
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
            },
        data=df.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in df.columns]
        ),
        ])
    return table




@app.callback(
    [Output("param_x","options")],
    [
         Input("upload-data", "contents"),
         Input("upload-data", "filename")
    ]
)
def update_dropdown(contents,filename):
    if contents is None:
        raise PreventUpdate
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        options = [
                 {"label":param_1,"value":param_1}
                  for param_1 in np.sort(df.columns.unique())
                  ],
        value = df.columns[0]
        return options
    else:
        options=[[{"label":"Not provided","value":"empty"}]]
        return options



@app.callback(
    [Output("param_y","options")],
    [
         Input("upload-data", "contents"),
         Input("upload-data", "filename")
    ]
)
def update_dropdown(contents,filename):
    if contents is None:
        raise PreventUpdate
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        options = [
                      {"label": param_2, "value": param_2}
                      for param_2 in np.sort(df.columns.unique())
                  ],
        value = df.columns[0]
        return options
    else:
        options = [[{"label":"Not provided","value":"empty"}]]
        return options



@app.callback(
     Output("plots","figure"),
     [
         Input("upload-data", "contents"),
         Input("upload-data", "filename"),
         Input("param_x","value"),
         Input("param_y","value")
     ],
 )
def update_plots(contents,filename,param_x,param_y):
    if contents is None:
        return dash.no_update
    else:
        if contents:
            contents = contents[0]
            filename = filename[0]
            df = parse_data(contents, filename)
            plots = {
                 "data": [
                {
                         "x": df['{}'.format(param_x)],
                         "y": df['{}'.format(param_y)],
                         'type': 'bar',
                         "hovertemplate": "$%{y:.2f}<extra></extra>",
                 },
             ],
                 "layout": {
                         "plot_bgcolor": "#00000",
                         "xaxis": {"fixedrange": True},
                         "yaxis": {"fixedrange": True},
                 },
             }
            return plots
        else:
            fig1 = go.Figure().add_annotation(x=2, y=2, text="No Data to Display",
                                           font=dict(family="sans serif", size=25, color="crimson"), showarrow=False,
                                           yshift=10)

            return fig1



@app.callback(
    Output("pdf_x","figure"),
    [
        Input("lowerrange","value"),
        Input("upperrange","value")
    ]
)
def pdf_plot(lowerrange,upperrange):
    param=Poly.Parameter(distribution="Gaussian",lower=lowerrange,upper=upperrange,order=3)
    s_values,pdf=param.get_pdf()
    fig = px.area(
         x=s_values, y=pdf)
    return fig






if __name__ == '__main__':
    app.run_server(debug=True)




