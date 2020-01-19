# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd 
from datetime import datetime as dt
import plotly.graph_objs as go

df1 = pd.read_excel('HSFO_volFLow.xlsx')
df1 = df1[['Period','ComplexCountry','FlowValue']]
df1 = pd.pivot_table(df1, index='Period', columns='ComplexCountry', values='FlowValue')
df1.index = pd.to_datetime(df1.index,format='%Y-%m')
country_list = df1.columns
value_list = list(map(lambda s: s.lower().replace(" ", ""), country_list))
value_to_country = { val: country for val, country in zip(value_list, country_list) }


def format_time(dt):
    return dt.strftime('%Y-%m-%d')

def generate_df(filepath):
    df = pd.read_excel(filepath)
    df = df[['Period','ComplexCountry','FlowValue']]
    df = pd.pivot_table(df, index='Period', columns='ComplexCountry', values='FlowValue')
    df.index = pd.to_datetime(df.index,format='%Y-%m')
    return df

def generate_country_list(df):
    country_list = df.columns
    return country_list

def generate_value_list(country_list):
    value_list = list(map(lambda s: s.lower().replace(" ", ""), country_list))
    return value_list

def generate_map_list(country_list,value_list):
    value_to_country = { val: country for val, country in zip(value_list, country_list) }
    return value_to_country

def list_generator(df, time, val_range):
    country_range = list(map(lambda x: value_to_country[x], val_range))
    flow_range = df[country_range].loc[time]
    return country_range, flow_range


def make_options(labels, values):
    return [dict((('label', str(l)), ('value', v))) for l, v in zip(labels, values)]



df2 = generate_df('LS.xlsx')


# print(flow_list)
country_dicts = make_options(country_list, value_list)

time = '2019-01-01'
vals = ['ara']

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

trace1 = go.Bar(
    x = country_list, y = df1.loc['2019-01-01']  ,
    name='Spot time for selected countries' ,width=0.8
)

def generate_line(country_list, data_list):
    return go.Scatter(x = country_list, y = data_list , name='cj')

def generate_defaultline(country_list,df):
    return go.Scatter(x = country_list, y = df.loc['2019-01-01'] , name='cj')

def generate_defaulttrace(country_list, df):
    return go.Bar(x = country_list, y = df.loc['2019-01-01']  ,name='Spot time for selected countries',width=0.8)

def generate_trace(country_list, data_list):
    return go.Bar( x = country_list, y = data_list, name='Spot time for selected countries',width=0.8)

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
        figure=go.Figure(data=[trace1,generate_defaulttrace(country_list, df2),generate_defaultline(country_list,df2)],
                               layout=go.Layout(barmode='stack'))
    
    ),

     dcc.Graph(
        id='graph2',
        figure={
            'data': [ {'x': df1.index, 'y': df1[value_to_country[val]].tolist()} for val in value_list ],
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
    countries, flows = list_generator(df1, format_time(dt(new_year, new_month, 1)), convals)
    countries2, flows2 = list_generator(df2, format_time(dt(new_year, new_month, 1)), convals)
    return go.Figure(data = [generate_trace(countries, flows),generate_trace(countries2, flows2),generate_line(countries2,flows2)],
                               layout=go.Layout(barmode='stack'))
        
    

@app.callback(
    Output('graph2', 'figure'),
    [Input(component_id='dropdown', component_property='value')]
)
def update_output_div2(convals):
    
    return {
            'data': [ {'x': df1.index, 'y': df1[value_to_country[val]].tolist(),'name': value_to_country[val]} for val in convals ],
            'layout': {
                'title': 'Time series for countries',
                'legend':{'x': 1, 'y': 1}
            }
        }





if __name__ == '__main__':
    app.run_server(debug=True)

