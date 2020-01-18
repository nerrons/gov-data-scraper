# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd 
from datetime import datetime as dt

def format_time(dt):
    return dt.strftime('%Y-%m-%d')

df = pd.read_excel('HSFO_volFLow.xlsx')
df = df[['Period','ComplexCountry','FlowValue']]
df = pd.pivot_table(df, index='Period', columns='ComplexCountry', values='FlowValue')

df.index = pd.to_datetime(df.index,format='%Y-%m')
print(df['ARA'].tolist())

country_list = df.columns
value_list = list(map(lambda s: s.lower().replace(" ", ""), country_list))
# time_list = list(df.index)
value_to_country = { val: country for val, country in zip(value_list, country_list) }

def list_generator(data_raw, time, val_range):
    country_range = list(map(lambda x: value_to_country[x], val_range))
    flow_range = data_raw[country_range].loc[time]
    return country_range, flow_range

def make_options(labels, values):
    return [dict((('label', str(l)), ('value', v))) for l, v in zip(labels, values)]

# print(flow_list)
country_dicts = make_options(country_list, value_list)

time = '2019-01-01'
vals = ['ara']

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='HSFO_production'),

    html.Div(children='''
        Dash: Chen Juan.
    '''),

    dcc.Dropdown(
        id='dropdown',
        options=country_dicts,
        value=['brazil','argentina','canada','norway'],
        multi=True
    ),

    dcc.Dropdown(
        id='year',
        options=make_options(range(2017, 2021), range(2017, 2021)),
        value=2019,
    ),

    dcc.Dropdown(
        id='month',
        options=make_options(range(1, 13), range(1, 13)),
        value=1,
    ),

    dcc.Graph(
        id='graph',
        figure={
            'data': [
                {'x': country_list, 'y': df.loc['2019-01-01'], 'type': 'bar'}
            ],
            'layout': {
                'title': 'Spot time for selected countries'
            }
        }
    ),

     dcc.Graph(
        id='graph2',
        figure={
            'data': [ {'x': df.index, 'y': df[value_to_country[val]].tolist()} for val in value_list ],
            'layout': {
                'title': 'Time series for countries'
            }
        }
    ),


])

@app.callback(
    Output('graph', 'figure'),
    [Input(component_id='dropdown', component_property='value'),
    Input(component_id='year', component_property='value'),
    Input(component_id='month', component_property='value')]
)
def update_output_div(convals, new_year, new_month):
    countries, flows = list_generator(df, format_time(dt(new_year, new_month, 1)), convals)
    return {
        'data': [
            {'x': countries, 'y': flows, 'type': 'bar'}
        ],
        'layout': {
            'title': str('Spot time for selected countries at '+str(new_year)+' ' +str(new_month))
        }        
    }

@app.callback(
    Output('graph2', 'figure'),
    [Input(component_id='dropdown', component_property='value')]
)
def update_output_div2(convals):
    
    return {
            'data': [ {'x': df.index, 'y': df[value_to_country[val]].tolist(),'name': value_to_country[val]} for val in convals ],
            'layout': {
                'title': 'Time series for countries',
                'legend':{'x': 1, 'y': 1}
            }
        }





if __name__ == '__main__':
    app.run_server(debug=True)

