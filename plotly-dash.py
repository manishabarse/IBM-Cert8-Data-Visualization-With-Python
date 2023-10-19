#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

def transition_delay(t: int, *args):
    for a in args:
        a.update_layout(transition_duration=t)

# Load the data using pandas
data = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv')

# Initialize the Dash app
app = dash.Dash(__name__)

# Set the title of the dashboard
app.title = "Automobile Statistics Dashboard"

#---------------------------------------------------------------------------------
# Create the dropdown menu options
dropdown_options = [
    {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
    {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
]
# List of years 
year_list = [i for i in range(1980, 2024, 1)]
#---------------------------------------------------------------------------------------
# Create the layout of the app
app.layout = html.Div([
    #TASK 2.1 Add title to the dashboard
    html.H1('Automobile Sales Statistics Dashboard', 
    style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 24}), #May include style for title
    html.Div([#TASK 2.2: Add two dropdown menus
        html.Label("Select Statistics:"),
        dcc.Dropdown(
            id='dropdown-statistics',
            options=[
                {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}],
			  
            value="Select Statistics",
            placeholder='Select a report type',
            style={'width': '90%', 'padding': '5px', 'fontSize': '20px', 'text-align': 'center'}
        )
    ]),
    html.Div(dcc.Dropdown(
            id='select-year',
            options=[{'label': i, 'value': i} for i in year_list],
            value="",
            placeholder=' Select a year',
            style={'width': '90%', 'padding': '5px', 'fontSize': '20px', 'text-align': 'center'}
        )),
    html.Div([#TASK 2.3: Add a division for output display
    html.Div(id='output-container', className='chart-grid', style={'display': 'flex', 'flexWrap': 'wrap'}),])
])


#TASK 2.4: Creating Callbacks
# Define the callback function to update the input container based on the selected statistics
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics',component_property='value'))

def update_input_container(value):
    if value =='Yearly Statistics': 
        return False
    return True

#Callback for plotting
# Define the callback function to update the input container based on the selected statistics
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-statistics', component_property='value'), Input(component_id='select-year', component_property='value')])
											 		   

def update_output_container(selected_statistics, input_year):

    if selected_statistics == 'Recession Period Statistics':
        # Filter the data for recession periods
        recession_data = data[data['Recession'] == 1]

        
#TASK 2.5: Create and display graphs for Recession Report Statistics

        # Plot 1: Automobile sales fluctuate over Recession Period (year-wise)
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(yearly_rec,
                           x='Year',
                           y='Automobile_Sales',
                           title='Average Automobile Sales fluctuation over Recession Period'))

        # Plot 2: Calculate the average number of vehicles sold by vehicle type
        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(
            figure=px.bar(average_sales, x='Vehicle_Type', y='Automobile_Sales', title='Average Number of Vehicles Sold by Vehicle Type'))

        # Plot 3: Pie chart for total expenditure share by vehicle type during recessions
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(
            figure=px.pie(exp_rec, names='Vehicle_Type', values='Advertising_Expenditure', title='Total Expenditure Share by Vehicle Type during Recessions'))

        # Plot 4: Bar chart for the effect of unemployment rate on vehicle type and sales
        unem_tysa = recession_data.groupby(['unemployment_rate', 'Vehicle_Type'], as_index=False)['Automobile_Sales'].sum()
        veh_Types = recession_data.Vehicle_Type.unique()
        fig = go.Figure()
        for v in veh_Types:
            fig.add_trace(go.Bar(x=unem_tysa[unem_tysa.Vehicle_Type == v]['unemployment_rate'],
                                 y=unem_tysa[unem_tysa.Vehicle_Type == v]['Automobile_Sales'], name=v))
        fig.update_layout(title='Effect of unemployment rate on vehicle type and sales',
                          xaxis_title='unemployment_rate', yaxis_title='Automobile_Sales')
        R_chart4 = dcc.Graph(figure=fig)
        
        return [
            html.Div(className='chart-item', children=[html.Div(children=R_chart1),html.Div(children=R_chart2)],style={'display': 'flex'}),
            html.Div(className='chart-item', children=[html.Div(children=R_chart3),html.Div(children=R_chart4)],style={'display': 'flex'})
            ]

    elif str(input_year).isnumeric() and selected_statistics == 'Yearly Statistics':
        yearly_data = data[data['Year'] == int(input_year)]

        # Plot 1: Yearly Automobile sales using a line chart for the whole period
        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y1 =px.line(yas, x='Year', y='Automobile_Sales', title='Yearly Automobile Sales')


        # Plot 2: Total Monthly Automobile sales using a line chart.
        tot_mon_sale = yearly_data.groupby('Month')['Automobile_Sales'].mean().reset_index()
        Y2 = px.line(tot_mon_sale, x='Month', y='Automobile_Sales',
                           title=f'Monthly Automobile sales for year {input_year}')

        # Plot 3: Bar chart for the average number of vehicles sold during the given year
        avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y3 = px.bar(avr_vdata, x='Vehicle_Type', y='Automobile_Sales',
                           title=f'Average Vehicles Sold by Vehicle Type in the year {input_year}')

        # Plot 4: Total Advertisement Expenditure for each vehicle using a pie chart
        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y4 = px.pie(exp_data, names='Vehicle_Type', values='Advertising_Expenditure',
                           title=f'Total Advertisement Expenditure by Vehicle Type in the year {input_year}')
        
        transition_delay(1000, Y1, Y2, Y3, Y4)

        Y_chart1=dcc.Graph(figure=Y1)
        Y_chart2=dcc.Graph(figure=Y2)
        Y_chart3=dcc.Graph(figure=Y3)
        Y_chart4=dcc.Graph(figure=Y4)

        return [
                html.Div(className='chart-item', children=[html.Div(Y_chart1),html.Div(Y_chart2)],style={'display': 'flex'}),
                html.Div(className='chart-item', children=[html.Div(Y_chart3),html.Div(Y_chart4)],style={'display': 'flex'})
                ]
    

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)