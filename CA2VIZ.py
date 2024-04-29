#!/usr/bin/env python
# coding: utf-8

# In[2]:


from dash import Dash, html, dcc, Input, Output, dash_table, callback
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd

# Step 3: Load your dataset
data = pd.read_csv('E:/e drive/DKIT/Sem 2/Data Viz/train.csv')  # Adjust the path as needed
# Convert 'Transported' column to int if it's a boolean
data['Transported'] = data['Transported'].astype(int)

# Step 4: Initialize the Dash app
app = Dash(__name__, suppress_callback_exceptions=True)

# Define the layout with navigation links

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Nav([
        dcc.Link('Home | ', href='/'),
        dcc.Link('Dataset Overview | ', href='/dataset-overview'),
        dcc.Link('Dataset | ', href='/dataset'),
        dcc.Link('Distribution | ', href='/distribution'),
        dcc.Link('Relationship | ', href='/relationship'),
        dcc.Link('Categorical Analysis | ', href='/categorical'),  # Moved up
        dcc.Link('Outcome Analysis', href='/outcome')  # Moved down
    ], className='navbar navbar-expand-lg navbar-light bg-light'),
    html.Div(id='page-content')
])

# Step 5: Define callbacks for dynamic page rendering
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return html.Div([
            html.H1('Home Page'),
            html.P('Welcome to the multi-page Dash app exploration.')
        ])
    elif pathname == '/dataset-overview':
        # Dataset Overview content
        return html.Div([
            html.H2("Spaceship Titanic Dataset Overview"),
            html.P("The journey of the Spaceship Titanic is one of the most ambitious space voyages in history."),
            html.P("On its maiden interstellar voyage, the marvel of engineering known as Spaceship Titanic encountered a cosmic anomaly. Despite advanced technology, the event led to an unknown number of passengers being transported elsewhere, mirroring the mystery and tragedy of its ancient Earth namesake."),
            html.P("As with the ocean-bound Titanic, certain demographic factors seemed to influence the likelihood of a passenger's transportation to parts unknown."),
            html.H3("Data Variables"),
            html.Ul([
                html.Li("Transported: 0 = Not Transported, 1 = Transported"),
                html.Li("HomePlanet: The planet from which the passenger boarded the spaceship"),
                html.Li("CryoSleep: Indicates if the passenger was in suspended animation for the trip"),
                html.Li("Cabin: Spacecraft cabin number indicating deck/number/side"),
                html.Li("Destination: The planet that the passenger was due to disembark at"),
                html.Li("Age: Passenger age"),
                html.Li("VIP: Indicates if the passenger paid for special VIP service during the voyage"),
                html.Li("RoomService, FoodCourt, ShoppingMall, Spa, VRDeck: Amount the passenger billed at each of the Spaceship Titanic's many luxury amenities"),
                html.Li("Name: Passenger name"),
            ]),
            html.P("This dataset invites us to examine the socio-economic factors aboard the Spaceship Titanic, mirroring the in-depth analyses possible with its historical counterpart."),
        ])
    elif pathname == '/dataset':
        return html.Div([
            html.H1('Dataset Overview'),
            dash_table.DataTable(
                data=data.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in data.columns if i not in ['PassengerId', 'Cabin', 'Name']],
                page_size=10,
                style_table={'overflowX': 'auto'}
            )
        ])
    elif pathname == '/distribution':
        return html.Div([
            html.H1('Distribution Analysis'),
            dcc.Dropdown(
                id='dist-dropdown',
                options=[{'label': col, 'value': col} for col in data.select_dtypes(include=['float64', 'int64']).columns],
                value='Age'
            ),
            dcc.Graph(id='dist-plot')
        ])
    elif pathname == '/relationship':
        return html.Div([
            html.H1('Relationship Analysis'),
            html.Div([
                dcc.Dropdown(
                    id='x-axis-dropdown',
                    options=[{'label': col, 'value': col} for col in data.select_dtypes(include=['number']).columns if col not in ['PassengerId', 'Cabin', 'Name']],
                    value='Age'  # default value for x-axis
                ),
                dcc.Dropdown(
                    id='y-axis-dropdown',
                    options=[{'label': col, 'value': col} for col in data.select_dtypes(include=['number']).columns if col not in ['PassengerId', 'Cabin', 'Name']],
                    value='FoodCourt'  # updated default value for y-axis
                )
            ], style={'margin-bottom': '20px'}),
            dcc.Graph(id='relationship-graph')
        ])
    elif pathname == '/categorical':
        return html.Div([
            html.H1('Categorical Analysis'),
            dcc.Dropdown(
                id='category-dropdown',
                options=[{'label': col, 'value': col} for col in ['HomePlanet', 'CryoSleep', 'Destination', 'VIP']],
                value='HomePlanet'  # default category selection
            ),
            dcc.Graph(id='categorical-transported-graph'),
        ])
    elif pathname == '/outcome':
        return html.Div([
            html.H1('Outcome Analysis'),
            dcc.Graph(id='outcome-graph')  # Placeholder for the graph that we will generate with a callback
        ])
    else:
        return '404 Page Not Found'

# Callbacks for the distribution plot
@app.callback(
    Output('dist-plot', 'figure'),
    [Input('dist-dropdown', 'value')]
)
def update_distribution_plot(selected_column):
    column_data = data[selected_column].dropna().astype(float)
    fig = px.histogram(column_data, x=selected_column)
    fig.update_layout(autosize=True)
    return fig

# Callbacks for the relationship plot
@app.callback(
    Output('relationship-graph', 'figure'),
    [Input('x-axis-dropdown', 'value'), Input('y-axis-dropdown', 'value')]
)
def update_relationship_graph(x_axis_name, y_axis_name):
    if not x_axis_name or not y_axis_name:
        raise PreventUpdate
    fig = px.scatter(data, x=x_axis_name, y=y_axis_name, title=f'Relationship between {x_axis_name} and {y_axis_name}')
    return fig
   
# Callback for the Categorical Analysis graph
@app.callback(
    Output('categorical-transported-graph', 'figure'),
    [Input('category-dropdown', 'value')]
)
def update_categorical_graph(selected_category):
    if selected_category not in data.columns:
        raise PreventUpdate
    
    category_proportions = data.groupby(selected_category)['Transported'].mean().reset_index()
    
    fig = px.bar(
        category_proportions,
        x=selected_category,
        y='Transported',
        title=f'Proportion of Transported Passengers by {selected_category}'
    )
    fig.update_traces(marker_color='blue')
    fig.update_layout(yaxis_title='Average Transported')
    
    return fig


# Callback for the Outcome Analysis graph
@app.callback(
    Output('outcome-graph', 'figure'),
    [Input('url', 'pathname')]  # This input is just a placeholder, you can remove it if not needed.
)
def update_outcome_graph(pathname):
    if pathname != '/outcome':
        raise PreventUpdate
    # Generate the stacked bar chart for 'HomePlanet' and 'Transported'
    fig = px.histogram(
        data_frame=data, 
        x='Transported', 
        color='HomePlanet', 
        barmode='stack',
        title='Transportation Status by Home Planet'
    )
    # Customize the layout of the figure as needed
    fig.update_layout(
        xaxis_title='Transported',
        yaxis_title='Count',
        xaxis=dict(type='category')  # Ensures that 'Transported' is treated as a categorical variable
    )
    return fig
 

# Step 6: Run the app
if __name__ == '__main__':
    app.run_server(port=8506)  # Make sure this port is free on your system


# In[ ]:




