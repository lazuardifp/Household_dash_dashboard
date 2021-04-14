# import library disini 
import dash # aplikasinya 
import dash_core_components as dcc # komponen komponen dashboard yang sering digunakan 
import dash_html_components as html #kerangka tempat naruh (layout)
import pandas as pd
import plotly.express as px
import numpy as np
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# masukan semua data wrangling disini 

household = pd.read_csv('data_input/household.csv', index_col=0)
household["purchase_time"] = household["purchase_time"].astype('Datetime64')
household["date"] = household["purchase_time"].dt.to_period("D")
household["date"] = household["date"].astype('str')
household["date"] = pd.to_datetime(household["date"])
household.sort_values("date", inplace=True)

household["sales"] = household["unit_price"] * household["quantity"]


# sampai disini data wranggiling 

app.title = "Dashboard Analisa Household"

app.layout = html.Div( #div utama
    children=[
        html.Div(
            className="header",
            children=[
                #ini untuk isi header.
                html.H1( # header1 
                    children="Household Analytics", className="header-title"
                ),
                html.P( # paragraph
                    children="Analyze the behavior of household prices"
                    " and the number of households sold in different markets"
                    " between October 2017 and September 2018"
                    " ",
                    className="header-description",
                ),
            ]
        ),

        html.Div(
            className="wrapper",
            children=[
                # ini untuk isi body 
                html.Div( # ini untuk filter
                    className='menu',
                    children=[
                        html.Div(
                            className = 'dropdown',
                            children = [ 
                                html.Div(children="Category", className="menu-title"),
                                dcc.Dropdown(id="category-filter",
                                            options=[
                                                {"label": Category, "value": Category}
                                                for Category in np.sort(household.sub_category.unique())
                                            ],
                                            value="Rice",
                                            clearable=False,
                                            className="dropdown",
                                ),
                            ]
                        ),
                        html.Div(
                                    children=[
                                        html.Div(children="Market", className="menu-title"),
                                        dcc.Dropdown(
                                            id="market-filter",
                                            options=[
                                                {"label": market, "value": market}
                                                for market in household.format.unique()
                                            ],
                                            value="supermarket",
                                            clearable=False,
                                            searchable=False,
                                            className="dropdown",
                                        ),
                                    ]
                                ),
                                html.Div(
                                    children=[
                                        html.Div(
                                            children="Date Range",
                                            className="menu-title"
                                            ),
                                        dcc.DatePickerRange(
                                            id="date-range",
                                            min_date_allowed=household.date.min().date(),
                                            max_date_allowed=household.date.max().date(),
                                            start_date=household.date.min().date(),
                                            end_date=household.date.max().date(),
                                        ),
                                    ]
                                )
                    ]
                ),
                
                html.Div(
                    className="card",
                    children=[
                        dcc.Graph(
                            id= 'price-chart'
                        )
                    ]
                ),
                html.Div(
                    className="card",
                    children=[
                        dcc.Graph(
                            id= 'volume-chart'
                        )
                    ]
                ),
            ]
            
        ),
    ]
)

@app.callback(
    [
        Output("price-chart", "figure"),
        Output("volume-chart", "figure")
        
    ],
    [
        Input("category-filter", "value"),
        Input("market-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)

def update_charts(Category, market, start_date, end_date):
    data_filter = (
        (household.sub_category == Category)
        & (household.format == market)
        & (household.date >= start_date)
        & (household.date <= end_date)
    )
    filtered_data = household.loc[data_filter, :]

    household_groupdate = filtered_data.groupby('date').mean().reset_index()

    price_chart_figure = px.line(household_groupdate,
                                    x="date", 
                                    y="sales",
                                    labels = {"date" : "Date",
                                            "sales" : "Sales"}
                                    )

    volume_chart_figure = px.histogram(filtered_data,
                                        y = "sales", 
                                        x = "quantity", 
                                        title = "Total Sales based on Quantity",
                                        labels = {"quantity" : "Purchase Quantities",
                                                  "sales" : "Sales"}
                                )

    return price_chart_figure, volume_chart_figure



if __name__ == "__main__":
    app.run_server(debug=True)